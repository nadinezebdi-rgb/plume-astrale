"""Post-processing OpenAI pour garantir 100% FR avec accents.

Détecte les segments anglais dans les réponses API v3 et les réécrit en français
poétique via GPT-5.4. Cache en mémoire + Supabase pour éviter les surcoûts.

Usage :
    from services.french_polish import polish_dict
    data = await polish_dict(data, context="love_languages")
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
import re
from typing import Any, Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# In-memory cache (per-process) — clé = hash du texte, valeur = traduction FR
_MEM_CACHE: dict[str, str] = {}
_MAX_MEM_ITEMS = 500

# Heuristique : détecte un texte majoritairement anglais
_ENGLISH_WORDS = re.compile(
    r'\b(the|and|of|to|in|is|you|that|for|with|are|this|as|be|have|will|not|it|your|from|they|which|one|all|there|been|has|more|when|who|its|may|about|but|can|other|would|these|our|these|their|his|her|so|out|up|about|make|help|life|love|energy|planet|planetary|influence|strength|score|meaning|health|career|finance|identity|relationships|creativity|spirituality|travel|home|learning|communication|wealth|power|leadership|recognition|authority|confidence|success|professional|charisma|magnified|shine|natural|emerges|magnetic|attractive|creative|passionate|romantic|inspiring|expressive|dynamic|vital|noble|ambitious|innovative|independent|adventurous)\b',
    re.IGNORECASE,
)
_FR_ACCENTS = re.compile(r'[éèêëàâäîïôöùûüçÉÈÊËÀÂÄÎÏÔÖÙÛÜÇ]')


def _is_english(text: str) -> bool:
    """Retourne True si le texte semble anglais (heuristique légère)."""
    if not isinstance(text, str) or len(text) < 30:
        return False
    # Compter mots anglais typiques
    english_matches = len(_ENGLISH_WORDS.findall(text))
    fr_accents = len(_FR_ACCENTS.findall(text))
    words = max(1, len(text.split()))
    density = english_matches / words
    # Si densité anglaise > 8% ET très peu d'accents → probablement anglais
    return density > 0.08 and fr_accents < 3


def _hash(text: str, context: str) -> str:
    return hashlib.sha256(f"{context}|{text}".encode()).hexdigest()[:32]


async def _polish_text(text: str, context: str = "") -> str:
    """Traduit/réécrit un texte anglais en FR poétique. Cache mémoire + DB."""
    if not text or not _is_english(text):
        return text

    h = _hash(text, context)

    # 1) Cache mémoire
    if h in _MEM_CACHE:
        return _MEM_CACHE[h]

    # 2) Cache DB (Supabase table translation_cache)
    try:
        sb = get_admin_client()
        res = sb.table('translation_cache').select('fr_text').eq('key', h).maybe_single().execute()
        if res and res.data and res.data.get('fr_text'):
            fr = res.data['fr_text']
            _add_mem(h, fr)
            return fr
    except Exception:
        pass  # table peut ne pas exister — non-bloquant

    # 3) Appel OpenAI
    api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not api_key:
        return text

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"polish-{h}",
            system_message=(
                "Tu es un traducteur français expert en astrologie. "
                "Tu réécris un texte anglais en FRANÇAIS impeccable, poétique, avec tous les accents. "
                "Tu conserves le sens exact. Tu ne cites pas de scores chiffrés. "
                "Tu tutoies. Tu ne rajoutes rien, tu réponds uniquement avec le texte traduit."
            ),
        ).with_model("openai", "gpt-5.4")
        resp = await chat.send_message(UserMessage(text=f"Traduis en français poétique :\n\n{text}"))
        fr = (resp or "").strip()
        if fr:
            _add_mem(h, fr)
            # Écrire en cache DB (best-effort)
            try:
                sb = get_admin_client()
                sb.table('translation_cache').upsert({
                    'key': h, 'source_text': text[:2000], 'fr_text': fr[:2000], 'context': context[:100],
                }).execute()
            except Exception:
                pass
            return fr
    except Exception as e:
        logger.warning(f"[french_polish] OpenAI failed for {context}: {e}")

    return text


def _add_mem(h: str, fr: str) -> None:
    if len(_MEM_CACHE) >= _MAX_MEM_ITEMS:
        # Purge simple : retire un item au hasard
        _MEM_CACHE.pop(next(iter(_MEM_CACHE)))
    _MEM_CACHE[h] = fr


# Clés à ne PAS traduire (données techniques, non affichées)
_SKIP_KEYS = {
    'id', 'uuid', 'key', 'code', 'name', 'code_iso', 'planet', 'sign', 'house', 'element', 'modality',
    'polarity', 'aspect', 'aspect_type', 'source', 'type', 'category', 'gender', 'system', 'tradition',
    'language', 'timezone', 'tz_name', 'city', 'country', 'country_code',
    'latitude', 'longitude', 'created_at', 'updated_at', 'success', 'status',
    'sun_sign', 'moon_sign', 'ascendant_sign', 'rising_sign', 'first_name', 'last_name',
    'line_type', 'angle', 'zodiac_sign', 'planet_name',
}


async def polish_dict(obj: Any, context: str = "", _depth: int = 0) -> Any:
    """Parcourt récursivement un dict/list et traduit les string anglaises.

    Optimisation : détecte TOUTES les strings anglaises en un seul parcours,
    puis les traduit toutes en UN SEUL appel GPT batché.

    Args:
        obj : dict, list ou string à traiter
        context : contexte pour le cache (ex: "love_languages", "energy_daily")

    Retourne l'objet avec les strings anglaises remplacées par leur version FR.
    """
    # 1) Collecte de toutes les strings anglaises (path + text)
    to_polish: list[tuple[list, str]] = []

    def _collect(o, path, depth=0):
        if depth > 12:
            return
        if isinstance(o, str):
            if _is_english(o):
                to_polish.append((path[:], o))
            return
        if isinstance(o, list):
            for i, v in enumerate(o):
                _collect(v, path + [i], depth + 1)
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and k.lower() in _SKIP_KEYS:
                    continue
                _collect(v, path + [k], depth + 1)

    _collect(obj, [])

    if not to_polish:
        return obj

    # 2) Vérifier le cache mémoire/DB pour chaque string
    to_call: list[tuple[list, str, str]] = []   # (path, text, hash)
    resolved: dict[str, str] = {}
    for path, text in to_polish:
        h = _hash(text, context)
        if h in _MEM_CACHE:
            resolved[h] = _MEM_CACHE[h]
        else:
            to_call.append((path, text, h))

    # 3) Cache DB en batch
    if to_call:
        try:
            sb = get_admin_client()
            keys = [t[2] for t in to_call]
            res = sb.table('translation_cache').select('key,fr_text').in_('key', keys).execute()
            for row in (res.data or []):
                resolved[row['key']] = row['fr_text']
                _add_mem(row['key'], row['fr_text'])
        except Exception:
            pass

    # 4) Appels OpenAI batchés pour les restants
    remaining = [t for t in to_call if t[2] not in resolved]
    if remaining:
        api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
        if api_key:
            try:
                # Batch : envoyer TOUTES les strings à traduire en 1 appel
                numbered = "\n".join(f"[{i}] {t[1]}" for i, t in enumerate(remaining))
                chat = LlmChat(
                    api_key=api_key,
                    session_id=f"polish-batch-{context}-{len(remaining)}",
                    system_message=(
                        "Tu es un traducteur français expert en astrologie. "
                        "Tu réécris des textes anglais en FRANÇAIS impeccable, poétique, avec tous les accents. "
                        "Tu conserves le sens exact. Tu tutoies. "
                        "Tu réponds par une liste JSON stricte avec exactement les mêmes indices numérotés. "
                        "Format : {\"0\": \"texte fr\", \"1\": \"texte fr\", ...}"
                    ),
                ).with_model("openai", "gpt-5.4")
                resp = await chat.send_message(UserMessage(
                    text=f"Traduis chaque ligne en français poétique. Garde exactement les mêmes indices :\n\n{numbered}"
                ))
                # Parser JSON
                translations = _parse_json_batch(resp)
                for i, (path, text, h) in enumerate(remaining):
                    fr = translations.get(str(i)) or translations.get(i)
                    if fr and isinstance(fr, str) and fr.strip():
                        resolved[h] = fr.strip()
                        _add_mem(h, fr.strip())
                # Sauver en DB en batch
                try:
                    sb = get_admin_client()
                    rows = [
                        {'key': h, 'source_text': text[:2000], 'fr_text': resolved[h][:2000], 'context': context[:100]}
                        for path, text, h in remaining if h in resolved
                    ]
                    if rows:
                        sb.table('translation_cache').upsert(rows).execute()
                except Exception:
                    pass
            except Exception as e:
                logger.warning(f"[french_polish] batch failed for {context}: {e}")

    # 5) Appliquer les traductions sur une copie de l'objet
    if not resolved:
        return obj

    import copy
    out = copy.deepcopy(obj)
    for path, text in to_polish:
        h = _hash(text, context)
        if h in resolved:
            _set_path(out, path, resolved[h])
    return out


def _set_path(obj, path, value):
    """Applique une valeur à un chemin (liste d'indices/clés)."""
    if not path:
        return
    target = obj
    for step in path[:-1]:
        target = target[step]
    target[path[-1]] = value


def _parse_json_batch(txt: str) -> dict:
    """Parse la réponse JSON du batch OpenAI."""
    if not txt:
        return {}
    t = txt.strip()
    if t.startswith('```'):
        t = t.strip('`')
        if t.lower().startswith('json'):
            t = t[4:]
        t = t.strip()
    try:
        start = t.index('{')
        end = t.rindex('}')
        return json.loads(t[start:end + 1])
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════
# Migration SQL pour créer la table de cache (à appliquer en Supabase Studio)
# ═══════════════════════════════════════════════════════════
TRANSLATION_CACHE_SQL = """
create table if not exists public.translation_cache (
    key text primary key,
    source_text text not null,
    fr_text text not null,
    context text,
    created_at timestamptz not null default now()
);
create index if not exists idx_translation_cache_context on public.translation_cache (context);
comment on table public.translation_cache is 'Cache des traductions FR OpenAI pour éviter les re-appels sur du contenu identique.';
"""
