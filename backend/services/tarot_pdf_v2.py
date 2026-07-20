"""
Tarot Croix Celtique V2 — style livre de luxe (framework pdf_luxury_theme).

Remplace le générateur `services/tarot_pdf.py` pour les tirages Croix Celtique.
"""
from __future__ import annotations
import io
from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, teaser_page, waouh_quote_page,
    chapter_illustration, planet_glyph_page, planet_analysis_page, emotional_ending,
    illustration_url, _dl_image,
)
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def build_croix_celtique_pdf_v2(question: str, prenom: str, tirage: list, synthese: str) -> bytes:
    """Génère le PDF Croix Celtique au format livre de luxe."""
    buf = io.BytesIO()
    doc = build_luxury_doc(buf, title=f'Croix Celtique — {prenom}')
    styles = luxury_styles()
    story = []

    # ─── Couverture ─────────────────────────────────────────────
    cover_page(story, styles, prenom=prenom,
               subtitle='La Croix Celtique — 10 arcanes révélés',
               illustration_slug='astral_mandala')

    # ─── Ouverture ──────────────────────────────────────────────
    opening_page(story, styles, prenom=prenom,
                 first_line="Ta question a trouvé sa réponse.")

    # ─── Teaser ─────────────────────────────────────────────────
    if question:
        teaser_page(story, styles, f'« {question} »')

    # ─── Une page par carte (position + carte illustrée + interp) ─
    for entry in tirage:
        pos_id = entry.get('position_id')
        pos_nom = entry.get('position_nom', '')
        pos_desc = entry.get('position_description', '')
        carte = entry.get('carte', {})
        interp = entry.get('interpretation', '')
        is_rev = carte.get('is_reversed', False)

        # Page titre position + illustration carte
        story.append(Spacer(1, 2 * cm))
        story.append(Paragraph(f'POSITION {pos_id}', styles['section_tag']))
        story.append(Paragraph(pos_nom.upper(), styles['planet_name']))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(pos_desc, styles['dialogue']))
        story.append(Spacer(1, 0.8 * cm))
        # Image de la carte tarot (bucket library/tarot) — variante 512px pour PDF
        card_img_url = carte.get('image', '')
        if card_img_url:
            # Swap 1080 → 512 pour réduire le poids du PDF (10 cartes × 3MB → 10 × 250KB)
            card_img_url_pdf = card_img_url.replace('_1080.png', '_512.png')
            img_bytes = _dl_image(card_img_url_pdf)
            if img_bytes:
                story.append(RLImage(img_bytes, width=6 * cm, height=10 * cm, mask='auto'))
                story.append(Spacer(1, 0.5 * cm))
        # Nom carte + retournée
        card_name_txt = carte.get('nom', '')
        if is_rev:
            card_name_txt += ' <font color="#E8C766"><i>(retournée)</i></font>'
        story.append(Paragraph(card_name_txt, ParagraphStyle(
            'card_lbl', fontName='Helvetica', fontSize=16, textColor=styles['cover_title'].textColor,
            alignment=TA_CENTER, spaceAfter=12,
        )))
        # Interp
        if interp:
            story.append(Paragraph(interp, styles['body_luxe']))
        story.append(PageBreak())

    # ─── Synthèse Soléna ────────────────────────────────────────
    chapter_illustration(story, styles,
                          chapter_tag='✦ Synthèse de Soléna ✦',
                          title='La croix révèle',
                          illustration_slug='fleurs_or')
    story.append(Spacer(1, 1.5 * cm))
    clean_synth = (synthese or '').replace('**', '').replace('*', '').strip()
    for para in clean_synth.split('\n\n'):
        para = para.strip()
        if para:
            story.append(Paragraph(para, styles['body_luxe']))
    story.append(PageBreak())

    # ─── Fin émotionnelle ───────────────────────────────────────
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()
