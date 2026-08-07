"""
Generateur de PDF "Ton Arbre de Vie Kabbalistique" — pack Kabbale 39 EUR.
Utilise ReportLab + les donnees de /kabbalah/tree-of-life-chart.

Structure du document (~15 pages) :
  1. Couverture
  2. Introduction — L'Arbre de Vie
  3. Ton profil : Sephirah dominante + Piliers
  4-8. Les 10 Sephiroth personnalisees (2 par page)
  9-12. Les 22 Chemins actives
  13. Da'at (la Connaissance cachee)
  14. Synthese spirituelle
  15. Rituels d'integration + signature Solena
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Frame, PageTemplate, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from services import library_images as libimg

# Palette Plume Astrale
NIGHT       = colors.HexColor('#111625')
NIGHT_SOFT  = colors.HexColor('#1A2035')
GOLD        = colors.HexColor('#D4AF37')
GOLD_LIGHT  = colors.HexColor('#E8C766')
LAVENDER    = colors.HexColor('#E3D7FF')
CREAM       = colors.HexColor('#F5EEE0')
MUTED       = colors.HexColor('#9089B5')

# Traductions des Sephirot (nom hebreu -> FR poetique)
_SEPHIROT_FR = {
    'kether':    ("Kether", "Couronne", "La Volonte divine, ton essence pure."),
    'chokmah':   ("Chokmah", "Sagesse", "L'inspiration brute, l'eclair createur."),
    'binah':     ("Binah", "Comprehension", "La forme qui accueille l'idee, la Mere cosmique."),
    'chesed':    ("Chesed", "Misericorde", "La generosite qui construit, la mansuetude."),
    'geburah':   ("Geburah", "Rigueur", "La discipline juste, le courage de trancher."),
    'tiphareth': ("Tiphareth", "Beaute", "L'harmonie du coeur, ton centre solaire."),
    'netzach':   ("Netzach", "Victoire", "La passion qui persiste, l'elan amoureux."),
    'hod':       ("Hod", "Splendeur", "La pensee raffinee, la communication juste."),
    'yesod':     ("Yesod", "Fondation", "L'inconscient, les reves, la memoire de l'ame."),
    'malkuth':   ("Malkuth", "Royaume", "L'incarnation, le corps, ta manifestation physique."),
    'daat':      ("Da'at", "Connaissance", "L'abime intime, la conscience du pont invisible."),
}


import re

_ALLOWED_TAGS_RE = re.compile(r'</?([bi])>', re.IGNORECASE)


def _p(text: str, style: ParagraphStyle) -> Paragraph:
    """Helper — wrap texte + gestion caracteres speciaux.
    Preserve les balises <b> et <i> retournees par l'API v3 (interpretations)
    pour que ReportLab les rende en gras/italique."""
    if text is None:
        text = ""
    t = str(text)
    # 1) Escape uniquement & (ampersand)
    t = t.replace('&', '&amp;')
    # 2) Placeholder les balises autorisees pour eviter double-escape
    tags = []
    def _hold(m):
        tags.append(m.group(0))
        return f'\x00TAG{len(tags)-1}\x00'
    t = _ALLOWED_TAGS_RE.sub(_hold, t)
    # 3) Escape les autres < >
    t = t.replace('<', '&lt;').replace('>', '&gt;')
    # 4) Restore les balises autorisees
    for i, tag in enumerate(tags):
        t = t.replace(f'\x00TAG{i}\x00', tag.lower())
    return Paragraph(t, style)


def _bg_canvas(canv, doc):
    """Fond prestige unifié Plume Astrale (cadre or + soleil ornemental + footer éditorial)."""
    from services.pdf_bg import make_bg_canvas as _mkbg
    return _mkbg('Ton Arbre de Vie')(canv, doc)


# ── Styles ──
def _make_styles():
    return {
        'title': ParagraphStyle('title', fontName='Helvetica', fontSize=32, textColor=GOLD,
                                alignment=TA_CENTER, leading=38, spaceAfter=10),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica-Oblique', fontSize=17,
                                    textColor=CREAM, alignment=TA_CENTER, leading=22, spaceAfter=8),
        'caption': ParagraphStyle('caption', fontName='Helvetica', fontSize=8, textColor=GOLD,
                                   alignment=TA_CENTER, leading=10),
        'h2': ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=22, textColor=GOLD_LIGHT,
                              spaceBefore=6, spaceAfter=10, leading=26),
        'h3': ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=15, textColor=GOLD,
                              spaceBefore=8, spaceAfter=6, leading=18),
        'meta': ParagraphStyle('meta', fontName='Helvetica', fontSize=9, textColor=MUTED,
                                leading=12),
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
    }


def _lib_image(story: list, path: Optional[str], width_cm: float = 6.0, hAlign: str = 'CENTER') -> None:
    """Ajoute une image de la bibliothèque au flowable story (silencieux si path=None)."""
    if not path:
        return
    try:
        img = Image(path, width=width_cm*cm, height=width_cm*cm)
        img.hAlign = hAlign
        story.append(img)
    except Exception:
        pass


def _cover(story, styles, first_name: str, birth_date: str, dominant_seph: str, spiritual_focus: str, birth_iso: str = ''):
    story.append(Spacer(1, 1.8*cm))
    story.append(_p("PLUME ASTRALE · KABBALE", styles['caption']))
    story.append(Spacer(1, 0.5*cm))
    # Illustration Arbre de Vie (Etz Chaim) — hero centrée
    from reportlab.platypus import Image as _RLImage
    from pathlib import Path as _Path
    _cover_img = _Path('/app/backend/assets/pdf_covers/arbre_de_vie_cover.png')
    if _cover_img.exists():
        try:
            img = _RLImage(str(_cover_img), width=8.5*cm, height=8.5*cm, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
        except Exception:
            _lib_image(story, libimg.sign_from_date(birth_iso, size=2048), width_cm=6.5)
    else:
        _lib_image(story, libimg.sign_from_date(birth_iso, size=2048), width_cm=6.5)
    story.append(Spacer(1, 0.5*cm))
    story.append(_p("TON ARBRE DE VIE", styles['title']))
    story.append(Spacer(1, 0.2*cm))
    story.append(_p("<i>KABBALISTIQUE</i>", styles['subtitle']))
    story.append(Spacer(1, 1.0*cm))
    story.append(_p(f"Etabli pour <b>{first_name}</b>", styles['italic']))
    if birth_date:
        story.append(_p(f"Ne(e) le {birth_date}", styles['meta']))
    story.append(Spacer(1, 0.8*cm))
    if dominant_seph:
        story.append(_p("Ta Sephirah dominante", styles['caption']))
        story.append(Spacer(1, 0.2*cm))
        story.append(_p(f"<b>{dominant_seph}</b>", styles['h2']))
    if spiritual_focus:
        story.append(_p(f"« {spiritual_focus} »", styles['quote']))
    story.append(PageBreak())


def _intro(story, styles):
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Introduction", styles['caption']))
    story.append(_p("<i>L'Arbre de Vie</i>", styles['h2']))
    story.append(Spacer(1, 0.3*cm))
    story.append(_p(
        "L'Arbre de Vie kabbalistique est une carte spirituelle vieille de deux mille ans. "
        "Il decrit dix spheres de conscience — les <b>Sephiroth</b> — reliees par vingt-deux <b>chemins</b>, "
        "qui representent la descente de la Lumiere divine dans le monde manifeste.",
        styles['body']))
    story.append(_p(
        "Dans cette lecture, ton theme natal a ete cartographie sur cet Arbre : chaque planete de ta naissance "
        "occupe une Sephirah, chaque signe active un chemin. Le resultat est un portrait spirituel unique — "
        "les forces divines qui parlent le plus fort en toi, tes zones d'apprentissage, et le sens profond "
        "de ton incarnation.",
        styles['body']))
    story.append(Spacer(1, 0.4*cm))
    story.append(_p(
        "Trois piliers structurent l'Arbre : la <b>Rigueur</b> (a gauche, la forme, la contrainte), "
        "la <b>Misericorde</b> (a droite, l'expansion, la generosite), et le <b>Milieu</b> (au centre, l'harmonie, "
        "la conscience). Ton equilibre entre ces trois axes revele ta trajectoire d'ame.",
        styles['body']))
    story.append(PageBreak())


def _pillars(story, styles, pillar_balance: dict):
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Vue d'ensemble", styles['caption']))
    story.append(_p("<i>Ton equilibre des Piliers</i>", styles['h2']))
    story.append(Spacer(1, 0.3*cm))
    if not pillar_balance:
        story.append(_p("Analyse d'equilibre non disponible.", styles['body']))
    else:
        sev = pillar_balance.get('severity_count') or 0
        mer = pillar_balance.get('mercy_count') or 0
        mid = pillar_balance.get('middle_count') or 0
        dom = pillar_balance.get('dominant_pillar', '')
        score = pillar_balance.get('balance_score')
        dom_fr = {'severity': 'Rigueur', 'mercy': 'Misericorde', 'middle': 'Milieu'}.get(dom, dom.title())
        story.append(_p(f"<b>{sev}</b> planetes sur le pilier de la <b>Rigueur</b>", styles['body']))
        story.append(_p(f"<b>{mer}</b> planetes sur le pilier de la <b>Misericorde</b>", styles['body']))
        story.append(_p(f"<b>{mid}</b> planetes sur le pilier du <b>Milieu</b>", styles['body']))
        story.append(Spacer(1, 0.4*cm))
        story.append(_p(f"Pilier dominant : <b>{dom_fr}</b>", styles['accent']))
        if score is not None:
            try:
                story.append(_p(f"Score d'equilibre global : <b>{float(score):.1f} / 100</b>", styles['accent']))
            except Exception:
                pass
        interp = pillar_balance.get('interpretation') or ''
        if interp:
            story.append(Spacer(1, 0.3*cm))
            story.append(_p(interp, styles['body']))
    story.append(PageBreak())


def _sephiroth_pages(story, styles, sephiroth, dominant_planet: str = ''):
    """Rend chaque Sephirah avec ses attributs personnalises. sephiroth = list of dicts."""
    if not sephiroth or not isinstance(sephiroth, list):
        return
    story.append(Spacer(1, 1.0*cm))
    story.append(_p("Chapitre I", styles['caption']))
    story.append(_p("<i>Les 10 Sephiroth</i>", styles['h2']))
    story.append(Spacer(1, 0.4*cm))
    # Image d'ouverture : planète dominante (via Sephirah dominante) sinon Soleil
    _lib_image(story, libimg.planet(dominant_planet or 'sun'), width_cm=5.0)
    story.append(Spacer(1, 0.3*cm))
    story.append(_p(
        "Chaque Sephirah est une sphere de conscience. Voici comment ton theme natal les active.",
        styles['italic']))
    story.append(PageBreak())

    count_on_page = 0
    for sf in sephiroth:
        if not isinstance(sf, dict):
            continue
        # english "Crown" -> match _SEPHIROT_FR key
        eng = (sf.get('english') or sf.get('meaning') or '').strip().lower().replace("'", '').replace(' ', '')
        # Map les noms EN vers cle FR
        en_to_key = {
            'crown': 'kether', 'wisdom': 'chokmah', 'understanding': 'binah',
            'mercy': 'chesed', 'severity': 'geburah', 'judgement': 'geburah', 'judgment': 'geburah',
            'beauty': 'tiphareth', 'victory': 'netzach', 'splendor': 'hod', 'splendour': 'hod',
            'foundation': 'yesod', 'kingdom': 'malkuth',
        }
        key = en_to_key.get(eng, eng)
        fr = _SEPHIROT_FR.get(key, (sf.get('english') or 'Sephirah', '', ''))
        heb_name, meaning, poetic = fr

        # planet peut etre dict per system
        planet_raw = sf.get('planet')
        if isinstance(planet_raw, dict):
            planet = planet_raw.get('modern_halevi') or planet_raw.get('classical') or planet_raw.get('golden_dawn') or ''
        else:
            planet = planet_raw or ''
        archangel = sf.get('archangel') or ''
        divine_name = sf.get('divine_name') or sf.get('divine_names') or ''
        if isinstance(divine_name, dict):
            divine_name = divine_name.get('modern_halevi') or divine_name.get('classical') or ''
        virtue = sf.get('virtue') or ''
        vice = sf.get('vice') or ''
        planets_present = sf.get('planets_present') or sf.get('planets') or []
        if isinstance(planets_present, dict):
            planets_present = list(planets_present.values())
        interp = sf.get('interpretation') or sf.get('description') or ''

        if count_on_page >= 2:
            story.append(PageBreak())
            count_on_page = 0
        story.append(_p(f"{heb_name} · <i>{meaning}</i>", styles['h3']))
        if poetic:
            story.append(_p(poetic, styles['italic']))
        meta_bits = []
        if planet: meta_bits.append(f"Planete : <b>{planet}</b>")
        if archangel: meta_bits.append(f"Archange : {archangel}")
        if divine_name: meta_bits.append(f"Nom divin : {divine_name}")
        if meta_bits:
            story.append(_p(" · ".join(meta_bits), styles['meta']))
        if virtue or vice:
            story.append(_p(f"Vertu : <i>{virtue}</i>   ·   Vice : <i>{vice or '—'}</i>", styles['meta']))
        if planets_present:
            names = ", ".join(str(p) for p in planets_present if p)
            if names:
                story.append(_p(f"<b>Tes planetes ici :</b> {names}", styles['accent']))
        if interp:
            story.append(_p(interp, styles['body']))
        story.append(Spacer(1, 0.3*cm))
        count_on_page += 1
    story.append(PageBreak())


def _paths_page(story, styles, paths: list):
    """Chemins actives (is_activated=true)."""
    story.append(Spacer(1, 1.0*cm))
    story.append(_p("Chapitre II", styles['caption']))
    story.append(_p("<i>Tes chemins actives</i>", styles['h2']))
    story.append(Spacer(1, 0.3*cm))
    # Image d'ouverture : premier tarot activé
    active_paths_all = [p for p in (paths or []) if p.get('is_activated')]
    first_tarot = None
    if active_paths_all:
        first_tarot = (active_paths_all[0].get('tarot_card') or '').strip()
    _lib_image(story, libimg.tarot(first_tarot) if first_tarot else None, width_cm=5.0)
    story.append(Spacer(1, 0.3*cm))
    story.append(_p(
        "Chaque chemin est une force zodiacale qui relie deux Sephiroth. "
        "Ceux qui suivent sont ouverts par tes placements planetaires.",
        styles['italic']))
    story.append(Spacer(1, 0.3*cm))

    active = active_paths_all
    if not active:
        story.append(_p("Aucun chemin fortement active pour l'instant — ta lumiere circule surtout dans les Sephiroth.", styles['body']))
        story.append(PageBreak())
        return

    for p in active[:12]:
        hebrew = p.get('hebrew_letter') or ''
        tarot = p.get('tarot_card') or ''
        zodiac = p.get('zodiac') or p.get('element') or ''
        interp = p.get('interpretation') or p.get('description') or ''
        activating = p.get('activating_bodies') or []
        title_bits = []
        if hebrew: title_bits.append(hebrew)
        if tarot: title_bits.append(f"<i>{tarot}</i>")
        if zodiac: title_bits.append(zodiac)
        story.append(_p(" · ".join(title_bits) or "Chemin", styles['h3']))
        if activating:
            story.append(_p(f"Active par : <b>{', '.join(str(x) for x in activating)}</b>", styles['meta']))
        if interp:
            story.append(_p(interp, styles['body']))
        story.append(Spacer(1, 0.25*cm))
    story.append(PageBreak())


def _daat_page(story, styles, daat: dict):
    """Da'at — la Connaissance cachee (11eme Sephirah)."""
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Chapitre III", styles['caption']))
    story.append(_p("<i>Da'at — la Connaissance</i>", styles['h2']))
    story.append(_p(
        "Entre les mondes superieurs et le champ manifeste, il existe un pont invisible : Da'at, "
        "la Sephirah non-numerique. Elle represente ton eveil interieur.",
        styles['italic']))
    story.append(Spacer(1, 0.4*cm))
    if daat:
        interp = daat.get('interpretation') or daat.get('description') or ''
        if interp:
            story.append(_p(interp, styles['body']))
        planets_present = daat.get('planets_present') or []
        if planets_present:
            story.append(_p(f"<b>Tes planetes de Da'at :</b> {', '.join(str(p) for p in planets_present)}", styles['accent']))
    else:
        story.append(_p("Ta connexion a Da'at reste discrete — elle s'eveillera par ta pratique.", styles['body']))
    story.append(PageBreak())


def _synthesis(story, styles, dominant_seph: str, spiritual_focus: str, synthesis: str):
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Synthese", styles['caption']))
    story.append(_p("<i>Ton chemin de vie</i>", styles['h2']))
    story.append(Spacer(1, 0.3*cm))
    if dominant_seph:
        story.append(_p(f"Ta Sephirah dominante : <b>{dominant_seph}</b>", styles['accent']))
    if spiritual_focus:
        story.append(_p(f"Ton focus spirituel : <i>{spiritual_focus}</i>", styles['italic']))
    story.append(Spacer(1, 0.3*cm))
    if synthesis:
        story.append(_p(synthesis, styles['body']))
    else:
        story.append(_p(
            "Ton Arbre de Vie te montre ou circule ta Lumiere. Chaque Sephirah que tu as activee est un "
            "muscle spirituel a exercer, chaque chemin, une porte a franchir. Le voyage n'est pas de "
            "chercher a l'exterieur, mais d'incarner ce qui vibre deja en toi.",
            styles['body']))
    story.append(PageBreak())


def _rituels_signature(story, styles, first_name: str, dominant_seph: str):
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Pour prolonger", styles['caption']))
    story.append(_p("<i>Rituels d'integration</i>", styles['h2']))
    story.append(Spacer(1, 0.3*cm))
    story.append(_p(
        "Voici trois pratiques simples pour ancrer ta lecture kabbalistique dans ton quotidien.",
        styles['body']))
    story.append(_p("1. La meditation des sept jours", styles['accent']))
    story.append(_p(
        "Pendant sept matins consecutifs, dedie 5 minutes a une Sephirah de ton Arbre. Prononce son nom "
        "hebreu a voix basse. Observe ce qui remonte.",
        styles['body']))
    story.append(_p("2. Le journal de piliers", styles['accent']))
    story.append(_p(
        "Chaque soir, note une action vecue selon la Rigueur (limites tenues), la Misericorde (generosite offerte) "
        "et le Milieu (moment de presence pure). Tu verras ton axe d'ame se dessiner.",
        styles['body']))
    story.append(_p("3. La lecture cyclique", styles['accent']))
    story.append(_p(
        "Reviens a ce document tous les six mois. Tu constateras que certaines pages resonnent differemment — "
        "signe que ta conscience a evolue le long de l'Arbre.",
        styles['body']))
    story.append(Spacer(1, 1.2*cm))
    story.append(_p("Avec toute ma tendresse,", styles['italic']))
    story.append(_p("<i>— Solena</i>", styles['h3']))
    story.append(_p("Guide chez Plume Astrale · plume-astrale.fr", styles['small']))


def _generate_kabbale_impl(
    first_name: str,
    birth_date_iso: str,
    tree_of_life: Dict[str, Any],
    ai_sections: Optional[Dict[str, str]] = None,
) -> bytes:
    """Genere le PDF Kabbale complet a partir des donnees /kabbalah/tree-of-life-chart.

    Args:
        first_name: Prenom pour la personnalisation
        birth_date_iso: Date de naissance ISO (YYYY-MM-DD) — sera formattee FR
        tree_of_life: Dictionnaire retourne par astrology-api.io v3 /kabbalah/tree-of-life-chart
                      Contient : sephiroth, daat, paths, pillar_balance, dominant_sephirah,
                                 spiritual_focus, synthesis, system, tradition
        ai_sections: sections narratives enrichies IA (optionnel)
    """
    data = tree_of_life.get('data', tree_of_life) if isinstance(tree_of_life, dict) else {}
    sephiroth = data.get('sephiroth') or {}
    daat = data.get('daat') or {}
    paths = data.get('paths') or []
    pillar_balance = data.get('pillar_balance') or {}
    dominant_sephirah = data.get('dominant_sephirah') or ''
    spiritual_focus = data.get('spiritual_focus') or ''
    synthesis = data.get('synthesis') or ''

    # Traduction FR de dominant_sephirah (ex: "Tiphareth" -> "Tiphareth · Beaute")
    dom_key = str(dominant_sephirah).lower()
    if dom_key in _SEPHIROT_FR:
        h, m, _ = _SEPHIROT_FR[dom_key]
        dominant_display = f"{h} · {m}"
    else:
        dominant_display = dominant_sephirah or ""

    # Formatage date FR
    birth_fr = birth_date_iso or ""
    if birth_date_iso and len(birth_date_iso) >= 10:
        try:
            from datetime import datetime
            dt = datetime.strptime(birth_date_iso[:10], '%Y-%m-%d')
            mois_fr = ['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre']
            birth_fr = f"{dt.day} {mois_fr[dt.month-1]} {dt.year}"
        except Exception:
            birth_fr = birth_date_iso

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Ton Arbre de Vie Kabbalistique", author="Solena · Plume Astrale",
    )
    styles = _make_styles()

    story: list = []
    # Extraire la planète dominante depuis les Sephiroth
    dominant_planet = ''
    try:
        if isinstance(sephiroth, list):
            for sf in sephiroth:
                if not isinstance(sf, dict):
                    continue
                if str(sf.get('english') or '').strip().lower() == str(dominant_sephirah).strip().lower():
                    pr = sf.get('planet')
                    if isinstance(pr, dict):
                        dominant_planet = pr.get('modern_halevi') or pr.get('classical') or ''
                    else:
                        dominant_planet = pr or ''
                    break
    except Exception:
        dominant_planet = ''

    _cover(story, styles, first_name or "Voyageur", birth_fr, dominant_display, spiritual_focus, birth_iso=birth_date_iso or '')
    _intro(story, styles)
    _pillars(story, styles, pillar_balance)
    _sephiroth_pages(story, styles, sephiroth, dominant_planet=str(dominant_planet or ''))
    _paths_page(story, styles, paths)
    _daat_page(story, styles, daat)
    _synthesis(story, styles, dominant_display, spiritual_focus, synthesis)

    # Enrichissement IA : insere des sections narratives premium avant les rituels
    if ai_sections:
        _append_ai_sections(story, styles, ai_sections, report_type='kabbale')

    _rituels_signature(story, styles, first_name or "Voyageur", dominant_display)

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    buffer.seek(0)
    return buffer.getvalue()


def _append_ai_sections(story, styles, ai_sections: Dict[str, str], report_type: str) -> None:
    """Ajoute les sections narratives IA au story SimpleDocTemplate.

    Reutilisable pour kabbale, pack_karmique et autres PDFs SimpleDocTemplate.
    """
    from reportlab.platypus import PageBreak, Paragraph, Spacer
    from services.report_ai_enrichment import get_expected_sections
    # Titres FR lisibles par cle
    LABELS = {
        # kabbale
        'introduction': "Introduction personnelle",
        'sephiroth_principales': "Tes 3 séphiroth dominantes",
        'chemin_kabbalistique': "Ton chemin kabbalistique",
        'gematria_nom': "La Gematria de ton nom",
        'lettres_hebraiques': "Tes lettres hébraïques clés",
        'invitation_finale': "Ton invitation finale",
        # pack_karmique
        'synthese': "Synthèse karmique",
        'axe_karmique_principal': "Ton axe karmique principal",
        'liens_karmiques': "Tes liens karmiques",
        # mediumnite
        'clairs': "Tes quatre clairs",
        'guides': "Tes guides et protecteurs",
        'blocages': "Blocages énergétiques",
        'pratiques': "Pratiques d'éveil",
        # karma_destin (au cas ou)
        'noeud_nord': "Ton Nœud Nord — chemin",
        'noeud_sud': "Ton Nœud Sud — héritage",
        'saturne': "Saturne — leçons karmiques",
        'chiron': "Chiron — blessure sacrée",
        'pluton': "Pluton — transformation",
        'karma_generationnel': "Karma générationnel",
        'dates_cles': "Dates-clés karmiques",
    }
    expected = get_expected_sections(report_type)
    if not expected:
        expected = list(ai_sections.keys())
    heading = styles.get('h2') or styles.get('heading') or styles.get('Heading')
    body = styles.get('body') or styles.get('BodyText') or styles.get('Body')
    for key in expected:
        content = ai_sections.get(key)
        if not content:
            continue
        story.append(PageBreak())
        story.append(Paragraph(f'✦ {LABELS.get(key, key.replace("_", " ").title())} ✦', heading))
        story.append(Spacer(0, 0.3 * 28.35))  # 0.3 cm
        story.append(Paragraph(content, body))


def generate_kabbale_pdf(
    first_name: str,
    birth_date_iso: str,
    tree_of_life: Dict[str, Any],
    ai_sections: Optional[Dict[str, str]] = None,
) -> bytes:
    return _generate_kabbale_impl(first_name, birth_date_iso, tree_of_life, ai_sections)


async def generate_kabbale_pdf_ai(
    first_name: str,
    birth_date_iso: str,
    tree_of_life: Dict[str, Any],
) -> bytes:
    """Version enrichie IA (voix Soléna, 6 sections premium).

    Le toggle admin `ai_enrichment_disabled` est géré au niveau d'enrich_report :
    - IA ON  → contenu généré par GPT-5.4
    - IA OFF → fallback statique riche pré-rédigé (pages étoffées)
    """
    try:
        from services.report_ai_enrichment import enrich_report
        ai_sections = await enrich_report(
            report_type='kabbale',
            prenom=first_name,
            birth_date_iso=birth_date_iso,
            context={'tree_of_life': tree_of_life},
        )
    except Exception:
        ai_sections = {}
    return _generate_kabbale_impl(first_name, birth_date_iso, tree_of_life, ai_sections)
