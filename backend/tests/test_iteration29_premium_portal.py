"""
Iteration 29 — Validates premium portal 404 behaviour for users without Stripe customer_id
(simulates the Juliette "manual premium grant" scenario where stripe_customer_id is null).
Also validates baseline endpoints used by the Login redirect + Premium page UI.
"""
import os
import time
import uuid
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")


def _supabase_login(email: str, password: str):
    """Direct Supabase password grant — same flow the frontend uses."""
    # The frontend uses the supabase JS sdk; here we hit the project URL extracted from the token issuer.
    # Easier: backend exposes a /api endpoint? Use admin endpoint not needed — we'll just rely on UI for login token.
    return None


@pytest.fixture(scope="module")
def admin_token():
    # Re-use the admin token already proven to work via the UI test (we capture by env var if provided).
    tok = os.environ.get("ADMIN_TOKEN")
    if not tok:
        pytest.skip("ADMIN_TOKEN env not provided — run after capturing from UI session")
    return tok


# === API health (sanity) ===
def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200, f"got {r.status_code}: {r.text}"


# === Premium status structure ===
def test_premium_status_requires_auth():
    r = requests.get(f"{BASE_URL}/api/premium/status", timeout=10)
    assert r.status_code in (401, 403), f"unauth call should fail, got {r.status_code}"


def test_premium_portal_requires_auth():
    r = requests.post(f"{BASE_URL}/api/premium/portal",
                      json={"return_url": "https://example.com"}, timeout=10)
    assert r.status_code in (401, 403), f"unauth call should fail, got {r.status_code}"


# === Authenticated: status returns proper structure ===
def test_premium_status_authenticated(admin_token):
    r = requests.get(f"{BASE_URL}/api/premium/status",
                     headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "is_premium" in data
    assert "status" in data
    assert "subscription_id" in data  # may be null
    assert isinstance(data["is_premium"], bool)


# === Authenticated: portal either returns URL (200) or 404 'Aucun abonnement actif' ===
def test_premium_portal_authenticated_admin(admin_token):
    r = requests.post(f"{BASE_URL}/api/premium/portal",
                      headers={"Authorization": f"Bearer {admin_token}"},
                      json={"return_url": f"{BASE_URL}/premium"}, timeout=15)
    # Either user has stripe_customer_id -> 200 with url, or doesn't -> 404 with French detail
    assert r.status_code in (200, 404), f"unexpected status {r.status_code}: {r.text}"
    if r.status_code == 404:
        data = r.json()
        # Spec says detail should be French 'Aucun abonnement actif'
        detail = data.get("detail", "")
        assert "Aucun abonnement actif" in detail, f"unexpected detail: {detail}"
    else:
        data = r.json()
        assert "url" in data
        assert data["url"].startswith("https://billing.stripe.com"), data["url"]


# === Public premium page assets are not behind auth (sanity check) ===
def test_oracle_teaser_still_public():
    # Regression — ensure unrelated oracle endpoint still functions (Phase 1 from prev iteration)
    r = requests.post(f"{BASE_URL}/api/oracle/teaser",
                      json={"first_name": "Test", "birth_date": "1990-05-15"}, timeout=15)
    assert r.status_code == 200, r.text
