"""Instagram Auto-post — publication automatique du visuel du signe de la
semaine sur Instagram Business @plumeastrale.fr chaque lundi 8h UTC.

Instagram Business ID : 17841440273868005
Meta Graph API endpoint : POST /{ig-user-id}/media puis /{ig-user-id}/media_publish

⚠ PREREQUIS OBLIGATOIRE — À CONFIGURER AVANT LA PREMIERE EXECUTION :
──────────────────────────────────────────────────────────────────
1. Obtenir un Long-Lived Access Token Meta (60 jours) :
   https://developers.facebook.com/tools/explorer/
   Permissions requises : instagram_basic, instagram_content_publish,
                          pages_show_list, business_management

2. Ajouter dans /app/backend/.env :
     INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxxxx...
     INSTAGRAM_BUSINESS_ID=17841440273868005

3. Le visuel doit être hosté sur une URL publique HTTPS accessible par Meta.
   → à branche sur ton bucket S3/CloudFront OU sur ton domaine plume-astrale.fr

──────────────────────────────────────────────────────────────────

Rotation hebdomadaire : chaque lundi, on publie le visuel d'un signe
different (semaine 1 = Bélier, semaine 2 = Taureau, etc.). 12 signes → cycle
de 12 semaines qui reboucle sur l'année.

Chaque post inclut :
  • L'image 1080x1350 générée par services/instagram_visual.py
  • Une légende éditoriale personnalisée (climat du mois + citation du signe)
  • Les hashtags stratégiques (#astrologie #cycles #{signe})
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

from services.monthly_mood_content import (
    get_monthly_mood, MONTH_NAMES_FR,
)
from services.instagram_visual import generate_ig_visual

logger = logging.getLogger(__name__)

IG_ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
IG_BUSINESS_ID = os.environ.get('INSTAGRAM_BUSINESS_ID', '17841440273868005')
LAST_RUN_FILE = Path('/tmp/plume_ig_weekly_last_run.txt')  # 'YYYY-WW'

# Rotation des 12 signes — index de la semaine ISO % 12 → signe
ZODIAC_ROTATION = [
    ('Bélier', 'Feu'), ('Taureau', 'Terre'), ('Gémeaux', 'Air'), ('Cancer', 'Eau'),
    ('Lion', 'Feu'), ('Vierge', 'Terre'), ('Balance', 'Air'), ('Scorpion', 'Eau'),
    ('Sagittaire', 'Feu'), ('Capricorne', 'Terre'), ('Verseau', 'Air'), ('Poissons', 'Eau'),
]

CAPTION_TEMPLATE = """{climate_title}.

{accent}

—
Recevoir ta lecture mensuelle → lien en bio
plume-astrale.fr

#astrologie #{sign_lower} #{element_lower} #cyclesdevie #developpementpersonnel #plumeastrale"""


def _current_iso_week() -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    iso = now.isocalendar()
    return iso.year, iso.week


def _current_week_key() -> str:
    y, w = _current_iso_week()
    return f'{y}-{w:02d}'


def _already_posted_this_week() -> bool:
    if not LAST_RUN_FILE.exists():
        return False
    try:
        return LAST_RUN_FILE.read_text().strip() == _current_week_key()
    except Exception:
        return False


def _mark_posted_this_week():
    try:
        LAST_RUN_FILE.write_text(_current_week_key())
    except Exception:
        pass


def _pick_sign_of_week() -> tuple[str, str]:
    _, week = _current_iso_week()
    return ZODIAC_ROTATION[(week - 1) % 12]


async def _upload_visual_to_public_url(png_bytes: bytes, sign_name: str) -> str | None:
    """Upload le PNG à un endpoint public (Supabase Storage / S3 / CloudFront).
    À implémenter selon l'infra choisie. Renvoie l'URL publique HTTPS.

    ⚠ Meta Graph API refuse les URLs locales ou signées temporairement — il
    faut une URL HTTPS accessible sans auth pendant au moins 24h.
    """
    # TODO(user) : implémenter selon l'infra
    # Options :
    #   1. Supabase Storage bucket public : upload puis get_public_url
    #   2. AWS S3 avec bucket policy public read
    #   3. Endpoint FastAPI qui sert temporairement depuis /tmp
    #
    # Exemple Supabase :
    #   from services.supabase_client import get_admin_client
    #   sb = get_admin_client()
    #   path = f'ig-weekly/{sign_name.lower()}-{_current_week_key()}.png'
    #   sb.storage.from_('public').upload(path, png_bytes,
    #       {'content-type': 'image/png', 'upsert': 'true'})
    #   return sb.storage.from_('public').get_public_url(path)
    logger.warning('[ig_weekly] upload public URL non configuré — post skippé. '
                  'À implémenter dans _upload_visual_to_public_url().')
    return None


async def _post_to_instagram(image_url: str, caption: str) -> str | None:
    """Publie via Meta Graph API — 2 étapes : create media container puis publish."""
    if not IG_ACCESS_TOKEN:
        logger.warning('[ig_weekly] INSTAGRAM_ACCESS_TOKEN absent — post skippé.')
        return None
    async with httpx.AsyncClient(timeout=45) as client:
        # 1) Créer le media container
        r = await client.post(
            f'https://graph.facebook.com/v20.0/{IG_BUSINESS_ID}/media',
            data={
                'image_url': image_url,
                'caption': caption,
                'access_token': IG_ACCESS_TOKEN,
            },
        )
        if r.status_code >= 400:
            logger.error(f'[ig_weekly] media container failed {r.status_code}: {r.text[:300]}')
            return None
        creation_id = r.json().get('id')
        if not creation_id:
            return None
        # Meta suggère d'attendre ~30s pour que le container soit prêt
        await asyncio.sleep(30)
        # 2) Publier
        r2 = await client.post(
            f'https://graph.facebook.com/v20.0/{IG_BUSINESS_ID}/media_publish',
            data={
                'creation_id': creation_id,
                'access_token': IG_ACCESS_TOKEN,
            },
        )
        if r2.status_code >= 400:
            logger.error(f'[ig_weekly] media_publish failed {r2.status_code}: {r2.text[:300]}')
            return None
        return r2.json().get('id')


async def post_weekly_ig_visual() -> dict:
    """Génère + upload + publie le visuel du signe de la semaine sur IG."""
    if _already_posted_this_week():
        return {'status': 'skipped', 'reason': 'already_posted_this_week'}

    sign_name, element = _pick_sign_of_week()
    now = datetime.now(timezone.utc)
    mood = get_monthly_mood(element, now.month - 1)
    month_name = MONTH_NAMES_FR[now.month - 1]

    # 1) Générer le visuel
    png_bytes = generate_ig_visual(sign_name, month_name, mood['accent'])

    # 2) Upload à URL publique
    public_url = await _upload_visual_to_public_url(png_bytes, sign_name)
    if not public_url:
        return {'status': 'error', 'reason': 'upload_failed', 'sign': sign_name}

    # 3) Construire la légende
    caption = CAPTION_TEMPLATE.format(
        climate_title=mood['title'],
        accent=mood['accent'],
        sign_lower=sign_name.lower().replace('é', 'e').replace('è', 'e'),
        element_lower=element.lower(),
    )

    # 4) Poster
    post_id = await _post_to_instagram(public_url, caption)
    if not post_id:
        return {'status': 'error', 'reason': 'publish_failed', 'sign': sign_name}

    _mark_posted_this_week()
    logger.info(f'[ig_weekly] ✓ posté sur IG · {sign_name} · post_id={post_id}')
    return {'status': 'ok', 'sign': sign_name, 'post_id': post_id, 'image_url': public_url}


def _seconds_until_next_monday_8h_utc() -> float:
    """Nombre de secondes jusqu'au prochain lundi 8h UTC."""
    now = datetime.now(timezone.utc)
    days_ahead = (0 - now.weekday()) % 7  # 0 = lundi
    if days_ahead == 0 and now.hour >= 8:
        days_ahead = 7
    target = now.replace(hour=8, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    target = target + timedelta(days=days_ahead)
    if target <= now:
        target = target + timedelta(days=7)
    return (target - now).total_seconds()


async def ig_weekly_post_loop():
    """Boucle asyncio : lance un post chaque lundi 8h UTC."""
    logger.info('[ig_weekly] boucle démarrée — cible lundi 8h UTC')
    # Recovery : si on est lundi après 8h et qu'on n'a pas posté cette semaine
    now = datetime.now(timezone.utc)
    if now.weekday() == 0 and now.hour >= 8 and not _already_posted_this_week():
        try:
            r = await post_weekly_ig_visual()
            logger.info(f'[ig_weekly] recovery : {r}')
        except Exception as e:
            logger.exception(f'[ig_weekly] recovery failed : {e}')

    while True:
        sleep_s = _seconds_until_next_monday_8h_utc()
        logger.info(f'[ig_weekly] prochain post dans {sleep_s / 3600:.1f}h')
        try:
            await asyncio.sleep(sleep_s)
        except asyncio.CancelledError:
            raise
        try:
            r = await post_weekly_ig_visual()
            logger.info(f'[ig_weekly] résultat : {r}')
        except Exception as e:
            logger.exception(f'[ig_weekly] post échoué : {e}')
        await asyncio.sleep(3600)  # marge de 1h avant relance
