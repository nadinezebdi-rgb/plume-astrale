"""admin_promo — Gestion des codes promo (CRUD).

Extrait de `routes/admin.py` lors du refactor 2026-02 (admin.py > 1200 lignes).
Monté sur le même préfixe `/admin` pour préserver les URLs existantes.
"""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException

from routes.admin import require_admin
from services.supabase_client import get_admin_client

router = APIRouter(prefix='/admin', tags=['admin', 'promo'])
logger = logging.getLogger(__name__)


@router.get('/promo-codes')
async def admin_promo_codes(_admin: dict = Depends(require_admin)):
    """Liste des codes promo + nombre d'utilisations."""
    sb = get_admin_client()
    codes = sb.table('promo_codes').select('*').order('created_at', desc=True).execute().data or []
    return {'codes': codes}


@router.post('/promo-codes')
async def admin_create_promo_code(payload: dict, _admin: dict = Depends(require_admin)):
    """Creer un code promo (credits OU premium_days)."""
    sb = get_admin_client()
    code = (payload.get('code') or '').strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail='Code requis')
    credits = int(payload.get('credits') or 0)
    premium_days = int(payload.get('premium_days') or 0)
    if credits <= 0 and premium_days <= 0:
        raise HTTPException(status_code=400, detail='Soit credits>0, soit premium_days>0')
    description = payload.get('description') or (f'Premium offert {premium_days} jours' if premium_days else f'{credits} credits offerts')
    max_uses = payload.get('max_uses')
    active = payload.get('active', True)
    try:
        sb.table('promo_codes').insert({
            'code': code,
            'credits': credits,
            'premium_days': premium_days if premium_days > 0 else None,
            'description': description,
            'max_uses': int(max_uses) if max_uses else None,
            'active': bool(active),
            'used_count': 0,
        }).execute()
    except Exception as e:
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
            raise HTTPException(status_code=409, detail='Ce code existe deja')
        raise
    return {'success': True, 'code': code}


@router.patch('/promo-codes/{code}')
async def admin_toggle_promo_code(code: str, payload: dict, _admin: dict = Depends(require_admin)):
    """Activer/desactiver un code promo."""
    sb = get_admin_client()
    code = code.strip().upper()
    update_fields = {}
    if 'active' in payload:
        update_fields['active'] = bool(payload['active'])
    if 'max_uses' in payload:
        update_fields['max_uses'] = int(payload['max_uses']) if payload['max_uses'] else None
    if not update_fields:
        raise HTTPException(status_code=400, detail='Aucun champ a modifier')
    res = sb.table('promo_codes').update(update_fields).eq('code', code).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail='Code introuvable')
    return {'success': True, 'code': code, 'updated': update_fields}


@router.delete('/promo-codes/{code}')
async def admin_delete_promo_code(code: str, _admin: dict = Depends(require_admin)):
    """Supprimer un code promo."""
    sb = get_admin_client()
    sb.table('promo_codes').delete().eq('code', code.strip().upper()).execute()
    return {'success': True}
