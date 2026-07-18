"""
Route /api/webhook/resend — réceptionne les events Resend et les persiste dans
la table `email_events` pour audit + alerting.

Events supportés (Resend v2) :
  - email.sent
  - email.delivered
  - email.delivery_delayed
  - email.bounced
  - email.complained
  - email.opened
  - email.clicked

Signature : Resend utilise Svix. Trois headers :
  svix-id, svix-timestamp, svix-signature
On vérifie la signature si RESEND_WEBHOOK_SECRET est défini (format 'whsec_...').
Sinon, on accepte (mode dev) mais on log un warning.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import logging
import os

from fastapi import APIRouter, Header, HTTPException, Request

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/webhook', tags=['webhook'])


def _verify_svix_signature(
    body: bytes,
    svix_id: str,
    svix_timestamp: str,
    svix_signature: str,
    secret: str,
) -> bool:
    """Vérifie la signature Svix (format Resend).
    Secret attendu : 'whsec_<base64>'. On calcule HMAC-SHA256 de '{id}.{ts}.{body}'."""
    if not (svix_id and svix_timestamp and svix_signature and secret):
        return False
    try:
        raw_secret = secret[6:] if secret.startswith('whsec_') else secret
        key = base64.b64decode(raw_secret)
        signed = f'{svix_id}.{svix_timestamp}.{body.decode("utf-8")}'.encode()
        expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
        # svix-signature peut contenir plusieurs versions : "v1,xxx v1,yyy"
        for token in svix_signature.split(' '):
            if ',' in token:
                _, sig = token.split(',', 1)
                if hmac.compare_digest(sig, expected):
                    return True
        return False
    except Exception as e:
        logger.warning(f'[resend_webhook] signature verify error: {e}')
        return False


@router.post('/resend')
async def resend_webhook(
    request: Request,
    svix_id: str | None = Header(default=None, alias='svix-id'),
    svix_timestamp: str | None = Header(default=None, alias='svix-timestamp'),
    svix_signature: str | None = Header(default=None, alias='svix-signature'),
):
    body = await request.body()

    # Vérification signature (optionnelle mais recommandée en prod)
    secret = os.environ.get('RESEND_WEBHOOK_SECRET', '').strip()
    if secret:
        if not _verify_svix_signature(body, svix_id or '', svix_timestamp or '', svix_signature or '', secret):
            logger.warning('[resend_webhook] invalid signature — rejected')
            raise HTTPException(401, 'Invalid signature')
    else:
        logger.info('[resend_webhook] RESEND_WEBHOOK_SECRET not set — accepting without verification')

    try:
        payload = json.loads(body.decode('utf-8'))
    except Exception as e:
        logger.warning(f'[resend_webhook] invalid JSON: {e}')
        raise HTTPException(400, 'Invalid JSON')

    event_type = payload.get('type') or 'unknown'
    data = payload.get('data') or {}
    provider_event_id = svix_id or payload.get('id')

    resend_id = data.get('email_id') or data.get('id')
    to_list = data.get('to') or []
    to_email = to_list[0] if to_list else None
    from_email = data.get('from')
    subject = data.get('subject')

    # Extraire l'erreur en cas de bounce/complaint
    error_message = None
    if event_type == 'email.bounced':
        b = data.get('bounce') or {}
        error_message = f"{b.get('subType') or b.get('type') or ''} — {b.get('message') or ''}".strip(' —')
    elif event_type == 'email.complained':
        error_message = 'complained (spam)'
    elif event_type == 'email.delivery_delayed':
        error_message = (data.get('reason') or 'delayed')

    logger.info(f'[resend_webhook] {event_type} → {to_email} ({resend_id})')

    try:
        sb = get_admin_client()
        # Dédoublonnage par provider_event_id (svix-id est unique)
        if provider_event_id:
            existing = sb.table('email_events').select('id').eq('provider_event_id', provider_event_id).limit(1).execute()
            if existing and existing.data:
                return {'ok': True, 'deduped': True}

        sb.table('email_events').insert({
            'source': 'resend',
            'event_type': event_type,
            'resend_id': resend_id,
            'provider_event_id': provider_event_id,
            'to_email': (to_email or '').strip().lower() if to_email else None,
            'from_email': from_email,
            'subject': subject,
            'error_message': error_message,
            'raw': payload,
        }).execute()
    except Exception as e:
        logger.warning(f'[resend_webhook] insert failed: {e}')
        # On répond 200 quand même : Resend re-livre pendant 3 jours en cas de 5xx,
        # mais si notre DB est down, on ne veut pas boucler.

    return {'ok': True}


@router.get('/resend/health')
async def resend_webhook_health():
    """Endpoint de diag pour vérifier que l'URL webhook est bien accessible depuis l'extérieur."""
    return {
        'ok': True,
        'endpoint': '/api/webhook/resend',
        'signature_check': bool(os.environ.get('RESEND_WEBHOOK_SECRET', '').strip()),
    }
