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
    Table, TableStyle, KeepTogether, CondPageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from services.pdf_theme import (
    register_fonts, make_styles, font,
    GOLD, GOLD_LIGHT, CREAM, LAVENDER, MUTED, NIGHT, NIGHT_SOFT, PALETTE,
)

# Enregistre les polices luxe (Cormorant + Cinzel + OrnamentSerif) au chargement
# du module → tout `<font name="OrnamentSerif">` inline dans les Paragraph est résolu.
register_fonts()

# Hex strings pour usage inline HTML `<font color="#..">`
GOLD_HEX       = '#79570F'
GOLD_LIGHT_HEX = '#8A6418'
CREAM_HEX      = '#26242B'
LAVENDER_HEX   = '#514657'
MUTED_HEX      = '#5E5A63'
NIGHT_HEX      = '#FFFFFF'
NIGHT_SOFT_HEX = '#F5F2EA'


SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
_ILLUS_BASE = f'{SUPABASE_URL}/storage/v1/object/public/library/pdf' if SUPABASE_URL else ''


def illustration_url(slug: str, size: int = 800) -> str:
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
#   FOND PRINT (papier blanc + cadre bronze discret)
# ═══════════════════════════════════════════════════════════

def luxury_bg(canvas, doc):
    """Fond blanc print, sans aplat sombre ni décor consommateur d'encre."""
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NIGHT)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # Filet bronze fin, imprimable sans aplat.
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.45)
    canvas.rect(1.2 * cm, 1.2 * cm, w - 2.4 * cm, h - 2.4 * cm, stroke=1, fill=0)
    # Soleil ornemental discret en haut
    if doc.page > 1:
        canvas.setFillColor(GOLD)
        canvas.setLineWidth(0.4)
        canvas.circle(w / 2, h - 1.55 * cm, 0.10 * cm, fill=1, stroke=0)
        canvas.line(w / 2 - 1.4 * cm, h - 1.55 * cm, w / 2 - 0.3 * cm, h - 1.55 * cm)
        canvas.line(w / 2 + 0.3 * cm, h - 1.55 * cm, w / 2 + 1.4 * cm, h - 1.55 * cm)
    # Footer éditorial
    if doc.page > 1:
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 6.5)
        canvas.drawString(2 * cm, 0.75 * cm, "PLUME ASTRALE · THÈME NATAL")
        canvas.drawRightString(w - 2 * cm, 0.75 * cm, f"— {doc.page} —")
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
                                       fontSize=18, leading=24, textColor=GOLD,
                                       alignment=TA_CENTER, spaceAfter=20),
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

def cover_page(story: list, styles: dict, prenom: str, subtitle: str, illustration_slug: str = 'ciel_zodiaque',
               sun_sign: str = None, birth_month: int = None):
    """Couverture pleine page : illustration cosmique + prénom + titre.

    Priorité (du plus personnel au plus générique) :
      1. sun_sign fourni → planète 3D personnalisée (planète maîtresse du signe)
         rendue dynamiquement (Lot 2 — Feb 2026).
      2. hero local /app/backend/assets/pdf_covers/natal_hero.png (palette V3 unifiée).
      3. Illustration cosmique distante par slug.

    Si `birth_month` est fourni (1-12), le fond étoilé de la planète est teinté
    selon la saison (hiver / printemps / été / automne) et une mention
    « ÉDITION {SAISON} » est ajoutée sous la planète (Lot 5 — Feb 2026).
    """
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph('<font name="OrnamentSerif">✦</font> PLUME ASTRALE <font name="OrnamentSerif">✦</font>', styles['section_tag']))
    # Titre « Thème Natal » (sans « complet » — c'était le titre marketing
    # externe, pas le titre éditorial du livre). Placé au-dessus du hero
    # pour établir d'emblée la nature du document.
    _book_title_style = styles.get('book_title_cover') or ParagraphStyle(
        'book_title_cover', fontName=font('Cormorant', 'Helvetica'),
        fontSize=34, leading=38, textColor=GOLD, alignment=TA_CENTER,
        spaceAfter=12,
    )
    story.append(Paragraph('Thème Natal', _book_title_style))
    story.append(Spacer(1, 0.2 * cm))

    img_used = False

    # Priorité 1 : planète 3D personnalisée (Lot 2 — Feb 2026)
    if sun_sign:
        try:
            from services.planet_renderer import (
                generate_planet_png, SIGN_TO_RULER,
                month_to_season, SEASON_LABELS_FR,
            )
            png_bytes = generate_planet_png(sun_sign, size=1200, birth_month=birth_month)
            img = RLImage(io.BytesIO(png_bytes), width=8.5 * cm, height=8.5 * cm, mask='auto')
            story.append(img)
            # Petite légende de la planète maîtresse (micro-personnalisation)
            ruler = SIGN_TO_RULER.get(sun_sign, 'Soleil')
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(
                f'<font name="OrnamentSerif">✦</font> {ruler.upper()} — ta planète maîtresse <font name="OrnamentSerif">✦</font>',
                ParagraphStyle('planet_caption', fontName=font('Cinzel', 'Helvetica'),
                               fontSize=9, textColor=GOLD, alignment=TA_CENTER,
                               spaceAfter=2),
            ))
            # Mention « Édition {Saison} » pour l'effet collection (Lot 5)
            if birth_month:
                season_key = month_to_season(birth_month)
                season_fr = SEASON_LABELS_FR.get(season_key, '').upper()
                if season_fr:
                    story.append(Paragraph(
                        f'ÉDITION {season_fr}',
                        ParagraphStyle('season_caption', fontName=font('Cinzel', 'Helvetica'),
                                       fontSize=7, textColor=MUTED, alignment=TA_CENTER,
                                       spaceAfter=2, letterSpacing=3),
                    ))
            story.append(Spacer(1, 0.3 * cm))
            img_used = True
        except Exception:
            img_used = False

    # Priorité 2 : hero V3 local
    from pathlib import Path as _P
    _hero_local = _P('/app/backend/assets/pdf_covers/natal_hero.png')
    if not img_used and _hero_local.exists():
        try:
            img = RLImage(str(_hero_local), width=10 * cm, height=10 * cm, mask='auto')
            story.append(img)
            story.append(Spacer(1, 1.2 * cm))
            img_used = True
        except Exception:
            img_used = False

    # Priorité 3 : illustration distante
    if not img_used:
        img_bytes = _dl_image(illustration_url(illustration_slug, 800))
        if img_bytes:
            img = RLImage(img_bytes, width=10 * cm, height=10 * cm, mask='auto')
            story.append(img)
            story.append(Spacer(1, 1.2 * cm))

    _cover_prenom_style = ParagraphStyle(
        'cover_prenom_fit', fontName=font('Cormorant', 'Helvetica'),
        fontSize=44, leading=50, textColor=CREAM,
        alignment=TA_CENTER, spaceAfter=10,
    )
    story.append(Paragraph(prenom, _cover_prenom_style))
    story.append(Paragraph(subtitle, styles['cover_sub']))
    story.append(Spacer(1, 0.3 * cm))
    # ═══ Nom du destinataire en dorure gaufrée (édition personnelle) ═══
    from services.pdf_cover_personalization import embossed_name as _embossed
    _embossed(story, prenom, size='medium')
    story.append(Spacer(1, 0.5 * cm))
    # Date FR (fix Feb 2026 : strftime('%B') dépend du locale et sortait
    # en anglais "OCTOBER" en prod. Mapping manuel pour garantir le FR).
    _FR_MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    _now = datetime.now()
    _date_fr = f'{_now.day} {_FR_MONTHS[_now.month - 1]} {_now.year}'
    story.append(Paragraph(_date_fr.upper(),
                           ParagraphStyle('date_cover', fontName=font('Cinzel', 'Helvetica'),
                                           fontSize=9, textColor=MUTED,
                                           alignment=TA_CENTER)))
    story.append(PageBreak())


def opening_page(story: list, styles: dict, prenom: str,
                 first_line: str = "Ton ciel n'a jamais été aussi clair.",
                 intro_text: Optional[str] = None):
    """Page 2 — l'accueil spectaculaire : prénom + ligne d'ouverture pleine page.

    Si `intro_text` est fourni, un paragraphe d'ouverture (60-120 mots) est
    posé sous la ligne « waouh » pour satisfaire la règle QA d'une page
    intérieure ≥ 40 mots (spec Feb 2026, §2).
    """
    story.append(Spacer(1, 8 * cm))
    story.append(Paragraph(f'<font color="{GOLD_HEX}"><font name="OrnamentSerif">✦</font></font>', styles['planet_glyph']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(prenom, styles['cover_title']))
    story.append(Paragraph(first_line, styles['waouh']))
    if intro_text:
        story.append(Spacer(1, 1.2 * cm))
        story.append(Paragraph(
            intro_text,
            ParagraphStyle('opening_intro', fontName=font('Cormorant', 'Helvetica'),
                           fontSize=12, leading=18, textColor=CREAM,
                           alignment=TA_CENTER, spaceAfter=12,
                           leftIndent=1.5 * cm, rightIndent=1.5 * cm),
        ))
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


def chapter_illustration(story: list, styles: dict, chapter_tag: str, title: str,
                         illustration_slug: str, intro_text: Optional[str] = None):
    """Page séparation de chapitre — tag + titre + illustration pleine page.

    Si `intro_text` est fourni (60-120 mots), il est posé sous l'illustration
    pour satisfaire la règle QA d'un chapter opener ≥ 40 mots (spec Feb 2026).
    """
    story.append(Spacer(1, 2 * cm))
    # Enveloppe les ✦ dans OrnamentSerif pour éviter les glyphes manquants (tofu) sur Cinzel.
    tag_html = chapter_tag.upper().replace(
        '✦', f'<font name="{font("OrnamentSerif", "Helvetica")}">✦</font>'
    )
    story.append(Paragraph(tag_html, styles['section_tag']))
    story.append(Paragraph(title, styles['cover_title']))
    story.append(Spacer(1, 1 * cm))
    img_bytes = _dl_image(illustration_url(illustration_slug, 800))
    if img_bytes:
        story.append(RLImage(img_bytes, width=12 * cm, height=12 * cm, mask='auto'))
    if intro_text:
        story.append(Spacer(1, 0.8 * cm))
        story.append(Paragraph(
            intro_text,
            ParagraphStyle('chapter_intro', fontName=font('Cormorant', 'Helvetica'),
                           fontSize=11, leading=16, textColor=CREAM,
                           alignment=TA_CENTER, spaceAfter=10,
                           leftIndent=1.5 * cm, rightIndent=1.5 * cm),
        ))
    story.append(PageBreak())


def chart_wheel_page(
    story: list, styles: dict, wheel_png_bytes: bytes,
    prenom: str, birth_date_fr: str, sun_sign: str, moon_sign: str, asc_sign: str,
):
    """
    Page STANDALONE dédiée à la carte du ciel — format "poster".

    La carte est agrandie au maximum (17 × 17 cm) pour permettre
    une impression poster future. Elle occupe toute la page A4 à elle seule.

    wheel_png_bytes : le SVG astrology-api.io v3 déjà converti en PNG
    (usage : `cairosvg.svg2png(bytestring=svg_str.encode(), output_width=1200)`).
    """
    from io import BytesIO

    # Page STANDALONE : la carte occupe une page entière à elle seule.
    # Le PageBreak final garantit l'isolement. On ne force PAS de PageBreak
    # en entrée car les appelants (natal_pdf_v2) viennent systématiquement
    # d'une opening_page qui finit déjà par un PageBreak.
    # Header compact (prend ~3 cm en haut)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph('<font name="OrnamentSerif">✦</font> TA CARTE DU CIEL <font name="OrnamentSerif">✦</font>', styles['section_tag']))
    story.append(Paragraph(f'La signature astrale de {prenom}', styles['cover_title']))
    story.append(Paragraph(
        f'Née le {birth_date_fr}',
        ParagraphStyle('birth_line', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                       fontSize=12, textColor=CREAM, alignment=TA_CENTER, spaceAfter=8),
    ))

    # Wheel image AGRANDIE au maximum pour impression poster (17 × 17 cm,
    # soit toute la largeur utile moins quelques millimètres de marge).
    try:
        img = RLImage(BytesIO(wheel_png_bytes), width=17 * cm, height=17 * cm, mask='auto')
        story.append(img)
    except Exception:
        img_bytes = _dl_image(illustration_url('roue_zodiaque', 800))
        if img_bytes:
            story.append(RLImage(img_bytes, width=15 * cm, height=15 * cm, mask='auto'))

    story.append(Spacer(1, 0.4 * cm))

    # Trio identitaire en pied de page (rendu compact)
    trio = (
        f'Soleil <font color="{GOLD_HEX}">{sun_sign}</font>  ·  '
        f'Lune <font color="{GOLD_HEX}">{moon_sign}</font>  ·  '
        f'Ascendant <font color="{GOLD_HEX}">{asc_sign}</font>'
    )
    story.append(Paragraph(trio, ParagraphStyle(
        'trio', fontName=font('Cinzel', 'Helvetica'),
        fontSize=11, textColor=CREAM,
        alignment=TA_CENTER, spaceAfter=6,
    )))

    # Saut de page final : la carte reste SEULE sur sa page.
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


def emotional_ending(story: list, styles: dict, prenom: str, signature: str = 'Soléna'):
    """Fin très émotionnelle — signature paramétrable.

    Refactor 2026-02-23 : tout tient sur UNE seule page (spacers ajustés) +
    ajout d'une petite illustration finale décorative sous la signature pour
    éviter la citation orpheline sur une page vide.

    Refactor 2026-02-27 : paramètre ``signature`` pour permettre au Thème Natal
    de signer « — Plume Astrale » (la voix Soléna est réservée aux autres
    produits : Cercle, chat, numérologie, karma, rencontres, astrocarto).
    """
    story.append(Spacer(1, 1.8 * cm))
    img_bytes = _dl_image(illustration_url("astral_silhouette", 800))
    if img_bytes:
        story.append(RLImage(img_bytes, width=6.5 * cm, height=6.5 * cm, mask='auto'))
        story.append(Spacer(1, 0.9 * cm))
    story.append(Paragraph('Ferme les yeux.', styles['waouh']))
    story.append(Paragraph(f'Repense à tout ce que tu viens de lire, {prenom}.', styles['dialogue']))
    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph(
        'Il y a une raison pour laquelle tu es arrivée jusqu\'ici.',
        styles['dialogue']))
    story.append(Spacer(1, 0.5 * cm))
    # Bloc citation + signature + petit ornement final — gardés ensemble pour éviter
    # que la dernière ligne finisse seule sur une page suivante.
    final_block = [
        Paragraph(
            'Les étoiles n\'écrivent pas ton destin.<br/>'
            'Elles éclairent simplement le chemin<br/>que tu es libre d\'emprunter.',
            styles['waouh']),
        Spacer(1, 0.9 * cm),
        Paragraph(f'— {signature}', styles['signature']),
        Spacer(1, 0.7 * cm),
        Paragraph(
            f'<font color="{GOLD_HEX}"><font name="OrnamentSerif">✦ ⁘ ✦</font></font>',
            ParagraphStyle('final_ornament', fontName=font('Cinzel', 'Helvetica'),
                           fontSize=18, textColor=GOLD, alignment=TA_CENTER,
                           leading=22, spaceBefore=6),
        ),
    ]
    story.append(KeepTogether(final_block))


# ═══════════════════════════════════════════════════════════
#   PRIMITIVES v2 — pages DENSES avec image intégrée
#   (refactor 2026-02-22 : suppression des pages 1-ligne)
# ═══════════════════════════════════════════════════════════

def planet_dense_page(
    story: list, styles: dict,
    planet_name: str, sign: str,
    body_html: str,
    image_local_path: Optional[str] = None,
    dialogue_question: Optional[str] = None,
    glyph: Optional[str] = None,
    is_first_in_chapter: bool = False,
):
    """Section d'une planète — flux continu type livre (plus de saut de page forcé).

    Layout (refactor 2026-02-26) :
      - Header "SOLEIL — CANCER" (Cinzel doré, centré) — gardé solidaire du bloc
      - Petite image planète 3,8 × 3,8 cm centrée
      - Dialogue psychologique (italique doré)
      - Corps 2–4 paragraphes
      - Séparateur ornemental final (filet or + étoile) qui tient compagnie au
        texte suivant au lieu de forcer un PageBreak.

    Le flux planète-après-planète se déroule maintenant comme un chapitre de
    livre, les sections s'enchaînant naturellement avec un simple filet
    ornemental pour marquer la transition. ReportLab gère automatiquement le
    saut de page si le contenu dépasse.
    """
    from reportlab.platypus import Image as RLImage

    # Header + image + dialogue tenus ensemble pour éviter qu'un titre reste
    # orphelin en bas de page.
    header_block = []
    header_block.append(Spacer(1, 0.9 * cm))
    header_str = f'{planet_name.upper()} — <font color="{GOLD_HEX}">{sign}</font>'
    header_block.append(Paragraph(
        header_str,
        ParagraphStyle('planet_dense_h', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=16, textColor=CREAM,
                       alignment=TA_CENTER, spaceAfter=14),
    ))
    if image_local_path and os.path.exists(image_local_path):
        try:
            header_block.append(RLImage(image_local_path, width=3.8 * cm, height=3.8 * cm, mask='auto'))
            header_block.append(Spacer(1, 0.4 * cm))
        except Exception:
            pass
    if dialogue_question:
        header_block.append(Paragraph(
            f'<i>{dialogue_question}</i>',
            ParagraphStyle('dialogue_dense', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                           fontSize=13, leading=20, textColor=GOLD_LIGHT,
                           alignment=TA_CENTER, leftIndent=1 * cm, rightIndent=1 * cm,
                           spaceAfter=14),
        ))
    # On garde ensemble le header + le début du corps pour éviter un titre
    # orphelin : premier paragraphe collé au titre.
    paragraphs = [p.strip() for p in (body_html or '').split('\n\n') if p.strip()]
    if paragraphs:
        header_block.append(Paragraph(paragraphs[0], styles['body_luxe']))
    story.append(KeepTogether(header_block))

    # Reste du corps : flux libre (ReportLab coupe aux pages si besoin)
    for para in paragraphs[1:]:
        story.append(Paragraph(para, styles['body_luxe']))

    # Séparateur ornemental final — pas de PageBreak. Chaque séparateur varie
    # (petite illustration IA ou filet typographique) pour un rythme de livre.
    _append_section_ornament(story, planet_name)
    # Refonte Feb 2026 — colonne vertébrale 50 pages : chaque section planète
    # occupe sa propre page. On force le saut de page pour que la numérotation
    # soit stable et prévisible (p.13–26 pour les 11 planètes + Chiron + Nœuds).
    story.append(PageBreak())


# ─────────────────────────────────────────────────────────────────────
# Ornements de séparation entre sections (planètes, maisons, aspects)
# ─────────────────────────────────────────────────────────────────────

_ORNAMENTS_DIR = '/app/backend/assets/pdf_ornaments'
_ORNAMENT_SLUGS = (
    'ornament_stars', 'ornament_moon_flowers', 'ornament_sun_rays',
    'ornament_planets_line', 'ornament_zodiac_wreath', 'ornament_butterfly',
)


def _available_ornaments() -> list[str]:
    """Retourne la liste des ornements IA disponibles sur disque."""
    out = []
    for slug in _ORNAMENT_SLUGS:
        p = os.path.join(_ORNAMENTS_DIR, f'{slug}.png')
        if os.path.exists(p) and os.path.getsize(p) > 10_000:
            out.append(p)
    return out


def _append_section_ornament(story: list, section_key: str = ''):
    """Insère un petit ornement de séparation entre deux sections consécutives.

    Alterne entre :
      - une illustration IA (bandeau 7 × 2 cm, générée via Nano Banana)
      - un filet typographique or ✦ · ❋ · ✦ (fallback systématique)

    Pas de PageBreak : laisse le flux continu. Un petit Spacer entoure
    l'ornement pour qu'il respire.
    """
    story.append(Spacer(1, 0.7 * cm))
    available = _available_ornaments()
    if available:
        # Alterne de façon déterministe sur la clé de section
        idx = (sum(ord(c) for c in section_key)) % len(available)
        img_path = available[idx]
        try:
            story.append(RLImage(img_path, width=7 * cm, height=2.1 * cm, mask='auto',
                                 hAlign='CENTER'))
            story.append(Spacer(1, 0.7 * cm))
            return
        except Exception:
            pass
    # Fallback : filet typographique or (toujours présent)
    story.append(Paragraph(
        f'<font color="{GOLD_HEX}" size="14"><font name="OrnamentSerif">✦ · ❋ · ✦</font></font>',
        ParagraphStyle('section_sep', fontName=font('Cinzel', 'Helvetica'),
                       fontSize=14, textColor=GOLD, alignment=TA_CENTER,
                       leading=18, spaceAfter=14),
    ))
    story.append(Spacer(1, 0.3 * cm))


def photos_grid_2x2(
    story: list, styles: dict,
    chapter_tag: str, title: str,
    cells: list,
):
    """Page grille 2×2 photos : tag + titre + 4 images avec caption courte.

    cells : liste de 4 dicts { 'image': str_path, 'label': 'Soleil', 'sublabel': 'Cancer' }.
    Les cellules manquantes affichent une puce or décorative comme placeholder.

    Refactor 2026-02-26 : saut de page EXPLICITE au début pour que la grille,
    qui est une section visuelle de type "chapitre", démarre toujours sur une
    page vierge (sinon elle écraserait le flux planète qui la précède).
    """
    from reportlab.platypus import Image as RLImage
    # CondPageBreak : saut de page uniquement si l'espace restant est insuffisant.
    # Évite une page blanche quand on vient juste de part_divider_page (qui finit
    # déjà par un PageBreak), tout en garantissant que la grille 2×2 ne soit
    # pas écrasée en pied de page.
    story.append(CondPageBreak(18 * cm))
    story.append(Spacer(1, 1.2 * cm))
    tag_html = chapter_tag.upper().replace(
        '✦', f'<font name="{font("OrnamentSerif", "Helvetica")}">✦</font>'
    )
    story.append(Paragraph(tag_html, styles['section_tag']))
    story.append(Paragraph(
        title,
        ParagraphStyle('grid_title', fontName=font('Cormorant', 'Helvetica'),
                       fontSize=24, leading=30, textColor=CREAM,
                       alignment=TA_CENTER, spaceAfter=24),
    ))

    def _cell(c):
        img_flow = None
        if c and c.get('image') and os.path.exists(c['image']):
            try:
                img_flow = RLImage(c['image'], width=5 * cm, height=5 * cm, mask='auto')
            except Exception:
                img_flow = None
        if img_flow is None:
            img_flow = Paragraph(f'<font color="{GOLD_HEX}" size="42"><font name="OrnamentSerif">✦</font></font>',
                                 ParagraphStyle('grid_placeholder', fontName='Helvetica',
                                                fontSize=42, textColor=GOLD,
                                                alignment=TA_CENTER, leading=44))
        label = (c or {}).get('label', '')
        sub = (c or {}).get('sublabel', '')
        label_p = Paragraph(
            label.upper(),
            ParagraphStyle('grid_lbl', fontName=font('Cinzel', 'Helvetica'),
                           fontSize=10, textColor=CREAM,
                           alignment=TA_CENTER, spaceBefore=6, spaceAfter=2),
        )
        sub_p = Paragraph(
            f'<font color="{GOLD_HEX}">{sub}</font>',
            ParagraphStyle('grid_sub', fontName=font('Cormorant-Italic', 'Helvetica-Oblique'),
                           fontSize=11, textColor=GOLD,
                           alignment=TA_CENTER, spaceAfter=2),
        )
        return [[img_flow], [label_p], [sub_p]]

    cells = (cells or []) + [None] * (4 - len(cells or []))
    tl = _cell(cells[0])
    tr = _cell(cells[1])
    bl = _cell(cells[2])
    br = _cell(cells[3])

    inner_tl = Table(tl, colWidths=[6.5 * cm], hAlign='CENTER')
    inner_tr = Table(tr, colWidths=[6.5 * cm], hAlign='CENTER')
    inner_bl = Table(bl, colWidths=[6.5 * cm], hAlign='CENTER')
    inner_br = Table(br, colWidths=[6.5 * cm], hAlign='CENTER')

    grid = Table(
        [[inner_tl, inner_tr], [inner_bl, inner_br]],
        colWidths=[7 * cm, 7 * cm],
        rowHeights=[8 * cm, 8 * cm],
        hAlign='CENTER',
    )
    grid.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Cadres retirés (2026-02-23) : plus de BOX ni d'INNERGRID or
        # → les photos respirent, plus de "petits carrés" superflus.
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(grid)
    story.append(PageBreak())


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
