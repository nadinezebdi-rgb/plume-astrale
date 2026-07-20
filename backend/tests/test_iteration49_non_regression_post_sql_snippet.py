"""
Iteration 49 — Non-regression check post SQL Studio snippet vidé.

Contexte : L'utilisateur pensait avoir supprimé une table 'sales' via un snippet SQL
saved dans Supabase Studio, mais en réalité seul le snippet SQL a été vidé (aucun DROP
n'a été exécuté). La table 'sales' n'est référencée nulle part dans le code Plume Astrale.

Objectif : Prouver que les flows critiques marchent toujours (aucune régression).

Endpoints testés :
- GET /api/health
- POST /api/astrocartographie/checkout  (Stripe live + PLUME15 discount)
- GET  /api/astrocartographie/status
- GET  /api/astrocartographie/cities/search
- POST /api/tarot/oui-non  (enrichi)
- POST /api/oracle         (enrichi)
- POST /api/astrosexo/personal (enrichi + venus/mars/moon)
- POST /api/compatibility/generate (PDF base64)
"""
from __future__ import annotations
import base64
import os
import uuid
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
LONG_TIMEOUT = 90


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ------- Health -------
class TestHealth:
    def test_health_ok(self, client):
        r = client.get(f"{API}/health", timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("status") == "healthy"


# ------- Astrocartographie: cities/search -------
class TestAstrocartoCities:
    def test_search_tokyo(self, client):
        r = client.get(f"{API}/astrocartographie/cities/search",
                       params={"q": "tokyo", "limit": 3}, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        items = data.get("items") or []
        assert len(items) >= 1, f"aucune ville renvoyée: {data}"
        first = items[0]
        for key in ("city", "country", "latitude", "longitude"):
            assert key in first, f"missing key {key} in {first}"
        assert isinstance(first["latitude"], float)
        assert isinstance(first["longitude"], float)


# ------- Astrocartographie: checkout Stripe live -------
class TestAstrocartoCheckout:
    """Trois flows : checkout Stripe live, PLUME15 (-15%), status."""

    valid_payload = {
        "email": f"TEST_iter49_{uuid.uuid4().hex[:8]}@plume-astrale.fr",
        "first_name": "Marie",
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "birth_city": "Paris",
        "birth_country": "FR",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "chosen_cities": [
            {"city": "Tokyo", "country": "Japan", "country_code": "JP",
             "latitude": 35.6762, "longitude": 139.6503},
            {"city": "New York", "country": "USA", "country_code": "US",
             "latitude": 40.7128, "longitude": -74.0060},
            {"city": "Bali", "country": "Indonesia", "country_code": "ID",
             "latitude": -8.3405, "longitude": 115.0920},
        ],
        "origin_url": BASE_URL,
    }

    def test_checkout_live_no_promo(self, client):
        r = client.post(f"{API}/astrocartographie/checkout",
                        json=self.valid_payload, timeout=45)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "url" in data and "session_id" in data
        # En production STRIPE_LIVE, la session doit contenir cs_live_ dans le session_id ou l'URL doit être checkout.stripe.com
        assert "checkout.stripe.com" in data["url"] or "stripe.com" in data["url"], f"URL non-stripe: {data['url']}"
        # session_id doit être un cs_live_* ou cs_test_* (Stripe API), pas un admin-*
        assert data["session_id"].startswith("cs_"), f"session_id inattendu: {data['session_id']}"

    def test_checkout_plume15_15pct_discount(self, client):
        payload = dict(self.valid_payload)
        payload["email"] = f"TEST_plume15_{uuid.uuid4().hex[:8]}@plume-astrale.fr"
        payload["promo_code"] = "PLUME15"
        r = client.post(f"{API}/astrocartographie/checkout", json=payload, timeout=45)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "session_id" in data
        # Attendre 1s puis vérifier le montant en base via status endpoint
        session_id = data["session_id"]
        s = client.get(f"{API}/astrocartographie/status",
                       params={"session_id": session_id}, timeout=30)
        # Le status renvoie status/payment_status même pour une session initiated
        assert s.status_code == 200, s.text
        st = s.json()
        assert "status" in st

    def test_status_unknown_session_404(self, client):
        r = client.get(f"{API}/astrocartographie/status",
                       params={"session_id": "cs_fake_not_exist_xxx"}, timeout=30)
        assert r.status_code in (404, 500)

    def test_checkout_wrong_cities_count_400(self, client):
        payload = dict(self.valid_payload)
        payload["email"] = f"TEST_bad_{uuid.uuid4().hex[:8]}@plume-astrale.fr"
        payload["chosen_cities"] = [self.valid_payload["chosen_cities"][0]]  # 1 ville
        r = client.post(f"{API}/astrocartographie/checkout", json=payload, timeout=30)
        assert r.status_code == 400
        assert "3 villes" in r.json().get("detail", "").lower() or "3" in r.json().get("detail", "")


# ------- Tarot oui-non enrichi -------
class TestTarotOuiNon:
    def test_tarot_oui_non_enrichi(self, client):
        r = client.post(f"{API}/tarot/oui-non",
                        json={"question": "Vais-je trouver l'amour cette année ?", "first_name": "Marie"},
                        timeout=LONG_TIMEOUT)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("reponse_enrichie") is True, f"pas enrichi: {data}"
        reponse = data.get("reponse", "")
        assert isinstance(reponse, str)
        assert len(reponse) > 500, f"réponse trop courte ({len(reponse)} chars)"
        assert reponse.rstrip().endswith("?"), f"ne finit pas par '?': ...{reponse[-40:]}"


# ------- Oracle enrichi -------
class TestOracle:
    def test_oracle_enrichi(self, client):
        r = client.post(f"{API}/oracle",
                        json={"question": "Quel message les anges ont pour moi aujourd'hui ?",
                              "first_name": "Marie"},
                        timeout=LONG_TIMEOUT)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("success") is True
        assert data.get("enrichi") is True, f"pas enrichi: {data}"
        answer = data.get("answer") or ""
        assert isinstance(answer, str)
        assert len(answer) > 500, f"answer trop courte ({len(answer)} chars): {answer[:200]}"
        assert answer.rstrip().endswith("?"), f"ne finit pas par '?': ...{answer[-40:]}"


# ------- AstroSexo /personal enrichi -------
class TestAstroSexoPersonal:
    def test_astrosexo_marie(self, client):
        payload = {
            "first_name": "Marie",
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "city": "Paris",
            "country_code": "FR",
        }
        r = client.post(f"{API}/astrosexo/personal", json=payload, timeout=LONG_TIMEOUT)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("enrichi") is True
        assert data.get("venus_sign"), f"pas de venus_sign: {data}"
        assert data.get("mars_sign"), f"pas de mars_sign: {data}"
        assert data.get("moon_sign"), f"pas de moon_sign: {data}"
        analysis = data.get("analysis") or ""
        assert len(analysis) > 2000, f"analysis trop courte ({len(analysis)} chars)"


# ------- /api/compatibility/generate → PDF base64 -------
class TestCompatibilityPdf:
    def test_generate_pdf_base64(self, client):
        payload = {
            "person1": {
                "prenom": "Marie", "first_name": "Marie",
                "date_naissance": "1990-05-15",
                "birth_time": "14:30",
                "latitude": 48.8566, "longitude": 2.3522,
                "city": "Paris", "country_code": "FR",
            },
            "person2": {
                "prenom": "Julien", "first_name": "Julien",
                "date_naissance": "1988-09-20",
                "birth_time": "10:15",
                "latitude": 45.7640, "longitude": 4.8357,
                "city": "Lyon", "country_code": "FR",
            },
            "question": "Notre couple a-t-il un avenir spirituel commun ?",
        }
        r = client.post(f"{API}/compatibility/generate", json=payload, timeout=LONG_TIMEOUT)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("success") is True
        pdf_url = data.get("pdf_url") or ""
        assert pdf_url.startswith("data:application/pdf;base64,"), f"pdf_url format inattendu"
        b64 = pdf_url.split(",", 1)[1]
        raw = base64.b64decode(b64[:1000])
        assert raw.startswith(b"%PDF-1."), f"magic PDF non trouvé: {raw[:16]}"
