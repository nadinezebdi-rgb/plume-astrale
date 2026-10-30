"""csp_reports — Collecte des violations Content-Security-Policy.

Nginx envoie en Report-Only une CSP ; les navigateurs POSTent les violations
sur `/api/csp-reports`. On stocke dans Mongo (collection `csp_reports`) avec
agrégation par (directive, blocked_uri) sur 24h pour détecter les anomalies.

Au-delà d'un seuil (CSP_SLACK_THRESHOLD, défaut 50 violations identiques
dans la fenêtre), ping Slack UNE fois par (directive, blocked_uri) et par
cycle de vie du pod — évite le spam.

Endpoints :
  POST /api/csp-reports      → ingestion publique (navigateur)
  GET  /api/admin/csp-reports → agrégation admin par directive/blocked_uri
"""
from __future__ import annotations

import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from routes.admin import require_admin
from services.slack_notify import send_slack_alert

logger = logging.getLogger(__name__)

router = APIRouter(tags=['csp-reports'])

_CSP_COLL = 'csp_reports'
_SLACK_THRESHOLD = int(os.environ.get('CSP_SLACK_THRESHOLD', '50'))
_SLACK_WINDOW_H = int(os.environ.get('CSP_SLACK_WINDOW_H', '24'))

# Dédup Slack in-memory : (directive, blocked_uri) déjà alertés ce run.
_alerted_slack: set = set()


class CspReportBody(BaseModel):
    """Format navigateur legacy `csp-report`. Les navigateurs modernes envoient
    aussi au format Reporting API (type=csp-violation, body=…)."""
    csp_report: Optional[Dict[str, Any]] = None


def _normalize(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise les 2 formats (legacy `csp-report` et Reporting API `body`)."""
    body = (
        payload.get('csp-report')
        or payload.get('body')
        or (payload if 'violated-directive' in payload or 'violatedDirective' in payload else {})
    )
    return {
        'document_uri':      (body.get('document-uri') or body.get('documentURL') or '')[:500],
        'violated_directive': (body.get('violated-directive') or body.get('effectiveDirective') or body.get('violatedDirective') or '')[:200],
        'effective_directive': (body.get('effective-directive') or body.get('effectiveDirective') or '')[:200],
        'blocked_uri':       (body.get('blocked-uri') or body.get('blockedURL') or body.get('blockedURI') or '')[:500],
        'original_policy':   (body.get('original-policy') or body.get('originalPolicy') or '')[:2000],
        'source_file':       (body.get('source-file') or body.get('sourceFile') or '')[:500],
        'line_number':       body.get('line-number') or body.get('lineNumber'),
        'column_number':     body.get('column-number') or body.get('columnNumber'),
        'disposition':       (body.get('disposition') or '')[:30],
    }


@router.post('/csp-reports', include_in_schema=False)
async def ingest_csp_report(request: Request) -> Dict[str, Any]:
    """Ingestion publique des violations CSP envoyées par le navigateur.

    Les navigateurs POSTent avec Content-Type `application/csp-report` ou
    `application/reports+json`. On parse manuellement pour supporter les 2.
    """
    try:
        payload = await request.json()
    except Exception:
        return {'ok': False, 'reason': 'invalid-json'}

    # Reporting API peut envoyer une liste de reports
    reports: List[Dict[str, Any]] = payload if isinstance(payload, list) else [payload]

    from services.mongo import get_db
    db = get_db()
    if db is None:
        return {'ok': False, 'reason': 'db-unavailable', 'count': 0}

    inserted = 0
    now = datetime.now(timezone.utc)
    ua = request.headers.get('user-agent', '')[:300]
    try:
        docs = []
        for rep in reports:
            if not isinstance(rep, dict):
                continue
            n = _normalize(rep)
            if not n['violated_directive'] and not n['blocked_uri']:
                continue
            docs.append({
                **n,
                'ua': ua,
                'reported_at': now,
            })
        if docs:
            await db[_CSP_COLL].insert_many(docs)
            inserted = len(docs)
    except Exception as e:
        logger.warning(f'[csp_reports] insert fail: {e}')
        return {'ok': False, 'reason': 'db-insert', 'error': str(e)[:200]}

    # Déclencheur Slack : agrège les 24 dernières heures par (directive, blocked_uri)
    try:
        await _maybe_slack_alert(db, now)
    except Exception as e:
        logger.info(f'[csp_reports] slack check skip: {e}')

    return {'ok': True, 'count': inserted}


async def _maybe_slack_alert(db, now: datetime) -> None:
    """Si une violation récurrente dépasse le seuil, ping Slack une fois."""
    cutoff = now - timedelta(hours=_SLACK_WINDOW_H)
    pipeline = [
        {'$match': {'reported_at': {'$gte': cutoff}}},
        {'$group': {
            '_id': {
                'directive': '$violated_directive',
                'blocked_uri': '$blocked_uri',
            },
            'n': {'$sum': 1},
            'last': {'$max': '$reported_at'},
            'first': {'$min': '$reported_at'},
        }},
        {'$match': {'n': {'$gte': _SLACK_THRESHOLD}}},
        {'$sort': {'n': -1}},
        {'$limit': 5},
    ]
    cursor = db[_CSP_COLL].aggregate(pipeline)
    async for group in cursor:
        key = f"{group['_id']['directive']}|{group['_id']['blocked_uri']}"
        if key in _alerted_slack:
            continue
        _alerted_slack.add(key)
        await send_slack_alert(
            title='CSP violation récurrente',
            summary=(
                f"*{group['n']} violations* en {_SLACK_WINDOW_H}h "
                f"au-delà du seuil ({_SLACK_THRESHOLD}).\n"
                f"Soit un script tiers légitime à autoriser dans la CSP, "
                f"soit une tentative d'injection."
            ),
            fields=[
                ('Directive', group['_id']['directive'] or '—'),
                ('Blocked URI', (group['_id']['blocked_uri'] or '—')[:200]),
                ('Fenêtre', f"{group['first']:%Y-%m-%d %H:%M} → {group['last']:%Y-%m-%d %H:%M}"),
                ('Occurrences', str(group['n'])),
            ],
            url='https://plume-astrale.fr/admin/csp-reports',
            url_label='Ouvrir /admin/csp-reports',
            emoji=':shield:',
        )


@router.get('/admin/csp-reports')
async def admin_csp_reports(
    hours: int = 24,
    _admin: dict = Depends(require_admin),
) -> Dict[str, Any]:
    """Agrégation admin des violations CSP sur ``hours`` dernières heures."""
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return {'ok': False, 'reason': 'db-unavailable', 'groups': [], 'total': 0}

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, min(hours, 24 * 30)))
    pipeline = [
        {'$match': {'reported_at': {'$gte': cutoff}}},
        {'$group': {
            '_id': {
                'directive': '$violated_directive',
                'blocked_uri': '$blocked_uri',
            },
            'n': {'$sum': 1},
            'last': {'$max': '$reported_at'},
            'first': {'$min': '$reported_at'},
            'sample_doc': {'$first': '$document_uri'},
        }},
        {'$sort': {'n': -1}},
        {'$limit': 100},
    ]
    groups: List[Dict[str, Any]] = []
    total = 0
    try:
        async for g in db[_CSP_COLL].aggregate(pipeline):
            groups.append({
                'directive': g['_id'].get('directive') or '',
                'blocked_uri': g['_id'].get('blocked_uri') or '',
                'count': g['n'],
                'first_seen': g['first'].isoformat() if g.get('first') else None,
                'last_seen':  g['last'].isoformat() if g.get('last') else None,
                'sample_document': g.get('sample_doc') or '',
            })
            total += g['n']
    except Exception as e:
        logger.warning(f'[csp_reports] admin aggregate fail: {e}')
        return {'ok': False, 'reason': 'aggregate', 'error': str(e)[:200]}

    return {
        'ok': True,
        'window_hours': hours,
        'threshold_slack': _SLACK_THRESHOLD,
        'total_in_window': total,
        'groups': groups,
    }
