"""Iteration 46 — Comprehensive regression tests for ALL Plume Astrale products.
Goal: identify ALL failing products/endpoints (bug from user: "plein de produits ne fonctionnent pas").

Priorities:
- P1: /api/astrology/v3/solar-return (Cloudflare 520 en prod)
- P2: Tous endpoints astrology_v3 avec admin auth
- P3: Endpoints des produits payants (archetype, kabbale, rencontres, synastrie, premium, plume-chat)
- P4: /api/discount/validate BIENVENUE
- P5: Détecter timeouts >15s
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'

REPORT = {}  # endpoint -> {status, time, error}


def _record(name, endpoint, status, elapsed, body_snippet):
    REPORT[name] = {
        'endpoint': endpoint,
        'http_status': status,
        'response_time_s': round(elapsed, 2),
        'body_snippet': body_snippet[:400] if body_snippet else '',
    }


@pytest.fixture(scope='session')
def admin_token():
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f'Supabase login failed: {r.status_code} {r.text[:200]}'
    return r.json()['access_token']


@pytest.fixture(scope='session')
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


# ═══════════════════════ HEALTH ═══════════════════════
class TestHealth:
    def test_health(self):
        r = requests.get(f'{BASE_URL}/api/health', timeout=10)
        assert r.status_code == 200

    def test_auth_me(self, auth_headers):
        t0 = time.time()
        r = requests.get(f'{BASE_URL}/api/auth/me', headers=auth_headers, timeout=15)
        _record('auth_me', '/api/auth/me', r.status_code, time.time() - t0, r.text)
        assert r.status_code == 200
        data = r.json()
        # /api/auth/me returns {user:{email:...}, credit_balance:...}
        user_obj = data.get('user') or data
        assert user_obj.get('email') == ADMIN_EMAIL


# ═══════════════════════ P1 : SOLAR RETURN ═══════════════════════
class TestSolarReturn:
    def test_solar_return_admin_empty_body(self, auth_headers):
        """PRIORITÉ 1 — Révolution Solaire avec profile natal admin.
        Doit répondre en <60s (Cloudflare kills à 100s en prod)."""
        t0 = time.time()
        try:
            r = requests.post(
                f'{BASE_URL}/api/astrology/v3/solar-return',
                headers=auth_headers,
                json={},
                timeout=90,
            )
            elapsed = time.time() - t0
            _record('solar_return', '/api/astrology/v3/solar-return', r.status_code, elapsed, r.text)
            print(f"[SOLAR RETURN] status={r.status_code}, time={elapsed:.1f}s")
            print(f"[SOLAR RETURN] body: {r.text[:500]}")
            assert r.status_code == 200, f'solar-return FAILED status={r.status_code} in {elapsed:.1f}s : {r.text[:300]}'
            assert elapsed < 60, f'solar-return TOO SLOW ({elapsed:.1f}s)'
        except requests.exceptions.Timeout:
            elapsed = time.time() - t0
            _record('solar_return', '/api/astrology/v3/solar-return', 'TIMEOUT', elapsed, 'TIMEOUT_90s')
            pytest.fail(f'solar-return TIMED OUT after {elapsed:.1f}s')


# ═══════════════════════ P2 : ASTROLOGY V3 ═══════════════════════
class TestAstrologyV3:
    def test_natal(self, auth_headers):
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/astrology/v3/natal', headers=auth_headers, json={}, timeout=90)
        elapsed = time.time() - t0
        _record('natal', '/api/astrology/v3/natal', r.status_code, elapsed, r.text)
        assert r.status_code == 200, f'natal FAILED: {r.status_code} {r.text[:300]}'

    def test_transits_today(self, auth_headers):
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/astrology/v3/transits/today', headers=auth_headers, json={}, timeout=90)
        elapsed = time.time() - t0
        _record('transits_today', '/api/astrology/v3/transits/today', r.status_code, elapsed, r.text)
        assert r.status_code == 200, f'transits/today FAILED: {r.status_code} {r.text[:300]}'

    def test_synastry(self, auth_headers):
        """Synastry uses admin as person1 + partner2 fixture."""
        person2 = {
            'name': 'Partenaire',
            'year': 1988, 'month': 3, 'day': 10, 'hour': 14, 'minute': 30,
            'city': 'Lyon', 'country_code': 'FR', 'latitude': 45.75, 'longitude': 4.85,
        }
        t0 = time.time()
        r = requests.post(
            f'{BASE_URL}/api/astrology/v3/synastry',
            headers=auth_headers,
            json={'person2': person2, 'relationship_type': 'love'},
            timeout=90,
        )
        elapsed = time.time() - t0
        _record('synastry', '/api/astrology/v3/synastry', r.status_code, elapsed, r.text)
        assert r.status_code == 200, f'synastry FAILED: {r.status_code} {r.text[:300]}'

    def test_natal_pdf(self, auth_headers):
        """Test natal-report endpoint (actually /natal/pdf)."""
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/astrology/v3/natal/pdf', headers=auth_headers, json={}, timeout=90)
        elapsed = time.time() - t0
        _record('natal_pdf', '/api/astrology/v3/natal/pdf', r.status_code, elapsed, r.text[:200] if r.headers.get('content-type', '').startswith('application/pdf') is False else 'PDF_binary')
        # PDF returned as binary — check content-type
        assert r.status_code == 200, f'natal/pdf FAILED: {r.status_code} {r.text[:300]}'

    def test_composite_missing(self, auth_headers):
        """Test if /composite endpoint exists (mentioned in review request)."""
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/astrology/v3/composite', headers=auth_headers, json={}, timeout=15)
        _record('composite', '/api/astrology/v3/composite', r.status_code, time.time() - t0, r.text)
        # Just record; don't fail if missing
        print(f"[COMPOSITE] status={r.status_code} (expected 404 if not implemented): {r.text[:200]}")


# ═══════════════════════ P3 : PRODUITS PAYANTS ═══════════════════════
class TestPaidProducts:
    def test_archetype_generate(self, auth_headers):
        """Ton Archétype (15cr). Utilise le profile natal de l'admin."""
        payload = {'force_refresh': True}
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/archetype/generate', headers=auth_headers, json=payload, timeout=90)
        elapsed = time.time() - t0
        _record('archetype', '/api/archetype/generate', r.status_code, elapsed, r.text)
        print(f"[ARCHETYPE] status={r.status_code} time={elapsed:.1f}s body={r.text[:300]}")
        assert r.status_code == 200, f'archetype FAILED: {r.status_code} {r.text[:400]}'

    def test_kabbale_checkout(self, auth_headers):
        """Kabbale — checkout Stripe. Doit renvoyer URL de session."""
        payload = {
            'email': 'admin@plume-astrale.fr',
            'first_name': 'Admin',
            'birth_date': '1990-05-15',
            'birth_time': '12:00',
            'birth_city': 'Paris',
            'birth_country': 'FR',
            'origin_url': BASE_URL,
        }
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/kabbale/checkout', headers=auth_headers, json=payload, timeout=30)
        elapsed = time.time() - t0
        _record('kabbale_checkout', '/api/kabbale/checkout', r.status_code, elapsed, r.text)
        print(f"[KABBALE] status={r.status_code} body={r.text[:300]}")
        assert r.status_code in (200, 201), f'kabbale/checkout FAILED: {r.status_code} {r.text[:400]}'

    def test_rencontres_reveal(self, auth_headers):
        """Rencontres — reveal (gratuit, gate freemium)."""
        payload = {
            'day': 15, 'month': 5, 'year': 1990,
            'hour': 12, 'minute': 0,
            'place': 'Paris', 'country': 'France',
            'first_name': 'Admin',
        }
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/rencontres/reveal', headers=auth_headers, json=payload, timeout=60)
        elapsed = time.time() - t0
        _record('rencontres_reveal', '/api/rencontres/reveal', r.status_code, elapsed, r.text)
        print(f"[RENCONTRES REVEAL] status={r.status_code} body={r.text[:300]}")
        assert r.status_code == 200, f'rencontres/reveal FAILED: {r.status_code} {r.text[:400]}'

    def test_rencontres_checkout(self, auth_headers):
        """Rencontres — checkout Ultime 29,99€."""
        payload = {
            'origin_url': BASE_URL,
            'email': 'admin@plume-astrale.fr',
        }
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/rencontres/checkout', headers=auth_headers, json=payload, timeout=30)
        elapsed = time.time() - t0
        _record('rencontres_checkout', '/api/rencontres/checkout', r.status_code, elapsed, r.text)
        print(f"[RENCONTRES CHECKOUT] status={r.status_code} body={r.text[:300]}")
        assert r.status_code in (200, 201), f'rencontres/checkout FAILED: {r.status_code} {r.text[:400]}'

    def test_synastrie_oneshot(self, auth_headers):
        """Synastrie oneshot / free-extract."""
        payload = {
            'person1': {'prenom': 'Admin', 'birth_date': '1990-05-15', 'birth_time': '12:00', 'birth_place': 'Paris'},
            'person2': {'prenom': 'Partenaire', 'birth_date': '1988-03-10', 'birth_time': '14:30', 'birth_place': 'Lyon'},
            'email': 'admin@plume-astrale.fr',
            'consent_marketing': True,
        }
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/synastrie/free-extract', headers=auth_headers, json=payload, timeout=120)
        elapsed = time.time() - t0
        _record('synastrie_oneshot', '/api/synastrie/free-extract', r.status_code, elapsed, r.text)
        print(f"[SYNASTRIE] status={r.status_code} body={r.text[:300]}")
        assert r.status_code == 200, f'synastrie/free-extract FAILED: {r.status_code} {r.text[:400]}'

    def test_premium_status(self, auth_headers):
        t0 = time.time()
        r = requests.get(f'{BASE_URL}/api/premium/status', headers=auth_headers, timeout=15)
        elapsed = time.time() - t0
        _record('premium_status', '/api/premium/status', r.status_code, elapsed, r.text)
        assert r.status_code == 200, f'premium/status FAILED: {r.status_code} {r.text[:200]}'

    def test_plume_chat(self, auth_headers):
        """Chat Soléna."""
        payload = {
            'message': 'Bonjour Soléna',
            'session_id': 'test-iter46',
        }
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/plume-chat', headers=auth_headers, json=payload, timeout=60)
        elapsed = time.time() - t0
        _record('plume_chat', '/api/plume-chat', r.status_code, elapsed, r.text)
        print(f"[PLUME-CHAT] status={r.status_code} time={elapsed:.1f}s body={r.text[:400]}")
        assert r.status_code == 200, f'plume-chat FAILED: {r.status_code} {r.text[:400]}'


# ═══════════════════════ P6 : DISCOUNT ═══════════════════════
class TestDiscount:
    def test_bienvenue(self):
        t0 = time.time()
        r = requests.post(f'{BASE_URL}/api/discount/validate', json={'code': 'BIENVENUE'}, timeout=15)
        elapsed = time.time() - t0
        _record('discount_bienvenue', '/api/discount/validate', r.status_code, elapsed, r.text)
        assert r.status_code == 200
        data = r.json()
        assert data.get('valid') is True, f'BIENVENUE should be valid: {data}'


# ═══════════════════════ FINAL REPORT ═══════════════════════
def test_zzz_print_report():
    """Not really a test — prints the final report table."""
    print('\n\n═══════════════════ FINAL REPORT ═══════════════════')
    print(f"{'PRODUCT':30s} {'STATUS':10s} {'TIME':>8s}  ENDPOINT")
    for name, info in REPORT.items():
        print(f"{name:30s} {str(info['http_status']):10s} {info['response_time_s']:>6.1f}s  {info['endpoint']}")
    print('════════════════════════════════════════════════════\n')
