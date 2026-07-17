"""Webhook handler para Fenêtres de Rencontre — gera PDF e envia email."""
import asyncio
import uuid
import logging
from config import get_settings
from services.supabase_client import get_admin_client
from routes.fenetre_rencontre import (
    _calculate_advanced_windows, _generate_and_email_pdf
)
from services.astrology_io_service import transits_today

logger = logging.getLogger(__name__)


async def handle_fenetre_rencontre_webhook(session_id: str):
    """Process fenetre rencontre payment → generate PDF + email in background."""
    try:
        sb = get_admin_client()
        
        # Recuperar transação
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            logger.warning(f'[fenetre_rencontre] Transaction not found: {session_id}')
            return
        
        tx = tx_res.data
        user_email = tx.get('user_email')
        metadata = tx.get('metadata') or {}
        pdf_ctx = metadata.get('pdf_ctx') or {}
        
        if not user_email:
            logger.warning(f'[fenetre_rencontre] No email in transaction: {session_id}')
            return
        
        logger.info(f'[fenetre_rencontre] Payment completed for {user_email}, generating PDF in background...')
        
        # Marca como processado e inicia PDF generation assincronamente
        asyncio.create_task(_generate_and_email_pdf(user_email, pdf_ctx))
        
    except Exception as e:
        logger.exception(f'[fenetre_rencontre] Webhook error: {e}')
