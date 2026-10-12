"""natal_chart_extract — Extraction aspects + maisons + degrés depuis le thème natal.
================================================================================

Pour tenir la promesse éditoriale "Thème Natal 43 pages", le PDF a besoin de 3
blocs de données que l'API `astrology-api.io` fournit :

  1. **Positions** : chaque planète avec signe + maison + degré exact
     → `/api/v3/data/positions`
  2. **Aspects** : trine, carré, opposition, etc. entre planètes
     → `/api/v3/data/aspects`
  3. **House cusps** : cuspides des 12 maisons avec leur signe
     → `/api/v3/data/house-cusps`

Ce module normalise la sortie API → format uniforme consommé par
`natal_manuscript_builder.py`. Si l'API ne renvoie pas tout (ex. tier Essential
sans aspects), on calcule un fallback à partir des positions brutes.

Pas d'appel IA ici — c'est du calcul géométrique + mapping. L'enrichissement
littéraire (interprétation de chaque aspect / maison) est fait en amont par
`enhanced_natal_analysis.py` ou par le prompt GPT du book builder.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ─── Constantes astro ────────────────────────────────────────────────
# Signes dans l'ordre du zodiaque (0 = Bélier, 11 = Poissons)
ZODIAC_SIGNS_EN = (
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
)
ZODIAC_SIGNS_FR = (
    'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
    'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
)
SIGN_EN_TO_FR = dict(zip(ZODIAC_SIGNS_EN, ZODIAC_SIGNS_FR))
SIGN_FR_TO_EN = dict(zip(ZODIAC_SIGNS_FR, ZODIAC_SIGNS_EN))

# Aspects majeurs avec orbes (degrés de tolérance) et nature (harmonique/dissonant)
MAJOR_ASPECTS = [
    ('conjunction', 0,   8, 'puissant', 'Conjonction'),
    ('opposition',  180, 8, 'dissonant', 'Opposition'),
    ('trine',       120, 6, 'harmonique', 'Trigone'),
    ('square',      90,  6, 'dissonant', 'Carré'),
    ('sextile',     60,  4, 'harmonique', 'Sextile'),
]

# Les 12 maisons (noms + thèmes classiques)
HOUSE_THEMES = {
    1:  ('Première maison',      'Le Soi',               'votre apparence, votre élan vital, votre masque'),
    2:  ('Deuxième maison',      'Les Ressources',       'vos valeurs, votre argent, votre rapport au corps'),
    3:  ('Troisième maison',     'La Pensée',            "l'esprit, la fratrie, les apprentissages courts"),
    4:  ('Quatrième maison',     'Les Racines',          'le foyer, les origines, la mémoire familiale'),
    5:  ('Cinquième maison',     'La Créativité',        'les amours, les enfants, le jeu, la création'),
    6:  ('Sixième maison',       'Le Quotidien',         'le travail, la santé, le service aux autres'),
    7:  ('Septième maison',      'Les Partenariats',     "l'autre, les contrats, le mariage"),
    8:  ('Huitième maison',      'Les Transformations',  'la mort, le sexe, les crises régénératrices'),
    9:  ('Neuvième maison',      'Les Horizons',         'les voyages lointains, la philosophie, la foi'),
    10: ('Dixième maison',       'La Vocation',          'la carrière, la reconnaissance publique'),
    11: ('Onzième maison',       'Les Amitiés',          'le collectif, les projets, les causes'),
    12: ('Douzième maison',      "L'Inconscient",        'le secret, le retrait, le karma'),
}


# Mapping noms de planètes EN → FR (pour normalisation des aspects API v3)
PLANET_EN_TO_FR = {
    'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus',
    'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne',
    'Uranus': 'Uranus', 'Neptune': 'Neptune', 'Pluto': 'Pluton',
    'Ascendant': 'Ascendant', 'ASC': 'Ascendant', 'Asc': 'Ascendant',
    'MC': 'Milieu du Ciel', 'Midheaven': 'Milieu du Ciel',
    'North Node': 'Nœud Nord', 'South Node': 'Nœud Sud', 'Chiron': 'Chiron',
}


def _to_fr_planet(name: str) -> str:
    """Accepte 'Sun' / 'Soleil' / 'sun' → 'Soleil'. Si inconnu, retourne tel quel."""
    if not name:
        return ''
    s = name.strip()
    if s in PLANET_EN_TO_FR:
        return PLANET_EN_TO_FR[s]
    s_cap = s.capitalize()
    if s_cap in PLANET_EN_TO_FR:
        return PLANET_EN_TO_FR[s_cap]
    return s


# ─── Normalizers ─────────────────────────────────────────────────────
def _to_fr_sign(sign: str) -> str:
    """Accepte 'Aries' / 'Bélier' / 'aries' → 'Bélier'."""
    if not sign:
        return ''
    s = sign.strip()
    if s in SIGN_EN_TO_FR:
        return SIGN_EN_TO_FR[s]
    s_cap = s.capitalize()
    if s_cap in SIGN_EN_TO_FR:
        return SIGN_EN_TO_FR[s_cap]
    if s in SIGN_FR_TO_EN:
        return s
    return s_cap


def _get_absolute_degree(planet: Dict[str, Any]) -> Optional[float]:
    """Récupère la longitude absolue (0-360°) depuis un dict planète.

    L'API peut retourner `fullDegree`, `absoluteDegree`, `normDegree + sign`,
    ou juste `degree` dans un signe. On tente dans l'ordre.
    """
    # Format 1 : fullDegree direct
    for key in ('fullDegree', 'full_degree', 'absoluteDegree', 'absolute_degree', 'longitude'):
        v = planet.get(key)
        if isinstance(v, (int, float)):
            return float(v) % 360
    # Format 2 : normDegree (dans le signe) + sign_name → calcul absolu
    norm = planet.get('normDegree', planet.get('norm_degree', planet.get('degree')))
    sign = planet.get('sign') or planet.get('sign_name')
    if isinstance(norm, (int, float)) and sign:
        sign_fr = _to_fr_sign(sign)
        if sign_fr in ZODIAC_SIGNS_FR:
            sign_idx = ZODIAC_SIGNS_FR.index(sign_fr)
            return (sign_idx * 30 + float(norm)) % 360
    return None


def _get_in_sign_degree(planet: Dict[str, Any]) -> Optional[float]:
    """Récupère le degré DANS LE SIGNE (0-30)."""
    for key in ('normDegree', 'norm_degree', 'degree'):
        v = planet.get(key)
        if isinstance(v, (int, float)):
            return float(v) % 30
    full = _get_absolute_degree(planet)
    return full % 30 if full is not None else None


def _fmt_degree(deg: Optional[float]) -> str:
    """15.5 → '15°30'' (degrés et minutes d'arc)."""
    if deg is None:
        return ''
    whole = int(deg)
    mins = int((deg - whole) * 60)
    return f'{whole}°{mins:02d}\''


# ─── Extraction : positions enrichies ────────────────────────────────
def extract_planet_positions(natal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalise la liste des planètes du natal_data.

    Retourne : [{name, sign, house, degree_in_sign_str, abs_degree, retrograde}]
    """
    planets_raw = natal_data.get('planets') or []
    # Accepte soit liste de dicts, soit dict {name: dict}
    if isinstance(planets_raw, dict):
        planets_iter = [{**v, 'name': k, **({'name_fr': v.get('name_fr', k)} if not v.get('name_fr') else {})}
                        for k, v in planets_raw.items()]
    else:
        planets_iter = planets_raw

    out: List[Dict[str, Any]] = []
    for p in planets_iter:
        if not isinstance(p, dict):
            continue
        name_raw = (p.get('name_fr') or p.get('name') or '').strip()
        if not name_raw:
            continue
        name = _to_fr_planet(name_raw)
        sign = _to_fr_sign(p.get('sign') or p.get('sign_name') or '')
        in_sign = _get_in_sign_degree(p)
        abs_deg = _get_absolute_degree(p)
        house = p.get('house') or p.get('house_number')
        retrograde = bool(p.get('retrograde') or p.get('is_retro'))
        out.append({
            'name': name,
            'sign': sign,
            'house': int(house) if isinstance(house, (int, float)) and 1 <= house <= 12 else None,
            'degree_in_sign': in_sign,
            'degree_in_sign_str': _fmt_degree(in_sign),
            'absolute_degree': abs_deg,
            'retrograde': retrograde,
            # Analyse préservée pour la section planète/signe
            'analysis': p.get('analysis', ''),
        })
    return out


# ─── Extraction : maisons avec planètes dedans ──────────────────────
def extract_houses(natal_data: Dict[str, Any],
                   planets: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Retourne 12 maisons : [{num, name, sign, cusp_degree_str, planets:[name,...], theme}].

    Lit `house_cusps` depuis natal_data si présent, sinon utilise seulement les
    planètes (maisons sans signe cuspide mais avec habitants).
    """
    planets = planets or extract_planet_positions(natal_data)

    # Group planets by house
    planets_by_house: Dict[int, List[str]] = {h: [] for h in range(1, 13)}
    for p in planets:
        h = p.get('house')
        if isinstance(h, int) and 1 <= h <= 12:
            name = p['name']
            if p.get('retrograde'):
                name += ' ℞'
            planets_by_house[h].append(name)

    # House cusps : {house_number: {sign, degree}}
    cusps_raw = natal_data.get('house_cusps') or natal_data.get('houses') or {}
    cusps: Dict[int, Dict[str, Any]] = {}
    if isinstance(cusps_raw, list):
        for i, c in enumerate(cusps_raw, start=1):
            if isinstance(c, dict):
                cusps[i] = c
    elif isinstance(cusps_raw, dict):
        for k, v in cusps_raw.items():
            try:
                n = int(k)
                if 1 <= n <= 12 and isinstance(v, dict):
                    cusps[n] = v
            except (TypeError, ValueError):
                continue

    out: List[Dict[str, Any]] = []
    for h in range(1, 13):
        name, _, theme_desc = HOUSE_THEMES[h]
        cusp = cusps.get(h, {})
        cusp_sign = _to_fr_sign(cusp.get('sign') or cusp.get('sign_name') or '')
        cusp_deg = cusp.get('degree') or cusp.get('normDegree') or cusp.get('full_degree')
        cusp_deg_str = _fmt_degree(float(cusp_deg) % 30 if isinstance(cusp_deg, (int, float)) else None)
        out.append({
            'num': h,
            'name': name,
            'theme': HOUSE_THEMES[h][1],
            'theme_desc': theme_desc,
            'sign': cusp_sign,
            'cusp_degree_str': cusp_deg_str,
            'planets': planets_by_house[h],
        })
    return out


# ─── Extraction : aspects ────────────────────────────────────────────
def extract_aspects(natal_data: Dict[str, Any],
                    planets: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Retourne la liste des aspects majeurs : [{planet_a, planet_b, type_fr,
    orb_degrees, nature}].

    Lit `aspects` depuis natal_data si fourni (API), sinon calcule depuis les
    positions absolues des planètes (fallback).
    """
    raw = natal_data.get('aspects') or []
    out: List[Dict[str, Any]] = []
    PLANET_SET = {'Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars', 'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton'}

    if isinstance(raw, list) and raw:
        # Format API attendu : liste de {aspecting_planet, aspected_planet, type, orb}
        for a in raw:
            if not isinstance(a, dict):
                continue
            # Noms possibles API
            pa = (a.get('aspecting_planet') or a.get('planet_a') or a.get('first')
                  or a.get('planet_1') or '').strip()
            pb = (a.get('aspected_planet') or a.get('planet_b') or a.get('second')
                  or a.get('planet_2') or '').strip()
            atype = (a.get('type') or a.get('aspect_name') or a.get('aspect') or '').strip().lower()
            orb = a.get('orb') or a.get('orb_degrees')
            # Normalize type → FR
            type_fr = {
                'conjunction': 'Conjonction', 'opposition': 'Opposition',
                'trine': 'Trigone', 'square': 'Carré', 'sextile': 'Sextile',
                'conjonction': 'Conjonction', 'trigone': 'Trigone', 'carré': 'Carré',
            }.get(atype, atype.title() if atype else '')
            nature = {
                'Conjonction': 'puissant', 'Opposition': 'dissonant',
                'Trigone': 'harmonique', 'Carré': 'dissonant', 'Sextile': 'harmonique',
            }.get(type_fr, 'neutre')
            if pa and pb and type_fr:
                out.append({
                    'planet_a': _to_fr_planet(pa), 'planet_b': _to_fr_planet(pb), 'type_fr': type_fr,
                    'orb_degrees': float(orb) if isinstance(orb, (int, float)) else None,
                    'nature': nature,
                })
        return out

    # Fallback : calcul géométrique depuis les positions planètes.
    planets = planets or extract_planet_positions(natal_data)
    pos_by_name = {p['name']: p['absolute_degree'] for p in planets
                   if p['absolute_degree'] is not None and p['name'] in PLANET_SET}

    names = sorted(pos_by_name.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_name, b_name = names[i], names[j]
            a_deg = pos_by_name[a_name]
            b_deg = pos_by_name[b_name]
            diff = abs(a_deg - b_deg)
            if diff > 180:
                diff = 360 - diff
            for _, target, orb_max, nature, type_fr in MAJOR_ASPECTS:
                if abs(diff - target) <= orb_max:
                    out.append({
                        'planet_a': a_name, 'planet_b': b_name, 'type_fr': type_fr,
                        'orb_degrees': round(abs(diff - target), 2),
                        'nature': nature,
                    })
                    break  # un seul aspect par paire
    # Trie : conjonctions et oppositions d'abord (plus intenses)
    priority = {'Conjonction': 0, 'Opposition': 1, 'Carré': 2, 'Trigone': 3, 'Sextile': 4}
    out.sort(key=lambda a: (priority.get(a['type_fr'], 5), a.get('orb_degrees') or 99))
    return out


# ─── Interprétation minimale d'un aspect (template) ──────────────────
_ASPECT_INTERP_TEMPLATES = {
    'Conjonction': "Fusion. {a} et {b} jouent la même note. Vous ressentez leurs qualités comme une seule et même énergie — amplifiée.",
    'Opposition':  "Tension. {a} et {b} se font face. Vous oscillez entre leurs deux pôles — l'équilibre se trouve au centre, pas dans l'un ou l'autre.",
    'Trigone':     "Harmonie. {a} et {b} s'entendent sans effort. Ce talent circule, parfois trop facilement — à vous de l'engager.",
    'Carré':       "Friction. {a} et {b} veulent chacun imposer leur rythme. C'est inconfortable, mais c'est votre moteur — rien ne pousse plus que ce frottement.",
    'Sextile':     "Opportunité. {a} et {b} se font signe. Si vous saisissez l'occasion, l'énergie s'ouvre — mais elle ne force rien.",
}


def interpret_aspect(aspect: Dict[str, Any]) -> str:
    """Retourne une phrase courte pour un aspect donné."""
    tmpl = _ASPECT_INTERP_TEMPLATES.get(aspect.get('type_fr', ''), '')
    if not tmpl:
        return ''
    return tmpl.format(a=aspect.get('planet_a', '?'), b=aspect.get('planet_b', '?'))


__all__ = [
    'extract_planet_positions', 'extract_houses', 'extract_aspects',
    'interpret_aspect', 'HOUSE_THEMES', 'ZODIAC_SIGNS_FR', 'SIGN_EN_TO_FR',
    'PLANET_EN_TO_FR', '_to_fr_sign', '_to_fr_planet', '_fmt_degree',
]
