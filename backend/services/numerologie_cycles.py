"""Calculs numérologiques déterministes à partir de la date de naissance.

Complète les nombres fournis par astrology-api.io (/numerology/core-numbers) avec
les chapitres que l'API v3 ne renvoie pas : mois personnels, pinacles, défis,
dettes karmiques, grille Lo-Shu et biorythmes. Aucun appel réseau.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

MASTER = (11, 22, 33)

MONTHS_FR = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
]

THEMES = {
    1: ('Nouveau départ', "Tu plantes une graine : initiative, indépendance, décisions franches. Ose commencer, sans attendre l'approbation des autres."),
    2: ('Coopération', "Le temps de la patience et de l'écoute. Les alliances, les relations et l'intuition passent avant l'action brute."),
    3: ('Expression', "Créativité, communication et joie sont à l'honneur. Montre-toi, parle, crée, mais évite de t'éparpiller."),
    4: ('Fondations', "Structure, travail régulier et organisation. Ce que tu bâtis maintenant tiendra longtemps."),
    5: ('Mouvement', "Changements, rencontres, voyages. La liberté appelle de la souplesse : reste ouvert(e) sans te disperser."),
    6: ('Cœur et foyer', "Famille, engagements, beauté et responsabilité affective. Prends soin des autres sans t'oublier."),
    7: ('Retrait fécond', "Étude, introspection et recul. Écoute ton intuition, ralentis, laisse mûrir avant de décider."),
    8: ('Réalisation', "Ambition, argent, autorité. Le moment d'aboutir concrètement, avec justesse et équilibre."),
    9: ('Bilan et lâcher-prise', "Un cycle se clôt. Pardonne, trie, transmets, libère la place pour la suite."),
}

MASTER_NOTE = {
    11: "Vibration maîtresse 11 : intuition amplifiée, sensibilité élevée. Reste ancré(e) pour ne pas te laisser submerger.",
    22: "Vibration maîtresse 22 : grand potentiel de construction concrète. Vise un projet qui te dépasse, par étapes.",
    33: "Vibration maîtresse 33 : élan de service et de compassion. Pose des limites pour durer.",
}

MONTH_HINT = {
    1: "Idéal pour lancer, proposer, trancher.",
    2: "Privilégie le dialogue et la patience.",
    3: "Bon mois pour créer et communiquer.",
    4: "Mets de l'ordre, avance pas à pas.",
    5: "Reste flexible : des imprévus ouvrent des portes.",
    6: "Soigne tes proches et ton cadre de vie.",
    7: "Ralentis, lis, médite, écoute-toi.",
    8: "Concentre-toi sur tes objectifs concrets.",
    9: "Termine, range, pardonne.",
}

PINNACLE_MEANING = {
    1: "Période d'affirmation de soi, d'autonomie et d'initiative.",
    2: "Période de partenariats, de diplomatie et d'écoute intérieure.",
    3: "Période d'expression créative, de sociabilité et de légèreté.",
    4: "Période de travail, de stabilité et de construction patiente.",
    5: "Période de changements, de découvertes et de liberté.",
    6: "Période d'engagements affectifs, de famille et de service.",
    7: "Période d'approfondissement, d'étude et de quête de sens.",
    8: "Période de réussite matérielle, de responsabilités et de pouvoir personnel.",
    9: "Période de générosité, de grandes prises de conscience et de transmission.",
    11: "Période d'inspiration et d'éveil intuitif, souvent exigeante nerveusement.",
    22: "Période de concrétisation à grande échelle, avec des responsabilités importantes.",
    33: "Période de dévouement et d'enseignement par l'exemple.",
}

CHALLENGE_MEANING = {
    0: "Pas de défi marqué : le choix et l'équilibre sont ton exercice. Évite l'indécision.",
    1: "Apprendre à t'affirmer sans dominer, et à croire en tes idées.",
    2: "Apprendre à gérer ta sensibilité sans t'effacer ni dépendre du regard des autres.",
    3: "Apprendre à t'exprimer sans te disperser ni te critiquer.",
    4: "Apprendre la rigueur sans rigidité, et à persévérer.",
    5: "Apprendre la liberté sans excès ni fuite devant l'engagement.",
    6: "Apprendre à aimer sans vouloir sauver ni contrôler.",
    7: "Apprendre à faire confiance, à sortir de l'isolement et du doute.",
    8: "Apprendre à gérer pouvoir et argent avec équité.",
}

KARMIC = {
    13: "Dette 13/4 : apprendre la constance et la valeur du travail, sans raccourcis ni découragement.",
    14: "Dette 14/5 : apprendre la modération et l'usage sage de la liberté (excès, dispersion, dépendances).",
    16: "Dette 16/7 : apprendre l'humilité. Les certitudes tombent pour laisser place à une vérité plus profonde.",
    19: "Dette 19/1 : apprendre à demander de l'aide et à partager le pouvoir, sans se croire seul(e) face à tout.",
}

LOSHU_DIGIT = {
    1: "Affirmation, volonté, communication directe.",
    2: "Sensibilité, intuition, sens de la relation.",
    3: "Créativité, curiosité, expression de soi.",
    4: "Sens pratique, méthode, endurance.",
    5: "Équilibre, adaptabilité, centre de gravité.",
    6: "Responsabilité, loyauté, sens de la famille.",
    7: "Réflexion, spiritualité, analyse.",
    8: "Ambition, gestion, force d'accomplissement.",
    9: "Idéal, générosité, vision d'ensemble.",
}

LOSHU_MISSING = {
    1: "Apprends à poser tes limites et à prendre la parole.",
    2: "Cultive l'écoute de ton intuition et la douceur dans les liens.",
    3: "Ose t'exprimer, créer et jouer, même imparfaitement.",
    4: "Mets en place des routines simples pour stabiliser ton quotidien.",
    5: "Cherche ton centre : respiration, corps, rituels de recentrage.",
    6: "Nourris tes liens proches et ton cadre de vie.",
    7: "Réserve du temps de silence pour te poser les bonnes questions.",
    8: "Travaille ton rapport à l'argent et à l'autorité, pas à pas.",
    9: "Élargis ton regard : bénévolat, transmission, projets utiles.",
}

# Plans et flèches classiques de la grille 3x3 (disposition Lo-Shu : 4 9 2 / 3 5 7 / 8 1 6)
LOSHU_GRID = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
LOSHU_ARROWS = [
    ((4, 9, 2), "Flèche de la planification (haut)", "Esprit d'analyse et vision."),
    ((3, 5, 7), "Flèche de l'âme (milieu)", "Équilibre émotionnel et profondeur."),
    ((8, 1, 6), "Flèche de l'action (bas)", "Capacité à réaliser concrètement."),
    ((4, 3, 8), "Flèche de la pensée (gauche)", "Réflexion et mémoire."),
    ((9, 5, 1), "Flèche de la volonté (centre)", "Détermination et constance."),
    ((2, 7, 6), "Flèche de l'action émotionnelle (droite)", "Passage à l'acte sensible."),
    ((4, 5, 6), "Flèche de la diagonale terrestre", "Stabilité et ancrage."),
    ((2, 5, 8), "Flèche de la diagonale spirituelle", "Intuition et ouverture."),
]


def reduce_number(n: int, keep_master: bool = True) -> int:
    while n > 9 and not (keep_master and n in MASTER):
        n = sum(int(c) for c in str(n))
    return n


def _base(n: int) -> int:
    """Réduit à un chiffre (11→2, 22→4, 33→6) pour accéder aux textes."""
    return reduce_number(n, keep_master=False)


def parse_birth(birth_date_iso: str) -> Optional[date]:
    try:
        return datetime.strptime(str(birth_date_iso)[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def personal_year(birth: date, year: int) -> int:
    return reduce_number(reduce_number(birth.day) + reduce_number(birth.month) + reduce_number(year))


def months_forecast(birth: date, today: Optional[date] = None, count: int = 12) -> List[Dict[str, Any]]:
    today = today or date.today()
    out: List[Dict[str, Any]] = []
    y, m = today.year, today.month
    for _ in range(count):
        py = personal_year(birth, y)
        pm = reduce_number(py + reduce_number(m))
        base = _base(pm)
        out.append({
            'label': f'{MONTHS_FR[m - 1].capitalize()} {y}',
            'personal_year': py,
            'personal_month': pm,
            'theme': THEMES[base][0],
            'text': f'{THEMES[base][1]} {MONTH_HINT[base]}',
        })
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return out


def pinnacles_and_challenges(birth: date) -> Dict[str, Any]:
    d = reduce_number(birth.day)
    m = reduce_number(birth.month)
    y = reduce_number(birth.year)
    life_path = reduce_number(d + m + y)
    first_end = 36 - _base(life_path)
    ranges = [(0, first_end), (first_end + 1, first_end + 9), (first_end + 10, first_end + 18), (first_end + 19, None)]
    values = [
        reduce_number(m + d),
        reduce_number(d + y),
    ]
    values.append(reduce_number(values[0] + values[1]))
    values.append(reduce_number(m + y))
    c1 = abs(_base(m) - _base(d))
    c2 = abs(_base(d) - _base(y))
    c3 = abs(c1 - c2)
    c4 = abs(_base(m) - _base(y))
    chal = [c1, c2, c3, c4]
    pinnacles = []
    for i, (v, (a, b)) in enumerate(zip(values, ranges)):
        age = f'de {a} à {b} ans' if b is not None else f'à partir de {a} ans'
        if i == 0:
            age = f'jusqu\'à {b} ans'
        pinnacles.append({
            'index': i + 1, 'number': v, 'age': age,
            'text': PINNACLE_MEANING.get(v, PINNACLE_MEANING[_base(v)]),
            'year_from': birth.year + a,
        })
    challenges = [
        {'index': i + 1, 'number': c, 'text': CHALLENGE_MEANING.get(c, CHALLENGE_MEANING[0])}
        for i, c in enumerate(chal)
    ]
    return {'pinnacles': pinnacles, 'challenges': challenges, 'life_path': life_path}


def karmic_debts(birth: date) -> List[Dict[str, Any]]:
    digits_sum = sum(int(c) for c in birth.strftime('%d%m%Y'))
    candidates = {
        'jour de naissance': birth.day,
        'somme de ta date': digits_sum,
        'chemin de vie (avant réduction)': reduce_number(birth.day) + reduce_number(birth.month) + reduce_number(birth.year),
    }
    found: List[Dict[str, Any]] = []
    for source, value in candidates.items():
        # Contrôle la valeur et ses étapes intermédiaires de réduction.
        seen = value
        while seen >= 10:
            if seen in KARMIC and not any(f['number'] == seen for f in found):
                found.append({'number': seen, 'source': source, 'text': KARMIC[seen]})
            seen = sum(int(c) for c in str(seen))
    return found


def lo_shu(birth: date) -> Dict[str, Any]:
    digits = [int(c) for c in birth.strftime('%d%m%Y') if c != '0']
    counts = {n: digits.count(n) for n in range(1, 10)}
    present = [n for n, c in counts.items() if c]
    missing = [n for n, c in counts.items() if not c]
    repeated = [n for n, c in counts.items() if c >= 2]
    arrows_full = [
        {'name': name, 'text': text} for nums, name, text in LOSHU_ARROWS
        if all(counts[n] for n in nums)
    ]
    arrows_empty = [
        {'name': name.replace('Flèche', 'Flèche absente'), 'text': text} for nums, name, text in LOSHU_ARROWS
        if not any(counts[n] for n in nums)
    ]
    return {
        'grid': LOSHU_GRID,
        'counts': counts,
        'present': [{'number': n, 'count': counts[n], 'text': LOSHU_DIGIT[n]} for n in present],
        'missing': [{'number': n, 'text': LOSHU_MISSING[n]} for n in missing],
        'repeated': repeated,
        'arrows': arrows_full,
        'empty_arrows': arrows_empty,
    }


def biorhythms(birth: date, today: Optional[date] = None, days: int = 90) -> Dict[str, Any]:
    today = today or date.today()
    elapsed = (today - birth).days
    periods = {'physique': 23, 'émotionnel': 28, 'intellectuel': 33}

    def value(period: int, offset: int) -> float:
        return math.sin(2 * math.pi * (elapsed + offset) / period)

    now = {k: round(value(p, 0) * 100) for k, p in periods.items()}
    peaks: Dict[str, List[str]] = {}
    critical: Dict[str, List[str]] = {}
    for k, p in periods.items():
        peaks[k], critical[k] = [], []
        for off in range(1, days + 1):
            prev, cur, nxt = value(p, off - 1), value(p, off), value(p, off + 1)
            d = today + timedelta(days=off)
            label = f'{d.day} {MONTHS_FR[d.month - 1]}'
            if cur > prev and cur >= nxt and cur > 0.9:
                peaks[k].append(label)
            if prev * cur < 0:
                critical[k].append(label)
    return {'today': now, 'peaks': peaks, 'critical': critical, 'days': days}


def build_cycles(birth_date_iso: str, today: Optional[date] = None) -> Optional[Dict[str, Any]]:
    birth = parse_birth(birth_date_iso)
    if not birth:
        return None
    today = today or date.today()
    pc = pinnacles_and_challenges(birth)
    py = personal_year(birth, today.year)
    return {
        'life_path': pc['life_path'],
        'birthday_number': reduce_number(birth.day),
        'personal_year': py,
        'personal_year_theme': THEMES[_base(py)][0],
        'personal_year_text': THEMES[_base(py)][1] + (' ' + MASTER_NOTE[py] if py in MASTER_NOTE else ''),
        'months': months_forecast(birth, today),
        'pinnacles': pc['pinnacles'],
        'challenges': pc['challenges'],
        'karmic_debts': karmic_debts(birth),
        'lo_shu': lo_shu(birth),
        'biorhythms': biorhythms(birth, today),
    }
