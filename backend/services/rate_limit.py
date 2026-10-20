"""Limitation de débit en mémoire (par IP) pour les endpoints publics sensibles.

Limite : l'état est propre à chaque processus. Suffisant pour freiner le brute-force de
codes promo et l'abus du checkout sur une instance unique ; à remplacer par un store partagé
(Redis) si le backend passe sur plusieurs instances.
"""
import os
import time
from collections import deque
from typing import Deque, Dict, Tuple

from fastapi import HTTPException, Request

_HITS: Dict[Tuple[str, str], Deque[float]] = {}
_MAX_KEYS = 10_000


def client_ip(request: Request) -> str:
    """IP du client derrière N proxys de confiance (TRUSTED_PROXY_HOPS, 1 par défaut).

    Chaque proxy ajoute l'IP qu'il voit à la fin de X-Forwarded-For : on lit donc depuis
    la droite, car les valeurs de gauche sont contrôlées par le client.
    """
    forwarded = [p.strip() for p in request.headers.get('x-forwarded-for', '').split(',') if p.strip()]
    if forwarded:
        try:
            hops = max(1, int(os.environ.get('TRUSTED_PROXY_HOPS', '1')))
        except ValueError:
            hops = 1
        return forwarded[-hops] if len(forwarded) >= hops else forwarded[0]
    return request.client.host if request.client else 'unknown'


def _check(key: Tuple[str, str], max_calls: int, window_s: float) -> float:
    """Enregistre un appel. Retourne 0 si autorisé, sinon le délai (s) avant de réessayer."""
    now = time.monotonic()
    if len(_HITS) > _MAX_KEYS:
        for k in [k for k, q in _HITS.items() if not q or now - q[-1] > window_s]:
            _HITS.pop(k, None)
    hits = _HITS.setdefault(key, deque())
    while hits and now - hits[0] > window_s:
        hits.popleft()
    if len(hits) >= max_calls:
        return window_s - (now - hits[0])
    hits.append(now)
    return 0.0


def rate_limit(name: str, max_calls: int, window_s: float = 60.0):
    """Dépendance FastAPI : `dependencies=[Depends(rate_limit('promo', 15))]`."""
    async def _dep(request: Request) -> None:
        retry = _check((name, client_ip(request)), max_calls, window_s)
        if retry:
            raise HTTPException(
                status_code=429,
                detail='Trop de requêtes, réessayez dans un instant.',
                headers={'Retry-After': str(int(retry) + 1)},
            )
    return _dep
