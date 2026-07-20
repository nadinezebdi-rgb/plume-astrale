"""
Charte graphique PDF unifiée pour tous les rapports Plume Astrale.

Palette officielle (dérivée de Kabbale · référence design) :
  - NIGHT      #111625   Fond nuit profonde (page background)
  - NIGHT_SOFT #1A2035   Bloc sombre secondaire
  - GOLD       #D4AF37   Or accent (titres, séparateurs)
  - GOLD_LIGHT #E8C766   Or clair (H2, hover)
  - CREAM      #F5EEE0   Corps texte principal
  - LAVENDER   #E3D7FF   Italiques poétiques
  - MUTED      #9089B5   Textes secondaires, pagination

Typographies :
  - Cinzel (small caps or) → captions, titres, signatures
  - Cormorant Garamond (serif italique) → corps texte, citations

Usage :
    from services.pdf_theme import PALETTE, register_fonts, starfield_bg, make_styles
    register_fonts()
    styles = make_styles()
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#   PALETTE OFFICIELLE
# ═══════════════════════════════════════════════════════════
PALETTE = {
    'NIGHT':      colors.HexColor('#111625'),
    'NIGHT_SOFT': colors.HexColor('#1A2035'),
    'GOLD':       colors.HexColor('#D4AF37'),
    'GOLD_LIGHT': colors.HexColor('#E8C766'),
    'CREAM':      colors.HexColor('#F5EEE0'),
    'LAVENDER':   colors.HexColor('#E3D7FF'),
    'MUTED':      colors.HexColor('#9089B5'),
    'SUCCESS':    colors.HexColor('#8FBC8F'),
    'WARNING':    colors.HexColor('#E8C766'),
    'ROSE':       colors.HexColor('#E8A0BF'),
}

# Alias flat pour import direct
NIGHT      = PALETTE['NIGHT']
NIGHT_SOFT = PALETTE['NIGHT_SOFT']
GOLD       = PALETTE['GOLD']
GOLD_LIGHT = PALETTE['GOLD_LIGHT']
CREAM      = PALETTE['CREAM']
LAVENDER   = PALETTE['LAVENDER']
MUTED      = PALETTE['MUTED']

# ═══════════════════════════════════════════════════════════
#   POLICES
# ═══════════════════════════════════════════════════════════
FONTS_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'fonts'

_FONTS_REGISTERED = False


def register_fonts() -> bool:
    """Enregistre Cinzel + Cormorant Garamond dans ReportLab (idempotent).

    Retourne True si les polices ont été chargées, False sinon (fallback Helvetica).
    """
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return True

    candidates = {
        'Cinzel':        ['Cinzel-Regular.ttf', 'Cinzel.ttf'],
        'Cinzel-Bold':   ['Cinzel-Bold.ttf'],
        'Cormorant':     ['CormorantGaramond-Regular.ttf', 'CormorantGaramond.ttf'],
        'Cormorant-Bold': ['CormorantGaramond-Bold.ttf'],
        'Cormorant-Italic': ['CormorantGaramond-Italic.ttf'],
    }

    loaded_any = False
    for logical_name, files in candidates.items():
        for f in files:
            path = FONTS_DIR / f
            if path.exists():
                try:
                    pdfmetrics.registerFont(TTFont(logical_name, str(path)))
                    loaded_any = True
                    break
                except Exception as e:
                    logger.warning(f"[pdf_theme] failed to load {path}: {e}")

    if not loaded_any:
        logger.info(f"[pdf_theme] custom fonts not found in {FONTS_DIR} — using Helvetica fallback")

    _FONTS_REGISTERED = True
    return loaded_any


def font(name: str, fallback: str = 'Helvetica') -> str:
    """Retourne le nom de police à utiliser (fallback Helvetica si non enregistrée)."""
    try:
        pdfmetrics.getFont(name)
        return name
    except Exception:
        return fallback


# ═══════════════════════════════════════════════════════════
#   STYLES PARAGRAPH (pour Platypus)
# ═══════════════════════════════════════════════════════════
def make_styles() -> dict[str, ParagraphStyle]:
    register_fonts()
    body_font = font('Cormorant', 'Helvetica')
    body_italic = font('Cormorant-Italic', 'Helvetica-Oblique')
    body_bold = font('Cormorant-Bold', 'Helvetica-Bold')
    display_font = font('Cinzel', 'Helvetica')
    display_bold = font('Cinzel-Bold', 'Helvetica-Bold')

    return {
        'title':     ParagraphStyle('title', fontName=display_bold, fontSize=30, textColor=GOLD,
                                    alignment=TA_CENTER, leading=36, spaceAfter=10),
        'subtitle':  ParagraphStyle('subtitle', fontName=body_italic, fontSize=17, textColor=CREAM,
                                    alignment=TA_CENTER, leading=22, spaceAfter=8),
        'caption':   ParagraphStyle('caption', fontName=display_font, fontSize=8, textColor=GOLD,
                                    alignment=TA_CENTER, leading=10),
        'h2':        ParagraphStyle('h2', fontName=display_bold, fontSize=22, textColor=GOLD_LIGHT,
                                    spaceBefore=6, spaceAfter=10, leading=26),
        'h3':        ParagraphStyle('h3', fontName=display_bold, fontSize=15, textColor=GOLD,
                                    spaceBefore=8, spaceAfter=6, leading=18),
        'h3c':       ParagraphStyle('h3c', fontName=display_bold, fontSize=15, textColor=GOLD,
                                    alignment=TA_CENTER, spaceBefore=8, spaceAfter=6, leading=18),
        'meta':      ParagraphStyle('meta', fontName=body_font, fontSize=9, textColor=MUTED, leading=12),
        'body':      ParagraphStyle('body', fontName=body_font, fontSize=10.5, textColor=CREAM,
                                    alignment=TA_JUSTIFY, leading=15, spaceAfter=8),
        'italic':    ParagraphStyle('italic', fontName=body_italic, fontSize=11, textColor=LAVENDER,
                                    alignment=TA_CENTER, leading=15, spaceAfter=10),
        'accent':    ParagraphStyle('accent', fontName=display_bold, fontSize=11, textColor=GOLD,
                                    spaceAfter=4),
        'quote':     ParagraphStyle('quote', fontName=body_italic, fontSize=12.5, textColor=LAVENDER,
                                    alignment=TA_CENTER, leading=17, spaceAfter=14),
        'small':     ParagraphStyle('small', fontName=body_font, fontSize=8.5, textColor=MUTED,
                                    leading=11.5, alignment=TA_CENTER),
        'label':     ParagraphStyle('label', fontName=display_bold, fontSize=9, textColor=GOLD,
                                    spaceBefore=6, spaceAfter=2, leading=11),
    }


# ═══════════════════════════════════════════════════════════
#   FOND DE PAGE COMMUN (starfield + halo doré)
# ═══════════════════════════════════════════════════════════
def starfield_bg(canv, doc, product_name: str = 'Plume Astrale'):
    """Fond de page standard : nuit profonde + halo doré + 30 étoiles + pagination."""
    import random
    canv.saveState()
    from reportlab.lib.pagesizes import A4
    W, H = A4
    # Nuit profonde
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Halo doré radial en haut
    for i, alpha in enumerate([0.02, 0.015, 0.01]):
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
        canv.circle(W / 2, H, (i + 1) * 6 * cm, fill=1, stroke=0)
    # 30 étoiles seed-based (stable par page)
    r = random.Random(hash((doc.page,)))
    for _ in range(30):
        x = r.uniform(1 * cm, W - 1 * cm)
        y = r.uniform(1 * cm, H - 1 * cm)
        s = r.choice([0.4, 0.5, 0.6, 0.8])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
        canv.circle(x, y, s, fill=1, stroke=0)
    # Footer pagination
    canv.setFillColor(MUTED)
    canv.setFont(font('Cormorant', 'Helvetica'), 7)
    canv.drawCentredString(W / 2, 0.9 * cm, f"Plume Astrale · {product_name} · page {doc.page}")
    canv.restoreState()


# ═══════════════════════════════════════════════════════════
#   RAW CANVAS HELPERS (pour PDFs bas-niveau : pdf_generator, compatibility)
# ═══════════════════════════════════════════════════════════
def paint_page_bg(canv, width: float, height: float, product_name: str = ''):
    """Version pour canvas raw : peint le fond nuit + halo + étoiles + footer."""
    import random
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, width, height, fill=1, stroke=0)
    for i, alpha in enumerate([0.02, 0.015, 0.01]):
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
        canv.circle(width / 2, height, (i + 1) * 6 * cm, fill=1, stroke=0)
    r = random.Random(hash((canv.getPageNumber(),)))
    for _ in range(30):
        x = r.uniform(1 * cm, width - 1 * cm)
        y = r.uniform(1 * cm, height - 1 * cm)
        s = r.choice([0.4, 0.5, 0.6, 0.8])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
        canv.circle(x, y, s, fill=1, stroke=0)
    if product_name:
        canv.setFillColor(MUTED)
        canv.setFont(font('Cormorant', 'Helvetica'), 7)
        canv.drawCentredString(width / 2, 0.9 * cm,
                               f"Plume Astrale · {product_name} · page {canv.getPageNumber()}")
