"""
Garde-fou anti-mode-test Stripe en production.

Bloque les endpoints de checkout Stripe si :
  - La clé STRIPE_API_KEY ne commence pas par 'sk_live_'
  - ET la requête provient d'un domaine de production (plume-astrale.fr)
  - ET STRIPE_ALLOW_TEST_MODE n'est pas explicitement à 'true'

Créé après l'incident 2026-02 où la production a redirigé une cliente vers
un checkout Stripe en mode test.
"""
from __future__ import annotations
import logging
import os
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Hôtes considérés comme production — toute requête depuis ces hôtes
# est bloquée si la clé Stripe n'est pas 'sk_live_'.
_PROD_HOSTS = (
    'plume-astrale.fr',
    'www.plume-astrale.fr',
)

# Suffixes d'URL de checkout à protéger (patterns FastAPI)
_CHECKOUT_SUFFIXES = ('/checkout',)


def _is_prod_host(host: str) -> bool:
    host = (host or '').lower().split(':')[0]
    return any(host == p or host.endswith('.' + p) for p in _PROD_HOSTS)


def _current_mode() -> str:
    key = os.environ.get('STRIPE_API_KEY', '').strip()
    if key.startswith('sk_live_'):
        return 'LIVE'
    # Clé spéciale Emergent : sk_test_emergent_* → routée via proxy Emergent vers
    # de vrais paiements Live (URLs cs_live_...). C'est un cas explicitement OK.
    if 'sk_test_emergent' in key:
        return 'LIVE_VIA_EMERGENT_PROXY'
    if key.startswith('sk_test_'):
        return 'TEST'
    if not key:
        return 'MISSING'
    return 'UNKNOWN'


def _test_mode_allowed() -> bool:
    """Escape hatch pour laisser passer le mode test explicitement (dev, staging)."""
    return os.environ.get('STRIPE_ALLOW_TEST_MODE', '').strip().lower() in ('1', 'true', 'yes', 'on')


def _is_effectively_live() -> bool:
    """Un mode est 'effectivement live' s'il génère des paiements réels."""
    return _current_mode() in ('LIVE', 'LIVE_VIA_EMERGENT_PROXY')


def log_startup_stripe_status() -> None:
    """Log un status Stripe au démarrage backend — visible dans les logs supervisor."""
    mode = _current_mode()
    allow_test = _test_mode_allowed()
    banner = '═' * 66
    if mode == 'LIVE':
        logger.info(f'\n{banner}\n[stripe_guard] ✓ STRIPE MODE = LIVE (paiements réels — clé sk_live_ directe)\n{banner}')
    elif mode == 'LIVE_VIA_EMERGENT_PROXY':
        logger.info(
            f'\n{banner}\n'
            f'[stripe_guard] ✓ STRIPE MODE = LIVE (via proxy Emergent — clé sk_test_emergent_*)\n'
            f'[stripe_guard]   Les URLs de checkout seront cs_live_... et les paiements sont réels.\n'
            f'{banner}'
        )
    elif mode == 'TEST':
        if allow_test:
            logger.warning(
                f'\n{banner}\n[stripe_guard] ⚠ STRIPE MODE = TEST (STRIPE_ALLOW_TEST_MODE=true — OK en dev/staging)\n{banner}'
            )
        else:
            logger.error(
                f'\n{banner}\n'
                f'[stripe_guard] ✗ STRIPE MODE = TEST — LES CHECKOUTS SERONT BLOQUÉS SUR plume-astrale.fr\n'
                f'[stripe_guard] → Configure STRIPE_API_KEY=sk_live_... (ou sk_test_emergent_*) en prod\n'
                f'[stripe_guard] → Ou définis STRIPE_ALLOW_TEST_MODE=true pour autoriser explicitement\n'
                f'{banner}'
            )
    else:
        logger.error(
            f'\n{banner}\n[stripe_guard] ✗ STRIPE MODE = {mode} — clé manquante ou invalide\n{banner}'
        )


async def stripe_live_guard_middleware(request: Request, call_next):
    """Middleware FastAPI : bloque /checkout en mode test depuis un hôte de production."""
    path = request.url.path
    if not any(path.endswith(sfx) for sfx in _CHECKOUT_SUFFIXES):
        return await call_next(request)

    # Uniquement pour les checkouts, on inspecte
    host = request.headers.get('host', '')
    is_prod = _is_prod_host(host)

    if is_prod and not _is_effectively_live() and not _test_mode_allowed():
        mode = _current_mode()
        logger.error(
            f'[stripe_guard] BLOCKED checkout {path} — host={host} mode={mode}. '
            f'Configure STRIPE_API_KEY=sk_live_... (ou sk_test_emergent_*) en prod pour débloquer.'
        )
        return JSONResponse(
            status_code=503,
            content={
                'detail': (
                    'Paiement temporairement indisponible. Notre équipe technique '
                    'a été notifiée. Merci de ne pas saisir ta carte bancaire — '
                    'contacte contact@plume-astrale.fr pour être aidée manuellement.'
                ),
                'code': 'stripe_not_live_in_prod',
            },
        )

    return await call_next(request)
