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


@router.post('/stripe-recovery')
async def stripe_recovery(payload: RecoveryPayload, _admin: dict = Depends(require_admin)) -> Dict[str, Any]:
    """Scan les sessions bloquées et déclenche la livraison si Stripe dit `paid`.

    - `dry_run=True` (défaut) : rapport seul, aucun handler appelé.
    - `dry_run=False` : mise à jour DB + trigger handlers produit.
    - `session_id=cs_xxx` : cible une seule session (utile pour recovery manuel).
    """
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
