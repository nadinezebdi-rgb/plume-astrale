"""natal_chart_extract — Aspects et maisons du thème natal, extraits des données réelles.

Avant ce module, les aspects et les maisons étaient lus uniquement dans le
`natal_report` (qui ne les contient pas) : le prompt GPT recevait « aucun aspect
fourni » / « maisons non fournies » et le livre le disait noir sur blanc
(« Faute d'aspects exacts fournis… »), avec des pages de maisons sans signe
ni planètes.

Ordre de priorité :
  1. aspects / cuspides renvoyés par /charts/natal (`chart_data`) ;
  2. aspects du natal_report ;
  3. calcul local à partir des longitudes écliptiques (déterministe).
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional

from services import astrology_io_service as aio

PLANETS_FR = {
    'sun': 'Soleil', 'moon': 'Lune', 'mercury': 'Mercure', 'venus': 'Vénus',
    'mars': 'Mars', 'jupiter': 'Jupiter', 'saturn': 'Saturne', 'uranus': 'Uranus',
    'neptune': 'Neptune', 'pluto': 'Pluton', 'ascendant': 'Ascendant', 'asc': 'Ascendant',
}
_SIGN_ORDER = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
               'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# (angle, nom FR, orbe max, nature)
_ASPECTS = [
    (0, 'conjonction', 8, 'neutre'),
    (60, 'sextile', 4, 'harmonieux'),
    (90, 'carré', 7, 'tension'),
    (120, 'trigone', 7, 'harmonieux'),
    (180, 'opposition', 8, 'tension'),
]
_NATURE = {name: nature for _, name, _, nature in _ASPECTS}
_NATURE['quinconce'] = 'tension'

_HOUSE_WORDS = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6,
    'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10, 'eleventh': 11, 'twelfth': 12,
}


def _planet_fr(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        value = value.get('name') or value.get('point')
    if not value:
        return None
    return PLANETS_FR.get(str(value).strip().lower().replace(' ', '_'))


def _aspect_fr(value: Any) -> Optional[str]:
    v = str(value or '').strip().lower()
    if v.startswith('conj'):
        return 'conjonction'
    if v.startswith('opp'):
        return 'opposition'
    if v.startswith('tri'):
        return 'trigone'
    if v.startswith('squ') or v.startswith('car'):
        return 'carré'
    if v.startswith('sext'):
        return 'sextile'
    if v.startswith('quinc') or v.startswith('inconj'):
        return 'quinconce'
    return None


def _orb(value: Any) -> Optional[float]:
    try:
        return round(abs(float(value)), 1)
    except (TypeError, ValueError):
        return None


def _longitude(point: Dict[str, Any]) -> Optional[float]:
    lon = point.get('absolute_longitude')
    try:
        if lon is not None:
            return float(lon) % 360
    except (TypeError, ValueError):
        pass
    sign = point.get('sign')
    deg = point.get('degree')
    try:
        deg = float(deg)
    except (TypeError, ValueError):
        return None
    if sign in _SIGN_ORDER and 0 <= deg < 30:
        return _SIGN_ORDER.index(sign) * 30 + deg
    if deg >= 30:
        return deg % 360
    return None


def _normalize_api_aspects(raw: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(raw, list):
        return out
    for a in raw:
        if not isinstance(a, dict):
            continue
        p1 = _planet_fr(a.get('planet1') or a.get('p1') or a.get('body1') or a.get('point1'))
        p2 = _planet_fr(a.get('planet2') or a.get('p2') or a.get('body2') or a.get('point2'))
        kind = _aspect_fr(a.get('type') or a.get('aspect') or a.get('aspect_type') or a.get('name'))
        if not (p1 and p2 and kind) or p1 == p2:
            continue
        out.append({
            'planet1': p1, 'planet2': p2, 'type': kind,
            'orb': _orb(a.get('orb') if a.get('orb') is not None else a.get('orb_deg')),
            'nature': _NATURE.get(kind, 'neutre'),
        })
    return out


def compute_aspects(planets_dict: Dict[str, Dict[str, Any]], include_ascendant: bool = False) -> List[Dict[str, Any]]:
    """Aspects majeurs calculés depuis les longitudes (orbes classiques)."""
    points = []
    for key, point in (planets_dict or {}).items():
        fr = PLANETS_FR.get(key)
        if not fr or (fr == 'Ascendant' and not include_ascendant):
            continue
        lon = _longitude(point)
        if lon is not None:
            points.append((fr, lon))
    out: List[Dict[str, Any]] = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            (n1, l1), (n2, l2) = points[i], points[j]
            diff = abs(l1 - l2) % 360
            diff = 360 - diff if diff > 180 else diff
            for angle, name, max_orb, nature in _ASPECTS:
                orb = abs(diff - angle)
                if orb <= max_orb:
                    out.append({'planet1': n1, 'planet2': n2, 'type': name,
                                'orb': round(orb, 1), 'nature': nature})
                    break
    return out


def extract_aspects(chart: Optional[dict], report: Optional[dict],
                    planets_dict: Dict[str, Dict[str, Any]],
                    include_ascendant: bool = False, limit: int = 20) -> List[Dict[str, Any]]:
    """Aspects triés par orbe croissant (les plus serrés d'abord)."""
    candidates: List[Any] = []
    if isinstance(chart, dict):
        cd = chart.get('chart_data')
        if isinstance(cd, dict):
            candidates.append(cd.get('aspects'))
        candidates.append(chart.get('aspects'))
    if isinstance(report, dict):
        candidates.append(report.get('aspects'))
        data = report.get('data')
        if isinstance(data, dict):
            candidates.append(data.get('aspects'))

    aspects: List[Dict[str, Any]] = []
    for raw in candidates:
        aspects = _normalize_api_aspects(raw)
        if aspects:
            break
    if not aspects:
        aspects = compute_aspects(planets_dict, include_ascendant=include_ascendant)
    if not include_ascendant:
        aspects = [a for a in aspects if 'Ascendant' not in (a['planet1'], a['planet2'])]
    aspects.sort(key=lambda a: a['orb'] if a['orb'] is not None else 99)
    return aspects[:limit]


def _house_number(value: Any) -> Optional[int]:
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v.isdigit() and 1 <= int(v) <= 12:
            return int(v)
        m = re.match(r'([a-z]+)_?house', v.replace(' ', '_'))
        if m and m.group(1) in _HOUSE_WORDS:
            return _HOUSE_WORDS[m.group(1)]
    return None


def extract_houses(chart: Optional[dict], planets_dict: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """12 maisons : signe de la cuspide + planètes qui y tombent."""
    cd = (chart or {}).get('chart_data') if isinstance(chart, dict) else None
    cusps = (cd or {}).get('house_cusps') or []
    houses: Dict[int, Dict[str, Any]] = {}
    for c in cusps:
        if not isinstance(c, dict):
            continue
        num = _house_number(c.get('house') if c.get('house') is not None else c.get('index'))
        if not num:
            continue
        houses[num] = {
            'num': num,
            'sign': aio.sign_to_fr(aio.expand_sign(c.get('sign') or '')),
            'planets_in_house': [],
            '_lon': _longitude({'absolute_longitude': c.get('absolute_longitude'),
                                'sign': aio.expand_sign(c.get('sign') or ''),
                                'degree': c.get('degree')}),
        }
    if len(houses) < 12:
        return []

    bounds = [houses[n]['_lon'] for n in range(1, 13)]
    can_place_by_longitude = all(b is not None for b in bounds)
    for key, point in (planets_dict or {}).items():
        fr = PLANETS_FR.get(key)
        if not fr or fr == 'Ascendant':
            continue
        num = None
        lon = _longitude(point)
        if can_place_by_longitude and lon is not None:
            for n in range(1, 13):
                start, end = bounds[n - 1], bounds[n % 12]
                span = (end - start) % 360
                if span and (lon - start) % 360 < span:
                    num = n
                    break
        if num is None:
            num = _house_number(point.get('house'))
        if num:
            houses[num]['planets_in_house'].append(fr)

    return [{k: v for k, v in houses[n].items() if k != '_lon'} for n in range(1, 13)]
