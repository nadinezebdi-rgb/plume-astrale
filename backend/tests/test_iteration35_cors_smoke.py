"""
Iteration 35 — Regression smoke test after 2 fixes:
  1. /app/frontend/src/lib/supabase.js: hardcoded fallbacks removed (env-only)
  2. /app/backend/.env: CORS_ORIGINS=* added

Validates:
- Backend health
- CORS headers present on /api/plume-chat (POST + OPTIONS preflight)
- /api/plume-chat still works with the exact birth_data from the review request
- /api/library/catalog reachable (note: /api/library/list does NOT exist)
- /api/rencontres/reveal reachable
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass


# --- Health ---
class TestHealth:
    def test_api_health(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=15)
        assert r.status_code == 200


# --- CORS on /api/plume-chat ---
class TestCORS:
    def test_preflight_plume_chat(self):
        r = requests.options(
            f"{BASE_URL}/api/plume-chat",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=15,
        )
        assert r.status_code in (200, 204), f"preflight {r.status_code}"
        aco = r.headers.get("access-control-allow-origin")
        assert aco is not None, "Missing Access-Control-Allow-Origin"

    def test_cors_header_on_post(self):
        r = requests.post(
            f"{BASE_URL}/api/plume-chat",
            headers={"Origin": "https://example.com", "Content-Type": "application/json"},
            json={"message": "Bonjour", "session_id": "test-cors-hdr"},
            timeout=90,
        )
        assert r.status_code == 200
        aco = r.headers.get("access-control-allow-origin")
        assert aco is not None, "Missing Access-Control-Allow-Origin on POST"


# --- Review-request exact payload ---
class TestPlumeChatReviewPayload:
    def test_with_birth_data_from_review_request(self):
        body = {
            "message": "Soléna, révèle-moi mon potentiel amoureux.",
            "session_id": "test-review-payload",
            "birth_data": {
                "name": "Test",
                "day": 15,
                "month": 6,
                "year": 1993,
                "hour": 14,
                "min": 30,
                "place": "Paris, France",
            },
        }
        r = requests.post(f"{BASE_URL}/api/plume-chat", json=body, timeout=90)
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") is True, data
        ans = data.get("answer", "")
        assert "🪶 Une plume mystique" in ans[:250]
        assert "##" in ans and "**" in ans and "---" in ans
        assert ans.rstrip().endswith("?")


# --- Other endpoints from review ---
class TestOtherEndpoints:
    def test_library_catalog(self):
        # Review mentioned /api/library/list — actual path is /api/library/catalog.
        r = requests.get(f"{BASE_URL}/api/library/catalog", timeout=15)
        assert r.status_code == 200, f"library/catalog {r.status_code}"

    def test_library_list_does_not_exist(self):
        r = requests.get(f"{BASE_URL}/api/library/list", timeout=15)
        assert r.status_code == 404  # confirms review-request path is wrong

    def test_rencontres_reveal(self):
        r = requests.post(
            f"{BASE_URL}/api/rencontres/reveal",
            json={
                "name": "Test",
                "day": 15,
                "month": 6,
                "year": 1993,
                "hour": 14,
                "min": 30,
                "place": "Paris, France",
            },
            timeout=30,
        )
        assert r.status_code == 200, f"reveal {r.status_code} {r.text[:200]}"
        data = r.json()
        assert "reveal_id" in data
        assert "portrait" in data
