"""Extraction des positions, maisons et aspects pour le manuscrit natal."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


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

MAJOR_ASPECTS = [
    ('conjunction', 0, 8, 'puissant', 'Conjonction'),
    ('opposition', 180, 8, 'dissonant', 'Opposition'),
    ('trine', 120, 6, 'harmonique', 'Trigone'),
    ('square', 90, 6, 'dissonant', 'Carré'),
    ('sextile', 60, 4, 'harmonique', 'Sextile'),
]

HOUSE_THEMES = {
    1: ('Première maison', 'Le Soi',
        'votre apparence, votre élan vital, votre masque'),
    2: ('Deuxième maison', 'Les Ressources',
        'vos valeurs, votre argent, votre rapport au corps'),
    3: ('Troisième maison', 'La Pensée',
        "l'esprit, la fratrie, les apprentissages courts"),
    4: ('Quatrième maison', 'Les Racines',
        'le foyer, les origines, la mémoire familiale'),
    5: ('Cinquième maison', 'La Créativité',
        'les amours, les enfants, le jeu, la création'),
    6: ('Sixième maison', 'Le Quotidien',
        'le travail, la santé, le service aux autres'),
    7: ('Septième maison', 'Les Partenariats',
        "l'autre, les contrats, le mariage"),
    8: ('Huitième maison', 'Les Transformations',
        'la mort, le sexe, les crises régénératrices'),
    9: ('Neuvième maison', 'Les Horizons',
        'les voyages lointains, la philosophie, la foi'),
    10: ('Dixième maison', 'La Vocation',
         'la carrière, la reconnaissance publique'),
    11: ('Onzième maison', 'Les Amitiés',
         'le collectif, les projets, les causes'),
    12: ('Douzième maison', "L'Inconscient",
         'le secret, le retrait, le karma'),
}

PLANET_EN_TO_FR = {
    'Sun': 'Soleil',
    'Moon': 'Lune',
    'Mercury': 'Mercure',
    'Venus': 'Vénus',
    'Mars': 'Mars',
    'Jupiter': 'Jupiter',
    'Saturn': 'Saturne',
    'Uranus': 'Uranus',
    'Neptune': 'Neptune',
    'Pluto': 'Pluton',
    'Ascendant': 'Ascendant',
    'ASC': 'Ascendant',
    'Asc': 'Ascendant',
    'MC': 'Milieu du Ciel',
    'Midheaven': 'Milieu du Ciel',
    'North Node': 'Nœud Nord',
    'South Node': 'Nœud Sud',
    'Chiron': 'Chiron',
}


def _to_fr_planet(name: str) -> str:
    if not name:
        return ''
    value = name.strip()
    if value in PLANET_EN_TO_FR:
        return PLANET_EN_TO_FR[value]
    capitalized = value.capitalize()
    return PLANET_EN_TO_FR.get(capitalized, value)


def _to_fr_sign(sign: str) -> str:
    if not sign:
        return ''
    value = sign.strip()
    if value in SIGN_EN_TO_FR:
        return SIGN_EN_TO_FR[value]
    capitalized = value.capitalize()
    if capitalized in SIGN_EN_TO_FR:
        return SIGN_EN_TO_FR[capitalized]
    if value in SIGN_FR_TO_EN:
        return value
    return capitalized


def _get_absolute_degree(planet: Dict[str, Any]) -> Optional[float]:
    for key in (
        'fullDegree', 'full_degree', 'absoluteDegree',
        'absolute_degree', 'longitude',
    ):
        value = planet.get(key)
        if isinstance(value, (int, float)):
            return float(value) % 360

    degree = planet.get(
        'normDegree',
        planet.get('norm_degree', planet.get('degree')),
    )
    sign = planet.get('sign') or planet.get('sign_name')

    if isinstance(degree, (int, float)) and sign:
        sign_fr = _to_fr_sign(sign)
        if sign_fr in ZODIAC_SIGNS_FR:
            index = ZODIAC_SIGNS_FR.index(sign_fr)
            return (index * 30 + float(degree)) % 360

    return None


def _get_in_sign_degree(planet: Dict[str, Any]) -> Optional[float]:
    for key in ('normDegree', 'norm_degree', 'degree'):
        value = planet.get(key)
        if isinstance(value, (int, float)):
            return float(value) % 30

    absolute = _get_absolute_degree(planet)
    return absolute % 30 if absolute is not None else None


def _fmt_degree(degree: Optional[float]) -> str:
    if degree is None:
        return ''
    whole = int(degree)
    minutes = int((degree - whole) * 60)
    return f"{whole}°{minutes:02d}'"


def extract_planet_positions(
    natal_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    raw = natal_data.get('planets') or []

    if isinstance(raw, dict):
        planets = [
            {
                **value,
                'name': key,
                **(
                    {'name_fr': value.get('name_fr', key)}
                    if not value.get('name_fr')
                    else {}
                ),
            }
            for key, value in raw.items()
        ]
    else:
        planets = raw

    out: List[Dict[str, Any]] = []
    for planet in planets:
        if not isinstance(planet, dict):
            continue

        name_raw = (
            planet.get('name_fr') or planet.get('name') or ''
        ).strip()
        if not name_raw:
            continue

        degree = _get_in_sign_degree(planet)
        house = planet.get('house') or planet.get('house_number')

        out.append({
            'name': _to_fr_planet(name_raw),
            'sign': _to_fr_sign(
                planet.get('sign') or planet.get('sign_name') or ''
            ),
            'house': (
                int(house)
                if isinstance(house, (int, float)) and 1 <= house <= 12
                else None
            ),
            'degree_in_sign': degree,
            'degree_in_sign_str': _fmt_degree(degree),
            'absolute_degree': _get_absolute_degree(planet),
            'retrograde': bool(
                planet.get('retrograde') or planet.get('is_retro')
            ),
            'analysis': planet.get('analysis', ''),
        })

    return out


def extract_houses(
    natal_data: Dict[str, Any],
    planets: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    planets = planets or extract_planet_positions(natal_data)
    residents: Dict[int, List[str]] = {
        house: [] for house in range(1, 13)
    }

    for planet in planets:
        house = planet.get('house')
        if isinstance(house, int) and 1 <= house <= 12:
            name = planet['name']
            if planet.get('retrograde'):
                name += ' ℞'
            residents[house].append(name)

    raw = (
        natal_data.get('house_cusps')
        or natal_data.get('houses')
        or {}
    )
    cusps: Dict[int, Dict[str, Any]] = {}

    if isinstance(raw, list):
        for number, cusp in enumerate(raw, start=1):
            if isinstance(cusp, dict):
                cusps[number] = cusp
    elif isinstance(raw, dict):
        for key, cusp in raw.items():
            try:
                number = int(key)
                if 1 <= number <= 12 and isinstance(cusp, dict):
                    cusps[number] = cusp
            except (TypeError, ValueError):
                continue

    out: List[Dict[str, Any]] = []
    for number in range(1, 13):
        name, theme, description = HOUSE_THEMES[number]
        cusp = cusps.get(number, {})
        degree = (
            cusp.get('degree')
            or cusp.get('normDegree')
            or cusp.get('full_degree')
        )

        out.append({
            'num': number,
            'name': name,
            'theme': theme,
            'theme_desc': description,
            'sign': _to_fr_sign(
                cusp.get('sign') or cusp.get('sign_name') or ''
            ),
            'cusp_degree_str': _fmt_degree(
                float(degree) % 30
                if isinstance(degree, (int, float))
                else None
            ),
            'planets': residents[number],
        })

    return out


def extract_aspects(
    natal_data: Dict[str, Any],
    planets: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    raw = natal_data.get('aspects') or []
    out: List[Dict[str, Any]] = []
    planet_names = {
        'Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars',
        'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton',
    }

    if isinstance(raw, list) and raw:
        for aspect in raw:
            if not isinstance(aspect, dict):
                continue

            planet_a = (
                aspect.get('aspecting_planet')
                or aspect.get('planet_a')
                or aspect.get('first')
                or aspect.get('planet_1')
                or ''
            ).strip()
            planet_b = (
                aspect.get('aspected_planet')
                or aspect.get('planet_b')
                or aspect.get('second')
                or aspect.get('planet_2')
                or ''
            ).strip()
            kind = (
                aspect.get('type')
                or aspect.get('aspect_name')
                or aspect.get('aspect')
                or ''
            ).strip().lower()
            orb = aspect.get('orb') or aspect.get('orb_degrees')

            type_fr = {
                'conjunction': 'Conjonction',
                'opposition': 'Opposition',
                'trine': 'Trigone',
                'square': 'Carré',
                'sextile': 'Sextile',
                'conjonction': 'Conjonction',
                'trigone': 'Trigone',
                'carré': 'Carré',
            }.get(kind, kind.title() if kind else '')

            nature = {
                'Conjonction': 'puissant',
                'Opposition': 'dissonant',
                'Trigone': 'harmonique',
                'Carré': 'dissonant',
                'Sextile': 'harmonique',
            }.get(type_fr, 'neutre')

            if planet_a and planet_b and type_fr:
                out.append({
                    'planet_a': _to_fr_planet(planet_a),
                    'planet_b': _to_fr_planet(planet_b),
                    'type_fr': type_fr,
                    'orb_degrees': (
                        float(orb)
                        if isinstance(orb, (int, float))
                        else None
                    ),
                    'nature': nature,
                })

        return out

    planets = planets or extract_planet_positions(natal_data)
    positions = {
        planet['name']: planet['absolute_degree']
        for planet in planets
        if planet['absolute_degree'] is not None
        and planet['name'] in planet_names
    }

    names = sorted(positions)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a, name_b = names[i], names[j]
            difference = abs(positions[name_a] - positions[name_b])
            if difference > 180:
                difference = 360 - difference

            for _, angle, max_orb, nature, type_fr in MAJOR_ASPECTS:
                orb = abs(difference - angle)
                if orb <= max_orb:
                    out.append({
                        'planet_a': name_a,
                        'planet_b': name_b,
                        'type_fr': type_fr,
                        'orb_degrees': round(orb, 2),
                        'nature': nature,
                    })
                    break

    priority = {
        'Conjonction': 0,
        'Opposition': 1,
        'Carré': 2,
        'Trigone': 3,
        'Sextile': 4,
    }
    out.sort(
        key=lambda aspect: (
            priority.get(aspect['type_fr'], 5),
            aspect.get('orb_degrees') or 99,
        )
    )
    return out


_ASPECT_INTERP_TEMPLATES = {
    'Conjonction': (
        'Fusion. {a} et {b} jouent la même note. '
        'Vous ressentez leurs qualités comme une seule '
        'et même énergie — amplifiée.'
    ),
    'Opposition': (
        'Tension. {a} et {b} se font face. '
        "Vous oscillez entre leurs deux pôles — l'équilibre "
        "se trouve au centre, pas dans l'un ou l'autre."
    ),
    'Trigone': (
        "Harmonie. {a} et {b} s'entendent sans effort. "
        'Ce talent circule, parfois trop facilement '
        "— à vous de l'engager."
    ),
    'Carré': (
        'Friction. {a} et {b} veulent chacun imposer leur rythme. '
        "C'est inconfortable, mais c'est votre moteur "
        '— rien ne pousse plus que ce frottement.'
    ),
    'Sextile': (
        'Opportunité. {a} et {b} se font signe. '
        "Si vous saisissez l'occasion, l'énergie s'ouvre "
        '— mais elle ne force rien.'
    ),
}


def interpret_aspect(aspect: Dict[str, Any]) -> str:
    template = _ASPECT_INTERP_TEMPLATES.get(
        aspect.get('type_fr', ''), ''
    )
    if not template:
        return ''
    return template.format(
        a=aspect.get('planet_a', '?'),
        b=aspect.get('planet_b', '?'),
    )


__all__ = [
    'extract_planet_positions',
    'extract_houses',
    'extract_aspects',
    'interpret_aspect',
    'HOUSE_THEMES',
    'ZODIAC_SIGNS_FR',
    'SIGN_EN_TO_FR',
    'PLANET_EN_TO_FR',
    '_to_fr_sign',
    '_to_fr_planet',
    '_fmt_degree',
]
