"""Wallet & credits — backed by Supabase Postgres via service_role client."""
from fastapi import HTTPException
from services.supabase_client import get_admin_client


async def get_balance(user_id: str) -> int:
    sb = get_admin_client()
    res = sb.table('wallets').select('credit_balance').eq('user_id', user_id).maybe_single().execute()
    if not res or not res.data:
        # auto-create wallet if missing (failsafe en plus du trigger)
        sb.table('wallets').insert({'user_id': user_id, 'credit_balance': 20}).execute()
        return 20
    return int(res.data['credit_balance'])


# ─── Chat credits (Cercle Soléna) — wallet séparé ────────────────────────
# Ajouté 2026-02 : les crédits chat_credits sont réservés au chat Plume/Solena.
# La logique `charge_or_premium(service_id='chat_astral')` consomme d'abord
# `chat_credit_balance`, puis fallback sur `credit_balance` (universel).

async def get_chat_balance(user_id: str) -> int:
    """Renvoie le solde de chat_credits (0 si la colonne n'existe pas encore)."""
    sb = get_admin_client()
    try:
        res = sb.table('wallets').select('chat_credit_balance').eq('user_id', user_id).maybe_single().execute()
        if not res or not res.data:
            return 0
        return int(res.data.get('chat_credit_balance') or 0)
    except Exception:
        # Colonne pas encore migrée en base → considère 0 (fallback safe)
        return 0


async def add_chat_credits(user_id: str, amount: int, description: str, tx_type: str = 'grant') -> int:
    """Crédite `amount` chat_credits. Renvoie le nouveau solde chat."""
    if amount <= 0:
        return await get_chat_balance(user_id)
    sb = get_admin_client()
    current = await get_chat_balance(user_id)
    new_balance = current + amount
    try:
        sb.table('wallets').update({'chat_credit_balance': new_balance}).eq('user_id', user_id).execute()
    except Exception as e:
        # Migration non appliquée : log + return current (best-effort)
        import logging
        logging.getLogger(__name__).warning(f'[wallet.add_chat_credits] echec update (colonne manquante?) : {e}')
        return current
    try:
        sb.table('credit_transactions').insert({
            'user_id': user_id,
            'tx_type': tx_type,
            'amount': amount,
            'description': f'[chat] {description}',
        }).execute()
    except Exception:
        pass
    return new_balance


async def deduct_chat_or_credits(user_id: str, amount: int, description: str) -> dict:
    """Deduit d'abord depuis chat_credit_balance, puis fallback sur credit_balance (universel).
    Renvoie {'chat_used': int, 'universal_used': int, 'chat_balance': int, 'balance': int}."""
    if amount <= 0:
        return {'chat_used': 0, 'universal_used': 0, 'chat_balance': await get_chat_balance(user_id), 'balance': await get_balance(user_id)}
    sb = get_admin_client()
    chat_bal = await get_chat_balance(user_id)
    univ_bal = await get_balance(user_id)
    if chat_bal + univ_bal < amount:
        raise HTTPException(status_code=402, detail='Solde insuffisant')
    chat_used = min(chat_bal, amount)
    univ_used = amount - chat_used
    new_chat = chat_bal - chat_used
    new_univ = univ_bal - univ_used
    try:
        if chat_used > 0:
            sb.table('wallets').update({'chat_credit_balance': new_chat}).eq('user_id', user_id).execute()
    except Exception:
        # Migration pas appliquée : bascule tout sur wallet universel
        chat_used = 0
        univ_used = amount
        new_chat = chat_bal
        new_univ = univ_bal - amount
    if univ_used > 0:
        sb.table('wallets').update({'credit_balance': new_univ}).eq('user_id', user_id).execute()
    sb.table('credit_transactions').insert({
        'user_id': user_id,
        'tx_type': 'deduction',
        'amount': -amount,
        'description': f'{description} (chat:{chat_used} + univ:{univ_used})',
    }).execute()
    return {'chat_used': chat_used, 'universal_used': univ_used, 'chat_balance': new_chat, 'balance': new_univ}


async def has_used_free_tarot(user_id: str) -> bool:
    sb = get_admin_client()
    res = sb.table('wallets').select('free_tarot_used').eq('user_id', user_id).maybe_single().execute()
    return bool(res and res.data and res.data.get('free_tarot_used'))


async def mark_free_tarot_used(user_id: str):
    sb = get_admin_client()
    sb.table('wallets').update({'free_tarot_used': True}).eq('user_id', user_id).execute()


async def is_premium_active(user_id: str) -> bool:
    """True si l'utilisateur a un premium en cours."""
    from datetime import datetime, timezone
    sb = get_admin_client()
    res = sb.table('profiles').select('premium_status, premium_until').eq('id', user_id).maybe_single().execute()
    if not res or not res.data:
        return False
    data = res.data
    if data.get('premium_status') != 'active':
        return False
    until = data.get('premium_until')
    if not until:
        return True
    try:
        dt = datetime.fromisoformat(str(until).replace('Z', '+00:00'))
        return dt > datetime.now(timezone.utc)
    except Exception:
        return False


async def deduct_credits(user_id: str, amount: int, description: str) -> int:
    """Deduct `amount` credits if balance is sufficient. Returns new balance."""
    sb = get_admin_client()
    balance = await get_balance(user_id)
    if balance < amount:
        raise HTTPException(status_code=402, detail='Solde insuffisant')
    new_balance = balance - amount
    sb.table('wallets').update({'credit_balance': new_balance}).eq('user_id', user_id).execute()
    sb.table('credit_transactions').insert({
        'user_id': user_id,
        'tx_type': 'deduction',
        'amount': -amount,
        'description': description,
    }).execute()
    return new_balance


async def charge_or_premium(user_id: str, service_id: str, amount: int, description: str) -> dict:
    """Premium = pas de deduction. Sinon deduit amount credits.
    Pour le chat (service_id='chat_astral'), consomme d'abord chat_credit_balance,
    puis fallback sur credit_balance universel.
    Renvoie {'charged': bool, 'amount': int, 'is_premium': bool, 'new_balance': int|None,
             'chat_used': int, 'universal_used': int, 'new_chat_balance': int}."""
    premium = await is_premium_active(user_id)
    if premium:
        return {'charged': False, 'amount': 0, 'is_premium': True, 'new_balance': None,
                'chat_used': 0, 'universal_used': 0, 'new_chat_balance': None}
    # Chat astral : consomme d'abord le wallet chat, puis fallback universel
    if service_id == 'chat_astral':
        result = await deduct_chat_or_credits(user_id, amount, description)
        return {
            'charged': True, 'amount': amount, 'is_premium': False,
            'new_balance': result['balance'],
            'chat_used': result['chat_used'],
            'universal_used': result['universal_used'],
            'new_chat_balance': result['chat_balance'],
        }
    # Autres services : deduction universelle classique
    new_balance = await deduct_credits(user_id, amount, description)
    return {'charged': True, 'amount': amount, 'is_premium': False, 'new_balance': new_balance,
            'chat_used': 0, 'universal_used': amount, 'new_chat_balance': None}


async def add_credits(user_id: str, amount: int, description: str, tx_type: str = 'purchase') -> int:
    sb = get_admin_client()
    balance = await get_balance(user_id)
    new_balance = balance + amount
    sb.table('wallets').update({'credit_balance': new_balance}).eq('user_id', user_id).execute()
    sb.table('credit_transactions').insert({
        'user_id': user_id,
        'tx_type': tx_type,
        'amount': amount,
        'description': description,
    }).execute()
    return new_balance


async def get_transactions(user_id: str, limit: int = 50) -> list:
    sb = get_admin_client()
    res = sb.table('credit_transactions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
    return res.data or []


async def get_profile(user_id: str) -> dict:
    sb = get_admin_client()
    res = sb.table('profiles').select('*').eq('id', user_id).maybe_single().execute()
    return (res.data if res else None) or {}


async def update_profile(user_id: str, data: dict) -> dict:
    sb = get_admin_client()
    payload = {k: v for k, v in data.items() if v is not None}
    if not payload:
        return await get_profile(user_id)
    sb.table('profiles').upsert({'id': user_id, **payload}).execute()
    return await get_profile(user_id)


async def redeem_promo(user_id: str, code: str) -> dict:
    sb = get_admin_client()
    code = code.strip().upper()
    promo = sb.table('promo_codes').select('*').eq('code', code).eq('active', True).maybe_single().execute()
    if not promo or not promo.data:
        raise HTTPException(status_code=404, detail='Code promo invalide ou expire')
    promo_data = promo.data
    if promo_data.get('max_uses') and promo_data.get('used_count', 0) >= promo_data['max_uses']:
        raise HTTPException(status_code=410, detail='Ce code promo a atteint sa limite')

    # Verifier que l'utilisateur ne l'a pas deja utilise
    redemption = sb.table('promo_code_redemptions').select('id').eq('user_id', user_id).eq('code', code).maybe_single().execute()
    if redemption and redemption.data:
        raise HTTPException(status_code=409, detail='Tu as deja utilise ce code promo')

    credits = int(promo_data.get('credits') or 0)
    premium_days = int(promo_data.get('premium_days') or 0)
    description = promo_data.get('description') or f'Code promo {code}'
    new_balance = await get_balance(user_id)

    # 1) Crediter si applicable
    if credits > 0:
        new_balance = await add_credits(user_id, credits, description, tx_type='promo')

    # 2) Activer Premium si applicable
    premium_until_iso = None
    if premium_days > 0:
        from datetime import datetime, timezone, timedelta
        # Si user a deja un premium_until futur, on l'etend ; sinon on demarre maintenant
        prof = sb.table('profiles').select('premium_until').eq('id', user_id).maybe_single().execute()
        now = datetime.now(timezone.utc)
        current_until = None
        if prof and prof.data and prof.data.get('premium_until'):
            try:
                current_until = datetime.fromisoformat(prof.data['premium_until'].replace('Z', '+00:00'))
            except Exception:
                current_until = None
        base = current_until if (current_until and current_until > now) else now
        new_until = base + timedelta(days=premium_days)
        premium_until_iso = new_until.isoformat()
        sb.table('profiles').update({
            'premium_status': 'active',
            'premium_until': premium_until_iso,
        }).eq('id', user_id).execute()

    # Enregistrer la redemption
    sb.table('promo_code_redemptions').insert({'user_id': user_id, 'code': code}).execute()
    sb.table('promo_codes').update({'used_count': promo_data.get('used_count', 0) + 1}).eq('code', code).execute()

    return {
        'credits_added': credits,
        'premium_days_added': premium_days,
        'premium_until': premium_until_iso,
        'description': description,
        'credit_balance': new_balance,
    }
