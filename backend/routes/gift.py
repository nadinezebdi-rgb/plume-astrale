"""
Endpoint POST /api/gift/reserve — réservation d'un cadeau (bon d'achat).

Body: { buyer_email, buyer_name, recipient_name, recipient_email, product_slug, message, occasion }
Envoie 2 emails :
  - Acheteur : confirmation + lien Stripe checkout dédié (dans MVP : lien vers la page produit)
  - Destinataire : notification de cadeau après paiement (dans MVP : simple ping avec message)

MVP simplifié : on ne facture pas dans cette route. On enregistre l'intention et on notifie l'acheteur
avec le lien vers la page produit à payer normalement + mention "cadeau".
"""
from __future__ import annotations
import logging, os, time
from datetime import datetime, timezone
from html import escape
from typing import Dict

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

load_dotenv(dotenv_path='/app/backend/.env')
from services.resend_service import send_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/gift', tags=['gift'])

SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'contact@plume-astrale.fr').strip()
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>').strip()

_RECENT: Dict[str, float] = {}
_WINDOW = 60.0

_PRODUCT_LABELS = {
    'natal':       ('Thème Natal Luxe', '/theme-natal-luxe', '17,99€'),
    'kabbale':     ('Arbre de Vie · Kabbale', '/kabbale', '39€'),
    'astrocarto':  ('Astrocartographie', '/astrocartographie', '49€'),
    'karma':       ('Karma & Destin', '/karma-destin-pdf', '29€'),
    'numerologie': ('Numérologie sacrée', '/numerologie-pdf', '29€'),
    'karmique':    ('Pack Karmique', '/pack-karmique', '89€'),
    'synastry':    ('Astrologie relationnelle', '/synastrie', '49€'),
}


class GiftReserveRequest(BaseModel):
    buyer_email: EmailStr
    buyer_name: str = Field(min_length=1, max_length=120)
    recipient_name: str = Field(min_length=1, max_length=120)
    recipient_email: EmailStr | None = None
    product_slug: str = Field(min_length=2, max_length=32)
    message: str = Field(default='', max_length=1000)
    occasion: str = Field(default='', max_length=60)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get('x-forwarded-for', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


@router.post('/reserve')
async def reserve_gift(payload: GiftReserveRequest, request: Request):
    ip = _client_ip(request)
    now = time.time()
    last = _RECENT.get(ip, 0)
    if now - last < _WINDOW:
        raise HTTPException(status_code=429, detail='Merci de patienter une minute avant un nouvel envoi.')
    _RECENT[ip] = now

    product_label, product_url, product_price = _PRODUCT_LABELS.get(
        payload.product_slug, ('ta lecture', '/nos-livres', '')
    )
    esc_buyer = escape(payload.buyer_name)
    esc_rec = escape(payload.recipient_name)
    esc_prod = escape(product_label)
    esc_price = escape(product_price)
    esc_occ = escape(payload.occasion)
    esc_msg = escape(payload.message).replace('\n', '<br>')
    full_url = f'https://plume-astrale.fr{product_url}?gift=1'

    occasion_line = f"à l'occasion de <strong>{esc_occ}</strong>" if esc_occ else ''
    message_block = (
        f'<div style="font-family:\'Inter\',sans-serif;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#6B7280;margin-bottom:6px;">Ton message</div>'
        f'<div style="font-family:\'Playfair Display\',Georgia,serif;font-size:15px;font-style:italic;color:#232323;line-height:1.55;">« {esc_msg} »</div>'
    ) if esc_msg else ''

    # Mail à l'acheteur — récap + lien
    html = f"""<!DOCTYPE html>
<html><body style="font-family: Georgia, 'Playfair Display', serif; color:#232323; padding:24px; background:#F7F5F0;">
  <div style="max-width:560px;margin:0 auto;background:#FFFFFF;padding:40px 32px;border-radius:12px;border:1px solid #E3E1DC;">
    <div style="font-family:'Playfair Display',Georgia,serif;font-size:24px;color:#0F1A3C;margin-bottom:4px;">
      Plume <span style="color:#C9A24B;">Astrale</span>
    </div>
    <div style="height:1px;background:#E3E1DC;margin:20px 0 28px;"></div>

    <p style="font-family:'Inter',sans-serif;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#C9A24B;margin:0 0 12px;">
      Ton projet cadeau
    </p>
    <h1 style="font-family:'Playfair Display',Georgia,serif;font-size:26px;font-weight:500;color:#0F1A3C;line-height:1.25;margin:0 0 20px;">
      Un cadeau pour <em style="color:#C9A24B;">{esc_rec}.</em>
    </h1>

    <p style="font-family:'Playfair Display',Georgia,serif;font-size:17px;line-height:1.65;color:#232323;margin:0 0 20px;">
      Bonjour {esc_buyer}, on a bien reçu ton intention d'offrir <strong>{esc_prod}</strong>
      {occasion_line}.
    </p>

    <div style="background:#FFFEF8;border:1.5px dashed #C9A24B;border-radius:12px;padding:20px;margin-bottom:24px;">
      <div style="font-family:'Inter',sans-serif;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#6B7280;margin-bottom:6px;">Pour</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:20px;color:#0F1A3C;margin-bottom:14px;">{esc_rec}</div>
      <div style="font-family:'Inter',sans-serif;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#6B7280;margin-bottom:6px;">Lecture</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:18px;color:#0F1A3C;margin-bottom:14px;">{esc_prod} · {esc_price}</div>
      {message_block}
    </div>

    <p style="font-family:'Playfair Display',Georgia,serif;font-size:16px;line-height:1.65;color:#232323;margin:0 0 24px;">
      Il te reste à finaliser le paiement. Clique ci-dessous — nous t'enverrons ensuite un joli bon cadeau PDF
      à transmettre à {esc_rec} quand tu voudras.
    </p>

    <div style="text-align:center;margin-bottom:24px;">
      <a href="{full_url}" style="display:inline-block;background:#C9A24B;color:#0F1A3C;padding:14px 28px;border-radius:999px;text-decoration:none;font-family:'Inter',sans-serif;font-size:15px;font-weight:600;">
        Finaliser le cadeau · {esc_price}
      </a>
    </div>

    <p style="font-family:'Playfair Display',Georgia,serif;font-size:14px;font-style:italic;color:#6B7280;margin:0;">
      Une question ? Réponds simplement à ce mail — on est là.<br>
      <span style="color:#C9A24B;">— Soléna</span>
    </p>
  </div>
</body></html>"""

    occ_line = f"Occasion : {payload.occasion}\n" if payload.occasion else ''
    msg_line = f"Message : {payload.message}\n\n" if payload.message else '\n'
    text = (
        f"Ton projet cadeau Plume Astrale\n\n"
        f"Bonjour {payload.buyer_name},\n\n"
        f"Cadeau pour : {payload.recipient_name}\n"
        f"Lecture : {product_label} · {product_price}\n"
        f"{occ_line}"
        f"{msg_line}"
        f"Finalise ici : {full_url}\n\n"
        f"— Soléna"
    )

    await send_email(
        to_email=payload.buyer_email,
        subject=f'Ton cadeau pour {payload.recipient_name} · Plume Astrale',
        html=html,
        text=text,
        from_email=SENDER_EMAIL,
    )

    # Notification support en interne
    try:
        support_html = f"<p><b>Nouveau projet cadeau</b></p><ul><li>Acheteur : {esc_buyer} &lt;{escape(payload.buyer_email)}&gt;</li><li>Destinataire : {esc_rec}{' (' + escape(payload.recipient_email) + ')' if payload.recipient_email else ''}</li><li>Lecture : {esc_prod} · {esc_price}</li><li>Occasion : {esc_occ or '—'}</li></ul>"
        if payload.message:
            support_html += f"<p><b>Message :</b><br>{esc_msg}</p>"
        await send_email(
            to_email=SUPPORT_EMAIL,
            subject=f'[Cadeau] {product_label} pour {payload.recipient_name}',
            html=support_html,
            text=f"Projet cadeau {product_label} pour {payload.recipient_name} par {payload.buyer_name} <{payload.buyer_email}>",
            from_email=SENDER_EMAIL,
        )
    except Exception as e:
        logger.warning(f'[gift] Support notification failed: {e}')

    return {
        'success': True,
        'message': "C'est parti ! Regarde ta boîte mail pour finaliser.",
        'checkout_url': full_url,
    }
