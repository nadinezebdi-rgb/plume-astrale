"""
Service de traduction IA pour le contenu astrologique
Traduit les reponses API (anglais) en francais avec vocabulaire esoterique
"""
import os
import hashlib
import logging
from dotenv import load_dotenv
from integrations.llm.chat import LlmChat, UserMessage

load_dotenv()
logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")

# Simple in-memory cache to avoid re-translating identical content
_translation_cache = {}

SYSTEM_PROMPT = """Tu es un traducteur specialise en astrologie et esoterisme. Tu traduis de l'anglais vers le francais avec un style poetique et mystique, adapte a une plateforme de guidance spirituelle appelee "Plume Astrale".

Regles:
- Utilise le vocabulaire astrologique francais correct (Trigone, Carre, Sextile, Opposition, Conjonction)
- Garde un ton bienveillant, inspirant et pedagogique
- Traduis les noms des planetes (Sun=Soleil, Moon=Lune, Mercury=Mercure, Venus=Venus, Mars=Mars, Jupiter=Jupiter, Saturn=Saturne, Uranus=Uranus, Neptune=Neptune, Pluto=Pluton)
- Traduis les signes (Aries=Belier, Taurus=Taureau, Gemini=Gemeaux, Cancer=Cancer, Leo=Lion, Virgo=Vierge, Libra=Balance, Scorpio=Scorpion, Sagittarius=Sagittaire, Capricorn=Capricorne, Aquarius=Verseau, Pisces=Poissons)
- Traduis les maisons (1st House=Maison 1, etc.)
- Ne traduis pas les noms propres
- Retourne UNIQUEMENT la traduction, sans commentaire ni explication
- Tutoie le lecteur pour creer de la proximite"""


async def translate_to_french(text: str) -> str:
    """Translate English astrological text to French using LLM"""
    if not text or not text.strip():
        return text
    if not EMERGENT_KEY:
        logger.warning("No EMERGENT_LLM_KEY, returning original text")
        return text

    # Check cache
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in _translation_cache:
        return _translation_cache[cache_key]

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"translate_{cache_key[:8]}",
            system_message=SYSTEM_PROMPT
        )
        chat.with_model("openai", "gpt-4o-mini")

        msg = UserMessage(text=f"Traduis ce texte astrologique en francais:\n\n{text}")
        response = await chat.send_message(msg)

        if response:
            result = response.strip()
            _translation_cache[cache_key] = result
            return result
    except Exception as e:
        logger.error(f"Translation error: {e}")

    return text


async def translate_dict_values(data: dict, keys_to_translate: list) -> dict:
    """Translate specific keys in a dictionary"""
    result = dict(data)
    for key in keys_to_translate:
        if key in result and isinstance(result[key], str) and result[key].strip():
            result[key] = await translate_to_french(result[key])
    return result


async def translate_list_of_dicts(items: list, keys_to_translate: list) -> list:
    """Translate specific keys in a list of dictionaries"""
    results = []
    for item in items:
        if isinstance(item, dict):
            translated = await translate_dict_values(item, keys_to_translate)
            results.append(translated)
        else:
            results.append(item)
    return results
