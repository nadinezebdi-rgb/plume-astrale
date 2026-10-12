"""Test dynamic tarot reveal endpoint (Sonnet 4.6 + Mongo cache 30min).

Objectif :
- Endpoint POST /api/experience/tarot-reveal accepte les 12 combos autorisés
- Cache hit sur 2ème appel identique
- Fallback silencieux (200 avec source='fallback') sur inputs invalides
- Structure de réponse conforme au contrat frontend
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'plume_astrale_test_tarot')

# Import après avoir configuré l'env
from routes.experience_tarot_reveal import (  # noqa: E402
    router,
    ALLOWED_CARDS,
    ALLOWED_INTENTS,
    _current_time_slot,
    _cache_key,
    CTA_BY_SERVICE,
)
from fastapi import FastAPI  # noqa: E402

app = FastAPI()
app.include_router(router, prefix='/api')


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


def test_time_slot_format():
    slot = _current_time_slot()
    # YYYYMMDD-HH{A|B}
    assert len(slot) == 12
    assert slot[8] == '-'
    assert slot[-1] in ('A', 'B')


def test_cache_key_deterministic_within_slot():
    k1 = _cache_key('heart', 'relationship')
    k2 = _cache_key('heart', 'relationship')
    assert k1 == k2
    assert k1.startswith('heart:relationship:')


def test_allowed_combos_count():
    # 3 cartes × 4 intents = 12
    assert len(ALLOWED_CARDS) == 3
    assert len(ALLOWED_INTENTS) == 4


def test_fallback_on_invalid_card(client):
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'invalid_zzz', 'intent_id': 'relationship'})
    assert r.status_code == 200
    body = r.json()
    assert body['source'] == 'fallback'
    assert body['revelation']
    assert body['tension']
    assert body['cta']


def test_fallback_on_invalid_intent(client):
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'heart', 'intent_id': 'nonsense'})
    assert r.status_code == 200
    assert r.json()['source'] == 'fallback'


def test_response_shape(client):
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'star', 'intent_id': 'self_discovery'})
    assert r.status_code == 200
    body = r.json()
    for key in ('title', 'revelation', 'tension', 'cta', 'source'):
        assert key in body, f'missing key: {key}'
    assert body['source'] in ('llm', 'cache', 'fallback')


def test_cta_maps_self_discovery_to_theme_natal(client):
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'moon', 'intent_id': 'self_discovery'})
    assert r.status_code == 200
    # self_discovery → theme_natal service
    assert r.json()['cta'] == CTA_BY_SERVICE['theme_natal']


def test_cta_maps_relationship_to_tirage(client):
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'heart', 'intent_id': 'relationship'})
    assert r.status_code == 200
    assert r.json()['cta'] == CTA_BY_SERVICE['tirage_complet']
