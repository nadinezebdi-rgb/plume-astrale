"""
Iteration 63 — Batch 4 features admin cockpit finales :
1. Reset test user (test@plume-astrale.fr / TestPlume2026!)
2. Slack rate limit 30s per-admin
3. SVG cache stats dashboard (/api/admin/cache/svg/stats)
4. Weekly Friday recap email + immediate trigger (/api/lecture-complete/admin/weekly-recap-now)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
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


# ── Feature 1: Reset test user login ────────────────────────────
class TestTestUserLogin:
    def test_test_user_can_login(self):
        tok = _login(USER_EMAIL, USER_PWD)
        assert len(tok) > 20

    def test_test_user_is_not_admin(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/weekly-recap-now',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403


# ── Feature 3: SVG cache stats ──────────────────────────────────
class TestSvgCacheStats:
    def test_no_token_401(self):
        r = requests.get(f'{BASE_URL}/api/admin/cache/svg/stats', timeout=15)
        assert r.status_code == 401

    def test_non_admin_403(self, user_token):
        r = requests.get(
            f'{BASE_URL}/api/admin/cache/svg/stats',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403

    def test_admin_shape(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/admin/cache/svg/stats',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=20,
        )
        assert r.status_code == 200
        d = r.json()
        for k in ('total_files', 'total_size_bytes', 'total_size_human', 'by_chart_type'):
            assert k in d, f'missing key {k}'
        for ct in ('natal', 'transit', 'progression', 'synastry', 'composite', 'solar_return', 'lunar_return'):
            assert ct in d['by_chart_type'], f'missing chart_type {ct}'
            assert 'files' in d['by_chart_type'][ct]
            assert 'size_bytes' in d['by_chart_type'][ct]
        assert isinstance(d['total_files'], int)
        assert isinstance(d['total_size_bytes'], int)


# ── Feature 4: Weekly recap immediate trigger ───────────────────
class TestWeeklyRecapNow:
    def test_no_token_401(self):
        r = requests.post(f'{BASE_URL}/api/lecture-complete/admin/weekly-recap-now', timeout=15)
        assert r.status_code == 401

    def test_non_admin_403(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/weekly-recap-now',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403

    def test_admin_send_and_alerts_history(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/weekly-recap-now',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=45,
        )
        assert r.status_code == 200
        d = r.json()
        assert 'sent_to' in d
        assert 'stats' in d
        stats = d['stats']
        for k in ('paid', 'refunded', 'rate_pct', 'revenue_eur', 'top_refund_reasons', 'j30_variants', 'forced_j30_variant'):
            assert k in stats, f'missing stats.{k}'
        # Give the log_alert a moment (sync but safe)
        time.sleep(1)
        # alerts_history should contain a weekly_recap entry (if sent > 0)
        if d['sent_to'] > 0:
            r2 = requests.get(
                f'{BASE_URL}/api/lecture-complete/admin/settings',
                headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
            )
            assert r2.status_code == 200
            hist = r2.json().get('alerts_history') or []
            kinds = [h.get('kind') for h in hist]
            assert 'weekly_recap' in kinds, f'weekly_recap missing from alerts_history: {kinds[:10]}'


# ── Feature 2: Slack rate limit 30s per-admin ───────────────────
class TestSlackRateLimit:
    def _reset_cooldown(self, admin_token):
        """Reset via set_setting endpoint if available — otherwise just wait 30s."""
        # No public reset endpoint; rely on cooldown expiry
        pass

    def test_rate_limit_429_on_second_call(self, admin_token):
        # First call — either succeeds or fails Slack-side, but status 200
        # If cooldown from previous test still active, wait
        # Try one call to prime; if we get 429, wait for it to expire.
        r1 = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/test-slack',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={}, timeout=15,
        )
        if r1.status_code == 429:
            # Parse remaining
            detail = r1.json().get('detail', '')
            import re
            m = re.search(r'(\d+)s', detail)
            wait_s = int(m.group(1)) + 2 if m else 32
            print(f'[test] cooldown detected, waiting {wait_s}s...')
            time.sleep(wait_s)
            r1 = requests.post(
                f'{BASE_URL}/api/lecture-complete/admin/test-slack',
                headers={'Authorization': f'Bearer {admin_token}'},
                json={}, timeout=15,
            )
        assert r1.status_code == 200, f'first call unexpected status {r1.status_code}: {r1.text[:200]}'

        # Second immediate call → 429
        r2 = requests.post(
            f'{BASE_URL}/api/lecture-complete/admin/test-slack',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={}, timeout=15,
        )
        assert r2.status_code == 429, f'expected 429, got {r2.status_code}: {r2.text[:200]}'
        detail = r2.json().get('detail', '')
        assert 'Cooldown' in detail, f'unexpected detail: {detail}'
        assert 'patienter' in detail.lower() or 'patient' in detail.lower()


# ── Feature 5: weekly_insights module import ────────────────────
class TestWeeklyInsightsModule:
    def test_import_module(self):
        from services import weekly_insights
        assert hasattr(weekly_insights, 'weekly_insights_loop')
        assert hasattr(weekly_insights, 'send_weekly_recap_now')


# ── Regression: iter62 endpoints still work ─────────────────────
class TestRegressionIter62:
    def test_admin_orders(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/orders',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=20,
        )
        assert r.status_code == 200

    def test_admin_ab_stats(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/ab-stats',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=20,
        )
        assert r.status_code == 200

    def test_admin_settings(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/settings',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 200
        d = r.json()
        assert 'forced_j30_variant' in d
        assert 'alerts_history' in d

    def test_admin_orders_export(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/orders/export',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=30,
        )
        assert r.status_code == 200


# ── Regression: landing scarcity + checkout ─────────────────────
class TestRegressionLanding:
    def test_scarcity_200(self):
        r = requests.get(f'{BASE_URL}/api/lecture-complete/scarcity', timeout=15)
        assert r.status_code == 200

    def test_checkout_valid_email(self):
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/checkout',
            json={'email': 'regression-iter63@plume-astrale.fr', 'origin_url': 'https://plume-astrale.fr'},
            timeout=30,
        )
        # 200 (session created) — accept 400/402 only if payload is missing something
        assert r.status_code in (200, 201), f'checkout failed: {r.status_code} {r.text[:200]}'
