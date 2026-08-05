"""
Route /api/astrocartographie : landing produit Astrocartographie 49€ (one-shot Stripe).

Endpoints :
  POST /api/astrocartographie/checkout   → session Stripe (49 EUR) ou bypass promo
  GET  /api/astrocartographie/status     → polling live pour la page succès
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from services.astrocartographie_service import handle_astrocartographie_webhook
from middleware.auth import get_optional_user
from integrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/astrocartographie', tags=['astrocartographie'])


@router.get('/cities/search')
async def search_cities(q: str, limit: int = 8):
    """Autocomplete ville pour le picker astrocartographie.
    Retourne [{city, country, country_code, latitude, longitude}] via API v3."""
    from services import astrology_io_service as aio
    q = (q or '').strip()
    if len(q) < 2:
        return {'items': []}
    try:
        items = await aio.search_cities(q, limit=max(1, min(limit, 15)))
    except Exception as e:
        logger.warning(f'[astrocarto] cities search failed for {q!r}: {e}')
        return {'items': []}
    # Normaliser
    out = []
    for it in (items or []):
        if not isinstance(it, dict):
            continue
        lat = it.get('latitude')
        lon = it.get('longitude')
        if lat is None or lon is None:
            continue
        out.append({
            'city': it.get('name') or it.get('city') or '',
            'country': it.get('country_name') or it.get('country') or '',
            'country_code': (it.get('country_code') or '').upper(),
            'latitude': float(lat),
            'longitude': float(lon),
        })
    return {'items': out}


class ChosenCity(BaseModel):
    city: str
    country: str = ''
    country_code: str = 'FR'
    latitude: float
    longitude: float


class AstrocartographieCheckoutPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''    # 'YYYY-MM-DD'
    birth_time: Optional[str] = ''    # 'HH:MM'
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    chosen_cities: List[ChosenCity]   # exactement 3
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/checkout')
async def astrocartographie_checkout(
    payload: AstrocartographieCheckoutPayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    settings = get_settings()
    pack = settings.PACKS.get('astrocartographie')
    if not pack:
        raise HTTPException(500, 'Produit indisponible.')

    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')
    if not payload.birth_date or not payload.birth_time:
        raise HTTPException(400, 'Date et heure de naissance requises.')
    if not payload.chosen_cities or len(payload.chosen_cities) != 3:
        raise HTTPException(400, 'Merci de choisir exactement 3 villes.')

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/astrocartographie/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/astrocartographie'

    # Préparer birth_data (v3 format)
    try:
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = payload.birth_time[:5].split(':')
        birth_data = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
        }
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

    chosen_locations = [c.model_dump() for c in payload.chosen_cities]

    pdf_ctx = {
        'first_name': (payload.first_name or '').strip(),
        'birth_date_iso': payload.birth_date,
        'birth_data': birth_data,
        'chosen_locations': chosen_locations,
    }

    # Bypass promo (admin) OU réduction 15% cross-sell (PLUME15) OU -20€ post-Kabbale (KABBALE20)
    promo = (payload.promo_code or '').strip().upper()

    # Code PLUME15 : 15% de réduction (cross-sell J+7 après Kabbale/Karma)
    # Code KABBALE20 : -20€ absolu (upsell immédiat post-achat Kabbale)
    discount_applied = None
    final_amount = float(pack['amount'])
    if promo == 'PLUME15':
        discount_applied = 0.15
        final_amount = round(float(pack['amount']) * (1 - discount_applied), 2)
    elif promo == 'KABBALE20':
        # Réduction absolue de 20€ (garanti ≥ 5€ pour éviter les cas limites Stripe)
        final_amount = max(5.0, round(float(pack['amount']) - 20.0, 2))
        discount_applied = round(1 - (final_amount / float(pack['amount'])), 4)

    # Bypass 100% — SEC-004 : réservé aux admins authentifiés
    if promo and try_consume_promo(promo, admin_user=current_user, product='astrocartographie'):
        fake_session_id = f'admin-astrocarto-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'astrocartographie',
                'amount': 0.0, 'currency': pack['currency'],
                'credits': 0, 'status': 'completed', 'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'astrocartographie',
                    'kind': 'astrocartographie',
                    'pdf_ctx': pdf_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[astrocarto] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_astrocartographie_webhook(fake_session_id))
        success_url = f'{origin}/astrocartographie/succes?session_id={fake_session_id}'
        return {'url': success_url, 'session_id': fake_session_id, 'admin_bypass': True}

    req = CheckoutSessionRequest(
        amount=final_amount,
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'astrocartographie',
            'kind': 'astrocartographie',
            'email': payload.email,
            'discount_percent': str(int((discount_applied or 0) * 100)),
            'promo_code': promo if discount_applied else '',
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'astrocartographie',
            'amount': final_amount, 'currency': pack['currency'],
            'credits': 0, 'status': 'initiated', 'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'astrocartographie',
                'kind': 'astrocartographie',
                'pdf_ctx': pdf_ctx,
                'original_amount': float(pack['amount']),
                'discount_percent': int((discount_applied or 0) * 100),
                'promo_code': promo if discount_applied else '',
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[astrocarto] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def astrocartographie_status(session_id: str):
    """Polling live pour la page /astrocartographie/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[astrocarto] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de récupérer le statut.')
    if not tx_res or not tx_res.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = tx_res.data
    md = tx.get('metadata') or {}
    from services.self_heal import self_heal_if_paid
    asyncio.create_task(self_heal_if_paid(session_id, bool(md.get('pdf_path')), handle_astrocartographie_webhook))
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_url': md.get('pdf_path'),
        'email_sent': bool(md.get('email_sent_at')),
        'pdf_ready': bool(md.get('pdf_path')),
    }
