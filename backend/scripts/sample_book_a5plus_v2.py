"""
sample_book_a5plus_v2.py — Sample étoffé 20 pages, direction éditoriale V2.

Différences vs v1 :
  - ZÉRO symbole emoji-like : uniquement glyphes astronomiques authentiques
    (☉ ☽ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇ + zodiaque ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓)
    et ornements dessinés au canvas ReportLab.
  - Densité de fond réduite : 20 étoiles au lieu de 45, halo divisé par 3.
  - Utilisation intensive de la bibliothèque locale :
      /app/backend/assets/library/signs/     (12 signes)
      /app/backend/assets/library/planets/   (10 planètes)
      /app/backend/assets/library/houses/    (12 maisons)
      /app/backend/assets/pdf_covers/        (heroes chapitres)

Structure 20 pages :
  1. Couverture
  2. Garde ornementale
  3. Page titre
  4. Colophon + dédicace
  5. Table des matières
  6. Épigraphe Ptolémée
  7-8. Intro Soléna (lettre d'ouverture)
  9. Ouverture Chapitre I — Ta carte du ciel
  10-12. Corps Chapitre I (carte, trio, synthèse)
  13. Ouverture Chapitre II — Ton trio identitaire
  14-16. Corps Chapitre II (Soleil Taureau, Lune Sagittaire, Ascendant Gémeaux)
  17. Synthèse trio
  18. Ouverture Chapitre VIII — L'Arbre de Vie (chapitre optionnel)
  19. Les 10 sphères de l'Arbre
  20. Sphère Kéter — la couronne
"""
from __future__ import annotations
import io
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND))

from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak, Image as RLImage,
    Table, TableStyle, KeepTogether, NextPageTemplate,
)

from services.pdf_theme import (
    register_fonts, font,
    GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED, NIGHT, NIGHT_SOFT,
)

register_fonts()

# ═══════════════════════════════════════════════════════════════
# FORMAT & MARGES A5+
# ═══════════════════════════════════════════════════════════════
PAGE_W = 156 * mm
PAGE_H = 234 * mm
INNER = 18 * mm
OUTER = 14 * mm
TOP = 20 * mm
BOTTOM = 20 * mm

BODY_FONT = font('Cormorant', 'Helvetica')
ITALIC_FONT = font('Cormorant-Italic', 'Helvetica-Oblique')
BOLD_FONT = font('Cormorant-Bold', 'Helvetica-Bold')
DISPLAY_FONT = font('Cinzel', 'Helvetica')
DISPLAY_BOLD = font('Cinzel-Bold', 'Helvetica-Bold')
ORN_FONT = 'OrnamentSerif'  # FreeSerif — pour glyphes astro authentiques

# Glyphes astronomiques (FreeSerif les supporte, Cinzel non)
G_SUN, G_MOON = '☉', '☽'
G_MERCURY, G_VENUS, G_MARS = '☿', '♀', '♂'
G_JUPITER, G_SATURN = '♃', '♄'
G_URANUS, G_NEPTUNE, G_PLUTO = '♅', '♆', '♇'
Z_ARIES, Z_TAURUS, Z_GEMINI, Z_CANCER = '♈', '♉', '♊', '♋'
Z_LEO, Z_VIRGO, Z_LIBRA, Z_SCORPIO = '♌', '♍', '♎', '♏'
Z_SAG, Z_CAP, Z_AQUA, Z_PISCES = '♐', '♑', '♒', '♓'

def orn(text: str, size: int = 12, color: str = '#D4AF37') -> str:
    """Wrap un glyphe astro dans FreeSerif (sinon Cinzel affiche des carrés)."""
    return f'<font name="{ORN_FONT}" size="{size}" color="{color}">{text}</font>'


def deg(text: str) -> str:
    """Wrap un degré/minute/seconde (° ′ ″) dans FreeSerif — Cormorant ne les a pas."""
    return f'<font name="{ORN_FONT}">{text}</font>'


# ═══════════════════════════════════════════════════════════════
# ORNEMENTS DESSINÉS AU CANVAS (jamais d'emojis)
# ═══════════════════════════════════════════════════════════════
def celestial_divider(canv, cx: float, cy: float, width: float = 60):
    """Divider célesté : ligne fine + point central doré + petits points latéraux.

    Motif inspiré des frontispices des grimoires du XVIIe.
    """
    canv.saveState()
    canv.setStrokeColor(GOLD)
    canv.setFillColor(GOLD)
    canv.setLineWidth(0.5)
    # Ligne principale
    canv.line(cx - width / 2, cy, cx - 8, cy)
    canv.line(cx + 8, cy, cx + width / 2, cy)
    # Point central losange
    canv.setFillColor(GOLD)
    canv.circle(cx, cy, 1.4, fill=1, stroke=0)
    # 2 points satellites plus petits
    canv.circle(cx - 4, cy, 0.6, fill=1, stroke=0)
    canv.circle(cx + 4, cy, 0.6, fill=1, stroke=0)
    canv.restoreState()


def art_deco_starburst(canv, cx: float, cy: float, radius: float = 12):
    """Rayonnement solaire art-déco : 8 rayons alternés long/court autour d'un point.

    Motif utilisé dans les pages d'ouverture de chapitre.
    """
    import math
    canv.saveState()
    canv.setStrokeColor(GOLD)
    canv.setFillColor(GOLD)
    canv.setLineWidth(0.6)
    # Point central
    canv.circle(cx, cy, 1.6, fill=1, stroke=0)
    # 8 rayons (4 longs, 4 courts alternés)
    for i in range(8):
        angle = i * math.pi / 4
        inner = 3.2
        outer = radius if i % 2 == 0 else radius * 0.6
        x1 = cx + inner * math.cos(angle)
        y1 = cy + inner * math.sin(angle)
        x2 = cx + outer * math.cos(angle)
        y2 = cy + outer * math.sin(angle)
        canv.line(x1, y1, x2, y2)
    canv.restoreState()


def zodiac_ring(canv, cx: float, cy: float, radius: float = 18):
    """Cercle zodiacal miniature : anneau + 12 tick marks aux points cardinaux."""
    import math
    canv.saveState()
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(0.4)
    canv.circle(cx, cy, radius, stroke=1, fill=0)
    canv.setLineWidth(0.3)
    for i in range(12):
        angle = i * math.pi / 6
        x1 = cx + (radius - 2) * math.cos(angle)
        y1 = cy + (radius - 2) * math.sin(angle)
        x2 = cx + (radius + 2) * math.cos(angle)
        y2 = cy + (radius + 2) * math.sin(angle)
        canv.line(x1, y1, x2, y2)
    # Point central
    canv.setFillColor(GOLD)
    canv.circle(cx, cy, 1.2, fill=1, stroke=0)
    canv.restoreState()


def crescent_moon(canv, cx: float, cy: float, size: float = 10):
    """Croissant de lune stylisé (utilisé sur ouvertures de chapitres liées à la Lune)."""
    canv.saveState()
    canv.setStrokeColor(GOLD)
    canv.setFillColor(GOLD)
    canv.setLineWidth(0.6)
    # Cercle plein
    canv.circle(cx, cy, size, fill=1, stroke=0)
    # Cercle "de soustraction" en fond nuit
    canv.setFillColor(NIGHT)
    canv.circle(cx + size * 0.45, cy, size * 0.85, fill=1, stroke=0)
    canv.restoreState()


# ═══════════════════════════════════════════════════════════════
# FOND DE PAGE V2 — moins dense, plus élégant
# ═══════════════════════════════════════════════════════════════
def _bg_common(canv, doc, is_right: bool):
    """Fond nuit sobre + starfield léger + pagination bord extérieur."""
    import random
    canv.saveState()

    # Fond nuit
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Halo doré unique et discret coin haut extérieur
    cx = (PAGE_W - 0.5 * cm) if is_right else (0.5 * cm)
    canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=0.02)
    canv.circle(cx, PAGE_H, 8 * cm, fill=1, stroke=0)
    canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=0.015)
    canv.circle(cx, PAGE_H, 5 * cm, fill=1, stroke=0)

    # Starfield : 20 étoiles (au lieu de 45), plus discret
    r = random.Random(hash(('sf-v2', doc.page)))
    for _ in range(20):
        x = r.uniform(0.8 * cm, PAGE_W - 0.8 * cm)
        y = r.uniform(0.8 * cm, PAGE_H - 0.8 * cm)
        s = r.choice([0.3, 0.4, 0.55])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.15, 0.4))
        canv.circle(x, y, s, fill=1, stroke=0)
    canv.setFillAlpha(1)

    # Ornement en tête (canvas-drawn) pour pages de corps
    if doc.page > 2:
        celestial_divider(canv, PAGE_W / 2, PAGE_H - 12 * mm, width=42)

    # Footer discret : pagination bord extérieur uniquement
    if doc.page > 2:
        canv.setFillColor(MUTED)
        canv.setFont(font('Cinzel', 'Helvetica'), 7)
        num_str = str(doc.page)
        if is_right:
            canv.drawRightString(PAGE_W - OUTER, 10 * mm, num_str)
        else:
            canv.drawString(OUTER, 10 * mm, num_str)
        # Titre courant très discret, centré
        canv.setFont(font('Cinzel', 'Helvetica'), 6.5)
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=0.45)
        canv.drawCentredString(PAGE_W / 2, 10 * mm, "PLUME ASTRALE  ·  LIVRE ASTRAL D'ALEXANDRA")

    canv.restoreState()


def bg_right(canv, doc): _bg_common(canv, doc, is_right=True)
def bg_left(canv, doc):  _bg_common(canv, doc, is_right=False)


# ═══════════════════════════════════════════════════════════════
# BOOK DOCUMENT
# ═══════════════════════════════════════════════════════════════
class BookDocument(BaseDocTemplate):
    def __init__(self, path, **kwargs):
        super().__init__(path, pagesize=(PAGE_W, PAGE_H), pageCompression=1, **kwargs)
        frame_right = Frame(INNER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                            id='right_frame')
        frame_left = Frame(OUTER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                           id='left_frame')
        self.addPageTemplates([
            PageTemplate(id='right', frames=[frame_right], onPage=bg_right),
            PageTemplate(id='left',  frames=[frame_left],  onPage=bg_left),
        ])


# ═══════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════
S = {
    'cover_eyebrow': ParagraphStyle('cover_eyebrow', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_CENTER, spaceAfter=6),
    'cover_title':   ParagraphStyle('cover_title', fontName=BODY_FONT, fontSize=42,
                                     leading=48, textColor=CREAM, alignment=TA_CENTER),
    'cover_name':    ParagraphStyle('cover_name', fontName=DISPLAY_BOLD, fontSize=30,
                                     leading=38, textColor=GOLD_LIGHT, alignment=TA_CENTER),
    'cover_sub':     ParagraphStyle('cover_sub', fontName=ITALIC_FONT, fontSize=15,
                                     leading=22, textColor=CREAM, alignment=TA_CENTER),
    'cover_date':    ParagraphStyle('cover_date', fontName=DISPLAY_FONT, fontSize=8,
                                     textColor=MUTED, alignment=TA_CENTER, spaceBefore=6),
    'title_page':    ParagraphStyle('title_page', fontName=BODY_FONT, fontSize=32,
                                     leading=38, textColor=CREAM, alignment=TA_CENTER),
    'section_tag':   ParagraphStyle('section_tag', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_CENTER, spaceAfter=14),
    'h1':            ParagraphStyle('h1', fontName=BODY_FONT, fontSize=26,
                                     leading=32, textColor=CREAM, alignment=TA_CENTER, spaceAfter=6),
    'h2':            ParagraphStyle('h2', fontName=BOLD_FONT, fontSize=17,
                                     leading=22, textColor=GOLD_LIGHT, spaceBefore=4, spaceAfter=10),
    'h3':            ParagraphStyle('h3', fontName=DISPLAY_FONT, fontSize=11,
                                     leading=16, textColor=GOLD, spaceBefore=8, spaceAfter=4),
    'body':          ParagraphStyle('body', fontName=BODY_FONT, fontSize=11.5,
                                     leading=17, textColor=CREAM, alignment=TA_JUSTIFY, spaceAfter=9),
    'italic':        ParagraphStyle('italic', fontName=ITALIC_FONT, fontSize=13,
                                     leading=20, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=12),
    'italic_left':   ParagraphStyle('italic_left', fontName=ITALIC_FONT, fontSize=12,
                                     leading=18, textColor=LAVENDER, alignment=TA_LEFT, spaceAfter=10),
    'signature':     ParagraphStyle('signature', fontName=ITALIC_FONT, fontSize=13,
                                     textColor=GOLD, alignment=TA_CENTER, spaceBefore=10),
    'toc_line':      ParagraphStyle('toc_line', fontName=BODY_FONT, fontSize=12,
                                     leading=22, textColor=CREAM, alignment=TA_LEFT),
    'toc_num':       ParagraphStyle('toc_num', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_RIGHT),
    'colophon_line': ParagraphStyle('colophon_line', fontName=BODY_FONT, fontSize=10,
                                     leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=3),
    'epigraph':      ParagraphStyle('epigraph', fontName=ITALIC_FONT, fontSize=15,
                                     leading=24, textColor=GOLD_LIGHT, alignment=TA_CENTER,
                                     leftIndent=8 * mm, rightIndent=8 * mm),
    'planet_h':      ParagraphStyle('planet_h', fontName=DISPLAY_BOLD, fontSize=20,
                                     leading=26, textColor=CREAM, alignment=TA_CENTER, spaceAfter=4),
    'planet_meta':   ParagraphStyle('planet_meta', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_CENTER, spaceAfter=14),
}

LIB = _BACKEND / 'assets' / 'library'
COVERS = _BACKEND / 'assets' / 'pdf_covers'

def img(path: Path, w_mm: float, h_mm: float):
    if path.exists():
        return RLImage(str(path), width=w_mm * mm, height=h_mm * mm, mask='auto')
    return Spacer(1, h_mm * mm)


# ═══════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════
def page_cover(story):
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph('PLUME ASTRALE', S['cover_eyebrow']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph('Le Livre Astral', S['cover_title']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('d\'Alexandra', S['cover_name']))
    story.append(Spacer(1, 12 * mm))
    story.append(img(COVERS / 'natal_hero.png', 72, 72))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph('Une carte du ciel personnelle,<br/>lue et racontée pour vous.', S['cover_sub']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('ÉDITION DU 28 FÉVRIER 2026', S['cover_date']))


def page_garde(story):
    # Garde : uniquement un cercle zodiacal miniature centré (canvas-drawn via placeholder)
    # Le zodiac_ring est dessiné dans le fond, mais ici on ajoute un Paragraph invisible
    # pour occuper la page. L'ornement viendra du canvas custom_garde.
    story.append(Spacer(1, 95 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="14">{Z_ARIES}  {Z_LEO}  {Z_SAG}</font>',
        ParagraphStyle('garde_symbols', fontName=ORN_FONT, fontSize=14,
                       textColor=GOLD, alignment=TA_CENTER, leading=22),
    ))


def page_titre(story):
    story.append(Spacer(1, 42 * mm))
    story.append(Paragraph('PLUME ASTRALE', S['cover_eyebrow']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('Le Livre Astral', S['title_page']))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph('d\'Alexandra', S['title_page']))
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph('Composé et signé par Soléna,', S['italic']))
    story.append(Paragraph('astrologue de la maison.', S['italic']))
    story.append(Spacer(1, 35 * mm))
    # Ornement en pied de page (glyphes zodiacaux au lieu d'un symbole)
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="12">{Z_ARIES}  {G_SUN}  {Z_LIBRA}</font>',
        ParagraphStyle('title_orn', fontName=ORN_FONT, fontSize=12,
                       textColor=GOLD, alignment=TA_CENTER),
    ))


def page_colophon(story):
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph('À Alexandra,', S['italic']))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph('née le 15 mai 1990 à Marseille,', S['italic']))
    story.append(Paragraph(f'sous un ciel de Taureau {orn(Z_TAURUS, 13)}.', S['italic']))
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph('Édition numérique · Plume Astrale · 2026', S['colophon_line']))
    story.append(Paragraph('Rédigée à partir des positions Swiss Ephemeris', S['colophon_line']))
    story.append(Paragraph('calculées le 27 février 2026 à 22 h 14.', S['colophon_line']))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph('Composée en Cormorant Garamond & Cinzel.', S['colophon_line']))
    story.append(Paragraph('Illustrations originales de la maison Plume Astrale.', S['colophon_line']))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph('Ce livre a été écrit pour une seule personne. Vous.', S['colophon_line']))


def page_toc(story):
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph('TABLE DES MATIÈRES', S['section_tag']))
    story.append(Spacer(1, 4 * mm))
    entries = [
        ('Ouverture', "Une lettre d'Alexandra à elle-même", '9'),
        ('Chapitre I', 'Ta carte du ciel', '15'),
        ('Chapitre II', 'Ton trio identitaire — Soleil, Lune, Ascendant', '27'),
        ('Chapitre III', 'Les planètes personnelles', '45'),
        ('Chapitre IV', 'Les planètes sociales', '69'),
        ('Chapitre V', 'Les planètes générationnelles', '87'),
        ('Chapitre VI', 'Tes maisons — les douze territoires', '103'),
        ('Chapitre VII', 'Les aspects majeurs de ta vie', '119'),
        ('Chapitre VIII', "L'Arbre de Vie — chapitre choisi", '135'),
        ('Épilogue', 'Ce que tu peux garder de tout ceci', '149'),
    ]
    for tag, title, num in entries:
        t = Table([[
            Paragraph(f'<font color="#D4AF37">{tag}</font>', ParagraphStyle(
                'toc_tag', fontName=DISPLAY_FONT, fontSize=9, textColor=GOLD)),
            Paragraph(title, S['toc_line']),
            Paragraph(num, S['toc_num']),
        ]], colWidths=[26 * mm, 78 * mm, 15 * mm], hAlign='LEFT')
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, -1), 0.15, HexColor('#3A3350')),
        ]))
        story.append(t)


def page_epigraph(story):
    story.append(Spacer(1, 68 * mm))
    story.append(Paragraph(
        '« Les étoiles ne décident rien.<br/>'
        'Elles inclinent, elles éclairent,<br/>'
        'elles se souviennent — mais ne commandent pas. »',
        S['epigraph'],
    ))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph('— Ptolémée, <i>Tétrabible</i>, II<sup>e</sup> siècle', S['colophon_line']))


def page_intro_1(story):
    story.append(Spacer(1, 14 * mm))
    story.append(Paragraph('OUVERTURE', S['section_tag']))
    story.append(Paragraph("Une lettre d'Alexandra à elle-même", S['h1']))
    story.append(Spacer(1, 10 * mm))
    paras = [
        f'<font name="{DISPLAY_BOLD}" color="#D4AF37" size="30">A</font>lexandra, ce livre '
        "n'est pas un horoscope. Ce n'est pas non plus une prédiction — nous ne savons ni ce "
        "que vous ferez demain, ni qui vous rencontrerez, ni ce que vous inventerez de votre "
        "vie. Nous savons seulement, avec la précision de l'astronomie, où se trouvaient les "
        "planètes le matin du <b>15 mai 1990 à 6 h 42</b>, quand vous avez pris votre première "
        "inspiration au vieil hôpital de la Belle-de-Mai.",

        "Ce que nous avons fait de cette information est un travail d'écriture, pas de "
        "divination. Nous avons regardé chaque planète, chaque maison, chaque aspect — nous "
        "nous sommes demandé ce que cette carte-là raconte, à cette personne-là, dans cette "
        "époque-ci. Et nous l'avons écrit à la main, pour vous seule.",

        "Vous verrez, en tournant les pages, que le ton reste sobre. L'astrologie sérieuse "
        "n'a pas besoin d'exclamations. Elle demande de l'attention.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_intro_2(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Comment lire ce livre', S['h2']))
    paras = [
        "Prenez votre temps. Ce livre est calibré pour une lecture de 6 à 8 heures — pas en "
        "une soirée. Un chapitre le dimanche matin, un autre trois semaines plus tard. Il y a "
        "des livres qu'on lit ; celui-ci, on l'habite.",

        "Nous avons volontairement placé, à la fin de chaque chapitre, une <i>page de "
        "respiration</i> : une image, une phrase, parfois rien. Ce vide n'est pas un défaut "
        "d'édition. C'est là que vous êtes invitée à poser le livre, à regarder par la "
        "fenêtre, et à laisser ce qui vient de se lire descendre.",

        f"Les glyphes que vous rencontrerez — {orn(G_SUN, 11)} Soleil, {orn(G_MOON, 11)} Lune, "
        f"{orn(Z_TAURUS, 11)} Taureau, {orn(Z_SAG, 11)} Sagittaire — sont ceux qu'utilisent "
        "les astronomes et les astrologues depuis dix siècles. Ils ne sont pas décoratifs. "
        "Chaque fois qu'ils apparaissent, ils vous rappellent qu'à l'origine de ce texte, il "
        "y a une position réelle dans le ciel réel.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph('— Soléna', S['signature']))


def page_ch1_opening(story):
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph('CHAPITRE I', S['section_tag']))
    story.append(Paragraph('Ta carte du ciel', S['h1']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="14">{Z_TAURUS}   {G_SUN}   {Z_GEMINI}</font>',
        ParagraphStyle('ch1_orn', fontName=ORN_FONT, fontSize=14,
                       textColor=GOLD, alignment=TA_CENTER),
    ))
    story.append(Spacer(1, 12 * mm))
    story.append(img(COVERS / 'natal_hero.png', 78, 78))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        'La photographie du ciel au moment précis<br/>où vous avez pris votre première inspiration.',
        S['italic'],
    ))


def page_ch1_body_1(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Ce que dit votre ciel', S['h2']))
    paras = [
        f'<font name="{DISPLAY_BOLD}" color="#D4AF37" size="30">V</font>otre thème natal a été '
        'calculé pour le <b>15 mai 1990 à 6 h 42</b>, dans le vieil hôpital de la Belle-de-Mai '
        f'à Marseille. À cet instant précis, le Soleil {orn(G_SUN, 11)} se levait à <b>' + deg('24° 12′') + ' '
        f'du Taureau {orn(Z_TAURUS, 11)}</b>, et l\'Ascendant montait à <b>' + deg('3° 47′') + f' du Gémeaux '
        f'{orn(Z_GEMINI, 11)}</b> — deux données qui écrivent, dès la première minute, la '
        'double langue que vous parlerez toute votre vie.',

        "Une naissance à l'aube n'est jamais anodine. La tradition hellénistique l'appelait "
        "<i>diurnal sect</i> : un enfant du jour, dont Jupiter et Saturne reçoivent une charge "
        "de dignité supplémentaire. Chez vous, cela veut dire concrètement que "
        f"<b>Jupiter {orn(G_JUPITER, 11)} en Cancer {orn(Z_CANCER, 11)}, en Maison II</b>, "
        "pèse davantage que la plupart des astrologues ne le lisent — c'est lui qui, "
        "silencieusement, protège votre rapport à la sécurité matérielle.",

        f"La Lune {orn(G_MOON, 11)} était à <b>" + deg('8° 03′') + f" du Sagittaire {orn(Z_SAG, 11)}</b> ce "
        "matin-là, en carré serré (orbe " + deg('2° 15′') + f") avec Vénus {orn(G_VENUS, 11)} rétrograde en "
        f"Poissons {orn(Z_PISCES, 11)}. Ce carré <i>ne se résout pas</i>. Il ne s'agit pas d'un "
        "défaut à corriger : c'est la ligne de faille éditoriale de votre vie affective. Vous "
        "aimerez toujours ce qui échappe, précisément parce qu'il échappe.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_ch1_body_2(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Votre trio identitaire, en un coup d\'œil', S['h2']))
    story.append(Paragraph(
        'Trois planètes structurent la lecture qui suit. Le <b>Soleil</b> raconte ce que vous '
        'venez apprendre. La <b>Lune</b> raconte ce que vous avez apporté avec vous. '
        "L'<b>Ascendant</b> raconte la porte par laquelle vous entrez dans une pièce.",
        S['body'],
    ))
    story.append(Spacer(1, 6 * mm))
    # Table 3 planètes
    def trio_cell(image, glyph, name, sign, sign_glyph, degree):
        return [
            [image] if image else [Spacer(1, 30 * mm)],
            [Paragraph(f'<font name="{ORN_FONT}" color="#D4AF37" size="20">{glyph}</font>',
                       ParagraphStyle('trio_glyph', fontName=ORN_FONT, fontSize=20,
                                       textColor=GOLD, alignment=TA_CENTER, leading=24))],
            [Paragraph(name.upper(),
                       ParagraphStyle('trio_name', fontName=DISPLAY_BOLD, fontSize=10,
                                       textColor=CREAM, alignment=TA_CENTER, spaceBefore=2))],
            [Paragraph(f'{sign} {orn(sign_glyph, 11, "#E8C766")}',
                       ParagraphStyle('trio_sign', fontName=ITALIC_FONT, fontSize=11,
                                       textColor=GOLD_LIGHT, alignment=TA_CENTER))],
            [Paragraph(degree,
                       ParagraphStyle('trio_deg', fontName=DISPLAY_FONT, fontSize=8,
                                       textColor=MUTED, alignment=TA_CENTER, spaceBefore=1))],
        ]

    sun_img = img(LIB / 'planets' / 'sun_512.png', 22, 22) if (LIB / 'planets' / 'sun_512.png').exists() else None
    moon_img = img(LIB / 'planets' / 'moon_512.png', 22, 22)
    # Ascendant → pas de fichier "ascendant" ; on met un cercle avec glyphe
    asc_img = None

    trio_table = Table([
        [
            Table(trio_cell(sun_img, G_SUN, 'Soleil', 'Taureau', Z_TAURUS, deg('24° 12′')), colWidths=[32 * mm]),
            Table(trio_cell(moon_img, G_MOON, 'Lune', 'Sagittaire', Z_SAG, deg('8° 03′')), colWidths=[32 * mm]),
            Table(trio_cell(asc_img, 'AC', 'Ascendant', 'Gémeaux', Z_GEMINI, deg('3° 47′')), colWidths=[32 * mm]),
        ]
    ], colWidths=[35 * mm, 35 * mm, 35 * mm], hAlign='CENTER')
    trio_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(trio_table)

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        'Nous consacrons le prochain chapitre à chacune de ces trois planètes. Vous les '
        'trouverez avec leur position exacte, leur maison, et — surtout — ce qu\'elles ont à '
        'dire de <i>vous</i>, pas d\'un signe astrologique en général.',
        S['body'],
    ))


def page_ch1_body_3(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Les aspects qui font votre carte', S['h2']))
    paras = [
        f"Un thème natal, ce ne sont pas les planètes prises isolément — ce sont les "
        f"<i>conversations</i> qu'elles entretiennent entre elles. On les appelle <b>aspects</b> : "
        f"conjonction (0°), sextile (60°), carré (90°), trigone (120°), opposition (180°). "
        f"Chez vous, six aspects majeurs sortent du lot :",

        f"— <b>Soleil {orn(G_SUN, 11)} carré Saturne {orn(G_SATURN, 11)}</b> (orbe " + deg('1° 42′') + ") : "
        "la voix intérieure critique. Ce que vous entreprenez, vous le faites avec un juge "
        "assis à côté de vous. Cet aspect ne se résout pas, il se <i>domestique</i>.",

        f"— <b>Lune {orn(G_MOON, 11)} trigone Mars {orn(G_MARS, 11)}</b> (orbe " + deg('0° 34′') + ") : "
        "l'aisance émotionnelle dans l'action. Vous sentez ce qui doit être fait avant même "
        "de l'avoir formulé.",

        f"— <b>Vénus {orn(G_VENUS, 11)} rétrograde en Poissons {orn(Z_PISCES, 11)}</b> : "
        "vous êtes née pendant une phase où Vénus semblait reculer dans le ciel. Cette "
        "particularité — que la plupart des gens n'ont pas — pèse sur votre rapport à l'amour "
        "toute votre vie.",

        "Nous vous prions de ne pas retenir ces mots comme des étiquettes. Ils sont, dans les "
        "chapitres suivants, dépliés en récit — car un thème natal se raconte, il ne se "
        "diagnostique pas.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_ch2_opening(story):
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph('CHAPITRE II', S['section_tag']))
    story.append(Paragraph('Ton trio identitaire', S['h1']))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph('Soleil · Lune · Ascendant', S['italic']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="18">{G_SUN}   {G_MOON}   AC</font>',
        ParagraphStyle('ch2_orn', fontName=ORN_FONT, fontSize=18,
                       textColor=GOLD, alignment=TA_CENTER, leading=24),
    ))
    story.append(Spacer(1, 14 * mm))
    # Image roue zodiaque
    story.append(img(LIB / 'style-refs' / 'wheel_ref.png', 72, 72))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        'Trois planètes qui répondent à trois questions.<br/>'
        'Qui suis-je devenue ? Qui étais-je déjà ? Comment est-ce que j\'apparais ?',
        S['italic'],
    ))


def page_sun(story):
    story.append(Spacer(1, 4 * mm))
    # En-tête planète : image + glyphe + nom + signe
    sun_img_path = LIB / 'planets' / 'sun_1080.png'
    if sun_img_path.exists():
        story.append(img(sun_img_path, 32, 32))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="22">{G_SUN}</font>',
        ParagraphStyle('sun_glyph', fontName=ORN_FONT, fontSize=22,
                       textColor=GOLD, alignment=TA_CENTER, leading=26),
    ))
    story.append(Paragraph('Votre Soleil', S['planet_h']))
    story.append(Paragraph(f'TAUREAU {orn(Z_TAURUS, 11)}  ·  MAISON XII  ·  ' + deg('24° 12′') + '', S['planet_meta']))
    paras = [
        "Vous êtes venue apprendre <b>la patience</b>. Pas la patience passive de celle qui "
        "attend — la patience active de celle qui sait qu'un chêne demande cinquante ans, et "
        "qui plante quand même. Le Taureau, chez vous, n'est pas la gourmandise ni le "
        "confort : c'est <i>la fidélité aux choses lentes</i>.",

        "Votre Soleil est placé en <b>Maison XII</b> — la maison la plus discrète du thème. "
        "Cela veut dire que votre puissance solaire ne se voit pas au premier regard. Elle "
        "travaille en sourdine, souvent seule, souvent la nuit. Ce placement est fréquent chez "
        "les gens qui, sans en faire un discours, tiennent quelque chose de fragile.",

        "Ne cherchez pas à briller au sens conventionnel — vous n'êtes pas taillée pour ça, et "
        "chaque fois que vous essayez, vous rentrez épuisée. Cherchez plutôt à <i>durer</i>. "
        "C'est là que votre Soleil s'épanouit.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_moon(story):
    story.append(Spacer(1, 4 * mm))
    moon_img_path = LIB / 'planets' / 'moon_1080.png'
    if moon_img_path.exists():
        story.append(img(moon_img_path, 32, 32))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="22">{G_MOON}</font>',
        ParagraphStyle('moon_glyph', fontName=ORN_FONT, fontSize=22,
                       textColor=GOLD, alignment=TA_CENTER, leading=26),
    ))
    story.append(Paragraph('Votre Lune', S['planet_h']))
    story.append(Paragraph(f'SAGITTAIRE {orn(Z_SAG, 11)}  ·  MAISON VII  ·  ' + deg('8° 03′') + '', S['planet_meta']))
    paras = [
        "Votre Lune est en Sagittaire — un signe de feu, de mouvement, de fuite parfois. Cela "
        "signifie que ce que vous avez apporté avec vous en naissant, ce n'est pas un bagage "
        "de sécurité : c'est un bagage <i>de départ</i>. Enfant, vous étiez celle qui rêvait "
        "d'un ailleurs quand la maison sentait bon la soupe.",

        "En <b>Maison VII</b> — la maison du partenaire —, cette Lune sagittaire cherche "
        "l'amour comme un horizon. Vous êtes attirée par des personnes qui ouvrent l'espace, "
        "qui vous parlent d'endroits où vous n'êtes pas encore allée. À l'inverse, une "
        "relation qui rétrécit votre monde vous fait suffoquer — non pas parce que vous êtes "
        "difficile, mais parce que votre nature émotionnelle a besoin d'oxygène et de "
        "kilomètres.",

        "Le carré de cette Lune avec Vénus rétrograde en Poissons (orbe " + deg('2° 15′') + ") explique une "
        "chose que vous avez sans doute déjà constatée : vous confondez parfois <i>aimer</i> "
        "et <i>vouloir sauver</i>. Ce n'est pas la même chose. Le reste de ce livre y revient.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_asc(story):
    story.append(Spacer(1, 4 * mm))
    # Pas d'image "ascendant" — on met le glyphe zodiaque du signe montant à la place
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="42">{Z_GEMINI}</font>',
        ParagraphStyle('asc_glyph', fontName=ORN_FONT, fontSize=42,
                       textColor=GOLD, alignment=TA_CENTER, leading=48),
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('Votre Ascendant', S['planet_h']))
    story.append(Paragraph(f'GÉMEAUX {orn(Z_GEMINI, 11)}  ·  DÉCAN 1  ·  ' + deg('3° 47′') + '', S['planet_meta']))
    paras = [
        "L'Ascendant est la porte. Ce n'est pas ce que vous êtes — c'est ce que les autres "
        "voient d'abord, quand vous entrez dans une pièce. Le vôtre est en Gémeaux, à un degré "
        "très précoce du signe (" + deg('3° 47′') + "), ce qui donne un accent : vous arrivez <i>en parlant</i>. "
        "Vous ouvrez la porte avec le langage.",

        "Cet ascendant colore ce que vos amis savent de vous : on vous imagine plus rapide "
        "que vous ne l'êtes vraiment, plus légère aussi. C'est un masque commode — il autorise "
        "la sortie de scène. Mais il crée un décalage : les gens qui vous rencontrent en "
        "surface ne voient pas votre Soleil taureau, patient, qui décide de dix ans en dix ans.",

        "L'un des grands chantiers de votre vie sera de faire correspondre <i>l'entrée en "
        "scène</i> (Gémeaux volubile) avec <i>la présence de fond</i> (Taureau silencieux). "
        "Ce n'est pas de la contradiction — c'est la marque d'une personne composée. Vous "
        "apprendrez, avec les années, à ne pas offrir tout de vous à la porte.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def page_trio_synthese(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Synthèse du trio', S['h2']))
    paras = [
        "Prise ensemble, votre triade dessine un portrait qui a peu à voir avec ce que les "
        "magazines vous ont raconté d'un « Taureau ». Vous êtes une <b>Taureau qui parle "
        "Gémeaux et rêve Sagittaire</b> — trois planètes, trois signes différents, trois "
        "élans qui se rencontrent en vous.",

        "C'est cette combinaison qui explique pourquoi les gens ont du mal à vous ranger. Vous "
        "êtes stable et vagabonde. Silencieuse et bavarde. Fidèle et curieuse. Ce n'est pas "
        "une contradiction : c'est <i>un accord de trois notes</i>, qui n'existe qu'en une "
        "seule personne au monde — vous.",

        "Le reste de ce livre déplie cette carte, chapitre par chapitre. Nous vous invitons "
        "à ne pas la lire comme un manuel, mais comme une <b>lettre longue</b> qu'une amie "
        "vous aurait écrite après avoir passé une nuit à regarder le ciel.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('— Soléna', S['signature']))


def page_ch8_opening(story):
    """Ouverture du chapitre optionnel L'Arbre de Vie (kabbalistique)"""
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph('CHAPITRE VIII  ·  CHAPITRE CHOISI', S['section_tag']))
    story.append(Paragraph("L'Arbre de Vie", S['h1']))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph('Les dix Séphiroth appliquées à votre ciel', S['italic']))
    story.append(Spacer(1, 8 * mm))
    story.append(img(COVERS / 'arbre_de_vie_cover.png', 78, 78))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "La kabbale hébraïque traduit tout thème natal<br/>en dix stations d'âme.",
        S['italic'],
    ))


def page_ch8_body_1(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Les dix sphères', S['h2']))
    paras = [
        "L'<b>Arbre de Vie</b> (Etz Ha'Hayim) est la structure centrale de la kabbale — dix "
        "sphères, appelées <i>Séphiroth</i>, reliées par vingt-deux sentiers. Chacune "
        "correspond à une qualité de l'âme et, dans notre lecture, à une planète de votre "
        "ciel personnel.",

        "Voici l'ordre dans lequel nous vous accompagnerons, de la couronne à la racine :",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))
    story.append(Spacer(1, 4 * mm))
    entries = [
        ('1', 'Kéter', 'La Couronne', f'{G_PLUTO} Pluton', '' + deg('17° 43′') + ' Scorpion'),
        ('2', 'Hokhmah', 'La Sagesse', f'{G_URANUS} Uranus', '' + deg('9° 12′') + ' Capricorne'),
        ('3', 'Binah', "L'Intelligence", f'{G_SATURN} Saturne', '' + deg('22° 04′') + ' Capricorne'),
        ('4', 'Hessed', 'La Grâce', f'{G_JUPITER} Jupiter', '' + deg('14° 55′') + ' Cancer'),
        ('5', 'Guévourah', 'La Rigueur', f'{G_MARS} Mars', '' + deg('2° 18′') + ' Bélier'),
        ('6', 'Tiferet', 'La Beauté', f'{G_SUN} Soleil', '' + deg('24° 12′') + ' Taureau'),
        ('7', 'Netzah', "L'Éternité", f'{G_VENUS} Vénus', '' + deg('11° 08′') + ' Poissons'),
        ('8', 'Hod', 'La Splendeur', f'{G_MERCURY} Mercure', '' + deg('3° 44′') + ' Taureau'),
        ('9', 'Yesod', 'Le Fondement', f'{G_MOON} Lune', '' + deg('8° 03′') + ' Sagittaire'),
        ('10', 'Malkhouth', 'Le Royaume', 'AC Ascendant', '' + deg('3° 47′') + ' Gémeaux'),
    ]
    for num, hebrew, meaning, planet, pos in entries:
        t = Table([[
            Paragraph(num, ParagraphStyle('sn', fontName=DISPLAY_BOLD, fontSize=9,
                                           textColor=GOLD, alignment=TA_CENTER)),
            Paragraph(f'<b>{hebrew}</b>', ParagraphStyle('sh', fontName=BODY_FONT, fontSize=11,
                                                          textColor=CREAM)),
            Paragraph(f'<i>{meaning}</i>', ParagraphStyle('sm', fontName=ITALIC_FONT, fontSize=10,
                                                            textColor=MUTED)),
            Paragraph(orn(planet.split()[0], 11) + ' ' + ' '.join(planet.split()[1:]),
                      ParagraphStyle('sp', fontName=BODY_FONT, fontSize=10, textColor=CREAM)),
            Paragraph(pos, ParagraphStyle('spo', fontName=DISPLAY_FONT, fontSize=8,
                                           textColor=GOLD, alignment=TA_RIGHT)),
        ]], colWidths=[8 * mm, 26 * mm, 30 * mm, 26 * mm, 30 * mm], hAlign='LEFT')
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -1), 0.15, HexColor('#3A3350')),
        ]))
        story.append(t)


def page_ch8_body_keter(story):
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f'{orn(G_PLUTO, 24)}', ParagraphStyle(
        'kg', fontName=ORN_FONT, fontSize=24, textColor=GOLD, alignment=TA_CENTER, leading=30)))
    story.append(Paragraph('Kéter · La Couronne', S['planet_h']))
    story.append(Paragraph(f'PLUTON en SCORPION {orn(Z_SCORPIO, 11)}  ·  ' + deg('17° 43′') + '  ·  MAISON VI',
                           S['planet_meta']))
    paras = [
        "Kéter est la première Séphira, celle qui contient toutes les autres — la couronne. "
        f"Dans votre ciel, elle correspond à <b>Pluton {orn(G_PLUTO, 11)} en Scorpion</b>, "
        "à " + deg('17° 43′') + ", dans la Maison VI (celle du travail quotidien et du corps).",

        "Ce placement, votre génération le porte tout entière : Pluton était en Scorpion de "
        "1983 à 1995. Ce que ce n'est pas anodin, en revanche, c'est <i>sa maison</i>. Dans "
        "votre Maison VI, Pluton veut dire une chose : votre transformation la plus profonde "
        "passera par la manière dont vous <b>travaillez</b> et prenez soin de votre corps. Pas "
        "par la relation, pas par la spiritualité — par l'ordinaire des jours.",

        "La kabbale dit de Kéter qu'elle est <i>Ain Soph Aor</i>, la lumière sans fin. "
        "Traduit dans votre vie : quelque chose de vous, dans ces gestes minuscules du "
        "quotidien, tient une flamme qui ne s'éteint pas. Vous le savez déjà, sans doute. Ce "
        "chapitre est là pour vous dire que vous avez raison de le sentir.",
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        f'<font name="{ORN_FONT}" color="#D4AF37" size="12">{Z_SCORPIO}  {G_PLUTO}  {Z_SCORPIO}</font>',
        ParagraphStyle('ke_orn', fontName=ORN_FONT, fontSize=12,
                       textColor=GOLD, alignment=TA_CENTER),
    ))


# ═══════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════
def build(out_path: str) -> None:
    doc = BookDocument(out_path,
                       title='Plume Astrale — Sample v2',
                       author='Plume Astrale',
                       subject='Sample A5+ · 20 pages · direction éditoriale v2')
    story: list = []
    pages = [
        (page_cover,           'right', 'Cover'),
        (page_garde,           'left',  'Garde'),
        (page_titre,           'right', 'Page titre'),
        (page_colophon,        'left',  'Colophon'),
        (page_toc,             'right', 'TOC'),
        (page_epigraph,        'left',  'Épigraphe'),
        (page_intro_1,         'right', 'Intro 1'),
        (page_intro_2,         'left',  'Intro 2'),
        (page_ch1_opening,     'right', 'Ouverture Ch. I'),
        (page_ch1_body_1,      'left',  'Ch. I body 1'),
        (page_ch1_body_2,      'right', 'Ch. I trio'),
        (page_ch1_body_3,      'left',  'Ch. I aspects'),
        (page_ch2_opening,     'right', 'Ouverture Ch. II'),
        (page_sun,             'left',  'Soleil Taureau'),
        (page_moon,            'right', 'Lune Sagittaire'),
        (page_asc,             'left',  'Ascendant Gémeaux'),
        (page_trio_synthese,   'right', 'Synthèse trio'),
        (page_ch8_opening,     'right', 'Ouverture Ch. VIII'),
        (page_ch8_body_1,      'left',  'Les 10 sphères'),
        (page_ch8_body_keter,  'right', 'Kéter'),
    ]
    # Note : le Ch. VIII ouvre sur page 18 (verso) → l'algorithme réel du moteur
    # v1 devra insérer une page blanche pour forcer l'ouverture sur droite.
    # Ici on garde 20 pages exactement pour la démo.
    for i, (fn, tmpl, _label) in enumerate(pages):
        if i == 0:
            story.append(NextPageTemplate(tmpl))
        fn(story)
        if i < len(pages) - 1:
            story.append(NextPageTemplate(pages[i + 1][1]))
            story.append(PageBreak())
    doc.build(story)


if __name__ == '__main__':
    out_dir = Path('/app/frontend/public')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'sample_book_v2.pdf'
    build(str(out_path))
    size_kb = out_path.stat().st_size // 1024
    print(f'✓ Sample v2 généré : {out_path} ({size_kb} Ko)')
    print(f'  Format A5+ : 156 × 234 mm · 20 pages')
    print(f'  Zéro symbole emoji · glyphes astro + ornements canvas')
    print(f'  → Accessible à https://<preview>/sample_book_v2.pdf')
