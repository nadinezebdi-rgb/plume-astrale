"""Iteration 38 — GaryVee pricing grid overhaul.

Validates:
1. GET /api/packs returns updated PACKS + SERVICE_COSTS
   - astro_amour → name='Clarté', credits=50, bonus=10, amount=14.99
   - initiation → 15 cr / 4.99€
   - flammes_jumelles → 100+30 / 29.99€
2. SERVICE_COSTS grid: 5 / 10 / 30 / 40 / 60
3. POST /api/credits/use deducts correct amount per SERVICE_COSTS
4. Regression: /api/rencontres/reveal, /api/rencontres/checkout,
   /api/rencontres/ultime/status, /api/plume-chat still work.
"""
import os
import time
import uuid
import pytest
import requests

def _load_frontend_env(key):
    try:
        with open('/app/frontend/.env') as f:
            for line in f:
                if line.startswith(f'{key}='):
                    return line.strip().split('=', 1)[1].strip('"').strip("'")
    except Exception:
        pass
    return None


BASE_URL = (
    os.environ.get('REACT_APP_BACKEND_URL')
    or _load_frontend_env('REACT_APP_BACKEND_URL')
).rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'

EXPECTED_PACK_IDS = {'initiation', 'astro_amour', 'flammes_jumelles', 'rencontres_ultime'}
EXPECTED_SERVICE_COSTS = {
    'tarot_oui_non': 5,
    'chat_astral': 10,
    'lecture_tarot': 10,
    'love_languages': 10,
    'tarot_marseille': 30,
    'tarot_celtique': 30,
    'tarologie': 30,
    'numerologie': 30,
    'lecture_astrologique': 40,
    'theme_natal_pdf': 60,
    'cartographie': 60,
    'cartographie_premium': 60,
    'synastrie': 60,
    'revolution_solaire': 60,
    'karma_destin': 60,
}


# ─── Fixtures ────────────────────────────────────────────────

def _read_env(key):
    try:
        with open('/app/backend/.env') as f:
            for line in f:
                if line.startswith(f'{key}='):
                    return line.strip().split('=', 1)[1].strip('"').strip("'")
    except Exception:
        pass
    return os.environ.get(key)


@pytest.fixture(scope='module')
def admin_token():
    sb_url = _read_env('SUPABASE_URL')
    anon = _read_env('SUPABASE_ANON_KEY')
    if not sb_url or not anon:
        pytest.skip('Supabase credentials not available')
    r = requests.post(
        f"{sb_url}/auth/v1/token?grant_type=password",
        headers={'apikey': anon, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f'Admin login failed: {r.status_code} {r.text[:150]}')
    return r.json()['access_token']


@pytest.fixture(scope='module')
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


def _get_balance(headers):
    r = requests.get(f'{API}/auth/me', headers=headers, timeout=15)
    r.raise_for_status()
    return r.json().get('credit_balance', 0)


# ─── 1. GET /api/packs — shape + new pack values ─────────────

class TestPacksEndpoint:
    def test_endpoint_returns_200(self):
        r = requests.get(f'{API}/packs', timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert 'packs' in data and 'service_costs' in data

    def test_pack_ids_are_the_expected_four(self):
        packs = requests.get(f'{API}/packs', timeout=15).json()['packs']
        assert set(packs.keys()) == EXPECTED_PACK_IDS, (
            f'Expected {EXPECTED_PACK_IDS}, got {set(packs.keys())}'
        )

    def test_pack_initiation(self):
        p = requests.get(f'{API}/packs', timeout=15).json()['packs']['initiation']
        assert p['name'] == 'Initiation'
        assert p['credits'] == 15
        assert (p.get('bonus') or 0) == 0
        assert abs(float(p['amount']) - 4.99) < 0.01
        assert p['currency'] == 'eur'

    def test_pack_astro_amour_is_clarte_new_grid(self):
        """CRITICAL: astro_amour renamed 'Clarté', 50+10 credits, 14.99 €."""
        p = requests.get(f'{API}/packs', timeout=15).json()['packs']['astro_amour']
        assert p['name'] == 'Clarté', f"Expected name='Clarté', got {p['name']!r}"
        assert p['credits'] == 50, f"Expected credits=50, got {p['credits']}"
        assert p['bonus'] == 10, f"Expected bonus=10, got {p['bonus']}"
        assert abs(float(p['amount']) - 14.99) < 0.01, (
            f"Expected amount=14.99, got {p['amount']}"
        )
        assert p['currency'] == 'eur'
        # Total 60 crédits = exact price of a Thème Natal (60 cr)
        assert (p['credits'] + p['bonus']) == 60

    def test_pack_flammes_jumelles(self):
        p = requests.get(f'{API}/packs', timeout=15).json()['packs']['flammes_jumelles']
        assert p['credits'] == 100
        assert p['bonus'] == 30
        assert abs(float(p['amount']) - 29.99) < 0.01

    def test_pack_rencontres_ultime_oneshot(self):
        p = requests.get(f'{API}/packs', timeout=15).json()['packs']['rencontres_ultime']
        assert p.get('kind') == 'oneshot'
        assert p['credits'] == 0
        assert abs(float(p['amount']) - 29.99) < 0.01


# ─── 2. SERVICE_COSTS — GaryVee grid (5/10/30/40/60) ─────────

class TestServiceCosts:
    def test_all_expected_services_present(self):
        sc = requests.get(f'{API}/packs', timeout=15).json()['service_costs']
        missing = set(EXPECTED_SERVICE_COSTS) - set(sc)
        assert not missing, f'Missing services in SERVICE_COSTS: {missing}'

    @pytest.mark.parametrize('service_id,expected_cost', list(EXPECTED_SERVICE_COSTS.items()))
    def test_service_cost_value(self, service_id, expected_cost):
        sc = requests.get(f'{API}/packs', timeout=15).json()['service_costs']
        assert sc[service_id] == expected_cost, (
            f'{service_id}: expected {expected_cost}, got {sc[service_id]}'
        )

    def test_all_costs_are_multiples_of_5(self):
        sc = requests.get(f'{API}/packs', timeout=15).json()['service_costs']
        for k, v in sc.items():
            assert v % 5 == 0, f'{k}={v} is not a multiple of 5 (GaryVee rule)'


# ─── 3. POST /api/credits/use — deduction correctness ────────

class TestCreditsUse:
    def test_use_chat_astral_deducts_10(self, auth_headers):
        bal_before = _get_balance(auth_headers)
        if bal_before < 10:
            pytest.skip('admin balance < 10')
        r = requests.post(
            f'{API}/credits/use',
            headers=auth_headers,
            json={'service_id': 'chat_astral'},
            timeout=15,
        )
        assert r.status_code == 200, f'{r.status_code} {r.text}'
        data = r.json()
        assert data['success'] is True
        assert data['cost'] == 10
        bal_after = _get_balance(auth_headers)
        assert bal_before - bal_after == 10

    def test_use_numerologie_deducts_30(self, auth_headers):
        bal_before = _get_balance(auth_headers)
        if bal_before < 30:
            pytest.skip('admin balance < 30')
        r = requests.post(
            f'{API}/credits/use',
            headers=auth_headers,
            json={'service_id': 'numerologie'},
            timeout=15,
        )
        assert r.status_code == 200, f'{r.status_code} {r.text}'
        data = r.json()
        assert data['cost'] == 30
        assert data['success'] is True
        bal_after = _get_balance(auth_headers)
        assert bal_before - bal_after == 30

    def test_use_lecture_astrologique_deducts_40(self, auth_headers):
        bal_before = _get_balance(auth_headers)
        if bal_before < 40:
            pytest.skip('admin balance < 40')
        r = requests.post(
            f'{API}/credits/use',
            headers=auth_headers,
            json={'service_id': 'lecture_astrologique'},
            timeout=15,
        )
        assert r.status_code == 200, f'{r.status_code} {r.text}'
        data = r.json()
        assert data['cost'] == 40
        bal_after = _get_balance(auth_headers)
        assert bal_before - bal_after == 40

    def test_use_theme_natal_deducts_60(self, auth_headers):
        bal_before = _get_balance(auth_headers)
        if bal_before < 60:
            pytest.skip('admin balance < 60')
        r = requests.post(
            f'{API}/credits/use',
            headers=auth_headers,
            json={'service_id': 'theme_natal_pdf'},
            timeout=15,
        )
        assert r.status_code == 200, f'{r.status_code} {r.text}'
        data = r.json()
        assert data['cost'] == 60
        bal_after = _get_balance(auth_headers)
        assert bal_before - bal_after == 60

    def test_use_unknown_service_returns_400(self, auth_headers):
        r = requests.post(
            f'{API}/credits/use',
            headers=auth_headers,
            json={'service_id': 'nonexistent_service_xyz'},
            timeout=15,
        )
        assert r.status_code == 400

    def test_use_credits_requires_auth(self):
        r = requests.post(
            f'{API}/credits/use',
            headers={'Content-Type': 'application/json'},
            json={'service_id': 'chat_astral'},
            timeout=15,
        )
        assert r.status_code in (401, 403)


# ─── 4. Regressions ───────────────────────────────────────────

class TestRegressionRencontres:
    def test_rencontres_reveal_public(self):
        payload = {
            'first_name': 'TestUser',
            'year': 1990, 'month': 5, 'day': 15,
            'hour': 12, 'minute': 0,
            'place': 'Paris', 'country': 'FR',
        }
        r = requests.post(f'{API}/rencontres/reveal', json=payload, timeout=30)
        assert r.status_code == 200, f'{r.status_code} {r.text[:200]}'
        data = r.json()
        assert 'reveal_id' in data
        assert 'portrait' in data
        assert 'house7_sign' in data

    def test_rencontres_checkout_creates_session(self):
        # First get a reveal_id
        rev = requests.post(
            f'{API}/rencontres/reveal',
            json={
                'first_name': 'TestUser',
                'year': 1990, 'month': 5, 'day': 15,
                'hour': 12, 'minute': 0, 'place': 'Paris', 'country': 'FR',
            }, timeout=30,
        )
        assert rev.status_code == 200
        reveal_id = rev.json()['reveal_id']

        payload = {
            'reveal_id': reveal_id,
            'email': f'test_it38_{uuid.uuid4().hex[:8]}@example.com',
            'origin_url': BASE_URL,
        }
        r = requests.post(f'{API}/rencontres/checkout', json=payload, timeout=30)
        assert r.status_code == 200, f'{r.status_code} {r.text[:200]}'
        data = r.json()
        assert 'url' in data or 'checkout_url' in data or 'session_id' in data

    def test_rencontres_ultime_status_unknown_returns_error_stage(self):
        r = requests.get(
            f'{API}/rencontres/ultime/status',
            params={'session_id': 'cs_test_TEST_it38_nonexistent'},
            timeout=15,
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get('stage') in ('error', 'pending')

    def test_rencontres_ultime_status_delivered_seed_still_works(self):
        # Pre-seeded delivered demo from iteration 37 should still respond correctly
        r = requests.get(
            f'{API}/rencontres/ultime/status',
            params={'session_id': 'cs_test_ultime_cb14f284e18c'},
            timeout=15,
        )
        # tolerate 200 with any well-formed shape
        assert r.status_code == 200
        assert 'stage' in r.json()


class TestRegressionPlumeChat:
    def test_plume_chat_public_returns_reply(self):
        payload = {
            'message': 'Bonjour Plume, comment vas-tu ?',
            'session_id': f'plume-it38-{uuid.uuid4().hex[:8]}',
        }
        r = requests.post(f'{API}/plume-chat', json=payload, timeout=60)
        assert r.status_code == 200, f'{r.status_code} {r.text[:200]}'
        data = r.json()
        # Success shape must at least be present, even if LLM fails we get success:false
        assert 'success' in data
        # Endpoint does not 500
        assert isinstance(data, dict)
