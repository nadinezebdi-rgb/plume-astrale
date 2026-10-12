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
async def route_admin_orders(limit: int = 50):
    """Liste simplifiée des commandes bump pour l'admin.

    Pas de require_admin ici pour simplifier le mock — à ajouter avant la prod.
    """
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    try:
        r = sb.table('payment_transactions').select(
            'stripe_session_id, email, amount_cents, status, fulfilled_at, created_at, metadata'
        ).eq('kind', 'natal_lulu_bump').order('created_at', desc=True).limit(limit).execute()
        return {'orders': r.data or []}
    except Exception as e:
        logger.exception('[natal_lulu_bump] admin list failed')
        raise HTTPException(status_code=500, detail=str(e))
