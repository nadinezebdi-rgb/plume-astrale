"""
Route /api/duo-completion : bundle 2 PDFs (Numérologie + Kabbale) 50€.
Cross-sell post-Thème Natal (2026-02 Gary Vee upsell).
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
from services.duo_completion_service import handle_duo_completion_webhook, get_duo_status
from middleware.auth import get_optional_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/duo-completion', tags=['duo-completion'])


class DuoCheckoutPayload(BaseModel):
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
    # Optionnel : session_id du Thème Natal parent (attribution cross-sell)
    parent_theme_natal_session_id: Optional[str] = None


@router.post('/checkout')
async def duo_completion_checkout(
    payload: DuoCheckoutPayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    settings = get_settings()
    pack = settings.PACKS.get('duo_completion')
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
    success_url = f'{origin}/duo-completion/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/theme-natal/succes'  # revient sur la page où le cross-sell est présenté

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

    # Admin promo bypass
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='duo_completion'
    ):
        fake_session_id = f'admin-duo-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'duo_completion',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'duo_completion',
                    'kind': 'duo_completion',
                    'pdf_ctx': pdf_ctx,
                    'parent_theme_natal_session_id': payload.parent_theme_natal_session_id,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[duo] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_duo_completion_webhook(fake_session_id))
        return {
            'url': f'{origin}/duo-completion/succes?session_id={fake_session_id}',
            'session_id': fake_session_id, 'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'duo_completion',
            'kind': 'duo_completion',
            'email': payload.email,
            'parent_theme_natal_session_id': payload.parent_theme_natal_session_id or '',
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'duo_completion',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'duo_completion',
                'kind': 'duo_completion',
                'pdf_ctx': pdf_ctx,
                'parent_theme_natal_session_id': payload.parent_theme_natal_session_id,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[duo] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def duo_completion_status(session_id: str):
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        status_data = await get_duo_status(session_id)
    except Exception as e:
        logger.warning(f'[duo] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if status_data.get('status') == 'not_found':
        raise HTTPException(404, 'Session introuvable.')
    return status_data


@router.get('/pdf-ctx-for-theme-natal')
async def get_pdf_ctx_from_theme_natal(session_id: str):
    """Récupère le pdf_ctx d'un checkout Thème Natal réussi pour pré-remplir le Duo.
    Permet au cross-sell de fonctionner sans redemander les infos de naissance."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    sb = get_admin_client()
    try:
        r = sb.table('payment_transactions').select('metadata, user_email').eq('session_id', session_id).maybe_single().execute()
    except Exception:
        raise HTTPException(500, 'Impossible de récuperer le contexte.')
    if not r or not r.data:
        raise HTTPException(404, 'Session introuvable.')
    md = r.data.get('metadata') or {}
    pdf_ctx = md.get('pdf_ctx') or {}
    return {
        'email': r.data.get('user_email', ''),
        'first_name': pdf_ctx.get('first_name', ''),
        'birth_date': pdf_ctx.get('birth_date_iso', ''),
        'birth_time': (pdf_ctx.get('birth_data') or {}).get('hour', 0),
        'birth_city': pdf_ctx.get('birth_city') or (pdf_ctx.get('birth_data') or {}).get('city', ''),
        'latitude': (pdf_ctx.get('birth_data') or {}).get('latitude'),
        'longitude': (pdf_ctx.get('birth_data') or {}).get('longitude'),
        'has_context': bool(pdf_ctx.get('birth_data')),
    }
