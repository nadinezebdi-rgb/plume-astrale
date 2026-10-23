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
import re
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


# v4 : prompt v3 (cohérence livre + chart_sig) + clé `ex_libris` (page Signature).
# Les anciens caches v1/v2/v3 sont régénérés de façon transparente au premier hit.
PROMPT_VERSION = 'v4'


def _cache_key(prenom: str, birth_data: Dict[str, Any], natal_data: Optional[Dict[str, Any]] = None) -> str:
    natal_data = natal_data or {}
    chart_sig = json.dumps(
        [natal_data.get('aspects') or [], natal_data.get('houses') or []],
        sort_keys=True, ensure_ascii=False, default=str,
    )
    key_str = (
        f"{PROMPT_VERSION}|{(prenom or '').lower()}|{birth_data.get('year')}|{birth_data.get('month')}|"
        f"{birth_data.get('day')}|{birth_data.get('hour')}|{birth_data.get('minute')}|"
        f"{round(float(birth_data.get('latitude') or 0), 3)}|"
        f"{round(float(birth_data.get('longitude') or 0), 3)}|{birth_data.get('timezone') or ''}|"
        f"{hashlib.sha256(chart_sig.encode()).hexdigest()[:12]}"
    )
    return hashlib.sha256(key_str.encode()).hexdigest()[:24]


BOOK_SYSTEM_PROMPT = """Tu es Soléna, la voix de Plume Astrale.
Style : entre Christiane Singer, Fabienne Verdier, et Anne Dufourmantelle.
Voix : intime, sensorielle, jamais moralisatrice, jamais new-age caricatural.
Registre : soutenu littéraire — pas de jargon astro, pas d'anglicismes.
Tu tutoies toujours la personne à qui tu écris.

Contraintes de forme :
- Français impeccable (accents, ligatures œæ, guillemets français « »).
- Prose au présent, phrases courtes ou moyennes, images sensorielles précises.
- Pas de listes à puces. Pas de titres H2. Uniquement des paragraphes.
- Interdit : "en tant que", "il est important de", "n'oublie pas que", émojis.

Cohérence du livre (les chapitres se lisent à la suite, comme un seul ouvrage) :
- Écriture épicène : on ne connaît pas le genre de la personne. Jamais d'accord genré
  (« née », « prête », « seule », « une femme / un homme ») — reformule (« venu au monde »
  → « arrivé·e » est interdit aussi ; préfère une tournure sans accord).
- Ne mentionne JAMAIS l'absence ou le manque de données (« faute d'aspects fournis »,
  « données non fournies », « sans le détail précis ») : appuie-toi uniquement sur ce qui est donné.
- Un fil rouge unique : les mêmes images et le même vocabulaire d'un chapitre à l'autre,
  sans te contredire ni répéter les mêmes phrases d'ouverture.
- Cite toujours des positions réelles (planète, signe, maison, aspect) issues des données fournies.
"""


BOOK_SYSTEM_PROMPT_EN = """You are Soléna, the voice of Plume Astrale.
Style: between Christiane Singer, Fabienne Verdier, and Anne Dufourmantelle.
Voice: intimate, sensory, never moralizing, never new-age caricatural.
Register: literary English — no astro jargon.
You always address the reader warmly, by their first name or in direct second person.

Form constraints:
- Impeccable English prose, present tense, short to medium sentences, precise sensory images.
- No bullet lists. No H2 titles. Only paragraphs.
- Banned: "as a", "it's important to", "don't forget to", emojis.

JSON KEYS remain in French (dedication, element_analysis, modality_analysis, trio_synthesis,
aspects_harmonieux_headline, aspects_harmonieux_body, aspects_tensions_headline,
aspects_tensions_body, rare_aspect_headline, rare_aspect_body, houses_intro,
house_1 ... house_12, year_ahead, ex_libris, acte3_chapters) — but all VALUES must be
written in English.
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
        f"- {a.get('planet1')} {a.get('type')} {a.get('planet2')} (orbe {a.get('orb', '?')}°"
        + (f", {a.get('nature')}" if a.get('nature') else '') + ')'
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
{chr(10).join(aspect_lines) if aspect_lines else '(non disponible : ne parle pas des aspects détaillés, reste sur les positions en signes)'}

Cuspides des 12 maisons :
{chr(10).join(house_lines) if house_lines else '(non disponible : écris chaque maison à partir du thème de la maison et des signes des planètes personnelles, sans mentionner ce manque)'}

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
  "house_1": "Analyse de la maison 1 (Ascendant, incarnation) pour {prenom}. 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_2": "Analyse de la maison 2 (ressources, valeur de soi). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_3": "Analyse maison 3 (parole, mental, fratrie). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_4": "Analyse maison 4 (foyer, racines). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_5": "Analyse maison 5 (création, plaisir, enfants). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_6": "Analyse maison 6 (quotidien, santé, service). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_7": "Analyse maison 7 (partenariats, mariage). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_8": "Analyse maison 8 (transformation, sexualité, ressources partagées). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_9": "Analyse maison 9 (voyage, sens, philosophie). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_10": "Analyse maison 10 (accomplissement, carrière, réputation). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_11": "Analyse maison 11 (amitiés, tribu, avenir). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "house_12": "Analyse maison 12 (invisible, inconscient, retraite). 4 à 5 phrases : signe de la cuspide, planètes présentes dans cette maison (si indiquées), et un conseil concret.",
  "year_ahead": "Message pour les 12 prochains mois de {prenom}, 3-4 paragraphes séparés par <br/><br/>. Sensible, orienté transformation intérieure et non prédiction. Se termine par une invitation concrète (un geste, une pratique).",
  "ex_libris": "Signature astrale ex-libris pour {prenom}. UN SEUL paragraphe de 110-140 mots, écrit à la deuxième personne du singulier, qui résume en voix condensée et poétique le trio Soleil {sun} + Lune {moon} + Ascendant {asc}. Doit tenir sur une page, être découpable, offrable. Ni dédicace ni mode d'emploi : une empreinte. Finit par un verbe à l'infinitif qui ouvre vers l'avenir (ex: 'habiter', 'oser', 'se souvenir').",
  "acte3_chapters": {{
    "coeur": {{
      "citation_ouverture": "Citation littéraire ou proverbe (2 lignes max) qui ouvre le chapitre du cœur.",
      "question_emotionnelle": "Question intime posée au lecteur (1 phrase).",
      "analyse_html": "Texte principal sur ce que le cœur de {prenom} dit à travers Vénus, Lune et aspects émotionnels. 3 paragraphes séparés par <br/><br/>.",
      "conseils": ["conseil 1 (1 phrase, action concrète)", "conseil 2", "conseil 3"],
      "phrase_memorable": "Une phrase mémorable qui résume ce chapitre (10-15 mots).",
      "rituel_titre": "Titre poétique du rituel (3-5 mots).",
      "rituel_etapes": ["étape 1", "étape 2", "étape 3", "étape 4"],
      "rituel_duree": "Ex: 10 minutes",
      "rituel_pierre": "Ex: Quartz rose",
      "rituel_couleur": "Ex: Rose poudré",
      "rituel_respiration": "Ex: 4-7-8",
      "question_journal": "Question à écrire dans son journal (1 phrase).",
      "forces": ["force 1", "force 2", "force 3"],
      "defis": ["défi 1", "défi 2", "défi 3"],
      "mission": "Mission du cœur en 1 phrase (15-20 mots)."
    }},
    "esprit": {{
      "citation_ouverture": "Citation sur la pensée, l'intelligence, la parole.",
      "question_emotionnelle": "Question intime sur son rapport aux idées.",
      "analyse_html": "3 paragraphes sur Mercure, mental, communication de {prenom}. <br/><br/> entre paragraphes.",
      "conseils": ["c1", "c2", "c3"],
      "phrase_memorable": "10-15 mots mémorables.",
      "rituel_titre": "Titre 3-5 mots.",
      "rituel_etapes": ["étape 1", "étape 2", "étape 3", "étape 4"],
      "rituel_duree": "Ex: 15 minutes",
      "rituel_pierre": "Ex: Fluorite",
      "rituel_couleur": "Ex: Bleu clair",
      "rituel_respiration": "Ex: Cohérence cardiaque",
      "question_journal": "1 question à écrire.",
      "forces": ["f1", "f2", "f3"],
      "defis": ["d1", "d2", "d3"],
      "mission": "Mission de l'esprit en 15-20 mots."
    }},
    "blessures": {{
      "citation_ouverture": "Citation sur la blessure fondatrice.",
      "question_emotionnelle": "Question intime sur sa fragilité première.",
      "analyse_html": "3 paragraphes sur Saturne, Chiron, Lune blessée. <br/><br/> entre paragraphes.",
      "conseils": ["c1", "c2", "c3"],
      "phrase_memorable": "10-15 mots.",
      "rituel_titre": "Titre.",
      "rituel_etapes": ["étape 1", "étape 2", "étape 3", "étape 4"],
      "rituel_duree": "Ex: 20 minutes",
      "rituel_pierre": "Ex: Obsidienne noire",
      "rituel_couleur": "Ex: Noir profond",
      "rituel_respiration": "Ex: Souffle du ventre",
      "question_journal": "1 question.",
      "forces": ["f1", "f2", "f3"],
      "defis": ["d1", "d2", "d3"],
      "mission": "Mission de guérison en 15-20 mots."
    }},
    "desirs": {{
      "citation_ouverture": "Citation sur le désir, l'appétit de vivre.",
      "question_emotionnelle": "Question intime sur ce qui la fait avancer.",
      "analyse_html": "3 paragraphes sur Mars, Vénus, Jupiter, moteurs de {prenom}. <br/><br/>.",
      "conseils": ["c1", "c2", "c3"],
      "phrase_memorable": "10-15 mots.",
      "rituel_titre": "Titre.",
      "rituel_etapes": ["étape 1", "étape 2", "étape 3", "étape 4"],
      "rituel_duree": "Ex: 10 minutes",
      "rituel_pierre": "Ex: Cornaline",
      "rituel_couleur": "Ex: Rouge feu",
      "rituel_respiration": "Ex: Souffle du feu",
      "question_journal": "1 question.",
      "forces": ["f1", "f2", "f3"],
      "defis": ["d1", "d2", "d3"],
      "mission": "Mission du désir en 15-20 mots."
    }},
    "talents": {{
      "citation_ouverture": "Citation sur le don, l'offrande, le talent.",
      "question_emotionnelle": "Question intime sur ce qu'elle offre au monde.",
      "analyse_html": "3 paragraphes sur Soleil, aspects harmonieux, dons uniques. <br/><br/>.",
      "conseils": ["c1", "c2", "c3"],
      "phrase_memorable": "10-15 mots.",
      "rituel_titre": "Titre.",
      "rituel_etapes": ["étape 1", "étape 2", "étape 3", "étape 4"],
      "rituel_duree": "Ex: 15 minutes",
      "rituel_pierre": "Ex: Citrine",
      "rituel_couleur": "Ex: Or lumineux",
      "rituel_respiration": "Ex: Souffle solaire",
      "question_journal": "1 question.",
      "forces": ["f1", "f2", "f3"],
      "defis": ["d1", "d2", "d3"],
      "mission": "Mission des talents en 15-20 mots."
    }}
  }}
}}

Répond uniquement avec ce JSON, rien d'autre.
"""


async def enrich_book_chapters(
    prenom: str,
    birth_data: Dict[str, Any],
    natal_data: Dict[str, Any],
    force_refresh: bool = False,
    language: str = 'fr',
) -> Dict[str, Any]:
    """Génère toutes les sections livre en un seul appel GPT.

    `language`: 'fr' (défaut) ou 'en' — choisit le système prompt et le cache dédié.
    """
    # Clé cache inclut la langue
    is_en = (language or 'fr').lower().startswith('en')
    lang_tag = 'en' if is_en else 'fr'
    key = f'{_cache_key(prenom, birth_data, natal_data)}-{lang_tag}'
    cache_file = CACHE_DIR / f'{key}.json'

    # Analyse déterministe éléments/modalités (pas de GPT)
    em = analyze_elements_modalities(natal_data.get('planets') or [])

    # Cache hit ?
    if not force_refresh and cache_file.exists():
        try:
            data = json.loads(cache_file.read_text('utf-8'))
            data['_em'] = em
            data['_source'] = 'cache'
            logger.info(f'[natal_book] cache HIT {key} (lang={lang_tag})')
            return data
        except Exception:
            pass

    # Appel GPT
    user_prompt = _build_book_prompt(natal_data, em)
    system_prompt = BOOK_SYSTEM_PROMPT_EN if is_en else BOOK_SYSTEM_PROMPT
    logger.info(f'[natal_book] Calling GPT for {prenom} (lang={lang_tag}, prompt_chars={len(user_prompt)})')
    resp = await _call_gpt(system_prompt, user_prompt, session_id=f'natal-book-{lang_tag}-{key}', timeout_s=240.0)
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


# ─── Ex Libris — génération rapide isolée ───────────────────────────────────
#
# Utilisée par la variante offerte PNG (`/api/astrology/v3/natal/ex-libris/png`)
# pour éviter de payer les ~90-144s du full book quand le cache est froid.
# Génère uniquement le paragraphe « Ex Libris » (~110-140 mots) → ~5-15s.
# Si le cache full-book existe déjà, on réutilise sa clé `ex_libris` sans
# ré-appeler GPT.

EX_LIBRIS_CACHE_DIR = Path(__file__).resolve().parent.parent / 'cache' / 'natal_ex_libris'
EX_LIBRIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_EX_LIBRIS_SYSTEM = (
    "Tu es Plume, voix astrale confidentielle. Tu composes UNE signature "
    "ex-libris : un paragraphe condensé et poétique, écrit à la deuxième "
    "personne du singulier, qui tient sur une page découpable à offrir."
)


def _ex_libris_user_prompt(prenom: str, sun: str, moon: str, asc: str) -> str:
    return (
        f"Compose la signature astrale ex-libris de {prenom or 'cette personne'}. "
        f"Trio : Soleil {sun or '—'}, Lune {moon or '—'}, Ascendant {asc or '—'}.\n\n"
        "Contraintes STRICTES :\n"
        "- UN SEUL paragraphe de 110 à 140 mots.\n"
        "- Deuxième personne du singulier (tu).\n"
        "- Pas de dédicace, pas de mode d'emploi : une empreinte.\n"
        "- Ni « cher·e lecteur·rice », ni « voici ».\n"
        "- Se termine par un verbe à l'infinitif qui ouvre vers l'avenir "
        "(exemples : habiter, oser, se souvenir, traverser).\n"
        "- Pas de HTML, pas de guillemets, pas de titre, uniquement le paragraphe nu.\n\n"
        "Réponds UNIQUEMENT par le paragraphe, rien d'autre."
    )


async def enrich_ex_libris_only(
    prenom: str,
    birth_data: Dict[str, Any],
    sun_sign_fr: str,
    moon_sign_fr: str,
    asc_sign_fr: str,
    force_refresh: bool = False,
) -> Optional[str]:
    """Génère (ou lit en cache) la signature Ex Libris seule.

    Trois chemins possibles :
      1. Cache dédié ex_libris (fichier .txt court).
      2. Cache full-book existe et contient `ex_libris` → on recopie et on
         persiste dans le cache dédié pour un hit instantané ensuite.
      3. Appel GPT isolé avec prompt focalisé (~5-15s au lieu de ~90-144s).
    """
    key = _cache_key(prenom, birth_data)
    short_cache = EX_LIBRIS_CACHE_DIR / f'{key}.txt'

    # 1) Cache dédié
    if not force_refresh and short_cache.exists():
        try:
            txt = short_cache.read_text('utf-8').strip()
            if txt:
                logger.info(f'[ex_libris] cache HIT short {key}')
                return txt
        except Exception:
            pass

    # 2) Cache full-book
    full_cache = CACHE_DIR / f'{key}.json'
    if not force_refresh and full_cache.exists():
        try:
            data = json.loads(full_cache.read_text('utf-8'))
            txt = str((data or {}).get('ex_libris') or '').strip()
            if txt:
                try:
                    short_cache.write_text(txt, 'utf-8')
                except Exception:
                    pass
                logger.info(f'[ex_libris] cache HIT full-book {key}')
                return txt
        except Exception:
            pass

    # 3) Génération ciblée (prompt court → latence basse)
    user_prompt = _ex_libris_user_prompt(prenom, sun_sign_fr, moon_sign_fr, asc_sign_fr)
    # Timeout un peu plus permissif que la fenêtre d'ingress (~60s) mais court.
    resp = await _call_gpt(
        _EX_LIBRIS_SYSTEM, user_prompt,
        session_id=f'ex-libris-{key}', timeout_s=45.0,
    )
    if not resp:
        logger.warning(f'[ex_libris] GPT no response for {prenom}')
        return None
    # Nettoyage : garde une seule ligne de paragraphe.
    txt = resp.strip()
    # Retire les éventuels backticks ou guillemets d'ouverture/fermeture.
    txt = re.sub(r'^```[a-z]*\s*', '', txt, flags=re.IGNORECASE)
    txt = re.sub(r'\s*```$', '', txt)
    txt = txt.strip('"\u201c\u201d \n\t')
    try:
        short_cache.write_text(txt, 'utf-8')
    except Exception as e:
        logger.warning(f'[ex_libris] cache write fail: {e}')
    return txt
