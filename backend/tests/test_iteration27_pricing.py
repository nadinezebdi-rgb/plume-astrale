"""Iteration 27 — validate new SERVICE_COSTS pricing/paywalls & premium offering."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PW = 'PlumeAdmin2026'


@pytest.fixture(scope='module')
def token():
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PW},
        timeout=15,
    )
    assert r.status_code == 200, f'Login failed: {r.status_code} {r.text}'
    return r.json()['access_token']


@pytest.fixture(scope='module')
def auth(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


def get_balance(auth):
    r = requests.get(f'{BASE_URL}/api/auth/me', headers=auth, timeout=15)
    assert r.status_code == 200
    return r.json()['credit_balance']


# --- SERVICE_COSTS validation ---

def test_packs_service_costs_new_values():
    r = requests.get(f'{BASE_URL}/api/packs', timeout=15)
    assert r.status_code == 200
    sc = r.json().get('service_costs', {})
    assert sc.get('chat_astral') == 3, f'chat_astral expected 3, got {sc.get("chat_astral")}'
    assert sc.get('karma_destin') == 20, f'karma_destin expected 20, got {sc.get("karma_destin")}'
    assert sc.get('synastrie') == 20
    assert sc.get('theme_natal_pdf') == 20
    assert sc.get('revolution_solaire') == 20
    assert sc.get('love_languages') == 10


# --- Auth/me regression ---

def test_auth_me_has_premium_and_balance(auth):
    r = requests.get(f'{BASE_URL}/api/auth/me', headers=auth, timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert 'credit_balance' in data
    assert isinstance(data['credit_balance'], int)
    assert 'is_premium' in data['user']
    assert isinstance(data['user']['is_premium'], bool)


# --- /api/credits/use deduction validation ---

def test_credits_use_karma_destin_deducts_20(auth):
    before = get_balance(auth)
    r = requests.post(f'{BASE_URL}/api/credits/use', headers=auth, json={'service_id': 'karma_destin'}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get('cost') == 20, f'expected cost=20 got {body}'
    after = get_balance(auth)
    assert after == before - 20, f'balance {before} -> {after}, expected -20'


def test_credits_use_chat_astral_deducts_3(auth):
    before = get_balance(auth)
    r = requests.post(f'{BASE_URL}/api/credits/use', headers=auth, json={'service_id': 'chat_astral'}, timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get('cost') == 3, body
    after = get_balance(auth)
    assert after == before - 3


# --- v3 Chat: refund on external API failure (balance unchanged) ---

def test_chat_v3_refund_on_api_failure(auth):
    before = get_balance(auth)
    r = requests.post(
        f'{BASE_URL}/api/astrology/v3/chat',
        headers=auth,
        json={'message': 'Bonjour Plume, parle-moi du jour.'},
        timeout=45,
    )
    # External API key invalid -> 502 with refund
    assert r.status_code in (200, 502), f'unexpected {r.status_code}: {r.text}'
    after = get_balance(auth)
    if r.status_code == 502:
        assert after == before, f'REFUND FAILED: before={before} after={after}'
    else:
        # API worked -> 3 credits charged
        assert after == before - 3 or after == before, f'balance odd: {before} -> {after}'


# --- v3 Synastry: auth required + paywall ---

def test_synastry_v3_requires_auth():
    r = requests.post(
        f'{BASE_URL}/api/astrology/v3/synastry',
        json={'person2': {'year': 1992, 'month': 7, 'day': 8, 'latitude': 48.85, 'longitude': 2.35}},
        timeout=15,
    )
    assert r.status_code in (401, 403), f'expected auth required, got {r.status_code}'


def test_synastry_v3_auth_and_charge(auth):
    before = get_balance(auth)
    r = requests.post(
        f'{BASE_URL}/api/astrology/v3/synastry',
        headers=auth,
        json={
            'person2': {'name': 'TEST', 'year': 1992, 'month': 7, 'day': 8, 'hour': 14, 'minute': 0, 'latitude': 48.85, 'longitude': 2.35},
            'relationship_type': 'love',
        },
        timeout=45,
    )
    # Charge happens BEFORE external API call -> 20cr deducted whether 502 or 200
    assert r.status_code in (200, 502), f'unexpected {r.status_code}: {r.text}'
    after = get_balance(auth)
    assert after == before - 20, f'synastry: expected -20, got {before}->{after}'


# --- v3 Solar Return ---

def test_solar_return_v3_requires_auth():
    r = requests.post(f'{BASE_URL}/api/astrology/v3/solar-return', json={}, timeout=15)
    assert r.status_code in (401, 403)


def test_solar_return_v3_charge_after_success(auth):
    before = get_balance(auth)
    r = requests.post(f'{BASE_URL}/api/astrology/v3/solar-return', headers=auth, json={}, timeout=45)
    after = get_balance(auth)
    # Charge AFTER API success -> if 502, no charge; if 200, -20cr
    if r.status_code == 502:
        assert after == before, f'solar-return 502 should not charge: {before}->{after}'
    elif r.status_code == 200:
        assert after == before - 20
    else:
        pytest.fail(f'unexpected status {r.status_code}: {r.text}')


# --- v3 Love Languages ---

def test_love_languages_v3_requires_auth():
    r = requests.post(f'{BASE_URL}/api/astrology/v3/love-languages', json={}, timeout=15)
    assert r.status_code in (401, 403)


def test_love_languages_v3_charge_after_success(auth):
    before = get_balance(auth)
    r = requests.post(f'{BASE_URL}/api/astrology/v3/love-languages', headers=auth, json={}, timeout=45)
    after = get_balance(auth)
    if r.status_code == 502:
        assert after == before, f'love-languages 502 should not charge: {before}->{after}'
    elif r.status_code == 200:
        assert after == before - 10
    else:
        pytest.fail(f'unexpected status {r.status_code}: {r.text}')


# --- v3 Natal PDF: charge BEFORE + refund on failure ---

def test_natal_pdf_v3_requires_auth():
    r = requests.post(f'{BASE_URL}/api/astrology/v3/natal/pdf', json={}, timeout=15)
    assert r.status_code in (401, 403)


def test_natal_pdf_v3_refund_on_api_failure(auth):
    before = get_balance(auth)
    r = requests.post(f'{BASE_URL}/api/astrology/v3/natal/pdf', headers=auth, json={}, timeout=60)
    after = get_balance(auth)
    if r.status_code == 502:
        # Refund flow: charge -20 then +20 => net 0
        assert after == before, f'natal/pdf 502 REFUND FAILED: {before}->{after}'
    elif r.status_code == 200:
        assert after == before - 20
    else:
        pytest.fail(f'unexpected status {r.status_code}: {r.text}')


# --- Karma & Destiny regression (public) ---

def test_karma_destiny_public_rich_data():
    r = requests.post(
        f'{BASE_URL}/api/astrology/karma-destiny',
        json={'prenom': 'Test', 'dateNaissance': '1990-05-15', 'heureNaissance': '12:00', 'ville': 'Paris', 'pays': 'France'},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    data = r.json().get('data', {})
    assert 'karma_principal' in data
    assert 'mission_de_vie' in data
    assert 'nombre_karmique' in data
    assert 'message_akashique' in data
    assert data['karma_principal'].get('theme')
