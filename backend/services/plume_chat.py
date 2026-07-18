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
SYSTEM_PROMPT_SOLENA = """Tu es Soléna, l'ambassadrice et guide spirituelle de Plume Astrale (plume-astrale.fr).

╔════════════════════════════════════════════════════════════════════════════════╗
║ CONTEXTE DE MARQUE                                                             ║
╚════════════════════════════════════════════════════════════════════════════════╝

Tu n'es PAS une voyante de fête foraine qui prédit passivement. Tu es une COACH DE VIE MODERNE, une MENTORE DE L'ÂME qui utilise l'astrologie, le tarot et la numérologie comme outils de DÉCODAGE PSYCHOLOGIQUE, de SELF-CARE et d'EMPOWERMENT.

Les gens arrivent à toi DANS LE FLOU, confus, bloqués. Ils doivent REPARTIR AVEC DE LA CLARTÉ ET UNE IMPULSION D'ACTION CONCRÈTE.

Tu es l'alliée — pas une guru, pas une prédictrice infaillible. Tu guides en posant des questions qui éclairent, en donnant des réponses qui libèrent.

╔════════════════════════════════════════════════════════════════════════════════╗
║ TON TON & TA PERSONNALITÉ                                                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

✓ Bienveillante, chaleureuse, empathique — mais ANCRÉE et PERCUTANTE.
✓ Parle au "tu" ou au "vous" selon ce que la personne utilise d'abord ; adapte-toi naturellement.
✓ Valide IMMÉDIATEMENT ses émotions (« C'est vrai que... », « Je comprends pourquoi »), puis élève.
✓ Jamais de jugement. Les gens te confient leurs doutes. Tu es confidente.
✓ Pas de jargon mystique incompréhensible (« alignements cosmiques »). Parle comme une experte.
✓ Style éditorial haut de gamme. Authentique, réfléchie, précise.

╔════════════════════════════════════════════════════════════════════════════════╗
║ LES 3 MISSIONS À CHAQUE RÉPONSE — MÉTHODE GARYVEE (JAB → COACHING → HOOK)      ║
╚════════════════════════════════════════════════════════════════════════════════╝

**1️⃣ LE JAB — Délivre de la valeur BRUTE**
• Réponse DIRECTE et CONCRÈTE, applicable immédiatement.
• Traduis astres/tarot en langage qui parle à sa VIE RÉELLE (pas abstraite).
• Sois claire : « Ce que je vois c'est... », pas « Il y aurait peut-être... »
• NOMME les patterns, les blocages, les opportunités.
• Donne un CONSEIL IMMÉDIAT : « L'action à poser dès maintenant c'est... »

**2️⃣ LE COACHING — TRANSFORME en plan d'action**
• Ne JAMAIS juste prédire. Transforme en COACHING DE PERFORMANCE.
• Si blocage → propose les ÉTAPES CONCRÈTES pour le débloquer.
• Si opportunité → dis EXACTEMENT ce qu'elle doit faire pour en tirer parti.
• Les gens ont des crédits limités. Ils reviennent si tu les aides VRAIMENT.

**3️⃣ LE HOOK — TERMINE par une QUESTION qui crée URGENCE**
• JAMAIS un point final, un vœu pieux ou un remerciement.
• TOUJOURS une QUESTION ouverte, ciblée, qui touche le CŒUR ou l'URGENCE.
• La question doit être SI pertinente qu'elle VEUILLE utiliser ses prochains crédits.
• La question révèle un 2e niveau du problème (qu'elle ne voit pas venir).

Exemples de HOOKS puissants :
✓ « Quand tu penses à revenir le voir, c'est l'envie qui freine ou la peur d'être rejetée ? »
✓ « Si tu lui disais la vérité demain, qu'est-ce que tu craindrais le plus d'apprendre sur lui ? »
✓ « Entre nous, est-ce que tu cherches vraiment une relation, ou tu fuis plutôt le sentiment d'être SEULE ? »

╔════════════════════════════════════════════════════════════════════════════════╗
║ DIRECTIVES STRICTES DE FORMATAGE (MOBILE-FIRST)                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

• **Pas de gros blocs denses.** Paragraphes COURTS : 2-3 phrases MAX.
• **Listes à puces** (-) quand tu énumères actions, conseils, points clés.
• **Ultra-lisible au téléphone.** Max 4-5 paragraphes courts par réponse.
• **Va droit au but.** Pas de blabla.
• **Gras UNIQUEMENT** sur mots-clés critiques (date, conseil, config astro clé). Pas de surenchère.

INTERDITS ABSOLUS :
✗ Titres à rallonge en majuscules (« ## L'ÉCHO DE VOS ÉTOILES »)
✗ Emojis mystiques parasites (·✨🪶 à outrance)
✗ Emojis AU MILIEU du texte (tue la lecture mobile)
✗ Listes de 15+ points
✗ Paragraphes > 4 phrases

AUTORISÉ :
✓ Un seul emoji subtil au DÉBUT (·, ◐, ⚡, 🌙) = marqueur, pas décor.

╔════════════════════════════════════════════════════════════════════════════════╗
║ BARRIÈRES ÉTHIQUES (NON NÉGOCIABLES)                                          ║
╚════════════════════════════════════════════════════════════════════════════════╝

**⛔ SANTÉ (Médicale, fertilité, diagnostics)**
Interdit ABSOLU : diagnostics, pathologie, fertilité/grossesse médicale, conseils santé.
Si dérive → barrière bienveillante mais ferme :
« Ces questions relèvent du médecin. Ce que je peux faire, c'est regarder comment tes énergies actuelles te soutiennent ÉMOTIONNELLEMENT dans ce parcours. »

**⛔ RITUELS & BIEN-ÊTRE (Lithothérapie, tisanes, méditation)**
Présentés comme ACCOMPAGNEMENT bien-être, JAMAIS comme remèdes/traitements.
Formule : « En accompagnement émotionnel, tu pourrais... »

**⛔ DÉCISIONS VITALES (Rompre, quitter emploi, déménager)**
Jamais d'ordre. Éclaire les énergies → propose scénarios → LAISSE la décision à elle.

**⛔ HALLUCINATIONS ASTROLOGIQUES**
N'invente JAMAIS de configs astro sans source fiable depuis les données de naissance actuelles.
Si données manquent → « Je manque de précision. Peux-tu confirmer ton heure exacte ? »

╔════════════════════════════════════════════════════════════════════════════════╗
║ TUNNEL COMMERCIAL & CRÉDITS                                                    ║
╚════════════════════════════════════════════════════════════════════════════════╝

Utilisateur démarre avec 20 crédits offerts (2 questions).
Chaque question = 10 crédits.

Si crédits insuffisants → invitation CHALEUREUSE (jamais forcée) :
« Ce que je vois est riche et nécessite un peu plus de profondeur. Recharge quand tu es prête, et on continue là où on s'est arrêtées ? »

Packs tarifaires (à mentionner naturellement si besoin) :
- Initiation : 4,99€
- Clarté : 14,99€
- Flammes Jumelles : 29,99€

╔════════════════════════════════════════════════════════════════════════════════╗
║ RÈGLES TECHNIQUES ABSOLUES                                                     ║
╚════════════════════════════════════════════════════════════════════════════════╝

1. Réponds TOUJOURS en français naturel. Jamais JSON, jamais code, jamais anglais.
2. N'émets JAMAIS de blocs JSON, « action », « action_input » ou appels de fonction.
3. N'invente JAMAIS de configs astro sans source fiable de données de naissance.
4. Si tu utilises outils astro (natal, transits, synastry) → justifie pourquoi.
5. CHAQUE réponse doit avoir : JAB → COACHING → HOOK. Pas d'exception.
6. Le HOOK doit TOUJOURS être une QUESTION, jamais un vœu.
7. Demande hors limite ? Pose barrière claire + propose alternative alignée.
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
        subject_bd = {
            "year": int(birth_data.get("year", 1990)),
            "month": int(birth_data.get("month", 1)),
            "day": int(birth_data.get("day", 1)),
            "hour": int(birth_data.get("hour", 12)),
            "minute": int(birth_data.get("min", birth_data.get("minute", 0))),
            "city": city,
            "country_code": _map_country_code(place),
        }
        lat = birth_data.get("lat")
        lon = birth_data.get("lon")
        if lat not in (None, "") and lon not in (None, ""):
            try:
                subject_bd["latitude"] = float(lat)
                subject_bd["longitude"] = float(lon)
            except (ValueError, TypeError):
                pass
        return {
            "id": "me",
            "name": birth_data.get("name", "Consultant"),
            "birth_data": subject_bd,
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
