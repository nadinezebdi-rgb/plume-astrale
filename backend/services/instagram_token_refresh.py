"""Instagram Access Token Auto-Refresh

Le token Instagram Long-Lived (60 jours) doit être rafraîchi AVANT expiration.
Ce service tourne toutes les 24h et rafraîchit le token s'il a plus de 50 jours,
évitant ainsi tout crash du service d'auto-post IG à J+60.

Endpoint Meta : GET /oauth/access_token?grant_type=fb_exchange_token
                 &client_id=... &client_secret=... &fb_exchange_token=CURRENT_TOKEN

Le nouveau token est stocké dans /tmp/plume_ig_token_meta.json avec sa date
d'émission. À chaque cycle, on lit ce fichier ; si absent (première fois),
on prend le token depuis .env.

⚠ Cette approche stocke le token sur disque local (/tmp), suffisant pour un
seul conteneur. Pour un déploiement multi-instance, migrer vers Supabase ou Redis.
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

TOKEN_STATE_FILE = Path('/tmp/plume_ig_token_meta.json')
REFRESH_INTERVAL_SEC = 24 * 3600  # tourne toutes les 24h
REFRESH_THRESHOLD_DAYS = 50  # rafraîchit si token > 50 jours

# Ces valeurs peuvent être définies via .env pour long-lived tokens issus
# d'une App Meta (pour user tokens Facebook Login, pas obligatoire).
META_APP_ID = os.environ.get('META_APP_ID')
META_APP_SECRET = os.environ.get('META_APP_SECRET')


def _load_state() -> dict:
    """Charge l'état du token depuis /tmp ou depuis .env si première fois."""
    if TOKEN_STATE_FILE.exists():
        try:
            return json.loads(TOKEN_STATE_FILE.read_text())
        except Exception as e:
            logger.warning(f'[ig_token] lecture state corrompue : {e}')
    # Bootstrap depuis .env
    env_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    if env_token:
        return {
            'token': env_token,
            'issued_at': datetime.now(timezone.utc).isoformat(),
            'source': 'env_bootstrap',
        }
    return {}


def _save_state(state: dict) -> None:
    try:
        TOKEN_STATE_FILE.write_text(json.dumps(state, indent=2))
        logger.info(f'[ig_token] state sauvegardé · issued_at={state.get("issued_at")}')
    except Exception as e:
        logger.error(f'[ig_token] sauvegarde échouée : {e}')


def get_current_token() -> str | None:
    """Retourne le token courant (depuis state ou .env)."""
    state = _load_state()
    return state.get('token') or os.environ.get('INSTAGRAM_ACCESS_TOKEN')


async def refresh_ig_token() -> dict:
    """Rafraîchit le token Long-Lived via l'endpoint Meta.

    Retourne un dict {status, token?, expires_in?, reason?}.
    """
    state = _load_state()
    current_token = state.get('token') or os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    if not current_token:
        return {'status': 'skipped', 'reason': 'no_token_configured'}

    # Endpoint standard pour rafraîchir un long-lived user token IG
    # https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/refresh_access_token
    url = 'https://graph.instagram.com/refresh_access_token'
    params = {
        'grant_type': 'ig_refresh_token',
        'access_token': current_token,
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            if r.status_code >= 400:
                logger.warning(f'[ig_token] refresh failed {r.status_code}: {r.text[:300]}')
                return {'status': 'error', 'reason': f'http_{r.status_code}', 'detail': r.text[:200]}
            data = r.json()
            new_token = data.get('access_token')
            expires_in = data.get('expires_in')  # secondes (typiquement ~5 184 000 = 60j)
            if not new_token:
                return {'status': 'error', 'reason': 'no_token_in_response', 'detail': str(data)[:200]}
            new_state = {
                'token': new_token,
                'issued_at': datetime.now(timezone.utc).isoformat(),
                'expires_in_days': expires_in / 86400 if expires_in else None,
                'source': 'refresh',
            }
            _save_state(new_state)
            logger.info(f'[ig_token] ✓ rafraîchi · expire dans {new_state["expires_in_days"]:.0f}j' if expires_in else '[ig_token] ✓ rafraîchi')
            return {'status': 'ok', 'expires_in_days': new_state['expires_in_days']}
    except Exception as e:
        logger.exception(f'[ig_token] exception : {e}')
        return {'status': 'error', 'reason': 'exception', 'detail': str(e)[:200]}


def _token_age_days() -> float | None:
    """Age du token en jours."""
    state = _load_state()
    issued = state.get('issued_at')
    if not issued:
        return None
    try:
        dt = datetime.fromisoformat(issued)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    except Exception:
        return None


async def ig_token_refresh_loop():
    """Boucle asyncio : vérifie l'âge du token toutes les 24h et rafraîchit si > 50j."""
    logger.info('[ig_token] boucle démarrée — cycle 24h, seuil 50j')
    # Sur startup, on vérifie tout de suite si le token est vieux
    while True:
        try:
            age = _token_age_days()
            if age is None:
                logger.info('[ig_token] pas de token configuré — skip')
            elif age >= REFRESH_THRESHOLD_DAYS:
                logger.info(f'[ig_token] token âge {age:.1f}j >= {REFRESH_THRESHOLD_DAYS}j — rafraîchissement...')
                result = await refresh_ig_token()
                logger.info(f'[ig_token] résultat : {result}')
            else:
                logger.debug(f'[ig_token] token âge {age:.1f}j — OK')
        except Exception as e:
            logger.exception(f'[ig_token] erreur boucle : {e}')

        try:
            await asyncio.sleep(REFRESH_INTERVAL_SEC)
        except asyncio.CancelledError:
            raise
