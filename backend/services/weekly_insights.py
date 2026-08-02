"""
Weekly insights recap — vendredi 09h00 UTC.

Envoie aux admins un recap hebdo :
  - Top raisons de refund (7j)
  - Variante A/B gagnante J+30 (CTR)
  - Nouveaux paiements & taux de refund

Idempotent : ne renvoie pas 2x le meme vendredi (via app_settings).
"""
from __future__ import annotations
import asyncio
import logging
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from services.supabase_client import get_admin_client
from services.resend_service import send_email
from services.app_settings import get_setting, set_setting, log_alert

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 60 * 60  # 1h
TARGET_WEEKDAY = 4  # 0=Mon .. 4=Fri
TARGET_HOUR_UTC = 9


def _extract_reason_key(reason: str) -> str:
    """Normalise une raison free-text en categorie principale."""
    if not reason:
        return 'sans_raison'
    r = reason.lower()
    if 'pdf' in r and ('defect' in r or 'incomplet' in r or 'blanc' in r):
        return 'pdf_defectueux'
    if 'doublon' in r or 'duplicate' in r:
        return 'doublon'
    if 'chargeback' in r or 'litige' in r:
        return 'chargeback'
    if 'insatisfait' in r or 'satisf' in r or 'mecontent' in r or 'décept' in r or 'decept' in r:
        return 'insatisfait'
    if 'erreur' in r or 'mauvais' in r:
        return 'achat_erreur'
    if 'livr' in r or 'recu' in r or 'reçu' in r:
        return 'non_livre'
    return 'autre'


def _compute_weekly_recap() -> Dict[str, Any]:
    sb = get_admin_client()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        r = sb.table('payment_transactions').select(
            'metadata, payment_status, amount, user_email, created_at'
        ).eq('pack_id', 'lecture_complete').gte('created_at', since).execute()
    except Exception as e:
        logger.warning(f'[weekly_insights] fetch fail: {e}')
        return {'error': str(e)}

    rows = (r.data or []) if r else []
    paid, refunded, revenue_cents = 0, 0, 0
    reason_counter: Counter = Counter()
    j30_variants: Counter = Counter()
    for row in rows:
        md = row.get('metadata') or {}
        if md.get('admin_bypass'):
            continue
        if row.get('payment_status') == 'paid':
            paid += 1
            try:
                revenue_cents += int(round(float(row.get('amount') or 0) * 100))
            except Exception:
                pass
            if md.get('refunded_at'):
                refunded += 1
                reason_counter[_extract_reason_key(md.get('refund_reason') or '')] += 1
        v = md.get('sequence_j30_variant')
        if v and md.get('sequence_j30_sent_at'):
            j30_variants[v] += 1

    forced_variant = get_setting('forced_j30_variant')
    rate = round((refunded / paid * 100), 2) if paid else 0.0
    top_reasons: List[Dict[str, Any]] = [
        {'reason': k, 'count': v} for k, v in reason_counter.most_common(5)
    ]
    return {
        'paid': paid,
        'refunded': refunded,
        'rate_pct': rate,
        'revenue_eur': round(revenue_cents / 100, 2),
        'top_refund_reasons': top_reasons,
        'j30_variants': dict(j30_variants),
        'forced_j30_variant': forced_variant,
    }


async def _get_admin_emails() -> List[str]:
    sb = get_admin_client()
    try:
        r = sb.table('profiles').select('email').eq('is_admin', True).execute()
        emails = [(row.get('email') or '').strip() for row in (r.data or [])]
        return [e for e in emails if e and '@' in e]
    except Exception:
        return ['admin@plume-astrale.fr']


def _render_html(stats: Dict[str, Any]) -> str:
    reasons_html = ''.join(
        f'<li style="margin-bottom:4px;"><strong style="color:#d9b26a;">{r["reason"]}</strong> '
        f'<span style="color:#b8b4c9;">· {r["count"]} refund{"s" if r["count"]>1 else ""}</span></li>'
        for r in stats.get('top_refund_reasons') or []
    ) or '<li style="color:#4ADE80;">Aucun refund cette semaine ✨</li>'

    j30 = stats.get('j30_variants') or {}
    j30_q, j30_i = j30.get('question', 0), j30.get('invitation', 0)
    j30_total = j30_q + j30_i
    winner_hint = ''
    if j30_total >= 20:
        pct_q = round(j30_q / j30_total * 100)
        pct_i = 100 - pct_q
        winner_hint = f'<div style="color:#e8e6f0;">Question <strong>{pct_q}%</strong> · Invitation <strong>{pct_i}%</strong> (basé sur {j30_total} envois)</div>'
    else:
        winner_hint = f'<div style="color:#b8b4c9;">{j30_total} envois — trop tôt pour un gagnant (seuil 20).</div>'
    forced = stats.get('forced_j30_variant')
    forced_note = ''
    if forced:
        forced_note = f'<div style="color:#a78bfa;margin-top:4px;font-size:12px;">🔒 Bascule forcée manuelle sur <strong>{forced}</strong></div>'

    return f'''
    <div style="max-width:640px;margin:0 auto;font-family:Georgia,serif;
                background:#0b1020;color:#e8e6f0;padding:32px 24px;line-height:1.6;">
      <div style="background:#141a33;border:1px solid rgba(217,178,106,0.35);border-radius:12px;padding:28px;">
        <div style="color:#d9b26a;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:8px;">
          📊 Recap hebdo Plume Astrale
        </div>
        <h1 style="color:#d9b26a;font-size:24px;font-weight:400;margin:0 0 20px;">
          {stats.get("paid",0)} paiements · {stats.get("revenue_eur",0)}€ · {stats.get("rate_pct",0)}% refund
        </h1>
        <p style="color:#b8b4c9;font-size:13px;">
          7 derniers jours, hors bypass admin.
        </p>

        <h3 style="color:#d9b26a;font-size:14px;margin:24px 0 8px;letter-spacing:.08em;text-transform:uppercase;">
          Top raisons de refund
        </h3>
        <ul style="padding-left:20px;color:#e8e6f0;font-size:13px;">{reasons_html}</ul>

        <h3 style="color:#d9b26a;font-size:14px;margin:24px 0 8px;letter-spacing:.08em;text-transform:uppercase;">
          A/B J+30 upsell
        </h3>
        {winner_hint}
        {forced_note}

        <p style="margin-top:28px;font-size:12px;">
          <a href="https://plume-astrale.fr/admin" style="color:#d9b26a;">Ouvrir le tableau de bord →</a>
        </p>
        <p style="font-size:11px;color:#7c7ce5;margin-top:16px;font-style:italic;">
          Automatique · Vendredi 09h UTC · Réponds à ce mail pour désactiver.
        </p>
      </div>
    </div>
    '''


async def _send_weekly_recap() -> int:
    stats = _compute_weekly_recap()
    if 'error' in stats:
        return 0
    admins = await _get_admin_emails()
    if not admins:
        return 0
    subject = f'📊 Plume Astrale — Recap {stats.get("paid",0)} paiements · {stats.get("rate_pct",0)}% refund'
    html = _render_html(stats)
    sent = 0
    for admin_email in admins:
        try:
            eid = await send_email(admin_email, subject, html)
            if eid:
                sent += 1
        except Exception as e:
            logger.warning(f'[weekly_insights] send fail to {admin_email}: {e}')
    if sent:
        try:
            log_alert(
                kind='weekly_recap',
                title=f'Recap hebdo envoyé ({stats.get("paid",0)} paiements, {stats.get("rate_pct",0)}% refund)',
                details=f"Top: {', '.join(r['reason'] for r in stats.get('top_refund_reasons') or []) or 'aucun refund'}",
                channels=[f'email x{sent}'],
            )
        except Exception:
            pass
    return sent


async def weekly_insights_loop() -> None:
    """Boucle background : verifie chaque heure, envoie le vendredi 09h UTC max 1x."""
    logger.info(f'[weekly_insights] boucle demarree (vendredi {TARGET_HOUR_UTC}h UTC)')
    while True:
        try:
            now = datetime.now(timezone.utc)
            today_key = now.strftime('%Y-%m-%d')
            if (
                now.weekday() == TARGET_WEEKDAY
                and now.hour == TARGET_HOUR_UTC
                and get_setting('weekly_recap_last_date') != today_key
            ):
                n = await _send_weekly_recap()
                if n:
                    set_setting('weekly_recap_last_date', today_key)
                    logger.info(f'[weekly_insights] recap envoyé à {n} admin(s) — {today_key}')
        except Exception as e:
            logger.warning(f'[weekly_insights] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)


async def send_weekly_recap_now() -> Dict[str, Any]:
    """Force l'envoi immediat (endpoint admin trigger)."""
    n = await _send_weekly_recap()
    return {'sent_to': n, 'stats': _compute_weekly_recap()}
