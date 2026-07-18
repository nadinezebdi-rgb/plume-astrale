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

_SIGN_EN_TO_FR = {
    'Aries': 'Bélier', 'Taurus': 'Taureau', 'Gemini': 'Gémeaux', 'Cancer': 'Cancer',
    'Leo': 'Lion', 'Virgo': 'Vierge', 'Libra': 'Balance', 'Scorpio': 'Scorpion',
    'Sagittarius': 'Sagittaire', 'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons',
}

# v3 renvoie les signes en abrege : "Tau", "Vir", "Cap", etc.
_SIGN_ABBR_TO_EN = {
    'Ari': 'Aries', 'Tau': 'Taurus', 'Gem': 'Gemini', 'Can': 'Cancer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Scorpio',
    'Sag': 'Sagittarius', 'Cap': 'Capricorn', 'Aqu': 'Aquarius', 'Pis': 'Pisces',
}


def expand_sign(sign: str) -> str:
    """v3 renvoie 'Tau'/'Vir' -> renvoie 'Taurus'/'Virgo' (nom EN complet)."""
    if not sign:
        return ''
    s = str(sign).strip().title()
    return _SIGN_ABBR_TO_EN.get(s, s)


def extract_planets(data: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """A partir d'une reponse v3 (/charts/natal, /data/positions, etc.), extrait un dict
    normalise {name.lower(): {name, sign (EN complet), house, degree}}.

    Gere les 2 formats :
    - /data/positions -> {"positions": [...]}
    - /charts/natal   -> {"chart_data": {"planetary_positions": [...], "house_cusps": [...]}}
    """
    if not data or not isinstance(data, dict):
        return {}
    pts: List[Dict[str, Any]] = []
    chart = data.get('chart_data') or {}
    if isinstance(chart, dict):
        pts = chart.get('planetary_positions') or chart.get('positions') or chart.get('points') or []
    if not pts:
        pts = data.get('positions') or data.get('planetary_positions') or data.get('points') or data.get('planets') or []
    if not isinstance(pts, list):
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for p in pts:
        if not isinstance(p, dict):
            continue
        nm = (p.get('name') or p.get('point') or '').strip()
        if not nm:
            continue
        sign = expand_sign(p.get('sign') or (p.get('position') or {}).get('sign') or '')
        house = p.get('house') if p.get('house') is not None else (p.get('position') or {}).get('house')
        out[nm.lower()] = {'name': nm, 'sign': sign, 'house': house, 'degree': p.get('degree')}
    return out


def extract_ascendant_sign_en(data: Optional[Dict[str, Any]]) -> Optional[str]:
    """Renvoie le signe de l'ascendant (EN complet, ex: 'Virgo') depuis une reponse v3.
    Cherche dans planetary_positions.Ascendant puis dans house_cusps[house=1]."""
    if not data or not isinstance(data, dict):
        return None
    planets = extract_planets(data)
    asc = planets.get('ascendant') or planets.get('asc')
    if asc and asc.get('sign'):
        return asc['sign']
    chart = data.get('chart_data') or data
    houses = chart.get('house_cusps') or chart.get('houses') or []
    if isinstance(houses, list):
        for h in houses:
            if isinstance(h, dict) and (h.get('house') == 1 or h.get('index') == 1):
                return expand_sign(h.get('sign'))
    return None


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


# ── Alerte email admin si la cle API est rejetee (401) — max 1 / 6h ──
_last_key_alert_ts = 0.0


async def _alert_invalid_key(path: str, detail: str) -> None:
    global _last_key_alert_ts
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).timestamp()
    if now - _last_key_alert_ts < 6 * 3600:
        return
    _last_key_alert_ts = now
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    to = os.environ.get('ADMIN_ALERT_EMAIL', '').strip()
    if not resend_key or not to:
        print('[astrology_io] 401 detecte mais RESEND_API_KEY/ADMIN_ALERT_EMAIL manquant — alerte non envoyee')
        return
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={
                    'from': os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>'),
                    'to': [to],
                    'subject': '🚨 ALERTE Plume Astrale — Clé astrology-api.io invalide (401)',
                    'html': (
                        "<div style='font-family:sans-serif;max-width:560px;margin:0 auto;'>"
                        "<h2 style='color:#B91C1C;'>🚨 La clé astrology-api.io est rejetée</h2>"
                        "<p>Le backend reçoit <b>401 Invalid credentials</b> : la clé est expirée, révoquée "
                        "ou le quota est dépassé. Les produits astrologiques (chat, PDF, rapports) sont "
                        "actuellement <b>en panne</b> pour les clients.</p>"
                        f"<p><b>Endpoint touché :</b> <code>{path}</code><br>"
                        f"<b>Réponse API :</b> <code>{detail}</code></p>"
                        "<p><b>Action :</b> vérifie ton compte sur "
                        "<a href='https://dashboard.astrology-api.io'>dashboard.astrology-api.io</a>, "
                        "génère une nouvelle clé si besoin, puis mets à jour la variable "
                        "<code>ASTROLOGY_API_IO_KEY</code> sur Railway et redéploie.</p>"
                        "<p style='color:#888;font-size:12px;'>Anti-spam : maximum 1 alerte toutes les 6 heures.</p>"
                        "</div>"
                    ),
                },
            )
            if r.status_code < 400:
                print(f'[astrology_io] ALERTE 401 envoyee a {to}')
            else:
                print(f'[astrology_io] alert email error {r.status_code}: {r.text[:200]}')
    except Exception as e:
        print(f'[astrology_io] alert email failed: {e}')


async def _call(path: str, payload: Dict[str, Any], timeout: float = 30.0) -> Optional[Dict[str, Any]]:
    """POST helper. Retourne data ou None si echec. Logs minimal."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
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
                if r.status_code == 401:
                    import asyncio
                    try:
                        asyncio.create_task(_alert_invalid_key(path, r.text[:200]))
                    except Exception:
                        pass
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


async def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """GET helper. Retourne data ou None si echec."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f'{BASE_URL}{path}',
                headers={
                    'Authorization': f'Bearer {_api_key()}',
                    'Accept': 'application/json',
                },
                params=params or {},
            )
            if r.status_code != 200:
                print(f'[astrology_io] GET {path} -> {r.status_code} : {r.text[:200]}')
                return None
            data = r.json()
            if isinstance(data, dict) and data.get('success') is False:
                return None
            if isinstance(data, dict) and 'data' in data and data.get('success'):
                return data['data']
            return data
    except Exception as e:
        print(f'[astrology_io] GET {path} EXCEPTION : {e}')
        return None



async def geocode_and_timezone(city: str, country_code: str,
                               year: int, month: int, day: int,
                               hour: int = 12, minute: int = 0) -> Optional[Dict[str, Any]]:
    """Geocode une ville + resout le fuseau via AstroAPI (/timezone).

    Retourne {latitude, longitude, tzone, tz_name, tz_reliable} ou None.
    Reutilise _call() qui deballe deja le wrapper {success, data}.
    """
    data = await _call('/timezone', {
        'day': day, 'month': month, 'year': year,
        'hour': hour, 'minute': minute,
        'city': city, 'country_code': country_code,
    })
    if not isinstance(data, dict):
        return None
    loc = data.get('resolved_location') or {}
    if loc.get('latitude') is None:
        return None
    return {
        'latitude': loc.get('latitude'),
        'longitude': loc.get('longitude'),
        'tzone': data.get('utc_offset_hours'),
        'tz_name': data.get('timezone'),
        'tz_reliable': data.get('is_historical_accurate', True),
    }


async def search_cities(query: str, country_code: Optional[str] = None,
                        limit: int = 10) -> list:
    """Autocompletion de villes (formulaire natal) via /glossary/cities.

    Retourne une liste d'items [{name, country_code, latitude, longitude, ...}].
    """
    params: Dict[str, Any] = {'search': query, 'limit': limit}
    if country_code:
        params['country_code'] = country_code
    data = await _get('/glossary/cities', params)
    if not isinstance(data, dict):
        return []
    return data.get('items') or []


async def _call_first(paths: list[str], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Try multiple API paths in order and return the first successful response."""
    for p in paths:
        data = await _call(p, payload)
        if data:
            return data
    return None


_CHINESE_ANIMALS = ["rat", "ox", "tiger", "rabbit", "dragon", "snake", "horse", "goat", "monkey", "rooster", "dog", "pig"]

def chinese_animal_for_year(year: int) -> str:
    """Animal du zodiaque chinois pour une annee."""
    try:
        return _CHINESE_ANIMALS[(int(year) - 4) % 12]
    except Exception:
        return "rat"


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


# ════════ ARCHETYPES JUNGIENS ════════

async def archetypes(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Profil archetypal (dominant + shadow + spectrum) base sur le theme natal.
    Renvoie profile_name, balance_type, dominant_archetypes[], shadow_archetype, spectrum{}."""
    return await _call('/analysis/archetypes', {
        'subject': make_subject(name, birth_data),
        'language': language,
    })


# ════════ KABBALE — Arbre de Vie ════════

async def tree_of_life_chart(
    birth_data: Dict[str, Any],
    system: str = 'modern_halevi',
    tradition: str = 'universal',
    language: str = 'fr',
) -> Optional[Dict]:
    """Mapping du theme natal sur les 10 Sephiroth (+ Da'at) et les 22 chemins.
    Retourne : sephiroth (10 dict), paths (22 dict), pillar_balance, dominant_sephirah,
    spiritual_focus, synthesis. Systemes disponibles : modern_halevi | classical |
    golden_dawn | golden_dawn_extended. Tradition : universal | psychological | classical."""
    return await _call('/kabbalah/tree-of-life-chart', {
        'birth_data': birth_data,
        'system': system,
        'tradition': tradition,
        'include_daat': True,
        'include_paths': True,
        'include_interpretations': True,
        'language': language,
    })


# ════════ KARMA — analyse karmique complete ════════

async def karmic_analysis(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Analyse karmique complete (80+ sections FR natif) : Noeuds Lunaires, Saturne,
    Chiron, Pluto, planetes retrogrades, karma des generations."""
    return await _call('/analysis/karmic', {
        'subject': make_subject(name, birth_data),
        'language': language,
    })


# ════════ AI CHAT ASTROLOGIQUE (avec contexte natal embedded) ════════

async def astro_chat(
    messages: list,
    birth_data: Optional[Dict[str, Any]] = None,
    name: str = 'Voyageur',
    session_id: Optional[str] = None,
    language: str = 'fr',
    temperature: float = 0.8,
    max_tokens: int = 1200,
    disable_tools: bool = False,
) -> Optional[Dict]:
    """Chat AI astrologique. Par defaut on desactive les enabled_tools cote API pour
    eviter les fuites d'appels d'outils en texte brut ; le contexte natal est
    injecte en amont dans le system prompt par l'appelant (voir routes/astrology_v3.py).
    """
    payload: Dict[str, Any] = {
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    if not disable_tools:
        payload['astrology'] = {
            'enabled_tools': ['positions', 'aspects', 'transits', 'natal'],
            'defaults': {'language': language},
        }
    if birth_data:
        payload.setdefault('astrology', {})['subjects'] = [make_subject(name, birth_data)]
    if session_id:
        payload.setdefault('astrology', {})['session_id'] = session_id
    return await _call('/chat/completions', payload, timeout=60.0)


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


# ════════════════════════════════════════════════════════════════════
# EXTENSIONS — TOUS LES ENDPOINTS MANQUANTS (upgrade Ultra/Business)
# ════════════════════════════════════════════════════════════════════

# ════════ ASTROLOGIE VÉDIQUE ════════

async def vedic_natal(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Thème natal védique (Kundli) avec Shadbala, Dasha, Ayanamsa."""
    return await _call('/vedic/birth-details', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'ayanamsa': 'lahiri'},
    })

async def vedic_nakshatra(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Nakshatra de naissance (mansion lunaire védique)."""
    return await _call('/vedic/nakshatra-predictions', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def vedic_dasha(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Timeline Vimshottari Dasha complète (10 Mahadashas + sous-périodes)."""
    return await _call('/vedic/vimshottari-dasha', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def vedic_navamsa(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Chart Navamsa (D9) — mariage, âme, partenaire idéal."""
    return await _call('/vedic/divisional-chart', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'ayanamsa': 'lahiri'},
    })

async def vedic_divisional_charts(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """16 charts divisionnels (D1-D60) en un seul appel."""
    return await _call('/vedic/divisional-chart', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'ayanamsa': 'lahiri'},
    })


# ════════ ASTROLOGIE CHINOISE ════════

async def chinese_zodiac(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Animal du zodiaque chinois + caractéristiques + compatibilités."""
    year = (birth_data or {}).get('year')
    if not year:
        return None
    animal = chinese_animal_for_year(year)
    return await _get(f'/chinese/zodiac/{animal}', {
        'year': int(year),
        'language': language,
    })

async def chinese_horoscope(birth_data: Dict[str, Any], name: str = 'Voyageur', period: str = 'daily', language: str = 'fr') -> Optional[Dict]:
    """Horoscope chinois IA (daily/weekly/monthly/yearly)."""
    return await _call('/chinese/horoscope', {
        'subject': make_subject(name, birth_data),
        'period': period,
        'options': {'language': language},
    })

async def chinese_bazi(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """BaZi (4 piliers du destin) — analyse complète Wu Xing."""
    return await _call('/chinese/bazi', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def chinese_compatibility(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    language: str = 'fr',
) -> Optional[Dict]:
    """Compatibilité zodiaque chinois entre 2 personnes."""
    return await _call('/chinese/compatibility', {
        'subjects': [make_subject(name_1, birth_data_1), make_subject(name_2, birth_data_2)],
        'options': {'language': language},
    })

async def chinese_elements(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Wu Xing (5 éléments) + analyse MTC."""
    year = (birth_data or {}).get('year')
    if not year:
        return None
    return await _get(f'/chinese/elements/balance/{int(year)}', {
        'include_predictions': True,
        'language': language,
    })

async def zi_wei_dou_shu(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Purple Star Astrology (Zi Wei Dou Shu) — 108 étoiles."""
    payload = {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    }
    return await _call_first(['/chinese/zi-wei', '/chinese/zi-wei-dou-shu'], payload)

async def feng_shui(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Feng Shui — numéro Kua, étoiles volantes, directions favorables."""
    payload = {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    }
    return await _call_first(['/chinese/feng-shui', '/chinese/fengshui'], payload)


# ════════ PRÉDICTIONS AVANCÉES ════════

async def lunar_return(birth_data: Dict[str, Any], return_month: Optional[int] = None, return_year: Optional[int] = None, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Retour Lunaire mensuel."""
    now = datetime.now(timezone.utc)
    target_year = int(return_year or now.year)
    target_month = int(return_month or now.month)
    payload = {
        'subject': make_subject(name, birth_data),
        'return_date': f'{target_year:04d}-{target_month:02d}-01',
        'options': {'language': language, 'house_system': 'P'},
    }
    return await _call('/charts/lunar-return', payload)

async def venus_return(birth_data: Dict[str, Any], return_year: Optional[int] = None, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Retour de Vénus (amour & finances)."""
    now = datetime.now(timezone.utc)
    target_year = int(return_year or now.year)
    month = int((birth_data or {}).get('month') or now.month)
    day = int((birth_data or {}).get('day') or now.day)
    return await _call('/charts/venus-return', {
        'subject': make_subject(name, birth_data),
        'return_date': f'{target_year:04d}-{month:02d}-{day:02d}',
        'options': {'language': language, 'house_system': 'P'},
    })

async def secondary_progressions(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Progressions secondaires (méthode jour-pour-année)."""
    now = datetime.now(timezone.utc)
    return await _call('/charts/progressions', {
        'subject': make_subject(name, birth_data),
        'target_date': f'{now.year:04d}-{now.month:02d}-{now.day:02d}',
        'options': {'language': language, 'house_system': 'P'},
    })

async def profections(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Profections hellénistiques — seigneur de l'année."""
    payload = {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    }
    return await _call_first(['/timing/annual-profections', '/timing/profections'], payload)

async def firdaria(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Firdaria (time-lord persan) — cycle de 75 ans."""
    _ = language
    return await _call('/timing/firdaria', {
        'subject': make_subject(name, birth_data),
    })

async def zodiacal_releasing(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Zodiacal Releasing (Vettius Valens) — périodes L1/L2/L3."""
    return await _call('/timing/zodiacal-releasing', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def solar_arc_planets(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Directions solaires (Solar Arc) — technique prédictive principale."""
    payload = {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    }
    return await _call_first(['/charts/solar-arc-directions', '/charts/solar-arc'], payload)


# ════════ TECHNIQUES TRADITIONNELLES ════════

async def arabic_parts(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """97+ Parts arabes (Part de Fortune, Part d'Esprit, etc.)."""
    return await _call('/traditional/lots', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language, 'house_system': 'P'},
    })

async def fixed_stars(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """50+ Étoiles fixes avec influences sur les planètes natales."""
    return await _call('/fixed-stars/positions', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def dignities(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Dignités planétaires essentielles (domicile, exaltation, chute, exil)."""
    return await _call('/traditional/dignities', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def sabian_symbols(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """360 Symboles Sabians — image symbolique pour chaque degré."""
    return await _call('/data/sabian-symbols', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def planetary_hours(language: str = 'fr') -> Optional[Dict]:
    """Heures planétaires du jour (timing traditionnel)."""
    now = datetime.now(timezone.utc)
    return await _call('/electional/planetary-hours', {
        'datetime_location': {
            'year': now.year, 'month': now.month, 'day': now.day,
            'hour': now.hour, 'minute': now.minute,
            'latitude': 48.8566, 'longitude': 2.3522, 'timezone': 'Europe/Paris',
        },
        'options': {'language': language},
    })

async def midpoints(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Points médians (midpoints) + cosmobiologie."""
    payload = {'subject': make_subject(name, birth_data), 'options': {'language': language}}
    return await _call_first(['/data/midpoints', '/traditional/midpoints'], payload)

async def asteroids(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Astéroïdes (Chiron, Cérès, Pallas, Junon, Vesta + archétypes féminins)."""
    payload = {'subject': make_subject(name, birth_data), 'options': {'language': language}}
    return await _call_first(['/data/asteroids', '/traditional/asteroids'], payload)

async def eclipse_data(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Éclipses solaires et lunaires proches + impact sur le thème natal."""
    return await _call('/eclipses/natal-check', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def draconic_chart(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Chart draconique — thème de l'âme / karmique."""
    return await _call('/charts/draconic', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def human_design(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Human Design — type, profil, centres, canaux, portes."""
    return await _call('/human-design/bodygraph', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def kabbalah(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Kabbale — Sephiroth, 72 anges, gématrie, corrections de l'âme."""
    return await _call('/kabbalah/tree-of-life-chart', {
        'birth_data': birth_data,
        'name': name,
        'options': {'language': language},
    })


# ════════ TAROT AVANCÉ ════════

async def tarot_birth(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Tarot de naissance — cartes personnelles basées sur le thème natal."""
    return await _call('/tarot/birth', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def tarot_houses(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Tirage Tarot & 12 maisons astrologiques."""
    return await _call('/tarot/houses', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def tarot_transit(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Tirage Tarot synchronisé avec les transits planétaires du jour."""
    return await _call('/tarot/transit', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def tarot_synastry(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    language: str = 'fr',
) -> Optional[Dict]:
    """Tarot synastronie — compatibilité entre 2 personnes par les cartes."""
    return await _call('/tarot/synastry', {
        'subjects': [make_subject(name_1, birth_data_1), make_subject(name_2, birth_data_2)],
        'options': {'language': language},
    })

async def tarot_spread(spread_type: str = 'celtic_cross', question: Optional[str] = None, language: str = 'fr') -> Optional[Dict]:
    """15+ tirages professionnels (celtic_cross, three_card, horseshoe, etc.)."""
    payload: Dict[str, Any] = {
        'spread_type': spread_type,
        'options': {'language': language},
    }
    if question:
        payload['question'] = question
    return await _call('/tarot/spread', payload)

async def tarot_tree_of_life(language: str = 'fr') -> Optional[Dict]:
    """Tirage Tarot sur l'Arbre de Vie Kabbalistique (10 Sephiroth)."""
    return await _call('/tarot/tree-of-life', {'options': {'language': language}})

async def tarot_quintessence(language: str = 'fr') -> Optional[Dict]:
    """Quintessence tarot — carte de synthèse (5ème élément)."""
    return await _call('/tarot/quintessence', {'options': {'language': language}})


# ════════ NUMÉROLOGIE AVANCÉE ════════

async def numerology_name(name: str, language: str = 'fr') -> Optional[Dict]:
    """Analyse numérologique du prénom/nom (expression, âme, personnalité)."""
    return await _call('/numerology/name', {'name': name, 'options': {'language': language}})

async def numerology_core_numbers(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Nombres fondamentaux (v3 /numerology/core-numbers) : life_path, destiny,
    soul_urge, personality, birthday, personal_year, maturity... avec interpretations FR."""
    return await _call('/numerology/core-numbers', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def numerology_compatibility(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    language: str = 'fr',
) -> Optional[Dict]:
    """Compatibilité numérologique multi-dimensionnelle."""
    return await _call('/numerology/compatibility', {
        'subjects': [make_subject(name_1, birth_data_1), make_subject(name_2, birth_data_2)],
        'options': {'language': language},
    })

async def numerology_personal_year(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Année personnelle + cycles de vie (thèmes pour chaque année)."""
    now = datetime.now(timezone.utc)
    return await _call('/numerology/personal-year', {
        'subject': make_subject(name, birth_data),
        'year': now.year,
        'options': {'language': language},
    })

async def numerology_forecast(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Prévision numérologique IA — timing des cycles de vie."""
    return await _call('/numerology/forecast', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def numerology_lo_shu(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Carré Magique Lo Shu — numérologie chinoise + Feng Shui."""
    return await _call('/numerology/lo-shu', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def kabbalah_numerology(birth_data: Dict[str, Any], name_str: str = 'Voyageur', full_name: Optional[str] = None, language: str = 'fr') -> Optional[Dict]:
    """Numérologie kabbalistique (Gématrie hébraïque + 72 anges + Sephiroth)."""
    payload: Dict[str, Any] = {
        'subject': make_subject(name_str, birth_data),
        'options': {'language': language},
    }
    if full_name:
        payload['full_name'] = full_name
    return await _call('/numerology/kabbalah', payload)


# ════════ INSIGHTS SPÉCIALISÉS ════════

async def biorhythms(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Biorythmes (physique, émotionnel, intellectuel, intuitif)."""
    now = datetime.now(timezone.utc)
    return await _call('/insights/wellness/biorhythms', {
        'subject': make_subject(name, birth_data),
        'target_date': {'year': now.year, 'month': now.month, 'day': now.day},
        'options': {'language': language},
    })

async def moon_wellness(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Bien-être selon les cycles lunaires — recommendations personnalisées."""
    return await _call('/insights/moon-wellness', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def body_health(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Santé & corps astral — influences planétaires sur les systèmes corporels."""
    return await _call('/insights/body-health', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def career_astrology(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Astrologie de carrière — aptitudes, timing professionnel, vocation."""
    return await _call('/insights/career', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def archetypes_jungian(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """12 archétypes Jungiens depuis le thème natal (Héros, Amant, Sage, etc.)."""
    return await _call('/insights/archetypes', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def personality_analysis(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Analyse de personnalité astrologique (traits, comportements, psychologie)."""
    return await _call('/analysis/psychological', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def energy_cycles(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Cycles d'énergie personnelle — optimisation workout/méditation/productivité."""
    return await _call('/insights/energy-cycles', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })


# ════════ ASTROCARTOGRAPHIE (Ultra+ requis) ════════

async def astrocartography(birth_data: Dict[str, Any], name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Astrocartographie — zones de puissance planétaire dans le monde."""
    return await _call('/astrocartography/map', {
        'subject': make_subject(name, birth_data),
        'options': {'language': language},
    })

async def astrocartography_city(birth_data: Dict[str, Any], city: str, country_code: str = 'FR', name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Analyse astrocartographique pour une ville spécifique."""
    return await _call('/astrocartography/city', {
        'subject': make_subject(name, birth_data),
        'city': city,
        'country_code': country_code.upper(),
        'options': {'language': language},
    })

async def relocation_scores(birth_data: Dict[str, Any], cities: list, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Scores de relocation (carrière, amour, lifestyle) pour plusieurs villes."""
    return await _call('/astrocartography/relocation-scores', {
        'subject': make_subject(name, birth_data),
        'cities': cities,
        'options': {'language': language},
    })


# ════════ ELECTIONAL ASTROLOGY (Ultra+ requis) ════════

async def electional_evaluate(
    target_datetime: Dict[str, Any],
    birth_data: Optional[Dict[str, Any]] = None,
    activity: str = 'business',
    language: str = 'fr',
) -> Optional[Dict]:
    """Évalue un moment spécifique pour une activité (business, mariage, voyage…)."""
    payload: Dict[str, Any] = {
        'datetime': target_datetime,
        'activity': activity,
        'options': {'language': language},
    }
    if birth_data:
        payload['subject'] = make_subject('Voyageur', birth_data)
    return await _call('/electional/evaluate', payload)


# ════════ PDF AVANCÉS (Ultra+ + addon requis) ════════

async def pdf_synastry(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Partenaire 1', name_2: str = 'Partenaire 2',
    language: str = 'fr',
) -> Optional[bytes]:
    """Génère un PDF de compatibilité synastronie (requiert Ultra + addon PDF)."""
    payload = {
        'subject1': make_subject(name_1, birth_data_1),
        'subject2': make_subject(name_2, birth_data_2),
        'pdf_options': {'language': language, 'include_cover_page': True},
    }
    try:
        import base64
        async with httpx.AsyncClient(timeout=90.0) as client:
            r = await client.post(
                f'{BASE_URL}/pdf/synastry-report',
                headers={'Authorization': f'Bearer {_api_key()}', 'Content-Type': 'application/json', 'Accept': 'application/pdf'},
                json=payload,
            )
            if r.status_code != 200:
                print(f'[astrology_io] /pdf/synastry-report -> {r.status_code}')
                return None
            if 'application/pdf' in r.headers.get('content-type', ''):
                return r.content
            try:
                data = r.json()
                b64 = data.get('pdf') or data.get('data') or ''
                if b64:
                    import base64
                    return base64.b64decode(b64)
            except Exception:
                pass
            return None
    except Exception as e:
        print(f'[astrology_io] /pdf/synastry EXCEPTION : {e}')
        return None


# ════════════════════════════════════════════════════════════════════
# FONCTIONNALITÉS ULTRA — MANQUANTES
# ════════════════════════════════════════════════════════════════════

# ════════ HORAIRIE (Ultra requis) ════════

async def horary_ask(question: str, language: str = 'fr') -> Optional[Dict]:
    """Horairie IA — pose une question, reçoit une réponse avec analyse traditionnelle."""
    _ = language
    now = datetime.now(timezone.utc)
    return await _call('/horary/analyze', {
        'question': question,
        'category': 'general',
        'question_time': {
            'year': now.year,
            'month': now.month,
            'day': now.day,
            'hour': now.hour,
            'minute': now.minute,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'timezone': 'Europe/Paris',
        },
    })

async def horary_chart(birth_data: Dict[str, Any], question: str, name: str = 'Voyageur', language: str = 'fr') -> Optional[Dict]:
    """Horairie traditionnelle — analyse de la question selon le thème horaire."""
    return await _call('/horary/chart', {
        'subject': make_subject(name, birth_data),
        'question': question,
        'options': {'language': language},
    })


# ════════ RECTIFICATION HEURE DE NAISSANCE (Ultra) ════════

async def birth_time_rectification(
    birth_data: Dict[str, Any],
    life_events: list,
    name: str = 'Voyageur',
    language: str = 'fr',
) -> Optional[Dict]:
    """Rectification automatique de l'heure de naissance à partir d'événements de vie.
    life_events: liste de dicts avec 'date', 'event_type', 'description'.
    """
    return await _call('/rectification/analyze', {
        'subject': make_subject(name, birth_data),
        'life_events': life_events,
        'options': {'language': language},
    })


# ════════ ÉLECTIONAL — RECHERCHE DES MEILLEURS MOMENTS (Ultra) ════════

async def electional_search(
    start_date: Dict[str, Any],
    end_date: Dict[str, Any],
    activity: str = 'business',
    birth_data: Optional[Dict[str, Any]] = None,
    language: str = 'fr',
) -> Optional[Dict]:
    """Recherche des meilleurs moments pour une activité dans une période donnée.
    activity: business | wedding | surgery | travel | investment | launch | meeting
    """
    activity_map = {
        'business': 'business_launch',
        'launch': 'business_launch',
        'meeting': 'contracts',
    }
    normalized_activity = activity_map.get(activity, activity)

    payload: Dict[str, Any] = {
        'date_range': {'start_date': start_date, 'end_date': end_date},
        'activity': normalized_activity,
        'location': {
            'latitude': 48.8566,
            'longitude': 2.3522,
            'timezone': 'Europe/Paris',
        },
        'options': {'language': language},
    }
    if birth_data:
        payload['subject'] = make_subject('Voyageur', birth_data)
    return await _call('/electional/search', payload)


# ════════ RENDU CHART SVG (Ultra — 10 crédits) ════════

async def chart_svg_render(
    birth_data: Dict[str, Any],
    name: str = 'Voyageur',
    chart_type: str = 'natal',
    theme: str = 'dark',
    language: str = 'fr',
) -> Optional[str]:
    """Génère un chart SVG (natal, synastry, transit, composite).
    Retourne le SVG sous forme de string.
    chart_type: natal | synastry | transit | composite
    theme: dark | light | cosmic | astrocom
    """
    result = await _call('/render/chart-svg', {
        'subject': make_subject(name, birth_data),
        'chart_type': chart_type,
        'options': {
            'language': language,
            'theme': theme,
            'house_system': 'P',
            'show_aspects': True,
            'show_arabic_parts': True,
        },
    })
    if not result:
        return None
    # Retourner le SVG string
    return result.get('svg') or result.get('chart_svg') or result.get('data')


async def chart_svg_synastry(
    birth_data_1: Dict[str, Any], birth_data_2: Dict[str, Any],
    name_1: str = 'Personne 1', name_2: str = 'Personne 2',
    theme: str = 'dark', language: str = 'fr',
) -> Optional[str]:
    """Génère un SVG synastronie biwheel."""
    result = await _call('/render/chart-svg', {
        'subject1': make_subject(name_1, birth_data_1),
        'subject2': make_subject(name_2, birth_data_2),
        'chart_type': 'synastry',
        'options': {'language': language, 'theme': theme, 'house_system': 'P'},
    })
    if not result:
        return None
    return result.get('svg') or result.get('chart_svg') or result.get('data')
