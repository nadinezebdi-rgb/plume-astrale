"""Route /api/edition-reliee — checkout Stripe 149 € + polling post-paiement.

Endpoints :
  POST /api/edition-reliee/checkout → session Stripe (149 EUR)
  GET  /api/edition-reliee/status   → polling live pour /edition-reliee/merci
"""
from __future__ import annotations
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from services.edition_reliee_service import create_edition_reliee_checkout
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/edition-reliee', tags=['edition-reliee'])


class CheckoutPayload(BaseModel):
    purchaser_email: EmailStr
    purchaser_first_name: str = Field(min_length=1, max_length=80)
    recipient_first_name: str = Field(min_length=1, max_length=80)
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    birth_time: str = Field(pattern=r'^\d{2}:\d{2}$')
    birth_city: str = Field(min_length=2, max_length=120)
    birth_country: Optional[str] = Field(default='FR', max_length=4)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    dedication: Optional[str] = Field(default=None, max_length=800)
    origin_url: str = Field(min_length=8, max_length=200)


@router.post('/checkout')
async def edition_reliee_checkout(payload: CheckoutPayload, request: Request):
    """Crée une session Stripe pour l'Édition Reliée 149 €."""
    try:
        result = await create_edition_reliee_checkout(
            purchaser_email=payload.purchaser_email.lower(),
            purchaser_first_name=payload.purchaser_first_name.strip(),
            recipient_first_name=payload.recipient_first_name.strip(),
            birth_date_iso=payload.birth_date,
            birth_time=payload.birth_time,
            birth_city=payload.birth_city.strip(),
            birth_country=(payload.birth_country or 'FR').upper(),
            latitude=payload.latitude,
            longitude=payload.longitude,
            dedication=(payload.dedication or '').strip() or None,
            origin=payload.origin_url,
        )
        return {'success': True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f'[edition_reliee] checkout failed: {e}')
        raise HTTPException(status_code=500, detail='Erreur lors de la création du paiement.')


@router.get('/status')
async def edition_reliee_status(session_id: str):
    """Polling léger pour /edition-reliee/merci — indique où en est la génération."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        r = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[edition_reliee] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de récupérer le statut.')
    if not r or not r.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = r.data
    md = tx.get('metadata') or {}
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_ready': bool(md.get('pdf_path')),
        'pdf_status': md.get('pdf_status'),
        'print_approval_id': md.get('print_approval_id'),
        'deadline_at': md.get('print_approval_deadline_at'),
        'email_sent': bool(md.get('print_approval_id')),
    }
