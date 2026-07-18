"""
Iteration 48 — Post GitHub-resync regression suite.

Covers:
  - GET /api/packs (10 packs including new GitHub oneshots)
  - POST /api/pack-karmique/checkout (promo TESTPLUME) + polling status
  - POST /api/rencontres/checkout partner validation + full flow
  - POST /api/kabbale/checkout with promo TESTPLUME
  - Smoke tests for GitHub oneshots:
      * POST /api/numerologie/checkout
      * POST /api/karma-destin/checkout
      * POST /api/fenetre-rencontre-avancee/checkout
  - POST /api/astrology/v3/chat (Bearer Supabase)
  - POST /api/credits/checkout for pack_id=nebuleuse
"""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")
SUPABASE_URL = "https://ebwicqvbkwogxneipaxh.supabase.co"
SUPABASE_ANON = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZW"
    "lwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0."
    "sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA"
)
ADMIN_EMAIL = "admin@plume-astrale.fr"
ADMIN_PASSWORD = "PlumeAdmin2026"
PROMO = "TESTPLUME"

TIMEOUT_S = 60


@pytest.fixture(scope="session")
def supabase_token():
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={"apikey": SUPABASE_ANON, "Content-Type": "application/json"},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    if r.status_code != 200:
        pytest.skip(f"Supabase login failed: {r.status_code} {r.text[:200]}")
    return r.json().get("access_token")


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ─────────────── Packs & discovery ───────────────
class TestPacksCatalog:
    def test_get_packs_returns_all_products(self, api):
        r = api.get(f"{BASE_URL}/api/packs", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        packs = data.get("packs", {})
        expected = {
            "comete", "nebuleuse", "constellation", "voie_lactee",
            "pack_karmique_kabbale", "rencontres_ultime", "kabbale_arbre_de_vie",
            "numerologie_code", "karma_destin_analysis", "fenetre_rencontre_avancee",
        }
        assert expected.issubset(packs.keys()), f"missing packs: {expected - packs.keys()}"
        # Sanity on pack_karmique price 89 EUR
        pk = packs["pack_karmique_kabbale"]
        assert float(pk["amount"]) == 89.0
        assert pk["currency"].lower() == "eur"
        # Numerology 19€ / Karma 24€ / Fenetre 29€
        assert float(packs["numerologie_code"]["amount"]) == 19.0
        assert float(packs["karma_destin_analysis"]["amount"]) == 24.0
        assert float(packs["fenetre_rencontre_avancee"]["amount"]) == 29.0


# ─────────────── Pack Karmique 89€ ───────────────
class TestPackKarmique:
    def test_checkout_with_promo_and_status_polling(self, api):
        payload = {
            "email": f"TEST_pk48_{uuid.uuid4().hex[:8]}@plume-astrale.fr",
            "first_name": "TestPK",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "origin_url": BASE_URL,
            "promo_code": PROMO,
        }
        r = api.post(f"{BASE_URL}/api/pack-karmique/checkout", json=payload, timeout=TIMEOUT_S)
        assert r.status_code == 200, f"{r.status_code} {r.text[:400]}"
        body = r.json()
        # Bypass response
        assert body.get("admin_bypass") is True or body.get("status") == "completed", body
        session_id = body.get("session_id")
        assert session_id and session_id.startswith("admin-"), body

        # Poll status until pdf_ready or timeout ≈ 120s
        deadline = time.time() + 130
        last = {}
        pdf_ready = False
        while time.time() < deadline:
            try:
                sr = api.get(
                    f"{BASE_URL}/api/pack-karmique/status",
                    params={"session_id": session_id},
                    timeout=45,
                )
                if sr.status_code == 200:
                    last = sr.json()
                    if last.get("pdf_ready") is True or last.get("pdf_url"):
                        pdf_ready = True
                        break
            except requests.exceptions.ReadTimeout:
                pass
            time.sleep(4)
        assert pdf_ready, f"pdf_ready never true within 120s, last={last}"


# ─────────────── Rencontres Ultime ───────────────
class TestRencontres:
    def _reveal(self, api):
        r = api.post(
            f"{BASE_URL}/api/rencontres/reveal",
            json={
                "first_name": "TestR",
                "day": 15,
                "month": 5,
                "year": 1990,
                "hour": 12,
                "minute": 0,
                "place": "Paris",
                "country": "France",
            },
            timeout=45,
        )
        assert r.status_code == 200, f"reveal {r.status_code} {r.text[:300]}"
        return r.json()

    def test_checkout_missing_partner_first_name_returns_400(self, api):
        reveal = self._reveal(api)
        reveal_id = reveal.get("reveal_id") or reveal.get("id")
        assert reveal_id, reveal
        r = api.post(
            f"{BASE_URL}/api/rencontres/checkout",
            json={
                "reveal_id": reveal_id,
                "email": f"TEST_r48_{uuid.uuid4().hex[:8]}@plume-astrale.fr",
                "partner_first_name": "",
                "partner_birth_date": "1988-03-10",
                "origin_url": BASE_URL,
                "promo_code": PROMO,
            },
            timeout=30,
        )
        assert r.status_code == 400, f"{r.status_code} {r.text[:300]}"
        assert "prénom" in r.text.lower() or "prenom" in r.text.lower(), r.text

    def test_checkout_missing_partner_birth_date_returns_400(self, api):
        reveal = self._reveal(api)
        reveal_id = reveal.get("reveal_id") or reveal.get("id")
        r = api.post(
            f"{BASE_URL}/api/rencontres/checkout",
            json={
                "reveal_id": reveal_id,
                "email": f"TEST_r48_{uuid.uuid4().hex[:8]}@plume-astrale.fr",
                "partner_first_name": "Alice",
                "partner_birth_date": "",
                "origin_url": BASE_URL,
                "promo_code": PROMO,
            },
            timeout=30,
        )
        assert r.status_code == 400, f"{r.status_code} {r.text[:300]}"
        assert "naissance" in r.text.lower() or "date" in r.text.lower(), r.text

    def test_full_flow_reveal_checkout_delivered(self, api):
        reveal = self._reveal(api)
        reveal_id = reveal.get("reveal_id") or reveal.get("id")
        assert reveal_id, reveal
        email = f"TEST_r48_{uuid.uuid4().hex[:8]}@plume-astrale.fr"
        cr = api.post(
            f"{BASE_URL}/api/rencontres/checkout",
            json={
                "reveal_id": reveal_id,
                "email": email,
                "partner_first_name": "Alice",
                "partner_birth_date": "1988-03-10",
                "partner_birth_time": "10:00",
                "partner_place": "Lyon",
                "origin_url": BASE_URL,
                "promo_code": PROMO,
            },
            timeout=TIMEOUT_S,
        )
        assert cr.status_code == 200, f"{cr.status_code} {cr.text[:400]}"
        body = cr.json()
        session_id = body.get("session_id")
        assert session_id, body

        # Poll /ultime/status
        deadline = time.time() + 130
        last = {}
        delivered = False
        while time.time() < deadline:
            try:
                sr = api.get(
                    f"{BASE_URL}/api/rencontres/ultime/status",
                    params={"session_id": session_id},
                    timeout=45,
                )
                if sr.status_code == 200:
                    last = sr.json()
                    stage = last.get("stage") or last.get("status")
                    if stage == "delivered" or last.get("pdf_url"):
                        delivered = True
                        break
            except requests.exceptions.ReadTimeout:
                pass
            time.sleep(4)
        assert delivered, f"Not delivered in 120s, last={last}"


# ─────────────── Kabbale + GitHub oneshots smoke ───────────────
class TestOneshotSmokes:
    def test_kabbale_checkout_promo_bypass(self, api):
        r = api.post(
            f"{BASE_URL}/api/kabbale/checkout",
            json={
                "email": f"TEST_kab48_{uuid.uuid4().hex[:8]}@plume-astrale.fr",
                "first_name": "TestKab",
                "birth_date": "1990-05-15",
                "birth_time": "12:00",
                "birth_city": "Paris",
                "origin_url": BASE_URL,
                "promo_code": PROMO,
            },
            timeout=TIMEOUT_S,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:400]}"
        b = r.json()
        assert b.get("admin_bypass") is True or b.get("status") == "completed", b

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/numerologie/checkout",
            "/api/karma-destin/checkout",
            "/api/fenetre-rencontre-avancee/checkout",
        ],
    )
    def test_github_oneshots_smoke_no_500(self, api, endpoint):
        """Smoke test — should return Stripe URL or clean 400 (no 500)."""
        payload = {
            "email": f"TEST_smoke48_{uuid.uuid4().hex[:6]}@plume-astrale.fr",
            "first_name": "Smoke",
            "birth_date": "1990-05-15",
            "birth_time": "12:00",
            "birth_city": "Paris",
            "origin_url": BASE_URL,
        }
        r = api.post(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT_S)
        assert r.status_code != 500, f"{endpoint} returned 500: {r.text[:400]}"
        assert r.status_code in (200, 400), f"{endpoint} {r.status_code}: {r.text[:300]}"
        if r.status_code == 200:
            body = r.json()
            # Should provide either stripe url (pending) or admin bypass (completed)
            assert body.get("url") or body.get("status"), body

    def test_github_oneshots_with_promo_bypass(self, api):
        """With TESTPLUME promo, oneshots should return completed session_id."""
        for endpoint, prefix in [
            ("/api/numerologie/checkout", "admin-numerologie"),
            ("/api/karma-destin/checkout", "admin-karma"),
            ("/api/fenetre-rencontre-avancee/checkout", "admin-fenetre"),
        ]:
            payload = {
                "email": f"TEST_promo48_{uuid.uuid4().hex[:6]}@plume-astrale.fr",
                "first_name": "Promo",
                "birth_date": "1990-05-15",
                "birth_time": "12:00",
                "birth_city": "Paris",
                "origin_url": BASE_URL,
                "promo_code": PROMO,
            }
            r = api.post(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT_S)
            assert r.status_code == 200, f"{endpoint} {r.status_code}: {r.text[:400]}"
            b = r.json()
            assert b.get("status") == "completed", f"{endpoint} not completed with promo: {b}"
            assert (b.get("session_id") or "").startswith(prefix), f"{endpoint} session_id: {b}"


# ─────────────── Astrology v3 chat (auth) + credits/checkout ───────────────
class TestChatAndCredits:
    def test_astrology_v3_chat(self, supabase_token, api):
        r = api.post(
            f"{BASE_URL}/api/astrology/v3/chat",
            headers={"Authorization": f"Bearer {supabase_token}"},
            json={"message": "Bonjour Soléna, comment vas-tu?", "session_id": f"test-{uuid.uuid4().hex[:8]}"},
            timeout=TIMEOUT_S,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:400]}"
        body = r.json()
        assert body.get("success") is True, body
        # French response expected
        text = (body.get("message") or body.get("response") or body.get("reply") or "").lower()
        assert text, body

    def test_credits_checkout_nebuleuse(self, supabase_token, api):
        r = api.post(
            f"{BASE_URL}/api/credits/checkout",
            headers={"Authorization": f"Bearer {supabase_token}"},
            json={"pack_id": "nebuleuse", "origin_url": BASE_URL},
            timeout=TIMEOUT_S,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:400]}"
        b = r.json()
        # Should return a Stripe URL (or admin_bypass if profile permits)
        assert b.get("url") or b.get("checkout_url") or b.get("admin_bypass"), b
        url = b.get("url") or b.get("checkout_url") or ""
        if url:
            assert "checkout.stripe.com" in url, f"URL not Stripe: {url}"
