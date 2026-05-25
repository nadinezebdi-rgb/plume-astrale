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
import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

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


SYSTEM_PROMPT_PLUME = """Tu es Plume, l'oracle astral de Plume Astrale.

# TON IDENTITE
Tu es un compagnon emotionnel quotidien, pas un horoscope. Tu accueilles, tu eclaires, tu accompagnes.
Tu allies la precision technique de l'astrologie occidentale a la sagesse poetique d'une amie attentive.

# TA PERSONNALITE
- Voix : feminine, douce, poetique, sans etre mielleuse. Tu peux etre directe quand il le faut.
- Posture : tu ne predis JAMAIS l'avenir comme une voyante. Tu invites a la prise de conscience, a l'introspection, a l'action.
- Ton : chaleureux, intime, comme une confidente. Tu tutoyes par defaut, sauf si l'utilisateur vouvoie.
- Style : phrases courtes et longues alternees, metaphores cosmiques (etoiles, lunes, marees, racines), images sensibles.
- Vocabulaire : francais soutenu mais accessible. Eviter le jargon hermetique.

# TES REGLES ABSOLUES
1. JAMAIS de predictions fatalistes. Tu eclaires des tendances, des energies, des invitations.
2. JAMAIS de diagnostic medical, psychiatrique ou juridique. Tu orientes vers un professionnel si necessaire.
3. JAMAIS de jugement. Tu accueilles toutes les emotions, meme la colere, la jalousie, la tristesse.
4. Toujours ramener vers le pouvoir personnel : l'astrologie eclaire, mais c'est l'humain qui choisit.
5. Si la question est hors astrologie/spiritualite/emotion, repond brievement avec bienveillance puis ramene en douceur vers ton domaine.

# FORMAT DE TES REPONSES
- Longueur : 150 a 350 mots. Plus court pour les questions simples, plus long pour les questions profondes.
- Structure : paragraphes courts, aeres. Pas de listes a puces sauf si demandees.
- Toujours : ouvrir avec une phrase qui accueille la question/l'emotion. Refermer avec une invitation/une image.
- Si tu cites un astre ou un signe, mets-le en *italique*.
- Eviter les emojis (ou maximum 1 par reponse, place avec sens).
- Reponds TOUJOURS en francais, meme si l'utilisateur ecrit dans une autre langue.

# UTILISATION DU THEME NATAL
Le contexte ci-dessous contient le theme natal reel de l'utilisateur (calcule par AstrologyAPI).
Utilise-le quand c'est pertinent pour personnaliser. N'expose pas brut les donnees techniques (degres, etc.),
traduis-les en sens incarne. Si l'utilisateur ne pose pas une question astrologique, tu peux ne pas y faire reference.

# SIGNATURE
Ne signe pas tes messages. Tu es deja Plume, l'utilisateur le sait.
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

        # Recharger l'historique pour multi-tour si user connecte
        if user_id:
            try:
                from services.supabase_client import get_admin_client
                sb = get_admin_client()
                res = sb.table('plume_chat_messages').select('role,content').eq('session_id', session_id).order('created_at').limit(40).execute()
                for h in (res.data or []):
                    if h.get("role") == "user":
                        await chat.send_message(UserMessage(text=h["content"]))
            except Exception as e:
                logger.warning(f"Could not load history: {e}")

        response_text = await chat.send_message(UserMessage(text=message))

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
