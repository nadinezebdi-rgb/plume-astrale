"""
Route publique /api/lead-magnet/* — Aperçu 5 pages "Thème Natal" gratuit.

Aucune authentification requise — c'est un lead magnet.
Rate-limit léger via cache mémoire (email → dernière génération < 5 min = 429).
"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field, field_validator

from services.lead_magnet_pdf import (
    build_lead_magnet_pdf, send_lead_magnet_email, LEAD_DIR,
)
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/lead-magnet', tags=['lead-magnet'])

# Rate-limit mémoire (par email) — 5 min entre deux générations
_LAST_GEN: dict[str, float] = {}
_RATE_LIMIT_SEC = 300


class LeadMagnetRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=80)
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    birth_time: Optional[str] = Field(default=None, pattern=r'^\d{2}:\d{2}$')
    birth_place: Optional[str] = Field(default=None, max_length=120)

    @field_validator('birth_date')
    @classmethod
    def valid_date(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except Exception:
            raise ValueError('date invalide')
        return v


@router.post('/generate')
async def generate_lead_magnet(payload: LeadMagnetRequest, request: Request):
    """Génère un aperçu 5 pages personnalisé et l'envoie par email + retourne l'URL.

    Public. Rate-limité à 1 génération / 5 min par email.
    """
    email = payload.email.lower().strip()
    now = time.time()

    # Rate limit
    last = _LAST_GEN.get(email, 0)
    if now - last < _RATE_LIMIT_SEC:
        raise HTTPException(
            status_code=429,
            detail={
                'message': 'Vous avez déjà reçu un aperçu récemment.',
                'retry_after_sec': int(_RATE_LIMIT_SEC - (now - last)),
            },
        )

    # Build PDF (bloquant CPU) — délégué au thread pool
    try:
        pdf_bytes = await asyncio.to_thread(
            build_lead_magnet_pdf,
            email=email,
            first_name=payload.first_name,
            birth_date_iso=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
        )
    except Exception as e:
        logger.exception(f'[lead_magnet] PDF build failed: {e}')
        raise HTTPException(status_code=500, detail='Génération de l\'aperçu échouée.')

    # Sauvegarde locale (le lien pointe vers /api/lead-magnet/download/{token})
    token = uuid.uuid4().hex
    filename = f'lead_{token}.pdf'
    out_path = LEAD_DIR / filename
    try:
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
    except Exception as e:
        logger.warning(f'[lead_magnet] disk write failed: {e}')

    _LAST_GEN[email] = now

    # Track dans Supabase (best-effort)
    # 2026-02-26 AUDIT FIX : l'ancien code insérait dans `lead_magnet_downloads`
    # qui n'existe PAS dans le schéma Supabase → les leads du formulaire aperçu
    # n'étaient JAMAIS persistés (log INFO silencieux). On insère désormais dans
    # `oracle_leads` — la même table que lit `/api/admin/leads`.
    try:
        sb = get_admin_client()
        # Upsert par email pour éviter les doublons si un visiteur ré-utilise le
        # formulaire après le rate-limit de 5 min.
        sb.table('oracle_leads').upsert({
            'email': email,
            'first_name': payload.first_name,
            'birth_date': payload.birth_date,
            'source': 'lead_magnet_apercu_5p',
            'consent_marketing': True,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }, on_conflict='email').execute()
    except Exception as e:
        logger.warning(f'[lead_magnet] oracle_leads persist FAILED: {e}')

    # Journal détaillé complémentaire (best-effort) — utile si un jour la table
    # `lead_magnet_downloads` est créée pour tracker le PDF token / téléchargement.
    try:
        sb.table('lead_magnet_downloads').insert({
            'email': email,
            'first_name': payload.first_name,
            'birth_date': payload.birth_date,
            'birth_place': payload.birth_place,
            'token': token,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        # Table optionnelle — ne pas polluer les logs si absente
        logger.debug(f'[lead_magnet] token journal skip: {e}')

    # URL absolue du PDF (via l'API — pas de partage direct du disque)
    base = str(request.base_url).rstrip('/')
    pdf_link = f'{base}/api/lead-magnet/download/{token}'

    # Email best-effort en tâche de fond
    asyncio.create_task(send_lead_magnet_email(
        email=email, first_name=payload.first_name, pdf_link=pdf_link,
    ))

    return {
        'success': True,
        'pdf_url': pdf_link,
        'token': token,
        'pages': 5,
        'message': 'Votre aperçu vous attend — nous vous l\'envoyons également par email.',
    }


@router.get('/download/{token}')
async def download_lead_magnet(token: str):
    """Sert le PDF généré. Token opaque (uuid4), non énumérable."""
    if not token or not token.isalnum() or len(token) < 16:
        raise HTTPException(status_code=404, detail='Aperçu introuvable.')
    p = LEAD_DIR / f'lead_{token}.pdf'
    if not p.exists():
        raise HTTPException(status_code=404, detail='Aperçu expiré ou introuvable.')
    try:
        data = p.read_bytes()
    except Exception as e:
        logger.warning(f'[lead_magnet] read failed: {e}')
        raise HTTPException(status_code=500, detail='Lecture du fichier échouée.')
    return Response(
        content=data,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="apercu-plume-astrale.pdf"',
            'Cache-Control': 'private, max-age=3600',
        },
    )
