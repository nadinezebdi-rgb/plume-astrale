# Tests for Tirage Complet 78 cartes: /api/tarot/complet + /api/tarot/pdf (type complet)
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
TIMEOUT = 70
_cache = {}


def _draw(nb):
    t0 = time.time()
    r = requests.post(f"{BASE_URL}/api/tarot/complet", json={
        "question": "Mon chemin professionnel 2026 ?", "domaine": "travail",
        "nb_cartes": nb, "first_name": "Camille"}, timeout=TIMEOUT)
    return r, time.time() - t0


# Core draw: 3/5/7 cards, structure, majors+minors, timing
@pytest.mark.parametrize("nb", [3, 5, 7])
def test_tarot_complet_draw(nb):
    r, elapsed = _draw(nb)
    print(f"nb={nb} status={r.status_code} elapsed={elapsed:.1f}s")
    assert r.status_code == 200, r.text[:300]
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    cartes = data["cartes"]
    assert len(cartes) == nb
    assert data["nb_cartes"] == nb
    for c in cartes:
        for k in ("position", "nom", "orientation", "interpretation"):
            assert c.get(k), f"missing {k}"
        assert isinstance(c["is_major"], bool)
        assert c["orientation"] in ("droit", "renverse")
        assert len(c["interpretation"]) > 50, c["interpretation"]
    names = [c["nom"] for c in cartes]
    assert len(set(names)) == nb, "duplicate cards drawn"
    synth = data["synthese"]
    assert synth["nb_majeurs"] + synth["nb_mineurs"] == nb
    assert sum(1 for c in cartes if c["is_major"]) == synth["nb_majeurs"]
    assert synth.get("tendance_generale")
    assert len(synth.get("fil_conducteur", "")) > 30
    assert len(data.get("conseil_final", "")) > 30
    assert elapsed < 55
    _cache[nb] = data


# Invalid nb_cartes falls back to 5
def test_tarot_complet_invalid_nb_fallback():
    r, _ = _draw(4)
    assert r.status_code == 200
    assert len(r.json()["data"]["cartes"]) == 5


# PDF generation for complet type
def test_tarot_pdf_complet():
    data = _cache.get(5)
    if not data:
        r, _ = _draw(5)
        data = r.json()["data"]
    r = requests.post(f"{BASE_URL}/api/tarot/pdf", json={
        "type": "complet", "question": "Mon chemin professionnel 2026 ?",
        "domaine": "travail", "data": data, "prenom": "Camille"}, timeout=TIMEOUT)
    print(f"pdf status={r.status_code} size={len(r.content)} cd={r.headers.get('content-disposition')}")
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
    assert len(r.content) > 1_000_000
    assert "tirage-complet-78" in (r.headers.get("content-disposition") or "")


# PDF with missing cards -> 400
def test_tarot_pdf_missing_data():
    r = requests.post(f"{BASE_URL}/api/tarot/pdf", json={"type": "complet", "data": {}}, timeout=30)
    assert r.status_code == 400
