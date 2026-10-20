"""routes/natal_lulu_bump.py — Routes pour le bump "Livre relié Lulu" 79 €
================================================================================

Endpoints publics :
  POST /api/natal-print-bump/quote      → devis Lulu live pour une destination
  POST /api/natal-print-bump/checkout   → crée session Stripe (avec devis + adresse)
  POST /api/natal-print-bump/webhook    → confirmation de retour Lulu (status change)

Endpoint admin :
  GET  /api/natal-print-bump/admin/orders → liste des commandes bump

Le webhook Stripe principal (`/api/stripe/webhook`) détecte
metadata.kind='natal_lulu_bump' et appelle `handle_bump_webhook`.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, EmailStr

from routes.admin import require_admin
from services.lulu_client import quote_print_job, verify_webhook_signature
from services.natal_lulu_bump_service import (
    BASE_PRICE_FR_EUR, compute_client_price_eur, create_bump_checkout,
    handle_bump_webhook,
)

router = APIRouter(prefix='/natal-print-bump', tags=['natal-print-bump'])
logger = logging.getLogger(__name__)


# ─── Pydantic models ────────────────────────────────────────────────
class LuluAddress(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    street1: str = Field(..., min_length=3, max_length=100)
    street2: Optional[str] = Field(None, max_length=80)
    city: str = Field(..., min_length=1, max_length=60)
    state_code: Optional[str] = Field(None, max_length=16)
    postcode: str = Field(..., min_length=2, max_length=16)
    country_code: str = Field(..., min_length=2, max_length=2)
    phone_number: str = Field(..., min_length=4, max_length=30)


class QuoteRequest(BaseModel):
    address: LuluAddress
    page_count: int = Field(42, ge=24, le=800)


class CheckoutRequest(BaseModel):
    source_session_id: str = Field(..., min_length=4, max_length=200)
    purchaser_email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=60)
    birth_date_iso: str = Field(..., min_length=10, max_length=10)
    address: LuluAddress


# ─── Routes ────────────────────────────────────────────────────────
@router.post('/quote')
async def route_quote(req: QuoteRequest):
    """Devis Lulu live pour une destination donnée. Retourne prix client EUR TTC."""
    try:
        quote = await quote_print_job(req.address.model_dump(), page_count=req.page_count)
    except Exception as e:
        logger.exception('[natal_lulu_bump] quote failed')
        raise HTTPException(status_code=502, detail=f'Devis indisponible : {e}')
    client_price = compute_client_price_eur(quote)
    return {
        'client_price_eur': client_price,
        'currency': 'EUR',
        'base_price_fr_eur': BASE_PRICE_FR_EUR,
        'quote': quote,
    }


@router.post('/checkout')
async def route_checkout(req: CheckoutRequest, request: Request):
    """Crée une session Stripe pour l'achat du livre relié bump."""
    origin = (
        request.headers.get('origin')
        or request.headers.get('referer', '').rstrip('/').rsplit('/', 1)[0]
        or 'https://plume-astrale.fr'
    ).rstrip('/')
    try:
        out = await create_bump_checkout(
            purchaser_email=req.purchaser_email,
            first_name=req.first_name,
            birth_date_iso=req.birth_date_iso,
            source_session_id=req.source_session_id,
            address=req.address.model_dump(),
            origin=origin,
        )
    except Exception as e:
        logger.exception('[natal_lulu_bump] checkout failed')
        raise HTTPException(status_code=500, detail=f'Création checkout impossible : {e}')
    return out


@router.post('/webhook')
async def route_lulu_webhook(request: Request):
    """Webhook Lulu `PRINT_JOB_STATUS_CHANGED`. Vérifie HMAC puis traite tracking."""
    raw = await request.body()
    hmac_header = request.headers.get('Lulu-HMAC-SHA256') or request.headers.get('lulu-hmac-sha256')
    if not verify_webhook_signature(raw, hmac_header):
        raise HTTPException(status_code=401, detail='Signature Lulu invalide')
    try:
        import json as _json
        event = _json.loads(raw.decode())
    except Exception:
        raise HTTPException(status_code=400, detail='Payload JSON invalide')
    # Traitement minimal : log + extraction tracking.
    # L'envoi d'email tracking est fait dans un prochain commit — ici on
    # journalise simplement pour que l'admin puisse voir le statut.
    data = (event.get('data') or {})
    status = (data.get('status') or {}).get('name') if isinstance(data.get('status'), dict) else data.get('status')
    logger.info(f'[lulu_webhook] event={event.get("topic")} status={status} external_id={data.get("external_id")}')
    return {'ok': True}


@router.get('/admin/orders')
async def route_admin_orders(
    limit: int = 100,
    status: Optional[str] = None,
    _admin: dict = Depends(require_admin),
):
    """Liste des commandes bump pour l admin, filtre optionnel par status.

    status attendus : 'initiated' (payé en attente), 'fulfilled' (print job envoyé),
    'cancelled', 'failed'. Sans filtre : toutes les commandes.
    """
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    try:
        q = sb.table('payment_transactions').select(
            'stripe_session_id, email, amount_cents, status, fulfilled_at, created_at, metadata'
        ).eq('kind', 'natal_lulu_bump')
        if status:
            q = q.eq('status', status)
        r = q.order('created_at', desc=True).limit(max(1, min(limit, 500))).execute()
        rows = r.data or []
        # Normalise pour le frontend : extrait tracking + lulu_job + address si présent
        orders = []
        for row in rows:
            md = row.get('metadata') or {}
            lulu_job = (md.get('lulu_job') or {}) if isinstance(md.get('lulu_job'), dict) else {}
            lulu_status = ((lulu_job.get('status') or {}).get('name')
                           if isinstance(lulu_job.get('status'), dict) else lulu_job.get('status'))
            addr = md.get('address') or {}
            tracking_urls = []
            for li in (lulu_job.get('line_items') or []):
                tracking_urls += (li.get('tracking_urls') or [])
            orders.append({
                'session_id': row.get('stripe_session_id'),
                'email': row.get('email'),
                'amount_eur': round((row.get('amount_cents') or 0) / 100.0, 2),
                'status': row.get('status'),
                'lulu_status': lulu_status,
                'tracking_urls': tracking_urls,
                'first_name': md.get('first_name'),
                'country': addr.get('country_code'),
                'city': addr.get('city'),
                'quote_mocked': md.get('quote', {}).get('mock') if isinstance(md.get('quote'), dict) else None,
                'created_at': row.get('created_at'),
                'fulfilled_at': row.get('fulfilled_at'),
            })
        return {'orders': orders, 'count': len(orders), 'filter_status': status or 'all'}
    except Exception as e:
        logger.exception('[natal_lulu_bump] admin list failed')
        raise HTTPException(status_code=500, detail=str(e))
