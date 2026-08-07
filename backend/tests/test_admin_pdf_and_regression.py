"""Iteration 72 — tests for /api/admin/pdf-test/{product} + regression."""
import os
import urllib.parse
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
TIMEOUT = 120


@pytest.fixture(scope="module")
def s():
    return requests.Session()


# ─── Admin PDF test endpoints ────────────────────────────────────────────
PRODUCTS = ['astrocartographie', 'kabbale', 'karma-destin', 'numerologie', 'theme-natal', 'synastrie']


@pytest.mark.parametrize("product", PRODUCTS)
def test_admin_pdf_test_generates_pdf(s, product):
    first_name = urllib.parse.quote('Léa')
    url = f"{BASE_URL}/api/admin/pdf-test/{product}?first_name={first_name}"
    r = s.get(url, timeout=TIMEOUT)
    assert r.status_code == 200, f"{product} -> {r.status_code}: {r.text[:300]}"
    assert r.headers.get('content-type', '').startswith('application/pdf'), r.headers
    assert r.content[:4] == b'%PDF', "Not a valid PDF"
    assert len(r.content) > 5000, f"PDF too small: {len(r.content)} bytes"


def test_admin_pdf_test_unknown_returns_404(s):
    r = s.get(f"{BASE_URL}/api/admin/pdf-test/unknown", timeout=30)
    assert r.status_code == 404


def test_admin_pdf_test_synastrie_with_partner(s):
    url = f"{BASE_URL}/api/admin/pdf-test/synastrie?first_name=Lucie&partner_name=Adrien"
    r = s.get(url, timeout=TIMEOUT)
    assert r.status_code == 200
    assert r.headers.get('content-type', '').startswith('application/pdf')
    assert r.content[:4] == b'%PDF'
    assert len(r.content) > 5000


# ─── Regression ──────────────────────────────────────────────────────────
REGRESSION_ROUTES = [
    ('/credits', 200),
    ('/choix', 200),
    ('/astrocartographie', 200),
    ('/livres', 200),
    ('/admin/analytics', 200),
]


@pytest.mark.parametrize("path,expected", REGRESSION_ROUTES)
def test_frontend_routes_load(s, path, expected):
    r = s.get(f"{BASE_URL}{path}", timeout=30, allow_redirects=True)
    assert r.status_code == expected, f"{path} -> {r.status_code}"


def test_services_tarot_redirect(s):
    r = s.get(f"{BASE_URL}/services/tarot", timeout=30, allow_redirects=False)
    # Could be 301/302/307/308 or just 200 (SPA)
    assert r.status_code in (200, 301, 302, 307, 308)


def test_outils_tarot_redirect(s):
    r = s.get(f"{BASE_URL}/outils/tarot", timeout=30, allow_redirects=False)
    assert r.status_code in (200, 301, 302, 307, 308)
