"""
PDF Tarot — génération des rapports de tirage (Croix Celtique).

Utilise le pdf_theme.py unifié (Cinzel + Cormorant, palette or/nuit).
"""
from __future__ import annotations
import io
import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from services.pdf_theme import (
    register_fonts, make_styles, starfield_bg,
    PALETTE, GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED, NIGHT,
)

logger = logging.getLogger(__name__)


def build_croix_celtique_pdf(question: str, prenom: str, tirage: list, synthese: str) -> bytes:
    """Génère le PDF de la Croix Celtique — 12 pages :
      - Couverture (question, date, prénom)
      - Vue d'ensemble (grille des 10 positions)
      - 1 page par carte (nom, mots-clés, position, interprétation)
      - Synthèse finale (Soléna)
    """
    register_fonts()
    styles = make_styles()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=f"Croix Celtique — {prenom}",
        author='Plume Astrale',
    )

    # Styles locaux
    cover_title = ParagraphStyle(
        'CoverTitle', parent=styles['title'],
        fontName='Cormorant', fontSize=44, leading=52, alignment=TA_CENTER,
        textColor=CREAM, spaceAfter=8,
    )
    cover_sub = ParagraphStyle(
        'CoverSub', parent=styles['body'],
        fontName='Cormorant-Italic', fontSize=18, alignment=TA_CENTER,
        textColor=GOLD, spaceAfter=30,
    )
    section_title = ParagraphStyle(
        'SectionTitle', parent=styles['h2'],
        fontName='Cinzel', fontSize=13, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=8, spaceBefore=0,
    )
    card_name = ParagraphStyle(
        'CardName', parent=styles['title'],
        fontName='Cormorant', fontSize=32, leading=38, alignment=TA_CENTER,
        textColor=CREAM, spaceAfter=6,
    )
    card_keyword = ParagraphStyle(
        'CardKeyword', parent=styles['body'],
        fontName='Cormorant-Italic', fontSize=13, alignment=TA_CENTER,
        textColor=LAVENDER, spaceAfter=18,
    )
    position_label = ParagraphStyle(
        'PositionLabel', parent=styles['body'],
        fontName='Cinzel', fontSize=10, textColor=GOLD,
        alignment=TA_CENTER, spaceAfter=4,
    )
    position_desc = ParagraphStyle(
        'PositionDesc', parent=styles['body'],
        fontName='Cormorant-Italic', fontSize=11, textColor=MUTED,
        alignment=TA_CENTER, spaceAfter=18,
    )
    interpretation = ParagraphStyle(
        'Interpretation', parent=styles['body'],
        fontName='Cormorant', fontSize=13, leading=20, textColor=CREAM,
        alignment=TA_CENTER, spaceAfter=8,
    )
    reversed_badge = ParagraphStyle(
        'ReversedBadge', parent=styles['body'],
        fontName='Cinzel', fontSize=9, textColor=GOLD_LIGHT,
        alignment=TA_CENTER, spaceAfter=14,
    )
    body_p = styles['body']  # noqa: F841

    story = []

    # ═══════════ COUVERTURE ═══════════
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph('✦ TIRAGE SACRÉ ✦', section_title))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph('La Croix Celtique', cover_title))
    story.append(Paragraph('10 arcanes majeurs — lecture profonde', cover_sub))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(f'Pour <b>{prenom or "Toi"}</b>', ParagraphStyle(
        'ForWhom', fontName='Cormorant', fontSize=15, alignment=TA_CENTER, textColor=CREAM,
    )))
    story.append(Spacer(1, 0.6 * cm))
    if question:
        story.append(Paragraph(f'« {question} »', ParagraphStyle(
            'Question', fontName='Cormorant-Italic', fontSize=14, alignment=TA_CENTER,
            textColor=LAVENDER, leftIndent=1.5 * cm, rightIndent=1.5 * cm,
        )))
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph(
        datetime.now().strftime('%d %B %Y').capitalize(),
        ParagraphStyle('DateP', fontName='Cinzel', fontSize=10, alignment=TA_CENTER, textColor=MUTED),
    ))
    story.append(PageBreak())

    # ═══════════ SOMMAIRE DES 10 POSITIONS ═══════════
    story.append(Paragraph('LE PLAN DE TA CROIX', section_title))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        'Chaque position raconte une facette de ta question. Lis-les dans l\'ordre — '
        'les cinq premières forment la Croix elle-même, les cinq suivantes la Colonne '
        'qui prolonge la lecture vers l\'issue finale.',
        ParagraphStyle('Intro', fontName='Cormorant-Italic', fontSize=13,
                       leading=20, alignment=TA_CENTER, textColor=CREAM, spaceAfter=20),
    ))

    for entry in tirage:
        pos_id = entry.get('position_id')
        pos_nom = entry.get('position_nom', '')
        carte_nom = entry.get('carte', {}).get('nom', '')
        is_rev = entry.get('carte', {}).get('is_reversed', False)
        rev_mark = ' <font color="' + GOLD_LIGHT + '">(retournée)</font>' if is_rev else ''
        line = f'<font color="{GOLD}">{pos_id}.</font> <b>{pos_nom}</b> — <font color="{LAVENDER}"><i>{carte_nom}</i></font>{rev_mark}'
        story.append(Paragraph(
            line,
            ParagraphStyle('SommaireLine', fontName='Cormorant', fontSize=13,
                           leading=22, textColor=CREAM, alignment=TA_CENTER, spaceAfter=6),
        ))
    story.append(PageBreak())

    # ═══════════ UNE PAGE PAR CARTE ═══════════
    for entry in tirage:
        pos_id = entry.get('position_id')
        pos_nom = entry.get('position_nom', '')
        pos_desc = entry.get('position_description', '')
        carte = entry.get('carte', {})
        interp = entry.get('interpretation', '')
        is_rev = carte.get('is_reversed', False)

        story.append(Spacer(1, 1.5 * cm))
        story.append(Paragraph(f'POSITION {pos_id} — {pos_nom.upper()}', position_label))
        story.append(Paragraph(pos_desc, position_desc))
        story.append(Paragraph(carte.get('nom', ''), card_name))
        keyword = carte.get('mots_cles', carte.get('energie', ''))
        if keyword:
            story.append(Paragraph(keyword, card_keyword))
        if is_rev:
            story.append(Paragraph('CARTE RETOURNÉE — blocage à conscientiser', reversed_badge))
        if interp:
            # Enveloppe interprétation dans un bloc lisible
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph(interp, interpretation))
        story.append(PageBreak())

    # ═══════════ SYNTHÈSE ═══════════
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph('✦ SYNTHÈSE DE SOLÉNA ✦', section_title))
    story.append(Spacer(1, 0.8 * cm))
    # Nettoyer les balises markdown éventuelles
    clean_synthese = (synthese or '').replace('**', '').replace('*', '').strip()
    # Split en paragraphes
    for para in clean_synthese.split('\n'):
        para = para.strip()
        if para:
            story.append(Paragraph(para, ParagraphStyle(
                'Synth', fontName='Cormorant', fontSize=13, leading=22,
                textColor=CREAM, alignment=TA_CENTER, spaceAfter=14,
                leftIndent=1 * cm, rightIndent=1 * cm,
            )))
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph('— Soléna, pour Plume Astrale', ParagraphStyle(
        'Signature', fontName='Cormorant-Italic', fontSize=13, textColor=GOLD,
        alignment=TA_CENTER,
    )))

    # Build final avec background étoilé
    doc.build(story, onFirstPage=starfield_bg, onLaterPages=starfield_bg)
    return buf.getvalue()
