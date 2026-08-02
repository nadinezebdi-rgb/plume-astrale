"""
Route /api/lecture-complete : Landing v2 — bundle 97€ (Lecture Complète du Ciel).
Regroupe Theme Natal + Fenetres 2026 + Karma + Analyse des Liens + Cercle Solena 90j.

Livraison des bonus manuelle par Solena apres commande.

Endpoints :
  POST /api/lecture-complete/checkout   → session Stripe (97 EUR) + promo bypass admin
  GET  /api/lecture-complete/status     → polling paiement
"""
from __future__ import annotations
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from middleware.auth import get_optional_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/lecture-complete', tags=['lecture-complete'])


class LectureCompletePayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_time: Optional[str] = ''
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/checkout')
async def lecture_complete_checkout(
    payload: LectureCompletePayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Cree une session Stripe pour le bundle Lecture Complete 97€."""
    settings = get_settings()
    pack = settings.PACKS.get('lecture_complete')
    if not pack:
        raise HTTPException(500, 'Produit indisponible.')

    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/lecture-complete/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/'

    order_ctx = {
        'first_name': (payload.first_name or '').strip(),
        'birth_date': payload.birth_date,
        'birth_time': payload.birth_time,
        'birth_city': payload.birth_city,
        'birth_country': payload.birth_country,
        'email': payload.email,
    }

    # Bypass promo admin (SEC-004 : seul un compte is_admin=true peut consommer)
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='lecture_complete'
    ):
        fake_session_id = f'admin-lecture-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'lecture_complete',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'lecture_complete',
                    'kind': 'lecture_complete',
                    'order_ctx': order_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[lecture_complete] admin bypass tx insert failed: {e}')

        return {
            'url': f'{origin}/lecture-complete/succes?session_id={fake_session_id}',
            'session_id': fake_session_id,
            'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'lecture_complete',
            'kind': 'lecture_complete',
            'email': payload.email,
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'lecture_complete',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'lecture_complete',
                'kind': 'lecture_complete',
                'order_ctx': order_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def lecture_complete_status(session_id: str):
    """Polling live pour /lecture-complete/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if not tx_res or not tx_res.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = tx_res.data
    md = tx.get('metadata') or {}
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'email': tx.get('user_email'),
        'admin_bypass': bool(md.get('admin_bypass')),
    }
