"""Plume Astrale — FastAPI backend (Supabase + Stripe + Astrology API)."""
from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import uuid
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

# Config + middleware
from config import get_settings
from middleware.auth import get_current_user, get_optional_user

# Services metier
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_en_croix
from services.tarot_premium import (
    tirage_marseille_question, tirage_croix_celtique, tirage_du_jour,
    DOMAINES_QUESTIONS,
)
from services.plume_chat import plume_chat as plume_chat_service, get_session_history
from services.daily_ritual import (
    get_today_scores, get_daily_insight, submit_checkin, get_today_checkin,
    update_streak, get_streak, journal_entry, get_journal_history, MOODS,
)
from services import wallet_service
from services.supabase_client import get_admin_client
from services.astrology_api import AstrologyAPIService
from services.energy_service import get_energy_today
from services import premium_subscription
from routes.admin import router as admin_router

# Stripe (via emergentintegrations — gere les sandbox keys aussi)
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
ASSETS_DIR = Path(__file__).parent / 'assets'

app = FastAPI(title='Plume Astrale API')
api_router = APIRouter(prefix='/api')
api_router.include_router(admin_router)


# ════════════════════════════════════════════
# AUTH (Supabase JWT — frontend signe via supabase-js, backend verifie)
# ════════════════════════════════════════════
class ProfileUpdate(BaseModel):
    prenom: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    birth_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gender: Optional[str] = None


@api_router.get('/auth/me')
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retourne profil + solde de credits de l'utilisateur authentifie."""
    user_id = current_user['id']
    profile = await wallet_service.get_profile(user_id)
    balance = await wallet_service.get_balance(user_id)
    # Normalize birth_time : Postgres TIME returns 'HH:MM:SS', frontend expects 'HH:MM'
    bt = profile.get('birth_time')
    if isinstance(bt, str) and len(bt) >= 5:
        bt = bt[:5]
    return {
        'user': {
            'id': user_id,
            'email': current_user.get('email') or profile.get('email'),
            'prenom': profile.get('prenom'),
            'birth_date': profile.get('birth_date'),
            'birth_time': bt,
            'birth_place': profile.get('birth_place'),
            'birth_country': profile.get('birth_country'),
            'gender': profile.get('gender'),
            'latitude': profile.get('latitude'),
            'longitude': profile.get('longitude'),
            'is_admin': profile.get('is_admin', False),
            'is_premium': profile.get('premium_status') == 'active',
            'premium_status': profile.get('premium_status', 'free'),
        },
        'credit_balance': balance,
    }


@api_router.put('/auth/profile')
async def update_profile_endpoint(
    payload: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    profile = await wallet_service.update_profile(current_user['id'], payload.model_dump(exclude_unset=True))
    return {'success': True, 'profile': profile}


# ════════════════════════════════════════════
# WALLET / CREDITS
# ════════════════════════════════════════════
@api_router.get('/wallet/balance')
async def wallet_balance(current_user: dict = Depends(get_current_user)):
    balance = await wallet_service.get_balance(current_user['id'])
    return {'credit_balance': balance}


_SIGNS_FR = {
    'Aries': 'Belier', 'Taurus': 'Taureau', 'Gemini': 'Gemeaux',
    'Cancer': 'Cancer', 'Leo': 'Lion', 'Virgo': 'Vierge',
    'Libra': 'Balance', 'Scorpio': 'Scorpion', 'Sagittarius': 'Sagittaire',
    'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons',
}

_SIGN_SYMBOLS = {
    'Belier': '♈', 'Taureau': '♉', 'Gemeaux': '♊', 'Cancer': '♋',
    'Lion': '♌', 'Vierge': '♍', 'Balance': '♎', 'Scorpion': '♏',
    'Sagittaire': '♐', 'Capricorne': '♑', 'Verseau': '♒', 'Poissons': '♓',
}

_SIGN_THEMES = {
    'Belier': "Audace, élan, action",
    'Taureau': "Stabilité, sensualité, persévérance",
    'Gemeaux': "Curiosité, parole, dualité",
    'Cancer': "Émotion, foyer, mémoire",
    'Lion': "Rayonnement, créativité, fierté",
    'Vierge': "Précision, service, discernement",
    'Balance': "Harmonie, relation, justice",
    'Scorpion': "Intensité, transformation, profondeur",
    'Sagittaire': "Aventure, sens, expansion",
    'Capricorne': "Structure, ambition, patience",
    'Verseau': "Liberté, innovation, idéal",
    'Poissons': "Intuition, rêve, compassion",
}

_PLANET_DESC = {
    'sun': ("Soleil", "ton essence, ce que tu rayonnes"),
    'moon': ("Lune", "tes émotions, ton monde intérieur"),
    'ascendant': ("Ascendant", "la façon dont tu te montres au monde"),
}


@api_router.get('/natal/essentials')
async def natal_essentials(current_user: dict = Depends(get_current_user)):
    """Retourne Soleil, Lune, Ascendant de l'utilisateur connecte (donnees natales).
    Utilisé en haut de la page Consultation pour montrer que la guidance est personnalisée."""
    profile = await wallet_service.get_profile(current_user['id'])
    bd = profile.get('birth_date')
    bt = profile.get('birth_time')
    lat = profile.get('latitude')
    lon = profile.get('longitude')
    if not bd or not bt or lat is None or lon is None:
        return {'success': False, 'message': 'Données natales incomplètes', 'has_data': False}

    try:
        time_str = bt[:5] if len(str(bt)) >= 5 else str(bt)
        svc = AstrologyAPIService()
        data = await svc.get_western_horoscope(str(bd), time_str, float(lat), float(lon), 1.0)
        if not data or 'planets' not in data:
            return {'success': False, 'message': 'API astrologique indisponible', 'has_data': False}

        planets = {p['name'].lower(): p for p in data['planets']}
        # Ascendant = signe de la maison 1
        asc_sign_en = None
        for h in (data.get('houses') or []):
            if h.get('house') == 1:
                asc_sign_en = h.get('sign')
                break
        if asc_sign_en:
            planets['ascendant'] = {'name': 'Ascendant', 'sign': asc_sign_en, 'house': 1, 'normDegree': 0}

        result = {}
        for key in ['sun', 'moon', 'ascendant']:
            p = planets.get(key)
            if not p:
                continue
            sign_en = p.get('sign', '')
            sign_fr = _SIGNS_FR.get(sign_en, sign_en)
            label, desc = _PLANET_DESC[key]
            result[key] = {
                'label': label,
                'sign': sign_fr,
                'symbol': _SIGN_SYMBOLS.get(sign_fr, ''),
                'description': desc,
                'theme': _SIGN_THEMES.get(sign_fr, ''),
                'house': p.get('house'),
            }
        return {
            'success': True,
            'has_data': True,
            'prenom': profile.get('prenom'),
            'birth_place': profile.get('birth_place'),
            'essentials': result,
        }
    except Exception as e:
        logger.error(f'natal_essentials error: {e}')
        return {'success': False, 'message': str(e), 'has_data': False}


@api_router.get('/energy/today')
async def energy_today(current_user: dict = Depends(get_current_user)):
    """Energie du jour (4 sections : dominante / relationnel / attention / opportunite).
    Cache automatique par user/jour."""
    profile = await wallet_service.get_profile(current_user['id'])
    if not profile.get('birth_date') or not profile.get('birth_time') or profile.get('latitude') is None:
        return {'success': False, 'has_data': False, 'message': 'Donnees natales incompletes'}
    result = await get_energy_today(current_user['id'], profile)
    result['prenom'] = profile.get('prenom')
    return result


@api_router.get('/wallet/transactions')
async def wallet_transactions(current_user: dict = Depends(get_current_user), limit: int = 50):
    transactions = await wallet_service.get_transactions(current_user['id'], limit=limit)
    return {'transactions': transactions}


class UseCreditsRequest(BaseModel):
    service_id: str
    amount: Optional[int] = None


@api_router.post('/credits/use')
async def use_credits(payload: UseCreditsRequest, current_user: dict = Depends(get_current_user)):
    cost = payload.amount if payload.amount is not None else settings.SERVICE_COSTS.get(payload.service_id)
    if not cost:
        raise HTTPException(status_code=400, detail='Service inconnu')

    # 1er tarot oui/non gratuit
    if payload.service_id == 'tarot_oui_non':
        used = await wallet_service.has_used_free_tarot(current_user['id'])
        if not used:
            await wallet_service.mark_free_tarot_used(current_user['id'])
            balance = await wallet_service.get_balance(current_user['id'])
            return {'success': True, 'free': True, 'credit_balance': balance}

    new_balance = await wallet_service.deduct_credits(
        current_user['id'], cost, f'Utilisation : {payload.service_id}'
    )
    return {'success': True, 'free': False, 'credit_balance': new_balance, 'cost': cost}


class PromoRequest(BaseModel):
    code: str


@api_router.post('/credits/promo')
async def redeem_promo(payload: PromoRequest, current_user: dict = Depends(get_current_user)):
    return await wallet_service.redeem_promo(current_user['id'], payload.code)


# ════════════════════════════════════════════
# STRIPE — CHECKOUT + WEBHOOK
# ════════════════════════════════════════════
class CheckoutRequest(BaseModel):
    pack_id: str
    origin_url: str


@api_router.post('/credits/checkout')
async def create_checkout(
    payload: CheckoutRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
):
    pack = settings.PACKS.get(payload.pack_id)
    if not pack:
        raise HTTPException(status_code=400, detail='Pack inconnu')

    host_url = str(http_request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/credits/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/acheter-credits'

    req = CheckoutSessionRequest(
        amount=float(pack['amount']),
        currency=pack['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': current_user['id'],
            'user_email': current_user.get('email') or '',
            'pack_id': payload.pack_id,
            'credits': str(pack['credits']),
        },
    )
    session = await stripe_checkout.create_checkout_session(req)

    # Enregistrer la transaction en pending
    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_id': current_user['id'],
            'user_email': current_user.get('email'),
            'pack_id': payload.pack_id,
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': int(pack['credits']),
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {'pack_name': pack['name']},
        }).execute()
    except Exception as e:
        logger.warning(f'Could not log payment_transaction: {e}')

    return {'url': session.url, 'session_id': session.session_id}


@api_router.get('/payments/status/{session_id}')
async def payment_status(session_id: str, current_user: dict = Depends(get_current_user)):
    """Polling endpoint apres redirection Stripe."""
    sb = get_admin_client()

    tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    if not tx_res or not tx_res.data:
        raise HTTPException(status_code=404, detail='Transaction inconnue')
    tx = tx_res.data
    if tx.get('user_id') and tx['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail='Accès refusé')

    # Si deja accordes, on renvoie le status existant
    if tx['credits_granted']:
        balance = await wallet_service.get_balance(current_user['id'])
        return {
            'status': tx['status'],
            'payment_status': tx['payment_status'],
            'credits_granted': True,
            'credits': tx['credits'],
            'credit_balance': balance,
        }

    # Sinon on interroge Stripe
    host_url = 'https://api.stripe.com'  # base inutilisee
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url='')
    checkout_status = await stripe_checkout.get_checkout_status(session_id)

    updates = {
        'status': checkout_status.status,
        'payment_status': checkout_status.payment_status,
    }
    new_balance = None
    # Si paye et pas encore credite -> on credite
    if checkout_status.payment_status == 'paid' and not tx['credits_granted']:
        credits = int(tx['credits'])
        new_balance = await wallet_service.add_credits(
            current_user['id'], credits,
            f"Achat pack {tx['pack_id']} — {credits} credits",
            tx_type='purchase',
        )
        updates['credits_granted'] = True

    sb.table('payment_transactions').update(updates).eq('session_id', session_id).execute()

    if new_balance is None:
        new_balance = await wallet_service.get_balance(current_user['id'])
    return {
        'status': checkout_status.status,
        'payment_status': checkout_status.payment_status,
        'credits_granted': updates.get('credits_granted', tx['credits_granted']),
        'credits': tx['credits'],
        'credit_balance': new_balance,
    }


@api_router.post('/webhook/stripe')
async def stripe_webhook(request: Request):
    """Webhook Stripe — credite l'utilisateur (one-shot) ou active Premium (subscription)."""
    body = await request.body()
    sig = request.headers.get('Stripe-Signature', '')

    # Detect subscription event via raw body parsing (apres handle_webhook ca devient typed)
    import stripe, json as _json
    stripe.api_key = settings.STRIPE_API_KEY
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

    # Si webhook secret configure, verifier la signature
    if webhook_secret:
        try:
            event = stripe.Webhook.construct_event(body, sig, webhook_secret)
        except Exception as e:
            logger.error(f'Webhook signature failed: {e}')
            raise HTTPException(status_code=400, detail='Invalid signature')
    else:
        # Mode permissif (dev / pas de secret)
        try:
            event = _json.loads(body)
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid body')

    event_type = event.get('type') if isinstance(event, dict) else event.type
    data_obj = (event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object)

    # Route vers subscription handler si subscription
    if event_type and ('subscription' in event_type or (event_type == 'checkout.session.completed' and (data_obj.get('mode') if isinstance(data_obj, dict) else getattr(data_obj, 'mode', None)) == 'subscription')):
        evt_dict = event if isinstance(event, dict) else _json.loads(stripe.util.json_dumps(event))
        premium_subscription.handle_subscription_webhook(evt_dict)
        return {'received': True, 'type': event_type}

    # Sinon : flow credits one-shot
    if event_type == 'checkout.session.completed':
        session_data = data_obj if isinstance(data_obj, dict) else data_obj.to_dict()
        if session_data.get('payment_status') != 'paid':
            return {'received': True}
        sb = get_admin_client()
        session_id = session_data.get('id')
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
        if not tx_res or not tx_res.data:
            return {'received': True}
        tx = tx_res.data
        if tx['credits_granted']:
            return {'received': True, 'already_granted': True}
        user_id = tx['user_id'] or (session_data.get('metadata') or {}).get('user_id')
        if not user_id:
            return {'received': True}
        credits = int(tx['credits'])
        await wallet_service.add_credits(user_id, credits, f"Achat pack {tx['pack_id']} — {credits} credits", tx_type='purchase')
        sb.table('payment_transactions').update({
            'credits_granted': True,
            'status': 'completed',
            'payment_status': 'paid',
        }).eq('session_id', session_id).execute()
        return {'received': True, 'granted': True}

    return {'received': True, 'type': event_type}


class PremiumCheckoutRequest(BaseModel):
    origin_url: str


@api_router.post('/premium/checkout')
async def premium_checkout(payload: PremiumCheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Cree une session Stripe pour souscrire au plan Premium 14,99€/mois."""
    return await premium_subscription.create_premium_checkout(
        current_user['id'], current_user.get('email') or '', payload.origin_url
    )


@api_router.get('/premium/status')
async def premium_status(current_user: dict = Depends(get_current_user)):
    """Statut Premium de l'utilisateur."""
    return await premium_subscription.get_subscription_status(current_user['id'])


class PortalRequest(BaseModel):
    return_url: str


@api_router.post('/premium/portal')
async def premium_portal(payload: PortalRequest, current_user: dict = Depends(get_current_user)):
    """Lien vers le Customer Portal Stripe (gerer/annuler son abonnement)."""
    url = await premium_subscription.create_billing_portal(current_user['id'], payload.return_url)
    return {'url': url}


# ════════════════════════════════════════════
# PACKS (lecture publique pour la page Acheter)
# ════════════════════════════════════════════
@api_router.get('/packs')
async def list_packs():
    return {'packs': settings.PACKS, 'service_costs': settings.SERVICE_COSTS}


@api_router.get('/stats/social-proof')
async def social_proof():
    """Compteur d'activite agrege pour preuve sociale.
    Affiche uniquement quand >= 100 (seuil credibilite)."""
    sb = get_admin_client()
    from datetime import datetime, timedelta, timezone
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    # Aggregat : consultations chat + tirages + check-ins
    try:
        msgs = sb.table('plume_chat_messages').select('id', count='exact').eq('role', 'user').gte('created_at', week_ago).execute().count or 0
    except Exception:
        msgs = 0
    try:
        users = sb.table('profiles').select('id', count='exact').gte('created_at', week_ago).execute().count or 0
    except Exception:
        users = 0
    try:
        # Energies generees (cache)
        energies = sb.table('energy_cache').select('user_id', count='exact').gte('created_at', week_ago).execute().count or 0
    except Exception:
        energies = 0

    total = msgs + users + energies
    SHOW_THRESHOLD = 100
    return {
        'consultations_7d': total,
        'visible': total >= SHOW_THRESHOLD,
        'label': f"{total} âmes ont consulté Plume cette semaine" if total >= SHOW_THRESHOLD else None,
    }


# ════════════════════════════════════════════
# TAROT
# ════════════════════════════════════════════
@api_router.get('/tarot/domaines')
async def get_domaines():
    return {'success': True, 'domaines': DOMAINES_QUESTIONS}


@api_router.get('/tarot/jour')
async def get_jour():
    return {'success': True, 'data': tirage_du_jour()}


@api_router.post('/tarot/oui-non')
async def tarot_oui_non_endpoint(request: Request):
    body = await request.json()
    return tirage_oui_non(body.get('question', ''))


@api_router.post('/tarot/marseille')
async def tarot_marseille_endpoint(request: Request):
    body = await request.json()
    result = tirage_marseille_question(body.get('question', ''), body.get('domaine', 'general'))
    return {'success': True, 'data': result}


@api_router.post('/tarot/celtique')
async def tarot_celtique_endpoint(request: Request):
    body = await request.json()
    result = tirage_croix_celtique(body.get('question', ''), body.get('domaine', 'general'))
    return {'success': True, 'data': result}


@api_router.post('/tarologie/tirage')
async def tirage_croix_endpoint(request: Request):
    body = await request.json()
    return tirage_en_croix(body.get('prenom', 'Ami'), '1990-01-01')


# ════════════════════════════════════════════
# DAILY HOROSCOPE
# ════════════════════════════════════════════
@api_router.get('/daily/{zodiac_sign}')
async def get_daily(zodiac_sign: str):
    return get_daily_content(zodiac_sign)


# ════════════════════════════════════════════
# PLUME CHAT IA
# ════════════════════════════════════════════
@api_router.post('/plume-chat')
async def plume_chat_endpoint(
    request: Request,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Body: { message, session_id, birth_data }. Auth optionnelle — invite OK."""
    try:
        body = await request.json()
        message = (body.get('message') or '').strip()
        if not message:
            return {'success': False, 'message': 'Message vide.'}

        session_id = body.get('session_id') or f'plume-{uuid.uuid4().hex[:12]}'
        birth_data = body.get('birth_data') or body.get('user_data')
        user_id = current_user['id'] if current_user else None

        result = await plume_chat_service(
            message=message,
            session_id=session_id,
            birth_data=birth_data,
            user_id=user_id,
        )
        result['session_id'] = session_id
        return result
    except Exception as e:
        logger.error(f'Plume chat endpoint error: {e}', exc_info=True)
        return {'success': False, 'message': 'Une perturbation cosmique empeche la connexion.'}


@api_router.get('/plume-chat/history/{session_id}')
async def plume_chat_history_endpoint(
    session_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    user_id = current_user['id'] if current_user else None
    messages = await get_session_history(session_id, user_id)
    return {'success': True, 'messages': messages}


# ════════════════════════════════════════════
# RITUEL QUOTIDIEN
# ════════════════════════════════════════════
@api_router.get('/ritual/today')
async def ritual_today_endpoint(
    user_id: str,
    name: Optional[str] = None,
    day: Optional[int] = None, month: Optional[int] = None, year: Optional[int] = None,
    hour: Optional[int] = None, minute: Optional[int] = None,
    lat: Optional[float] = None, lon: Optional[float] = None, tzone: Optional[float] = None,
):
    birth_data = None
    if day and month and year:
        birth_data = {
            'name': name or 'Voyageur',
            'day': day, 'month': month, 'year': year,
            'hour': hour or 12, 'min': minute or 0,
            'lat': lat or 48.8566, 'lon': lon or 2.3522, 'tzone': tzone or 1.0,
        }
    checkin = await get_today_checkin(user_id, None)
    mood = checkin.get('mood') if checkin else None
    scores_data = get_today_scores(user_id, mood=mood)
    insight_data = await get_daily_insight(user_id, birth_data=birth_data, mood=mood, db=None)
    streak = await get_streak(user_id, None)
    return {
        'success': True,
        'date': scores_data['date'],
        'scores': scores_data['scores'],
        'moon_phase': scores_data['moon_phase'],
        'moon_theme': scores_data['moon_theme'],
        'insight': insight_data['insight'],
        'checkin': checkin,
        'streak': streak,
    }


@api_router.get('/ritual/moods')
async def ritual_moods_endpoint():
    return {'moods': [{'id': k, **v} for k, v in MOODS.items()]}


@api_router.post('/ritual/checkin')
async def ritual_checkin_endpoint(request: Request):
    body = await request.json()
    user_id = body.get('user_id')
    mood = body.get('mood')
    intention = body.get('intention')
    if not user_id or not mood:
        return {'success': False, 'message': 'user_id et mood requis.'}
    if mood not in MOODS:
        return {'success': False, 'message': 'Humeur inconnue.'}
    result = await submit_checkin(user_id, mood, intention, None)
    streak = await update_streak(user_id, None)
    result['streak'] = streak
    return result


@api_router.post('/journal/entry')
async def journal_entry_endpoint(request: Request):
    body = await request.json()
    user_id = body.get('user_id')
    entry = (body.get('entry') or '').strip()
    if not user_id or not entry:
        return {'success': False, 'message': 'user_id et entry requis.'}
    if len(entry) < 5:
        return {'success': False, 'message': 'Ecris au moins quelques mots.'}
    if len(entry) > 4000:
        return {'success': False, 'message': "L'entree est trop longue (max 4000 caracteres)."}
    result = await journal_entry(user_id, entry, mood=body.get('mood'), birth_data=body.get('birth_data'), db=None)
    return result


@api_router.get('/journal/history')
async def journal_history_endpoint(user_id: str, limit: int = 30):
    history = await get_journal_history(user_id, None, limit=limit)
    return {'success': True, 'entries': history}


# ════════════════════════════════════════════
# FINAL APP CONFIG
# ════════════════════════════════════════════
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'plume-astrale'}


if ASSETS_DIR.exists():
    app.mount('/api/assets', StaticFiles(directory=str(ASSETS_DIR)), name='assets')
