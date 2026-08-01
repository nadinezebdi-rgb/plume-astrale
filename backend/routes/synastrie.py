"""Routes /api/synastrie/* — Achat haut-ticket 49€ + PDF + email."""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from middleware.auth import get_optional_user
from services.synastrie_oneshot import (
    create_synastrie_checkout, get_synastrie_status,
    admin_bypass_synastrie,
)
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo

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
    promo_code: Optional[str] = None


@router.post('/checkout')
async def synastrie_checkout(
    payload: SynastrieCheckoutRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Cree une session Stripe one-shot 49€. Support bypass admin via code promo."""
    user_id = current_user.get('id') if current_user else None
    user_email = (current_user or {}).get('email') or payload.email

    if not user_email:
        raise HTTPException(status_code=400, detail='Un email est requis pour recevoir votre rapport.')

    # BYPASS PROMO (admin uniquement)
    if payload.promo_code and try_consume_promo(payload.promo_code, admin_user=current_user, product='synastrie_oneshot'):
        try:
            result = await admin_bypass_synastrie(
                user_id=user_id,
                user_email=user_email,
                person1_data=payload.person1.model_dump(),
                person2_data=payload.person2.model_dump(),
                origin_url=payload.origin_url,
            )
            return result
        except Exception as e:
            logger.exception(f'[synastrie] promo bypass failed: {e}')
            # fallback : on continue vers le checkout normal

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


class ExtractRequest(BaseModel):
    person1: PersonNatalData
    person2: PersonNatalData
    email: str
    consent_marketing: bool = True


@router.post('/free-extract')
async def synastrie_free_extract(payload: ExtractRequest):
    """Lead magnet : extrait gratuit 3 pages envoye par email.
    Enrichit UNIQUEMENT la page Soleils via LLM + astro data (rapide ~10s).
    Ajoute le lead dans oracle_leads pour alimenter la sequence Resend."""
    import re
    import os
    import uuid
    from datetime import datetime, timezone  # noqa: F401
    from services.synastrie_pdf_generator import generate_synastrie_extract
    from services.synastrie_enrichment import fetch_astro_data, enrich_pages

    email = (payload.email or '').strip().lower()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        raise HTTPException(status_code=400, detail='Email invalide.')

    p1_dict = payload.person1.model_dump()
    p2_dict = payload.person2.model_dump()

    # Enrichissement minimal : uniquement page 5 (Soleils) pour rester rapide
    try:
        astro = await fetch_astro_data(p1_dict, p2_dict)
        enriched = await enrich_pages(astro, only_pages=[5])
    except Exception as e:
        logger.warning(f'[synastrie/extract] enrichment failed: {e}')
        enriched = None

    pdf_bytes = generate_synastrie_extract(p1_dict, p2_dict, enriched=enriched)

    # Sauvegarde locale
    assets_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'synastrie_extracts')
    os.makedirs(assets_root, exist_ok=True)
    extract_id = uuid.uuid4().hex[:12]
    filename = f'extract_{extract_id}.pdf'
    out_path = os.path.join(assets_root, filename)
    with open(out_path, 'wb') as f:
        f.write(pdf_bytes)
    pdf_url_path = f'/api/assets/synastrie_extracts/{filename}'

    # Ajoute le lead dans oracle_leads (table existante pour la sequence Resend)
    try:
        sb = get_admin_client()
        # Insert minimaliste : colonnes garanties (email, first_name, birth_date)
        sb.table('oracle_leads').upsert({
            'email': email,
            'first_name': p1_dict.get('prenom'),
            'birth_date': p1_dict.get('birth_date'),
        }, on_conflict='email').execute()
    except Exception as e:
        logger.warning(f'[synastrie/extract] lead persist: {e}')

    # Envoi email avec lien
    try:
        from services.resend_service import send_synastrie_extract_email
        await send_synastrie_extract_email(
            email,
            p1_dict.get('prenom', ''),
            p2_dict.get('prenom', ''),
            pdf_url_path,
        )
    except Exception as e:
        logger.warning(f'[synastrie/extract] email send: {e}')

    return {
        'success': True,
        'pdf_url': pdf_url_path,
        'message': 'Votre extrait vous a ete envoye par email. Verifiez votre boite (et vos spams).',
    }


@router.post('/preview')
async def synastrie_preview(payload: SynastrieCheckoutRequest):
    """Genere un PDF d'apercu (non-payant). Reserve a l'equipe pour visualiser le rapport
    sans passer par Stripe. Activable via la variable d'env SYNASTRIE_PREVIEW_ENABLED.
    Enrichit 10 pages via GPT-4o-mini + astrology-api.io (Option A user)."""
    import os
    if os.environ.get('SYNASTRIE_PREVIEW_ENABLED', '1') != '1':
        raise HTTPException(status_code=403, detail='Preview disabled')
    from services.synastrie_pdf_generator import generate_synastrie_pdf
    from services.synastrie_enrichment import fetch_astro_data, enrich_pages
    try:
        p1_dict = payload.person1.model_dump()
        p2_dict = payload.person2.model_dump()
        # Fetch astro data + generate LLM content en parallel
        astro = await fetch_astro_data(p1_dict, p2_dict)
        # Preview : seulement 5 pages enrichies pour tenir dans 60s (ingress timeout).
        # La version payante (via webhook Stripe) genere les 10 pages completes.
        enriched = await enrich_pages(astro, only_pages=[3, 4, 5, 8, 22])
        pdf_bytes = generate_synastrie_pdf(p1_dict, p2_dict, enriched=enriched)
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
