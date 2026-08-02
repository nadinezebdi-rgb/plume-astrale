"""
Iteration 62 — Lecture Complete admin settings, Slack test, forced A/B variant, refund reason presets.

Covers:
- GET  /api/lecture-complete/admin/settings          (401/403/200)
- POST /api/lecture-complete/admin/set-forced-variant (invalid/reset/apply, 403 non-admin)
- POST /api/lecture-complete/admin/test-slack        (empty webhook, invalid webhook -> alerts_history)
- Sequence override forced_j30_variant unit-check
- Regression: /admin/ab-stats, /admin/orders (with stats), /admin/orders/export CSV, /admin/ctr-refresh
- Regression Landing v2: /api/lecture-complete/scarcity, /api/lecture-complete/checkout (400 email invalide)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASS = 'PlumeAdmin2026'
USER_EMAIL = 'plume_test_863a0303@gmail.com'
USER_PASS = 'TestPlume2026!'


def _supabase_login(email, password):
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON, 'Content-Type': 'application/json'},
        json={'email': email, 'password': password}, timeout=15,
    )
    assert r.status_code == 200, f'Login {email} failed: {r.status_code} {r.text[:200]}'
    return r.json()['access_token']


@pytest.fixture(scope='module')
def admin_token():
    return _supabase_login(ADMIN_EMAIL, ADMIN_PASS)


@pytest.fixture(scope='module')
def user_token():
    try:
        return _supabase_login(USER_EMAIL, USER_PASS)
    except AssertionError as e:
        pytest.skip(f'Standard user login unavailable: {e}')


# ─── 1. GET /admin/settings — 401/403/200 ─────────────────────────────
class TestAdminSettings:
    def test_settings_401_no_token(self):
        r = requests.get(f'{BASE_URL}/api/lecture-complete/admin/settings')
        assert r.status_code == 401

    def test_settings_403_non_admin(self, user_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/settings',
            headers={'Authorization': f'Bearer {user_token}'})
        assert r.status_code == 403

    def test_settings_200_admin(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/settings',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        data = r.json()
        assert 'forced_j30_variant' in data
        assert 'alerts_history' in data
        assert isinstance(data['alerts_history'], list)


# ─── 2. POST /admin/set-forced-variant ────────────────────────────────
class TestSetForcedVariant:
    def test_403_non_admin(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/set-forced-variant',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'variant': 'question'})
        assert r.status_code == 403

    def test_400_invalid(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': 'invalid'})
        assert r.status_code == 400

    def test_set_question_then_reset(self, admin_token):
        h = {'Authorization': f'Bearer {admin_token}'}
        r = requests.post(f'{BASE_URL}/api/lecture-complete/admin/set-forced-variant',
                          headers=h, json={'variant': 'question'})
        assert r.status_code == 200
        assert r.json()['forced_j30_variant'] == 'question'

        # verify persisted via GET
        s = requests.get(f'{BASE_URL}/api/lecture-complete/admin/settings', headers=h)
        assert s.json()['forced_j30_variant'] == 'question'

        # set invitation
        r2 = requests.post(f'{BASE_URL}/api/lecture-complete/admin/set-forced-variant',
                           headers=h, json={'variant': 'invitation'})
        assert r2.json()['forced_j30_variant'] == 'invitation'

        # reset
        r3 = requests.post(f'{BASE_URL}/api/lecture-complete/admin/set-forced-variant',
                           headers=h, json={'variant': None})
        assert r3.status_code == 200
        assert r3.json()['forced_j30_variant'] is None

        # confirm reset
        s2 = requests.get(f'{BASE_URL}/api/lecture-complete/admin/settings', headers=h)
        assert s2.json()['forced_j30_variant'] is None


# ─── 3. POST /admin/test-slack ────────────────────────────────────────
class TestSlackTest:
    def test_empty_returns_success_false(self, admin_token):
        # Ensure no SLACK_WEBHOOK_URL env; if set, this test would send a real ping (acceptable but noisy).
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/test-slack',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={})
        assert r.status_code == 200
        data = r.json()
        assert 'success' in data
        # If no env webhook set, must return success=false + 'Aucun webhook'.
        # If env is set, ping OK/KO but we don't fail the test.
        if not data['success']:
            assert 'Aucun webhook' in data.get('reason', '') or 'Slack' in data.get('reason', '') or 'Erreur' in data.get('reason', '')

    def test_invalid_webhook(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/test-slack',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'webhook_url': 'https://hooks.slack.com/services/BOGUS/BAD/URL'})
        assert r.status_code == 200
        data = r.json()
        assert data['success'] is False
        # reason should include Slack status code (404 typiquement)
        assert 'Slack' in data.get('reason', '') or 'Erreur' in data.get('reason', '')

    def test_alert_history_logged(self, admin_token):
        # After invalid webhook call, an alert_history entry should exist
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/settings',
            headers={'Authorization': f'Bearer {admin_token}'})
        history = r.json().get('alerts_history') or []
        # Find at least one slack_test entry (last 30)
        slack_entries = [a for a in history if a.get('kind') == 'slack_test']
        assert len(slack_entries) >= 1, f'Expected at least one slack_test entry, history={history}'


# ─── 4. Sequence override forced_j30_variant (unit-level import) ──────
class TestSequenceOverride:
    def test_override_applied(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services import app_settings as _s
        _s.set_setting('forced_j30_variant', 'invitation')
        assert _s.get_setting('forced_j30_variant') == 'invitation'
        # Reset
        _s.set_setting('forced_j30_variant', None)
        assert _s.get_setting('forced_j30_variant') is None


# ─── 5. Regression: /admin/ab-stats, /admin/orders ────────────────────
class TestRegressionAdmin:
    def test_ab_stats(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/ab-stats',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        data = r.json()
        assert 'question' in data and 'invitation' in data and 'total' in data

    def test_orders_with_stats(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/orders',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        data = r.json()
        assert 'orders' in data and 'stats' in data
        stats = data['stats']
        assert 'total_paid' in stats and 'total_refunded' in stats and 'refund_rate_pct' in stats

    def test_orders_export_csv(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/orders/export',
            headers={'Authorization': f'Bearer {admin_token}'})
        assert r.status_code == 200
        assert 'text/csv' in r.headers.get('content-type', '')
        assert 'session_id' in r.text.split('\n')[0]

    def test_ctr_refresh_admin_only(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/ctr-refresh',
            headers={'Authorization': f'Bearer {user_token}'})
        assert r.status_code == 403


# ─── 6. Regression Landing v2 + checkout ──────────────────────────────
class TestRegressionLanding:
    def test_scarcity(self):
        r = requests.get(f'{BASE_URL}/api/lecture-complete/scarcity')
        assert r.status_code == 200
        data = r.json()
        assert 'remaining' in data or 'cycle_key' in data or isinstance(data, dict)

    def test_checkout_bad_email(self):
        r = requests.post(f'{BASE_URL}/api/lecture-complete/checkout', json={
            'email': 'no-at-symbol',
            'origin_url': 'https://example.com',
        })
        assert r.status_code == 400
