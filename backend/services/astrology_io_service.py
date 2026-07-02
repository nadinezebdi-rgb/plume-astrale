"""Service Astrology API v3 (astrology-api.io)
Service unifie pour appeler l'API v3 :
- Horoscopes daily/weekly/monthly/yearly (par signe ou personnalise)
- Positions planetaires, cuspides des maisons, aspects, metriques lunaires
- Themes natals, synastrie (compatibilite), composite, rapports textuels

Tous les appels prennent en compte un cache 24h dans Supabase (table energy_cache).
"""
import os
import httpx
import hashlib
from typing import Optional, Dict, Any, List
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

_SIGN_EN_TO_FR = {
    'Aries': 'Bélier', 'Taurus': 'Taureau', 'Gemini': 'Gémeaux', 'Cancer': 'Cancer',
    'Leo': 'Lion', 'Virgo': 'Vierge', 'Libra': 'Balance', 'Scorpio': 'Scorpion',
    'Sagittarius': 'Sagittaire', 'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons',
}


def normalize_sign(sign: str) -> str:
    if not sign:
        return 'aries'
    return _SIGN_FR_TO_EN.get(sign.strip(), sign.strip().lower())


def sign_to_fr(sign: str) -> str:
    if not sign:
        return ''
    s = sign.strip()
    return _SIGN_EN_TO_FR.get(s.title(), s)


def _api_key() -> str:
    k = os.environ.get('ASTROLOGY_API_IO_KEY')
    if not k:
        raise RuntimeError('ASTROLOGY_API_IO_KEY env var manquante')
    return k


async def _call(path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """POST helper. Retourne data ou None si echec. Logs minimal."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
            if not isinstance(data, dict):
                return data
            # Explicit error : success:false + error dict present -> fail
            if data.get('success') is False and data.get('error'):
                print(f"[astrology_io] {path} success=false : {data.get('error')}")
                return None
            # v3 wraps in {success:true, data: {...}} sometimes
            if 'data' in data and data.get('success') is True:
                return data['data']
            # Sinon on retourne le payload tel quel (certains endpoints comme synastry
            # renvoient chart_data + subject_data au niveau racine, sans wrapper).
            return data
    except Exception as e:
        print(f'[astrology_io] {path} EXCEPTION : {e}')
        return None


# ════════ HELPERS pour construire le Subject ════════

def make_birth_data(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0,
    latitude: Optional[float] = None, longitude: Optional[float] = None,
    city: Optional[str] = None, country_code: Optional[str] = None,
    timezone_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Construit un objet birth_data compatible v3 (DateTimeLocation + BirthData)."""
    bd: Dict[str, Any] = {
        'year': int(year), 'month': int(month), 'day': int(day),
        'hour': int(hour), 'minute': int(minute),
    }
    if latitude is not None and longitude is not None:
        bd['latitude'] = float(latitude)
        bd['longitude'] = float(longitude)
    if city:
        bd['city'] = city
    if country_code:
        bd['country_code'] = country_code.upper()[:2]
    if timezone_name:
        bd['timezone'] = timezone_name
    return bd


def make_subject(name: str, birth_data: Dict[str, Any]) -> Dict[str, Any]:
    return {'name': name or 'Anonymous', 'birth_data': birth_data}


def parse_profile(profile: Dict[str, Any], default_name: str = 'Voyageur') -> Optional[Dict[str, Any]]:
    """A partir d'un profil Supabase user, retourne un birth_data v3 (ou None si incomplet)."""
    bd = profile.get('birth_date')
    bt = profile.get('birth_time') or '12:00'
    if not bd:
        return None
    try:
        y, m, d = str(bd)[:10].split('-')
        h, mn = str(bt)[:5].split(':')
        return make_birth_data(
            int(y), int(m), int(d), int(h), int(mn),
            latitude=profile.get('latitude'),
            longitude=profile.get('longitude'),
            city=(profile.get('birth_place') or '').split(',')[0].strip() or None,
            country_code=_country_to_code(profile.get('birth_country')),
        )
    except Exception as e:
        print(f'[astrology_io.parse_profile] {e}')
        return None


_COUNTRY_CODE_MAP = {
    'france': 'FR', 'belgium': 'BE', 'belgique': 'BE', 'suisse': 'CH', 'switzerland': 'CH',
    'canada': 'CA', 'maroc': 'MA', 'morocco': 'MA', 'algerie': 'DZ', 'algeria': 'DZ',
    'tunisie': 'TN', 'tunisia': 'TN', 'senegal': 'SN', 'sénégal': 'SN', 'cote d\'ivoire': 'CI',
    'united kingdom': 'GB', 'uk': 'GB', 'royaume-uni': 'GB', 'usa': 'US', 'us': 'US',
    'united states': 'US', 'spain': 'ES', 'espagne': 'ES', 'italy': 'IT', 'italie': 'IT',
    'germany': 'DE', 'allemagne': 'DE', 'portugal': 'PT',
}


def _country_to_code(country: Optional[str]) -> Optional[str]:
    if not country:
        return None
    c = country.strip()
    if len(c) == 2 and c.isalpha():
        return c.upper()
    return _COUNTRY_CODE_MAP.get(c.lower())


# ════════ HOROSCOPE BY SIGN ════════

async def horoscope_sign(sign: str, period: str = 'daily', language: str = 'fr') -> Optional[Dict]:
    valid = {'daily', 'weekly', 'monthly', 'yearly'}
    if period not in valid:
        period = 'daily'
    return await _call(
        f'/horoscope/sign/{period}',
        {'sign': normalize_sign(sign), 'language': language},
    )


# ════════ HOROSCOPE PERSONNALISE ════════

async def horoscope_personal(
    birth_data: Dict[str, Any],
    period: str = 'daily',
    language: str = 'fr',
    name: str = 'Voyageur',
) -> Optional[Dict]:
    valid = {'daily', 'weekly', 'monthly', 'yearly'}
    if period not in valid:
        period = 'daily'
    payload = {
        'subject': make_subject(name, birth_data),
        'horoscope_type': period,
        'language': language,
    }
    return await _call(f'/horoscope/personal/{period}', payload)


# ════════ DATA : POSITIONS / CUSPIDES / ASPECTS / LUNAIRE ════════

async def get_positions(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Positions planetaires precises (signes, degres, maisons)."""
    return await _call('/data/positions', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


async def get_house_cusps(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Cuspides des 12 maisons (Placidus)."""
    return await _call('/data/house-cusps', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


async def get_aspects(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Aspects planetaires (conjonctions, trigones, carres, etc)."""
    return await _call('/data/aspects', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


async def get_lunar_metrics(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Phase lunaire, signe lunaire, mansion, etc."""
    return await _call('/data/lunar-metrics', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })


# ════════ CHARTS : NATAL / SYNASTRY / COMPOSITE ════════

async def natal_chart(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    return await _call('/charts/natal', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


async def synastry_chart(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Partenaire 1', name_2: str = 'Partenaire 2',
    language: str = 'fr',
) -> Optional[Dict]:
    return await _call('/charts/synastry', {
        'subject1': make_subject(name_1, birth_data_1),
        'subject2': make_subject(name_2, birth_data_2),
        'options': {'language': language, 'house_system': 'P'},
    })


async def composite_chart(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Partenaire 1', name_2: str = 'Partenaire 2',
    language: str = 'fr',
) -> Optional[Dict]:
    return await _call('/charts/composite', {
        'subject1': make_subject(name_1, birth_data_1),
        'subject2': make_subject(name_2, birth_data_2),
        'options': {'language': language, 'house_system': 'P'},
    })


# ════════ INSIGHTS RELATIONNELS ════════

async def relationship_compatibility_score(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    language: str = 'fr',
) -> Optional[Dict]:
    """Score de compatibilite (0-100) + interpretation."""
    return await _call('/insights/relationship/compatibility-score', {
        'subjects': [
            make_subject(name_1, birth_data_1),
            make_subject(name_2, birth_data_2),
        ],
        'options': {'language': language},
    })


async def relationship_compatibility(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    language: str = 'fr',
) -> Optional[Dict]:
    """Analyse complete de compatibilite (forces, defis, conseils)."""
    return await _call('/insights/relationship/compatibility', {
        'subjects': [
            make_subject(name_1, birth_data_1),
            make_subject(name_2, birth_data_2),
        ],
        'options': {'language': language},
    })


# ════════ RAPPORTS TEXTUELS ════════

async def natal_report(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Rapport natal textuel (interpretation complete)."""
    return await _call('/analysis/natal-report', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


async def natal_report_pdf(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr', chart_theme: str = 'dark') -> Optional[bytes]:
    """Genere un PDF complet du theme natal (chart wheel + interpretations).
    Renvoie les bytes du PDF ou None si echec."""
    payload = {
        'subject': make_subject(name, birth_data),
        'tradition': 'psychological',
        'include_chart_svg': True,
        'chart_theme': chart_theme,
        'pdf_options': {
            'language': language,
            'include_cover_page': True,
            'include_table_of_contents': True,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(
                f'{BASE_URL}/pdf/natal-report',
                headers={
                    'Authorization': f'Bearer {_api_key()}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/pdf',
                },
                json=payload,
            )
            if r.status_code != 200:
                print(f'[astrology_io] /pdf/natal-report -> {r.status_code} : {r.text[:300]}')
                return None
            ctype = r.headers.get('content-type', '')
            if 'application/pdf' in ctype:
                return r.content
            # Some APIs return base64 in JSON
            try:
                data = r.json()
                import base64
                b64 = data.get('pdf') or data.get('data') or ''
                if b64:
                    return base64.b64decode(b64)
            except Exception:
                pass
            return None
    except Exception as e:
        print(f'[astrology_io] /pdf/natal-report EXCEPTION : {e}')
        return None


async def synastry_report(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Partenaire 1', name_2: str = 'Partenaire 2',
    language: str = 'fr',
) -> Optional[Dict]:
    return await _call('/analysis/synastry-report', {
        'subject1': make_subject(name_1, birth_data_1),
        'subject2': make_subject(name_2, birth_data_2),
        'options': {'language': language, 'house_system': 'P'},
    })


# ════════ SOLAR RETURN (rapport annuel d'anniversaire) ════════

async def solar_return(birth_data: Dict[str, Any], return_year: int, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    return await _call('/charts/solar-return', {
        'subject': make_subject(name, birth_data),
        'return_year': int(return_year),
        'options': {'language': language, 'house_system': 'P'},
    })


async def solar_return_report(birth_data: Dict[str, Any], return_year: int, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Rapport textuel complet de revolution solaire (themes de l'annee a venir)."""
    return await _call('/analysis/solar-return-report', {
        'subject': make_subject(name, birth_data),
        'return_year': int(return_year),
        'options': {'language': language, 'house_system': 'P'},
        'include_life_areas': True,
    })


# ════════ TRANSITS DU JOUR ════════

def _today_dt_payload() -> Dict[str, Any]:
    """Construit un DateTimeLocation pour le moment present (UTC noon Paris)."""
    now = datetime.now(timezone.utc)
    return {
        'year': now.year, 'month': now.month, 'day': now.day,
        'hour': 12, 'minute': 0,
        'latitude': 48.8566, 'longitude': 2.3522,
        'timezone': 'Europe/Paris',
    }


async def transits_today(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr', orb: float = 2.0) -> Optional[Dict]:
    """Transits planetaires affectant le theme natal aujourd'hui."""
    return await _call('/charts/transit', {
        'subject': make_subject(name, birth_data),
        'transit_time': {'datetime': _today_dt_payload()},
        'orb': float(orb),
        'options': {'language': language, 'house_system': 'P'},
    })


async def transit_report_today(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr', orb: float = 2.0) -> Optional[Dict]:
    """Rapport textuel des transits du jour (interpretations)."""
    today = datetime.now(timezone.utc)
    return await _call('/analysis/natal-transit-report', {
        'subject': make_subject(name, birth_data),
        'transit_time': {
            'date_range': {
                'start_date': {'year': today.year, 'month': today.month, 'day': today.day},
                'end_date': {'year': today.year, 'month': today.month, 'day': today.day},
            },
        },
        'orb': float(orb),
        'report_options': {'language': language},
    })


# ════════ LOVE LANGUAGES ASTROLOGIQUES ════════

async def love_languages(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Langages de l'amour astrologiques (besoin emotionnel principal selon Venus/Mars/Lune)."""
    return await _call('/insights/relationship/love-languages', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })


# ════════ AI CHAT ASTROLOGIQUE (avec contexte natal embedded) ════════

async def astro_chat(
    messages: list,
    birth_data: Optional[Dict[str, Any]] = None,
    name: str = 'Voyageur',
    session_id: Optional[str] = None,
    language: str = 'fr',
    temperature: float = 0.7,
    max_tokens: int = 600,
) -> Optional[Dict]:
    """Chat AI astrologique avec le theme natal embarque (acces direct par l'IA aux positions)."""
    payload: Dict[str, Any] = {
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'astrology': {
            'enabled_tools': ['positions', 'aspects', 'transits', 'natal'],
            'defaults': {'language': language},
        },
    }
    if birth_data:
        payload['astrology']['subjects'] = [make_subject(name, birth_data)]
    if session_id:
        payload['astrology']['session_id'] = session_id
    return await _call('/chat/completions', payload)


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
        cached = sb.table('energy_cache').select('*').eq('day', today).eq('user_id', key).maybe_single().execute()
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
            'day': today, 'user_id': key, 'energy_data': fresh,
        }).execute()
    except Exception as e:
        print(f'[astrology_io.cache] write error: {e}')

    return fresh
