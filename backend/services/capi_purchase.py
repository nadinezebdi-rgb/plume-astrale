"""Envoi unique de l'event Meta `Purchase`, tous produits confondus.

Un paiement peut être confirmé par deux chemins indépendants :
  * le webhook Stripe (`checkout.session.completed`) ;
  * l'auto-réparation `self_heal_if_paid`, quand le webhook n'arrive pas.

Le verrou est un UPDATE conditionnel sur `checkout_attribution.capi_sent_at` :
seul l'appelant qui réussit à passer la colonne de NULL à une date envoie
réellement l'event à Meta.
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def _claim(session_id: str) -> Optional[dict]:
    """Réserve l'envoi pour cet appelant. Renvoie l'attribution, ou None."""
    from services.supabase_client import get_admin_client
    sb = get_admin_client()

    try:
        sb.table('checkout_attribution').upsert(
            {'session_id': session_id}, on_conflict='session_id',
            ignore_duplicates=True,
        ).execute()
    except Exception as e:
        logger.warning(f'[capi_purchase] upsert verrou {session_id}: {e}')

    now = datetime.now(timezone.utc).isoformat()
    try:
        res = (
            sb.table('checkout_attribution')
            .update({'capi_sent_at': now})
            .eq('session_id', session_id)
            .is_('capi_sent_at', 'null')
            .execute()
        )
    except Exception as e:
        logger.warning(f'[capi_purchase] claim update {session_id}: {e}')
        return None
    rows = res.data or []
    if not rows:
        return None
    return rows[0]


def _release(session_id: str) -> None:
    """Rend le verrou après un échec d'envoi, pour permettre une reprise."""
    from services.supabase_client import get_admin_client
    try:
        (
            get_admin_client().table('checkout_attribution')
            .update({'capi_sent_at': None})
            .eq('session_id', session_id)
            .execute()
        )
    except Exception as e:
        logger.warning(f'[capi_purchase] release {session_id}: {e}')


def _load_transaction(session_id: str) -> Optional[dict]:
    from services.supabase_client import get_admin_client
    res = (
        get_admin_client().table('payment_transactions')
        .select('session_id, user_email, pack_id, amount, currency, credits, payment_status')
        .eq('session_id', session_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None


async def track_purchase_once(
    session_id: str,
    session_data: Optional[dict] = None,
) -> bool:
    """Envoie `Purchase` à Meta pour ce paiement, au plus une fois."""
    if not session_id:
        return False
    try:
        tx = await asyncio.to_thread(_load_transaction, session_id)
    except Exception as e:
        logger.warning(f'[capi_purchase] lecture transaction {session_id}: {e}')
        tx = None

    sd = session_data or {}
    paid = sd.get('payment_status') == 'paid' or (tx and tx.get('payment_status') == 'paid')
    if not paid:
        return False

    try:
        attribution = await asyncio.to_thread(_claim, session_id)
    except Exception as e:
        logger.warning(f'[capi_purchase] verrou {session_id}: {e}')
        return False
    if attribution is None:
        return False

    amount_total = sd.get('amount_total')
    value_eur = round(amount_total / 100, 2) if amount_total else float((tx or {}).get('amount') or 0)
    currency = (sd.get('currency') or (tx or {}).get('currency') or 'eur').upper()
    # Fallback email : session Stripe > tx > None (Match Quality dégradé mais event envoyé)
    email = (
        (tx or {}).get('user_email')
        or (sd.get('customer_details') or {}).get('email')
        or sd.get('customer_email')
    )

    from services.meta_capi import send_capi_event
    ok = await send_capi_event(
        event_name='Purchase',
        event_id=attribution.get('event_id') or session_id,
        user_email=email,
        client_ip=attribution.get('client_ip'),
        client_user_agent=attribution.get('client_user_agent'),
        fbp=attribution.get('fbp'),
        fbc=attribution.get('fbc'),
        event_source_url=attribution.get('event_source_url'),
        value=value_eur,
        currency=currency,
        content_name=(tx or {}).get('pack_id') or 'oneshot',
        content_type='product',
        num_items=int((tx or {}).get('credits') or 0) or 1,
    )
    if not ok:
        await asyncio.to_thread(_release, session_id)
    return ok
