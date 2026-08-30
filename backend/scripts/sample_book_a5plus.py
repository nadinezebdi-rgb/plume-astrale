"""
sample_book_a5plus.py — Sample de 8 pages pour valider l'architecture du
Plume Astrale Book Rendering Engine avant coding complet.

Format : A5+ (156 × 234 mm) — dit "royal octavo", format roman haut de gamme.

Démonstration :
  - Pages recto/verso avec MARGES MIROIR (gouttière intérieure vs bord extérieur)
  - Pagination sur le bord extérieur (droite en page droite, gauche en page gauche)
  - Ouverture de chapitre TOUJOURS sur page de droite (impaire)
  - Cover · Page de garde · Page titre · Colophon · TOC · Épigraphe ·
    Ouverture chapitre · Corps chapitre

Usage :
    cd /app/backend && python scripts/sample_book_a5plus.py
    → /app/frontend/public/sample_book_a5plus.pdf
"""
from __future__ import annotations
import io
import os
import sys
from pathlib import Path

# Bootstrap path pour importer services.*
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
# FORMAT A5+ (roman) & MARGES
# ═══════════════════════════════════════════════════════════════
PAGE_W = 156 * mm
PAGE_H = 234 * mm

# Marges miroir — gouttière intérieure plus large que le bord extérieur
INNER = 18 * mm  # côté reliure
OUTER = 14 * mm  # bord tranche
TOP = 20 * mm
BOTTOM = 20 * mm

# ═══════════════════════════════════════════════════════════════
# FOND DE PAGE (identique recto/verso mais pagination position mirroir)
# ═══════════════════════════════════════════════════════════════
def _bg_common(canv, doc, is_right: bool):
    """Fond nuit + starfield + ornements + pagination bord extérieur.

    is_right=True  → page droite (impaire), pagination bord droit
    is_right=False → page gauche (paire), pagination bord gauche
    """
    import random
    canv.saveState()

    # Fond nuit
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Halo doré subtil coin extérieur
    for i, alpha in enumerate([0.03, 0.02, 0.012]):
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
        cx = (PAGE_W - 1 * cm) if is_right else (1 * cm)
        canv.circle(cx, PAGE_H, (i + 1) * 5 * cm, fill=1, stroke=0)

    # Starfield 45 étoiles seed-based (stable par page)
    r = random.Random(hash(('sf', doc.page)))
    canv.setFillColor(GOLD)
    for _ in range(45):
        x = r.uniform(0.8 * cm, PAGE_W - 0.8 * cm)
        y = r.uniform(0.8 * cm, PAGE_H - 0.8 * cm)
        s = r.choice([0.35, 0.5, 0.65, 0.8, 0.4])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.18, 0.55))
        canv.circle(x, y, s, fill=1, stroke=0)
    canv.setFillAlpha(1)

    # Cadre or pointillé (marge sécurité — visible seulement sur pages de corps)
    if doc.page > 2:
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.3)
        canv.setDash([0.5, 2.2], 0)
        # Décalé selon recto/verso pour respecter la gouttière
        left = INNER if is_right else OUTER
        right = OUTER if is_right else INNER
        canv.rect(
            left - 4 * mm, BOTTOM - 4 * mm,
            PAGE_W - left - right + 8 * mm,
            PAGE_H - TOP - BOTTOM + 8 * mm,
            stroke=1, fill=0,
        )
        canv.setDash([], 0)

    # Ornement soleil discret en haut de chaque page de corps
    if doc.page > 3:
        canv.setFillColor(GOLD)
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.4)
        canv.circle(PAGE_W / 2, PAGE_H - 12 * mm, 0.9 * mm, fill=1, stroke=0)
        canv.line(PAGE_W / 2 - 10 * mm, PAGE_H - 12 * mm, PAGE_W / 2 - 2.5 * mm, PAGE_H - 12 * mm)
        canv.line(PAGE_W / 2 + 2.5 * mm, PAGE_H - 12 * mm, PAGE_W / 2 + 10 * mm, PAGE_H - 12 * mm)

    # Footer : pagination bord extérieur + chemin lecteur bord intérieur
    if doc.page > 2:
        canv.setFillColor(MUTED)
        canv.setFont(font('Cinzel', 'Helvetica'), 7)
        # Pagination : bord extérieur
        num_str = f"— {doc.page} —"
        if is_right:
            canv.drawRightString(PAGE_W - OUTER, 10 * mm, num_str)
        else:
            canv.drawString(OUTER, 10 * mm, num_str)
        # Titre courant : centré (chemin de lecture)
        canv.setFont(font('Cinzel', 'Helvetica'), 6.5)
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=0.55)
        canv.drawCentredString(PAGE_W / 2, 10 * mm, "PLUME ASTRALE · LIVRE ASTRAL D'ALEXANDRA")

    canv.restoreState()


def bg_right(canv, doc):
    _bg_common(canv, doc, is_right=True)

def bg_left(canv, doc):
    _bg_common(canv, doc, is_right=False)


# ═══════════════════════════════════════════════════════════════
# BOOK DOCUMENT — BaseDocTemplate avec 2 PageTemplate (recto/verso)
# ═══════════════════════════════════════════════════════════════
class BookDocument(BaseDocTemplate):
    """Document A5+ avec marges miroir et alternance auto recto/verso."""

    def __init__(self, path_or_buf, **kwargs):
        super().__init__(
            path_or_buf,
            pagesize=(PAGE_W, PAGE_H),
            pageCompression=1,
            **kwargs,
        )
        # Frame page droite (impaire) : marge intérieure à GAUCHE
        frame_right = Frame(
            x1=INNER, y1=BOTTOM,
            width=PAGE_W - INNER - OUTER,
            height=PAGE_H - TOP - BOTTOM,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            id='right_frame',
        )
        # Frame page gauche (paire) : marge intérieure à DROITE
        frame_left = Frame(
            x1=OUTER, y1=BOTTOM,
            width=PAGE_W - INNER - OUTER,
            height=PAGE_H - TOP - BOTTOM,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
            id='left_frame',
        )
        self.addPageTemplates([
            PageTemplate(id='right', frames=[frame_right], onPage=bg_right),
            PageTemplate(id='left',  frames=[frame_left],  onPage=bg_left),
        ])

    # Note : l'alternance recto/verso est pilotée explicitement par le caller
    # via NextPageTemplate('right'|'left') avant chaque PageBreak. On garde
    # la logique explicite plutôt qu'auto pour permettre l'insertion de
    # pages blanches (ex: chapitre qui doit s'ouvrir sur une page droite).


def start_chapter_on_right(story: list):
    """Ajoute une page blanche si nécessaire pour ouvrir sur page de droite."""
    # Marqueur : au moment de la génération, si le total de pages est pair,
    # on est actuellement sur une droite → il faut sauter la prochaine gauche.
    # Comme on ne connaît pas le n° à ce stade, on force avec un token spécial :
    # ici on triche en injectant NextPageTemplate + PageBreak. Le layout final
    # sera post-processé par pypdf si besoin.
    story.append(NextPageTemplate('right'))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════
# STYLES
# ═══════════════════════════════════════════════════════════════
BODY_FONT = font('Cormorant', 'Helvetica')
ITALIC_FONT = font('Cormorant-Italic', 'Helvetica-Oblique')
BOLD_FONT = font('Cormorant-Bold', 'Helvetica-Bold')
DISPLAY_FONT = font('Cinzel', 'Helvetica')
DISPLAY_BOLD = font('Cinzel-Bold', 'Helvetica-Bold')

S = {
    'cover_eyebrow': ParagraphStyle('cover_eyebrow', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_CENTER, spaceAfter=6),
    'cover_title':   ParagraphStyle('cover_title', fontName=BODY_FONT, fontSize=48,
                                     leading=54, textColor=CREAM, alignment=TA_CENTER),
    'cover_name':    ParagraphStyle('cover_name', fontName=DISPLAY_BOLD, fontSize=34,
                                     leading=42, textColor=GOLD_LIGHT, alignment=TA_CENTER),
    'cover_sub':     ParagraphStyle('cover_sub', fontName=ITALIC_FONT, fontSize=15,
                                     leading=22, textColor=CREAM, alignment=TA_CENTER),
    'cover_date':    ParagraphStyle('cover_date', fontName=DISPLAY_FONT, fontSize=8,
                                     textColor=MUTED, alignment=TA_CENTER, spaceBefore=8),
    'title_page':    ParagraphStyle('title_page', fontName=BODY_FONT, fontSize=36,
                                     leading=42, textColor=CREAM, alignment=TA_CENTER),
    'section_tag':   ParagraphStyle('section_tag', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_CENTER, spaceAfter=18),
    'h1':            ParagraphStyle('h1', fontName=BODY_FONT, fontSize=28,
                                     leading=34, textColor=CREAM, alignment=TA_CENTER, spaceAfter=6),
    'h2':            ParagraphStyle('h2', fontName=BOLD_FONT, fontSize=18,
                                     leading=24, textColor=GOLD_LIGHT, spaceBefore=4, spaceAfter=12),
    'body':          ParagraphStyle('body', fontName=BODY_FONT, fontSize=11.5,
                                     leading=17, textColor=CREAM, alignment=TA_JUSTIFY, spaceAfter=10),
    'dropcap_body':  ParagraphStyle('dropcap_body', fontName=BODY_FONT, fontSize=11.5,
                                     leading=17, textColor=CREAM, alignment=TA_JUSTIFY, spaceAfter=10,
                                     firstLineIndent=0),
    'italic':        ParagraphStyle('italic', fontName=ITALIC_FONT, fontSize=13,
                                     leading=20, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=14),
    'signature':     ParagraphStyle('signature', fontName=ITALIC_FONT, fontSize=14,
                                     textColor=GOLD, alignment=TA_CENTER, spaceBefore=10),
    'toc_line':      ParagraphStyle('toc_line', fontName=BODY_FONT, fontSize=12,
                                     leading=22, textColor=CREAM, alignment=TA_LEFT),
    'toc_num':       ParagraphStyle('toc_num', fontName=DISPLAY_FONT, fontSize=9,
                                     textColor=GOLD, alignment=TA_RIGHT),
    'colophon_line': ParagraphStyle('colophon_line', fontName=BODY_FONT, fontSize=10,
                                     leading=16, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4),
    'epigraph':      ParagraphStyle('epigraph', fontName=ITALIC_FONT, fontSize=15,
                                     leading=24, textColor=GOLD_LIGHT, alignment=TA_CENTER,
                                     leftIndent=8 * mm, rightIndent=8 * mm),
}

ORN = '<font name="OrnamentSerif">✦</font>'
ORN3 = '<font name="OrnamentSerif">✦ ⁘ ✦</font>'
ORN_DIAMOND = '<font name="OrnamentSerif">◆</font>'


# ═══════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════
def page1_cover(story: list):
    """Page 1 · COVER — face avant de l'édition numérique (= couverture livre)"""
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f'{ORN}  PLUME ASTRALE  {ORN}', S['cover_eyebrow']))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph('Le Livre Astral', S['cover_title']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('d\'Alexandra', S['cover_name']))
    story.append(Spacer(1, 14 * mm))

    hero_path = _BACKEND / 'assets' / 'pdf_covers' / 'natal_hero.png'
    if hero_path.exists():
        story.append(RLImage(str(hero_path), width=70 * mm, height=70 * mm, mask='auto'))

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        'Une carte du ciel personnelle,<br/>lue et racontée pour vous.',
        S['cover_sub'],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('ÉDITION DU 28 FÉVRIER 2026', S['cover_date']))


def page2_garde_blanche(story: list):
    """Page 2 · Page de garde — élément décoratif minimal (motif ornemental)"""
    story.append(Spacer(1, 80 * mm))
    story.append(Paragraph(f'<font size="20" color="#D4AF37">{ORN3}</font>',
                           ParagraphStyle('garde', fontName=DISPLAY_FONT, fontSize=20,
                                           textColor=GOLD, alignment=TA_CENTER, leading=28)))


def page3_titre(story: list):
    """Page 3 · Page titre (recto) — nom du livre + éditeur"""
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph(f'{ORN}  P L U M E  A S T R A L E  {ORN}', S['cover_eyebrow']))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('Le Livre Astral', S['title_page']))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph('d\'Alexandra', S['title_page']))
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph('Composé et signé par Soléna,', S['italic']))
    story.append(Paragraph('astrologue de Plume Astrale.', S['italic']))
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph(f'<font color="#D4AF37">{ORN_DIAMOND}</font>',
                           ParagraphStyle('divider', fontName=DISPLAY_FONT, fontSize=14,
                                           textColor=GOLD, alignment=TA_CENTER)))


def page4_colophon(story: list):
    """Page 4 · Colophon avant (verso de page titre) — dédicace + mentions"""
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph('À Alexandra,', S['italic']))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph('née le 15 mai 1990 à Marseille,', S['italic']))
    story.append(Paragraph('sous un ciel de Taureau.', S['italic']))
    story.append(Spacer(1, 55 * mm))
    story.append(Paragraph('Édition numérique · Plume Astrale · 2026', S['colophon_line']))
    story.append(Paragraph('Rédigée à partir des positions Swiss Ephemeris', S['colophon_line']))
    story.append(Paragraph('calculées le 27 février 2026 à 22 h 14.', S['colophon_line']))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph('Composée en Cormorant Garamond & Cinzel.', S['colophon_line']))
    story.append(Paragraph('Illustrations originales de la maison Plume Astrale.', S['colophon_line']))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph('Ce livre a été écrit pour une seule personne. Vous.', S['colophon_line']))


def page5_toc(story: list):
    """Page 5 · Table des matières (recto)"""
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph('TABLE DES MATIÈRES', S['section_tag']))
    story.append(Paragraph(f'<font color="#D4AF37">{ORN}</font>',
                           ParagraphStyle('divider', fontName=DISPLAY_FONT, fontSize=12,
                                           textColor=GOLD, alignment=TA_CENTER, spaceAfter=20)))

    toc_entries = [
        ('Ouverture', 'Une lettre d\'Alexandra à elle-même', '9'),
        ('Chapitre I', 'Ta carte du ciel', '15'),
        ('Chapitre II', 'Ton trio identitaire — Soleil, Lune, Ascendant', '27'),
        ('Chapitre III', 'Les planètes personnelles', '45'),
        ('Chapitre IV', 'Les planètes sociales', '69'),
        ('Chapitre V', 'Les planètes générationnelles', '87'),
        ('Chapitre VI', 'Tes maisons — les 12 territoires', '103'),
        ('Chapitre VII', 'Les aspects majeurs de ta vie', '119'),
        ('Chapitre VIII', 'L\'Arbre de Vie — chapitre choisi', '135'),
        ('Épilogue', 'Ce que tu peux garder de tout ceci', '149'),
    ]
    for tag, title, page_num in toc_entries:
        table = Table(
            [[
                Paragraph(f'<font color="#D4AF37">{tag}</font>', ParagraphStyle(
                    'toc_tag', fontName=DISPLAY_FONT, fontSize=9, textColor=GOLD)),
                Paragraph(title, S['toc_line']),
                Paragraph(page_num, S['toc_num']),
            ]],
            colWidths=[26 * mm, 78 * mm, 15 * mm],
            hAlign='LEFT',
        )
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.15, HexColor('#3A3350')),
        ]))
        story.append(table)


def page6_epigraph(story: list):
    """Page 6 · Épigraphe (verso) — citation pleine page, invite au chapitre suivant"""
    story.append(Spacer(1, 65 * mm))
    story.append(Paragraph(
        '« Les étoiles ne décident rien.<br/>'
        'Elles inclinent, elles éclairent,<br/>'
        'elles se souviennent — mais ne commandent pas. »',
        S['epigraph'],
    ))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph('— Ptolémée, <i>Tétrabible</i>, IIᵉ siècle', S['colophon_line']))


def page7_chapter_opening(story: list):
    """Page 7 · Ouverture chapitre "Ta carte du ciel" (droite/impaire)"""
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph('CHAPITRE I', S['section_tag']))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph('Ta carte du ciel', S['h1']))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(f'<font color="#D4AF37">{ORN3}</font>',
                           ParagraphStyle('divider', fontName=DISPLAY_FONT, fontSize=14,
                                           textColor=GOLD, alignment=TA_CENTER)))
    story.append(Spacer(1, 12 * mm))
    hero_path = _BACKEND / 'assets' / 'pdf_covers' / 'natal_hero.png'
    if hero_path.exists():
        story.append(RLImage(str(hero_path), width=78 * mm, height=78 * mm, mask='auto'))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        'La photographie du ciel au moment précis<br/>où vous avez pris votre première inspiration.',
        S['italic'],
    ))


def page8_chapter_body(story: list):
    """Page 8 · Premier corps du chapitre (verso)"""
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('Ce que dit votre ciel', S['h2']))

    # Utilise une "capitale ornée" via <font> inline (drop cap manuel)
    body_paras = [
        f'<font name="{DISPLAY_BOLD}" color="#D4AF37" size="32">V</font>otre thème natal '
        'a été calculé pour le <b>15 mai 1990 à 6 h 42</b>, dans le vieil hôpital de la '
        'Belle-de-Mai à Marseille. À cet instant précis, le Soleil se levait à 24° 12′ du '
        'Taureau, et l\'Ascendant montait à 3° 47′ du Gémeaux — deux données qui '
        'écrivent, dès la première minute, la double langue que vous parlerez toute votre vie.',

        'Une naissance à l\'aube n\'est jamais anodine. La tradition hellénistique '
        'l\'appelait <i>diurnal sect</i> : un enfant du jour, dont Jupiter et Saturne '
        'reçoivent une charge de dignité supplémentaire. Chez vous, cela veut dire '
        'concrètement que <b>Jupiter en Cancer, en Maison II</b>, pèse davantage que la '
        'plupart des astrologues ne le lisent — c\'est lui qui, silencieusement, protège '
        'votre rapport à la sécurité matérielle.',

        'La Lune, elle, était à 8° 03′ du Sagittaire ce matin-là, en carré serré (orbe '
        '2° 15′) avec Vénus rétrograde en Poissons. Ce carré <i>ne se résout pas</i>. '
        'Il ne s\'agit pas d\'un défaut à corriger : c\'est la ligne de faille éditoriale '
        'de votre vie affective. Vous aimerez toujours ce qui échappe, précisément parce '
        'qu\'il échappe. Et c\'est très bien ainsi.',

        'Nous allons regarder chaque planète, une à une, dans les pages qui suivent. '
        'Prenez le temps qu\'il faut. Ce livre a été écrit pour être lu lentement, '
        'reposé, puis repris — comme un ami sûr.',
    ]
    for p in body_paras:
        story.append(Paragraph(p, S['body']))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph('— Soléna', S['signature']))


# ═══════════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════════
def build_sample(out_path: str) -> None:
    doc = BookDocument(out_path,
                       title='Plume Astrale — Sample Livre Astral',
                       author='Plume Astrale',
                       subject='Sample A5+ recto/verso · 8 pages')
    story: list = []
    # Verrouille explicitement chaque page à son template (recto = right, verso = left)
    # via NextPageTemplate AVANT le PageBreak qui transitionne vers cette page.
    pages = [
        (page1_cover,           'right'),
        (page2_garde_blanche,   'left'),
        (page3_titre,           'right'),
        (page4_colophon,        'left'),
        (page5_toc,             'right'),
        (page6_epigraph,        'left'),
        (page7_chapter_opening, 'right'),  # chapitre s'ouvre TOUJOURS sur page droite
        (page8_chapter_body,    'left'),
    ]
    for i, (page_fn, tmpl_id) in enumerate(pages):
        if i == 0:
            # 1re page : force le template dès le début
            story.append(NextPageTemplate(tmpl_id))
        page_fn(story)
        if i < len(pages) - 1:
            # Force le template de la page SUIVANTE avant le break
            story.append(NextPageTemplate(pages[i + 1][1]))
            story.append(PageBreak())
    doc.build(story)


if __name__ == '__main__':
    out_dir = Path('/app/frontend/public')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'sample_book_a5plus.pdf'
    build_sample(str(out_path))
    size_kb = out_path.stat().st_size // 1024
    print(f'✓ Sample généré : {out_path} ({size_kb} Ko)')
    print(f'  Format A5+ : 156 × 234 mm')
    print(f'  8 pages recto/verso avec marges miroir')
    print(f'  → Accessible à https://<preview>/sample_book_a5plus.pdf')
