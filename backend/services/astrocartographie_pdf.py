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
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 7)
    canv.drawCentredString(W / 2, 0.9 * cm, f"Plume Astrale · Astrocartographie · page {doc.page}")
    canv.restoreState()


def _make_styles():
    return {
        'title': ParagraphStyle('title', fontName='Helvetica', fontSize=30, textColor=GOLD,
                                alignment=TA_CENTER, leading=36, spaceAfter=10),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica-Oblique', fontSize=17,
                                   textColor=CREAM, alignment=TA_CENTER, leading=22, spaceAfter=8),
        'caption': ParagraphStyle('caption', fontName='Helvetica', fontSize=8, textColor=GOLD,
                                  alignment=TA_CENTER, leading=10),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=22, textColor=GOLD_LIGHT,
                             spaceBefore=6, spaceAfter=10, leading=26),
        'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=15, textColor=GOLD,
                             spaceBefore=8, spaceAfter=6, leading=18),
        'h3c': ParagraphStyle('h3c', fontName='Helvetica-Bold', fontSize=15, textColor=GOLD,
                              alignment=TA_CENTER, spaceBefore=8, spaceAfter=6, leading=18),
        'meta': ParagraphStyle('meta', fontName='Helvetica', fontSize=9, textColor=MUTED, leading=12),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=10.5, textColor=CREAM,
                               alignment=TA_JUSTIFY, leading=15, spaceAfter=8),
        'italic': ParagraphStyle('italic', fontName='Helvetica-Oblique', fontSize=11, textColor=LAVENDER,
                                 alignment=TA_CENTER, leading=15, spaceAfter=10),
        'accent': ParagraphStyle('accent', fontName='Helvetica-Bold', fontSize=11, textColor=GOLD,
                                 spaceAfter=4),
        'quote': ParagraphStyle('quote', fontName='Helvetica-Oblique', fontSize=12.5, textColor=LAVENDER,
                                alignment=TA_CENTER, leading=17, spaceAfter=14),
        'small': ParagraphStyle('small', fontName='Helvetica', fontSize=8.5, textColor=MUTED,
                                leading=11.5, alignment=TA_CENTER),
        'label': ParagraphStyle('label', fontName='Helvetica-Bold', fontSize=9, textColor=GOLD,
                                spaceBefore=6, spaceAfter=2, leading=11),
    }


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


def _cover(story, styles, first_name: str, birth_fr: str):
    story.append(Spacer(1, 3.5 * cm))
    story.append(_p("PLUME ASTRALE · RAPPORTS PRESTIGE", styles['caption']))
    story.append(Spacer(1, 0.4 * cm))
    story.append(_p("ASTROCARTOGRAPHIE", styles['title']))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_p("<i>Où vivre ta meilleure vie</i>", styles['subtitle']))
    story.append(Spacer(1, 2.2 * cm))
    story.append(_p(f"Établi pour <b>{first_name}</b>", styles['italic']))
    if birth_fr:
        story.append(_p(f"Né(e) le {birth_fr}", styles['meta']))
    story.append(Spacer(1, 1.8 * cm))
    story.append(_p(
        "« Le ciel ne t'a pas donné une seule maison. Il t'en a offert plusieurs — "
        "il te reste à découvrir laquelle t'attend. »",
        styles['quote']))
    story.append(PageBreak())


def _intro(story, styles):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p("Introduction", styles['caption']))
    story.append(_p("<i>L'astrocartographie</i>", styles['h2']))
    story.append(Spacer(1, 0.3 * cm))
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
    story.append(PageBreak())


def _world_map(story, styles, map_svg: Optional[str]):
    """Insère la carte du monde SVG convertie en PNG."""
    story.append(Spacer(1, 0.8 * cm))
    story.append(_p("Ta carte du monde", styles['caption']))
    story.append(_p("<i>Les lignes de ton ciel projetées sur la Terre</i>", styles['h2']))
    story.append(Spacer(1, 0.5 * cm))

    png_bytes = _svg_to_png_bytes(map_svg) if map_svg else None
    if png_bytes:
        try:
            img = Image(BytesIO(png_bytes), width=17 * cm, height=8.5 * cm)
            img.hAlign = 'CENTER'
            story.append(img)
        except Exception as e:
            logger.warning(f"[astrocarto_pdf] image insert failed: {e}")
            story.append(_p("[Carte indisponible — voir tes villes ci-après]", styles['italic']))
    else:
        story.append(_p("[Carte du monde non disponible pour l'instant]", styles['italic']))

    story.append(Spacer(1, 0.6 * cm))
    story.append(_p(
        "Chaque couleur représente une planète. Chaque trait vertical (nord-sud) est une ligne d'Ascendant "
        "ou de Descendant, chaque trait courbe est une ligne de Milieu du Ciel ou de Fond du Ciel. "
        "Là où plusieurs lignes se croisent, l'énergie est intense — c'est ce qu'on appelle un <b>paran</b>. "
        "Les villes situées à moins de 800 km d'une ligne sont fortement influencées par la planète concernée.",
        styles['body']))
    story.append(PageBreak())


def _city_pages(story, styles, city_data: Dict[str, Any], enriched: Dict[str, str], is_bonus: bool = False):
    """3 pages par ville (bonus = 2 pages)."""
    city = city_data.get('city', 'Ville inconnue')
    country = city_data.get('country', '')

    # PAGE 1 : Titre + headline + ambiance
    story.append(Spacer(1, 1.5 * cm))
    label = "DESTINATION BONUS · SOLÉNA" if is_bonus else "TA VILLE CHOISIE"
    story.append(_p(label, styles['caption']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p(f"<i>{city}</i>", styles['title']))
    story.append(_p(country, styles['subtitle']))
    story.append(Spacer(1, 0.8 * cm))
    if enriched.get('headline'):
        story.append(_p(f"« {enriched['headline']} »", styles['quote']))
    story.append(Spacer(1, 0.4 * cm))

    story.append(_p("L'ambiance de ce lieu", styles['h3']))
    story.append(_p(enriched.get('ambiance', ''), styles['body']))

    if is_bonus and enriched.get('why'):
        story.append(_p("Pourquoi Soléna te l'offre", styles['h3']))
        story.append(_p(enriched['why'], styles['body']))
        if enriched.get('promise'):
            story.append(Spacer(1, 0.3 * cm))
            story.append(_p(f"« {enriched['promise']} »", styles['quote']))

    story.append(PageBreak())

    # PAGE 2 : Domaines de vie
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p(f"{city} · Domaines de vie", styles['caption']))
    story.append(_p(f"<i>Ce que le lieu active en toi</i>", styles['h2']))
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
        story.append(Spacer(1, 1.5 * cm))
        story.append(_p(f"{city} · Le mot de Soléna", styles['caption']))
        story.append(_p("<i>Un conseil pour toi</i>", styles['h2']))
        story.append(Spacer(1, 0.5 * cm))
        story.append(_p(enriched.get('advice', ''), styles['body']))

        # Lignes planétaires actives
        nearby = city_data.get('nearby_lines') or []
        if nearby:
            story.append(Spacer(1, 0.5 * cm))
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


def _planet_fr(planet: str) -> str:
    return {
        'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Mars': 'Mars',
        'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 'Neptune': 'Neptune',
        'Pluto': 'Pluton', 'North Node': 'Nœud Nord', 'South Node': 'Nœud Sud', 'Chiron': 'Chiron',
    }.get(planet, planet)


def _synthesis_page(story, styles, first_name: str, synthesis_text: str):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p("Synthèse", styles['caption']))
    story.append(_p("<i>Le message de Soléna</i>", styles['h2']))
    story.append(Spacer(1, 0.5 * cm))
    # Split paragraphs
    paragraphs = [p.strip() for p in synthesis_text.split('\n') if p.strip()]
    for para in paragraphs:
        if para.startswith('—') or para.startswith('- '):
            story.append(_p(f"<i>{para}</i>", styles['italic']))
        else:
            story.append(_p(para, styles['body']))
    story.append(PageBreak())


def _rituel_signature(story, styles, first_name: str):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p("Rituel d'ancrage", styles['caption']))
    story.append(_p("<i>Avant de partir</i>", styles['h2']))
    story.append(Spacer(1, 0.4 * cm))
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
    story.append(Spacer(1, 1 * cm))
    story.append(_p("Avec toute ma tendresse,", styles['italic']))
    story.append(_p("<i>— Soléna</i>", styles['h3c']))
    story.append(_p("Guide chez Plume Astrale · plume-astrale.fr", styles['small']))


def generate_astrocartographie_pdf(
    first_name: str,
    birth_date_iso: str,
    map_svg: Optional[str],
    chosen_cities: List[Dict[str, Any]],      # 3 villes analysées avec 'enriched' + 'raw'
    bonus_cities: List[Dict[str, Any]],        # 2 villes bonus avec 'enriched'
    synthesis_text: str,
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
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Astrocartographie — Où vivre ta meilleure vie",
        author="Soléna · Plume Astrale",
    )
    styles = _make_styles()
    story: list = []

    _cover(story, styles, first_name or "Voyageur", birth_fr)
    _intro(story, styles)
    _world_map(story, styles, map_svg)

    for c in chosen_cities:
        _city_pages(story, styles, c, c.get('enriched') or {}, is_bonus=False)

    for b in bonus_cities:
        _city_pages(story, styles, b, b.get('enriched') or {}, is_bonus=True)

    _synthesis_page(story, styles, first_name, synthesis_text or "")
    _rituel_signature(story, styles, first_name)

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    buffer.seek(0)
    return buffer.getvalue()
