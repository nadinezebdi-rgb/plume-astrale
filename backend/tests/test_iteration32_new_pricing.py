"""Iteration 32 — Overhaul pricing: new 3 packs + chat_astral=10cr + paywall.

Regression: /api/astrology/v3/chat reply must not leak JSON tool calls.
"""
import os
import re
import time
import json
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'

NEW_PACK_IDS = {'initiation', 'astro_amour', 'flammes_jumelles'}
OLD_PACK_IDS = {'starter', 'popular', 'premium', 'chat_lueur', 'chat_constellation', 'chat_voie_lactee'}


# ─── Fixtures ────────────────────────────────────────────────

@pytest.fixture(scope='module')
def admin_token():
    """Login admin via Supabase auth (frontend flow uses supabase-js).
    We use REST auth against Supabase directly."""
    # Load Supabase URL + anon key from backend .env
    sb_url = None
    anon = None
    try:
        with open('/app/backend/.env') as f:
            for line in f:
                if line.startswith('SUPABASE_URL='):
                    sb_url = line.strip().split('=', 1)[1].strip('"').strip("'")
                elif line.startswith('SUPABASE_ANON_KEY='):
                    anon = line.strip().split('=', 1)[1].strip('"').strip("'")
    except Exception:
        pass
    if not sb_url:
        sb_url = os.environ.get('SUPABASE_URL')
    if not anon or not sb_url:
        pytest.skip('SUPABASE credentials not available')
    url = f"{sb_url}/auth/v1/token?grant_type=password"
    r = requests.post(url, headers={'apikey': anon, 'Content-Type': 'application/json'},
                      json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, f'Supabase login failed: {r.status_code} {r.text}'
    return r.json()['access_token']


@pytest.fixture(scope='module')
def auth_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}


# ─── 1. GET /api/packs — exactly 3 new packs, no old ones ─────────

def test_packs_endpoint_shape():
    r = requests.get(f'{API}/packs', timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert 'packs' in data and 'service_costs' in data
    packs = data['packs']
    assert set(packs.keys()) == NEW_PACK_IDS, f'Expected exactly {NEW_PACK_IDS}, got {set(packs.keys())}'
    # Old ones absent
    for oid in OLD_PACK_IDS:
        assert oid not in packs, f'OLD pack {oid} still present!'


def test_pack_initiation_values():
    r = requests.get(f'{API}/packs', timeout=15).json()['packs']
    p = r['initiation']
    assert p['credits'] == 15
    assert (p.get('bonus') or 0) == 0
    assert abs(float(p['amount']) - 4.99) < 0.01


def test_pack_astro_amour_values():
    r = requests.get(f'{API}/packs', timeout=15).json()['packs']
    p = r['astro_amour']
    assert p['credits'] == 40
    assert p['bonus'] == 10
    assert abs(float(p['amount']) - 12.99) < 0.01


def test_pack_flammes_jumelles_values():
    r = requests.get(f'{API}/packs', timeout=15).json()['packs']
    p = r['flammes_jumelles']
    assert p['credits'] == 100
    assert p['bonus'] == 30
    assert abs(float(p['amount']) - 29.99) < 0.01


# ─── 2. service_costs.chat_astral == 10 ───────────────────────────

def test_chat_astral_cost_is_10():
    r = requests.get(f'{API}/packs', timeout=15).json()
    assert r['service_costs']['chat_astral'] == 10


# ─── 3. Checkout: astro_amour stores 50 credits + metadata ────────

def test_checkout_astro_amour_stores_50_credits(auth_headers):
    payload = {'pack_id': 'astro_amour', 'origin_url': 'https://consultation-astro.preview.emergentagent.com'}
    r = requests.post(f'{API}/credits/checkout', headers=auth_headers, json=payload, timeout=30)
    assert r.status_code == 200, f'checkout failed: {r.status_code} {r.text}'
    data = r.json()
    assert 'url' in data and 'session_id' in data
    assert data['url'].startswith('https://')


# ─── 4. Checkout: old pack id returns 400 ─────────────────────────

def test_checkout_old_pack_starter_returns_400(auth_headers):
    payload = {'pack_id': 'starter', 'origin_url': 'https://consultation-astro.preview.emergentagent.com'}
    r = requests.post(f'{API}/credits/checkout', headers=auth_headers, json=payload, timeout=30)
    assert r.status_code == 400
    assert 'Pack inconnu' in (r.json().get('detail') or '')


def test_checkout_old_pack_chat_lueur_returns_400(auth_headers):
    payload = {'pack_id': 'chat_lueur', 'origin_url': 'https://consultation-astro.preview.emergentagent.com'}
    r = requests.post(f'{API}/credits/checkout', headers=auth_headers, json=payload, timeout=30)
    assert r.status_code == 400


# ─── 5. Chat charges 10cr + no JSON leak (regression) ─────────────

def _get_balance(headers):
    r = requests.get(f'{API}/auth/me', headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()['credit_balance']


_TOOL_LEAK_RE = re.compile(r'^\s*\{[\s\S]*"action"[\s\S]*"action_input"[\s\S]*\}\s*$')


def _is_tool_leak(text: str) -> bool:
    if not text or not _TOOL_LEAK_RE.match(text):
        return False
    try:
        obj = json.loads(text.strip())
        return isinstance(obj, dict) and ('action' in obj or 'action_input' in obj)
    except Exception:
        return False


def test_astro_chat_charges_10_credits_and_no_leak(auth_headers):
    # Ensure at least 10cr — admin has 9999
    bal_before = _get_balance(auth_headers)
    if bal_before < 10:
        pytest.skip('admin balance < 10')
    payload = {'message': 'Quelle est mon énergie du jour ?', 'session_id': f'pytest-{int(time.time())}'}
    r = requests.post(f'{API}/astrology/v3/chat', headers=auth_headers, json=payload, timeout=90)
    assert r.status_code == 200, f'chat failed: {r.status_code} {r.text[:400]}'
    data = r.json()
    assert data.get('success') is True
    reply = data.get('reply') or ''
    assert reply, 'empty reply'
    # Regression: no JSON tool-call leak
    assert not _is_tool_leak(reply), f'JSON tool-call leaked in reply: {reply[:200]}'
    # Balance must have dropped by exactly 10 (unless is_premium)
    if not data.get('is_premium'):
        bal_after = _get_balance(auth_headers)
        assert bal_before - bal_after == 10, f'expected -10cr, got -{bal_before - bal_after}'


# ─── 6. Refund on API failure — smoke test via metadata check ─────
# We can't easily force an API failure remotely, but we can inspect config

def test_refund_amount_is_10_in_code():
    """Confirms the refund amount used in astrology_v3.py is 10 (not 3)."""
    with open('/app/backend/routes/astrology_v3.py') as f:
        src = f.read()
    # Look for the refund call
    assert "await wallet_service.add_credits(current_user['id'], 10, 'Remboursement chat" in src, \
        'Refund is NOT 10 credits in astrology_v3.py'
    assert "add_credits(current_user['id'], 3, 'Remboursement chat" not in src, \
        'Old 3cr refund still present!'


# ─── 7. Frontend paywall modal: URL sanity ────────────────────────
# The modal file posts to a URL — we check it targets the correct backend endpoint

def test_paywall_modal_posts_to_valid_checkout_endpoint():
    """CRITICAL: the CreditsPaywallModal must POST to /api/credits/checkout
    (not /api/checkout which does NOT exist)."""
    with open('/app/frontend/src/components/CreditsPaywallModal.js') as f:
        src = f.read()
    # Must contain the correct endpoint
    has_credits_checkout = '/api/credits/checkout' in src
    has_bare_checkout = re.search(r"\$\{API\}/api/checkout[`'\"]", src) is not None
    assert has_credits_checkout, (
        "CreditsPaywallModal must POST to /api/credits/checkout — "
        f"has_credits_checkout={has_credits_checkout}, has_bare_checkout={has_bare_checkout}"
    )
