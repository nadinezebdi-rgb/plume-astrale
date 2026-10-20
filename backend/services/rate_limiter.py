"""rate_limiter — Rate limiter in-memory par IP (sliding window)
================================================================================

Léger : pas de dépendance (Redis non requis). TTL 1 h glissant.
Thread-safe (lock asyncio).

Usage :
    from services.rate_limiter import check_rate_limit
    await check_rate_limit(request, key='promo_checkout', max_hits=5, window_seconds=600)
"""
from __future__ import annotations
import asyncio
import time
import logging
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Clé = (bucket_name, ip), valeur = deque de timestamps récents
_buckets: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
_lock = asyncio.Lock()
_last_cleanup = 0.0


def _client_ip(request: Request) -> str:
    """Extrait l'IP client en tenant compte des proxies (X-Forwarded-For)."""
    xff = request.headers.get('x-forwarded-for', '')
    if xff:
        # Premier IP = client original (avant les proxies)
        return xff.split(',')[0].strip()
    xri = request.headers.get('x-real-ip', '')
    if xri:
        return xri.strip()
    return request.client.host if request.client else 'unknown'


async def check_rate_limit(
    request: Request, *, key: str, max_hits: int, window_seconds: int,
    cost: int = 1,
) -> None:
    """Lève 429 si l'IP dépasse `max_hits` dans la fenêtre glissante.

    `cost` permet de pondérer un appel (défaut 1).
    """
    now = time.monotonic()
    ip = _client_ip(request)
    bucket_key = (key, ip)

    async with _lock:
        q = _buckets[bucket_key]
        cutoff = now - window_seconds
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) + cost > max_hits:
            logger.warning(
                f'[rate_limit] 429 ip={ip} key={key} hits={len(q)}/{max_hits}'
            )
            retry = int(window_seconds - (now - q[0])) if q else window_seconds
            raise HTTPException(
                status_code=429,
                detail='Trop de requêtes. Merci de patienter avant de réessayer.',
                headers={'Retry-After': str(max(retry, 1))},
            )
        for _ in range(cost):
            q.append(now)

        # Nettoyage opportuniste (toutes les 10 min) des buckets vides/anciens
        global _last_cleanup
        if now - _last_cleanup > 600:
            _last_cleanup = now
            empty = [k for k, v in _buckets.items() if not v or v[-1] < cutoff - 3600]
            for k in empty:
                _buckets.pop(k, None)


__all__ = ['check_rate_limit']
