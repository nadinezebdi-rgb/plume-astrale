"""Security regression : /api/admin/pdf-test/{product} now protected by require_admin.
Also validates that public /api/pdf-preview/{product} remain accessible and core public
routes still respond 200.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    # Fallback for testing environment: read from frontend/.env
    with open('/app/frontend/.env') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BASE_URL = line.split('=', 1)[1].strip().rstrip('/')

PRODUCTS = ['astrocartographie', 'kabbale', 'karma-destin', 'numerologie', 'theme-natal', 'synastrie']


@pytest.fixture(scope='session')
def client():
    s = requests.Session()
    return s


# ── SECURITY : admin pdf-test must require auth ─────────────────────
@pytest.mark.parametrize('product', PRODUCTS)
def test_admin_pdf_test_requires_auth(client, product):
    """Sans Authorization header, doit renvoyer 401 (ou 403)."""
    r = client.get(f'{BASE_URL}/api/admin/pdf-test/{product}?first_name=Lea', timeout=30)
    assert r.status_code in (401, 403), (
        f'Expected 401/403 for unauthenticated /admin/pdf-test/{product}, got {r.status_code}'
    )


def test_admin_pdf_test_bad_token(client):
    """Token invalide → 401."""
    r = client.get(
        f'{BASE_URL}/api/admin/pdf-test/kabbale?first_name=Lea',
        headers={'Authorization': 'Bearer invalid.token.here'},
        timeout=30,
    )
    assert r.status_code in (401, 403)


# ── Public PDF preview must remain open ─────────────────────────────
def test_pdf_preview_public_kabbale(client):
    r = client.get(f'{BASE_URL}/api/pdf-preview/kabbale', timeout=60)
    assert r.status_code == 200, f'kabbale preview failed: {r.status_code}'
    assert r.headers.get('content-type', '').startswith('application/pdf')
    assert len(r.content) > 10_000


def test_pdf_preview_public_astrocartographie(client):
    r = client.get(f'{BASE_URL}/api/pdf-preview/astrocartographie', timeout=60)
    assert r.status_code == 200
    assert r.headers.get('content-type', '').startswith('application/pdf')


# ── Public / core routes regression ─────────────────────────────────
@pytest.mark.parametrize('path', [
    '/credits', '/choix', '/astrocartographie', '/livres',
])
def test_public_pages_return_200(client, path):
    r = client.get(f'{BASE_URL}{path}', timeout=30, allow_redirects=True)
    assert r.status_code == 200, f'{path} returned {r.status_code}'


@pytest.mark.parametrize('old,new', [('/outils/tarot', '/services/tarot')])
def test_outils_redirects(client, old, new):
    """/outils/* SPA-redirect handled client-side. Just ensure the app HTML loads (200)."""
    r = client.get(f'{BASE_URL}{old}', timeout=30, allow_redirects=True)
    assert r.status_code == 200
