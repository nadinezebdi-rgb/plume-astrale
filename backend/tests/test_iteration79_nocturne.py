"""Iteration 79 — Nocturne refonte: Lead Magnet + Voyage Karmique."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')


@pytest.fixture(scope='module')
def s():
    return requests.Session()


# ── Regression health/products/packs ─────────────────────────────────
def test_health(s):
    r = s.get(f'{BASE_URL}/api/health', timeout=15)
    assert r.status_code == 200

def test_products(s):
    r = s.get(f'{BASE_URL}/api/products', timeout=15)
    assert r.status_code == 200

def test_packs_contains_voyage_karmique(s):
    r = s.get(f'{BASE_URL}/api/packs', timeout=15)
    assert r.status_code == 200
    data = r.json()
    # data could be dict {packs: ...} or dict of packs
    packs = data.get('packs') if isinstance(data, dict) and 'packs' in data else data
    assert 'voyage_karmique' in packs, f'voyage_karmique missing from packs. keys: {list(packs.keys()) if isinstance(packs, dict) else packs}'
    vk = packs['voyage_karmique']
    assert float(vk['amount']) == 49.00


# ── Lead Magnet ───────────────────────────────────────────────────────
LM_EMAIL = f'test.nocturne-{int(time.time())}@plume-astrale.fr'

def test_lead_magnet_generate(s):
    payload = {
        'email': LM_EMAIL,
        'first_name': 'Aurore',
        'birth_date': '1990-06-15',
    }
    r = s.post(f'{BASE_URL}/api/lead-magnet/generate', json=payload, timeout=60)
    assert r.status_code == 200, f'{r.status_code}: {r.text[:400]}'
    data = r.json()
    assert data.get('success') is True
    assert 'pdf_url' in data and 'token' in data
    pytest.lm_token = data['token']
    pytest.lm_url = data['pdf_url']


def test_lead_magnet_rate_limit(s):
    payload = {
        'email': LM_EMAIL,
        'first_name': 'Aurore',
        'birth_date': '1990-06-15',
    }
    r = s.post(f'{BASE_URL}/api/lead-magnet/generate', json=payload, timeout=30)
    assert r.status_code == 429, f'expected 429 got {r.status_code}: {r.text[:200]}'


def test_lead_magnet_download(s):
    token = getattr(pytest, 'lm_token', None)
    assert token, 'no token from previous test'
    r = s.get(f'{BASE_URL}/api/lead-magnet/download/{token}', timeout=30)
    assert r.status_code == 200
    assert 'application/pdf' in r.headers.get('Content-Type', '')
    assert len(r.content) > 5000, f'PDF too small: {len(r.content)}'
    assert r.content[:4] == b'%PDF'


# ── Voyage Karmique ──────────────────────────────────────────────────
def test_voyage_karmique_checkout(s):
    payload = {
        'email': f'test.vk-{int(time.time())}@plume-astrale.fr',
        'first_name': 'Aurore',
        'birth_date': '1990-06-15',
        'birth_time': '14:30',
        'origin_url': BASE_URL,
    }
    r = s.post(f'{BASE_URL}/api/voyage-karmique/checkout', json=payload, timeout=45)
    assert r.status_code == 200, f'{r.status_code}: {r.text[:400]}'
    data = r.json()
    assert 'url' in data and 'session_id' in data
    assert data['url'].startswith('http')


def test_voyage_karmique_status_unknown(s):
    r = s.get(f'{BASE_URL}/api/voyage-karmique/status?session_id=unknown-session-xyz', timeout=15)
    assert r.status_code == 404, f'expected 404 got {r.status_code}: {r.text[:200]}'
