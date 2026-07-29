"""
Endpoints health check publics — utilisables par UptimeRobot, Pingdom, etc.
Pas d'auth requise (statut de santé non sensible).
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.stripe_guard import _current_mode, _is_effectively_live, _test_mode_allowed

router = APIRouter(prefix='/health', tags=['health'])


@router.get('/stripe')
async def health_stripe():
    """
    Statut Stripe pour monitoring externe.
    - HTTP 200 si mode LIVE ou LIVE_VIA_EMERGENT_PROXY (ou test explicitement autorisé)
    - HTTP 503 si mode TEST / MISSING (paiements non fonctionnels)

    Configurable dans UptimeRobot : monitor HTTP → https://plume-astrale.fr/api/health/stripe
    → alerte si status ≠ 200. Ping toutes les 5 min recommandé.
    """
    mode = _current_mode()
    ok = _is_effectively_live() or _test_mode_allowed()

    body = {
        'ok': ok,
        'mode': mode,
        'test_mode_explicitly_allowed': _test_mode_allowed(),
        'checkouts_functional': ok,
    }
    if not ok:
        body['message'] = (
            "Clé Stripe non-live détectée en production. "
            "Configure STRIPE_API_KEY=sk_live_... (ou sk_test_emergent_*) dans Emergent Deploy → Env Vars."
        )
    return JSONResponse(status_code=200 if ok else 503, content=body)


@router.get('')
async def health_root():
    """Health check global — pour ping de base UptimeRobot."""
    return {'ok': True, 'service': 'plume-astrale-api'}
