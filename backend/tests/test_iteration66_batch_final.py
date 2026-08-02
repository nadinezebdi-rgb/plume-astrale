"""
Iteration 66 — Plume Astrale batch final validation.
Covers:
 - Slack/log_alert new_testimonial notification
 - A/B hero forced-variant (serve-variant + set-forced-variant)
 - rating-timeseries, trust-stats, testimonials limit param
 - testimonials admin list
 - Chat AI: /api/chat/support, /api/chat/feedback, /api/chat/analytics
 - Regression: /api/health, /api/lecture-complete/checkout basic
"""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
    'eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.'
    'sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'
)

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PWD = 'PlumeAdmin2026'
USER_EMAIL = 'test@plume-astrale.fr'
USER_PWD = 'TestPlume2026!'


def _login(email: str, pwd: str) -> str:
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': email, 'password': pwd},
        timeout=20,
    )
    assert r.status_code == 200, f'Login {email} failed: {r.status_code} {r.text[:200]}'
    return r.json()['access_token']


@pytest.fixture(scope='module')
def admin_token():
    return _login(ADMIN_EMAIL, ADMIN_PWD)


@pytest.fixture(scope='module')
def user_token():
    return _login(USER_EMAIL, USER_PWD)


# ─────────────────────────────────────────────────────────────
# Feature 1: log_alert new_testimonial
# ─────────────────────────────────────────────────────────────
class TestNewTestimonialAlert:
    def test_submit_creates_new_testimonial_alert(self, user_token, admin_token):
        marker = f'TEST_Iter66_{uuid.uuid4().hex[:6]}'
        payload = {
            'name': marker,
            'sign': 'Balance',
            'city': 'Lyon',
            'quote': f'Retour de test iter66 pour valider le log_alert Slack ({marker}).',
        }
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            headers={'Authorization': f'Bearer {user_token}'},
            json=payload, timeout=15,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get('submitted') is True
        assert data.get('status') == 'pending'

        # Let asyncio task complete
        time.sleep(2)

        r2 = requests.get(
            f'{BASE_URL}/api/lecture-complete/admin/settings',
            headers={'Authorization': f'Bearer {admin_token}'},
            timeout=15,
        )
        assert r2.status_code == 200, r2.text
        history = r2.json().get('alerts_history') or []
        assert isinstance(history, list) and len(history) > 0
        # Find our alert
        recent = [h for h in history if h.get('kind') == 'new_testimonial'
                  and marker in (h.get('title') or '')]
        assert recent, f'Expected new_testimonial alert with {marker}. History kinds: {[h.get("kind") for h in history[-10:]]}'


# ─────────────────────────────────────────────────────────────
# Feature 2 & 3: A/B serve-variant + set-forced-variant
# ─────────────────────────────────────────────────────────────
class TestABForcedVariant:
    def test_reset_then_serve_variant_null(self, admin_token):
        # Reset first
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': None}, timeout=15,
        )
        assert r.status_code == 200, r.text
        assert r.json().get('forced_variant') is None

        r2 = requests.get(f'{BASE_URL}/api/landing/ab/serve-variant', timeout=15)
        assert r2.status_code == 200
        d = r2.json()
        # After reset it may still be null unless auto-lock triggers
        assert 'variant' in d and 'forced' in d
        if d['variant'] is None:
            assert d['forced'] is False

    def test_set_variant_A_then_serve_returns_A_forced(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': 'A'}, timeout=15,
        )
        assert r.status_code == 200
        assert r.json().get('forced_variant') == 'A'
        r2 = requests.get(f'{BASE_URL}/api/landing/ab/serve-variant', timeout=15)
        assert r2.status_code == 200
        d = r2.json()
        assert d['variant'] == 'A' and d['forced'] is True

    def test_set_variant_B_then_serve_returns_B_forced(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': 'B'}, timeout=15,
        )
        assert r.status_code == 200
        assert r.json().get('forced_variant') == 'B'
        r2 = requests.get(f'{BASE_URL}/api/landing/ab/serve-variant', timeout=15)
        assert r2.json()['variant'] == 'B'

    def test_set_invalid_variant_400(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': 'invalid'}, timeout=15,
        )
        assert r.status_code == 400

    def test_set_variant_no_token_401(self):
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            json={'variant': 'A'}, timeout=15,
        )
        assert r.status_code == 401

    def test_set_variant_non_admin_403(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'variant': 'A'}, timeout=15,
        )
        assert r.status_code == 403

    def test_final_reset(self, admin_token):
        """Teardown : remet à null pour ne pas bloquer les tests suivants."""
        r = requests.post(
            f'{BASE_URL}/api/landing/ab/set-forced-variant',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'variant': None}, timeout=15,
        )
        assert r.status_code == 200


# ─────────────────────────────────────────────────────────────
# Feature 4: rating-timeseries
# ─────────────────────────────────────────────────────────────
class TestRatingTimeseries:
    def test_default_30_days(self):
        r = requests.get(f'{BASE_URL}/api/landing/rating-timeseries?days=30', timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d.get('days') == 30
        pts = d.get('points') or []
        assert len(pts) == 30
        for p in pts[:3]:
            assert 'date' in p and 'count' in p and 'avg' in p
            assert isinstance(p['count'], int)
            assert isinstance(p['avg'], (int, float))


# ─────────────────────────────────────────────────────────────
# Feature 5: trust-stats
# ─────────────────────────────────────────────────────────────
class TestTrustStats:
    def test_trust_stats_structure(self):
        r = requests.get(f'{BASE_URL}/api/landing/trust-stats', timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ('total_readings', 'approved_reviews', 'average_rating', 'display_count'):
            assert k in d, f'Missing key {k}'
        assert isinstance(d['total_readings'], int)
        assert isinstance(d['approved_reviews'], int)
        assert isinstance(d['display_count'], str)


# ─────────────────────────────────────────────────────────────
# Feature 6 & 7: testimonials limit + admin list
# ─────────────────────────────────────────────────────────────
class TestTestimonialsLimits:
    def test_default_limit_6(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        assert r.status_code == 200
        items = r.json().get('testimonials') or []
        assert len(items) <= 6

    def test_limit_100(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials?limit=100', timeout=15)
        assert r.status_code == 200
        items = r.json().get('testimonials') or []
        assert len(items) <= 100
        # Sorted desc by created_at implicitly ensured server-side; check structure
        if items:
            t = items[0]
            for k in ('id', 'initial', 'quote', 'stars'):
                assert k in t

    def test_admin_list_admin_ok(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/landing/testimonials/admin',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 200
        items = r.json().get('testimonials') or []
        # pending + approved
        statuses = {t.get('status') for t in items}
        assert 'pending' in statuses or 'approved' in statuses

    def test_admin_list_non_admin_403(self, user_token):
        r = requests.get(
            f'{BASE_URL}/api/landing/testimonials/admin',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403


# ─────────────────────────────────────────────────────────────
# Feature 8-11: Chat AI
# ─────────────────────────────────────────────────────────────
class TestChatSupport:
    def test_chat_normal_no_escalate(self):
        r = requests.post(
            f'{BASE_URL}/api/chat/support',
            json={'message': "C'est quoi la garantie ?"}, timeout=45,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        assert d.get('escalate') is False
        assert d.get('session_id')
        assert d.get('exchange_idx') == 0 or isinstance(d.get('exchange_idx'), int)
        assert 'support_email' in d
        assert d.get('reply') and len(d['reply']) > 5
        # store for feedback test
        pytest.chat_session = d['session_id']
        pytest.chat_idx = d['exchange_idx']

    def test_chat_escalate_case(self):
        r = requests.post(
            f'{BASE_URL}/api/chat/support',
            json={'message': "J'ai payé hier et je n'ai rien reçu, aucun PDF."},
            timeout=45,
        )
        assert r.status_code == 200, r.text
        d = r.json()
        # LLM behavior — may or may not escalate; verify at least support_email present
        assert 'support_email' in d
        assert d.get('reply')
        # Prefer escalate=true but tolerate false; check that reply mentions contact
        if d.get('escalate'):
            assert 'contact@plume-astrale.fr' in d['reply'] or 'plume-astrale.fr' in d['reply']

    def test_chat_feedback_ok(self):
        sess = getattr(pytest, 'chat_session', None)
        idx = getattr(pytest, 'chat_idx', None)
        if not sess:
            pytest.skip('no chat session recorded')
        r = requests.post(
            f'{BASE_URL}/api/chat/feedback',
            json={'session_id': sess, 'exchange_idx': idx, 'helpful': True},
            timeout=15,
        )
        assert r.status_code == 200
        assert r.json().get('ok') is True

    def test_chat_feedback_404(self):
        r = requests.post(
            f'{BASE_URL}/api/chat/feedback',
            json={'session_id': 'no-such-sess', 'exchange_idx': 99999, 'helpful': False},
            timeout=15,
        )
        assert r.status_code == 404

    def test_chat_analytics_admin(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/chat/analytics',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 200
        d = r.json()
        for k in ('total_exchanges', 'unique_sessions', 'escalate_rate_pct',
                  'helpful_rate_pct', 'positive_feedback', 'negative_feedback',
                  'faq_gaps', 'recent'):
            assert k in d, f'Missing key {k}'
        assert isinstance(d['faq_gaps'], list)
        assert isinstance(d['recent'], list)
        assert len(d['faq_gaps']) <= 10
        assert len(d['recent']) <= 50

    def test_chat_analytics_non_admin_403(self, user_token):
        r = requests.get(
            f'{BASE_URL}/api/chat/analytics',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403


# ─────────────────────────────────────────────────────────────
# Regression
# ─────────────────────────────────────────────────────────────
class TestRegression:
    def test_health(self):
        r = requests.get(f'{BASE_URL}/api/health', timeout=15)
        assert r.status_code == 200

    def test_lecture_complete_checkout_reachable(self):
        # Just ensure endpoint exists — actual payment may need extra data
        r = requests.post(
            f'{BASE_URL}/api/lecture-complete/checkout',
            json={}, timeout=15,
        )
        # Expect 400/422 (missing fields) — NOT 404 or 500
        assert r.status_code in (400, 401, 422), f'Unexpected {r.status_code}: {r.text[:200]}'
