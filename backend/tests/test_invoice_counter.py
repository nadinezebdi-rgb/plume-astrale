"""Tests de services/invoice_counter — compteur FACT-AAAA-NNNNNN.

Utilise un fake Mongo in-memory pour isoler les tests (pas de dépendance
sur une vraie base en CI).
"""
from __future__ import annotations
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from services import invoice_counter


# ───────────────────────── Fake Mongo in-memory ─────────────────────────

class _FakeCollection:
    def __init__(self):
        self.docs = {}
        self._by_id = {}
        self.unique_fields = set()

    async def create_index(self, field, unique=False):
        if unique:
            self.unique_fields.add(field)

    async def find_one(self, flt):
        for d in self.docs.values():
            if all(d.get(k) == v for k, v in flt.items()):
                return d
        return None

    async def find_one_and_update(self, flt, update, upsert=False, return_document=None):
        key = flt.get('_id')
        doc = self.docs.get(key)
        if not doc:
            if not upsert:
                return None
            doc = {'_id': key, 'seq': 0}
            self.docs[key] = doc
        if '$inc' in update:
            for k, v in update['$inc'].items():
                doc[k] = int(doc.get(k) or 0) + int(v)
        return doc

    async def insert_one(self, doc):
        from pymongo.errors import DuplicateKeyError
        for field in self.unique_fields:
            for existing in self.docs.values():
                if existing.get(field) == doc.get(field):
                    raise DuplicateKeyError(f'duplicate {field}')
        self.docs[doc.get('session_id', len(self.docs))] = dict(doc)


class _FakeDB:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = _FakeCollection()
        return self._collections[name]


@pytest.fixture
def fake_db():
    db = _FakeDB()
    with patch('services.mongo.get_db', return_value=db):
        yield db


# ───────────────────────────── Tests ─────────────────────────────────

def test_format_number_zero_padded():
    assert invoice_counter.format_number(2026, 1) == 'FACT-2026-000001'
    assert invoice_counter.format_number(2026, 42) == 'FACT-2026-000042'
    assert invoice_counter.format_number(2026, 123456) == 'FACT-2026-123456'


@pytest.mark.asyncio
async def test_allocate_first_number_is_one(fake_db):
    n = await invoice_counter.allocate_or_get(
        'cs_live_abc',
        datetime(2026, 2, 27, tzinfo=timezone.utc),
    )
    assert n == 'FACT-2026-000001'


@pytest.mark.asyncio
async def test_allocate_monotonic(fake_db):
    n1 = await invoice_counter.allocate_or_get('cs_a', datetime(2026, 3, 1, tzinfo=timezone.utc))
    n2 = await invoice_counter.allocate_or_get('cs_b', datetime(2026, 3, 2, tzinfo=timezone.utc))
    n3 = await invoice_counter.allocate_or_get('cs_c', datetime(2026, 3, 3, tzinfo=timezone.utc))
    assert [n1, n2, n3] == ['FACT-2026-000001', 'FACT-2026-000002', 'FACT-2026-000003']


@pytest.mark.asyncio
async def test_allocate_idempotent_same_session(fake_db):
    """Replay webhook : même session_id → même numéro, pas d'incrément inutile."""
    n1 = await invoice_counter.allocate_or_get('cs_X', datetime(2026, 2, 1, tzinfo=timezone.utc))
    n2 = await invoice_counter.allocate_or_get('cs_X', datetime(2026, 2, 1, tzinfo=timezone.utc))
    n3 = await invoice_counter.allocate_or_get('cs_Y', datetime(2026, 2, 1, tzinfo=timezone.utc))
    assert n1 == n2 == 'FACT-2026-000001'
    assert n3 == 'FACT-2026-000002'


@pytest.mark.asyncio
async def test_counter_resets_each_year(fake_db):
    n_2026 = await invoice_counter.allocate_or_get('cs_a', datetime(2026, 12, 31, tzinfo=timezone.utc))
    n_2027 = await invoice_counter.allocate_or_get('cs_b', datetime(2027, 1, 1, tzinfo=timezone.utc))
    assert n_2026 == 'FACT-2026-000001'
    assert n_2027 == 'FACT-2027-000001'


@pytest.mark.asyncio
async def test_fallback_when_mongo_down():
    """Si get_db() renvoie None, allocate_or_get retourne None (le caller fallback)."""
    with patch('services.mongo.get_db', return_value=None):
        n = await invoice_counter.allocate_or_get('cs_offline', datetime(2026, 2, 1, tzinfo=timezone.utc))
    assert n is None
