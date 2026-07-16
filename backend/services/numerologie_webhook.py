"""Webhook handler para Numérologie — gera PDF e envia email."""
import asyncio
import logging
from services.supabase_client import get_admin_client
from services.numerologie_pdf import generate_numerologie_pdf
from services.email_service import send_pdf_email

logger = logging.getLogger(__name__)


async def handle_numerologie_webhook(session_id: str):
    """Process numerologie payment → generate PDF + email."""
    try:
        sb = get_admin_client()
        
        # Recuperar transação
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            logger.warning(f'[numerologie] Transaction not found: {session_id}')
            return
        
        tx = tx_res.data
        user_email = tx.get('user_email')
        pdf_ctx = tx.get('metadata', {}).get('pdf_ctx') or {}
        
        if not user_email:
            logger.warning(f'[numerologie] No email in transaction: {session_id}')
            return
        
        logger.info(f'[numerologie] Generating PDF for {user_email}...')
        
        # Gerar PDF
        pdf_bytes = await generate_numerologie_pdf(
            first_name=pdf_ctx.get('first_name', ''),
            birth_date_iso=pdf_ctx.get('birth_date_iso', ''),
            birth_data=pdf_ctx.get('birth_data', {}),
        )
        
        # Enviar email
        await send_pdf_email(
            email=user_email,
            pdf_bytes=pdf_bytes,
            filename='Numerologie_Report.pdf',
            subject='Ton Rapport Numérologique - Plume Astrale',
        )
        
        # Upload para storage
        filename = f"numerologie/{session_id}.pdf"
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
        
        logger.info(f'[numerologie] PDF generated and emailed to {user_email}')
        
    except Exception as e:
        logger.exception(f'[numerologie] Webhook error: {e}')
