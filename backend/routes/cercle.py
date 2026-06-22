"""
Routes /api/cercle/* — Dashboard rituel quotidien "Le Cercle"
Phase 2 du cahier des charges Plume Astrale.

Toutes les routes sont :
- protegees par Bearer Auth Supabase
- gatees Premium (gate dans la dependency `require_cercle_access`)
- persistees dans Supabase (tables cercle_daily_insights, cercle_checkins, cercle_reflections, cercle_streaks)
"""
import os
import logging
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from middleware.auth import get_current_user
from services.supabase_client import get_admin_client
from services.daily_ritual import (
    get_today_scores, MOODS, MOON_PHASES_FR, MOON_THEMES, _moon_phase_index,
)
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/cercle', tags=['cercle'])

# Bonus credits aux paliers de streak
STREAK_MILESTONES = {7: 3, 14: 5, 30: 10, 60: 15, 100: 25}
DAILY_CHECKIN_CREDIT = 1


# ═══════════════════════════════════════════════════════════
# Dependency : verifie acces au Cercle (Premium OU abonnement cercle_mensuel)
# ═══════════════════════════════════════════════════════════
async def require_cercle_access(current_user: dict = Depends(get_current_user)) -> dict:
    sb = get_admin_client()
    profile = sb.table('profiles').select('premium_status, premium_until, is_admin').eq(
        'id', current_user['id']
    ).maybe_single().execute()
    p = profile.data if profile and profile.data else {}
    is_admin = p.get('is_admin', False)
    is_active = p.get('premium_status') == 'active'

    # premium_until still valid?
    until = p.get('premium_until')
    if is_active and until:
        try:
            until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            is_active = until_dt > datetime.now(timezone.utc)
        except Exception:
            pass

    if not (is_active or is_admin):
        raise HTTPException(
            status_code=403,
            detail='Acces reserve aux membres du Cercle. Rejoignez Le Cercle pour 14,90€/mois.'
        )
    return current_user


# ═══════════════════════════════════════════════════════════
# Helpers Supabase persistence
# ═══════════════════════════════════════════════════════════
def _today_iso() -> str:
    return date.today().isoformat()


def _safe_select_one(query):
    """Wrap maybe_single() with table-missing graceful fallback."""
    try:
        r = query.execute()
        return r.data if r else None
    except Exception as e:
        logger.warning(f'[cercle] supabase select: {e}')
        return None


def _safe_upsert(table_name: str, payload: dict, on_conflict: str = ''):
    sb = get_admin_client()
    try:
        q = sb.table(table_name).upsert(payload, on_conflict=on_conflict) if on_conflict else sb.table(table_name).upsert(payload)
        q.execute()
        return True
    except Exception as e:
        logger.warning(f'[cercle] upsert {table_name}: {e}')
        return False


# ═══════════════════════════════════════════════════════════
# Conseil de la Plume — genere via GPT-4o-mini, cache 24h par user
# ═══════════════════════════════════════════════════════════
async def _generate_or_get_insight(user_id: str, profile: dict, mood: Optional[str]) -> str:
    sb = get_admin_client()
    today = _today_iso()

    # 1) Cache hit ?
    cached = _safe_select_one(
        sb.table('cercle_daily_insights').select('insight').eq('user_id', user_id).eq('day', today).maybe_single()
    )
    if cached and cached.get('insight'):
        return cached['insight']

    # 2) Genere via Plume IA
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return _fallback_insight()

    name = (profile.get('prenom') or 'Voyageur').strip() or 'Voyageur'
    birth_date = profile.get('birth_date')
    sun_sign = _sun_sign_from_date(birth_date)
    moon_phase = MOON_PHASES_FR[_moon_phase_index(date.today())]
    moon_theme = MOON_THEMES[moon_phase]
    mood_label = MOODS.get(mood or '', {}).get('label', '')

    prompt = f"""Genere un message du jour pour {name}{f' (Soleil en {sun_sign})' if sun_sign else ''}.
Date : {date.today().strftime('%d %B %Y')}.
Phase lunaire : {moon_phase} — {moon_theme}
{f'Humeur du matin : {mood_label}.' if mood_label else ''}

Contraintes strictes :
- 60 a 100 mots maximum, un seul paragraphe.
- Voix Plume : poetique, francaise, douce mais precise, jamais fataliste.
- Donne une invitation concrete pour la journee (1 action, 1 attention).
- Commence directement par l'insight (pas de salutation).
- Termine par une image evocatrice.
- Pas d'emoji. Pas de liste a puces. Pas de citation."""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f'cercle-{user_id}-{today}',
            system_message='Tu es Plume, oracle astrologique francais. Tu generes des messages du jour courts, poetiques, ancres dans le reel.',
        ).with_model('openai', 'gpt-4o-mini')

        response = await chat.send_message(UserMessage(text=prompt))
        insight = (response or '').strip() or _fallback_insight()

        # 3) Persist cache
        _safe_upsert('cercle_daily_insights', {
            'user_id': user_id,
            'day': today,
            'insight': insight,
            'mood_snapshot': mood,
        }, on_conflict='user_id,day')

        return insight

    except Exception as e:
        logger.error(f'[cercle] insight gen failed: {e}')
        return _fallback_insight()


def _fallback_insight() -> str:
    phase = MOON_PHASES_FR[_moon_phase_index(date.today())]
    return f"{MOON_THEMES[phase]} Aujourd'hui, ouvre une fenetre interieure et observe ce qui te traverse, sans le saisir."


def _sun_sign_from_date(birth_date: Optional[str]) -> str:
    if not birth_date:
        return ''
    try:
        d = datetime.fromisoformat(birth_date).date()
        m, day = d.month, d.day
        signs = [
            (1, 20, 'Capricorne'), (2, 19, 'Verseau'), (3, 20, 'Poissons'),
            (4, 20, 'Belier'), (5, 21, 'Taureau'), (6, 21, 'Gemeaux'),
            (7, 22, 'Cancer'), (8, 22, 'Lion'), (9, 23, 'Vierge'),
            (10, 23, 'Balance'), (11, 22, 'Scorpion'), (12, 21, 'Sagittaire'),
            (12, 31, 'Capricorne'),
        ]
        for sm, sd, sg in signs:
            if m < sm or (m == sm and day <= sd):
                return sg
    except Exception:
        pass
    return ''


# ═══════════════════════════════════════════════════════════
# STREAK helpers (Supabase persistent)
# ═══════════════════════════════════════════════════════════
def _next_milestone(current: int) -> dict:
    for m in sorted(STREAK_MILESTONES.keys()):
        if current < m:
            return {'days': m, 'bonus': STREAK_MILESTONES[m], 'remaining': m - current}
    return {'days': None, 'bonus': 0, 'remaining': 0}


def _get_streak_state(user_id: str) -> dict:
    sb = get_admin_client()
    row = _safe_select_one(
        sb.table('cercle_streaks').select('*').eq('user_id', user_id).maybe_single()
    ) or {}
    return {
        'current_streak': row.get('current_streak', 0) or 0,
        'longest_streak': row.get('longest_streak', 0) or 0,
        'total_checkins': row.get('total_checkins', 0) or 0,
        'last_checkin_day': row.get('last_checkin_day'),
        'grace_used_month': row.get('grace_used_month'),
    }


def _streak_status_payload(state: dict) -> dict:
    today = date.today()
    last = state.get('last_checkin_day')
    last_dt = None
    if last:
        try:
            last_dt = date.fromisoformat(last) if isinstance(last, str) else last
        except Exception:
            last_dt = None

    current = state['current_streak']
    if last_dt:
        gap = (today - last_dt).days
        if gap >= 2:
            current = 0  # expired
        elif gap == 1:
            # streak vivante mais pas check-in aujourd'hui
            pass
        # gap == 0 : deja fait aujourd'hui

    checked_in_today = (last_dt == today)
    return {
        'streak_count': current,
        'longest_streak': state['longest_streak'],
        'total_checkins': state['total_checkins'],
        'checked_in_today': checked_in_today,
        'next_milestone': _next_milestone(current),
    }


async def _do_checkin(user_id: str) -> dict:
    """Increment streak + grant daily credit + milestone bonus. Idempotent same-day."""
    from services.wallet_service import add_credits

    state = _get_streak_state(user_id)
    today = date.today()
    today_iso = today.isoformat()
    last = state.get('last_checkin_day')
    last_dt = None
    if last:
        try:
            last_dt = date.fromisoformat(last) if isinstance(last, str) else last
        except Exception:
            last_dt = None

    if last_dt == today:
        # Deja fait aujourd'hui — idempotent
        payload = _streak_status_payload(state)
        return {'already_checked_in': True, 'credits_earned': 0, 'milestone_bonus': 0, **payload}

    # Calcul du nouveau streak
    gap = (today - last_dt).days if last_dt else 999
    current_month = today.strftime('%Y-%m')

    if gap == 1:
        new_streak = state['current_streak'] + 1
    elif gap == 2 and state.get('grace_used_month') != current_month:
        # Jour de grace mensuel : on conserve le streak
        new_streak = state['current_streak'] + 1
        state['grace_used_month'] = current_month
    else:
        new_streak = 1

    new_longest = max(state['longest_streak'], new_streak)
    new_total = state['total_checkins'] + 1
    milestone_bonus = STREAK_MILESTONES.get(new_streak, 0)
    credits_earned = DAILY_CHECKIN_CREDIT + milestone_bonus

    # Persiste (et gate l'octroi de credits sur succes pour eviter l'abus quand la table manque)
    upsert_payload = {
        'user_id': user_id,
        'current_streak': new_streak,
        'longest_streak': new_longest,
        'total_checkins': new_total,
        'last_checkin_day': today_iso,
        'grace_used_month': state.get('grace_used_month'),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    streak_persisted = _safe_upsert('cercle_streaks', upsert_payload, on_conflict='user_id')

    # Credit le wallet UNIQUEMENT si l'idempotence est garantie (table presente)
    if streak_persisted:
        description = f"Check-in du Cercle (jour {new_streak})"
        if milestone_bonus > 0:
            description += f" — palier {new_streak}j +{milestone_bonus}cr"
        try:
            await add_credits(user_id, credits_earned, description, tx_type='reward')
        except Exception as e:
            logger.warning(f'[cercle] add_credits failed: {e}')
    else:
        credits_earned = 0
        milestone_bonus = 0
        logger.warning(f'[cercle] streak upsert failed for {user_id} — skipping credit grant (idempotency unsafe)')

    return {
        'already_checked_in': False,
        'credits_earned': credits_earned,
        'milestone_bonus': milestone_bonus,
        'streak_count': new_streak,
        'longest_streak': new_longest,
        'total_checkins': new_total,
        'checked_in_today': True,
        'next_milestone': _next_milestone(new_streak),
    }


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get('/streak')
async def cercle_streak(current_user: dict = Depends(get_current_user)):
    """Statut de streak (lecture seule). Accessible meme aux non-abonnes."""
    state = _get_streak_state(current_user['id'])
    return _streak_status_payload(state)


@router.post('/checkin')
async def cercle_checkin(request: Request, current_user: dict = Depends(require_cercle_access)):
    """Check-in matinal : humeur + intention + maj streak + credits."""
    body = await request.json()
    mood = (body.get('mood') or '').strip()
    intention = (body.get('intention') or '').strip()[:500] or None

    if not mood or mood not in MOODS:
        raise HTTPException(status_code=400, detail='Humeur invalide.')

    user_id = current_user['id']
    today_iso = _today_iso()

    # 1) Persister le check-in (humeur + intention)
    _safe_upsert('cercle_checkins', {
        'user_id': user_id,
        'day': today_iso,
        'mood': mood,
        'intention': intention,
    }, on_conflict='user_id,day')

    # 2) Update streak + credits
    streak_result = await _do_checkin(user_id)

    return {
        'success': True,
        'mood': mood,
        'intention': intention,
        **streak_result,
    }


class ReflectionRequest(BaseModel):
    entry: str = Field(..., min_length=5, max_length=4000)


@router.post('/reflection')
async def cercle_reflection(payload: ReflectionRequest, current_user: dict = Depends(require_cercle_access)):
    """Reflexion du soir : l'utilisateur ecrit, Plume repond."""
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=503, detail='Service IA momentanement indisponible.')

    sb = get_admin_client()
    user_id = current_user['id']
    today_iso = _today_iso()

    # Recupere mood du jour pour contextualiser
    checkin = _safe_select_one(
        sb.table('cercle_checkins').select('mood').eq('user_id', user_id).eq('day', today_iso).maybe_single()
    ) or {}
    mood = checkin.get('mood')

    # Recupere prenom + sign
    profile = _safe_select_one(
        sb.table('profiles').select('prenom, birth_date').eq('id', user_id).maybe_single()
    ) or {}
    name = profile.get('prenom') or 'Voyageur'
    sun_sign = _sun_sign_from_date(profile.get('birth_date'))
    moon_phase = MOON_PHASES_FR[_moon_phase_index(date.today())]

    system_msg = """Tu es Plume, oracle astrologique francais et compagnon emotionnel.
L'utilisateur t'ouvre son journal du soir. Tu lis ce qu'il/elle a ecrit avec attention,
puis tu reponds comme une amie sage et bienveillante.

Regles strictes :
- 100 a 180 mots maximum.
- Voix Plume : douce, poetique, presente, jamais directive.
- Refleter brievement ce qui semble se jouer (sans interpreter sauvagement).
- Apporter un eclairage astrologique LEGER (1 mention de planete ou de phase lunaire si pertinent).
- Inviter a une micro-action ou une introspection, jamais a un changement radical.
- Ne JAMAIS donner de diagnostic, de conseil medical, juridique, ou financier.
- Si l'ecrit revele une detresse profonde, reconnaitre la souffrance et orienter vers une ressource humaine (3114, ami, professionnel).
- Pas de salutation. Commence directement par accueillir ce qu'il/elle a partage.
- Termine par une image evocatrice ou une invitation tendre.
- Aucun emoji. Pas de liste a puces."""

    mood_label = MOODS.get(mood or '', {}).get('label', '')
    context = f'Phase lunaire : {moon_phase}.'
    if mood_label:
        context += f' Humeur du matin : {mood_label}.'
    if sun_sign:
        context += f' Soleil en {sun_sign}.'

    prompt = f"""{context}

{name} ecrit ce soir dans son journal :

\"\"\"
{payload.entry.strip()}
\"\"\"

Repond comme Plume."""

    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f'reflection-{user_id}-{datetime.now().timestamp()}',
            system_message=system_msg,
        ).with_model('openai', 'gpt-4o-mini')

        response_text = (await chat.send_message(UserMessage(text=prompt))).strip()

        # Persiste
        try:
            sb.table('cercle_reflections').insert({
                'user_id': user_id,
                'day': today_iso,
                'entry': payload.entry.strip(),
                'plume_response': response_text,
                'mood': mood,
            }).execute()
        except Exception as e:
            logger.warning(f'[cercle] reflection persist: {e}')

        return {'success': True, 'response': response_text}

    except Exception as e:
        logger.error(f'[cercle] reflection gen failed: {e}')
        raise HTTPException(status_code=503, detail='Plume est momentanement silencieuse. Reessayez dans un instant.')


@router.get('/reflections')
async def cercle_reflections_history(limit: int = 30, current_user: dict = Depends(require_cercle_access)):
    """Historique des reflexions du soir (lecture seule, max 30 derniers)."""
    sb = get_admin_client()
    user_id = current_user['id']
    try:
        res = sb.table('cercle_reflections').select(
            'id, day, entry, plume_response, mood, created_at'
        ).eq('user_id', user_id).order('created_at', desc=True).limit(min(limit, 100)).execute()
        return {'reflections': res.data or []}
    except Exception as e:
        logger.warning(f'[cercle] reflections history: {e}')
        return {'reflections': []}


@router.get('/daily')
async def cercle_daily(current_user: dict = Depends(require_cercle_access)):
    """Payload complet du dashboard quotidien Le Cercle."""
    sb = get_admin_client()
    user_id = current_user['id']
    today = date.today()
    today_iso = today.isoformat()

    # 1) Profile (prenom + birth)
    profile = _safe_select_one(
        sb.table('profiles').select('prenom, birth_date, birth_time, birth_place').eq(
            'id', user_id
        ).maybe_single()
    ) or {}

    # 2) Check-in d'aujourd'hui
    checkin = _safe_select_one(
        sb.table('cercle_checkins').select('mood, intention').eq(
            'user_id', user_id
        ).eq('day', today_iso).maybe_single()
    )
    mood = (checkin or {}).get('mood')

    # 3) Scores (4 jauges)
    scores_data = get_today_scores(user_id, mood=mood)

    # 4) Insight cache 24h (genere si manque)
    insight = await _generate_or_get_insight(user_id, profile, mood)

    # 5) Streak status
    streak_payload = _streak_status_payload(_get_streak_state(user_id))

    # 6) Tarot du jour (deterministe par user + date)
    tarot = _daily_tarot(user_id, today_iso)

    # 7) Liste des humeurs (pour UI)
    moods_list = [{'id': k, **v} for k, v in MOODS.items()]

    # 8) A-t-il deja fait sa reflexion du soir aujourd'hui ?
    reflection_today = _safe_select_one(
        sb.table('cercle_reflections').select('id, entry, plume_response, created_at').eq(
            'user_id', user_id
        ).eq('day', today_iso).order('created_at', desc=True).limit(1).maybe_single()
    )

    return {
        'date': today_iso,
        'profile': {
            'prenom': profile.get('prenom') or 'Voyageur',
            'sun_sign': _sun_sign_from_date(profile.get('birth_date')),
        },
        'moon': {
            'phase': scores_data['moon_phase'],
            'theme': scores_data['moon_theme'],
            'index': scores_data['moon_phase_index'],
        },
        'scores': scores_data['scores'],
        'insight': insight,
        'checkin': checkin,
        'moods': moods_list,
        'streak': streak_payload,
        'tarot': tarot,
        'reflection_today': reflection_today,
    }


# ═══════════════════════════════════════════════════════════
# Tarot du jour — deterministe per user+date (carte symbolique)
# ═══════════════════════════════════════════════════════════
_TAROT_MAJORS = [
    ('Le Bateleur', 'Initiative, debut, potentiel a activer.'),
    ('La Papesse', 'Intuition, savoir interieur, silence fertile.'),
    ("L'Imperatrice", "Creativite, abondance, douceur maternelle."),
    ("L'Empereur", 'Structure, decision, autorite saine.'),
    ('Le Pape', 'Transmission, alignement, repere spirituel.'),
    ("L'Amoureux", 'Choix du coeur, alliance, harmonisation.'),
    ('Le Chariot', "Volonte, mouvement, prise d'elan."),
    ('La Justice', 'Equilibre, verite, responsabilite.'),
    ("L'Hermite", 'Retrait, sagesse, eclairage interieur.'),
    ('La Roue de Fortune', 'Cycle, retournement, opportunite.'),
    ('La Force', 'Maitrise douce, courage tranquille.'),
    ('Le Pendu', 'Lacher-prise, perspective renversee.'),
    ("L'Arcane sans nom", 'Transformation, fin necessaire, mue.'),
    ('La Temperance', 'Alchimie, mesure, fluidite.'),
    ('Le Diable', 'Attachement, ombre, faces cachees.'),
    ('La Maison Dieu', 'Liberation soudaine, verite revelee.'),
    ("L'Etoile", 'Esperance, regeneration, eau qui guerit.'),
    ('La Lune', 'Reve, peur, navigation a l\'instinct.'),
    ('Le Soleil', 'Joie, clarte, retour de l\'enfant interieur.'),
    ('Le Jugement', 'Appel, eveil, retour a la lumiere.'),
    ('Le Monde', 'Accomplissement, plenitude, integration.'),
    ('Le Fou', 'Liberte, pas de cote, confiance dans le chemin.'),
]


def _daily_tarot(user_id: str, day_iso: str) -> dict:
    import hashlib
    h = hashlib.sha256(f'{user_id}-{day_iso}-tarot'.encode()).hexdigest()
    idx = int(h[:8], 16) % len(_TAROT_MAJORS)
    name, message = _TAROT_MAJORS[idx]
    return {'name': name, 'message': message, 'index': idx}
