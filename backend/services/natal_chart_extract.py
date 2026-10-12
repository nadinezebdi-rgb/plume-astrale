"""natal_chart_extract — Extraction aspects + maisons + degrés depuis le thème natal.
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
