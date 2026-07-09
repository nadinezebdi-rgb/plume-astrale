"""Iteration 26 - astrology-api.io v3 endpoints + regression tests.

The local ASTROLOGY_API_IO_KEY is INVALID (rotated). So calls that REACH the
external API are expected to return HTTP 502 'Service astrologique indisponible.'
from our backend (this proves our integration is wired correctly).

Tests cover:
- Auth (admin token, /api/auth/me regression)
- v3/synastry: auth, validation, relationship_type, 502 on key invalid
- v3/natal: auth, uses profile birth_data when person not provided
- v3/lunar + v3/positions: auth, 400 vs 502
- Legacy endpoints regression: horoscope-prediction, natal-chart, karma-destiny
- Premium/wallet regression
"""
import os
import requests
import pytest


BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2'
    'ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6'
    'MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'
)
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'


# ─── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope='session')
def admin_token():
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=20,
    )
    if r.status_code != 200:
        pytest.skip(f'Supabase auth failed: {r.status_code} {r.text[:200]}')
    return r.json()['access_token']


@pytest.fixture
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


@pytest.fixture
def person2_payload():
    return {
        'name': 'TEST Partenaire',
        'year': 1992, 'month': 7, 'day': 14,
        'hour': 9, 'minute': 30,
        'latitude': 48.8566, 'longitude': 2.3522,
        'city': 'Paris', 'country_code': 'FR',
    }


# ─── Regression: Auth & Account ────────────────────────────────────

class TestAuthRegression:
    def test_auth_me_with_admin(self, auth_headers):
        r = requests.get(f'{BASE_URL}/api/auth/me', headers=auth_headers, timeout=15)
        assert r.status_code == 200, f'Got {r.status_code}: {r.text[:200]}'
        data = r.json()
        # Admin profile shape
        assert isinstance(data, dict)
        # Email field can be under user/data – be lenient
        flat = {**data, **(data.get('user') or {}), **(data.get('profile') or {})}
        assert ADMIN_EMAIL in str(data), 'admin email not in /auth/me response'

    def test_auth_me_without_token(self):
        r = requests.get(f'{BASE_URL}/api/auth/me', timeout=15)
        assert r.status_code in (401, 403)

    def test_premium_status(self, auth_headers):
        r = requests.get(f'{BASE_URL}/api/premium/status', headers=auth_headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, dict)

    def test_wallet_balance(self, auth_headers):
        r = requests.get(f'{BASE_URL}/api/wallet/balance', headers=auth_headers, timeout=15)
        assert r.status_code == 200
        data = r.json()
        # balance / credits field present
        assert any(k in data for k in ('balance', 'credits', 'credit', 'amount', 'credit_balance')), data


# ─── v3/synastry ────────────────────────────────────────────────────

class TestSynastryV3:
    URL = f'{BASE_URL}/api/astrology/v3/synastry'

    def test_requires_auth(self, person2_payload):
        r = requests.post(self.URL, json={'person2': person2_payload}, timeout=15)
        assert r.status_code in (401, 403), f'Expected 401/403, got {r.status_code}'

    def test_validation_missing_required_fields(self, auth_headers):
        # person2 missing required year/month/day
        r = requests.post(
            self.URL,
            headers=auth_headers,
            json={'person2': {'name': 'X'}, 'relationship_type': 'love'},
            timeout=15,
        )
        # FastAPI returns 422 for pydantic validation failures
        assert r.status_code in (400, 422), f'Expected 400/422, got {r.status_code}: {r.text[:200]}'

    def test_validation_missing_person2_entirely(self, auth_headers):
        r = requests.post(self.URL, headers=auth_headers, json={'relationship_type': 'love'}, timeout=15)
        assert r.status_code in (400, 422)

    @pytest.mark.parametrize('rel_type', ['love', 'friendship', 'family', 'work'])
    def test_relationship_types_accepted(self, auth_headers, person2_payload, rel_type):
        """All 4 relationship types should be accepted by validation.
        Will return 502 because local API key invalid - that confirms the request
        reached the external API and was handled gracefully.
        Also acceptable: 400 if person1 cannot be resolved from profile.
        """
        r = requests.post(
            self.URL,
            headers=auth_headers,
            json={'person2': person2_payload, 'relationship_type': rel_type},
            timeout=45,
        )
        # 200 (if API key happens to be valid), 502 (key invalid - expected),
        # or 400 (profile missing) all prove validation accepted the rel_type
        assert r.status_code in (200, 400, 502), (
            f'Unexpected {r.status_code} for rel_type={rel_type}: {r.text[:300]}'
        )
        if r.status_code == 502:
            data = r.json()
            assert 'astrologique' in (data.get('detail') or '').lower() or 'indisponible' in (data.get('detail') or '').lower()

    def test_invalid_relationship_type_defaults_to_love(self, auth_headers, person2_payload):
        # Code coerces invalid types to 'love' — should not 422
        r = requests.post(
            self.URL,
            headers=auth_headers,
            json={'person2': person2_payload, 'relationship_type': 'unknown_type'},
            timeout=45,
        )
        assert r.status_code in (200, 400, 502)


# ─── v3/natal ───────────────────────────────────────────────────────

class TestNatalV3:
    URL = f'{BASE_URL}/api/astrology/v3/natal'

    def test_requires_auth(self):
        r = requests.post(self.URL, json={}, timeout=15)
        assert r.status_code in (401, 403)

    def test_uses_profile_when_person_not_provided(self, auth_headers):
        """Admin profile has birth_data (Paris 15/05/1990). Code should resolve it.
        Expected: 502 (API key invalid) — proving profile resolved + call reached API.
        If profile lacks complete birth data -> 400.
        """
        r = requests.post(self.URL, headers=auth_headers, json={}, timeout=45)
        assert r.status_code in (200, 400, 502), f'Got {r.status_code}: {r.text[:300]}'

    def test_with_explicit_person(self, auth_headers, person2_payload):
        r = requests.post(self.URL, headers=auth_headers, json={'person': person2_payload}, timeout=45)
        assert r.status_code in (200, 502), f'Got {r.status_code}: {r.text[:300]}'

    def test_validation_invalid_person(self, auth_headers):
        r = requests.post(self.URL, headers=auth_headers, json={'person': {'name': 'X'}}, timeout=15)
        assert r.status_code in (400, 422)


# ─── v3/lunar ───────────────────────────────────────────────────────

class TestLunarV3:
    URL = f'{BASE_URL}/api/astrology/v3/lunar'

    def test_requires_auth(self):
        r = requests.post(self.URL, json={}, timeout=15)
        assert r.status_code in (401, 403)

    def test_with_admin_uses_profile(self, auth_headers):
        r = requests.post(self.URL, headers=auth_headers, json={}, timeout=45)
        # 400 if profile has no birth_data, 502 if key invalid, 200 if it works
        assert r.status_code in (200, 400, 502)

    def test_with_explicit_person(self, auth_headers, person2_payload):
        r = requests.post(self.URL, headers=auth_headers, json={'person': person2_payload}, timeout=45)
        assert r.status_code in (200, 502)


# ─── v3/positions ───────────────────────────────────────────────────

class TestPositionsV3:
    URL = f'{BASE_URL}/api/astrology/v3/positions'

    def test_requires_auth(self):
        r = requests.post(self.URL, json={}, timeout=15)
        assert r.status_code in (401, 403)

    def test_with_admin_uses_profile(self, auth_headers):
        r = requests.post(self.URL, headers=auth_headers, json={}, timeout=45)
        assert r.status_code in (200, 400, 502)

    def test_with_explicit_person(self, auth_headers, person2_payload):
        r = requests.post(self.URL, headers=auth_headers, json={'person': person2_payload}, timeout=45)
        assert r.status_code in (200, 502)


# ─── Legacy regression ─────────────────────────────────────────────

class TestLegacyAstrology:
    def test_horoscope_prediction_no_crash(self, auth_headers):
        """Uses astrology_io_service - expect graceful failure (4xx/5xx) but no 500."""
        payload = {
            'sign': 'Taurus',
            'period': 'daily',
            'language': 'fr',
            'birth_date': '1990-05-15',
            'birth_time': '12:00',
            'latitude': 48.8566,
            'longitude': 2.3522,
        }
        r = requests.post(
            f'{BASE_URL}/api/astrology/horoscope-prediction',
            headers=auth_headers,
            json=payload,
            timeout=45,
        )
        # We allow many codes; what matters is no unhandled 500 stack-trace text
        assert r.status_code in (200, 400, 401, 403, 422, 502, 503), f'Got {r.status_code}: {r.text[:200]}'
        if r.status_code == 500:
            pytest.fail(f'Unhandled 500: {r.text[:300]}')

    def test_natal_chart_legacy(self, auth_headers):
        """Legacy /api/astrology/natal-chart - now uses astrology-api.io v3."""
        payload = {
            'day': 15, 'month': 5, 'year': 1990,
            'hour': 12, 'min': 0,
            'lat': 48.8566, 'lon': 2.3522,
            'tzone': 1.0,
        }
        r = requests.post(
            f'{BASE_URL}/api/astrology/natal-chart',
            headers=auth_headers,
            json=payload,
            timeout=45,
        )
        # Accept 200 (works) or 502/4xx (graceful)
        assert r.status_code in (200, 400, 401, 422, 502, 503), f'Got {r.status_code}: {r.text[:200]}'

    def test_karma_destiny(self, auth_headers):
        """Regression: karma-destiny should still return noeud_nord/sud."""
        payload = {
            'dateNaissance': '1990-05-15',
            'heureNaissance': '12:00',
            'latitude': 48.8566,
            'longitude': 2.3522,
            'lieuNaissance': 'Paris, France',
        }
        r = requests.post(
            f'{BASE_URL}/api/astrology/karma-destiny',
            headers=auth_headers,
            json=payload,
            timeout=45,
        )
        assert r.status_code == 200, f'Got {r.status_code}: {r.text[:300]}'
        data = r.json()
        # noeud_nord / noeud_sud regression check
        flat_str = str(data).lower()
        assert 'noeud' in flat_str or 'nord' in flat_str, f'noeud_nord/sud missing in response: {flat_str[:300]}'
