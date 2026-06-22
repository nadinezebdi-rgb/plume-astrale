"""
Synastrie haut-ticket 49€ (Phase 3 cahier des charges).

Flow:
1. Frontend collecte les donnees natales des 2 personnes
2. POST /api/synastrie/checkout -> cree session Stripe one-shot (mode=payment)
3. Stripe redirige vers /synastrie/succes?session_id=...
4. Webhook checkout.session.completed -> handle_synastrie_webhook ->
   - status='paid'
   - genere le PDF (compatibility_pdf_generator)
   - envoie email Resend avec lien telechargement
5. Frontend poll GET /api/synastrie/status/{session_id} -> renvoie pdf_path quand pret
"""
import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import stripe
from fastapi import HTTPException

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

SYNASTRIE_PRICE_EUR = 49.00
SYNASTRIE_PRODUCT_NAME = 'Synastrie Plume Astrale — Rapport personnalise'
SYNASTRIE_DESCRIPTION = 'Rapport synastrie 25 pages : aspects planetaires, dynamiques relationnelles, points de croissance et invitations concretes.'


async def create_synastrie_checkout(
    user_id: Optional[str],
    user_email: Optional[str],
    person1_data: Dict[str, Any],
    person2_data: Dict[str, Any],
    origin_url: str,
) -> Dict[str, Any]:
    """Cree une session Stripe one-shot 49€ et enregistre l'achat en pending."""
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail='Service de paiement indisponible.')

    sb = get_admin_client()
    origin = (origin_url or '').rstrip('/') or 'https://plume-astrale.fr'

    # Validation minimale
    for label, p in [('person1', person1_data), ('person2', person2_data)]:
        if not p or not p.get('prenom') or not p.get('birth_date'):
            raise HTTPException(status_code=400, detail=f'Donnees natales incompletes pour {label}.')

    # 1) Cree l'enregistrement pending
    insert_payload = {
        'user_id': user_id,
        'email': user_email,
        'amount_cents': int(SYNASTRIE_PRICE_EUR * 100),
        'currency': 'eur',
        'status': 'pending',
        'person1_data': person1_data,
        'person2_data': person2_data,
    }
    purchase_id: Optional[str] = None
    try:
        ins = sb.table('synastrie_purchases').insert(insert_payload).execute()
        purchase_id = (ins.data or [{}])[0].get('id')
    except Exception as e:
        logger.warning(f'[synastrie] insert pending: {e}')

    # 2) Cree la session Stripe
    metadata = {
        'kind': 'synastrie_oneshot',
        'user_id': user_id or '',
        'purchase_id': purchase_id or '',
    }

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': SYNASTRIE_PRODUCT_NAME,
                    'description': SYNASTRIE_DESCRIPTION,
                },
                'unit_amount': int(SYNASTRIE_PRICE_EUR * 100),
            },
            'quantity': 1,
        }],
        customer_email=user_email,
        success_url=f'{origin}/synastrie/succes?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{origin}/synastrie',
        metadata=metadata,
    )

    # 3) Maj session_id
    if purchase_id:
        try:
            sb.table('synastrie_purchases').update({
                'stripe_session_id': session.id,
            }).eq('id', purchase_id).execute()
        except Exception as e:
            logger.warning(f'[synastrie] update session_id: {e}')

    return {
        'session_id': session.id,
        'checkout_url': session.url,
        'purchase_id': purchase_id,
    }


def handle_synastrie_webhook(event: Any) -> None:
    """A appeler depuis le webhook Stripe global pour les events kind=synastrie_oneshot."""
    sb = get_admin_client()
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    metadata = data.get('metadata') or {}

    if metadata.get('kind') != 'synastrie_oneshot':
        return  # pas pour nous

    if event_type != 'checkout.session.completed':
        return

    if data.get('payment_status') != 'paid':
        return

    session_id = data.get('id')
    payment_intent = data.get('payment_intent')

    try:
        sb.table('synastrie_purchases').update({
            'status': 'paid',
            'stripe_payment_intent': payment_intent,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }).eq('stripe_session_id', session_id).execute()
        logger.info(f'[synastrie] purchase paid: {session_id}')
    except Exception as e:
        logger.error(f'[synastrie] webhook update: {e}')


def get_synastrie_status(session_id: str) -> Dict[str, Any]:
    sb = get_admin_client()
    try:
        r = sb.table('synastrie_purchases').select(
            'id, status, pdf_path, pdf_generated_at, email_sent_at, person1_data, person2_data, created_at'
        ).eq('stripe_session_id', session_id).maybe_single().execute()
        if r and r.data:
            return r.data
    except Exception as e:
        logger.warning(f'[synastrie] get status: {e}')
    return {'status': 'unknown'}
