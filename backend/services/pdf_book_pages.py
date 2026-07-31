"""pdf_book_pages — Pages "livre" pour le Thème Natal Plume Astrale.

Front matter (faux-titre, copyright, dédicace, TOC), diviseurs de parties,
pages thématiques (éléments, modalités, trio synthèse, aspects détaillés,
maisons), épilogue (année à venir, colophon parrainage).

Toutes les fonctions ont la même signature que celles de pdf_luxury_theme.py :
    fn(story, styles, ...args) — mutent la story ReportLab en place.

Chaque page appelle libimg pour un fond ou illustration cohérent avec le
reste du PDF (planètes, signes, maisons, tarot, style_refs).
"""
from __future__ import annotations
import os
from typing import Optional, List, Dict, Any
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Image as RLImage, Table, TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

from services.pdf_luxury_theme import (
    GOLD_HEX, CREAM_HEX, LAVENDER_HEX,
)
from services.pdf_theme import GOLD, CREAM, LAVENDER, MUTED, font
from services import library_images as libimg

MUTED_HEX      = '#9E9AA8'


# ═══════════════════════════════════════════════════════════════════
# FRONT MATTER
# ═══════════════════════════════════════════════════════════════════

def half_title_page(story, styles, book_title: str = 'Thème Natal') -> None:
    """Faux-titre minimaliste : juste le titre au centre, sur fond nuit.
    Convention édition : deuxième feuillet après la couverture."""
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦</font>',
        ParagraphStyle('ht_star', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=28, alignment=TA_CENTER, spaceAfter=30),
    ))
    story.append(Paragraph(
        book_title,
        ParagraphStyle('ht_title', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=42, textColor=CREAM, alignment=TA_CENTER,
                       leading=48, spaceAfter=20),
    ))
    story.append(Paragraph(
        'Plume Astrale',
        ParagraphStyle('ht_pub', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER,
                       spaceAfter=8),
    ))
    story.append(PageBreak())


def copyright_page(story, styles, prenom: str, birth_date_fr: str) -> None:
    """Page copyright + éphéméride personnelle. Petit texte centré en bas."""
    story.append(Spacer(1, 20 * cm))
    story.append(Paragraph(
        f'Écrit sous les étoiles pour {prenom}, née le {birth_date_fr}.',
        ParagraphStyle('cr_line', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=12, textColor=LAVENDER, alignment=TA_CENTER,
                       leading=18, spaceAfter=30),
    ))
    story.append(Paragraph(
        '© Plume Astrale — Éditions du Ciel Intérieur',
        ParagraphStyle('cr_pub', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=9, textColor=MUTED, alignment=TA_CENTER,
                       spaceAfter=4),
    ))
    story.append(Paragraph(
        'Tous droits réservés. Nulle partie de ce grimoire ne peut être reproduite<br/>'
        'ni transmise sans le consentement écrit de son autrice-oracle.',
        ParagraphStyle('cr_notice', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=8, textColor=MUTED, alignment=TA_CENTER, leading=12),
    ))
    story.append(Paragraph(
        'plume-astrale.fr',
        ParagraphStyle('cr_url', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=8, textColor=GOLD, alignment=TA_CENTER, spaceBefore=20),
    ))
    story.append(PageBreak())


def dedication_page(story, styles, prenom: str, dedication_text: Optional[str] = None) -> None:
    """Dédicace personnalisée signée Soléna."""
    text = dedication_text or (
        f'Pour toi, {prenom} —<br/>'
        f'qui as ouvert ce grimoire ce soir<br/>'
        f'et qui vas t\'y trouver.<br/><br/>'
        f'Puissent ces pages t\'être un miroir<br/>'
        f'et non un tribunal.'
    )
    story.append(Spacer(1, 9 * cm))
    story.append(Paragraph(
        text,
        ParagraphStyle('ded', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=17, textColor=CREAM, alignment=TA_CENTER,
                       leading=28, spaceAfter=40),
    ))
    story.append(Paragraph(
        '— Soléna',
        ParagraphStyle('ded_sign', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER),
    ))
    story.append(PageBreak())


def table_of_contents_page(story, styles, entries: List[Dict[str, Any]]) -> None:
    """Table des matières formatée à la manière d'un livre relié.

    entries = liste de dicts { 'type': 'part'|'chapter', 'label': str, 'page': int? }.
    Les 'part' sont en Cinzel doré, les 'chapter' en Cormorant crème.
    """
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦</font>  TABLE DES MATIÈRES  <font color="{GOLD_HEX}">✦</font>',
        ParagraphStyle('toc_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=14, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=30, letterSpacing=2),
    ))
    for e in entries:
        etype = e.get('type', 'chapter')
        label = e.get('label', '')
        if etype == 'part':
            story.append(Spacer(1, 0.5 * cm))
            story.append(Paragraph(
                f'<font color="{GOLD_HEX}">{label.upper()}</font>',
                ParagraphStyle(f'toc_p_{label}', fontName=font('Cinzel', 'Helvetica'),
                               fontSize=11, alignment=TA_LEFT, leading=18,
                               leftIndent=1.5 * cm, spaceAfter=6),
            ))
        else:
            story.append(Paragraph(
                f'<font color="{CREAM_HEX}">{label}</font>',
                ParagraphStyle(f'toc_c_{label}', fontName=font('Cormorant Garamond', 'Times-Roman'),
                               fontSize=12, alignment=TA_LEFT, leading=18,
                               leftIndent=2.5 * cm, spaceAfter=4),
            ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# DIVISEURS DE PARTIES
# ═══════════════════════════════════════════════════════════════════

def part_divider_page(story, styles, part_roman: str, part_title: str,
                       subtitle: Optional[str] = None,
                       illustration_local_path: Optional[str] = None) -> None:
    """Grande page d'ouverture de partie (Partie II, III...) avec numéro romain doré,
    titre en Cormorant, sous-titre italique, illustration ronde en dessous."""
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">PARTIE {part_roman}</font>',
        ParagraphStyle('pd_num', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=13, alignment=TA_CENTER, spaceAfter=18,
                       letterSpacing=4),
    ))
    story.append(Paragraph(
        part_title,
        ParagraphStyle('pd_t', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=34, textColor=CREAM, alignment=TA_CENTER,
                       leading=40, spaceAfter=14),
    ))
    if subtitle:
        story.append(Paragraph(
            subtitle,
            ParagraphStyle('pd_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=14, textColor=LAVENDER, alignment=TA_CENTER,
                           leading=22, spaceAfter=32),
        ))
    if illustration_local_path and os.path.exists(illustration_local_path):
        try:
            story.append(RLImage(illustration_local_path, width=7 * cm, height=7 * cm, mask='auto'))
        except Exception:
            pass
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# PARTIE I — FONDATIONS (éléments & modalités)
# ═══════════════════════════════════════════════════════════════════

_ELEMENT_META = {
    'Feu':   {'signs': ('Bélier', 'Lion', 'Sagittaire'),  'tarot': 'soleil', 'color': '#E85D3B'},
    'Terre': {'signs': ('Taureau', 'Vierge', 'Capricorne'), 'tarot': 'imperatrice', 'color': '#8B6B3D'},
    'Air':   {'signs': ('Gémeaux', 'Balance', 'Verseau'),  'tarot': 'etoile', 'color': '#8FA3C7'},
    'Eau':   {'signs': ('Cancer', 'Scorpion', 'Poissons'), 'tarot': 'lune', 'color': '#4C6D8E'},
}
_MODALITY_META = {
    'Cardinal': {'signs': ('Bélier', 'Cancer', 'Balance', 'Capricorne'),
                 'tarot': 'chariot', 'accent': 'Élan d\'initiative — tu ouvres les portes'},
    'Fixe':     {'signs': ('Taureau', 'Lion', 'Scorpion', 'Verseau'),
                 'tarot': 'force', 'accent': 'Solidité d\'ancrage — tu tiens la ligne'},
    'Mutable':  {'signs': ('Gémeaux', 'Vierge', 'Sagittaire', 'Poissons'),
                 'tarot': 'pendu', 'accent': 'Grâce d\'adaptation — tu épouses les courants'},
}


def element_dominant_page(story, styles, dominant_element: str, planet_count: int,
                           body_html: str) -> None:
    """Page dédiée à l'élément dominant du thème (Feu/Terre/Air/Eau)."""
    meta = _ELEMENT_META.get(dominant_element, _ELEMENT_META['Feu'])
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ TON ÉLÉMENT DOMINANT ✦</font>',
        ParagraphStyle('el_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        dominant_element.upper(),
        ParagraphStyle('el_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=32, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=8, letterSpacing=4),
    ))
    story.append(Paragraph(
        f'{planet_count} planètes en signe de {dominant_element.lower()}',
        ParagraphStyle('el_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=12, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=20),
    ))
    img = libimg.tarot(meta['tarot'], size=1080)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4.5 * cm, height=4.5 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('el_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, spaceAfter=8, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


def modality_dominant_page(story, styles, dominant_modality: str, planet_count: int,
                            body_html: str) -> None:
    """Page dédiée à la modalité dominante (Cardinal/Fixe/Mutable)."""
    meta = _MODALITY_META.get(dominant_modality, _MODALITY_META['Cardinal'])
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ TA MODALITÉ DOMINANTE ✦</font>',
        ParagraphStyle('md_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        dominant_modality.upper(),
        ParagraphStyle('md_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=32, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=8, letterSpacing=4),
    ))
    story.append(Paragraph(
        meta['accent'],
        ParagraphStyle('md_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=13, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=20),
    ))
    img = libimg.tarot(meta['tarot'], size=1080)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4.5 * cm, height=4.5 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('md_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# PARTIE II — ANALYSE CROISÉE TRIO IDENTITAIRE
# ═══════════════════════════════════════════════════════════════════

def trio_cross_analysis_page(story, styles, sun_sign: str, moon_sign: str,
                              asc_sign: str, body_html: str) -> None:
    """Analyse croisée Soleil-Lune-Ascendant : la trinité identitaire.
    Trois mini-images alignées en haut, texte d'analyse profonde en dessous."""
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ TON TRIANGLE INTIME ✦</font>',
        ParagraphStyle('tc_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=10, letterSpacing=3),
    ))
    story.append(Paragraph(
        'Soleil × Lune × Ascendant',
        ParagraphStyle('tc_h', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=22, textColor=CREAM, alignment=TA_CENTER, spaceAfter=20),
    ))
    # Grille de 3 mini-images en ligne
    sun_img = libimg.planet('Soleil', size=1080)
    moon_img = libimg.planet('Lune', size=1080)
    asc_img = libimg.sign(asc_sign, size=1080) if asc_sign else None
    cells = []
    for img, label, subl in [
        (sun_img, 'Soleil', sun_sign),
        (moon_img, 'Lune', moon_sign),
        (asc_img, 'Ascendant', asc_sign),
    ]:
        content = []
        if img and os.path.exists(img):
            try:
                content.append(RLImage(img, width=3.5 * cm, height=3.5 * cm, mask='auto'))
            except Exception:
                pass
        content.append(Paragraph(label,
            ParagraphStyle(f'tc_l_{label}', fontName=font('Cinzel', 'Helvetica'),
                           fontSize=10, textColor=CREAM, alignment=TA_CENTER, spaceBefore=6)))
        content.append(Paragraph(subl or '—',
            ParagraphStyle(f'tc_s_{label}', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=11, textColor=GOLD, alignment=TA_CENTER)))
        cells.append(content)
    tbl = Table([cells], colWidths=[5.5 * cm] * 3, hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        body_html,
        ParagraphStyle('tc_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=11.5, textColor=CREAM, alignment=TA_LEFT,
                       leading=17, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# PARTIE IV — ASPECTS DÉTAILLÉS
# ═══════════════════════════════════════════════════════════════════

def aspects_group_page(story, styles, category: str, headline: str,
                        body_html: str, tarot_slug: str = 'amoureux') -> None:
    """Page pour un groupe d'aspects (harmonieux / tensions / rare).

    category = tag en petit doré, headline = titre H1, body = texte long.
    tarot_slug alimente une petite image ronde évocatrice.
    """
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ {category.upper()} ✦</font>',
        ParagraphStyle('ag_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=12, letterSpacing=3),
    ))
    story.append(Paragraph(
        headline,
        ParagraphStyle('ag_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=24, textColor=CREAM, alignment=TA_CENTER,
                       leading=30, spaceAfter=18),
    ))
    img = libimg.tarot(tarot_slug, size=1080)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4 * cm, height=4 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('ag_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# PARTIE V — MAISONS ASTROLOGIQUES
# ═══════════════════════════════════════════════════════════════════

_HOUSE_THEMES = {
    1:  'L\'incarnation — Comment tu apparais au monde',
    2:  'Les ressources — Ce que tu possèdes et ce que tu vaux',
    3:  'La parole — Comment tu penses et communiques',
    4:  'Le foyer — Tes racines, ta famille intime',
    5:  'La création — Ce que tu offres au monde par joie',
    6:  'Le service — Ton quotidien, ta santé, tes rituels',
    7:  'L\'autre — Tes partenariats amoureux et professionnels',
    8:  'La transformation — Sexualité, mort, ressources partagées',
    9:  'L\'horizon — Voyage, philosophie, sens de la vie',
    10: 'L\'accomplissement — Ta réputation, ta carrière, ton legs',
    11: 'La tribu — Amitiés, communautés, projections d\'avenir',
    12: 'Le mystère — L\'invisible, l\'inconscient, la retraite',
}


def house_detail_page(story, styles, house_num: int, sign: str,
                       planets_in_house: List[str], body_html: str) -> None:
    """Une maison astrologique — signe qui l'occupe + planètes présentes + analyse.

    Cite l'image de la maison (libimg.house(n)) si disponible.
    """
    theme = _HOUSE_THEMES.get(house_num, '')
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">MAISON {house_num}</font>',
        ParagraphStyle('h_num', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, alignment=TA_CENTER, spaceAfter=6, letterSpacing=4),
    ))
    story.append(Paragraph(
        theme,
        ParagraphStyle('h_theme', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=18, textColor=CREAM, alignment=TA_CENTER,
                       leading=24, spaceAfter=10),
    ))
    if sign:
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">Cuspide en {sign}</font>' + (
                f' · {", ".join(planets_in_house)}' if planets_in_house else ''),
            ParagraphStyle('h_cusp', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=11, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=14),
        ))
    img = libimg.house(house_num, size=1080)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4.2 * cm, height=4.2 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('h_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=11.5, textColor=CREAM, alignment=TA_LEFT,
                       leading=17, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# ÉPILOGUE
# ═══════════════════════════════════════════════════════════════════

def year_ahead_page(story, styles, prenom: str, body_html: str) -> None:
    """Épilogue orienté 12 prochains mois — transits majeurs à venir."""
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦ TON ANNÉE À VENIR ✦</font>',
        ParagraphStyle('ya_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        f'{prenom}, sous les prochaines lunes',
        ParagraphStyle('ya_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=26, textColor=CREAM, alignment=TA_CENTER,
                       leading=32, spaceAfter=20),
    ))
    img = libimg.tarot('etoile', size=1080)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4.5 * cm, height=4.5 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('ya_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


def colophon_page(story, styles, prenom: str, referral_code: Optional[str] = None,
                   referral_link: Optional[str] = None) -> None:
    """Dernier feuillet : signature Soléna + code parrainage discret."""
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">✦</font>',
        ParagraphStyle('col_star', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=22, alignment=TA_CENTER, spaceAfter=24),
    ))
    story.append(Paragraph(
        f'Merci, {prenom}.',
        ParagraphStyle('col_thanks', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=22, textColor=CREAM, alignment=TA_CENTER,
                       leading=28, spaceAfter=14),
    ))
    story.append(Paragraph(
        'Que ces pages voyagent avec toi<br/>comme un feu doux dans ta poche.',
        ParagraphStyle('col_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=13, textColor=LAVENDER, alignment=TA_CENTER,
                       leading=20, spaceAfter=40),
    ))
    if referral_code and referral_link:
        story.append(Paragraph(
            f'<font color="{GOLD_HEX}">Offre à un proche</font>',
            ParagraphStyle('col_ref_tag', fontName=font('Cinzel', 'Helvetica'),
                           fontSize=9, alignment=TA_CENTER, spaceAfter=8, letterSpacing=3),
        ))
        story.append(Paragraph(
            f'Ton code personnel de parrainage : <b>{referral_code}</b>',
            ParagraphStyle('col_ref_code', fontName=font('Cormorant Garamond', 'Times-Roman'),
                           fontSize=11, textColor=CREAM, alignment=TA_CENTER, spaceAfter=4),
        ))
        story.append(Paragraph(
            f'<font color="{MUTED_HEX}">{referral_link}</font>',
            ParagraphStyle('col_ref_link', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=9, alignment=TA_CENTER, spaceAfter=30),
        ))
    story.append(Paragraph(
        '— Soléna, ton oracle numérique<br/>Plume Astrale · plume-astrale.fr',
        ParagraphStyle('col_sig', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=9, textColor=GOLD, alignment=TA_CENTER, spaceBefore=20, letterSpacing=2),
    ))
