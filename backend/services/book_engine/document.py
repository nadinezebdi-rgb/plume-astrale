"""BookDocument — ReportLab renderer A5 recto/verso pour Plume Astrale.

Sortie : PDF numérique fac-similé du livre imprimé.
Extraction propre du prototype `scripts/prototype_book_a5.py` — mêmes
palettes, mêmes styles, même plume dorée.

Le renderer prend un `Manuscript` (dataclass typée) et produit un PDF.
Il ne parle jamais à Stripe, à Supabase, ni à Lulu — c'est un composant pur.

Pipeline d'un chapitre :
  1. Story vide + NextPageTemplate('right') si `roman_num` set (chapitre)
  2. Chaque `ChapterBlock` est dispatché vers son renderer selon `kind`
  3. `doc.build(story)` produit le PDF

L'appelant peut ensuite passer le PDF au PrintProvider pour appliquer
BleedBox + TrimBox et générer la cover imprimée.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import math

from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, PageBreak, Image as RLImage,
    Table, TableStyle, NextPageTemplate, Flowable,
)

from services.pdf_theme import register_fonts, font
from .domain import Manuscript, Chapter, ChapterBlock, BlockKind

register_fonts()

# ═══════════════════════════════════════════════════════════════
# Palette Plume Astrale v1 (extrait du prototype validé)
# ═══════════════════════════════════════════════════════════════
IVORY = HexColor('#FBF7EE')
INK = HexColor('#1C1B26')
NIGHT = HexColor('#0F1A3C')
BRONZE = HexColor('#B8935A')
BRONZE_LIGHT = HexColor('#C9A97A')
GOLD_VIVID = HexColor('#D4AF37')
CREAM = HexColor('#F5EEE0')
MUTED = HexColor('#7A7488')

# ═══════════════════════════════════════════════════════════════
# Format A5 + marges miroir
# ═══════════════════════════════════════════════════════════════
PAGE_W = 148 * mm
PAGE_H = 210 * mm
INNER = 20 * mm
OUTER = 16 * mm
TOP = 22 * mm
BOTTOM = 22 * mm

# ═══════════════════════════════════════════════════════════════
# Polices
# ═══════════════════════════════════════════════════════════════
SERIF = font('Cormorant', 'Helvetica')
ITAL = font('Cormorant-Italic', 'Helvetica-Oblique')
BOLD = font('Cormorant-Bold', 'Helvetica-Bold')
CAPS = font('Cinzel', 'Helvetica')
CAPS_BOLD = font('Cinzel-Bold', 'Helvetica-Bold')
SCRIPT = font('Allura', font('Cormorant-Italic', 'Helvetica-Oblique'))
ORN = 'OrnamentSerif'

NBSP = '\u00A0'
def spaced(text: str, gap: int = 2) -> str:
    out = []
    for ch in text:
        if ch == ' ':
            out.append(NBSP * (gap + 2))
        else:
            out.append(ch)
    return (NBSP * gap).join(out)


# ═══════════════════════════════════════════════════════════════
# Plume dorée
# ═══════════════════════════════════════════════════════════════
def _draw_feather(canv, cx: float, cy: float, height: float,
                  color=BRONZE, angle_deg: float = -8):
    h = height
    w = height * 0.28
    canv.saveState()
    canv.translate(cx, cy - h / 2)
    if angle_deg:
        canv.rotate(angle_deg)
    canv.setStrokeColor(color)
    canv.setFillColor(color)
    path = canv.beginPath()
    path.moveTo(0, 0)
    path.curveTo(w * 0.10, h * 0.35, -w * 0.06, h * 0.75, 0, h)
    canv.setLineWidth(0.7)
    canv.drawPath(path, stroke=1, fill=0)
    canv.setLineWidth(0.35)
    for i in range(1, 20):
        t = i / 20
        y = h * t
        barb_len = w * 1.15 * (1 - (2 * abs(t - 0.5)) ** 1.6)
        if barb_len < 0.3:
            continue
        rachis_x = w * 0.10 * math.sin(t * math.pi)
        theta = math.radians(40 + (t - 0.5) * 20)
        ax = barb_len * math.cos(theta)
        ay = barb_len * math.sin(theta)
        canv.line(rachis_x, y, rachis_x - ax, y + ay * 0.6)
        canv.line(rachis_x, y, rachis_x + ax * 0.85, y + ay * 0.55)
    canv.setFillColor(color)
    canv.circle(0, h, 0.5, fill=1, stroke=0)
    canv.setLineWidth(1.0)
    canv.line(0, 0, w * 0.05, -h * 0.05)
    canv.restoreState()


class Feather(Flowable):
    def __init__(self, height=18 * mm, color=BRONZE, angle_deg: float = -8):
        super().__init__()
        self.height = height
        self.width = height * 0.7
        self.color = color
        self.angle_deg = angle_deg

    def wrap(self, availW, availH):
        return self.width, self.height

    def draw(self):
        _draw_feather(self.canv, self.width / 2, self.height / 2,
                      self.height, self.color, self.angle_deg)


# ═══════════════════════════════════════════════════════════════
# Fonds de page
# ═══════════════════════════════════════════════════════════════
def _bg_white(canv, doc, is_right: bool, show_folio: bool = True, running_title: str = ''):
    canv.saveState()
    canv.setFillColor(IVORY)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    if show_folio:
        canv.setFillColor(MUTED)
        canv.setFont(CAPS, 7)
        num = str(doc.page)
        if is_right:
            canv.drawRightString(PAGE_W - OUTER, 12 * mm, num)
        else:
            canv.drawString(OUTER, 12 * mm, num)
        if running_title:
            canv.setFont(CAPS, 6.5)
            canv.setFillColor(HexColor('#A19986'))
            canv.drawCentredString(PAGE_W / 2, 12 * mm, running_title)
    canv.restoreState()


# ═══════════════════════════════════════════════════════════════
# Styles
# ═══════════════════════════════════════════════════════════════
def _styles():
    return {
        'section_cap': ParagraphStyle('section_cap', fontName=CAPS, fontSize=8,
                                       textColor=BRONZE, alignment=TA_CENTER, spaceAfter=10),
        'h1': ParagraphStyle('h1', fontName=SERIF, fontSize=26,
                              textColor=INK, alignment=TA_CENTER, leading=32, spaceAfter=6),
        'h2': ParagraphStyle('h2', fontName=BOLD, fontSize=15,
                              textColor=INK, alignment=TA_LEFT, leading=20,
                              spaceBefore=6, spaceAfter=10),
        'kicker_script': ParagraphStyle('kicker_script', fontName=SCRIPT, fontSize=22,
                                         textColor=BRONZE, alignment=TA_CENTER, leading=28,
                                         spaceAfter=10),
        'kicker_italic': ParagraphStyle('kicker_italic', fontName=ITAL, fontSize=12.5,
                                         textColor=MUTED, alignment=TA_CENTER, leading=18,
                                         spaceAfter=10),
        'body': ParagraphStyle('body', fontName=SERIF, fontSize=10.5,
                                textColor=INK, alignment=TA_JUSTIFY, leading=16,
                                spaceBefore=4, spaceAfter=10),
        'body_dropcap': ParagraphStyle('body_dropcap', fontName=SERIF, fontSize=10.5,
                                        textColor=INK, alignment=TA_JUSTIFY, leading=18,
                                        spaceBefore=4, spaceAfter=14),
        'natal_meta': ParagraphStyle('natal_meta', fontName=CAPS, fontSize=8,
                                      textColor=MUTED, alignment=TA_CENTER, spaceAfter=10),
        'encart_label': ParagraphStyle('encart_label', fontName=CAPS, fontSize=8,
                                        textColor=BRONZE, alignment=TA_LEFT, spaceAfter=4),
        'encart_body': ParagraphStyle('encart_body', fontName=ITAL, fontSize=11,
                                       textColor=INK, alignment=TA_LEFT, leading=17),
        'quote': ParagraphStyle('quote', fontName=ITAL, fontSize=14,
                                 textColor=INK, alignment=TA_CENTER, leading=22,
                                 leftIndent=6 * mm, rightIndent=6 * mm),
        'dedication_script': ParagraphStyle('dedication_script', fontName=SCRIPT, fontSize=24,
                                             textColor=BRONZE, alignment=TA_CENTER, leading=32,
                                             spaceAfter=8),
    }


# ═══════════════════════════════════════════════════════════════
# BookDocument — le document ReportLab A5 recto/verso
# ═══════════════════════════════════════════════════════════════
class BookDocument(BaseDocTemplate):
    def __init__(self, buf, running_title: str = '', **kwargs):
        super().__init__(buf, pagesize=(PAGE_W, PAGE_H), pageCompression=1, **kwargs)
        self._running_title = running_title
        frame_right = Frame(INNER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                            id='right_frame')
        frame_left = Frame(OUTER, BOTTOM, PAGE_W - INNER - OUTER, PAGE_H - TOP - BOTTOM,
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
                           id='left_frame')
        self.addPageTemplates([
            PageTemplate(id='right', frames=[frame_right],
                         onPage=lambda c, d: _bg_white(c, d, True, True, self._running_title)),
            PageTemplate(id='left', frames=[frame_left],
                         onPage=lambda c, d: _bg_white(c, d, False, True, self._running_title)),
            PageTemplate(id='right_nf', frames=[frame_right],
                         onPage=lambda c, d: _bg_white(c, d, True, False, '')),
            PageTemplate(id='left_nf', frames=[frame_left],
                         onPage=lambda c, d: _bg_white(c, d, False, False, '')),
        ])


# ═══════════════════════════════════════════════════════════════
# Block dispatch → renderers ReportLab
# ═══════════════════════════════════════════════════════════════
def _render_block(block: ChapterBlock, story: list, S: dict):
    """Dispatch un ChapterBlock vers son flowable ReportLab."""
    d = block.data
    kind = block.kind

    if kind == BlockKind.CHAPTER_OPENING:
        story.append(Spacer(1, 38 * mm))
        story.append(Feather(height=18 * mm))
        story.append(Spacer(1, 10 * mm))
        if d.get('roman_num'):
            story.append(Paragraph(spaced(f"CHAPITRE {d['roman_num']}"), S['section_cap']))
        story.append(Paragraph(d.get('title', ''), S['h1']))
        if d.get('kicker'):
            story.append(Spacer(1, 4 * mm))
            story.append(Paragraph(d['kicker'], S['kicker_script']))
        story.append(Spacer(1, 32 * mm))
        story.append(Feather(height=12 * mm, color=BRONZE_LIGHT))

    elif kind == BlockKind.H2:
        story.append(Paragraph(d.get('text', ''), S['h2']))

    elif kind == BlockKind.PARAGRAPH:
        story.append(Paragraph(d.get('text', ''), S['body']))

    elif kind == BlockKind.PARAGRAPH_DROPCAP:
        text = d.get('text', '').strip()
        if text:
            first_letter, rest = text[0], text[1:]
            html = (f'<font name="{BOLD}" color="#B8935A" size="22">{first_letter}</font>'
                    f'{rest}')
            story.append(Paragraph(html, S['body_dropcap']))

    elif kind == BlockKind.KICKER_SCRIPT:
        story.append(Paragraph(d.get('text', ''), S['kicker_script']))

    elif kind == BlockKind.NATAL_META:
        parts = [d.get('sign', ''), d.get('house', ''), d.get('degree', '')]
        if d.get('note'):
            parts.append(d['note'])
        parts = [p for p in parts if p]
        line = '  ·  '.join(parts)
        story.append(Paragraph(
            f'<font name="{CAPS}" size="8" color="#7A7488">{line}</font>',
            S['natal_meta']))

    elif kind == BlockKind.ENCART:
        cell = Table([
            [Paragraph(d.get('label', ''), S['encart_label'])],
            [Paragraph(d.get('text', ''), S['encart_body'])],
        ], colWidths=[PAGE_W - INNER - OUTER - 8 * mm], hAlign='LEFT')
        cell.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 0.4, BRONZE),
            ('LINEBELOW', (0, -1), (-1, -1), 0.4, BRONZE),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(cell)
        story.append(Spacer(1, 10 * mm))

    elif kind == BlockKind.QUOTE_LITERARY:
        story.append(Paragraph(d.get('text', ''), S['quote']))
        if d.get('source'):
            story.append(Spacer(1, 6 * mm))
            story.append(Paragraph(
                f'<font name="{CAPS}" size="7.5" color="#7A7488">{d["source"]}</font>',
                ParagraphStyle('qsrc', fontName=CAPS, fontSize=7.5,
                                textColor=MUTED, alignment=TA_CENTER)))

    elif kind == BlockKind.QUOTE_BREATH:
        story.append(Spacer(1, 26 * mm))
        story.append(Paragraph(d.get('text', ''), S['quote']))

    elif kind == BlockKind.DEDICATION_SCRIPT:
        story.append(Paragraph(d.get('text', ''), S['dedication_script']))

    elif kind == BlockKind.FEATHER:
        story.append(Feather(height=d.get('height_mm', 14) * mm))

    elif kind == BlockKind.HAIRLINE:
        story.append(Paragraph(
            f'<font name="{ORN}" color="#B8935A" size="10">— · —</font>',
            ParagraphStyle('hr', fontName=ORN, fontSize=10,
                            textColor=BRONZE, alignment=TA_CENTER)))

    elif kind == BlockKind.PAGE_BREAK:
        story.append(PageBreak())

    elif kind == BlockKind.IMAGE:
        slug = d.get('slug')
        w_mm = d.get('width_mm', 78)
        h_mm = d.get('height_mm', 78)
        # Slug est un chemin relatif à backend/assets ; caller fournit le path complet dans 'path'
        p = d.get('path')
        if p and Path(p).exists():
            story.append(RLImage(p, width=w_mm * mm, height=h_mm * mm, mask='auto'))


# ═══════════════════════════════════════════════════════════════
# API publique
# ═══════════════════════════════════════════════════════════════
def render_manuscript_to_pdf(manuscript: Manuscript) -> bytes:
    """Rend un `Manuscript` en PDF bytes A5 numérique.

    Chaque chapitre commence sur une page droite. Le folio et le titre
    courant sont automatiquement gérés selon `running_title`.
    """
    buf = BytesIO()
    running = f"LE LIVRE ASTRAL D{NBSP}{NBSP}{manuscript.first_name.upper()}"
    doc = BookDocument(buf, running_title=running,
                       title=f"Livre Astral — {manuscript.first_name}",
                       author='Plume Astrale')
    S = _styles()
    story: list = []
    for i, chap in enumerate(manuscript.chapters):
        # Chaque chapitre commence sur page droite (recto)
        if i == 0:
            story.append(NextPageTemplate('right'))
        else:
            story.append(NextPageTemplate('right'))
            story.append(PageBreak())
        for block in chap.blocks:
            _render_block(block, story, S)
    doc.build(story)
    return buf.getvalue()
