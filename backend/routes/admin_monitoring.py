"""admin_monitoring — Observabilité : cache SVG, PDF failures, alertes, A/B stats.

Extrait de `routes/admin.py` lors du refactor 2026-02 pour maintenir admin.py < 300 lignes.
Monté sur le même préfixe `/admin`.
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from routes.admin import require_admin
from services.supabase_client import get_admin_client

router = APIRouter(prefix='/admin', tags=['admin', 'monitoring'])
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Cache SVG (Supabase Storage)
# ─────────────────────────────────────────────────────────────────
@router.get('/cache/svg/stats')
async def admin_svg_cache_stats(_admin: dict = Depends(require_admin)):
    """Stats du cache SVG (Supabase Storage bucket 'reports' / prefix chart-svg-cache/).

    Retourne : { total_files, total_size_bytes, total_size_human, by_chart_type: {...} }
    """
    sb = get_admin_client()
    chart_types = ['natal', 'transit', 'progression', 'synastry', 'composite', 'solar_return', 'lunar_return']
    by_type: dict = {}
    total_files = 0
    total_size = 0
    for ct in chart_types:
        prefix = f'chart-svg-cache/{ct}'
        try:
            listing = sb.storage.from_('reports').list(prefix, {'limit': 1000, 'offset': 0})
            files = [f for f in (listing or []) if f.get('name') and not f.get('name').endswith('/')]
        except Exception as e:
            logger.warning(f'[admin/svg_cache_stats] list {prefix} fail: {e}')
            files = []
        n = len(files)
        size = 0
        for f in files:
            meta = f.get('metadata') or {}
            s = meta.get('size') or meta.get('contentLength') or 0
            try:
                size += int(s)
            except Exception:
                pass
        by_type[ct] = {'files': n, 'size_bytes': size}
        total_files += n
        total_size += size

    def _human(b: int) -> str:
        for unit in ('B', 'KB', 'MB', 'GB'):
            if b < 1024 or unit == 'GB':
                return f'{b:.1f} {unit}' if unit != 'B' else f'{b} B'
            b = b / 1024
        return f'{b:.1f} GB'

    return {
        'total_files': total_files,
        'total_size_bytes': total_size,
        'total_size_human': _human(total_size),
        'by_chart_type': by_type,
    }


# ─────────────────────────────────────────────────────────────────
# Silent Failure Radar : PDFs failed
# ─────────────────────────────────────────────────────────────────
@router.get('/pdf-failures/last-24h')
async def admin_pdf_failures_last_24h(
    hours: int = 24,
    _admin: dict = Depends(require_admin),
):
    """Liste les sessions dont `metadata.pdf_status='failed'` dans les X dernières heures."""
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max(1, min(hours, 168)))).isoformat()
    try:
        res = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, metadata'
        ).gte('created_at', cutoff).order('created_at', desc=True).limit(500).execute()
    except Exception as e:
        logger.exception(f'[admin] pdf-failures fetch failed: {e}')
        return {'items': [], 'total': 0, 'error': str(e)[:200]}

    items = []
    for row in (res.data or []):
        md = row.get('metadata') or {}
        if md.get('pdf_status') != 'failed':
            continue
        pdf_ctx = md.get('pdf_ctx') or {}
        items.append({
            'session_id': row.get('session_id'),
            'user_email': row.get('user_email') or pdf_ctx.get('email') or '',
            'first_name': pdf_ctx.get('first_name') or '',
            'kind': md.get('kind') or 'unknown',
            'created_at': row.get('created_at'),
            'pdf_error': (md.get('pdf_error') or '')[:400],
            'pdf_failed_at': md.get('pdf_failed_at'),
            'planets_core_missing': md.get('planets_core_missing') or [],
            'regenerate_in_progress': bool(md.get('regenerate_started_at')
                                           and not md.get('regenerate_diag')
                                           and not md.get('regenerate_error')),
        })
    return {'items': items, 'total': len(items), 'window_hours': hours, 'since': cutoff}


# ─────────────────────────────────────────────────────────────────
# Admin alerts (health-checks tiers)
# ─────────────────────────────────────────────────────────────────
@router.get('/alerts')
async def admin_alerts_list(
    limit: int = Query(50, ge=1, le=200),
    alert_type: Optional[str] = Query(None, description='Filtre par alert_type exact'),
    period: Optional[str] = Query(None, regex='^(7d|30d|all)$', description='Fenêtre temporelle'),
    status: Optional[str] = Query(None, regex='^(open|resolved)$', description='Statut'),
    _admin: dict = Depends(require_admin),
):
    """Liste des alertes système envoyées (astrology-api.io health-check, etc.)."""
    sb = get_admin_client()
    try:
        q = sb.table('admin_alerts').select(
            'id, alert_type, severity, subject, reason, http_status, '
            'error_detail, payload, resend_id, recipient, resolved_at, created_at'
        )
        if alert_type:
            q = q.eq('alert_type', alert_type)
        if period in ('7d', '30d'):
            days = 7 if period == '7d' else 30
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            q = q.gte('created_at', cutoff)
        if status == 'open':
            q = q.is_('resolved_at', 'null')
        elif status == 'resolved':
            q = q.not_.is_('resolved_at', 'null')
        r = q.order('created_at', desc=True).limit(limit).execute()
        items = r.data or []
        return {
            'items': items,
            'total': len(items),
            'migration_needed': False,
            'filters': {'alert_type': alert_type, 'period': period or 'all', 'status': status or 'all'},
        }
    except Exception as e:
        msg = str(e)
        if 'admin_alerts' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning('[admin/alerts] table absente — exécuter 2026_02_admin_alerts.sql')
            return {'items': [], 'total': 0, 'migration_needed': True, 'filters': {}}
        raise HTTPException(status_code=500, detail=f'alerts fetch failed: {msg[:200]}')


@router.post('/alerts/{alert_id}/resolve')
async def admin_alert_resolve(
    alert_id: str,
    _admin: dict = Depends(require_admin),
):
    """Marque une alerte comme résolue (resolved_at = now())."""
    sb = get_admin_client()
    try:
        r = sb.table('admin_alerts').update({
            'resolved_at': datetime.now(timezone.utc).isoformat(),
        }).eq('id', alert_id).execute()
        return {'success': True, 'updated': len(r.data or [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'resolve failed: {str(e)[:200]}')


# ─────────────────────────────────────────────────────────────────
# A/B stats dashboard (table ab_events)
# ─────────────────────────────────────────────────────────────────
@router.get('/ab-stats')
async def admin_ab_stats(
    experiment: str = Query(..., min_length=1, max_length=80),
    period: Optional[str] = Query('30d', regex='^(7d|30d|all)$'),
    _admin: dict = Depends(require_admin),
):
    """Agrège les évènements A/B pour un `experiment` donné."""
    sb = get_admin_client()
    try:
        q = sb.table('ab_events').select('variant, event_name').eq('experiment', experiment)
        if period in ('7d', '30d'):
            days = 7 if period == '7d' else 30
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            q = q.gte('created_at', cutoff)
        r = q.limit(50000).execute()
        rows = r.data or []
        agg: dict[str, dict[str, int]] = {}
        for row in rows:
            v = row.get('variant')
            e = row.get('event_name')
            if not v or not e:
                continue
            agg.setdefault(v, {}).setdefault(e, 0)
            agg[v][e] += 1
        variants = []
        for v, counts in sorted(agg.items()):
            shown = counts.get('shown', 0)
            dismissed = counts.get('dismissed', 0)
            converted = counts.get('converted', 0)
            variants.append({
                'variant': v,
                'shown': shown,
                'dismissed': dismissed,
                'converted': converted,
                'dismiss_rate': round(100.0 * dismissed / shown, 2) if shown else 0.0,
                'conversion_rate': round(100.0 * converted / shown, 2) if shown else 0.0,
                'all_events': counts,
            })
        return {
            'experiment': experiment,
            'period': period,
            'variants': variants,
            'total_events': len(rows),
            'migration_needed': False,
        }
    except Exception as e:
        msg = str(e)
        if 'ab_events' in msg and ('schema cache' in msg or 'does not exist' in msg):
            return {
                'experiment': experiment,
                'period': period,
                'variants': [],
                'total_events': 0,
                'migration_needed': True,
            }
        raise HTTPException(status_code=500, detail=f'ab_stats failed: {msg[:200]}')


# ─────────────────────────────────────────────────────────────────
# Background loops kill-switch — observabilité multi-déploiement
# ─────────────────────────────────────────────────────────────────
@router.get('/background-loops/status')
async def admin_background_loops_status(_admin: dict = Depends(require_admin)):
    """Diagnostic du pod courant pour piloter les kill-switches sur plusieurs
    déploiements (Emergent + Railway + staging) qui pointent la même base.

    Permet, en appelant la même URL publique depuis des contextes différents,
    de confirmer que la variable d'env a bien pris effet sur chaque pod.
    Expose :
      - `running` : True si les loops sont actifs (set au startup)
      - `env_disable_alias` : valeur brute de DISABLE_BACKGROUND_TASKS
      - `env_bg_enabled`    : valeur brute de BACKGROUND_LOOPS_ENABLED
      - `hostname`          : nom DNS du conteneur (différencie Emergent/Railway)
      - `deploy_target`     : indice RAILWAY_* / EMERGENT_* / autre si posé
      - `warmup_sec`        : fenêtre de warmup appliquée
    """
    import os as _os
    import socket as _socket
    from fastapi import Request as _Req  # local pour garder la signature propre

    # On accède à l'état posé au startup
    from server import app as _app  # type: ignore
    running = bool(getattr(_app.state, 'background_loops_running', False))

    # Indice sur la plateforme : Railway et Emergent set des env différentes
    deploy_target = 'unknown'
    if _os.environ.get('RAILWAY_ENVIRONMENT') or _os.environ.get('RAILWAY_PROJECT_ID'):
        deploy_target = 'railway'
    elif _os.environ.get('K_SERVICE') or _os.environ.get('EMERGENT_DEPLOYMENT_ID') or _os.environ.get('EMERGENT_APP_ID'):
        deploy_target = 'emergent'
    elif _os.environ.get('KUBERNETES_SERVICE_HOST'):
        deploy_target = 'kubernetes'

    try:
        hostname = _socket.gethostname()
    except Exception:
        hostname = ''

    return {
        'running': running,
        'env_disable_alias': _os.environ.get('DISABLE_BACKGROUND_TASKS', ''),
        'env_bg_enabled': _os.environ.get('BACKGROUND_LOOPS_ENABLED', '1'),
        'warmup_sec': int(_os.environ.get('BACKGROUND_LOOPS_WARMUP_SEC', '90')),
        'hostname': hostname,
        'deploy_target': deploy_target,
    }

