"""
pdf_luxury_theme — Building blocks pour PDFs Plume Astrale style "livre de luxe".

Design cible : Dior × Cartier × Harry Potter × Astrologie.
Fournit des flowables ReportLab de haut niveau pour composer facilement
n'importe quel rapport astro (Thème Natal, Kabbale, Karma, Astrocarto...).

Import direct depuis les générateurs de PDF spécifiques :
    from services.pdf_luxury_theme import (
        LuxuryDoc, cover_page, opening_page, teaser_page,
        planet_double_page, chapter_illustration, waouh_quote_page,
        emotional_ending, illustration_url
    )
"""
from __future__ import annotations
import io
import os
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage,
    Table, TableStyle, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from services.pdf_theme import (
    register_fonts, make_styles, font,
    GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED, NIGHT, NIGHT_SOFT, PALETTE,
)

# Hex strings pour usage inline HTML `<font color="#..">`
GOLD_HEX       = '#D4AF37'
GOLD_LIGHT_HEX = '#E8C766'
CREAM_HEX      = '#F5EEE0'
LAVENDER_HEX   = '#E3D7FF'
MUTED_HEX      = '#B8B0C8'
NIGHT_HEX      = '#0A0813'
NIGHT_SOFT_HEX = '#1a1230'


SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
_ILLUS_BASE = f'{SUPABASE_URL}/storage/v1/object/public/library/pdf' if SUPABASE_URL else ''


def illustration_url(slug: str, size: int = 1200) -> str:
    """Retourne l'URL publique d'une illustration Plume Astrale (bucket library/pdf).

    Slugs disponibles :
        amoureux, fleurs_or, astrologica_alt, roue_zodiaque, couple,
        chapitre_bleu, ciel_zodiaque, fleurs_violette, astral_fruits,
        astral_planete, astral_mandala, astral_ciel, astral_silhouette
    """
    return f'{_ILLUS_BASE}/{slug}_{size}.png'


def _dl_image(url: str) -> Optional[io.BytesIO]:
    """Télécharge une image publique et la retourne en BytesIO (ou None si erreur)."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=10) as r:
            return io.BytesIO(r.read())
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
#   FOND PLEINE PAGE (starfield doré + texture parchemin subtile)
# ═══════════════════════════════════════════════════════════

def luxury_bg(canvas, doc):
    """Fond nuit + starfield doré + coin ornemental (invoqué par doc.build)."""
    canvas.saveState()
    w, h = A4
    # Fond nuit profonde
    canvas.setFillColor(NIGHT)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # Overlay dégradé subtil vers coin (effet parchemin cosmique)
    canvas.setFillColor(NIGHT_SOFT)
    canvas.setFillAlpha(0.5)
    canvas.circle(w * 0.85, h * 0.15, 200, fill=1, stroke=0)
    canvas.setFillAlpha(1)
    # Starfield doré (pseudo-random déterministe)
    import random as _r
    rng = _r.Random(42)
    canvas.setFillColor(GOLD)
    for _ in range(80):
        x = rng.random() * w
        y = rng.random() * h
        r = rng.choice([0.4, 0.6, 0.8, 1.0, 0.5])
        canvas.setFillAlpha(rng.uniform(0.2, 0.7))
        canvas.circle(x, y, r, fill=1, stroke=0)
    canvas.setFillAlpha(1)
    # Cadre or fin (marge intérieure)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.4)
    canvas.rect(1.3 * cm, 1.3 * cm, w - 2.6 * cm, h - 2.6 * cm, stroke=1, fill=0)
    # Pagination discrète
    if doc.page > 1:
        canvas.setFont(font('Cinzel', 'Helvetica'), 7)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(w / 2, 1 * cm, f'✦ {doc.page} ✦')
    canvas.restoreState()


# ═══════════════════════════════════════════════════════════
#   STYLES LUXE (surcharge du pdf_theme de base)
# ═══════════════════════════════════════════════════════════

def luxury_styles() -> dict:
    register_fonts()
    base = make_styles()
    return {
        **base,
        'cover_title': ParagraphStyle('cover_title', fontName=font('Cormorant', 'Helvetica'),
                                       fontSize=52, leading=60, textColor=CREAM,
                                       alignment=TA_CENTER, spaceAfter=12),
        'cover_sub':   ParagraphStyle('cover_sub', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                                       fontSize=20, leading=28, textColor=GOLD,
                                       alignment=TA_CENTER, spaceAfter=40),
        'section_tag': ParagraphStyle('section_tag', fontName=font('Cinzel', 'Helvetica'),
                                       fontSize=10, textColor=GOLD,
                                       alignment=TA_CENTER, spaceAfter=24),
        'planet_glyph': ParagraphStyle('planet_glyph', fontName='Helvetica',
                                        fontSize=140, leading=140, textColor=GOLD,
                                        alignment=TA_CENTER, spaceAfter=6),
        'planet_name': ParagraphStyle('planet_name', fontName=font('Cinzel', 'Helvetica'),
                                       fontSize=22, leading=30, textColor=CREAM,
                                       alignment=TA_CENTER, spaceAfter=10),
        'waouh': ParagraphStyle('waouh', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                                 fontSize=28, leading=38, textColor=GOLD_LIGHT,
                                 alignment=TA_CENTER, leftIndent=1.5 * cm, rightIndent=1.5 * cm,
                                 spaceAfter=30),
        'body_luxe': ParagraphStyle('body_luxe', fontName=font('Cormorant', 'Helvetica'),
                                     fontSize=13, leading=22, textColor=CREAM,
                                     alignment=TA_LEFT, spaceAfter=14),
        'dialogue': ParagraphStyle('dialogue', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                                    fontSize=15, leading=26, textColor=LAVENDER,
                                    alignment=TA_CENTER, leftIndent=1.5 * cm, rightIndent=1.5 * cm,
                                    spaceAfter=20),
        'teaser': ParagraphStyle('teaser', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                                  fontSize=22, leading=32, textColor=GOLD_LIGHT,
                                  alignment=TA_CENTER, leftIndent=2 * cm, rightIndent=2 * cm,
                                  spaceAfter=20),
        'signature': ParagraphStyle('signature', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                                     fontSize=16, textColor=GOLD,
                                     alignment=TA_CENTER, spaceAfter=8),
    }


# ═══════════════════════════════════════════════════════════
#   BUILDING BLOCKS — pages standardisées
# ═══════════════════════════════════════════════════════════

def cover_page(story: list, styles: dict, prenom: str, subtitle: str, illustration_slug: str = 'ciel_zodiaque'):
    """Couverture pleine page : illustration cosmique + prénom + titre."""
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph('✦ PLUME ASTRALE ✦', styles['section_tag']))
    story.append(Spacer(1, 0.6 * cm))
    img_bytes = _dl_image(illustration_url(illustration_slug, 1200))
    if img_bytes:
        img = RLImage(img_bytes, width=10 * cm, height=10 * cm, mask='auto')
        story.append(img)
        story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(prenom, styles['cover_title']))
    story.append(Paragraph(subtitle, styles['cover_sub']))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(datetime.now().strftime('%d %B %Y').upper(),
                           ParagraphStyle('date_cover', fontName=font('Cinzel', 'Helvetica'),
                                           fontSize=9, textColor=MUTED,
                                           alignment=TA_CENTER)))
    story.append(PageBreak())


def opening_page(story: list, styles: dict, prenom: str, first_line: str = "Ton ciel n'a jamais été aussi clair."):
    """Page 2 — l'accueil spectaculaire : prénom + ligne d'ouverture pleine page."""
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph(f'<font color="{GOLD_HEX}">✦</font>', styles['planet_glyph']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(prenom, styles['cover_title']))
    story.append(Paragraph(first_line, styles['waouh']))
    story.append(PageBreak())


def teaser_page(story: list, styles: dict, teaser_text: str):
    """Page teaser type Netflix : une phrase seule, pleine page, qui donne envie de tourner."""
    story.append(Spacer(1, 11 * cm))
    story.append(Paragraph(teaser_text, styles['teaser']))
    story.append(PageBreak())


def waouh_quote_page(story: list, styles: dict, quote: str, illustration_slug: Optional[str] = None):
    """Page pleine avec une phrase 'waouh' + illustration optionnelle."""
    story.append(Spacer(1, 3 * cm))
    if illustration_slug:
        img_bytes = _dl_image(illustration_url(illustration_slug, 800))
        if img_bytes:
            story.append(RLImage(img_bytes, width=8 * cm, height=8 * cm, mask='auto'))
            story.append(Spacer(1, 2 * cm))
    else:
        story.append(Spacer(1, 6 * cm))
    story.append(Paragraph(f'« {quote} »', styles['waouh']))
    story.append(PageBreak())


def chapter_illustration(story: list, styles: dict, chapter_tag: str, title: str, illustration_slug: str):
    """Page séparation de chapitre — tag + titre + illustration pleine page."""
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(chapter_tag.upper(), styles['section_tag']))
    story.append(Paragraph(title, styles['cover_title']))
    story.append(Spacer(1, 1 * cm))
    img_bytes = _dl_image(illustration_url(illustration_slug, 1200))
    if img_bytes:
        story.append(RLImage(img_bytes, width=12 * cm, height=12 * cm, mask='auto'))
    story.append(PageBreak())


def planet_glyph_page(story: list, styles: dict, glyph: str, planet_name: str, tagline: str):
    """Page personnage planète : glyph géant + nom + tagline poétique."""
    story.append(Spacer(1, 5 * cm))
    story.append(Paragraph(glyph, styles['planet_glyph']))
    story.append(Paragraph(planet_name.upper(), styles['planet_name']))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(f'« {tagline} »', styles['waouh']))
    story.append(PageBreak())


def planet_analysis_page(story: list, styles: dict, planet_name: str, sign: str, body_html: str,
                          dialogue_question: Optional[str] = None):
    """Page analyse d'une planète : nom+signe en haut, dialogue psy, puis corps texte."""
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(f'{planet_name.upper()} — <font color="{GOLD_HEX}">{sign}</font>',
                           ParagraphStyle('planet_h', fontName=font('Cinzel', 'Helvetica'),
                                           fontSize=14, textColor=CREAM,
                                           alignment=TA_CENTER, spaceAfter=24)))
    if dialogue_question:
        story.append(Paragraph(dialogue_question, styles['dialogue']))
        story.append(Spacer(1, 0.4 * cm))
    # Corps
    for para in body_html.split('\n\n'):
        para = para.strip()
        if para:
            story.append(Paragraph(para, styles['body_luxe']))
    story.append(PageBreak())


def emotional_ending(story: list, styles: dict, prenom: str):
    """Fin très émotionnelle — signée Soléna."""
    story.append(Spacer(1, 4 * cm))
    img_bytes = _dl_image(illustration_url('astral_silhouette', 800))
    if img_bytes:
        story.append(RLImage(img_bytes, width=8 * cm, height=8 * cm, mask='auto'))
        story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph('Ferme les yeux.', styles['waouh']))
    story.append(Paragraph(f'Repense à tout ce que tu viens de lire, {prenom}.', styles['dialogue']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        'Il y a une raison pour laquelle tu es arrivée jusqu\'ici.',
        styles['dialogue']))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        'Les étoiles n\'écrivent pas ton destin.<br/>'
        'Elles éclairent simplement le chemin<br/>que tu es libre d\'emprunter.',
        styles['waouh']))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph('— Soléna', styles['signature']))


def build_luxury_doc(buf: io.BytesIO, title: str, author: str = 'Plume Astrale') -> SimpleDocTemplate:
    """Fabrique un SimpleDocTemplate configuré pour le rendu luxe."""
    return SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=title,
        author=author,
    )
