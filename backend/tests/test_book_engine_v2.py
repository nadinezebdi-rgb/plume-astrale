"""Tests unitaires du moteur v2 — Le Livre Astral (LOT 4.1).

Couvre :
  - wheel : extract_wheel_data, extract_tables_data, format positions/aspects
  - renderer : render_manuscript_to_html (HTML valide, gabarits présents)
  - render_manuscript_to_pdf_v2 : PDF bytes générés + QA basiques
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.book_engine.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)
from services.book_engine_v2.wheel import (
    _fmt_position, _find_aspects, _house_of, _to_longitude_deg,
    extract_tables_data, extract_wheel_data,
)


# ─── Sample astro data ────────────────────────────────────────────
def _sample_astro() -> dict:
    return {
        'planets': {
            'sun': {'sign': 'leo', 'house': 11, 'degree': 7.4},
            'moon': {'sign': 'aries', 'house': 7, 'degree': 18.9},
            'mercury': {'sign': 'leo', 'house': 12, 'degree': 21.2},
            'venus': {'sign': 'cancer', 'house': 10, 'degree': 8.6},
            'mars': {'sign': 'capricorn', 'house': 4, 'degree': 12.3},
            'jupiter': {'sign': 'taurus', 'house': 9, 'degree': 25.1},
            'saturn': {'sign': 'aquarius', 'house': 6, 'degree': 18.7, 'retrograde': True},
            'uranus': {'sign': 'taurus', 'house': 8, 'degree': 6.4},
            'neptune': {'sign': 'capricorn', 'house': 5, 'degree': 27.9, 'retrograde': True},
            'pluto': {'sign': 'sagittarius', 'house': 3, 'degree': 24.5, 'retrograde': True},
            'true node': {'sign': 'scorpio', 'house': 2, 'degree': 2.8, 'retrograde': True},
            'chiron': {'sign': 'aries', 'house': 7, 'degree': 9.3},
        },
        'houses': [{'sign': s, 'degree': d} for s, d in [
            ('virgo', 22.5), ('libra', 20.5), ('scorpio', 21.0),
            ('sagittarius', 22.0), ('capricorn', 21.5), ('aquarius', 20.0),
            ('pisces', 22.0), ('aries', 20.5), ('taurus', 21.0),
            ('gemini', 22.0), ('cancer', 21.5), ('leo', 20.0),
        ]],
    }


# ═══════════════════════════════════════════════════════════════════
# WHEEL
# ═══════════════════════════════════════════════════════════════════
def test_to_longitude_deg_sign_plus_relative():
    lon = _to_longitude_deg({'sign': 'cancer', 'degree': 8.6})
    # Cancer = 90-119.99°, 8.6° dans Cancer = 90 + 8.6 = 98.6
    assert abs(lon - 98.6) < 0.01


def test_fmt_position():
    pos, glyph = _fmt_position(98.6)
    assert pos == '8°36'
    assert glyph == '♋'


def test_house_of_within_cusps():
    cusps = [172.0, 200.5, 231.0, 262.0, 291.5, 320.0, 352.0, 20.5, 51.0, 82.0, 111.5, 140.0]
    # Soleil à Leo 7.4 → lon = 120 + 7.4 = 127.4 → maison 11 (cusp[10]=111.5 → cusp[11]=140)
    assert _house_of(127.4, cusps) == 11


def test_extract_wheel_data_shapes():
    d = extract_wheel_data(_sample_astro())
    assert len(d['svg_cusps']) == 12
    # ~12 planètes (moins si certaines fusionnent : true node ↔ mean node)
    assert len(d['svg_planets']) >= 10
    assert 'Vierge' in d['asc_label']       # Ascendant cusp[0] = Virgo 22.5
    assert 'Gémeaux' in d['mc_label']       # MC cusp[9] = Gemini 22.0


def test_extract_tables_data_aspects_sorted_by_orb():
    d = extract_tables_data(_sample_astro())
    orbs = [a['orb_value'] for a in d['aspects']]
    assert orbs == sorted(orbs)             # aspects triés par serrure


def test_extract_tables_distribution_percentages():
    d = extract_tables_data(_sample_astro())
    line = d['distribution_line']
    assert 'Feu' in line and 'Cardinal' in line
    # Vérifie une syntaxe de pourcentage propre
    import re
    assert re.search(r'Feu\s+\d+', line)


def test_find_aspects_detects_opposition():
    # Deux planètes opposées → aspect détecté
    planets = [('Soleil', 0.0, False), ('Lune', 179.5, False)]
    aspects = _find_aspects(planets)
    assert any(a['name'] == 'Opposition' for a in aspects)


# ═══════════════════════════════════════════════════════════════════
# RENDERER
# ═══════════════════════════════════════════════════════════════════
def _sample_manuscript() -> Manuscript:
    m = Manuscript(
        session_id='test_v2_render',
        user_email='test@x.fr',
        first_name='Amélie',
        birth_data=BirthData(
            date_iso='1990-05-15', time_hhmm='14:30',
            city='Paris', country_code='FR',
            latitude=48.8566, longitude=2.3522,
        ),
        astro_data=_sample_astro(),
        edition=Edition.NUMERIQUE,
        created_at=datetime.now(timezone.utc),
    )
    c1 = Chapter(slug='ciel_naissance', title='Votre ciel de naissance',
                 kicker='Le portrait fixé.', roman_num='I', order=1)
    c1.blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {}))
    m.chapters.append(c1)
    c4 = Chapter(slug='facon_aimer', title="Votre façon d'aimer",
                 kicker='Vénus, chez vous.', roman_num='IV', order=4)
    c4.blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {}))
    c4.blocks.append(ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {
        'text': "Vénus, chez vous, s'est posée en Cancer."
    }))
    c4.blocks.append(ChapterBlock(BlockKind.H2, {'text': 'Ce que Vénus dit'}))
    c4.blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': "Vous aimez sur un mode de refuge."
    }))
    m.chapters.append(c4)
    return m


def test_render_html_contains_cover_and_wheel():
    from services.book_engine_v2 import render_manuscript_to_html
    html = render_manuscript_to_html(_sample_manuscript(), profile='screen')
    # Sanity : couverture, prénom, roue SVG inline, folios
    assert 'Le Livre Astral' in html
    assert 'Amélie' in html
    assert '<svg' in html
    assert 'viewBox="0 0 1000 1000"' in html
    assert 'CHAPITRE' in html.upper() or 'Chapitre' in html


def test_render_pdf_v2_bytes_and_pages():
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    pdf = render_manuscript_to_pdf_v2(_sample_manuscript(), profile='screen')
    assert pdf.startswith(b'%PDF'), 'PDF signature manquante'
    assert len(pdf) > 50_000, f'PDF trop petit ({len(pdf)} bytes)'


def test_render_pdf_v2_qa_page_format_ok(tmp_path):
    """Vérifie que le PDF v2 passe les checks QA de format et de roue."""
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    from services.book_engine_v2.pdf_qa import (
        check_page_format, check_no_bitmap, check_wheel_geometry,
    )
    pdf = render_manuscript_to_pdf_v2(_sample_manuscript(), profile='screen')
    p = tmp_path / 'book.pdf'
    p.write_bytes(pdf)
    assert check_page_format(p).status == 'pass'
    assert check_no_bitmap(p).status == 'pass'
    # Roue en page 6 sur cet exemple (cover, blank, title, blank, ch1-opener, wheel)
    wheel_check = check_wheel_geometry(p, page_num=6)
    assert wheel_check.status in ('pass', 'skip'), wheel_check.detail
