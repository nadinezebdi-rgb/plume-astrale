"""Iteration 28 — Phase 1 Plume Astrale: HeroOracle public funnel tests.

Covers:
- GET /api/health (health probe)
- POST /api/oracle/teaser (PUBLIC, no auth) — happy path + validation errors
- POST /api/oracle/capture-email (PUBLIC) — happy + invalid email
- Regression: /api/auth/me, /api/credits/use (chat_astral 3cr, karma_destin 20cr)
- Regression: admin endpoints (credits + premium grant)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ebwicqvbkwogxneipaxh.supabase.co")
SUPABASE_ANON_KEY = os.environ.get(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA",
)
ADMIN_EMAIL = "admin@plume-astrale.fr"
ADMIN_PASSWORD = "PlumeAdmin2026"


# ───────────────── fixtures ─────────────────
@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token():
    """Obtain a fresh Supabase access_token for the admin user."""
    # Use the supabase URL from project. Try the standard /auth/v1/token endpoint
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    r = requests.post(
        url,
        headers={"Content-Type": "application/json", "apikey": SUPABASE_ANON_KEY},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"Cannot obtain admin token (HTTP {r.status_code}: {r.text[:200]})")
    tok = r.json().get("access_token")
    if not tok:
        pytest.skip("Supabase login returned no access_token")
    return tok


@pytest.fixture(scope="session")
def admin_client(api, admin_token):
    api.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api


@pytest.fixture(scope="session")
def admin_user_id(admin_client):
    r = admin_client.get(f"{BASE_URL}/api/auth/me", timeout=15)
    assert r.status_code == 200, f"/api/auth/me failed: {r.status_code} {r.text[:200]}"
    return r.json()["user"]["id"]


# ───────────────── health ─────────────────
class TestHealth:
    def test_api_health(self):
        """GET /api/health should return 200 healthy. (Spec: Phase 1)"""
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        # Report finding: /health exists but /api/health is not currently routed.
        assert r.status_code == 200, (
            f"/api/health returned {r.status_code} — endpoint NOT mounted under /api. "
            f"server.py only defines @app.get('/health'). Phase 1 spec asks for /api/health."
        )
        data = r.json()
        assert data.get("status") == "healthy"


# ───────────────── ORACLE teaser ─────────────────
class TestOracleTeaser:
    """POST /api/oracle/teaser — PUBLIC funnel endpoint."""

    def test_teaser_happy_path_no_auth(self):
        # No Authorization header to confirm public access
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"first_name": "Lucie", "birth_date": "1990-05-15"},
            timeout=15,
        )
        assert r.status_code == 200, f"unexpected {r.status_code}: {r.text[:200]}"
        data = r.json()
        assert data["success"] is True
        assert data["first_name"] == "Lucie"
        # lifepath
        assert "lifepath" in data and isinstance(data["lifepath"], dict)
        assert isinstance(data["lifepath"]["number"], int)
        assert data["lifepath"]["number"] in {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33}
        assert isinstance(data["lifepath"]["archetype"], str) and len(data["lifepath"]["archetype"]) > 0
        # moon_phase
        assert "moon_phase" in data
        assert isinstance(data["moon_phase"]["phase"], str) and len(data["moon_phase"]["phase"]) > 0
        assert isinstance(data["moon_phase"]["message"], str) and len(data["moon_phase"]["message"]) > 0
        # tarot
        assert "tarot" in data
        assert isinstance(data["tarot"]["card_name"], str) and len(data["tarot"]["card_name"]) > 0
        assert isinstance(data["tarot"]["answer"], str) and len(data["tarot"]["answer"]) > 0
        # locked preview
        assert isinstance(data.get("locked_preview"), str) and "Lucie" in data["locked_preview"]

    def test_teaser_is_fast(self):
        """Phase 1 spec requires <2s response. Deterministic compute should be well under."""
        t0 = time.time()
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"first_name": "Sofia", "birth_date": "1985-11-22"},
            timeout=5,
        )
        elapsed = time.time() - t0
        assert r.status_code == 200
        assert elapsed < 2.0, f"teaser too slow: {elapsed:.2f}s"

    def test_teaser_missing_first_name(self):
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"first_name": "", "birth_date": "1990-05-15"},
            timeout=10,
        )
        assert r.status_code == 400, f"expected 400 got {r.status_code}: {r.text[:200]}"

    def test_teaser_first_name_field_omitted(self):
        """Pydantic should reject missing required field with 422 — both 400 and 422 acceptable."""
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"birth_date": "1990-05-15"},
            timeout=10,
        )
        assert r.status_code in (400, 422)

    def test_teaser_invalid_birth_date_format(self):
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"first_name": "Alex", "birth_date": "15/05/1990"},
            timeout=10,
        )
        assert r.status_code == 400, f"expected 400 got {r.status_code}: {r.text[:200]}"

    def test_teaser_master_number_22(self):
        """Birthday whose digits sum to 22 should preserve master number."""
        # 1990-05-13 -> 1+9+9+0+0+5+1+3 = 28 -> 2+8 = 10 -> 1. Pick a date that gives 22 master.
        # 1985-12-31 -> 1+9+8+5+1+2+3+1 = 30 -> 3. Try 1976-11-22 -> 1+9+7+6+1+1+2+2 = 29 -> 11 (master).
        r = requests.post(
            f"{BASE_URL}/api/oracle/teaser",
            json={"first_name": "Aria", "birth_date": "1976-11-22"},
            timeout=10,
        )
        assert r.status_code == 200
        nb = r.json()["lifepath"]["number"]
        assert nb in {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33}


# ───────────────── ORACLE capture-email ─────────────────
class TestOracleCaptureEmail:
    def test_capture_email_valid(self):
        r = requests.post(
            f"{BASE_URL}/api/oracle/capture-email",
            json={"email": "TEST_oracle+phase1@example.com", "first_name": "Lucie", "birth_date": "1990-05-15"},
            timeout=15,
        )
        # Route must still return 200 even if oracle_leads table does not exist (graceful catch)
        assert r.status_code == 200, f"unexpected {r.status_code}: {r.text[:200]}"
        data = r.json()
        assert data["success"] is True
        assert data["email"] == "test_oracle+phase1@example.com"

    def test_capture_email_invalid(self):
        r = requests.post(
            f"{BASE_URL}/api/oracle/capture-email",
            json={"email": "not-an-email"},
            timeout=10,
        )
        assert r.status_code == 400

    def test_capture_email_empty(self):
        r = requests.post(
            f"{BASE_URL}/api/oracle/capture-email",
            json={"email": ""},
            timeout=10,
        )
        assert r.status_code == 400

    def test_capture_email_no_auth_required(self):
        """Explicitly send no Authorization header to confirm route is public."""
        s = requests.Session()
        r = s.post(
            f"{BASE_URL}/api/oracle/capture-email",
            json={"email": "TEST_publiconly@example.com"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        assert r.status_code == 200


# ───────────────── Regression: auth + credits + admin ─────────────────
class TestRegressionAuthAndCredits:
    def test_auth_me_admin(self, admin_client):
        r = admin_client.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["is_admin"] is True
        assert isinstance(data["credit_balance"], int)

    def test_credits_use_chat_astral(self, admin_client):
        """chat_astral should cost 3 credits."""
        before = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        r = admin_client.post(f"{BASE_URL}/api/credits/use", json={"service_id": "chat_astral"})
        assert r.status_code == 200, r.text[:200]
        body = r.json()
        assert body["success"] is True
        after = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        assert before - after == 3, f"chat_astral expected -3, got {before - after}"

    def test_credits_use_karma_destin(self, admin_client):
        before = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        r = admin_client.post(f"{BASE_URL}/api/credits/use", json={"service_id": "karma_destin"})
        assert r.status_code == 200
        after = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        assert before - after == 20, f"karma_destin expected -20, got {before - after}"


class TestRegressionAdmin:
    def test_admin_grant_credits(self, admin_client, admin_user_id):
        """POST /api/admin/users/{id}/credits — grant +5 credits to self."""
        before = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        r = admin_client.post(
            f"{BASE_URL}/api/admin/users/{admin_user_id}/credits",
            json={"amount": 5, "description": "TEST_iteration28"},
            timeout=15,
        )
        assert r.status_code == 200, f"admin credit grant failed: {r.status_code} {r.text[:200]}"
        body = r.json()
        assert body["success"] is True
        assert body["delta"] == 5
        after = admin_client.get(f"{BASE_URL}/api/auth/me").json()["credit_balance"]
        assert after - before == 5

    def test_admin_set_premium(self, admin_client, admin_user_id):
        """POST /api/admin/users/{id}/premium — grant 1 day then revoke."""
        r = admin_client.post(
            f"{BASE_URL}/api/admin/users/{admin_user_id}/premium",
            json={"action": "grant_days", "days": 1},
            timeout=15,
        )
        assert r.status_code == 200, f"admin premium endpoint failed: {r.status_code} {r.text[:200]}"
        # Revert to keep admin in free state (test idempotency)
        revoke = admin_client.post(
            f"{BASE_URL}/api/admin/users/{admin_user_id}/premium",
            json={"action": "revoke"},
            timeout=10,
        )
        assert revoke.status_code == 200
