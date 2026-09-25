"""natal_manuscript_builder — Construit un Manuscript léger pour le PDF Thème Natal
================================================================================

Contexte : le pack payant "Thème Natal PDF Ultra" (80 crédits) doit être rendu
via `book_engine_v2/` (fond blanc print, celui qu'on avait construit ensemble)
et non plus via `natal_pdf_v2.py` (fond sombre luxe legacy).

Ce module reçoit les mêmes entrées que l'ancien adaptateur :
  - `prenom`, `birth_date`
  - `natal_data` = {sun_sign, moon_sign, ascendant_sign, planets[], synthese_aspects, tier}
  - `chart_png_bytes` (roue du ciel — optionnel)

Et retourne un `Manuscript` prêt à passer à `render_manuscript_to_pdf_v2(profile='print')`.

Design : 1 chapitre unique "Le Ciel de {Prénom}" qui contient dans l'ordre :
  1. CHAPTER_OPENING (belle page)
  2. TRIO_CARDS (Soleil / Lune / Ascendant)
  3. NATAL_CHART (roue du ciel — si chart_png_bytes fourni)
  4. Pour chaque planète : H2 (Planète en Signe) + PARAGRAPH (analyse IA)
  5. Si `synthese_aspects` : H2 "Vos aspects clés" + PARAGRAPH
  6. FEATHER (ornement final)

Le renderer HTML/CSS de book_engine_v2 gérera automatiquement :
  - Fond blanc `--paper: #FFFFFF`
  - Marges A5 print (148×210 mm)
  - Belle page pour chaque chapter_opener
  - Nombre de pages multiple de 4 (blanches en fin)
  - Ornements dorés bronze fin
"""
from __future__ import annotations
import base64
import logging
from datetime import datetime, timezone

from services.book_engine.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)

logger = logging.getLogger(__name__)


def _parse_birth_date(birth_date: str) -> BirthData:
    """Best-effort parsing de la date ISO — le rendu n'en a besoin que pour
    l'affichage colophon, pas pour de vrais calculs (déjà faits en amont)."""
    return BirthData(
        date_iso=birth_date or '',
        time_hhmm=None,
        city='',
        country_code='FR',
    )


def build_natal_manuscript(
    *,
    prenom: str,
    birth_date: str,
    natal_data: dict,
    chart_png_bytes: bytes | None = None,
    user_email: str = '',
    session_id: str = '',
) -> Manuscript:
    """Construit un Manuscript léger prêt à être rendu en PDF print blanc.

    Ne fait AUCUN appel LLM ni API externe — tout doit déjà être dans
    `natal_data` (fourni par l'appelant depuis astrology-api.io + AI enrichment).
    """
    prenom = (prenom or 'Voyageuse').strip() or 'Voyageuse'

    blocks: list[ChapterBlock] = []

    # 1) CHAPTER_OPENING (belle page ornée)
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'I',
        'title': f'Le Ciel de {prenom}',
        'kicker': 'Votre thème natal, dévoilé.',
    }))

    # 2) TRIO_CARDS Soleil / Lune / Ascendant (skip Ascendant si no_birth_time)
    trio: list[dict] = []
    if natal_data.get('sun_sign'):
        trio.append({'label': 'Soleil', 'sign': natal_data['sun_sign']})
    if natal_data.get('moon_sign'):
        trio.append({'label': 'Lune', 'sign': natal_data['moon_sign']})
    asc = natal_data.get('ascendant_sign')
    if asc and not natal_data.get('no_birth_time'):
        trio.append({'label': 'Ascendant', 'sign': asc})
    if trio:
        blocks.append(ChapterBlock(BlockKind.TRIO_CARDS, {'items': trio}))

    # 3) NATAL_CHART (roue du ciel) — data URI PNG pour être self-contained
    if chart_png_bytes:
        try:
            b64 = base64.b64encode(chart_png_bytes).decode('ascii')
            blocks.append(ChapterBlock(BlockKind.NATAL_CHART, {
                'src': f'data:image/png;base64,{b64}',
                'alt': f'Roue du ciel de {prenom}',
            }))
        except Exception as e:
            logger.warning(f'[natal_manuscript] chart encoding failed: {e}')

    # 4) H2 + PARAGRAPH pour chaque planète
    for p in natal_data.get('planets') or []:
        name = p.get('name', '').strip()
        sign = p.get('sign', '').strip()
        analysis = p.get('analysis', '').strip()
        if not name or not sign or not analysis:
            continue
        blocks.append(ChapterBlock(BlockKind.H2, {
            'text': f'{name} en {sign}',
        }))
        # Découpe l'analyse en paragraphes (double newline = nouveau para)
        paras = [pp.strip() for pp in analysis.split('\n\n') if pp.strip()]
        if not paras:
            paras = [analysis]
        for para in paras:
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))

    # 5) Synthèse aspects (si tier=ultra et présente)
    synthese = (natal_data.get('synthese_aspects') or '').strip()
    if synthese:
        blocks.append(ChapterBlock(BlockKind.H2, {
            'text': 'Vos aspects clés',
        }))
        for para in [p.strip() for p in synthese.split('\n\n') if p.strip()]:
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))

    # 6) Ornement final — respiration avant la fin
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))

    chapter = Chapter(
        slug='natal_full',
        title=f'Le Ciel de {prenom}',
        kicker='Votre thème natal, dévoilé.',
        roman_num='I',
        order=1,
        blocks=blocks,
    )

    manuscript = Manuscript(
        session_id=session_id or f'natal-{prenom.lower()}-{int(datetime.now(timezone.utc).timestamp())}',
        user_email=user_email,
        first_name=prenom,
        birth_data=_parse_birth_date(birth_date),
        astro_data={
            'sun_sign': natal_data.get('sun_sign'),
            'moon_sign': natal_data.get('moon_sign'),
            'ascendant_sign': natal_data.get('ascendant_sign'),
            'tier': natal_data.get('tier', 'legacy'),
            'planet_count': len(natal_data.get('planets') or []),
        },
        edition=Edition.NUMERIQUE,
        chapters=[chapter],
        design_version='plume-astrale-v2-print',
        created_at=datetime.now(timezone.utc),
    )
    return manuscript
