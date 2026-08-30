"""
Alerte admin email — envoie un mail à Soléna en cas de webhook Stripe cassé.

Rate-limité à 1 email / heure (persisté in-memory) pour éviter le spam si le
webhook boucle en 503.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Rate limit persisté en mémoire (reset au restart du pod, acceptable)
_last_alert_at: dict = {}
_MIN_INTERVAL = timedelta(hours=1)


async def send_webhook_alert(reason: str, details: str = '', *, dedup_key: Optional[str] = None) -> bool:
    """Envoie une alerte email à l'admin. Retourne True si envoyé.

    - `reason` : 'webhook_secret_missing' | 'signature_invalid' | 'handler_error' | …
    - `details` : contexte technique (event type, session id, exception…)
    - Rate-limit : 1 email / heure par `dedup_key` (défaut = `reason`)
    """
    dedup_key = dedup_key or reason
    now = datetime.now(timezone.utc)
    last = _last_alert_at.get(dedup_key)
    if last and (now - last) < _MIN_INTERVAL:
        logger.info(f'[webhook_alert] rate-limited (last sent {(now - last).total_seconds():.0f}s ago)')
        return False

    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not resend_key:
        logger.warning('[webhook_alert] RESEND_API_KEY absent, alerte non envoyée')
        return False

    admin_email = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>')

    subject = f'[URGENT] Webhook Stripe cassé — {reason}'
    html = f"""
    <div style="font-family: system-ui, sans-serif; max-width:600px; margin:0 auto; padding:24px; color:#111;">
      <h2 style="color:#c0392b;">🚨 Alerte Webhook Stripe</h2>
      <p><strong>Motif :</strong> {reason}</p>
      <p><strong>Horodatage :</strong> {now.isoformat()}</p>
      <p><strong>Détails :</strong></p>
      <pre style="background:#f5f5f5;padding:12px;border-radius:6px;overflow:auto;">{details or 'n/a'}</pre>
      <hr/>
      <p><strong>Impact business :</strong> tant que le webhook Stripe échoue, les paiements clients
      ne déclenchent PAS la génération et l'envoi des PDFs. Les clients paient mais ne reçoivent rien.</p>
      <p><strong>Action requise :</strong></p>
      <ul>
        <li>Vérifiez la configuration <code>STRIPE_WEBHOOK_SECRET</code> dans <code>backend/.env</code></li>
        <li>Vérifiez le dashboard Stripe → Developers → Webhooks (mode LIVE)</li>
        <li>Consultez <code>/admin/payments-health</code> pour voir les sessions bloquées</li>
      </ul>
      <p style="color:#888;font-size:12px;">Prochaine alerte possible dans 1 heure minimum (rate-limit).</p>
    </div>
    """

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={
                    'from': sender,
                    'to': [admin_email],
                    'subject': subject,
                    'html': html,
                },
            )
        if r.status_code >= 300:
            logger.warning(f'[webhook_alert] Resend {r.status_code}: {r.text[:200]}')
            return False
        _last_alert_at[dedup_key] = now
        logger.info(f'[webhook_alert] envoyée à {admin_email} (reason={reason})')
        return True
    except Exception as e:
        logger.warning(f'[webhook_alert] envoi fail: {e}')
        return False
