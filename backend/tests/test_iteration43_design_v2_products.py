"""
Iteration 43 - Design system v2 + 3 new products (Solena, Archetype, Kabbale)
Backend regression tests.
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")

ADMIN_EMAIL = "admin@plume-astrale.fr"
ADMIN_PASSWORD = "PlumeAdmin2026"

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ebwicqvbkwogxneipaxh.supabase.co")
SUPABASE_ANON = os.environ.get(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA",
)


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(session):
    """Sign in as admin via Supabase Auth (password grant)."""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    r = session.post(
        url,
        headers={
            "apikey": SUPABASE_ANON,
            "Content-Type": "application/json",
        },
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"Cannot login admin via Supabase: {r.status_code} {r.text[:200]}")
    data = r.json()
    tok = data.get("access_token")
    if not tok:
        pytest.skip("No access_token in Supabase response")
    return tok


# -----------------------------
# Base health
# -----------------------------
class TestHealth:
    def test_root(self, session):
        r = session.get(f"{BASE_URL}/api/", timeout=15)
        assert r.status_code == 200
        data = r.json()
        # "status ok" tolerant match
        joined = str(data).lower()
        assert "ok" in joined or data.get("status") == "ok" or data.get("message"), data


# -----------------------------
# Kabbale
# -----------------------------
class TestKabbale:
    def test_checkout_creates_stripe_session(self, session):
        payload = {
            "email": "TEST_kabbale@plume-astrale.fr",
            "first_name": "TestKab",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "birth_country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "origin_url": BASE_URL,
        }
        r = session.post(f"{BASE_URL}/api/kabbale/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        assert "url" in data and data["url"].startswith("https://"), data
        assert "session_id" in data and isinstance(data["session_id"], str) and data["session_id"], data
        # Store for status
        pytest.kabbale_session_id = data["session_id"]

    def test_status_returns_state(self, session):
        sid = getattr(pytest, "kabbale_session_id", None)
        if not sid:
            pytest.skip("No session_id from checkout")
        r = session.get(f"{BASE_URL}/api/kabbale/status", params={"session_id": sid}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        for k in ("status", "pdf_ready", "email_sent"):
            assert k in data, f"missing key {k} in {data}"

    def test_checkout_rejects_invalid_email(self, session):
        payload = {
            "email": "",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "origin_url": BASE_URL,
        }
        r = session.post(f"{BASE_URL}/api/kabbale/checkout", json=payload, timeout=10)
        assert r.status_code in (400, 422), r.status_code


# -----------------------------
# Solena GaryVee prompt
# -----------------------------
class TestPlumeChatSolena:
    def test_prompt_is_garyvee(self, session, admin_token):
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "message": "Bonjour Solena, comment vais-je aujourd'hui ?",
            "session_id": f"test_iter43_{os.getpid()}",
        }
        r = session.post(f"{BASE_URL}/api/plume-chat", json=payload, headers=headers, timeout=90)
        assert r.status_code == 200, f"{r.status_code} {r.text[:500]}"
        data = r.json()
        # find text field
        text = ""
        for k in ("message", "response", "content", "reply", "text"):
            if isinstance(data.get(k), str):
                text = data[k]
                break
        if not text:
            # deep-search
            text = str(data)
        assert text, f"Empty response: {data}"

        # Not the old prompt
        assert not text.strip().startswith("🪶 Une plume mystique"), f"Old prompt still active! text={text[:200]}"

        # GaryVee "hook" : ends with a question
        # Look at the last 300 chars for a question mark
        last_chunk = text.strip()[-300:]
        assert "?" in last_chunk, f"No hook question in last part: ...{last_chunk!r}"


# -----------------------------
# Archetype
# -----------------------------
class TestArchetype:
    def test_generate_returns_archetype(self, session, admin_token):
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        # Fetch credits before
        # (we accept whatever balance the wallet has, admin has 9999)
        r = session.post(
            f"{BASE_URL}/api/archetype/generate",
            json={"force_refresh": True},
            headers=headers,
            timeout=90,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:500]}"
        data = r.json()
        assert data.get("success") is True, data
        arc = data.get("archetype") or {}
        # Required keys
        for k in ("profile_name", "dominant", "shadow", "spectrum"):
            assert k in arc, f"missing {k} in archetype: {list(arc.keys())}"
        assert isinstance(arc["dominant"], list), arc["dominant"]
        # credit_balance present (deduction ok)
        assert "credit_balance" in data, data
