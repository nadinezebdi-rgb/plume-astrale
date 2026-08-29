"""Route /api/edition-reliee — checkout Stripe 149 € + polling post-paiement.

Endpoints :
  POST /api/edition-reliee/checkout → session Stripe (149 EUR)
  GET  /api/edition-reliee/status   → polling live pour /edition-reliee/merci
"""
from __future__ import annotations
import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from services.edition_reliee_service import create_edition_reliee_checkout
from services.edition_reliee_service import handle_edition_reliee_webhook
from services.supabase_client import get_admin_client
from services.self_heal import self_heal_if_paid

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/edition-reliee', tags=['edition-reliee'])


class CheckoutPayload(BaseModel):
    purchaser_email: EmailStr
    purchaser_first_name: str = Field(min_length=1, max_length=80)
    recipient_first_name: str = Field(min_length=1, max_length=80)
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    # §V audit marque Feb 2026 : heure OPTIONNELLE ; sans elle,
    # PDF sortira en "Édition des Planètes" (skip ascendant + maisons).
    birth_time: Optional[str] = Field(default=None, pattern=r'^\d{2}:\d{2}$')
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
        # §V audit marque : détecte heure absente ou défaut 12:00 suspect
        no_birth_time = not payload.birth_time or payload.birth_time.strip() in ('', '12:00', '12:00:00')
        birth_time_effective = payload.birth_time or '12:00'
        result = await create_edition_reliee_checkout(
            purchaser_email=payload.purchaser_email.lower(),
            purchaser_first_name=payload.purchaser_first_name.strip(),
            recipient_first_name=payload.recipient_first_name.strip(),
            birth_date_iso=payload.birth_date,
            birth_time=birth_time_effective,
            birth_city=payload.birth_city.strip(),
            birth_country=(payload.birth_country or 'FR').upper(),
            latitude=payload.latitude,
            longitude=payload.longitude,
            dedication=(payload.dedication or '').strip() or None,
            origin=payload.origin_url,
            no_birth_time=no_birth_time,
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

    # Fallback self-heal : si webhook Stripe non reçu, vérifie côté Stripe et
    # relance le handler. Idempotent (verrou _inflight + payment_transactions
    # update conditionnel côté service). Cf. incident sales P0 Feb 2026.
    asyncio.create_task(self_heal_if_paid(session_id, bool(md.get('pdf_path')), handle_edition_reliee_webhook))

    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_ready': bool(md.get('pdf_path')),
        'pdf_status': md.get('pdf_status'),
        'print_approval_id': md.get('print_approval_id'),
        'deadline_at': md.get('print_approval_deadline_at'),
        'email_sent': bool(md.get('print_approval_id')),
    }
