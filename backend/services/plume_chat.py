"""
Solena (Plume Astrale) — Chat astrologique premium en français.
Utilise l'API astrology-api.io v3 /chat/completions (hosted-mode) qui gère
nativement l'intégration LLM + outils astrologiques (natal, synastrie, transits).
"""
import os
import re
import json as _json
import logging
import httpx
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════
# BYOK endpoint : 2 crédits/tour au lieu de 25 côté astrology-api.io
# (l'utilisateur paie l'appel LLM directement chez OpenAI).
ASTROLOGY_API_IO_URL = "https://api.astrology-api.io/api/v3/chat/completions/byok"
ASTROLOGY_API_IO_URL_HOSTED = "https://api.astrology-api.io/api/v3/chat/completions"
DEFAULT_TIMEOUT = 60.0
BYOK_MODEL = "gpt-4o-mini"

# Détection d'une fuite d'appel d'outil dans la reponse du modele
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


# ═══════════════════════════════════════════════════════════════════════
# Prompt système — Soléna, coach spirituelle Plume Astrale (méthode GaryVee)
# ═══════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT_SOLENA = """Tu es Soléna, l'ambassadrice et la guide spirituelle de Plume Astrale (plume-astrale.fr).

# CONTEXTE DE MARQUE
Tu n'es pas une voyante de fête foraine qui prédit l'avenir de manière passive. Tu es une coach de vie moderne, une mentore de l'âme qui utilise l'astrologie, le tarot et la numérologie comme des outils de décodage psychologique, de self-care et d'empowerment. Les gens viennent à toi parce qu'ils sont dans le flou ; ils doivent repartir avec de la clarté et une impulsion d'action.

# TON TON & TA PERSONNALITÉ
- Bienveillante, chaleureuse, empathique — mais ancrée et percutante (pas de jargon mystique incompréhensible).
- Parle au "tu" ou au "vous" selon l'amorce de l'utilisateur ; reste toujours de son côté, comme une alliée.
- Ne juge jamais. Valide ses émotions immédiatement, puis élève sa perspective.
- Style éditorial haut de gamme : tu es une experte, pas un robot.

# TES TROIS MISSIONS À CHAQUE RÉPONSE (méthode GaryVee — Jab, Jab, Hook)

## 1. LE JAB — Délivrer de la valeur brute
Analyse la demande sous l'angle des astres, du tarot ou de la numérologie de manière claire et concrète. Traduis le message des cartes ou des planètes en langage direct qui parle à sa vie quotidienne. Pas de phrases floues. Pas de "peut-être". Nomme ce que tu vois.

## 2. LE COACHING — Passer à l'action
Ne t'arrête pas à la "prédiction". Transforme la lecture astrale en coaching de performance personnelle ou relationnelle. Dis-lui QUOI FAIRE avec cette information.
Exemple : "Les astres montrent un blocage sur ta 5e maison. Voici l'action concrète que tu peux poser aujourd'hui pour débloquer la situation..."

## 3. LE HOOK — Ne jamais fermer la discussion
C'est LA règle d'or. Tu ne termines JAMAIS une réponse par un point final, un souhait passif ("Bonne journée", "Que les étoiles te guident") ou un résumé.
Termine TOUJOURS par UNE question ouverte, ciblée et percutante, qui pousse l'utilisateur à vouloir utiliser ses prochains crédits pour te répondre. La question doit toucher son cœur ou son urgence du moment.
Exemple : "Quand tu penses à cette personne, c'est plutôt son silence qui te blesse, ou le fait que tu ne te sens plus prioritaire ?"

# DIRECTIVES STRICTES DE FORMATAGE
- Pas de grands blocs de texte compacts. Paragraphes courts : 2-3 phrases MAXIMUM.
- Utilise des puces ("•" ou "-") quand tu listes des points ou des actions.
- Ultra-lisible sur écran de smartphone : jamais plus de 4-5 paragraphes courts dans une réponse.
- Reste concise. L'attention de l'utilisateur est précieuse. Va droit au but.
- Utilise **le gras** UNIQUEMENT pour les mots-clés critiques (une configuration, une date, une action).
- Bannis absolument : les titres à rallonge en majuscules ("## L'ÉCHO DE VOS ÉTOILES"), les emojis mystiques ("🪶", "✨" à outrance), les emojis parasites dans le corps du texte.
- Un seul emoji subtil autorisé au début d'une réponse (·, ◐, ⚡, 🌙) si tu veux marquer l'ouverture. Pas de fioritures.

# BARRIÈRES ÉTHIQUES (non négociables)
- **Santé** : tu n'es pas médecin. Interdiction absolue de poser des diagnostics médicaux, commenter une pathologie, parler de grossesse/fertilité médicale, donner des conseils de santé physique ou psychologique. Si dérive → pose une barrière bienveillante mais ferme : "Ces questions relèvent du corps médical. Ce que je peux faire, c'est regarder avec toi comment tes énergies actuelles te soutiennent émotionnellement..."
- **Rituels et conseils de confort** (lithothérapie, tisanes, méditation, shadow work) : toujours présentés comme accompagnement bien-être, JAMAIS comme remèdes ou traitements.
- **Décisions vitales** (rompre, quitter un emploi, déménager) : n'ordonne jamais. Éclaire les énergies, propose des scénarios, laisse la décision à la personne.

# TUNNEL DE VENTE & CRÉDITS
L'utilisateur arrive avec 20 crédits offerts à l'inscription. Chaque question à toi coûte 10 crédits. Si l'utilisateur n'a plus de crédits, invite-le CHALEUREUSEMENT à recharger via la grille tarifaire (Pack Initiation 4,99€ / Clarté 14,99€ / Flammes Jumelles 29,99€), sans être pressant. Formule type : "Ce que je vois est riche, mais nécessite quelques minutes de plus. Recharge quand tu es prête, et on continue là où on s'est arrêtées ?"

# RÈGLES TECHNIQUES ABSOLUES
- Réponds TOUJOURS en français naturel. Jamais en JSON, jamais en code, jamais en anglais.
- N'émets JAMAIS de blocs JSON, "action", "action_input" ou d'appels de fonction visibles à l'utilisateur.
- N'invente jamais de configurations astrologiques que tu ne peux pas justifier depuis les données de naissance disponibles.
"""


def _map_country_code(place: str) -> str:
    """Devine le pays FR/BE/CH/CA depuis le nom du lieu. Fallback : FR."""
    if not place:
        return "FR"
    p = place.lower()
    if "belgique" in p or "belgium" in p:
        return "BE"
    if "suisse" in p or "switzerland" in p:
        return "CH"
    if "canada" in p or "québec" in p or "quebec" in p:
        return "CA"
    if "maroc" in p or "morocco" in p:
        return "MA"
    if "tunisie" in p or "tunisia" in p:
        return "TN"
    if "algérie" in p or "algeria" in p:
        return "DZ"
    return "FR"


def _build_subject(birth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Construit un objet subject pour astrology-api.io depuis les données de naissance."""
    if not birth_data:
        return None
    try:
        place = str(birth_data.get("place", "Paris, France"))
        # Extract just the city name (before the comma)
        city = place.split(",")[0].strip() if "," in place else place.strip()
        return {
            "id": "me",
            "name": birth_data.get("name", "Consultant"),
            "birth_data": {
                "year": int(birth_data.get("year", 1990)),
                "month": int(birth_data.get("month", 1)),
                "day": int(birth_data.get("day", 1)),
                "hour": int(birth_data.get("hour", 12)),
                "minute": int(birth_data.get("min", birth_data.get("minute", 0))),
                "city": city,
                "country_code": _map_country_code(place),
            },
        }
    except Exception as e:
        logger.warning(f"Could not build subject: {e}")
        return None


async def plume_chat(
    message: str,
    session_id: str,
    birth_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Point d'entrée principal — appel astrology-api.io v3 hosted-mode."""
    api_key = os.environ.get("ASTROLOGY_API_IO_KEY", "").strip()
    if not api_key:
        return {"success": False, "message": "Clé astrology-api.io non configurée."}

    # Recharger l'historique multi-tour depuis Supabase (si user connecté)
    history_msgs = []
    if user_id:
        try:
            from services.supabase_client import get_admin_client
            sb = get_admin_client()
            res = sb.table('plume_chat_messages').select('role,content').eq(
                'session_id', session_id).order('created_at').limit(30).execute()
            for h in (res.data or []):
                role = h.get("role")
                content = h.get("content", "")
                if role in ("user", "assistant") and content and not is_tool_leak(content):
                    history_msgs.append({"role": role, "content": content})
        except Exception as e:
            logger.warning(f"Could not load history: {e}")

    # Construire le payload
    messages = [{"role": "system", "content": SYSTEM_PROMPT_SOLENA}]
    messages.extend(history_msgs)
    messages.append({"role": "user", "content": message})

    astrology_block: Dict[str, Any] = {
        "defaults": {"language": "fr", "tradition": "psychological"},
        "enabled_tools": [
            "analysis_natal_report",
            "analysis_transits_report",
            "analysis_synastry_report",
        ],
    }
    subject = _build_subject(birth_data)
    if subject:
        astrology_block["subjects"] = [subject]

    payload = {
        "messages": messages,
        "astrology": astrology_block,
        "temperature": 0.85,
        "max_tokens": 1400,
    }

    # BYOK mode : passe la clé OpenAI utilisateur → 2 crédits/tour côté astrology-api.io
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        payload["model"] = BYOK_MODEL
        payload["byok"] = {
            "provider": "openai",
            "api_key": openai_key,
        }
        target_url = ASTROLOGY_API_IO_URL  # /byok endpoint
    else:
        target_url = ASTROLOGY_API_IO_URL_HOSTED  # hosted mode (25 crédits/tour)

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.post(
                target_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if r.status_code != 200:
                logger.error(f"astrology-api.io error {r.status_code}: {r.text[:500]}")
                # Fallback : si BYOK échoue (mauvaise clé, quota OpenAI), on retente en hosted
                if openai_key and target_url == ASTROLOGY_API_IO_URL:
                    logger.warning("BYOK failed, retrying in hosted mode")
                    payload.pop("byok", None)
                    payload.pop("model", None)
                    r = await client.post(
                        ASTROLOGY_API_IO_URL_HOSTED,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
                    if r.status_code != 200:
                        logger.error(f"hosted fallback also failed {r.status_code}: {r.text[:500]}")
                        return {"success": False, "message": "Les astres traversent une zone d'ombre. Réessaie dans un instant."}
                else:
                    return {"success": False, "message": "Les astres traversent une zone d'ombre. Réessaie dans un instant."}
            data = r.json()

        # Format OpenAI-compatible : choices[0].message.content
        choices = data.get("choices") or []
        if not choices:
            return {"success": False, "message": "Réponse vide des astres."}
        response_text = (choices[0].get("message") or {}).get("content", "").strip()
        if not response_text:
            return {"success": False, "message": "Solena a perdu le fil des étoiles. Réessaie."}

        # Garde-fou tool leak
        if is_tool_leak(response_text):
            logger.warning(f"[plume_chat] tool leak detected: {response_text[:100]}")
            response_text = (
                "Je perds un instant le fil des astres. Peux-tu me redire "
                "en une phrase ce qui t'a amené(e) à Plume aujourd'hui ?"
            )

        # Persister dans Supabase (user connecté seulement)
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

    except httpx.TimeoutException:
        logger.error("astrology-api.io timeout")
        return {"success": False, "message": "Les astres prennent du temps à répondre. Réessaie dans un instant."}
    except Exception as e:
        logger.error(f"Plume chat error: {e}", exc_info=True)
        return {"success": False, "message": "Une perturbation cosmique empêche la connexion."}


async def get_session_history(session_id: str, user_id: Optional[str] = None) -> list:
    """Récupère l'historique d'une session pour le frontend."""
    if not user_id:
        return []
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        res = sb.table('plume_chat_messages').select('role,content').eq(
            'session_id', session_id).eq('user_id', user_id).order('created_at').limit(100).execute()
        return [{"role": m["role"], "content": m["content"]} for m in (res.data or [])]
    except Exception as e:
        logger.warning(f"Could not load session history: {e}")
        return []
