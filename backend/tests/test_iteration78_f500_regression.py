"""Iteration 78 — F500 conversion audit backend regression."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
SUPABASE_URL = "https://ebwicqvbkwogxneipaxh.supabase.co"
SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA"


def _supabase_login(email, password):
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPABASE_ANON, "Content-Type": "application/json"},
        json={"email": email, "password": password}, timeout=15,
    )
    assert r.status_code == 200, f"supabase login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def user_token():
    return _supabase_login("test@plume-astrale.fr", "TestPlume2026!")


@pytest.fixture(scope="module")
def admin_token():
    return _supabase_login("admin@plume-astrale.fr", "PlumeAdmin2026")


# Regression: auth login returns JWT
def test_login_user_returns_token(user_token):
    assert isinstance(user_token, str) and len(user_token) > 20


# Regression: tarot/jour public endpoint
def test_tarot_jour_public():
    r = requests.get(f"{BASE_URL}/api/tarot/jour", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)


# Regression: plume-chat history requires auth
def test_plume_chat_history_unauth():
    r = requests.get(f"{BASE_URL}/api/plume-chat/history/test-session", timeout=15)
    assert r.status_code in (401, 403)


# Admin endpoint capi-health: 401 without auth
def test_capi_health_unauth():
    r = requests.get(f"{BASE_URL}/api/admin/capi-health", timeout=15)
    assert r.status_code in (401, 403)


# Admin endpoint capi-health: 200 with admin, token_configured false
def test_capi_health_admin(admin_token):
    r = requests.get(
        f"{BASE_URL}/api/admin/capi-health",
        headers={"Authorization": f"Bearer {admin_token}"}, timeout=15
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("token_configured") is False


# Admin endpoint ig-token/refresh: 401 without auth
def test_ig_token_refresh_unauth():
    r = requests.post(f"{BASE_URL}/api/admin/ig-token/refresh", timeout=15)
    assert r.status_code in (401, 403)


# Admin endpoint ig-token/refresh: skipped status
def test_ig_token_refresh_admin(admin_token):
    r = requests.post(
        f"{BASE_URL}/api/admin/ig-token/refresh",
        headers={"Authorization": f"Bearer {admin_token}"}, timeout=15
    )
    assert r.status_code == 200
    assert r.json().get("status") == "skipped"


# Video generator lazy import
def test_video_generator_import():
    import subprocess
    r = subprocess.run(
        ["python", "-c", "import sys; sys.path.insert(0, '/app/backend'); import services.video_generator; print('ok')"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"import failed: {r.stderr}"
    assert "ok" in r.stdout
