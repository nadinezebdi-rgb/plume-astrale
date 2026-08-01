"""Système éditorial "Livre-Roman" pour PDFs Plume Astrale.

Grille typographique fixe. Aucune improvisation. Chaque page appartient à un
modèle listé dans `pdf_editorial_templates.py`. Ce fichier définit :
- La palette exacte (fond, or, blanc-cassé, gris).
- Les tailles typographiques (H_CHAPTER..CAPTION).
- Les espacements canoniques (8, 16, 24, 32, 48, 64 pt).
- Les marges + largeur maximale de ligne.
- Un helper `col()` pour positionner en grille 12-colonnes.
"""
from __future__ import annotations
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

# ─── PALETTE ─────────────────────────────────────────────────────────
BG_NIGHT     = HexColor('#0B1020')
GOLD         = HexColor('#C8A24A')
CREAM        = HexColor('#F8F3E8')
GREY_SUBTLE  = HexColor('#A9B0C3')
BG_NIGHT_HEX = '#0B1020'
GOLD_HEX     = '#C8A24A'
CREAM_HEX    = '#F8F3E8'
GREY_HEX     = '#A9B0C3'

# ─── TYPOGRAPHIE (pt) ────────────────────────────────────────────────
H_CHAPTER = 52   # ouvertures de chapitre monumentales
H_PAGE    = 34   # titre de page
SUBTITLE  = 20   # sous-titre
BODY      = 16   # corps de texte principal
QUOTE     = 24   # citation italique
CALLOUT   = 18   # encadré "à retenir"
CAPTION   = 13   # légendes, notes

# ─── LEADING (interlignage, ~1.3× la taille) ────────────────────────
LEAD_CHAPTER = 60
LEAD_PAGE    = 40
LEAD_BODY    = 22
LEAD_QUOTE   = 32
LEAD_CALLOUT = 24

# ─── ESPACEMENTS ─────────────────────────────────────────────────────
SP_XS = 8
SP_S  = 16
SP_M  = 24
SP_L  = 32
SP_XL = 48
SP_XXL = 64

# ─── LAYOUT PAGE ─────────────────────────────────────────────────────
PAGE_MARGIN_PT = 80          # 80pt de marge chaque côté (règle éditoriale)
MAX_LINE_CHARS = 70          # jamais plus de 70 caractères par ligne

# Grille 12 colonnes — page utile ~ 435pt (595pt A4 - 2×80pt), gutter 12pt
def col(n_cols: int, page_width_pt: float = 595.0, gutter_pt: float = 12.0) -> float:
    """Retourne la largeur en pt de `n_cols` colonnes dans la grille 12."""
    usable = page_width_pt - 2 * PAGE_MARGIN_PT
    single = (usable - 11 * gutter_pt) / 12.0
    return single * n_cols + gutter_pt * (n_cols - 1)


# ─── FONT NAMES (résolus par pdf_theme.font()) ──────────────────────
def _f(name: str, fallback: str) -> str:
    from services.pdf_theme import font
    return font(name, fallback)


def styles_cormorant() -> str:
    return _f('Cormorant Garamond', 'Times-Roman')


def styles_cormorant_italic() -> str:
    return _f('Cormorant Garamond Italic', 'Times-Italic')


def styles_cinzel() -> str:
    return _f('Cinzel', 'Helvetica')
