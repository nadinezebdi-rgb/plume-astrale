"""
Route /api/consultation-ultime : hyperpremium anchor 149€ (Thème Natal 40p + chat
illimité 24h + lecture personnalisée par Soléna).

Ce pack déclenche une orchestration manuelle : après paiement, un email est
envoyé à Soléna pour qu'elle prépare la lecture personnalisée. Le PDF Thème
Natal est généré automatiquement via le pipeline theme_natal_oneshot.
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
from middleware.auth import get_optional_user
from integrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/consultation-ultime', tags=['consultation-ultime'])


class ConsultationUltimeCheckoutPayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_time: Optional[str] = ''
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = ''
    question: Optional[str] = ''
    origin_url: str
    promo_code: Optional[str] = None


async def handle_consultation_ultime_webhook(session_id: str) -> None:
    """Traite le paiement Consultation Ultime : génère le PDF + alerte Soléna."""
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[consultation_ultime] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'consultation_ultime':
        return

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    if md.get('consultation_dispatched_at'):
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    if not email or not pdf_ctx:
        return

    # 1) Crée un enfant Thème Natal (auto PDF via handler existant)
    child_sid = f'consultation-natal-{uuid.uuid4().hex[:16]}'
    try:
        sb.table('payment_transactions').insert({
            'session_id': child_sid,
            'user_email': email,
            'pack_id': 'theme_natal_pdf_oneshot',
            'amount': 0.0,
            'currency': 'eur',
            'credits': 0,
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
            'metadata': {
                'kind': 'theme_natal_pdf_oneshot',
                'product': 'theme_natal_pdf_oneshot',
                'pdf_ctx': pdf_ctx,
                'consultation_parent_session_id': session_id,
            },
        }).execute()
        asyncio.create_task(handle_theme_natal_oneshot_webhook(child_sid))
    except Exception as e:
        logger.warning(f"[consultation_ultime] child natal insert failed: {e}")

    # 2) Alerte email à Soléna (admin)
    try:
        import os, httpx
        api_key = os.environ.get('RESEND_API_KEY', '').strip()
        solena_email = os.environ.get('SOLENA_ADMIN_EMAIL', 'contact@plume-astrale.fr').strip()
        sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
        if api_key:
            html = f"""
            <div style="font-family:Georgia,serif;background:#111625;color:#F5EEE0;padding:32px;">
              <h2 style="color:#D4AF37;">✦ Nouvelle Consultation Ultime commandée ✦</h2>
              <p><b>Client :</b> {pdf_ctx.get('first_name','')} — {email}</p>
              <p><b>Téléphone :</b> {md.get('phone','—')}</p>
              <p><b>Date naiss. :</b> {pdf_ctx.get('birth_date_iso','')} à {pdf_ctx.get('birth_time','')} — {pdf_ctx.get('birth_city','')} ({pdf_ctx.get('birth_country','')})</p>
              <p><b>Question :</b> {md.get('question') or '—'}</p>
              <p><b>Session :</b> {session_id}</p>
              <hr/>
              <p style="color:#9089B5;">Action requise : prépare la lecture personnalisée enregistrée + le chat illimité 24h dans les 48h. Le PDF Thème Natal a été envoyé automatiquement au client.</p>
            </div>
            """
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(
                    'https://api.resend.com/emails',
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                    json={'from': sender, 'to': [solena_email],
                          'subject': f'✦ Consultation Ultime · {pdf_ctx.get("first_name","client")} ({email})',
                          'html': html},
                )
    except Exception as e:
        logger.warning(f"[consultation_ultime] admin alert email failed: {e}")

    md['consultation_dispatched_at'] = datetime.now(timezone.utc).isoformat()
    md['consultation_child_natal_sid'] = child_sid
    sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    logger.info(f"[consultation_ultime] dispatched pour {email} (session {session_id})")


@router.post('/checkout')
async def consultation_ultime_checkout(
    payload: ConsultationUltimeCheckoutPayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    settings = get_settings()
    pack = settings.PACKS.get('consultation_ultime')
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
    success_url = f'{origin}/consultation-ultime/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/consultation-ultime'

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

    common_meta = {
        'product': 'consultation_ultime',
        'kind': 'consultation_ultime',
        'pdf_ctx': pdf_ctx,
        'phone': payload.phone or '',
        'question': payload.question or '',
    }

    # Admin promo bypass
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='consultation_ultime'
    ):
        fake_session_id = f'admin-consultation-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'consultation_ultime',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {**common_meta, 'admin_bypass': True, 'promo_code': payload.promo_code.strip().upper()},
            }).execute()
        except Exception as e:
            logger.warning(f'[consultation_ultime] admin bypass tx insert failed: {e}')

        asyncio.create_task(handle_consultation_ultime_webhook(fake_session_id))
        return {
            'url': f'{origin}/consultation-ultime/succes?session_id={fake_session_id}',
            'session_id': fake_session_id, 'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'product': 'consultation_ultime', 'kind': 'consultation_ultime', 'email': payload.email},
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'consultation_ultime',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': common_meta,
        }).execute()
    except Exception as e:
        logger.warning(f'[consultation_ultime] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def consultation_ultime_status(session_id: str):
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    sb = get_admin_client()
    try:
        r = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        raise HTTPException(500, f'Erreur : {e}')
    if not r or not r.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = r.data
    md = tx.get('metadata') or {}
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'dispatched': bool(md.get('consultation_dispatched_at')),
        'solena_notified': bool(md.get('consultation_dispatched_at')),
    }
