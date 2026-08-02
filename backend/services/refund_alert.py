"""
Refund alerting service — surveille le taux de refund sur 7 jours glissants
et alerte les admins par email + Slack (opt-in) si depasse 5%.

Idempotent : ne renvoie pas 2 fois la meme alerte le meme jour.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

import httpx

from services.supabase_client import get_admin_client
from services.resend_service import send_email

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 60 * 60  # 1h
REFUND_ALERT_THRESHOLD_PCT = 5.0
MIN_PAID_TO_ALERT = 5  # ne pas alerter sur des petits volumes (1/1 = 100%)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '').strip()
_ALERT_STATE: Dict[str, str] = {'last_alert_date': ''}


def _compute_refund_stats_7d() -> Dict[str, Any]:
    """Calcule le taux de refund sur les 7 derniers jours."""
    sb = get_admin_client()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        r = sb.table('payment_transactions').select(
            'metadata, payment_status, user_email, created_at'
        ).eq('pack_id', 'lecture_complete').eq('payment_status', 'paid').gte(
            'created_at', since
        ).execute()
    except Exception as e:
        logger.warning(f'[refund_alert] fetch fail: {e}')
        return {'error': str(e)}

    rows = (r.data or []) if r else []
    paid, refunded = 0, 0
    refunded_details: List[Dict[str, Any]] = []
    for row in rows:
        md = row.get('metadata') or {}
        if md.get('admin_bypass'):
            continue  # exclu du monitoring
        paid += 1
        if md.get('refunded_at'):
            refunded += 1
            refunded_details.append({
                'email': row.get('user_email'),
                'refunded_at': md.get('refunded_at'),
                'reason': md.get('refund_reason'),
                'via_webhook': bool(md.get('refund_via_stripe_webhook')),
            })
    rate = round((refunded / paid * 100), 2) if paid else 0.0
    return {
        'paid': paid,
        'refunded': refunded,
        'rate_pct': rate,
        'window_days': 7,
        'details': refunded_details,
    }


async def _get_admin_emails() -> List[str]:
    sb = get_admin_client()
    try:
        r = sb.table('profiles').select('email').eq('is_admin', True).execute()
        emails = [(row.get('email') or '').strip() for row in (r.data or [])]
        return [e for e in emails if e and '@' in e]
    except Exception as e:
        logger.warning(f'[refund_alert] admin emails fetch fail: {e}')
        return ['admin@plume-astrale.fr']  # fallback


async def send_slack_refund_alert(stats: Dict[str, Any]) -> bool:
    """Poste un message dans Slack via incoming webhook. No-op si SLACK_WEBHOOK_URL absent."""
    if not SLACK_WEBHOOK_URL:
        return False
    rate = stats.get('rate_pct', 0)
    paid = stats.get('paid', 0)
    refunded = stats.get('refunded', 0)
    details = stats.get('details', [])
    detail_lines = '\n'.join(
        f'• `{d["email"]}` — {d["refunded_at"][:10]}'
        + (f' ({d["reason"][:60]})' if d.get('reason') else '')
        + (' _via webhook_' if d.get('via_webhook') else '')
        for d in details[:10]
    ) or '_Aucun refund detaille._'

    payload = {
        'text': f':warning: *Plume Astrale — Refund alert {rate}%*',
        'blocks': [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': f'⚠️ Refund Lecture Complete : {rate}%'},
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*{refunded}* remboursements sur *{paid}* paiements (7 jours, hors bypass admin).\n'
                            f'Seuil d\'alerte : {REFUND_ALERT_THRESHOLD_PCT}%.',
                },
            },
            {
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': f'*Refunds récents :*\n{detail_lines}'},
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': 'Ouvrir /admin'},
                        'url': 'https://plume-astrale.fr/admin',
                        'style': 'primary',
                    },
                ],
            },
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.post(SLACK_WEBHOOK_URL, json=payload)
            if r.status_code in (200, 204):
                logger.info('[refund_alert] Slack ping OK')
                return True
            logger.warning(f'[refund_alert] Slack returned {r.status_code}: {r.text[:200]}')
    except Exception as e:
        logger.warning(f'[refund_alert] Slack post fail: {e}')
    return False


async def send_refund_alert(stats: Dict[str, Any]) -> int:
    """Envoie l'alerte aux admins. Retourne le nombre d'emails envoyes."""
    admins = await _get_admin_emails()
    if not admins:
        return 0

    lines = ''.join(
        f'<li style="margin-bottom:6px;font-size:13px;">'
        f'<code>{d["email"]}</code> · remboursé le {d["refunded_at"][:10]}'
        + (f' · <em>{d["reason"]}</em>' if d.get("reason") else '')
        + (' · <span style="color:#a78bfa;">via Stripe webhook</span>' if d.get("via_webhook") else '')
        + '</li>'
        for d in stats.get('details', [])[:20]
    )

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:Georgia,serif;
                background:#0b1020;color:#e8e6f0;padding:32px 24px;line-height:1.6;">
      <div style="background:#141a33;border:1px solid #f87171;border-radius:12px;padding:26px;">
        <div style="color:#f87171;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:8px;">
          ⚠️ Alerte Refund
        </div>
        <h1 style="color:#d9b26a;font-size:22px;font-weight:400;margin:0 0 16px;">
          Taux de refund Lecture Complète : <strong style="color:#f87171;">{stats.get('rate_pct')}%</strong>
        </h1>
        <p>Sur les 7 derniers jours, <strong>{stats.get('refunded')} remboursements</strong> ont été
          enregistrés sur <strong>{stats.get('paid')} paiements</strong> (hors bypass admin).</p>
        <p>Seuil d'alerte : <strong>{REFUND_ALERT_THRESHOLD_PCT}%</strong>. Ce chiffre suggère un pattern
          à investiguer avant qu'il ne s'installe.</p>
        {"<h3 style='color:#d9b26a;font-size:14px;margin:20px 0 8px;'>Remboursements récents</h3><ul style='padding-left:18px;'>" + lines + "</ul>" if lines else ""}
        <p style="margin-top:24px;">
          <a href="https://plume-astrale.fr/admin" style="color:#d9b26a;">Ouvrir le tableau de bord →</a>
        </p>
        <p style="font-size:11px;color:#b8b4c9;margin-top:20px;">
          Alerte automatique. Une seule alerte par jour maximum.
        </p>
      </div>
    </div>
    """

    sent = 0
    subject = f'⚠️ Refund Plume Astrale : {stats.get("rate_pct")}% cette semaine'
    for admin_email in admins:
        try:
            eid = await send_email(admin_email, subject, html)
            if eid:
                sent += 1
        except Exception as e:
            logger.warning(f'[refund_alert] send fail to {admin_email}: {e}')

    # Slack notification en parallele (opt-in via SLACK_WEBHOOK_URL)
    slack_sent = False
    try:
        slack_sent = await send_slack_refund_alert(stats)
    except Exception as e:
        logger.warning(f'[refund_alert] slack fail: {e}')

    # Historique alertes (visible dans /admin)
    try:
        from services.app_settings import log_alert
        channels = []
        if sent:
            channels.append(f'email x{sent}')
        if slack_sent:
            channels.append('slack')
        log_alert(
            kind='refund_alert',
            title=f'Taux de refund {stats.get("rate_pct")}% (7j)',
            details=f'{stats.get("refunded")}/{stats.get("paid")} remboursements sur 7 jours.',
            channels=channels,
        )
    except Exception as e:
        logger.warning(f'[refund_alert] log_alert fail: {e}')

    return sent


async def refund_alert_loop() -> None:
    """Boucle background : verifie toutes les heures, envoie max 1 alerte/jour."""
    logger.info(f'[refund_alert] boucle demarree (seuil {REFUND_ALERT_THRESHOLD_PCT}%, verif chaque heure)')
    while True:
        try:
            stats = _compute_refund_stats_7d()
            if 'error' not in stats:
                today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                if (
                    stats.get('paid', 0) >= MIN_PAID_TO_ALERT
                    and stats.get('rate_pct', 0) >= REFUND_ALERT_THRESHOLD_PCT
                    and _ALERT_STATE.get('last_alert_date') != today
                ):
                    n = await send_refund_alert(stats)
                    if n:
                        _ALERT_STATE['last_alert_date'] = today
                        logger.info(f'[refund_alert] alerte envoyee a {n} admin(s) — taux {stats["rate_pct"]}%')
        except Exception as e:
            logger.warning(f'[refund_alert] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
