"""invoice_counter — Compteur de facture séquentiel, strictement croissant.

Exigence comptable française : les numéros de facture doivent former une
séquence chronologique continue et sans trou volontaire. On utilise un
compteur Mongo atomique (`find_one_and_update $inc + upsert`) remis à zéro
chaque année civile.

Format produit : ``FACT-AAAA-NNNNNN`` (ex. ``FACT-2026-000042``).

Idempotence : chaque ``session_id`` Stripe reçoit UN seul numéro. En cas de
replay webhook, on lit le numéro existant au lieu d'en allouer un nouveau,
pour éviter les trous dans la séquence et les factures en double.

Fallback : si Mongo n'est pas joignable, retour sur l'ancien format
``AAMM-XXXX`` (`invoice_pdf.make_invoice_number`) pour ne jamais bloquer la
livraison d'une facture.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COUNTERS_COLL = 'invoice_counters'
_REGISTRY_COLL = 'invoice_numbers'


def format_number(year: int, seq: int) -> str:
    """``FACT-2026-000042`` — 4 chiffres pour l'année, 6 chiffres zéro-paddés."""
    return f'FACT-{year:04d}-{seq:06d}'


async def _ensure_registry_index(db) -> None:
    """Crée l'index unique sur `session_id` à la demande (idempotent)."""
    try:
        await db[_REGISTRY_COLL].create_index('session_id', unique=True)
    except Exception as e:
        logger.info(f'[invoice_counter] index registry: {e}')


async def allocate_or_get(session_id: str, paid_at: Optional[datetime] = None) -> Optional[str]:
    """Retourne le numéro de facture pour ``session_id``.

    - S'il existe déjà en registry : on le réutilise (idempotence).
    - Sinon : incrémente atomiquement le compteur annuel et persiste
      l'association ``session_id → number``.

    Retourne ``None`` si Mongo est indisponible — le caller doit alors
    retomber sur l'ancien format ``AAMM-XXXX`` pour ne pas bloquer la
    livraison.
    """
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return None

    paid_at = paid_at or datetime.now(timezone.utc)
    year = paid_at.year

    try:
        # 1) Numéro déjà alloué pour cette session ?
        existing = await db[_REGISTRY_COLL].find_one({'session_id': session_id})
        if existing and existing.get('number'):
            return existing['number']

        # 2) Allocation atomique du prochain seq de l'année
        from pymongo import ReturnDocument
        counter = await db[_COUNTERS_COLL].find_one_and_update(
            {'_id': str(year)},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        seq = int(counter.get('seq') or 1)
        number = format_number(year, seq)

        # 3) Enregistrement de la correspondance (unique sur session_id)
        await _ensure_registry_index(db)
        from pymongo.errors import DuplicateKeyError
        try:
            await db[_REGISTRY_COLL].insert_one({
                'session_id': session_id,
                'number': number,
                'year': year,
                'seq': seq,
                'allocated_at': datetime.now(timezone.utc),
            })
        except DuplicateKeyError:
            # Course entre deux workers : on relit le numéro vainqueur.
            # Le seq qu'on vient d'incrémenter restera inutilisé (trou toléré).
            existing = await db[_REGISTRY_COLL].find_one({'session_id': session_id})
            if existing and existing.get('number'):
                return existing['number']

        return number
    except Exception as e:
        logger.warning(f'[invoice_counter] allocation fail session={session_id}: {e}')
        return None


async def peek_current_seq(year: int) -> int:
    """Lecture du dernier seq alloué pour l'année (0 si aucun). Pour admin."""
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
