"""
Iteration 34 — Tests for POST /api/plume-chat rebuilt on astrology-api.io v3.
Verifies:
- Success schema with birth_data
- Opening animation "🪶 Une plume mystique..."
- Markdown formatting (## headings, **bold**, --- separators)
- Astrological configurations mentioned (Vénus/Lune/Mars/Maison V/VII/etc.)
- Ends with an open question (not closed conclusion)
- Works without birth_data (asks for date politely)
- Multi-turn context with same session_id
- Empty message rejected
"""
import os
import re
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback: read from frontend/.env
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass

ENDPOINT = f"{BASE_URL}/api/plume-chat"

OPENING = "🪶 Une plume mystique glisse sur l'écran, traçant ces mots à l'encre d'or"

DEFAULT_BIRTH = {
    "name": "Testeuse",
    "day": 15,
    "month": 5,
    "year": 1990,
    "hour": 12,
    "min": 30,
    "place": "Paris, France",
}


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _post(client, payload):
    return client.post(ENDPOINT, json=payload, timeout=90)


# ═══════════════════════════════════════════════════════════════════
# Health / config check
# ═══════════════════════════════════════════════════════════════════
class TestHealth:
    def test_backend_url_configured(self):
        assert BASE_URL.startswith("http"), f"REACT_APP_BACKEND_URL missing: {BASE_URL!r}"


# ═══════════════════════════════════════════════════════════════════
# Core: success with birth_data
# ═══════════════════════════════════════════════════════════════════
class TestPlumeChatWithBirthData:
    """Envoie un message + birth_data et valide la réponse riche de Soléna."""

    @pytest.fixture(scope="class")
    def success_response(self, api_client):
        sid = f"test-{uuid.uuid4().hex[:12]}"
        payload = {
            "message": "Soléna, révèle-moi mon potentiel amoureux et le portrait de mon futur partenaire.",
            "session_id": sid,
            "birth_data": DEFAULT_BIRTH,
        }
        r = _post(api_client, payload)
        assert r.status_code == 200, f"HTTP {r.status_code} — body: {r.text[:400]}"
        data = r.json()
        return {"data": data, "session_id": sid}

    def test_success_true(self, success_response):
        data = success_response["data"]
        assert data.get("success") is True, f"Expected success=true, got: {data}"

    def test_response_has_answer_field(self, success_response):
        data = success_response["data"]
        assert isinstance(data.get("answer"), str) and len(data["answer"]) > 100, \
            f"answer missing or too short: {data.get('answer')!r}"

    def test_session_id_returned(self, success_response):
        data = success_response["data"]
        assert data.get("session_id") == success_response["session_id"]

    def test_response_starts_with_opening_animation(self, success_response):
        answer = success_response["data"]["answer"]
        # First 200 chars must contain the plume opening
        head = answer[:250]
        assert OPENING in head, (
            f"Opening animation missing in first 250 chars. Head:\n{head!r}"
        )

    def test_response_has_markdown_heading(self, success_response):
        answer = success_response["data"]["answer"]
        assert re.search(r'^#{2,3}\s+\S', answer, re.MULTILINE), \
            "No ## or ### markdown heading found"

    def test_response_has_bold_text(self, success_response):
        answer = success_response["data"]["answer"]
        # At least one **...** bold segment
        assert re.search(r'\*\*[^*]{2,}\*\*', answer), "No **bold** markdown found"

    def test_response_has_horizontal_separator(self, success_response):
        answer = success_response["data"]["answer"]
        assert re.search(r'^\s*---\s*$', answer, re.MULTILINE), \
            "No --- horizontal separator found"

    def test_response_mentions_astrological_config(self, success_response):
        answer = success_response["data"]["answer"].lower()
        keywords = ["vénus", "venus", "lune", "mars", "soleil", "ascendant",
                    "maison v", "maison vii", "maison 5", "maison 7", "jupiter",
                    "saturne", "mercure"]
        found = [k for k in keywords if k in answer]
        assert len(found) >= 1, f"No astrological config mentioned. Answer: {answer[:600]}"

    def test_response_ends_with_open_question(self, success_response):
        answer = success_response["data"]["answer"].rstrip()
        # Must end with '?' (open question, per Règle d'or de la relance)
        last_chunk = answer[-300:]
        assert answer.endswith("?"), (
            f"Answer does not end with an open question. Last 300 chars:\n{last_chunk!r}"
        )

    def test_no_tool_leak_in_response(self, success_response):
        answer = success_response["data"]["answer"]
        # Response must not be raw JSON with action/action_input
        assert not (answer.strip().startswith("{") and '"action"' in answer[:200]), \
            f"Tool leak detected: {answer[:200]!r}"


# ═══════════════════════════════════════════════════════════════════
# Without birth_data → Solena should politely ask for birth info
# ═══════════════════════════════════════════════════════════════════
class TestPlumeChatWithoutBirthData:
    def test_no_birth_data_still_responds(self, api_client):
        sid = f"test-nobd-{uuid.uuid4().hex[:12]}"
        payload = {
            "message": "Bonjour Soléna, peux-tu m'aider ?",
            "session_id": sid,
        }
        r = _post(api_client, payload)
        assert r.status_code == 200, f"HTTP {r.status_code} — {r.text[:300]}"
        data = r.json()
        assert data.get("success") is True, f"Expected success=true, got {data}"
        answer = data.get("answer", "")
        assert len(answer) > 30, f"Answer too short: {answer!r}"
        # Should still open with the plume animation
        assert OPENING in answer[:250], f"Opening animation missing: {answer[:200]!r}"

    def test_no_birth_data_asks_for_date(self, api_client):
        """Solena should mention date/naissance/étoiles when birth_data is absent."""
        sid = f"test-ask-{uuid.uuid4().hex[:12]}"
        payload = {
            "message": "Bonjour Soléna.",
            "session_id": sid,
        }
        r = _post(api_client, payload)
        assert r.status_code == 200
        data = r.json()
        answer = (data.get("answer") or "").lower()
        # Heuristic: should mention naissance/date/étoiles or ask a question
        hints = ["naissance", "date", "né(e)", "née", "étoiles", "astres", "prénom", "lieu"]
        has_hint = any(h in answer for h in hints)
        has_question = "?" in answer
        assert has_hint or has_question, (
            f"Response should ask for birth data or a question. Got: {answer[:400]}"
        )


# ═══════════════════════════════════════════════════════════════════
# Multi-turn context (same session_id) — user_id is None so history is
# not persisted in Supabase, but API should still work for 2 calls.
# ═══════════════════════════════════════════════════════════════════
class TestPlumeChatMultiTurn:
    def test_two_successive_messages_same_session(self, api_client):
        sid = f"test-mt-{uuid.uuid4().hex[:12]}"

        r1 = _post(api_client, {
            "message": "Soléna, parle-moi de ma Vénus.",
            "session_id": sid,
            "birth_data": DEFAULT_BIRTH,
        })
        assert r1.status_code == 200, f"Turn1 failed: {r1.status_code} {r1.text[:300]}"
        d1 = r1.json()
        assert d1.get("success") is True, f"Turn1 not success: {d1}"
        assert d1.get("session_id") == sid

        time.sleep(1)

        r2 = _post(api_client, {
            "message": "Et concernant ma Lune, que peux-tu ajouter ?",
            "session_id": sid,
            "birth_data": DEFAULT_BIRTH,
        })
        assert r2.status_code == 200, f"Turn2 failed: {r2.status_code} {r2.text[:300]}"
        d2 = r2.json()
        assert d2.get("success") is True, f"Turn2 not success: {d2}"
        assert d2.get("session_id") == sid
        answer2 = d2.get("answer", "")
        assert len(answer2) > 100, "Turn2 answer too short"
        # Both responses should have the opening animation
        assert OPENING in answer2[:250], "Turn2 missing opening animation"


# ═══════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════
class TestPlumeChatEdgeCases:
    def test_empty_message_rejected(self, api_client):
        r = _post(api_client, {"message": "", "session_id": "test-empty"})
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") is False
        assert "vide" in (data.get("message") or "").lower()

    def test_no_session_id_autogenerated(self, api_client):
        r = _post(api_client, {
            "message": "Bonjour Soléna.",
            "birth_data": DEFAULT_BIRTH,
        })
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") is True, f"Expected success=true: {data}"
        assert isinstance(data.get("session_id"), str) and len(data["session_id"]) > 5
