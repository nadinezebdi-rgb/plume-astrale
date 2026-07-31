"""
Route /api/theme-natal-oneshot : landing produit Thème Natal 29€ (one-shot Stripe).
Créé 2026-02 dans le cadre de la refonte Gary Vee pricing.

Endpoints :
  POST /api/theme-natal-oneshot/checkout   → session Stripe (29 EUR) ou bypass via promo_code
  GET  /api/theme-natal-oneshot/status     → polling live pour la page succès
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
from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
from middleware.auth import get_optional_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/theme-natal-oneshot', tags=['theme-natal'])


class ThemeNatalCheckoutPayload(BaseModel):
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
async def theme_natal_oneshot_checkout(
    payload: ThemeNatalCheckoutPayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Crée une session Stripe pour le Thème Natal 29 EUR one-shot."""
    settings = get_settings()
    pack = settings.PACKS.get('theme_natal_pdf_oneshot')
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
    success_url = f'{origin}/theme-natal/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/theme-natal'

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
        'birth_data': birth_data,
    }

    # Bypass promo admin
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='theme_natal_pdf_oneshot'
    ):
        fake_session_id = f'admin-natal-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'theme_natal_pdf_oneshot',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'theme_natal_pdf_oneshot',
                    'kind': 'theme_natal_pdf_oneshot',
                    'pdf_ctx': pdf_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[theme_natal_oneshot] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_theme_natal_oneshot_webhook(fake_session_id))
        return {
            'url': f'{origin}/theme-natal/succes?session_id={fake_session_id}',
            'session_id': fake_session_id, 'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'theme_natal_pdf_oneshot',
            'kind': 'theme_natal_pdf_oneshot',
            'email': payload.email,
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'theme_natal_pdf_oneshot',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'theme_natal_pdf_oneshot',
                'kind': 'theme_natal_pdf_oneshot',
                'pdf_ctx': pdf_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[theme_natal_oneshot] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def theme_natal_oneshot_status(session_id: str):
    """Polling live pour /theme-natal/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[theme_natal_oneshot] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if not tx_res or not tx_res.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = tx_res.data
    md = tx.get('metadata') or {}
    from services.self_heal import self_heal_if_paid
    asyncio.create_task(self_heal_if_paid(session_id, bool(md.get('pdf_path')), handle_theme_natal_oneshot_webhook))
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_url': md.get('pdf_path'),
        'email_sent': bool(md.get('email_sent_at')),
        'pdf_ready': bool(md.get('pdf_path')),
        'pdf_status': md.get('pdf_status'),  # 'success' | 'failed' | undefined (en cours)
        'pdf_error': md.get('pdf_error'),
    }
