"""
Tirage Complet 78 cartes — Marseille étendu (22 Majeurs + 56 Mineurs).

Format :
  - Pioche aléatoire parmi les 78 cartes (sans remise)
  - Spread personnalisable (3, 5, 7 cartes)
  - Format de sortie homogène avec `tarot_premium.tirage_marseille_question`
    pour pouvoir réutiliser le PDF et le composant frontend.

L'IA (`enrich_narrative.enrich_and_ask`) enrichit chaque interprétation.
"""
from __future__ import annotations
import hashlib
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.tarot_premium import ARCANES_MAJEURS, DOMAINES_QUESTIONS
from services.deck_78_mineurs import ALL_MINEURS

# ──────────────────────────────────────────────────────────────────────
# Positions pour 3 spreads (3, 5, 7 cartes)
# ──────────────────────────────────────────────────────────────────────

SPREADS: Dict[int, List[Dict[str, str]]] = {
    3: [
        {'nom': 'Passé', 'description': 'Ce qui a influencé la situation'},
        {'nom': 'Présent', 'description': "L'énergie actuelle de la question"},
        {'nom': 'Futur', 'description': "L'évolution probable"},
    ],
    5: [
        {'nom': 'Fondement', 'description': 'Les racines de la situation'},
        {'nom': 'Passé', 'description': "Ce qui est à l'œuvre récemment"},
        {'nom': 'Présent', 'description': "La situation telle qu'elle est"},
        {'nom': 'Futur proche', 'description': "L'évolution dans les semaines à venir"},
        {'nom': 'Résultat', 'description': "L'issue probable si rien ne change"},
    ],
    7: [
        {'nom': 'Vous aujourd\'hui', 'description': 'Votre état intérieur'},
        {'nom': 'Ce qui vous bloque', 'description': 'Le défi actuel'},
        {'nom': 'Ce qui vous soutient', 'description': 'Vos alliés visibles ou invisibles'},
        {'nom': 'Racines passées', 'description': "Ce qui a semé la situation"},
        {'nom': 'Chemin présent', 'description': "La voie qui s'ouvre maintenant"},
        {'nom': 'Avenir proche', 'description': "L'horizon à 3-6 mois"},
        {'nom': 'Conseil des Arcanes', 'description': "Ce que les cartes vous disent de faire"},
    ],
}


# ──────────────────────────────────────────────────────────────────────
# Deck complet : 22 Majeurs + 56 Mineurs
# ──────────────────────────────────────────────────────────────────────

def _normalize_major(num: int, arcane: Dict) -> Dict:
    """Harmonise un Majeur au format Mineur (sans toucher au dict original)."""
    return {
        'nom': arcane['nom'],
        'suite': 'Arcane Majeur',
        'rang': f"Arcane {num}",
        'numero': num,
        'mots_cles': arcane.get('mots_cles', []),
        'element': arcane.get('element', ''),
        'planete': arcane.get('planete', ''),
        'couleur': arcane.get('couleur', '#C9A24B'),
        'symbole': arcane.get('symbole', '✦'),
        'description': arcane.get('description', ''),
        'droit': arcane.get('droit', {}),
        'renverse': arcane.get('renverse', {}),
        'is_major': True,
    }


ALL_MAJEURS: List[Dict] = [_normalize_major(num, a) for num, a in ARCANES_MAJEURS.items()]
ALL_78: List[Dict] = ALL_MAJEURS + [{**c, 'is_major': False} for c in ALL_MINEURS]
assert len(ALL_78) == 78, f"Deck doit avoir 78 cartes, trouvé {len(ALL_78)}"


# ──────────────────────────────────────────────────────────────────────
# Tirage
# ──────────────────────────────────────────────────────────────────────

def tirage_complet_78(
    question: str,
    domaine: str = 'general',
    nb_cartes: int = 5,
    seed: Optional[str] = None,
) -> Dict[str, Any]:
    """Tire `nb_cartes` cartes (3, 5 ou 7) parmi les 78, avec orientation aléatoire.

    Format homogène avec `tirage_marseille_question` : `cartes`, `synthese`,
    `conseil_final`, `question`, `domaine`, `date`, `type`.
    """
    if nb_cartes not in SPREADS:
        nb_cartes = 5

    if seed:
        random.seed(int(hashlib.blake2b(seed.encode(), digest_size=16).hexdigest(), 16) % (2**32))
    else:
        random.seed()

    # Tirage sans remise parmi les 78
    tirage = random.sample(ALL_78, nb_cartes)
    orientations = [random.choice(['droit', 'renverse']) for _ in range(nb_cartes)]
    positions = SPREADS[nb_cartes]
    domaine_key = domaine if domaine in ('amour', 'travail') else 'general'

    cartes: List[Dict[str, Any]] = []
    for i, (base, orient) in enumerate(zip(tirage, orientations)):
        interp_bloc = base.get(orient, {}) if isinstance(base.get(orient), dict) else {}
        interp_raw = interp_bloc.get(domaine_key) or interp_bloc.get('general') or ''
        conseil = interp_bloc.get('conseil') or ''
        pos = positions[i]
        # Pour les Mineurs, les interprétations sont parfois très courtes
        # (<20 chars) ; on les étoffe avec les mots-clés et la position pour
        # garantir à l'IA (enrich_and_ask) un contexte > 20 chars.
        mots = base.get('mots_cles', [])
        if len(interp_raw) < 60 and (mots or base.get('description')):
            mots_part = ', '.join(mots[:4]) if mots else ''
            desc_part = base.get('description', '')
            interp = f"{interp_raw} En position « {pos['nom']} », {base['nom']} {('(renversée) ' if orient == 'renverse' else '')}" \
                     f"évoque les énergies de {mots_part}. {desc_part}".strip()
        else:
            interp = interp_raw
        cartes.append({
            'position': pos['nom'],
            'position_description': pos['description'],
            'nom': base['nom'],
            'suite': base.get('suite', ''),
            'rang': base.get('rang', ''),
            'is_major': base.get('is_major', False),
            'orientation': orient,
            'orientation_fr': 'Droit' if orient == 'droit' else 'Renversé',
            'mots_cles': base.get('mots_cles', []),
            'element': base.get('element', ''),
            'planete': base.get('planete', ''),
            'couleur': base.get('couleur', '#C9A24B'),
            'symbole': base.get('symbole', '✦'),
            'description_arcane': base.get('description', ''),
            'interpretation': interp,
            'conseil': conseil,
        })

    # Synthèse (sera enrichie par IA au niveau endpoint)
    synthese = _generer_synthese_78(cartes, question, domaine)
    conseil_final = _generer_conseil_final_78(cartes, domaine)

    return {
        'type': 'tirage_complet_78',
        'nb_cartes': nb_cartes,
        'question': question,
        'domaine': DOMAINES_QUESTIONS.get(domaine, DOMAINES_QUESTIONS['general']),
        'cartes': cartes,
        'synthese': synthese,
        'conseil_final': conseil_final,
        'date': datetime.now().isoformat(),
    }


def _generer_synthese_78(cartes: List[Dict], question: str, domaine: str) -> Dict[str, Any]:
    """Résumé lisible (sera enrichi par l'IA ensuite)."""
    droits = sum(1 for c in cartes if c['orientation'] == 'droit')
    total = len(cartes)
    tendance = 'favorable' if droits * 2 > total else 'nuancée' if droits * 2 == total else 'à travailler'

    # Mix majeurs / mineurs
    majeurs = [c for c in cartes if c.get('is_major')]
    mineurs = [c for c in cartes if not c.get('is_major')]

    # Élément dominant
    elements = [c.get('element') for c in cartes if c.get('element')]
    if elements:
        element_dominant = max(set(elements), key=elements.count)
    else:
        element_dominant = 'Mixte'

    # Suite dominante (chez les mineurs)
    suites_mineurs = [c.get('suite') for c in mineurs if c.get('suite')]
    suite_dom = max(set(suites_mineurs), key=suites_mineurs.count) if suites_mineurs else None

    fil = (
        f"Votre tirage mêle {len(majeurs)} arcane{'s' if len(majeurs) > 1 else ''} "
        f"majeur{'s' if len(majeurs) > 1 else ''} et {len(mineurs)} arcane{'s' if len(mineurs) > 1 else ''} "
        f"mineur{'s' if len(mineurs) > 1 else ''}. "
    )
    if majeurs:
        fil += f"Les Majeurs ({', '.join(c['nom'] for c in majeurs)}) marquent les forces structurantes à l'œuvre. "
    if suite_dom:
        fil += f"La couleur dominante des Mineurs est {suite_dom}, soulignant l'importance de ce champ dans votre vie en ce moment. "
    fil += f"L'énergie globale est {tendance}."

    return {
        'tendance_generale': tendance,
        'nb_droites': droits,
        'nb_renversees': total - droits,
        'element_dominant': element_dominant,
        'suite_dominante': suite_dom or 'équilibrée',
        'nb_majeurs': len(majeurs),
        'nb_mineurs': len(mineurs),
        'fil_conducteur': fil,
    }


def _generer_conseil_final_78(cartes: List[Dict], domaine: str) -> str:
    """Conseil basé sur la dernière carte (position finale)."""
    if not cartes:
        return ''
    derniere = cartes[-1]
    conseil = derniere.get('conseil') or ''
    nom = derniere.get('nom', 'La dernière carte')
    orient = derniere.get('orientation_fr', '').lower()
    return (
        f"{nom} ({orient}) conclut votre tirage. {conseil} "
        "Prenez cette parole comme une graine : plantez-la dans votre quotidien et observez ce qui germe."
    )
