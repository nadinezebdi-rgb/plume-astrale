"""
Scheduler daily 6h UTC : régénère les 12 PDFs d'horoscope journalier
avec les vrais transits du jour depuis astrology-api.io + GPT enrichissement.

Boucle background asyncio idempotente : ne relance pas si déjà exécuté pour la date du jour.
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, time, timezone, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# 6h00 UTC (= 7h Paris hiver / 8h Paris été) — bon compromis
TARGET_HOUR_UTC = 6
LAST_RUN_FILE = Path('/tmp/plume_horoscopes_last_run.txt')


def _seconds_until_next_run() -> float:
    """Calcule les secondes jusqu'au prochain 6h UTC."""
    now = datetime.now(timezone.utc)
    target = now.replace(hour=TARGET_HOUR_UTC, minute=0, second=0, microsecond=0)
    if now >= target:
        target = target + timedelta(days=1)
    delta = (target - now).total_seconds()
    return delta


def _already_ran_today() -> bool:
    if not LAST_RUN_FILE.exists():
        return False
    try:
        content = LAST_RUN_FILE.read_text().strip()
        return content == datetime.now(timezone.utc).strftime('%Y-%m-%d')
    except Exception:
        return False


def _mark_ran_today() -> None:
    try:
        LAST_RUN_FILE.write_text(datetime.now(timezone.utc).strftime('%Y-%m-%d'))
    except Exception as e:
        logger.warning(f'[horoscope_scheduler] mark_ran_today failed: {e}')


async def _regenerate_all() -> None:
    """Régénère les 12 PDFs et log les résultats."""
    from scripts.build_daily_horoscope import build_all
    logger.info('[horoscope_scheduler] ═══ Lancement régénération quotidienne 12 signes ═══')
    try:
        paths = await build_all()
        total_kb = sum(p.stat().st_size for p in paths) // 1024
        logger.info(f'[horoscope_scheduler] ✓ {len(paths)}/12 PDFs régénérés ({total_kb} KB total)')
        _mark_ran_today()
    except Exception as e:
        logger.exception(f'[horoscope_scheduler] échec régénération : {e}')


async def daily_horoscope_scheduler_loop() -> None:
    """Boucle infinie : dort jusqu'à 6h UTC puis lance la régénération."""
    logger.info('[horoscope_scheduler] boucle démarrée — cible 6h UTC quotidien')

    # Au démarrage : si on n'a pas encore tourné aujourd'hui ET qu'il est déjà passé 6h,
    # lance immédiatement (recovery cas de restart tardif).
    now = datetime.now(timezone.utc)
    if now.hour >= TARGET_HOUR_UTC and not _already_ran_today():
        logger.info('[horoscope_scheduler] recovery — pas encore tourné aujourd\u2019hui, lancement immédiat')
        await _regenerate_all()

    while True:
        sleep_s = _seconds_until_next_run()
        h = int(sleep_s // 3600)
        m = int((sleep_s % 3600) // 60)
        logger.info(f'[horoscope_scheduler] prochain run dans {h}h{m:02d} (à 6h UTC)')
        try:
            await asyncio.sleep(sleep_s)
        except asyncio.CancelledError:
            logger.info('[horoscope_scheduler] boucle arrêtée (CancelledError)')
            raise
        # C'est l'heure — lance la régénération
        await _regenerate_all()
        # Petite marge pour éviter double lancement (2 min)
        await asyncio.sleep(120)
