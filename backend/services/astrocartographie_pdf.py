"""
Générateur de PDF "Astrocartographie — Où vivre ta meilleure vie" — 49 EUR.
Utilise ReportLab + les données astrology-api.io v3 + enrichissement OpenAI.

Structure (~18 pages) :
  1. Couverture
  2. Introduction — L'astrocartographie
  3. Ta carte du monde (SVG /astrocartography/map converti en PNG)
  4-6. Ville 1 choisie (analyse enrichie sur 3 pages)
  7-9. Ville 2 choisie
  10-12. Ville 3 choisie
  13-14. Bonus 1 (Soléna)
  15-16. Bonus 2 (Soléna)
  17. Synthèse
  18. Signature Soléna + rituel d'ancrage
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)

# Palette Plume Astrale
NIGHT       = colors.HexColor('#111625')
NIGHT_SOFT  = colors.HexColor('#1A2035')
GOLD        = colors.HexColor('#D4AF37')
GOLD_LIGHT  = colors.HexColor('#E8C766')
LAVENDER    = colors.HexColor('#E3D7FF')
CREAM       = colors.HexColor('#F5EEE0')
MUTED       = colors.HexColor('#9089B5')


import re
_ALLOWED_TAGS_RE = re.compile(r'</?([bi])>', re.IGNORECASE)


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    """Wrap texte en préservant <b>/<i> pour ReportLab."""
    if text is None:
        text = ""
    t = str(text)
    # 1) Escape uniquement & (ampersand)
    t = t.replace('&', '&amp;')
    # 2) Placeholder les balises autorisées pour éviter double-escape
    tags = []

    def _hold(m):
        tags.append(m.group(0))
        return f'\x00TAG{len(tags) - 1}\x00'

    t = _ALLOWED_TAGS_RE.sub(_hold, t)
    # 3) Escape les autres < >
    t = t.replace('<', '&lt;').replace('>', '&gt;')
    # 4) Restore les balises autorisées
    for i, tag in enumerate(tags):
        t = t.replace(f'\x00TAG{i}\x00', tag.lower())
    return Paragraph(t, style)


def _bg_canvas(canv, doc):
    canv.saveState()
    W, H = A4
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    for i, alpha in enumerate([0.02, 0.015, 0.01]):
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
        canv.circle(W / 2, H, (i + 1) * 6 * cm, fill=1, stroke=0)
    import random
    r = random.Random(hash((doc.page,)))
    for _ in range(30):
        x = r.uniform(1 * cm, W - 1 * cm)
        y = r.uniform(1 * cm, H - 1 * cm)
        s = r.choice([0.4, 0.5, 0.6, 0.8])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
        canv.circle(x, y, s, fill=1, stroke=0)
    # ─── Cadre de page prestige (fine ligne dorée) ───
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(0.35)
    canv.setDash([0.6, 2.4], 0)
    canv.rect(1.2 * cm, 1.2 * cm, W - 2.4 * cm, H - 2.4 * cm, fill=0, stroke=1)
    canv.setDash([], 0)
    # ─── Ornement en haut de page (petit soleil doré) ───
    canv.setFillColor(GOLD)
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(0.4)
    canv.circle(W / 2, H - 1.55 * cm, 0.10 * cm, fill=1, stroke=0)
    canv.line(W / 2 - 1.4 * cm, H - 1.55 * cm, W / 2 - 0.3 * cm, H - 1.55 * cm)
    canv.line(W / 2 + 0.3 * cm, H - 1.55 * cm, W / 2 + 1.4 * cm, H - 1.55 * cm)
    # ─── Footer : titre du livre + page ───
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 6.5)
    canv.drawString(2 * cm, 0.75 * cm, "PLUME ASTRALE · ASTROCARTOGRAPHIE")
    canv.drawRightString(W - 2 * cm, 0.75 * cm, f"— {doc.page} —")
    canv.restoreState()


def _make_styles():
    """Utilise la charte unifiée (Cinzel + Cormorant Garamond via pdf_theme)."""
    from services.pdf_theme import make_styles as _shared_styles
    return _shared_styles()


def _svg_to_png_bytes(svg_str: str) -> Optional[bytes]:
    """Convertit un SVG (string) en PNG bytes via cairosvg si dispo, sinon None."""
    if not svg_str:
        return None
    try:
        import cairosvg  # type: ignore
        return cairosvg.svg2png(bytestring=svg_str.encode('utf-8'),
                                output_width=1600, background_color='white')
    except Exception as e:
        logger.warning(f"[astrocarto_pdf] cairosvg unavailable, trying svglib: {e}")
    try:
        # Fallback : svglib + reportlab
        from svglib.svglib import svg2rlg  # type: ignore
        from reportlab.graphics import renderPM  # type: ignore
        from io import StringIO
        drawing = svg2rlg(StringIO(svg_str))
        if drawing is None:
            return None
        bio = BytesIO()
        renderPM.drawToFile(drawing, bio, fmt='PNG')
        return bio.getvalue()
    except Exception as e2:
        logger.warning(f"[astrocarto_pdf] svglib fallback failed: {e2}")
        return None


def _ornament(story, kind: str = 'star'):
    """Séparateur décoratif discret : petit motif doré centré."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as _c
    glyph = {'star': '✦', 'diamond': '◆', 'dot': '·'}.get(kind, '✦')
    # 3-glyph horizontal ornament centered
    text = f'<font color="#D4AF37">{glyph}&nbsp;&nbsp;&nbsp;{glyph}&nbsp;&nbsp;&nbsp;{glyph}</font>'
    p_style = ParagraphStyle('ornament', fontName='Helvetica', fontSize=9,
                             alignment=TA_CENTER, leading=12, spaceBefore=6, spaceAfter=6)
    story.append(Paragraph(text, p_style))


def _cover(story, styles, first_name: str, birth_fr: str):
    story.append(Spacer(1, 4.5 * cm))
    story.append(_p("PLUME ASTRALE · RAPPORTS PRESTIGE", styles['caption']))
    _ornament(story, 'star')
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p("ASTROCARTOGRAPHIE", styles['title']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p("<i>Où vivre ta meilleure vie</i>", styles['subtitle']))
    story.append(Spacer(1, 0.4 * cm))
    # ═══ Nom du destinataire en dorure gaufrée ═══
    from services.pdf_cover_personalization import embossed_name as _embossed
    _embossed(story, first_name, size='large')
    story.append(Spacer(1, 0.4 * cm))
    _ornament(story, 'diamond')
    story.append(Spacer(1, 1.8 * cm))
    if birth_fr:
        story.append(_p(f"Né(e) le {birth_fr}", styles['meta']))
    story.append(Spacer(1, 2.0 * cm))
    story.append(_p(
        "« Le ciel ne t'a pas donné une seule maison. Il t'en a offert plusieurs — "
        "il te reste à découvrir laquelle t'attend. »",
        styles['quote']))
    story.append(Spacer(1, 0.4 * cm))
    _ornament(story, 'star')
    story.append(PageBreak())


def _intro(story, styles):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p("Introduction", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>L'astrocartographie</i>", styles['h2']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(_p(
        "L'astrocartographie est une science ancienne réactualisée dans les années 1970 par Jim Lewis. "
        "Elle part d'un principe simple : ton thème natal est calculé pour l'instant précis et le lieu précis de ta naissance. "
        "Si tu déplaces ce point géographique, les <b>angles</b> de ton ciel changent — et donc les énergies "
        "que tu incarnes différemment selon l'endroit du monde où tu poses tes pas.",
        styles['body']))
    story.append(_p(
        "Chaque planète de ton thème projette sur la Terre <b>quatre lignes</b> : Ascendant (identité), "
        "Descendant (relations), Milieu du Ciel (carrière et image publique), Fond du Ciel (racines et intimité). "
        "Ces lignes tracent des couloirs invisibles. Vivre sur une ligne, ou à moins de 800 km d'elle, active "
        "profondément l'énergie de la planète concernée.",
        styles['body']))
    story.append(_p(
        "Ce document explore trois villes que tu as choisies, deux destinations bonus que Soléna a sélectionnées "
        "pour toi selon la géographie unique de ton ciel, et une carte du monde qui te montre où passent tes lignes. "
        "Ce n'est pas une ordonnance — c'est une invitation.",
        styles['body']))
    story.append(Spacer(1, 0.6 * cm))
    _ornament(story, 'diamond')
    story.append(PageBreak())


def _world_map(story, styles, map_svg: Optional[str]):
    """Insère la carte du monde SVG convertie en PNG — pleine page format paysage sur A4 portrait."""
    story.append(Spacer(1, 0.8 * cm))
    story.append(_p("Ta carte du monde", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>Les lignes de ton ciel projetées sur la Terre</i>", styles['h2']))
    story.append(Spacer(1, 0.6 * cm))

    png_bytes = _svg_to_png_bytes(map_svg) if map_svg else None
    if png_bytes:
        try:
            # Format paysage plus grand — occupe presque toute la largeur utile A4 (~17cm)
            # avec une hauteur généreuse pour révéler tous les détails géographiques
            img = Image(BytesIO(png_bytes), width=17 * cm, height=11.5 * cm)
            img.hAlign = 'CENTER'
            story.append(img)
        except Exception as e:
            logger.warning(f"[astrocarto_pdf] image insert failed: {e}")
            story.append(_p("[Carte indisponible — voir tes villes ci-après]", styles['italic']))
    else:
        story.append(_p("[Carte du monde non disponible pour l'instant]", styles['italic']))

    story.append(Spacer(1, 0.8 * cm))
    story.append(_p(
        "Chaque couleur représente une planète. Chaque trait vertical (nord-sud) est une ligne d'Ascendant "
        "ou de Descendant, chaque trait courbe est une ligne de Milieu du Ciel ou de Fond du Ciel. "
        "Là où plusieurs lignes se croisent, l'énergie est intense — c'est ce qu'on appelle un <b>paran</b>. "
        "Les villes situées à moins de 800 km d'une ligne sont fortement influencées par la planète concernée.",
        styles['body']))
    story.append(Spacer(1, 0.4 * cm))
    _ornament(story, 'diamond')
    story.append(PageBreak())


def _city_pages(story, styles, city_data: Dict[str, Any], enriched: Dict[str, str], is_bonus: bool = False):
    """3 pages par ville (bonus = 2 pages) — présentation prestige avec ornements."""
    city = city_data.get('city', 'Ville inconnue')
    country = city_data.get('country', '')

    # PAGE 1 : Titre + headline + ambiance
    story.append(Spacer(1, 1.8 * cm))
    label = "DESTINATION BONUS · SOLÉNA" if is_bonus else "TA VILLE CHOISIE"
    story.append(_p(label, styles['caption']))
    _ornament(story, 'star')
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p(f"<i>{city}</i>", styles['title']))
    story.append(_p(country, styles['subtitle']))
    story.append(Spacer(1, 0.6 * cm))
    _ornament(story, 'diamond')
    story.append(Spacer(1, 0.4 * cm))
    if enriched.get('headline'):
        story.append(_p(f"« {enriched['headline']} »", styles['quote']))
    story.append(Spacer(1, 0.4 * cm))

    story.append(_p("L'ambiance de ce lieu", styles['h3']))
    story.append(_p(enriched.get('ambiance', ''), styles['body']))

    if is_bonus and enriched.get('why'):
        story.append(Spacer(1, 0.2 * cm))
        story.append(_p("Pourquoi Soléna te l'offre", styles['h3']))
        story.append(_p(enriched['why'], styles['body']))
        if enriched.get('promise'):
            story.append(Spacer(1, 0.3 * cm))
            story.append(_p(f"« {enriched['promise']} »", styles['quote']))

    story.append(PageBreak())

    # PAGE 2 : Domaines de vie
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p(f"{city} · Domaines de vie", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>Ce que le lieu active en toi</i>", styles['h2']))
    story.append(Spacer(1, 0.5 * cm))

    story.append(_p("Ta trajectoire professionnelle", styles['h3']))
    story.append(_p(enriched.get('career', ''), styles['body']))

    story.append(_p("Ta vie affective", styles['h3']))
    story.append(_p(enriched.get('love', ''), styles['body']))

    story.append(_p("Ta spiritualité", styles['h3']))
    story.append(_p(enriched.get('spirituality', ''), styles['body']))

    story.append(_p("Ton corps, ton énergie", styles['h3']))
    story.append(_p(enriched.get('body', ''), styles['body']))

    story.append(PageBreak())

    # PAGE 3 : Conseil + lignes actives (chosen only, pas bonus)
    if not is_bonus:
        story.append(Spacer(1, 1.8 * cm))
        story.append(_p(f"{city} · Le mot de Soléna", styles['caption']))
        _ornament(story, 'star')
        story.append(_p("<i>Un conseil pour toi</i>", styles['h2']))
        story.append(Spacer(1, 0.6 * cm))
        story.append(_p(enriched.get('advice', ''), styles['body']))

        # Lignes planétaires actives
        nearby = city_data.get('nearby_lines') or []
        if nearby:
            story.append(Spacer(1, 0.6 * cm))
            _ornament(story, 'diamond')
            story.append(_p("Les lignes planétaires actives ici", styles['h3']))
            for line in nearby[:6]:
                if not isinstance(line, dict):
                    continue
                planet = line.get('planet', '')
                lt = line.get('line_type', '')
                dist = line.get('distance_km')
                lt_fr = {'AC': "Ascendant", 'DC': 'Descendant', 'MC': 'Milieu du Ciel', 'IC': 'Fond du Ciel'}.get(lt, lt)
                planet_fr = _planet_fr(planet)
                if dist is not None:
                    story.append(_p(f"• <b>{planet_fr} · {lt_fr}</b> — à {int(dist)} km", styles['body']))
                else:
                    story.append(_p(f"• <b>{planet_fr} · {lt_fr}</b>", styles['body']))
        story.append(PageBreak())


def _planetary_lines_pages(story, styles, lines_data: list):
    """Ajoute une section détaillée avec chaque ligne planétaire de l'utilisateur.

    lines_data : liste de dicts {'planet': str, 'line_type': str} déjà dédupliquée.
    """
    from services.astrocartographie_lines_data import get_line_interpretation

    if not lines_data:
        return

    # Page d'intro à la section
    story.append(Spacer(1, 1.4 * cm))
    story.append(_p("Tes lignes planétaires en détail", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>Ce que chaque ligne active en toi</i>", styles['h2']))
    story.append(Spacer(1, 0.6 * cm))
    story.append(_p(
        "Chaque planète de ton thème natal projette 4 lignes sur la Terre : "
        "<b>Ascendant</b> (ton identité), <b>Descendant</b> (tes relations), "
        "<b>Milieu du Ciel</b> (ta vocation), <b>Fond du Ciel</b> (tes racines). "
        "Vivre à moins de 800 km d'une de ces lignes active profondément l'énergie de la planète concernée. "
        "Voici l'interprétation de chacune de tes lignes principales.",
        styles['body']))
    story.append(Spacer(1, 0.5 * cm))
    _ornament(story, 'diamond')
    story.append(PageBreak())

    # Regrouper 2 interprétations par page (pour ne pas exploser la longueur)
    entries = []
    for line in lines_data:
        interp = get_line_interpretation(line.get('planet', ''), line.get('line_type', ''))
        if interp:
            entries.append(interp)

    # Pages : 2 lignes par page
    for i in range(0, len(entries), 2):
        chunk = entries[i:i + 2]
        story.append(Spacer(1, 1.4 * cm))
        story.append(_p("Tes lignes planétaires", styles['caption']))
        _ornament(story, 'star')
        story.append(Spacer(1, 0.4 * cm))
        for j, entry in enumerate(chunk):
            title = f"{entry['planet_fr']} · {entry['line_fr']}"
            story.append(_p(title, styles['h3']))
            story.append(_p(f"<i>{entry['headline']}</i>", styles['italic']))
            story.append(_p(entry['body'], styles['body']))
            if j == 0 and len(chunk) > 1:
                story.append(Spacer(1, 0.3 * cm))
                _ornament(story, 'dot')
                story.append(Spacer(1, 0.3 * cm))
        story.append(PageBreak())


def _planet_fr(planet: str) -> str:
    return {
        'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Mars': 'Mars',
        'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 'Neptune': 'Neptune',
        'Pluto': 'Pluton', 'North Node': 'Nœud Nord', 'South Node': 'Nœud Sud', 'Chiron': 'Chiron',
    }.get(planet, planet)


def _synthesis_page(story, styles, first_name: str, synthesis_text: str):
    story.append(Spacer(1, 1.4 * cm))
    story.append(_p("Synthèse", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>Le message de Soléna</i>", styles['h2']))
    story.append(Spacer(1, 0.6 * cm))
    # Split paragraphs
    paragraphs = [p.strip() for p in synthesis_text.split('\n') if p.strip()]
    for para in paragraphs:
        if para.startswith('—') or para.startswith('- '):
            story.append(_p(f"<i>{para}</i>", styles['italic']))
        else:
            story.append(_p(para, styles['body']))
    story.append(Spacer(1, 0.5 * cm))
    _ornament(story, 'diamond')
    story.append(PageBreak())


def _rituel_signature(story, styles, first_name: str):
    story.append(Spacer(1, 1.4 * cm))
    story.append(_p("Rituel d'ancrage", styles['caption']))
    _ornament(story, 'star')
    story.append(_p("<i>Avant de partir</i>", styles['h2']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(_p(
        "Avant de réserver un billet ou de signer un bail, offre-toi ce rituel simple. Il ne demande "
        "qu'une bougie, un carnet, et vingt minutes de calme.",
        styles['body']))
    story.append(_p("1. Le silence de la carte", styles['accent']))
    story.append(_p(
        "Reprends la carte du monde de ce document. Pose ton doigt sur chacune des cinq villes, l'une après l'autre. "
        "Ferme les yeux 30 secondes. Note dans ton carnet la première image, sensation, ou couleur qui vient. "
        "Ne juge pas — reçois.",
        styles['body']))
    story.append(_p("2. Le test du corps", styles['accent']))
    story.append(_p(
        "Prononce à voix haute le nom de chaque ville. Observe ton corps. Serrement dans la poitrine ? "
        "Chaleur dans le ventre ? Sourire spontané ? Ton corps sait avant ta tête. Fais-lui confiance.",
        styles['body']))
    story.append(_p("3. Le voyage-graine", styles['accent']))
    story.append(_p(
        "Ne prends pas de décision définitive avant d'y avoir passé au moins 7 jours. L'astrocartographie révèle, "
        "mais c'est toi qui goûtes. Prévois un séjour d'exploration, avec l'intention d'y écouter, pas d'y trancher.",
        styles['body']))
    story.append(Spacer(1, 1.2 * cm))
    _ornament(story, 'diamond')
    story.append(Spacer(1, 0.4 * cm))
    story.append(_p("Avec toute ma tendresse,", styles['italic']))
    story.append(_p("<i>— Soléna</i>", styles['h3c']))
    story.append(_p("Guide chez Plume Astrale · plume-astrale.fr", styles['small']))
    story.append(Spacer(1, 0.6 * cm))
    _ornament(story, 'star')


def generate_astrocartographie_pdf(
    first_name: str,
    birth_date_iso: str,
    map_svg: Optional[str],
    chosen_cities: List[Dict[str, Any]],      # 3 villes analysées avec 'enriched' + 'raw'
    bonus_cities: List[Dict[str, Any]],        # 2 villes bonus avec 'enriched'
    synthesis_text: str,
    lines_data: Optional[List[Dict[str, Any]]] = None,   # lignes brutes (planet+line_type)
) -> bytes:
    """Génère le PDF complet.

    chosen_cities[i] = {
        'city': str, 'country': str, 'country_code': str,
        'raw': dict (location-analysis),
        'enriched': dict (from astrocarto_ai.enrich_city_analysis),
        'nearby_lines': [...]
    }
    bonus_cities[i] = {
        'city': str, 'country': str, 'enriched': dict (with 'why', 'promise'),
        'nearby_lines': [] (empty for bonus)
    }
    """
    # Formatage date FR
    birth_fr = birth_date_iso or ""
    if birth_date_iso and len(birth_date_iso) >= 10:
        try:
            from datetime import datetime
            dt = datetime.strptime(birth_date_iso[:10], '%Y-%m-%d')
            mois_fr = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                       'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            birth_fr = f"{dt.day} {mois_fr[dt.month - 1]} {dt.year}"
        except Exception:
            birth_fr = birth_date_iso

    buffer = BytesIO()
    styles = _make_styles()

    # ─── Story builder appelé en 2 passes (pour numérotation TOC réelle) ───
    from services.pdf_multipass_toc import build_with_toc, chapter_marker
    from services.pdf_prestige import toc_page, chapter_opener as _chapter_opener, simple_world_map_svg

    def _build_story(page_map):
        story: list = []

        _cover(story, styles, first_name or "Voyageur", birth_fr)

        # ─── Sommaire éditorial avec vraies pages (2e passe) ou None (1re) ───
        def _pg(cid, fallback=None):
            if page_map is None:
                return fallback
            return page_map.get(cid, fallback)

        toc = [
            {'roman': 'I',   'title': "L'astrocartographie",              'page': _pg('chap1')},
            {'roman': 'II',  'title': "Ta carte du monde",                 'page': _pg('chap2')},
            {'roman': 'III', 'title': "Tes lignes planétaires en détail", 'page': _pg('chap3')},
            {'roman': 'IV',  'title': "Tes trois villes choisies",         'page': _pg('chap4')},
            {'roman': 'V',   'title': "Les destinations de Soléna",        'page': _pg('chap5')},
            {'roman': 'VI',  'title': "Synthèse",                          'page': _pg('chap6')},
            {'roman': 'VII', 'title': "Rituel d'ancrage",                  'page': _pg('chap7')},
        ]
        toc_page(story, styles, toc)

        story.append(chapter_marker('chap1'))
        _chapter_opener(story, styles, 'I', "L'astrocartographie", "Comprendre ce que ta carte révèle")
        _intro(story, styles)

        story.append(chapter_marker('chap2'))
        _chapter_opener(story, styles, 'II', "Ta carte du monde", "Sept lignes tracées sur la Terre")
        # Fallback : si l'API n'a pas renvoyé de SVG, on injecte la carte de secours
        effective_map = map_svg
        if not effective_map:
            city_names = [c.get('city', '') for c in (chosen_cities or [])[:3]]
            effective_map = simple_world_map_svg(city_names=city_names)
        _world_map(story, styles, effective_map)

        if lines_data:
            from services.astrocartographie_lines_data import dedupe_lines
            story.append(chapter_marker('chap3'))
            _chapter_opener(story, styles, 'III', "Tes lignes planétaires en détail",
                            "L'interprétation de chacune de tes lignes")
            _planetary_lines_pages(story, styles, dedupe_lines(lines_data))

        if chosen_cities:
            story.append(chapter_marker('chap4'))
            _chapter_opener(story, styles, 'IV', "Tes trois villes choisies",
                            "Les lieux que tu as sélectionnés")
        for c in chosen_cities:
            _city_pages(story, styles, c, c.get('enriched') or {}, is_bonus=False)

        if bonus_cities:
            story.append(chapter_marker('chap5'))
            _chapter_opener(story, styles, 'V', "Les destinations de Soléna",
                            "Deux lieux inattendus, choisis pour toi")
        for b in bonus_cities:
            _city_pages(story, styles, b, b.get('enriched') or {}, is_bonus=True)

        story.append(chapter_marker('chap6'))
        _chapter_opener(story, styles, 'VI', "Synthèse", "Le message de Soléna")
        _synthesis_page(story, styles, first_name, synthesis_text or "")

        story.append(chapter_marker('chap7'))
        _chapter_opener(story, styles, 'VII', "Rituel d'ancrage", "Avant de partir")
        _rituel_signature(story, styles, first_name)

        return story

    pdf_bytes = build_with_toc(
        _build_story,
        doc_kwargs={
            'pagesize': A4,
            'leftMargin': 2.2 * cm, 'rightMargin': 2.2 * cm,
            'topMargin': 2 * cm, 'bottomMargin': 2 * cm,
            'title': "Astrocartographie — Où vivre ta meilleure vie",
            'author': "Soléna · Plume Astrale",
        },
        on_first_page=_bg_canvas,
        on_later_pages=_bg_canvas,
    )
    return pdf_bytes
