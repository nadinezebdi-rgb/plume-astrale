"""
Couche d'enrichissement narrative universelle.

Prend un texte brut (souvent factuel/court) issu de l'API v3 ou de calculs
locaux, et le passe dans GPT-5.4 pour :
  1. Le rallonger (2-3× la longueur, ton poétique Soléna)
  2. Terminer TOUJOURS par une question engageante à l'utilisatrice

Cache mémoire + Supabase (`narrative_cache`) pour éviter les surcoûts.

Usage :
    from services.enrich_narrative import enrich_and_ask
    enriched = await enrich_and_ask(
        text="Ta Vénus en Taureau...",
        context="astrosexo_venus",
        first_name="Marie",
    )
"""
from __future__ import annotations
import hashlib
import json
import logging
import os
from typing import Any

from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# Cache mémoire (per-process)
_MEM_CACHE: dict[str, str] = {}
_MAX_MEM = 400

SYSTEM_MSG = (
    "Tu es Soléna, guide astrologique française chez Plume Astrale. "
    "Tu écris exclusivement en FRANÇAIS impeccable, avec tous les accents et cédilles correctement placés. "
    "Ton ton est poétique, sensuel, précis, ni New Age ni technique. Tu tutoies. "
    "Tu ne cites JAMAIS de scores chiffrés ni de jargon anglais. "
    "Tu réponds uniquement en JSON valide, jamais en markdown."
)


def _hash(text: str, context: str, first_name: str = "") -> str:
    return hashlib.sha256(f"{context}|{first_name}|{text}".encode()).hexdigest()[:32]


def _add_mem(h: str, value: str) -> None:
    if len(_MEM_CACHE) >= _MAX_MEM:
        _MEM_CACHE.pop(next(iter(_MEM_CACHE)))
    _MEM_CACHE[h] = value


async def enrich_and_ask(
    text: str,
    context: str = "",
    first_name: str = "toi",
    target_length: str = "long",   # 'short' | 'medium' | 'long'
) -> str:
    """Enrichit un texte + termine par une question. Cache mémoire + DB."""
    if not text or not text.strip():
        return text
    text = text.strip()
    if len(text) < 20:
        return text  # trop court pour enrichir

    h = _hash(text, context, first_name.lower())

    # 1) Cache mémoire
    if h in _MEM_CACHE:
        return _MEM_CACHE[h]

    # 2) Cache DB
    try:
        sb = get_admin_client()
        res = sb.table('narrative_cache').select('enriched_text').eq('key', h).maybe_single().execute()
        if res and res.data and res.data.get('enriched_text'):
            e = res.data['enriched_text']
            _add_mem(h, e)
            return e
    except Exception:
        pass  # table peut ne pas exister

    api_key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not api_key:
        return text

    length_hint = {
        'short': "environ 4-6 phrases (150-200 mots)",
        'medium': "environ 8-12 phrases (250-350 mots)",
        'long': "environ 15-20 phrases (400-550 mots)",
    }.get(target_length, "environ 15-20 phrases")

    fn_display = first_name.strip().title() or "toi"

    prompt = f"""Réécris ce texte astrologique pour {fn_display} en français poétique et sensuel.

Texte source :
「{text}」

Consignes strictes :
- Longueur cible : {length_hint}.
- Tutoie {fn_display}.
- Développe chaque idée avec des images, des sensations concrètes, des exemples de vie.
- Garde toutes les informations factuelles du texte source.
- Ne mentionne aucun score chiffré, aucun jargon anglais, aucune abréviation astro.
- Termine OBLIGATOIREMENT par une question personnelle qui invite {fn_display} à s'introspecter (ex : "Quelle est la première chose que tu ressens en lisant ces lignes ?", "Où cette énergie s'exprime-t-elle déjà dans ta vie ?", "Quel geste concret voudrais-tu poser aujourd'hui ?").

Réponds en JSON strict : {{"text": "ton texte enrichi FR se terminant par une question"}}"""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"enrich-{context}-{h}",
            system_message=SYSTEM_MSG,
        ).with_model("openai", "gpt-5.4")
        resp = await chat.send_message(UserMessage(text=prompt))
        parsed = _parse_json(resp) or {}
        enriched = (parsed.get("text") or "").strip()
        if not enriched:
            return text
        # Sécurité : forcer une question à la fin si l'IA a oublié
        if not enriched.rstrip().endswith('?'):
            enriched = enriched.rstrip('.,;: ') + "\n\nEt toi, qu'est-ce que ça éveille en toi ?"
        _add_mem(h, enriched)
        # Cache DB (best-effort)
        try:
            sb = get_admin_client()
            sb.table('narrative_cache').upsert({
                'key': h, 'source_text': text[:3000], 'enriched_text': enriched[:5000],
                'context': context[:100], 'first_name': first_name[:60],
            }).execute()
        except Exception:
            pass
        return enriched
    except Exception as e:
        logger.warning(f"[enrich_narrative] failed for {context}: {e}")
        return text


async def enrich_dict_fields(
    obj: Any,
    fields: list[str],
    context: str = "",
    first_name: str = "toi",
    target_length: str = "long",
) -> Any:
    """Enrichit uniquement les champs listés d'un dict/list (ex: ['description', 'meaning'])."""
    if isinstance(obj, dict):
        out = dict(obj)
        for k, v in out.items():
            if k in fields and isinstance(v, str):
                out[k] = await enrich_and_ask(v, context=f"{context}.{k}", first_name=first_name, target_length=target_length)
            elif isinstance(v, (dict, list)):
                out[k] = await enrich_dict_fields(v, fields, context=f"{context}.{k}", first_name=first_name, target_length=target_length)
        return out
    if isinstance(obj, list):
        return [await enrich_dict_fields(v, fields, context=context, first_name=first_name, target_length=target_length) for v in obj]
    return obj


def _parse_json(txt: str) -> dict | None:
    if not txt:
        return None
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
        return None


# Migration SQL (à appliquer côté Supabase Studio en même temps que les autres)
NARRATIVE_CACHE_SQL = """
create table if not exists public.narrative_cache (
    key text primary key,
    source_text text not null,
    enriched_text text not null,
    context text,
    first_name text,
    created_at timestamptz not null default now()
);
create index if not exists idx_narrative_cache_context on public.narrative_cache (context);
"""
