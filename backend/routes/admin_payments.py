"""
Admin — Payments Health & Stripe Recovery.

Endpoints :
  GET  /api/admin/payments-health    → KPIs live pour dashboard feu tricolore
  POST /api/admin/stripe-recovery    → scan + recovery batch des sessions bloquées
  GET  /api/admin/stripe-webhook-status → état du webhook Stripe (secret configuré ?)

Créé Feb 2026 après incident P0 (STRIPE_WEBHOOK_SECRET manquant → 83 sessions
bloquées, 0 vente visible).
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from routes.admin import require_admin
from services.supabase_client import get_admin_client
from services.stripe_recovery import recover_stuck_batch, recover_session, list_stuck_sessions

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin-payments'])


@router.get('/payments-health')
async def payments_health(
    days: int = Query(default=30, ge=1, le=365),
    stuck_after_minutes: int = Query(default=15, ge=1, le=120,
                                     description="Nombre de minutes après `created_at` avant de considérer une session comme bloquée (défaut 15 min — temps de génération normale)"),
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Retourne les KPIs de santé des paiements Stripe.

    Règles ajustées Feb 2026 suite feedback fondatrice :
      • Déduplication par session_id : chaque session Stripe ne compte qu'UNE fois,
        même si plusieurs lignes `payment_transactions` existent (retries, double-insert).
        Préférence : paid > stuck > autres.
      • Seuil « bloquée » : une session n'est marquée bloquée qu'après `stuck_after_minutes`
        depuis sa création (défaut : 15 min, temps de génération normal).
      • Exclusion des e-mails de test (contact@, admin@, test@, @plume-astrale.fr, @test.*,
        @example.*).

    Réponse :
    - overall_status : 'green' | 'orange' | 'red'
    - webhook_secret_configured : bool
    - conversion_rate_pct : float (paid / (paid+stuck) sur X jours, hors admin bypass)
    - stuck_sessions_count : nb de sessions RÉELLES encore `initiated/unpaid` après le seuil
    - stuck_sessions_amount_eur : montant total potentiellement perdu
    - paid_sessions_count : nb de vraies conversions payées Stripe (uniques)
    - by_pack : détail par pack_id
    - latest_stuck : 20 dernières sessions bloquées
    """
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    stuck_threshold = datetime.now(timezone.utc) - timedelta(minutes=stuck_after_minutes)

    # Toutes les tx sur la fenêtre
    r = (
        sb.table('payment_transactions')
        .select('session_id, user_email, pack_id, amount, currency, status, payment_status, metadata, created_at')
        .gte('created_at', cutoff)
        .order('created_at', desc=True)
        .limit(2000)
        .execute()
    )
    rows = r.data or []

    # Filtre : uniquement sessions Stripe RÉELLES (exclut admin bypass)
    real = [row for row in rows if (row.get('session_id') or '').startswith('cs_')]

    # ─── Exclusion e-mails de test (fondatrice, admin, testeurs internes) ──
    def _is_test_email(email: Optional[str]) -> bool:
        if not email:
            return False
        e = email.lower().strip()
        if '@plume-astrale.fr' in e:          # emails internes
            return True
        if e.startswith('contact@') or e.startswith('admin@') or e.startswith('test@'):
            return True
        if '@test.' in e or '@example.' in e:  # TLDs de test standards
            return True
        if '+test' in e or '+debug' in e:      # alias gmail "+test"
            return True
        return False

    real = [row for row in real if not _is_test_email(row.get('user_email'))]

    # ─── Déduplication par session_id (bug fix : évite les 2× la même session) ──
    def _row_priority(row) -> int:
        """paid=0 (prio max) > stuck=1 > autres=2 — l'ordre pour `min()`."""
        if row.get('payment_status') == 'paid':
            return 0
        if row.get('status') == 'initiated' and row.get('payment_status') == 'unpaid':
            return 1
        return 2

    by_session: Dict[str, dict] = {}
    for row in real:
        sid = row.get('session_id')
        if not sid:
            continue
        if sid not in by_session or _row_priority(row) < _row_priority(by_session[sid]):
            by_session[sid] = row
    dedup_real = list(by_session.values())

    def _tx_ok(row) -> bool:
        return row.get('payment_status') == 'paid'

    def _tx_stuck_after_threshold(row) -> bool:
        """Session bloquée uniquement si assez vieille (> stuck_after_minutes)."""
        if row.get('status') != 'initiated' or row.get('payment_status') != 'unpaid':
            return False
        created = row.get('created_at')
        if not created:
            return True
        try:
            # Supabase renvoie '2026-02-27T17:34:12.345+00:00' ou similaire
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            return created_dt < stuck_threshold
        except Exception:
            return True  # fail-open : si on ne parse pas, on la compte comme bloquée

    paid = [row for row in dedup_real if _tx_ok(row)]
    stuck = [row for row in dedup_real if _tx_stuck_after_threshold(row)]

    total = len(paid) + len(stuck)
    conv_pct = round(100.0 * len(paid) / total, 2) if total else 0.0
    stuck_amount = round(sum(float(row.get('amount') or 0) for row in stuck), 2)
    paid_amount = round(sum(float(row.get('amount') or 0) for row in paid), 2)

    # Par pack
    from collections import defaultdict
    by_pack: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'paid': 0, 'stuck': 0, 'stuck_amount': 0.0})
    for row in dedup_real:
        pack = row.get('pack_id') or 'unknown'
        if _tx_ok(row):
            by_pack[pack]['paid'] += 1
        elif _tx_stuck_after_threshold(row):
            by_pack[pack]['stuck'] += 1
            by_pack[pack]['stuck_amount'] += float(row.get('amount') or 0)
    by_pack_list = [
        {'pack_id': k, **v, 'stuck_amount': round(v['stuck_amount'], 2)}
        for k, v in sorted(by_pack.items(), key=lambda kv: -(kv[1]['paid'] + kv[1]['stuck']))
    ]

    # Webhook secret
    webhook_ok = bool(os.environ.get('STRIPE_WEBHOOK_SECRET', '').strip())

    # Feu tricolore — seuils ajustés : « red » exige maintenant des sessions
    # réellement bloquées (après le seuil 15 min), pas des sessions en cours
    # de génération.
    if not webhook_ok or (total >= 10 and conv_pct < 5):
        overall = 'red'
    elif (total >= 10 and conv_pct < 15) or len(stuck) > 20:
        overall = 'orange'
    else:
        overall = 'green'

    return {
        'overall_status': overall,
        'window_days': days,
        'stuck_after_minutes': stuck_after_minutes,
        'webhook_secret_configured': webhook_ok,
        'conversion_rate_pct': conv_pct,
        'stuck_sessions_count': len(stuck),
        'stuck_sessions_amount_eur': stuck_amount,
        'paid_sessions_count': len(paid),
        'paid_sessions_amount_eur': paid_amount,
        'total_real_sessions': total,
        'by_pack': by_pack_list,
        'latest_stuck': [
            {
                'session_id': row.get('session_id'),
                'user_email': row.get('user_email'),
                'pack_id': row.get('pack_id'),
                'amount': row.get('amount'),
                'created_at': row.get('created_at'),
            }
            for row in stuck[:20]
        ],
    }


class RecoveryPayload(BaseModel):
    days: int = 60
    limit: int = 100
    dry_run: bool = True
    session_id: Optional[str] = None  # cible une session unique si fourni
    mode: str = 'stripe'              # 'stripe' (default) | 'db_replay' (from stripe_webhook_events)


@router.post('/stripe-recovery')
async def stripe_recovery(payload: RecoveryPayload, _admin: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Scan les sessions bloquées et déclenche la livraison si Stripe dit `paid`.

    Deux modes :
    - `mode='stripe'` (default) : croise avec l'API Stripe → limité aux 30j de
      rétention Stripe, mais couvre les sessions dont on n'a pas de payload local.
    - `mode='db_replay'` : rejoue depuis `stripe_webhook_events` (colonne payload).
      Fonctionne au-delà des 30j Stripe, plus rapide, mais nécessite que l'event
      soit passé au moins une fois par notre webhook.

    Params :
    - `dry_run=True` (défaut) : rapport seul, aucun handler appelé.
    - `dry_run=False` : mise à jour DB + trigger handlers produit.
    - `session_id=cs_xxx` : cible une seule session (mode stripe uniquement).
    """
    if payload.mode == 'db_replay':
        # Rejoue les events failed / orphans depuis stripe_webhook_events
        from server import replay_pending_events
        report = await replay_pending_events(limit=payload.limit, dry_run=payload.dry_run)
        return {'mode': 'db_replay', **report}

    if payload.session_id:
        result = await recover_session(payload.session_id, dry_run=payload.dry_run)
        return {'mode': 'single', 'result': result}

    report = await recover_stuck_batch(
        days=payload.days,
        limit=payload.limit,
        dry_run=payload.dry_run,
    )
    return {'mode': 'batch', **report}


@router.get('/stripe-recovery/preview')
async def stripe_recovery_preview(
    days: int = Query(default=60, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=500),
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Liste les sessions candidates au recovery, sans rien déclencher."""
    stuck = await list_stuck_sessions(days=days, limit=limit)
    return {
        'count': len(stuck),
        'sessions': [
            {
                'session_id': row.get('session_id'),
                'user_email': row.get('user_email'),
                'pack_id': row.get('pack_id'),
                'amount': row.get('amount'),
                'kind': (row.get('metadata') or {}).get('kind'),
                'created_at': row.get('created_at'),
            }
            for row in stuck
        ],
    }



@router.get('/stripe-webhook-health')
async def admin_stripe_webhook_health(_admin: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Diagnostic Stripe webhook — indique si STRIPE_WEBHOOK_SECRET est configuré,
    SANS jamais le révéler. Retourne aussi les stats récentes de webhooks reçus.

    Utilisé pour valider après un ajout de variable env sur Emergent Deployments.
    """
    from datetime import timedelta as _td
    secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '').strip()
    api_key = os.environ.get('STRIPE_API_KEY', '').strip()

    # Ne JAMAIS retourner la valeur. Uniquement des indicateurs booléens et un hash court non-réversible.
    secret_configured = bool(secret)
    secret_format_ok = secret.startswith('whsec_') if secret else False
    secret_len = len(secret) if secret else 0
    # Fingerprint = 8 premiers chars du sha256 (non-réversible, sert juste à confirmer si prod ↔ preview matchent)
    fingerprint = None
    if secret:
        import hashlib
        fingerprint = hashlib.sha256(secret.encode()).hexdigest()[:8]

    api_key_mode = None
    if api_key.startswith('sk_live_'):
        api_key_mode = 'live'
    elif api_key.startswith('sk_test_'):
        api_key_mode = 'test'
    elif api_key:
        api_key_mode = 'unknown'

    # Stats webhooks récents (24h) — table stripe_webhook_events (colonne handled_at)
    sb = get_admin_client()
    webhook_stats: Dict[str, Any] = {'last_24h': None, 'error': None}
    try:
        cutoff = (datetime.now(timezone.utc) - _td(hours=24)).isoformat()
        # `handled_at` = null pour les rows encore en processing ; on prend tout et on filtre côté Python
        res = sb.table('stripe_webhook_events').select(
            'event_type, status, handled_at'
        ).gte('handled_at', cutoff).limit(500).execute()
        rows = res.data or []
        by_status: Dict[str, int] = {}
        by_type: Dict[str, int] = {}
        for r in rows:
            s = r.get('status') or 'unknown'
            t = r.get('event_type') or 'unknown'
            by_status[s] = by_status.get(s, 0) + 1
            by_type[t] = by_type.get(t, 0) + 1
        webhook_stats['last_24h'] = {
            'total': len(rows),
            'by_status': by_status,
            'by_type': by_type,
        }
    except Exception as e:
        webhook_stats['error'] = str(e)[:200]

    ready = secret_configured and secret_format_ok and bool(api_key)
    hints = []
    if not secret_configured:
        hints.append("STRIPE_WEBHOOK_SECRET absent — ajouter la variable via Emergent Deployments → Production → Environment Variables (valeur commence par 'whsec_')")
    elif not secret_format_ok:
        hints.append(f"STRIPE_WEBHOOK_SECRET présent mais ne commence pas par 'whsec_' (longueur={secret_len}). Vérifier qu'aucun espace/guillemet n'a été copié.")
    if not api_key:
        hints.append("STRIPE_API_KEY absent — impossible d'appeler l'API Stripe")
    if api_key_mode == 'test' and secret_configured:
        hints.append("STRIPE_API_KEY en mode TEST mais webhook secret configuré : vérifier cohérence live/test avec le dashboard Stripe")

    return {
        'ready': ready,
        'secret': {
            'configured': secret_configured,
            'format_valid': secret_format_ok,
            'length': secret_len,
            'fingerprint': fingerprint,  # 8 chars sha256, non-réversible
        },
        'api_key': {
            'configured': bool(api_key),
            'mode': api_key_mode,
        },
        'webhook_events': webhook_stats,
        'hints': hints,
        'checked_at': datetime.now(timezone.utc).isoformat(),
    }


# ───────────────────────────────────────────────────────────────────────
# Remboursement Stripe (one-shot, ciblé — pour tests internes / incidents)
# ───────────────────────────────────────────────────────────────────────

class RefundPayload(BaseModel):
    session_id: Optional[str] = None       # cs_... (recommandé)
    payment_intent: Optional[str] = None    # pi_... (alternative directe)
    reason: Optional[str] = 'requested_by_customer'   # ou 'duplicate' | 'fraudulent'
    dry_run: bool = True
    note: Optional[str] = None              # ajouté en metadata du refund


@router.post('/stripe-refund')
async def stripe_refund(payload: RefundPayload, _admin: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Rembourse 100 % d'un paiement Stripe (ciblé par session_id ou payment_intent).

    - `dry_run=True` (défaut) : retourne les infos du charge sans rembourser.
    - `dry_run=False` : exécute `stripe.Refund.create(payment_intent=...)`.
    - `reason` doit être parmi : `requested_by_customer`, `duplicate`, `fraudulent`.
    - Marque la ligne `payment_transactions` associée avec `metadata.refunded_at`
      pour cohérence avec le dashboard refund_alert.

    Idempotent côté Stripe : si un refund existe déjà pour le PaymentIntent,
    Stripe retourne 400 — on le remonte proprement.
    """
    api_key = os.environ.get('STRIPE_API_KEY', '').strip()
    if not api_key:
        raise HTTPException(500, 'STRIPE_API_KEY non configuré')
    stripe.api_key = api_key

    allowed_reasons = {'requested_by_customer', 'duplicate', 'fraudulent'}
    reason = (payload.reason or 'requested_by_customer').strip()
    if reason not in allowed_reasons:
        raise HTTPException(400, f'reason invalide — valeurs permises : {sorted(allowed_reasons)}')

    pi_id = (payload.payment_intent or '').strip() or None

    # Résolution : session_id → payment_intent
    session_dict: Optional[Dict[str, Any]] = None
    if payload.session_id:
        try:
            sess = stripe.checkout.Session.retrieve(payload.session_id.strip())
            session_dict = sess.to_dict() if hasattr(sess, 'to_dict') else dict(sess)
            pi_id = pi_id or session_dict.get('payment_intent')
        except Exception as e:
            raise HTTPException(404, f'session Stripe introuvable : {e}')

    if not pi_id:
        raise HTTPException(400, 'session_id OU payment_intent est obligatoire')

    # Infos sur le charge pour le dry-run / confirmation
    charge_info: Dict[str, Any] = {}
    try:
        pi = stripe.PaymentIntent.retrieve(pi_id, expand=['latest_charge'])
        pi_dict = pi.to_dict() if hasattr(pi, 'to_dict') else dict(pi)
        latest = pi_dict.get('latest_charge') or {}
        if hasattr(latest, 'to_dict'):
            latest = latest.to_dict()
        charge_info = {
            'payment_intent': pi_id,
            'amount': (pi_dict.get('amount') or 0) / 100,
            'currency': pi_dict.get('currency'),
            'status': pi_dict.get('status'),
            'already_refunded': bool(latest.get('refunded')) if isinstance(latest, dict) else False,
            'charge_id': latest.get('id') if isinstance(latest, dict) else None,
            'customer_email': (pi_dict.get('receipt_email')
                               or ((latest or {}).get('billing_details') or {}).get('email')),
            'card_last4': (((latest or {}).get('payment_method_details') or {}).get('card') or {}).get('last4'),
        }
    except Exception as e:
        raise HTTPException(404, f'PaymentIntent introuvable : {e}')

    if payload.dry_run:
        return {
            'dry_run': True,
            'would_refund': True,
            'session_id': payload.session_id,
            'reason': reason,
            'charge': charge_info,
            'hint': 'Rappeler ce même endpoint avec `dry_run=false` pour exécuter.',
        }

    if charge_info.get('already_refunded'):
        return {
            'dry_run': False,
            'refunded': False,
            'reason_skipped': 'charge déjà remboursé',
            'charge': charge_info,
        }

    # Exécution du remboursement
    try:
        refund = stripe.Refund.create(
            payment_intent=pi_id,
            reason=reason,
            metadata={
                'admin_initiated': 'true',
                'note': (payload.note or '')[:200],
                'triggered_at': datetime.now(timezone.utc).isoformat(),
            },
        )
        refund_dict = refund.to_dict() if hasattr(refund, 'to_dict') else dict(refund)
    except stripe.error.StripeError as e:  # type: ignore[attr-defined]
        logger.warning(f'[stripe_refund] fail pi={pi_id}: {e}')
        raise HTTPException(400, f'Stripe refund rejeté : {e.user_message or str(e)}')

    # Marque la ligne payment_transactions associée (best-effort)
    try:
        sb = get_admin_client()
        sid = payload.session_id or (session_dict or {}).get('id')
        if sid:
            now_iso = datetime.now(timezone.utc).isoformat()
            r = sb.table('payment_transactions').select('metadata, session_id').eq('session_id', sid).limit(1).execute()
            if r.data:
                md = (r.data[0] or {}).get('metadata') or {}
                md['refunded_at'] = now_iso
                md['refund_reason'] = reason
                md['refund_id'] = refund_dict.get('id')
                sb.table('payment_transactions').update({'metadata': md}).eq('session_id', sid).execute()
    except Exception as e:
        logger.info(f'[stripe_refund] marquage DB skip: {e}')

    return {
        'dry_run': False,
        'refunded': True,
        'refund_id': refund_dict.get('id'),
        'amount_refunded': (refund_dict.get('amount') or 0) / 100,
        'currency': refund_dict.get('currency'),
        'status': refund_dict.get('status'),
        'charge': charge_info,
    }


@router.get('/stripe-refund/find-test-payments')
async def find_test_payments(
    amount_eur: float = Query(default=24.0, description='Montant TTC à chercher'),
    days: int = Query(default=30, ge=1, le=90),
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Liste les paiements correspondant à un montant donné (helper pour trouver
    la session à rembourser quand on n'a que « j'ai testé pour 24 € »)."""
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    r = (
        sb.table('payment_transactions')
        .select('session_id, user_email, pack_id, amount, currency, status, payment_status, created_at, metadata')
        .eq('payment_status', 'paid')
        .gte('created_at', cutoff)
        .order('created_at', desc=True)
        .limit(100)
        .execute()
    )
    rows = r.data or []
    matches = [row for row in rows if abs(float(row.get('amount') or 0) - amount_eur) < 0.01]
    return {
        'amount_eur': amount_eur,
        'window_days': days,
        'count': len(matches),
        'matches': [
            {
                'session_id': row.get('session_id'),
                'user_email': row.get('user_email'),
                'pack_id': row.get('pack_id'),
                'amount': row.get('amount'),
                'created_at': row.get('created_at'),
                'already_refunded': bool((row.get('metadata') or {}).get('refunded_at')),
            }
            for row in matches
        ],
    }
