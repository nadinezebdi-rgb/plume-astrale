"""
Orchestrateur post-paiement pour le pack "trio_decouverte" (79 EUR).
Génère les 3 PDFs (Thème Natal + Numérologie + Kabbale) en parallèle et envoie 3 emails.

Approche : insère 3 payment_transactions enfants et délègue aux handlers existants.
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


async def handle_trio_decouverte_webhook(session_id: str) -> None:
    """Traite le paiement Trio : marque completed + lance 3 handlers PDFs en parallèle."""
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[trio] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        logger.warning(f"[trio] tx not found for {session_id}")
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'trio_decouverte':
        return

    # Marque parent completed
    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence : ne relance pas si déjà dispatché
    if md.get('trio_dispatched_at'):
        logger.info(f"[trio] déjà dispatché pour {session_id}")
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    if not email or not pdf_ctx:
        logger.error(f"[trio] email ou pdf_ctx manquant pour {session_id}")
        return

    # Crée 3 sessions enfants et dispatche aux handlers existants
    now = datetime.now(timezone.utc).isoformat()
    children_config = [
        ('theme_natal_pdf_oneshot', 'theme_natal', 'trio-natal'),
        ('numerologie', 'numerologie', 'trio-numerologie'),
        ('kabbale_arbre_de_vie', 'kabbale_arbre_de_vie', 'trio-kabbale'),
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
                    'trio_parent_session_id': session_id,
                    'trio_child': True,
                },
            }).execute()
            dispatched.append((kind_key, child_sid))
        except Exception as e:
            logger.error(f"[trio] insert child échoué ({pack_id}): {e}")

    # Marque le parent avec les 3 enfants dispatchés
    md['trio_children'] = [{'kind': k, 'session_id': s} for k, s in dispatched]
    md['trio_dispatched_at'] = now
    sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()

    # Lance les 3 handlers en background (parallèle)
    for kind_key, child_sid in dispatched:
        if kind_key == 'theme_natal':
            from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
            asyncio.create_task(handle_theme_natal_oneshot_webhook(child_sid))
        elif kind_key == 'numerologie':
            from services.numerologie_webhook import handle_numerologie_webhook
            asyncio.create_task(handle_numerologie_webhook(child_sid))
        elif kind_key == 'kabbale_arbre_de_vie':
            from services.kabbale_service import handle_kabbale_webhook
            asyncio.create_task(handle_kabbale_webhook(child_sid))

    logger.info(f"[trio] {len(dispatched)}/3 PDFs dispatchés pour {email} (session {session_id})")


async def get_trio_status(session_id: str) -> dict:
    """Renvoie le statut consolidé du Trio (3 PDFs)."""
    sb = get_admin_client()
    try:
        parent_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        return {'status': 'error', 'error': str(e), 'children': []}
    if not parent_res or not parent_res.data:
        return {'status': 'not_found', 'children': []}
    parent = parent_res.data
    md = parent.get('metadata') or {}
    children_meta = md.get('trio_children') or []
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
            logger.warning(f"[trio] status child fail: {e}")
            children_status.append({'kind': c['kind'], 'pdf_ready': False, 'pdf_url': None, 'email_sent': False})

    all_ready = len(children_status) == 3 and all(c['pdf_ready'] for c in children_status)
    return {
        'status': parent.get('status'),
        'payment_status': parent.get('payment_status'),
        'dispatched': bool(md.get('trio_dispatched_at')),
        'all_ready': all_ready,
        'children': children_status,
    }
