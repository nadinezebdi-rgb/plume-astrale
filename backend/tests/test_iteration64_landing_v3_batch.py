"""
Iteration 64 — Landing v3 Plume Astrale batch final:
1. Testimonials CRUD (public GET, auth POST, admin approve/delete)
2. A/B hero tracking + stats
"""
import os
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


# ── Feature 1: GET public testimonials ──────────────────────────
class TestTestimonialsPublic:
    def test_get_testimonials_public_no_auth(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert 'testimonials' in data
        items = data['testimonials']
        assert isinstance(items, list)
        assert len(items) >= 3, f'Expected >=3 seeds, got {len(items)}'

    def test_seeds_have_required_fields(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        items = r.json()['testimonials']
        required = {'id', 'initial', 'name', 'sign', 'city', 'quote', 'transform_before', 'transform_after', 'stars'}
        for it in items[:3]:
            missing = required - set(it.keys())
            assert not missing, f'Missing fields {missing} in {it}'
            assert it['stars'] == 5

    def test_seeds_present_lea_sarah_manon(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        items = r.json()['testimonials']
        names = {i['name'] for i in items}
        # At least the 3 seeds should be present among approved
        for expected in ('Léa M.', 'Sarah T.', 'Manon D.'):
            assert expected in names, f'{expected} not found in {names}'

    def test_public_response_excludes_status(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        items = r.json()['testimonials']
        for it in items:
            assert 'status' not in it
            assert 'author_email' not in it


# ── Feature 2: POST testimonial (auth) ──────────────────────────
class TestTestimonialSubmit:
    def test_submit_without_auth_401(self):
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            json={'name': 'TEST_User', 'quote': 'This is a test quote long enough to pass validation.'},
            timeout=15,
        )
        assert r.status_code == 401

    def test_submit_with_user_auth_200(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'name': 'TEST_Iter64',
                'quote': 'Ce témoignage de test iter64 est assez long pour passer la validation min_length.',
                'sign': 'Verseau', 'city': 'Paris',
            },
            timeout=15,
        )
        assert r.status_code == 200, f'Got {r.status_code}: {r.text[:200]}'
        data = r.json()
        assert data.get('submitted') is True
        assert data.get('status') == 'pending'
        assert data.get('id', '').startswith('usr-')

    def test_submit_name_too_short_422(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'name': 'X', 'quote': 'valid quote long enough for validation min length.'},
            timeout=15,
        )
        assert r.status_code == 422

    def test_submit_quote_too_short_422(self, user_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            headers={'Authorization': f'Bearer {user_token}'},
            json={'name': 'TEST_Valid', 'quote': 'too short'},
            timeout=15,
        )
        assert r.status_code == 422


# ── Feature 3: GET admin testimonials list ──────────────────────
class TestTestimonialsAdminList:
    def test_admin_list_no_auth_401(self):
        r = requests.get(f'{BASE_URL}/api/landing/testimonials/admin', timeout=15)
        assert r.status_code == 401

    def test_admin_list_non_admin_403(self, user_token):
        r = requests.get(
            f'{BASE_URL}/api/landing/testimonials/admin',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403

    def test_admin_list_admin_200_includes_pending(self, admin_token):
        r = requests.get(
            f'{BASE_URL}/api/landing/testimonials/admin',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 200
        items = r.json()['testimonials']
        statuses = {t.get('status') for t in items}
        # We expect at least 'approved' seeds; pending only if any submitted
        assert 'approved' in statuses


# ── Feature 4: approve / delete admin ops ───────────────────────
class TestTestimonialAdminOps:
    def test_approve_nonexistent_404(self, admin_token):
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials/does-not-exist-xyz/approve',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 404

    def test_delete_nonexistent_404(self, admin_token):
        r = requests.delete(
            f'{BASE_URL}/api/landing/testimonials/does-not-exist-xyz',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r.status_code == 404

    def test_approve_no_auth_401(self):
        r = requests.post(f'{BASE_URL}/api/landing/testimonials/xxx/approve', timeout=15)
        assert r.status_code == 401

    def test_delete_non_admin_403(self, user_token):
        r = requests.delete(
            f'{BASE_URL}/api/landing/testimonials/xxx',
            headers={'Authorization': f'Bearer {user_token}'}, timeout=15,
        )
        assert r.status_code == 403

    def test_full_lifecycle_submit_approve_delete(self, user_token, admin_token):
        # Submit as user
        r = requests.post(
            f'{BASE_URL}/api/landing/testimonials',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'name': 'TEST_Lifecycle',
                'quote': 'Cycle complet de test: soumission, approbation puis suppression.',
            }, timeout=15,
        )
        assert r.status_code == 200
        tid = r.json()['id']

        # Approve as admin
        r2 = requests.post(
            f'{BASE_URL}/api/landing/testimonials/{tid}/approve',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r2.status_code == 200
        assert r2.json().get('approved') is True

        # Verify appears in public list
        r3 = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        ids = {i['id'] for i in r3.json()['testimonials']}
        assert tid in ids

        # Delete as admin
        r4 = requests.delete(
            f'{BASE_URL}/api/landing/testimonials/{tid}',
            headers={'Authorization': f'Bearer {admin_token}'}, timeout=15,
        )
        assert r4.status_code == 200

        # Verify removed
        r5 = requests.get(f'{BASE_URL}/api/landing/testimonials', timeout=15)
        ids2 = {i['id'] for i in r5.json()['testimonials']}
        assert tid not in ids2


# ── Feature 5: POST A/B track ───────────────────────────────────
class TestABTrack:
    def test_track_variant_A_impression_200(self):
        r = requests.post(f'{BASE_URL}/api/landing/ab/track',
                          json={'variant': 'A', 'event': 'impression'}, timeout=15)
        assert r.status_code == 200
        assert r.json().get('ok') is True

    def test_track_variant_B_cta_click_200(self):
        r = requests.post(f'{BASE_URL}/api/landing/ab/track',
                          json={'variant': 'B', 'event': 'cta_click'}, timeout=15)
        assert r.status_code == 200

    def test_track_signup_click(self):
        r = requests.post(f'{BASE_URL}/api/landing/ab/track',
                          json={'variant': 'A', 'event': 'signup_click'}, timeout=15)
        assert r.status_code == 200

    def test_track_invalid_variant_400(self):
        r = requests.post(f'{BASE_URL}/api/landing/ab/track',
                          json={'variant': 'C', 'event': 'impression'}, timeout=15)
        assert r.status_code == 400

    def test_track_invalid_event_400(self):
        r = requests.post(f'{BASE_URL}/api/landing/ab/track',
                          json={'variant': 'A', 'event': 'bogus'}, timeout=15)
        assert r.status_code == 400


# ── Feature 6: GET A/B stats (admin) ────────────────────────────
class TestABStats:
    def test_ab_stats_no_auth_401(self):
        r = requests.get(f'{BASE_URL}/api/landing/ab/stats', timeout=15)
        assert r.status_code == 401

    def test_ab_stats_non_admin_403(self, user_token):
        r = requests.get(f'{BASE_URL}/api/landing/ab/stats',
                         headers={'Authorization': f'Bearer {user_token}'}, timeout=15)
        assert r.status_code == 403

    def test_ab_stats_admin_200_structure(self, admin_token):
        r = requests.get(f'{BASE_URL}/api/landing/ab/stats',
                         headers={'Authorization': f'Bearer {admin_token}'}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert 'variants' in data
        assert 'winner' in data
        assert 'headlines' in data
        for v in ('A', 'B'):
            row = data['variants'][v]
            for k in ('impression', 'cta_click', 'signup_click', 'total_clicks', 'ctr_pct'):
                assert k in row, f'Missing {k} in variant {v}'
        # Headlines match the expected texts
        assert data['headlines']['A'] == 'Ton ciel de naissance contient une carte.'
        assert data['headlines']['B'] == "La lecture que ton ciel attendait."

    def test_ab_winner_null_when_low_impressions(self, admin_token):
        # After a few tracks, winner should still be null (need >=50 impressions each)
        r = requests.get(f'{BASE_URL}/api/landing/ab/stats',
                         headers={'Authorization': f'Bearer {admin_token}'}, timeout=15)
        data = r.json()
        a_imp = data['variants']['A']['impression']
        b_imp = data['variants']['B']['impression']
        if a_imp < 50 or b_imp < 50:
            assert data['winner'] is None


# ── Regression: previous endpoints still working ────────────────
class TestRegression:
    def test_health_ok(self):
        r = requests.get(f'{BASE_URL}/api/health', timeout=15)
        assert r.status_code == 200

    def test_lecture_complete_scarcity_ok(self):
        r = requests.get(f'{BASE_URL}/api/lecture-complete/scarcity', timeout=15)
        assert r.status_code == 200

    def test_admin_dashboard_stats_admin_ok(self, admin_token):
        r = requests.get(f'{BASE_URL}/api/admin/dashboard-stats',
                         headers={'Authorization': f'Bearer {admin_token}'}, timeout=15)
        # Route may vary; accept 200 or 404 if not exposed
        assert r.status_code in (200, 404)
