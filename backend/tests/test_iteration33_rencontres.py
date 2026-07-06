"""
Iteration 33 — Backend tests for Rencontres Astrales (Decodeur du Destin Amoureux)

Covers:
- POST /api/rencontres/reveal (public)
- POST /api/rencontres/capture (public)
- POST /api/rencontres/checkout (public, Stripe)
- Invalid input → 400
- Expired reveal_id → 410
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")

VALID_BIRTH = {
    "day": 15, "month": 5, "year": 1990,
    "hour": 12, "minute": 0,
    "place": "Paris", "country": "France",
    "first_name": "Test",
}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def reveal_data(api):
    """Do a single reveal used by capture / checkout tests to share reveal_id."""
    r = api.post(f"{BASE_URL}/api/rencontres/reveal", json=VALID_BIRTH, timeout=30)
    assert r.status_code == 200, f"reveal setup failed: {r.status_code} {r.text}"
    return r.json()


# ═══════════════════════════════════════════════════════════════
# C.1 — /reveal happy path
# ═══════════════════════════════════════════════════════════════
class TestReveal:
    def test_reveal_success_shape(self, api):
        r = api.post(f"{BASE_URL}/api/rencontres/reveal", json=VALID_BIRTH, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text}"
        d = r.json()

        # reveal_id (uuid hex, 32 chars)
        assert "reveal_id" in d
        assert isinstance(d["reveal_id"], str)
        assert len(d["reveal_id"]) == 32

        # house7_sign — French sign
        french_signs = {"Belier", "Taureau", "Gemeaux", "Cancer", "Lion", "Vierge",
                        "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons"}
        assert d["house7_sign"] in french_signs, f"unexpected sign: {d['house7_sign']}"

        # element must be French (Feu/Air/Eau/Terre)
        assert d["element"] in {"Feu", "Air", "Eau", "Terre"}, f"element={d['element']}"

        # portrait non-empty and contains markdown bold
        assert isinstance(d["portrait"], str) and len(d["portrait"]) > 50
        assert "**" in d["portrait"], "portrait should contain **bold** markdown"

        # next_step exists
        assert "next_step" in d and len(d["next_step"]) > 0

    def test_reveal_missing_place_400(self, api):
        payload = dict(VALID_BIRTH, place="")
        r = api.post(f"{BASE_URL}/api/rencontres/reveal", json=payload, timeout=30)
        assert r.status_code == 400, f"expected 400 for empty place, got {r.status_code}: {r.text}"
        # French error message
        detail = (r.json().get("detail") or "").lower()
        assert any(word in detail for word in ("donnees", "invalides", "naissance", "invalide")), \
            f"error not in French: {detail}"

    def test_reveal_invalid_date_400(self, api):
        payload = dict(VALID_BIRTH, month=13, day=32)
        r = api.post(f"{BASE_URL}/api/rencontres/reveal", json=payload, timeout=30)
        assert r.status_code == 400, f"expected 400 for invalid date, got {r.status_code}"


# ═══════════════════════════════════════════════════════════════
# C.3 — /capture happy path
# ═══════════════════════════════════════════════════════════════
class TestCapture:
    def test_capture_valid_reveal_id(self, api, reveal_data):
        payload = {
            "reveal_id": reveal_data["reveal_id"],
            "email": "test-astro-1@plume-test.fr",
            "consent_marketing": True,
        }
        r = api.post(f"{BASE_URL}/api/rencontres/capture", json=payload, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text}"
        d = r.json()

        assert d.get("ok") is True
        assert d.get("email_sent") is True

        # windows: array of 3
        windows = d.get("windows")
        assert isinstance(windows, list) and len(windows) == 3
        for w in windows:
            assert "kind" in w and "period" in w and "text" in w
            assert isinstance(w["text"], str) and len(w["text"]) > 20

        # cta
        cta = d.get("cta")
        assert cta is not None
        assert cta.get("product") == "rencontres_ultime"
        assert cta.get("price") == "29,99 €"
        assert isinstance(cta.get("features"), list) and len(cta["features"]) >= 3

    def test_capture_expired_reveal_410(self, api):
        payload = {
            "reveal_id": "deadbeef" * 4,  # 32 hex, not in cache
            "email": "test@plume-test.fr",
            "consent_marketing": True,
        }
        r = api.post(f"{BASE_URL}/api/rencontres/capture", json=payload, timeout=15)
        assert r.status_code == 410, f"expected 410 for unknown reveal_id, got {r.status_code}: {r.text}"
        detail = (r.json().get("detail") or "").lower()
        assert "expir" in detail, f"expected 'expiree' message, got: {detail}"


# ═══════════════════════════════════════════════════════════════
# C.5 — /checkout Stripe
# ═══════════════════════════════════════════════════════════════
class TestCheckout:
    def test_checkout_returns_stripe_url(self, api, reveal_data):
        payload = {
            "origin_url": "https://consultation-astro.preview.emergentagent.com",
            "reveal_id": reveal_data["reveal_id"],
            "email": "test-astro-1@plume-test.fr",
        }
        r = api.post(f"{BASE_URL}/api/rencontres/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text}"
        d = r.json()
        assert "url" in d
        assert "checkout.stripe.com" in d["url"], f"not a Stripe URL: {d['url']}"
        assert "session_id" in d and d["session_id"].startswith("cs_")

    def test_checkout_without_reveal_still_works(self, api):
        """checkout should not require reveal_id (email optional too)."""
        payload = {
            "origin_url": "https://consultation-astro.preview.emergentagent.com",
        }
        r = api.post(f"{BASE_URL}/api/rencontres/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"got {r.status_code}: {r.text}"
        d = r.json()
        assert "checkout.stripe.com" in d["url"]
