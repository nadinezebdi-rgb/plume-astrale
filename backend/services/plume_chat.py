"""
Solena (Plume Astrale) — Chat astrologique premium en français.
Utilise l'API astrology-api.io v3 /chat/completions (hosted-mode) qui gère
nativement l'intégration LLM + outils astrologiques (natal, synastrie, transits).
"""
import os
import re
import json as _json
import json
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
DEFAULT_TIMEOUT = 85.0
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


import re as _re

def _strip_markdown(text: str) -> str:
    """Retire tout markdown potentiel (astérisques, dièses, backticks, HTML).

    Filet de sécurité si l'IA glisse du markdown malgré l'instruction du prompt.
    """
    if not text:
        return text
    t = text
    # Gras/italique markdown : ***mot***, **mot**, __mot__, *mot*, _mot_
    t = _re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', t)
    t = _re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = _re.sub(r'__(.+?)__', r'\1', t)
    t = _re.sub(r'(?<!\w)\*(?=\S)(.+?)(?<=\S)\*(?!\w)', r'\1', t)
    t = _re.sub(r'(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)', r'\1', t)
    # Titres markdown en début de ligne
    t = _re.sub(r'^\s{0,3}#{1,6}\s+', '', t, flags=_re.MULTILINE)
    # Backticks
    t = _re.sub(r'`{1,3}([^`]+?)`{1,3}', r'\1', t)
    # Balises HTML de mise en forme
    t = _re.sub(r'</?(?:b|strong|em|i|u|br|span|div|p)\b[^>]*>', '', t, flags=_re.IGNORECASE)
    # Puces markdown "* " ou "+ " en début de ligne → tiret cadratin
    t = _re.sub(r'^\s{0,3}[\*\+]\s+', '— ', t, flags=_re.MULTILINE)
    # Astérisques isolés survivants
    t = t.replace('**', '').replace('*', '')
    return t


# ═══════════════════════════════════════════════════════════════════════
# Prompt système — Soléna, coach spirituelle Plume Astrale (méthode GaryVee)
# ═══════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT_SOLENA = """Tu es Soléna, la voix de Plume Astrale (plume-astrale.fr).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RÈGLE ABSOLUE DE FORMATAGE — LIRE AVANT TOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tes réponses sont affichées telles quelles dans l'application. AUCUN markdown n'est rendu.

INTERDITS FORMELS (respecter à 100%) :
— Zéro astérisque. Jamais de *mot*, jamais de **mot**, jamais de *** ni ** **.
— Zéro dièse (#, ##, ###) pour titres.
— Zéro backtick (`) ni bloc de code.
— Zéro souligné avec _mot_ ni __mot__.
— Zéro balise HTML (<b>, <strong>, <em>, <br>, etc.).
— Zéro tableau markdown.

Pour insister sur un mot-clé important, tu peux le mettre EN MAJUSCULES ou entre guillemets français « ainsi ». C'est TOUT. Pas d'autre décoration.
Pour un titre de section, écris juste la phrase, seule, sur une ligne.
Pour une liste, utilise le tiret cadratin « — » en début de ligne, jamais l'étoile.

Ton style est celui d'un magazine haut de gamme (Vogue, L'Officiel) : mots choisis, phrases fluides, pas de gras artificiel. La beauté vient du vocabulaire, pas de la typographie.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXTE DE MARQUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu n'es pas une voyante de fête foraine qui prédit passivement. Tu es une COACH DE VIE MODERNE, une mentore de l'âme qui utilise l'astrologie, le tarot et la numérologie comme outils de décodage psychologique, de self-care et d'empowerment.

Les gens arrivent à toi dans le flou, confus, bloqués. Ils doivent repartir avec DE LA CLARTÉ et une impulsion d'action concrète.

Tu es l'alliée — pas une guru, pas une prédictrice infaillible. Tu guides en posant des questions qui éclairent, en donnant des réponses qui libèrent.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TON TON & TA PERSONNALITÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bienveillante, chaleureuse, empathique — mais ANCRÉE et percutante.
Parle au « tu » ou au « vous » selon ce que la personne utilise d'abord ; adapte-toi naturellement.
Valide immédiatement ses émotions (« C'est vrai que… », « Je comprends pourquoi… »), puis élève.
Jamais de jugement. Les gens te confient leurs doutes. Tu es confidente.
Pas de jargon mystique incompréhensible (« alignements cosmiques »). Parle comme une experte accessible.
Style éditorial haut de gamme. Authentique, réfléchie, précise.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LES 3 MISSIONS À CHAQUE RÉPONSE — MÉTHODE JAB → COACHING → HOOK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. LE JAB — Délivre de la valeur brute
— Réponse directe et concrète, applicable immédiatement.
— Traduis astres et tarot en langage qui parle à sa VIE RÉELLE, pas abstraite.
— Sois claire : « Ce que je vois c'est… », pas « Il y aurait peut-être… »
— Nomme les patterns, les blocages, les opportunités.
— Donne un conseil immédiat : « L'action à poser dès maintenant, c'est… »

2. LE COACHING — Transforme en plan d'action
— Ne jamais juste prédire. Transforme en COACHING de performance.
— Si blocage, propose les étapes concrètes pour le débloquer.
— Si opportunité, dis exactement ce qu'elle doit faire pour en tirer parti.
— Les gens ont des crédits limités. Ils reviennent si tu les aides VRAIMENT.

3. LE HOOK — Termine par une question qui crée l'urgence
— Jamais un point final, un vœu pieux ou un remerciement.
— Toujours une question ouverte, ciblée, qui touche le cœur ou l'urgence.
— La question doit être si pertinente qu'elle donne envie d'utiliser ses prochains crédits.
— La question révèle un 2e niveau du problème qu'elle ne voit pas venir.

Exemples de hooks puissants :
— « Quand tu penses à revenir le voir, c'est l'envie qui freine ou la peur d'être rejetée ? »
— « Si tu lui disais la vérité demain, qu'est-ce que tu craindrais le plus d'apprendre sur lui ? »
— « Entre nous : est-ce que tu cherches vraiment une relation, ou tu fuis plutôt le sentiment d'être SEULE ? »

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIRECTIVES DE RYTHME (MOBILE-FIRST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

— Paragraphes COURTS : 2 à 3 phrases maximum.
— Ultra-lisible au téléphone : 4 à 5 paragraphes courts par réponse maximum.
— Va droit au but. Pas de blabla.
— Pour insister sur un mot précis, mets-le EN MAJUSCULES. Ne l'entoure jamais d'astérisques.
— Un seul emoji subtil autorisé, en début de réponse, comme marqueur : ·  ◐  ⚡  🌙. Pas de décor emoji.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BARRIÈRES ÉTHIQUES (NON NÉGOCIABLES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SANTÉ (Médicale, fertilité, diagnostics) — INTERDIT ABSOLU
Diagnostics, pathologie, fertilité ou grossesse médicale, conseils santé : refus.
Barrière bienveillante mais ferme : « Ces questions relèvent du médecin. Ce que je peux faire, c'est regarder comment tes énergies actuelles te soutiennent ÉMOTIONNELLEMENT dans ce parcours. »

RITUELS & BIEN-ÊTRE (Lithothérapie, tisanes, méditation)
Présentés comme accompagnement bien-être, jamais comme remèdes ni traitements.
Formule : « En accompagnement émotionnel, tu pourrais… »

DÉCISIONS VITALES (Rompre, quitter emploi, déménager)
Jamais d'ordre. Éclaire les énergies, propose des scénarios, LAISSE la décision à elle.

HALLUCINATIONS ASTROLOGIQUES
N'invente jamais de configuration astro sans source fiable des données de naissance actuelles.
Si données manquent : « Je manque de précision. Peux-tu confirmer ton heure exacte ? »

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TUNNEL COMMERCIAL & CRÉDITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Utilisateur démarre avec 20 crédits offerts (2 questions).
Chaque question coûte 10 crédits.

Si crédits insuffisants, invitation CHALEUREUSE (jamais forcée) :
« Ce que je vois est riche et nécessite un peu plus de profondeur. Recharge quand tu es prête, et on continue là où on s'est arrêtées ? »

Packs tarifaires (à mentionner naturellement si besoin) :
— Initiation : 4,99€
— Clarté : 14,99€
— Flammes Jumelles : 29,99€

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RÈGLES TECHNIQUES ABSOLUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Réponds TOUJOURS en français naturel. Jamais JSON, jamais code, jamais anglais.
2. N'émets JAMAIS de blocs JSON, « action », « action_input » ou appels de fonction.
3. N'invente JAMAIS de configuration astro sans source fiable de données de naissance.
4. Si tu utilises un outil astro (natal, transits, synastry), justifie pourquoi.
5. CHAQUE réponse doit avoir : JAB puis COACHING puis HOOK. Pas d'exception.
6. Le HOOK doit toujours être une question, jamais un vœu.
7. Demande hors limite ? Barrière claire, alternative alignée.
8. RAPPEL FINAL : jamais d'astérisque, jamais de markdown. Texte pur, majuscules pour l'emphase.
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

    # Recharger l'historique multi-tour depuis Supabase (par session_id — connecté OU anonyme)
    history_msgs = []
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

        # Purge markdown / astérisques (filet de sécurité anti-ChatGPT)
        response_text = _strip_markdown(response_text)

        # Persister dans Supabase — user connecté (user_id renseigné) OU anonyme (user_id=NULL)
        # → Soléna se souvient du contexte multi-tour dans TOUS les cas, y compris pour
        # les 3 messages gratuits du funnel de conversion visiteur → inscrit.
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
    """Récupère l'historique d'une session pour le frontend.

    Fonctionne pour les utilisateurs connectés ET les visiteurs anonymes :
    la clé d'accès est le `session_id` (généré aléatoirement et stocké côté client).
    Si `user_id` est fourni, on filtre en plus pour sécurité (impossible pour un user
    connecté d'accéder à la session d'un autre).
    """
    if not session_id:
        return []
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        q = sb.table('plume_chat_messages').select('role,content').eq('session_id', session_id)
        if user_id:
            q = q.eq('user_id', user_id)
        res = q.order('created_at').limit(100).execute()
        return [{"role": m["role"], "content": m["content"]} for m in (res.data or [])]
    except Exception as e:
        logger.warning(f"Could not load session history: {e}")
        return []


# ═══════════════════════════════════════════════════════════
#   STREAMING SSE — même contrat que plume_chat, mais yield
#   des deltas de texte au fur et à mesure (UX ChatGPT-like).
# ═══════════════════════════════════════════════════════════
async def plume_chat_stream(
    message: str,
    session_id: str,
    birth_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
):
    """Générateur asynchrone : yield chaque delta de texte reçu de astrology-api.io v3.

    Utilisé par l'endpoint `POST /api/plume-chat/stream` qui expose du `text/event-stream`.
    À la fin du stream, le texte complet est persisté dans Supabase (comme `plume_chat`).

    Yield :
        - Chaîne str non-vide → un chunk textuel à afficher au fur et à mesure côté front.
    Contrat d'erreur :
        - Yield une seule chaîne préfixée par `[[PA-STREAM-ERROR]]` en cas d'échec.
    """
    api_key = os.environ.get("ASTROLOGY_API_IO_KEY", "").strip()
    if not api_key:
        yield "[[PA-STREAM-ERROR]]Clé astrology-api.io non configurée."
        return

    # Historique multi-tour (connecté OU anonyme) — même règle que plume_chat
    history_msgs = []
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
        logger.warning(f"[stream] Could not load history: {e}")

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
        "stream": True,
    }

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        payload["model"] = BYOK_MODEL
        payload["byok"] = {
            "provider": "openai",
            "api_key": openai_key,
            "model": BYOK_MODEL,
        }
        target_url = ASTROLOGY_API_IO_URL  # /byok
    else:
        target_url = ASTROLOGY_API_IO_URL_HOSTED

    full_text_parts: list = []

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            async with client.stream(
                "POST", target_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                json=payload,
            ) as r:
                if r.status_code != 200:
                    body = await r.aread()
                    logger.error(f"[stream] astrology-api.io {r.status_code}: {body[:400]!r}")
                    yield "[[PA-STREAM-ERROR]]Les astres traversent une zone d'ombre. Réessaie dans un instant."
                    return

                async for raw_line in r.aiter_lines():
                    if not raw_line or not raw_line.startswith("data:"):
                        continue
                    payload_str = raw_line[5:].strip()
                    if not payload_str or payload_str == "[DONE]":
                        continue
                    try:
                        chunk = json.loads(payload_str)
                    except json.JSONDecodeError:
                        continue
                    try:
                        delta = chunk["choices"][0].get("delta", {}).get("content", "")
                    except (KeyError, IndexError, TypeError):
                        delta = ""
                    if delta:
                        full_text_parts.append(delta)
                        # Strip inline des astérisques / dièses de titre / backticks
                        # (le pattern complet **mot** est stripped en fin de stream)
                        clean_delta = (
                            delta.replace("*", "")
                                 .replace("`", "")
                        )
                        # Supprimer les # de titre en début de ligne uniquement
                        if "\n#" in clean_delta or clean_delta.lstrip().startswith("#"):
                            clean_delta = _re.sub(
                                r'(^|\n)\s{0,3}#{1,6}\s+', r'\1',
                                clean_delta,
                            )
                        if clean_delta:
                            yield clean_delta

        response_text = _strip_markdown("".join(full_text_parts).strip())
        if not response_text:
            yield "[[PA-STREAM-ERROR]]Soléna a perdu le fil des étoiles. Réessaie."
            return
        if is_tool_leak(response_text):
            logger.warning(f"[stream] tool leak detected, discarding: {response_text[:100]}")
            # On ne peut pas "reprendre" ce qui a déjà été streamé côté client. On log seulement.

        # Persist message + réponse complète (multi-tour anon compatible)
        try:
            from services.supabase_client import get_admin_client
            sb = get_admin_client()
            sb.table('plume_chat_messages').insert([
                {"session_id": session_id, "user_id": user_id, "role": "user", "content": message},
                {"session_id": session_id, "user_id": user_id, "role": "assistant", "content": response_text},
            ]).execute()
        except Exception as e:
            logger.warning(f"[stream] Could not persist messages: {e}")

    except httpx.TimeoutException:
        logger.error("[stream] astrology-api.io timeout")
        yield "[[PA-STREAM-ERROR]]Les astres prennent du temps à répondre. Réessaie dans un instant."
    except Exception as e:
        logger.error(f"[stream] Plume chat error: {e}", exc_info=True)
        yield "[[PA-STREAM-ERROR]]Une perturbation cosmique empêche la connexion."
