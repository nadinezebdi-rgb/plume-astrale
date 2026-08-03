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


def build_croix_celtique_pdf_v2(question: str, prenom: str, tirage: list, synthese: str,
                                  ai_sections: dict | None = None) -> bytes:
    """Génère le PDF Croix Celtique au format livre de luxe.

    Si `ai_sections` est fourni (dict enrichi via enrich_report('croix_celtique', ...)),
    on insère 7 chapitres narratifs Soléna après la synthèse et avant la fin
    émotionnelle. Les clés attendues correspondent à REPORT_SPECS['croix_celtique'].
    """
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

    # ─── Chapitres narratifs IA (Soléna) ────────────────────────
    # Insérés seulement si `ai_sections` est fourni (7 sections).
    if ai_sections:
        _CHAP_LABELS = [
            ('introduction',      "Le sens de ta Croix"),
            ('noeud_present',     "Le nœud du présent"),
            ('racines_du_passe',  "Les racines du passé"),
            ('lumiere_a_venir',   "La lumière à venir"),
            ('forces_croisees',   "Les forces croisées"),
            ('message_final',     "Le message final"),
            ('invitation_finale', "L'invitation de Soléna"),
        ]
        for key, label in _CHAP_LABELS:
            html = (ai_sections.get(key) or '').strip()
            if not html:
                continue
            story.append(Paragraph('✦ Chapitre Soléna ✦', styles['section_tag']))
            story.append(Paragraph(label.upper(), styles['planet_name']))
            story.append(Spacer(1, 0.8 * cm))
            # Découpe en paragraphes autour de <br/><br/> ou double newline
            for para in html.replace('<br/><br/>', '\n\n').split('\n\n'):
                para = para.strip()
                if para:
                    story.append(Paragraph(para, styles['body_luxe']))
                    story.append(Spacer(1, 0.3 * cm))
            story.append(PageBreak())

    # ─── Fin émotionnelle ───────────────────────────────────────
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()


async def build_croix_celtique_pdf_v2_ai(
    question: str,
    prenom: str,
    tirage: list,
    synthese: str,
    birth_date_iso: str = '',
) -> bytes:
    """Version enrichie IA — 7 chapitres narratifs Soléna après la synthèse.

    Le toggle admin `ai_enrichment_disabled` est géré par enrich_report :
    - IA ON  → GPT-5.4 rédige les chapitres en fonction du tirage réel.
    - IA OFF → fallback statique riche (7 sections pré-rédigées).
    """
    try:
        from services.report_ai_enrichment import enrich_report
        # On envoie un context compact (les 10 positions + cartes tirées) au LLM.
        compact_tirage = [
            {
                'pos': (e.get('position_id'), e.get('position_nom')),
                'carte': (e.get('carte') or {}).get('nom'),
                'renversee': (e.get('carte') or {}).get('is_reversed'),
            }
            for e in (tirage or [])
        ]
        ai_sections = await enrich_report(
            report_type='croix_celtique',
            prenom=prenom or 'Voyageuse',
            birth_date_iso=birth_date_iso,
            context={'question': question, 'tirage': compact_tirage, 'synthese_soléna': synthese[:2000]},
        )
    except Exception:
        ai_sections = {}
    return build_croix_celtique_pdf_v2(
        question=question,
        prenom=prenom,
        tirage=tirage,
        synthese=synthese,
        ai_sections=ai_sections or None,
    )
