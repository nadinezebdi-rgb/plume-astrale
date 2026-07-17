"""
Iteration 47 — Backend regression testing for:
  1. Pack Karmique + Kabbale 89€ (checkout, bypass promo, PDF polling)
  2. Rencontres Ultime 29,99€ (validation partenaire OBLIGATOIRE)
  3. Kabbale 39€ regression (bypass promo)
  4. Astrology v3 chat regression (Supabase Bearer auth)
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
ADMIN_PASS = "PlumeAdmin2026"
PROMO = "TESTPLUME"


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(api):
    r = api.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASS},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"Supabase login failed: {r.status_code} {r.text[:200]}")
    return r.json().get("access_token")


# =============================================================
# 1) PACK KARMIQUE
# =============================================================
class TestPackKarmique:
    """Pack Karmique + Kabbale (89 EUR) checkout & polling"""

    def test_checkout_no_promo_returns_stripe_url(self, api):
        payload = {
            "email": "test.plume@example.com",
            "first_name": "Camille",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "birth_country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "origin_url": BASE_URL,
        }
        r = api.post(f"{BASE_URL}/api/pack-karmique/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert "url" in data and "session_id" in data
        assert "checkout.stripe.com" in data["url"], f"Expected Stripe URL, got: {data['url']}"
        assert not data.get("admin_bypass"), "Should NOT be admin_bypass without promo"

    def test_checkout_invalid_email_400(self, api):
        payload = {
            "email": "not-an-email",
            "first_name": "X",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "origin_url": BASE_URL,
        }
        r = api.post(f"{BASE_URL}/api/pack-karmique/checkout", json=payload, timeout=15)
        assert r.status_code == 400

    def test_checkout_missing_birth_date_400(self, api):
        payload = {
            "email": "ok@example.com",
            "first_name": "X",
            "birth_date": "",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "origin_url": BASE_URL,
        }
        r = api.post(f"{BASE_URL}/api/pack-karmique/checkout", json=payload, timeout=15)
        assert r.status_code == 400

    def test_checkout_promo_bypass_and_polling(self, api):
        """Full flow: TESTPLUME promo bypass → session_id → poll until pdf_ready"""
        payload = {
            "email": "TEST_pack@plume-astrale.fr",
            "first_name": "Admin",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "birth_country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "origin_url": BASE_URL,
            "promo_code": PROMO,
        }
        r = api.post(f"{BASE_URL}/api/pack-karmique/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("admin_bypass") is True, f"Expected admin_bypass=True: {data}"
        session_id = data.get("session_id")
        assert session_id and session_id.startswith("admin-packkarma-")

        # Poll status until pdf_ready or 150s timeout
        deadline = time.time() + 150
        last_status = None
        pdf_url = None
        while time.time() < deadline:
            sr = api.get(f"{BASE_URL}/api/pack-karmique/status", params={"session_id": session_id}, timeout=45)
            assert sr.status_code == 200, f"status HTTP {sr.status_code}: {sr.text[:200]}"
            last_status = sr.json()
            if last_status.get("pdf_ready"):
                pdf_url = last_status.get("pdf_url")
                break
            time.sleep(6)

        assert last_status is not None
        assert last_status.get("pdf_ready") is True, f"PDF not ready in 150s. Last: {last_status}"
        assert pdf_url, f"pdf_url missing. Last: {last_status}"
        # Try downloading the PDF
        pdf_full = pdf_url if pdf_url.startswith("http") else f"{BASE_URL}{pdf_url}"
        pr = requests.get(pdf_full, timeout=30)
        assert pr.status_code == 200, f"PDF fetch HTTP {pr.status_code}"
        assert pr.headers.get("content-type", "").startswith("application/pdf") or pr.content[:4] == b"%PDF", \
            f"Not a PDF: content-type={pr.headers.get('content-type')} head={pr.content[:20]!r}"
        # Sanity: PDF is a decent size (>50KB for 44 pages)
        assert len(pr.content) > 50000, f"PDF suspiciously small: {len(pr.content)} bytes"


# =============================================================
# 2) RENCONTRES ULTIME (partner data required)
# =============================================================
class TestRencontresUltime:
    """Compat Ultime 29,99€ - partner fields required"""

    def test_checkout_missing_partner_firstname_400_french(self, api):
        payload = {
            "origin_url": BASE_URL,
            "email": "user@example.com",
            "partner_first_name": "",
            "partner_birth_date": "1988-03-10",
        }
        r = api.post(f"{BASE_URL}/api/rencontres/checkout", json=payload, timeout=15)
        assert r.status_code == 400
        detail = r.json().get("detail", "")
        assert "prénom" in detail.lower() or "prenom" in detail.lower(), f"French error missing: {detail}"

    def test_checkout_missing_partner_birthdate_400_french(self, api):
        payload = {
            "origin_url": BASE_URL,
            "email": "user@example.com",
            "partner_first_name": "Alice",
            "partner_birth_date": None,
        }
        r = api.post(f"{BASE_URL}/api/rencontres/checkout", json=payload, timeout=15)
        assert r.status_code == 400
        detail = r.json().get("detail", "").lower()
        assert "naissance" in detail or "date" in detail, f"French error missing: {detail}"

    def test_full_flow_reveal_checkout_bypass_polling(self, api):
        # STEP 1 — reveal
        reveal_payload = {
            "day": 15, "month": 5, "year": 1990,
            "hour": 12, "minute": 0,
            "place": "Paris", "country": "France",
            "first_name": "Camille",
        }
        rv = api.post(f"{BASE_URL}/api/rencontres/reveal", json=reveal_payload, timeout=45)
        assert rv.status_code == 200, f"reveal HTTP {rv.status_code}: {rv.text[:300]}"
        rvd = rv.json()
        reveal_id = rvd.get("reveal_id")
        assert reveal_id, "reveal_id missing"

        # STEP 2 — checkout with promo TESTPLUME + partner data
        checkout_payload = {
            "origin_url": BASE_URL,
            "reveal_id": reveal_id,
            "email": "TEST_ultime@plume-astrale.fr",
            "promo_code": PROMO,
            "partner_first_name": "Alexandre",
            "partner_birth_date": "1988-03-10",
            "partner_birth_time": "14:30",
            "partner_place": "Lyon",
        }
        cr = api.post(f"{BASE_URL}/api/rencontres/checkout", json=checkout_payload, timeout=30)
        assert cr.status_code == 200, f"checkout HTTP {cr.status_code}: {cr.text[:300]}"
        cd = cr.json()
        assert cd.get("admin_bypass") is True, f"Expected admin_bypass=True: {cd}"
        session_id = cd.get("session_id")
        assert session_id and session_id.startswith("admin-rencontres-")

        # STEP 3 — poll /ultime/status until 'delivered' with pdf_url
        deadline = time.time() + 150
        stages_seen = set()
        last = None
        while time.time() < deadline:
            sr = api.get(f"{BASE_URL}/api/rencontres/ultime/status",
                         params={"session_id": session_id}, timeout=45)
            assert sr.status_code == 200, f"status HTTP {sr.status_code}: {sr.text[:200]}"
            last = sr.json()
            stages_seen.add(last.get("stage"))
            if last.get("stage") == "delivered" and last.get("pdf_url"):
                break
            time.sleep(6)

        assert last is not None
        assert last.get("stage") == "delivered", f"Stage not delivered in 150s. Stages seen: {stages_seen}. Last: {last}"
        pdf_url = last.get("pdf_url")
        assert pdf_url, f"pdf_url missing. Last: {last}"
        pdf_full = pdf_url if pdf_url.startswith("http") else f"{BASE_URL}{pdf_url}"
        pr = requests.get(pdf_full, timeout=30)
        assert pr.status_code == 200
        assert pr.headers.get("content-type", "").startswith("application/pdf") or pr.content[:4] == b"%PDF"
        assert len(pr.content) > 30000, f"PDF suspiciously small: {len(pr.content)} bytes"


# =============================================================
# 3) REGRESSION — Kabbale + Astrology v3 chat
# =============================================================
class TestRegression:
    """Regression: kabbale checkout + astrology/v3/chat"""

    def test_kabbale_checkout_bypass(self, api):
        payload = {
            "email": "TEST_kab@plume-astrale.fr",
            "first_name": "Camille",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "birth_country": "FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "origin_url": BASE_URL,
            "promo_code": PROMO,
        }
        r = api.post(f"{BASE_URL}/api/kabbale/checkout", json=payload, timeout=30)
        assert r.status_code == 200, f"kabbale HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        # bypass path : admin_bypass=True + session_id
        assert data.get("admin_bypass") is True or "checkout.stripe.com" in data.get("url", ""), \
            f"Neither bypass nor stripe URL: {data}"

    def test_astrology_v3_chat_success(self, api, admin_token):
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
        }
        payload = {"message": "Bonjour Plume, comment vas-tu ?", "session_id": "test_iter47"}
        r = requests.post(f"{BASE_URL}/api/astrology/v3/chat", headers=headers, json=payload, timeout=60)
        assert r.status_code == 200, f"chat HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success") is True, f"success not True: {data}"
