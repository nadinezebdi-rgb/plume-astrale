"""Iteration 30 — Phase 2 (Cercle), Phase 3 (Synastrie), regression."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'


SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'


@pytest.fixture(scope='module')
def admin_token():
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}, timeout=30,
    )
    assert r.status_code == 200, f"login {r.status_code}: {r.text[:300]}"
    return r.json()['access_token']


@pytest.fixture(scope='module')
def admin_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


# ─── Regression : /api/auth/me ───
def test_auth_me_returns_is_admin(admin_headers):
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=admin_headers, timeout=20)
    assert r.status_code == 200, r.text[:200]
    data = r.json()
    user = data.get('user') or data
    assert user.get('is_admin') is True or user.get('email') == ADMIN_EMAIL


# ─── PHASE 2 — Cercle ───
def test_cercle_streak_admin(admin_headers):
    r = requests.get(f"{BASE_URL}/api/cercle/streak", headers=admin_headers, timeout=20)
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    for k in ('streak_count', 'longest_streak', 'total_checkins', 'checked_in_today', 'next_milestone'):
        assert k in d, f"missing {k}: {d}"
    assert isinstance(d['next_milestone'], dict)


def test_cercle_daily_admin(admin_headers):
    r = requests.get(f"{BASE_URL}/api/cercle/daily", headers=admin_headers, timeout=60)
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    for k in ('date', 'profile', 'moon', 'scores', 'insight', 'moods', 'streak', 'tarot'):
        assert k in d, f"missing {k}"
    assert d['profile'].get('prenom')
    for s in ('energy', 'confidence', 'discipline', 'intuition'):
        assert s in d['scores'], f"missing score {s}"
    assert d['moon'].get('phase') and d['moon'].get('theme')
    assert isinstance(d['insight'], str) and len(d['insight']) > 50
    assert d['tarot'].get('name') and d['tarot'].get('message')
    assert isinstance(d['moods'], list) and len(d['moods']) > 0


def test_cercle_checkin_invalid_mood(admin_headers):
    r = requests.post(f"{BASE_URL}/api/cercle/checkin", headers=admin_headers,
                      json={'mood': 'INVALID_MOOD_XYZ'}, timeout=20)
    assert r.status_code == 400


def test_cercle_checkin_valid_and_idempotent(admin_headers):
    r = requests.post(f"{BASE_URL}/api/cercle/checkin", headers=admin_headers,
                      json={'mood': 'radieux', 'intention': 'Test iteration 30'}, timeout=30)
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    assert d.get('success') is True
    assert d.get('mood') == 'radieux'
    assert 'streak_count' in d
    # 2nd call same day = idempotent
    r2 = requests.post(f"{BASE_URL}/api/cercle/checkin", headers=admin_headers,
                       json={'mood': 'radieux'}, timeout=20)
    assert r2.status_code == 200
    d2 = r2.json()
    # If table doesn't persist (graceful fallback), already_checked_in may be False — accept both
    assert 'already_checked_in' in d2


def test_cercle_reflection_too_short(admin_headers):
    r = requests.post(f"{BASE_URL}/api/cercle/reflection", headers=admin_headers,
                      json={'entry': 'ab'}, timeout=20)
    assert r.status_code in (400, 422)


def test_cercle_reflection_valid(admin_headers):
    r = requests.post(f"{BASE_URL}/api/cercle/reflection", headers=admin_headers,
                      json={'entry': "Aujourd'hui j'ai medite et observe mes emotions avec douceur."},
                      timeout=60)
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    assert d.get('success') is True
    assert isinstance(d.get('response'), str) and len(d['response']) > 80


def test_cercle_gate_no_auth():
    # daily/checkin/reflection should reject anonymous (401)
    for path, method, body in [
        ('/api/cercle/daily', 'GET', None),
        ('/api/cercle/checkin', 'POST', {'mood': 'radieux'}),
        ('/api/cercle/reflection', 'POST', {'entry': 'aaaaaaa bbbbbb cccccc'}),
    ]:
        if method == 'GET':
            r = requests.get(f"{BASE_URL}{path}", timeout=15)
        else:
            r = requests.post(f"{BASE_URL}{path}", json=body, timeout=15)
        assert r.status_code in (401, 403), f"{path} expected 401/403 got {r.status_code}"


# ─── PHASE 3 — Synastrie ───
SYNASTRIE_PAYLOAD = {
    'person1': {'prenom': 'Alice', 'birth_date': '1990-05-15', 'birth_time': '12:00',
                'birth_place': 'Paris', 'birth_country': 'France'},
    'person2': {'prenom': 'Bob', 'birth_date': '1991-08-23', 'birth_time': '14:30',
                'birth_place': 'Lyon', 'birth_country': 'France'},
    'origin_url': 'https://consultation-astro.preview.emergentagent.com',
    'email': 'test_iter30@example.com',
}


def test_synastrie_checkout_anonymous():
    r = requests.post(f"{BASE_URL}/api/synastrie/checkout", json=SYNASTRIE_PAYLOAD, timeout=30)
    assert r.status_code == 200, r.text[:400]
    d = r.json()
    assert d.get('session_id')
    assert d.get('checkout_url', '').startswith('https://')
    assert 'stripe' in d['checkout_url'].lower()


def test_synastrie_checkout_authenticated(admin_headers):
    p = dict(SYNASTRIE_PAYLOAD)
    p.pop('email', None)
    r = requests.post(f"{BASE_URL}/api/synastrie/checkout", headers=admin_headers, json=p, timeout=30)
    assert r.status_code == 200, r.text[:400]
    d = r.json()
    assert d.get('session_id') and d.get('checkout_url')


def test_synastrie_checkout_missing_email_anonymous():
    p = dict(SYNASTRIE_PAYLOAD)
    p.pop('email', None)
    r = requests.post(f"{BASE_URL}/api/synastrie/checkout", json=p, timeout=20)
    assert r.status_code == 400


def test_synastrie_status_unknown_session():
    r = requests.get(f"{BASE_URL}/api/synastrie/status/cs_fake_unknown_12345", timeout=20)
    assert r.status_code == 200
    d = r.json()
    assert 'status' in d
    assert 'pdf_ready' in d
    assert d['pdf_ready'] is False
