"""
Route /api/trio-decouverte : bundle 3 PDFs (Thème Natal + Numérologie + Kabbale) 79€.
Créé 2026-02 dans le cadre de la refonte Gary Vee (économie 12€ vs achats séparés).
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from services.trio_decouverte_service import handle_trio_decouverte_webhook, get_trio_status
from middleware.auth import get_optional_user
from integrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/trio-decouverte', tags=['trio-decouverte'])


class TrioCheckoutPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_time: Optional[str] = ''
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/checkout')
async def trio_decouverte_checkout(
    payload: TrioCheckoutPayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Crée une session Stripe pour le Trio Découverte 79 EUR."""
    settings = get_settings()
    pack = settings.PACKS.get('trio_decouverte')
    if not pack:
        raise HTTPException(500, 'Produit indisponible.')

    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')
    if not payload.birth_date or not payload.birth_time:
        raise HTTPException(400, 'Date et heure de naissance requises.')

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/trio-decouverte/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/trio-decouverte'

    # Prépare birth_data v3
    try:
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = payload.birth_time[:5].split(':')
        birth_data = {'year': int(y), 'month': int(m), 'day': int(d), 'hour': int(h), 'minute': int(mi)}
        if payload.latitude is not None:
            birth_data['latitude'] = float(payload.latitude)
        if payload.longitude is not None:
            birth_data['longitude'] = float(payload.longitude)
        if payload.birth_city:
            birth_data['city'] = payload.birth_city
        if payload.birth_country:
            birth_data['country_code'] = payload.birth_country
    except Exception as e:
        raise HTTPException(400, f'Format date/heure invalide : {e}')

    pdf_ctx = {
        'first_name': (payload.first_name or '').strip(),
        'birth_date_iso': payload.birth_date,
        'birth_time': payload.birth_time,
        'birth_city': payload.birth_city,
        'birth_country': payload.birth_country,
        'birth_data': birth_data,
    }

    # Bypass promo admin
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='trio_decouverte'
    ):
        fake_session_id = f'admin-trio-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'trio_decouverte',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'trio_decouverte',
                    'kind': 'trio_decouverte',
                    'pdf_ctx': pdf_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[trio] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_trio_decouverte_webhook(fake_session_id))
        return {
            'url': f'{origin}/trio-decouverte/succes?session_id={fake_session_id}',
            'session_id': fake_session_id, 'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'trio_decouverte',
            'kind': 'trio_decouverte',
            'email': payload.email,
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'trio_decouverte',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'trio_decouverte',
                'kind': 'trio_decouverte',
                'pdf_ctx': pdf_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[trio] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def trio_decouverte_status(session_id: str):
    """Polling live pour /trio-decouverte/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        status_data = await get_trio_status(session_id)
    except Exception as e:
        logger.warning(f'[trio] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if status_data.get('status') == 'not_found':
        raise HTTPException(404, 'Session introuvable.')
    return status_data
