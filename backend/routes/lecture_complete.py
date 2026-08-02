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


@router.get('/admin/ab-stats')
async def lecture_complete_admin_ab_stats(
    include_ctr: bool = False,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Stats A/B test J+30 : nombre d'envois par variant + CTR reel via Resend API.

    include_ctr=true → aggrege les stats Resend (opens/clicks) par variant (peut prendre 5-10s).
    """
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    try:
        r = sb.table('payment_transactions').select('metadata').eq('pack_id', 'lecture_complete').execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    rows = (r.data or []) if r else []
    stats: Dict[str, Any] = {
        'question': 0, 'invitation': 0, 'total': 0,
        'sample_email_ids': {'question': [], 'invitation': []},
    }
    variant_email_ids: Dict[str, List[str]] = {'question': [], 'invitation': []}
    for row in rows:
        md = row.get('metadata') or {}
        if not md.get('sequence_j30_sent_at'):
            continue
        variant = md.get('sequence_j30_variant') or 'question'
        stats[variant] = stats.get(variant, 0) + 1
        stats['total'] += 1
        eid = md.get('sequence_j30_email_id')
        if eid:
            variant_email_ids[variant].append(eid)
            if len(stats['sample_email_ids'][variant]) < 5:
                stats['sample_email_ids'][variant].append(eid)

    if include_ctr and stats['total'] > 0:
        # Utilise le cache 24h ; si expire, refresh en arriere-plan et renvoie old stale
        try:
            from services.resend_stats import get_cached_ab_ctr, refresh_ab_ctr_cache
            cached = get_cached_ab_ctr()
            if cached:
                stats['ctr'] = cached
            else:
                # Refresh synchrone (peut prendre 5-10s pour la 1ere fois)
                stats['ctr'] = await refresh_ab_ctr_cache()
        except Exception as e:
            logger.warning(f'[ab-stats] CTR aggregation fail: {e}')
            stats['ctr_error'] = str(e)[:200]

    return stats


@router.post('/admin/ctr-refresh')
async def lecture_complete_admin_ctr_refresh(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Force le refresh du cache CTR (utile apres avoir envoye de nouveaux emails)."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    from services.resend_stats import refresh_ab_ctr_cache
    result = await refresh_ab_ctr_cache()
    return {'refreshed': True, 'ctr': result}


@router.get('/admin/orders/export')
async def lecture_complete_admin_export_csv(
    since: Optional[str] = None,
    until: Optional[str] = None,
    payment_status: Optional[str] = None,
    include_bypass: bool = True,
    refunded_only: bool = False,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Export CSV filtre des commandes 97€.

    Query params :
      - since : ISO date (2026-08-01) — inclut les tx crees a partir de cette date
      - until : ISO date — exclut les tx apres cette date
      - payment_status : 'paid' | 'unpaid' | 'initiated' — filtre exact
      - include_bypass : false pour exclure les admin bypass (comptabilite reelle)
      - refunded_only : true pour ne prendre que les remboursees
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv as _csv

    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    try:
        q = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, amount, currency, payment_status, metadata'
        ).eq('pack_id', 'lecture_complete')
        if since:
            q = q.gte('created_at', since)
        if until:
            q = q.lte('created_at', until)
        if payment_status:
            q = q.eq('payment_status', payment_status)
        r = q.order('created_at', desc=True).limit(2000).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    rows = (r.data or []) if r else []
    # Filtres Python (Supabase ne peut pas filtrer sur metadata sans jsonb)
    filtered_rows: List[Dict[str, Any]] = []
    for row in rows:
        md = row.get('metadata') or {}
        if not include_bypass and md.get('admin_bypass'):
            continue
        if refunded_only and not md.get('refunded_at'):
            continue
        filtered_rows.append(row)

    buf = io.StringIO()
    writer = _csv.writer(buf, quoting=_csv.QUOTE_MINIMAL)
    writer.writerow([
        'session_id', 'email', 'created_at', 'amount_eur', 'currency', 'payment_status',
        'admin_bypass', 'bundle_dispatched', 'refunded_at', 'refunded_amount_cents',
        'refund_reason', 'refund_partial', 'stripe_refund_id',
        'first_name', 'birth_date',
        'sequence_j1', 'sequence_j7', 'sequence_j13', 'sequence_j30', 'j30_variant',
    ])
    for row in filtered_rows:
        md = row.get('metadata') or {}
        octx = md.get('order_ctx') or {}
        writer.writerow([
            row.get('session_id') or '',
            row.get('user_email') or '',
            row.get('created_at') or '',
            row.get('amount') if row.get('amount') is not None else '',
            row.get('currency') or '',
            row.get('payment_status') or '',
            'yes' if md.get('admin_bypass') else '',
            'yes' if md.get('bundle_dispatched') else '',
            md.get('refunded_at') or '',
            md.get('refunded_amount_cents') or '',
            (md.get('refund_reason') or '').replace('\n', ' '),
            'yes' if md.get('refund_partial') else '',
            md.get('stripe_refund_id') or '',
            octx.get('first_name') or '',
            octx.get('birth_date') or '',
            'yes' if md.get('sequence_j1_sent_at') else '',
            'yes' if md.get('sequence_j7_sent_at') else '',
            'yes' if md.get('sequence_j13_sent_at') else '',
            'yes' if md.get('sequence_j30_sent_at') else '',
            md.get('sequence_j30_variant') or '',
        ])
    buf.seek(0)
    from datetime import datetime as _dt
    filter_suffix = []
    if since: filter_suffix.append(f'from-{since[:10]}')
    if until: filter_suffix.append(f'to-{until[:10]}')
    if not include_bypass: filter_suffix.append('no-bypass')
    if refunded_only: filter_suffix.append('refunds-only')
    fname_suffix = ('-' + '-'.join(filter_suffix)) if filter_suffix else ''
    fname = f'plume-astrale-lecture-complete-{_dt.now().strftime("%Y%m%d")}{fname_suffix}.csv'
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{fname}"'},
    )


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
            'admin_actions': md.get('admin_actions') or [],
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
    skip_stripe: Optional[bool] = False  # true → seulement marquer refunded, ne pas appeler Stripe
    amount_cents: Optional[int] = None    # None = refund total ; sinon montant partiel en centimes
    suspend_notifications: Optional[bool] = None  # None = auto (true si total refund)


@router.post('/admin/refund/{session_id}')
async def lecture_complete_admin_refund(
    session_id: str,
    payload: RefundRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Rembourse une commande via l'API Stripe + marque la tx.

    Ordre :
      1. Verifie admin
      2. Charge la tx, verifie qu'elle n'est pas deja remboursee (integralement)
      3. Si skip_stripe=false ET session_id commence par 'cs_' : appelle stripe.Refund.create()
         Si amount_cents fourni : refund partiel via param `amount=`
      4. Marque metadata.refunded_at / refund_reason / stripe_refund_id / refund_partial / refunded_amount_cents
      5. Retourne le detail
    """
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    try:
        r = sb.table('payment_transactions').select('metadata, amount').eq(
            'session_id', session_id).maybe_single().execute()
        if not r or not r.data:
            raise HTTPException(status_code=404, detail='Session introuvable.')
        md = r.data.get('metadata') or {}
        # Refund total deja fait → 409. Un refund partiel deja fait n'empeche PAS un refund additionnel.
        if md.get('refunded_at') and not md.get('refund_partial'):
            raise HTTPException(status_code=409, detail='Deja remboursee integralement.')

        # Validation montant partiel
        amount_cents: Optional[int] = payload.amount_cents
        tx_amount_cents = int(round((r.data.get('amount') or 0) * 100))
        already_refunded_cents = int(md.get('refunded_amount_cents') or 0)
        if amount_cents is not None:
            if amount_cents <= 0:
                raise HTTPException(status_code=400, detail='Montant refund doit etre > 0.')
            if amount_cents + already_refunded_cents > tx_amount_cents:
                raise HTTPException(
                    status_code=400,
                    detail=f'Montant depasse le solde restant ({tx_amount_cents - already_refunded_cents} centimes).',
                )

        stripe_refund_id: Optional[str] = None
        stripe_refund_error: Optional[str] = None
        skip = bool(payload.skip_stripe) or session_id.startswith('admin-') or bool(md.get('admin_bypass'))

        if not skip:
            try:
                import stripe as _stripe
                settings = get_settings()
                _stripe.api_key = settings.STRIPE_API_KEY
                sess = _stripe.checkout.Session.retrieve(session_id)
                pi = sess.get('payment_intent') if isinstance(sess, dict) else sess.payment_intent
                if not pi:
                    raise Exception('Aucun payment_intent sur cette session Stripe.')
                refund_kwargs: Dict[str, Any] = {
                    'payment_intent': pi,
                    'reason': 'requested_by_customer',
                    'metadata': {
                        'session_id': session_id,
                        'admin_id': current_user.get('id', ''),
                        'reason_user': (payload.reason or '')[:250],
                    },
                }
                if amount_cents is not None:
                    refund_kwargs['amount'] = int(amount_cents)
                refund = _stripe.Refund.create(**refund_kwargs)
                stripe_refund_id = refund.get('id') if isinstance(refund, dict) else refund.id
            except HTTPException:
                raise
            except Exception as e:
                stripe_refund_error = str(e)[:400]
                logger.error(f'[lecture_complete/refund] Stripe refund failed for {session_id}: {e}')
                raise HTTPException(
                    status_code=502,
                    detail=f'Refund Stripe echoue : {stripe_refund_error}. Aucune donnee modifiee.',
                )

        from datetime import datetime as _dt, timezone as _tz
        md['refunded_at'] = _dt.now(_tz.utc).isoformat()
        if payload.reason:
            md['refund_reason'] = payload.reason[:500]
        md['refunded_by'] = current_user.get('id')
        if stripe_refund_id:
            md['stripe_refund_id'] = stripe_refund_id
        if skip:
            md['refund_stripe_skipped'] = True
        # Gestion du montant refund (partiel vs total)
        if amount_cents is not None and amount_cents < tx_amount_cents - already_refunded_cents:
            md['refund_partial'] = True
            md['refunded_amount_cents'] = already_refunded_cents + amount_cents
        else:
            md['refund_partial'] = False
            md['refunded_amount_cents'] = tx_amount_cents
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()

        # Cascade : suspendre les notifications si refund total (par defaut) ou explicitement demande
        is_total = not md.get('refund_partial')
        suspend = payload.suspend_notifications if payload.suspend_notifications is not None else is_total
        suspended_profile = False
        if suspend:
            # Marque au niveau tx (sequence email + journal guests le respectent)
            md['notifications_suspended'] = True
            md['notifications_suspended_at'] = md['refunded_at']
            # Tente aussi de marquer au niveau profile (registered user)
            try:
                tx2 = sb.table('payment_transactions').select('user_email').eq('session_id', session_id).maybe_single().execute()
                target_email = (tx2.data or {}).get('user_email') if tx2 else None
                if target_email:
                    prof_res = sb.table('profiles').select('id, metadata').ilike('email', target_email).maybe_single().execute()
                    if prof_res and prof_res.data:
                        pmd = prof_res.data.get('metadata') or {}
                        pmd['notifications_suspended_at'] = md['refunded_at']
                        pmd['notifications_suspended_reason'] = 'refund_lecture_complete'
                        sb.table('profiles').update({'metadata': pmd}).eq('id', prof_res.data['id']).execute()
                        suspended_profile = True
            except Exception as _e:
                # colonne metadata absente sur profiles → non-bloquant (cf. migration SQL)
                logger.info(f'[lecture_complete/refund] profile cascade skipped ({_e.__class__.__name__}); tx flag set')
            # Persist tx suspend flag
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()

        # Trace timeline admin
        try:
            from services.lecture_complete_bundle import append_admin_action
            details_txt = (payload.reason or '')[:150]
            if amount_cents is not None:
                details_txt += f' · partiel {amount_cents/100:.2f}€'
            if stripe_refund_id:
                details_txt += f' · stripe={stripe_refund_id}'
            if suspend:
                details_txt += ' · notifications suspendues' + (' (profile)' if suspended_profile else '')
            append_admin_action(
                session_id,
                'refund_stripe' if stripe_refund_id else 'refund',
                admin_id=current_user.get('id'),
                admin_email=current_user.get('email'),
                details=details_txt,
            )
        except Exception as _e:
            logger.warning(f'[lecture_complete/refund] admin_action log failed: {_e}')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        'refunded': True,
        'session_id': session_id,
        'refunded_at': md['refunded_at'],
        'stripe_refund_id': stripe_refund_id,
        'stripe_skipped': skip,
        'partial': bool(md.get('refund_partial')),
        'refunded_amount_cents': md.get('refunded_amount_cents'),
        'notifications_suspended': bool(md.get('notifications_suspended')),
    }


@router.post('/admin/test-slack')
async def lecture_complete_admin_test_slack(
    payload: Dict[str, Any] = None,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Envoie un ping de test vers Slack. Utilise `webhook_url` du body si fourni,
    sinon fallback sur SLACK_WEBHOOK_URL env."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')

    import os as _os
    custom_url = ((payload or {}).get('webhook_url') or '').strip() if isinstance(payload, dict) else ''
    target_url = custom_url or _os.environ.get('SLACK_WEBHOOK_URL', '').strip()
    if not target_url:
        return {'success': False, 'reason': 'Aucun webhook Slack fourni (input vide + SLACK_WEBHOOK_URL absent).'}

    import httpx as _httpx
    try:
        async with _httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(target_url, json={
                'text': f':white_check_mark: *Plume Astrale — Ping de test*\n'
                        f'Webhook OK. Test lance par {current_user.get("email","admin")}.',
            })
            success = r.status_code in (200, 204)
            try:
                from services.app_settings import log_alert
                log_alert(
                    kind='slack_test',
                    title='Ping Slack test' + (' (OK)' if success else f' (FAIL {r.status_code})'),
                    details=f'Lance par {current_user.get("email","admin")} · '
                            + ('URL custom' if custom_url else 'SLACK_WEBHOOK_URL env'),
                    channels=['slack'] if success else [],
                )
            except Exception:
                pass
            if success:
                return {'success': True, 'reason': 'Ping envoye (' + ('custom URL' if custom_url else '.env') + ')'}
            return {'success': False, 'reason': f'Slack a renvoye {r.status_code}: {r.text[:200]}'}
    except Exception as e:
        return {'success': False, 'reason': f'Erreur reseau: {e}'}


@router.get('/admin/settings')
async def lecture_complete_admin_settings_get(
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Retourne les app settings (forced_j30_variant, historique alertes)."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    from services.app_settings import get_setting, get_alerts_history
    return {
        'forced_j30_variant': get_setting('forced_j30_variant'),
        'alerts_history': get_alerts_history(),
    }


@router.post('/admin/set-forced-variant')
async def lecture_complete_admin_set_forced_variant(
    payload: Dict[str, Any],
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Force 100% sur une variante A/B J+30 (ou reset avec variant=null)."""
    if not current_user or not current_user.get('id'):
        raise HTTPException(status_code=401, detail='Authentification requise.')
    sb = get_admin_client()
    prof = sb.table('profiles').select('is_admin').eq('id', current_user['id']).maybe_single().execute()
    if not prof or not prof.data or not prof.data.get('is_admin'):
        raise HTTPException(status_code=403, detail='Reserve aux administrateurs.')
    variant = (payload or {}).get('variant')
    if variant not in (None, 'question', 'invitation'):
        raise HTTPException(status_code=400, detail='variant doit etre null, "question" ou "invitation".')
    from services.app_settings import set_setting
    set_setting('forced_j30_variant', variant)
    # Trace audit
    try:
        from services.app_settings import log_alert
        log_alert(
            kind='ab_override',
            title=f'A/B J+30 forcé sur {variant}' if variant else 'A/B J+30 réinitialisé (50/50)',
            details=f'Par {current_user.get("email","admin")}',
            channels=[],
        )
    except Exception:
        pass
    return {'forced_j30_variant': variant}


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
    from services.lecture_complete_bundle import handle_lecture_complete_webhook, append_admin_action
    try:
        append_admin_action(
            session_id, 'redispatch',
            admin_id=current_user.get('id'),
            admin_email=current_user.get('email'),
            details='Re-generation des 5 PDFs bundles',
        )
    except Exception as _e:
        logger.warning(f'[lecture_complete/redispatch] admin_action log failed: {_e}')
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
