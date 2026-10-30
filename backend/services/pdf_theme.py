"""
Charte graphique PDF unifiée pour tous les rapports Plume Astrale.

Palette print commune : papier blanc, encre foncée et accents bronze lisibles.

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
import re
from pathlib import Path
from reportlab.platypus import Paragraph
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
    'NIGHT':      colors.white,
    'NIGHT_SOFT': colors.HexColor('#F5F2EA'),
    'GOLD':       colors.HexColor('#79570F'),
    'GOLD_LIGHT': colors.HexColor('#8A6418'),
    'CREAM':      colors.HexColor('#26242B'),
    'LAVENDER':   colors.HexColor('#514657'),
    'MUTED':      colors.HexColor('#5E5A63'),
    'SUCCESS':    colors.HexColor('#28613D'),
    'WARNING':    colors.HexColor('#79570F'),
    'ROSE':       colors.HexColor('#87394F'),
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
        # Allura — cursive manuscrite élégante (Google Fonts, OFL).
        # Usage RESTREINT : citations personnelles, sous-titres émotionnels,
        # dédicaces, messages de fin. JAMAIS pour paragraphes longs (lisibilité).
        # ReportLab embarque + subsette automatiquement la TTF dans le PDF final
        # → rendu strictement identique en numérique et en print (Lulu/Bookelis).
        'Allura':        ['Allura-Regular.ttf'],
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

    # Alias « Cormorant Garamond » : les pages « livre » (pdf_book_pages,
    # pdf_editorial_*) demandent ce nom, jamais enregistré jusqu'ici → elles
    # retombaient en Times alors que les pages planètes utilisaient Cormorant,
    # d'où une typographie incohérente dans un même PDF.
    for alias, source in (
        ('Cormorant Garamond', 'Cormorant'),
        ('Cormorant Garamond Italic', 'Cormorant-Italic'),
        ('Cormorant Garamond Bold', 'Cormorant-Bold'),
    ):
        try:
            if _is_registered(source) and not _is_registered(alias):
                font_file = next(
                    (FONTS_DIR / f for f in candidates[source] if (FONTS_DIR / f).exists()), None)
                if font_file:
                    pdfmetrics.registerFont(TTFont(alias, str(font_file)))
        except Exception as e:
            logger.warning(f"[pdf_theme] alias {alias} failed: {e}")
    # Familles : sans elles, <b>/<i> dans un Paragraph lèvent une erreur de mapping.
    for family, normal, bold, italic in (
        ('Cormorant', 'Cormorant', 'Cormorant-Bold', 'Cormorant-Italic'),
        ('Cormorant Garamond', 'Cormorant Garamond', 'Cormorant Garamond Bold', 'Cormorant Garamond Italic'),
    ):
        if all(_is_registered(n) for n in (normal, bold, italic)):
            try:
                pdfmetrics.registerFontFamily(
                    family, normal=normal, bold=bold, italic=italic, boldItalic=bold)
            except Exception as e:
                logger.warning(f"[pdf_theme] family {family} failed: {e}")

    # Police `OrnamentSerif` pour glyphes ornementaux (✦ ⚜ ◆ ❖ ─).
    # Cormorant/Cinzel ne fournissent PAS ces glyphes — sans cette police,
    # ReportLab affiche des carrés vides (.notdef). FreeSerif couvre le
    # bloc "Dingbats" + "Miscellaneous Symbols" nécessaires à nos ornements.
    # ⚠ NE JAMAIS renommer en "Symbol" (nom PS built-in réservé qui shadow la registration).
    symbol_paths = [
        Path('/usr/share/fonts/truetype/freefont/FreeSerif.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'),
        FONTS_DIR / 'FreeSerif.ttf',
        Path('C:/Windows/Fonts/seguisym.ttf'),
    ]
    for symbol_path in symbol_paths:
        if symbol_path.exists():
            try:
                pdfmetrics.registerFont(TTFont('OrnamentSerif', str(symbol_path)))
                # ReportLab ps2tt fallback ne connaît pas les fonts custom → on doit
                # enregistrer une family mapping pour que `<font name="OrnamentSerif">`
                # dans un Paragraph ne lève pas "Can't map determine family/bold/italic".
                pdfmetrics.registerFontFamily(
                    'OrnamentSerif',
                    normal='OrnamentSerif', bold='OrnamentSerif',
                    italic='OrnamentSerif', boldItalic='OrnamentSerif',
                )
                break
            except Exception as e:
                logger.warning(f"[pdf_theme] failed to load OrnamentSerif font {symbol_path}: {e}")

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


_MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août',
            'septembre', 'octobre', 'novembre', 'décembre']


def format_date_fr(dt=None) -> str:
    """Date en français ('31 juillet 2026'), indépendante de la locale du serveur."""
    from datetime import datetime
    dt = dt or datetime.now()
    return f'{dt.day} {_MOIS_FR[dt.month - 1]} {dt.year}'


def _is_registered(name: str) -> bool:
    try:
        pdfmetrics.getFont(name)
        return True
    except Exception:
        return False


# Glyphes absents de Cinzel / Cormorant : ils s'affichent en carré vide (.notdef).
_ORNAMENT_CHARS = '✦✧❖◆⚜⁘'
_ORNAMENT_FALLBACK = {'✦': '*', '✧': '*', '❖': '*', '◆': '*', '⚜': '*', '⁘': '·'}


def ornament_safe(text: str) -> str:
    """Rend les glyphes ornementaux sûrs : police OrnamentSerif si disponible,
    sinon remplacement par un caractère ASCII (jamais de carré vide)."""
    if not text or not any(c in text for c in _ORNAMENT_CHARS):
        return text
    register_fonts()
    out = []
    has_ornament_font = _is_registered('OrnamentSerif')
    in_ornament_font = False
    for part in re.split(r'(<[^<>]+>)', text):
        if part.startswith('<'):
            low = part.lower()
            if 'name="ornamentserif"' in low or "name='ornamentserif'" in low:
                in_ornament_font = True
            elif low.startswith('</font'):
                in_ornament_font = False
            out.append(part)
            continue
        if has_ornament_font and not in_ornament_font:
            part = re.sub(f'([{_ORNAMENT_CHARS}]+)', r'<font name="OrnamentSerif">\1</font>', part)
        elif not has_ornament_font:
            part = ''.join(_ORNAMENT_FALLBACK.get(c, c) for c in part)
        out.append(part)
    return ''.join(out)


class SafeParagraph(Paragraph):
    """Paragraph qui neutralise les glyphes ornementaux manquants dans la police courante."""

    def __init__(self, text, style=None, *args, **kwargs):
        super().__init__(ornament_safe(text), style, *args, **kwargs)


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
#   FOND DE PAGE COMMUN (papier blanc, sans aplat consommateur d'encre)
# ═══════════════════════════════════════════════════════════
def starfield_bg(canv, doc, product_name: str = 'Plume Astrale'):
    """Fond de page print blanc avec pagination sobre."""
    canv.saveState()
    from reportlab.lib.pagesizes import A4
    W, H = A4
    canv.setFillColor(colors.white)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    canv.setFillColor(MUTED)
    canv.setFont(font('Cormorant', 'Helvetica'), 7)
    canv.drawCentredString(W / 2, 0.9 * cm, f"Plume Astrale · {product_name} · page {doc.page}")
    canv.restoreState()


# ═══════════════════════════════════════════════════════════
#   RAW CANVAS HELPERS (pour PDFs bas-niveau : pdf_generator, compatibility)
# ═══════════════════════════════════════════════════════════
def paint_page_bg(canv, width: float, height: float, product_name: str = ''):
    """Version canvas brut : page blanche et footer à fort contraste."""
    canv.setFillColor(colors.white)
    canv.rect(0, 0, width, height, fill=1, stroke=0)
    if product_name:
        canv.setFillColor(MUTED)
        canv.setFont(font('Cormorant', 'Helvetica'), 7)
        canv.drawCentredString(width / 2, 0.9 * cm,
                               f"Plume Astrale · {product_name} · page {canv.getPageNumber()}")
