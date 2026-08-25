"""
Rituel quotidien — services pour le sprint 2 "Compagnon emotionnel".

Inclut :
- scores cosmiques quotidiens (Energie / Confiance / Discipline / Intuition)
- check-in matinal (humeur + intention)
- message du jour personnalise par Plume IA (cache 24h)
- streak (jours consecutifs de visite)
- journal IA (entree texte + reponse Plume)

Persistance : Supabase (service_role). LLM : OpenAI natif via integrations.llm.chat.
"""
import os
import hashlib
import logging
from datetime import datetime, date, timezone
from typing import Optional, Dict, Any, List
from integrations.llm.chat import LlmChat, UserMessage
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# HUMEURS — chaque humeur module legerement les scores
# ═══════════════════════════════════════════════════════════
MOODS = {
    "radieux":    {"label": "Radieux",    "icon": "Sun",       "color": "#F4D98C", "energy": 12, "confidence": 8,  "intuition": 5},
    "paisible":   {"label": "Paisible",   "icon": "Cloud",     "color": "#C4B5FD", "energy": 3,  "confidence": 4,  "intuition": 8},
    "pensif":     {"label": "Pensif",     "icon": "Moon",      "color": "#9089B5", "energy": -3, "confidence": -2, "intuition": 10},
    "inquiet":    {"label": "Inquiet",    "icon": "Wind",      "color": "#A78BFA", "energy": -8, "confidence": -12,"intuition": 6},
    "determine":  {"label": "Determine",  "icon": "Flame",     "color": "#FF9F66", "energy": 10, "confidence": 12, "intuition": 0},
    "amour":      {"label": "Amour",      "icon": "Heart",     "color": "#F47F92", "energy": 7,  "confidence": 6,  "intuition": 4},
    "triste":     {"label": "Triste",     "icon": "CloudRain", "color": "#7C9BC4", "energy": -10,"confidence": -8, "intuition": 7},
}

MOON_PHASES_FR = [
    "Nouvelle Lune", "Premier Croissant", "Premier Quartier", "Gibbeuse Croissante",
    "Pleine Lune", "Gibbeuse Decroissante", "Dernier Quartier", "Dernier Croissant",
]

# Sens emotionnel de chaque phase pour les conseils
MOON_THEMES = {
    "Nouvelle Lune":          "Temps des graines. Pose une intention claire.",
    "Premier Croissant":      "L'elan grandit. Ose le premier pas.",
    "Premier Quartier":       "Ajustements. Decide sans hesiter.",
    "Gibbeuse Croissante":    "Affinage. Ecoute ce qui doit etre raffine.",
    "Pleine Lune":            "Apogee. Tes verites montent a la surface.",
    "Gibbeuse Decroissante":  "Partage. Transmets ce que tu as appris.",
    "Dernier Quartier":       "Tri. Libere ce qui t'encombre.",
    "Dernier Croissant":      "Repos. Accueille la pause, prepare la suite.",
}

# Themes des 4 scores (pour l'UI)
SCORE_THEMES = {
    "energy":     {"label": "Energie",     "desc": "Ta vitalite et ton elan du jour"},
    "confidence": {"label": "Confiance",   "desc": "Ton ancrage et ta certitude interieure"},
    "discipline": {"label": "Discipline",  "desc": "Ta capacite a tenir tes engagements"},
    "intuition":  {"label": "Intuition",   "desc": "Ta lecture subtile du monde"},
}


# ═══════════════════════════════════════════════════════════
# SCORES — deterministes par user + jour + axe
# ═══════════════════════════════════════════════════════════
def _seeded_score(user_id: str, day: str, axis: str, base: int = 65) -> int:
    """Score deterministe entre 35 et 92, varie chaque jour par utilisateur."""
    h = hashlib.sha256(f"{user_id}-{day}-{axis}".encode()).hexdigest()
    val = int(h[:8], 16) % 58       # 0-57
    score = base - 30 + val          # 35-92
    return max(35, min(92, score))


def _moon_phase_index(d: date) -> int:
    """Index 0-7 de la phase lunaire pour une date."""
    # Approximation : cycle de 29.5306 jours, ref Nouvelle Lune le 6 Jan 2000
    ref = date(2000, 1, 6)
    diff = (d - ref).days
    phase_position = (diff % 29.5306) / 29.5306
    return min(7, int(phase_position * 8))


def get_today_scores(user_id: str, mood: Optional[str] = None) -> Dict[str, Any]:
    """Renvoie les 4 scores cosmiques du jour, modules par l'humeur si fournie."""
    today = date.today()
    iso = today.isoformat()

    scores = {
        "energy":     _seeded_score(user_id, iso, "energy"),
        "confidence": _seeded_score(user_id, iso, "confidence"),
        "discipline": _seeded_score(user_id, iso, "discipline"),
        "intuition":  _seeded_score(user_id, iso, "intuition"),
    }

    # Modulation par l'humeur (max ±15)
    if mood and mood in MOODS:
        m = MOODS[mood]
        scores["energy"]     = max(20, min(98, scores["energy"]     + m.get("energy", 0)))
        scores["confidence"] = max(20, min(98, scores["confidence"] + m.get("confidence", 0)))
        scores["intuition"]  = max(20, min(98, scores["intuition"]  + m.get("intuition", 0)))

    return {
        "date": iso,
        "scores": scores,
        "moon_phase_index": _moon_phase_index(today),
        "moon_phase": MOON_PHASES_FR[_moon_phase_index(today)],
        "moon_theme": MOON_THEMES[MOON_PHASES_FR[_moon_phase_index(today)]],
    }


# ═══════════════════════════════════════════════════════════
# MESSAGE DU JOUR — genere 1x/jour par utilisateur, cache Supabase
# ═══════════════════════════════════════════════════════════
async def get_daily_insight(
    user_id: str,
    birth_data: Optional[Dict] = None,
    mood: Optional[str] = None,
) -> Dict[str, Any]:
    """Recupere ou genere le message du jour personnalise (Conseil de la Plume)."""
    today = date.today().isoformat()

    # Recuperer du cache Supabase
    try:
        sb = get_admin_client()
        cached = sb.table('daily_insights').select('insight').eq('user_id', user_id).eq('date', today).maybe_single().execute()
        if cached and cached.data and cached.data.get('insight'):
            return {"insight": cached.data['insight'], "cached": True}
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")

    # Generer via Plume IA (OpenAI natif)
    api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"insight": "Les astres te chuchotent : sois present a ce qui est, ce jour t'appartient.", "cached": False}

    moon_phase_idx = _moon_phase_index(date.today())
    moon_phase = MOON_PHASES_FR[moon_phase_idx]
    moon_theme = MOON_THEMES[moon_phase]
    mood_label = MOODS.get(mood or "", {}).get("label", "")

    name = (birth_data or {}).get("name", "Voyageur")
    sun_sign_hint = ""
    if birth_data and birth_data.get("month") and birth_data.get("day"):
        m, d = birth_data["month"], birth_data["day"]
        signs = [
            (1, 20, "Capricorne"), (2, 19, "Verseau"), (3, 20, "Poissons"),
            (4, 20, "Belier"), (5, 21, "Taureau"), (6, 21, "Gemeaux"),
            (7, 22, "Cancer"), (8, 22, "Lion"), (9, 23, "Vierge"),
            (10, 23, "Balance"), (11, 22, "Scorpion"), (12, 21, "Sagittaire"),
            (12, 31, "Capricorne"),
        ]
        for sm, sd, sg in signs:
            if m < sm or (m == sm and d <= sd):
                sun_sign_hint = sg
                break

    prompt = f"""Génère un rituel du jour personnalisé pour {name} (Soleil en {sun_sign_hint}, humeur du matin : {mood_label or 'inconnue'}).
Date : {date.today().strftime('%d %B %Y')}.
Phase lunaire actuelle : {moon_phase} — {moon_theme}

Contraintes :
- **250 à 350 mots** (une lecture complète, pas courte).
- Voix Soléna : poétique, française, sensuelle, ancrée dans le réel — jamais fataliste, jamais new age.
- Structure implicite : (1) ce que ta journée révèle, (2) une invitation concrète (1 action, 1 attention), (3) une image évocatrice, (4) une question finale engageante.
- Tutoiement systématique.
- Pas de salutation type "Bonjour {name}" — commence directement par l'insight.
- Pas d'emoji, pas de liste à puces, pas de markdown.
- **TERMINE OBLIGATOIREMENT PAR UNE QUESTION** qui invite à l'introspection (ex : « Qu'est-ce qui, aujourd'hui, mérite ta pleine attention ? »)."""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"daily-{user_id}-{today}",
            system_message="Tu es Soléna, la voix de Plume Astrale. Tu écris uniquement en FRANÇAIS impeccable avec tous les accents. Ton ton est poétique, sensuel, ancré. Tu tutoies systématiquement.",
        ).with_model("openai", "gpt-5.4")

        response = await chat.send_message(UserMessage(text=prompt))
        insight = response.strip()

        # Cacher dans Supabase
        try:
            sb = get_admin_client()
            sb.table('daily_insights').upsert({
                "user_id": user_id,
                "date": today,
                "insight": insight,
            }, on_conflict="user_id,date").execute()
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

        return {"insight": insight, "cached": False}

    except Exception as e:
        logger.error(f"Daily insight generation failed: {e}")
        return {"insight": f"{moon_theme} Aujourd'hui, ouvre une fenetre interieure et observe ce qui te traverse, sans le saisir.", "cached": False}


# ═══════════════════════════════════════════════════════════
# CHECK-IN MATINAL — humeur + intention
# ═══════════════════════════════════════════════════════════
async def submit_checkin(
    user_id: str,
    mood: str,
    intention: Optional[str] = None,
) -> Dict[str, Any]:
    today = date.today().isoformat()
    try:
        sb = get_admin_client()
        sb.table('daily_checkins').upsert({
            "user_id": user_id,
            "date": today,
            "mood": mood,
            "intention": intention or "",
        }, on_conflict="user_id,date").execute()
    except Exception as e:
        logger.warning(f"Checkin persist failed: {e}")

    return {"success": True, "checkin": {"mood": mood, "intention": intention, "date": today}}


async def get_today_checkin(user_id: str) -> Optional[Dict]:
    try:
        today = date.today().isoformat()
        sb = get_admin_client()
        res = sb.table('daily_checkins').select('mood,intention,date').eq('user_id', user_id).eq('date', today).maybe_single().execute()
        if res and res.data:
            return {"mood": res.data.get("mood"), "intention": res.data.get("intention", ""), "date": res.data.get("date")}
    except Exception as e:
        logger.warning(f"Get checkin failed: {e}")
    return None


# ═══════════════════════════════════════════════════════════
# STREAK — jours consecutifs de visite
# ═══════════════════════════════════════════════════════════
async def update_streak(user_id: str) -> Dict[str, int]:
    """Met a jour la streak en fonction du dernier jour actif."""
    try:
        sb = get_admin_client()
        today = date.today()
        res = sb.table('user_streaks').select('current,longest,last_date').eq('user_id', user_id).maybe_single().execute()
        existing = res.data if res else None

        if not existing:
            sb.table('user_streaks').insert({
                "user_id": user_id,
                "current": 1,
                "longest": 1,
                "last_date": today.isoformat(),
            }).execute()
            return {"current": 1, "longest": 1}

        last_date = date.fromisoformat(existing.get("last_date", today.isoformat()))
        gap = (today - last_date).days
        current = existing.get("current", 1)
        longest = existing.get("longest", 1)

        if gap == 0:
            # Deja compte aujourd'hui
            return {"current": current, "longest": longest}
        elif gap == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

        sb.table('user_streaks').update({
            "current": current,
            "longest": longest,
            "last_date": today.isoformat(),
        }).eq('user_id', user_id).execute()
        return {"current": current, "longest": longest}

    except Exception as e:
        logger.warning(f"Streak update failed: {e}")
        return {"current": 1, "longest": 1}


async def get_streak(user_id: str) -> Dict[str, int]:
    try:
        sb = get_admin_client()
        res = sb.table('user_streaks').select('current,longest,last_date').eq('user_id', user_id).maybe_single().execute()
        s = res.data if res else None
        if s:
            # Reset si gap > 1
            today = date.today()
            last_date = date.fromisoformat(s.get("last_date", today.isoformat()))
            gap = (today - last_date).days
            current = s.get("current", 0) if gap <= 1 else 0
            return {"current": current, "longest": s.get("longest", current)}
    except Exception as e:
        logger.warning(f"Get streak failed: {e}")
    return {"current": 0, "longest": 0}


# ═══════════════════════════════════════════════════════════
# JOURNAL IA — l'utilisateur ecrit, Plume repond
# ═══════════════════════════════════════════════════════════
JOURNAL_SYSTEM_PROMPT = """Tu es Plume, oracle astrologique francais et compagnon emotionnel.
L'utilisateur t'ouvre son journal intime du jour. Tu lis ce qu'il/elle a ecrit avec attention,
puis tu reponds comme une amie sage et bienveillante.

Regles strictes :
- 120 a 220 mots maximum.
- Voix Plume : douce, poetique, presente, jamais directive.
- Refleter brievement ce qui semble se jouer (sans interpreter sauvagement).
- Apporter un eclairage astrologique LEGER (1 mention de planete ou de phase lunaire actuelle si pertinent).
- Inviter a une micro-action ou une introspection, jamais a un changement radical.
- Ne JAMAIS donner de diagnostic, de conseil medical, juridique, ou financier.
- Si l'ecrit revele une detresse profonde, reconnaitre la souffrance et orienter vers une ressource humaine (3114, ami, professionnel)."""


async def journal_entry(
    user_id: str,
    entry_text: str,
    mood: Optional[str] = None,
    birth_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    api_key = os.environ.get("EMERGENT_LLM_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"success": False, "message": "Service IA indisponible."}

    moon_phase = MOON_PHASES_FR[_moon_phase_index(date.today())]
    mood_label = MOODS.get(mood or "", {}).get("label", "")

    context = f"Phase lunaire du jour : {moon_phase}."
    if mood_label:
        context += f" Humeur du matin de l'utilisateur : {mood_label}."
    if birth_data and birth_data.get("month") and birth_data.get("day"):
        m, d = birth_data["month"], birth_data["day"]
        signs = [
            (1, 20, "Capricorne"), (2, 19, "Verseau"), (3, 20, "Poissons"),
            (4, 20, "Belier"), (5, 21, "Taureau"), (6, 21, "Gemeaux"),
            (7, 22, "Cancer"), (8, 22, "Lion"), (9, 23, "Vierge"),
            (10, 23, "Balance"), (11, 22, "Scorpion"), (12, 21, "Sagittaire"),
            (12, 31, "Capricorne"),
        ]
        for sm, sd, sg in signs:
            if m < sm or (m == sm and d <= sd):
                context += f" Soleil en {sg}."
                break

    prompt = f"""{context}

Voici ce que l'utilisateur a ecrit dans son journal aujourd'hui :

\"\"\"
{entry_text}
\"\"\"

Repond comme Plume."""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f"journal-{user_id}-{datetime.now().timestamp()}",
            system_message=JOURNAL_SYSTEM_PROMPT,
        ).with_model("openai", "gpt-4o-mini")

        response_text = await chat.send_message(UserMessage(text=prompt))

        # Persister dans Supabase
        try:
            sb = get_admin_client()
            sb.table('journal_entries').insert({
                "user_id": user_id,
                "date": date.today().isoformat(),
                "entry": entry_text,
                "response": response_text,
                "mood": mood,
            }).execute()
        except Exception as e:
            logger.warning(f"Journal persist failed: {e}")

        return {"success": True, "response": response_text}

    except Exception as e:
        logger.error(f"Journal entry failed: {e}")
        return {"success": False, "message": "Plume est momentanement silencieuse. Reessaie."}


async def get_journal_history(user_id: str, limit: int = 30) -> List[Dict]:
    try:
        sb = get_admin_client()
        res = sb.table('journal_entries').select('date,entry,response,mood,ts').eq('user_id', user_id).order('ts', desc=True).limit(limit).execute()
        items = []
        for e in (res.data or []):
            items.append({
                "date": e.get("date"),
                "entry": e.get("entry"),
                "response": e.get("response"),
                "mood": e.get("mood"),
                "ts": e.get("ts"),
            })
        return items
    except Exception as e:
        logger.warning(f"Journal history failed: {e}")
        return []
