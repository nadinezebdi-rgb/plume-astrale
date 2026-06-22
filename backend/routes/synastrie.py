"""Routes /api/synastrie/* — Achat haut-ticket 49€ + PDF + email."""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from middleware.auth import get_optional_user
from services.synastrie_oneshot import (
    create_synastrie_checkout, get_synastrie_status,
)
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/synastrie', tags=['synastrie'])


class PersonNatalData(BaseModel):
    prenom: str = Field(..., min_length=1, max_length=80)
    birth_date: str = Field(..., description='YYYY-MM-DD')
    birth_time: Optional[str] = Field(None, description='HH:MM')
    birth_place: Optional[str] = None
    birth_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gender: Optional[str] = None


class SynastrieCheckoutRequest(BaseModel):
    person1: PersonNatalData
    person2: PersonNatalData
    origin_url: str
    email: Optional[str] = None  # pour les invites (achat sans compte)


@router.post('/checkout')
async def synastrie_checkout(
    payload: SynastrieCheckoutRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Cree une session Stripe one-shot 49€."""
    user_id = current_user.get('id') if current_user else None
    user_email = (current_user or {}).get('email') or payload.email

    if not user_email:
        raise HTTPException(status_code=400, detail='Un email est requis pour recevoir votre rapport.')

    return await create_synastrie_checkout(
        user_id=user_id,
        user_email=user_email,
        person1_data=payload.person1.model_dump(),
        person2_data=payload.person2.model_dump(),
        origin_url=payload.origin_url,
    )


@router.get('/status/{session_id}')
async def synastrie_status_endpoint(session_id: str):
    """Polled apres la redirection Stripe pour suivre l'etat de l'achat."""
    data = get_synastrie_status(session_id)
    # Ne pas exposer person1/2_data en clair via cette route publique
    safe = {
        'status': data.get('status'),
        'pdf_ready': bool(data.get('pdf_path')),
        'pdf_path': data.get('pdf_path'),
        'email_sent': bool(data.get('email_sent_at')),
        'created_at': data.get('created_at'),
    }
    return safe


@router.post('/preview')
async def synastrie_preview(payload: SynastrieCheckoutRequest):
    """Genere un PDF d'apercu (non-payant). Reserve a l'equipe pour visualiser le rapport
    sans passer par Stripe. Activable via la variable d'env SYNASTRIE_PREVIEW_ENABLED."""
    import os
    if os.environ.get('SYNASTRIE_PREVIEW_ENABLED', '1') != '1':
        raise HTTPException(status_code=403, detail='Preview disabled')
    from services.synastrie_pdf_generator import generate_synastrie_pdf
    try:
        pdf_bytes = generate_synastrie_pdf(payload.person1.model_dump(), payload.person2.model_dump())
        return Response(
            content=pdf_bytes,
            media_type='application/pdf',
            headers={'Content-Disposition': 'inline; filename="synastrie_preview.pdf"'}
        )
    except Exception as e:
        logger.error(f'[synastrie] preview gen failed: {e}')
        raise HTTPException(status_code=500, detail=f'PDF generation failed: {e}')


@router.post('/instagram-card')
async def synastrie_instagram_card(payload: SynastrieCheckoutRequest):
    """Genere un visuel carre 1080x1080 PNG (format Instagram) avec la couverture stylisee
    + les prenoms du couple. Utilise pour le partage social et l'attache email."""
    from services.synastrie_instagram_card import generate_instagram_card
    from services.synastrie_pdf_generator import _sign_from_date
    try:
        p1 = payload.person1.model_dump()
        p2 = payload.person2.model_dump()
        png_bytes = generate_instagram_card(
            prenom1=p1.get('prenom', ''),
            prenom2=p2.get('prenom', ''),
            sign1=_sign_from_date(p1.get('birth_date', '')),
            sign2=_sign_from_date(p2.get('birth_date', '')),
        )
        return Response(
            content=png_bytes,
            media_type='image/png',
            headers={'Content-Disposition': 'inline; filename="synastrie_instagram.png"'}
        )
    except Exception as e:
        logger.error(f'[synastrie] instagram card gen failed: {e}')
        raise HTTPException(status_code=500, detail=f'Card generation failed: {e}')
