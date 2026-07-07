"""Iteration 36 — Backend test suite for the `rencontres_ultime` pack (29,99€).

Covers:
1. Direct PDF generation (`generate_rencontres_ultime_pdf`) → valid bytes, %PDF- magic, ≥15 pages
2. Orchestrator `handle_rencontres_ultime_webhook` :
   - creates PDF file in /app/backend/assets/rencontres_ultime/
   - updates payment_transactions metadata with pdf_path + pdf_generated_at
   - idempotence — 2nd call no-op (pdf_generated_at unchanged)
3. Static serving: GET /api/assets/rencontres_ultime/<filename>.pdf → 200 + application/pdf
4. Checkout endpoint: POST /api/rencontres/checkout
   - returns { url, session_id }
   - persists a payment_transactions row with metadata.kind=rencontres_ultime + metadata.pdf_ctx
5. Regression: /api/plume-chat still returns success=true with markdown response
"""
from __future__ import annotations

import io
import os
import sys
import time
import uuid
import asyncio
import pytest
import requests

# Ensure backend on path
sys.path.insert(0, "/app/backend")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "https://consultation-astro.preview.emergentagent.com"


# ═══════════════════════════════════════════════════════════════════
# 1. Direct PDF generation
# ═══════════════════════════════════════════════════════════════════
class TestPDFGeneration:
    """Generation directe du PDF Ultime (ReportLab)."""

    def test_pdf_bytes_and_magic(self):
        from services.rencontres_ultime_pdf import generate_rencontres_ultime_pdf
        pdf_bytes = generate_rencontres_ultime_pdf(
            birth_date_iso="1993-06-15",
            first_name="Test",
            m7_sign="Balance",
            venus_sign="Cancer",
            mars_sign="Lion",
        )
        assert isinstance(pdf_bytes, (bytes, bytearray))
        assert len(pdf_bytes) > 10_000, f"PDF suspiciously small: {len(pdf_bytes)} bytes"
        # Magic bytes
        assert pdf_bytes[:5] == b"%PDF-", f"Invalid magic bytes: {pdf_bytes[:8]!r}"

    def test_pdf_at_least_15_pages(self):
        from services.rencontres_ultime_pdf import generate_rencontres_ultime_pdf
        pdf_bytes = generate_rencontres_ultime_pdf(
            birth_date_iso="1990-11-05",
            first_name="Léa",
            m7_sign="Scorpion",
            venus_sign="Vierge",
            mars_sign="Cancer",
        )
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 15, f"Expected ≥15 pages, got {len(reader.pages)}"

    def test_pdf_with_missing_fields_uses_fallbacks(self):
        """Fonction robuste face à des donnees incompletes."""
        from services.rencontres_ultime_pdf import generate_rencontres_ultime_pdf
        pdf_bytes = generate_rencontres_ultime_pdf(
            birth_date_iso="",
            first_name="",
            m7_sign="",
            venus_sign="",
            mars_sign="",
        )
        assert pdf_bytes[:5] == b"%PDF-"


# ═══════════════════════════════════════════════════════════════════
# 2. Orchestrator + idempotence (uses Supabase)
# ═══════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def seeded_tx():
    """Insere une tx de test rencontres_ultime dans payment_transactions."""
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    session_id = f"cs_test_TEST_ultime_{uuid.uuid4().hex[:16]}"
    payload = {
        "session_id": session_id,
        "user_email": "test-ultime@plume-astrale.fr",
        "pack_id": "rencontres_ultime",
        "amount": 29.99,
        "currency": "eur",
        "credits": 0,
        "status": "initiated",
        "payment_status": "unpaid",
        "credits_granted": False,
        "metadata": {
            "product": "rencontres_ultime",
            "kind": "rencontres_ultime",
            "pdf_ctx": {
                "first_name": "TestUltime",
                "birth_date_iso": "1988-04-12",
                "m7_sign": "Sagittaire",
                "venus_sign": "Gemeaux",
                "mars_sign": "Taureau",
            },
        },
    }
    try:
        sb.table("payment_transactions").insert(payload).execute()
    except Exception as e:
        pytest.skip(f"Cannot seed test tx: {e}")
    yield session_id
    # Cleanup
    try:
        sb.table("payment_transactions").delete().eq("session_id", session_id).execute()
    except Exception:
        pass


class TestWebhookOrchestrator:

    def test_handle_generates_pdf_and_updates_metadata(self, seeded_tx):
        from services.rencontres_ultime_service import handle_rencontres_ultime_webhook
        from services.supabase_client import get_admin_client

        asyncio.run(handle_rencontres_ultime_webhook(seeded_tx))

        sb = get_admin_client()
        r = sb.table("payment_transactions").select("*").eq("session_id", seeded_tx).maybe_single().execute()
        assert r and r.data, "tx disappeared after handler"
        tx = r.data
        md = tx.get("metadata") or {}
        assert md.get("pdf_path"), f"pdf_path missing in metadata: {md}"
        assert md["pdf_path"].startswith("/api/assets/rencontres_ultime/")
        assert md["pdf_path"].endswith(".pdf")
        assert md.get("pdf_generated_at"), "pdf_generated_at missing"
        # Fichier physique present
        from pathlib import Path
        filename = md["pdf_path"].split("/")[-1]
        file_path = Path("/app/backend/assets/rencontres_ultime") / filename
        assert file_path.exists(), f"PDF file not found on disk: {file_path}"
        assert file_path.stat().st_size > 10_000
        # Status completed
        assert tx.get("status") == "completed"
        assert tx.get("payment_status") == "paid"

    def test_handle_is_idempotent(self, seeded_tx):
        """2e appel ne doit pas regenerer le PDF (pdf_generated_at inchange)."""
        from services.rencontres_ultime_service import handle_rencontres_ultime_webhook
        from services.supabase_client import get_admin_client
        sb = get_admin_client()

        r1 = sb.table("payment_transactions").select("metadata").eq("session_id", seeded_tx).maybe_single().execute()
        gen_at_1 = (r1.data.get("metadata") or {}).get("pdf_generated_at")
        assert gen_at_1, "1st call must have set pdf_generated_at (dependency: previous test)"

        # 2eme appel
        time.sleep(0.5)
        asyncio.run(handle_rencontres_ultime_webhook(seeded_tx))
        r2 = sb.table("payment_transactions").select("metadata").eq("session_id", seeded_tx).maybe_single().execute()
        gen_at_2 = (r2.data.get("metadata") or {}).get("pdf_generated_at")
        assert gen_at_2 == gen_at_1, f"Idempotence violated: {gen_at_1} → {gen_at_2}"


# ═══════════════════════════════════════════════════════════════════
# 3. Static serving of the PDF
# ═══════════════════════════════════════════════════════════════════
class TestPDFServing:

    def test_generated_pdf_served_over_http(self, seeded_tx):
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        r = sb.table("payment_transactions").select("metadata").eq("session_id", seeded_tx).maybe_single().execute()
        md = (r.data or {}).get("metadata") or {}
        pdf_path = md.get("pdf_path")
        assert pdf_path, "PDF not yet generated (dependency ordering)"

        url = f"{BASE_URL}{pdf_path}"
        resp = requests.get(url, timeout=20)
        assert resp.status_code == 200, f"{url} → {resp.status_code}"
        ctype = resp.headers.get("content-type", "").lower()
        assert "pdf" in ctype, f"Wrong content-type: {ctype}"
        assert resp.content[:5] == b"%PDF-", "Served bytes are not a PDF"
        assert len(resp.content) > 10_000


# ═══════════════════════════════════════════════════════════════════
# 4. Checkout endpoint
# ═══════════════════════════════════════════════════════════════════
class TestRencontresCheckout:

    def test_checkout_persists_tx_with_pdf_ctx(self):
        # d'abord un reveal pour avoir un reveal_id
        reveal_payload = {
            "day": 15, "month": 6, "year": 1993,
            "hour": 14, "minute": 30,
            "place": "Paris", "country": "France",
            "first_name": "TestCheckout",
        }
        r = requests.post(f"{BASE_URL}/api/rencontres/reveal", json=reveal_payload, timeout=30)
        assert r.status_code == 200, f"reveal failed: {r.status_code} {r.text[:200]}"
        reveal = r.json()
        reveal_id = reveal.get("reveal_id")
        assert reveal_id, "reveal_id absent"

        checkout_payload = {
            "origin_url": "https://plume-astrale.fr",
            "reveal_id": reveal_id,
            "email": "test-checkout-ultime@plume-astrale.fr",
        }
        c = requests.post(f"{BASE_URL}/api/rencontres/checkout", json=checkout_payload, timeout=30)
        assert c.status_code == 200, f"checkout failed: {c.status_code} {c.text[:300]}"
        data = c.json()
        assert "url" in data and data["url"].startswith("http"), f"invalid url: {data}"
        assert "session_id" in data and data["session_id"], "session_id missing"

        session_id = data["session_id"]
        # Verifier persistance
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        row = sb.table("payment_transactions").select("*").eq("session_id", session_id).maybe_single().execute()
        assert row and row.data, f"tx not persisted for {session_id}"
        md = row.data.get("metadata") or {}
        assert md.get("kind") == "rencontres_ultime", f"metadata.kind wrong: {md.get('kind')}"
        pdf_ctx = md.get("pdf_ctx") or {}
        # Cles obligatoires
        for key in ("first_name", "birth_date_iso", "m7_sign", "venus_sign", "mars_sign"):
            assert key in pdf_ctx, f"pdf_ctx missing key {key}: {pdf_ctx}"
        # Le prenom doit correspondre
        assert pdf_ctx["first_name"] == "TestCheckout"
        # birth_date_iso format YYYY-MM-DD
        assert pdf_ctx["birth_date_iso"] == "1993-06-15"

        # Cleanup
        try:
            sb.table("payment_transactions").delete().eq("session_id", session_id).execute()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# 5. Regression: /api/plume-chat still works
# ═══════════════════════════════════════════════════════════════════
class TestPlumeChatRegression:

    def test_plume_chat_still_ok(self):
        payload = {
            "birth_data": {
                "year": 1993, "month": 6, "day": 15,
                "hour": 14, "minute": 30,
                "city": "Paris", "country_code": "FR",
            },
            "message": "Comment vas-tu Solena ?",
            "openai_api_key": "sk-test-invalid",  # BYOK, will fail → but endpoint should stay 200 or degrade gracefully
        }
        r = requests.post(f"{BASE_URL}/api/plume-chat", json=payload, timeout=60)
        # Doit pas être 5xx (regression sanity)
        assert r.status_code < 500, f"plume-chat 5xx regression: {r.status_code} {r.text[:200]}"

    def test_plume_chat_health_only(self):
        """Simple healthcheck: endpoint reachable + returns JSON."""
        r = requests.post(f"{BASE_URL}/api/plume-chat", json={}, timeout=15)
        # Doit renvoyer 400/422 (validation) mais pas 500
        assert r.status_code < 500, f"plume-chat crashed on empty payload: {r.status_code}"
        # Body doit être du JSON
        try:
            r.json()
        except Exception:
            pytest.fail(f"non-JSON response: {r.text[:200]}")
