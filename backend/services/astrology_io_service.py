"""Service Astrology API v3 (astrology-api.io)
Bien plus riche que astrologyapi.com : horoscopes daily/weekly/monthly/yearly en FR,
8+ life areas, ratings, mots-cles, emojis.

Cache 24h dans Supabase (table energy_cache reutilisable) pour limiter les appels.
"""
import os
import httpx
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timezone


BASE_URL = 'https://api.astrology-api.io/api/v3'


_SIGN_FR_TO_EN = {
    'Bélier': 'aries', 'Belier': 'aries', 'aries': 'aries',
    'Taureau': 'taurus', 'taurus': 'taurus',
    'Gémeaux': 'gemini', 'Gemeaux': 'gemini', 'gemini': 'gemini',
    'Cancer': 'cancer', 'cancer': 'cancer',
    'Lion': 'leo', 'leo': 'leo',
    'Vierge': 'virgo', 'virgo': 'virgo',
    'Balance': 'libra', 'libra': 'libra',
    'Scorpion': 'scorpio', 'scorpio': 'scorpio',
    'Sagittaire': 'sagittarius', 'sagittarius': 'sagittarius',
    'Capricorne': 'capricorn', 'capricorn': 'capricorn',
    'Verseau': 'aquarius', 'aquarius': 'aquarius',
    'Poissons': 'pisces', 'pisces': 'pisces',
}


def _normalize_sign(sign: str) -> str:
    if not sign:
        return 'aries'
    return _SIGN_FR_TO_EN.get(sign.strip(), sign.strip().lower())


def _api_key() -> str:
    k = os.environ.get('ASTROLOGY_API_IO_KEY')
    if not k:
        raise RuntimeError('ASTROLOGY_API_IO_KEY env var manquante')
    return k


async def _call(path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """POST helper. Retourne data ou None si echec."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                f'{BASE_URL}{path}',
                headers={
                    'Authorization': f'Bearer {_api_key()}',
                    'Content-Type': 'application/json',
                },
                json=payload,
            )
            if r.status_code != 200:
                print(f'[astrology_io] {path} -> {r.status_code} : {r.text[:200]}')
                return None
            data = r.json()
            return data.get('data', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f'[astrology_io] {path} EXCEPTION : {e}')
        return None


# ════════ HOROSCOPE BY SIGN (no birth data needed) ════════

async def horoscope_sign(sign: str, period: str = 'daily', language: str = 'fr') -> Optional[Dict]:
    """period: daily | weekly | monthly | yearly"""
    valid = {'daily', 'weekly', 'monthly', 'yearly'}
    if period not in valid:
        period = 'daily'
    return await _call(
        f'/horoscope/sign/{period}',
        {'sign': _normalize_sign(sign), 'language': language},
    )


# ════════ PERSONAL HOROSCOPE (uses birth data for personalization) ════════

async def horoscope_personal(
    birth_date: str,   # YYYY-MM-DD
    birth_time: str,   # HH:MM
    lat: float,
    lon: float,
    tzone: float = 1.0,
    period: str = 'daily',
    language: str = 'fr',
) -> Optional[Dict]:
    """Horoscope personnalise utilisant le theme natal de l'utilisateur.
    Bien plus precis que horoscope par signe."""
    valid = {'daily', 'weekly', 'monthly', 'yearly'}
    if period not in valid:
        period = 'daily'

    try:
        y, m, d = birth_date.split('-')
        h, mn = (birth_time or '12:00').split(':')[:2]
    except Exception as e:
        print(f'[astrology_io] parse birth_date/time error: {e}')
        return None

    payload = {
        'birth_data': {
            'date': {'year': int(y), 'month': int(m), 'day': int(d)},
            'time': {'hour': int(h), 'minute': int(mn)},
            'location': {'latitude': float(lat), 'longitude': float(lon), 'timezone': float(tzone)},
        },
        'language': language,
    }
    return await _call(f'/horoscope/personal/{period}', payload)


# ════════ Cache helper (24h) using Supabase energy_cache table ════════

def _cache_key(*parts) -> str:
    raw = '|'.join(str(p) for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()


async def get_cached_or_fetch(key: str, fetch_fn, ttl_hours: int = 24) -> Optional[Dict]:
    """Lit le cache Supabase, sinon appelle fetch_fn et stocke."""
    try:
        from services.wallet_service import get_admin_client
        sb = get_admin_client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        cached = sb.table('energy_cache').select('*').eq('date', today).eq('user_id', key).maybe_single().execute()
        if cached and cached.data:
            return cached.data.get('energy_data') or cached.data.get('data')
    except Exception as e:
        print(f'[astrology_io.cache] read error: {e}')

    fresh = await fetch_fn()
    if not fresh:
        return None

    try:
        from services.wallet_service import get_admin_client
        sb = get_admin_client()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        sb.table('energy_cache').upsert({
            'date': today, 'user_id': key, 'energy_data': fresh,
        }).execute()
    except Exception as e:
        print(f'[astrology_io.cache] write error: {e}')

    return fresh
