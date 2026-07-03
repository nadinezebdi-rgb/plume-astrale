"""
Plume IA — Chat astrologique premium en français
Utilise GPT-5.4 via emergentintegrations + thème natal calculé via AstrologyAPI

Architecture :
1. Le frontend envoie : { message, session_id, birth_data }
2. Au PREMIER message d'une session, on enrichit le contexte avec le thème natal réel
3. GPT-5.4 répond avec la personnalité "Plume" — astrologue mystique francophone
4. Les messages sont stockés dans MongoDB pour persistance multi-tour
"""
import os
import re
import json as _json
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

# Detection d'une fuite d'appel d'outil dans la reponse du modele
_TOOL_LEAK_RE = re.compile(r'^\s*\{[\s\S]*"action"[\s\S]*"action_input"[\s\S]*\}\s*$')


def is_tool_leak(text: str) -> bool:
    """Retourne True si le texte ressemble a un appel d'outil JSON (leak)."""
    if not text or len(text) > 3000:
        return False
    if not _TOOL_LEAK_RE.match(text):
        return False
    try:
        obj = _json.loads(text.strip())
        return isinstance(obj, dict) and ('action' in obj or 'action_input' in obj)
    except Exception:
        return False

# Mapping des signes en français
SIGNS_FR = {
    "Aries": "Belier", "Taurus": "Taureau", "Gemini": "Gemeaux",
    "Cancer": "Cancer", "Leo": "Lion", "Virgo": "Vierge",
    "Libra": "Balance", "Scorpio": "Scorpion", "Sagittarius": "Sagittaire",
    "Capricorn": "Capricorne", "Aquarius": "Verseau", "Pisces": "Poissons",
}

PLANETS_FR = {
    "Sun": "Soleil", "Moon": "Lune", "Mercury": "Mercure", "Venus": "Venus",
    "Mars": "Mars", "Jupiter": "Jupiter", "Saturn": "Saturne", "Uranus": "Uranus",
    "Neptune": "Neptune", "Pluto": "Pluton", "Ascendant": "Ascendant",
}


SYSTEM_PROMPT_PLUME = """Tu es Plume, astrologue, tarologue et medium de grande renommee, reconnue pour la precision de tes intuitions, ta bienveillance et ta capacite a accompagner les ames sur leur chemin de vie. Ton approche est holistique : tu consideres le consultant dans sa globalite (esprit, emotions, energies), tout en respectant une ethique et une deontologie professionnelles absolues.

Adopte les directives suivantes pour chacune de tes reponses :

1. CADRE ETHIQUE ET SECURITE (Barriere stricte sur la sante) :
- Tu as l'interdiction absolue de poser des diagnostics medicaux, de commenter des pathologies, de donner des conseils d'ordre medical ou de te prononcer sur l'evolution de la sante physique ou psychologique d'un consultant.
- Si un consultant pose une question liee a sa sante (maladie, traitement, grossesse a risque, guerison), tu dois poser une barriere immediate, bienveillante mais ferme : rappelle-lui que tu n'es pas medecin et invite-le a consulter un professionnel de sante. Tu peux ensuite reorienter la seance uniquement sur le plan emotionnel ou spirituel.

2. TON ET STYLE : 
Inspirant, mystique mais ancre, chaleureux et empathique. Tu es une alliee et un miroir. Utilise un vocabulaire riche et vibratoire (alignement, resonance, flux energetique, cycles).

3. METHODOLOGIE ET APPROCHE HOLISTIQUE :
- Les Etoiles & l'Ame : appuie-toi sur les elements du theme natal fournis (Signe solaire, Lunaire, Ascendant, maisons).
- Les Messages Subtils : integre le Tarot ou tes ressentis mediumniques pour eclairer la situation presente.
- Conseils Holistiques (Bien-etre uniquement) : rituels symboliques, meditation, shadow work, pierres, plantes — TOUJOURS presentes comme complements de confort, jamais comme des remedes.

4. FORMATTING :
- Utilise des titres clairs (## L'Echo des Etoiles, ### Conseils et Rituels de Confort).
- Utilise **le gras** pour les mots-cles.
- Separe tes idees par --- pour rendre la lecture fluide.

5. REGLE D'OR (Ne jamais clore) :
- Ne termine JAMAIS par une conclusion fermee.
- Termine TOUJOURS par une question ouverte, curieuse, personnalisee, qui invite le consultant a explorer ses emotions, ses ressentis, ou la facon dont son theme natal resonne dans sa vie actuelle.

6. REGLES TECHNIQUES ABSOLUES :
- Reponds TOUJOURS en francais naturel, jamais en JSON, jamais en code, jamais en anglais.
- N'emets JAMAIS de blocs JSON, "action", "action_input" ou d'appels de fonction.
- Le theme natal du consultant t'est deja fourni ci-dessous ; utilise-le directement, aucun outil a appeler.
"""


def _build_natal_context(birth_data: Dict[str, Any], horoscope: Dict[str, Any]) -> str:
    """Convertit le theme natal brut d'AstrologyAPI en contexte lisible pour le LLM."""
    if not horoscope or "planets" not in horoscope:
        return ""

    name = birth_data.get("name", "L'ame")
    parts = [f"\n# CONTEXTE — THEME NATAL DE {name.upper()}"]
    parts.append(f"Date : {birth_data.get('day')}/{birth_data.get('month')}/{birth_data.get('year')} a {birth_data.get('hour'):02d}h{birth_data.get('min', 0):02d}")
    parts.append(f"Lieu : {birth_data.get('place', '?')}")

    planets = horoscope.get("planets", [])
    houses = horoscope.get("houses", [])

    # Planetes principales
    key_planets = ["Sun", "Moon", "Ascendant", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    parts.append("\n## Planetes principales (signe — maison)")
    for p in planets:
        if p.get("name") in key_planets:
            name_fr = PLANETS_FR.get(p["name"], p["name"])
            sign_fr = SIGNS_FR.get(p.get("sign", ""), p.get("sign", "?"))
            house = p.get("house", "?")
            retro = " (retrograde)" if str(p.get("is_retro", "false")).lower() == "true" else ""
            parts.append(f"- {name_fr} en {sign_fr}, maison {house}{retro}")

    # Maisons cardinales (1, 4, 7, 10)
    if houses:
        parts.append("\n## Maisons cardinales (axes de vie)")
        for h in houses:
            if h.get("house") in [1, 4, 7, 10]:
                sign_fr = SIGNS_FR.get(h.get("sign", ""), h.get("sign", "?"))
                axis = {1: "Ascendant (identite)", 4: "Fond du ciel (racines)", 7: "Descendant (relations)", 10: "Milieu du ciel (vocation)"}.get(h["house"], "")
                parts.append(f"- Maison {h['house']} en {sign_fr} — {axis}")

    parts.append("\n(Utilise ce contexte avec subtilite, sans deballer les donnees techniques.)\n")
    return "\n".join(parts)


async def _fetch_natal_chart(birth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Recupere le theme natal complet via AstrologyAPI (western_horoscope)."""
    user_id = os.environ.get("ASTROLOGY_API_USER_ID")
    api_key = os.environ.get("ASTROLOGY_API_KEY")
    if not user_id or not api_key:
        return None
    try:
        payload = {
            "day": int(birth_data.get("day", 1)),
            "month": int(birth_data.get("month", 1)),
            "year": int(birth_data.get("year", 1990)),
            "hour": int(birth_data.get("hour", 12)),
            "min": int(birth_data.get("min", 0)),
            "lat": float(birth_data.get("lat", 48.8566)),
            "lon": float(birth_data.get("lon", 2.3522)),
            "tzone": float(birth_data.get("tzone", 1)),
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                "https://json.astrologyapi.com/v1/western_horoscope",
                auth=(user_id, api_key),
                json=payload,
                headers={"Accept-Language": "fr"},
            )
            if r.status_code == 200:
                return r.json()
            logger.warning(f"western_horoscope returned {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.warning(f"Failed to fetch natal chart: {e}")
    return None


async def plume_chat(
    message: str,
    session_id: str,
    birth_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Point d'entree principal — historique stocke dans Supabase."""
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        return {"success": False, "message": "Cle LLM non configuree."}

    system_message = SYSTEM_PROMPT_PLUME
    if birth_data:
        horoscope = await _fetch_natal_chart(birth_data)
        if horoscope:
            system_message += _build_natal_context(birth_data, horoscope)

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message,
        ).with_model("openai", "gpt-4o-mini")
        try:
            chat = chat.with_params(temperature=0.8, max_tokens=1200)
        except Exception:
            pass

        # Recharger l'historique pour multi-tour si user connecte
        if user_id:
            try:
                from services.supabase_client import get_admin_client
                sb = get_admin_client()
                res = sb.table('plume_chat_messages').select('role,content').eq('session_id', session_id).order('created_at').limit(40).execute()
                for h in (res.data or []):
                    if h.get("role") == "user" and not is_tool_leak(h.get("content", "")):
                        await chat.send_message(UserMessage(text=h["content"]))
            except Exception as e:
                logger.warning(f"Could not load history: {e}")

        response_text = await chat.send_message(UserMessage(text=message))

        # Garde-fou : si la reponse est une fuite d'outil JSON, on retente 1x
        if is_tool_leak(response_text):
            logger.warning(f"[plume_chat] tool leak detected, retrying: {response_text[:100]}")
            retry_msg = (
                "Ta reponse precedente contenait un JSON technique au lieu d'un vrai message. "
                "Reponds de nouveau a ma question, en francais naturel et poetique, "
                "sans aucun bloc JSON ni appel de fonction. Termine par une question ouverte."
            )
            response_text = await chat.send_message(UserMessage(text=retry_msg))
            if is_tool_leak(response_text):
                response_text = (
                    "Les astres sont un peu bavards ce soir. Peux-tu reformuler ta question, "
                    "ou me dire ce qui t'a amene(e) a Plume aujourd'hui ?"
                )

        # Persister dans Supabase si user connecte
        if user_id:
            try:
                from services.supabase_client import get_admin_client
                sb = get_admin_client()
                sb.table('plume_chat_messages').insert([
                    {"session_id": session_id, "user_id": user_id, "role": "user", "content": message},
                    {"session_id": session_id, "user_id": user_id, "role": "assistant", "content": response_text},
                ]).execute()
            except Exception as e:
                logger.warning(f"Could not persist messages: {e}")

        return {"success": True, "answer": response_text, "session_id": session_id}

    except Exception as e:
        logger.error(f"Plume chat error: {e}", exc_info=True)
        return {"success": False, "message": "Les astres traversent une zone d'ombre. Reessaie dans un instant."}


async def get_session_history(session_id: str, user_id: Optional[str] = None) -> list:
    """Recupere l'historique d'une session pour le frontend."""
    if not user_id:
        return []
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        res = sb.table('plume_chat_messages').select('role,content').eq('session_id', session_id).eq('user_id', user_id).order('created_at').limit(100).execute()
        return [{"role": m["role"], "content": m["content"]} for m in (res.data or [])]
    except Exception as e:
        logger.warning(f"Could not load session history: {e}")
        return []
