"""natal_preface_generator — Génère la préface "Comment lire ce livre"
================================================================================

Produit un texte éditorial chaleureux (3 blocs ~250 mots) expliquant au lecteur
comment utiliser son thème natal **tout au long de sa vie** — pas d'un seul
coup, mais comme un compagnon des grandes étapes.

Appel Claude Sonnet 4-6 via EMERGENT_LLM_KEY (idem book_engine_shared).
Fallback statique de haute qualité si l'API échoue.

Signature retour : list[dict] — [{'kind': 'h2'|'paragraph', 'text': '…'}]
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """Tu es Soléna, éditrice de Plume Astrale — maison française d'astrologie éditoriale.
Tu rédiges une **préface** pour le Thème Natal personnalisé d'un lecteur.
Objectif : lui expliquer comment utiliser ce livre **tout au long de sa vie**, pas d'une traite.

RÈGLES DE VOIX :
- Tu : chaleureuse, directe, sans mièvrerie
- Images concrètes, pas de jargon astrologique
- Phrases courtes alternant avec des phrases amples
- Rythme littéraire : Christian Bobin + Nancy Huston
- JAMAIS : « destin », « révélation », « magie », « pouvoirs », « prédiction »
- JAMAIS : « cosmique », « voyage intérieur », « plonger dans », « invite à »
- Chaque paragraphe fait 60-100 mots strict

STRUCTURE DEMANDÉE (JSON strict) :
{
  "blocks": [
    {"kind": "paragraph", "text": "Paragraphe d'ouverture (90 mots) — reconnaissance : vous tenez un objet rare, personnel, non reproductible. Pose le livre comme un compagnon."},
    {"kind": "h2", "text": "Un livre à consulter, pas à lire d'une traite"},
    {"kind": "paragraph", "text": "Paragraphe (80 mots) : lire par petites touches. Y revenir aux grandes étapes de la vie — rupture, naissance, déménagement, deuil, démarrage."},
    {"kind": "paragraph", "text": "Paragraphe (80 mots) : garder le livre à portée, le consulter en période de doute. Chaque relecture révèle une couche différente."},
    {"kind": "h2", "text": "Comment lire chaque partie"},
    {"kind": "paragraph", "text": "Paragraphe (90 mots) : expliquer concrètement les 3 parties — vos planètes (qui vous êtes), vos maisons (où vous jouez votre vie), vos aspects (comment vos forces dialoguent)."},
    {"kind": "h2", "text": "Un compagnon pour vos années à venir"},
    {"kind": "paragraph", "text": "Paragraphe (90 mots) : le ciel natal ne change pas, mais vous changez. Le même paragraphe prendra un sens différent à 30, 40, 50 ans. Les cycles planétaires activent tour à tour des pans de votre thème."},
    {"kind": "paragraph", "text": "Paragraphe (70 mots) : clôture tendre — « que ce livre vous accompagne ». Signé Soléna · Plume Astrale."}
  ]
}

RETOURNE UNIQUEMENT LE JSON. Aucun préambule, aucun markdown, aucune autre balise."""


def _user_prompt(first_name: str, sun_sign: str, moon_sign: str, asc_sign: str) -> str:
    parts = [
        f"Rédige la préface du Thème Natal de {first_name}.",
    ]
    identity = []
    if sun_sign:
        identity.append(f"Soleil en {sun_sign}")
    if moon_sign:
        identity.append(f"Lune en {moon_sign}")
    if asc_sign:
        identity.append(f"Ascendant en {asc_sign}")
    if identity:
        parts.append(f"Identité astrale : {', '.join(identity)}.")
    parts.append(
        "Évoque ces 3 signatures discrètement si cela te sert pour illustrer, mais "
        "ne les énumère jamais frontalement — la préface n'est pas une analyse, "
        "c'est un mode d'emploi affectueux."
    )
    return '\n'.join(parts)


# ─── Fallback statique de haute qualité ─────────────────────────────
def _static_fallback(first_name: str) -> List[Dict[str, str]]:
    return [
        {'kind': 'paragraph', 'text': (
            f"{first_name}, ce livre n'est pas un livre comme les autres. "
            "Il n'a été écrit qu'une fois, et il n'a été écrit que pour vous. "
            "Il porte la carte d'un ciel précis — le vôtre — tel qu'il brillait à votre premier souffle. "
            "Vous ne le lirez pas d'une traite, et c'est bien ainsi : il est fait pour vivre à vos côtés, "
            "pas pour être avalé en une soirée."
        )},
        {'kind': 'h2', 'text': "Un livre à consulter, pas à lire d'une traite"},
        {'kind': 'paragraph', 'text': (
            "Lisez-le par petites touches. Un paragraphe au réveil, une page le dimanche soir, "
            "un chapitre quand une question vous traverse. Les mots ont besoin de respirer, "
            "et vous aussi. Ce livre résiste à la boulimie — il préfère la lenteur."
        )},
        {'kind': 'paragraph', 'text': (
            "Revenez-y aux grandes étapes : une rupture, une naissance, un déménagement, un deuil, "
            "un démarrage. À chaque fois, vous verrez que les mêmes pages vous parlent autrement. "
            "C'est que ce n'est pas le livre qui change — c'est vous. Et c'est précisément cela qu'il "
            "vous aide à voir."
        )},
        {'kind': 'h2', 'text': "Comment lire chaque partie"},
        {'kind': 'paragraph', 'text': (
            "Vous trouverez trois mouvements. D'abord <b>vos planètes</b> : qui vous êtes, "
            "quelles sont les dix forces qui composent votre palette intérieure. "
            "Puis <b>vos douze maisons</b> : les scènes de votre vie, les territoires que le ciel "
            "a particulièrement éclairés chez vous. Enfin <b>vos aspects</b> : la manière dont ces "
            "forces se parlent entre elles — en harmonie, en frottement, en complicité silencieuse."
        )},
        {'kind': 'h2', 'text': "Un compagnon pour vos années à venir"},
        {'kind': 'paragraph', 'text': (
            "Votre ciel natal ne bouge plus — il est votre partition fixe, tracée à votre naissance. "
            "Mais vous, vous changez. À trente ans, un paragraphe sur Saturne pourra vous ennuyer ; "
            "à quarante, il deviendra lumineux. À cinquante, le chapitre des maisons prendra un sens "
            "neuf. Les planètes du ciel actuel activent tour à tour des zones de votre thème : "
            "ce livre vous aide à décoder ces appels."
        )},
        {'kind': 'paragraph', 'text': (
            "Alors prenez votre temps. Posez-le sur une étagère, revenez-y, soulignez, annotez, "
            "offrez-vous le droit de ne pas tout comprendre tout de suite. "
            "Que ce livre vous accompagne — longtemps."
        )},
        {'kind': 'paragraph', 'text': (
            '<i>— Soléna, pour Plume Astrale.</i>'
        )},
    ]


# ─── Appel LLM ──────────────────────────────────────────────────────
def _parse_json_blocks(raw: str) -> List[Dict[str, str]]:
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if m:
        raw = m.group(1)
    start = raw.find('{')
    if start < 0:
        raise ValueError(f'no JSON in raw={raw[:200]!r}')
    depth = 0
    end = -1
    for i in range(start, len(raw)):
        if raw[i] == '{':
            depth += 1
        elif raw[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < 0:
        raise ValueError('unbalanced JSON')
    obj = json.loads(raw[start:end + 1])
    blocks = obj.get('blocks') or []
    out: List[Dict[str, str]] = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        kind = (b.get('kind') or '').strip().lower()
        text = (b.get('text') or '').strip()
        if kind in ('h2', 'paragraph') and text:
            out.append({'kind': kind, 'text': text})
    return out


async def _call_claude_sonnet(system: str, user: str, session_id: str) -> str:
    """Appel Claude Sonnet via EMERGENT_LLM_KEY (idem book_engine_shared)."""
    import asyncio as _a
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    key = os.environ.get('EMERGENT_LLM_KEY')
    if not key:
        raise RuntimeError('EMERGENT_LLM_KEY absent de .env')

    def _sync_call() -> str:
        loop = _a.new_event_loop()
        try:
            chat = (
                LlmChat(api_key=key, session_id=session_id, system_message=system)
                .with_model('anthropic', 'claude-sonnet-4-6')
            )
            resp = loop.run_until_complete(chat.send_message(UserMessage(text=user)))
            if isinstance(resp, str):
                return resp.strip()
            return (getattr(resp, 'text', None) or getattr(resp, 'content', None) or str(resp)).strip()
        finally:
            loop.close()

    return await _a.to_thread(_sync_call)


async def generate_preface_blocks(
    *, first_name: str, sun_sign: str = '', moon_sign: str = '',
    asc_sign: str = '', session_id: str = '',
    timeout_s: float = 45.0,
) -> List[Dict[str, str]]:
    """Génère les blocs de la préface. Fallback statique en cas d'échec."""
    first_name = (first_name or 'Voyageuse').strip() or 'Voyageuse'
    sid = session_id or f'preface-{first_name.lower()}'
    try:
        raw = await asyncio.wait_for(
            _call_claude_sonnet(_SYSTEM_PROMPT, _user_prompt(first_name, sun_sign, moon_sign, asc_sign), sid),
            timeout=timeout_s,
        )
        blocks = _parse_json_blocks(raw)
        if not blocks or sum(1 for b in blocks if b['kind'] == 'paragraph') < 3:
            raise ValueError(f'preface too short: {len(blocks)} blocks')
        logger.info(f'[preface_generator] AI preface generated ({len(blocks)} blocks)')
        return blocks
    except Exception as e:
        logger.warning(f'[preface_generator] AI failed, static fallback: {e}')
        return _static_fallback(first_name)


__all__ = ['generate_preface_blocks']
