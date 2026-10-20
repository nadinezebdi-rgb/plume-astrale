"""Routes /api/analytics/* — tracking first-party des expériences A/B.

Endpoint public POST /ab-event : écrit dans la table `ab_events` (voir migration
/app/backend/migrations/2026_02_ab_events.sql). Dégrade gracieusement si table
absente (log warning).
"""
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/analytics', tags=['analytics'])


class ABEventRequest(BaseModel):
    experiment: str = Field(..., min_length=1, max_length=80)
    variant: str = Field(..., min_length=1, max_length=20)
    event_name: str = Field(..., min_length=1, max_length=40)
    session_id: Optional[str] = Field(None, max_length=120)
    metadata: Optional[Dict[str, Any]] = None


@router.post('/ab-event')
async def ab_event(payload: ABEventRequest):
    """Persiste un évènement A/B. Toujours 200 OK (ne doit jamais casser le front)."""
    try:
        sb = get_admin_client()
        sb.table('ab_events').insert({
            'experiment': payload.experiment[:80],
            'variant': payload.variant[:20],
            'event_name': payload.event_name[:40],
            'session_id': (payload.session_id or '')[:120] or None,
            'metadata': payload.metadata or {},
        }).execute()
        return {'ok': True}
    except Exception as e:
        msg = str(e)
        if 'ab_events' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning('[ab_event] Table ab_events absente — exécuter 2026_02_ab_events.sql')
        else:
            logger.warning(f'[ab_event] persist failed: {msg[:200]}')
        return {'ok': False, 'reason': 'persist_failed'}
