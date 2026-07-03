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
from routes.astrology_v3 import router as astrology_v3_router
from routes.oracle import router as oracle_router
from routes.cercle import router as cercle_router
from routes.synastrie import router as synastrie_router
from routes.library import router as library_router

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
api_router.include_router(astrology_v3_router)
api_router.include_router(oracle_router)
api_router.include_router(cercle_router)
api_router.include_router(synastrie_router)
api_router.include_router(library_router)


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
            'premium_until': profile.get('premium_until'),
            'created_at': profile.get('created_at'),
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
