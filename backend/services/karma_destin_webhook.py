"""Webhook handler para Karma Destin — gera PDF e envia email."""
import asyncio
import logging
from services.supabase_client import get_admin_client
from services.karma_destin_pdf import generate_karma_destin_pdf
from services.email_service import send_pdf_email

logger = logging.getLogger(__name__)


async def handle_karma_destin_webhook(session_id: str):
    """Process karma destin payment → generate PDF + email."""
    try:
        sb = get_admin_client()
        
        # Recuperar transação
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            logger.warning(f'[karma_destin] Transaction not found: {session_id}')
            return
        
        tx = tx_res.data
        user_email = tx.get('user_email')
        pdf_ctx = tx.get('metadata', {}).get('pdf_ctx') or {}
        
        if not user_email:
            logger.warning(f'[karma_destin] No email in transaction: {session_id}')
            return
        
        logger.info(f'[karma_destin] Generating PDF for {user_email}...')
        
        # Gerar PDF
        pdf_bytes = await generate_karma_destin_pdf(
            first_name=pdf_ctx.get('first_name', ''),
            birth_date_iso=pdf_ctx.get('birth_date_iso', ''),
            birth_data=pdf_ctx.get('birth_data', {}),
        )
        
        # Enviar email
        await send_pdf_email(
            email=user_email,
            pdf_bytes=pdf_bytes,
            filename='Karma_Destin_Report.pdf',
            subject='Analyse Karmique & Destinée - Plume Astrale',
        )
        
        # Upload para storage
        filename = f"karma_destin/{session_id}.pdf"
        sb.storage.from_('reports').upload(filename, pdf_bytes, {'content-type': 'application/pdf'})
        
        # Atualizar transaction
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'metadata': {
                **tx.get('metadata', {}),
                'pdf_url': f"https://{sb.storage.url_parts(filename)['bucket']}.supabase.co/storage/v1/object/public/{filename}"
            }
        }).eq('session_id', session_id).execute()
        
        logger.info(f'[karma_destin] PDF generated and emailed to {user_email}')
        
    except Exception as e:
        logger.exception(f'[karma_destin] Webhook error: {e}')
