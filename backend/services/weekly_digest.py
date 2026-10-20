"""Journal hebdo Plume Astrale — envoyé chaque vendredi à 9h UTC via Resend.

Contenu (sans Search Console, qui nécessite OAuth séparé) :
- A/B stats : variantes gagnantes `home_hero_h1` + `synastrie_exit_intent` (7j)
- Alertes système envoyées (7j) depuis `admin_alerts`
- Leads lead-magnet synastrie (7j) depuis `synastrie_lead_followups` + `oracle_leads`
- Achats synastrie (7j) depuis `synastrie_purchases`

Après l'envoi, déclenche aussi `experiment_auto_lock.check_and_lock_experiment()`
pour verrouiller les variantes gagnantes au cas où les seuils seraient atteints.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr')


def _seconds_until_next_friday_9utc() -> float:
    """Nombre de secondes jusqu'au prochain vendredi 9h UTC."""
    now = datetime.now(timezone.utc)
    days_until_fri = (4 - now.weekday()) % 7  # vendredi = 4
    target = (now + timedelta(days=days_until_fri)).replace(hour=9, minute=0, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=7)
    return (target - now).total_seconds()


async def _collect_metrics() -> dict[str, Any]:
    """Agrège tous les KPIs 7 derniers jours. Chaque bloc gracieux si table absente."""
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    metrics: dict[str, Any] = {'ab': {}, 'alerts_count': 0, 'leads_count': 0, 'purchases_count': 0}

    # --- AB stats par expérience ---
    for exp in ('home_hero_h1', 'synastrie_exit_intent'):
        try:
            r = sb.table('ab_events').select('variant, event_name').eq('experiment', exp).gte('created_at', cutoff).limit(50000).execute()
            agg: dict[str, dict[str, int]] = {}
            for row in (r.data or []):
                v, e = row.get('variant'), row.get('event_name')
                if not v or not e:
                    continue
                agg.setdefault(v, {}).setdefault(e, 0)
                agg[v][e] += 1
            stats = []
            for v, counts in sorted(agg.items()):
                shown = counts.get('shown', 0)
                conv = counts.get('cta_click', 0) + counts.get('converted', 0) + counts.get('purchased', 0)
                stats.append({'variant': v, 'shown': shown, 'conversions': conv, 'rate': round(100.0 * conv / shown, 1) if shown else 0.0})
            metrics['ab'][exp] = stats
        except Exception as ex:
            logger.warning(f'[weekly] ab {exp} failed: {ex}')
            metrics['ab'][exp] = []

    # --- Alertes ---
    try:
        r = sb.table('admin_alerts').select('alert_type').gte('created_at', cutoff).limit(1000).execute()
        metrics['alerts_count'] = len(r.data or [])
    except Exception:
        pass

    # --- Leads ---
    try:
        r = sb.table('oracle_leads').select('id').gte('created_at', cutoff).limit(10000).execute()
        metrics['leads_count'] = len(r.data or [])
    except Exception:
        pass

    # --- Achats synastrie ---
    try:
        r = sb.table('synastrie_purchases').select('id, status').eq('status', 'paid').gte('created_at', cutoff).limit(10000).execute()
        metrics['purchases_count'] = len(r.data or [])
    except Exception:
        pass

    return metrics


def _render_html(m: dict[str, Any]) -> str:
    def _rows(exp_stats):
        if not exp_stats:
            return '<tr><td colspan="4" style="color:#94A3B8;font-style:italic;padding:8px 0;">Pas de données cette semaine</td></tr>'
        rows = []
        max_rate = max((s['rate'] for s in exp_stats), default=0)
        for s in exp_stats:
            is_winner = s['rate'] == max_rate and s['rate'] > 0 and len(exp_stats) > 1
            style = ' style="color:#4ADE80;font-weight:600;"' if is_winner else ''
            rows.append(
                f'<tr{style}><td style="padding:6px 0;">Variante <strong>{s["variant"]}</strong>{" 🏆" if is_winner else ""}</td>'
                f'<td>{s["shown"]} vues</td><td>{s["conversions"]} conv.</td><td><strong>{s["rate"]}%</strong></td></tr>'
            )
        return '\n'.join(rows)

    return f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 640px; margin: 0 auto; padding: 32px 24px; color: #0B1A2E; background: #FBF8F3;">
      <p style="font-family: Cinzel, serif; font-size: 10px; letter-spacing: 0.25em; text-transform: uppercase; color: #B8935A; margin: 0 0 10px;">Journal hebdomadaire</p>
      <h1 style="font-family: Fraunces, Georgia, serif; font-weight: 400; font-size: 28px; margin: 0 0 20px; letter-spacing: -0.01em;">
        Plume Astrale — les 7 derniers jours
      </h1>

      <h2 style="font-family: Fraunces, serif; font-size: 18px; font-weight: 400; margin: 32px 0 10px;">A/B · Hero home</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;color:#334155;"><tbody>{_rows(m['ab'].get('home_hero_h1', []))}</tbody></table>

      <h2 style="font-family: Fraunces, serif; font-size: 18px; font-weight: 400; margin: 32px 0 10px;">A/B · Exit-intent synastrie</h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;color:#334155;"><tbody>{_rows(m['ab'].get('synastrie_exit_intent', []))}</tbody></table>

      <h2 style="font-family: Fraunces, serif; font-size: 18px; font-weight: 400; margin: 32px 0 10px;">Activité</h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;color:#334155;">
        <tr><td style="padding:6px 0;">Leads générés</td><td style="text-align:right;font-weight:600;">{m['leads_count']}</td></tr>
        <tr><td style="padding:6px 0;">Achats synastrie 49€</td><td style="text-align:right;font-weight:600;color:#B8935A;">{m['purchases_count']} <span style="font-size:11px;color:#94A3B8;">({m['purchases_count']*49}€)</span></td></tr>
        <tr><td style="padding:6px 0;">Alertes système envoyées</td><td style="text-align:right;color:{'#F87171' if m['alerts_count'] > 0 else '#4ADE80'};">{m['alerts_count']}</td></tr>
      </table>

      <p style="margin-top: 36px; font-size: 12px; color: #94A3B8;">
        Journal généré automatiquement chaque vendredi à 9h UTC. 
        <a href="https://plume-astrale.fr/admin/alerts" style="color:#B8935A;">Voir le dashboard complet →</a>
      </p>
    </div>
    """


async def send_weekly_digest() -> bool:
    from services.resend_service import send_email
    metrics = await _collect_metrics()
    week_end = datetime.now(timezone.utc).strftime('%d/%m/%Y')
    subject = f'📬 Plume Astrale — Journal hebdo (semaine du {week_end})'
    html = _render_html(metrics)
    text = (
        f'Plume Astrale — Journal hebdo au {week_end}\n'
        f'Leads : {metrics["leads_count"]} · Achats 49€ : {metrics["purchases_count"]} · '
        f'Alertes système : {metrics["alerts_count"]}'
    )
    try:
        eid = await send_email(ADMIN_ALERT_EMAIL, subject, html, text)
        logger.info(f'[weekly_digest] envoyé → {ADMIN_ALERT_EMAIL} (resend_id={eid})')
        return bool(eid)
    except Exception as e:
        logger.exception(f'[weekly_digest] send failed: {e}')
        return False


async def weekly_digest_loop() -> None:
    """Vendredi 9h UTC → envoie digest + check auto-lock variantes gagnantes."""
    logger.info('[weekly_digest] boucle démarrée — envoi vendredi 9h UTC')
    while True:
        try:
            sleep_s = _seconds_until_next_friday_9utc()
            logger.info(f'[weekly_digest] prochain envoi dans {int(sleep_s/3600)}h')
            await asyncio.sleep(sleep_s)
            await send_weekly_digest()
            # Auto-lock variantes gagnantes après l'envoi
            try:
                from services.experiment_auto_lock import check_and_lock_experiment
                for exp in ('home_hero_h1', 'synastrie_exit_intent'):
                    result = await check_and_lock_experiment(exp)
                    logger.info(f'[weekly_digest] auto-lock {exp} → {result.get("status")} · {result.get("reason")}')
            except Exception as e:
                logger.warning(f'[weekly_digest] auto-lock failed: {e}')
        except asyncio.CancelledError:
            logger.info('[weekly_digest] boucle arrêtée')
            raise
        except Exception as e:
            logger.exception(f'[weekly_digest] iteration failed: {e}')
            await asyncio.sleep(3600)  # retry dans 1h si erreur
