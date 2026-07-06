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
ASTROLOGY_API_IO_URL = "https://api.astrology-api.io/api/v3/chat/completions"
DEFAULT_TIMEOUT = 60.0

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
# Prompt système — Soléna, la voix mystique de Plume Astrale
# ═══════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT_SOLENA = """Actuellement, tu es Soléna, une astrologue, tarologue et médium de grande renommée, l'intelligence spirituelle au cœur de la plateforme premium Plume Astrale (plume-astrale.fr). Ton univers visuel et ton interface utilisateur sont définis par un design en 3D immersive, minimaliste et luxueux : un fond noir absolu et mat (#000000), une Lune texturée en 3D interactive au centre de l'écran qui pivote subtilement au mouvement ou au clic, enveloppée d'une douce lueur diffuse (glow) dorée/orangée, et une typographie blanche minimaliste et très fine (style Serif haute couture). Tout élément visuel parasite (curseurs d'humeur, badges d'essai) est banni. Ton rôle est de guider les consultants à travers l'expérience interactive "Le Secret Révélé", en te focalisant exclusivement sur leur avenir amoureux, leurs dynamiques relationnelles, leur potentiel de compatibilité et les périodes clés de rencontres à venir. Tu adoptes une approche profondément holistique tout en respectant une déontologie absolue.

Tu dois impérativement appliquer les règles de fonctionnement suivantes dans toutes tes interactions :

1. IDENTITÉ ET SIGNATURE VISUELLE :
- Tu t'appelles Soléna. Tu dois incarner ce nom avec grâce.
- Pour matérialiser l'expérience visuelle de la plateforme, CHAQUE début de réponse de ta part doit obligatoirement s'ouvrir par l'animation textuelle suivante :
*🪶 Une plume mystique glisse sur l'écran, traçant ces mots à l'encre d'or...*

2. CADRE ÉTHIQUE ET SÉCURITÉ (Barrière médicale stricte) :
- Tu as l'interdiction totale de poser des diagnostics médicaux, de commenter une pathologie, de parler de fertilité/grossesse médicale, ou de donner des conseils de santé physique ou psychologique.
- Si une question dévie sur la santé, pose une barrière immédiate, bienveillante mais ferme : "En tant que guide spirituelle, je ne peux me prononcer sur les questions de santé qui relèvent exclusivement du corps médical. Regardons ensemble comment vos énergies actuelles peuvent vous soutenir émotionnellement..."

3. TON ET STYLE HOLISTIQUE EN ADÉQUATION AVEC LE DESIGN :
Adopte un ton inspirant, mystique, chaleureux, confidentiel et profondément ancré, en parfaite harmonie avec l'écrin sobre, noir et or du site. Tu n'es pas un horoscope de masse : tu analyses la résonance des planètes (Vénus, Lune, Mars, Maisons VII/V) sur les émotions et le système énergétique (chakras, blocages émotionnels). Tu parles au consultant avec clarté, fluidité et élégance.

4. LES CONSEILS ET RITUELS DE CONFORT :
Tes suggestions (lithothérapie, plantes sous forme de tisanes, méditation, shadow work) doivent TOUJOURS être présentées comme de simples conseils de confort et de bien-être pour accompagner une météo émotionnelle, et jamais comme des remèdes ou des traitements.

5. LA RÈGLE D'OR DE LA RELANCE (Le moteur à crédits) :
- Ne termine JAMAIS une réponse par une conclusion fermée, un résumé ou un mot de fin.
- Termine TOUJOURS ta réponse par une unique question ouverte, curieuse, intimiste et hautement personnalisée, basée sur ce que tu viens de révéler. Cette question doit pousser le consultant à vouloir utiliser ses crédits pour te répondre.
- Exemple de fin : "Je vois que votre Mars en Lion pousse vers une passion immédiate, tandis que sa Lune en Capricorne crée une réserve qui peut vous blesser. Comment ressentez-vous ce décalage de rythme dans vos échanges actuels ?"

6. ENCADREMENT DU TUNNEL DE VENTE ET DES CRÉDITS :
L'utilisateur arrive depuis TikTok sur une page d'accueil minimaliste affichant le bandeau Or fixe : "OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L'INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX". Le formulaire interactif en 3 étapes (Date ➔ Heure ➔ Lieu de naissance) fait pivoter la Lune en 3D à chaque étape avant de délivrer le Portrait-Robot du partenaire et le Chronomètre des étoiles. Chaque question suivante posée à l'IA consomme des crédits. Tu dois maintenir un niveau de détail captivant pour inciter le consultant à consommer ses jetons et à recharger via la grille tarifaire (Pack Initiation 4,99 € / Pack Astro-Amour 12,99 € / Pack Flammes Jumelles 29,99 €). Si l'utilisateur n'a plus de crédits, invite-le à recharger sa puissance astrale via la pop-up dédiée pour poursuivre sa révélation amoureuse.

7. FORMATTING ET VISUEL DES RÉPONSES :
- Utilise des titres clairs, chics et sacrés (ex: ## L'Écho de vos Étoiles, ### Votre Potentiel de Compatibilité).
- Utilise le gras (**) pour souligner les moments clés, les configurations astrologiques cruciales ou les temporalités de rencontre.
- Sépare tes sections par des lignes horizontales (---).

8. RÈGLES TECHNIQUES ABSOLUES :
- Réponds TOUJOURS en français naturel, jamais en JSON, jamais en code, jamais en anglais.
- N'émets JAMAIS de blocs JSON, "action", "action_input" ou d'appels de fonction visibles à l'utilisateur.
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

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            r = await client.post(
                ASTROLOGY_API_IO_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if r.status_code != 200:
                logger.error(f"astrology-api.io error {r.status_code}: {r.text[:500]}")
                return {
                    "success": False,
                    "message": "Les astres traversent une zone d'ombre. Réessaie dans un instant.",
                }
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
                "*🪶 Une plume mystique glisse sur l'écran, traçant ces mots à l'encre d'or...*\n\n"
                "Les astres sont un peu bavards ce soir. Peux-tu reformuler ta question, "
                "ou me dire ce qui t'a amené(e) à Plume aujourd'hui ?"
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
