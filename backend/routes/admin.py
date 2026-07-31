"""Admin endpoints — dashboard stats + listings (protected by is_admin flag)."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta, timezone
from typing import Optional

from middleware.auth import get_current_user
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin'])


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency : verifie que l'utilisateur est admin."""
    sb = get_admin_client()
    r = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not r or not r.data or not r.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Acces admin requis')
    return current_user


@router.get('/stats')
async def admin_stats(_admin: dict = Depends(require_admin)):
    """KPIs principaux du dashboard."""
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()

    # Total utilisateurs
    total_users = sb.table('profiles').select('id', count='exact').execute().count or 0

    # Signups aujourd'hui / 7j / 30j (via created_at)
    signups_today = sb.table('profiles').select('id', count='exact').gte('created_at', today + 'T00:00:00').execute().count or 0
    signups_7d = sb.table('profiles').select('id', count='exact').gte('created_at', week_ago).execute().count or 0
    signups_30d = sb.table('profiles').select('id', count='exact').gte('created_at', month_ago).execute().count or 0

    # Paiements completes (credits_granted=true)
    paid_txs = sb.table('payment_transactions').select('*').eq('credits_granted', True).execute().data or []
    total_revenue = sum(float(t.get('amount') or 0) for t in paid_txs)
    revenue_7d = sum(float(t.get('amount') or 0) for t in paid_txs if t.get('created_at', '') >= week_ago)
    revenue_30d = sum(float(t.get('amount') or 0) for t in paid_txs if t.get('created_at', '') >= month_ago)
    total_paid_count = len(paid_txs)
    paying_users = len({t['user_id'] for t in paid_txs if t.get('user_id')})

    # Stripe sessions initiees mais pas payees (= abandons / en attente)
    pending = sb.table('payment_transactions').select('session_id', count='exact').eq('credits_granted', False).execute().count or 0

    # Credits en circulation
    wallets = sb.table('wallets').select('credit_balance').execute().data or []
    credits_in_wallets = sum(int(w['credit_balance']) for w in wallets)

    # Messages chat envoyes
    chat_msgs = sb.table('plume_chat_messages').select('id', count='exact').eq('role', 'user').execute().count or 0

    # Codes promo utilises
    promo_redemptions = sb.table('promo_code_redemptions').select('id', count='exact').execute().count or 0

    conversion_rate = round((paying_users / total_users * 100), 2) if total_users else 0.0

    return {
        'users': {
            'total': total_users,
            'signups_today': signups_today,
            'signups_7d': signups_7d,
            'signups_30d': signups_30d,
            'paying_users': paying_users,
            'conversion_rate_pct': conversion_rate,
        },
        'revenue': {
            'total_eur': round(total_revenue, 2),
            'last_7d_eur': round(revenue_7d, 2),
            'last_30d_eur': round(revenue_30d, 2),
            'total_paid_count': total_paid_count,
            'pending_count': pending,
        },
        'engagement': {
            'credits_in_wallets': credits_in_wallets,
            'chat_messages_sent': chat_msgs,
            'promo_redemptions': promo_redemptions,
        },
        'updated_at': now.isoformat(),
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

    # Recuperer wallets en batch
    user_ids = [p['id'] for p in profiles]
    wallets_map = {}
    if user_ids:
        w_res = sb.table('wallets').select('user_id,credit_balance,free_tarot_used').in_('user_id', user_ids).execute()
        wallets_map = {w['user_id']: w for w in (w_res.data or [])}

    # Recuperer total depense en batch
    spent_map = {}
    if user_ids:
        p_res = sb.table('payment_transactions').select('user_id,amount').eq('credits_granted', True).in_('user_id', user_ids).execute()
        for p in (p_res.data or []):
            spent_map[p['user_id']] = spent_map.get(p['user_id'], 0) + float(p.get('amount') or 0)

    users = []
    for p in profiles:
        w = wallets_map.get(p['id'], {})
        users.append({
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
        })

    return {'users': users, 'total': total, 'page': page, 'page_size': page_size}


# ─────────────────────────────────────────────────────────────────
# Admin actions on a single user : credits & premium
# ─────────────────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import Literal


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
        # Si deja Premium actif futur, on prolonge ; sinon on demarre maintenant
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


@router.get('/chat-sessions')
async def admin_chat_sessions(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Liste des sessions de chat avec compteur de messages."""
    sb = get_admin_client()
    # Aggregation : count par session_id + dernier message
    res = sb.table('plume_chat_messages').select('*').order('created_at', desc=True).limit(page_size * 2).execute()
    msgs = res.data or []

    # Grouper par session
    sessions = {}
    for m in msgs:
        sid = m['session_id']
        if sid not in sessions:
            sessions[sid] = {
                'session_id': sid,
                'user_id': m.get('user_id'),
                'last_message_at': m['created_at'],
                'last_message': m['content'][:100],
                'message_count': 0,
            }
        sessions[sid]['message_count'] += 1

    return {'sessions': list(sessions.values())[:page_size]}


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
        # tables optionnelles -> on ignore les erreurs
        print(f'[admin_delete_user] cascade warning: {e}')

    # Supprimer le profil
    sb.table('profiles').delete().eq('id', user_id).execute()

    # Supprimer le compte Supabase Auth
    try:
        sb.auth.admin.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Profil supprime, mais auth.users a echoue : {e}')

    return {'success': True, 'deleted_user_id': user_id, 'email': target.data.get('email')}


@router.post('/cron/send-daily-journal')
async def cron_send_daily_journal(cron_secret: Optional[str] = Query(None)):
    """Envoyer le journal quotidien à tous les utilisateurs (cron task).

    SEC-hardening : CRON_SECRET est OBLIGATOIRE. Sans lui, refus explicite
    pour empêcher un attaquant de déclencher un spam Resend en masse.
    Appelé par une tâche cron externe (EasyCron, Railway Cron, etc).
    """
    import os
    env_secret = os.getenv('CRON_SECRET')
    if not env_secret:
        logger.error('[cron] CRON_SECRET manquant en env — refus.')
        raise HTTPException(status_code=503, detail='CRON_SECRET not configured on server')
    if not cron_secret or cron_secret != env_secret:
        raise HTTPException(status_code=403, detail='Invalid cron secret')

    from services.journal_email_service import send_daily_journal_batch
    result = await send_daily_journal_batch()
    return result



@router.post('/regenerate-horoscopes')
async def regenerate_horoscopes(_admin: dict = Depends(require_admin)):
    """
    Force la régénération manuelle des 12 PDFs d'horoscope journalier.
    Utile pour tester ou forcer un rafraîchissement hors de la fenêtre quotidienne 6h UTC.

    Le processus prend ~2 min (12 appels API + 12 appels GPT-5.2).
    Renvoie immédiatement (background task).
    """
    import asyncio
    from services.horoscope_scheduler import _regenerate_all
    asyncio.create_task(_regenerate_all())
    return {
        'ok': True,
        'message': "Régénération lancée en background — ~2 min. Vérifie /api/health/horoscopes ou les logs backend.",
    }



@router.get('/pdfs-sent')
async def admin_pdfs_sent(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    product: str = '',
):
    """
    Liste des PDFs envoyés aux clients — filtrés sur metadata.pdf_supabase_url
    (uniquement les rapports stockés dans le bucket Supabase 'reports',
    dont l'URL survit aux redeploys).

    Renvoie : email du client, type de rapport, date d'envoi, URL de téléchargement.
    """
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
            continue  # Filtre : uniquement les PDFs présents sur Supabase Storage
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
    return {'items': items, 'total_with_supabase_url': len(items), 'total_completed': res.count or 0, 'page': page, 'page_size': page_size}



@router.post('/theme-natal/regenerate/{session_id}')
async def admin_regenerate_theme_natal(session_id: str, _admin: dict = Depends(require_admin)):
    """Force la régénération complète d'un PDF Thème Natal one-shot pour une session donnée.

    Utile après refonte du template : les anciennes sessions ont l'ancien PDF
    en cache (idempotence). Cet endpoint bypass l'idempotence et upload un
    nouveau PDF avec cache-buster sur l'URL Supabase.
    """
    from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
    sb = get_admin_client()
    # Vérification que la session existe et est bien un theme_natal one-shot
    r = sb.table('payment_transactions').select('metadata, status').eq('session_id', session_id).maybe_single().execute()
    if not r or not r.data:
        raise HTTPException(status_code=404, detail='Session introuvable')
    md = r.data.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        raise HTTPException(status_code=400, detail='La session n\'est pas un Thème Natal one-shot')
    try:
        await handle_theme_natal_oneshot_webhook(session_id, force=True)
    except Exception as e:
        logger.exception(f'[admin] regenerate theme_natal fail {session_id}')
        raise HTTPException(status_code=500, detail=f'Regénération échouée : {e}')
    # Retourne la nouvelle URL fraîche
    r2 = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
    md2 = (r2.data or {}).get('metadata') or {}
    return {
        'ok': True,
        'session_id': session_id,
        'pdf_path': md2.get('pdf_path'),
        'pdf_supabase_url': md2.get('pdf_supabase_url'),
        'pdf_generated_at': md2.get('pdf_generated_at'),
    }



@router.get('/theme-natal/inspect/{session_id}')
async def admin_inspect_theme_natal(session_id: str, _admin: dict = Depends(require_admin)):
    """Renvoie l'état complet en base pour une session Thème Natal, incluant :
    - status / payment_status
    - metadata.pdf_ctx (les données de naissance saisies au checkout — SOURCE de vérité)
    - metadata.pdf_generated_at (dernière régénération)
    - metadata.pdf_supabase_url (URL servie, avec cache-buster si récent)
    - kind / user_email
    Permet de vérifier que force=True a bien mis à jour la row et que les
    birth_data utilisées ne sont pas des valeurs de test.
    """
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
    }
