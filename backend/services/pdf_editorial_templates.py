"""14 templates de pages éditoriales pour le PDF Roman.

Chaque fonction mute une story ReportLab en place. Aucune improvisation :
tout PDF Plume Astrale est composé exclusivement de ces 14 templates.

Templates :
  1. t_cover                    — grande illustration + titre + sous-titre
  2. t_quote                    — une phrase, fond cosmique
  3. t_chapter_opening          — numéro romain + titre + petit texte
  4. t_data                     — infographie type icônes+chiffres
  5. t_portrait                 — image + titre + question + texte + encadré
  6. t_analysis                 — 2 colonnes : texte à gauche, illustration à droite
  7. t_focus                    — une seule notion, énormément d'espace blanc
  8. t_infographic              — barres/jauges/cercles (non-Excel)
  9. t_double_illustration      — image pleine page + peu de texte
 10. t_callout                  — 3 conseils + une phrase mémorable
 11. t_ritual                   — étapes + temps + pierre + couleur + respiration
 12. t_journal                  — question + zone d'écriture blanche
 13. t_synthesis                — résumé/forces/défis/mission/citation
 14. t_ending                   — lettre finale de Soléna

Le pilote (Phase C) implémente les 9 templates nécessaires à l'Acte III.
Les autres seront ajoutés en Phase 2/3.
"""
from __future__ import annotations
import os
from typing import Optional, List, Dict, Any
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor

from services.pdf_editorial_system import (
    GOLD, CREAM, GREY_SUBTLE, GOLD_HEX, CREAM_HEX, GREY_HEX,
    H_CHAPTER, H_PAGE, SUBTITLE, BODY, QUOTE, CALLOUT, CAPTION,
    LEAD_CHAPTER, LEAD_PAGE, LEAD_BODY, LEAD_QUOTE, LEAD_CALLOUT,
    SP_XS, SP_S, SP_M, SP_L, SP_XL, SP_XXL,
    styles_cormorant, styles_cormorant_italic, styles_cinzel,
)


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 2 — t_quote : une phrase, silence autour
# ═══════════════════════════════════════════════════════════════════

def t_quote(story, quote_text: str, attribution: Optional[str] = None) -> None:
    """Page-citation : centre de la page, un seul texte italique doré."""
    story.append(Spacer(1, 8.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦</font>',
        ParagraphStyle('quote_star', fontName=styles_cinzel(),
                       fontSize=18, alignment=TA_CENTER, spaceAfter=SP_M),
    ))
    story.append(Paragraph(
        f'« {quote_text} »',
        ParagraphStyle('quote_body', fontName=styles_cormorant_italic(),
                       fontSize=QUOTE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_QUOTE),
    ))
    if attribution:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            f'— {attribution}',
            ParagraphStyle('quote_attr', fontName=styles_cinzel(),
                           fontSize=CAPTION, textColor=GOLD, alignment=TA_CENTER),
        ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 3 — t_chapter_opening : ouverture d'Acte
# ═══════════════════════════════════════════════════════════════════

def t_chapter_opening(story, roman: str, title: str,
                       kicker: Optional[str] = None,
                       illustration_path: Optional[str] = None) -> None:
    """Grande ouverture d'Acte : numéro romain + titre monumental + phrase-fil."""
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">ACTE {roman}</font>',
        ParagraphStyle('co_roman', fontName=styles_cinzel(),
                       fontSize=13, alignment=TA_CENTER, spaceAfter=SP_M),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('co_title', fontName=styles_cormorant(),
                       fontSize=H_CHAPTER, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_CHAPTER, spaceAfter=SP_L),
    ))
    if kicker:
        story.append(Paragraph(
            kicker,
            ParagraphStyle('co_kicker', fontName=styles_cormorant_italic(),
                           fontSize=SUBTITLE, textColor=GREY_SUBTLE,
                           alignment=TA_CENTER, leading=LEAD_BODY, spaceAfter=SP_XL),
        ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(illustration_path, width=8 * cm, height=8 * cm, mask='auto'))
        except Exception:
            pass
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 5 — t_portrait : image + titre + question + texte + encadré
# ═══════════════════════════════════════════════════════════════════

def t_portrait(story, chapter_tag: str, title: str, question: str,
                body_html: str, illustration_path: Optional[str] = None) -> None:
    """Ouverture de chapitre de l'âme (Acte III)."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ {chapter_tag.upper()} ✦</font>',
        ParagraphStyle('p_tag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_S),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('p_title', fontName=styles_cormorant(),
                       fontSize=H_PAGE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_PAGE, spaceAfter=SP_M),
    ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(illustration_path, width=5 * cm, height=5 * cm, mask='auto'))
            story.append(Spacer(1, SP_S))
        except Exception:
            pass
    story.append(Paragraph(
        f'« {question} »',
        ParagraphStyle('p_q', fontName=styles_cormorant_italic(),
                       fontSize=SUBTITLE, textColor=GOLD, alignment=TA_CENTER,
                       leading=LEAD_BODY, spaceAfter=SP_L),
    ))
    story.append(Paragraph(
        body_html,
        ParagraphStyle('p_body', fontName=styles_cormorant(),
                       fontSize=BODY, textColor=CREAM, alignment=TA_JUSTIFY,
                       leading=LEAD_BODY, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 6 — t_analysis : 2 colonnes (texte + illustration + citation)
# ═══════════════════════════════════════════════════════════════════

def t_analysis(story, title: str, body_html: str,
                illustration_path: Optional[str] = None,
                inset_quote: Optional[str] = None) -> None:
    """Analyse en 2 colonnes : texte à gauche, image + citation à droite."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        title,
        ParagraphStyle('a_title', fontName=styles_cormorant(),
                       fontSize=H_PAGE, textColor=CREAM, alignment=TA_LEFT,
                       leading=LEAD_PAGE, spaceAfter=SP_L, leftIndent=1.5 * cm),
    ))
    text_para = Paragraph(
        body_html,
        ParagraphStyle('a_body', fontName=styles_cormorant(),
                       fontSize=BODY, textColor=CREAM, alignment=TA_JUSTIFY,
                       leading=LEAD_BODY),
    )
    right_col: list = []
    if illustration_path and os.path.exists(illustration_path):
        try:
            right_col.append(RLImage(illustration_path, width=6.5 * cm, height=6.5 * cm, mask='auto'))
            right_col.append(Spacer(1, SP_S))
        except Exception:
            pass
    if inset_quote:
        right_col.append(Paragraph(
            f'<font color="{GOLD_HEX}">« {inset_quote} »</font>',
            ParagraphStyle('a_inset', fontName=styles_cormorant_italic(),
                           fontSize=CALLOUT, textColor=GOLD, alignment=TA_LEFT,
                           leading=LEAD_CALLOUT),
        ))
    tbl = Table([[text_para, right_col]],
                colWidths=[9 * cm, 7 * cm], hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), SP_M),
    ]))
    story.append(tbl)
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 7 — t_focus : une notion, beaucoup d'espace blanc
# ═══════════════════════════════════════════════════════════════════

def t_focus(story, kicker: str, single_word: str, meaning: str) -> None:
    """Page-focus : espace, un mot immense, une glose sous-jacente."""
    story.append(Spacer(1, 7 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">{kicker.upper()}</font>',
        ParagraphStyle('f_kicker', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_L),
    ))
    story.append(Paragraph(
        single_word.upper(),
        ParagraphStyle('f_word', fontName=styles_cormorant(),
                       fontSize=H_CHAPTER + 8, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_CHAPTER + 10, spaceAfter=SP_XL),
    ))
    story.append(Paragraph(
        meaning,
        ParagraphStyle('f_mean', fontName=styles_cormorant_italic(),
                       fontSize=SUBTITLE, textColor=GREY_SUBTLE, alignment=TA_CENTER,
                       leading=LEAD_BODY, leftIndent=3 * cm, rightIndent=3 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 10 — t_callout : 3 conseils + phrase mémorable
# ═══════════════════════════════════════════════════════════════════

def t_callout(story, title: str, tips: List[str], memorable_line: str) -> None:
    """Encadré "À RETENIR" : 3 conseils numérotés + une phrase-clé."""
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ À RETENIR ✦</font>',
        ParagraphStyle('cl_tag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_S),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('cl_title', fontName=styles_cormorant(),
                       fontSize=H_PAGE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_PAGE, spaceAfter=SP_L),
    ))
    for i, tip in enumerate(tips[:3], 1):
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">{i:02d}</font>&nbsp;&nbsp;{tip}',
            ParagraphStyle(f'cl_tip{i}', fontName=styles_cormorant(),
                           fontSize=CALLOUT, textColor=CREAM, alignment=TA_LEFT,
                           leading=LEAD_CALLOUT, leftIndent=2 * cm, rightIndent=1.5 * cm,
                           spaceAfter=SP_S),
        ))
    story.append(Spacer(1, SP_L))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">« {memorable_line} »</font>',
        ParagraphStyle('cl_mem', fontName=styles_cormorant_italic(),
                       fontSize=QUOTE, alignment=TA_CENTER, leading=LEAD_QUOTE,
                       leftIndent=2 * cm, rightIndent=2 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 11 — t_ritual : étapes + temps + pierre + couleur + respiration
# ═══════════════════════════════════════════════════════════════════

def t_ritual(story, title: str, steps: List[str], duration: str,
              stone: str, color: str, breathing: str,
              illustration_path: Optional[str] = None) -> None:
    """Page-rituel : étapes concrètes + paramètres sensoriels."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ RITUEL ✦</font>',
        ParagraphStyle('r_tag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_S),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('r_title', fontName=styles_cormorant(),
                       fontSize=H_PAGE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_PAGE, spaceAfter=SP_M),
    ))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(illustration_path, width=4.5 * cm, height=4.5 * cm, mask='auto'))
            story.append(Spacer(1, SP_M))
        except Exception:
            pass
    # 4 paramètres sensoriels en ligne
    sens = [
        (['Temps', duration]),
        (['Pierre', stone]),
        (['Couleur', color]),
        (['Souffle', breathing]),
    ]
    rows = [[Paragraph(f'<font color="{GOLD_HEX}">{l}</font>',
                        ParagraphStyle(f'r_hdr{i}', fontName=styles_cinzel(),
                                       fontSize=CAPTION - 2, alignment=TA_CENTER))
             for i, (l, _) in enumerate(sens)]]
    rows.append([Paragraph(v,
                            ParagraphStyle(f'r_val{i}', fontName=styles_cormorant_italic(),
                                           fontSize=BODY, textColor=CREAM, alignment=TA_CENTER,
                                           leading=LEAD_BODY))
                 for i, (_, v) in enumerate(sens)])
    tbl = Table(rows, colWidths=[3.8 * cm] * 4, hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), SP_S),
        ('TOPPADDING', (0, 1), (-1, 1), SP_XS),
    ]))
    story.append(tbl)
    story.append(Spacer(1, SP_L))
    # Étapes numérotées
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">{i}.</font>&nbsp;&nbsp;{step}',
            ParagraphStyle(f'r_st{i}', fontName=styles_cormorant(),
                           fontSize=BODY, textColor=CREAM, alignment=TA_LEFT,
                           leading=LEAD_BODY, leftIndent=1.5 * cm, rightIndent=1.5 * cm,
                           spaceAfter=SP_S),
        ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 12 — t_journal : question + zone d'écriture blanche
# ═══════════════════════════════════════════════════════════════════

def t_journal(story, question: str, context_line: Optional[str] = None) -> None:
    """Page-journal : le lecteur écrit lui-même. Vraie zone d'écriture visible."""
    from reportlab.platypus import HRFlowable
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ JOURNAL ✦</font>',
        ParagraphStyle('j_tag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_M),
    ))
    story.append(Paragraph(
        question,
        ParagraphStyle('j_q', fontName=styles_cormorant_italic(),
                       fontSize=SUBTITLE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_BODY, spaceAfter=SP_S,
                       leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    if context_line:
        story.append(Paragraph(
            context_line,
            ParagraphStyle('j_ctx', fontName=styles_cormorant_italic(),
                           fontSize=CAPTION, textColor=GREY_SUBTLE, alignment=TA_CENTER,
                           spaceAfter=SP_L),
        ))
    else:
        story.append(Spacer(1, SP_L))
    # 8 lignes d'écriture (HRFlowable dorées discrètes)
    for _ in range(10):
        story.append(HRFlowable(width='75%', thickness=0.5,
                                 color=HexColor('#332E22'), spaceBefore=SP_S + 4,
                                 spaceAfter=0, hAlign='CENTER'))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 13 — t_synthesis : résumé/forces/défis/mission
# ═══════════════════════════════════════════════════════════════════

def t_synthesis(story, title: str, forces: List[str], defis: List[str],
                 mission: str, closing_quote: Optional[str] = None) -> None:
    """Synthèse de chapitre : Forces (à gauche), Défis (à droite), Mission dessous."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ SYNTHÈSE ✦</font>',
        ParagraphStyle('s_tag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_S),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('s_title', fontName=styles_cormorant(),
                       fontSize=H_PAGE, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_PAGE, spaceAfter=SP_L),
    ))

    def _bulleted(items: List[str], header: str, color: str) -> Paragraph:
        html = f'<font color="{color}"><b>{header}</b></font><br/><br/>' + \
               '<br/><br/>'.join(f'✦&nbsp;&nbsp;{it}' for it in items[:3])
        return Paragraph(html,
            ParagraphStyle(f's_{header}', fontName=styles_cormorant(),
                           fontSize=BODY, textColor=CREAM, alignment=TA_LEFT,
                           leading=LEAD_BODY))
    tbl = Table([[
        _bulleted(forces, 'FORCES', GOLD_HEX),
        _bulleted(defis, 'DÉFIS', GREY_HEX),
    ]], colWidths=[8 * cm, 8 * cm], hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), SP_L),
    ]))
    story.append(tbl)
    story.append(Spacer(1, SP_XL))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">MISSION</font>',
        ParagraphStyle('s_mtag', fontName=styles_cinzel(),
                       fontSize=CAPTION, alignment=TA_CENTER, spaceAfter=SP_XS),
    ))
    story.append(Paragraph(
        mission,
        ParagraphStyle('s_m', fontName=styles_cormorant_italic(),
                       fontSize=CALLOUT, textColor=CREAM, alignment=TA_CENTER,
                       leading=LEAD_CALLOUT, leftIndent=2 * cm, rightIndent=2 * cm),
    ))
    if closing_quote:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            f'« {closing_quote} »',
            ParagraphStyle('s_cq', fontName=styles_cormorant_italic(),
                           fontSize=SUBTITLE, textColor=GOLD, alignment=TA_CENTER,
                           leading=LEAD_BODY, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
        ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE 9 — t_double_illustration : image pleine page
# ═══════════════════════════════════════════════════════════════════

def t_double_illustration(story, illustration_path: str, caption: Optional[str] = None) -> None:
    """Page monumentale : image quasi pleine page, peu de texte."""
    story.append(Spacer(1, 2 * cm))
    if illustration_path and os.path.exists(illustration_path):
        try:
            story.append(RLImage(illustration_path, width=14 * cm, height=14 * cm, mask='auto'))
        except Exception:
            pass
    if caption:
        story.append(Spacer(1, SP_L))
        story.append(Paragraph(
            caption,
            ParagraphStyle('di_cap', fontName=styles_cormorant_italic(),
                           fontSize=SUBTITLE, textColor=GOLD, alignment=TA_CENTER,
                           leading=LEAD_BODY, leftIndent=2 * cm, rightIndent=2 * cm),
        ))
    story.append(PageBreak())
