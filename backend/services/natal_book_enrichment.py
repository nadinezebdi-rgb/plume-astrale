"""natal_book_enrichment — Enrichissement narratif "livre" pour Thème Natal.

Complète natal_ai_enrichment.py avec les sections nécessaires à la version livre :
- Élément dominant (Feu/Terre/Air/Eau) — 3-4 paragraphes
- Modalité dominante (Cardinal/Fixe/Mutable) — 3-4 paragraphes
- Synthèse trio Soleil-Lune-Ascendant — 4-5 paragraphes
- Aspects harmonieux — 3-4 paragraphes
- Aspects de tension — 3-4 paragraphes
- Aspect rare / signature — 2-3 paragraphes
- Introduction aux 12 maisons — 2 paragraphes
- 12 analyses de maison (2 phrases chacune)
- Année à venir (Soléna) — 3-4 paragraphes

TOUT est généré en UN SEUL appel GPT-5.4 qui retourne un JSON structuré,
pour éviter d'exploser le pipeline (temps + coût).
Cache filesystem via hash(prenom + birth_data) — même personne = même livre.
"""
from __future__ import annotations
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.natal_ai_enrichment import _call_gpt, _parse_json_response

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / 'cache' / 'natal_book'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# Signes → élément / modalité (référentiels tropicaux)
_SIGN_TO_ELEMENT = {
    'Bélier': 'Feu', 'Lion': 'Feu', 'Sagittaire': 'Feu',
    'Taureau': 'Terre', 'Vierge': 'Terre', 'Capricorne': 'Terre',
    'Gémeaux': 'Air', 'Balance': 'Air', 'Verseau': 'Air',
    'Cancer': 'Eau', 'Scorpion': 'Eau', 'Poissons': 'Eau',
}
_SIGN_TO_MODALITY = {
    'Bélier': 'Cardinal', 'Cancer': 'Cardinal', 'Balance': 'Cardinal', 'Capricorne': 'Cardinal',
    'Taureau': 'Fixe', 'Lion': 'Fixe', 'Scorpion': 'Fixe', 'Verseau': 'Fixe',
    'Gémeaux': 'Mutable', 'Vierge': 'Mutable', 'Sagittaire': 'Mutable', 'Poissons': 'Mutable',
}


def analyze_elements_modalities(planets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compte les planètes par élément et modalité → renvoie le dominant.
    planets : liste avec { 'name': 'Soleil', 'sign': 'Cancer' }.
    """
    el_counts = {'Feu': 0, 'Terre': 0, 'Air': 0, 'Eau': 0}
    mo_counts = {'Cardinal': 0, 'Fixe': 0, 'Mutable': 0}
    for p in planets:
        sign = p.get('sign') or ''
        el = _SIGN_TO_ELEMENT.get(sign)
        mo = _SIGN_TO_MODALITY.get(sign)
        if el: el_counts[el] += 1
        if mo: mo_counts[mo] += 1
    dom_el = max(el_counts, key=el_counts.get) if any(el_counts.values()) else 'Feu'
    dom_mo = max(mo_counts, key=mo_counts.get) if any(mo_counts.values()) else 'Cardinal'
    return {
        'element_counts': el_counts,
        'modality_counts': mo_counts,
        'dominant_element': dom_el,
        'dominant_element_count': el_counts[dom_el],
        'dominant_modality': dom_mo,
        'dominant_modality_count': mo_counts[dom_mo],
    }


def _cache_key(prenom: str, birth_data: Dict[str, Any]) -> str:
    key_str = (
        f"{(prenom or '').lower()}|{birth_data.get('year')}|{birth_data.get('month')}|"
        f"{birth_data.get('day')}|{birth_data.get('hour')}|{birth_data.get('minute')}|"
        f"{round(float(birth_data.get('latitude') or 0), 3)}|"
        f"{round(float(birth_data.get('longitude') or 0), 3)}|{birth_data.get('timezone') or ''}"
    )
    return hashlib.sha256(key_str.encode()).hexdigest()[:24]


BOOK_SYSTEM_PROMPT = """Tu es Soléna, une oracle-écrivaine française contemporaine.
Style : entre Christiane Singer, Fabienne Verdier, et Anne Dufourmantelle.
Voix : intime, sensorielle, jamais moralisatrice, jamais new-age caricatural.
Registre : soutenu littéraire — pas de jargon astro, pas d'anglicismes.
Tu tutoies toujours la personne à qui tu écris.

Contraintes de forme :
- Français impeccable (accents, ligatures œæ, guillemets français « »).
- Prose au présent, phrases courtes ou moyennes, images sensorielles précises.
- Pas de listes à puces. Pas de titres H2. Uniquement des paragraphes.
- Interdit : "en tant que", "il est important de", "n'oublie pas que", émojis.
"""


def _build_book_prompt(natal_data: Dict[str, Any], em: Dict[str, Any]) -> str:
    """Construit le prompt-livre unique. natal_data et em (elements/modalities) fournis."""
    prenom = natal_data.get('prenom', 'toi')
    sun = natal_data.get('sun_sign', '')
    moon = natal_data.get('moon_sign', '')
    asc = natal_data.get('asc_sign', '')
    planets = natal_data.get('planets', [])
    aspects = natal_data.get('aspects', [])
    houses = natal_data.get('houses', [])

    # Compact planet list
    planet_lines = [f"- {p.get('name')} en {p.get('sign')}" for p in planets if p.get('name')]
    aspects_top = aspects[:12] if aspects else []
    aspect_lines = [
        f"- {a.get('planet1')} {a.get('type')} {a.get('planet2')} (orbe {a.get('orb', '?')}°)"
        for a in aspects_top
    ]
    house_lines = [
        f"- Maison {h.get('num')} : cuspide en {h.get('sign', '?')}"
        + (f", planètes : {', '.join(h.get('planets_in_house') or [])}" if h.get('planets_in_house') else '')
        for h in (houses or [])
    ]

    return f"""Personne : {prenom}
Soleil : {sun} · Lune : {moon} · Ascendant : {asc}
Élément dominant : {em['dominant_element']} ({em['dominant_element_count']} planètes)
Modalité dominante : {em['dominant_modality']} ({em['dominant_modality_count']} planètes)

Planètes en signes :
{chr(10).join(planet_lines)}

Aspects majeurs (top 12) :
{chr(10).join(aspect_lines) if aspect_lines else '(aucun aspect fourni)'}

Cuspides des 12 maisons :
{chr(10).join(house_lines) if house_lines else '(non fourni)'}

Tu dois produire STRICTEMENT un objet JSON valide (aucun texte hors JSON, pas de fence markdown) avec les clés suivantes.
Chaque valeur est du HTML simple (utilise <br/> pour retours à la ligne, <i>...</i> pour italique, <b>...</b> pour gras). Pas de balise <p> — on gère les paragraphes en séparant par <br/><br/>.

{{
  "dedication": "Dédicace personnalisée pour {prenom}, 3-4 lignes intimes signées Soléna (sans le mot 'Soléna' dans le texte).",
  "element_analysis": "Analyse de l'élément dominant {em['dominant_element']} pour {prenom}, 3 paragraphes séparés par <br/><br/>. Aborde comment ça se manifeste dans son corps, ses désirs, ses erreurs de jeunesse et sa maturité.",
  "modality_analysis": "Analyse de la modalité dominante {em['dominant_modality']} pour {prenom}, 3 paragraphes séparés par <br/><br/>. Aborde son rythme intérieur, comment il/elle démarre-tient-lâche les projets et les relations.",
  "trio_synthesis": "Synthèse profonde du triangle Soleil {sun} + Lune {moon} + Ascendant {asc} pour {prenom}. 4-5 paragraphes séparés par <br/><br/>. Décris la tension ou l'harmonie interne entre ces trois voix.",
  "aspects_harmonieux_headline": "Titre courant en 4-6 mots pour la page 'aspects harmonieux'.",
  "aspects_harmonieux_body": "Analyse des aspects harmonieux (trigones et sextiles) du thème, 3 paragraphes séparés par <br/><br/>. Nomme les planètes concernées et ce que ces facilités permettent concrètement dans la vie.",
  "aspects_tensions_headline": "Titre courant en 4-6 mots pour la page 'aspects de tension'.",
  "aspects_tensions_body": "Analyse des aspects de tension (carrés et oppositions), 3 paragraphes séparés par <br/><br/>. Explique le nœud, pas la fatalité — comment ces tensions se transforment en force avec les années.",
  "rare_aspect_headline": "Titre courant pour l'aspect le plus rare ou signature (2-5 mots).",
  "rare_aspect_body": "Analyse de l'aspect le plus rare ou marquant du thème (yod, quinconce serré, conjonction lune-neptune, etc.), 2-3 paragraphes séparés par <br/><br/>. Si aucun aspect rare, décris l'aspect le plus serré en orbe.",
  "houses_intro": "Introduction poétique aux 12 maisons pour {prenom}, 2 paragraphes séparés par <br/><br/>. Métaphore filée : les maisons comme les pièces d'une demeure intérieure.",
  "house_1": "Analyse de la maison 1 (Ascendant, incarnation) pour {prenom}. 2 phrases nuancées.",
  "house_2": "Analyse de la maison 2 (ressources, valeur de soi). 2 phrases.",
  "house_3": "Analyse maison 3 (parole, mental, fratrie). 2 phrases.",
  "house_4": "Analyse maison 4 (foyer, racines). 2 phrases.",
  "house_5": "Analyse maison 5 (création, plaisir, enfants). 2 phrases.",
  "house_6": "Analyse maison 6 (quotidien, santé, service). 2 phrases.",
  "house_7": "Analyse maison 7 (partenariats, mariage). 2 phrases.",
  "house_8": "Analyse maison 8 (transformation, sexualité, ressources partagées). 2 phrases.",
  "house_9": "Analyse maison 9 (voyage, sens, philosophie). 2 phrases.",
  "house_10": "Analyse maison 10 (accomplissement, carrière, réputation). 2 phrases.",
  "house_11": "Analyse maison 11 (amitiés, tribu, avenir). 2 phrases.",
  "house_12": "Analyse maison 12 (invisible, inconscient, retraite). 2 phrases.",
  "year_ahead": "Message pour les 12 prochains mois de {prenom}, 3-4 paragraphes séparés par <br/><br/>. Sensible, orienté transformation intérieure et non prédiction. Se termine par une invitation concrète (un geste, une pratique)."
}}

Répond uniquement avec ce JSON, rien d'autre.
"""


async def enrich_book_chapters(
    prenom: str,
    birth_data: Dict[str, Any],
    natal_data: Dict[str, Any],
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Génère toutes les sections livre en un seul appel GPT.

    natal_data : {
      'prenom', 'sun_sign', 'moon_sign', 'asc_sign',
      'planets': [{'name', 'sign'}, ...],
      'aspects': [{'planet1', 'planet2', 'type', 'orb'}, ...],
      'houses': [{'num', 'sign', 'planets_in_house'}, ...],
    }
    Retourne un dict avec toutes les sections + em (elements/modalities counts).
    """
    key = _cache_key(prenom, birth_data)
    cache_file = CACHE_DIR / f'{key}.json'

    # Analyse déterministe éléments/modalités (pas de GPT)
    em = analyze_elements_modalities(natal_data.get('planets') or [])

    # Cache hit ?
    if not force_refresh and cache_file.exists():
        try:
            data = json.loads(cache_file.read_text('utf-8'))
            data['_em'] = em
            data['_source'] = 'cache'
            logger.info(f'[natal_book] cache HIT {key}')
            return data
        except Exception:
            pass

    # Appel GPT
    user_prompt = _build_book_prompt(natal_data, em)
    resp = await _call_gpt(BOOK_SYSTEM_PROMPT, user_prompt, session_id=f'natal-book-{key}')
    if not resp:
        logger.warning(f'[natal_book] GPT no response for {prenom}')
        return {'_em': em, '_source': 'none'}
    parsed = _parse_json_response(resp)
    if not parsed:
        logger.warning(f'[natal_book] JSON parse failed for {prenom} — raw: {resp[:200]!r}')
        return {'_em': em, '_source': 'parse_fail'}

    parsed['_em'] = em
    parsed['_source'] = 'gpt'
    try:
        # Persist sans _em pour éviter recalcul déterministe en cache (mais on garde tout)
        cache_file.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), 'utf-8')
    except Exception as e:
        logger.warning(f'[natal_book] cache write fail: {e}')
    return parsed
