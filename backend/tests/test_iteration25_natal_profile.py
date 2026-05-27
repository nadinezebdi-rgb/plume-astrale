"""
Iteration 25 — Backend non-regression for natal data sync feature.

Validates:
- GET /api/auth/me returns full user with birth_date/birth_time/birth_place/birth_country/prenom/gender
- PUT /api/auth/profile updates these fields and is reflected in subsequent /me calls
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASS = 'AdminPlume2026!'
USER_EMAIL = 'plume_test_863a0303@gmail.com'
USER_PASS = 'TestPlume2026!'


def _login(email, password):
    r = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_ANON, 'Content-Type': 'application/json'},
        json={'email': email, 'password': password},
        timeout=15,
    )
    assert r.status_code == 200, f'Login failed {r.status_code}: {r.text}'
    return r.json()['access_token']


@pytest.fixture(scope='module')
def admin_token():
    return _login(ADMIN_EMAIL, ADMIN_PASS)


@pytest.fixture(scope='module')
def user_token():
    return _login(USER_EMAIL, USER_PASS)


def _auth(token):
    return {'Authorization': f'Bearer {token}'}


class TestAuthMe:
    """GET /api/auth/me must return all natal fields"""

    def test_admin_me_has_natal(self, admin_token):
        r = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(admin_token), timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert 'user' in data and 'credit_balance' in data
        u = data['user']
        # All natal fields present (may be None) — keys must exist
        for k in ['id', 'email', 'prenom', 'birth_date', 'birth_time',
                  'birth_place', 'birth_country', 'gender', 'is_admin',
                  'is_premium', 'premium_status']:
            assert k in u, f'missing key: {k}'
        assert u['email'] == ADMIN_EMAIL
        assert u['is_admin'] is True
        # Admin should have natal data per seed
        assert u['birth_date'] is not None, 'admin must have birth_date pre-seeded'
        assert u['birth_place'] is not None, 'admin must have birth_place pre-seeded'

    def test_user_me_has_keys(self, user_token):
        r = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(user_token), timeout=15)
        assert r.status_code == 200
        u = r.json()['user']
        for k in ['birth_date', 'birth_time', 'birth_place', 'birth_country', 'prenom', 'gender']:
            assert k in u

    def test_me_unauthenticated(self):
        r = requests.get(f'{BASE_URL}/api/auth/me', timeout=15)
        assert r.status_code in (401, 403)


class TestProfileUpdate:
    """PUT /api/auth/profile must persist & reflect in /me"""

    def test_update_and_verify_persistence(self, user_token):
        # Snapshot current
        before = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(user_token), timeout=15).json()['user']
        original = {
            'prenom': before.get('prenom'),
            'birth_date': before.get('birth_date'),
            'birth_time': before.get('birth_time'),
            'birth_place': before.get('birth_place'),
            'birth_country': before.get('birth_country'),
            'gender': before.get('gender'),
        }

        new_payload = {
            'prenom': 'TestPlume',
            'birth_date': '1992-07-21',
            'birth_time': '14:30',
            'birth_place': 'Lyon',
            'birth_country': 'France',
            'gender': 'female',
        }
        r = requests.put(
            f'{BASE_URL}/api/auth/profile',
            headers={**_auth(user_token), 'Content-Type': 'application/json'},
            json=new_payload, timeout=15,
        )
        assert r.status_code == 200, r.text
        assert r.json().get('success') is True

        # GET /me to verify persistence
        after = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(user_token), timeout=15).json()['user']
        for k, v in new_payload.items():
            actual = after[k]
            # Backend stores TIME as HH:MM:SS — normalize for compare
            if k == 'birth_time' and isinstance(actual, str) and actual.startswith(v):
                continue
            assert actual == v, f'{k} not persisted: got {actual} expected {v}'

        # Restore original (cleanup) — only fields that were not None
        restore = {k: v for k, v in original.items() if v is not None}
        if restore:
            requests.put(
                f'{BASE_URL}/api/auth/profile',
                headers={**_auth(user_token), 'Content-Type': 'application/json'},
                json=restore, timeout=15,
            )

    def test_update_partial_field_only(self, user_token):
        # Only update prenom — other fields untouched
        before = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(user_token), timeout=15).json()['user']
        r = requests.put(
            f'{BASE_URL}/api/auth/profile',
            headers={**_auth(user_token), 'Content-Type': 'application/json'},
            json={'prenom': 'PartialUpdate'}, timeout=15,
        )
        assert r.status_code == 200
        after = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(user_token), timeout=15).json()['user']
        assert after['prenom'] == 'PartialUpdate'
        # birth_date should NOT have changed
        assert after['birth_date'] == before['birth_date']

        # Restore
        if before.get('prenom') is not None:
            requests.put(
                f'{BASE_URL}/api/auth/profile',
                headers={**_auth(user_token), 'Content-Type': 'application/json'},
                json={'prenom': before['prenom']}, timeout=15,
            )

    def test_admin_profile_unchanged_paris(self, admin_token):
        # Admin should remain Paris/1990-05-15 (no test should accidentally overwrite it)
        r = requests.get(f'{BASE_URL}/api/auth/me', headers=_auth(admin_token), timeout=15)
        u = r.json()['user']
        assert u['birth_place'] == 'Paris', f'Admin natal regression: {u["birth_place"]}'
