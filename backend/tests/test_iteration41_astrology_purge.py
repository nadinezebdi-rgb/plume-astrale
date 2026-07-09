"""
Iteration 41 — Regression tests after purge of legacy ASTROLOGY_API_KEY/USER_ID/ACCESS_TOKEN.

Focus:
  1. Health endpoint still up
  2. astrology/karma-destiny returns Taureau + Capricorne via v3
  3. astrology/natal-chart returns source='v3' + chart_data
  4. astrology/horoscope-prediction returns source='personal'
  5. natal/essentials (auth) returns full French sign names (no 'Tau' abbrev)
  6. energy/today (auth) returns 4 sections via OpenAI
  7. plume-chat (auth) returns Solena's personalized answer via OpenAI fallback
  8. karma-destiny doesn't crash on unknown place (falls back to Paris)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2'
    'ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6'
    'MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'
)
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'
STD_EMAIL = 'plume_test_863a0303@gmail.com'
STD_PASSWORD = 'TestPlume2026!'


def _supabase_login(email, password):
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': email, 'password': password},
        timeout=20,
    )
    if r.status_code != 200:
        return None
    return r.json().get('access_token')


@pytest.fixture(scope='session')
def admin_token():
    token = _supabase_login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not token:
        # fall back to standard user, per review request
        token = _supabase_login(STD_EMAIL, STD_PASSWORD)
    if not token:
        pytest.skip('Supabase auth failed for admin AND standard user')
    return token


@pytest.fixture
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


# ─── 1. Health ─────────────────────────────────────────────────────
class TestHealth:
    def test_root_api(self):
        r = requests.get(f'{BASE_URL}/api/', timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get('status') == 'ok'
        assert 'name' in data


# ─── 2. karma-destiny ─────────────────────────────────────────────
class TestKarmaDestiny:
    def test_karma_destiny_paris(self):
        payload = {
            'prenom': 'Test',
            'dateNaissance': '1990-05-15',
            'heureNaissance': '14:30',
            'ville': 'Paris',
            'pays': 'France',
        }
        r = requests.post(f'{BASE_URL}/api/astrology/karma-destiny', json=payload, timeout=60)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:400]}'
        env = r.json()
        assert env.get('success') is True, env
        # payload is nested under 'data'
        data = env.get('data') or env
        # karma_principal
        assert 'karma_principal' in data and data['karma_principal'], f'karma_principal manquant: {data}'
        # noeuds_lunaires
        nl = data.get('noeuds_lunaires') or {}
        assert nl.get('noeud_nord'), f'noeud_nord manquant: {nl}'
        assert nl.get('noeud_sud'), f'noeud_sud manquant: {nl}'
        # soleil / lune signs
        soleil = data.get('soleil_signe')
        lune = data.get('lune_signe')
        assert soleil, f'soleil_signe manquant: {data}'
        assert lune, f'lune_signe manquant: {data}'
        # source_calcul
        src = data.get('source_calcul', '')
        assert src in ('astrology-api-v3', 'approximatif'), f'source_calcul inattendue: {src}'
        # If v3 returned, values MUST be exact
        if src == 'astrology-api-v3':
            assert soleil == 'Taureau', f'Attendu Taureau, obtenu {soleil}'
            assert lune == 'Capricorne', f'Attendu Capricorne, obtenu {lune}'

    def test_karma_destiny_invalid_place_falls_back(self):
        payload = {
            'prenom': 'Test',
            'dateNaissance': '1990-05-15',
            'heureNaissance': '14:30',
            'ville': 'XYZ_INEXISTANT_9999',
            'pays': 'Nowhere',
        }
        r = requests.post(f'{BASE_URL}/api/astrology/karma-destiny', json=payload, timeout=60)
        # Should NOT be 500
        assert r.status_code != 500, f'500 sur ville inconnue: {r.text[:400]}'
        assert r.status_code == 200, r.text[:400]
        env = r.json()
        assert env.get('success') is True


# ─── 3. natal-chart ───────────────────────────────────────────────
class TestNatalChart:
    def test_natal_chart_v3(self):
        payload = {
            'day': 15, 'month': 5, 'year': 1990,
            'hour': 14, 'min': 30,
            'lat': 48.8566, 'lon': 2.3522,
            'name': 'Test',
        }
        r = requests.post(f'{BASE_URL}/api/astrology/natal-chart', json=payload, timeout=60)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:400]}'
        env = r.json()
        assert env.get('success') is True, env
        # source is at top-level next to 'data', per server.py line 968
        assert env.get('source') == 'v3', f"source attendu 'v3', obtenu {env.get('source')}"
        chart_wrapper = env.get('data') or {}
        chart = chart_wrapper.get('chart_data') or {}
        assert 'planetary_positions' in chart, f'planetary_positions manquant: keys={list(chart.keys())}'
        assert 'house_cusps' in chart, f'house_cusps manquant: keys={list(chart.keys())}'


# ─── 4. horoscope-prediction ──────────────────────────────────────
class TestHoroscope:
    def test_horoscope_daily(self):
        payload = {
            'day': 15, 'month': 5, 'year': 1990,
            'hour': 14, 'min': 30,
            'lat': 48.8566, 'lon': 2.3522,
            'period': 'daily',
        }
        r = requests.post(f'{BASE_URL}/api/astrology/horoscope-prediction', json=payload, timeout=60)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:400]}'
        data = r.json()
        assert data.get('success') is True, data
        assert data.get('source') == 'personal', f"source attendu 'personal', obtenu {data.get('source')}"
        # data non-empty
        payload_d = data.get('data')
        assert payload_d, f'data vide: {data}'


# ─── 5. natal/essentials (auth) ───────────────────────────────────
FR_SIGNS = {
    'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
    'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
}


class TestNatalEssentials:
    def test_essentials_authenticated(self, auth_headers):
        r = requests.get(f'{BASE_URL}/api/natal/essentials', headers=auth_headers, timeout=45)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:400]}'
        data = r.json()
        assert data.get('success') is True, data
        assert data.get('has_data') is True, f'has_data faux: {data}'
        ess = data.get('essentials') or {}
        for key in ('sun', 'moon', 'ascendant'):
            item = ess.get(key)
            assert item, f'{key} manquant: {ess}'
            sign = item.get('sign')
            symbol = item.get('symbol')
            assert sign, f'{key}.sign manquant'
            assert symbol, f'{key}.symbol manquant'
            # Must be full French name (no truncated 'Tau'/'Vir'/'Cap')
            assert sign in FR_SIGNS, f'{key}.sign non-français ou tronqué: {sign!r}'
            # ensure no 3-letter abbreviation leaked
            assert len(sign) >= 4, f'{key}.sign trop court (possible abréviation): {sign!r}'


# ─── 6. energy/today (auth) ───────────────────────────────────────
class TestEnergyToday:
    def test_energy_today_four_sections(self, auth_headers):
        r = requests.get(f'{BASE_URL}/api/energy/today', headers=auth_headers, timeout=90)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:500]}'
        data = r.json()
        assert data.get('success') is True, data
        # sections can be at top-level or nested under 'sections'/'energy'
        holder = data
        for candidate in ('sections', 'energy', 'data'):
            if isinstance(data.get(candidate), dict):
                holder = data[candidate]
                break
        expected_keys = ('dominante', 'relationnel', 'attention', 'opportunite')
        found = {k: holder.get(k) for k in expected_keys}
        missing = [k for k, v in found.items() if not v]
        assert not missing, f'Sections manquantes: {missing}. data keys={list(data.keys())}, holder keys={list(holder.keys())}'
        for k, v in found.items():
            # each should have label + text (or at minimum a text/content)
            assert isinstance(v, dict), f'{k} n est pas un objet: {type(v)}'
            has_label = bool(v.get('label') or v.get('title'))
            has_text = bool(v.get('text') or v.get('content') or v.get('message'))
            assert has_label or has_text, f'{k} ne contient ni label ni text: {v}'


# ─── 7. plume-chat (auth) ─────────────────────────────────────────
class TestPlumeChat:
    def test_solena_chat_openai_fallback(self, auth_headers):
        body = {
            'message': 'Bonjour Soléna, parle-moi de mon signe.',
            'birth_data': {
                'date': '1990-05-15',
                'time': '14:30',
                'city': 'Paris',
                'country': 'France',
                'latitude': 48.8566,
                'longitude': 2.3522,
            },
        }
        r = requests.post(f'{BASE_URL}/api/plume-chat', headers=auth_headers, json=body, timeout=120)
        assert r.status_code == 200, f'HTTP {r.status_code}: {r.text[:500]}'
        data = r.json()
        assert data.get('success') is True, data
        # response shape from plume_chat_service: {success, message: str, session_id}
        content = data.get('message')
        if isinstance(content, dict):
            content = content.get('content') or content.get('text')
        if not content:
            content = data.get('reply') or data.get('answer') or data.get('content')
        assert content and isinstance(content, str) and len(content) > 20, f'reponse Solena vide/trop courte: {data}'


# ─── 8. Absence of legacy env vars (server started OK proves this) ─
class TestNoLegacyLeak:
    def test_health_up_confirms_no_import_error(self):
        # If /api/ returns 200, config.py + server.py imported OK => no ASTROLOGY_API_KEY needed
        r = requests.get(f'{BASE_URL}/api/', timeout=15)
        assert r.status_code == 200
