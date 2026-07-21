"""
natal_ai_enrichment — Enrichissement AI Thème Natal Ultra.

Pipeline :
  1. API astrology-api.io v3 → 73 interprétations riches (anglais)
     • 10 planètes en signes (Sun/Moon/Mercury/Venus/Mars/Jupiter/Saturn/
       Uranus/Neptune/Pluto)
     • Ascendant
     • Aspects majeurs (conjonction, opposition, trigone, carré, sextile)
     • Maisons + dignités
  2. On sélectionne le contenu impactant (planètes + top aspects par orbe serré)
  3. GPT-5.4 traduit en français ET reformule en voix Soléna
  4. Cache filesystem (24 chars sha256) — évite de repayer 2× la même personne
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / 'cache' / 'natal_ai'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Planètes à extraire dans l'ordre du PDF (Ultra = 10 planètes + Ascendant)
PLANET_ORDER = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn',
    'Uranus', 'Neptune', 'Pluto',
    'Ascendant',
]

# Mapping planet EN → clé JSON française
PLANET_KEY_FR = {
    'Sun': 'soleil', 'Moon': 'lune', 'Mercury': 'mercure',
    'Venus': 'venus', 'Mars': 'mars', 'Jupiter': 'jupiter',
    'Saturn': 'saturne', 'Uranus': 'uranus',
    'Neptune': 'neptune', 'Pluto': 'pluton',
    'Ascendant': 'ascendant',
}

# Mapping planet EN → nom français pour le PDF
PLANET_NAME_FR = {
    'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure',
    'Venus': 'Vénus', 'Mars': 'Mars', 'Jupiter': 'Jupiter',
    'Saturn': 'Saturne', 'Uranus': 'Uranus',
    'Neptune': 'Neptune', 'Pluto': 'Pluton',
    'Ascendant': 'Ascendant',
}


# ─────────────────────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────────────────────
def _cache_key(prenom: str, birth_data: Dict[str, Any], tier: str = 'ultra') -> str:
    bd_str = json.dumps({
        't': tier,
        'p': (prenom or '').lower().strip(),
        'd': birth_data.get('day'), 'm': birth_data.get('month'), 'y': birth_data.get('year'),
        'h': birth_data.get('hour'), 'mn': birth_data.get('minute') or birth_data.get('min'),
        'lat': round(birth_data.get('latitude', 0) or 0, 3),
        'lon': round(birth_data.get('longitude', 0) or 0, 3),
    }, sort_keys=True)
    return hashlib.sha256(bd_str.encode()).hexdigest()[:24]


def _cache_read(key: str) -> Optional[Dict]:
    f = CACHE_DIR / f'{key}.json'
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding='utf-8'))
    except Exception:
        return None


def _cache_write(key: str, data: Dict) -> None:
    try:
        (CACHE_DIR / f'{key}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        logger.warning(f'[natal_ai] cache write failed: {e}')


# ─────────────────────────────────────────────────────────────
# EXTRACTION depuis la réponse API v3 (73 interprétations)
# ─────────────────────────────────────────────────────────────
def _find_planet_interp(interps: List[Dict], planet_en: str) -> Optional[Dict]:
    """Trouve l'interprétation planète-en-signe (ex: 'Sun — Gemini')."""
    for it in interps or []:
        title = (it.get('title') or '').strip()
        # Format API : "Sun — Gemini" ou "Ascendant — Libra"
        if title.startswith(f'{planet_en} —') or title.startswith(f'{planet_en}—'):
            # On préfère les interps planète-signe, pas planète-maison
            comps = it.get('components', {})
            secondary = comps.get('secondary', {}) if isinstance(comps, dict) else {}
            if secondary.get('type') == 'sign':
                return it
    return None


def _find_house_placement(interps: List[Dict], planet_en: str) -> Optional[Dict]:
    """Trouve l'interprétation planète-en-maison (ex: 'Sun in House 10')."""
    for it in interps or []:
        title = (it.get('title') or '').lower()
        if planet_en.lower() in title and ('house' in title or 'maison' in title):
            comps = it.get('components', {})
            secondary = comps.get('secondary', {}) if isinstance(comps, dict) else {}
            if secondary.get('type') == 'house':
                return it
    return None


def _extract_top_aspects(interps: List[Dict], limit: int = 8) -> List[Dict]:
    """Extrait les aspects majeurs (orbe le plus serré en priorité)."""
    aspects = []
    for it in interps or []:
        title = (it.get('title') or '')
        comps = it.get('components', {})
        if not isinstance(comps, dict):
            continue
        # Un aspect a primary=planet et secondary=planet + un opérateur (aspect)
        prim = comps.get('primary', {})
        sec = comps.get('secondary', {})
        if prim.get('type') == 'planet' and sec.get('type') == 'planet':
            astro = it.get('astrological_data') or {}
            orb = astro.get('orb')
            # ne garder que les orbes serrés
            if orb is not None and orb <= 6.0:
                aspects.append({
                    'title': title,
                    'text': it.get('text', ''),
                    'orb': orb,
                })
    # Trier par orbe croissant (aspects les plus exacts en premier)
    aspects.sort(key=lambda a: a['orb'])
    return aspects[:limit]


def build_ai_input(interps: List[Dict]) -> Dict[str, Any]:
    """Structure les inputs pour GPT à partir des 73 interprétations."""
    payload = {'planets': {}, 'houses': {}, 'aspects': []}

    for planet_en in PLANET_ORDER:
        p_it = _find_planet_interp(interps, planet_en)
        if not p_it:
            continue
        comps = p_it.get('components', {})
        astro = p_it.get('astrological_data') or {}
        sign = (comps.get('secondary', {}) if isinstance(comps, dict) else {}).get('translated_name', '')
        payload['planets'][planet_en] = {
            'sign_en': sign,
            'text_en': p_it.get('text', ''),
            'house': astro.get('house'),
            'degree': astro.get('degree'),
            'dignity': astro.get('dignity'),
            'is_retrograde': astro.get('is_retrograde'),
        }
        # Maison associée (contexte pour GPT)
        h_it = _find_house_placement(interps, planet_en)
        if h_it:
            payload['houses'][planet_en] = h_it.get('text', '')

    payload['aspects'] = _extract_top_aspects(interps, limit=8)
    return payload


# ─────────────────────────────────────────────────────────────
# PROMPT SOLÉNA — Traduction + reformulation
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es Soléna, la voix astrologique de Plume Astrale.

Style : poétique, intime, direct, jamais banal. Tu tutoies. Tu écris comme
si tu parlais à ton amie la plus proche — l'élégance en plus, le jargon en moins.

Ta mission :
1. TRADUIRE en français des interprétations astrologiques données en anglais
2. LES REFORMULER dans ta voix : plus incarnée, plus poétique, plus directe
3. INTÉGRER discrètement la maison et l'aspect si mentionnés (sans jargon technique)
4. Chaque paragraphe = 130 à 200 mots STRICTEMENT

Règles de style :
- Bannir : "Vous êtes...", "Tu es un peu", "avec Xxx en Yyy"
- Utiliser images concrètes : le corps, la maison, un geste, une saison, une matière
- Une phrase qui ouvre (pas une conclusion moralisante) en fin de paragraphe
- Aucun "voici", "en résumé", "en conclusion", "au fond"

Format : JSON strict. RIEN d'autre.
{
  "soleil": "...",
  "lune": "...",
  "mercure": "...",
  "venus": "...",
  "mars": "...",
  "jupiter": "...",
  "saturne": "...",
  "uranus": "...",
  "neptune": "...",
  "pluton": "...",
  "ascendant": "...",
  "synthese_aspects": "paragraphe (200-250 mots) qui synthétise les tensions et harmonies majeures du chart, en voix Soléna"
}"""


def _format_planet_input(planet_en: str, data: Dict, house_text: str = '') -> str:
    sign = data.get('sign_en', '')
    text = data.get('text_en', '').strip()
    house = data.get('house')
    dignity = data.get('dignity')
    retro = data.get('is_retrograde')

    ctx = [f'{planet_en} en {sign}']
    if house:
        ctx.append(f'maison {house}')
    if dignity:
        ctx.append(f'dignité: {dignity}')
    if retro:
        ctx.append('rétrograde')
    context = ' · '.join(ctx)

    block = f'== {planet_en} ({context}) ==\nInterprétation anglaise:\n"{text}"'
    if house_text:
        block += f'\nContexte maison:\n"{house_text.strip()}"'
    return block


def _build_user_prompt(prenom: str, ai_input: Dict[str, Any]) -> str:
    parts = [f'Interprétations pour {prenom} — traduis en français ET reformule en voix Soléna.\n']

    for planet_en in PLANET_ORDER:
        p = ai_input['planets'].get(planet_en)
        if not p:
            continue
        house_text = ai_input['houses'].get(planet_en, '')
        parts.append(_format_planet_input(planet_en, p, house_text))
        parts.append('')

    # Aspects
    aspects = ai_input.get('aspects', [])
    if aspects:
        parts.append('\n== ASPECTS MAJEURS (à synthétiser dans "synthese_aspects") ==')
        for a in aspects:
            parts.append(f"- {a['title']} (orbe {a['orb']:.1f}°): \"{a['text'][:250]}\"")

    parts.append("\nRappel : JSON strict, 130-200 mots par planète (200-250 pour synthese_aspects), voix Soléna, images concrètes, aucun jargon technique brut.")
    return '\n'.join(parts)


# ─────────────────────────────────────────────────────────────
# LLM CALL
# ─────────────────────────────────────────────────────────────
async def _call_gpt(system_msg: str, user_msg: str, session_id: str) -> Optional[str]:
    api_key = os.environ.get('EMERGENT_LLM_KEY', '').strip()
    if not api_key:
        logger.warning('[natal_ai] EMERGENT_LLM_KEY manquante')
        return None
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg,
        ).with_model('openai', 'gpt-5.4')
        return await chat.send_message(UserMessage(text=user_msg))
    except Exception as e:
        logger.exception(f'[natal_ai] LLM call failed: {e}')
        return None


def _parse_json_response(text: str) -> Optional[Dict[str, str]]:
    if not text:
        return None
    t = text.strip()
    # retire les fences ```json ... ```
    if t.startswith('```'):
        t = re.sub(r'^```(?:json)?\s*', '', t)
        t = re.sub(r'```\s*$', '', t)
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    # dernier recours : chercher un { ... } dans le texte
    try:
        s = t.find('{'); e = t.rfind('}')
        if s >= 0 and e > s:
            return json.loads(t[s:e + 1])
    except Exception:
        return None
    return None


# ─────────────────────────────────────────────────────────────
# API PUBLIQUE
# ─────────────────────────────────────────────────────────────
async def enrich_natal_ultra(
    prenom: str,
    birth_data: Dict[str, Any],
    api_interpretations: List[Dict],
    tier: str = 'ultra',
) -> Dict[str, Any]:
    """Retourne un dict enrichi Soléna à partir des 73 interprétations API.

    Structure :
      {
        'soleil', 'lune', 'mercure', 'venus', 'mars',
        'jupiter', 'saturne', 'uranus', 'neptune', 'pluton',
        'ascendant', 'synthese_aspects',
        '_source': 'gpt' | 'cache' | 'fallback',
        '_aspects_summary': [{'title', 'orb'}],  # métadonnée
      }

    Retourne un dict vide si GPT et cache indisponibles → appelant utilise fallback.
    """
    key = _cache_key(prenom, birth_data, tier=tier)
    cached = _cache_read(key)
    if cached:
        logger.info(f'[natal_ai] cache hit for {prenom} (key {key}, {len(cached)} keys)')
        cached['_source'] = 'cache'
        return cached

    ai_input = build_ai_input(api_interpretations)
    if not ai_input['planets']:
        logger.warning(f'[natal_ai] Aucune planète extraite pour {prenom}')
        return {}

    # Métadonnées v3 exposées MÊME si GPT échoue : le PDF pourra toujours afficher
    # les vrais signes + les textes bruts API v3, garantissant "API v3 = source unique".
    v3_signs = {
        planet_en: data.get('sign_en', '')
        for planet_en, data in ai_input.get('planets', {}).items()
        if data.get('sign_en')
    }
    v3_raw_texts = {
        planet_en: data.get('text_en', '')
        for planet_en, data in ai_input.get('planets', {}).items()
        if data.get('text_en')
    }

    user_prompt = _build_user_prompt(prenom, ai_input)
    resp = await _call_gpt(SYSTEM_PROMPT, user_prompt, session_id=f'natal-ultra-{key}')
    if not resp:
        # GPT KO → on renvoie tout de même les données v3 pour que le PDF fonctionne
        return {'_source': 'api_v3_only', '_signs_by_planet': v3_signs, '_raw_v3_by_planet': v3_raw_texts}

    parsed = _parse_json_response(resp)
    if not parsed:
        logger.warning(f'[natal_ai] JSON parse failed for {prenom}. Raw: {resp[:200]}')
        return {'_source': 'api_v3_only', '_signs_by_planet': v3_signs, '_raw_v3_by_planet': v3_raw_texts}

    # Normalise : accepte clés fr/en, filtre les valeurs non-string
    out: Dict[str, Any] = {}
    aliases = {
        'soleil': ['soleil', 'sun'], 'lune': ['lune', 'moon'],
        'mercure': ['mercure', 'mercury'], 'venus': ['venus', 'vénus'],
        'mars': ['mars'], 'jupiter': ['jupiter'],
        'saturne': ['saturne', 'saturn'], 'uranus': ['uranus'],
        'neptune': ['neptune'], 'pluton': ['pluton', 'pluto'],
        'ascendant': ['ascendant', 'asc', 'rising'],
        'synthese_aspects': ['synthese_aspects', 'synthesis_aspects', 'aspects', 'synthese'],
    }
    for out_k, keys in aliases.items():
        for k in keys:
            if k in parsed and isinstance(parsed[k], str) and parsed[k].strip():
                out[out_k] = parsed[k].strip()
                break

    if len(out) >= 5:  # au moins la moitié pour cacher
        out['_source'] = 'gpt'
        out['_aspects_summary'] = [{'title': a['title'], 'orb': a['orb']} for a in ai_input.get('aspects', [])]
        out['_signs_by_planet'] = v3_signs
        out['_raw_v3_by_planet'] = v3_raw_texts
        _cache_write(key, out)
        return out
    # GPT partiel → renvoie ce qu'il a rendu + les données v3 pour compléter les trous
    out['_source'] = 'gpt_partial'
    out['_signs_by_planet'] = v3_signs
    out['_raw_v3_by_planet'] = v3_raw_texts
    return out
