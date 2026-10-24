"""Admin — core : require_admin + /stats + /chat-sessions.

Refactor 2026-02 : ce fichier contenait précédemment 1174 lignes. Les routes
ont été éclatées dans :
  - routes/admin_users.py          : users (list, credits, premium, delete, grant)
  - routes/admin_promo.py          : promo-codes CRUD
  - routes/admin_pdfs.py           : payments/transactions/leads/pdfs-sent/
                                     theme-natal (search/regenerate/inspect/patch)
                                     + cron journal + regenerate-horoscopes
  - routes/admin_viralite.py       : tarot-share/top (viralité)
  - routes/admin_illustrations.py  : audit Ex Libris Nano Banana
  - routes/admin_monitoring.py     : cache SVG, PDF failures, alerts, A/B stats

Tous les sous-routers sont montés sur le préfixe `/admin` → les URLs publiques
restent identiques.
"""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from middleware.auth import get_current_user
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/admin', tags=['admin'])


# ═══════════════════════════════════════════════════════════════
# Exclusion des emails internes / tests des compteurs revenus.
# 2026-02-26 — L'audit a révélé que le dashboard mélangeait sessions
# de test (admin, TEST_*, @example.com, contact@, t@test.fr) avec les
# vrais paiements clients → 165€ affichés = 0€ réels.
# ═══════════════════════════════════════════════════════════════
_INTERNAL_EMAIL_ALLOWLIST_EXACT = {
    'admin@plume-astrale.fr',
    'contact@plume-astrale.fr',
    'test@plume-astrale.fr',
    'test@plume.fr',
    't@test.fr',
    'test2.stripe@example.com',
    'guest@example.com',
    # Comptes proches/famille — dépenses hors périmètre commercial
    'nadine.zebdi@gmail.com',
    'aml.numerique30@gmail.com',
}

_INTERNAL_EMAIL_PATTERNS = (
    'test-',
    'test_',
    '_test',
    '+test',
    '@example.com',
    '@example.org',
    '@example.fr',
    '@plume-astrale.fr',
)


def _is_internal_email(email) -> bool:
    """True si l'email est un compte interne/test à exclure des compteurs revenus."""
    if not email:
        return True
    e = str(email).strip().lower()
    if e in _INTERNAL_EMAIL_ALLOWLIST_EXACT:
        return True
    return any(p in e for p in _INTERNAL_EMAIL_PATTERNS)


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency : vérifie que l'utilisateur est admin."""
    sb = get_admin_client()
    r = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not r or not r.data or not r.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Acces admin requis')
    return current_user


# ═══════════════════════════════════════════════════════════════
# /admin/stats — KPIs dashboard
# ═══════════════════════════════════════════════════════════════
def _stats_user_counters(sb, now: datetime) -> dict:
    today_iso = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()
    total = sb.table('profiles').select('id', count='exact').execute().count or 0
    today = sb.table('profiles').select('id', count='exact').gte('created_at', today_iso + 'T00:00:00').execute().count or 0
    d7 = sb.table('profiles').select('id', count='exact').gte('created_at', week_ago).execute().count or 0
    d30 = sb.table('profiles').select('id', count='exact').gte('created_at', month_ago).execute().count or 0
    return {'total': total, 'today': today, 'd7': d7, 'd30': d30}


def _stats_revenue_counters(sb, now: datetime) -> dict:
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()
    raw_paid = sb.table('payment_transactions').select('*').in_(
        'payment_status', ['paid', 'completed'],
    ).execute().data or []
    paid = [t for t in raw_paid if not _is_internal_email(t.get('user_email'))]
    total_rev = sum(float(t.get('amount') or 0) for t in paid)
    rev_7d = sum(float(t.get('amount') or 0) for t in paid if t.get('created_at', '') >= week_ago)
    rev_30d = sum(float(t.get('amount') or 0) for t in paid if t.get('created_at', '') >= month_ago)
    paying_users = len({t['user_id'] for t in paid if t.get('user_id')})
    raw_pending = sb.table('payment_transactions').select('user_email').in_(
        'payment_status', ['unpaid', 'pending'],
    ).execute().data or []
    pending = sum(1 for t in raw_pending if not _is_internal_email(t.get('user_email')))
    return {
        'total_eur': round(total_rev, 2),
        'last_7d_eur': round(rev_7d, 2),
        'last_30d_eur': round(rev_30d, 2),
        'total_paid_count': len(paid),
        'pending_count': pending,
        'internal_txs_excluded': len(raw_paid) - len(paid),
        'paying_users': paying_users,
    }


def _stats_engagement_counters(sb) -> dict:
    wallets = sb.table('wallets').select('credit_balance').execute().data or []
    credits = sum(int(w['credit_balance']) for w in wallets)
    chat = sb.table('plume_chat_messages').select('id', count='exact').eq('role', 'user').execute().count or 0
    promo = sb.table('promo_code_redemptions').select('id', count='exact').execute().count or 0
    return {
        'credits_in_wallets': credits,
        'chat_messages_sent': chat,
        'promo_redemptions': promo,
    }


@router.get('/stats')
async def admin_stats(_admin: dict = Depends(require_admin)):
    """KPIs principaux du dashboard.

    2026-02-26 — Compteurs assainis :
    - Revenus : uniquement `payment_status IN ('paid','completed')`.
    - Exclusion des emails internes/test.
    - Expose `internal_txs_excluded` pour transparence.
    """
    sb = get_admin_client()
    now = datetime.now(timezone.utc)

    u = _stats_user_counters(sb, now)
    r = _stats_revenue_counters(sb, now)
    e = _stats_engagement_counters(sb)

    conversion = round((r['paying_users'] / u['total'] * 100), 2) if u['total'] else 0.0

    return {
        'users': {
            'total': u['total'],
            'signups_today': u['today'],
            'signups_7d': u['d7'],
            'signups_30d': u['d30'],
            'paying_users': r['paying_users'],
            'conversion_rate_pct': conversion,
        },
        'revenue': {
            'total_eur': r['total_eur'],
            'last_7d_eur': r['last_7d_eur'],
            'last_30d_eur': r['last_30d_eur'],
            'total_paid_count': r['total_paid_count'],
            'pending_count': r['pending_count'],
            'internal_txs_excluded': r['internal_txs_excluded'],
        },
        'engagement': e,
        'updated_at': now.isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# /admin/chat-sessions — Sessions chat agrégées
# ═══════════════════════════════════════════════════════════════
@router.get('/chat-sessions')
async def admin_chat_sessions(
    _admin: dict = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Liste des sessions de chat avec compteur de messages."""
    sb = get_admin_client()
    res = sb.table('plume_chat_messages').select('*').order('created_at', desc=True).limit(page_size * 2).execute()
    msgs = res.data or []

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
