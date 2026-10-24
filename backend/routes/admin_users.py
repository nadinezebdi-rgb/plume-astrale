"""admin_users — Gestion des utilisateurs (listing, crédits, premium, delete).

Extrait de `routes/admin.py` lors du refactor 2026-02.
Monté sur le même préfixe `/admin`.
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from routes.admin import require_admin
from services.supabase_client import get_admin_client

router = APIRouter(prefix='/admin', tags=['admin', 'users'])
logger = logging.getLogger(__name__)


def _users_fetch_wallets(sb, user_ids: list) -> dict:
    if not user_ids:
        return {}
    w_res = sb.table('wallets').select('user_id,credit_balance,free_tarot_used').in_('user_id', user_ids).execute()
    return {w['user_id']: w for w in (w_res.data or [])}


def _users_fetch_spent(sb, user_ids: list) -> dict:
    if not user_ids:
        return {}
    spent = {}
    p_res = sb.table('payment_transactions').select('user_id,amount').eq('credits_granted', True).in_('user_id', user_ids).execute()
    for p in (p_res.data or []):
        spent[p['user_id']] = spent.get(p['user_id'], 0) + float(p.get('amount') or 0)
    return spent


def _format_admin_user(p: dict, wallets_map: dict, spent_map: dict) -> dict:
    w = wallets_map.get(p['id'], {})
    return {
        'id': p['id'],
        'email': p.get('email'),
        'prenom': p.get('prenom'),
        'birth_date': p.get('birth_date'),
        'birth_place': p.get('birth_place'),
        'is_admin': p.get('is_admin', False),
        'premium_status': p.get('premium_status', 'free'),
        'premium_until': p.get('premium_until'),
        'created_at': p.get('created_at'),
        'credit_balance': w.get('credit_balance', 0),
        'free_tarot_used': w.get('free_tarot_used', False),
        'total_spent_eur': round(spent_map.get(p['id'], 0), 2),
    }


@router.get('/users')
async def admin_users(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
):
    """Liste paginee des utilisateurs avec leur solde."""
    sb = get_admin_client()
    offset = (page - 1) * page_size

    q = sb.table('profiles').select('*', count='exact').order('created_at', desc=True)
    if search:
        q = q.ilike('email', f'%{search}%')

    res = q.range(offset, offset + page_size - 1).execute()
    profiles = res.data or []
    total = res.count or 0

    user_ids = [p['id'] for p in profiles]
    wallets_map = _users_fetch_wallets(sb, user_ids)
    spent_map = _users_fetch_spent(sb, user_ids)

    users = [_format_admin_user(p, wallets_map, spent_map) for p in profiles]

    return {'users': users, 'total': total, 'page': page, 'page_size': page_size}


# ─────────────────────────────────────────────────────────────────
# Admin actions on a single user : credits & premium
# ─────────────────────────────────────────────────────────────────
class AdminCreditsRequest(BaseModel):
    amount: int  # positif = add, negatif = retirer
    description: Optional[str] = 'Ajustement admin'


@router.post('/users/{user_id}/credits')
async def admin_adjust_credits(
    user_id: str,
    payload: AdminCreditsRequest,
    _admin: dict = Depends(require_admin),
):
    """Ajoute (ou retire si negatif) des credits a un utilisateur."""
    if payload.amount == 0:
        raise HTTPException(status_code=400, detail='Le montant ne peut pas etre 0')

    sb = get_admin_client()
    w = sb.table('wallets').select('credit_balance').eq('user_id', user_id).maybe_single().execute()
    current = int((w.data or {}).get('credit_balance', 0)) if w and w.data else 0
    new_balance = max(0, current + payload.amount)

    if w and w.data:
        sb.table('wallets').update({'credit_balance': new_balance}).eq('user_id', user_id).execute()
    else:
        sb.table('wallets').insert({'user_id': user_id, 'credit_balance': new_balance}).execute()

    sb.table('credit_transactions').insert({
        'user_id': user_id,
        'tx_type': 'admin_gift' if payload.amount > 0 else 'admin_deduction',
        'amount': payload.amount,
        'description': payload.description or 'Ajustement admin',
    }).execute()

    return {
        'success': True,
        'user_id': user_id,
        'previous_balance': current,
        'new_balance': new_balance,
        'delta': payload.amount,
    }


class AdminPremiumRequest(BaseModel):
    action: Literal['grant_days', 'grant_lifetime', 'revoke']
    days: Optional[int] = None  # requis si action == grant_days


@router.post('/users/{user_id}/premium')
async def admin_set_premium(
    user_id: str,
    payload: AdminPremiumRequest,
    _admin: dict = Depends(require_admin),
):
    """Gere le Premium d'un utilisateur :
    - grant_days N : ajoute N jours a partir d'aujourd'hui ou prolonge si deja Premium
    - grant_lifetime : Premium a vie (jusqu'en 2099)
    - revoke : retire le Premium immediatement
    """
    sb = get_admin_client()

    if payload.action == 'revoke':
        sb.table('profiles').update({
            'premium_status': 'free',
            'premium_until': None,
        }).eq('id', user_id).execute()
        return {'success': True, 'user_id': user_id, 'premium_status': 'free', 'premium_until': None}

    if payload.action == 'grant_lifetime':
        until_iso = '2099-12-31T23:59:59+00:00'
    elif payload.action == 'grant_days':
        if not payload.days or payload.days <= 0:
            raise HTTPException(status_code=400, detail="Le nombre de jours doit etre > 0")
        prof = sb.table('profiles').select('premium_until').eq('id', user_id).maybe_single().execute()
        base = datetime.now(timezone.utc)
        if prof and prof.data and prof.data.get('premium_until'):
            try:
                current_until = datetime.fromisoformat(prof.data['premium_until'].replace('Z', '+00:00'))
                if current_until > base:
                    base = current_until
            except Exception:
                pass
        until_iso = (base + timedelta(days=int(payload.days))).isoformat()
    else:
        raise HTTPException(status_code=400, detail='Action invalide')

    sb.table('profiles').update({
        'premium_status': 'active',
        'premium_until': until_iso,
    }).eq('id', user_id).execute()

    return {
        'success': True,
        'user_id': user_id,
        'premium_status': 'active',
        'premium_until': until_iso,
        'action': payload.action,
    }


@router.post('/users/{user_id}/grant-credits')
async def admin_grant_credits(
    user_id: str,
    payload: dict,
    _admin: dict = Depends(require_admin),
):
    """Crediter manuellement un utilisateur depuis le dashboard."""
    from services.wallet_service import add_credits
    amount = int(payload.get('amount', 0))
    reason = payload.get('reason', 'Credit manuel admin')
    if amount == 0:
        raise HTTPException(status_code=400, detail='amount requis')
    new_balance = await add_credits(user_id, amount, reason, tx_type='admin_grant')
    return {'success': True, 'new_balance': new_balance}


@router.delete('/users/{user_id}')
async def admin_delete_user(user_id: str, current_admin: dict = Depends(require_admin)):
    """Supprimer definitivement un utilisateur (auth + profil + donnees liees).
    Protection : impossible de se supprimer soi-meme ou de supprimer un autre admin."""
    if user_id == current_admin['id']:
        raise HTTPException(status_code=400, detail='Impossible de te supprimer toi-meme')
    sb = get_admin_client()
    target = sb.table('profiles').select('is_admin,email').eq('id', user_id).maybe_single().execute()
    if not target or not target.data:
        raise HTTPException(status_code=404, detail='Utilisateur introuvable')
    if target.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Impossible de supprimer un admin')

    # Cascade manuelle sur les tables qui ne sont pas ON DELETE CASCADE
    try:
        sb.table('wallets').delete().eq('user_id', user_id).execute()
        sb.table('credit_transactions').delete().eq('user_id', user_id).execute()
        sb.table('payment_transactions').delete().eq('user_id', user_id).execute()
        sb.table('plume_chat_messages').delete().eq('user_id', user_id).execute()
        sb.table('promo_code_redemptions').delete().eq('user_id', user_id).execute()
        sb.table('subscriptions').delete().eq('user_id', user_id).execute()
        sb.table('energy_cache').delete().eq('user_id', user_id).execute()
    except Exception as e:
        logger.warning(f'[admin_delete_user] cascade warning: {e}')

    sb.table('profiles').delete().eq('id', user_id).execute()

    try:
        sb.auth.admin.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Profil supprime, mais auth.users a echoue : {e}')

    return {'success': True, 'deleted_user_id': user_id, 'email': target.data.get('email')}
