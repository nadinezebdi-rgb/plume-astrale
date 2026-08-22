"""Capture des signaux d'attribution Meta sur tous les checkouts.

Problème résolu
---------------
Le site (plume-astrale.fr) et l'API sont sur des origines différentes : les
cookies `_fbp` / `_fbc` posés par le pixel ne sont donc PAS envoyés au backend.
Le navigateur les transmet explicitement via des en-têtes, ajoutés côté client
par `frontend/src/lib/metaAttribution.js`.

Défense en profondeur (2026-08) : la table `checkout_attribution` est créée
en amont via migration. En cas de rollout inversé (backend avant migration),
on log un warning au lieu de crasher.
"""
from __future__ import annotations
import asyncio
import json
import logging

from starlette.responses import Response

logger = logging.getLogger(__name__)

_MAX_BODY = 64 * 1024
_TABLE_MISSING_WARNED = False


def _extract_signals(request) -> dict:
    """En-têtes d'attribution + IP réelle et User-Agent."""
    from services.meta_capi import extract_client_signals
    h = request.headers
    return {
        **extract_client_signals(request),
        'event_id': h.get('x-meta-event-id') or None,
        'fbp': h.get('x-meta-fbp') or None,
        'fbc': h.get('x-meta-fbc') or None,
        'event_source_url': h.get('origin') or h.get('referer') or None,
    }


def _persist(session_id: str, signals: dict) -> None:
    """Écriture synchrone (supabase-py) — appelée dans un thread.

    Défense en profondeur : si la table `checkout_attribution` n'existe pas
    (migration non exécutée), on log un warning une seule fois, on ne crashe
    pas. Un checkout doit toujours pouvoir aboutir même sans tracking.
    """
    global _TABLE_MISSING_WARNED
    from services.supabase_client import get_admin_client
    row = {'session_id': session_id, **signals}
    try:
        get_admin_client().table('checkout_attribution').upsert(
            row, on_conflict='session_id',
        ).execute()
    except Exception as e:
        msg = str(e).lower()
        if 'checkout_attribution' in msg or 'does not exist' in msg or 'not found' in msg:
            if not _TABLE_MISSING_WARNED:
                _TABLE_MISSING_WARNED = True
                logger.warning(
                    "[meta_attribution] table 'checkout_attribution' introuvable — "
                    "exécutez supabase/checkout_attribution_migration.sql. "
                    "Le tracking Meta est désactivé jusqu'à la migration."
                )
            return
        raise


async def meta_attribution_middleware(request, call_next):
    """Associe les signaux Meta au session_id renvoyé par une route de checkout."""
    is_checkout = request.method == 'POST' and '/checkout' in request.url.path
    response = await call_next(request)
    if not is_checkout or response.status_code != 200:
        return response

    body = b''
    try:
        async for chunk in response.body_iterator:
            body += chunk
    except Exception as e:
        logger.warning(f'[meta_attribution] lecture reponse impossible: {e}')
        return response

    rebuilt = Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

    if len(body) > _MAX_BODY:
        return rebuilt
    try:
        session_id = (json.loads(body) or {}).get('session_id')
    except Exception:
        return rebuilt
    if not session_id:
        return rebuilt

    signals = _extract_signals(request)
    try:
        await asyncio.to_thread(_persist, session_id, signals)
    except Exception as e:
        logger.warning(f'[meta_attribution] persist {session_id} echoue: {e}')

    return rebuilt
