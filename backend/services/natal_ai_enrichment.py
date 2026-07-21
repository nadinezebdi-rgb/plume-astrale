"""
natal_ai_enrichment — Enrichissement AI (GPT-5.4) pour le Thème Natal.

Prend les données API v3 (positions + maisons + aspects) et génère des
interprétations personnalisées voix Soléna, poétiques et profondes.

Cache filesystem : hash(prenom + birth_data) → JSON stocké dans
`/app/backend/cache/natal_ai/`. Évite de repayer GPT sur regénération.
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / 'cache' / 'natal_ai'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────────────────────
def _cache_key(prenom: str, birth_data: Dict[str, Any]) -> str:
    bd_str = json.dumps({
        'p': prenom.lower().strip(),
        'd': birth_data.get('day'), 'm': birth_data.get('month'), 'y': birth_data.get('year'),
        'h': birth_data.get('hour'), 'mn': birth_data.get('min'),
        'lat': round(birth_data.get('lat', 0), 3), 'lon': round(birth_data.get('lon', 0), 3),
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
        (CACHE_DIR / f'{key}.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    except Exception as e:
        logger.warning(f'[natal_ai] cache write failed: {e}')


# ─────────────────────────────────────────────────────────────
# PROMPT SOLÉNA
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es Soléna, la voix astrologique de Plume Astrale.

Style : poétique, intime, direct, jamais banal. Tu tutoies. Tu écris comme
Amanda Bourdain aurait écrit sur l'âme : élégant, sans jargon technique, sans
paillette. Tu parles au corps ET à l'inconscient de la femme qui te lit.

Chaque paragraphe doit :
- Commencer sans "Tu es un peu" ou "Vous êtes..." — trop banal
- Éviter les clichés type "sensible", "créative", "unique" employés seuls
- Utiliser des images concrètes (le corps, la maison, un geste, une saison)
- Faire au moins UNE référence directe à un aspect du chart (aspect, maison, degré) sans jargon
- Terminer par une phrase qui ouvre une réflexion, pas une conclusion
- Longueur : 120 à 180 mots STRICTEMENT

Format de sortie : JSON strict, RIEN d'autre.
{
  "soleil": "paragraphe sur le Soleil...",
  "lune": "paragraphe sur la Lune...",
  "venus": "paragraphe sur Vénus...",
  "mars": "paragraphe sur Mars...",
  "ascendant": "paragraphe sur l'Ascendant..."
}"""


def _build_user_prompt(prenom: str, planets: Dict[str, Dict], houses: List[Dict], aspects: List[Dict]) -> str:
    p = planets
    def _pd(k):
        d = p.get(k, {})
        sign = d.get('sign') or ''
        house = d.get('house') or ''
        deg = d.get('degree', '')
        return f"{sign} (maison {house}, {deg}°)" if house else sign

    # Aspects majeurs seulement (orbe < 6°)
    major = [a for a in (aspects or []) if _is_major_aspect(a)][:10]
    aspects_str = '\n'.join(
        f"- {a.get('planet1', '?')} {a.get('aspect', '?')} {a.get('planet2', '?')} "
        f"(orbe {a.get('orb', '?')}°)"
        for a in major
    ) or 'Aucun aspect majeur communiqué.'

    return f"""Écris les interprétations pour {prenom} — 5 paragraphes séparés (JSON strict).

DONNÉES DU CIEL DE NAISSANCE :
- Soleil en {_pd('sun')}
- Lune en {_pd('moon')}
- Vénus en {_pd('venus')}
- Mars en {_pd('mars')}
- Ascendant en {_pd('ascendant')}

ASPECTS MAJEURS (orbe serré) :
{aspects_str}

Rappelle-toi : voix Soléna, 120-180 mots par paragraphe, JSON strict,
inclure un détail précis du chart (aspect, maison ou degré) dans chaque
paragraphe. Aucune formule creuse — chaque phrase doit apporter."""


def _is_major_aspect(a: Dict) -> bool:
    t = (a.get('aspect') or '').lower()
    return any(m in t for m in ('conjunction', 'opposition', 'trine', 'square', 'sextile',
                                 'conjonction', 'trigone', 'carré', 'carre'))


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
        resp = await chat.send_message(UserMessage(text=user_msg))
        return resp
    except Exception as e:
        logger.exception(f'[natal_ai] LLM call failed: {e}')
        return None


def _parse_json_response(text: str) -> Optional[Dict[str, str]]:
    """Extrait le JSON de la réponse GPT (peut inclure markdown fences)."""
    if not text:
        return None
    t = text.strip()
    # retire les fences ```json ... ```
    if t.startswith('```'):
        lines = t.split('\n')
        t = '\n'.join(lines[1:-1]) if len(lines) > 2 else t
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    # dernier recours : trouver { ... } dans le texte
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
async def enrich_natal_interpretations(
    prenom: str,
    birth_data: Dict[str, Any],
    planets: Dict[str, Dict[str, Any]],
    houses: List[Dict] = None,
    aspects: List[Dict] = None,
) -> Dict[str, str]:
    """Retourne un dict {soleil, lune, venus, mars, ascendant} avec paragraphes riches.

    Cache filesystem par hash. Si GPT échoue, retourne {} et l'appelant
    utilisera les fallbacks statiques.
    """
    key = _cache_key(prenom, birth_data)
    cached = _cache_read(key)
    if cached:
        logger.info(f'[natal_ai] cache hit for {prenom} (key {key})')
        return cached

    user_prompt = _build_user_prompt(prenom, planets, houses or [], aspects or [])
    resp = await _call_gpt(SYSTEM_PROMPT, user_prompt, session_id=f'natal-{key}')
    if not resp:
        return {}

    parsed = _parse_json_response(resp)
    if not parsed:
        logger.warning(f'[natal_ai] Failed to parse JSON for {prenom}. Raw: {resp[:200]}')
        return {}

    # Normalise clés (accepte fr/en)
    normalized = {}
    for out_k, aliases in [
        ('soleil', ['soleil', 'sun']),
        ('lune', ['lune', 'moon']),
        ('venus', ['venus', 'vénus']),
        ('mars', ['mars']),
        ('ascendant', ['ascendant', 'asc', 'rising']),
    ]:
        for a in aliases:
            if a in parsed and isinstance(parsed[a], str) and parsed[a].strip():
                normalized[out_k] = parsed[a].strip()
                break

    if len(normalized) >= 3:
        _cache_write(key, normalized)
    return normalized
