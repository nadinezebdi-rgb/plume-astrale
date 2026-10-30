"""credit_note_counter — Compteur d'avoirs séquentiel annuel.

Miroir de `invoice_counter.py` pour les refunds. Même règle comptable FR :
numérotation strictement croissante, sans trou volontaire, remise à zéro
chaque année civile.

Format : ``AVOIR-AAAA-NNNNNN`` (ex. ``AVOIR-2026-000001``).

Idempotent par ``refund_id`` Stripe : rejouer n'alloue pas un nouveau numéro.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COUNTERS_COLL = 'credit_note_counters'
_REGISTRY_COLL = 'credit_note_numbers'


def format_number(year: int, seq: int) -> str:
    """``AVOIR-2026-000042`` — 4 chiffres pour l'année, 6 chiffres zéro-paddés."""
    return f'AVOIR-{year:04d}-{seq:06d}'


async def _ensure_registry_index(db) -> None:
    try:
        await db[_REGISTRY_COLL].create_index('refund_id', unique=True)
    except Exception as e:
        logger.info(f'[credit_note_counter] index: {e}')


async def allocate_or_get(refund_id: str, refunded_at: Optional[datetime] = None) -> Optional[str]:
    """Alloue atomiquement le prochain numéro d'avoir pour ce refund Stripe.

    Retourne ``None`` si Mongo indisponible — l'appelant doit alors retomber
    sur un format fallback (ex. ``AVOIR-{refund_id[-8:]}``).
    """
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return None

    refunded_at = refunded_at or datetime.now(timezone.utc)
    year = refunded_at.year

    try:
        existing = await db[_REGISTRY_COLL].find_one({'refund_id': refund_id})
        if existing and existing.get('number'):
            return existing['number']

        from pymongo import ReturnDocument
        counter = await db[_COUNTERS_COLL].find_one_and_update(
            {'_id': str(year)},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        seq = int(counter.get('seq') or 1)
        number = format_number(year, seq)

        await _ensure_registry_index(db)
        from pymongo.errors import DuplicateKeyError
        try:
            await db[_REGISTRY_COLL].insert_one({
                'refund_id': refund_id,
                'number': number,
                'year': year,
                'seq': seq,
                'allocated_at': datetime.now(timezone.utc),
            })
        except DuplicateKeyError:
            existing = await db[_REGISTRY_COLL].find_one({'refund_id': refund_id})
            if existing and existing.get('number'):
                return existing['number']

        return number
    except Exception as e:
        logger.warning(f'[credit_note_counter] allocation fail refund={refund_id}: {e}')
        return None


async def peek_current_seq(year: int) -> int:
    """Dernier seq alloué pour l'année (0 si aucun). Pour admin."""
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return 0
    try:
        doc = await db[_COUNTERS_COLL].find_one({'_id': str(year)})
        return int((doc or {}).get('seq') or 0)
    except Exception:
        return 0


__all__ = ['allocate_or_get', 'format_number', 'peek_current_seq']
