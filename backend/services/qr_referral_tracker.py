"""
qr_referral_tracker.py — endpoint /r/{code} qui trace les scans QR PDF vers /?ref={code}.

Flow :
  1. Un client scanne le QR d'un PDF (colophon Nocturne) → ouvre /r/SOPH1234
  2. On incrémente un compteur dans Supabase (`referral_scans`) pour analytics
  3. On redirige vers /?ref=SOPH1234 (302), avec cookie `ref` pour attribution

Sur le tableau de bord admin, on pourra comparer :
  - Impressions PDF (nombre de PDFs générés avec ce code)
  - Scans QR (compteur /r/{code})
  - Conversions (paiements attribués via ?ref=)

Table Supabase attendue (best-effort — soft fail si absente) :
    referral_scans {code TEXT, ua TEXT, ip TEXT, scanned_at TIMESTAMPTZ}
    referral_scan_counters {code TEXT PK, count INTEGER, updated_at TIMESTAMPTZ}
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _log_scan(code: str, ua: str, ip: str) -> None:
    """Best-effort insertion dans referral_scans + increment counter."""
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        now_iso = datetime.now(timezone.utc).isoformat()
        # Insert scan brut (append-only journal)
        try:
            sb.table('referral_scans').insert({
                'code': code, 'ua': ua[:400], 'ip': ip[:64],
                'scanned_at': now_iso,
            }).execute()
        except Exception as e:
            logger.info(f'[qr_tracker] insert referral_scans skipped: {e}')
        # Upsert counter agrégé (pour lecture rapide côté admin)
        try:
            existing = sb.table('referral_scan_counters').select('code, count').eq('code', code).maybe_single().execute()
            if existing and existing.data:
                new_count = int(existing.data.get('count', 0)) + 1
                sb.table('referral_scan_counters').update({
                    'count': new_count, 'updated_at': now_iso,
                }).eq('code', code).execute()
            else:
                sb.table('referral_scan_counters').insert({
                    'code': code, 'count': 1, 'updated_at': now_iso,
                }).execute()
        except Exception as e:
            logger.info(f'[qr_tracker] upsert counter skipped: {e}')
    except Exception as e:
        # Jamais faire échouer la redirection à cause du tracking
        logger.warning(f'[qr_tracker] scan tracking failed silently: {e}')


@router.get('/r/{code}')
async def qr_referral_redirect(code: str, request: Request):
    """Trace le scan QR puis redirige vers la home avec le paramètre ?ref=.

    Le cookie `ref` (30 jours) permet l'attribution même si l'utilisateur
    revient plus tard via un autre canal (bookmark, search, direct).
    """
    # Normalisation défensive : le code est max 32 chars alphanum
    safe_code = ''.join(c for c in code if c.isalnum() or c in '-_')[:32].upper()
    if not safe_code:
        # Redirect propre vers la home sans param (code corrompu)
        return RedirectResponse(url='/', status_code=302)

    ua = request.headers.get('user-agent', '')[:400]
    # X-Forwarded-For depuis Cloudflare / Vercel proxy en priorité
    ip = (
        request.headers.get('cf-connecting-ip')
        or request.headers.get('x-forwarded-for', '').split(',')[0].strip()
        or (request.client.host if request.client else '')
    )
    _log_scan(safe_code, ua, ip)

    # Destination : home avec ?ref= + query utm pour attribution GA/Meta
    base = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
    dest = f'{base}/?ref={safe_code}&utm_source=pdf_qr&utm_medium=print&utm_campaign=colophon'

    resp = RedirectResponse(url=dest, status_code=302)
    # Cookie 30j — attribution même sur navigation ultérieure
    resp.set_cookie(
        key='ref', value=safe_code,
        max_age=30 * 24 * 3600,
        httponly=False,   # lisible par analytics.js pour trackevent
        secure=True, samesite='lax',
    )
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return resp


def ensure_referral_scan_tables() -> dict:
    """Bootstrap idempotent : vérifie que les tables QR referral existent.

    Ne crée PAS les tables (Supabase RESTful API ne permet pas le DDL).
    Sonde `referral_scan_counters` par une lecture rapide. Si absente,
    log une WARNING actionnable avec le chemin du fichier SQL à jouer
    dans le SQL editor Supabase. Retourne un diag pour l'admin.
    """
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        r = sb.table('referral_scan_counters').select('code').limit(1).execute()
        return {'exists': True, 'rows_sample': len(r.data or [])}
    except Exception as e:
        err = str(e)
        if 'PGRST205' in err or 'not find the table' in err.lower() or 'does not exist' in err.lower():
            logger.warning(
                '[qr_tracker] Table `referral_scan_counters` absente. '
                'Exécuter /app/backend/migrations/2026_02_referral_scan_counters.sql '
                'dans le SQL Editor Supabase pour activer les analytics QR. '
                "Sans ça, le dashboard /admin/qr-stats affiche 'aucun scan'."
            )
            return {'exists': False, 'error': 'table_missing', 'sql_path': '/app/backend/migrations/2026_02_referral_scan_counters.sql'}
        logger.warning(f'[qr_tracker] table probe failed: {e}')
        return {'exists': False, 'error': err[:200]}


@router.get('/api/admin/referral-scan-stats')
async def referral_scan_stats(top: int = 50):
    """Admin : renvoie les codes les plus scannés (best-effort, silent fail).

    PGRST205 (table manquante) = pas d'erreur pour l'utilisateur, retourne
    simplement une liste vide → le dashboard affiche l'état "aucun scan"
    plutôt qu'une bannière d'erreur alarmante.
    """
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        r = sb.table('referral_scan_counters').select('code, count, updated_at').order('count', desc=True).limit(top).execute()
        return {'ok': True, 'top_codes': r.data or []}
    except Exception as e:
        err_str = str(e)
        # PGRST205 = "The schema must be reloaded" / table missing → traiter comme empty
        if 'PGRST205' in err_str or 'not find the table' in err_str.lower() or 'does not exist' in err_str.lower():
            return {'ok': True, 'top_codes': []}
        logger.info(f'[qr_tracker] stats endpoint soft-fail: {e}')
        return {'ok': False, 'error': err_str[:200], 'top_codes': []}
