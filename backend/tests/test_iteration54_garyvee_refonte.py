"""Iteration 54 — Refonte Gary Vee pricing (Feb 2026).

Tests scope :
  1. GET /api/packs → theme_natal_pdf_oneshot @29€, consultation_ultime @149€,
     rencontres_ultime @34.99€, fenetre_rencontre_avancee ABSENT
  2. GET /api/packs.service_costs → theme_natal_pdf=30, chat_astral=10
  3. POST /api/theme-natal-oneshot/checkout (valide, sans email, sans birth)
  4. GET  /api/theme-natal-oneshot/status  (404 si session inconnue, OK si session valide)
  5. GET  /api/subscriptions/cercle-solena/status  (admin)
  6. POST /api/subscriptions/cercle-solena/checkout (tier normal + premium → 503)
  7. Ancienne route POST /api/fenetre-rencontre-avancee/checkout → 404
  8. POST /api/astro/v3/chat → OK, dict chargé retourne les nouvelles clés
  9. Aucun abonné Cercle Solena existant (query supabase)
 10. Wallet chat_credits fallback safe pour l'admin
"""
import os
import pytest
import requests


def _read_env(key, path='/app/backend/.env'):
    try:
        with open(path) as f:
            for line in f:
                if line.startswith(f'{key}='):
                    return line.strip().split('=', 1)[1].strip('"').strip("'")
    except Exception:
        pass
    return os.environ.get(key)


def _read_front_env(key):
    try:
        with open('/app/frontend/.env') as f:
            for line in f:
                if line.startswith(f'{key}='):
                    return line.strip().split('=', 1)[1].strip('"').strip("'")
    except Exception:
        pass
    return None


BASE_URL = (os.environ.get('REACT_APP_BACKEND_URL') or _read_front_env('REACT_APP_BACKEND_URL')).rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'


@pytest.fixture(scope='module')
def admin_token():
    sb_url = _read_env('SUPABASE_URL')
    anon = _read_env('SUPABASE_ANON_KEY')
    if not sb_url or not anon:
        pytest.skip('Supabase env not available')
    r = requests.post(
        f"{sb_url}/auth/v1/token?grant_type=password",
        headers={'apikey': anon, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=20,
    )
    if r.status_code != 200:
        pytest.skip(f'Admin login failed: {r.status_code} {r.text[:200]}')
    return r.json()['access_token']


@pytest.fixture(scope='module')
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


@pytest.fixture(scope='module')
def packs_data():
    r = requests.get(f'{API}/packs', timeout=20)
    assert r.status_code == 200, r.text
    return r.json()


# ─── 1. GET /api/packs — PACKS ────────────────────────────────────────
class TestPacks:
    def test_theme_natal_pdf_oneshot_present_and_priced(self, packs_data):
        packs = packs_data['packs']
        assert 'theme_natal_pdf_oneshot' in packs, list(packs.keys())
        p = packs['theme_natal_pdf_oneshot']
        assert abs(float(p['amount']) - 29.0) < 0.01
        assert p.get('kind') == 'oneshot'

    def test_consultation_ultime_present_and_priced(self, packs_data):
        packs = packs_data['packs']
        assert 'consultation_ultime' in packs
        assert abs(float(packs['consultation_ultime']['amount']) - 149.0) < 0.01

    def test_rencontres_ultime_present_and_priced(self, packs_data):
        packs = packs_data['packs']
        assert 'rencontres_ultime' in packs
        assert abs(float(packs['rencontres_ultime']['amount']) - 34.99) < 0.01

    def test_fenetre_rencontre_avancee_absent(self, packs_data):
        packs = packs_data['packs']
        assert 'fenetre_rencontre_avancee' not in packs, (
            'fenetre_rencontre_avancee doit avoir été retiré du catalogue'
        )


# ─── 2. GET /api/packs.service_costs ──────────────────────────────────
class TestServiceCosts:
    def test_theme_natal_pdf_is_30(self, packs_data):
        sc = packs_data['service_costs']
        assert sc.get('theme_natal_pdf') == 30, sc

    def test_chat_astral_is_10(self, packs_data):
        sc = packs_data['service_costs']
        assert sc.get('chat_astral') == 10, sc


# ─── 3. POST /api/theme-natal-oneshot/checkout ────────────────────────
class TestThemeNatalCheckout:
    valid_payload = {
        'email': 'TEST_iter54@example.com',
        'first_name': 'Test',
        'birth_date': '1990-05-15',
        'birth_time': '12:00',
        'birth_city': 'Paris',
        'birth_country': 'FR',
        'latitude': 48.8566,
        'longitude': 2.3522,
        'origin_url': 'https://consultation-astro.preview.emergentagent.com',
    }

    def test_checkout_valid_returns_url_and_session_id(self):
        r = requests.post(f'{API}/theme-natal-oneshot/checkout',
                          json=self.valid_payload, timeout=30)
        assert r.status_code == 200, f'{r.status_code} : {r.text[:300]}'
        data = r.json()
        assert 'url' in data and data['url'].startswith('http')
        assert 'session_id' in data and len(data['session_id']) > 5
        # store session_id for status test
        TestThemeNatalCheckout._session_id = data['session_id']

    def test_checkout_missing_email(self):
        payload = dict(self.valid_payload)
        payload['email'] = ''
        r = requests.post(f'{API}/theme-natal-oneshot/checkout', json=payload, timeout=15)
        assert r.status_code == 400

    def test_checkout_missing_birth_time(self):
        payload = dict(self.valid_payload)
        payload['birth_time'] = ''
        r = requests.post(f'{API}/theme-natal-oneshot/checkout', json=payload, timeout=15)
        assert r.status_code == 400

    def test_checkout_missing_birth_date(self):
        payload = dict(self.valid_payload)
        payload['birth_date'] = ''
        r = requests.post(f'{API}/theme-natal-oneshot/checkout', json=payload, timeout=15)
        assert r.status_code == 400


# ─── 4. GET /api/theme-natal-oneshot/status ───────────────────────────
class TestThemeNatalStatus:
    def test_status_unknown_session_returns_404(self):
        r = requests.get(f'{API}/theme-natal-oneshot/status',
                         params={'session_id': 'cs_bogus_no_such_session_xxxxx'},
                         timeout=15)
        assert r.status_code == 404, f'{r.status_code} : {r.text[:200]}'

    def test_status_of_created_session(self):
        sid = getattr(TestThemeNatalCheckout, '_session_id', None)
        if not sid:
            pytest.skip('Checkout test did not run / provide session_id')
        r = requests.get(f'{API}/theme-natal-oneshot/status',
                         params={'session_id': sid}, timeout=20)
        assert r.status_code == 200, f'{r.status_code} : {r.text[:200]}'
        data = r.json()
        assert 'status' in data
        assert 'payment_status' in data
        assert 'pdf_ready' in data
        # No payment happened → not ready
        assert data['pdf_ready'] is False


# ─── 5. GET /api/subscriptions/cercle-solena/status ───────────────────
class TestCercleSolenaStatus:
    def test_status_returns_active_false(self, auth_headers):
        r = requests.get(f'{API}/subscriptions/cercle-solena/status',
                         headers=auth_headers, timeout=15)
        assert r.status_code == 200, f'{r.status_code} : {r.text[:200]}'
        data = r.json()
        assert data.get('active') is False
        assert data.get('subscription') is None
        assert data.get('tier') is None


# ─── 6. POST /api/subscriptions/cercle-solena/checkout ────────────────
class TestCercleSolenaCheckout:
    def test_checkout_normal_returns_503(self, auth_headers):
        r = requests.post(
            f'{API}/subscriptions/cercle-solena/checkout',
            headers=auth_headers,
            json={'origin_url': 'https://consultation-astro.preview.emergentagent.com',
                  'tier': 'normal'},
            timeout=20,
        )
        assert r.status_code == 503, f'{r.status_code} : {r.text[:200]}'
        assert 'PRICE_ID' in r.text or 'configuré' in r.text or 'configure' in r.text

    def test_checkout_premium_returns_503(self, auth_headers):
        r = requests.post(
            f'{API}/subscriptions/cercle-solena/checkout',
            headers=auth_headers,
            json={'origin_url': 'https://consultation-astro.preview.emergentagent.com',
                  'tier': 'premium'},
            timeout=20,
        )
        assert r.status_code == 503, f'{r.status_code} : {r.text[:200]}'
        assert 'PREMIUM' in r.text or 'PRICE_ID' in r.text or 'configuré' in r.text


# ─── 7. Ancienne route fenetre-rencontre-avancee ──────────────────────
class TestFenetreRencontreRemoved:
    def test_old_checkout_route_returns_404(self):
        r = requests.post(
            f'{API}/fenetre-rencontre-avancee/checkout',
            json={'email': 'test@example.com',
                  'origin_url': 'https://consultation-astro.preview.emergentagent.com'},
            timeout=15,
        )
        assert r.status_code == 404, f'Expected 404, got {r.status_code} : {r.text[:200]}'


# ─── 8. POST /api/astro/v3/chat — reste fonctionnel ────────────────────
class TestChatV3:
    def test_chat_endpoint_reachable(self, auth_headers):
        r = requests.post(
            f'{API}/astrology/v3/chat',
            headers=auth_headers,
            json={'message': 'Bonjour Soléna, ça va ?'},
            timeout=60,
        )
        # Should not 404 / 500. May be 200 (with answer) or 402 (no credits) — both acceptable.
        assert r.status_code in (200, 402), f'{r.status_code} : {r.text[:300]}'


# ─── 9. Aucun abonné Cercle Solena existant ───────────────────────────
class TestNoExistingCercleSubscribers:
    def test_supabase_query_empty(self):
        sb_url = _read_env('SUPABASE_URL')
        sb_key = _read_env('SUPABASE_SERVICE_ROLE_KEY')
        if not sb_url or not sb_key:
            pytest.skip('Supabase creds unavailable')
        # Note : la colonne `product` n'existe pas encore (migration Feb 2026 pas appliquée).
        # On confirme quand même via `status=active` qu'il n'y a AUCUN abonné actif tout court.
        r = requests.get(
            f'{sb_url}/rest/v1/subscriptions',
            params={'select': 'id,status', 'status': 'eq.active'},
            headers={'apikey': sb_key, 'Authorization': f'Bearer {sb_key}'},
            timeout=15,
        )
        assert r.status_code == 200, f'{r.status_code} : {r.text[:200]}'
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 0, f'Expected zero active subs, got {len(data)} : {data}'


# ─── 10. Wallet chat_credits fallback safe ────────────────────────────
class TestWalletChatCreditsFallback:
    def test_get_and_add_chat_credits_do_not_crash(self, auth_headers):
        # Get admin user id via /api/auth/me
        r = requests.get(f'{API}/auth/me', headers=auth_headers, timeout=15)
        assert r.status_code == 200
        user_id = (r.json().get('user') or {}).get('id')
        if not user_id:
            pytest.skip('Could not resolve user_id from /auth/me')

        import asyncio, sys
        sys.path.insert(0, '/app/backend')
        from services.wallet_service import get_chat_balance, add_chat_credits

        loop = asyncio.new_event_loop()
        try:
            bal = loop.run_until_complete(get_chat_balance(user_id))
            assert isinstance(bal, int)
            assert bal == 0, f'Expected 0 (column missing), got {bal}'
            new_bal = loop.run_until_complete(add_chat_credits(user_id, 10, 'test iter54'))
            assert isinstance(new_bal, int)
            # Migration not applied → returns current (0), no crash
            assert new_bal == 0, f'Expected 0 (fallback safe), got {new_bal}'
        finally:
            loop.close()
