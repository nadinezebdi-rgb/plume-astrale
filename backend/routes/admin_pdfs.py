"""admin_pdfs — Payments, transactions, leads, PDFs envoyés, Thème Natal admin, cron, horoscopes.

Extrait de `routes/admin.py` lors du refactor 2026-02.
Monté sur le même préfixe `/admin`.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from routes.admin import require_admin
from services.supabase_client import get_admin_client

router = APIRouter(prefix='/admin', tags=['admin', 'pdfs', 'payments'])
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Payments / Transactions / Leads
# ─────────────────────────────────────────────────────────────────
@router.get('/payments')
async def admin_payments(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias='status'),
):
    """Liste paginee des transactions Stripe."""
    sb = get_admin_client()
    offset = (page - 1) * page_size
    q = sb.table('payment_transactions').select('*', count='exact').order('created_at', desc=True)
    if status_filter:
        q = q.eq('payment_status', status_filter)
    res = q.range(offset, offset + page_size - 1).execute()
    return {'payments': res.data or [], 'total': res.count or 0, 'page': page, 'page_size': page_size}


@router.get('/transactions')
async def admin_transactions(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    tx_type: Optional[str] = None,
):
    """Liste paginee des transactions de credits."""
    sb = get_admin_client()
    offset = (page - 1) * page_size
    q = sb.table('credit_transactions').select('*', count='exact').order('created_at', desc=True)
    if tx_type:
        q = q.eq('tx_type', tx_type)
    res = q.range(offset, offset + page_size - 1).execute()
    return {'transactions': res.data or [], 'total': res.count or 0, 'page': page, 'page_size': page_size}


@router.get('/leads')
async def admin_leads(
    source: str = '',
    page: int = 1,
    page_size: int = 100,
    _admin: dict = Depends(require_admin),
):
    """Leads capturés (extrait gratuit karmique, oracle, etc.) — table oracle_leads."""
    sb = get_admin_client()
    q = sb.table('oracle_leads').select('*', count='exact')
    if source:
        q = q.eq('source', source)
    start = (max(page, 1) - 1) * page_size
    res = q.order('created_at', desc=True).range(start, start + page_size - 1).execute()
    return {'leads': res.data or [], 'total': res.count or 0}


# ─────────────────────────────────────────────────────────────────
# Daily journal cron + regenerate horoscopes
# ─────────────────────────────────────────────────────────────────
@router.post('/cron/send-daily-journal')
async def cron_send_daily_journal(cron_secret: Optional[str] = Query(None)):
    """Envoyer le journal quotidien à tous les utilisateurs (cron task).

    SEC-hardening : CRON_SECRET est OBLIGATOIRE. Sans lui, refus explicite
    pour empêcher un attaquant de déclencher un spam Resend en masse.
    """
    env_secret = os.getenv('CRON_SECRET')
    if not env_secret:
        logger.error('[cron] CRON_SECRET manquant en env — refus.')
        raise HTTPException(status_code=503, detail='CRON_SECRET not configured on server')
    if not cron_secret or cron_secret != env_secret:
        raise HTTPException(status_code=403, detail='Invalid cron secret')

    from services.journal_email_service import send_daily_journal_batch
    return await send_daily_journal_batch()


@router.post('/regenerate-horoscopes')
async def regenerate_horoscopes(_admin: dict = Depends(require_admin)):
    """Force la régénération manuelle des 12 PDFs d'horoscope journalier.

    Le processus prend ~2 min (12 appels API + 12 appels GPT-5.2).
    Renvoie immédiatement (background task).
    """
    from services.horoscope_scheduler import _regenerate_all
    asyncio.create_task(_regenerate_all())
    return {
        'ok': True,
        'message': "Régénération lancée en background — ~2 min. Vérifie /api/health/horoscopes ou les logs backend.",
    }


# ─────────────────────────────────────────────────────────────────
# PDFs envoyés
# ─────────────────────────────────────────────────────────────────
@router.get('/pdfs-sent')
async def admin_pdfs_sent(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    product: str = '',
):
    """Liste des PDFs envoyés aux clients (filtrés sur metadata.pdf_supabase_url)."""
    sb = get_admin_client()
    query = sb.table('payment_transactions').select(
        'session_id, user_email, pack_id, amount, currency, status, created_at, metadata',
        count='exact',
    ).eq('status', 'completed').order('created_at', desc=True)
    if product:
        query = query.eq('pack_id', product)
    offset = (page - 1) * page_size
    query = query.range(offset, offset + page_size - 1)
    res = query.execute()

    items = []
    for tx in (res.data or []):
        md = tx.get('metadata') or {}
        supabase_url = md.get('pdf_supabase_url')
        if not supabase_url:
            continue
        items.append({
            'session_id': tx['session_id'],
            'user_email': tx.get('user_email') or '',
            'product': tx.get('pack_id') or md.get('product') or 'unknown',
            'amount': tx.get('amount') or 0,
            'currency': tx.get('currency') or 'eur',
            'sent_at': md.get('email_sent_at') or md.get('pdf_generated_at') or tx.get('created_at'),
            'pdf_url': supabase_url,
            'pdf_generated_at': md.get('pdf_generated_at'),
            'email_sent': bool(md.get('email_sent_at')),
        })
    return {
        'items': items,
        'total_with_supabase_url': len(items),
        'total_completed': res.count or 0,
        'page': page,
        'page_size': page_size,
    }


# ─────────────────────────────────────────────────────────────────
# Theme Natal admin : search + regenerate + inspect + patch birth-data
# ─────────────────────────────────────────────────────────────────
def _tn_row_matches(q_clean: str, row: dict) -> bool:
    md = row.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        return False
    pdf_ctx = md.get('pdf_ctx') or {}
    haystack = ' '.join([
        str(row.get('user_email') or ''),
        str(pdf_ctx.get('email') or ''),
        str(pdf_ctx.get('first_name') or ''),
        str(pdf_ctx.get('last_name') or ''),
        str(row.get('session_id') or ''),
    ]).lower()
    return q_clean in haystack


def _tn_format_search_item(row: dict) -> dict:
    md = row.get('metadata') or {}
    pdf_ctx = md.get('pdf_ctx') or {}
    return {
        'session_id': row.get('session_id'),
        'user_email': row.get('user_email') or pdf_ctx.get('email') or '',
        'first_name': pdf_ctx.get('first_name') or '',
        'birth_date': pdf_ctx.get('birth_date') or '',
        'birth_city': pdf_ctx.get('birth_city') or '',
        'created_at': row.get('created_at'),
        'status': row.get('status'),
        'pdf_status': md.get('pdf_status') or 'ok',
        'pdf_error': (md.get('pdf_error') or '')[:200],
        'has_pdf_url': bool(md.get('pdf_url') or md.get('pdf_signed_url')),
    }


@router.get('/theme-natal/search')
async def admin_search_theme_natal(
    q: str,
    limit: int = 20,
    _admin: dict = Depends(require_admin),
):
    """Cherche des sessions Thème Natal par prénom, email ou fragment de session_id."""
    q_clean = (q or '').strip().lower()
    if len(q_clean) < 2:
        return {'items': [], 'query': q_clean, 'note': 'Requête trop courte (min 2 char)'}
    sb = get_admin_client()
    try:
        res = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, status, metadata'
        ).order('created_at', desc=True).limit(500).execute()
    except Exception as e:
        logger.exception(f'[admin] search theme_natal fail: {e}')
        return {'items': [], 'error': str(e)[:200]}

    cap = max(1, min(limit, 50))
    items = []
    for row in (res.data or []):
        if _tn_row_matches(q_clean, row):
            items.append(_tn_format_search_item(row))
            if len(items) >= cap:
                break
    return {'items': items, 'total': len(items), 'query': q_clean}


async def _regen_fetch_and_validate(sb, session_id: str) -> Optional[dict]:
    try:
        r = sb.table('payment_transactions').select('metadata, status').eq('session_id', session_id).maybe_single().execute()
    except Exception:
        logger.exception(f'[admin] regenerate: fetch tx fail {session_id}')
        return None
    if not r or not r.data:
        logger.error(f'[admin] regenerate: session {session_id} introuvable')
        return None
    md = r.data.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        logger.error(f'[admin] regenerate: {session_id} n\'est pas un theme_natal one-shot (kind={md.get("kind")})')
        return None
    return md


def _regen_mark_started(sb, session_id: str, md: dict) -> None:
    try:
        md['regenerate_started_at'] = datetime.now(timezone.utc).isoformat()
        md.pop('regenerate_diag', None)
        md.pop('regenerate_error', None)
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[admin] regenerate: mark started fail {session_id}: {e}')


def _regen_persist_result(sb, session_id: str, *, diag: Optional[dict] = None, error: Optional[str] = None) -> None:
    try:
        r2 = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
        md2 = (r2.data or {}).get('metadata') or {}
        if diag is not None:
            md2['regenerate_diag'] = diag
        if error is not None:
            md2['regenerate_error'] = error[:500]
        md2['regenerate_finished_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md2}).eq('session_id', session_id).execute()
    except Exception:
        pass


@router.post('/theme-natal/regenerate/{session_id}')
async def admin_regenerate_theme_natal(session_id: str, _admin: dict = Depends(require_admin)):
    """Force la régénération du PDF Thème Natal pour une session (background task, retour immédiat)."""
    from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook

    async def _worker():
        sb = get_admin_client()
        md = await _regen_fetch_and_validate(sb, session_id)
        if md is None:
            return
        _regen_mark_started(sb, session_id, md)
        try:
            diag = await handle_theme_natal_oneshot_webhook(session_id, force=True)
            _regen_persist_result(sb, session_id, diag=diag)
            logger.info(f'[admin] regenerate DONE {session_id} diag={diag}')
        except Exception as e:
            logger.exception(f'[admin] regenerate theme_natal fail {session_id}')
            _regen_persist_result(sb, session_id, error=str(e))

    asyncio.create_task(_worker())
    return {
        'ok': True,
        'status': 'accepted',
        'session_id': session_id,
        'poll_url': f'/api/admin/theme-natal/inspect/{session_id}',
        'message': "Régénération lancée. Poll /inspect toutes les 3-5s.",
    }


@router.get('/theme-natal/inspect/{session_id}')
async def admin_inspect_theme_natal(session_id: str, _admin: dict = Depends(require_admin)):
    """Renvoie l'état complet en base pour une session Thème Natal."""
    sb = get_admin_client()
    r = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    if not r or not r.data:
        raise HTTPException(status_code=404, detail='Session introuvable')
    tx = r.data
    md = tx.get('metadata') or {}
    pdf_ctx = md.get('pdf_ctx') or {}
    bd = pdf_ctx.get('birth_data') or {}
    return {
        'session_id': session_id,
        'kind': md.get('kind'),
        'user_email': tx.get('user_email'),
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'created_at': tx.get('created_at'),
        'birth_data_source': {
            'first_name': pdf_ctx.get('first_name'),
            'birth_date_iso': pdf_ctx.get('birth_date_iso'),
            'year': bd.get('year'),
            'month': bd.get('month'),
            'day': bd.get('day'),
            'hour': bd.get('hour'),
            'minute': bd.get('minute'),
            'city': bd.get('city') or bd.get('location'),
            'latitude': bd.get('latitude'),
            'longitude': bd.get('longitude'),
            'timezone': bd.get('timezone'),
        },
        'pdf_path': md.get('pdf_path'),
        'pdf_supabase_url': md.get('pdf_supabase_url'),
        'pdf_generated_at': md.get('pdf_generated_at'),
        'email_sent_at': md.get('email_sent_at'),
        'regenerate_started_at': md.get('regenerate_started_at'),
        'regenerate_finished_at': md.get('regenerate_finished_at'),
        'regenerate_error': md.get('regenerate_error'),
        'regenerate_diag': md.get('regenerate_diag'),
        'regenerate_in_progress': bool(md.get('regenerate_started_at')) and not (md.get('regenerate_finished_at') or md.get('regenerate_error')),
    }


class BirthDataPatch(BaseModel):
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None


async def _geocode_city_osm(query: str) -> dict:
    """Géocode une ville via Nominatim + timezone via timeapi.io."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        r_geo = await client.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': query, 'format': 'json', 'limit': 1, 'addressdetails': 1},
            headers={'User-Agent': 'PlumeAstrale-Admin/1.0 (contact@plume-astrale.fr)'},
        )
        geo_results = r_geo.json() if r_geo.status_code == 200 else []
        if not geo_results:
            raise HTTPException(status_code=422, detail=f'Ville "{query}" introuvable — précise "Ville, Pays"')
        g = geo_results[0]
        lat = float(g['lat'])
        lon = float(g['lon'])
        display_name = g.get('display_name', query)
        tz = None
        try:
            r_tz = await client.get(
                'https://timeapi.io/api/TimeZone/coordinate',
                params={'latitude': lat, 'longitude': lon},
            )
            if r_tz.status_code == 200:
                tz = r_tz.json().get('timeZone')
        except Exception:
            tz = None
        if not tz:
            country = (g.get('address', {}).get('country_code') or '').lower()
            tz = 'Europe/Paris' if country == 'fr' else 'UTC'
        return {'display_name': display_name, 'lat': lat, 'lon': lon, 'tz': tz}


def _apply_birth_data_manual(bd: dict, payload: BirthDataPatch) -> None:
    if payload.city is not None:
        bd['city'] = payload.city
        bd['location'] = payload.city
    if payload.latitude is not None:
        bd['latitude'] = float(payload.latitude)
    if payload.longitude is not None:
        bd['longitude'] = float(payload.longitude)
    if payload.timezone is not None:
        bd['timezone'] = payload.timezone


@router.patch('/theme-natal/{session_id}/birth-data')
async def admin_patch_birth_data(session_id: str, payload: BirthDataPatch, _admin: dict = Depends(require_admin)):
    """Met à jour les données de naissance stockées dans metadata.pdf_ctx.birth_data."""
    sb = get_admin_client()
    r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
    if not r or not r.data:
        raise HTTPException(status_code=404, detail='Session introuvable')
    md = r.data.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        raise HTTPException(status_code=400, detail='La session n\'est pas un Thème Natal one-shot')

    pdf_ctx = md.get('pdf_ctx') or {}
    bd = dict(pdf_ctx.get('birth_data') or {})

    if payload.city and not (payload.latitude and payload.longitude):
        try:
            geo = await _geocode_city_osm(payload.city.strip())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=502, detail=f'Géocodage échoué : {e}')
        bd['city'] = geo['display_name']
        bd['location'] = geo['display_name']
        bd['latitude'] = geo['lat']
        bd['longitude'] = geo['lon']
        bd['timezone'] = geo['tz']
        resolved = {'source': 'geocode', **geo}
    else:
        _apply_birth_data_manual(bd, payload)
        resolved = {'source': 'manual'}

    pdf_ctx['birth_data'] = bd
    md['pdf_ctx'] = pdf_ctx
    md.pop('pdf_path', None)
    sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    return {'ok': True, 'birth_data': bd, 'resolved': resolved}
