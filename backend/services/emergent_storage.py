"""emergent_storage — Thin wrapper around Emergent Object Storage.

Used by `natal_book_illustrations` to persist Nano Banana outputs across
container restarts/redeploys so we never re-pay generation cost for the
same signature.

Pattern :
- `init_storage()` est appelé lazily à la première opération ; la clé de
  session est conservée en module-global et réutilisée.
- `put_object(path, data, content_type)` upload bytes.
- `get_object(path)` → bytes ou None (404 géré proprement, pas d'exception).
- `object_exists(path)` → bool (fait un GET HEAD-like).

Toutes les opérations sont wrappées dans `asyncio.to_thread` pour un usage
depuis du code async FastAPI.
"""
from __future__ import annotations
import asyncio
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_STORAGE_BASE = (os.environ.get('INTEGRATION_PROXY_URL') or '').strip() or \
    'https://integrations.emergentagent.com'
_STORAGE_URL = _STORAGE_BASE.rstrip('/') + '/objstore/api/v1/storage'

_storage_key: Optional[str] = None
_init_lock = asyncio.Lock()


def _init_storage_sync() -> Optional[str]:
    """Blocking init call ; returns storage_key or None on failure."""
    global _storage_key
    if _storage_key:
        return _storage_key
    emergent_key = os.environ.get('EMERGENT_LLM_KEY')
    if not emergent_key:
        logger.warning('[emergent_storage] EMERGENT_LLM_KEY missing, storage disabled')
        return None
    try:
        resp = requests.post(
            f'{_STORAGE_URL}/init',
            json={'emergent_key': emergent_key},
            timeout=30,
        )
        resp.raise_for_status()
        _storage_key = resp.json().get('storage_key')
        if _storage_key:
            logger.info('[emergent_storage] initialized')
        return _storage_key
    except Exception as e:
        logger.warning(f'[emergent_storage] init failed: {e}')
        return None


async def ensure_storage_key() -> Optional[str]:
    """Async init (thread-safe)."""
    if _storage_key:
        return _storage_key
    async with _init_lock:
        if _storage_key:
            return _storage_key
        return await asyncio.to_thread(_init_storage_sync)


def _put_sync(path: str, data: bytes, content_type: str) -> bool:
    global _storage_key
    key = _init_storage_sync()
    if not key:
        return False
    try:
        resp = requests.put(
            f'{_STORAGE_URL}/objects/{path}',
            headers={'X-Storage-Key': key, 'Content-Type': content_type},
            data=data,
            timeout=120,
        )
        if resp.status_code in (401, 403, 404):
            # storage_key invalide / expiré → on reset et on retente une fois
            _storage_key = None
            key2 = _init_storage_sync()
            if not key2:
                return False
            resp = requests.put(
                f'{_STORAGE_URL}/objects/{path}',
                headers={'X-Storage-Key': key2, 'Content-Type': content_type},
                data=data,
                timeout=120,
            )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f'[emergent_storage] put({path}) failed: {e}')
        return False


def _get_sync(path: str) -> Optional[bytes]:
    global _storage_key
    key = _init_storage_sync()
    if not key:
        return None
    try:
        resp = requests.get(
            f'{_STORAGE_URL}/objects/{path}',
            headers={'X-Storage-Key': key},
            timeout=60,
        )
        if resp.status_code == 404:
            return None
        if resp.status_code in (401, 403):
            # storage_key invalide / expiré → reset + retry une fois
            _storage_key = None
            key2 = _init_storage_sync()
            if not key2:
                return None
            resp = requests.get(
                f'{_STORAGE_URL}/objects/{path}',
                headers={'X-Storage-Key': key2},
                timeout=60,
            )
            if resp.status_code == 404:
                return None
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        logger.warning(f'[emergent_storage] get({path}) failed: {e}')
        return None


async def put_object(path: str, data: bytes, content_type: str = 'image/jpeg') -> bool:
    """Upload bytes to Emergent Object Storage. Returns True on success."""
    return await asyncio.to_thread(_put_sync, path, data, content_type)


async def get_object(path: str) -> Optional[bytes]:
    """Download bytes from Emergent Object Storage. Returns None if 404 or error."""
    return await asyncio.to_thread(_get_sync, path)
