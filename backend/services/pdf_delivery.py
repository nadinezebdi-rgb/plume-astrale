"""
Helper partage pour finaliser la livraison d'un PDF one-shot :
- merge des metadata sur la transaction (par session_id, fallback email)
- envoi email via l'API HTTP Resend (SENDER_EMAIL env, domaine verifie)
Utilise par routes/numerologie.py, karma_destin.py, fenetre_rencontre.py.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
import httpx

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def update_tx_pdf_metadata(session_id: str, email: str, pdf_url: str, log_tag: str) -> None:
    """Merge {pdf_path, email_sent_at} dans metadata SANS ecraser le reste."""
    try:
        sb = get_admin_client()
        md = {}
        row = None
        if session_id:
            r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
            row = r.data if r else None
        if row:
            md = row.get('metadata') or {}
        md.update({
            'pdf_path': pdf_url,
            'email_sent_at': datetime.now(timezone.utc).isoformat(),
        })
        upd = sb.table('payment_transactions').update({'metadata': md})
        if session_id:
            upd = upd.eq('session_id', session_id)
        else:
            upd = upd.eq('user_email', email)
        upd.execute()
    except Exception as e:
        logger.warning(f'[{log_tag}] tx metadata update failed: {e}')


async def send_pdf_email(email: str, subject: str, html: str, log_tag: str) -> None:
    """Envoie l'email de livraison via Resend (best-effort)."""
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    if not resend_key or not email:
        logger.warning(f'[{log_tag}] RESEND_API_KEY ou email manquant — email non envoye')
        return
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [email], 'subject': subject, 'html': html},
            )
            if r.status_code >= 400:
                logger.warning(f'[{log_tag}] Resend error {r.status_code}: {r.text[:200]}')
            else:
                logger.info(f'[{log_tag}] Email envoye a {email}')
    except Exception as e:
        logger.warning(f'[{log_tag}] email failed: {e}')
