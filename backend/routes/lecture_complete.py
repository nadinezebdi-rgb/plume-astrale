"""
Route /api/lecture-complete : Landing v2 — bundle 97€ (Lecture Complète du Ciel).
Regroupe Theme Natal + Fenetres 2026 + Karma + Analyse des Liens + Cercle Solena 90j.

Livraison des bonus manuelle par Solena apres commande.

Endpoints :
  POST /api/lecture-complete/checkout   → session Stripe (97 EUR) + promo bypass admin
  GET  /api/lecture-complete/status     → polling paiement
"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from services.promo_bypass import try_consume_promo
from middleware.auth import get_optional_user
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/lecture-complete', tags=['lecture-complete'])


class LectureCompletePayload(BaseModel):
    email: str
    first_name: Optional[str] = ''
    birth_date: Optional[str] = ''
    birth_time: Optional[str] = ''
    birth_city: Optional[str] = ''
    birth_country: Optional[str] = 'FR'
    origin_url: str
    promo_code: Optional[str] = None


@router.post('/checkout')
async def lecture_complete_checkout(
    payload: LectureCompletePayload,
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Cree une session Stripe pour le bundle Lecture Complete 97€."""
    settings = get_settings()
    pack = settings.PACKS.get('lecture_complete')
    if not pack:
        raise HTTPException(500, 'Produit indisponible.')

    if not payload.email or '@' not in payload.email:
        raise HTTPException(400, 'Email invalide.')

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/lecture-complete/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/'

    order_ctx = {
        'first_name': (payload.first_name or '').strip(),
        'birth_date': payload.birth_date,
        'birth_time': payload.birth_time,
        'birth_city': payload.birth_city,
        'birth_country': payload.birth_country,
        'email': payload.email,
    }

    # Bypass promo admin (SEC-004 : seul un compte is_admin=true peut consommer)
    if payload.promo_code and try_consume_promo(
        payload.promo_code, admin_user=current_user, product='lecture_complete'
    ):
        fake_session_id = f'admin-lecture-{uuid.uuid4().hex[:16]}'
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email,
                'pack_id': 'lecture_complete',
                'amount': 0.0,
                'currency': pack['currency'],
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'product': 'lecture_complete',
                    'kind': 'lecture_complete',
                    'order_ctx': order_ctx,
                    'admin_bypass': True,
                    'promo_code': payload.promo_code.strip().upper(),
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[lecture_complete] admin bypass tx insert failed: {e}')

        # Declenche l'orchestration bundle en arriere-plan
        import asyncio
        from services.lecture_complete_bundle import handle_lecture_complete_webhook
        asyncio.create_task(handle_lecture_complete_webhook(fake_session_id))

        return {
            'url': f'{origin}/lecture-complete/succes?session_id={fake_session_id}',
            'session_id': fake_session_id,
            'admin_bypass': True,
        }

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'lecture_complete',
            'kind': 'lecture_complete',
            'email': payload.email,
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email,
            'pack_id': 'lecture_complete',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'lecture_complete',
                'kind': 'lecture_complete',
                'order_ctx': order_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@router.get('/status')
async def lecture_complete_status(session_id: str):
    """Polling live pour /lecture-complete/succes."""
    if not session_id:
        raise HTTPException(400, 'session_id requis.')
    try:
        sb = get_admin_client()
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] status fetch failed: {e}')
        raise HTTPException(500, 'Impossible de recuperer le statut.')
    if not tx_res or not tx_res.data:
        raise HTTPException(404, 'Session introuvable.')
    tx = tx_res.data
    md = tx.get('metadata') or {}
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'email': tx.get('user_email'),
        'admin_bypass': bool(md.get('admin_bypass')),
        'bundle_dispatched': bool(md.get('bundle_dispatched')),
        'bundle_children': md.get('bundle_children') or {},
    }


@router.get('/scarcity')
async def lecture_complete_scarcity():
    """Compteur honnete des lectures restantes ce cycle (mois calendaire).

    Utilise par le bandeau homepage : 'Il reste X lectures completes pour ce cycle lunaire'.
    Cache TTL 60s cote service.
    """
    from services.lecture_complete_bundle import get_scarcity_status
    return get_scarcity_status()


@router.get('/admin/orders')
async def lecture_complete_admin_orders(current_user: Optional[dict] = Depends(get_optional_user)):
    """Panneau admin : liste toutes les commandes 97€ avec l'etat des 5 PDFs enfants.

    Reserve aux admins (is_admin=true). Non-admin -> 403.
    """
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    try:
        prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
        if not prof or not prof.data or not prof.data.get('is_admin'):
            raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f'[lecture_complete/admin] admin check fail: {e}')
        raise HTTPException(status_code=500, detail='Impossible de verifier vos droits.')

    # Charge les commandes parentes
    try:
        r = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, amount, payment_status, metadata'
        ).eq('pack_id', 'lecture_complete').order('created_at', desc=True).limit(100).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Fetch parents: {e}')
    parents = (r.data or []) if r else []
    if not parents:
        return {'orders': []}

    parent_sids = [p['session_id'] for p in parents]
    # BATCH FETCH: une seule requete pour tous les enfants (via metadata->>parent_bundle IN parents)
    # Utilise le fait que tous les enfants ont metadata.lecture_complete_bundle = True et
    # metadata.parent_bundle = <parent session_id>.
    children_by_parent: Dict[str, List[Dict[str, Any]]] = {sid: [] for sid in parent_sids}
    try:
        # Filtre JSONB : metadata->>parent_bundle IN (parent_sids)
        rr = sb.table('payment_transactions').select(
            'session_id, pack_id, metadata, created_at'
        ).in_('metadata->>parent_bundle', parent_sids).execute()
        for row in (rr.data or []):
            cmd = row.get('metadata') or {}
            parent = cmd.get('parent_bundle')
            if parent in children_by_parent:
                children_by_parent[parent].append(row)
    except Exception as e:
        logger.warning(f'[lecture_complete/admin] batch children fetch fail: {e}')
        # Fallback : boucle avec .like (N+1) si le filtre JSONB echoue
        try:
            for sid in parent_sids:
                rr = sb.table('payment_transactions').select(
                    'session_id, pack_id, metadata, created_at'
                ).like('session_id', f'{sid}--%').execute()
                for row in (rr.data or []):
                    children_by_parent[sid].append(row)
        except Exception as ee:
            logger.warning(f'[lecture_complete/admin] fallback children fetch fail: {ee}')

    orders = []
    total_paid = 0
    total_refunded = 0
    for p in parents:
        sid = p['session_id']
        md = p.get('metadata') or {}
        seq_status = {
            'j1': bool(md.get('sequence_j1_sent_at')),
            'j7': bool(md.get('sequence_j7_sent_at')),
            'j13': bool(md.get('sequence_j13_sent_at')),
            'j30': bool(md.get('sequence_j30_sent_at')),
        }
        refunded_at = md.get('refunded_at')
        is_bypass = bool(md.get('admin_bypass'))
        if p.get('payment_status') == 'paid' and not is_bypass:
            total_paid += 1
            if refunded_at:
                total_refunded += 1
        children_summary = []
        for c in children_by_parent.get(sid, []):
            cmd = c.get('metadata') or {}
            children_summary.append({
                'session_id': c['session_id'],
                'kind': cmd.get('kind') or c.get('pack_id'),
                'pdf_status': cmd.get('pdf_status') or ('success' if cmd.get('pdf_path') else 'pending'),
                'pdf_ready': bool(cmd.get('pdf_path')),
                'email_sent': bool(cmd.get('email_sent_at')),
                'pdf_error': cmd.get('pdf_error'),
            })
        orders.append({
            'session_id': sid,
            'email': p.get('user_email'),
            'created_at': p.get('created_at'),
            'amount': p.get('amount'),
            'payment_status': p.get('payment_status'),
            'admin_bypass': is_bypass,
            'bundle_dispatched': bool(md.get('bundle_dispatched')),
            'bundle_error': md.get('bundle_error'),
            'refunded_at': refunded_at,
            'refund_reason': md.get('refund_reason'),
            'sequence': seq_status,
            'children': children_summary,
        })

    refund_rate_pct = round((total_refunded / total_paid * 100), 1) if total_paid else 0.0
    return {
        'orders': orders,
        'stats': {
            'total_paid': total_paid,
            'total_refunded': total_refunded,
            'refund_rate_pct': refund_rate_pct,
        },
    }


class RefundRequest(BaseModel):
    reason: Optional[str] = None


@router.post('/admin/refund/{session_id}')
async def lecture_complete_admin_refund(
    session_id: str,
    payload: RefundRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Marque une commande comme remboursee.

    Attention : n'effectue PAS le remboursement Stripe automatiquement — l'admin doit
    lancer le refund manuellement dans le dashboard Stripe. Cette API sert uniquement
    a tracker le statut cote base + arreter la sequence email et le journal.
    """
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    try:
        r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
        if not r or not r.data:
            raise HTTPException(status_code=404, detail='Session introuvable.')
        md = r.data.get('metadata') or {}
        from datetime import datetime as _dt, timezone as _tz
        md['refunded_at'] = _dt.now(_tz.utc).isoformat()
        if payload.reason:
            md['refund_reason'] = payload.reason[:500]
        md['refunded_by'] = current_user.get('id')
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {'refunded': True, 'session_id': session_id, 'refunded_at': md['refunded_at']}


@router.post('/admin/redispatch/{session_id}')
async def lecture_complete_admin_redispatch(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Force la re-generation d'un bundle (utile si un enfant a echoue)."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    # Reset le flag bundle_dispatched pour permettre le re-dispatch
    try:
        r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
        if not r or not r.data:
            raise HTTPException(status_code=404, detail='Session introuvable.')
        md = r.data.get('metadata') or {}
        md['bundle_dispatched'] = False
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    import asyncio
    from services.lecture_complete_bundle import handle_lecture_complete_webhook
    asyncio.create_task(handle_lecture_complete_webhook(session_id))
    return {'redispatched': True, 'session_id': session_id}


@router.get('/cercle-status')
async def lecture_complete_cercle_status(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Indique si l'utilisateur courant a un Cercle Solena 90j actif via un bundle 97€.

    Retourne {active, days_remaining, expires_at, purchased_at, source} ou {active:false}.
    """
    if not current_user or not current_user.get('id'):
        return {'active': False, 'reason': 'not_authenticated'}
    email = (current_user.get('email') or '').lower()
    if not email:
        return {'active': False, 'reason': 'no_email'}

    sb = get_admin_client()
    try:
        r = sb.table('payment_transactions').select(
            'session_id, created_at, payment_status, metadata'
        ).eq('pack_id', 'lecture_complete').eq('payment_status', 'paid').ilike(
            'user_email', email
        ).order('created_at', desc=True).limit(1).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete/cercle-status] fetch fail: {e}')
        return {'active': False, 'reason': 'db_error'}

    rows = (r.data or []) if r else []
    if not rows:
        return {'active': False}

    tx = rows[0]
    md = tx.get('metadata') or {}
    if md.get('refunded_at'):
        return {'active': False, 'refunded': True, 'refunded_at': md['refunded_at']}
    from datetime import datetime, timedelta, timezone
    try:
        created_dt = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00'))
    except Exception:
        return {'active': False, 'reason': 'bad_created_at'}
    expires_at = created_dt + timedelta(days=90)
    now = datetime.now(timezone.utc)
    if now >= expires_at:
        return {
            'active': False,
            'expired': True,
            'purchased_at': created_dt.isoformat(),
            'expires_at': expires_at.isoformat(),
        }
    days_remaining = max(0, (expires_at - now).days)
    return {
        'active': True,
        'days_remaining': days_remaining,
        'expires_at': expires_at.isoformat(),
        'purchased_at': created_dt.isoformat(),
        'source': 'lecture_complete',
    }
