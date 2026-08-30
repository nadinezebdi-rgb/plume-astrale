"""Tests unitaires pour le pipeline PDF /composer (LOT 3 P0).

Couvre :
  - svg_bronze : reskin idempotent, résolution `var(--kerykeion-*)`, palette
  - prose_generator : détection anti-slop, extraction signature Vénus,
    formatage degrés / signes FR / maisons romaines
  - pipeline : assemblage minimal (fallback LLM), rendu PDF sans réseau
"""
from __future__ import annotations
import io

import pytest


# ═══════════════════════════════════════════════════════════════
# SVG BRONZE
# ═══════════════════════════════════════════════════════════════
def test_svg_bronze_map_color_dark_to_bronze():
    from services.book_engine.svg_bronze import _map_color, BRONZE, INK, IVORY

    assert _map_color('#000000') == BRONZE
    assert _map_color('#000000', is_text_like=True) == INK
    assert _map_color('#FFFFFF') == IVORY
    # Named
    assert _map_color('black') == BRONZE
    assert _map_color('white') == IVORY
    # None/transparent → passe-plat
    assert _map_color('none') == 'none'
    assert _map_color('') == ''


def test_svg_bronze_resolve_kerykeion_vars():
    from services.book_engine.svg_bronze import _resolve_kerykeion_vars

    txt = 'stroke:var(--kerykeion-color-primary); fill:var(--kerykeion-chart-color-sun);'
    out = _resolve_kerykeion_vars(txt)
    assert 'var(' not in out
    # bronze pour primary, bronze foncé pour sun
    assert '#B8935A' in out
    assert '#A17840' in out


def test_svg_bronze_reskin_idempotent():
    from services.book_engine.svg_bronze import reskin_svg_bronze

    sample = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400' "
        "style='background-color: #0f172a'>"
        "<circle cx='200' cy='200' r='150' stroke='#000' fill='none'/>"
        "<text x='10' y='10' fill='#000'>Test</text>"
        "</svg>"
    )
    once = reskin_svg_bronze(sample)
    twice = reskin_svg_bronze(once)
    assert once == twice, 'reskin doit être idempotent'
    assert 'data-plume-bronze="1"' in once
    # Bronze + ink présents
    assert '#B8935A' in once
    assert '#1C1B26' in once
    # Fond ivoire injecté sur la racine
    assert '#FBF7EE' in once


def test_svg_bronze_kerykeion_full_resolution():
    """Vérifie que toutes les var(--kerykeion-*) sont substituées."""
    import re
    from services.book_engine.svg_bronze import reskin_svg_bronze

    sample = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 550' "
        "style='background-color: var(--kerykeion-chart-color-paper-1)'>"
        "<circle cx='400' cy='275' r='200' "
        "style='stroke:var(--kerykeion-chart-color-zodiac-radix-ring-0); fill:none'/>"
        "<text fill='var(--kerykeion-color-base-content)'>Sun</text>"
        "</svg>"
    )
    out = reskin_svg_bronze(sample)
    # Zéro var(--kerykeion-...) restant
    assert re.search(r'var\(--kerykeion', out) is None


# ═══════════════════════════════════════════════════════════════
# PROSE GENERATOR
# ═══════════════════════════════════════════════════════════════
def test_prose_contains_slop_detection():
    from services.book_engine.prose_generator import contains_slop

    assert 'il est important de noter' in contains_slop(
        'Il est important de noter que Vénus vous invite à…'
    )
    assert 'cosmique' in contains_slop('Une énergie cosmique traverse votre thème.')
    assert contains_slop('Une phrase propre et directe.') == []


def test_prose_extract_venus_signature_from_planets_dict():
    from services.book_engine.prose_generator import extract_venus_signature

    astro = {
        'planets': {
            'venus': {'sign': 'Pisces', 'house': 5, 'degree': 11.13, 'retrograde': True},
            'mars': {'sign': 'Aries', 'house': 1, 'degree': 22.5, 'retrograde': False},
            'moon': {'sign': 'Cancer', 'house': 4, 'degree': 4.9},
            'sun': {'sign': 'Leo', 'house': 5, 'degree': 15.0},
        }
    }
    sig = extract_venus_signature(astro)
    assert sig['venus']['sign_fr'] == 'POISSONS'
    assert sig['venus']['degree'] == '11° 08′'
    assert sig['venus']['house_fr'] == 'MAISON V'
    assert sig['venus']['retrograde'] is True
    assert sig['mars']['sign_fr'] == 'BÉLIER'
    assert sig['lune']['sign_fr'] == 'CANCER'
    assert sig['lune']['degree'] == '4° 54′'


def test_prose_fmt_house_romans():
    from services.book_engine.prose_generator import _fmt_house

    assert _fmt_house(5) == 'MAISON V'
    assert _fmt_house(12) == 'MAISON XII'
    assert _fmt_house(1) == 'MAISON I'
    assert _fmt_house(None) == ''


def test_prose_parse_json_blocks_with_code_fence():
    from services.book_engine.prose_generator import _parse_json_blocks

    raw = '''Voici le résultat:
```json
{"blocks": [
    {"kind": "h2", "data": {"text": "Titre"}},
    {"kind": "paragraph", "data": {"text": "Corps."}}
]}
```
Fin.'''
    blocks = _parse_json_blocks(raw)
    assert len(blocks) == 2
    assert blocks[0]['kind'] == 'h2'


# ═══════════════════════════════════════════════════════════════
# PIPELINE (assemblage minimal, sans réseau)
# ═══════════════════════════════════════════════════════════════
@pytest.mark.asyncio
async def test_pipeline_render_pdf_bytes_with_fallback():
    """Vérifie que le pipeline peut assembler un PDF même sans LLM ni réseau.

    On mock `generate_chapter_iv_love` pour éviter l'appel Claude.
    On mock `_fetch_svg_bronze_png` pour éviter l'appel astrology-api.
    """
    from unittest.mock import patch, AsyncMock
    from datetime import datetime, timezone
    from services.book_engine.pipeline import _assemble_chapters
    from services.book_engine.document import render_manuscript_to_pdf
    from services.book_engine.domain import (
        Manuscript, BirthData, Edition, ChapterBlock, BlockKind,
    )

    astro = {
        'planets': {
            'venus': {'sign': 'Pisces', 'house': 5, 'degree': 11.13},
            'mars': {'sign': 'Aries', 'house': 1, 'degree': 22.5},
            'moon': {'sign': 'Cancer', 'house': 4, 'degree': 4.9},
            'sun': {'sign': 'Leo', 'house': 5, 'degree': 15.0},
        }
    }

    async def _fake_prose(*, first_name, astro_data, session_id):
        return [
            ChapterBlock(BlockKind.H2, {'text': 'Ce que Vénus dit'}),
            ChapterBlock(BlockKind.PARAGRAPH, {'text': 'Un paragraphe de test.'}),
        ]

    with patch(
        'services.book_engine.pipeline.generate_chapter_iv_love',
        side_effect=_fake_prose,
    ):
        chapters = await _assemble_chapters(
            first_name='Amélie',
            astro_data=astro,
            session_id='test_pipeline',
            chart_png_bytes=None,
            chapters_slugs=[],
        )

    assert len(chapters) == 12, 'Doit couvrir les 12 chapitres du socle'
    m = Manuscript(
        session_id='test_pipeline',
        user_email='t@t.fr',
        first_name='Amélie',
        birth_data=BirthData(date_iso='1990-05-15', time_hhmm='12:00',
                             city='Paris', country_code='FR',
                             latitude=48.8, longitude=2.35),
        astro_data=astro,
        edition=Edition.NUMERIQUE,
        chapters=chapters,
        created_at=datetime.now(timezone.utc),
    )
    pdf = render_manuscript_to_pdf(m)
    assert len(pdf) > 20_000
    # PDF header
    assert pdf.startswith(b'%PDF')
