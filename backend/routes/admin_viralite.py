"""admin_viralite — Endpoints admin sur la viralité des tirages tarot partagés.

Extrait de `routes/admin.py` lors du refactor 2026-02 (admin.py > 1200 lignes).
Monté sur le même préfixe `/admin` pour conserver les URLs existantes.
"""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query

from db import get_db
from routes.admin import require_admin

router = APIRouter(prefix='/admin', tags=['admin', 'viralite'])
logger = logging.getLogger(__name__)


@router.get('/tarot-share/top')
async def admin_top_shared_tirages(
    limit: int = Query(20, ge=1, le=100),
    _admin: dict = Depends(require_admin),
):
    """Top N des tirages partagés par nombre de vues (collection `shared_tirages`).

    Utile pour identifier les tirages qui buzzent (bouche-à-oreille, viralité
    IG/WhatsApp). Chaque entrée : share_id, type, question, first_name,
    view_count, created_at.
    """
    try:
        db = get_db()
        cursor = db.shared_tirages.find(
            {},
            projection={
                '_id': 0, 'share_id': 1, 'type': 1, 'question': 1,
                'domaine': 1, 'first_name': 1, 'view_count': 1,
                'created_at': 1,
            },
        ).sort('view_count', -1).limit(limit)
        items = []
        async for doc in cursor:
            if doc.get('created_at') and hasattr(doc['created_at'], 'isoformat'):
                doc['created_at'] = doc['created_at'].isoformat()
            items.append(doc)
        total_shares = await db.shared_tirages.count_documents({})
        total_views_cursor = db.shared_tirages.aggregate([
            {'$group': {'_id': None, 'total': {'$sum': '$view_count'}}}
        ])
        total_views = 0
        async for row in total_views_cursor:
            total_views = row.get('total') or 0
        return {
            'items': items,
            'total_shares': total_shares,
            'total_views': total_views,
            'avg_views_per_share': round(total_views / total_shares, 1) if total_shares else 0,
        }
    except Exception as e:
        logger.exception(f'[admin_viralite] top-shared-tirages failed: {e}')
        raise HTTPException(status_code=500, detail='Lecture viralité indisponible.')
