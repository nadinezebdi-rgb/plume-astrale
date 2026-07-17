"""
Generateur PDF "Pack Karmique + Kabbale" — produit 89 EUR (~40 pages).

Structure :
  1.  Couverture
  2.  Introduction — Le voyage de ton ame
  PARTIE I — Ton Empreinte Karmique (/analysis/karmic, FR natif, 80 sections)
  3.  Ch.1 Les points karmiques (Noeuds, Lilith, Chiron, Vertex, Juno)
  4.  Ch.2 Tes planetes dans les signes
  5.  Ch.3 Tes maisons de vie
  6.  Ch.4 Les dialogues de ton ciel (aspects)
  PARTIE II — Ton Arbre de Vie (/kabbalah/tree-of-life-chart)
  7.  Piliers, 10 Sephiroth, 22 chemins, Da'at
  PARTIE III — La Synthese Croisee (GPT-4o-mini)
  8.  Essence karmique · Mission d'ame · Pratiques d'integration
  9.  Rituels + signature Solena
"""
from __future__ import annotations
from io import BytesIO
from typing import Any, Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak

from services.kabbale_pdf import (
    _p, _make_styles, _bg_canvas, _intro as _kabbale_intro,
    _pillars, _sephiroth_pages, _paths_page, _daat_page,
    _SEPHIROT_FR,
)

_KARMIC_POINTS = ('Nœud Nord', 'Nœud Sud', 'Noeud Nord', 'Noeud Sud', 'Lilith', 'Chiron', 'Vertex', 'Juno')


def _classify_interpretations(interps: List[dict]) -> Dict[str, List[dict]]:
    """Regroupe les 80 sections karmiques en 4 chapitres, dedupliquees par titre."""
    seen = set()
    out = {'points': [], 'signs': [], 'houses': [], 'aspects': []}
    for it in interps or []:
        title = (it.get('title') or '').strip()
        text = (it.get('text') or '').strip()
        if not title or not text or title in seen:
            continue
        seen.add(title)
        if ' — Maison ' in title or ' - Maison ' in title:
            out['houses'].append(it)
        elif ' — ' in title or ' - ' in title:
            if any(title.startswith(p) for p in _KARMIC_POINTS):
                out['points'].append(it)
            else:
                out['signs'].append(it)
        else:
            out['aspects'].append(it)
    return out


def _fmt_date_fr(birth_date_iso: str) -> str:
    if not birth_date_iso or len(birth_date_iso) < 10:
        return birth_date_iso or ''
    try:
        from datetime import datetime
        dt = datetime.strptime(birth_date_iso[:10], '%Y-%m-%d')
        mois = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
                'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
        return f'{dt.day} {mois[dt.month - 1]} {dt.year}'
    except Exception:
        return birth_date_iso


def _cover(story, styles, first_name: str, birth_fr: str):
    story.append(Spacer(1, 4 * cm))
    story.append(_p('PLUME ASTRALE · EDITION PRESTIGE', styles['caption']))
    story.append(Spacer(1, 1.5 * cm))
    story.append(_p('PACK KARMIQUE', styles['title']))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_p('<i>+ KABBALE</i>', styles['subtitle']))
    story.append(Spacer(1, 2 * cm))
    story.append(_p(f'Etabli pour <b>{first_name}</b>', styles['italic']))
    if birth_fr:
        story.append(_p(f'Ne(e) le {birth_fr}', styles['meta']))
    story.append(Spacer(1, 2 * cm))
    story.append(_p(
        '« Ton ame n\'est pas arrivee ici par hasard. Elle porte une memoire, '
        'une dette, une promesse. Ce document est sa carte. »',
        styles['quote']))
    story.append(PageBreak())


def _intro(story, styles):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p('Introduction', styles['caption']))
    story.append(_p("<i>Le voyage de ton ame</i>", styles['h2']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p(
        "Ce document reunit deux traditions millenaires en une seule lecture : "
        "l'<b>astrologie karmique</b>, qui decode la memoire de tes vies anterieures a travers "
        "les Noeuds Lunaires, Saturne, Chiron et Pluton — et la <b>Kabbale</b>, qui cartographie "
        "ta lumiere sur l'Arbre de Vie, ses dix Sephiroth et ses vingt-deux chemins.",
        styles['body']))
    story.append(_p(
        "La premiere partie explore ton <b>empreinte karmique</b> : ce que ton ame a deja appris, "
        "ce qu'elle vient guerir, et la direction qu'elle a choisie pour cette incarnation. "
        "La deuxieme partie revele ton <b>Arbre de Vie kabbalistique</b> personnel. "
        "La troisieme croise les deux lectures dans une <b>synthese unique</b>, redigee "
        "specialement pour toi.",
        styles['body']))
    story.append(Spacer(1, 0.4 * cm))
    story.append(_p(
        "Prends ton temps. Ce n'est pas un document qui se lit — c'est un document qui se medite.",
        styles['italic']))
    story.append(PageBreak())


def _part_divider(story, styles, kicker: str, title: str, subtitle: str):
    story.append(Spacer(1, 8 * cm))
    story.append(_p(kicker, styles['caption']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(_p(title, styles['title']))
    story.append(Spacer(1, 0.5 * cm))
    story.append(_p(f'<i>{subtitle}</i>', styles['italic']))
    story.append(PageBreak())


def _karmic_chapter(story, styles, kicker: str, title: str, lead: str, items: List[dict], per_page: int = 3):
    story.append(Spacer(1, 1.0 * cm))
    story.append(_p(kicker, styles['caption']))
    story.append(_p(f'<i>{title}</i>', styles['h2']))
    story.append(_p(lead, styles['italic']))
    story.append(Spacer(1, 0.3 * cm))
    count = 0
    for it in items:
        if count >= per_page:
            story.append(PageBreak())
            story.append(Spacer(1, 0.8 * cm))
            count = 0
        story.append(_p(it.get('title') or '', styles['h3']))
        story.append(_p(it.get('text') or '', styles['body']))
        story.append(Spacer(1, 0.25 * cm))
        count += 1
    story.append(PageBreak())


def _synthesis_pages(story, styles, synthesis: Dict[str, str]):
    sections = [
        ('essence', 'Synthese I', 'Ton essence karmique',
         "La ou ta memoire d'ame et ton Arbre de Vie racontent la meme histoire."),
        ('mission', 'Synthese II', "Ta mission d'ame",
         "La direction que ton Noeud Nord et ta Sephirah dominante dessinent ensemble."),
        ('pratiques', 'Synthese III', "Tes pratiques d'integration",
         "Comment incarner cette lecture dans ta vie quotidienne."),
    ]
    for key, kicker, title, lead in sections:
        text = (synthesis or {}).get(key) or ''
        if not text:
            continue
        story.append(Spacer(1, 1.0 * cm))
        story.append(_p(kicker, styles['caption']))
        story.append(_p(f'<i>{title}</i>', styles['h2']))
        story.append(_p(lead, styles['italic']))
        story.append(Spacer(1, 0.3 * cm))
        for para in text.split('\n\n'):
            if para.strip():
                story.append(_p(para.strip(), styles['body']))
        story.append(PageBreak())


def _closing(story, styles, first_name: str):
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p('Pour prolonger', styles['caption']))
    story.append(_p("<i>Rituels d'ancrage</i>", styles['h2']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(_p('1. Le rituel du Noeud Nord', styles['accent']))
    story.append(_p(
        "Chaque nouvelle lune, relis la page consacree a ton Noeud Nord. Ecris une action concrete, "
        "meme minuscule, qui va dans sa direction. Ton karma ne se transforme pas par la comprehension — "
        "il se transforme par le geste.",
        styles['body']))
    story.append(_p('2. La meditation des Sephiroth', styles['accent']))
    story.append(_p(
        "Pendant dix jours, consacre cinq minutes chaque matin a une Sephirah de ton Arbre, dans l'ordre "
        "de Malkuth vers Kether. Prononce son nom, observe ce qui remonte, note un mot.",
        styles['body']))
    story.append(_p('3. La lettre a ton ame', styles['accent']))
    story.append(_p(
        "Une fois ce document lu en entier, ecris une lettre a ton ame comme si elle etait une vieille amie "
        "retrouvee. Remercie-la pour le chemin deja parcouru. Scelle la lettre. Rouvre-la dans un an.",
        styles['body']))
    story.append(Spacer(1, 1.2 * cm))
    story.append(_p('Avec toute ma tendresse,', styles['italic']))
    story.append(_p('<i>— Solena</i>', styles['h3']))
    story.append(_p('Guide chez Plume Astrale · plume-astrale.fr', styles['small']))


def generate_pack_karmique_pdf(
    first_name: str,
    birth_date_iso: str,
    karmic: Dict[str, Any],
    tree_of_life: Dict[str, Any],
    synthesis: Dict[str, str],
) -> bytes:
    """Genere le PDF complet Pack Karmique + Kabbale (~40 pages)."""
    kdata = karmic.get('data', karmic) if isinstance(karmic, dict) else {}
    interps = kdata.get('interpretations') or []
    chapters = _classify_interpretations(interps)

    tdata = tree_of_life.get('data', tree_of_life) if isinstance(tree_of_life, dict) else {}
    sephiroth = tdata.get('sephiroth') or {}
    daat = tdata.get('daat') or {}
    paths = tdata.get('paths') or []
    pillar_balance = tdata.get('pillar_balance') or {}
    dominant_sephirah = tdata.get('dominant_sephirah') or ''
    spiritual_focus = tdata.get('spiritual_focus') or ''
    tree_synthesis = tdata.get('synthesis') or ''

    dom_key = str(dominant_sephirah).lower()
    if dom_key in _SEPHIROT_FR:
        h, m, _ = _SEPHIROT_FR[dom_key]
        dominant_display = f'{h} · {m}'
    else:
        dominant_display = dominant_sephirah or ''

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title='Pack Karmique + Kabbale', author='Solena · Plume Astrale',
    )
    styles = _make_styles()
    story: list = []

    fn = first_name or 'Voyageur'
    _cover(story, styles, fn, _fmt_date_fr(birth_date_iso))
    _intro(story, styles)

    # ── PARTIE I : Empreinte Karmique ──
    _part_divider(story, styles, 'Partie I', 'TON EMPREINTE KARMIQUE',
                  "La memoire de ton ame, decodee par les Noeuds Lunaires, Saturne, Chiron et Pluton.")
    if chapters['points']:
        _karmic_chapter(story, styles, 'Chapitre 1', 'Les points karmiques',
                        "Noeuds Lunaires, Lilith, Chiron — les cicatrices et promesses de tes vies anterieures.",
                        chapters['points'], per_page=3)
    if chapters['signs']:
        _karmic_chapter(story, styles, 'Chapitre 2', 'Tes planetes dans les signes',
                        "L'energie brute que chaque planete a choisie pour cette incarnation.",
                        chapters['signs'], per_page=3)
    if chapters['houses']:
        _karmic_chapter(story, styles, 'Chapitre 3', 'Tes maisons de vie',
                        "Les domaines terrestres ou ton karma se joue concretement.",
                        chapters['houses'], per_page=3)
    if chapters['aspects']:
        _karmic_chapter(story, styles, 'Chapitre 4', 'Les dialogues de ton ciel',
                        "Chaque aspect est une conversation entre deux forces de ton ame.",
                        chapters['aspects'], per_page=4)

    # ── PARTIE II : Arbre de Vie ──
    _part_divider(story, styles, 'Partie II', 'TON ARBRE DE VIE',
                  'Ton theme natal cartographie sur les 10 Sephiroth et les 22 chemins de la Kabbale.')
    _kabbale_intro(story, styles)
    _pillars(story, styles, pillar_balance)
    _sephiroth_pages(story, styles, sephiroth)
    _paths_page(story, styles, paths)
    _daat_page(story, styles, daat)
    if dominant_display or tree_synthesis:
        story.append(Spacer(1, 1.2 * cm))
        story.append(_p("Bilan de l'Arbre", styles['caption']))
        story.append(_p('<i>Ta lumiere dominante</i>', styles['h2']))
        if dominant_display:
            story.append(_p(f'Ta Sephirah dominante : <b>{dominant_display}</b>', styles['accent']))
        if spiritual_focus:
            story.append(_p(f'Ton focus spirituel : <i>{spiritual_focus}</i>', styles['italic']))
        if tree_synthesis:
            story.append(Spacer(1, 0.3 * cm))
            story.append(_p(tree_synthesis, styles['body']))
        story.append(PageBreak())

    # ── PARTIE III : Synthese croisee ──
    _part_divider(story, styles, 'Partie III', 'LA SYNTHESE CROISEE',
                  "La ou l'astrologie karmique et la Kabbale se repondent — redigee pour toi seul(e).")
    _synthesis_pages(story, styles, synthesis)
    _closing(story, styles, fn)

    doc.build(story, onFirstPage=_bg_canvas, onLaterPages=_bg_canvas)
    buffer.seek(0)
    return buffer.getvalue()
