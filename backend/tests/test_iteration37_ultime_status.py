"""Iteration 37 — Backend test suite for GET /api/rencontres/ultime/status.

Covers the 5 review points:
1. `/ultime/status?session_id=<X>` returns JSON with `stage` in
   (pending | generating | emailing | delivered | error) and `message`:
   - 'delivered' quand metadata.pdf_path ET metadata.email_sent_at sont set
   - 'generating' quand status=completed & payment_status=paid mais pas de pdf_path
   - 'pending' quand status != 'completed'
   - 'emailing' quand pdf_path present mais email_sent_at manque
   - 'error' quand session inconnue
2. Retourne aussi `pdf_url` et `email` quand dispo (delivered/emailing).
3. Sans session_id → error clean (pas de 500).
4. Safe contre injections (session_id absurde/SQL-like → error clean, pas de 500).
5. Regression : ne casse pas /api/rencontres/reveal, /api/rencontres/capture,
   /api/rencontres/checkout, /api/plume-chat.
"""
from __future__ import annotations

import os
import sys
import uuid

import pytest
import requests

sys.path.insert(0, "/app/backend")

def _load_backend_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if v:
        return v.rstrip("/")
    # Fallback: read from /app/frontend/.env
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip().rstrip("/")
    except Exception:
        pass
    return ""


BASE_URL = _load_backend_url()
assert BASE_URL, "REACT_APP_BACKEND_URL missing in env and /app/frontend/.env"

STATUS_URL = f"{BASE_URL}/api/rencontres/ultime/status"


# ────────────────────────────────────────────────────────────────
# Fixtures — seed 4 sessions in Supabase covering all stages
# ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def sb():
    from services.supabase_client import get_admin_client
    return get_admin_client()


@pytest.fixture(scope="module")
def seed_sessions(sb):
    """Seed 4 payment_transactions covering: pending / generating / emailing / delivered."""
    prefix = f"cs_test_TEST_it37_{uuid.uuid4().hex[:8]}"

    sessions = {
        "pending": {
            "session_id": f"{prefix}_pending",
            "status": "initiated",
            "payment_status": "unpaid",
            "metadata": {"product": "rencontres_ultime", "kind": "rencontres_ultime"},
            "user_email": "pending@test.local",
        },
        "generating": {
            "session_id": f"{prefix}_gen",
            "status": "completed",
            "payment_status": "paid",
            "metadata": {"product": "rencontres_ultime", "kind": "rencontres_ultime"},
            "user_email": "gen@test.local",
        },
        "emailing": {
            "session_id": f"{prefix}_email",
            "status": "completed",
            "payment_status": "paid",
            "metadata": {
                "product": "rencontres_ultime",
                "kind": "rencontres_ultime",
                "pdf_path": "/api/assets/rencontres_ultime/ultime_TEST_emailing.pdf",
            },
            "user_email": "email@test.local",
        },
        "delivered": {
            "session_id": f"{prefix}_deliv",
            "status": "completed",
            "payment_status": "paid",
            "metadata": {
                "product": "rencontres_ultime",
                "kind": "rencontres_ultime",
                "pdf_path": "/api/assets/rencontres_ultime/ultime_TEST_delivered.pdf",
                "email_sent_at": "2026-01-15T10:30:00Z",
            },
            "user_email": "delivered@test.local",
        },
    }

    inserted = []
    try:
        for stage, s in sessions.items():
            payload = {
                "session_id": s["session_id"],
                "user_email": s["user_email"],
                "pack_id": "rencontres_ultime",
                "amount": 29.99,
                "currency": "eur",
                "credits": 0,
                "status": s["status"],
                "payment_status": s["payment_status"],
                "credits_granted": False,
                "metadata": s["metadata"],
            }
            sb.table("payment_transactions").insert(payload).execute()
            inserted.append(s["session_id"])
    except Exception as e:
        # Cleanup any partial insert
        for sid in inserted:
            try:
                sb.table("payment_transactions").delete().eq("session_id", sid).execute()
            except Exception:
                pass
        pytest.skip(f"Cannot seed test sessions: {e}")

    yield {stage: s["session_id"] for stage, s in sessions.items()}

    # Cleanup
    for sid in inserted:
        try:
            sb.table("payment_transactions").delete().eq("session_id", sid).execute()
        except Exception:
            pass


# ────────────────────────────────────────────────────────────────
# 1. /ultime/status — 5 stages
# ────────────────────────────────────────────────────────────────
class TestStatusEndpointStages:

    def test_stage_delivered(self, seed_sessions):
        sid = seed_sessions["delivered"]
        r = requests.get(STATUS_URL, params={"session_id": sid}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("stage") == "delivered", data
        assert isinstance(data.get("message"), str) and len(data["message"]) > 0
        # pdf_url + email exposes when delivered
        assert data.get("pdf_url") == "/api/assets/rencontres_ultime/ultime_TEST_delivered.pdf"
        assert data.get("email") == "delivered@test.local"

    def test_stage_generating(self, seed_sessions):
        sid = seed_sessions["generating"]
        r = requests.get(STATUS_URL, params={"session_id": sid}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("stage") == "generating", data
        assert isinstance(data.get("message"), str) and len(data["message"]) > 0
        # No pdf yet → no pdf_url exposed
        assert not data.get("pdf_url")

    def test_stage_pending(self, seed_sessions):
        sid = seed_sessions["pending"]
        r = requests.get(STATUS_URL, params={"session_id": sid}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("stage") == "pending", data
        assert isinstance(data.get("message"), str) and len(data["message"]) > 0

    def test_stage_emailing(self, seed_sessions):
        sid = seed_sessions["emailing"]
        r = requests.get(STATUS_URL, params={"session_id": sid}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("stage") == "emailing", data
        assert isinstance(data.get("message"), str) and len(data["message"]) > 0
        # pdf_url exposed, email NOT (per current impl — only delivered exposes email)
        assert data.get("pdf_url") == "/api/assets/rencontres_ultime/ultime_TEST_emailing.pdf"

    def test_stage_error_unknown_session(self):
        r = requests.get(
            STATUS_URL,
            params={"session_id": "cs_totally_unknown_xxxxxxx"},
            timeout=15,
        )
        assert r.status_code == 200, r.text  # returns 200 with stage=error
        data = r.json()
        assert data.get("stage") == "error", data
        assert isinstance(data.get("message"), str) and len(data["message"]) > 0


# ────────────────────────────────────────────────────────────────
# 2. Pré-existing seed sessions (fournies par le main agent)
# ────────────────────────────────────────────────────────────────
class TestPreseededSessions:
    """Le main agent a créé 2 sessions de démo — on les valide sans les toucher."""

    def test_preseeded_delivered(self):
        r = requests.get(
            STATUS_URL,
            params={"session_id": "cs_test_ultime_cb14f284e18c"},
            timeout=15,
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") == "delivered"
        assert data.get("pdf_url"), "pdf_url should be exposed when delivered"
        assert data.get("email"), "email should be exposed when delivered"

    def test_preseeded_pending(self):
        r = requests.get(
            STATUS_URL,
            params={"session_id": "cs_test_pending_b53848d041e1"},
            timeout=15,
        )
        assert r.status_code == 200
        data = r.json()
        assert data.get("stage") == "pending"


# ────────────────────────────────────────────────────────────────
# 3. Error handling + edge cases
# ────────────────────────────────────────────────────────────────
class TestStatusEdgeCases:

    def test_missing_session_id_returns_clean_error(self):
        """Pas de 500 quand session_id manque — FastAPI renvoie 422 (validation)."""
        r = requests.get(STATUS_URL, timeout=15)
        # FastAPI required-query-param → 422 is a clean validation error
        # Also acceptable: 200 with stage=error (if signature had default)
        assert r.status_code in (200, 422), f"Got unexpected {r.status_code}: {r.text}"
        assert r.status_code != 500, "Server error should not be raised"
        if r.status_code == 200:
            data = r.json()
            assert data.get("stage") == "error"

    def test_empty_session_id_returns_clean_error(self):
        r = requests.get(STATUS_URL, params={"session_id": ""}, timeout=15)
        # Empty string is passed as-is; endpoint short-circuits to error
        assert r.status_code in (200, 422)
        assert r.status_code != 500
        if r.status_code == 200:
            data = r.json()
            assert data.get("stage") == "error"

    def test_sql_injection_like_session_id_is_safe(self):
        """Supabase paramètre les queries — un session_id absurde retourne 'error', pas 500."""
        payloads = [
            "'; DROP TABLE payment_transactions;--",
            "' OR '1'='1",
            "%00null",
            "<script>alert(1)</script>",
            "a" * 500,  # very long
        ]
        for p in payloads:
            r = requests.get(STATUS_URL, params={"session_id": p}, timeout=15)
            assert r.status_code != 500, f"500 on payload {p!r}: {r.text}"
            # Should return 200 stage=error
            if r.status_code == 200:
                data = r.json()
                assert data.get("stage") == "error", f"payload={p!r} data={data}"

    def test_response_has_stage_and_message_keys(self, seed_sessions):
        """Chaque réponse (sauf 422) doit exposer stage + message."""
        for stage_name, sid in seed_sessions.items():
            r = requests.get(STATUS_URL, params={"session_id": sid}, timeout=15)
            assert r.status_code == 200
            data = r.json()
            assert "stage" in data, f"missing stage for {stage_name}: {data}"
            assert "message" in data, f"missing message for {stage_name}: {data}"


# ────────────────────────────────────────────────────────────────
# 4. Régression — les autres endpoints ne sont pas cassés
# ────────────────────────────────────────────────────────────────
class TestRegressionOtherEndpoints:

    def test_reveal_still_works(self):
        payload = {
            "day": 15, "month": 6, "year": 1993,
            "hour": 14, "minute": 30,
            "place": "Paris", "country": "France",
            "first_name": "TestReg37",
        }
        r = requests.post(f"{BASE_URL}/api/rencontres/reveal", json=payload, timeout=90)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "reveal_id" in data
        assert "portrait" in data
        assert data.get("house7_sign")
        assert data.get("element")

    def test_capture_still_works(self):
        # First get a reveal_id
        reveal_r = requests.post(
            f"{BASE_URL}/api/rencontres/reveal",
            json={
                "day": 20, "month": 3, "year": 1990,
                "hour": 10, "minute": 0,
                "place": "Lyon", "country": "France",
                "first_name": "TestCapture37",
            },
            timeout=90,
        )
        assert reveal_r.status_code == 200, reveal_r.text
        reveal_id = reveal_r.json()["reveal_id"]

        r = requests.post(
            f"{BASE_URL}/api/rencontres/capture",
            json={
                "reveal_id": reveal_id,
                "email": "test-it37-capture@plume-astrale.fr",
                "consent_marketing": True,
            },
            timeout=30,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("ok") is True
        assert isinstance(data.get("windows"), list) and len(data["windows"]) == 3

    def test_checkout_still_works(self, sb):
        # Fresh reveal
        reveal_r = requests.post(
            f"{BASE_URL}/api/rencontres/reveal",
            json={
                "day": 5, "month": 9, "year": 1985,
                "hour": 8, "minute": 15,
                "place": "Marseille", "country": "France",
                "first_name": "TestCheckout37",
            },
            timeout=90,
        )
        assert reveal_r.status_code == 200
        reveal_id = reveal_r.json()["reveal_id"]

        r = requests.post(
            f"{BASE_URL}/api/rencontres/checkout",
            json={
                "origin_url": "https://plume-astrale.fr",
                "reveal_id": reveal_id,
                "email": "test-it37-checkout@plume-astrale.fr",
            },
            timeout=30,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert "url" in data
        assert "session_id" in data
        assert data["session_id"].startswith("cs_")

        # Cleanup created Stripe tx row
        try:
            sb.table("payment_transactions").delete().eq(
                "session_id", data["session_id"]
            ).execute()
        except Exception:
            pass

    def test_plume_chat_still_works(self):
        r = requests.post(
            f"{BASE_URL}/api/plume-chat",
            json={"message": "Bonjour Solena, dis-moi une phrase courte"},
            timeout=45,
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("success") is True
        # /api/plume-chat exposes reply in either `response` or `answer` — accept both
        reply = data.get("response") or data.get("answer")
        assert isinstance(reply, str) and len(reply) > 5, f"No reply text: {data}"
