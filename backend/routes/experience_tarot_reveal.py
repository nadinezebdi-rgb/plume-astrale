"""Experience Tarot Reveal — Dynamic LLM generation (Feb 2026)

Objectif produit :
  Remplacer les 12 phrases statiques Scene 3 (`scene3Revelations.js`) par
  des révélations dynamiques Claude Sonnet 4.6, personnalisées au moment
  du tirage. Cache Mongo agressif (fenêtre 30 minutes) pour maintenir un
  coût quasi nul même en trafic élevé.

Architecture :
  - POST /api/experience/tarot-reveal : {card_id, intent_id} → révélation
  - Cache Mongo : `experience_tarot_reveals_cache`
    Clé = f"{card_id}:{intent_id}:{time_slot_30min}"
    TTL naturel : la clé change toutes les 30 min → nouvelle génération.
  - Fallback statique intégré côté backend (SCENE3_FALLBACK_BACKEND) si
    la clé LLM échoue (timeout, JSON invalide, etc.). Le front dispose
    aussi de son fallback local pour cas offline.

Coût : ~1 appel LLM / (carte × intent × 30 min) → 12 combos × 48 slots/jour
= 576 appels max/jour, indépendant du trafic. En pratique ~50 slots actifs.
"""
from __future__ import annotations
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from db import get_db as _get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/experience', tags=['experience-tarot'])


# ─── Config : cartes × intents whitelist (bloque le flood LLM) ────────
ALLOWED_CARDS = frozenset({'heart', 'moon', 'star'})
ALLOWED_INTENTS = frozenset({'relationship', 'clarity', 'self_discovery', 'specific_question'})

CARD_META = {
    'heart': {'title': 'La Rencontre', 'symbol': 'lien', 'tagline': 'Ce qui vous relie'},
    'moon':  {'title': 'Le Voile',     'symbol': 'silence', 'tagline': 'Ce qui se dévoile'},
    'star':  {'title': 'La Trajectoire', 'symbol': 'mouvement', 'tagline': 'Ce qui vous porte'},
}

INTENT_META = {
    'relationship':      {'label': 'une relation qui questionne', 'service': 'tirage_complet'},
    'clarity':           {'label': "un besoin d'y voir plus clair", 'service': 'tirage_complet'},
    'self_discovery':    {'label': 'un désir de mieux se comprendre', 'service': 'theme_natal'},
    'specific_question': {'label': 'une question précise', 'service': 'tirage_complet'},
}

CTA_BY_SERVICE = {
    'tirage_complet': 'Découvrir la suite de mon tirage',
    'theme_natal':    'Découvrir mon thème natal',
}


# ─── Fallback statique backend (miroir minimal du front) ──────────────
# On duplique exprès une version courte ici. Le front garde son propre
# fallback exhaustif — mais si l'API tombe complètement, on renvoie quand
# même une phrase de qualité (pas de 500 → UX préservée).
STATIC_FALLBACK = {
    'title': 'Cette carte',
    'revelation': 'Cette carte éclaire une partie de votre question.',
    'tension':    "Mais seule, elle ne raconte pas toute l'histoire.",
    'cta':        'Découvrir la suite de mon tirage',
}


# ─── Mongo accessor ───────────────────────────────────────────────────
# Partagé via db.get_db() (singleton pool) — plus de client ad-hoc.


async def _ensure_index():
    db = _get_db()
    try:
        await db.experience_tarot_reveals_cache.create_index('key', unique=True, name='uniq_key')
    except Exception as e:
        logger.warning(f'[tarot-reveal] index warning: {e}')


def _current_time_slot() -> str:
    """Fenêtre de 30 min → clé de cache stable dans l'intervalle.

    Format : YYYYMMDD-HH{A|B}  (A=0-29, B=30-59). Simple, lisible,
    tri-alphabétique compatible avec un scan chronologique.
    """
    now = datetime.now(timezone.utc)
    half = 'A' if now.minute < 30 else 'B'
    return f"{now.strftime('%Y%m%d-%H')}{half}"


def _cache_key(card_id: str, intent_id: str) -> str:
    return f'{card_id}:{intent_id}:{_current_time_slot()}'


# ─── LLM generation ───────────────────────────────────────────────────
LLM_SYSTEM_PROMPT = (
    "Tu es Plume Astrale, une voix française, littéraire, précise. "
    "Tu génères des révélations de tarot en 2 courtes phrases, sans "
    "clichés (bannis 'cosmique', 'invite à', 'plonger', 'révélation'). "
    "Voix : élégante, sensuelle, jamais mystique-cheap. Tu réponds "
    "uniquement en JSON strict, sans balise markdown, sans commentaire. "
    "Schéma : {\"revelation\": str, \"tension\": str}. "
    "revelation : 1 phrase courte (max 22 mots) qui nomme un fragment "
    "concret que la carte éclaire — au présent, à la 2e personne du "
    "pluriel (\"vous\"). Interdit : mots blacklist ci-dessus. "
    "tension : 1 phrase courte (max 18 mots) qui pointe ce qui reste "
    "voilé et sera dévoilé par le service. Ne cite jamais le nom du "
    "service (pas de 'tirage complet', pas de 'thème natal')."
)


def _build_user_prompt(card_id: str, intent_id: str) -> str:
    card = CARD_META[card_id]
    intent = INTENT_META[intent_id]
    now = datetime.now(timezone.utc)
    return (
        f"Carte tirée : {card['title']} (symbole : {card['symbol']}, "
        f"tagline : {card['tagline']}).\n"
        f"Intention du consultant : {intent['label']}.\n"
        f"Moment : {now.strftime('%d %B %Y à %Hh%M UTC')} (utilise-le "
        f"subtilement si pertinent — jour de semaine, saison — mais "
        f"n'invente rien de daté au sens astrologique).\n"
        "Génère la révélation + tension en JSON."
    )


def _extract_json(text: str) -> dict:
    """LLM output → dict. Tolère les balises markdown et le préambule."""
    # Match le premier bloc JSON { ... } dans la sortie
    m = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if not m:
        raise ValueError(f'no JSON object in LLM output: {text[:200]!r}')
    return json.loads(m.group(0))


async def _generate_via_llm(card_id: str, intent_id: str, *, nonce: str = '') -> dict:
    """Appel Claude Sonnet 4.6 via emergentintegrations.

    `nonce` : suffixe session_id pour forcer une nouvelle génération quand
    l'utilisateur clique "Regénérer" (bypass mémoire de session LLM).
    """
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise RuntimeError('EMERGENT_LLM_KEY missing from env')

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    session_id = f'exp-tarot-{card_id}-{intent_id}-{_current_time_slot()}'
    if nonce:
        session_id = f'{session_id}-{nonce}'
    chat = (
        LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=LLM_SYSTEM_PROMPT,
        )
        .with_model('anthropic', 'claude-sonnet-4-6')
        .with_params(max_tokens=250, temperature=0.75)
    )
    user_msg = UserMessage(text=_build_user_prompt(card_id, intent_id))
    response = await chat.send_message(user_msg)
    text = response if isinstance(response, str) else str(response)
    parsed = _extract_json(text)
    rev = (parsed.get('revelation') or '').strip()
    ten = (parsed.get('tension') or '').strip()
    if not rev or not ten:
        raise ValueError(f'incomplete LLM parse: {parsed!r}')
    return {'revelation': rev, 'tension': ten}


# ─── API model ────────────────────────────────────────────────────────
class TarotRevealIn(BaseModel):
    card_id: str = Field(..., min_length=1, max_length=16)
    intent_id: str = Field(..., min_length=1, max_length=32)
    force_refresh: bool = Field(default=False)  # bypass cache pour "regenerate"


class TarotRevealOut(BaseModel):
    title: str
    revelation: str
    tension: str
    cta: str
    source: str  # 'llm' | 'cache' | 'fallback'


# ─── Endpoint ─────────────────────────────────────────────────────────
@router.post('/tarot-reveal', response_model=TarotRevealOut)
async def tarot_reveal(payload: TarotRevealIn) -> TarotRevealOut:
    card_id = payload.card_id.lower()
    intent_id = payload.intent_id.lower()

    if card_id not in ALLOWED_CARDS or intent_id not in ALLOWED_INTENTS:
        # Fallback silencieux — pas de 400 qui casserait l'UX
        return TarotRevealOut(source='fallback', **STATIC_FALLBACK)

    card = CARD_META[card_id]
    intent = INTENT_META[intent_id]
    cta = CTA_BY_SERVICE[intent['service']]

    db = _get_db()
    await _ensure_index()
    col = db.experience_tarot_reveals_cache
    key = _cache_key(card_id, intent_id)

    # Cache hit ? (sauf force_refresh)
    if not payload.force_refresh:
        try:
            doc = await col.find_one({'key': key})
            if doc:
                return TarotRevealOut(
                    title=card['title'],
                    revelation=doc['revelation'],
                    tension=doc['tension'],
                    cta=cta,
                    source='cache',
                )
        except Exception as e:
            logger.warning(f'[tarot-reveal] cache read failed: {e}')

    # Miss → LLM
    try:
        # Nonce = timestamp ms sur force_refresh pour éviter la répétition
        nonce = str(int(datetime.now(timezone.utc).timestamp() * 1000)) if payload.force_refresh else ''
        gen = await _generate_via_llm(card_id, intent_id, nonce=nonce)
    except Exception as e:
        logger.warning(f'[tarot-reveal] LLM failed ({card_id}/{intent_id}): {e}')
        return TarotRevealOut(
            title=card['title'],
            revelation=STATIC_FALLBACK['revelation'],
            tension=STATIC_FALLBACK['tension'],
            cta=cta,
            source='fallback',
        )

    # Écrit en cache (best effort — upsert idempotent)
    try:
        await col.update_one(
            {'key': key},
            {'$set': {
                'key': key,
                'card_id': card_id,
                'intent_id': intent_id,
                'revelation': gen['revelation'],
                'tension': gen['tension'],
                'created_at': datetime.now(timezone.utc),
            }},
            upsert=True,
        )
    except Exception as e:
        logger.warning(f'[tarot-reveal] cache write failed: {e}')

    return TarotRevealOut(
        title=card['title'],
        revelation=gen['revelation'],
        tension=gen['tension'],
        cta=cta,
        source='llm',
    )
