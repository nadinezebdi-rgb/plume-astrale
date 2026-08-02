"""Tests for Lecture Complete scarcity endpoint + bundle orchestration structure."""
import os
import re
import requests
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')


class TestScarcity:
    def test_scarcity_endpoint_returns_valid_json(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/scarcity", timeout=10)
        assert r.status_code == 200
        data = r.json()
        for k in ("remaining", "sold", "quota", "cycle_end", "sold_out"):
            assert k in data, f"missing key: {k}"

    def test_scarcity_fields_types_and_ranges(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/scarcity", timeout=10)
        d = r.json()
        assert isinstance(d["remaining"], int)
        assert 0 <= d["remaining"] <= 12
        assert isinstance(d["sold"], int) and d["sold"] >= 0
        assert d["quota"] == 12
        assert isinstance(d["sold_out"], bool)
        assert d["sold_out"] == (d["remaining"] == 0)
        # cycle_end is a valid ISO datetime
        # datetime.fromisoformat handles +00:00 in Python 3.11+
        dt = datetime.fromisoformat(d["cycle_end"])
        assert dt.tzinfo is not None

    def test_status_endpoint_requires_session_id(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/status", timeout=10)
        # session_id is required query param -> 422
        assert r.status_code in (400, 422)

    def test_status_endpoint_unknown_session(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/status?session_id=nope-nope-nope", timeout=10)
        assert r.status_code == 404


class TestBundleOrchestrationCodeStructure:
    """Static-code assertions per review request (no live PDF regeneration)."""
    SERVER = "/app/backend/server.py"
    BUNDLE = "/app/backend/services/lecture_complete_bundle.py"
    ROUTE = "/app/backend/routes/lecture_complete.py"

    def test_server_has_lecture_complete_webhook_hook(self):
        code = open(self.SERVER).read()
        assert "md.get('kind') == 'lecture_complete'" in code or 'md.get("kind") == "lecture_complete"' in code
        assert "handle_lecture_complete_webhook" in code

    def test_bundle_service_five_kinds(self):
        code = open(self.BUNDLE).read()
        for kind in (
            "theme_natal_pdf_oneshot",
            "karma_destin_analysis",
            "kabbale_arbre_de_vie",
            "fenetre_rencontre_avancee",
            "rencontres_ultime",
        ):
            assert kind in code, f"missing kind {kind}"
        assert "handle_lecture_complete_webhook" in code
        assert "get_scarcity_status" in code
        assert "bundle_dispatched" in code
        # child session_id pattern parent--suffix
        assert "f'{parent_session_id}--{suffix}'" in code or 'f"{parent_session_id}--{suffix}"' in code

    def test_route_bypass_triggers_bundle(self):
        code = open(self.ROUTE).read()
        assert "handle_lecture_complete_webhook" in code
        assert "asyncio.create_task" in code
        # Ensure the bundle dispatch is inside the admin bypass block
        # (the create_task line must be after try_consume_promo)
        idx_promo = code.find("try_consume_promo")
        idx_task = code.find("asyncio.create_task(handle_lecture_complete_webhook")
        assert idx_promo > 0 and idx_task > idx_promo

    def test_status_returns_bundle_fields(self):
        code = open(self.ROUTE).read()
        assert "bundle_dispatched" in code
        assert "bundle_children" in code
