"""alert_cooldown — Lock Mongo-backed pour dédupliquer les alertes Slack.

Remplace les `set()` in-memory qui se vident à chaque restart pod. Format :
    collection = alert_cooldowns
    document   = {
        _id: "<channel>:<key>",   # ex "credit_note_monthly:2026-10"
        acquired_at: datetime,
        expires_at:  datetime,    # TTL managed-by-Mongo via index
    }

Index TTL sur `expires_at` → Mongo supprime automatiquement les locks expirés.

API :
    await try_acquire('credit_note_monthly', '2026-10', ttl_hours=24*35)
    → True une seule fois par (channel, key), False ensuite jusqu'à expiration.

Fail-open : si Mongo indisponible, retourne True pour ne pas bloquer les
alertes critiques (préférer un ping dupliqué à aucun ping).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_COLL = 'alert_cooldowns'
_INDEX_READY = False


async def _ensure_index(db) -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return
    try:
        await db[_COLL].create_index('expires_at', expireAfterSeconds=0)
        _INDEX_READY = True
    except Exception as e:
        logger.info(f'[alert_cooldown] index: {e}')


async def try_acquire(channel: str, key: str, ttl_hours: int = 24 * 35) -> bool:
    """Tente d'acquérir le lock (channel, key).

    Retourne True si l'alerte doit partir (premier appel ou ancien lock expiré),
    False si déjà envoyée récemment. Fail-open (True) si Mongo down.
    """
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return True  # fail-open

    lock_id = f'{channel}:{key}'
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ttl_hours)

    try:
        await _ensure_index(db)
        from pymongo.errors import DuplicateKeyError
        try:
            await db[_COLL].insert_one({
                '_id': lock_id,
                'channel': channel,
                'key': key,
                'acquired_at': now,
                'expires_at': expires,
            })
            logger.debug(f'[alert_cooldown] acquired fresh {lock_id}')
            return True
        except DuplicateKeyError:
            logger.debug(f'[alert_cooldown] duplicate for {lock_id}, checking expiry')
            existing = await db[_COLL].find_one({'_id': lock_id})
            exp = (existing or {}).get('expires_at')
            # Mongo stocke les datetimes BSON en UTC-naive → re-attache tzinfo.
            if exp and exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp and exp > now:
                return False
            # Expiré → remplace
            await db[_COLL].update_one(
                {'_id': lock_id},
                {'$set': {'acquired_at': now, 'expires_at': expires}},
            )
            return True
    except Exception as e:
        from pymongo.errors import DuplicateKeyError as _DKE
        if isinstance(e, _DKE):
            existing = await db[_COLL].find_one({'_id': lock_id})
            exp = (existing or {}).get('expires_at')
            if exp and exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp and exp > now:
                return False
            return True
        logger.info(f'[alert_cooldown] fail-open {lock_id}: {e}')
        return True


async def release(channel: str, key: str) -> None:
    """Supprime manuellement un lock (utile pour les tests)."""
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return
    try:
        await db[_COLL].delete_one({'_id': f'{channel}:{key}'})
    except Exception:
        pass


__all__ = ['try_acquire', 'release']
