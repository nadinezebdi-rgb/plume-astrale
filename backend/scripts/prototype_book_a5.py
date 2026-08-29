"""
prototype_book_a5.py — PROTOTYPE v3, 12 pages, direction artistique blanche.

Pivot majeur vs v2 :
  - Fond intérieur BLANC IVOIRE (#FBF7EE), pas de nuit permanente
  - Texte anthracite (#1C1B26)
  - Bronze doré mat (#B8935A) — plus premium que l'or vif sur blanc
  - Bleu nuit uniquement en couverture + garde
  - Beaucoup d'espace blanc (marges généreuses)
  - Signature : PLUME ASTRALE (jamais Soléna)
  - Encarts éditoriaux : Votre Force / Votre Défi

Format : A5 exact = 148 × 210 mm

12 pages :
  1. Couverture (nuit + or spectaculaire)
  2. Page de garde (nuit épurée)
  3. Page titre (blanc)
  4. Sommaire (blanc)
  5. Votre ciel de naissance (blanc + roue)
  6. Ouverture chapitre IV — Votre façon d'aimer (blanc)
  7. Page texte standard (blanc)
  8. Page planète Vénus (blanc)
  9. Encarts Votre Force / Votre Défi (blanc)
  10. Page de respiration (blanc, minimaliste)
  11. Double page premium — citation pleine page (verso, blanc)
  12. Dernière page Plume Astrale (blanc)
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
    Table, TableStyle, NextPageTemplate,
)

from services.pdf_theme import register_fonts, font
register_fonts()

# ═══════════════════════════════════════════════════════════════
# PALETTE V3 — livre d'édition Premium
# ═══════════════════════════════════════════════════════════════
IVORY = HexColor('#FBF7EE')      # Fond papier ivoire
INK = HexColor('#1C1B26')        # Anthracite corps texte
NIGHT = HexColor('#0F1A3C')      # Bleu nuit marque (cover + garde)
BRONZE = HexColor('#B8935A')     # Bronze doré mat (accent intérieur)
BRONZE_LIGHT = HexColor('#C9A97A')
GOLD_VIVID = HexColor('#D4AF37') # Or vif (cover uniquement)
CREAM = HexColor('#F5EEE0')      # Cream (cover text)
MUTED = HexColor('#7A7488')      # Gris pour métas

# ═══════════════════════════════════════════════════════════════
# FORMAT A5 + MARGES
# ═══════════════════════════════════════════════════════════════
PAGE_W = 148 * mm
PAGE_H = 210 * mm

# Marges généreuses — l'espace blanc est premium
INNER = 20 * mm
OUTER = 16 * mm
TOP = 22 * mm
BOTTOM = 22 * mm

# ═══════════════════════════════════════════════════════════════
# POLICES & GLYPHES
# ═══════════════════════════════════════════════════════════════
SERIF = font('Cormorant', 'Helvetica')
ITAL = font('Cormorant-Italic', 'Helvetica-Oblique')
BOLD = font('Cormorant-Bold', 'Helvetica-Bold')
CAPS = font('Cinzel', 'Helvetica')
CAPS_BOLD = font('Cinzel-Bold', 'Helvetica-Bold')
ORN = 'OrnamentSerif'

# Helper : espacement letter-spacing pour Cinzel (ReportLab colapse les espaces normaux)
NBSP = '\u00A0'
def spaced(text: str, gap: int = 2) -> str:
    """Insère des NBSP entre chaque caractère pour un effet letter-spacing.

    gap=2 → 2 NBSP entre lettres ; gap=1 → 1 NBSP.
    Les espaces normaux dans `text` sont convertis en un multiple de NBSP.
    """
    out = []
    for ch in text:
        if ch == ' ':
            out.append(NBSP * (gap + 2))
        else:
            out.append(ch)
    return (NBSP * gap).join(out)

G_SUN, G_MOON = '☉', '☽'
G_VENUS, G_MARS, G_MERCURY = '♀', '♂', '☿'
G_JUPITER, G_SATURN = '♃', '♄'
Z_TAURUS, Z_GEMINI, Z_SAG, Z_PISCES = '♉', '♊', '♐', '♓'

def orn(g: str, size: int = 11, color=BRONZE) -> str:
    return f'<font name="{ORN}" size="{size}" color="{color.hexval() if hasattr(color, "hexval") else color}">{g}</font>'

def deg(text: str) -> str:
    return f'<font name="{ORN}">{text}</font>'


# ═══════════════════════════════════════════════════════════════
# ORNEMENTS CANVAS
# ═══════════════════════════════════════════════════════════════
def hairline(canv, cx: float, cy: float, width: float = 40, color=BRONZE):
    """Filet fin doré horizontal avec point central — délicat, presque invisible."""
    canv.saveState()
    canv.setStrokeColor(color)
    canv.setFillColor(color)
    canv.setLineWidth(0.4)
    canv.line(cx - width / 2, cy, cx - 3, cy)
    canv.line(cx + 3, cy, cx + width / 2, cy)
    canv.circle(cx, cy, 0.9, fill=1, stroke=0)
    canv.restoreState()


def tiny_star(canv, cx: float, cy: float, size: float = 2.2, color=BRONZE):
    """Petite étoile à 4 branches (art-deco), pour numéros de chapitre etc."""
    canv.saveState()
    canv.setStrokeColor(color)
    canv.setFillColor(color)
    canv.setLineWidth(0.35)
    canv.line(cx, cy - size, cx, cy + size)
    canv.line(cx - size, cy, cx + size, cy)
    canv.circle(cx, cy, 0.5, fill=1, stroke=0)
    canv.restoreState()


def corner_bracket(canv, cx: float, cy: float, size: float = 3, color=BRONZE):
    """Petit crochet d'angle (encarts éditoriaux)."""
    canv.saveState()
    canv.setStrokeColor(color)
    canv.setLineWidth(0.5)
    canv.line(cx, cy, cx + size, cy)
    canv.line(cx, cy, cx, cy - size)
    canv.restoreState()


# ═══════════════════════════════════════════════════════════════
# FONDS DE PAGE
# ═══════════════════════════════════════════════════════════════
def bg_cover(canv, doc):
    """Couverture : image de référence Plume Astrale (astro wheel + starfield doré)
    + overlay typographique propre en zones supérieure et inférieure."""
    canv.saveState()
    # 1) Fond nuit de secours
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # 2) Image de référence en plein cadre
    ref = _BACKEND / 'assets' / 'cover_refs' / 'COUVERTURE_PLUME_masked_1400.jpg'
    if ref.exists():
        canv.drawImage(str(ref), 0, 0, width=PAGE_W, height=PAGE_H,
                       preserveAspectRatio=False, mask='auto')
    # 3) Cadre or fin (par-dessus l'image)
    canv.setStrokeColor(GOLD_VIVID)
    canv.setLineWidth(0.6)
    canv.rect(8 * mm, 8 * mm, PAGE_W - 16 * mm, PAGE_H - 16 * mm, stroke=1, fill=0)
    # 4) 4 petits ornements de coins (canvas-drawn)
    for cx, cy in [(14 * mm, PAGE_H - 14 * mm), (PAGE_W - 14 * mm, PAGE_H - 14 * mm),
                   (14 * mm, 14 * mm), (PAGE_W - 14 * mm, 14 * mm)]:
        canv.setStrokeColor(GOLD_VIVID)
        canv.setLineWidth(0.35)
        # petite étoile 4 branches
        for a in [0, 90, 180, 270]:
            import math
            rad = math.radians(a)
            canv.line(cx, cy, cx + 4 * math.cos(rad), cy + 4 * math.sin(rad))
        canv.setFillColor(GOLD_VIVID)
        canv.circle(cx, cy, 0.5, fill=1, stroke=0)
    canv.restoreState()


def bg_garde(canv, doc):
    """Page de garde : bleu nuit épuré, quelques étoiles seulement."""
    import random
    canv.saveState()
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    r = random.Random(84)
    for _ in range(15):
        x = r.uniform(1 * cm, PAGE_W - 1 * cm)
        y = r.uniform(1 * cm, PAGE_H - 1 * cm)
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.15, 0.4))
        canv.circle(x, y, 0.4, fill=1, stroke=0)
    canv.restoreState()


def bg_white(canv, doc, is_right: bool = True, show_folio: bool = True):
    """Fond blanc ivoire — direction artistique intérieure."""
    canv.saveState()
    canv.setFillColor(IVORY)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    if show_folio:
        canv.setFillColor(MUTED)
        canv.setFont(CAPS, 7)
        # Pagination bord extérieur
        num = str(doc.page)
        if is_right:
            canv.drawRightString(PAGE_W - OUTER, 12 * mm, num)
        else:
            canv.drawString(OUTER, 12 * mm, num)
        # Titre courant très discret, centré
        canv.setFont(CAPS, 6.5)
        canv.setFillColor(HexColor('#A19986'))
        canv.drawCentredString(PAGE_W / 2, 12 * mm, "LE  LIVRE  ASTRAL  D'ALEXANDRA")
    canv.restoreState()


def bg_white_right(canv, doc): bg_white(canv, doc, is_right=True)
def bg_white_left(canv, doc):  bg_white(canv, doc, is_right=False)
def bg_white_right_no_folio(canv, doc): bg_white(canv, doc, is_right=True, show_folio=False)


# ═══════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════
S = {
    # Couverture
    'cover_top': ParagraphStyle('cover_top', fontName=CAPS, fontSize=8.5,
                                textColor=GOLD_VIVID, alignment=TA_CENTER,
                                spaceAfter=4),
    'cover_of': ParagraphStyle('cover_of', fontName=ITAL, fontSize=14,
                                textColor=CREAM, alignment=TA_CENTER, spaceAfter=4),
    'cover_name': ParagraphStyle('cover_name', fontName=BOLD, fontSize=44,
                                  textColor=GOLD_VIVID, alignment=TA_CENTER,
                                  leading=52, spaceAfter=10),
    'cover_sub': ParagraphStyle('cover_sub', fontName=ITAL, fontSize=11,
                                 textColor=CREAM, alignment=TA_CENTER, leading=17),
    'cover_brand': ParagraphStyle('cover_brand', fontName=CAPS, fontSize=8,
                                    textColor=GOLD_VIVID, alignment=TA_CENTER,
                                    spaceBefore=6),
    'cover_brand_sub': ParagraphStyle('cover_brand_sub', fontName=ITAL, fontSize=8.5,
                                        textColor=CREAM, alignment=TA_CENTER,
                                        spaceBefore=3, leading=13),
    # Garde
    'garde_top': ParagraphStyle('garde_top', fontName=CAPS, fontSize=7,
                                 textColor=BRONZE_LIGHT, alignment=TA_CENTER),
    'garde_name': ParagraphStyle('garde_name', fontName=BOLD, fontSize=26,
                                  textColor=CREAM, alignment=TA_CENTER, leading=32),
    # Page titre blanc
    'title_brand': ParagraphStyle('title_brand', fontName=CAPS, fontSize=8.5,
                                    textColor=BRONZE, alignment=TA_CENTER),
    'title_h1': ParagraphStyle('title_h1', fontName=SERIF, fontSize=32,
                                textColor=INK, alignment=TA_CENTER, leading=40),
    'title_name': ParagraphStyle('title_name', fontName=SERIF, fontSize=32,
                                    textColor=INK, alignment=TA_CENTER, leading=40),
    'title_sub': ParagraphStyle('title_sub', fontName=ITAL, fontSize=12,
                                 textColor=MUTED, alignment=TA_CENTER, leading=18),
    # Structure intérieure
    'section_cap': ParagraphStyle('section_cap', fontName=CAPS, fontSize=8,
                                   textColor=BRONZE, alignment=TA_CENTER,
                                   spaceAfter=10),
    'section_cap_left': ParagraphStyle('section_cap_left', fontName=CAPS, fontSize=8,
                                        textColor=BRONZE, alignment=TA_LEFT,
                                        spaceAfter=6),
    'h1': ParagraphStyle('h1', fontName=SERIF, fontSize=26,
                          textColor=INK, alignment=TA_CENTER, leading=32,
                          spaceAfter=6),
    'h1_left': ParagraphStyle('h1_left', fontName=SERIF, fontSize=24,
                               textColor=INK, alignment=TA_LEFT, leading=30,
                               spaceAfter=6),
    'h2': ParagraphStyle('h2', fontName=BOLD, fontSize=15,
                          textColor=INK, alignment=TA_LEFT, leading=20,
                          spaceBefore=6, spaceAfter=8),
    'kicker': ParagraphStyle('kicker', fontName=ITAL, fontSize=12.5,
                              textColor=MUTED, alignment=TA_CENTER, leading=18,
                              spaceAfter=10),
    # Corps
    'body': ParagraphStyle('body', fontName=SERIF, fontSize=10.5,
                            textColor=INK, alignment=TA_JUSTIFY, leading=16,
                            spaceAfter=8),
    'body_lead': ParagraphStyle('body_lead', fontName=SERIF, fontSize=11.5,
                                 textColor=INK, alignment=TA_JUSTIFY, leading=18,
                                 spaceAfter=10),
    # Sommaire
    'toc_num': ParagraphStyle('toc_num', fontName=CAPS, fontSize=7.5,
                               textColor=BRONZE, alignment=TA_LEFT),
    'toc_title': ParagraphStyle('toc_title', fontName=SERIF, fontSize=11.5,
                                 textColor=INK, alignment=TA_LEFT, leading=18),
    'toc_page': ParagraphStyle('toc_page', fontName=CAPS, fontSize=8,
                                textColor=MUTED, alignment=TA_RIGHT),
    # Métas ciel
    'natal_label': ParagraphStyle('natal_label', fontName=CAPS, fontSize=7.5,
                                    textColor=BRONZE, alignment=TA_CENTER,
                                    spaceAfter=2),
    'natal_val': ParagraphStyle('natal_val', fontName=SERIF, fontSize=11,
                                 textColor=INK, alignment=TA_CENTER,
                                 spaceAfter=6),
    # Encarts
    'encart_label': ParagraphStyle('encart_label', fontName=CAPS, fontSize=8,
                                     textColor=BRONZE, alignment=TA_LEFT,
                                     spaceAfter=4),
    'encart_body': ParagraphStyle('encart_body', fontName=ITAL, fontSize=11,
                                    textColor=INK, alignment=TA_LEFT, leading=17,
                                    leftIndent=0, spaceAfter=0),
    # Respiration
    'breath_line': ParagraphStyle('breath_line', fontName=ITAL, fontSize=15,
                                    textColor=INK, alignment=TA_CENTER,
                                    leading=24, leftIndent=10 * mm, rightIndent=10 * mm),
    # Signature marque
    'brand_sig': ParagraphStyle('brand_sig', fontName=CAPS_BOLD, fontSize=12,
                                 textColor=INK, alignment=TA_CENTER, leading=16,
                                 spaceAfter=6),
    'brand_sig_sub': ParagraphStyle('brand_sig_sub', fontName=ITAL, fontSize=10,
                                     textColor=MUTED, alignment=TA_CENTER, leading=16),
    'legal': ParagraphStyle('legal', fontName=CAPS, fontSize=6.5,
                             textColor=MUTED, alignment=TA_CENTER, leading=10),
}

LIB = _BACKEND / 'assets' / 'library'
COVERS = _BACKEND / 'assets' / 'pdf_covers'

def img(path: Path, w_mm: float, h_mm: float):
    if path.exists():
        return RLImage(str(path), width=w_mm * mm, height=h_mm * mm, mask='auto')
    return Spacer(1, h_mm * mm)


# ═══════════════════════════════════════════════════════════════
# BOOK DOCUMENT
# ═══════════════════════════════════════════════════════════════
class BookDocument(BaseDocTemplate):
    def __init__(self, path, **kwargs):
        super().__init__(path, pagesize=(PAGE_W, PAGE_H), pageCompression=1, **kwargs)
        # 5 templates : cover · garde · white_right · white_left · white_no_folio
        frame_cover = Frame(0, 0, PAGE_W, PAGE_H,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                            id='cover_frame')
        frame_right = Frame(INNER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                            id='right_frame')
        frame_left = Frame(OUTER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                           id='left_frame')
        self.addPageTemplates([
            PageTemplate(id='cover',    frames=[frame_cover], onPage=bg_cover),
            PageTemplate(id='garde',    frames=[frame_cover], onPage=bg_garde),
            PageTemplate(id='right',    frames=[frame_right], onPage=bg_white_right),
            PageTemplate(id='left',     frames=[frame_left],  onPage=bg_white_left),
            PageTemplate(id='right_nf', frames=[frame_right], onPage=bg_white_right_no_folio),
        ])


# ═══════════════════════════════════════════════════════════════
# PAGES DU PROTOTYPE
# ═══════════════════════════════════════════════════════════════
def p1_cover(story):
    """Couverture avec image de référence en fond + typographie propre.

    L'image masquée a gardé le cadran astral + starfield intacts, et voilé
    les zones supérieure/inférieure — c'est là qu'on pose le texte propre.
    """
    # Bloc typographique HAUT (nom + tagline) sur les 33% supérieurs de la page
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph('L E&nbsp;&nbsp;L I V R E&nbsp;&nbsp;A S T R A L&nbsp;&nbsp;D E', S['cover_top']))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Alexandra', S['cover_name']))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(
        'Une exploration personnelle<br/>de votre ciel de naissance',
        S['cover_sub']))
    # Le cadran astral est dans l'image de fond — pas d'image à insérer
    # Espace pour laisser voir le cadran
    story.append(Spacer(1, 108 * mm))
    # Bloc typographique BAS (marque)
    story.append(Paragraph(spaced('PLUME ASTRALE'), S['cover_brand']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        'Création éditoriale personnalisée<br/>à partir de votre ciel de naissance',
        S['cover_brand_sub']))


def p2_garde(story):
    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph('— ' + spaced('PLUME ASTRALE') + ' —', S['garde_top']))
    story.append(Spacer(1, 14 * mm))
    story.append(Paragraph('Alexandra', S['garde_name']))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#C9A97A" size="16">{Z_TAURUS}   {G_SUN}   {Z_SAG}</font>',
        ParagraphStyle('garde_orn', fontName=ORN, fontSize=16,
                       textColor=BRONZE_LIGHT, alignment=TA_CENTER, leading=22)))


def p3_titre(story):
    """Page titre blanche — très épurée."""
    story.append(Spacer(1, 45 * mm))
    story.append(Paragraph(spaced('PLUME ASTRALE'), S['title_brand']))
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph('Le Livre Astral', S['title_h1']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('d\'Alexandra', S['title_name']))
    story.append(Spacer(1, 14 * mm))
    story.append(Paragraph(
        '<i>Une exploration personnelle de votre ciel de naissance.</i>',
        S['title_sub']))


def p4_sommaire(story):
    """Sommaire — blanc, filets fins, entrées aérées."""
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(spaced('SOMMAIRE'), S['section_cap']))
    story.append(Spacer(1, 8 * mm))
    entries = [
        ('I',    'Votre ciel de naissance',                  '9'),
        ('II',   'Les grandes lignes de votre personnalité', '17'),
        ('III',  'Vos planètes personnelles',                '29'),
        ('IV',   'Votre façon d\'aimer',                     '45'),
        ('V',    'Vos relations',                            '59'),
        ('VI',   'Vos forces naturelles',                    '71'),
        ('VII',  'Vos défis',                                '83'),
        ('VIII', 'Votre potentiel professionnel',            '95'),
        ('IX',   'Vos grandes dynamiques de vie',           '107'),
        ('X',    'Vos cycles',                              '117'),
        ('XI',   'Votre chemin personnel',                  '129'),
        ('XII',  'Synthèse de votre portrait astral',       '141'),
    ]
    for num, title, page in entries:
        t = Table([[
            Paragraph(num, S['toc_num']),
            Paragraph(title, S['toc_title']),
            Paragraph(page, S['toc_page']),
        ]], colWidths=[13 * mm, 78 * mm, 12 * mm], hAlign='LEFT')
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, -1), 0.2, HexColor('#E3DDCF')),
        ]))
        story.append(t)


def p5_ciel_naissance(story):
    """Page pivot du livre : la véritable carte du ciel personnalisée."""
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(spaced('CHAPITRE I'), S['section_cap']))
    story.append(Paragraph('Votre ciel de naissance', S['h1']))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="10">— · —</font>',
        ParagraphStyle('h_rule', fontName=ORN, fontSize=10,
                       textColor=BRONZE, alignment=TA_CENTER)))
    story.append(Spacer(1, 6 * mm))
    # Carte du ciel — pièce maîtresse (plus compacte)
    story.append(img(COVERS / 'natal_hero.png', 62, 62))
    story.append(Spacer(1, 6 * mm))
    # Bloc infos naissance
    meta_table = Table([
        [Paragraph('ALEXANDRA', ParagraphStyle('nm', fontName=CAPS_BOLD, fontSize=10,
                                                 textColor=INK, alignment=TA_CENTER))],
        [Paragraph('15 mai 1990  ·  6 h 42  ·  Marseille, France',
                   ParagraphStyle('nm2', fontName=SERIF, fontSize=10, textColor=MUTED,
                                   alignment=TA_CENTER, spaceBefore=3))],
    ], colWidths=[110 * mm], hAlign='CENTER')
    story.append(meta_table)
    story.append(Spacer(1, 4 * mm))
    # 3 planètes clés — plus resserré
    trio = Table([[
        Paragraph(f'{orn(G_SUN, 14, BRONZE)}<br/><font name="{CAPS}" size="7" color="#B8935A">SOLEIL</font><br/>'
                  f'<font name="{SERIF}" size="10" color="#1C1B26">Taureau {orn(Z_TAURUS, 10, INK)}</font><br/>'
                  f'<font name="{CAPS}" size="7" color="#7A7488">{deg("24° 12′")}</font>',
                  ParagraphStyle('trio', fontName=SERIF, fontSize=10, alignment=TA_CENTER, leading=13)),
        Paragraph(f'{orn(G_MOON, 14, BRONZE)}<br/><font name="{CAPS}" size="7" color="#B8935A">LUNE</font><br/>'
                  f'<font name="{SERIF}" size="10" color="#1C1B26">Sagittaire {orn(Z_SAG, 10, INK)}</font><br/>'
                  f'<font name="{CAPS}" size="7" color="#7A7488">{deg("8° 03′")}</font>',
                  ParagraphStyle('trio', fontName=SERIF, fontSize=10, alignment=TA_CENTER, leading=13)),
        Paragraph(f'<font name="{CAPS_BOLD}" size="12" color="#B8935A">AC</font><br/><font name="{CAPS}" size="7" color="#B8935A">ASCENDANT</font><br/>'
                  f'<font name="{SERIF}" size="10" color="#1C1B26">Gémeaux {orn(Z_GEMINI, 10, INK)}</font><br/>'
                  f'<font name="{CAPS}" size="7" color="#7A7488">{deg("3° 47′")}</font>',
                  ParagraphStyle('trio', fontName=SERIF, fontSize=10, alignment=TA_CENTER, leading=13)),
    ]], colWidths=[36 * mm, 36 * mm, 36 * mm], hAlign='CENTER')
    story.append(trio)


def p6_ouverture_ch4(story):
    """Ouverture chapitre IV — Votre façon d'aimer.

    Ouverture pleine page très aérée : symbole, tag, titre, sous-titre, puis BLANC.
    """
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="14">{G_VENUS}</font>',
        ParagraphStyle('orn_venus', fontName=ORN, fontSize=14,
                       textColor=BRONZE, alignment=TA_CENTER, leading=20)))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(spaced('CHAPITRE IV'), S['section_cap']))
    story.append(Paragraph('Votre façon d\'aimer', S['h1']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        '<i>Ce que Vénus révèle de votre manière d\'aimer,<br/>de recevoir et de vous attacher.</i>',
        S['kicker']))
    # Beaucoup de blanc volontaire en dessous — pas d'autre contenu


def p7_texte_standard(story):
    """Page texte standard — narration avec capitale ornée."""
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('Le langage secret de votre Vénus', S['h2']))
    paras = [
        (
            f'<font name="{BOLD}" color="#B8935A" size="30">V</font>ous n\'aimez pas comme la plupart des gens de votre âge. '
            f'Là où beaucoup cherchent la certitude, vous êtes attirée par ce qui vibre — '
            f'par ce qui pourrait ne pas rester. Votre Vénus est en Poissons, rétrograde ({deg("11° 08′")}), '
            f'et c\'est cette particularité — que seuls quelques thèmes de votre génération portent — '
            f'qui donne à votre rapport amoureux son grain si singulier.'
        ),
        (
            "Rétrograde ne veut pas dire défaillante. Cela signifie que Vénus, chez vous, a "
            "appris à faire un pas en arrière avant de tendre la main. Vous rencontrez quelqu\'un, "
            "et il y a un temps de silence intérieur — quelques semaines, parfois plus — avant "
            "que quelque chose s\'ouvre. Ceux qui vous aiment finissent par apprendre à "
            "respecter cette lenteur. C\'est votre manière de rester fidèle à vous-même."
        ),
        (
            "En Poissons, Vénus dissout les frontières. Vous confondez parfois <i>aimer</i> et "
            "<i>ressentir avec</i>. La peine de l\'autre devient la vôtre en quelques secondes. "
            "Cela fait de vous une amie très aimée — et une compagne pour qui certains soirs "
            "ne se referment pas facilement."
        ),
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def p8_planete_venus(story):
    """Page dédiée à une planète — Vénus, structure éditoriale."""
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="26">{G_VENUS}</font>',
        ParagraphStyle('venus_glyph', fontName=ORN, fontSize=26,
                       textColor=BRONZE, alignment=TA_CENTER, leading=32)))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(spaced('VOTRE VÉNUS'), S['section_cap']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f'<font name="{CAPS}" size="8" color="#7A7488">POISSONS {orn(Z_PISCES, 8, MUTED)}  ·  MAISON X  ·  {deg("11° 08′")}  ·  RÉTROGRADE</font>',
        ParagraphStyle('venus_meta', fontName=CAPS, fontSize=8, textColor=MUTED,
                       alignment=TA_CENTER, spaceAfter=10)))
    story.append(Spacer(1, 8 * mm))
    paras = [
        (
            "Vénus en Poissons, en Maison X. Ce placement — rare dans votre génération — "
            "installe l\'amour au sommet de la carte : très haut, très visible, très exposé. "
            "Ce que vous aimez, les autres finissent par le voir. Vos affections deviennent, "
            "à leur manière, une déclaration publique — même si vous ne dites jamais rien."
        ),
        (
            "La Maison X est celle de la vocation. Chez d\'autres, on y trouverait Saturne "
            "et l\'ambition. Chez vous, il y a Vénus — et c\'est <i>cela</i> qui pilote votre "
            "orientation professionnelle. Vous ne choisirez jamais un métier qui ne vous "
            "permet pas d\'aimer ce que vous faites. Vous en avez déjà fait l\'expérience."
        ),
    ]
    for p in paras:
        story.append(Paragraph(p, S['body']))


def p9_encart_force_defi(story):
    """Page avec 2 encarts éditoriaux (Votre Force / Votre Défi)."""
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Ce que ce placement dessine en vous', S['h2']))
    story.append(Spacer(1, 4 * mm))

    def _encart(label: str, text: str):
        """Encart éditorial : filet fin doré + label + texte italique."""
        cell = Table([
            [Paragraph(label, S['encart_label'])],
            [Paragraph(text, S['encart_body'])],
        ], colWidths=[PAGE_W - INNER - OUTER - 8 * mm], hAlign='LEFT')
        cell.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.4, BRONZE),
            ('LINEBELOW', (0, -1), (-1, -1), 0.4, BRONZE),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        return cell

    story.append(_encart(
        'VOTRE FORCE',
        "Vous sentez ce que les autres ressentent avant qu\'ils ne l\'aient formulé. "
        "Dans un couple, dans une équipe, dans une famille — vous êtes celle qui perçoit "
        "le glissement d\'humeur, et qui, souvent en silence, accueille."
    ))
    story.append(Spacer(1, 10 * mm))
    story.append(_encart(
        'VOTRE DÉFI',
        "Apprendre à laisser aux autres leurs propres émotions. Vous absorbez trop, trop tôt. "
        "Votre travail intérieur, ces prochaines années, sera de tracer une petite frontière — "
        "poreuse, mais réelle — entre vous et ce que porte l\'autre."
    ))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "Nous reviendrons sur ce point dans le chapitre <b>VII</b>. Pour l\'instant, gardez "
        "simplement cette phrase : <i>ce que vous ressentez ne vous appartient pas toujours</i>.",
        S['body']))


def p10_respiration(story):
    """Page de respiration — minimaliste, une phrase, beaucoup de blanc."""
    story.append(Spacer(1, 68 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="13">— · —</font>',
        ParagraphStyle('breath_orn', fontName=ORN, fontSize=13,
                       textColor=BRONZE, alignment=TA_CENTER)))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        '<i>Certaines parts de nous ne demandent pas à être changées.<br/>'
        'Seulement à être comprises.</i>',
        S['breath_line']))


def p11_double_page_premium(story):
    """Double page premium — grande citation littéraire pleine page.

    Sur une double page, cette page (verso) se lit AVEC la page suivante (recto).
    Ici c\'est l\'auteur du livre qui parle de la lecture qui va suivre.
    """
    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="10">— · —</font>',
        ParagraphStyle('quote_orn', fontName=ORN, fontSize=10,
                       textColor=BRONZE, alignment=TA_CENTER)))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        '« Les étoiles ne décident rien.<br/><br/>'
        'Elles inclinent, elles éclairent,<br/>'
        'elles se souviennent — mais ne commandent<br/>pas. »',
        ParagraphStyle('quote', fontName=ITAL, fontSize=16,
                       textColor=INK, alignment=TA_CENTER, leading=26,
                       leftIndent=6 * mm, rightIndent=6 * mm)))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        f'<font name="{CAPS}" size="8" color="#7A7488">PTOLÉMÉE   ·   TÉTRABIBLE   ·   II<sup>e</sup> SIÈCLE</font>',
        ParagraphStyle('quote_src', fontName=CAPS, fontSize=8,
                       textColor=MUTED, alignment=TA_CENTER)))


def p12_derniere_page(story):
    """Dernière page — signature de marque, très épurée."""
    story.append(Spacer(1, 62 * mm))
    story.append(Paragraph(
        f'<font name="{ORN}" color="#B8935A" size="16">{Z_TAURUS}   {G_SUN}   {Z_SAG}</font>',
        ParagraphStyle('last_orn', fontName=ORN, fontSize=16,
                       textColor=BRONZE, alignment=TA_CENTER, leading=22)))
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph(spaced('PLUME ASTRALE'), S['brand_sig']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        '<i>Une création éditoriale personnelle,<br/>inspirée de votre ciel de naissance.</i>',
        S['brand_sig_sub']))
    story.append(Spacer(1, 42 * mm))
    story.append(Paragraph(spaced('CONCEPTION & ÉDITION — PLUME ASTRALE', gap=1), S['legal']))
    story.append(Paragraph('plume-astrale.fr  ·  contact@plume-astrale.fr', S['legal']))


# ═══════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════
def build(out_path: str) -> None:
    doc = BookDocument(out_path,
                       title='Plume Astrale — Prototype Livre Astral',
                       author='Plume Astrale',
                       subject='Prototype v3 · A5 · 12 pages · direction blanche')
    story: list = []
    pages = [
        (p1_cover,               'cover'),
        (p2_garde,               'garde'),
        (p3_titre,               'right_nf'),  # page titre sans folio
        (p4_sommaire,            'left'),
        (p5_ciel_naissance,      'right'),
        (p6_ouverture_ch4,       'left'),
        (p7_texte_standard,      'right'),
        (p8_planete_venus,       'left'),
        (p9_encart_force_defi,   'right'),
        (p10_respiration,        'left'),
        (p11_double_page_premium,'right'),
        (p12_derniere_page,      'right_nf'),  # dernière page sans folio
    ]
    for i, (fn, tmpl) in enumerate(pages):
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
    out = out_dir / 'prototype_book_a5.pdf'
    build(str(out))
    print(f'✓ Prototype généré : {out} ({out.stat().st_size // 1024} Ko)')
    print(f'  Format A5 : 148 × 210 mm · 12 pages')
    print(f'  Direction blanche · signature PLUME ASTRALE')
