"""
Orchestrateur post-paiement pour le pack "duo_completion" (50 EUR).
Bundle Numérologie + Kabbale (économie 8€), utilisé en cross-sell sur la page succès Thème Natal.

Approche : insère 2 payment_transactions enfants et délègue aux handlers existants
(numerologie_webhook + kabbale_service). Mirror du pattern trio_decouverte_service.
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


async def handle_duo_completion_webhook(session_id: str) -> None:
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[duo] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        logger.warning(f"[duo] tx not found for {session_id}")
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'duo_completion':
        return

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    if md.get('duo_dispatched_at'):
        logger.info(f"[duo] déjà dispatché pour {session_id}")
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    if not email or not pdf_ctx:
        logger.error(f"[duo] email ou pdf_ctx manquant pour {session_id}")
        return

    now = datetime.now(timezone.utc).isoformat()
    children_config = [
        ('numerologie', 'numerologie', 'duo-num'),
        ('kabbale_arbre_de_vie', 'kabbale_arbre_de_vie', 'duo-kabbale'),
    ]
    dispatched = []

    for pack_id, kind_key, prefix in children_config:
        child_sid = f'{prefix}-{uuid.uuid4().hex[:16]}'
        try:
            sb.table('payment_transactions').insert({
                'session_id': child_sid,
                'user_email': email,
                'pack_id': pack_id,
                'amount': 0.0,
                'currency': 'eur',
                'credits': 0,
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'kind': kind_key,
                    'product': pack_id,
                    'pdf_ctx': pdf_ctx,
                    'duo_parent_session_id': session_id,
                    'duo_child': True,
                },
            }).execute()
            dispatched.append((kind_key, child_sid))
        except Exception as e:
            logger.error(f"[duo] insert child échoué ({pack_id}): {e}")

    md['duo_children'] = [{'kind': k, 'session_id': s} for k, s in dispatched]
    md['duo_dispatched_at'] = now
    sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()

    for kind_key, child_sid in dispatched:
        if kind_key == 'numerologie':
            from services.numerologie_webhook import handle_numerologie_webhook
            asyncio.create_task(handle_numerologie_webhook(child_sid))
        elif kind_key == 'kabbale_arbre_de_vie':
            from services.kabbale_service import handle_kabbale_webhook
            asyncio.create_task(handle_kabbale_webhook(child_sid))

    logger.info(f"[duo] {len(dispatched)}/2 PDFs dispatchés pour {email} (session {session_id})")


async def get_duo_status(session_id: str) -> dict:
    sb = get_admin_client()
    try:
        parent_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'children': []}
    if not parent_res or not parent_res.data:
        return {'status': 'not_found', 'children': []}
    parent = parent_res.data
    md = parent.get('metadata') or {}
    children_meta = md.get('duo_children') or []
    children_status = []
    for c in children_meta:
        try:
            cres = sb.table('payment_transactions').select('metadata,status').eq('session_id', c['session_id']).maybe_single().execute()
            cmd = ((cres.data or {}).get('metadata') or {}) if cres else {}
            children_status.append({
                'kind': c['kind'],
                'pdf_ready': bool(cmd.get('pdf_path') or cmd.get('pdf_url')),
                'pdf_url': cmd.get('pdf_path') or cmd.get('pdf_url'),
                'email_sent': bool(cmd.get('email_sent_at')),
            })
        except Exception as e:
            logger.warning(f"[duo] status child fail: {e}")
            children_status.append({'kind': c['kind'], 'pdf_ready': False, 'pdf_url': None, 'email_sent': False})

    all_ready = len(children_status) == 2 and all(c['pdf_ready'] for c in children_status)
    return {
        'status': parent.get('status'),
        'payment_status': parent.get('payment_status'),
        'dispatched': bool(md.get('duo_dispatched_at')),
        'all_ready': all_ready,
        'children': children_status,
    }
