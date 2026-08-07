"""Iteration 71 tests: /livres landing, static PDF covers, PDF preview endpoints regression."""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')

COVERS = ["kabbale_hero.png", "karma_hero.png", "synastrie_hero.png", "natal_hero.png",
          "numerologie_hero.png", "astrocarto_hero.png"]

PDF_PRODUCTS = ["astrocartographie", "kabbale", "karma-destin", "numerologie", "theme-natal", "synastrie"]


@pytest.mark.parametrize("cover", COVERS)
def test_pdf_cover_static(cover):
    r = requests.get(f"{BASE_URL}/api/assets/pdf_covers/{cover}", timeout=30)
    assert r.status_code == 200, f"{cover} -> {r.status_code}"
    assert r.headers.get("content-type", "").startswith("image/png"), f"{cover} content-type: {r.headers.get('content-type')}"
    assert len(r.content) > 1000, f"{cover} too small: {len(r.content)} bytes"


@pytest.mark.parametrize("product", PDF_PRODUCTS)
def test_pdf_preview(product):
    r = requests.get(f"{BASE_URL}/api/pdf-preview/{product}", timeout=60)
    assert r.status_code == 200, f"{product} -> {r.status_code}"
    assert r.headers.get("content-type", "").startswith("application/pdf"), f"{product} ct: {r.headers.get('content-type')}"
    assert len(r.content) > 100_000, f"{product} PDF too small: {len(r.content)} bytes"
