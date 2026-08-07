"""
services/mongo.py — client Mongo asynchrone partagé.

Utilisation :
    from services.mongo import get_db
    db = get_db()
    if db is not None:
        await db.my_collection.insert_one({...})

Retourne None si MONGO_URL n'est pas configuré (aucune erreur bloquante,
les callers utilisent la valeur pour skipper silencieusement).
"""
from __future__ import annotations
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_CLIENT = None
_DB = None


def get_db():
    """Retourne le db motor asynchrone (Database) ou None si Mongo indispo."""
    global _CLIENT, _DB
    if _DB is not None:
        return _DB
    url = os.environ.get('MONGO_URL')
    if not url:
        return None
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        _CLIENT = AsyncIOMotorClient(url, serverSelectionTimeoutMS=1500)
        db_name = os.environ.get('DB_NAME', 'plume_astrale')
        _DB = _CLIENT[db_name]
        return _DB
    except Exception as e:
        logger.warning(f'[services.mongo] init failed: {e}')
        return None
