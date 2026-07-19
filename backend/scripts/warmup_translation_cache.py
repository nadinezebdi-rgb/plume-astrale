"""Warm-up du cache de traduction FR (french_polish).

Appelle chaque fonction API v3 décorée @fr_polish avec un jeu de données
représentatif pour peupler `translation_cache` (Supabase) et le cache mémoire.

Après un run, les prochains appels utilisateurs sont quasi-instantanés (0s de
latence GPT car tout est en cache).

Usage :
    cd /app/backend && python3 scripts/warmup_translation_cache.py

Variantes explorées (birth_data différentes) → couvre plus de segments FR
possibles. Le cache est indexé par SHA256(context|source_text), donc des
sujets natals variés = plus de strings uniques cachées.
"""
from __future__ import annotations
import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from services import astrology_io_service as aio  # noqa: E402
from services.french_polish import _is_english, _MEM_CACHE  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('warmup')

# 6 profils natals variés — planètes différentes = interprétations différentes
SAMPLE_PROFILES = [
    {'year': 1990, 'month': 5, 'day': 15, 'hour': 14, 'minute': 30, 'latitude': 48.8566, 'longitude': 2.3522, 'city': 'Paris', 'country_code': 'FR', 'name': 'Marie'},
    {'year': 1985, 'month': 11, 'day': 3, 'hour': 8, 'minute': 45, 'latitude': 45.7640, 'longitude': 4.8357, 'city': 'Lyon', 'country_code': 'FR', 'name': 'Sophie'},
    {'year': 1995, 'month': 7, 'day': 22, 'hour': 20, 'minute': 10, 'latitude': 43.6047, 'longitude': 1.4442, 'city': 'Toulouse', 'country_code': 'FR', 'name': 'Camille'},
    {'year': 1978, 'month': 2, 'day': 9, 'hour': 3, 'minute': 20, 'latitude': 43.7102, 'longitude': 7.2620, 'city': 'Nice', 'country_code': 'FR', 'name': 'Sarah'},
    {'year': 2000, 'month': 12, 'day': 27, 'hour': 11, 'minute': 55, 'latitude': 50.6292, 'longitude': 3.0573, 'city': 'Lille', 'country_code': 'FR', 'name': 'Léa'},
    {'year': 1970, 'month': 4, 'day': 18, 'hour': 17, 'minute': 5, 'latitude': 44.8378, 'longitude': -0.5792, 'city': 'Bordeaux', 'country_code': 'FR', 'name': 'Nathalie'},
]

# Signes zodiacaux pour horoscope_sign
SIGNS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
         'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']


def _count_en(obj) -> int:
    if isinstance(obj, str):
        return 1 if _is_english(obj) else 0
    if isinstance(obj, dict):
        return sum(_count_en(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_count_en(v) for v in obj)
    return 0


async def _warm(label: str, coro):
    t0 = time.time()
    try:
        result = await coro
    except Exception as e:
        logger.warning(f'  ⚠️  {label}: {e}')
        return
    if not result:
        logger.info(f'  ⚠️  {label}: no data')
        return
    dt = time.time() - t0
    en = _count_en(result)
    status = '✅' if en == 0 else f'🟡 ({en} EN restants)'
    logger.info(f'  {status} {label} ({dt:.1f}s)')


async def main():
    logger.info('═══════════════════════════════════════════════════════════')
    logger.info('  WARM-UP CACHE TRADUCTION FR — début')
    logger.info('═══════════════════════════════════════════════════════════')
    logger.info(f'{len(SAMPLE_PROFILES)} profils × 7 endpoints = ~42 appels')
    logger.info(f'{len(SIGNS)} signes × horoscope_sign = 12 appels supplémentaires')
    t_start = time.time()

    # Endpoints natal-based (décorés @fr_polish)
    for i, prof in enumerate(SAMPLE_PROFILES, 1):
        name = prof.pop('name')
        logger.info(f'\n─── Profil {i}/{len(SAMPLE_PROFILES)} · {name} ({prof["year"]}) ───')
        await _warm(f'love_languages/{name}', aio.love_languages(prof, name=name, language='fr'))
        await _warm(f'archetypes/{name}', aio.archetypes(prof, name=name, language='fr'))
        await _warm(f'karmic_analysis/{name}', aio.karmic_analysis(prof, name=name, language='fr'))
        await _warm(f'numerology_core/{name}', aio.numerology_core_numbers(prof, name=name, language='fr'))
        await _warm(f'personality_analysis/{name}', aio.personality_analysis(prof, name=name, language='fr'))
        await _warm(f'chinese_zodiac/{name}', aio.chinese_zodiac(prof, name=name, language='fr'))
        await _warm(f'horoscope_personal/{name}', aio.horoscope_personal(prof, period='daily', name=name, language='fr'))

    # Endpoints par signe (daily + weekly + monthly)
    logger.info('\n─── Horoscopes par signe (36 appels) ───')
    for sign in SIGNS:
        for period in ('daily', 'weekly', 'monthly'):
            await _warm(f'horoscope_sign/{sign}/{period}', aio.horoscope_sign(sign, period=period, language='fr'))

    total = time.time() - t_start
    logger.info('\n═══════════════════════════════════════════════════════════')
    logger.info(f'  TERMINÉ en {total:.1f}s — cache mémoire : {len(_MEM_CACHE)} entrées')
    logger.info('═══════════════════════════════════════════════════════════')
    logger.info('Les traductions sont persistées dans translation_cache (Supabase)')
    logger.info('et disponibles instantanément pour tous les futurs utilisateurs.')


if __name__ == '__main__':
    asyncio.run(main())
