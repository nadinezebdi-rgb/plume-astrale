"""
Route /api/numerologie : Rapport numérologique téléchargeable (PDF 12 pages).
Endpoints :
  POST /api/numerologie/checkout   → session Stripe (19€) pour numérologie
  GET  /api/numerologie/status     → polling PDF ready
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
from services.astrology_io_service import numerology_name, numerology_personal_year, numerology_forecast
from services.numerologie_pdf import generate_numerologie_pdf
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/numerologie', tags=['numerologie'])


class NumerologieCheckoutPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''   # 'YYYY-MM-DD'
    birth_time: Optional[str] = ''   # 'HH:MM'
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/checkout')
async def numerologie_checkout(payload: NumerologieCheckoutPayload, request: Request):
    """Crée une session Stripe pour le rapport numérologique 19 EUR."""
    settings = get_settings()
    pack = settings.PACKS.get('numerologie_code')
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
    success_url = f'{origin}/numerologie/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/numerologie'
    
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
        fake_session_id = f'admin-numerologie-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'numerologie_code',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'metadata': {'pdf_ctx': pdf_ctx, 'promo_bypass': True},
            })
            # Generer PDF en arrière-plan
            asyncio.create_task(_generate_and_email_pdf(payload.email, pdf_ctx))
        except Exception as e:
            logger.exception(f'Erreur promo bypass numerologie : {e}')
        
        return {
            'session_id': fake_session_id,
            'status': 'completed',
            'message': 'Rapport numérologique en cours de génération...',
        }
    
    # CHECKOUT STRIPE NORMAL
    try:
        checkout_request = CheckoutSessionRequest(
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=payload.email,
            line_items=[{
                'price_data': {
                    'currency': pack['currency'].lower(),
                    'product_data': {
                        'name': pack['name'],
                        'description': 'Ton Code Numérologique — 12 pages',
                    },
                    'unit_amount': int(pack['amount'] * 100),
                },
                'quantity': 1,
            }],
        )
        session = stripe_checkout.create_checkout_session(checkout_request)
        session_id = session.get('id')
        
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session_id,
            'user_email': payload.email,
            'pack_id': 'numerologie_code',
            'amount': pack['amount'],
            'currency': pack['currency'],
            'credits': 0,
            'status': 'pending',
            'payment_status': 'pending',
            'metadata': {'pdf_ctx': pdf_ctx},
        })
        
        return {
            'session_id': session_id,
            'url': session.get('url'),
            'status': 'pending',
        }
    except Exception as e:
        logger.exception(f'Erreur Stripe numerologie : {e}')
        raise HTTPException(500, f'Erreur Stripe : {str(e)}')


@router.get('/status')
async def numerologie_status(session_id: str):
    """Polling pour vérifier si PDF est prêt."""
    try:
        sb = get_admin_client()
        tx = sb.table('payment_transactions').select('*').eq('session_id', session_id).single().execute()
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
        logger.exception(f'Erreur status numerologie : {e}')
        raise HTTPException(500, str(e))


async def _generate_and_email_pdf(email: str, pdf_ctx: dict):
    """Génère le PDF et l'envoie par email."""
    try:
        # Récupérer données API
        first_name = pdf_ctx.get('first_name', 'Ami(e)')
        birth_data = pdf_ctx.get('birth_data')
        birth_date_iso = pdf_ctx.get('birth_date_iso')
        
        # Appels API (avec language='fr' partout!)
        numerology_data = await numerology_name(first_name, language='fr') or {}
        personal_year_data = await numerology_personal_year(birth_data, first_name, language='fr') or {}
        forecast_data = await numerology_forecast(birth_data, first_name, language='fr') or {}
        
        # Générer PDF
        pdf_bytes = generate_numerologie_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            numerology_data=numerology_data,
            personal_year_data=personal_year_data,
            forecast_data=forecast_data,
        )
        
        # Uploader sur Supabase Storage (ou AWS S3)
        sb = get_admin_client()
        file_name = f'numerologie_{uuid.uuid4().hex[:12]}.pdf'
        
        # Store in Supabase
        sb.storage.from_('reports').upload(
            f'numerologie/{file_name}',
            pdf_bytes,
            {'content-type': 'application/pdf'},
        )
        
        pdf_url = sb.storage.from_('reports').get_public_url(f'numerologie/{file_name}')
        
        # Mettre à jour DB + envoyer email
        sb.table('payment_transactions').update({
            'metadata': {'pdf_path': pdf_url, 'email_sent_at': 'now()'},
        }).eq('user_email', email).execute()
        
        # Email avec Resend
        from resend import Resend
        resend = Resend(api_key=get_settings().RESEND_API_KEY)
        resend.emails.send({
            'from': 'no-reply@plumeastrale.fr',
            'to': email,
            'subject': f'{first_name}, ton Code Numérologique t\'attend',
            'html': f'''
            <h2>✦ Ton Code Numérologique ✦</h2>
            <p>Chère {first_name},</p>
            <p>Ton rapport numérologique est prêt ! <a href="{pdf_url}">Télécharge-le ici</a></p>
            <p>Découvre tes nombres de destin, d'expression et de cœur.</p>
            <p>Par Solena — La voix de Plume Astrale</p>
            ''',
        })
        
        logger.info(f'PDF numérologie envoyé à {email}')
    except Exception as e:
        logger.exception(f'Erreur génération PDF numerologie : {e}')
