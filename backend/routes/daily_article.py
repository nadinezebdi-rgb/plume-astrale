"""Route /api/daily-article/send — envoie l'article du jour par email.

Endpoint léger et public. Capture l'email dans `oracle_leads` (source='daily_article')
puis envoie un email court avec le titre + extrait + lien direct vers /blog/{slug}.

Anti-abus : rate-limit basique 1 envoi / 60s par email (mémoire process).
"""
from __future__ import annotations
import logging
import os
import time
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from services.resend_service import send_email
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/daily-article', tags=['daily-article'])

_RATE_LIMIT_SEC = 60
_LAST_SEND: dict[str, float] = {}
_SITE = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')


class DailyArticleSendRequest(BaseModel):
    email: EmailStr
    slug: str = Field(min_length=3, max_length=120, pattern=r'^[a-z0-9-]+$')
    title: str = Field(min_length=3, max_length=200)
    excerpt: str = Field(min_length=10, max_length=600)
    tag: Optional[str] = Field(default=None, max_length=60)


@router.post('/send')
async def daily_article_send(payload: DailyArticleSendRequest):
    """Envoie l'article du jour par email + upsert lead (source='daily_article')."""
    email = payload.email.lower().strip()
    now = time.time()

    last = _LAST_SEND.get(email, 0.0)
    if now - last < _RATE_LIMIT_SEC:
        raise HTTPException(status_code=429, detail='Vous avez déjà reçu un article très récemment. Réessayez dans une minute.')

    # 1. Upsert lead (best-effort, ne bloque pas l'envoi si Supabase échoue)
    try:
        sb = get_admin_client()
        sb.table('oracle_leads').upsert({
            'email': email,
            'source': 'daily_article',
        }, on_conflict='email').execute()
    except Exception as e:
        logger.warning(f'[daily_article] oracle_leads upsert failed: {e}')

    # 2. Envoi email
    article_url = f'{_SITE}/blog/{payload.slug}'
    tag_line = f"<span style=\"color:#8F6E24;\">{payload.tag}</span> · " if payload.tag else ''

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F8F5EE;font-family:Georgia,'Cormorant Garamond',serif;color:#2A2417;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
  <tr><td align="center" style="padding:36px 16px;">
    <table role="presentation" width="580" style="max-width:580px;background:#FFFDF7;border:1px solid rgba(143,110,36,0.16);border-radius:8px;overflow:hidden;">
      <tr><td style="padding:34px 40px 12px;text-align:center;border-bottom:1px solid rgba(143,110,36,0.14);">
        <p style="margin:0;font-family:'Cinzel',Georgia,serif;font-size:10.5px;letter-spacing:0.32em;color:#8F6E24;text-transform:uppercase;">Plume Astrale · Votre article du jour</p>
      </td></tr>
      <tr><td style="padding:34px 40px 30px;">
        <p style="font-family:'Cinzel',Georgia,serif;font-size:11px;letter-spacing:0.24em;text-transform:uppercase;margin:0 0 14px;">{tag_line}Une lecture de 4 minutes</p>
        <h1 style="font-family:'Playfair Display',Georgia,serif;font-size:26px;font-weight:400;line-height:1.25;color:#0F1A3C;margin:0 0 20px;">{payload.title}</h1>
        <p style="font-family:'Cormorant Garamond',Georgia,serif;font-style:italic;font-size:18px;line-height:1.6;color:rgba(42,36,23,0.85);margin:0 0 28px;">{payload.excerpt}</p>
        <p style="margin:24px 0;">
          <a href="{article_url}" style="display:inline-block;padding:14px 30px;background:linear-gradient(135deg,#8F6E24,#C4A25C);color:#FFFDF7;text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:11.5px;letter-spacing:0.24em;text-transform:uppercase;border-radius:4px;font-weight:600;">LIRE L'ARTICLE COMPLET</a>
        </p>
        <p style="margin-top:24px;font-family:'Cormorant Garamond',serif;font-size:15px;line-height:1.65;color:rgba(42,36,23,0.72);">
          Chaque jour, nous choisissons un article différent parmi les neuf publiés — vous pouvez à tout moment revenir en découvrir un autre sur <a href="{_SITE}/blog" style="color:#8F6E24;">notre blog</a>.
        </p>
        <p style="margin:32px 0 0;font-family:'Playfair Display',Georgia,serif;font-style:italic;font-size:17px;color:#8F6E24;text-align:right;">— Nadine, éditrice</p>
      </td></tr>
      <tr><td style="padding:16px 40px 24px;border-top:1px solid rgba(143,110,36,0.12);text-align:center;font-family:'Inter',sans-serif;font-size:10.5px;line-height:1.7;color:rgba(42,36,23,0.5);">
        Plume Astrale · <a href="{_SITE}" style="color:#8F6E24;text-decoration:none;">plume-astrale.fr</a><br>
        Cet article vous est envoyé suite à votre visite. <a href="{_SITE}/api/oracle/unsubscribe?email={email}" style="color:#8F6E24;">Se désinscrire</a>.
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

    subject = f'Votre article du jour · {payload.title[:80]}'
    try:
        email_id = await send_email(email, subject, html)
    except Exception as e:
        logger.exception(f'[daily_article] send_email failed: {e}')
        raise HTTPException(status_code=500, detail="L'envoi de l'article a échoué. Réessayez dans quelques minutes.")

    if not email_id:
        raise HTTPException(status_code=500, detail="L'envoi de l'article a échoué. Réessayez dans quelques minutes.")

    _LAST_SEND[email] = now
    return {'success': True, 'article_url': article_url}
