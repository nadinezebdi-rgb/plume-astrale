"""Service IA (GPT-5.4) pour enrichir/traduire les analyses astrocartographiques.

L'API astrology-api.io v3 renvoie les analyses en anglais.
Ce module :
  1. Traduit et enrichit les descriptions pour un ton poétique et français impeccable
  2. Génère 2 destinations bonus (SolÃ©na choisit selon le thème natal)
"""
from __future__ import annotations
import json
import logging
import os
from typing import Any, Dict, List, Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

SYSTEM_MSG = (
    "Tu es Soléna, la voix de Plume Astrale. "
    "Tu écris exclusivement en FRANÇAIS impeccable, avec tous les accents et cédilles correctement placés. "
    "Ton ton est poétique, sensuel, précis, ni New Age ni technique. "
    "Tu ne cites JAMAIS de scores chiffrés ni de jargon anglais. "
    "Tu parles à une femme adulte, éveillée, qui envisage un changement de vie. "
    "Tu réponds uniquement en JSON valide, jamais en markdown."
)


def _model():
    return "openai", "gpt-5.4"


async def enrich_city_analysis(
    city: str,
    country: str,
    raw_summary: str,
    life_area_ratings: Dict[str, Any],
    planetary_influences: Dict[str, Any],
    first_name: str = "toi",
) -> Dict[str, str]:
    """Enrichit l'analyse brute d'une ville en français poétique.

    Retourne : {'headline', 'ambiance', 'career', 'love', 'spirituality', 'body', 'advice'}
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not api_key:
        return _fallback_city(city, country, raw_summary)

    # Ne retenir que les 6 domaines les plus significatifs
    ratings_sorted = sorted(
        [(k, v) for k, v in (life_area_ratings or {}).items() if isinstance(v, (int, float))],
        key=lambda x: x[1], reverse=True
    )[:6]
    top_influences = [
        f"{k}: {v.get('meaning', '')[:120]}"
        for k, v in list((planetary_influences or {}).items())[:8]
        if isinstance(v, dict) and v.get("meaning")
    ]

    prompt = f"""Écris une analyse poétique et française pour la ville de {city} ({country}) destinée à {first_name}.

Données brutes de l'API (à traduire, enrichir, humaniser — ne pas mentionner de scores) :
- Résumé anglais : {raw_summary[:400]}
- Domaines forts : {json.dumps(ratings_sorted, ensure_ascii=False)}
- Influences planétaires clés : {json.dumps(top_influences[:5], ensure_ascii=False)}

Retourne EXCLUSIVEMENT un JSON avec ces clés (chaque valeur = 2-3 phrases FR poétiques) :
{{
  "headline": "Une phrase-choc qui résume l'énergie de la ville (ex: 'Le sol qui réveille ta lumière')",
  "ambiance": "L'ambiance générale — ce qu'on ressent en y vivant",
  "career": "Ce que ce lieu offre à ta trajectoire professionnelle",
  "love": "Ce que ce lieu déclenche dans ta vie affective",
  "spirituality": "Ce que ce lieu ouvre spirituellement",
  "body": "Ce que ce lieu fait à ton corps, ta santé, ton énergie",
  "advice": "Un conseil concret de Soléna (2 phrases max)"
}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"astrocarto-city-{city}-{country}",
            system_message=SYSTEM_MSG,
        ).with_model(*_model())
        resp = await chat.send_message(UserMessage(text=prompt))
        return _parse_json(resp) or _fallback_city(city, country, raw_summary)
    except Exception as e:
        logger.warning(f"[astrocarto_ai] enrich_city failed for {city}: {e}")
        return _fallback_city(city, country, raw_summary)


async def generate_bonus_destinations(
    first_name: str,
    natal_summary: str,
    already_chosen_cities: List[str],
) -> List[Dict[str, str]]:
    """Génère 2 villes bonus recommandées par Soléna en fonction du thème natal.

    Retourne : liste de {'city', 'country', 'latitude', 'longitude', 'why', 'promise'}
    """
    api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not api_key:
        return _fallback_bonus()

    prompt = f"""Tu es Soléna. Propose 2 villes MONDIALES surprenantes et cohérentes pour {first_name}.

Contexte natal (résumé) : {natal_summary[:400]}
Villes DÉJÀ choisies (à éviter) : {", ".join(already_chosen_cities) if already_chosen_cities else "aucune"}

Contraintes :
- Deux villes RÉELLES et différentes des continents choisis (varie).
- Chacune doit avoir une identité astrocartographique forte (ligne planétaire favorable).
- Écris en français poétique.

Retourne un JSON strict :
{{
  "destinations": [
    {{
      "city": "Nom de ville",
      "country": "Nom pays FR",
      "country_code": "Code ISO 2 lettres",
      "latitude": 0.0,
      "longitude": 0.0,
      "why": "Pourquoi cette ville (2-3 phrases FR poétiques)",
      "promise": "La promesse (1 phrase FR, 12-18 mots)"
    }},
    {{ ... deuxième ville ... }}
  ]
}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"astrocarto-bonus-{hash(natal_summary) & 0xFFFF}",
            system_message=SYSTEM_MSG,
        ).with_model(*_model())
        resp = await chat.send_message(UserMessage(text=prompt))
        parsed = _parse_json(resp) or {}
        dests = parsed.get("destinations") or []
        if len(dests) >= 2:
            return dests[:2]
    except Exception as e:
        logger.warning(f"[astrocarto_ai] bonus failed: {e}")
    return _fallback_bonus()


async def write_synthesis(
    first_name: str,
    cities_analyses: List[Dict[str, Any]],
) -> str:
    """Rédige la synthèse finale du PDF (2-3 paragraphes FR)."""
    api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not api_key:
        return _fallback_synthesis(first_name)

    resume = [
        {"city": c.get("city"), "country": c.get("country"), "headline": c.get("headline")}
        for c in cities_analyses if c
    ]
    prompt = f"""Rédige la SYNTHÈSE finale du rapport d'astrocartographie de {first_name}.

Villes analysées : {json.dumps(resume, ensure_ascii=False)}

Écris 3 paragraphes en FRANÇAIS poétique :
1. Ce que ces villes révèlent sur son axe de vie profond
2. Comment choisir entre elles (critères intimes, pas techniques)
3. Un dernier mot de Soléna, tendre et fort

Ne fais pas la liste des villes. Écris en flux continu, un texte narratif de 300-400 mots. Réponds en JSON : {{"text": "..."}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"astrocarto-syn-{first_name}",
            system_message=SYSTEM_MSG,
        ).with_model(*_model())
        resp = await chat.send_message(UserMessage(text=prompt))
        parsed = _parse_json(resp) or {}
        return (parsed.get("text") or "").strip() or _fallback_synthesis(first_name)
    except Exception as e:
        logger.warning(f"[astrocarto_ai] synthesis failed: {e}")
        return _fallback_synthesis(first_name)


def _parse_json(txt: str) -> Optional[Dict]:
    if not txt:
        return None
    t = txt.strip()
    # Retirer les fences markdown si présents
    if t.startswith("```"):
        t = t.strip("`")
        if t.lower().startswith("json"):
            t = t[4:]
        t = t.strip()
    # Trouver le premier { et le dernier }
    try:
        start = t.index("{")
        end = t.rindex("}")
        return json.loads(t[start:end + 1])
    except Exception:
        return None


def _fallback_city(city: str, country: str, raw: str) -> Dict[str, str]:
    return {
        "headline": f"{city}, une porte à ouvrir",
        "ambiance": f"{city} porte une énergie unique que ton thème natal met en résonance. Chaque ville active des cordes différentes en toi.",
        "career": "Une direction professionnelle peut s'y ouvrir, portée par les lignes planétaires locales.",
        "love": "Les relations y prennent une texture particulière — plus intense ou plus douce selon les aspects activés.",
        "spirituality": "Un espace où ton intériorité peut respirer autrement.",
        "body": "Ton énergie physique s'y accorde à un rythme différent — écoute-le.",
        "advice": f"Si tu envisages {city}, passes-y d'abord une semaine avec l'intention d'y écouter, pas d'y décider.",
    }


def _fallback_bonus() -> List[Dict[str, str]]:
    return [
        {
            "city": "Lisbonne", "country": "Portugal", "country_code": "PT",
            "latitude": 38.7223, "longitude": -9.1393,
            "why": "Une ville douce, lumineuse, où la mer parle à l'inconscient. Elle apaise sans endormir, elle éveille sans brûler.",
            "promise": "Là où ton âme peut recommencer à respirer lentement.",
        },
        {
            "city": "Kyoto", "country": "Japon", "country_code": "JP",
            "latitude": 35.0116, "longitude": 135.7681,
            "why": "Une géographie de la finesse. Kyoto affine le regard et ralentit le corps. C'est un lieu qui enseigne le geste juste.",
            "promise": "Là où ta profondeur trouve enfin la lenteur qu'elle mérite.",
        },
    ]


def _fallback_synthesis(first_name: str) -> str:
    return (
        f"{first_name}, ces villes ne sont pas des adresses : ce sont des versions de toi. "
        f"Chacune propose une géographie intérieure — un climat, un rythme, une manière d'aimer et de travailler.\n\n"
        f"Choisir n'est pas un calcul. C'est écouter laquelle te fait vibrer sans que tu saches pourquoi. "
        f"L'astrocartographie ne prédit pas : elle révèle. À toi de traverser physiquement ces lieux pour sentir "
        f"lequel te ressemble le plus à cet instant de ta vie.\n\n"
        f"Rappelle-toi : la carte n'oblige à rien. Elle t'invite à rêver plus grand, à oser plus loin. "
        f"Et si le ciel a mis ces lignes sur ton chemin, c'est peut-être qu'il attend simplement que tu poses le pas.\n"
        f"— Soléna"
    )
