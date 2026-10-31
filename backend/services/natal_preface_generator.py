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
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """Tu rédiges pour Plume Astrale — maison française d'astrologie éditoriale.
Tu rédiges une **préface** pour le Thème Natal personnalisé d'un lecteur.
Objectif : lui expliquer comment utiliser ce livre **tout au long de sa vie**, pas d'une traite.

INTERDICTION ABSOLUE : ne jamais signer ni mentionner « Soléna » dans la préface finale. La signature est Plume Astrale.

RÈGLES DE VOIX :
- Tu : chaleureuse, directe, sans mièvrerie
- Tutoiement obligatoire (jamais de "vous") — tu parles à UNE personne, intimement
- Images concrètes, pas de jargon astrologique
- Phrases courtes alternant avec des phrases amples
- Rythme littéraire : Christian Bobin + Nancy Huston
- JAMAIS : « destin », « révélation », « magie », « pouvoirs », « prédiction »
- JAMAIS : « cosmique », « voyage intérieur », « plonger dans », « invite à »
- Chaque paragraphe fait 60-100 mots strict

STRUCTURE DEMANDÉE (JSON strict) :
{
  "blocks": [
    {"kind": "paragraph", "text": "Paragraphe d'ouverture (90 mots) — reconnaissance : tu tiens un objet rare, personnel, non reproductible. Pose le livre comme un compagnon."},
    {"kind": "h2", "text": "Un livre à consulter, pas à lire d'une traite"},
    {"kind": "paragraph", "text": "Paragraphe (80 mots) : lire par petites touches. Y revenir aux grandes étapes de la vie — rupture, naissance, déménagement, deuil, démarrage."},
    {"kind": "paragraph", "text": "Paragraphe (80 mots) : garder le livre à portée, le consulter en période de doute. Chaque relecture révèle une couche différente."},
    {"kind": "h2", "text": "Comment lire chaque partie"},
    {"kind": "paragraph", "text": "Paragraphe (90 mots) : expliquer concrètement les 3 parties — tes planètes (qui tu es), tes maisons (où tu joues ta vie), tes aspects (comment tes forces dialoguent)."},
    {"kind": "h2", "text": "Un compagnon pour tes années à venir"},
    {"kind": "paragraph", "text": "Paragraphe (90 mots) : le ciel natal ne change pas, mais tu changes. Le même paragraphe prendra un sens différent à 30, 40, 50 ans. Les cycles planétaires activent tour à tour des pans de ton thème."},
    {"kind": "paragraph", "text": "Paragraphe (70 mots) : clôture tendre — « que ce livre t'accompagne ». Signé Plume Astrale (jamais le prénom Soléna)."}
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
def _static_fallback(first_name: str, language: str = 'fr') -> List[Dict[str, str]]:
    language = (language or 'fr').lower()
    if language == 'en':
        return [
            {'kind': 'paragraph', 'text': (
                f"{first_name}, this book is not a book like any other. "
                "It has been written only once, and only for you. "
                "It carries the map of a precise sky — yours — as it shone at your first breath. "
                "You won't read it in one go, and that is as it should be: it is made to live by your side, "
                "not to be swallowed in a single evening."
            )},
            {'kind': 'h2', 'text': 'A book to consult, not to read in one go'},
            {'kind': 'paragraph', 'text': (
                "Read it in small touches. A paragraph at waking, a page on Sunday evening, "
                "a chapter when a question crosses your mind. Words need to breathe, "
                "and so do you. This book resists bingeing — it prefers slowness."
            )},
            {'kind': 'paragraph', 'text': (
                "Return to it at life's turning points: a breakup, a birth, a move, a mourning, "
                "a start. Each time, the same pages will speak to you differently. "
                "That's because it isn't the book that changes — it's you. And that is precisely "
                "what it helps you see."
            )},
            {'kind': 'h2', 'text': 'How to read each part'},
            {'kind': 'paragraph', 'text': (
                "You will find three movements. First <b>your planets</b>: who you are, "
                "what the ten forces of your inner palette are. "
                "Then <b>your twelve houses</b>: the scenes of your life, the territories the sky "
                "has lit particularly brightly for you. Finally <b>your aspects</b>: the way these "
                "forces speak to each other — in harmony, in friction, in silent complicity."
            )},
            {'kind': 'h2', 'text': 'A companion for the years to come'},
            {'kind': 'paragraph', 'text': (
                "Your birth sky doesn't move anymore — it is your fixed score, drawn at your birth. "
                "But you, you change. At thirty, a paragraph on Saturn might bore you; "
                "at forty, it will become luminous. At fifty, the chapter on houses will take on "
                "fresh meaning. The planets of the current sky activate zones of your chart in turn: "
                "this book helps you decode those calls."
            )},
            {'kind': 'paragraph', 'text': (
                "So take your time. Set it on a shelf, come back to it, underline, annotate, "
                "give yourself the right not to understand everything at once. "
                "May this book accompany you — for a long time."
            )},
            {'kind': 'paragraph', 'text': (
                '<i>— Plume Astrale</i>'
            )},
        ]
    return [
        {'kind': 'paragraph', 'text': (
            f"{first_name}, ce livre n'est pas un livre comme les autres. "
            "Il n'a été écrit qu'une fois, et il n'a été écrit que pour toi. "
            "Il porte la carte d'un ciel précis — le tien — tel qu'il brillait à ton premier souffle. "
            "Tu ne le liras pas d'une traite, et c'est bien ainsi : il est fait pour vivre à tes côtés, "
            "pas pour être avalé en une soirée."
        )},
        {'kind': 'h2', 'text': "Un livre à consulter, pas à lire d'une traite"},
        {'kind': 'paragraph', 'text': (
            "Lis-le par petites touches. Un paragraphe au réveil, une page le dimanche soir, "
            "un chapitre quand une question te traverse. Les mots ont besoin de respirer, "
            "et toi aussi. Ce livre résiste à la boulimie — il préfère la lenteur."
        )},
        {'kind': 'paragraph', 'text': (
            "Reviens-y aux grandes étapes : une rupture, une naissance, un déménagement, un deuil, "
            "un démarrage. À chaque fois, tu verras que les mêmes pages te parlent autrement. "
            "C'est que ce n'est pas le livre qui change — c'est toi. Et c'est précisément cela qu'il "
            "t'aide à voir."
        )},
        {'kind': 'h2', 'text': "Comment lire chaque partie"},
        {'kind': 'paragraph', 'text': (
            "Tu trouveras trois mouvements. D'abord <b>tes planètes</b> : qui tu es, "
            "quelles sont les dix forces qui composent ta palette intérieure. "
            "Puis <b>tes douze maisons</b> : les scènes de ta vie, les territoires que le ciel "
            "a particulièrement éclairés chez toi. Enfin <b>tes aspects</b> : la manière dont ces "
            "forces se parlent entre elles — en harmonie, en frottement, en complicité silencieuse."
        )},
        {'kind': 'h2', 'text': "Un compagnon pour tes années à venir"},
        {'kind': 'paragraph', 'text': (
            "Ton ciel natal ne bouge plus — il est ta partition fixe, tracée à ta naissance. "
            "Mais toi, tu changes. À trente ans, un paragraphe sur Saturne pourra t'ennuyer ; "
            "à quarante, il deviendra lumineux. À cinquante, le chapitre des maisons prendra un sens "
            "neuf. Les planètes du ciel actuel activent tour à tour des zones de ton thème : "
            "ce livre t'aide à décoder ces appels."
        )},
        {'kind': 'paragraph', 'text': (
            "Alors prends ton temps. Pose-le sur une étagère, reviens-y, souligne, annote, "
            "offre-toi le droit de ne pas tout comprendre tout de suite. "
            "Que ce livre t'accompagne — longtemps."
        )},
        {'kind': 'paragraph', 'text': (
            '<i>— Plume Astrale</i>'
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
    """Use the same direct OpenAI client as the natal book enrichment."""
    from services.natal_ai_enrichment import _call_gpt
    response = await _call_gpt(system, user, session_id, timeout_s=120.0)
    if not response:
        raise RuntimeError('OpenAI n’a pas retourné de texte complet')
    return response


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
