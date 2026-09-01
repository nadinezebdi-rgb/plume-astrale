"""assemble — Assemble un manuscrit COMPLET (12 chapitres LLM en parallèle).

Point d'entrée : `build_full_manuscript(session_id, first_name, birth_data, astro,
                                        chapters_slugs, edition, email)`

Génère les 12 chapitres du socle en parallèle (asyncio.gather) via
`chapter_prompts.generate_chapter_blocks`, puis assemble le Manuscript v2 prêt
à être rendu par `renderer.render_manuscript_to_pdf_v2`.

L'ordre du socle est verrouillé par `book_engine.registry.SOCLE` (12 spec figées).
Les slugs `chapters_slugs` (add-on) sont ajoutés en Deuxième partie via
`assemble_addon_chapters` (P2 — placeholders légers en attendant l'écriture).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Iterable, Optional

from services.book_engine.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)
from services.book_engine.registry import SOCLE, ADDONS
from .chapter_prompts import generate_chapter_blocks

logger = logging.getLogger(__name__)


def _add_opener(chapter: Chapter) -> None:
    """Ajoute le bloc CHAPTER_OPENING au début du chapitre (obligatoire)."""
    chapter.blocks.insert(0, ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': chapter.roman_num,
        'title': chapter.title,
        'kicker': chapter.kicker,
    }))


async def _build_one_chapter(spec, first_name: str, astro: dict, session_id: str) -> Chapter:
    ch = Chapter(
        slug=spec.slug, title=spec.title, kicker=spec.kicker,
        roman_num=spec.roman_num, order=spec.order,
    )
    blocks = await generate_chapter_blocks(
        slug=spec.slug,
        first_name=first_name,
        astro_data=astro,
        session_id=session_id,
    )
    if not blocks:
        # Fallback : bloc respiration signalant chapitre à écrire
        blocks = [ChapterBlock(BlockKind.QUOTE_BREATH, {
            'text': "Ce chapitre s'écrit encore. Il rejoindra votre livre à la prochaine édition."
        })]
    ch.blocks.extend(blocks)
    _add_opener(ch)
    return ch


async def build_full_manuscript(
    *,
    session_id: str,
    user_email: str,
    first_name: str,
    birth_data: BirthData,
    astro_data: dict,
    edition: Edition = Edition.NUMERIQUE,
    addon_slugs: Optional[list[str]] = None,
    max_parallel: int = 3,
) -> Manuscript:
    """Assemble le Manuscript complet avec les 12 chapitres du socle.

    `max_parallel` contrôle le nombre d'appels LLM concurrents (rate limiting).
    """
    logger.info(f'[assemble] démarrage build manuscrit complet pour {session_id}')

    # Génère les 12 chapitres en parallèle avec sémaphore
    semaphore = asyncio.Semaphore(max_parallel)

    async def _bounded(spec):
        async with semaphore:
            return await _build_one_chapter(spec, first_name, astro_data, session_id)

    chapters: list[Chapter] = await asyncio.gather(*[_bounded(s) for s in SOCLE])
    chapters.sort(key=lambda c: c.order)

    # Add-ons : placeholders légers pour l'instant (P2 : écriture LLM à faire)
    if addon_slugs:
        addon_specs = [s for s in ADDONS if s.slug in addon_slugs]
        for spec in addon_specs:
            ch = Chapter(slug=spec.slug, title=spec.title, kicker=spec.kicker,
                         roman_num=spec.roman_num, order=spec.order)
            ch.blocks.append(ChapterBlock(BlockKind.QUOTE_BREATH, {
                'text': "Ce chapitre s'écrit encore. Il rejoindra votre livre à la prochaine édition."
            }))
            _add_opener(ch)
            chapters.append(ch)

    m = Manuscript(
        session_id=session_id,
        user_email=user_email,
        first_name=first_name,
        birth_data=birth_data,
        astro_data=astro_data,
        edition=edition,
        selected_add_ons=addon_slugs or [],
        chapters=chapters,
        created_at=datetime.now(timezone.utc),
    )
    logger.info(f'[assemble] manuscrit assemblé : {len(chapters)} chapitres, '
                f'{sum(len(c.blocks) for c in chapters)} blocs')
    return m
