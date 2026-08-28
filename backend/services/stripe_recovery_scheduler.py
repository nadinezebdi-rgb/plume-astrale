"""
Recovery Nocturne Stripe — cron qui tourne toutes les nuits à 03h00 UTC
et rejoue le batch recovery sur les 24 dernières heures.

Objectif : filet de sécurité qui rattrape automatiquement les paiements
Stripe non livrés (webhook down, timeout, handler crashé) avant que le
client ne râle sur les DMs Instagram.

Le vrai fix reste le webhook + le handler async. Ce cron est ceinture ET
bretelles pour les cas edge (webhook Stripe temporairement KO, incident
Supabase pendant le processing, etc.).
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Configuration
CHECK_INTERVAL_S = 15 * 60          # boucle toutes les 15 min (vérifie si on est proche de 03h UTC)
RECOVERY_HOUR_UTC = 3               # heure UTC de déclenchement (03h Paris été = 01h UTC ; 03h UTC = 04h Paris été / 05h hiver)
RECOVERY_WINDOW_DAYS = 1            # fenêtre 24h
RECOVERY_LIMIT = 200                # max sessions par run


async def _run_recovery_once() -> None:
    """Exécute un recovery batch sur les dernières 24h (dry_run=False)."""
    from services.stripe_recovery import recover_stuck_batch
    logger.info('[stripe_recovery_scheduler] lancement recovery nocturne (24h, réel)')
    try:
        report = await recover_stuck_batch(
            days=RECOVERY_WINDOW_DAYS,
            limit=RECOVERY_LIMIT,
            dry_run=False,
            concurrency=8,
        )
        logger.info(
            f'[stripe_recovery_scheduler] terminé — scanned={report["scanned"]} '
            f'actions={report.get("action_counts") or {}}'
        )
        # Si au moins 1 session a été "recovered", envoie un email admin de synthèse
        recovered_n = (report.get('action_counts') or {}).get('recovered', 0)
        if recovered_n > 0:
            try:
                from services.webhook_alert import send_webhook_alert
                await send_webhook_alert(
                    reason='nightly_recovery_saved',
                    details=f"Recovery nocturne : {recovered_n} paiement(s) Stripe rattrapé(s) sur les 24h. Vérifiez /admin/payments-health.",
                    dedup_key=f'nightly_recovery_{datetime.now(timezone.utc).date()}',
                )
            except Exception as _e:
                logger.warning(f'[stripe_recovery_scheduler] alerte admin fail: {_e}')
    except Exception as e:
        logger.exception(f'[stripe_recovery_scheduler] erreur recovery: {e}')


async def stripe_recovery_nightly_loop() -> None:
    """Boucle qui déclenche `_run_recovery_once` chaque nuit à 03h UTC.

    Utilise un flag in-memory `_last_run_date` pour éviter la double exécution
    dans la fenêtre 03h00-03h15 UTC. Reset à minuit.
    """
    logger.info(f'[stripe_recovery_scheduler] boucle démarrée '
                f'(déclenchement quotidien à {RECOVERY_HOUR_UTC:02d}h UTC, fenêtre 24h)')
    last_run_date = None
    while True:
        try:
            now = datetime.now(timezone.utc)
            today = now.date()
            # Déclenche entre RECOVERY_HOUR_UTC:00 et RECOVERY_HOUR_UTC:15
            in_window = (now.hour == RECOVERY_HOUR_UTC and now.minute < 15)
            if in_window and last_run_date != today:
                last_run_date = today
                await _run_recovery_once()
        except Exception as e:
            logger.warning(f'[stripe_recovery_scheduler] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
