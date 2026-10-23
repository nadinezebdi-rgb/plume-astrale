"""Générateur PDF léger pour la synthèse d'un tirage de tarot (Marseille 3 cartes
ou Croix Celtique 10 cartes).

Prend en entrée les données du tirage telles que renvoyées par
`/api/tarot/marseille` ou `/api/tarot/celtique`, et produit un PDF A4 cohérent
avec le thème « livre de luxe » utilisé pour les thèmes natals.
"""
from __future__ import annotations
import io
import os
import re
from typing import Any, Dict, List, Optional

from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    Image as RLImage, Paragraph, Spacer, PageBreak, KeepTogether,
)

from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, teaser_page, chapter_illustration,
    emotional_ending, _dl_image,
)

try:
    from PIL import Image as PILImage
    _HAS_PIL = True
except Exception:  # pragma: no cover
    _HAS_PIL = False

_SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
_TAROT_CDN = f"{_SUPABASE_URL}/storage/v1/object/public/library/tarot" if _SUPABASE_URL else ''


# ─── Normalisation nom → slug Supabase ────────────────────────────────────

_TAROT_SLUGS: Dict[str, str] = {
    'le mat': '00_le_mat', 'le fou': '00_le_mat',
    'le bateleur': '01_le_bateleur', 'le magicien': '01_le_bateleur',
    'la papesse': '02_la_papesse',
    "l'imperatrice": '03_l_imperatrice', 'imperatrice': '03_l_imperatrice',
    "l'empereur": '04_l_empereur', 'empereur': '04_l_empereur',
    'le pape': '05_le_pape',
    "l'amoureux": '06_les_amoureux', 'les amoureux': '06_les_amoureux', 'amoureux': '06_les_amoureux',
    'le chariot': '07_le_chariot',
    'la justice': '08_la_justice',
    "l'hermite": '09_l_hermite', 'hermite': '09_l_hermite',
    'la roue de fortune': '10_la_roue_de_fortune',
    'la force': '11_la_force',
    'le pendu': '12_le_pendu',
    "l'arcane sans nom": '13_l_arcane_sans_nom', 'arcane sans nom': '13_l_arcane_sans_nom', 'la mort': '13_l_arcane_sans_nom',
    'la temperance': '14_la_temperance', 'temperance': '14_la_temperance',
    'le diable': '15_le_diable',
    'la maison dieu': '16_la_maison_dieu', 'la tour': '16_la_maison_dieu',
    "l'etoile": '17_l_etoile', 'etoile': '17_l_etoile',
    'la lune': '18_la_lune',
    'le soleil': '19_le_soleil',
    'le jugement': '20_le_jugement',
    'le monde': '21_le_monde',
}


def _norm(s: str) -> str:
    if not s:
        return ''
    s = s.strip().lower()
    # strip accents
    s = (s.replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('ë', 'e')
          .replace('à', 'a').replace('â', 'a').replace('ä', 'a')
          .replace('î', 'i').replace('ï', 'i')
          .replace('ô', 'o').replace('ö', 'o')
          .replace('ù', 'u').replace('û', 'u').replace('ü', 'u')
          .replace('ç', 'c'))
    s = re.sub(r'\s+', ' ', s)
    return s


def _card_image_bytes(card_name: str) -> Optional[io.BytesIO]:
    if not _TAROT_CDN:
        return None
    slug = _TAROT_SLUGS.get(_norm(card_name))
    if not slug:
        return None
    url = f"{_TAROT_CDN}/{slug}_512.png"
    raw = _dl_image(url)
    if not raw or not _HAS_PIL:
        return raw
    # Compress to ~250KB JPEG — PDF n'a pas besoin de PNG transparent.
    try:
        raw.seek(0)
        img = PILImage.open(raw).convert('RGB')
        # Resize to 320px wide (plenty for a 5.5cm image on A4)
        w, h = img.size
        if w > 320:
            img = img.resize((320, int(h * 320 / w)), PILImage.LANCZOS)
        out = io.BytesIO()
        img.save(out, format='JPEG', quality=78, optimize=True)
        out.seek(0)
        return out
    except Exception:
        raw.seek(0)
        return raw


# ─── Builders ─────────────────────────────────────────────────────────────

def _domaine_label(domaine: str) -> str:
    return {
        'amour': 'Amour & Relations',
        'travail': 'Carrière & Travail',
        'argent': 'Finances & Abondance',
        'sante': 'Santé & Bien-être',
        'spirituel': 'Spiritualité',
        'general': 'Question Générale',
    }.get(domaine, 'Question Générale')


def _clean(text: str) -> str:
    if not text:
        return ''
    return (text or '').replace('**', '').replace('*', '').strip()


def _card_block(story: list, styles: dict, carte: Dict[str, Any], position_label: str):
    """Ajoute une page avec la position, l'image, le nom, l'interprétation."""
    story.append(Paragraph(position_label.upper(), styles['section_tag']))
    nom = carte.get('nom', '')
    orient = (carte.get('orientation') or '').lower()
    is_rev = orient in ('renverse', 'renversé', 'reversed')
    story.append(Paragraph(
        nom + (' <font color="#B8A9E8"><i>(renversée)</i></font>' if is_rev else ''),
        styles['planet_name'],
    ))
    story.append(Spacer(1, 0.6 * cm))

    img = _card_image_bytes(nom)
    if img:
        story.append(RLImage(img, width=5.5 * cm, height=9 * cm, mask='auto'))
        story.append(Spacer(1, 0.5 * cm))

    mots = carte.get('mots_cles') or []
    if mots:
        story.append(Paragraph(
            ' · '.join(str(m) for m in mots[:4]),
            ParagraphStyle('mots', fontName='Helvetica-Oblique', fontSize=10,
                            textColor=styles['cover_title'].textColor,
                            alignment=TA_CENTER, spaceAfter=8),
        ))

    interp = _clean(carte.get('interpretation', ''))
    if interp:
        story.append(Spacer(1, 0.3 * cm))
        for para in interp.split('\n\n'):
            para = para.strip()
            if para:
                story.append(Paragraph(para, styles['body_luxe']))

    conseil = _clean(carte.get('conseil', ''))
    if conseil:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(
            f'<i>« {conseil} »</i>',
            ParagraphStyle('conseil', fontName='Helvetica-Oblique', fontSize=11,
                            textColor=styles['cover_title'].textColor,
                            alignment=TA_CENTER, leading=16),
        ))

    story.append(PageBreak())


def build_tarot_pdf(
    tirage_type: str,
    question: str,
    domaine: str,
    data: Dict[str, Any],
    prenom: str = 'Voyageur',
) -> bytes:
    """Génère un PDF cohérent avec le thème luxury à partir des données renvoyées
    par les endpoints /api/tarot/marseille ou /api/tarot/celtique."""
    buf = io.BytesIO()
    is_celtique = tirage_type == 'celtique'
    title = 'Croix Celtique' if is_celtique else 'Tarot de Marseille'
    doc = build_luxury_doc(buf, title=f'{title} — {prenom}')
    styles = luxury_styles()
    story: list = []

    # Couverture
    cover_page(story, styles, prenom=prenom,
               subtitle=f'{title} — Synthèse personnelle',
               illustration_slug='astral_mandala')

    # Ouverture
    opening_page(story, styles, prenom=prenom,
                 first_line='Les Arcanes ont parlé.')

    # Teaser avec la question
    if question:
        teaser_page(story, styles, f'« {question} »')

    # Domaine
    story.append(Paragraph(_domaine_label(domaine).upper(), styles['section_tag']))
    story.append(Spacer(1, 0.3 * cm))

    # Pages par carte
    cartes: List[Dict[str, Any]] = data.get('cartes', []) or []
    positions_marseille = ['Passé', 'Présent', 'Futur']
    positions_celtique = [
        'La Situation Présente', "L'Obstacle ou le Défi", 'Le Fondement',
        'Le Passé Récent', 'La Couronne — Le Meilleur Possible',
        'Le Futur Proche', 'Votre Attitude', "L'Environnement",
        'Espoirs et Craintes', 'Le Résultat Final',
    ]
    positions = positions_celtique if is_celtique else positions_marseille

    for i, carte in enumerate(cartes):
        pos_label = carte.get('position') or (positions[i] if i < len(positions) else f'Position {i+1}')
        _card_block(story, styles, carte, pos_label)

    # Synthèse
    chapter_illustration(story, styles,
                          chapter_tag='✦ Synthèse de Soléna ✦',
                          title='Les Arcanes révèlent',
                          illustration_slug='fleurs_or')
    story.append(Spacer(1, 1.2 * cm))

    if is_celtique:
        analyse = data.get('analyse') or {}
        _add_section(story, styles, 'Énergie Globale', analyse.get('energie_globale'))
        _add_bloc(story, styles, 'Situation Actuelle', analyse.get('situation_actuelle'))
        _add_bloc(story, styles, 'Obstacle Principal', analyse.get('obstacle_principal'))
        _add_bloc(story, styles, 'Fondement', analyse.get('fondement'))
        _add_bloc(story, styles, 'Résultat Probable', analyse.get('resultat_probable'))
        _add_section(story, styles, 'Synthèse Finale', analyse.get('synthese_finale'))
        _add_section(story, styles, "Conseil d'Action", analyse.get('conseil_action'))
    else:
        synth = data.get('synthese') or {}
        if synth.get('tendance_generale'):
            _add_section(story, styles, f"Tendance Générale : {synth['tendance_generale']}",
                         synth.get('fil_conducteur'))
        if synth.get('message_passe'):
            _add_section(story, styles, 'Message du Passé', synth['message_passe'])
        if synth.get('message_present'):
            _add_section(story, styles, 'Message du Présent', synth['message_present'])
        if synth.get('message_futur'):
            _add_section(story, styles, 'Message du Futur', synth['message_futur'])
        if data.get('conseil_final'):
            _add_section(story, styles, 'Conseil des Arcanes', data['conseil_final'])

    story.append(PageBreak())
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()


def _add_section(story: list, styles: dict, title: str, body: Optional[str]):
    body = _clean(body or '')
    if not body:
        return
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(title, ParagraphStyle(
        'section', fontName='Helvetica-Bold', fontSize=14,
        textColor=styles['cover_title'].textColor, spaceAfter=10,
    )))
    for para in body.split('\n\n'):
        para = para.strip()
        if para:
            story.append(Paragraph(para, styles['body_luxe']))
            story.append(Spacer(1, 0.15 * cm))


def _add_bloc(story: list, styles: dict, title: str, bloc: Optional[Dict[str, Any]]):
    if not bloc:
        return
    carte = bloc.get('carte', '')
    message = _clean(bloc.get('message', ''))
    if not (carte or message):
        return
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(title, ParagraphStyle(
        'section_mini', fontName='Helvetica-Bold', fontSize=12,
        textColor=styles['cover_title'].textColor, spaceAfter=6,
    )))
    if carte:
        story.append(Paragraph(f'<b>{carte}</b>', ParagraphStyle(
            'card_name', fontName='Helvetica', fontSize=11,
            textColor=styles['cover_title'].textColor, spaceAfter=4,
        )))
    if message:
        story.append(Paragraph(message, styles['body_luxe']))
