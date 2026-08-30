"""wheel — Adaptateur entre astrology-io et le générateur `natal_wheel.py` du kit.

Le kit fourni définit `build_wheel(planets, cusps, asc)` où :
  - planets : liste de tuples `(nom_fr, longitude_degres_deci, retrograde_bool)`
  - cusps   : liste de 12 longitudes (maisons 1..12) en degrés décimaux
  - asc     : longitude de l'Ascendant (par défaut cusps[0])

Nos données astro-io (`extract_planets`) sont formatées différemment. Ce module
convertit + ajoute deux fonctions supplémentaires :
  - `extract_wheel_data`  → pour la page roue céleste (SVG + libellés AS/MC)
  - `extract_tables_data` → pour la page tableaux (planètes, aspects, distribution)
"""
from __future__ import annotations

import logging
import math
from typing import Any

from .vendor.natal_wheel_kit import build_wheel, GLYPH

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Traductions et signes zodiacaux
# ═══════════════════════════════════════════════════════════════════
_SIGN_EN_FR = {
    'aries': 'Bélier', 'taurus': 'Taureau', 'gemini': 'Gémeaux',
    'cancer': 'Cancer', 'leo': 'Lion', 'virgo': 'Vierge',
    'libra': 'Balance', 'scorpio': 'Scorpion', 'sagittarius': 'Sagittaire',
    'capricorn': 'Capricorne', 'aquarius': 'Verseau', 'pisces': 'Poissons',
}
_SIGN_GLYPH = {
    'Bélier': '♈', 'Taureau': '♉', 'Gémeaux': '♊', 'Cancer': '♋',
    'Lion': '♌', 'Vierge': '♍', 'Balance': '♎', 'Scorpion': '♏',
    'Sagittaire': '♐', 'Capricorne': '♑', 'Verseau': '♒', 'Poissons': '♓',
}
_SIGN_ORDER = list(_SIGN_GLYPH.keys())
_SIGN_MODE = {
    'Bélier': 'Cardinal', 'Cancer': 'Cardinal', 'Balance': 'Cardinal', 'Capricorne': 'Cardinal',
    'Taureau': 'Fixe', 'Lion': 'Fixe', 'Scorpion': 'Fixe', 'Verseau': 'Fixe',
    'Gémeaux': 'Mutable', 'Vierge': 'Mutable', 'Sagittaire': 'Mutable', 'Poissons': 'Mutable',
}
_SIGN_ELEMENT = {
    'Bélier': 'Feu', 'Lion': 'Feu', 'Sagittaire': 'Feu',
    'Taureau': 'Terre', 'Vierge': 'Terre', 'Capricorne': 'Terre',
    'Gémeaux': 'Air', 'Balance': 'Air', 'Verseau': 'Air',
    'Cancer': 'Eau', 'Scorpion': 'Eau', 'Poissons': 'Eau',
}

# Ordre canonique des planètes affichées (colonnes tableau + roue)
_PLANET_ORDER_FR = [
    'Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars',
    'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton',
    'Nœud Nord', 'Chiron',
]
_PLANET_EN_FR = {
    'sun': 'Soleil', 'moon': 'Lune', 'mercury': 'Mercure', 'venus': 'Vénus',
    'mars': 'Mars', 'jupiter': 'Jupiter', 'saturn': 'Saturne', 'uranus': 'Uranus',
    'neptune': 'Neptune', 'pluto': 'Pluton',
    'true node': 'Nœud Nord', 'mean node': 'Nœud Nord',
    'north node': 'Nœud Nord', 'chiron': 'Chiron',
}


def _to_longitude_deg(value: Any) -> float | None:
    """Convertit une position en degrés décimaux [0, 360).

    Accepte :
      - float direct (degré absolu 0-360)
      - dict {'sign': 'aries', 'degree': 12.5}  → 0° Bélier = 0, 12.5° Bélier = 12.5
      - dict {'degree': 42.3}  → utilisation directe
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) % 360.0
    if isinstance(value, dict):
        deg = value.get('degree')
        if isinstance(deg, (int, float)) and deg > 30:
            # Déjà en longitude absolue
            return float(deg) % 360.0
        # Sinon combine sign + degré relatif
        sign = (value.get('sign') or '').lower()
        sign_fr = _SIGN_EN_FR.get(sign, '')
        if sign_fr in _SIGN_ORDER and isinstance(deg, (int, float)):
            base = _SIGN_ORDER.index(sign_fr) * 30.0
            return (base + float(deg)) % 360.0
    return None


def _fmt_position(lon: float) -> tuple[str, str]:
    """Retourne ('12°18', '♌') à partir d'une longitude absolue."""
    lon = lon % 360.0
    sign_idx = int(lon // 30)
    sign_fr = _SIGN_ORDER[sign_idx]
    within = lon - sign_idx * 30
    deg = int(within)
    minutes = int(round((within - deg) * 60))
    if minutes == 60:
        deg += 1
        minutes = 0
    return f'{deg}°{minutes:02d}', _SIGN_GLYPH[sign_fr]


def extract_wheel_data(astro: dict) -> dict:
    """Extrait les données nécessaires à la roue SVG + les libellés AS/MC.

    Attendu (sortie de `astrology_io_service.natal_chart` + `extract_planets`) :
        astro = {
            'planets': { 'sun': {sign, house, degree}, ... },
            'houses':  [ {'house': 1, 'sign': 'virgo', 'degree': 22.5}, ... ]  # optionnel
            'raw_natal': { ... },  # payload brut de l'API si besoin
        }

    Retourne :
        { 'svg_planets': [(nom_fr, longitude, retrograde), ...],
          'svg_cusps':   [12 longitudes],
          'asc_label':   'Vierge 22°18',
          'mc_label':    'Gémeaux 20°06' }
    """
    planets = astro.get('planets') or {}
    houses_data = astro.get('houses') or (astro.get('raw_natal') or {}).get('houses') or []
    raw = astro.get('raw_natal') or {}

    # Longitudes des planètes
    svg_planets: list[tuple[str, float, bool]] = []
    for en, fr in _PLANET_EN_FR.items():
        if fr in [p[0] for p in svg_planets]:
            continue
        p = planets.get(en)
        if not p:
            continue
        lon = _to_longitude_deg(p)
        if lon is None:
            continue
        retro = bool(p.get('retrograde') or p.get('is_retrograde'))
        svg_planets.append((fr, lon, retro))

    # Ordonne selon _PLANET_ORDER_FR
    svg_planets.sort(key=lambda t: _PLANET_ORDER_FR.index(t[0]) if t[0] in _PLANET_ORDER_FR else 999)

    # Cuspides des 12 maisons
    svg_cusps: list[float] = []
    if isinstance(houses_data, list) and len(houses_data) >= 12:
        for h in houses_data[:12]:
            lon = _to_longitude_deg(h)
            if lon is not None:
                svg_cusps.append(lon)
    if len(svg_cusps) < 12:
        # Fallback : signe équal-house depuis l'Ascendant si disponible
        asc_lon = _to_longitude_deg((raw.get('ascendant') or {})) or 0.0
        svg_cusps = [(asc_lon + i * 30.0) % 360.0 for i in range(12)]

    asc_lon = svg_cusps[0]
    mc_lon = svg_cusps[9]
    asc_deg, asc_glyph = _fmt_position(asc_lon)
    mc_deg, mc_glyph = _fmt_position(mc_lon)
    asc_sign_fr = _SIGN_ORDER[int(asc_lon // 30)]
    mc_sign_fr = _SIGN_ORDER[int(mc_lon // 30)]

    return {
        'svg_planets': svg_planets,
        'svg_cusps': svg_cusps,
        'asc_label': f'{asc_sign_fr} {asc_deg}',
        'mc_label': f'{mc_sign_fr} {mc_deg}',
    }


def build_wheel_svg(wheel_data: dict) -> str:
    """Génère le SVG carré 1000×1000 de la roue céleste.

    Le SVG produit a `viewBox="0 0 1000 1000"` + `preserveAspectRatio="xMidYMid meet"`,
    donc l'inclusion HTML avec width=116mm et height=116mm garantit un cercle
    (§5.2 : |largeur − hauteur| < 0,2 mm dans le contrôle QA).
    """
    return build_wheel(wheel_data['svg_planets'], wheel_data['svg_cusps'])


# ═══════════════════════════════════════════════════════════════════
# Tableaux positions + aspects (§5.6)
# ═══════════════════════════════════════════════════════════════════
_ASPECT_ORBS = [
    ('Conjonction',   0,   8),
    ('Opposition',  180,   8),
    ('Trigone',     120,   7),
    ('Carré',        90,   7),
    ('Sextile',      60,   5),
]


def _find_aspects(planets: list[tuple[str, float, bool]]) -> list[dict]:
    """Détecte les aspects majeurs entre les planètes selon les orbes du guide (§5.4)."""
    out = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            name_a, lon_a, _ = planets[i]
            name_b, lon_b, _ = planets[j]
            d = abs(lon_a - lon_b) % 360.0
            d = min(d, 360.0 - d)
            for asp_name, angle, orb in _ASPECT_ORBS:
                if abs(d - angle) <= orb:
                    orb_val = abs(d - angle)
                    deg = int(orb_val)
                    minutes = int(round((orb_val - deg) * 60))
                    if minutes == 60:
                        deg += 1; minutes = 0
                    out.append({
                        'planet_a': name_a, 'planet_b': name_b,
                        'glyph_a': GLYPH.get(name_a, '?'),
                        'glyph_b': GLYPH.get(name_b, '?'),
                        'name': asp_name,
                        'orb': f'{deg}°{minutes:02d}',
                        'orb_value': orb_val,
                    })
                    break
    # Trie par orbe (les plus serrés en premier)
    out.sort(key=lambda a: a['orb_value'])
    return out


def _distribution_line(planets: list[tuple[str, float, bool]]) -> str:
    """Calcule la ligne 'Feu 24% · Terre 31% · Air 19% · Eau 26% — Cardinal ... Fixe ... Mutable ...'"""
    if not planets:
        return ''
    elements = {'Feu': 0, 'Terre': 0, 'Air': 0, 'Eau': 0}
    modes = {'Cardinal': 0, 'Fixe': 0, 'Mutable': 0}
    for _, lon, _ in planets:
        sign_fr = _SIGN_ORDER[int(lon // 30) % 12]
        elements[_SIGN_ELEMENT[sign_fr]] += 1
        modes[_SIGN_MODE[sign_fr]] += 1
    total = sum(elements.values()) or 1
    elem_str = ' · '.join(f'{k} {round(v * 100 / total)}\u202f%' for k, v in elements.items())
    mode_str = ' · '.join(f'{k} {round(v * 100 / total)}\u202f%' for k, v in modes.items())
    return f'{elem_str} — {mode_str}'


def _house_of(lon: float, cusps: list[float]) -> int:
    """Retourne la maison (1-12) contenant la longitude lon selon les cuspides fournies."""
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        # Domaine circulaire
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1


def extract_tables_data(astro: dict) -> dict:
    """Compose les données pour le template `_tables.html` (§5.6)."""
    wheel = extract_wheel_data(astro)
    planets = wheel['svg_planets']
    cusps = wheel['svg_cusps']

    rows = []
    for name, lon, retro in planets:
        pos, glyph_sign = _fmt_position(lon)
        rows.append({
            'name': name,
            'glyph': GLYPH.get(name, '?'),
            'position': f'{pos} {glyph_sign}',
            'retrograde': retro,
            'house': _house_of(lon, cusps),
        })

    half = (len(rows) + 1) // 2
    return {
        'planets_left': rows[:half],
        'planets_right': rows[half:],
        'aspects': _find_aspects(planets),
        'distribution_line': _distribution_line(planets),
    }
