"""admin_book — routes admin pour le Livre Astral v2 (LOT 4).

Endpoints :
  POST /api/admin/book/generate/{session_id}?engine=v2&profile=print
       Génère un PDF via le nouveau moteur HTML/Chromium et l'attache à la session.
       Ne persiste PAS dans Supabase Storage (usage debug/aperçu).

  GET  /api/admin/book/qa/{session_id}
       Lance les contrôles QA sur le dernier PDF généré et retourne le rapport JSON.

  GET  /api/admin/book/preview.pdf?session_id=…
       Sert le dernier PDF v2 généré en local pour visualisation directe.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse

from services.book_engine.pipeline import (
    ASSETS_DIR as PIPELINE_ASSETS_DIR,
    _fetch_astro,
    _assemble_chapters,
)
from services.book_engine.domain import (
    BirthData, Edition, Manuscript,
)
from services.book_engine_v2 import render_manuscript_to_pdf_v2
from services.book_engine_v2.pdf_qa import run_all_checks, report
from services.supabase_client import get_admin_client
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/admin/book', tags=['admin', 'book'])

V2_LOCAL_DIR = PIPELINE_ASSETS_DIR / 'composer_books_v2'
V2_LOCAL_DIR.mkdir(parents=True, exist_ok=True)


def _pdf_path_for(session_id: str) -> Path:
    safe = session_id.replace('/', '_')
    return V2_LOCAL_DIR / f'{safe}.pdf'


async def _build_manuscript_from_session(session_id: str) -> Manuscript:
    """Charge une session /composer et assemble un Manuscript prêt à rendre."""
    sb = get_admin_client()
    row = sb.table('payment_transactions').select('*').eq(
        'session_id', session_id
    ).limit(1).execute()
    if not row.data:
        raise HTTPException(404, 'session inconnue')
    tx = row.data[0]
    md = tx.get('metadata') or {}
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Voyageuse'
    birth_data = pdf_ctx.get('birth_data') or {}
    edition_str = md.get('edition') or 'numerique'
    chapters_slugs = md.get('chapters') or pdf_ctx.get('chapters') or []
    email = tx.get('user_email') or pdf_ctx.get('email') or ''

    # Fetch astro data (positions + houses)
    astro = await _fetch_astro(birth_data, first_name)

    # Assemble les chapitres (reuse le moteur v1 pour la logique de composition + LLM)
    chapters = await _assemble_chapters(
        first_name=first_name,
        astro_data=astro,
        session_id=session_id,
        chart_png_bytes=None,          # inutile en v2 : la roue est un SVG carré
        chapters_slugs=chapters_slugs,
    )

    try:
        edition_enum = Edition(edition_str)
    except ValueError:
        edition_enum = Edition.NUMERIQUE

    return Manuscript(
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


@router.post('/generate/{session_id}')
async def admin_generate_v2(
    session_id: str,
    profile: str = Query('screen', description="'print' ou 'screen'"),
    with_cover: bool = Query(False, description='Génère la cover Nano Banana avant rendu'),
):
    """Génère un PDF v2 (Chromium/HTML) et le sauve en local pour aperçu.

    Si `with_cover=true`, appelle d'abord Gemini Nano Banana pour créer une
    couverture personnalisée (cadran cosmique bronze) à partir de Soleil/Lune/Ascendant.
    N'écrit PAS dans Supabase Storage ni dans `payment_transactions.metadata`.
    """
    manuscript = await _build_manuscript_from_session(session_id)
    cover_path: Optional[Path] = None
    if with_cover:
        try:
            from services.book_engine_v2.cover_generator import (
                generate_cover_image, resolve_signs_fr, COVER_CACHE_DIR,
            )
            sun, moon, asc = resolve_signs_fr(manuscript.astro_data or {})
            png = await generate_cover_image(
                first_name=manuscript.first_name,
                sun_sign=sun, moon_sign=moon, asc_sign=asc,
            )
            if png:
                cover_path = COVER_CACHE_DIR / f'{session_id}.png'
                cover_path.write_bytes(png)
        except Exception as exc:
            logger.warning(f'[admin/book] cover gen failed: {exc}')
    pdf_bytes = await asyncio.to_thread(
        render_manuscript_to_pdf_v2, manuscript, profile=profile,
        cover_png_path=cover_path,
    )
    out = _pdf_path_for(session_id)
    out.write_bytes(pdf_bytes)
    logger.info(f'[admin/book] v2 PDF {out} ({len(pdf_bytes)} bytes)')
    return {
        'ok': True,
        'session_id': session_id,
        'engine': 'v2',
        'profile': profile,
        'bytes': len(pdf_bytes),
        'local_path': str(out),
        'cover_generated': cover_path is not None,
        'preview_url': f'/api/admin/book/preview.pdf?session_id={session_id}',
    }


@router.get('/qa/{session_id}')
async def admin_qa(session_id: str):
    """Lance les contrôles QA sur le dernier PDF v2 généré."""
    pdf = _pdf_path_for(session_id)
    if not pdf.exists():
        raise HTTPException(404, 'aucun PDF v2 pour cette session — lancer /generate d abord')
    checks = await asyncio.to_thread(run_all_checks, pdf)
    return report(checks)


@router.get('/preview.pdf')
async def admin_preview_pdf(session_id: str):
    """Sert le dernier PDF v2 généré (usage aperçu navigateur)."""
    pdf = _pdf_path_for(session_id)
    if not pdf.exists():
        raise HTTPException(404, 'aucun PDF v2 disponible')
    return FileResponse(str(pdf), media_type='application/pdf',
                        filename=f'livre_astral_v2_{session_id}.pdf')


@router.get('/pdf-engine-health')
async def admin_pdf_engine_health():
    """Diagnostic complet de l'infra PDF v2 sur l'environnement courant.

    Retourne un JSON avec l'état des 6 dépendances critiques :
      1. USE_V2_ENGINE lu depuis l'env
      2. Chromium binaire trouvé + version
      3. Fichiers de polices Cormorant + NotoSansSymbols2
      4. EMERGENT_LLM_KEY présent (booléen, jamais la valeur)
      5. Table Supabase book_manuscripts accessible
      6. Cache directories accessibles en écriture

    Usage prod : `curl https://plume-astrale.fr/api/admin/book/pdf-engine-health | jq`
    """
    import os
    import shutil
    import subprocess
    from datetime import datetime, timezone
    from pathlib import Path

    checks: dict = {}

    # 1. USE_V2_ENGINE
    v2_env = os.environ.get('USE_V2_ENGINE')
    checks['use_v2_engine'] = {
        'value': v2_env,
        'v2_active': v2_env == '1',
        'ok': v2_env == '1',
        'hint': '' if v2_env == '1' else
                'Ajouter USE_V2_ENGINE=1 dans les env vars prod puis redéployer.',
    }

    # 2. Chromium
    from services.book_engine_v2.renderer import CHROMIUM_BINARIES
    chromium_path = None
    chromium_version = None
    for name in CHROMIUM_BINARIES:
        p = shutil.which(name)
        if p:
            chromium_path = p
            try:
                r = subprocess.run([p, '--version'], capture_output=True, timeout=8)
                chromium_version = r.stdout.decode(errors='replace').strip()
            except Exception:
                chromium_version = 'version-check-failed'
            break
    checks['chromium'] = {
        'binary_path': chromium_path,
        'version': chromium_version,
        'ok': chromium_path is not None,
        'hint': '' if chromium_path else
                "Chromium introuvable. Ajouter 'chromium' aux apt packages du build "
                "Docker en prod, sinon fallback WeasyPrint (dégradé).",
    }

    # 3. Polices
    fonts_dir = Path('/app/backend/assets/book/fonts')
    expected = [
        'CormorantGaramond-Light.ttf', 'CormorantGaramond-Regular.ttf',
        'CormorantGaramond-Italic.ttf', 'CormorantGaramond-Bold.ttf',
        'NotoSansSymbols2-Regular.ttf',
    ]
    found = {f: (fonts_dir / f).exists() for f in expected}
    checks['fonts'] = {
        'fonts_dir': str(fonts_dir),
        'dir_exists': fonts_dir.exists(),
        'files': found,
        'missing': [f for f, v in found.items() if not v],
        'ok': all(found.values()),
    }

    # 4. EMERGENT_LLM_KEY (booléen)
    llm_key = os.environ.get('EMERGENT_LLM_KEY')
    checks['emergent_llm_key'] = {
        'present': bool(llm_key),
        'valid_prefix': (llm_key or '').startswith('sk-emergent-') if llm_key else False,
        'ok': bool(llm_key),
        'hint': '' if llm_key else
                "Sans EMERGENT_LLM_KEY : ni chapitres LLM, ni cover Nano Banana. "
                "À ajouter dans env vars prod.",
    }

    # 5. Supabase table book_manuscripts
    sb_check: dict = {'ok': False, 'accessible': False, 'error': None}
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        row = sb.table('book_manuscripts').select('id', count='exact').limit(1).execute()
        sb_check['accessible'] = True
        sb_check['row_count'] = getattr(row, 'count', None)
        sb_check['ok'] = True
    except Exception as e:
        msg = str(e)[:250]
        sb_check['error'] = msg
        if 'book_manuscripts' in msg.lower() and (
            'not found' in msg.lower() or 'does not exist' in msg.lower()
            or 'schema cache' in msg.lower()
        ):
            sb_check['hint'] = ('Table absente. Exécuter 2026_03_book_manuscripts.sql '
                                'dans le SQL Editor Supabase du projet.')
    checks['supabase'] = sb_check

    # 6. Cache dirs
    cache_dirs = {
        'covers_cache': '/app/backend/assets/book/covers_cache',
        'flipbook_cache': '/app/backend/assets/book/flipbook_cache',
        'composer_books': '/app/backend/assets/composer_books',
        'composer_books_v2': '/app/backend/assets/composer_books_v2',
    }
    cache_status = {}
    for name, path in cache_dirs.items():
        p = Path(path)
        writable = False
        if p.exists():
            try:
                t = p / '.write_test'
                t.write_text('ok'); t.unlink()
                writable = True
            except Exception:
                pass
        cache_status[name] = {
            'path': path, 'exists': p.exists(), 'writable': writable,
            'file_count': (len(list(p.iterdir())) if p.exists() else 0),
        }
    checks['cache_dirs'] = {
        'dirs': cache_status,
        'ok': all(d['writable'] or d['exists'] for d in cache_status.values()),
    }

    # Verdict global
    return {
        'ok': all(v.get('ok', False) for v in checks.values()),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'engine_active': 'v2' if checks['use_v2_engine']['v2_active'] else 'v1',
        'checks': checks,
        'summary': {
            'passing': sum(1 for v in checks.values() if v.get('ok')),
            'failing': sum(1 for v in checks.values() if not v.get('ok')),
        },
    }


@router.post('/regen-cover/{session_id}')
async def admin_regen_cover(
    session_id: str,
    force: bool = Query(True, description='Bypasse le cache Nano Banana'),
    preview: bool = Query(False, description='Retourne le PNG au lieu du JSON'),
):
    """Force la régénération de la couverture Nano Banana pour une session.

    Bypasse le cache si `force=true` (défaut). Le filtre OCR anti-texte-parasite
    reste actif (jusqu'à 2 retries). En `preview=true`, retourne directement
    l'image PNG (200 OK, image/png).
    """
    from services.book_engine_v2.cover_generator import (
        COVER_CACHE_DIR, generate_cover_image, resolve_signs_fr,
        _detect_text_in_image,
    )
    from services.book_engine.pipeline import _fetch_astro
    from fastapi.responses import Response as FResponse

    # Fetch minimal : astro data seulement (pas de LLM ni de manuscrit)
    sb = get_admin_client()
    row = sb.table('payment_transactions').select('metadata,user_email').eq(
        'session_id', session_id).limit(1).execute()
    if not row.data:
        raise HTTPException(404, 'session inconnue')
    md = row.data[0].get('metadata') or {}
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Voyageuse'
    birth_data = pdf_ctx.get('birth_data') or {}
    try:
        astro = await _fetch_astro(birth_data, first_name)
    except Exception as e:
        raise HTTPException(500, f'astro fetch failed: {e}')

    sun, moon, asc = resolve_signs_fr(astro)
    png = await generate_cover_image(
        first_name=first_name, sun_sign=sun, moon_sign=moon, asc_sign=asc,
        force=force,
    )
    if not png:
        raise HTTPException(502, 'Gemini n a pas retourné d image après retries')

    n_chars, sample = _detect_text_in_image(png)
    session_copy = COVER_CACHE_DIR / f'{session_id}.png'
    session_copy.write_bytes(png)

    if preview:
        return FResponse(png, media_type='image/png',
                         headers={'Cache-Control': 'no-store'})
    return {
        'ok': True,
        'session_id': session_id,
        'first_name': first_name,
        'signature': {'sun': sun, 'moon': moon, 'ascendant': asc},
        'bytes': len(png),
        'ocr_chars': n_chars,
        'ocr_sample': sample if n_chars else '',
        'session_png_path': str(session_copy),
        'preview_url': f'/api/admin/book/regen-cover/{session_id}?force=false&preview=true',
    }
