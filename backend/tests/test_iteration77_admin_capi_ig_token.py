"""Iteration 77 — Test the 2 new admin endpoints + regression on existing routes.

- GET /api/admin/capi-health        (401 no auth, 403 non-admin, 200 admin)
- POST /api/admin/ig-token/refresh  (401 no auth, 200 admin)
- Regression: /api/tarot/jour, /api/apercu/discount, /api/plume-chat/history
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = "admin@plume-astrale.fr"
ADMIN_PASSWORD = "PlumeAdmin2026"
USER_EMAIL = "test@plume-astrale.fr"
USER_PASSWORD = "TestPlume2026!"

SUPABASE_URL = "https://ebwicqvbkwogxneipaxh.supabase.co"
SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA"


def _supabase_login(email, password):
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPABASE_ANON, "Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def admin_token():
    return _supabase_login(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="module")
def user_token():
    return _supabase_login(USER_EMAIL, USER_PASSWORD)


# ---------------- /api/admin/capi-health ----------------
class TestCapiHealth:
    def test_no_auth_401(self):
        r = requests.get(f"{BASE_URL}/api/admin/capi-health", timeout=15)
        assert r.status_code in (401, 403), f"Expected 401/403 got {r.status_code}: {r.text}"

    def test_non_admin_403(self, user_token):
        r = requests.get(
            f"{BASE_URL}/api/admin/capi-health",
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=15,
        )
        assert r.status_code == 403, f"Expected 403 got {r.status_code}: {r.text}"

    def test_admin_200(self, admin_token):
        r = requests.get(
            f"{BASE_URL}/api/admin/capi-health",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=20,
        )
        assert r.status_code == 200, f"Expected 200 got {r.status_code}: {r.text}"
        data = r.json()
        for k in ("status", "pixel_id", "token_configured", "capi_ok"):
            assert k in data, f"Missing key {k} in response: {data}"
        # token not configured in test env
        assert data["token_configured"] is False
        assert data["status"] == "error"
        assert data["capi_ok"] is False


# ---------------- /api/admin/ig-token/refresh ----------------
class TestIgTokenRefresh:
    def test_no_auth_401(self):
        r = requests.post(f"{BASE_URL}/api/admin/ig-token/refresh", timeout=15)
        assert r.status_code in (401, 403), f"Expected 401/403 got {r.status_code}: {r.text}"

    def test_admin_200(self, admin_token):
        r = requests.post(
            f"{BASE_URL}/api/admin/ig-token/refresh",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=20,
        )
        assert r.status_code == 200, f"Expected 200 got {r.status_code}: {r.text}"
        data = r.json()
        assert "status" in data
        assert "current_token_age_days" in data
        # Without INSTAGRAM_ACCESS_TOKEN → status skipped
        assert data["status"] == "skipped"
        assert data.get("reason") == "no_token_configured"


# ---------------- Regression ----------------
class TestRegression:
    def test_tarot_jour(self):
        r = requests.get(f"{BASE_URL}/api/tarot/jour", timeout=20)
        assert r.status_code == 200, f"Expected 200 got {r.status_code}: {r.text}"

    def test_apercu_discount(self):
        r = requests.post(
            f"{BASE_URL}/api/apercu/discount",
            json={"email": "test-regression@example.com"},
            timeout=20,
        )
        # Accept 200 or 400 (validation)
        assert r.status_code in (200, 400, 409), f"Unexpected {r.status_code}: {r.text}"

    def test_plume_chat_history_no_auth(self):
        r = requests.get(f"{BASE_URL}/api/plume-chat/history/test-session", timeout=15)
        # Should be 401 without auth
        assert r.status_code in (401, 403), f"Expected 401/403 got {r.status_code}: {r.text}"
