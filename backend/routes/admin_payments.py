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

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from routes.admin import require_admin
from services.supabase_client import get_admin_client
from services.stripe_recovery import recover_stuck_batch, recover_session, list_stuck_sessions

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin-payments'])


@router.get('/payments-health')
async def payments_health(
    days: int = Query(default=30, ge=1, le=365),
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Retourne les KPIs de santé des paiements Stripe.

    Réponse :
    - overall_status : 'green' | 'orange' | 'red'
    - webhook_secret_configured : bool
    - conversion_rate_pct : float (paid / (initiated+paid) sur X jours, hors admin bypass)
    - stuck_sessions_count : nb de sessions RÉELLES `initiated/unpaid` sur X jours
    - stuck_sessions_amount_eur : montant total potentiellement perdu
    - paid_sessions_count : nb de vraies conversions payées Stripe
    - by_pack : détail par pack_id
    - latest_stuck : 20 dernières sessions bloquées
    """
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

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

    def _tx_ok(row) -> bool:
        return row.get('payment_status') == 'paid'

    def _tx_stuck(row) -> bool:
        return row.get('status') == 'initiated' and row.get('payment_status') == 'unpaid'

    paid = [row for row in real if _tx_ok(row)]
    stuck = [row for row in real if _tx_stuck(row)]

    total = len(paid) + len(stuck)
    conv_pct = round(100.0 * len(paid) / total, 2) if total else 0.0
    stuck_amount = round(sum(float(row.get('amount') or 0) for row in stuck), 2)
    paid_amount = round(sum(float(row.get('amount') or 0) for row in paid), 2)

    # Par pack
    from collections import defaultdict
    by_pack: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'paid': 0, 'stuck': 0, 'stuck_amount': 0.0})
    for row in real:
        pack = row.get('pack_id') or 'unknown'
        if _tx_ok(row):
            by_pack[pack]['paid'] += 1
        elif _tx_stuck(row):
            by_pack[pack]['stuck'] += 1
            by_pack[pack]['stuck_amount'] += float(row.get('amount') or 0)
    by_pack_list = [
        {'pack_id': k, **v, 'stuck_amount': round(v['stuck_amount'], 2)}
        for k, v in sorted(by_pack.items(), key=lambda kv: -(kv[1]['paid'] + kv[1]['stuck']))
    ]

    # Webhook secret
    webhook_ok = bool(os.environ.get('STRIPE_WEBHOOK_SECRET', '').strip())

    # Feu tricolore
    if not webhook_ok or conv_pct < 5:
        overall = 'red'
    elif conv_pct < 15 or len(stuck) > 20:
        overall = 'orange'
    else:
        overall = 'green'

    return {
        'overall_status': overall,
        'window_days': days,
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
