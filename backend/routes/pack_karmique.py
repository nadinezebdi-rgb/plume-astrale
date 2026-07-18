"""
Route /api/pack-karmique : produit Pack Karmique + Kabbale 89€ (one-shot Stripe).

Endpoints :
  POST /api/pack-karmique/checkout   → session Stripe (89 EUR) ou bypass promo
  GET  /api/pack-karmique/status     → polling live pour la page succes
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
from services.pack_karmique_service import handle_pack_karmique_webhook
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/pack-karmique', tags=['pack-karmique'])


class PackKarmiqueCheckoutPayload(BaseModel):
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
async def pack_karmique_checkout(payload: PackKarmiqueCheckoutPayload, request: Request):
    """Cree une session Stripe pour le Pack Karmique + Kabbale 89 EUR."""
    settings = get_settings()
    pack = settings.PACKS.get('pack_karmique_kabbale')
    if not pack:
        raise HTTPException(500, 'Produit indisponible.')

    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')
    if not (payload.first_name or '').strip():
        raise HTTPException(400, 'Prénom requis.')
    if not payload.birth_date or not payload.birth_time:
        raise HTTPException(400, 'Date et heure de naissance requises.')

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/pack-karmique/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/pack-karmique'

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

    # BYPASS PROMO — si code valide (ex: ADMIN26), on saute Stripe
    if payload.promo_code and try_consume_promo(payload.promo_code):
        fake_session_id = f'admin-packkarma-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'pack_karmique_kabbale',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'pack_karmique_kabbale',
                    'kind': 'pack_karmique_kabbale',
                    'pdf_ctx': pdf_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[pack_karmique] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_pack_karmique_webhook(fake_session_id))
        success_url = f'{origin}/pack-karmique/succes?session_id={fake_session_id}'
        return {'url': success_url, 'session_id': fake_session_id, 'admin_bypass': True}

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'pack_karmique_kabbale',
            'kind': 'pack_karmique_kabbale',
            'email': payload.email,
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'pack_karmique_kabbale',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'pack_karmique_kabbale',
                'kind': 'pack_karmique_kabbale',
                'pdf_ctx': pdf_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[pack_karmique] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


class ExtraitPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: str
    birth_time: Optional[str] = '12:00'
    birth_city: Optional[str] = 'Paris'
    birth_country: Optional[str] = 'FR'


@router.post('/extrait')
async def pack_karmique_extrait(payload: ExtraitPayload):
    """Lead magnet : extrait gratuit 3 pages du Pack Karmique contre un email."""
    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')
    if not payload.birth_date:
        raise HTTPException(400, 'Date de naissance requise.')
    first_name = (payload.first_name or 'Voyageur').strip() or 'Voyageur'

    try:
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = (payload.birth_time or '12:00')[:5].split(':')
        birth_data = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
            'city': (payload.birth_city or 'Paris').split(',')[0].strip(),
            'country_code': payload.birth_country or 'FR',
        }
    except Exception:
        raise HTTPException(400, 'Format de date invalide (AAAA-MM-JJ).')

    from services import astrology_io_service as aio
    karmic = await aio.karmic_analysis(birth_data, name=first_name, language='fr')
    if not karmic:
        raise HTTPException(502, 'Les astres sont momentanément silencieux — réessaie dans un instant.')

    interps = karmic.get('interpretations') or []
    points = ('Nœud Nord', 'Nœud Sud', 'Noeud Nord', 'Noeud Sud', 'Chiron', 'Lilith', 'Saturne')
    items, seen = [], set()
    for it in interps:
        t = (it.get('title') or '').strip()
        if t in seen:
            continue
        if any(t.startswith(p) for p in points):
            seen.add(t)
            items.append(it)
        if len(items) >= 3:
            break
    if not items:
        items = interps[:3]

    from services.pack_karmique_pdf import generate_extrait_pdf
    pdf_bytes = generate_extrait_pdf(first_name, items)
    from services.pack_karmique_service import ASSETS_DIR
    out_dir = ASSETS_DIR / 'pack_karmique'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'extrait_{uuid.uuid4().hex[:12]}.pdf'
    with open(out_dir / filename, 'wb') as f:
        f.write(pdf_bytes)
    pdf_url = f'/api/assets/pack_karmique/{filename}'

    # Lead best-effort dans oracle_leads (table existante des lead magnets)
    try:
        sb = get_admin_client()
        sb.table('oracle_leads').insert({
            'email': payload.email.strip().lower(),
            'first_name': first_name,
            'birth_date': payload.birth_date[:10],
            'source': 'extrait_karmique',
            'consent_marketing': True,
        }).execute()
    except Exception as e:
        logger.warning(f'[pack_karmique] lead insert failed: {e}')

    asyncio.create_task(_send_extrait_email(payload.email.strip(), first_name, pdf_bytes, filename))
    return {'pdf_url': pdf_url, 'message': 'Ton extrait est prêt — il arrive aussi par email.'}


async def _send_extrait_email(email: str, first_name: str, pdf_bytes: bytes, filename: str) -> None:
    import base64
    import httpx
    import os
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    if not resend_key:
        return
    html = f"""
    <div style="max-width:560px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:36px 24px;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:20px;">✦ Plume Astrale ✦</div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:32px 26px;">
        <h1 style="font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;">{first_name}, voici <em style="color:#D4AF37;">ton extrait offert</em></h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Trois pages de ta mémoire karmique t'attendent en pièce jointe : tes Nœuds Lunaires,
          les cicatrices et promesses de tes vies antérieures.
        </p>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Le document complet — <strong style="color:#D4AF37;">~40 pages</strong> croisant ton analyse karmique
          et ton Arbre de Vie kabbalistique — est disponible dès maintenant.
        </p>
        <div style="text-align:center;margin:26px 0;">
          <a href="https://www.plume-astrale.fr/pack-karmique" style="display:inline-block;background:#D4AF37;color:#111625;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none;">
            Débloquer les 40 pages — 89€ →
          </a>
        </div>
        <p style="text-align:center;font-style:italic;color:#9089B5;font-size:13px;">— Soléna</p>
      </div>
    </div>
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={
                    'from': sender, 'to': [email],
                    'subject': f'{first_name}, ton extrait karmique offert ✦',
                    'html': html,
                    'attachments': [{'filename': filename, 'content': base64.b64encode(pdf_bytes).decode('ascii')}],
                },
            )
            if r.status_code >= 400:
                logger.warning(f'[pack_karmique] extrait email {r.status_code}: {r.text[:150]}')
    except Exception as e:
        logger.warning(f'[pack_karmique] extrait email failed: {e}')


@router.get('/status')
async def pack_karmique_status(session_id: str):
    """Polling live pour la page /pack-karmique/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[pack_karmique] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if not tx_res or not tx_res.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = tx_res.data
    md = tx.get('metadata') or {}
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_url': md.get('pdf_path'),
        'email_sent': bool(md.get('email_sent_at')),
        'pdf_ready': bool(md.get('pdf_path')),
    }
