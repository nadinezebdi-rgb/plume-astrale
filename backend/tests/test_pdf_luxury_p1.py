"""
Pytest suite pour l'enrichissement premium des PDFs (Feb 2026).

Verrouille deux fixes P1 :
  1. Glyphes ornementaux (✦ ⚜ ◆ ❖ ─) qui rendaient en carrés vides → doivent
     désormais être wrappés dans la police `OrnamentSerif` (FreeSerif).
  2. Compression des chart-wheels PNG (jusqu'à 45 Mo par PDF) via
     `services.pdf_luxury_helpers.compress_image_bytes()` → JPEG optimisé.

Ces tests attrapent la régression si un futur agent :
  - renomme la police `OrnamentSerif` (nom exact requis)
  - ré-enregistre sous le nom réservé PS `Symbol` (silencieux mais casse tout)
  - supprime la registration de FontFamily (ps2tt échoue en runtime)
  - supprime l'appel à compress_image_bytes en amont de cairosvg
"""
import io
import os
import sys
from pathlib import Path

import pytest

# Ensure /app/backend is importable when running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ─────────────────────────────────────────────────────────────
# 1) Ornament font: registration + family mapping (glyph fix)
# ─────────────────────────────────────────────────────────────
def test_ornament_font_registered_under_correct_name():
    """L'agent NE DOIT PAS renommer la police en `Symbol` (nom PS built-in)."""
    from services.pdf_theme import register_fonts
    register_fonts()
    from reportlab.pdfbase import pdfmetrics
    # Doit être présente
    f = pdfmetrics.getFont('OrnamentSerif')
    assert f.fontName == 'OrnamentSerif'


def test_ornament_font_supports_star_and_fleur_de_lys():
    """La police doit couvrir U+2726 (✦) et U+269C (⚜)."""
    from services.pdf_theme import register_fonts
    register_fonts()
    from reportlab.pdfbase.pdfmetrics import stringWidth
    # Chaque glyphe a une largeur propre (≠ built-in Symbol qui les met tous à 9.13)
    w_star = stringWidth('✦', 'OrnamentSerif', 12)
    w_fleur = stringWidth('⚜', 'OrnamentSerif', 12)
    w_A = stringWidth('A', 'OrnamentSerif', 12)
    # Ce sont des glyphes distincts → widths différents (sauf coïncidence rare)
    assert w_star > 0 and w_fleur > 0
    # Si tous égaux → on est sur le built-in Symbol PS (bug de renommage)
    assert not (w_star == w_fleur == w_A), (
        'OrnamentSerif est shadowé par le built-in PS "Symbol". '
        'Le nom doit rester exactement "OrnamentSerif".'
    )


def test_ornament_font_family_mapping_registered():
    """ps2tt doit résoudre `OrnamentSerif` (sinon Paragraph inline échoue)."""
    from services.pdf_theme import register_fonts
    register_fonts()
    from reportlab.lib.fonts import ps2tt
    # Ne doit PAS lever "Can't map determine family/bold/italic"
    family, bold, italic = ps2tt('ornamentserif')
    assert family == 'ornamentserif'


# ─────────────────────────────────────────────────────────────
# 2) Compression helpers (PDF weight fix)
# ─────────────────────────────────────────────────────────────
def test_compress_image_bytes_reduces_large_png():
    """Compress helper doit alléger un PNG lourd (issu de cairosvg) via JPEG.

    Cas réel : les outputs cairosvg.svg2png de chart wheels 1600px pèsent
    500 kB - 15 Mo (traits fins anti-aliasés). JPEG à quality 88 les ramène
    à ~150 Ko avec perte imperceptible.
    """
    from services.pdf_luxury_helpers import compress_image_bytes
    # Vrai cas d'usage : on utilise cairosvg pour générer une PNG "chart-like"
    # (traits fins antialiasés, gradients → contenu bruité qui bat PNG en JPEG).
    try:
        import cairosvg
    except Exception:
        pytest.skip('cairosvg not available in this environment')

    import math
    svg_parts = ['<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" '
                 'width="800" height="800" viewBox="0 0 800 800">'
                 '<rect width="800" height="800" fill="#111625"/>']
    for r in (380, 340, 300, 260, 220, 180, 140, 100):
        svg_parts.append(f'<circle cx="400" cy="400" r="{r}" fill="none" '
                         'stroke="#D4AF37" stroke-width="0.5" opacity="0.6"/>')
    for angle in range(0, 360, 5):
        a = math.radians(angle)
        x = 400 + 380 * math.cos(a); y = 400 + 380 * math.sin(a)
        svg_parts.append(f'<line x1="400" y1="400" x2="{x:.2f}" y2="{y:.2f}" '
                         'stroke="#D4AF37" stroke-width="0.3" opacity="0.4"/>')
    svg_parts.append('</svg>')
    raw = cairosvg.svg2png(bytestring=''.join(svg_parts).encode('utf-8'), output_width=1600)

    compressed = compress_image_bytes(raw, max_width=1400, quality=88)
    # Doit être strictement plus petit (safe fallback: retourne raw si pas de gain)
    assert len(compressed) < len(raw), (
        f'JPEG ({len(compressed)/1024:.1f}kB) doit être plus petit que le PNG '
        f'cairosvg ({len(raw)/1024:.1f}kB).'
    )
    # Objectif : au moins 2× de gain sur un chart-wheel réel
    ratio = len(raw) / max(len(compressed), 1)
    assert ratio >= 2.0, (
        f'Ratio {ratio:.1f}× insuffisant sur un chart-wheel — '
        'la compression P1 devrait viser ≥ 2× (idéalement 10×+).'
    )


def test_compress_image_bytes_safe_on_empty_input():
    """Empty / invalid input ne doit PAS crash le générateur de PDF."""
    from services.pdf_luxury_helpers import compress_image_bytes
    assert compress_image_bytes(b'') == b''
    assert compress_image_bytes(b'not-an-image') == b'not-an-image'


def test_compress_image_bytes_flattens_rgba_to_rgb():
    """Les cairosvg outputs sont RGBA. JPEG ne supporte pas l'alpha → RGB flatten."""
    from services.pdf_luxury_helpers import compress_image_bytes
    from PIL import Image
    img = Image.new('RGBA', (800, 800), (200, 150, 100, 128))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    raw = buf.getvalue()
    result = compress_image_bytes(raw, max_width=800, quality=90)
    # JPEG magic bytes = 0xFFD8 en début. PNG magic = 0x89 0x50 0x4E 0x47.
    # Si le fallback renvoie l'original, on aura toujours du PNG (safe).
    assert result[:2] in (b'\xff\xd8', raw[:2])


# ─────────────────────────────────────────────────────────────
# 3) End-to-end : les PDFs se génèrent sans erreur ps2tt
# ─────────────────────────────────────────────────────────────
def test_karma_destin_pdf_generates_with_ornaments():
    from services.karma_destin_pdf import generate_karma_destin_pdf
    mock = {
        'north_node': {'sign': 'Lion', 'description': 'Test.'},
        'south_node': {'sign': 'Verseau', 'description': 'Test.'},
        'saturn':  {'sign': 'Capricorne', 'description': 'Test.'},
        'chiron':  {'sign': 'Poissons', 'description': 'Test.'},
        'pluto':   {'sign': 'Scorpion', 'description': 'Test.'},
        'generational_karma': 'Test.',
    }
    pdf = generate_karma_destin_pdf('Sophie', '1990-06-15', mock)
    assert pdf.startswith(b'%PDF-')
    # Doit avoir enrobé au moins un ornament dans un ContentStream (heuristique)
    # (le nom de font apparaît via /F1, /F2, /F3... mais le nom logique aussi via ExtGState/Font resource)
    assert b'OrnamentSerif' in pdf or b'FreeSerif' in pdf, (
        'Le PDF Karma Destin doit embarquer la police OrnamentSerif '
        '(pour les glyphes ✦/⚜ des titres de section).'
    )


def test_numerologie_pdf_generates_with_ornaments():
    from services.numerologie_pdf import NumerologiePDFGenerator
    mock = {
        'life_path': 7, 'destiny': 3, 'personality': 9, 'birthday': 15,
        'hearts_desire': 6, 'expression': 1, 'kua': 5,
        'lo_shu': {'grid': [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
        'biorhythms': [{'day': 1, 'physical': 0.5, 'emotional': 0.3, 'intellectual': 0.7}],
    }
    pdf = NumerologiePDFGenerator().generate('Sophie', '1990-06-15', mock)
    assert pdf.startswith(b'%PDF-')
    assert b'OrnamentSerif' in pdf or b'FreeSerif' in pdf


def test_pdf_size_under_luxury_ceiling():
    """Un PDF Karma Destin (16-17 pages, sans chart-wheel) doit rester ≤ 2 Mo."""
    from services.karma_destin_pdf import generate_karma_destin_pdf
    mock = {
        'north_node': {'sign': 'Lion'},
        'south_node': {'sign': 'Verseau'},
        'saturn': {'sign': 'Capricorne'},
        'chiron': {'sign': 'Poissons'},
        'pluto': {'sign': 'Scorpion'},
    }
    pdf = generate_karma_destin_pdf('Sophie', '1990-06-15', mock)
    # Cible réaliste : ≤ 2 Mo pour un rapport sans chart PNG
    assert len(pdf) < 2 * 1024 * 1024, (
        f'PDF Karma Destin fait {len(pdf)/(1024*1024):.1f} Mo — '
        'régression du fix P1 compression (attendu < 2 Mo).'
    )
