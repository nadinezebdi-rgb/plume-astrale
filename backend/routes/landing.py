"""
Landing v3 endpoints :
  - GET  /api/landing/testimonials  → 5 derniers témoignages approuvés (public)
  - POST /api/landing/testimonials  → soumission témoignage (auth requise, statut pending)
  - GET  /api/landing/testimonials/admin → tous (approuvés + pending), admin only
  - POST /api/landing/testimonials/{id}/approve  → admin only
  - DELETE /api/landing/testimonials/{id}  → admin only

  - POST /api/landing/ab/track  → track impression/click d'une variante hero (public)
  - GET  /api/landing/ab/stats  → stats A/B hero, admin only

Persiste sur disque via services.app_settings (JSON) — pas de table DB dedicated.
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from middleware.auth import get_optional_user
from services.supabase_client import get_admin_client
from services.app_settings import get_setting, set_setting

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/landing', tags=['landing'])

# ═══════════════════════════════════════════════════════════════
# Testimonials
# ═══════════════════════════════════════════════════════════════

_SEED_TESTIMONIALS = [
    {
        'id': 'seed-lea-m',
        'initial': 'L', 'name': 'Léa M.', 'sign': 'Poissons', 'city': 'Lyon',
        'quote': "Rien de générique, rien de flou. Soléna m'a expliqué pourquoi je revivais toujours le même schéma — et comment le comprendre.",
        'transform_before': 'Je tournais en rond avec la même relation depuis 3 ans.',
        'transform_after': "J'ai enfin compris le nœud, et posé un vrai choix.",
        'status': 'approved', 'stars': 5,
        'created_at': '2026-07-15T10:00:00+00:00',
    },
    {
        'id': 'seed-sarah-t',
        'initial': 'S', 'name': 'Sarah T.', 'sign': 'Cancer', 'city': 'Bordeaux',
        'quote': "J'étais sceptique. La finesse de la lecture m'a scotchée. Ça m'a aidée à faire la paix avec une histoire de famille.",
        'transform_before': 'Un secret familial que je portais depuis toujours.',
        'transform_after': 'Une paix nouvelle avec mes racines.',
        'status': 'approved', 'stars': 5,
        'created_at': '2026-07-18T14:30:00+00:00',
    },
    {
        'id': 'seed-manon-d',
        'initial': 'M', 'name': 'Manon D.', 'sign': 'Lion', 'city': 'Marseille',
        'quote': 'Je relis ma lecture chaque semaine. Plus apaisant que trois ans à ressasser toute seule.',
        'transform_before': 'Nuits blanches à retourner les mêmes questions.',
        'transform_after': "Un cap clair pour l'année, et le sommeil revenu.",
        'status': 'approved', 'stars': 5,
        'created_at': '2026-07-22T09:15:00+00:00',
    },
]


def _load_testimonials() -> List[Dict[str, Any]]:
    """Charge la liste; seed le premier appel."""
    data = get_setting('landing_testimonials')
    if data is None:
        set_setting('landing_testimonials', _SEED_TESTIMONIALS)
        return list(_SEED_TESTIMONIALS)
    return list(data)


def _save_testimonials(items: List[Dict[str, Any]]) -> None:
    set_setting('landing_testimonials', items)


class TestimonialSubmit(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    sign: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=60)
    quote: str = Field(..., min_length=20, max_length=500)
    transform_before: Optional[str] = Field(None, max_length=200)
    transform_after: Optional[str] = Field(None, max_length=200)


@router.get('/testimonials')
async def landing_testimonials_public():
    """Renvoie jusqu'à 6 témoignages approuvés, du plus récent au plus ancien."""
    items = _load_testimonials()
    approved = [t for t in items if t.get('status') == 'approved']
    approved.sort(key=lambda t: t.get('created_at', ''), reverse=True)
    # Champs safe pour public (pas de status, pas d'email)
    return {
        'testimonials': [{
            'id': t['id'],
            'initial': t.get('initial') or (t.get('name') or '?')[:1].upper(),
            'name': t.get('name'),
            'sign': t.get('sign'),
            'city': t.get('city'),
            'quote': t.get('quote'),
            'transform_before': t.get('transform_before'),
            'transform_after': t.get('transform_after'),
            'stars': t.get('stars', 5),
        } for t in approved[:6]],
    }


@router.post('/testimonials')
async def landing_testimonial_submit(
    payload: TestimonialSubmit,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Soumission d'un témoignage. Reserve aux utilisateurs authentifies. Status pending."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Connecte-toi pour partager ton témoignage.')
    items = _load_testimonials()
    name = payload.name.strip()
    initial = (name[:1] or '?').upper()
    new = {
        'id': f'usr-{uuid.uuid4().hex[:12]}',
        'initial': initial,
        'name': name,
        'sign': (payload.sign or '').strip() or None,
        'city': (payload.city or '').strip() or None,
        'quote': payload.quote.strip(),
        'transform_before': (payload.transform_before or '').strip() or None,
        'transform_after': (payload.transform_after or '').strip() or None,
        'status': 'pending',
        'stars': 5,
        'author_id': current_user.get('id'),
        'author_email': current_user.get('email'),
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    items.append(new)
    _save_testimonials(items)
    return {'submitted': True, 'id': new['id'], 'status': 'pending'}


async def _require_admin(current_user: Optional[dict]) -> dict:
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    return current_user


@router.get('/testimonials/admin')
async def landing_testimonials_admin_list(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    items.sort(key=lambda t: t.get('created_at', ''), reverse=True)
    return {'testimonials': items}


@router.post('/testimonials/{tid}/approve')
async def landing_testimonial_approve(
    tid: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    for t in items:
        if t.get('id') == tid:
            t['status'] = 'approved'
            _save_testimonials(items)
            return {'approved': True, 'id': tid}
    raise HTTPException(status_code=404, detail='Témoignage introuvable.')


@router.delete('/testimonials/{tid}')
async def landing_testimonial_delete(
    tid: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    await _require_admin(current_user)
    items = _load_testimonials()
    new_items = [t for t in items if t.get('id') != tid]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail='Témoignage introuvable.')
    _save_testimonials(new_items)
    return {'deleted': True, 'id': tid}


# ═══════════════════════════════════════════════════════════════
# A/B test hero headline
# ═══════════════════════════════════════════════════════════════

VALID_VARIANTS = ('A', 'B')
VALID_EVENTS = ('impression', 'cta_click', 'signup_click')


class ABTrackPayload(BaseModel):
    variant: str
    event: str


@router.post('/ab/track')
async def landing_ab_track(payload: ABTrackPayload):
    """Track une impression ou un clic pour la variante hero A/B (public, no auth)."""
    if payload.variant not in VALID_VARIANTS:
        raise HTTPException(status_code=400, detail='variant doit être A ou B.')
    if payload.event not in VALID_EVENTS:
        raise HTTPException(status_code=400, detail=f'event doit être parmi {VALID_EVENTS}.')
    stats = get_setting('landing_ab_hero_stats') or {}
    key = payload.variant
    row = stats.get(key) or {'impression': 0, 'cta_click': 0, 'signup_click': 0}
    row[payload.event] = int(row.get(payload.event, 0)) + 1
    stats[key] = row
    set_setting('landing_ab_hero_stats', stats)
    return {'ok': True}


@router.get('/ab/stats')
async def landing_ab_stats(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Stats A/B hero, admin only."""
    await _require_admin(current_user)
    stats = get_setting('landing_ab_hero_stats') or {}
    result: Dict[str, Any] = {'variants': {}}
    for v in VALID_VARIANTS:
        row = stats.get(v) or {'impression': 0, 'cta_click': 0, 'signup_click': 0}
        imp = row.get('impression', 0)
        ctc = row.get('cta_click', 0) + row.get('signup_click', 0)
        ctr = round((ctc / imp * 100), 2) if imp else 0.0
        result['variants'][v] = {
            **row,
            'total_clicks': ctc,
            'ctr_pct': ctr,
        }
    # Detect winner (>50 impressions each + CTR delta ≥ 1pt)
    a, b = result['variants']['A'], result['variants']['B']
    if a['impression'] >= 50 and b['impression'] >= 50 and abs(a['ctr_pct'] - b['ctr_pct']) >= 1.0:
        result['winner'] = 'A' if a['ctr_pct'] > b['ctr_pct'] else 'B'
    else:
        result['winner'] = None
    result['headlines'] = {
        'A': 'Ton ciel de naissance contient une carte.',
        'B': "La lecture que ton ciel attendait.",
    }
    return result
