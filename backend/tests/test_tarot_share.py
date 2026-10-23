# Tarot share endpoints — POST /api/tarot/share + GET /api/tarot/shared/{id} (iteration 94)
import os
import re
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

PAYLOAD = {
    'type': 'marseille', 'question': 'TEST_ question partage ?', 'domaine': 'amour',
    'first_name': 'TEST_Camille',
    'data': {'cartes': [
        {'nom': 'Le Bateleur', 'position': 'Passé', 'interpretation': 'x'},
        {'nom': 'La Lune', 'position': 'Présent', 'interpretation': 'y'},
        {'nom': 'Le Soleil', 'position': 'Futur', 'interpretation': 'z'},
    ], 'synthese': 'TEST synthese'},
}


@pytest.fixture(scope='module')
def created():
    r = requests.post(f'{BASE_URL}/api/tarot/share', json=PAYLOAD, timeout=20)
    assert r.status_code == 200, r.text
    return r.json()


def test_create_share(created):
    assert created['success'] is True
    assert re.fullmatch(r'[0-9a-f]{12}', created['share_id'])
    # share_url pointe sur le wrapper OG (meilleures previews WhatsApp/Discord),
    # web_url pointe sur la page React directe.
    assert created['share_url'].endswith(f"/api/og/tirage/{created['share_id']}")
    assert created['web_url'].endswith(f"/tirage-partage/{created['share_id']}")
    assert 'expires_at' in created and created['expires_at']


def test_create_missing_cartes():
    r = requests.post(f'{BASE_URL}/api/tarot/share', json={'type': 'marseille', 'data': {}}, timeout=20)
    assert r.status_code == 200
    assert r.json()['success'] is False and r.json().get('message')


def test_create_invalid_type():
    r = requests.post(f'{BASE_URL}/api/tarot/share', json={**PAYLOAD, 'type': 'bogus'}, timeout=20)
    assert r.status_code == 200 and r.json()['success'] is False


def test_fetch_and_view_count(created):
    sid = created['share_id']
    r1 = requests.get(f'{BASE_URL}/api/tarot/shared/{sid}', timeout=20)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1['first_name'] == 'TEST_Camille'
    assert d1['question'] == PAYLOAD['question']
    assert len(d1['data']['cartes']) == 3
    assert '_id' not in d1
    r2 = requests.get(f'{BASE_URL}/api/tarot/shared/{sid}', timeout=20)
    assert r2.json()['view_count'] == d1['view_count'] + 1
    assert d1['view_count'] >= 1


def test_fetch_bad_id():
    r = requests.get(f'{BASE_URL}/api/tarot/shared/badID12345x', timeout=20)
    assert r.status_code == 400
    assert 'share_id invalide' in r.json()['detail']


def test_fetch_not_found():
    r = requests.get(f'{BASE_URL}/api/tarot/shared/0000000000ff', timeout=20)
    assert r.status_code == 404
    assert 'introuvable' in r.json()['detail']


def test_uppercase_id_normalized(created):
    r = requests.get(f"{BASE_URL}/api/tarot/shared/{created['share_id'].upper()}", timeout=20)
    assert r.status_code == 200
