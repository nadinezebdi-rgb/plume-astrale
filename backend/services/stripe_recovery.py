"""
Stripe Recovery — rattrape les sessions Stripe payées mais non livrées.

Contexte : incident P0 février 2026 — `STRIPE_WEBHOOK_SECRET` manquant a
provoqué 83 sessions bloquées en `initiated/unpaid` alors que le paiement
avait bien eu lieu côté Stripe. Ce service :

1. Liste les transactions `initiated/unpaid` récentes
2. Vérifie leur statut RÉEL côté Stripe via `Session.retrieve()`
3. Si `paid` et livraison non faite → déclenche le bon handler produit
4. Met à jour la DB en conséquence

Idempotent et safe à relancer plusieurs fois.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import stripe

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# Mapping `metadata.kind` → (module_import_path, function_name)
# Cf. `server.py` /webhook/stripe pour la source de vérité.
_HANDLER_MAP: Dict[str, tuple] = {
    'theme_natal_pdf_oneshot':  ('services.theme_natal_oneshot_service', 'handle_theme_natal_oneshot_webhook'),
    'kabbale_arbre_de_vie':     ('services.kabbale_service',              'handle_kabbale_webhook'),
    'pack_karmique_kabbale':    ('services.pack_karmique_service',        'handle_pack_karmique_webhook'),
    'numerologie_code':         ('services.numerologie_webhook',          'handle_numerologie_webhook'),
    'karma_destin_analysis':    ('services.karma_destin_webhook',         'handle_karma_destin_webhook'),
    'voyage_karmique':          ('services.voyage_karmique_service',      'handle_voyage_karmique_webhook'),
    'consultation_ultime':      ('routes.consultation_ultime',            'handle_consultation_ultime_webhook'),
    'duo_completion':           ('services.duo_completion_service',       'handle_duo_completion_webhook'),
    'trio_decouverte':          ('services.trio_decouverte_service',      'handle_trio_decouverte_webhook'),
    'astrocartographie':        ('services.astrocartographie_service',    'handle_astrocartographie_webhook'),
    'lecture_complete':         ('services.lecture_complete_bundle',      'handle_lecture_complete_webhook'),
    'edition_reliee':           ('services.edition_reliee_service',       'handle_edition_reliee_webhook'),
    'rencontres_ultime':        ('services.rencontres_ultime_service',    'handle_rencontres_ultime_webhook'),
    'fenetre_rencontre_avancee': ('services.fenetre_rencontre_webhook',   'handle_fenetre_rencontre_webhook'),
}


def _resolve_handler(kind: Optional[str]):
    """Retourne la fonction handler pour un `kind` donné, ou None."""
    if not kind or kind not in _HANDLER_MAP:
        return None
    module_path, fn_name = _HANDLER_MAP[kind]
    try:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, fn_name, None)
    except Exception as e:
        logger.warning(f'[recovery] failed to import {module_path}.{fn_name}: {e}')
        return None


async def list_stuck_sessions(days: int = 60, limit: int = 500) -> List[Dict[str, Any]]:
    """Retourne les sessions Stripe RÉELLES bloquées en `initiated/unpaid`
    sur les X derniers jours."""
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    r = (
        sb.table('payment_transactions')
        .select('session_id, user_email, pack_id, amount, currency, status, payment_status, metadata, created_at')
        .gte('created_at', cutoff)
        .eq('status', 'initiated')
        .eq('payment_status', 'unpaid')
        .like('session_id', 'cs_%')
        .order('created_at', desc=True)
        .limit(limit)
        .execute()
    )
    return r.data or []


async def recover_session(session_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """Vérifie côté Stripe et déclenche la livraison si `paid`.

    - Idempotent : ne fait rien si déjà `completed/paid`.
    - `dry_run=True` : retourne juste le statut Stripe sans déclencher le handler.
    """
    stripe.api_key = os.environ['STRIPE_API_KEY']
    sb = get_admin_client()

    tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    if not tx_res or not tx_res.data:
        return {'session_id': session_id, 'ok': False, 'reason': 'tx_not_found'}
    tx = tx_res.data
    md = tx.get('metadata') or {}

    # Récupère l'état réel côté Stripe (offloadé en thread — la lib stripe est sync)
    import asyncio
    try:
        sess = await asyncio.to_thread(stripe.checkout.Session.retrieve, session_id)
    except stripe.error.InvalidRequestError as e:
        # Session inconnue de Stripe (expirée / ancien compte / cs_test)
        # → à traiter comme "abandonnée définitive", pas comme erreur métier.
        msg = str(e).lower()
        if 'no such checkout.session' in msg or 'resource_missing' in msg:
            return {
                'session_id': session_id,
                'user_email': tx.get('user_email'),
                'pack_id': tx.get('pack_id'),
                'kind': (md.get('kind') or md.get('product')),
                'db_status': tx.get('status'),
                'db_payment_status': tx.get('payment_status'),
                'stripe_payment_status': 'missing',
                'action': 'unknown_by_stripe',
                'ok': True,
            }
        return {'session_id': session_id, 'ok': False, 'reason': f'stripe_retrieve_fail: {e}'}
    except Exception as e:
        return {'session_id': session_id, 'ok': False, 'reason': f'stripe_retrieve_fail: {e}'}

    stripe_ps = sess.get('payment_status') if isinstance(sess, dict) else getattr(sess, 'payment_status', None)
    kind = md.get('kind') or md.get('product')

    result: Dict[str, Any] = {
        'session_id': session_id,
        'user_email': tx.get('user_email'),
        'pack_id': tx.get('pack_id'),
        'kind': kind,
        'db_status': tx.get('status'),
        'db_payment_status': tx.get('payment_status'),
        'stripe_payment_status': stripe_ps,
        'action': 'none',
        'ok': True,
    }

    if stripe_ps != 'paid':
        # Pas payé côté Stripe → rien à faire, session vraiment abandonnée
        result['action'] = 'abandoned'
        return result

    if dry_run:
        result['action'] = 'would_recover'
        return result

    # Marque la tx payée avant de dispatcher (idempotence + audit trail)
    try:
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
            'metadata': {**md, 'recovered_via': 'admin_recovery', 'recovered_at': datetime.now(timezone.utc).isoformat()},
        }).eq('session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[recovery] tx update fail {session_id}: {e}')

    handler = _resolve_handler(kind)
    if not handler:
        result['action'] = 'no_handler'
        result['ok'] = False
        return result

    try:
        await handler(session_id)
        result['action'] = 'recovered'
    except Exception as e:
        logger.exception(f'[recovery] handler {kind} fail for {session_id}: {e}')
        result['action'] = 'handler_error'
        result['ok'] = False
        result['error'] = str(e)

    return result


async def recover_stuck_batch(days: int = 60, limit: int = 100, dry_run: bool = True, concurrency: int = 8) -> Dict[str, Any]:
    """Scan et recovery en batch. Retourne un rapport agrégé.

    - `concurrency` : nb de sessions traitées en parallèle (limite les appels
      Stripe pour ne pas dépasser le timeout Cloudflare de 60s).
    """
    import asyncio
    stuck = await list_stuck_sessions(days=days, limit=limit)
    results: List[Dict[str, Any]] = []

    sem = asyncio.Semaphore(concurrency)

    async def _run_one(tx):
        async with sem:
            try:
                return await recover_session(tx['session_id'], dry_run=dry_run)
            except Exception as e:
                logger.warning(f"[recovery] batch item fail: {e}")
                return {'session_id': tx.get('session_id'), 'ok': False, 'reason': f'exception: {e}'}

    results = await asyncio.gather(*[_run_one(tx) for tx in stuck])

    # Agrégation
    from collections import Counter
    action_counts = Counter(r.get('action') or ('error' if not r.get('ok') else 'unknown') for r in results)
    return {
        'scanned': len(stuck),
        'dry_run': dry_run,
        'action_counts': dict(action_counts),
        'results': results,
    }
