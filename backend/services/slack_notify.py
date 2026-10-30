"""slack_notify — Notification Slack via Incoming Webhook (optionnel).

Envoie un message JSON à ``SLACK_WEBHOOK_URL`` si la variable d'environnement
est configurée. Fail-silent : si la webhook est absente, mal configurée ou
inaccessible, on log en INFO/WARNING et on retourne False sans jamais
lever d'exception vers l'appelant.

Format `blocks` Slack Block Kit (plus riche que le simple `text`).
Rate-limit implicite : géré par le caller via dédup (ex. ``_alerted`` dans
stuck_sessions_alert).

Usage :
    from services.slack_notify import send_slack_alert
    await send_slack_alert(
        title='⚠️ 3 sessions Stripe bloquées >1h',
        summary='Vérifier /admin/payments-health',
        fields=[('Session', 'cs_live_abc…'), ('Montant', '24 €')],
        url='https://plume-astrale.fr/admin/payments-health',
    )
"""
from __future__ import annotations

import json
import logging
import os
from typing import Iterable, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

_TIMEOUT_S = float(os.environ.get('SLACK_HTTP_TIMEOUT_S', '5.0'))


def _webhook_url() -> str:
    return (os.environ.get('SLACK_WEBHOOK_URL') or '').strip()


def is_configured() -> bool:
    return bool(_webhook_url())


async def send_slack_alert(
    *,
    title: str,
    summary: str = '',
    fields: Optional[Iterable[Tuple[str, str]]] = None,
    url: Optional[str] = None,
    url_label: str = 'Ouvrir le dashboard',
    channel: Optional[str] = None,
    emoji: str = ':warning:',
) -> bool:
    """Envoie une alerte Slack. Retourne True si HTTP 2xx, False sinon."""
    webhook = _webhook_url()
    if not webhook:
        logger.info('[slack_notify] SLACK_WEBHOOK_URL absent, skip.')
        return False

    blocks: List[dict] = [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': f'{emoji} {title}'[:150], 'emoji': True},
        }
    ]
    if summary:
        blocks.append({
            'type': 'section',
            'text': {'type': 'mrkdwn', 'text': summary[:2800]},
        })
    if fields:
        kv: List[dict] = []
        for key, val in list(fields)[:10]:
            kv.append({'type': 'mrkdwn', 'text': f'*{key}*\n{val}'[:2000]})
        if kv:
            blocks.append({'type': 'section', 'fields': kv})
    if url:
        blocks.append({
            'type': 'actions',
            'elements': [{
                'type': 'button',
                'text': {'type': 'plain_text', 'text': url_label[:70]},
                'url': url,
            }],
        })

    payload: dict = {'blocks': blocks, 'text': title}
    if channel:
        payload['channel'] = channel

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
            r = await client.post(webhook, json=payload)
        if 200 <= r.status_code < 300:
            logger.info(f'[slack_notify] alert sent (status={r.status_code})')
            return True
        logger.warning(
            f'[slack_notify] non-2xx status={r.status_code} body={r.text[:200]}'
        )
        return False
    except httpx.TimeoutException:
        logger.warning('[slack_notify] timeout')
        return False
    except Exception as e:
        logger.warning(f'[slack_notify] fail: {e}')
        return False


__all__ = ['send_slack_alert', 'is_configured']
