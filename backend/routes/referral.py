"""Routes publiques du système de parrainage.

- GET  /api/referral/me       → { code, link, invited_count, purchased_count, rewards_earned, referrals[] }
- POST /api/referral/attach   → { code } lie le user courant à un parrain (idempotent, refuse si déjà lié)
"""
from __future__ import annotations
import logging
import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from middleware.auth import get_current_user
from services import referral_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/referral', tags=['referral'])


class AttachPayload(BaseModel):
    code: str


def _public_base_url() -> str:
    """URL publique utilisée pour construire les liens partagés."""
    return os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')


@router.get('/me')
async def referral_me(current_user: dict = Depends(get_current_user)):
    stats = await referral_service.get_stats(current_user['id'])
    base = _public_base_url()
    return {
        **stats,
        'link': f"{base}/?ref={stats['code']}",
        'share_text': (
            "J'ai découvert Plume Astrale — une IA astrologue qui écrit tes thèmes en français. "
            "Avec mon lien tu bénéficies de mon parrainage, et moi je reçois un horoscope offert dès ton premier achat 🌙"
        ),
    }


@router.post('/attach')
async def referral_attach(payload: AttachPayload, current_user: dict = Depends(get_current_user)):
    result = await referral_service.attach_referrer(current_user['id'], payload.code)
    if not result.get('ok'):
        return {'ok': False, 'reason': result.get('error')}
    return {'ok': True}
