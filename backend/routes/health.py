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


@router.get('/horoscopes')
async def health_horoscopes():
    """Statut de la génération quotidienne des horoscopes des 12 signes."""
    from pathlib import Path
    from datetime import datetime, timezone
    from services.horoscope_scheduler import LAST_RUN_FILE

    hor_dir = Path('/app/frontend/public/marketing/horoscopes')
    pdfs = sorted(hor_dir.glob('horoscope_journalier_*.pdf'))
    last_run = None
    if LAST_RUN_FILE.exists():
        try:
            last_run = LAST_RUN_FILE.read_text().strip()
        except Exception:
            pass
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    is_today = last_run == today
    return JSONResponse(
        status_code=200 if is_today and len(pdfs) >= 12 else 503,
        content={
            'ok': is_today and len(pdfs) >= 12,
            'last_regeneration_utc': last_run,
            'today_utc': today,
            'is_up_to_date': is_today,
            'pdfs_count': len(pdfs),
            'pdfs_expected': 12,
        },
    )


@router.get('')
async def health_root():
    """Health check global — pour ping de base UptimeRobot."""
    return {'ok': True, 'service': 'plume-astrale-api'}
