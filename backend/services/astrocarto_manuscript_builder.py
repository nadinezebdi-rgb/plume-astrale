"""astrocarto_manuscript_builder — Bâtit un Manuscript book_engine_v2 (print blanc)
=================================================================================

Migration Astrocartographie legacy `astrocartographie_pdf.py` (ReportLab, fond
sombre) → book_engine_v2 (Chromium A5 blanc, cohérent avec le Thème Natal payant).

FEATURE FLAG : `USE_V2_ASTROCARTO_ENGINE=1` dans l'env backend. Sinon → legacy.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.book_engine_shared.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)

logger = logging.getLogger(__name__)


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
        slug=f'astrocarto-{order}', title=title, kicker=kicker,
        roman_num=roman, order=order, blocks=all_blocks,
    )


def _h2(text: str) -> ChapterBlock:
    return ChapterBlock(BlockKind.H2, {'text': text})


def _para(text: str) -> ChapterBlock:
    return ChapterBlock(BlockKind.PARAGRAPH, {'text': text})


def _paras(text: str) -> List[ChapterBlock]:
    return [_para(p.strip()) for p in (text or '').split('\n\n') if p.strip()]


def build_astrocarto_manuscript(
    *,
    first_name: str,
    birth_date_iso: str,
    map_svg: Optional[str],
    chosen_cities: List[Dict[str, Any]],
    bonus_cities: List[Dict[str, Any]],
    synthesis_text: str,
    lines_data: Optional[List[Dict[str, Any]]] = None,
    user_email: str = '',
    session_id: str = '',
) -> Manuscript:
    """Construit un Manuscript book_engine_v2 pour le PDF Astrocartographie."""
    first_name = (first_name or 'Voyageur').strip() or 'Voyageur'
    chosen_cities = chosen_cities or []
    bonus_cities = bonus_cities or []
    lines_data = lines_data or []

    chapters: List[Chapter] = []

    # ── Chapitre I — L'astrocartographie ──────────────────────────────
    intro_blocks: List[ChapterBlock] = []
    birth_fr = _fmt_date_fr(birth_date_iso)
    if birth_fr:
        intro_blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': f'<span class="lede-date">Né·e le {birth_fr}.</span>',
            'raw': True,
        }))
    intro_blocks.append(_para(
        "L'astrocartographie révèle comment ton ciel de naissance résonne "
        'aux différents endroits du globe. Chaque planète y trace une ligne — '
        "sous laquelle ton énergie s'exprime autrement. Ce livre te guide vers "
        "les lieux qui te portent, et te met en garde contre ceux qui te vident."
    ))
    chapters.append(_chapter('I', 1, "L'astrocartographie",
                             'Comprendre les lignes planétaires', intro_blocks))

    # ── Chapitre II — Tes lignes planétaires ──────────────────────────
    lines_blocks: List[ChapterBlock] = []
    for line in lines_data[:8]:  # cap à 8 pour tenir la longueur
        if not isinstance(line, dict):
            continue
        planet = line.get('planet') or ''
        line_type = line.get('line_type') or ''
        interp = line.get('interpretation') or line.get('meaning') or ''
        if planet and line_type:
            lines_blocks.append(_h2(f'{planet} — {line_type}'))
        if interp:
            lines_blocks.extend(_paras(str(interp)))
    if not lines_blocks:
        lines_blocks.append(_para(
            'Chaque planète de ton thème projette quatre lignes sur la carte — '
            'ascendant, descendant, méridien, fond du ciel. Elles composent la '
            'trame invisible de ta géographie intime.'
        ))
    chapters.append(_chapter('II', 2, 'Tes lignes planétaires',
                             'La trame invisible de ton chemin', lines_blocks))

    # ── Chapitre III — Tes trois villes choisies ──────────────────────
    cities_blocks: List[ChapterBlock] = []
    for city in chosen_cities:
        if not isinstance(city, dict):
            continue
        name = city.get('city') or ''
        country = city.get('country') or ''
        title = f'{name}, {country}'.strip(', ')
        enriched = city.get('enriched') or {}
        cities_blocks.append(_h2(title))
        for section_key in ('summary', 'promise', 'why', 'atmosphere', 'warning'):
            text = enriched.get(section_key)
            if text:
                cities_blocks.extend(_paras(str(text)))
    if not cities_blocks:
        cities_blocks.append(_para(
            'Aucune ville analysée. Choisis trois destinations dans ton espace personnel pour recevoir leur lecture.'
        ))
    chapters.append(_chapter('III', 3, 'Tes trois villes choisies',
                             'Là où ton ciel te répond', cities_blocks))

    # ── Chapitre IV — Villes bonus (Soléna) ───────────────────────────
    bonus_blocks: List[ChapterBlock] = []
    for city in bonus_cities:
        if not isinstance(city, dict):
            continue
        name = city.get('city') or ''
        country = city.get('country') or ''
        title = f'{name}, {country}'.strip(', ')
        enriched = city.get('enriched') or {}
        bonus_blocks.append(_h2(title))
        for section_key in ('why', 'promise', 'summary'):
            text = enriched.get(section_key)
            if text:
                bonus_blocks.extend(_paras(str(text)))
    if not bonus_blocks:
        bonus_blocks.append(_para(
            "Soléna n'a pas encore sélectionné de villes bonus pour toi — reviens bientôt."
        ))
    chapters.append(_chapter('IV', 4, 'Les destinations de Soléna',
                             'Deux villes bonus, choisies pour toi', bonus_blocks))

    # ── Chapitre V — Synthèse ─────────────────────────────────────────
    synth_blocks = _paras(synthesis_text) if synthesis_text else [_para(
        "Ta carte du monde n'est pas un décor : c'est une boussole. Où tu poses les pieds change ce que tu deviens."
    )]
    chapters.append(_chapter('V', 5, 'Synthèse',
                             'Le message de Soléna', synth_blocks))

    return Manuscript(
        session_id=session_id or f'astrocarto-{first_name.lower()}-{int(datetime.now(timezone.utc).timestamp())}',
        user_email=user_email,
        first_name=first_name,
        birth_data=BirthData(date_iso=birth_date_iso or '', time_hhmm=None, city='', country_code='FR'),
        astro_data={
            'city_count': len(chosen_cities),
            'bonus_city_count': len(bonus_cities),
            'engine': 'book_engine_v2',
            'book_title': 'Ton Astrocartographie',
        },
        edition=Edition.NUMERIQUE,
        chapters=chapters,
        design_version='plume-astrale-v2-print',
        created_at=datetime.now(timezone.utc),
    )
