"""Webhook handler para Karma Destin — gera PDF e envia email."""
import asyncio
import logging
from config import get_settings
from services.supabase_client import get_admin_client
from routes.karma_destin import _generate_and_email_pdf

logger = logging.getLogger(__name__)


async def handle_karma_destin_webhook(session_id: str):
    """Process karma destin payment → generate PDF + email in background."""
    try:
        sb = get_admin_client()
        
        # Recuperar transação
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            logger.warning(f'[karma_destin] Transaction not found: {session_id}')
            return
        
        tx = tx_res.data
        user_email = tx.get('user_email')
        metadata = tx.get('metadata') or {}
        pdf_ctx = metadata.get('pdf_ctx') or {}
        
        if not user_email:
            logger.warning(f'[karma_destin] No email in transaction: {session_id}')
            return
        
        logger.info(f'[karma_destin] Payment completed for {user_email}, generating PDF in background...')
        
        # Inicia PDF generation assincronamente
        asyncio.create_task(_generate_and_email_pdf(user_email, pdf_ctx))
        
    except Exception as e:
        logger.exception(f'[karma_destin] Webhook error: {e}')
