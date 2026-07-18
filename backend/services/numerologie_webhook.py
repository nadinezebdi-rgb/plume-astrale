"""Webhook handler para Numérologie — gera PDF e envia email."""
import asyncio
import logging
from config import get_settings
from services.supabase_client import get_admin_client
from routes.numerologie import _generate_and_email_pdf

logger = logging.getLogger(__name__)


async def handle_numerologie_webhook(session_id: str):
    """Process numerologie payment → generate PDF + email in background."""
    try:
        sb = get_admin_client()
        
        # Recuperar transação
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            logger.warning(f'[numerologie] Transaction not found: {session_id}')
            return
        
        tx = tx_res.data
        user_email = tx.get('user_email')
        metadata = tx.get('metadata') or {}
        pdf_ctx = metadata.get('pdf_ctx') or {}
        
        if not user_email:
            logger.warning(f'[numerologie] No email in transaction: {session_id}')
            return
        
        logger.info(f'[numerologie] Payment completed for {user_email}, generating PDF in background...')
        
        # Inicia PDF generation assincronamente
        asyncio.create_task(_generate_and_email_pdf(user_email, pdf_ctx, session_id))
        
    except Exception as e:
        logger.exception(f'[numerologie] Webhook error: {e}')
