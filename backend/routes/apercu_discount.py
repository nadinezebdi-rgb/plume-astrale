"""
Endpoint POST /api/apercu/discount — capture email en fin d'aperçu
et envoie un code promo -10% par mail.

Body: { email, product_slug }
Response: { success: bool, message: str, code: str }

- Anti-spam : rate limit 60s/IP (comme /api/contact)
- Validation Pydantic stricte
- Log dans Mongo `apercu_discount_leads` pour analytics
- Envoi via Resend, sujet et corps signés Soléna
- Code envoyé : PROMO_CODE (env-configurable, défaut MERCI10)
"""
from __future__ import annotations
import logging
import os
import time
from datetime import datetime, timezone
from html import escape
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

load_dotenv(dotenv_path='/app/backend/.env')

from services.resend_service import send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/apercu', tags=['apercu'])

PROMO_CODE = os.environ.get('APERCU_PROMO_CODE', 'MERCI10').strip()
DISCOUNT_LABEL = '10%'
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>').strip()

# Rate limit
_RECENT: Dict[str, float] = {}
_WINDOW = 60.0

# Mapping produit → nom lisible + URL
_PRODUCT_LABELS = {
    'natal':       ('Thème Natal', '/theme-natal-luxe'),
    'kabbale':     ('Arbre de Vie · Kabbale', '/kabbale'),
    'astrocarto':  ('Astrocartographie', '/astrocartographie'),
    'karma':       ('Karma & Destin', '/karma-destin-pdf'),
    'numerologie': ('Numérologie sacrée', '/numerologie-pdf'),
    'karmique':    ('Pack Karmique', '/pack-karmique'),
    'synastry':    ('Astrologie relationnelle', '/synastrie'),
}


class ApercuDiscountRequest(BaseModel):
    email: EmailStr
    product_slug: str = Field(default='natal', max_length=32)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get('x-forwarded-for', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


async def _log_lead(email: str, product_slug: str, ip: str):
    """Log discret dans Mongo — non-bloquant."""
    try:
        from services.mongo import get_db  # type: ignore
        db = get_db()
        if db is not None:
            await db.apercu_discount_leads.insert_one({
                'email': email,
                'product_slug': product_slug,
                'promo_code': PROMO_CODE,
                'ip': ip,
                'created_at': datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        logger.debug(f'[apercu-discount] Mongo log skipped: {e}')


@router.post('/discount')
async def request_discount(payload: ApercuDiscountRequest, request: Request):
    ip = _client_ip(request)
    now = time.time()
    last = _RECENT.get(ip, 0)
    if now - last < _WINDOW:
        raise HTTPException(status_code=429, detail='Merci de patienter une minute avant un nouvel envoi.')
    _RECENT[ip] = now

    product_label, product_url = _PRODUCT_LABELS.get(
        payload.product_slug, ('ta lecture', '/nos-livres')
    )
    esc_label = escape(product_label)
    esc_code = escape(PROMO_CODE)
    site_url = 'https://plume-astrale.fr'
    full_url = f'{site_url}{product_url}'

    html = f"""<!DOCTYPE html>
<html><body style="font-family: Georgia, 'Playfair Display', serif; color: #232323; padding: 24px; background: #F7F5F0;">
  <div style="max-width: 560px; margin: 0 auto; background: #FFFFFF; padding: 40px 32px; border-radius: 12px; border: 1px solid #E3E1DC;">
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 24px; color: #0F1A3C; margin-bottom: 4px;">
      Plume <span style="color: #C9A24B;">Astrale</span>
    </div>
    <div style="height: 1px; background: #E3E1DC; margin: 20px 0 28px;"></div>

    <p style="font-family: 'Inter', sans-serif; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: #C9A24B; margin: 0 0 12px;">
      Ta réduction bienvenue
    </p>
    <h1 style="font-family: 'Playfair Display', Georgia, serif; font-size: 28px; font-weight: 500; color: #0F1A3C; line-height: 1.2; margin: 0 0 20px;">
      Voici tes <em style="color: #C9A24B;">{DISCOUNT_LABEL} de réduction.</em>
    </h1>

    <p style="font-family: 'Playfair Display', Georgia, serif; font-size: 17px; line-height: 1.65; color: #232323; margin: 0 0 20px;">
      Merci d'avoir pris le temps de lire un extrait — c'est comme ça qu'on se rencontre vraiment.
    </p>
    <p style="font-family: 'Playfair Display', Georgia, serif; font-size: 17px; line-height: 1.65; color: #232323; margin: 0 0 28px;">
      Voici ton code de bienvenue pour {esc_label}. Il te fait économiser {DISCOUNT_LABEL} sur ta première commande — pas d'expiration surprise, promis.
    </p>

    <div style="background: linear-gradient(135deg, #FFFEF8 0%, #FFFFFF 100%); border: 1.5px dashed #C9A24B; border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 32px;">
      <div style="font-family: 'Inter', sans-serif; font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; color: #6B7280; margin-bottom: 8px;">
        Ton code
      </div>
      <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 36px; font-weight: 500; color: #0F1A3C; letter-spacing: 0.06em;">
        {esc_code}
      </div>
      <div style="font-family: 'Inter', sans-serif; font-size: 13px; color: #6B7280; margin-top: 12px;">
        À entrer sur la page de paiement Stripe · valable une seule fois.
      </div>
    </div>

    <div style="text-align: center; margin-bottom: 32px;">
      <a href="{full_url}" style="display: inline-block; background: #C9A24B; color: #0F1A3C; padding: 14px 28px; border-radius: 999px; text-decoration: none; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600;">
        Recevoir {esc_label}
      </a>
    </div>

    <p style="font-family: 'Playfair Display', Georgia, serif; font-size: 15px; line-height: 1.6; color: #6B7280; font-style: italic; margin: 0 0 8px;">
      Prends le temps qu'il te faut pour choisir.<br>
      Je suis là quand tu es prête.
    </p>
    <p style="font-family: 'Playfair Display', Georgia, serif; font-size: 15px; color: #C9A24B; margin: 20px 0 0;">
      — Soléna
    </p>

    <div style="border-top: 1px solid #E3E1DC; margin-top: 32px; padding-top: 20px; font-family: 'Inter', sans-serif; font-size: 11px; color: #6B7280; letter-spacing: 0.06em; text-align: center;">
      Plume Astrale · <a href="{site_url}/mentions-legales" style="color: #6B7280;">Mentions légales</a> · <a href="{site_url}/cgv" style="color: #6B7280;">CGV</a>
    </div>
  </div>
</body></html>"""

    text = (
        f"Ta réduction bienvenue Plume Astrale\n\n"
        f"Merci d'avoir pris le temps de lire un extrait.\n\n"
        f"Voici ton code de bienvenue pour {product_label} :\n\n"
        f"    {PROMO_CODE}\n\n"
        f"Il te fait économiser {DISCOUNT_LABEL} sur ta première commande.\n"
        f"À entrer sur la page de paiement Stripe.\n\n"
        f"→ Recevoir {product_label} : {full_url}\n\n"
        f"— Soléna"
    )

    eid = await send_email(
        to_email=payload.email,
        subject=f'Ta réduction {DISCOUNT_LABEL} pour {product_label} · Plume Astrale',
        html=html,
        text=text,
        from_email=SENDER_EMAIL,
    )
    if not eid:
        logger.error(f'[apercu-discount] Resend échec pour {payload.email}')
        # On ne casse pas l'UX : on affiche succès quand même, le log serveur permet retry manuel.

    await _log_lead(payload.email, payload.product_slug, ip)

    return {
        'success': True,
        'message': f"C'est envoyé ! Regarde ta boîte mail (et les spams au cas où).",
        'code': PROMO_CODE,
    }
