"""Plume Astrale — FastAPI backend (Supabase + Stripe + Astrology API)."""
from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import uuid
import base64
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from urllib.parse import urlparse

# Config + middleware
from config import get_settings
from middleware.auth import get_current_user, get_optional_user

# Services metier
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_en_croix, tirage_mediumnite_complet
from services.tarot_premium import (
    tirage_marseille_question, tirage_croix_celtique, tirage_du_jour,
    DOMAINES_QUESTIONS,
)
from services.pdf_generator import generate_manuscrit_pdf
from services.mediumnite_pdf import generate_mediumnite_pdf
from services.compatibility_pdf_generator import generate_compatibility_pdf
from services.premium_pdf_generator import generate_premium_pdf
from services.share_card_generator import generate_share_card
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
from routes.astrology_v3 import router as astrology_v3_router
from routes.oracle import router as oracle_router
from routes.cercle import router as cercle_router
from routes.synastrie import router as synastrie_router
from routes.library import router as library_router
from routes.rencontres import router as rencontres_router

# Stripe (via emergentintegrations — gere les sandbox keys aussi)
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
ASSETS_DIR = Path(__file__).parent / 'assets'

# Legacy products kept for backwards compatibility with older frontend flows.
PRODUCT_CATALOG = {
    'manuscrit': {'name': 'Manuscrit Astral', 'amount': 19.90, 'currency': 'eur', 'success_path': '/paiement/succes', 'cancel_path': '/apercu'},
    'tarot_oui_non': {'name': 'Tarot Oui/Non', 'amount': 4.99, 'currency': 'eur', 'success_path': '/paiement/succes', 'cancel_path': '/tarot-oui-non'},
    'tarologie_mediumnite': {'name': 'Tarologie Mediumnite', 'amount': 35.00, 'currency': 'eur', 'success_path': '/paiement/succes', 'cancel_path': '/tarologie'},
    'compatibilite': {'name': 'Compatibilite Amoureuse', 'amount': 29.90, 'currency': 'eur', 'success_path': '/paiement/succes', 'cancel_path': '/compatibilite-amoureuse'},
    'book': {'name': 'Livre Astrologique', 'amount': 29.90, 'currency': 'eur', 'success_path': '/commande/succes', 'cancel_path': '/livre'},
}

STREAK_MILESTONES = {7: 3, 14: 5, 30: 10, 60: 15, 100: 25}

app = FastAPI(title='Plume Astrale API')
api_router = APIRouter(prefix='/api')
api_router.include_router(admin_router)
api_router.include_router(astrology_v3_router)
api_router.include_router(oracle_router)
api_router.include_router(cercle_router)
api_router.include_router(synastrie_router)
api_router.include_router(library_router)
api_router.include_router(rencontres_router)


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
    tzone: Optional[float] = None
    tz_manual_override: Optional[bool] = None
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
            'premium_until': profile.get('premium_until'),
            'created_at': profile.get('created_at'),
        },
        'credit_balance': balance,
    }


# Correspondance pays (labels du <select> PAYS) -> code ISO 3166-1 alpha-2
_COUNTRY_TO_ISO = {
    'France': 'FR',
    'Belgique': 'BE',
    'Suisse': 'CH',
    'Canada': 'CA',
    'Luxembourg': 'LU',
    'Monaco': 'MC',
    'Algérie': 'DZ',
    'Maroc': 'MA',
    'Tunisie': 'TN',
    'Sénégal': 'SN',
    "Côte d'Ivoire": 'CI',
    'États-Unis': 'US',
    'Royaume-Uni': 'GB',
    'Allemagne': 'DE',
    'Espagne': 'ES',
    'Italie': 'IT',
    'Portugal': 'PT',
    'Autre': None,
}


@api_router.put('/auth/profile')
async def update_profile_endpoint(
    payload: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)

    # Geocodage automatique : ville presente, coordonnees absentes, pays geocodable
    needs_geo = data.get('birth_place') and data.get('latitude') is None
    iso = _COUNTRY_TO_ISO.get(data.get('birth_country', ''))
    if needs_geo and data.get('birth_date') and iso:
        try:
            y, mo, d = (int(x) for x in data['birth_date'].split('-'))
            hh, mi = 12, 0
            if data.get('birth_time'):
                hh, mi = (int(x) for x in data['birth_time'].split(':'))
            geo = await aio.geocode_and_timezone(
                data['birth_place'], iso, y, mo, d, hh, mi)
            if geo:
                data['latitude'] = geo['latitude']
                data['longitude'] = geo['longitude']
                # Ne pas ecraser le fuseau si l'utilisateur l'a force manuellement
                if not data.get('tz_manual_override'):
                    data['tzone'] = geo['tzone']
        except Exception as e:
            print(f'[profile] geocode skip: {e}')

    profile = await wallet_service.update_profile(current_user['id'], data)
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
            return {'success': True, 'free': True, 'free_draw': True, 'credit_balance': balance}

    new_balance = await wallet_service.deduct_credits(
        current_user['id'], cost, f'Utilisation : {payload.service_id}'
    )
    return {'success': True, 'free': False, 'free_draw': False, 'credit_balance': new_balance, 'cost': cost}


@api_router.get('/credits/check-free-tarot')
async def check_free_tarot(current_user: dict = Depends(get_current_user)):
    free_used = await wallet_service.has_used_free_tarot(current_user['id'])
    return {'free_used': free_used}


def _next_milestone(streak_count: int) -> dict:
    for day in sorted(STREAK_MILESTONES.keys()):
        if streak_count < day:
            return {
                'days': day,
                'bonus': STREAK_MILESTONES[day],
                'remaining': day - streak_count,
            }
    return {
        'days': max(STREAK_MILESTONES.keys()),
        'bonus': STREAK_MILESTONES[max(STREAK_MILESTONES.keys())],
        'remaining': 0,
    }


@api_router.get('/streak/status')
async def streak_status(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    streak = await get_streak(user_id)
    today_checkin = await get_today_checkin(user_id)
    total_checkins = 0
    try:
        sb = get_admin_client()
        total_checkins = sb.table('daily_checkins').select('id', count='exact').eq('user_id', user_id).execute().count or 0
    except Exception:
        total_checkins = 0

    return {
        'streak_count': streak.get('current', 0),
        'longest_streak': streak.get('longest', 0),
        'checked_in_today': bool(today_checkin),
        'total_checkins': total_checkins,
        'next_milestone': _next_milestone(streak.get('current', 0)),
    }


@api_router.post('/streak/checkin')
async def streak_checkin(current_user: dict = Depends(get_current_user)):
    user_id = current_user['id']
    today_checkin = await get_today_checkin(user_id)
    streak = await get_streak(user_id)

    if today_checkin:
        balance = await wallet_service.get_balance(user_id)
        return {
            'already_checked_in': True,
            'streak_count': streak.get('current', 0),
            'credits_earned': 0,
            'milestone_bonus': 0,
            'credit_balance': balance,
            'next_milestone': _next_milestone(streak.get('current', 0)),
        }

    # Legacy daily streak check-in awards +1 credit (+ milestone bonus).
    await submit_checkin(user_id, 'paisible', None)
    streak = await update_streak(user_id)
    streak_count = streak.get('current', 1)
    milestone_bonus = STREAK_MILESTONES.get(streak_count, 0)
    credits_earned = 1 + milestone_bonus
    balance = await wallet_service.add_credits(
        user_id,
        credits_earned,
        f'Check-in quotidien (jour {streak_count})',
        tx_type='bonus',
    )

    return {
        'already_checked_in': False,
        'streak_count': streak_count,
        'credits_earned': credits_earned,
        'milestone_bonus': milestone_bonus,
        'credit_balance': balance,
        'next_milestone': _next_milestone(streak_count),
    }


class PromoRequest(BaseModel):
    code: str


@api_router.post('/credits/promo')
async def redeem_promo(payload: PromoRequest, current_user: dict = Depends(get_current_user)):
    return await wallet_service.redeem_promo(current_user['id'], payload.code)


# ════════════════════════════════════════════
# DISCOUNT CODES (réutilise promo_codes Supabase)
# ════════════════════════════════════════════
class DiscountValidateRequest(BaseModel):
    code: str
    product_id: str | None = None


@api_router.post('/discount/validate')
async def validate_discount(payload: DiscountValidateRequest):
    """Valide un code de reduction. Renvoie discount_percent=100 si le code donne acces gratuit.
    Public (pas d'auth requise) car appele depuis pages de checkout invitees."""
    from services.wallet_service import get_admin_client
    sb = get_admin_client()
    code = payload.code.strip().upper() if payload.code else ''
    if not code:
        return {'valid': False, 'message': 'Code requis', 'discount_percent': 0}
    res = sb.table('promo_codes').select('*').eq('code', code).eq('active', True).maybe_single().execute()
    if not res or not res.data:
        return {'valid': False, 'message': 'Code invalide ou expire', 'discount_percent': 0}
    d = res.data
    if d.get('max_uses') and d.get('used_count', 0) >= d['max_uses']:
        return {'valid': False, 'message': 'Ce code a atteint sa limite', 'discount_percent': 0}
    # Tout code promo valide donne 100% de reduction (acces gratuit)
    return {
        'valid': True,
        'discount_percent': 100,
        'message': d.get('description') or 'Code valide',
        'credits': d.get('credits') or 0,
        'premium_days': d.get('premium_days') or 0,
    }


class FreeAccessRequest(BaseModel):
    product_id: str
    discount_code: str
    user_data: dict | None = None


@api_router.post('/access/free')
async def grant_free_access(payload: FreeAccessRequest, current_user: dict = Depends(get_current_user)):
    """Applique un code de reduction (en redeem) pour debloquer l'acces a un produit.
    Reutilise redeem_promo qui credite OU active Premium selon le code."""
    try:
        result = await wallet_service.redeem_promo(current_user['id'], payload.discount_code)
        return {
            'success': True,
            'access_granted': True,
            'product_id': payload.product_id,
            **result,
        }
    except HTTPException as e:
        if e.status_code == 409:
            # Deja utilise -> on considere quand meme que l'acces est valide
            return {'success': True, 'access_granted': True, 'already_redeemed': True}
        raise


class LegacyCheckoutRequest(BaseModel):
    product_id: str
    origin_url: str
    user_email: str | None = None
    user_data: dict | None = None


@api_router.get('/products')
async def list_products():
    return PRODUCT_CATALOG


@api_router.post('/checkout/create')
async def legacy_checkout_create(payload: LegacyCheckoutRequest, http_request: Request):
    product = PRODUCT_CATALOG.get(payload.product_id)
    if not product:
        raise HTTPException(status_code=400, detail='Produit inconnu')

    host_url = str(http_request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_path = product.get('success_path', '/paiement/succes')
    cancel_path = product.get('cancel_path', '/')
    success_url = f'{origin}{success_path}?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}{cancel_path}'

    req = CheckoutSessionRequest(
        amount=float(product['amount']),
        currency=product['currency'],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product_id': payload.product_id,
            'user_email': payload.user_email or '',
            'flow': 'legacy_checkout',
        },
    )
    session = await stripe_checkout.create_checkout_session(req)
    return {'url': session.url, 'session_id': session.session_id}


@api_router.get('/checkout/status/{session_id}')
async def legacy_checkout_status(session_id: str):
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url='')
    status = await stripe_checkout.get_checkout_status(session_id)
    return {
        'status': status.status,
        'payment_status': status.payment_status,
        'session_id': session_id,
    }


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

    total_credits = int(pack.get('credits', 0)) + int(pack.get('bonus', 0) or 0)

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
            'credits': str(total_credits),
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
            'credits': total_credits,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'pack_name': pack['name'],
                'base_credits': int(pack.get('credits', 0)),
                'bonus': int(pack.get('bonus', 0) or 0),
            },
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

    # Route vers synastrie handler si kind=synastrie_oneshot
    md = (data_obj.get('metadata') if isinstance(data_obj, dict) else getattr(data_obj, 'metadata', {})) or {}
    if md.get('kind') == 'synastrie_oneshot':
        from services.synastrie_oneshot import handle_synastrie_webhook
        evt_dict = event if isinstance(event, dict) else _json.loads(stripe.util.json_dumps(event))
        handle_synastrie_webhook(evt_dict)
        # Tente generation PDF + email en arriere-plan (best-effort)
        try:
            await _trigger_synastrie_pdf_email(data_obj.get('id') if isinstance(data_obj, dict) else data_obj.id)
        except Exception as e:
            logger.warning(f'[synastrie] post-webhook fail: {e}')
        return {'received': True, 'type': event_type, 'kind': 'synastrie_oneshot'}

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


async def _trigger_synastrie_pdf_email(session_id: Optional[str]) -> None:
    """Apres paiement synastrie : genere le PDF et envoie l'email via Resend."""
    if not session_id:
        return
    from datetime import datetime, timezone
    sb = get_admin_client()
    r = sb.table('synastrie_purchases').select(
        'id, email, person1_data, person2_data, pdf_path'
    ).eq('stripe_session_id', session_id).maybe_single().execute()
    if not r or not r.data:
        return
    rec = r.data
    if rec.get('pdf_path'):
        return  # deja genere

    # Generation PDF best-effort
    pdf_path = None
    try:
        from services.synastrie_pdf_generator import generate_synastrie_pdf
        from services.synastrie_enrichment import fetch_astro_data, enrich_pages
        p1 = rec['person1_data']
        p2 = rec['person2_data']
        # Enrichissement Option A : 10 pages personnalisees via GPT-4o-mini + astro-api
        try:
            astro = await fetch_astro_data(p1, p2)
            enriched = await enrich_pages(astro)
        except Exception as ee:
            logger.warning(f'[synastrie] enrichment failed, falling back to static: {ee}')
            enriched = None
        pdf_bytes = generate_synastrie_pdf(p1, p2, enriched=enriched)
        out_dir = ASSETS_DIR / 'synastrie'
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f'synastrie_{rec["id"]}.pdf'
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/synastrie/{filename}'
        sb.table('synastrie_purchases').update({
            'pdf_path': pdf_path,
            'pdf_generated_at': datetime.now(timezone.utc).isoformat(),
        }).eq('id', rec['id']).execute()
        logger.info(f'[synastrie] PDF generated: {pdf_path}')
    except Exception as e:
        logger.error(f'[synastrie] PDF gen failed: {e}')

    # Envoi email best-effort
    try:
        if pdf_path and rec.get('email'):
            from services.resend_service import send_synastrie_email
            await send_synastrie_email(rec['email'], rec['person1_data'].get('prenom', ''), rec['person2_data'].get('prenom', ''), pdf_path)
            sb.table('synastrie_purchases').update({
                'email_sent_at': datetime.now(timezone.utc).isoformat(),
            }).eq('id', rec['id']).execute()
    except Exception as e:
        logger.warning(f'[synastrie] email send failed: {e}')


class PremiumCheckoutRequest(BaseModel):
    origin_url: str


@api_router.post('/premium/checkout')
async def premium_checkout(payload: PremiumCheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Cree une session Stripe pour souscrire au plan Premium 14,99€/mois."""
    return await premium_subscription.create_premium_checkout(
        current_user['id'], current_user.get('email') or '', payload.origin_url
    )


class LegacySubscriptionRequest(BaseModel):
    origin_url: str | None = None


class PlanetsLegacyRequest(BaseModel):
    date_naissance: str
    heure_naissance: str | None = '12:00'
    ville: str | None = 'Paris'
    pays: str | None = 'France'


class HoroscopeLegacyRequest(PlanetsLegacyRequest):
    pass


class PdfUserDataRequest(BaseModel):
    user_data: dict


class PremiumGenerateRequest(BaseModel):
    prenom: str
    dateNaissance: str
    heureNaissance: str | None = '12:00'
    ville: str | None = 'Paris'


class PremiumPdfRequest(BaseModel):
    data: dict


class CompatibilityGenerateRequest(BaseModel):
    person1: dict
    person2: dict
    question: str | None = ''


class BookOrderRequest(BaseModel):
    product_id: str
    origin_url: str
    user_email: str | None = None
    user_data: dict | None = None
    shipping_address: dict | None = None


def _resolve_origin_url(request: Request, explicit_origin: str | None) -> str:
    if explicit_origin and explicit_origin.strip():
        return explicit_origin.rstrip('/')
    header_origin = (request.headers.get('origin') or '').strip()
    if header_origin:
        return header_origin.rstrip('/')
    referer = (request.headers.get('referer') or '').strip()
    if referer:
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            return f'{parsed.scheme}://{parsed.netloc}'
    return str(request.base_url).rstrip('/')


def _extract_sign_from_date(date_str: str) -> str:
    from datetime import datetime as _dt
    d = _dt.strptime(date_str, '%Y-%m-%d')
    m, day = d.month, d.day
    if (m == 3 and day >= 21) or (m == 4 and day <= 19):
        return 'Aries'
    if (m == 4 and day >= 20) or (m == 5 and day <= 20):
        return 'Taurus'
    if (m == 5 and day >= 21) or (m == 6 and day <= 20):
        return 'Gemini'
    if (m == 6 and day >= 21) or (m == 7 and day <= 22):
        return 'Cancer'
    if (m == 7 and day >= 23) or (m == 8 and day <= 22):
        return 'Leo'
    if (m == 8 and day >= 23) or (m == 9 and day <= 22):
        return 'Virgo'
    if (m == 9 and day >= 23) or (m == 10 and day <= 22):
        return 'Libra'
    if (m == 10 and day >= 23) or (m == 11 and day <= 21):
        return 'Scorpio'
    if (m == 11 and day >= 22) or (m == 12 and day <= 21):
        return 'Sagittarius'
    if (m == 12 and day >= 22) or (m == 1 and day <= 19):
        return 'Capricorn'
    if (m == 1 and day >= 20) or (m == 2 and day <= 18):
        return 'Aquarius'
    return 'Pisces'


@api_router.post('/subscription/cercle')
async def subscription_cercle(
    payload: LegacySubscriptionRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    origin = _resolve_origin_url(request, payload.origin_url)
    checkout = await premium_subscription.create_premium_checkout(
        current_user['id'],
        current_user.get('email') or '',
        origin,
    )
    return {'checkout_url': checkout.get('url'), 'session_id': checkout.get('session_id')}


@api_router.post('/subscription/journal-quotidien')
async def subscription_journal_quotidien(
    payload: LegacySubscriptionRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    origin = _resolve_origin_url(request, payload.origin_url)
    checkout = await premium_subscription.create_premium_checkout(
        current_user['id'],
        current_user.get('email') or '',
        origin,
    )
    return {'checkout_url': checkout.get('url'), 'session_id': checkout.get('session_id')}


@api_router.post('/astrology/planets')
async def legacy_astrology_planets(payload: PlanetsLegacyRequest):
    try:
        sign = _extract_sign_from_date(payload.date_naissance)
    except Exception:
        sign = 'Aries'
    planets = [
        {'name': 'Sun', 'sign': sign, 'house': 1, 'normDegree': 0},
        {'name': 'Moon', 'sign': sign, 'house': 4, 'normDegree': 15},
        {'name': 'Ascendant', 'sign': sign, 'house': 1, 'normDegree': 0},
    ]
    try:
        svc = AstrologyAPIService()
        geo = await svc.get_geo_details(f"{payload.ville}, {payload.pays}")
        lat, lon, tz = 48.8566, 2.3522, 1.0
        if geo and isinstance(geo, list) and len(geo) > 0:
            g = geo[0]
            lat = float(g.get('latitude', lat))
            lon = float(g.get('longitude', lon))
            tz = float(g.get('timezone_offset', tz)) if g.get('timezone_offset') else tz
        data = await svc.get_western_horoscope(payload.date_naissance, payload.heure_naissance or '12:00', lat, lon, tz)
        if data and isinstance(data, dict):
            planets_map = data.get('planets') or []
            asc_sign = None
            for h in (data.get('houses') or []):
                if h.get('house') == 1:
                    asc_sign = h.get('sign')
                    break
            if asc_sign:
                planets_map = list(planets_map) + [{'name': 'Ascendant', 'sign': asc_sign, 'house': 1, 'normDegree': 0}]
            planets = planets_map or planets
    except Exception:
        pass
    return {'success': True, 'data': planets}


@api_router.post('/astrology/horoscope')
async def legacy_astrology_horoscope(payload: HoroscopeLegacyRequest):
    sign = _extract_sign_from_date(payload.date_naissance)
    sign_fr = _SIGNS_FR.get(sign, sign)
    data = None
    try:
        svc = AstrologyAPIService()
        data = await svc.get_daily_horoscope(sign.lower(), 1.0)
    except Exception:
        data = None
    if not data:
        data = {
            'prediction': f"Aujourd'hui, {sign_fr} avance avec confiance. Ose une action simple et alignee.",
            'health': 'Ralentis le rythme et ecoute ton corps.',
            'love': 'Privilégie la clarté et la douceur dans les échanges.',
            'career': 'Un petit pas concret vaut mieux qu\'un grand plan.',
        }
    return {'success': True, 'zodiac_french': sign_fr, 'data': data}


@api_router.post('/share/generate-card')
async def share_generate_card(payload: PdfUserDataRequest):
    user_data = payload.user_data or {}
    # Robust fallback with no external dependency required.
    path_life = 1
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(user_data.get('dateNaissance') or user_data.get('birth_date') or '1990-01-01', '%Y-%m-%d')
        n = d.day + d.month + d.year
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(c) for c in str(n))
        path_life = n
    except Exception:
        path_life = 1
    png = generate_share_card(user_data=user_data, planets_data=None, chemin_vie=path_life)
    return Response(content=png, media_type='image/png', headers={'Cache-Control': 'no-store'})


@api_router.post('/pdf/generate')
async def pdf_generate(payload: PdfUserDataRequest):
    user_data = payload.user_data or {}
    pdf_bytes = generate_manuscrit_pdf(user_data=user_data, planets_data=None, horoscope_data=None)
    return Response(content=pdf_bytes, media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="manuscrit_{user_data.get("prenom", "plume")}.pdf"'
    })


@api_router.post('/pdf/pro-horoscope')
async def pdf_pro_horoscope(request: Request):
    body = await request.json()
    user_data = {
        'prenom': body.get('name') or 'Voyageur',
        'dateNaissance': f"{int(body.get('year', 1990)):04d}-{int(body.get('month', 1)):02d}-{int(body.get('day', 1)):02d}",
        'heureNaissance': f"{int(body.get('hour', 12)):02d}:{int(body.get('minute', 0)):02d}",
        'ville': (body.get('place') or 'Paris').split(',')[0].strip(),
        'pays': 'France',
    }
    pdf_bytes = generate_manuscrit_pdf(user_data=user_data, planets_data=None, horoscope_data=None)
    return Response(content=pdf_bytes, media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="theme_astral_pro_{user_data.get("prenom", "plume")}.pdf"'
    })


@api_router.post('/pdf/preview')
async def pdf_preview(payload: PdfUserDataRequest):
    # Lightweight preview fallback to keep the front flow operational.
    tiny_png = base64.b64encode(
        bytes.fromhex('89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000A49444154789C6360000000020001E221BC330000000049454E44AE426082')
    ).decode('ascii')
    previews = [f'data:image/png;base64,{tiny_png}' for _ in range(3)]
    return {'previews': previews, 'total_pages': 1}


@api_router.post('/premium/generate')
async def premium_generate(payload: PremiumGenerateRequest):
    try:
        sign = _extract_sign_from_date(payload.dateNaissance)
    except Exception:
        sign = 'Aries'
    sign_fr = _SIGNS_FR.get(sign, sign)

    premium_data = {
        'prenom': payload.prenom or 'Voyageur',
        'signe': sign_fr,
        'date_naissance': payload.dateNaissance,
        'steps': {
            'step_1_fondement': {
                'title': 'Fondement Natal',
                'subtitle': 'La base vibratoire de votre theme',
                'signe': sign_fr,
                'element': _SIGN_THEMES.get(sign_fr, 'Essence en construction'),
                'modalite': 'Cardinale',
                'forces': ['Presence intuitive', 'Puissance de regeneration'],
                'tensions': ['Dispersion energetique'],
                'interpretation': 'Votre base natale indique une forte sensibilite aux cycles.\nAncrez votre energie dans une pratique quotidienne simple.',
                'reflection': 'Qu\'est-ce qui vous recentre instantanement ?'
            },
            'step_2_chemin_ame': {
                'title': 'Chemin d\'Ame',
                'subtitle': 'Votre axe d\'evolution interieur',
                'chemin_de_vie': 7,
                'titre_chemin': 'Le Sage',
                'nombre_expression': 4,
                'nombre_ame': 2,
                'forces': ['Vision interieure', 'Recherche de sens'],
                'tensions': ['Doute excessif'],
                'interpretation': 'Votre chemin vous appelle a transformer l\'intuition en decisions concretes.',
                'reflection': 'Quelle verite personnelle n\'osez-vous pas encore affirmer ?'
            },
            'step_3_cycle': {
                'title': 'Cycle Actuel',
                'subtitle': 'La dynamique des 12 prochains mois',
                'annee_personnelle': 6,
                'periode': 'Stabilisation et engagement',
                'forces': ['Constance', 'Clarte relationnelle'],
                'tensions': ['Surcharge de responsabilites'],
                'interpretation': 'Cette periode favorise la construction durable et la coherence emotionnelle.',
                'reflection': 'Quel engagement merite d\'etre simplifie pour durer ?'
            },
            'step_4_schemas': {
                'title': 'Schemas Repetitifs',
                'subtitle': 'Identifier pour transmuter',
                'forces': ['Lucidite psychologique'],
                'tensions': ['Auto-pression', 'Perfectionnisme'],
                'interpretation': 'Vos schemas anciens se dissolvent lorsque vous privilegiez l\'action imparfaite.',
                'reflection': 'Quel petit geste ferait deja basculer la tendance ?'
            },
            'step_5_projection': {
                'title': 'Projection Alignee',
                'subtitle': 'Votre prochaine expansion',
                'forces': ['Vision long terme', 'Puissance creatrice'],
                'tensions': ['Hesitation a vous exposer'],
                'interpretation': 'Le prochain palier demande de rendre visible votre singularite.',
                'reflection': 'Quelle action visible pouvez-vous poser cette semaine ?'
            },
        }
    }
    return {'success': True, 'data': premium_data}


@api_router.post('/premium/pdf')
async def premium_pdf(payload: PremiumPdfRequest):
    pdf_bytes = generate_premium_pdf(payload.data or {})
    prenom = (payload.data or {}).get('prenom', 'plume')
    return Response(content=pdf_bytes, media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="cartographie_premium_{prenom}.pdf"'
    })


@api_router.post('/compatibility/generate')
async def compatibility_generate(payload: CompatibilityGenerateRequest):
    person1 = payload.person1 or {}
    person2 = payload.person2 or {}
    pdf_bytes = generate_compatibility_pdf(person1=person1, person2=person2, question=payload.question or '')
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    return {'success': True, 'pdf_url': f'data:application/pdf;base64,{pdf_b64}'}


@api_router.post('/tarologie/pdf')
async def tarologie_pdf(request: Request):
    body = await request.json()
    prenom = (body.get('prenom') or 'Voyageur').strip() or 'Voyageur'
    date_naissance = body.get('date_naissance') or '1990-01-01'
    tirage = tirage_mediumnite_complet(prenom, date_naissance)
    pdf_bytes = generate_mediumnite_pdf(tirage)
    return Response(content=pdf_bytes, media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="tarologie_croix_{prenom}.pdf"'
    })


@api_router.post('/order/book')
async def order_book(payload: BookOrderRequest, http_request: Request):
    if payload.product_id != 'livre':
        raise HTTPException(status_code=400, detail='Produit livre attendu')
    order_req = LegacyCheckoutRequest(
        product_id='book',
        origin_url=payload.origin_url,
        user_email=payload.user_email,
        user_data=payload.user_data,
    )
    checkout = await legacy_checkout_create(order_req, http_request)
    return {
        'url': checkout['url'],
        'session_id': checkout['session_id'],
        'order_id': f"book-{checkout['session_id'][:12]}",
    }


@api_router.get('/order/book/{session_id}')
async def order_book_status(session_id: str):
    status = await legacy_checkout_status(session_id)
    return {
        'session_id': session_id,
        'status': status.get('status'),
        'payment_status': status.get('payment_status'),
    }


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


# ════════════════════════════════════════════
# NUMEROLOGIE
# ════════════════════════════════════════════
from services import numerology_service


@api_router.post('/numerology/complete')
async def numerology_complete(request: Request):
    body = await request.json()
    try:
        return numerology_service.compute_complete(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post('/numerology/deep-profile')
async def numerology_deep(request: Request):
    body = await request.json()
    try:
        return numerology_service.compute_deep(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ════════════════════════════════════════════
# ASTROLOGIE (Karma & Destin + Natal chart)
# ════════════════════════════════════════════
@api_router.post('/astrology/karma-destiny')
async def astrology_karma_destiny(request: Request):
    """Karma & destin — calcul precis du Noeud Nord via astrology-api.io v3, fallback
    AstrologyAPI puis approximatif. Renvoie une lecture karmique riche prete a afficher."""
    body = await request.json()
    prenom = body.get('prenom', '').strip()
    date_naissance = body.get('dateNaissance')
    heure = body.get('heureNaissance') or '12:00'
    ville = body.get('ville') or 'Paris'
    pays = body.get('pays') or 'France'

    if not date_naissance:
        raise HTTPException(status_code=400, detail='dateNaissance requise')
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(date_naissance, '%Y-%m-%d')
        hh_str, mm_str = (heure.split(':') + ['0'])[:2]
        hh, mm = int(hh_str), int(mm_str)
    except ValueError:
        raise HTTPException(status_code=400, detail='Format date invalide (YYYY-MM-DD)')

    signes_fr = {
        'Aries': 'Bélier', 'Taurus': 'Taureau', 'Gemini': 'Gémeaux', 'Cancer': 'Cancer',
        'Leo': 'Lion', 'Virgo': 'Vierge', 'Libra': 'Balance', 'Scorpio': 'Scorpion',
        'Sagittarius': 'Sagittaire', 'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons',
    }
    signes_ordre = ['Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
                    'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons']

    KARMA_PROFILES = {
        'Bélier': {
            'icon': '♈',
            'theme': "L'Eveil du Guerrier",
            'description': "Votre ame revient dans cette vie pour apprendre l'audace et l'autonomie. Les blessures du passe vous ont enseigne la dependance ; cette incarnation vous invite a oser etre seul, a affirmer vos desirs sans demander pardon.",
            'lecon': "Cesser d'attendre la permission. Choisir votre propre chemin meme s'il deplait.",
            'don_cache': "Un courage instinctif. Vous savez agir vite et juste quand les autres hesitent.",
        },
        'Taureau': {
            'icon': '♉',
            'theme': "L'Ancrage Sacre",
            'description': "Vous etes ici pour habiter pleinement votre corps et le monde sensoriel. Les vies passees vous ont rendu intense, obsessionnel ; cette incarnation vous propose la simplicite, la lenteur, le plaisir tranquille.",
            'lecon': "Ralentir. Construire patiemment ce qui dure plutot que tout consommer.",
            'don_cache': "Un sens inne de la valeur. Vous reconnaissez ce qui est precieux et stable.",
        },
        'Gémeaux': {
            'icon': '♊',
            'theme': "La Voix qui Relie",
            'description': "Votre mission est de communiquer, d'apprendre et de partager. Vous arrivez avec une habitude de la verite absolue ; cette vie vous demande d'accueillir la nuance, la curiosite, le dialogue.",
            'lecon': "Quitter le dogme. Ecouter avant d'enseigner.",
            'don_cache': "Une intelligence agile. Vous tissez des liens entre les idees et les etres.",
        },
        'Cancer': {
            'icon': '♋',
            'theme': "Le Retour au Foyer",
            'description': "Vous revenez pour apprendre l'art de la tendresse et du sanctuaire interieur. Les vies passees vous ont fait gravir des sommets ; cette vie vous invite a redescendre dans le coeur.",
            'lecon': "Choisir l'intime avant l'ambition. Honorer vos emotions comme des messagers sacres.",
            'don_cache': "Une intuition emotionnelle profonde. Vous percevez ce que les autres ne disent pas.",
        },
        'Lion': {
            'icon': '♌',
            'theme': "Le Rayonnement Assume",
            'description': "Vous arrivez avec une habitude de l'effacement et du collectif. Cette vie vous invite a oser briller, a creer, a etre vu pour ce que vous etes vraiment.",
            'lecon': "Sortir de l'ombre. Recevoir l'admiration sans la fuir.",
            'don_cache': "Une noblesse naturelle. Vous inspirez les autres par votre simple presence.",
        },
        'Vierge': {
            'icon': '♍',
            'theme': "Le Service Sacre",
            'description': "Votre mission est d'ancrer le reve dans le concret. Vous portez une habitude de la dispersion ou de l'idealisme ; cette vie vous demande de raffiner, servir, perfectionner.",
            'lecon': "Quitter la reverie. Faire les petites choses avec une grande attention.",
            'don_cache': "Un sens du detail qui guerit. Vous savez ce qu'il faut corriger pour que tout tienne.",
        },
        'Balance': {
            'icon': '♎',
            'theme': "Le Pont entre Deux Rives",
            'description': "Cette incarnation vous invite a sortir de l'ego pour decouvrir l'art du partage. Vous portez une habitude de l'autonomie farouche ; cette vie vous propose l'altruisme et l'union.",
            'lecon': "Cesser de tout porter seul. Apprendre a co-creer.",
            'don_cache': "Le sens de la justice et de la beaute. Vous restaurez l'harmonie partout ou vous passez.",
        },
        'Scorpion': {
            'icon': '♏',
            'theme': "La Plongee Initiatique",
            'description': "Vous etes ici pour traverser les seuils interieurs. Les vies passees vous ont rendu confortablement ancre ; cette incarnation vous propose la metamorphose, le mystere, la verite profonde.",
            'lecon': "Quitter le confort. Embrasser ce qui meurt pour faire naitre ce qui veut vivre.",
            'don_cache': "Une force de regeneration. Vous renaissez de chaque chute plus lumineux.",
        },
        'Sagittaire': {
            'icon': '♐',
            'theme': "La Quete du Sens",
            'description': "Cette vie vous appelle a elargir vos horizons : voyages, philosophie, foi. Vous portez une habitude de la dispersion mentale ; cette incarnation vous invite a chercher la verite plutot que les details.",
            'lecon': "Lever les yeux. Faire confiance a la vision plutot qu'au plan.",
            'don_cache': "Un optimisme contagieux. Vous savez ouvrir les portes que les autres croient fermees.",
        },
        'Capricorne': {
            'icon': '♑',
            'theme': "La Construction Royale",
            'description': "Votre mission est de batir une oeuvre solide et durable. Vous arrivez avec une habitude de l'emotion fusionnelle ; cette vie vous propose la maturite, la structure, la responsabilite assumee.",
            'lecon': "Sortir du nid emotionnel. Devenir votre propre autorite.",
            'don_cache': "Une endurance silencieuse. Vous tenez la, quand tous les autres abandonnent.",
        },
        'Verseau': {
            'icon': '♒',
            'theme': "Le Visionnaire au Service du Collectif",
            'description': "Vous etes ici pour servir une cause plus grande que vous. Vous portez une habitude du regne personnel ou de la quete de pouvoir ; cette vie vous invite a la fraternite et a l'innovation.",
            'lecon': "Lacher le tron. Offrir vos dons a la communaute.",
            'don_cache': "Une intuition du futur. Vous voyez ce qui vient avant les autres.",
        },
        'Poissons': {
            'icon': '♓',
            'theme': "Le Lacher Prise Sacre",
            'description': "Cette incarnation vous invite a faire confiance au mystere. Vous portez une habitude de la perfection et du controle ; cette vie vous propose la compassion universelle, l'abandon, la spiritualite vivante.",
            'lecon': "Quitter le perfectionnisme. Vous laisser porter par plus grand que vous.",
            'don_cache': "Un canal d'amour inconditionnel. Vous touchez les ames par simple presence.",
        },
    }

    MISSIONS = {
        'Bélier': "Eveiller votre puissance personnelle et l'incarner sans excuse.",
        'Taureau': "Construire une vie sensorielle, stable et porteuse de paix.",
        'Gémeaux': "Devenir un pont vivant entre les idees et les coeurs.",
        'Cancer': "Creer un refuge emotionnel pour vous et ceux que vous aimez.",
        'Lion': "Rayonner votre creativite avec joie et generosite.",
        'Vierge': "Servir avec precision, soigner par la qualite de votre attention.",
        'Balance': "Restaurer l'harmonie dans vos relations et autour de vous.",
        'Scorpion': "Traverser vos profondeurs et accompagner les autres dans la leur.",
        'Sagittaire': "Transmettre une vision elargie, inspirer la quete de sens.",
        'Capricorne': "Batir une oeuvre solide qui survivra a votre passage.",
        'Verseau': "Innover au service d'un futur plus juste et libre.",
        'Poissons': "Offrir une presence aimante, canaliser le sacre dans le quotidien.",
    }

    MESSAGES_AKASHIQUES = {
        'Bélier': "Ton ame murmure : ose. Ce que tu crains de demander, demande-le. Ce que tu crains d'etre, sois-le.",
        'Taureau': "Ton ame murmure : ralentis. Le tresor que tu cherches est deja dans le simple battement de ton coeur.",
        'Gémeaux': "Ton ame murmure : ecoute. Chaque rencontre est un fragment du livre que tu es venu lire.",
        'Cancer': "Ton ame murmure : reviens chez toi. Le foyer que tu cherches est dans ta poitrine.",
        'Lion': "Ton ame murmure : brille. Tu n'es pas venu te cacher. Le monde a besoin de ta lumiere.",
        'Vierge': "Ton ame murmure : soigne. Chaque geste juste est une priere silencieuse.",
        'Balance': "Ton ame murmure : aime. Et laisse-toi aimer. C'est la meme chose.",
        'Scorpion': "Ton ame murmure : plonge. Sous la peur dort le tresor que tu cherches depuis des vies.",
        'Sagittaire': "Ton ame murmure : leve les yeux. L'horizon t'attend, et il est plus vaste que ta carte.",
        'Capricorne': "Ton ame murmure : batis. Pierre apres pierre, tu construis le temple de ton ame.",
        'Verseau': "Ton ame murmure : libere. La cage que tu vois autour de toi, tu peux l'ouvrir.",
        'Poissons': "Ton ame murmure : abandonne-toi. Le courant qui te porte est plus sage que tes plans.",
    }

    # ── 1) Tentative v3 (positions planetaires precises) ─────────────
    noeud_nord = None
    soleil_signe = None
    lune_signe = None
    source = 'approximatif'
    try:
        from services import astrology_io_service as aio
        bd_v3 = aio.make_birth_data(
            d.year, d.month, d.day, hh, mm,
            city=ville, country_code='FR' if pays.lower() == 'france' else None,
        )
        positions = await aio.get_positions(bd_v3, name=prenom or 'Voyageur', language='fr')
        if positions and isinstance(positions, dict):
            pts = positions.get('points') or positions.get('positions') or positions.get('planets') or []
            for p in (pts if isinstance(pts, list) else []):
                name = (p.get('name') or p.get('point') or '').lower()
                sign_raw = p.get('sign') or (p.get('position') or {}).get('sign') or ''
                sign_fr = signes_fr.get(str(sign_raw).title(), str(sign_raw))
                if 'node' in name and ('north' in name or 'mean' in name or 'true' in name) and not noeud_nord:
                    if 'south' not in name:
                        noeud_nord = sign_fr
                elif name == 'sun' or name == 'soleil':
                    soleil_signe = sign_fr
                elif name == 'moon' or name == 'lune':
                    lune_signe = sign_fr
            if noeud_nord:
                source = 'astrology-api-v3'
    except Exception as e:
        print(f'[karma-destiny] v3 fallback: {e}')

    # ── 2) Tentative AstrologyAPI legacy ─────────────────────────────
    if not noeud_nord:
        try:
            from services.astrology_api import get_astrology_service
            svc = get_astrology_service()
            lat, lon, tz = 48.8566, 2.3522, 1.0
            try:
                geo = await svc.get_geo_details(f"{ville}, {pays}" if pays else ville)
                if geo and isinstance(geo, list) and len(geo) > 0:
                    g = geo[0]
                    lat = float(g.get('latitude', lat))
                    lon = float(g.get('longitude', lon))
                    tz = float(g.get('timezone_offset', tz)) if g.get('timezone_offset') else tz
            except Exception:
                pass
            wh = await svc.get_western_horoscope(date_naissance, heure, lat, lon, tz)
            if wh and isinstance(wh, dict):
                for p in wh.get('planets', []):
                    if p.get('name') == 'Node':
                        noeud_nord = signes_fr.get(p.get('sign'))
                        source = 'astrologyapi'
                    elif p.get('name') == 'Sun' and not soleil_signe:
                        soleil_signe = signes_fr.get(p.get('sign'))
                    elif p.get('name') == 'Moon' and not lune_signe:
                        lune_signe = signes_fr.get(p.get('sign'))
        except Exception as e:
            print(f'[karma-destiny] legacy fallback: {e}')

    # ── 3) Fallback approximatif si tout echoue ──────────────────────
    if not noeud_nord:
        ref = _dt(2000, 1, 1)
        years_diff = (d - ref).days / 365.25
        signe_idx = int((3 - (years_diff / (18.6 / 12)))) % 12
        noeud_nord = signes_ordre[signe_idx]

    nn_idx = signes_ordre.index(noeud_nord)
    noeud_sud = signes_ordre[(nn_idx + 6) % 12]

    # Nombre karmique : reduction des chiffres de la date jusqu'a 1 chiffre (maitres 11/22/33 preserves)
    def reduce_nb(n: int) -> int:
        while n > 9 and n not in (11, 22, 33):
            n = sum(int(c) for c in str(n))
        return n
    raw = sum(int(c) for c in date_naissance.replace('-', ''))
    nombre_karmique = reduce_nb(raw)

    karma_principal = KARMA_PROFILES.get(noeud_nord, KARMA_PROFILES['Bélier'])
    karma_sud = KARMA_PROFILES.get(noeud_sud, {})

    return {
        'success': True,
        'data': {
            'prenom': prenom,
            'date_naissance': date_naissance,
            'heure_naissance': heure,
            'lieu_naissance': f"{ville}, {pays}" if pays else ville,
            'source_calcul': source,
            'nombre_karmique': nombre_karmique,
            'karma_principal': karma_principal,
            'mission_de_vie': {
                'mission': MISSIONS.get(noeud_nord, ''),
                'description': karma_principal.get('description', ''),
            },
            'noeuds_lunaires': {
                'noeud_nord': noeud_nord,
                'noeud_sud': noeud_sud,
                'message': (
                    f"Votre Noeud Nord en {noeud_nord} indique la direction d'evolution de votre ame. "
                    f"Votre Noeud Sud en {noeud_sud} represente la zone de confort herite des vies passees : "
                    f"{(karma_sud.get('description') or '').split('.')[0]}."
                ),
            },
            'message_akashique': MESSAGES_AKASHIQUES.get(noeud_nord, ''),
            'axe_evolution': f"{noeud_sud} → {noeud_nord}",
            # legacy fields preserved pour retro-compat
            'noeud_nord': {
                'signe': noeud_nord,
                'mission': MISSIONS.get(noeud_nord, ''),
            },
            'noeud_sud': {
                'signe': noeud_sud,
                'memoire': KARMA_PROFILES.get(noeud_sud, {}).get('description', ''),
            },
            'lecon_karmique': karma_principal.get('lecon', ''),
            # bonus pour le panel "Carte natale"
            'soleil_signe': soleil_signe,
            'lune_signe': lune_signe,
        },
    }


@api_router.post('/astrology/natal-chart')
async def astrology_natal_chart(request: Request):
    """Wrapper vers AstrologyAPI pour le theme natal complet (legacy + fallback v3).
    Le frontend Karma & Destin l'appelle pour enrichir le rapport."""
    body = await request.json()
    try:
        from services.astrology_api import get_astrology_service
        svc = get_astrology_service()
        day = int(body.get('day', 1)); month = int(body.get('month', 1)); year = int(body.get('year', 2000))
        hour = int(body.get('hour', 12)); minute = int(body.get('min', 0))
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"
        data = await svc.get_western_horoscope(
            date_str, time_str,
            body.get('lat', 48.8566), body.get('lon', 2.3522), body.get('tzone', 1),
        )
        if data:
            return {'success': True, 'data': data, 'source': 'astrologyapi'}
    except Exception as e:
        logger.warning(f'natal-chart legacy failed, trying v3: {e}')

    # Fallback v3
    try:
        from services import astrology_io_service as aio
        bd = aio.make_birth_data(
            int(body.get('year', 2000)), int(body.get('month', 1)), int(body.get('day', 1)),
            int(body.get('hour', 12)), int(body.get('min', 0)),
            latitude=body.get('lat'), longitude=body.get('lon'),
        )
        chart = await aio.natal_chart(bd, name=body.get('name', 'Voyageur'), language='fr')
        if chart:
            return {'success': True, 'data': chart, 'source': 'v3'}
    except Exception as e:
        return {'success': False, 'message': str(e)[:120]}
    return {'success': False, 'message': 'Astrology API indisponible'}


# ═══════════════════════════════════════════════════
# HOROSCOPE — astrology-api.io v3 (texte enrichi FR)
# ═══════════════════════════════════════════════════
class HoroscopeRequest(BaseModel):
    day: int | None = None
    month: int | None = None
    year: int | None = None
    hour: int | None = 12
    min: int | None = 0
    lat: float | None = 48.8566
    lon: float | None = 2.3522
    tzone: float | None = 1.0
    period: str = 'daily'  # daily | weekly | monthly | yearly
    sign: str | None = None  # fallback si pas de birth data


@api_router.post('/astrology/horoscope-prediction')
async def horoscope_prediction(payload: HoroscopeRequest):
    """Horoscope personnalise via astrology-api.io v3.
    Si birth data complete -> appel /horoscope/personal/{period} (richement personnalise).
    Sinon -> fallback /horoscope/sign/{period} avec le signe."""
    from services import astrology_io_service as aio

    period = payload.period if payload.period in {'daily', 'weekly', 'monthly', 'yearly'} else 'daily'

    # Si on a birth_date complete -> personalize
    has_birth = bool(payload.day and payload.month and payload.year)
    if has_birth:
        bd = aio.make_birth_data(
            payload.year, payload.month, payload.day,
            payload.hour or 12, payload.min or 0,
            latitude=payload.lat, longitude=payload.lon,
        )
        cache_key = aio._cache_key('personal', payload.year, payload.month, payload.day,
                                   payload.hour, payload.min, payload.lat, payload.lon, period)
        data = await aio.get_cached_or_fetch(
            cache_key,
            lambda: aio.horoscope_personal(bd, period, 'fr'),
        )
        if data:
            return {'success': True, 'data': data, 'source': 'personal'}

    # Fallback : signe seulement
    sign = payload.sign
    if not sign and has_birth:
        # Deduce sign from birth date
        from datetime import date as _date
        signs_dates = [
            (((3, 21), (4, 19)), 'aries'), (((4, 20), (5, 20)), 'taurus'),
            (((5, 21), (6, 20)), 'gemini'), (((6, 21), (7, 22)), 'cancer'),
            (((7, 23), (8, 22)), 'leo'), (((8, 23), (9, 22)), 'virgo'),
            (((9, 23), (10, 22)), 'libra'), (((10, 23), (11, 21)), 'scorpio'),
            (((11, 22), (12, 21)), 'sagittarius'), (((12, 22), (1, 19)), 'capricorn'),
            (((1, 20), (2, 18)), 'aquarius'), (((2, 19), (3, 20)), 'pisces'),
        ]
        m, d = payload.month, payload.day
        for ((sm, sd), (em, ed)), s in signs_dates:
            if (m == sm and d >= sd) or (m == em and d <= ed) or sm > em and (m == sm and d >= sd or m == em and d <= ed):
                sign = s; break
        if not sign:
            sign = 'aries'

    cache_key = aio._cache_key('sign', sign, period)
    data = await aio.get_cached_or_fetch(
        cache_key,
        lambda: aio.horoscope_sign(sign or 'aries', period, 'fr'),
    )
    if data:
        return {'success': True, 'data': data, 'source': 'sign'}
    return {'success': False, 'message': 'Horoscope indisponible (API)'}


@api_router.get('/tarot/jour')
async def get_jour():
    return {'success': True, 'data': tirage_du_jour()}


class OracleQuestionRequest(BaseModel):
    question: str


@api_router.post('/oracle')
async def legacy_oracle_question(payload: OracleQuestionRequest):
    question = (payload.question or '').strip()
    if not question:
        raise HTTPException(status_code=400, detail='question requise')
    reading = tirage_oui_non(question)
    return {
        'success': True,
        'answer': reading.get('reponse'),
        'data': reading,
    }


@api_router.get('/tarot/predictions')
async def tarot_predictions():
    prompts = [
        "Quel est le message du jour en amour ?",
        "Quel est le message du jour pour ma vie pro ?",
        "Quel est le conseil du jour pour mon energie ?",
    ]
    predictions = []
    for prompt in prompts:
        reading = tirage_oui_non(prompt)
        predictions.append({
            'theme': prompt,
            'carte': reading.get('carte'),
            'message': reading.get('reponse'),
        })
    return {'success': True, 'predictions': predictions}


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


@api_router.post('/astro-chat')
async def legacy_astro_chat_alias(request: Request):
    """Legacy alias used by older OracleChat component.
    Delegates to plume-chat and keeps response shape with `answer`."""
    result = await plume_chat_endpoint(request, current_user=None)
    return {
        'success': bool(result.get('success')),
        'answer': result.get('answer') or result.get('message') or '',
        **result,
    }


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
    checkin = await get_today_checkin(user_id)
    mood = checkin.get('mood') if checkin else None
    scores_data = get_today_scores(user_id, mood=mood)
    insight_data = await get_daily_insight(user_id, birth_data=birth_data, mood=mood)
    streak = await get_streak(user_id)
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
    result = await submit_checkin(user_id, mood, intention)
    streak = await update_streak(user_id)
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
    result = await journal_entry(user_id, entry, mood=body.get('mood'), birth_data=body.get('birth_data'))
    return result


@api_router.get('/journal/history')
async def journal_history_endpoint(user_id: str, limit: int = 30):
    history = await get_journal_history(user_id, limit=limit)
    return {'success': True, 'entries': history}


# ════════════════════════════════════════════
# FINAL APP CONFIG
# ════════════════════════════════════════════
app.include_router(api_router)

# Build CORS origins list: env var + production domains always whitelisted
_cors_from_env = [o.strip() for o in os.environ.get('CORS_ORIGINS', '').split(',') if o.strip()]
_default_origins = [
    'https://plume-astrale.fr',
    'https://www.plume-astrale.fr',
    'https://consultation-astro.preview.emergentagent.com',
    'https://consultation-astro.emergent.host',
]
_allow_origins = list(set(_cors_from_env + _default_origins)) if _cors_from_env else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=_allow_origins,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'plume-astrale'}


@app.get('/api/health')
async def api_health_check():
    """Mirror of /health under /api for Kubernetes ingress probes."""
    return {'status': 'healthy', 'service': 'plume-astrale'}


if ASSETS_DIR.exists():
    app.mount('/api/assets', StaticFiles(directory=str(ASSETS_DIR)), name='assets')
