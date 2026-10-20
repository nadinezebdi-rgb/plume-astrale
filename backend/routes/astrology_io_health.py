"""Health-check endpoint pour la clé astrology-api.io.

GET /api/health/astrology-io
  → { ok, status, latency_ms, error, key_fingerprint, checked_at }
"""
from fastapi import APIRouter

from services.astrology_io_health import ping_astrology_api

router = APIRouter(prefix='/health', tags=['health'])


@router.get('/astrology-io')
async def astrology_io_health():
    result = await ping_astrology_api()
    return result
