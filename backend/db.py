"""db — Shared Mongo client singleton.

Avant ce module : chaque route / service créait son propre
`AsyncIOMotorClient(MONGO_URL)` par appel, ce qui fuyait des pools de
connexions sous charge (voir rapport testing agent iteration 96).

Après ce module : un unique `AsyncIOMotorClient` initialisé paresseusement
au premier appel de `get_db()`, puis réutilisé pour toutes les requêtes.
"""
from __future__ import annotations
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None
_db_cache: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    """Retourne la DB Mongo partagée. Thread-safe (CPython GIL)."""
    global _client, _db_cache
    if _db_cache is not None:
        return _db_cache
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    if not mongo_url or not db_name:
        raise RuntimeError('MONGO_URL/DB_NAME manquants dans l\'environnement.')
    _client = AsyncIOMotorClient(mongo_url)
    _db_cache = _client[db_name]
    return _db_cache


async def close_db() -> None:
    """À appeler au shutdown FastAPI pour fermer proprement le client."""
    global _client, _db_cache
    if _client is not None:
        _client.close()
    _client = None
    _db_cache = None
