"""Iteration 70 - PDF preview endpoint tests"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://consultation-astro.preview.emergentagent.com").rstrip("/")

PRODUCTS = ["astrocartographie", "kabbale", "karma-destin", "numerologie", "theme-natal", "synastrie"]


@pytest.mark.parametrize("product", PRODUCTS)
def test_pdf_preview_valid(product):
    r = requests.get(f"{BASE_URL}/api/pdf-preview/{product}", timeout=120)
    assert r.status_code == 200, f"{product} status {r.status_code}"
    assert r.headers.get("content-type", "").startswith("application/pdf"), f"{product} CT {r.headers.get('content-type')}"
    assert len(r.content) > 100_000, f"{product} size {len(r.content)}"
    assert r.content[:4] == b"%PDF", f"{product} not a PDF file"


def test_pdf_preview_unknown_404():
    r = requests.get(f"{BASE_URL}/api/pdf-preview/inconnu", timeout=30)
    assert r.status_code == 404
    # Message may be JSON detail
    body = r.text.lower()
    assert "inconnu" in body or "not found" in body or "unknown" in body
