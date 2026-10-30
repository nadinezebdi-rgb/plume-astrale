"""stuck_sessions_alert — Alerte admin pour les sessions Stripe bloquées > 1h.

Scanne toutes les 15 minutes la table ``payment_transactions`` et envoie un
email admin (via Resend) listant les sessions ``initiated/unpaid`` plus
anciennes que ``STUCK_ALERT_THRESHOLD_MIN`` (défaut 60 min) qui n'ont pas
encore été alertées.

Déduplication :
  • Par ``session_id`` : chaque session n'est alertée qu'une seule fois.
  • Les e-mails de test (contact@, admin@, test@, @plume-astrale.fr) sont
    exclus (même logique que `/admin/payments-health`).
  • Un batch regroupe toutes les nouvelles sessions sur un seul email ;
    rate-limit implicite via l'intervalle de scan (15 min).

Destinataire : ``ADMIN_ALERT_EMAIL`` depuis l'environnement.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from services.log_redact import redact_email
from services.resend_service import send_email
from services.slack_notify import send_slack_alert
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = int(os.environ.get('STUCK_ALERT_INTERVAL_S', str(15 * 60)))
STUCK_THRESHOLD_MIN = int(os.environ.get('STUCK_ALERT_THRESHOLD_MIN', '60'))
LOOKBACK_HOURS = int(os.environ.get('STUCK_ALERT_LOOKBACK_H', '72'))

# État in-memory : session_ids déjà alertés. Reset au restart (acceptable :
# si une session reste bloquée après restart, elle sera réalertée une fois).
_alerted: set = set()  # legacy — conservé pour compat tests, non utilisé.


def _is_test_email(email: Optional[str]) -> bool:
    if not email:
        return False
    e = email.lower().strip()
    if '@plume-astrale.fr' in e:
        return True
    if e.startswith('contact@') or e.startswith('admin@') or e.startswith('test@'):
        return True
    if '@test.' in e or '@example.' in e:
        return True
    if '+test' in e or '+debug' in e:
        return True
    return False


def _collect_stuck_sessions(threshold_min: int = STUCK_THRESHOLD_MIN,
                            lookback_h: int = LOOKBACK_HOURS) -> List[Dict]:
    """Renvoie les sessions `initiated/unpaid` plus vieilles que ``threshold_min``,
    dédupées par session_id, hors e-mails de test, hors sessions déjà alertées.
    """
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    lookback_cutoff = (now - timedelta(hours=lookback_h)).isoformat()
    stuck_cutoff = now - timedelta(minutes=threshold_min)

    try:
        r = (
            sb.table('payment_transactions')
            .select('session_id, user_email, pack_id, amount, currency, status, payment_status, metadata, created_at')
            .gte('created_at', lookback_cutoff)
            .order('created_at', desc=True)
            .limit(500)
            .execute()
        )
        rows = r.data or []
    except Exception as e:
        logger.warning(f'[stuck_sessions_alert] fetch fail: {e}')
        return []

    # Index par session_id : si une ligne passe à `paid`, la session n'est plus bloquée.
    paid_sessions: set = set()
    stuck_candidates: Dict[str, Dict] = {}
    for row in rows:
        sid = (row.get('session_id') or '').strip()
        if not sid or not sid.startswith('cs_'):
            continue
        if _is_test_email(row.get('user_email')):
            continue
        if row.get('payment_status') == 'paid':
            paid_sessions.add(sid)
            continue
        if row.get('status') == 'initiated' and row.get('payment_status') == 'unpaid':
            created = row.get('created_at')
            try:
                created_dt = datetime.fromisoformat((created or '').replace('Z', '+00:00'))
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if created_dt < stuck_cutoff:
                # On garde la plus ancienne ligne pour cette session
                prev = stuck_candidates.get(sid)
                if not prev or created_dt < datetime.fromisoformat(
                    prev['created_at'].replace('Z', '+00:00')
                ):
                    row['_age_min'] = int((now - created_dt).total_seconds() / 60)
                    stuck_candidates[sid] = row

    stuck = [row for sid, row in stuck_candidates.items() if sid not in paid_sessions]
    # Dédup déplacé dans check_once (via services.alert_cooldown Mongo-backed).
    return stuck


def _build_email(stuck_rows: List[Dict]) -> tuple[str, str]:
    """Compose (subject, html) pour l'email admin."""
    n = len(stuck_rows)
    subject = f'[Plume Astrale] {n} session{"s" if n > 1 else ""} Stripe bloquée{"s" if n > 1 else ""} > {STUCK_THRESHOLD_MIN} min'

    rows_html = []
    for r in stuck_rows:
        age = r.get('_age_min', 0)
        hours = age // 60
        mins = age % 60
        age_label = f'{hours}h{mins:02d}' if hours else f'{mins} min'
        amount = r.get('amount') or 0
        try:
            amount_str = f'{float(amount):.2f} €'.replace('.', ',')
        except Exception:
            amount_str = f'{amount} €'
        rows_html.append(f'''
          <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;font-family:monospace;font-size:12px;">{r.get("session_id", "n/a")[:28]}…</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{r.get("user_email") or "—"}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{r.get("pack_id") or "—"}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:right;">{amount_str}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;color:#c0392b;">{age_label}</td>
          </tr>''')

    html = f'''
<div style="font-family:'Helvetica Neue',Arial,sans-serif;max-width:720px;margin:0 auto;padding:32px;color:#0B1A2E;">
  <h2 style="color:#c0392b;margin-top:0;">⚠️ {n} session{"s" if n > 1 else ""} Stripe en attente de livraison</h2>
  <p style="font-size:14px;line-height:1.6;">
    Ces sessions ont été initiées il y a plus de <strong>{STUCK_THRESHOLD_MIN} minutes</strong>
    et n'ont toujours pas abouti à une livraison. Elles méritent une vérification manuelle via
    <code>/admin/payments-health</code> ou <code>/admin/stripe-recovery</code>.
  </p>
  <table style="width:100%;border-collapse:collapse;margin-top:16px;font-size:13px;">
    <thead>
      <tr style="background:#F5EEE0;color:#0B1A2E;">
        <th style="padding:10px 12px;text-align:left;">Session</th>
        <th style="padding:10px 12px;text-align:left;">Email</th>
        <th style="padding:10px 12px;text-align:left;">Pack</th>
        <th style="padding:10px 12px;text-align:right;">Montant</th>
        <th style="padding:10px 12px;text-align:left;">Âge</th>
      </tr>
    </thead>
    <tbody>{"".join(rows_html)}</tbody>
  </table>
  <p style="font-size:12px;color:#8891A4;margin-top:24px;font-style:italic;">
    Alerte générée automatiquement — chaque session n'est signalée qu'une seule fois par cycle de vie du pod.
    Prochain scan dans {CHECK_INTERVAL_S // 60} min.
  </p>
</div>'''
    return subject, html


async def check_once() -> int:
    """Un passage de scan ; renvoie le nombre de sessions nouvellement alertées."""
    candidates = _collect_stuck_sessions()
    if not candidates:
        return 0

    # Dédup Mongo-backed (TTL = LOOKBACK_HOURS) : ne pas re-alerter sur la même
    # session dans la fenêtre. Survit aux restarts pod. Fail-open si Mongo down.
    from services.alert_cooldown import try_acquire
    stuck: List[Dict] = []
    for row in candidates:
        sid = row.get('session_id')
        if not sid:
            continue
        if await try_acquire('stuck_session', sid, ttl_hours=LOOKBACK_HOURS):
            stuck.append(row)
    if not stuck:
        return 0

    admin_email = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr').strip()
    if not admin_email:
        logger.warning('[stuck_sessions_alert] ADMIN_ALERT_EMAIL absent — scan effectué mais pas d\'envoi')
        return 0

    subject, html = _build_email(stuck)
    eid = await send_email(admin_email, subject, html)

    # AUDIT (2026-10-30 · Nao) : ping Slack en plus de l'email, si webhook configurée.
    # Fail-silent — si Slack est down, l'email reste la source de vérité.
    try:
        n = len(stuck)
        total_eur = sum(float(r.get('amount') or 0) for r in stuck)
        fields = []
        for r in stuck[:5]:  # cap à 5 pour la lisibilité Slack
            age = r.get('_age_min', 0)
            hours, mins = divmod(age, 60)
            age_label = f'{hours}h{mins:02d}' if hours else f'{mins} min'
            fields.append((
                r.get('user_email') or 'inconnu',
                f"{r.get('pack_id') or '—'} · {float(r.get('amount') or 0):.2f} € · {age_label}",
            ))
        if n > 5:
            fields.append(('…', f'et {n - 5} session(s) supplémentaires'))
        await send_slack_alert(
            title=f"{n} session{'s' if n > 1 else ''} Stripe bloquée{'s' if n > 1 else ''} > {STUCK_THRESHOLD_MIN} min",
            summary=f'*Montant total potentiellement perdu* : {total_eur:.2f} €\nFenêtre {LOOKBACK_HOURS}h.',
            fields=fields,
            url='https://plume-astrale.fr/admin/payments-health',
            url_label='Ouvrir /admin/payments-health',
            emoji=':rotating_light:',
        )
    except Exception as e:
        logger.info(f'[stuck_sessions_alert] slack ping skip: {e}')

    if eid:
        logger.info(
            f'[stuck_sessions_alert] alerté {len(stuck)} session(s) à '
            f'{redact_email(admin_email)} (resend_id={eid})'
        )
        return len(stuck)
    logger.warning('[stuck_sessions_alert] send_email a échoué, cooldown à revalider manuellement')
    return 0


async def stuck_sessions_alert_loop() -> None:
    """Boucle background : scan toutes les 15 min des sessions bloquées > 1h."""
    logger.info(
        f'[stuck_sessions_alert] démarrage (seuil {STUCK_THRESHOLD_MIN} min, '
        f'scan toutes les {CHECK_INTERVAL_S}s)'
    )
    while True:
        try:
            await check_once()
        except Exception as e:
            logger.warning(f'[stuck_sessions_alert] boucle err: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)


__all__ = ['stuck_sessions_alert_loop', 'check_once', '_collect_stuck_sessions']
