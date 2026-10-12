"""kabbale_manuscript_builder — Bâtit un Manuscript book_engine_v2 (print blanc)
=============================================================================

Migration Kabbale legacy `kabbale_pdf.py` (ReportLab, fond sombre) → book_engine_v2
(Chromium print-to-pdf A5 blanc, en cohérence avec le Thème Natal payant).

FEATURE FLAG : cette route n'est activée que si `USE_V2_KABBALE_ENGINE=1` dans
l'env backend. Sinon on retombe sur le legacy. Le legacy reste production tant
que la parité visuelle n'a pas été validée en dev.

Input : mêmes données que `generate_kabbale_pdf` :
  - first_name : str
  - birth_date_iso : str (YYYY-MM-DD)
  - tree_of_life : dict avec `sephiroth`, `paths`, `daat`, `pillar_balance`,
    `dominant_sephirah`, `spiritual_focus`, `synthesis`, `tree_of_life_meaning`
  - ai_sections : dict optionnel {introduction, sephiroth_principales, ...}

Output : Manuscript prêt pour `render_manuscript_to_pdf_v2(profile='print')`.

Cette version minimale garantit la STRUCTURE (7 chapitres numérotés, TOC
automatique via le renderer, pages numérotées, folio). Le contenu détaillé
Sephiroth/Chemins/Da'at est rendu en paragraphes plutôt qu'en tables ornées
— parité visuelle à finaliser dans une prochaine itération.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.book_engine_shared.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)

logger = logging.getLogger(__name__)


# ─── Traductions Sephirot (miroir de kabbale_pdf._SEPHIROT_FR) ─────────
_SEPHIROT_FR = {
    'kether':    ('Kether', 'Couronne', "La Volonté divine, ton essence pure."),
    'chokmah':   ('Chokmah', 'Sagesse', "L'inspiration brute, l'éclair créateur."),
    'binah':     ('Binah', 'Compréhension', "La forme qui accueille l'idée, la Mère cosmique."),
    'chesed':    ('Chesed', 'Miséricorde', "La générosité qui construit, la mansuétude."),
    'geburah':   ('Geburah', 'Rigueur', "La discipline juste, le courage de trancher."),
    'tiphareth': ('Tiphareth', 'Beauté', "L'harmonie du cœur, ton centre solaire."),
    'netzach':   ('Netzach', 'Victoire', "La passion qui persiste, l'élan amoureux."),
    'hod':       ('Hod', 'Splendeur', "La pensée raffinée, la communication juste."),
    'yesod':     ('Yesod', 'Fondation', "L'inconscient, les rêves, la mémoire de l'âme."),
    'malkuth':   ('Malkuth', 'Royaume', "L'incarnation, le corps, ta manifestation physique."),
}


def _fmt_date_fr(date_iso: str) -> str:
    if not date_iso:
        return ''
    try:
        parts = date_iso.split('-')
        y, mo, d = parts[0], int(parts[1]), int(parts[2])
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        return f'{d} {months[mo - 1]} {y}'
    except Exception:
        return date_iso


def _chapter(roman: str, order: int, title: str, kicker: str,
             blocks: List[ChapterBlock]) -> Chapter:
    all_blocks = [ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': roman, 'title': title, 'kicker': kicker,
    })] + blocks + [ChapterBlock(BlockKind.FEATHER, {})]
    return Chapter(
        slug=f'kabbale-{order}', title=title, kicker=kicker,
        roman_num=roman, order=order, blocks=all_blocks,
    )


def _para(text: str) -> ChapterBlock:
    return ChapterBlock(BlockKind.PARAGRAPH, {'text': text})


def _h2(text: str) -> ChapterBlock:
    return ChapterBlock(BlockKind.H2, {'text': text})


def _paras(text: str) -> List[ChapterBlock]:
    """Découpe un texte multi-para (double-newline) en blocs PARAGRAPH."""
    return [_para(p.strip()) for p in (text or '').split('\n\n') if p.strip()]


def build_kabbale_manuscript(
    *,
    first_name: str,
    birth_date_iso: str,
    tree_of_life: Dict[str, Any],
    ai_sections: Optional[Dict[str, str]] = None,
    user_email: str = '',
    session_id: str = '',
) -> Manuscript:
    """Construit un Manuscript book_engine_v2 pour le PDF Kabbale."""
    first_name = (first_name or 'Voyageur').strip() or 'Voyageur'
    ai_sections = ai_sections or {}

    sephiroth = tree_of_life.get('sephiroth') or []
    paths = tree_of_life.get('paths') or []
    daat = tree_of_life.get('daat') or {}
    pillar_balance = tree_of_life.get('pillar_balance') or {}
    dominant_sephirah = tree_of_life.get('dominant_sephirah') or ''
    spiritual_focus = tree_of_life.get('spiritual_focus') or ''
    synthesis = tree_of_life.get('synthesis') or ''
    tree_meaning = tree_of_life.get('tree_of_life_meaning') or ''

    dominant_fr = _SEPHIROT_FR.get(str(dominant_sephirah).lower(), (dominant_sephirah, '', ''))[0]

    chapters: List[Chapter] = []

    # ── Chapitre I — L'Arbre de Vie ───────────────────────────────────
    intro_blocks: List[ChapterBlock] = []
    birth_fr = _fmt_date_fr(birth_date_iso)
    if birth_fr:
        intro_blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': f'<span class="lede-date">Né·e le {birth_fr}.</span>',
            'raw': True,
        }))
    if ai_sections.get('introduction'):
        intro_blocks.extend(_paras(ai_sections['introduction']))
    elif tree_meaning:
        intro_blocks.extend(_paras(tree_meaning))
    else:
        intro_blocks.append(_para(
            "L'Arbre de Vie kabbalistique est le schéma vivant qui relie "
            'les dix sphères de conscience (les Sephiroth) et les vingt-deux '
            "chemins qui les traversent. Il cartographie ton évolution "
            "intérieure — ce qui te porte, ce qui te freine, ce qui reste "
            'à explorer.'
        ))
    chapters.append(_chapter('I', 1, "L'Arbre de Vie kabbalistique",
                             "Comprendre l'ancien schéma", intro_blocks))

    # ── Chapitre II — Trois piliers ───────────────────────────────────
    piliers_blocks: List[ChapterBlock] = []
    for pillar, label in [('severity', 'Rigueur'), ('mildness', 'Équilibre'), ('mercy', 'Miséricorde')]:
        val = pillar_balance.get(pillar)
        if val is not None:
            piliers_blocks.append(_h2(f'Pilier de la {label}'))
            piliers_blocks.append(_para(f'Force : {val}%.'))
    if not piliers_blocks:
        piliers_blocks.append(_para(
            'Les trois piliers de ton Arbre équilibrent Rigueur, Miséricorde et harmonie centrale.'
        ))
    chapters.append(_chapter('II', 2, 'Tes trois piliers',
                             'Rigueur, Miséricorde, Équilibre', piliers_blocks))

    # ── Chapitre III — 10 Sephiroth ───────────────────────────────────
    seph_blocks: List[ChapterBlock] = []
    if isinstance(sephiroth, list):
        for sf in sephiroth:
            if not isinstance(sf, dict):
                continue
            key = str(sf.get('english') or '').lower()
            name_fr, subtitle, description = _SEPHIROT_FR.get(key, (sf.get('name', key.title()), '', ''))
            title = f'{name_fr} · {subtitle}' if subtitle else name_fr
            seph_blocks.append(_h2(title))
            interpretation = sf.get('interpretation') or description
            if interpretation:
                seph_blocks.extend(_paras(str(interpretation)))
    if ai_sections.get('sephiroth_principales'):
        seph_blocks.append(_h2('Tes trois Sephiroth dominantes'))
        seph_blocks.extend(_paras(ai_sections['sephiroth_principales']))
    chapters.append(_chapter('III', 3, 'Les 10 Sephiroth',
                             'Les dix sphères de conscience', seph_blocks))

    # ── Chapitre IV — 22 Chemins ──────────────────────────────────────
    paths_blocks: List[ChapterBlock] = []
    if isinstance(paths, list) and paths:
        # Ne rend que les 6 chemins les plus significatifs pour tenir 15 pages
        for p in paths[:6]:
            if not isinstance(p, dict):
                continue
            letter = p.get('letter') or p.get('hebrew_letter') or ''
            title = p.get('title') or p.get('name') or 'Chemin'
            if letter:
                paths_blocks.append(_h2(f'{letter} · {title}'))
            else:
                paths_blocks.append(_h2(str(title)))
            interp = p.get('interpretation') or p.get('meaning') or ''
            if interp:
                paths_blocks.extend(_paras(str(interp)))
    if ai_sections.get('chemin_kabbalistique'):
        paths_blocks.append(_h2('Ton chemin kabbalistique'))
        paths_blocks.extend(_paras(ai_sections['chemin_kabbalistique']))
    if not paths_blocks:
        paths_blocks.append(_para(
            'Les vingt-deux chemins hébraïques dessinent la trame invisible qui relie tes Sephiroth.'
        ))
    chapters.append(_chapter('IV', 4, 'Les 22 chemins',
                             'Les sentiers de la Lumière', paths_blocks))

    # ── Chapitre V — Da'at ────────────────────────────────────────────
    daat_blocks: List[ChapterBlock] = []
    if daat.get('description'):
        daat_blocks.extend(_paras(str(daat['description'])))
    if daat.get('interpretation'):
        daat_blocks.extend(_paras(str(daat['interpretation'])))
    if not daat_blocks:
        daat_blocks.append(_para(
            "Da'at, la sphère invisible, est le pont entre le Divin et l'incarnation. "
            "Elle n'apparaît pas sur l'Arbre — mais elle traverse tes silences."
        ))
    chapters.append(_chapter('V', 5, "Da'at, la sphère invisible",
                             "L'abîme et la connaissance", daat_blocks))

    # ── Chapitre VI — Synthèse ────────────────────────────────────────
    synth_blocks: List[ChapterBlock] = []
    if dominant_fr:
        synth_blocks.append(_para(
            f'Ta Sephirah dominante est <b>{dominant_fr}</b>.'
        ))
    if spiritual_focus:
        synth_blocks.append(_para(f'<b>Focus spirituel :</b> {spiritual_focus}'))
    if synthesis:
        synth_blocks.extend(_paras(synthesis))
    if ai_sections.get('invitation_finale'):
        synth_blocks.append(_h2('Ton invitation finale'))
        synth_blocks.extend(_paras(ai_sections['invitation_finale']))
    chapters.append(_chapter('VI', 6, 'Synthèse',
                             'Le message de Soléna', synth_blocks))

    # ── Chapitre VII — Rituels ────────────────────────────────────────
    ritual_blocks: List[ChapterBlock] = [_para(
        f'{first_name}, ton Arbre de Vie est une carte à honorer chaque jour. '
        f'Prends un instant, respire, et laisse {dominant_fr or "ta Sephirah dominante"} '
        'te rappeler ce qui t\'appelle en ce moment.'
    )]
    chapters.append(_chapter('VII', 7, 'Rituels de communion',
                             'Prières pour honorer ton Arbre', ritual_blocks))

    return Manuscript(
        session_id=session_id or f'kabbale-{first_name.lower()}-{int(datetime.now(timezone.utc).timestamp())}',
        user_email=user_email,
        first_name=first_name,
        birth_data=BirthData(date_iso=birth_date_iso or '', time_hhmm=None, city='', country_code='FR'),
        astro_data={'dominant_sephirah': dominant_sephirah, 'engine': 'book_engine_v2',
                    'book_title': 'Ton Arbre de Vie Kabbalistique'},
        edition=Edition.NUMERIQUE,
        chapters=chapters,
        design_version='plume-astrale-v2-print',
        created_at=datetime.now(timezone.utc),
    )
