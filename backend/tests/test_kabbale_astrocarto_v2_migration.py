"""Tests migration Kabbale + Astrocarto → book_engine_v2 (Feb 2026).

- Flag OFF → legacy inchangé
- Flag ON  → book_engine_v2 blanc A5
- Fallback silencieux (jamais 500 pour un produit payant)
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'plume_astrale_test_migration')


TREE = {
    'sephiroth': [
        {'english': 'kether', 'name': 'Kether', 'interpretation': 'Ta Couronne.'},
        {'english': 'tiphareth', 'name': 'Tiphareth', 'interpretation': 'Ton cœur solaire.'},
    ],
    'paths': [{'letter': 'א', 'title': 'Aleph', 'interpretation': 'Souffle.'}],
    'daat': {'description': "Da'at."},
    'pillar_balance': {'severity': 30, 'mildness': 40, 'mercy': 30},
    'dominant_sephirah': 'tiphareth',
    'spiritual_focus': 'harmonie',
    'synthesis': 'Synthèse.',
    'tree_of_life_meaning': "L'Arbre de Vie.",
}

CITIES = [
    {'city': 'Lisbonne', 'country': 'Portugal', 'enriched': {'summary': 'Ligne Vénus IC.'}},
]


def test_kabbale_flag_off_uses_legacy(monkeypatch):
    monkeypatch.delenv('USE_V2_KABBALE_ENGINE', raising=False)
    from services.kabbale_pdf import generate_kabbale_pdf
    pdf = generate_kabbale_pdf('Test', '2000-01-01', TREE, None)
    # Legacy = ReportLab → tag %PDF-1.x + skia absent
    assert pdf.startswith(b'%PDF')
    assert b'Skia' not in pdf[:4096]  # legacy ReportLab, pas chromium


def test_kabbale_flag_on_uses_v2(monkeypatch):
    monkeypatch.setenv('USE_V2_KABBALE_ENGINE', '1')
    from services.kabbale_pdf import generate_kabbale_pdf
    pdf = generate_kabbale_pdf('Test', '2000-01-01', TREE, None)
    assert pdf.startswith(b'%PDF')
    # v2 = chromium → producer contient Skia
    assert b'Skia' in pdf[:8192]


def test_astrocarto_flag_off_uses_legacy(monkeypatch):
    monkeypatch.delenv('USE_V2_ASTROCARTO_ENGINE', raising=False)
    from services.astrocartographie_pdf import generate_astrocartographie_pdf
    pdf = generate_astrocartographie_pdf('Test', '2000-01-01', None, CITIES, [], 'ok', [])
    assert pdf.startswith(b'%PDF')
    assert b'Skia' not in pdf[:4096]


def test_astrocarto_flag_on_uses_v2(monkeypatch):
    monkeypatch.setenv('USE_V2_ASTROCARTO_ENGINE', '1')
    from services.astrocartographie_pdf import generate_astrocartographie_pdf
    pdf = generate_astrocartographie_pdf('Test', '2000-01-01', None, CITIES, [], 'ok', [])
    assert pdf.startswith(b'%PDF')
    assert b'Skia' in pdf[:8192]


def test_kabbale_manuscript_builder_structure():
    from services.kabbale_manuscript_builder import build_kabbale_manuscript
    m = build_kabbale_manuscript(
        first_name='Nadine',
        birth_date_iso='1985-06-12',
        tree_of_life=TREE,
        ai_sections={'introduction': 'Cher voyageur.'},
    )
    assert len(m.chapters) == 7  # 7 chapitres
    assert m.first_name == 'Nadine'
    assert m.chapters[0].roman_num == 'I'
    assert m.chapters[-1].roman_num == 'VII'


def test_astrocarto_manuscript_builder_structure():
    from services.astrocarto_manuscript_builder import build_astrocarto_manuscript
    m = build_astrocarto_manuscript(
        first_name='Nadine',
        birth_date_iso='1985-06-12',
        map_svg=None,
        chosen_cities=CITIES,
        bonus_cities=[],
        synthesis_text='Synthèse.',
        lines_data=[],
    )
    assert len(m.chapters) == 5
    assert m.chapters[0].title == "L'astrocartographie"


def test_tarot_reveal_force_refresh():
    """force_refresh doit être accepté et déclencher un miss LLM."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.experience_tarot_reveal import router
    app = FastAPI()
    app.include_router(router, prefix='/api')
    client = TestClient(app)
    r = client.post('/api/experience/tarot-reveal',
                    json={'card_id': 'heart', 'intent_id': 'clarity', 'force_refresh': True})
    assert r.status_code == 200
    body = r.json()
    # force_refresh doit produire 'llm' ou 'fallback' (jamais 'cache' au premier appel post-refresh)
    assert body['source'] in ('llm', 'fallback')
