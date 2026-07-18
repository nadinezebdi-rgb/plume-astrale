"""
Journal centralisé des envois email.

Objectif : détecter les emails jamais demandés (bug type aml.numerique30@gmail.com)
et les emails demandés mais rejetés par Resend.

Deux fonctions publiques :
- log_send_attempt(...)      → à appeler AVANT chaque POST /emails Resend
- log_send_response(row_id, http_status, resend_id, body)  → à appeler APRÈS

Best-effort : n'importe quelle erreur d'insertion Supabase est loggée mais
n'interrompt jamais le flow d'envoi.
"""
from __future__ import annotations
import logging
from typing import Any, Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def log_send_attempt(
    to_email: str,
    subject: str,
    product: str,
    from_email: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Optional[str]:
    """Log une tentative d'envoi (statut 'queued'). Retourne l'id de la ligne pour update ultérieur."""
    try:
        sb = get_admin_client()
        res = sb.table('email_events').insert({
            'source': 'app',
            'event_type': 'queued',
            'to_email': (to_email or '').strip().lower(),
            'from_email': from_email,
            'subject': subject,
            'product': product,
            'session_id': session_id,
        }).execute()
        if res and res.data:
            return res.data[0].get('id')
    except Exception as e:
        logger.debug(f'[email_journal] log_send_attempt failed (table missing?): {e}')
    return None


def log_send_response(
    row_id: Optional[str],
    http_status: int,
    resend_id: Optional[str] = None,
    body: Optional[str] = None,
    to_email: Optional[str] = None,
    subject: Optional[str] = None,
    product: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """Met à jour la ligne 'queued' avec le résultat Resend, ou insère une ligne
    'send_failed' si row_id est None (fallback quand le log initial a échoué)."""
    is_ok = 200 <= http_status < 300
    event_type = 'app.sent' if is_ok else 'send_failed'
    error = None if is_ok else (body or '')[:1000]

    try:
        sb = get_admin_client()
        if row_id:
            sb.table('email_events').update({
                'event_type': event_type,
                'resend_id': resend_id,
                'http_status': http_status,
                'error_message': error,
            }).eq('id', row_id).execute()
        else:
            sb.table('email_events').insert({
                'source': 'app',
                'event_type': event_type,
                'resend_id': resend_id,
                'to_email': (to_email or '').strip().lower(),
                'subject': subject,
                'product': product,
                'session_id': session_id,
                'http_status': http_status,
                'error_message': error,
            }).execute()
    except Exception as e:
        logger.debug(f'[email_journal] log_send_response failed (table missing?): {e}')
