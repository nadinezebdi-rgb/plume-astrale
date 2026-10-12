"""Extraction des aspects et maisons depuis les données réelles du thème natal."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from services import astrology_io_service as aio


PLANETS_FR = {
    "sun": "Soleil",
    "moon": "Lune",
    "mercury": "Mercure",
    "venus": "Vénus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturne",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluton",
    "ascendant": "Ascendant",
    "asc": "Ascendant",
}

_SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Angle, nom français, orbe maximal, nature.
_ASPECTS = [
    (0, "conjonction", 8, "neutre"),
    (60, "sextile", 4, "harmonieux"),
    (90, "carré", 7, "tension"),
    (120, "trigone", 7, "harmonieux"),
    (180, "opposition", 8, "tension"),
]

_NATURE = {name: nature for _, name, _, nature in _ASPECTS}
_NATURE["quinconce"] = "tension"

_HOUSE_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
}


def _planet_fr(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        value = value.get("name") or value.get("point")
    if not value:
        return None
    key = str(value).strip().lower().replace(" ", "_")
    return PLANETS_FR.get(key)


def _aspect_fr(value: Any) -> Optional[str]:
    value = str(value or "").strip().lower()
    if value.startswith("conj"):
        return "conjonction"
    if value.startswith("opp"):
        return "opposition"
    if value.startswith("tri"):
        return "trigone"
    if value.startswith("squ") or value.startswith("car"):
        return "carré"
    if value.startswith("sext"):
        return "sextile"
    if value.startswith("quinc") or value.startswith("inconj"):
        return "quinconce"
    return None


def _orb(value: Any) -> Optional[float]:
    try:
        return round(abs(float(value)), 1)
    except (TypeError, ValueError):
        return None


def _longitude(point: Dict[str, Any]) -> Optional[float]:
    longitude = point.get("absolute_longitude")
    try:
        if longitude is not None:
            return float(longitude) % 360
    except (TypeError, ValueError):
        pass

    sign = point.get("sign")
    degree = point.get("degree")
    try:
        degree = float(degree)
    except (TypeError, ValueError):
        return None

    if sign in _SIGN_ORDER and 0 <= degree < 30:
        return _SIGN_ORDER.index(sign) * 30 + degree
    if degree >= 30:
        return degree % 360
    return None


def _normalize_api_aspects(raw: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not isinstance(raw, list):
        return out

    for aspect in raw:
        if not isinstance(aspect, dict):
            continue

        planet1 = _planet_fr(
            aspect.get("planet1")
            or aspect.get("p1")
            or aspect.get("body1")
            or aspect.get("point1")
        )
        planet2 = _planet_fr(
            aspect.get("planet2")
            or aspect.get("p2")
            or aspect.get("body2")
            or aspect.get("point2")
        )
        kind = _aspect_fr(
            aspect.get("type")
            or aspect.get("aspect")
            or aspect.get("aspect_type")
            or aspect.get("name")
        )

        if not (planet1 and planet2 and kind) or planet1 == planet2:
            continue

        orb = (
            aspect.get("orb")
            if aspect.get("orb") is not None
            else aspect.get("orb_deg")
        )

        out.append({
            "planet1": planet1,
            "planet2": planet2,
            "type": kind,
            "orb": _orb(orb),
            "nature": _NATURE.get(kind, "neutre"),
        })

    return out


def compute_aspects(
    planets_dict: Dict[str, Dict[str, Any]],
    include_ascendant: bool = False,
) -> List[Dict[str, Any]]:
    """Calcule les aspects majeurs depuis les longitudes des planètes."""
    points = []
    for key, point in (planets_dict or {}).items():
        name = PLANETS_FR.get(key)
        if not name or (name == "Ascendant" and not include_ascendant):
            continue

        longitude = _longitude(point)
        if longitude is not None:
            points.append((name, longitude))

    out: List[Dict[str, Any]] = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            (name1, longitude1), (name2, longitude2) = points[i], points[j]
            difference = abs(longitude1 - longitude2) % 360
            if difference > 180:
                difference = 360 - difference

            for angle, name, max_orb, nature in _ASPECTS:
                orb = abs(difference - angle)
                if orb <= max_orb:
                    out.append({
                        "planet1": name1,
                        "planet2": name2,
                        "type": name,
                        "orb": round(orb, 1),
                        "nature": nature,
                    })
                    break

    return out


def extract_aspects(
    chart: Optional[dict],
    report: Optional[dict],
    planets_dict: Dict[str, Dict[str, Any]],
    include_ascendant: bool = False,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Lit les aspects API ou les calcule depuis les positions réelles."""
    candidates: List[Any] = []

    if isinstance(chart, dict):
        chart_data = chart.get("chart_data")
        if isinstance(chart_data, dict):
            candidates.append(chart_data.get("aspects"))
        candidates.append(chart.get("aspects"))

    if isinstance(report, dict):
        candidates.append(report.get("aspects"))
        data = report.get("data")
        if isinstance(data, dict):
            candidates.append(data.get("aspects"))

    aspects: List[Dict[str, Any]] = []
    for raw in candidates:
        aspects = _normalize_api_aspects(raw)
        if aspects:
            break

    if not aspects:
        aspects = compute_aspects(
            planets_dict,
            include_ascendant=include_ascendant,
        )

    if not include_ascendant:
        aspects = [
            aspect for aspect in aspects
            if "Ascendant" not in (aspect["planet1"], aspect["planet2"])
        ]

    aspects.sort(
        key=lambda aspect: (
            aspect["orb"] if aspect["orb"] is not None else 99
        )
    )
    return aspects[:limit]


def _house_number(value: Any) -> Optional[int]:
    if isinstance(value, int) and 1 <= value <= 12:
        return value

    if isinstance(value, str):
        value = value.strip().lower()
        if value.isdigit() and 1 <= int(value) <= 12:
            return int(value)

        match = re.match(
            r"([a-z]+)_?house",
            value.replace(" ", "_"),
        )
        if match and match.group(1) in _HOUSE_WORDS:
            return _HOUSE_WORDS[match.group(1)]

    return None


def extract_houses(
    chart: Optional[dict],
    planets_dict: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Extrait les 12 maisons et y place les planètes."""
    chart_data = (
        (chart or {}).get("chart_data")
        if isinstance(chart, dict)
        else None
    )
    cusps = (chart_data or {}).get("house_cusps") or []
    houses: Dict[int, Dict[str, Any]] = {}

    for cusp in cusps:
        if not isinstance(cusp, dict):
            continue

        number = _house_number(
            cusp.get("house")
            if cusp.get("house") is not None
            else cusp.get("index")
        )
        if not number:
            continue

        sign = aio.expand_sign(cusp.get("sign") or "")
        houses[number] = {
            "num": number,
            "sign": aio.sign_to_fr(sign),
            "planets_in_house": [],
            "_lon": _longitude({
                "absolute_longitude": cusp.get("absolute_longitude"),
                "sign": sign,
                "degree": cusp.get("degree"),
            }),
        }

    if len(houses) < 12:
        return []

    bounds = [houses[number]["_lon"] for number in range(1, 13)]
    can_place_by_longitude = all(bound is not None for bound in bounds)

    for key, point in (planets_dict or {}).items():
        name = PLANETS_FR.get(key)
        if not name or name == "Ascendant":
            continue

        number = None
        longitude = _longitude(point)
        if can_place_by_longitude and longitude is not None:
            for house_number in range(1, 13):
                start = bounds[house_number - 1]
                end = bounds[house_number % 12]
                span = (end - start) % 360

                if span and (longitude - start) % 360 < span:
                    number = house_number
                    break

        if number is None:
            number = _house_number(point.get("house"))

        if number:
            houses[number]["planets_in_house"].append(name)

    return [
        {
            key: value
            for key, value in houses[number].items()
            if key != "_lon"
        }
        for number in range(1, 13)
    ]
