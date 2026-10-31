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
    GOLD_HEX, CREAM_HEX,
)
from services.pdf_theme import GOLD, CREAM, LAVENDER, MUTED, font
from services import library_images as libimg

MUTED_HEX      = '#9E9AA8'


def _star(color_hex: str = GOLD_HEX) -> str:
    """Retourne un glyphe ✦ rendu avec la police OrnamentSerif (évite les tofu).
    À utiliser dans tout Paragraph dont le fontName est Cinzel/Cormorant."""
    return f'<font name="{font("OrnamentSerif", "Helvetica")}" color="{color_hex}">✦</font>'


# ═══════════════════════════════════════════════════════════════════
# FRONT MATTER
# ═══════════════════════════════════════════════════════════════════

def half_title_page(story, styles, book_title: str = 'Thème Natal') -> None:
    """Faux-titre minimaliste : juste le titre au centre, sur fond nuit.
    Convention édition : deuxième feuillet après la couverture."""
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph(
        _star(),
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


def dedication_page(story, styles, prenom: str, dedication_text: Optional[str] = None,
                    signature: str = 'Soléna') -> None:
    """Dédicace personnalisée — signature paramétrable (Thème Natal → Plume Astrale)."""
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
        f'— {signature}',
        ParagraphStyle('ded_sign', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=GOLD, alignment=TA_CENTER),
    ))
    story.append(PageBreak())


def table_of_contents_page(story, styles, entries: List[Dict[str, Any]]) -> None:
    """Table des matières formatée à la manière d'un livre relié.

    entries = liste de dicts :
      { 'type': 'part'|'chapter', 'label': str, 'page': int? (optionnel) }
    Les 'part' sont en Cinzel doré, les 'chapter' en Cormorant crème.
    Si 'page' est présent, un feuillet de points menant au numéro de page est ajouté.
    """
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        f'<font name="{font("OrnamentSerif", "Helvetica")}" color="{GOLD_HEX}">✦</font>  TABLE DES MATIÈRES  <font name="{font("OrnamentSerif", "Helvetica")}" color="{GOLD_HEX}">✦</font>',
        ParagraphStyle('toc_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=14, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=30, letterSpacing=2),
    ))
    for e in entries:
        etype = e.get('type', 'chapter')
        label = e.get('label', '')
        page = e.get('page')
        if etype == 'part':
            story.append(Spacer(1, 0.5 * cm))
            page_html = (f'&nbsp;&nbsp;<font color="{GOLD_HEX}">{page}</font>'
                         if page is not None else '')
            story.append(Paragraph(
                f'<font color="{GOLD_HEX}">{label.upper()}</font>{page_html}',
                ParagraphStyle(f'toc_p_{label}', fontName=font('Cinzel', 'Helvetica'),
                               fontSize=11, alignment=TA_LEFT, leading=18,
                               leftIndent=1.5 * cm, spaceAfter=6),
            ))
        else:
            if page is not None:
                # Chapitre avec pointillés menant au numéro de page (façon livre)
                inner = (
                    f'<font color="{CREAM_HEX}">{label}</font>'
                    f'&nbsp;&nbsp;<font color="#8B7A32">···········</font>&nbsp;&nbsp;'
                    f'<font color="{GOLD_HEX}">{page}</font>'
                )
            else:
                inner = f'<font color="{CREAM_HEX}">{label}</font>'
            story.append(Paragraph(
                inner,
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
        f'{_star()} TON ÉLÉMENT DOMINANT {_star()}',
        ParagraphStyle('el_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        dominant_element.upper(),
        ParagraphStyle('el_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=32, leading=40, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=18, letterSpacing=4),
    ))
    story.append(Paragraph(
        f'{planet_count} planètes en signe de {dominant_element.lower()}',
        ParagraphStyle('el_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=12, leading=15, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=20),
    ))
    img = libimg.tarot(meta['tarot'], size=512)
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
        f'{_star()} TA MODALITÉ DOMINANTE {_star()}',
        ParagraphStyle('md_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        dominant_modality.upper(),
        ParagraphStyle('md_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=32, leading=40, textColor=CREAM, alignment=TA_CENTER,
                       spaceAfter=18, letterSpacing=4),
    ))
    story.append(Paragraph(
        meta['accent'],
        ParagraphStyle('md_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=13, leading=16, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=20),
    ))
    img = libimg.tarot(meta['tarot'], size=512)
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
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        f'{_star()} TON TRIANGLE INTIME {_star()}',
        ParagraphStyle('tc_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=8, letterSpacing=3),
    ))
    story.append(Paragraph(
        'Soleil × Lune × Ascendant',
        ParagraphStyle('tc_h', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=20, leading=24, textColor=CREAM, alignment=TA_CENTER, spaceAfter=14),
    ))
    # Grille de 3 mini-images en ligne
    sun_img = libimg.planet('Soleil', size=512)
    moon_img = libimg.planet('Lune', size=512)
    asc_img = libimg.sign(asc_sign, size=512) if asc_sign else None
    cells = []
    for img, label, subl in [
        (sun_img, 'Soleil', sun_sign),
        (moon_img, 'Lune', moon_sign),
        (asc_img, 'Ascendant', asc_sign),
    ]:
        content = []
        if img and os.path.exists(img):
            try:
                content.append(RLImage(img, width=3 * cm, height=3 * cm, mask='auto'))
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
    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph(
        body_html,
        ParagraphStyle('tc_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=11, textColor=CREAM, alignment=TA_LEFT,
                       leading=15, leftIndent=1.2 * cm, rightIndent=1.2 * cm, spaceAfter=4),
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
        f'{_star()} {category.upper()} {_star()}',
        ParagraphStyle('ag_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=12, letterSpacing=3),
    ))
    story.append(Paragraph(
        headline,
        ParagraphStyle('ag_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=24, textColor=CREAM, alignment=TA_CENTER,
                       leading=30, spaceAfter=18),
    ))
    img = libimg.tarot(tarot_slug, size=512)
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
    # Refonte Feb 2026 — colonne vertébrale 50 pages : chaque groupe d'aspects
    # occupe sa propre page, pour une numérotation stable et des titres jamais
    # orphelins. L'ornement reste comme signature visuelle de fin de bloc.
    from services.pdf_luxury_theme import _append_section_ornament
    _append_section_ornament(story, f'aspects_{category}')
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
    img = libimg.house(house_num, size=512)
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
    # Refactor 2026-02-26 : plus de PageBreak forcé → les 12 maisons s'enchaînent
    # comme un chapitre de livre, séparées par un ornement.
    from services.pdf_luxury_theme import _append_section_ornament
    _append_section_ornament(story, f'house_{house_num}')
    # Refonte Feb 2026 — chaque maison occupe sa propre page (p.27–36).
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════
# ÉPILOGUE
# ═══════════════════════════════════════════════════════════════════

def year_ahead_page(story, styles, prenom: str, body_html: str) -> None:
    """Épilogue orienté 12 prochains mois — transits majeurs à venir."""
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(
        f'{_star()} TON ANNÉE À VENIR {_star()}',
        ParagraphStyle('ya_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        f'{prenom}, sous les prochaines lunes',
        ParagraphStyle('ya_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=26, textColor=CREAM, alignment=TA_CENTER,
                       leading=32, spaceAfter=20),
    ))
    img = libimg.tarot('etoile', size=512)
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


# ═══════════════════════════════════════════════════════════════════
# NOUVELLES PAGES — Refonte "Thème Natal 50 pages" (Lot 2 — Feb 2026)
# ═══════════════════════════════════════════════════════════════════

_SIGN_ELEMENT = {
    'Bélier': 'Feu', 'Lion': 'Feu', 'Sagittaire': 'Feu',
    'Taureau': 'Terre', 'Vierge': 'Terre', 'Capricorne': 'Terre',
    'Gémeaux': 'Air', 'Balance': 'Air', 'Verseau': 'Air',
    'Cancer': 'Eau', 'Scorpion': 'Eau', 'Poissons': 'Eau',
}


def method_intro_page(story, styles, prenom: str) -> None:
    """Page 4 — Comment lire ce livre (méthode courte + intro).

    Tient sur une page avec le sommaire généré via `table_of_contents_page`
    appelé AVANT. C'est la page qui ouvre la lecture avant le vrai contenu.
    """
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph(
        f'{_star()} COMMENT LIRE CE LIVRE {_star()}',
        ParagraphStyle('mi_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=18, letterSpacing=3),
    ))
    story.append(Paragraph(
        f'Un mode d\'emploi tendre, {prenom}.',
        ParagraphStyle('mi_h', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=18, textColor=LAVENDER, alignment=TA_CENTER,
                       leading=24, spaceAfter=22),
    ))
    for para in (
        "Ce livre est composé à partir de ton ciel de naissance. "
        "Il propose une lecture symbolique et personnelle, à confronter à ton expérience. "
        "Il ne prédit pas un avenir certain et ne remplace pas ta liberté de choix.",
        "La structure se lit comme un vrai livre : d'abord les fondations (ta roue, ton trio Soleil-Lune-Ascendant, "
        "ton élément et ta modalité dominants), puis le détail planète par planète, maison par maison, aspect par aspect. "
        "Prends le temps : chaque page a été écrite pour être relue, soulignée, méditée.",
        "Si une interprétation ne te parle pas, laisse-la. "
        "Tu restes la personne la mieux placée pour donner du sens à ton vécu.",
    ):
        story.append(Paragraph(
            para,
            ParagraphStyle('mi_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                           fontSize=11.5, textColor=CREAM, alignment=TA_LEFT,
                           leading=17, leftIndent=1.5 * cm, rightIndent=1.5 * cm,
                           spaceAfter=10),
        ))
    story.append(PageBreak())


def birth_data_page(story, styles, prenom: str, birth_date_fr: str,
                     birth_time_fr: Optional[str], birth_place: Optional[str],
                     sun_sign: str, moon_sign: str, asc_sign: str,
                     planet_count: int, aspect_count: int, house_count: int,
                     dominant_element: Optional[str] = None,
                     dominant_modality: Optional[str] = None) -> None:
    """Page 5 — Données de naissance (date, heure, lieu + signatures + stats)."""
    story.append(Spacer(1, 1.3 * cm))
    story.append(Paragraph(
        f'{_star()} TES DONNÉES DE NAISSANCE {_star()}',
        ParagraphStyle('bd_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=18, letterSpacing=3),
    ))
    story.append(Paragraph(
        prenom,
        ParagraphStyle('bd_name', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=28, textColor=CREAM, alignment=TA_CENTER,
                       leading=34, spaceAfter=24),
    ))
    rows: list[list[str]] = []
    if birth_date_fr:
        rows.append(['Date', birth_date_fr])
    if birth_time_fr:
        rows.append(['Heure', birth_time_fr])
    if birth_place:
        rows.append(['Lieu', birth_place])
    if sun_sign:
        rows.append(['Soleil', sun_sign])
    if moon_sign:
        rows.append(['Lune', moon_sign])
    if asc_sign:
        rows.append(['Ascendant', asc_sign])
    if dominant_element:
        rows.append(['Élément dominant', dominant_element])
    if dominant_modality:
        rows.append(['Modalité dominante', dominant_modality])
    rows.append(['Planètes commentées', str(planet_count)])
    if aspect_count:
        rows.append(['Aspects majeurs', str(aspect_count)])
    if house_count:
        rows.append(['Maisons actives', str(house_count)])

    label_style = ParagraphStyle('bd_lab', fontName=font('Cinzel', 'Helvetica'),
                                  fontSize=9, textColor=GOLD, alignment=TA_LEFT, letterSpacing=2)
    value_style = ParagraphStyle('bd_val', fontName=font('Cormorant Garamond', 'Times-Roman'),
                                  fontSize=12, textColor=CREAM, alignment=TA_LEFT, leading=16)
    cells = [[Paragraph(lab.upper(), label_style), Paragraph(val, value_style)] for lab, val in rows]
    tbl = Table(cells, colWidths=[4.8 * cm, 9 * cm], hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, HexColor('#5c4e26')),
    ]))
    story.append(tbl)
    story.append(PageBreak())


def chart_legend_page(story, styles) -> None:
    """Page 7 — Légende de la roue : symboles planétaires, signes, aspects.

    Permet au lecteur de décoder la carte du ciel qui précède.
    """
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'{_star()} LA LÉGENDE DE TA ROUE {_star()}',
        ParagraphStyle('cl_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        'Les symboles qui dansent sur ta carte',
        ParagraphStyle('cl_h', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=15, textColor=LAVENDER, alignment=TA_CENTER,
                       leading=20, spaceAfter=18),
    ))
    sym_style = ParagraphStyle('cl_sym', fontName=font('OrnamentSerif', 'Helvetica'),
                                fontSize=14, textColor=GOLD, alignment=TA_CENTER)
    lab_style = ParagraphStyle('cl_lab', fontName=font('Cinzel', 'Helvetica'),
                                fontSize=9, textColor=CREAM, alignment=TA_LEFT, letterSpacing=1)
    desc_style = ParagraphStyle('cl_desc', fontName=font('Cormorant Garamond', 'Times-Roman'),
                                 fontSize=10, textColor=CREAM, alignment=TA_LEFT, leading=14)
    sections = [
        ('Les planètes', [
            ('☉', 'Soleil', 'ton identité, ta volonté'),
            ('☽', 'Lune', 'tes émotions, ta sensibilité'),
            ('☿', 'Mercure', 'ta pensée, ta parole'),
            ('♀', 'Vénus', 'tes amours, tes goûts'),
            ('♂', 'Mars', 'ton action, tes désirs'),
            ('♃', 'Jupiter', 'ton expansion, ta chance'),
            ('♄', 'Saturne', 'ta discipline, tes limites'),
            ('♅', 'Uranus', 'tes ruptures, tes libérations'),
            ('♆', 'Neptune', 'tes rêves, ton inspiration'),
            ('♇', 'Pluton', 'tes transformations profondes'),
        ]),
        ('Les aspects', [
            ('☌', 'Conjonction', 'fusion — deux planètes jouent la même note'),
            ('☍', 'Opposition', 'tension — polarité à équilibrer'),
            ('△', 'Trigone', 'harmonie — talent qui circule sans effort'),
            ('□', 'Carré', 'friction — moteur de croissance'),
            ('⚹', 'Sextile', 'opportunité — à saisir sans forcer'),
        ]),
    ]
    for title, items in sections:
        story.append(Paragraph(
            title,
            ParagraphStyle(f'cl_s_{title}', fontName=font('Cinzel', 'Helvetica'),
                           fontSize=11, textColor=GOLD, alignment=TA_LEFT,
                           letterSpacing=2, leftIndent=1.2 * cm, spaceBefore=8, spaceAfter=6),
        ))
        rows = []
        for sym, label, desc in items:
            rows.append([
                Paragraph(sym, sym_style),
                Paragraph(label.upper(), lab_style),
                Paragraph(desc, desc_style),
            ])
        tbl = Table(rows, colWidths=[1.2 * cm, 3.2 * cm, 9.2 * cm], hAlign='CENTER')
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(tbl)
    story.append(PageBreak())


def personal_synthesis_page(story, styles, prenom: str, sun_sign: str,
                             moon_sign: str, asc_sign: str,
                             dominant_element: Optional[str],
                             dominant_modality: Optional[str],
                             aspect_count: int, active_house_count: int,
                             synthese_text: Optional[str] = None) -> None:
    """Page 8 — Synthèse personnelle courte : les grandes signatures en un regard."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'{_star()} TA SYNTHÈSE PERSONNELLE {_star()}',
        ParagraphStyle('ps_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        f'{prenom}, en un seul regard',
        ParagraphStyle('ps_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=22, textColor=CREAM, alignment=TA_CENTER,
                       leading=28, spaceAfter=16),
    ))
    phrases: list[str] = []
    if sun_sign:
        phrases.append(f'Soleil en <font color="{GOLD_HEX}">{sun_sign}</font> — ton identité.')
    if moon_sign:
        phrases.append(f'Lune en <font color="{GOLD_HEX}">{moon_sign}</font> — ton monde intérieur.')
    if asc_sign:
        phrases.append(f'Ascendant en <font color="{GOLD_HEX}">{asc_sign}</font> — ton masque.')
    if dominant_element:
        phrases.append(f'Élément dominant : <font color="{GOLD_HEX}">{dominant_element}</font>.')
    if dominant_modality:
        phrases.append(f'Modalité dominante : <font color="{GOLD_HEX}">{dominant_modality}</font>.')
    if aspect_count:
        phrases.append(f'<font color="{GOLD_HEX}">{aspect_count}</font> aspects majeurs entre tes planètes.')
    if active_house_count:
        phrases.append(f'<font color="{GOLD_HEX}">{active_house_count}</font> des douze maisons accueillent au moins une planète.')
    for p in phrases:
        story.append(Paragraph(
            p,
            ParagraphStyle(f'ps_line_{len(story)}', fontName=font('Cormorant Garamond', 'Times-Roman'),
                           fontSize=12.5, textColor=CREAM, alignment=TA_LEFT,
                           leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm, spaceAfter=4),
        ))
    if synthese_text:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            synthese_text,
            ParagraphStyle('ps_body', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=11, textColor=LAVENDER, alignment=TA_LEFT,
                           leading=16, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
        ))
    story.append(PageBreak())


def transversal_synthesis_page(story, styles, title: str, kicker: str,
                                body_html: str, tarot_slug: str = 'etoile') -> None:
    """Pages 45-48 — synthèse transversale (4 axes : relations/activité/ressources/tensions)."""
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        f'{_star()} SYNTHÈSE TRANSVERSALE {_star()}',
        ParagraphStyle('ts_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=10, letterSpacing=3),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('ts_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=22, textColor=CREAM, alignment=TA_CENTER,
                       leading=28, spaceAfter=6),
    ))
    if kicker:
        story.append(Paragraph(
            kicker,
            ParagraphStyle('ts_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=12, textColor=LAVENDER, alignment=TA_CENTER, spaceAfter=16),
        ))
    img = libimg.tarot(tarot_slug, size=512)
    if img and os.path.exists(img):
        try:
            story.append(RLImage(img, width=4 * cm, height=4 * cm, mask='auto'))
            story.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    story.append(Paragraph(
        body_html,
        ParagraphStyle('ts_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


def conclusion_page(story, styles, prenom: str, body_html: str) -> None:
    """Page 49 — Conclusion complète (fin émotionnelle développée)."""
    story.append(Spacer(1, 1.3 * cm))
    story.append(Paragraph(
        f'{_star()} CONCLUSION {_star()}',
        ParagraphStyle('cc_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    story.append(Paragraph(
        f'{prenom}, ton livre te laisse sur ce seuil',
        ParagraphStyle('cc_h', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=20, textColor=CREAM, alignment=TA_CENTER,
                       leading=26, spaceAfter=20),
    ))
    story.append(Paragraph(
        body_html,
        ParagraphStyle('cc_body', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=12, textColor=CREAM, alignment=TA_LEFT,
                       leading=18, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


def glossary_technical_page(story, styles) -> None:
    """Page 50 — Glossaire court + repères techniques (orbes, maisons, aspects)."""
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f'{_star()} GLOSSAIRE & REPÈRES TECHNIQUES {_star()}',
        ParagraphStyle('gl_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=14, letterSpacing=3),
    ))
    term_style = ParagraphStyle('gl_term', fontName=font('Cinzel', 'Helvetica'),
                                 fontSize=9, textColor=GOLD, alignment=TA_LEFT, letterSpacing=1)
    def_style = ParagraphStyle('gl_def', fontName=font('Cormorant Garamond', 'Times-Roman'),
                                fontSize=10, textColor=CREAM, alignment=TA_LEFT, leading=14)
    story.append(Paragraph(
        'Glossaire',
        ParagraphStyle('gl_s1', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=CREAM, alignment=TA_LEFT,
                       letterSpacing=2, leftIndent=1.2 * cm, spaceAfter=6),
    ))
    glossary = [
        ('ASCENDANT', 'signe qui se levait à l\'horizon est à l\'instant de ta naissance ; ton masque social.'),
        ('CUSPIDE', 'frontière entre deux maisons astrologiques.'),
        ('MAISON', 'secteur de 30° (en moyenne) qui situe où une planète s\'incarne dans ta vie.'),
        ('ORBE', 'tolérance en degrés dans la mesure d\'un aspect ; plus l\'orbe est faible, plus l\'aspect est net.'),
        ('RÉTROGRADE', 'planète en mouvement apparent inversé ; son énergie se tourne vers l\'intérieur.'),
        ('TRANSIT', 'passage d\'une planète actuelle devant un point de ta carte natale.'),
    ]
    rows = [[Paragraph(t, term_style), Paragraph(d, def_style)] for t, d in glossary]
    tbl = Table(rows, colWidths=[3.5 * cm, 10.5 * cm], hAlign='CENTER')
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        'Repères techniques',
        ParagraphStyle('gl_s2', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=11, textColor=CREAM, alignment=TA_LEFT,
                       letterSpacing=2, leftIndent=1.2 * cm, spaceAfter=6),
    ))
    tech_lines = (
        'Les positions planétaires sont calculées à partir de l\'heure et du lieu que tu as fournis, '
        'avec les éphémérides suisses. Les maisons sont tracées selon le système Placidus. '
        'Les aspects majeurs sont retenus dans leur orbe classique : 8° pour la conjonction et l\'opposition, '
        '6° pour le trigone et le carré, 4° pour le sextile. '
        'Les signes du zodiaque sont tropicaux (relatifs aux saisons terrestres, non aux constellations).'
    )
    story.append(Paragraph(
        tech_lines,
        ParagraphStyle('gl_tech', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=10.5, textColor=CREAM, alignment=TA_LEFT,
                       leading=15, leftIndent=1.5 * cm, rightIndent=1.5 * cm),
    ))
    story.append(PageBreak())


def aspects_opening_page(story, styles, aspects: List[Dict[str, Any]]) -> None:
    """Page d'ouverture de la Section 6 — table dense des aspects calculés.

    Rend la liste complète (planète A — type — planète B — orbe) comme table
    de référence avant les 3 pages d'interprétation thématique.
    """
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph(
        f'{_star()} TES ASPECTS CALCULÉS {_star()}',
        ParagraphStyle('ao_tag', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=10, alignment=TA_CENTER, spaceAfter=10, letterSpacing=3),
    ))
    story.append(Paragraph(
        'La table de tes dialogues célestes',
        ParagraphStyle('ao_h', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                       fontSize=15, textColor=LAVENDER, alignment=TA_CENTER,
                       leading=20, spaceAfter=14),
    ))
    if not aspects:
        story.append(Paragraph(
            'Aucun aspect majeur n\'a été calculé pour cette carte.',
            ParagraphStyle('ao_empty', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=11, textColor=MUTED, alignment=TA_CENTER),
        ))
        story.append(PageBreak())
        return
    header_style = ParagraphStyle('ao_hdr', fontName=font('Cinzel', 'Helvetica'),
                                   fontSize=8, textColor=GOLD, alignment=TA_LEFT, letterSpacing=1)
    cell_style = ParagraphStyle('ao_cell', fontName=font('Cormorant Garamond', 'Times-Roman'),
                                 fontSize=10, textColor=CREAM, alignment=TA_LEFT, leading=14)
    rows = [[Paragraph('PLANÈTE A', header_style),
             Paragraph('ASPECT', header_style),
             Paragraph('PLANÈTE B', header_style),
             Paragraph('ORBE', header_style)]]
    for a in aspects[:40]:  # cap at ~40 aspects to fit on page
        orb = a.get('orb_degrees')
        orb_txt = f'{orb:.2f}°'.replace('.', ',') if isinstance(orb, (int, float)) else '—'
        rows.append([
            Paragraph(a.get('planet_a', '—'), cell_style),
            Paragraph(a.get('type_fr', '—'), cell_style),
            Paragraph(a.get('planet_b', '—'), cell_style),
            Paragraph(orb_txt, cell_style),
        ])
    tbl = Table(rows, colWidths=[3.4 * cm, 3 * cm, 3.4 * cm, 2 * cm], hAlign='CENTER',
                 repeatRows=1)
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, 0), 0.4, HexColor(GOLD_HEX)),
        ('LINEBELOW', (0, 1), (-1, -2), 0.2, HexColor('#5c4e26')),
    ]))
    story.append(tbl)
    story.append(PageBreak())


def section_divider_page(story, styles, section_num: str, title: str,
                          subtitle: Optional[str] = None,
                          illustration_local_path: Optional[str] = None) -> None:
    """Diviseur de section (remplace part_divider_page) adapté à la nouvelle structure 8 sections."""
    story.append(Spacer(1, 3.5 * cm))
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}">SECTION {section_num}</font>',
        ParagraphStyle('sd_num', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=12, alignment=TA_CENTER, spaceAfter=18, letterSpacing=4),
    ))
    story.append(Paragraph(
        title,
        ParagraphStyle('sd_t', fontName=font('Cormorant Garamond', 'Times-Roman'),
                       fontSize=32, textColor=CREAM, alignment=TA_CENTER,
                       leading=38, spaceAfter=14),
    ))
    if subtitle:
        story.append(Paragraph(
            subtitle,
            ParagraphStyle('sd_s', fontName=font('Cormorant Garamond Italic', 'Times-Italic'),
                           fontSize=13, textColor=LAVENDER, alignment=TA_CENTER,
                           leading=20, spaceAfter=28),
        ))
    if illustration_local_path and os.path.exists(illustration_local_path):
        try:
            story.append(RLImage(illustration_local_path, width=6 * cm, height=6 * cm, mask='auto'))
        except Exception:
            pass
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════


def colophon_page(story, styles, prenom: str, referral_code: Optional[str] = None,
                   referral_link: Optional[str] = None, product_name: str = 'Ton Thème Natal',
                   signature: str = 'Soléna') -> None:
    """Dernier feuillet : délègue au colophon Nocturne partagé (QR code + citation).

    Historique 2026-02 → 2026-02-26 : remplacement de l'ancien colophon texte-only
    par le module `pdf_colophon` unifié (avec QR code, code letter-spaced, kicker
    éditorial) pour cohérence visuelle avec Karma, Numérologie, Voyage Karmique.

    Feb 2026 (§V audit marque) : `product_name` paramétrable pour distinguer
    l'édition standard de l'"Édition des Planètes" (sans ascendant, sans maisons).

    Feb 2026-02-27 : `signature` paramétrable — le Thème Natal passe
    "Plume Astrale" (la voix Soléna reste sur les autres produits).
    """
    from services.pdf_colophon import build_colophon
    # `styles` du natal book n'a pas les mêmes clés que celui de pdf_prestige,
    # mais build_colophon lit ses propres styles via pdf_theme — on passe {} en fallback.
    build_colophon(
        story, {}, prenom=prenom,
        referral_code=referral_code, referral_link=referral_link,
        product_name=product_name, signature=signature,
    )
