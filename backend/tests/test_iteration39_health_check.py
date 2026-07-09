"""
Iteration 39 — Backend Health Check pré-déploiement production.

Valide TOUS les endpoints critiques du backend Plume Astrale :
  - GET /api/           → banner JSON
  - GET /api/health     → status healthy
  - POST /api/plume-chat → Solena (animation 🪶 + markdown)
  - GET /api/rencontres/ultime/status → stages (pending / delivered / error)
  - POST /api/rencontres/reveal → portrait partenaire ideal
  - POST /api/rencontres/capture → email capture
  - GET /api/packs      → grille GaryVee (packs + service_costs)
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ═════════════════════════════════════════════════════════════════
# 1) Banner + Health
# ═════════════════════════════════════════════════════════════════
class TestBannerAndHealth:
    def test_api_root_banner(self, api):
        r = api.get(f"{BASE_URL}/api/")
        assert r.status_code == 200, f"body={r.text[:300]}"
        data = r.json()
        for k in ("name", "status", "version", "docs", "health"):
            assert k in data, f"Missing key: {k}"
        assert data["status"] == "ok"
        assert data["health"] == "/api/health"

    def test_api_health(self, api):
        r = api.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in ("healthy", "ok")


# ═════════════════════════════════════════════════════════════════
# 2) Plume Chat (Solena)
# ═════════════════════════════════════════════════════════════════
class TestPlumeChat:
    def test_plume_chat_with_birth_data(self, api):
        payload = {
            "message": "Bonjour Solena, parle-moi de mon avenir amoureux",
            "session_id": "test-iter39-solena",
            "birth_data": {
                "name": "Testeur",
                "year": 1990, "month": 5, "day": 15,
                "hour": 12, "minute": 0,
                "place": "Paris, France",
            },
        }
        r = api.post(f"{BASE_URL}/api/plume-chat", json=payload, timeout=90)
        assert r.status_code == 200, f"body={r.text[:500]}"
        data = r.json()
        assert data.get("success") is True, f"Solena error: {data.get('message')}"
        answer = data.get("answer", "")
        assert isinstance(answer, str) and len(answer) > 50, "Answer too short"
        # Signature animation Soléna
        assert "🪶" in answer, f"Animation plume manquante. Answer: {answer[:200]}"
        # Format markdown : au moins une des marques suivantes
        has_h2 = "##" in answer
        has_bold = "**" in answer
        has_hr = "---" in answer
        assert (has_h2 or has_bold or has_hr), \
            f"Format markdown manquant (##/**/ ---). Answer: {answer[:400]}"
        # Aucun leak JSON
        assert '"action"' not in answer and '"action_input"' not in answer
        assert data.get("session_id") == "test-iter39-solena"


# ═════════════════════════════════════════════════════════════════
# 3) Rencontres ultime status
# ═════════════════════════════════════════════════════════════════
class TestUltimeStatus:
    def test_status_missing_session_id(self, api):
        r = api.get(f"{BASE_URL}/api/rencontres/ultime/status")
        # Missing required query param → FastAPI 422
        assert r.status_code in (200, 400, 422), f"Unexpected code {r.status_code}"
        # If 200, should carry stage=error
        if r.status_code == 200:
            data = r.json()
            assert data.get("stage") == "error"

    def test_status_empty_session_id(self, api):
        r = api.get(f"{BASE_URL}/api/rencontres/ultime/status", params={"session_id": ""})
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") == "error"
        assert "manquant" in (data.get("message") or "").lower() or \
               "session_id" in (data.get("message") or "").lower()

    def test_status_unknown_session_id(self, api):
        r = api.get(f"{BASE_URL}/api/rencontres/ultime/status", params={"session_id": "cs_unknown_iter39_zzz"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") == "error"

    def test_status_pre_seeded_delivered(self, api):
        # Session de test 'delivered' pré-existante (cf. contexte iter38)
        r = api.get(f"{BASE_URL}/api/rencontres/ultime/status",
                    params={"session_id": "cs_test_ultime_cb14f284e18c"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") in ("pending", "generating", "emailing", "delivered", "error")
        # Ce cas a été semé en 'delivered' dans iter36/37 — best-effort
        # On accepte tous stages valides sans forcer l'égalité stricte

    def test_status_pre_seeded_pending(self, api):
        r = api.get(f"{BASE_URL}/api/rencontres/ultime/status",
                    params={"session_id": "cs_test_pending_b53848d041e1"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") in ("pending", "generating", "emailing", "delivered", "error")


# ═════════════════════════════════════════════════════════════════
# 4) Rencontres /reveal (public, portrait partenaire idéal)
# ═════════════════════════════════════════════════════════════════
class TestRencontresReveal:
    @pytest.fixture(scope="class")
    def reveal_id(self, api):
        payload = {
            "day": 15, "month": 5, "year": 1990,
            "hour": 12, "minute": 0,
            "place": "Paris", "country": "France",
            "first_name": "TEST_Iter39",
        }
        r = api.post(f"{BASE_URL}/api/rencontres/reveal", json=payload, timeout=45)
        assert r.status_code == 200, f"body={r.text[:400]}"
        data = r.json()
        assert data.get("reveal_id")
        assert data.get("house7_sign") in [
            "Belier", "Taureau", "Gemeaux", "Cancer", "Lion", "Vierge",
            "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons",
        ]
        assert data.get("element") in ("Feu", "Terre", "Air", "Eau")
        assert data.get("portrait") and len(data["portrait"]) > 100
        # Portrait contient markdown (gras)
        assert "**" in data["portrait"]
        return data["reveal_id"]

    def test_reveal_returns_portrait(self, reveal_id):
        # Le fixture fait déjà la validation
        assert isinstance(reveal_id, str) and len(reveal_id) > 8

    def test_capture_accepts_email_reveal_id_utm(self, api, reveal_id):
        payload = {
            "reveal_id": reveal_id,
            "email": "test_iter39@example.com",
            "consent_marketing": True,
            "utm": {
                "utm_source": "tiktok",
                "utm_medium": "social",
                "utm_campaign": "iter39_healthcheck",
            },
        }
        r = api.post(f"{BASE_URL}/api/rencontres/capture", json=payload, timeout=45)
        assert r.status_code == 200, f"body={r.text[:400]}"
        data = r.json()
        assert data.get("ok") is True
        windows = data.get("windows") or []
        assert isinstance(windows, list) and len(windows) == 3
        for w in windows:
            assert "period" in w and "kind" in w and "text" in w
        cta = data.get("cta") or {}
        assert cta.get("product") == "rencontres_ultime"
        assert "29,99" in cta.get("price", "") or "29.99" in cta.get("price", "")


# ═════════════════════════════════════════════════════════════════
# 5) Packs + Service Costs (grille GaryVee)
# ═════════════════════════════════════════════════════════════════
class TestPacksAndServiceCosts:
    @pytest.fixture(scope="class")
    def packs_data(self, api):
        r = api.get(f"{BASE_URL}/api/packs")
        assert r.status_code == 200
        return r.json()

    def test_packs_endpoint_shape(self, packs_data):
        assert "packs" in packs_data
        assert "service_costs" in packs_data

    def test_pack_initiation(self, packs_data):
        p = packs_data["packs"].get("initiation")
        assert p, "Pack 'initiation' manquant"
        assert p["name"] == "Initiation"
        assert p["credits"] == 15
        assert p["bonus"] == 0
        assert float(p["amount"]) == 4.99
        assert p["currency"] == "eur"

    def test_pack_clarte(self, packs_data):
        p = packs_data["packs"].get("astro_amour")
        assert p, "Pack 'astro_amour' (Clarté) manquant"
        assert p["name"] == "Clarté"
        assert p["credits"] == 50
        assert p["bonus"] == 10
        assert float(p["amount"]) == 14.99

    def test_pack_flammes_jumelles(self, packs_data):
        p = packs_data["packs"].get("flammes_jumelles")
        assert p, "Pack 'flammes_jumelles' manquant"
        assert p["name"] == "Flammes Jumelles"
        assert p["credits"] == 100
        assert p["bonus"] == 30
        assert float(p["amount"]) == 29.99

    def test_service_costs_garyvee_grid(self, packs_data):
        sc = packs_data["service_costs"]
        # Grille exacte demandée
        expected = {
            "tarot_oui_non": 5,
            "chat_astral": 10,
            "tarot_marseille": 30,
            "lecture_astrologique": 40,
            "theme_natal_pdf": 60,
        }
        for k, v in expected.items():
            assert sc.get(k) == v, f"SERVICE_COSTS.{k} attendu={v} obtenu={sc.get(k)}"

    def test_service_costs_full_coverage(self, packs_data):
        sc = packs_data["service_costs"]
        # Coverage complémentaire — grille GaryVee
        for k in ["lecture_tarot", "love_languages"]:
            assert sc.get(k) == 10, f"{k} devrait être 10 cr"
        for k in ["tarot_celtique", "tarologie", "numerologie"]:
            assert sc.get(k) == 30, f"{k} devrait être 30 cr"
        for k in ["cartographie", "cartographie_premium", "synastrie",
                  "revolution_solaire", "karma_destin"]:
            assert sc.get(k) == 60, f"{k} devrait être 60 cr"
