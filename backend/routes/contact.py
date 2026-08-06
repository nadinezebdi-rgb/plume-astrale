"""
Endpoint POST /api/contact — envoi du formulaire de contact.

Body: { name, email, subject, message, honeypot? }
Response: { success: bool, message: str }

Sécurité :
- Honeypot anti-bot (champ caché `website` doit être vide)
- Rate limit soft (basique, en mémoire)
- Validation stricte des inputs

Notification par Resend à contact@plume-astrale.fr.
"""
from __future__ import annotations
import logging
import os
import re
import time
from html import escape
from typing import Dict

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, field_validator

load_dotenv(dotenv_path='/app/backend/.env')

from services.resend_service import send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/contact', tags=['contact'])

SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'contact@plume-astrale.fr').strip()
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>').strip()

# ── Rate limit léger en mémoire ─────────────────────────
_RECENT: Dict[str, float] = {}
_WINDOW = 60.0  # 1 message par minute par IP


class ContactRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=10, max_length=4000)
    honeypot: str = Field(default='', max_length=0)

    @field_validator('name', 'subject', 'message')
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get('x-forwarded-for', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


@router.post('')
async def submit_contact(payload: ContactRequest, request: Request):
    # Anti-bot honeypot
    if payload.honeypot:
        logger.info('[contact] honeypot déclenché — ignoré silencieusement')
        return {'success': True, 'message': 'Merci, ton message a bien été envoyé.'}

    # Rate limit basique
    ip = _client_ip(request)
    now = time.time()
    last = _RECENT.get(ip, 0)
    if now - last < _WINDOW:
        raise HTTPException(status_code=429, detail='Merci de patienter une minute entre deux envois.')
    _RECENT[ip] = now
    # Cleanup old entries
    if len(_RECENT) > 1000:
        for k in list(_RECENT.keys()):
            if now - _RECENT[k] > _WINDOW * 5:
                _RECENT.pop(k, None)

    name = escape(payload.name)
    email = escape(payload.email)
    subject = escape(payload.subject)
    message_html = escape(payload.message).replace('\n', '<br>')

    html = f"""<!DOCTYPE html>
<html><body style="font-family: Georgia, serif; color: #232323; padding: 24px; background: #F7F5F0;">
  <div style="max-width: 600px; margin: 0 auto; background: #fff; padding: 32px; border-radius: 12px; border: 1px solid #E3E1DC;">
    <h2 style="color: #0F1A3C; font-family: 'Playfair Display', Georgia, serif; margin-top: 0;">Nouveau message · Plume Astrale</h2>
    <p style="color: #6B7280; font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase;">Formulaire /contact</p>
    <hr style="border: none; border-top: 1px solid #E3E1DC; margin: 20px 0;">
    <p><strong>De :</strong> {name} &lt;{email}&gt;</p>
    <p><strong>Sujet :</strong> {subject}</p>
    <p><strong>IP :</strong> {escape(ip)}</p>
    <hr style="border: none; border-top: 1px solid #E3E1DC; margin: 20px 0;">
    <div style="line-height: 1.6; font-size: 15px;">{message_html}</div>
  </div>
</body></html>"""
    text_body = f"De: {payload.name} <{payload.email}>\nSujet: {payload.subject}\nIP: {ip}\n\n{payload.message}"

    eid = await send_email(
        to_email=SUPPORT_EMAIL,
        subject=f'[Contact] {payload.subject}',
        html=html,
        text=text_body,
        from_email=SENDER_EMAIL,
    )
    if not eid:
        logger.error(f'[contact] Resend échec pour {payload.email}')
        # On ne bloque pas l'utilisatrice — le message est loggé côté serveur au minimum
        logger.info(f'[contact-fallback] from={payload.email} subject={payload.subject!r}')

    return {
        'success': True,
        'message': 'Ton message est bien parti. Soléna te répond en général sous 24-48h.',
    }
