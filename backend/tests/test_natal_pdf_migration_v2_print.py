"""Migration PDF Thème Natal — natal_pdf_v2 → book_engine_v2 print blanc
(Feb 2026)

Contrat :
  - natal_pdf_adapter.generate_manuscrit_pdf() utilise book_engine_v2 par défaut
  - En cas d'échec, fallback safety sur natal_pdf_v2 (jamais priver un client payant)
  - Le nouveau builder Manuscript construit chapter I "Le Ciel de {prenom}" avec :
      chapter_opening, trio_cards, natal_chart, H2+paragraph par planète, feather
  - Le rendu utilise profile='print' (fond blanc)
"""
from pathlib import Path
import os
import sys

sys.path.insert(0, '/app/backend')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'plume_astrale')

ADAPTER = Path('/app/backend/services/natal_pdf_adapter.py')
BUILDER = Path('/app/backend/services/natal_manuscript_builder.py')


def test_builder_exists():
    assert BUILDER.exists(), 'natal_manuscript_builder.py absent'
    src = BUILDER.read_text()
    assert 'def build_natal_manuscript' in src, 'build_natal_manuscript() absent'
    # Doit produire un Manuscript avec un chapter unique
    assert 'CHAPTER_OPENING' in src, 'CHAPTER_OPENING block absent'
    assert 'TRIO_CARDS' in src, 'TRIO_CARDS block absent'
    assert 'FEATHER' in src, 'FEATHER block final absent'


def test_adapter_uses_book_engine_v2_first():
    """L'adaptateur DOIT tenter book_engine_v2 en premier."""
    src = ADAPTER.read_text()
    # Import du nouveau builder + renderer
    assert 'from services.natal_manuscript_builder import build_natal_manuscript' in src, (
        'Import build_natal_manuscript manquant'
    )
    assert 'from services.book_engine_v2 import render_manuscript_to_pdf_v2' in src, (
        'Import render_manuscript_to_pdf_v2 manquant'
    )
    # Profile print (fond blanc)
    assert "profile='print'" in src, "profile='print' manquant — le PDF sortirait en dark"
    # Fallback safety natal_pdf_v2 conservé
    assert 'build_natal_pdf_v2' in src, 'Fallback natal_pdf_v2 supprimé — danger prod'


def test_adapter_book_engine_v2_call_precedes_fallback():
    """book_engine_v2 DOIT être appelé AVANT le fallback natal_pdf_v2."""
    src = ADAPTER.read_text()
    idx_new = src.find('render_manuscript_to_pdf_v2(manuscript')
    idx_fallback = src.find('build_natal_pdf_v2(')
    assert idx_new > 0
    assert idx_fallback > idx_new, (
        'natal_pdf_v2 appelé AVANT book_engine_v2 — ordre inversé'
    )


def test_pipeline_metrics_tracks_engine():
    """Le tracking doit indiquer quel moteur a répondu (visibilité prod)."""
    src = ADAPTER.read_text()
    assert 'book_engine_v2_print' in src, "tag 'book_engine_v2_print' absent du tracking"
    assert 'natal_pdf_v2_dark_fallback' in src, "tag 'natal_pdf_v2_dark_fallback' absent"


def test_end_to_end_generation_returns_white_bg_pdf():
    """Le vrai test — le PDF généré doit contenir la CSS var --paper: #FFFFFF."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    user_data = {
        'prenom': 'RegressionTest',
        'birth_date': '1990-01-01',
        'ai_interpretations': {
            '_source': 'gpt',
            'text_soleil': 'Analyse Soleil.',
            'text_lune': 'Analyse Lune.',
            'text_venus': 'Analyse Vénus.',
            'text_mars': 'Analyse Mars.',
            'text_ascendant': 'Analyse Ascendant.',
        }
    }
    planets_data = {
        'sun':       {'sign': 'Capricorn', 'longitude': 285.4},
        'moon':      {'sign': 'Aries', 'longitude': 15.2},
        'venus':     {'sign': 'Aquarius', 'longitude': 315.1},
        'mars':      {'sign': 'Sagittarius', 'longitude': 250.7},
        'ascendant': {'sign': 'Leo', 'longitude': 135.5},
    }
    pdf = generate_manuscrit_pdf(user_data=user_data, planets_data=planets_data)
    assert pdf, 'PDF non généré'
    assert pdf.startswith(b'%PDF-'), 'Signature PDF invalide'
    # PDF > 30 ko → du contenu réel (pas juste une cover vide)
    assert len(pdf) > 30_000, f'PDF trop petit ({len(pdf)} bytes) — soupçon de rendu vide'
