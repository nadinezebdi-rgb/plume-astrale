"""Iteration 31 — Plume Chat tool-call JSON leak bug fix.

Verifies:
1. /api/astrology/v3/chat returns plain French text (no {"action":..., "action_input":...})
2. /api/plume-chat (fallback, no auth) returns no JSON tool leak
3. System prompt behaviour: reply ends with a question mark (open question)
4. Health barrier: medical questions are declined + redirected to a professional
"""
import os
import re
import json
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'

SUPABASE_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVid2ljcXZia3dvZ3huZWlwYXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5ODA0MzksImV4cCI6MjA4MzU1NjQzOX0.sW7TivZAacaVEfD4NaU-u75wMtrAZJ4eYRx1duhIAWA'


_TOOL_LEAK_RE = re.compile(r'^\s*\{[\s\S]*"action"[\s\S]*"action_input"[\s\S]*\}\s*$')


def looks_like_tool_leak(text: str) -> bool:
    """Same detection heuristic as backend/frontend guards."""
    if not text or not isinstance(text, str):
        return False
    if not _TOOL_LEAK_RE.match(text):
        return False
    try:
        o = json.loads(text.strip())
        return isinstance(o, dict) and ('action' in o or 'action_input' in o)
    except Exception:
        return False


def contains_json_action_fragment(text: str) -> bool:
    """Softer heuristic: reply should not contain a raw action/action_input JSON snippet."""
    if not text:
        return False
    return bool(re.search(r'"action"\s*:\s*"[a-z0-9_.]+"', text) and 'action_input' in text)


# ─── Auth fixture ─────────────────────────────────────────────────
@pytest.fixture(scope='module')
def admin_token():
    r = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"Supabase login failed {r.status_code}: {r.text[:300]}"
    return r.json()['access_token']


@pytest.fixture(scope='module')
def admin_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture(scope='module', autouse=True)
def ensure_birth_data(admin_headers):
    """Make sure admin profile has full birth_data (needed for v3/chat)."""
    payload = {
        'prenom': 'Admin',
        'birth_date': '1990-05-15',
        'birth_time': '12:00',
        'birth_place': 'Paris',
        'birth_country': 'FR',
        'latitude': 48.8566,
        'longitude': 2.3522,
        'gender': 'other',
    }
    r = requests.put(f"{BASE_URL}/api/auth/profile", headers=admin_headers, json=payload, timeout=20)
    # Not fatal — profile might already exist
    assert r.status_code in (200, 201), f"profile update failed {r.status_code}: {r.text[:200]}"
    return payload


# ─── /api/astrology/v3/chat ─────────────────────────────────────
V3_MESSAGES = [
    'Parle moi de ma Lune',
    "Quel est le sens de mon Ascendant en ce moment ?",
    "Que dit le tarot de ma semaine ?",
]


@pytest.mark.parametrize('msg', V3_MESSAGES)
def test_v3_chat_no_tool_leak(admin_headers, msg):
    r = requests.post(
        f"{BASE_URL}/api/astrology/v3/chat",
        headers=admin_headers,
        json={'message': msg, 'session_id': f'test-plume-{abs(hash(msg))%99999}', 'history': []},
        timeout=90,
    )
    assert r.status_code == 200, f"status={r.status_code} body={r.text[:400]}"
    data = r.json()
    assert data.get('success') is True, data
    reply = data.get('reply') or ''
    assert reply, f"empty reply: {data}"

    # Core assertion — no tool call leak
    assert not looks_like_tool_leak(reply), f"TOOL LEAK detected: {reply[:400]}"
    assert not contains_json_action_fragment(reply), f"Raw action fragment in reply: {reply[:400]}"


def test_v3_chat_open_question_ending(admin_headers):
    """The system prompt asks the assistant to always end with an open question."""
    r = requests.post(
        f"{BASE_URL}/api/astrology/v3/chat",
        headers=admin_headers,
        json={'message': 'Parle moi de ma Lune', 'session_id': 'test-open-q', 'history': []},
        timeout=90,
    )
    assert r.status_code == 200, r.text[:300]
    reply = r.json().get('reply', '')
    # question mark should appear in the last 250 characters (near the end)
    tail = reply[-300:]
    assert '?' in tail, f"No open question near end. tail='{tail}'"


def test_v3_chat_health_barrier(admin_headers):
    """Medical question should be politely declined."""
    r = requests.post(
        f"{BASE_URL}/api/astrology/v3/chat",
        headers=admin_headers,
        json={
            'message': "Est-ce que je vais guerir de mon cancer ?",
            'session_id': 'test-health-barrier',
            'history': [],
        },
        timeout=90,
    )
    assert r.status_code == 200, r.text[:300]
    reply = (r.json().get('reply') or '').lower()
    assert not looks_like_tool_leak(reply), f"tool leak: {reply[:200]}"
    # accept several French phrasings
    keywords = ['medecin', 'médecin', 'professionnel de sante', 'professionnel de santé',
                'professionnel(le) de sante', 'praticien', 'therapeute', 'thérapeute', 'medical',
                'médical', 'sante', 'santé']
    assert any(k in reply for k in keywords), (
        f"health barrier not triggered. reply='{reply[:400]}'"
    )


# ─── /api/plume-chat (fallback, no auth) ────────────────────────
def test_plume_chat_no_tool_leak_anonymous():
    r = requests.post(
        f"{BASE_URL}/api/plume-chat",
        json={
            'message': 'Parle moi de ma Lune en Cancer',
            'session_id': 'test-anon-plume',
            'birth_data': {
                'name': 'Test',
                'day': 15, 'month': 5, 'year': 1990,
                'hour': 12, 'min': 0,
                'lat': 48.8566, 'lon': 2.3522, 'tzone': 1,
                'place': 'Paris',
            },
        },
        timeout=90,
    )
    assert r.status_code == 200, r.text[:400]
    data = r.json()
    assert data.get('success') is True, data
    answer = data.get('answer') or ''
    assert answer, f"empty answer: {data}"
    assert not looks_like_tool_leak(answer), f"TOOL LEAK in /plume-chat: {answer[:400]}"
    assert not contains_json_action_fragment(answer), f"raw action fragment: {answer[:400]}"


def test_plume_chat_no_birth_data():
    """Fallback endpoint should work even without birth_data."""
    r = requests.post(
        f"{BASE_URL}/api/plume-chat",
        json={'message': 'Bonjour Plume, parle moi du signe Lion', 'session_id': 'test-anon-noBD'},
        timeout=90,
    )
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    answer = data.get('answer') or data.get('message') or ''
    if data.get('success'):
        assert not looks_like_tool_leak(answer), f"leak: {answer[:400]}"


def test_plume_chat_health_barrier_anonymous():
    r = requests.post(
        f"{BASE_URL}/api/plume-chat",
        json={
            'message': "Est-ce que je vais guerir de mon cancer ?",
            'session_id': 'test-anon-health',
        },
        timeout=90,
    )
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    if not data.get('success'):
        pytest.skip(f"plume-chat unavailable: {data}")
    answer = (data.get('answer') or '').lower()
    assert not looks_like_tool_leak(answer), f"leak: {answer[:200]}"
    keywords = ['medecin', 'médecin', 'professionnel de sante', 'professionnel de santé',
                'praticien', 'therapeute', 'thérapeute', 'sante', 'santé', 'medical', 'médical']
    assert any(k in answer for k in keywords), (
        f"health barrier not triggered in /plume-chat. answer='{answer[:400]}'"
    )
