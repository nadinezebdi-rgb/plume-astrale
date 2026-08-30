"""pipeline — Orchestrateur du BookRenderingEngine.

Reçoit une transaction /composer complète (email, birth_data, chapters
choisis) et produit :

  1. Fetch astro data via astrology-api.io (positions natales)
  2. Fetch chart SVG + reskin bronze/ivoire (Chapitre I asset)
  3. Génération LLM anti-slop du Chapitre IV pilote (extensible)
  4. Assemblage Manuscript
  5. Rendu ReportLab BookDocument A5 → bytes PDF
  6. Upload Supabase Storage + signed URL
  7. Marquage transaction (pdf_supabase_url, pdf_path, pdf_status)

Ce pipeline est appelé :
  - Dans le webhook Stripe (`kind=composer_book`)
  - Dans le bypass promo `TOUT2026` (asyncio.create_task)

Idempotent : ne relance pas la génération si `pdf_status=success` déjà.
"""
from __future__ import annotations
import base64
import logging
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional

from services import astrology_io_service as aio
from services.supabase_client import get_admin_client
from .domain import (
    BirthData, Chapter, ChapterBlock, BlockKind, Edition,
    Manuscript,
)
from .document import render_manuscript_to_pdf
from .prose_generator import generate_chapter_iv_love
from .registry import SOCLE, all_chapters_for_manuscript
from .svg_bronze import svg_bronze_to_png_bytes

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / 'assets'


# ═══════════════════════════════════════════════════════════════
# Cover — utilise le fallback existant (couverture générique)
# ═══════════════════════════════════════════════════════════════
def _load_cover_fallback() -> Optional[bytes]:
    p = ASSETS_DIR / 'COUVERTURE_PLUME_masked_1400.jpg'
    if p.exists():
        return p.read_bytes()
    return None


# ═══════════════════════════════════════════════════════════════
# Astro data — fetch + shape pour le prose generator
# ═══════════════════════════════════════════════════════════════
async def _fetch_astro(birth_data_dict: dict, name: str) -> dict:
    """Récupère positions + aspects + SVG bronze en une passe."""
    natal = await aio.natal_chart(birth_data_dict, name=name, language='fr')
    planets = aio.extract_planets(natal) if natal else {}
    asc_sign_en = aio.extract_ascendant_sign_en(natal) if natal else None
    # extract_planets renvoie déjà un dict {name.lower(): {name, sign, house, degree}}
    return {
        'planets': planets,
        'ascendant_sign_en': asc_sign_en,
        'raw_natal': natal or {},
    }


async def _fetch_svg_bronze_png(birth_data_dict: dict, name: str) -> Optional[bytes]:
    """Fetch le SVG natal chez astrology-api.io + reskin bronze + rasterize PNG."""
    svg = await aio.chart_svg_render(
        birth_data=birth_data_dict, name=name,
        chart_type='natal', theme='light', language='fr',
    )
    if not svg:
        logger.warning('[pipeline] chart_svg_render returned None')
        return None
    png = svg_bronze_to_png_bytes(svg, target_px=1200)
    if not png:
        logger.warning('[pipeline] svg_bronze_to_png_bytes returned None (cairosvg?)')
    return png


# ═══════════════════════════════════════════════════════════════
# Assemblage chapitres — socle minimal (pilote Chapitre IV)
# ═══════════════════════════════════════════════════════════════
async def _assemble_chapters(
    *,
    first_name: str,
    astro_data: dict,
    session_id: str,
    chart_png_bytes: Optional[bytes],
    chapters_slugs: list[str] | None = None,
) -> list[Chapter]:
    """Assemble les chapitres pour le manuscrit.

    Pour la première itération (LOT 3 P0) :
      - Chapitre I : Votre ciel de naissance (avec roue céleste bronze)
      - Chapitre IV : Votre façon d'aimer (prose anti-slop LLM)
      - Autres chapitres du socle : placeholder minimal (à écrire dans LOT 3.5+)
    """
    chapters: list[Chapter] = []

    # Chapitre I — Votre ciel de naissance (roue céleste)
    spec_i = next(c for c in SOCLE if c.slug == 'ciel_naissance')
    ch_i = Chapter(
        slug=spec_i.slug, title=spec_i.title, kicker=spec_i.kicker,
        roman_num=spec_i.roman_num, order=spec_i.order,
    )
    ch_i.blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': spec_i.roman_num,
        'title': spec_i.title,
        'kicker': spec_i.kicker,
    }))
    ch_i.blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
    ch_i.blocks.append(ChapterBlock(BlockKind.H2, {
        'text': 'Le cadran de votre ciel'
    }))
    ch_i.blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': (
            f"Voici le dessin exact du ciel au moment de votre naissance, "
            f"tracé selon les positions calculées à la minute près. "
            f"Chaque planète y occupe une place unique — sa signature."
        )
    }))
    # Injection de la roue céleste bronze (si dispo)
    if chart_png_bytes:
        # On sauvegarde le PNG dans un fichier temporaire pour RLImage
        chart_dir = ASSETS_DIR / 'composer_charts'
        chart_dir.mkdir(parents=True, exist_ok=True)
        chart_path = chart_dir / f'{session_id}_bronze.png'
        chart_path.write_bytes(chart_png_bytes)
        ch_i.blocks.append(ChapterBlock(BlockKind.IMAGE, {
            'path': str(chart_path),
            'width_mm': 100, 'height_mm': 100,
        }))
    else:
        ch_i.blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': (
                "(Illustration de la roue céleste — génération en cours, "
                "elle apparaîtra dans la prochaine édition PDF.)"
            )
        }))
    ch_i.blocks.append(ChapterBlock(BlockKind.HAIRLINE, {}))
    chapters.append(ch_i)

    # Chapitres II, III — placeholders légers (extensibles)
    for slug in ('grandes_lignes', 'trio_identitaire'):
        spec = next(c for c in SOCLE if c.slug == slug)
        chapters.append(_placeholder_chapter(spec))

    # Chapitre IV — Votre façon d'aimer (pilote anti-slop)
    spec_iv = next(c for c in SOCLE if c.slug == 'facon_aimer')
    ch_iv = Chapter(
        slug=spec_iv.slug, title=spec_iv.title, kicker=spec_iv.kicker,
        roman_num=spec_iv.roman_num, order=spec_iv.order,
    )
    ch_iv.blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': spec_iv.roman_num,
        'title': spec_iv.title,
        'kicker': spec_iv.kicker,
    }))
    ch_iv.blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
    # Ligne méta (signature Vénus)
    planets = astro_data.get('planets') or {}
    venus = planets.get('venus') or {}
    if venus:
        from .prose_generator import _fmt_sign_fr, _fmt_house, _fmt_deg
        ch_iv.blocks.append(ChapterBlock(BlockKind.NATAL_META, {
            'sign': _fmt_sign_fr(venus.get('sign', '')),
            'house': _fmt_house(venus.get('house')),
            'degree': _fmt_deg(venus.get('degree')),
            'note': 'RÉTROGRADE' if venus.get('retrograde') else '',
        }))
    # Prose LLM
    prose_blocks = await generate_chapter_iv_love(
        first_name=first_name,
        astro_data=astro_data,
        session_id=session_id,
    )
    ch_iv.blocks.extend(prose_blocks)
    chapters.append(ch_iv)

    # Chapitres V-XII — placeholders légers pour tenir le volume
    remaining = [c for c in SOCLE if c.slug not in {'ciel_naissance', 'grandes_lignes',
                                                     'trio_identitaire', 'facon_aimer'}]
    for spec in remaining:
        chapters.append(_placeholder_chapter(spec))

    # Add-ons éventuels (Deuxième partie) — placeholders
    if chapters_slugs:
        all_specs = all_chapters_for_manuscript(chapters_slugs)
        addons_only = [s for s in all_specs if s.is_addon]
        for spec in addons_only:
            chapters.append(_placeholder_chapter(spec, is_addon=True))

    return chapters


def _placeholder_chapter(spec, is_addon: bool = False) -> Chapter:
    """Chapitre placeholder tant que la prose LLM n'est pas encore écrite.

    Structure minimale : opening + kicker + une phrase de transition +
    une respiration. C'est propre à l'œil, JAMAIS de lorem ipsum.
    """
    ch = Chapter(
        slug=spec.slug, title=spec.title, kicker=spec.kicker,
        roman_num=spec.roman_num, order=spec.order,
    )
    ch.blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': spec.roman_num,
        'title': spec.title,
        'kicker': spec.kicker,
    }))
    ch.blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
    ch.blocks.append(ChapterBlock(BlockKind.QUOTE_BREATH, {
        'text': "Ce chapitre s'écrit encore. Il rejoindra votre livre à la prochaine édition."
    }))
    return ch


# ═══════════════════════════════════════════════════════════════
# API publique — pipeline complet appelable depuis le webhook
# ═══════════════════════════════════════════════════════════════
async def build_book_pdf_for_session(session_id: str, *, force: bool = False) -> dict:
    """Point d'entrée unique du pipeline PDF /composer.

    Lit la transaction, exécute le pipeline complet, écrit le résultat
    dans `payment_transactions.metadata`. Idempotent : ne rejoue pas si
    `pdf_status=success` sauf `force=True`.

    Retourne un dict de diagnostic : {ok, pdf_bytes, pdf_pages, pdf_supabase_url, error?}
    """
    diag: dict = {'session_id': session_id, 'ok': False}
    sb = get_admin_client()

    # Charge la transaction
    try:
        row = sb.table('payment_transactions').select('*').eq(
            'session_id', session_id
        ).limit(1).execute()
    except Exception as e:
        diag['error'] = f'Supabase read failed: {e}'
        return diag
    if not row.data:
        diag['error'] = 'Transaction non trouvée'
        return diag
    tx = row.data[0]
    md = tx.get('metadata') or {}

    # Idempotence
    if not force and md.get('pdf_status') == 'success' and md.get('pdf_supabase_url'):
        diag['ok'] = True
        diag['pdf_supabase_url'] = md['pdf_supabase_url']
        diag['skipped'] = True
        return diag

    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Voyageuse'
    birth_data = pdf_ctx.get('birth_data') or {}
    edition_str = md.get('edition') or 'numerique'
    chapters_slugs = md.get('chapters') or pdf_ctx.get('chapters') or []
    email = tx.get('user_email') or pdf_ctx.get('email') or ''

    # 1. Fetch astro
    try:
        astro = await _fetch_astro(birth_data, first_name)
    except Exception as e:
        diag['error'] = f'astro fetch failed: {e}'
        logger.exception('[pipeline] astro fetch failed')
        return diag

    # 2. Fetch roue céleste + reskin bronze
    chart_png = None
    try:
        chart_png = await _fetch_svg_bronze_png(birth_data, first_name)
    except Exception as e:
        logger.warning(f'[pipeline] chart svg bronze failed: {e}')

    # 3. Assemble chapters (Chapitre I roue + Chapitre IV LLM + placeholders)
    try:
        chapters = await _assemble_chapters(
            first_name=first_name,
            astro_data=astro,
            session_id=session_id,
            chart_png_bytes=chart_png,
            chapters_slugs=chapters_slugs,
        )
    except Exception as e:
        diag['error'] = f'chapter assembly failed: {e}'
        logger.exception('[pipeline] chapter assembly failed')
        return diag

    # 4. Construire le Manuscript
    try:
        edition_enum = Edition(edition_str)
    except ValueError:
        edition_enum = Edition.NUMERIQUE

    manuscript = Manuscript(
        session_id=session_id,
        user_email=email,
        first_name=first_name,
        birth_data=BirthData(
            date_iso=pdf_ctx.get('birth_date_iso') or '1990-01-01',
            time_hhmm=(f"{birth_data.get('hour', 12):02d}:{birth_data.get('minute', 0):02d}"
                       if birth_data else None),
            city=birth_data.get('city') or '',
            country_code=birth_data.get('country_code') or 'FR',
            latitude=birth_data.get('latitude'),
            longitude=birth_data.get('longitude'),
        ),
        astro_data=astro,
        edition=edition_enum,
        selected_add_ons=chapters_slugs,
        chapters=chapters,
        created_at=datetime.now(timezone.utc),
    )

    # 5. Rendu ReportLab
    try:
        import asyncio
        pdf_bytes = await asyncio.to_thread(render_manuscript_to_pdf, manuscript)
    except Exception as e:
        diag['error'] = f'render failed: {e}'
        logger.exception('[pipeline] render failed')
        return diag

    diag['pdf_bytes'] = len(pdf_bytes)
    diag['pdf_pages'] = pdf_bytes.count(b'/Type /Page') or pdf_bytes.count(b'/Type/Page')

    # 6. Sauvegarde disque (fallback) + upload Supabase Storage
    out_dir = ASSETS_DIR / 'composer_books'
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f'plume_astrale_{first_name.lower()}_{session_id[:12]}.pdf'
    local_path = out_dir / filename
    try:
        local_path.write_bytes(pdf_bytes)
    except Exception as e:
        logger.warning(f'[pipeline] local write failed: {e}')

    supabase_url = None
    try:
        from services.pdf_download import (
            new_pdf_token, build_signed_pdf_url, upload_pdf_to_reports_bucket,
        )
        pdf_token = new_pdf_token()
        md['pdf_token'] = pdf_token
        md['pdf_path'] = build_signed_pdf_url(session_id, pdf_token)
        md['pdf_local_path'] = str(local_path)
        supabase_url = await asyncio.to_thread(
            upload_pdf_to_reports_bucket,
            pdf_bytes, session_id, 'composer_book', filename,
            str(int(datetime.now(timezone.utc).timestamp())),
        )
        if supabase_url:
            md['pdf_supabase_url'] = supabase_url
    except Exception as e:
        logger.warning(f'[pipeline] supabase upload failed: {e}')

    md['pdf_status'] = 'success'
    md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
    md['pdf_pages'] = diag['pdf_pages']
    md.pop('pdf_error', None)

    try:
        sb.table('payment_transactions').update({'metadata': md}).eq(
            'session_id', session_id
        ).execute()
    except Exception as e:
        logger.warning(f'[pipeline] tx metadata update failed: {e}')

    diag['ok'] = True
    diag['pdf_supabase_url'] = supabase_url
    diag['pdf_local_path'] = str(local_path)
    diag['pdf_signed_url'] = md.get('pdf_path')
    logger.info(
        f'[pipeline] Book PDF built for {session_id}: '
        f'{diag["pdf_pages"]} pages, {diag["pdf_bytes"]} bytes'
    )
    return diag
