"""Liste blanche des origines frontend autorisées (CORS + URLs de redirection Stripe).

`origin_url` est fourni par le client : sans contrôle, il permettrait de rediriger
un acheteur vers un domaine tiers après paiement (open redirect / hameçonnage).
"""
import os
from urllib.parse import urlparse

from fastapi import HTTPException

DEFAULT_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://plume-astrale.vercel.app',
    'https://plume-astrale.fr',
    'https://www.plume-astrale.fr',
    'https://consultation-astro.preview.emergentagent.com',
    'https://consultation-astro.emergent.host',
]


def _normalize(origin: str) -> str:
    parsed = urlparse((origin or '').strip())
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return ''
    return f'{parsed.scheme}://{parsed.netloc}'.lower()


def get_allowed_origins() -> list:
    """Origines par défaut + CORS_ORIGINS + FRONTEND_URL (le joker `*` est ignoré)."""
    extra = os.environ.get('CORS_ORIGINS', '').split(',')
    extra.append(os.environ.get('FRONTEND_URL', ''))
    origins = list(DEFAULT_ORIGINS)
    for o in extra:
        o = o.strip().rstrip('/')
        if o and o != '*' and o not in origins:
            origins.append(o)
    return origins


def validate_origin(origin: str) -> str:
    """Retourne l'origine normalisée (sans `/` final) ou lève une 400 si non autorisée."""
    normalized = _normalize(origin)
    allowed = {_normalize(o) for o in get_allowed_origins()}
    if not normalized or normalized not in allowed:
        raise HTTPException(status_code=400, detail='origin_url non autorisée')
    return normalized


def validate_redirect_url(url: str) -> str:
    """Vérifie que l'origine d'une URL de redirection (success/cancel) est autorisée."""
    parsed = urlparse((url or '').strip())
    validate_origin(f'{parsed.scheme}://{parsed.netloc}')
    return url
