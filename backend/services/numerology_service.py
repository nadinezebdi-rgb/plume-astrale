"""Numerologie : calculs purs (chemin de vie, expression, intime, etc.)
Profil complet + profil profond.
"""
from datetime import datetime

NUM_DESCRIPTIONS = {
    'chemin_de_vie': {
        1: 'Leader naturel, indépendant, pionnier. Tu dois apprendre à diriger sans écraser.',
        2: 'Diplomate, collaborateur, sensible. Tu apportes paix et harmonie autour de toi.',
        3: 'Créatif, expressif, joyeux. Ta mission est de communiquer la beauté.',
        4: 'Travailleur, méthodique, fiable. Tu construis des fondations solides.',
        5: 'Aventurier, libre, curieux. Tu cherches l\'expérience et la transformation.',
        6: 'Aimant, responsable, guérisseur. Tu sers la famille et la communauté.',
        7: 'Mystique, analytique, introspectif. Tu cherches la vérité spirituelle.',
        8: 'Ambitieux, organisateur, puissant. Tu manifestes l\'abondance matérielle.',
        9: 'Humaniste, généreux, universel. Tu sers l\'humanité avec compassion.',
        11: 'Visionnaire, inspiré, médium. Tu portes une lumière spirituelle rare.',
        22: 'Bâtisseur universel. Tu réalises de grandes œuvres pour l\'humanité.',
        33: 'Maître spirituel, guérisseur ultime. Service inconditionnel à l\'amour.',
    },
    'expression': {
        1: 'Tu t\'exprimes avec autorité et originalité.',
        2: 'Tu rayonnes par ta sensibilité et ta diplomatie.',
        3: 'Ta créativité naturelle illumine ceux qui t\'entourent.',
        4: 'Ta rigueur et ta loyauté inspirent confiance.',
        5: 'Ton magnétisme et ta liberté attirent les autres.',
        6: 'Ton cœur ouvert et ton sens du devoir réconfortent.',
        7: 'Ta sagesse silencieuse impressionne ceux qui savent voir.',
        8: 'Tu inspires par ta force et ton sens des affaires.',
        9: 'Ta compassion universelle te rend lumineuse.',
        11: 'Tu illumines les autres par ton intuition.',
        22: 'Tu réalises l\'impossible avec discipline.',
        33: 'Tu guéris par ta seule présence.',
    },
    'intime': {
        1: 'Tu aspires à l\'indépendance totale et à diriger ta vie.',
        2: 'Tu rêves d\'amour pur et de partenariats harmonieux.',
        3: 'Tu vibres pour la joie, l\'art et l\'expression.',
        4: 'Tu cherches la sécurité, l\'ordre et la stabilité.',
        5: 'Tu désires liberté, voyages et expériences variées.',
        6: 'Tu rêves d\'une famille unie et d\'un foyer chaleureux.',
        7: 'Tu aspires à la connaissance profonde et au mystère.',
        8: 'Tu vises la réussite matérielle et le pouvoir.',
        9: 'Tu désires aider l\'humanité et te dévouer.',
        11: 'Tu cherches à éclairer le monde par la spiritualité.',
        22: 'Tu rêves de bâtir un héritage durable.',
        33: 'Tu aspires à servir l\'amour inconditionnel.',
    },
    'realisation': {
        1: 'Tu accompliras de grandes choses par ta volonté.',
        2: 'Ta réussite passera par la collaboration.',
        3: 'Tu rayonneras par tes créations.',
        4: 'Tu bâtiras une œuvre solide et durable.',
        5: 'Ta vie sera riche d\'expériences variées.',
        6: 'Tu seras le pilier d\'une communauté aimante.',
        7: 'Tu deviendras une référence inspirante pour les autres.',
        8: 'Tu atteindras succès matériel et reconnaissance.',
        9: 'Tu marqueras le monde par ta générosité.',
        11: 'Tu illumineras spirituellement ton entourage.',
        22: 'Tu réaliseras des projets d\'envergure mondiale.',
        33: 'Tu seras un modèle d\'amour universel.',
    },
}

LETTRES_VAL = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8,
}
VOYELLES = set('AEIOUY')


def _reduce(n: int) -> int:
    """Reduit a un seul chiffre, sauf maitres-nombres 11/22/33."""
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def _strip_accents(s: str) -> str:
    repl = {
        'à':'a','â':'a','ä':'a','é':'e','è':'e','ê':'e','ë':'e',
        'î':'i','ï':'i','ô':'o','ö':'o','ù':'u','û':'u','ü':'u',
        'ç':'c','ÿ':'y','ñ':'n',
    }
    out = ''
    for ch in s.lower():
        out += repl.get(ch, ch)
    return out.upper()


def chemin_de_vie(date_naissance: str) -> int:
    d = datetime.strptime(date_naissance, '%Y-%m-%d')
    total = sum(int(c) for c in date_naissance if c.isdigit())
    _ = d  # unused but validates date
    return _reduce(total)


def annee_personnelle(date_naissance: str) -> int:
    d = datetime.strptime(date_naissance, '%Y-%m-%d')
    annee = datetime.now().year
    total = d.day + d.month + sum(int(c) for c in str(annee))
    return _reduce(total)


def expression(prenom: str, nom: str = '') -> int:
    nom_complet = _strip_accents(f"{prenom} {nom}".strip())
    total = sum(LETTRES_VAL.get(c, 0) for c in nom_complet if c.isalpha())
    return _reduce(total)


def nombre_intime(prenom: str, nom: str = '') -> int:
    nom_complet = _strip_accents(f"{prenom} {nom}".strip())
    total = sum(LETTRES_VAL.get(c, 0) for c in nom_complet if c in VOYELLES)
    return _reduce(total)


def nombre_realisation(prenom: str, nom: str = '') -> int:
    nom_complet = _strip_accents(f"{prenom} {nom}".strip())
    total = sum(LETTRES_VAL.get(c, 0) for c in nom_complet if c.isalpha() and c not in VOYELLES)
    return _reduce(total)


def compute_complete(payload: dict) -> dict:
    prenom = payload.get('prenom', '').strip()
    nom = payload.get('nom', '').strip()
    date_naissance = payload.get('dateNaissance') or payload.get('birth_date')
    if not prenom or not date_naissance:
        raise ValueError('prenom et dateNaissance requis')

    cdv = chemin_de_vie(date_naissance)
    expr = expression(prenom, nom)
    intime = nombre_intime(prenom, nom)
    real = nombre_realisation(prenom, nom)
    ap = annee_personnelle(date_naissance)

    return {
        'success': True,
        'data': {
            'prenom': prenom,
            'chemin_de_vie': {
                'nombre': cdv,
                'description': NUM_DESCRIPTIONS['chemin_de_vie'].get(cdv, ''),
            },
            'expression': {
                'nombre': expr,
                'description': NUM_DESCRIPTIONS['expression'].get(expr, ''),
            },
            'intime': {
                'nombre': intime,
                'description': NUM_DESCRIPTIONS['intime'].get(intime, ''),
            },
            'realisation': {
                'nombre': real,
                'description': NUM_DESCRIPTIONS['realisation'].get(real, ''),
            },
            'annee_personnelle': {
                'nombre': ap,
                'description': f"Cette année est une vibration {ap} pour toi.",
            },
        },
    }


def compute_deep(payload: dict) -> dict:
    """Profil profond : ajoute defis, cycles, jour de naissance."""
    base = compute_complete(payload)
    if not base['success']:
        return base
    data = base['data']
    date_naissance = payload.get('dateNaissance') or payload.get('birth_date')
    d = datetime.strptime(date_naissance, '%Y-%m-%d')

    # Defis
    defi1 = _reduce(abs(d.month - d.day))
    defi2 = _reduce(abs(d.day - (d.year % 100)))
    defi_principal = _reduce(abs(defi1 - defi2))

    # Nombre du jour
    nombre_jour = _reduce(d.day)

    data['defis'] = {
        'mineur_1': {'nombre': defi1, 'description': f"Défi {defi1} à apprivoiser durant la première moitié de vie."},
        'mineur_2': {'nombre': defi2, 'description': f"Défi {defi2} pendant la seconde moitié de vie."},
        'principal': {'nombre': defi_principal, 'description': f"Défi central à transformer en force {defi_principal}."},
    }
    data['nombre_jour'] = {
        'nombre': nombre_jour,
        'description': f"Talent inné lié au {nombre_jour}.",
    }
    data['cycles'] = {
        'formation': _reduce(d.month),
        'productivite': _reduce(d.day),
        'recolte': _reduce(d.year),
    }
    return {'success': True, 'data': data}
