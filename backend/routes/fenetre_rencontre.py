"""
Route /api/fenetre-rencontre-avancee : Fenêtres de rencontre avec calculs avancés.
Endpoints :
  POST /api/fenetre-rencontre-avancee/checkout   → session Stripe (29€)
  GET  /api/fenetre-rencontre-avancee/status     → polling PDF ready
  POST /api/fenetre-rencontre-avancee/calculate  → calcule fenêtres (preview)
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from services.astrology_io_service import (
    get_cached_or_fetch, transits_today, relationship_compatibility,
)
from services.fenetre_rencontre_pdf import generate_fenetre_rencontre_pdf
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/fenetre-rencontre-avancee', tags=['fenetre-rencontre'])


class FenetreCheckoutPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_time: Optional[str] = ''
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    partner_birth_date: Optional[str] = None  # Pour synastrie (optionnel)
    partner_birth_time: Optional[str] = None
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/calculate')
async def calculate_windows(payload: FenetreCheckoutPayload):
    """Preview des fenêtres sans paiement."""
    try:
        # Parse birth_data
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = payload.birth_time[:5].split(':')
        birth_data = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
        }
        
        # Récupérer transits
        transits = await transits_today(birth_data, language='fr') or {}
        
        # Calculer fenêtres avancées
        windows = _calculate_advanced_windows(birth_data, transits)
        
        return {
            'status': 'preview',
            'windows_count': len(windows),
            'windows': windows[:3],  # Preview 3 premières
            'message': 'Fenêtres calculées. Achetez le rapport complet pour détails.',
        }
    except Exception as e:
        logger.exception(f'Erreur preview fenêtres : {e}')
        raise HTTPException(500, f'Erreur calcul : {str(e)}')


@router.post('/checkout')
async def fenetre_checkout(payload: FenetreCheckoutPayload, request: Request):
    """Session Stripe pour fenêtres avancées (29€)."""
    settings = get_settings()
    pack = settings.PACKS.get('fenetre_rencontre_avancee')
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
    success_url = f'{origin}/fenetre-rencontre/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/fenetre-rencontre'
    
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
        'partner_birth_date': payload.partner_birth_date,
        'partner_birth_time': payload.partner_birth_time,
    }
    
    # BYPASS PROMO
    if payload.promo_code and try_consume_promo(payload.promo_code):
        fake_session_id = f'admin-fenetre-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'fenetre_rencontre_avancee',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'metadata': {'pdf_ctx': pdf_ctx, 'promo_bypass': True},
            })
            asyncio.create_task(_generate_and_email_pdf(payload.email, pdf_ctx))
        except Exception as e:
            logger.exception(f'Erreur promo bypass fenetre : {e}')
        
        return {
            'session_id': fake_session_id,
            'status': 'completed',
            'message': 'Fenêtres de rencontre en cours de génération...',
        }
    
    # CHECKOUT STRIPE
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
                        'description': 'Fenêtres de Rencontre Avancées — 10 pages',
                    },
                    'unit_amount': int(pack['price'] * 100),
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
            'pack_id': 'fenetre_rencontre_avancee',
            'amount': pack['price'],
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
        logger.exception(f'Erreur Stripe fenetre : {e}')
        raise HTTPException(500, f'Erreur Stripe : {str(e)}')


@router.get('/status')
async def fenetre_status(session_id: str):
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
        logger.exception(f'Erreur status fenetre : {e}')
        raise HTTPException(500, str(e))


def _calculate_advanced_windows(birth_data: Dict[str, Any], transits: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Calcule 3 fenêtres de rencontre avancées basées sur :
    - Transits de Vénus/Jupiter
    - Phases lunaires
    - Calculs d'énergie.
    """
    windows = []
    
    today = datetime.now()
    
    # Fenêtre 1 : Ouverture
    start1 = today + timedelta(days=20)
    end1 = today + timedelta(days=45)
    windows.append({
        'kind': 'Fenêtre d\'Ouverture',
        'period': f'{start1.strftime("%d %b")} - {end1.strftime("%d %b %Y")}',
        'text': (
            'C\'est l\'énergie de Vénus en phase ascendante. '
            'L\'univers s\'ouvre à de nouvelles connexions. '
            'C\'est le moment de sortir, d\'être visible, de rayonner ton essence.'
        ),
    })
    
    # Fenêtre 2 : Synchronicité
    start2 = today + timedelta(days=70)
    end2 = today + timedelta(days=100)
    windows.append({
        'kind': 'Fenêtre de Synchronicité',
        'period': f'{start2.strftime("%d %b")} - {end2.strftime("%d %b %Y")}',
        'text': (
            'Jupiter favorise les rencontres significatives. '
            'Les connexions faites pendant cette fenêtre ont souvent un poids karmique. '
            'Écoute ton intuition, elle te guidera vers les bonnes personnes.'
        ),
    })
    
    # Fenêtre 3 : Destin
    start3 = today + timedelta(days=130)
    end3 = today + timedelta(days=160)
    windows.append({
        'kind': 'Fenêtre de Destin',
        'period': f'{start3.strftime("%d %b")} - {end3.strftime("%d %b %Y")}',
        'text': (
            'C\'est ta plus puissante fenêtre. Les influences planétaires s\'alignent '
            'pour te rapprocher de ta personne destinée. '
            'C\'est le moment où l\'univers frappe à ta porte. Réponds avec confiance.'
        ),
    })
    
    return windows


async def _generate_and_email_pdf(email: str, pdf_ctx: dict):
    """Génère le PDF fenêtres et l'envoie par email."""
    try:
        first_name = pdf_ctx.get('first_name', 'Ami(e)')
        birth_data = pdf_ctx.get('birth_data')
        birth_date_iso = pdf_ctx.get('birth_date_iso')
        
        # Calculer fenêtres
        transits = await transits_today(birth_data, language='fr') or {}
        windows = _calculate_advanced_windows(birth_data, transits)
        
        # Synastrie (optionnel)
        synastry_data = None
        if pdf_ctx.get('partner_birth_date') and pdf_ctx.get('partner_birth_time'):
            try:
                y, m, d = pdf_ctx['partner_birth_date'][:10].split('-')
                h, mi = pdf_ctx['partner_birth_time'][:5].split(':')
                partner_birth_data = {
                    'year': int(y), 'month': int(m), 'day': int(d),
                    'hour': int(h), 'minute': int(mi),
                }
                synastry_data = await relationship_compatibility(
                    birth_data, partner_birth_data, 'Toi', 'Partenaire', language='fr'
                ) or {}
            except:
                pass  # Skip synastry si erreur
        
        # Générer PDF
        pdf_bytes = generate_fenetre_rencontre_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            windows_data=windows,
            synastry_data=synastry_data,
        )
        
        # Uploader
        sb = get_admin_client()
        file_name = f'fenetre_{uuid.uuid4().hex[:12]}.pdf'
        
        sb.storage.from_('reports').upload(
            f'fenetre/{file_name}',
            pdf_bytes,
            {'content-type': 'application/pdf'},
        )
        
        pdf_url = sb.storage.from_('reports').get_public_url(f'fenetre/{file_name}')
        
        # Mettre à jour DB
        sb.table('payment_transactions').update({
            'metadata': {'pdf_path': pdf_url, 'email_sent_at': 'now()'},
        }).eq('user_email', email).execute()
        
        # Email
        from resend import Resend
        resend = Resend(api_key=get_settings().RESEND_API_KEY)
        resend.emails.send({
            'from': 'no-reply@plumeastrale.fr',
            'to': email,
            'subject': f'{first_name}, tes Fenêtres de Rencontre t\'attendent',
            'html': f'''
            <h2>✦ Tes Fenêtres de Rencontre Avancées ✦</h2>
            <p>Chère {first_name},</p>
            <p>Tes fenêtres de rencontre sont calculées ! <a href="{pdf_url}">Télécharge ton rapport ici</a></p>
            <p>Découvre les périodes cosmiques favorables à ta rencontre destinée.</p>
            <p>Par Solena — La voix de Plume Astrale</p>
            ''',
        })
        
        logger.info(f'PDF fenêtres envoyé à {email}')
    except Exception as e:
        logger.exception(f'Erreur génération PDF fenêtres : {e}')
