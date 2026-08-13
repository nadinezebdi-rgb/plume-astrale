"""
Iteration 76 — Cercle Soléna monthly report admin endpoints.

Tests:
1. GET /api/admin/cercle-monthly-report/preview
   - Admin: returns application/pdf > 20KB
   - Non-admin: 403
   - No token: 401
2. POST /api/admin/cercle-monthly-report/send-all
   - Admin: returns JSON with sent/failed/skipped/total keys
   - Non-admin: 403
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PWD = 'PlumeAdmin2026'
USER_EMAIL = 'test@plume-astrale.fr'
USER_PWD = 'TestPlume2026!'


def _login(email: str, pwd: str) -> str:
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': email, 'password': pwd},
        timeout=15,
    )
    assert r.status_code == 200, f'Login {email} failed: {r.status_code} {r.text[:200]}'
    tok = r.json().get('access_token')
    assert tok
    return tok


@pytest.fixture(scope='module')
def admin_token():
    return _login(ADMIN_EMAIL, ADMIN_PWD)


@pytest.fixture(scope='module')
def user_token():
    return _login(USER_EMAIL, USER_PWD)


PREVIEW_URL = f'{BASE_URL}/api/admin/cercle-monthly-report/preview'
SEND_ALL_URL = f'{BASE_URL}/api/admin/cercle-monthly-report/send-all'


# ─── PDF preview ───────────────────────────────────────────
class TestCerclePdfPreview:
    def test_preview_admin_returns_pdf(self, admin_token):
        r = requests.get(
            PREVIEW_URL,
            params={'sign': 'Bélier', 'element': 'Feu', 'month': 0, 'first_name': 'Camille'},
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=60,
        )
        assert r.status_code == 200, f'{r.status_code}: {r.text[:300]}'
        assert r.headers.get('content-type', '').startswith('application/pdf'), r.headers
        assert r.content[:4] == b'%PDF', 'Not a valid PDF magic bytes'
        assert len(r.content) > 20 * 1024, f'PDF too small: {len(r.content)} bytes (expected >20KB)'

    def test_preview_non_admin_returns_403(self, user_token):
        r = requests.get(
            PREVIEW_URL,
            params={'sign': 'Bélier', 'element': 'Feu', 'month': 0, 'first_name': 'Camille'},
            headers={'Authorization': f'Bearer {user_token}'},
            timeout=30,
        )
        assert r.status_code == 403, f'Expected 403 got {r.status_code}: {r.text[:200]}'
        assert 'administrateur' in r.text.lower() or 'admin' in r.text.lower()

    def test_preview_no_token_returns_401(self):
        r = requests.get(
            PREVIEW_URL,
            params={'sign': 'Bélier', 'element': 'Feu', 'month': 0, 'first_name': 'Camille'},
            timeout=30,
        )
        assert r.status_code == 401, f'Expected 401 got {r.status_code}: {r.text[:200]}'


# ─── Send-all trigger ──────────────────────────────────────
class TestCercleSendAll:
    def test_send_all_admin_returns_json_shape(self, admin_token):
        r = requests.post(
            SEND_ALL_URL,
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=120,
        )
        assert r.status_code == 200, f'{r.status_code}: {r.text[:300]}'
        data = r.json()
        for k in ('sent', 'failed', 'skipped', 'total'):
            assert k in data, f'Missing key {k} in {data}'
            assert isinstance(data[k], int), f'{k} not int: {type(data[k])}'

    def test_send_all_non_admin_returns_403(self, user_token):
        r = requests.post(
            SEND_ALL_URL,
            headers={'Authorization': f'Bearer {user_token}'},
            timeout=30,
        )
        assert r.status_code == 403, f'Expected 403 got {r.status_code}: {r.text[:200]}'
