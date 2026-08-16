"""Backend regression tests — SEO Technical Rebuild P0+P1 (Feb 2026).

Covers:
  - GET /api/health (non-regression)
  - GET /api/sitemap.xml (200, application/xml, no /nos-livres, no /theme-natal-luxe)
  - POST /api/lead-magnet/generate (non-regression)
  - GET /robots.txt (informational — preview infra serves Cloudflare-managed file)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")


# ── Health check ──────────────────────────────────────────────────────
def test_health_ok():
    r = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True


# ── Sitemap ───────────────────────────────────────────────────────────
def test_sitemap_status_and_content_type():
    r = requests.get(f"{BASE_URL}/api/sitemap.xml", timeout=15)
    assert r.status_code == 200
    assert "xml" in r.headers.get("Content-Type", "").lower()
    assert "<urlset" in r.text


def test_sitemap_no_deprecated_urls():
    """After SEO Rebuild P1, /nos-livres and /theme-natal-luxe should be removed."""
    r = requests.get(f"{BASE_URL}/api/sitemap.xml", timeout=15)
    assert r.status_code == 200
    assert "/nos-livres" not in r.text, "sitemap still exposes /nos-livres (must redirect to /livres)"
    assert "/theme-natal-luxe" not in r.text, "sitemap still exposes /theme-natal-luxe (must redirect to /theme-natal)"


# ── Lead magnet (non-regression from previous wave) ───────────────────
def test_lead_magnet_generate():
    payload = {
        "email": "TEST_seo_rebuild@example.com",
        "first_name": "SEOTest",
        "birth_date": "1990-05-15",
        "birth_time": "12:00",
        "birth_city": "Paris",
    }
    r = requests.post(f"{BASE_URL}/api/lead-magnet/generate", json=payload, timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert "token" in data
    assert data.get("pages", 0) > 0


# ── Robots.txt (informational only) ───────────────────────────────────
def test_robots_txt_reachable():
    """Preview infra serves Cloudflare-managed robots.txt overriding /public/robots.txt.
    We only verify the endpoint is reachable — production plume-astrale.fr will
    serve the actual file with Ahrefs/Semrush/Disallow ?q= directives.
    """
    r = requests.get(f"{BASE_URL}/robots.txt", timeout=15)
    assert r.status_code == 200
    assert "User-agent" in r.text
