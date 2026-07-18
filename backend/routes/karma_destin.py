"""
Route /api/karma-destin : Analyse Karmique téléchargeable (PDF 15 pages).
Endpoints :
  POST /api/karma-destin/checkout   → session Stripe (24€)
  GET  /api/karma-destin/status     → polling PDF ready
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from services.astrology_io_service import karmic_analysis
from services.karma_destin_pdf import generate_karma_destin_pdf
from services.pdf_delivery import update_tx_pdf_metadata, send_pdf_email
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/karma-destin', tags=['karma-destin'])


class KarmaDestinCheckoutPayload(BaseModel):
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
async def karma_destin_checkout(payload: KarmaDestinCheckoutPayload, request: Request):
    """Crée session Stripe pour analyse karmique 24 EUR."""
    settings = get_settings()
    pack = settings.PACKS.get('karma_destin_analysis')
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
    success_url = f'{origin}/karma-destin-pdf/attente?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/karma-destin-pdf'
    
    # Préparer birth_data
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
    
    pdf_ctx = {
        'first_name': (payload.first_name or '').strip(),
        'birth_date_iso': payload.birth_date,
        'birth_data': birth_data,
    }
    
    # BYPASS PROMO
    if payload.promo_code and try_consume_promo(payload.promo_code):
        fake_session_id = f'admin-karma-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'karma_destin_analysis',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'metadata': {'pdf_ctx': pdf_ctx, 'promo_bypass': True},
            }).execute()
            # Générer PDF en arrière-plan
            asyncio.create_task(_generate_and_email_pdf(payload.email, pdf_ctx, fake_session_id))
        except Exception as e:
            logger.exception(f'Erreur promo bypass karma : {e}')
        
        return {
            'session_id': fake_session_id,
            'status': 'completed',
            'message': 'Analyse karmique en cours de génération...',
        }
    
    # CHECKOUT STRIPE
    try:
        checkout_request = CheckoutSessionRequest(
            amount=float(pack['amount']),
            currency=pack['currency'],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'kind': 'karma_destin_analysis',
                'product': 'karma_destin_analysis',
                'email': payload.email,
                'pack_name': pack['name'],
            },
        )
        session = await stripe_checkout.create_checkout_session(checkout_request)
        session_id = session.session_id
        
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session_id,
            'user_email': payload.email,
            'pack_id': 'karma_destin_analysis',
            'amount': pack['amount'],
            'currency': pack['currency'],
            'credits': 0,
            'status': 'pending',
            'payment_status': 'pending',
            'metadata': {'pdf_ctx': pdf_ctx},
        }).execute()
        
        return {
            'session_id': session_id,
            'url': session.url,
            'status': 'pending',
        }
    except Exception as e:
        logger.exception(f'Erreur Stripe karma : {e}')
        raise HTTPException(500, f'Erreur Stripe : {str(e)}')


@router.get('/status')
async def karma_destin_status(session_id: str):
    """Polling pour vérifier si PDF est prêt."""
    try:
        sb = get_admin_client()
        tx = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx or not tx.data:
            raise HTTPException(404, 'Session non trouvée.')
        
        md = tx.data.get('metadata') or {}
        return {
            'status': tx.data.get('status'),
            'payment_status': tx.data.get('payment_status'),
            'pdf_url': md.get('pdf_path'),
            'email_sent': bool(md.get('email_sent_at')),
        }
    except Exception as e:
        logger.exception(f'Erreur status karma : {e}')
        raise HTTPException(500, str(e))


async def _generate_and_email_pdf(email: str, pdf_ctx: dict, session_id: str = ''):
    """Génère le PDF et l'envoie par email."""
    try:
        first_name = pdf_ctx.get('first_name', 'Ami(e)')
        birth_data = pdf_ctx.get('birth_data')
        birth_date_iso = pdf_ctx.get('birth_date_iso')
        
        # Appel API avec language='fr'
        karmic_data = await karmic_analysis(birth_data, first_name, language='fr') or {}
        
        # Générer PDF
        pdf_bytes = generate_karma_destin_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            karmic_data=karmic_data,
        )
        
        # Uploader
        sb = get_admin_client()
        file_name = f'karma_{uuid.uuid4().hex[:12]}.pdf'
        
        sb.storage.from_('reports').upload(
            f'karma/{file_name}',
            pdf_bytes,
            {'content-type': 'application/pdf'},
        )
        
        pdf_url = sb.storage.from_('reports').get_public_url(f'karma/{file_name}')

        # Mettre à jour DB (merge metadata, ciblé par session_id) + email
        update_tx_pdf_metadata(session_id, email, pdf_url, 'karma_destin')
        await send_pdf_email(
            email,
            f'{first_name}, ton Analyse Karmique t\'attend',
            f'''
            <h2>✦ Ton Analyse Karmique & Destinée ✦</h2>
            <p>Chère {first_name},</p>
            <p>Ton rapport karmique est prêt ! <a href="{pdf_url}">Télécharge-le ici</a></p>
            <p>Découvre les leçons de vie que ton âme est venue apprendre.</p>
            <p>Par Solena — La voix de Plume Astrale</p>
            ''',
            'karma_destin',
        )
        
        logger.info(f'PDF karma envoyé à {email}')
    except Exception as e:
        logger.exception(f'Erreur génération PDF karma : {e}')
