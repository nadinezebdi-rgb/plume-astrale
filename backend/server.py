from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
from integrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from services.astrology_api import get_astrology_service, AstrologyAPIService
from services.astrology_api_premium import get_premium_astrology_service, AstrologyAPIPremium
from services.pdf_generator_v2 import generate_manuscrit_complet
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_mediumnite_complet, tirage_en_croix
from services.mediumnite_pdf import generate_mediumnite_pdf
from services.astrology_pdf_api import generate_pro_horoscope_pdf, generate_match_making_pdf
from services.share_card_generator import generate_share_card
from services.translation_service import translate_to_french, translate_dict_values
from services.auth_service import hash_password, verify_password, create_token, get_current_user
from services.wallet_service import (
    create_wallet, get_wallet, deduct_credits, add_credits,
    get_transactions, check_free_tarot_used, mark_free_tarot_used
)
from services.streak_service import get_streak, do_checkin


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Static assets dir
ASSETS_DIR = Path(__file__).parent / "assets"

# Stripe configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Fixed product packages - prices defined server-side only
PRODUCTS = {
    "manuscrit": {
        "name": "Thème Astral Professionnel",
        "amount": 29.90,
        "currency": "eur",
        "description": "Votre thème astral professionnel complet - 28+ pages enrichies (PDF)"
    },
    "chemin_ame": {
        "name": "Le Chemin d'Âme",
        "amount": 24.90,
        "currency": "eur",
        "description": "Votre chemin d'âme personnalisé - Numérologie, prévisions et guidance (PDF)"
    },
    "livre": {
        "name": "Le Livre de la Plume",
        "amount": 49.90,
        "currency": "eur",
        "description": "Votre manuscrit imprimé en livre relié - Livraison sous 5 jours",
        "requires_address": True,
        "delivery_days": 5
    },
    "tarot_oui_non": {
        "name": "Tarot Oui/Non",
        "amount": 4.99,
        "currency": "eur",
        "description": "Tirage d'un Arcane Majeur pour répondre à votre question"
    },
    "tarologie_mediumnite": {
        "name": "Tarologie & Médiumnité",
        "amount": 35.00,
        "currency": "eur",
        "description": "Tirage complet 7 cartes + lecture médiumnique en PDF"
    },
    "compatibilite": {
        "name": "Compatibilité Astrale",
        "amount": 29.90,
        "currency": "eur",
        "description": "Analyse de compatibilité amoureuse complète - 24 pages (PDF)"
    },
    "premium": {
        "name": "Expérience Premium",
        "amount": 199.00,
        "currency": "eur",
        "description": "Cartographie céleste complète - Parcours guidé en 5 étapes + PDF Premium"
    },
    # ═══ NOUVEAUX PRODUITS PREMIUM ═══
    "amour_premium": {
        "name": "Analyse Amour Premium",
        "amount": 49.00,
        "currency": "eur",
        "description": "Analyse complète de compatibilité amoureuse - Synastrie, profil romantique et guidance"
    },
    "cercle_mensuel": {
        "name": "Le Cercle - Abonnement Mensuel",
        "amount": 14.90,
        "currency": "eur",
        "description": "Accès quotidien: Tarot, Lune, Horoscope Premium - Contenu personnalisé chaque jour",
        "subscription": True,
        "interval": "month"
    },
    "profil_complet": {
        "name": "Profil Astro-Numérologique Complet",
        "amount": 39.00,
        "currency": "eur",
        "description": "Karma, Destinée, Personnalité + Numérologie complète en PDF Premium"
    },
    "numerologie_complete": {
        "name": "Numérologie Complète",
        "amount": 49.00,
        "currency": "eur",
        "description": "Analyse numérologique approfondie - Chemin de vie, Nombre d'âme, Expression, Défis et Cycles personnels"
    },
    "horoscope_premium": {
        "name": "Horoscope Premium Annuel",
        "amount": 69.00,
        "currency": "eur",
        "description": "Prévisions astrologiques détaillées - 12 mois complets avec transits et conseils personnalisés"
    },
    "tarot_marseille": {
        "name": "Tirage Tarot de Marseille",
        "amount": 19.00,
        "currency": "eur",
        "description": "Tirage personnalisé avec votre question - Interprétation complète des Arcanes Majeurs"
    },
    "tarot_celtique": {
        "name": "Tirage Croix Celtique",
        "amount": 29.00,
        "currency": "eur",
        "description": "Tirage complet 10 cartes - Analyse approfondie de votre situation avec guidance détaillée"
    }
}

# Discount codes - defined server-side only for security
DISCOUNT_CODES = {
    "ASTRO100": {
        "discount_percent": 100,
        "description": "Acces gratuit complet",
        "products": ["manuscrit"]
    },
    "PLUME2026": {
        "discount_percent": 100,
        "description": "Acces gratuit a tous les services",
        "products": "all"
    }
}

# Credit promo codes
CREDIT_PROMO_CODES = {
    "PLUMEASTRALE": {"credits": 100, "description": "100 crédits offerts", "max_uses_per_user": 1},
    "TESTPLUME": {"credits": 200, "description": "200 crédits de test", "max_uses_per_user": 1},
    "BIENVENUE": {"credits": 50, "description": "50 crédits de bienvenue", "max_uses_per_user": 1},
}

# ═══ CREDIT PACKS ═══
CREDIT_PACKS = {
    "decouverte": {
        "name": "Pack Découverte",
        "credits": 10,
        "amount": 9.00,
        "currency": "eur",
        "description": "10 crédits pour explorer nos services",
    },
    "exploration": {
        "name": "Pack Exploration",
        "credits": 50,
        "amount": 24.99,
        "currency": "eur",
        "description": "50 crédits — notre meilleur rapport qualité-prix",
    },
    "premium": {
        "name": "Pack Premium",
        "credits": 100,
        "amount": 44.99,
        "currency": "eur",
        "description": "100 crédits pour un accès complet",
    },
}

# Service costs in credits
SERVICE_COSTS = {
    "tarot_oui_non": 2,
    "lecture_tarot": 10,
    "lecture_astrologique": 10,
    "numerologie": 10,
    "cartographie_premium": 60,
}

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Auth Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    birth_date: str          # YYYY-MM-DD
    birth_time: str          # HH:MM (24h)
    birth_place: str
    birth_country: str = "France"

class LoginRequest(BaseModel):
    email: str
    password: str

class CreditCheckoutRequest(BaseModel):
    pack_id: str
    origin_url: str

# Payment Models
class CheckoutRequest(BaseModel):
    product_id: str
    origin_url: str
    user_email: Optional[str] = None
    user_data: Optional[Dict] = None
    discount_code: Optional[str] = None
    shipping_address: Optional[Dict] = None

class DiscountValidationRequest(BaseModel):
    code: str

class DiscountValidationResponse(BaseModel):
    valid: bool
    discount_percent: Optional[int] = None
    message: str

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    product_id: str
    product_name: str
    amount: float
    currency: str
    user_email: Optional[str] = None
    user_data: Optional[Dict] = None
    payment_status: str = "pending"
    status: str = "initiated"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# ========== AUTH ROUTES ==========

@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    """Register a new user with astrological profile + 20 bonus credits."""
    email = req.email.strip().lower()
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(req.password),
        "birth_date": req.birth_date,
        "birth_time": req.birth_time,
        "birth_place": req.birth_place,
        "birth_country": req.birth_country,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user_doc)
    wallet = await create_wallet(db, user_id)
    token = create_token(user_id, email)
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": email,
            "birth_date": req.birth_date,
            "birth_time": req.birth_time,
            "birth_place": req.birth_place,
            "birth_country": req.birth_country,
        },
        "credit_balance": wallet["credit_balance"],
    }

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    """Login and return JWT + credit balance."""
    email = req.email.strip().lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_token(user["id"], email)
    wallet = await get_wallet(db, user["id"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "birth_date": user.get("birth_date"),
            "birth_time": user.get("birth_time"),
            "birth_place": user.get("birth_place"),
            "birth_country": user.get("birth_country"),
        },
        "credit_balance": wallet["credit_balance"] if wallet else 0,
    }

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current user profile + credit balance."""
    user = await get_current_user(request, db)
    wallet = await get_wallet(db, user["id"])
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "birth_date": user.get("birth_date"),
            "birth_time": user.get("birth_time"),
            "birth_place": user.get("birth_place"),
            "birth_country": user.get("birth_country"),
        },
        "credit_balance": wallet["credit_balance"] if wallet else 0,
    }

# ========== WALLET & CREDITS ROUTES ==========

@api_router.get("/wallet/balance")
async def wallet_balance(request: Request):
    """Get current credit balance."""
    user = await get_current_user(request, db)
    wallet = await get_wallet(db, user["id"])
    return {"credit_balance": wallet["credit_balance"] if wallet else 0}

@api_router.get("/wallet/transactions")
async def wallet_transactions(request: Request):
    """Get credit transaction history."""
    user = await get_current_user(request, db)
    txs = await get_transactions(db, user["id"])
    return {"transactions": txs}

@api_router.get("/credits/packs")
async def get_credit_packs():
    """Return available credit packs (public)."""
    packs = []
    for pack_id, pack in CREDIT_PACKS.items():
        packs.append({
            "id": pack_id,
            "name": pack["name"],
            "credits": pack["credits"],
            "amount": pack["amount"],
            "currency": pack["currency"],
            "description": pack["description"],
        })
    return {"packs": packs}

@api_router.get("/credits/service-costs")
async def get_service_costs():
    """Return service credit costs (public)."""
    return {"costs": SERVICE_COSTS}

@api_router.post("/credits/checkout")
async def create_credit_checkout(req: CreditCheckoutRequest, request: Request):
    """Create Stripe checkout session for a credit pack. Requires auth."""
    user = await get_current_user(request, db)

    if req.pack_id not in CREDIT_PACKS:
        raise HTTPException(status_code=400, detail="Pack invalide")

    pack = CREDIT_PACKS[req.pack_id]
    success_url = f"{req.origin_url}/credits/succes?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{req.origin_url}/acheter-credits"

    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

    checkout_request = CheckoutSessionRequest(
        amount=pack["amount"],
        currency=pack["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "type": "credit_purchase",
            "pack_id": req.pack_id,
            "credits": str(pack["credits"]),
            "user_id": user["id"],
            "user_email": user["email"],
        },
    )

    session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)

    # Record pending payment transaction
    tx_doc = {
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "type": "credit_purchase",
        "pack_id": req.pack_id,
        "pack_name": pack["name"],
        "credits": pack["credits"],
        "amount": pack["amount"],
        "currency": pack["currency"],
        "user_id": user["id"],
        "user_email": user["email"],
        "payment_status": "pending",
        "status": "initiated",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.payment_transactions.insert_one(tx_doc)

    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/credits/checkout/status/{session_id}")
async def credit_checkout_status(session_id: str, request: Request):
    """Poll credit checkout status and add credits if paid."""
    user = await get_current_user(request, db)

    existing = await db.payment_transactions.find_one(
        {"session_id": session_id, "type": "credit_purchase"}, {"_id": 0}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction introuvable")

    # Already processed — return immediately
    if existing.get("payment_status") == "paid":
        wallet = await get_wallet(db, user["id"])
        return {
            "status": "complete",
            "payment_status": "paid",
            "already_processed": True,
            "credit_balance": wallet["credit_balance"] if wallet else 0,
        }

    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)

    if status.payment_status == "paid":
        # Idempotent: check again to avoid double-credit
        recheck = await db.payment_transactions.find_one(
            {"session_id": session_id, "type": "credit_purchase"}, {"_id": 0}
        )
        if recheck and recheck.get("payment_status") != "paid":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"payment_status": "paid", "status": "complete",
                           "updated_at": datetime.now(timezone.utc).isoformat()}},
            )
            credits_to_add = existing.get("credits", 0)
            await add_credits(db, user["id"], credits_to_add,
                              f"Achat {existing.get('pack_name', '')} ({credits_to_add} crédits)")

    wallet = await get_wallet(db, user["id"])
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "credit_balance": wallet["credit_balance"] if wallet else 0,
    }

@api_router.post("/credits/use")
async def use_credits(request: Request):
    """Deduct credits for a service. Body: {service_id: str}"""
    user = await get_current_user(request, db)
    body = await request.json()
    service_id = body.get("service_id")

    if service_id not in SERVICE_COSTS:
        raise HTTPException(status_code=400, detail="Service inconnu")

    # Special case: Tarot Oui/Non first draw is free
    if service_id == "tarot_oui_non":
        free_used = await check_free_tarot_used(db, user["id"])
        if not free_used:
            await mark_free_tarot_used(db, user["id"])
            wallet = await get_wallet(db, user["id"])
            return {"success": True, "free_draw": True, "credit_balance": wallet["credit_balance"]}

    cost = SERVICE_COSTS[service_id]
    try:
        result = await deduct_credits(db, user["id"], cost,
                                       f"Service: {service_id} ({cost} crédits)")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    return {"success": True, "free_draw": False, "credit_balance": result["credit_balance"]}

@api_router.get("/credits/check-free-tarot")
async def check_free_tarot(request: Request):
    """Check if user has used their free Tarot Oui/Non draw."""
    user = await get_current_user(request, db)
    used = await check_free_tarot_used(db, user["id"])
    return {"free_used": used}

@api_router.post("/credits/promo")
async def apply_promo_code(request: Request):
    """Apply a promo code to get free credits."""
    user = await get_current_user(request, db)
    body = await request.json()
    code = (body.get("code") or "").strip().upper()

    if code not in CREDIT_PROMO_CODES:
        raise HTTPException(status_code=400, detail="Code promo invalide")

    promo = CREDIT_PROMO_CODES[code]

    # Check if already used by this user
    existing = await db.credit_transactions.find_one(
        {"user_id": user["id"], "description": {"$regex": f"Promo: {code}"}},
        {"_id": 0},
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ce code a déjà été utilisé sur votre compte")

    result = await add_credits(db, user["id"], promo["credits"], f"Promo: {code} — {promo['description']}")
    return {
        "success": True,
        "credits_added": promo["credits"],
        "description": promo["description"],
        "credit_balance": result["credit_balance"],
    }

# ========== STREAK ROUTES ==========

@api_router.get("/streak/status")
async def streak_status(request: Request):
    """Get current streak info."""
    user = await get_current_user(request, db)
    streak = await get_streak(db, user["id"])
    return streak

@api_router.post("/streak/checkin")
async def streak_checkin(request: Request):
    """Perform daily check-in, earn credits + streak bonus."""
    user = await get_current_user(request, db)
    result = await do_checkin(db, user["id"])

    # Add earned credits to wallet
    if not result["already_checked_in"] and result["credits_earned"] > 0:
        desc = f"Check-in jour {result['streak_count']}"
        if result["milestone_name"]:
            desc += f" + {result['milestone_name']} (+{result['milestone_bonus']} bonus)"
        await add_credits(db, user["id"], result["credits_earned"], desc)

    wallet = await get_wallet(db, user["id"])
    return {
        **result,
        "credit_balance": wallet["credit_balance"] if wallet else 0,
    }

# ========== STRIPE PAYMENT ROUTES ==========

@api_router.post("/checkout/create")
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    """Create a Stripe checkout session for the Manuscrit de la Plume"""
    
    # Validate product exists
    if request.product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Produit invalide")
    
    product = PRODUCTS[request.product_id]
    
    # Build URLs from provided origin (NEVER hardcode)
    success_url = f"{request.origin_url}/paiement/succes?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.origin_url}/apercu"
    
    # Initialize Stripe
    host_url = str(http_request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session with fixed price from server
    checkout_request = CheckoutSessionRequest(
        amount=product["amount"],
        currency=product["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product_id": request.product_id,
            "product_name": product["name"],
            "user_email": request.user_email or ""
        }
    )
    
    try:
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record BEFORE redirect
        transaction = PaymentTransaction(
            session_id=session.session_id,
            product_id=request.product_id,
            product_name=product["name"],
            amount=product["amount"],
            currency=product["currency"],
            user_email=request.user_email,
            user_data=request.user_data,
            payment_status="pending",
            status="initiated"
        )
        
        doc = transaction.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        
        await db.payment_transactions.insert_one(doc)
        
        logger.info(f"Checkout session created: {session.session_id}")
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du paiement: {str(e)}")

@api_router.get("/checkout/status/{session_id}")
async def get_checkout_status(session_id: str, http_request: Request):
    """Get the status of a checkout session and update the transaction"""
    
    # Check if already processed
    existing = await db.payment_transactions.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )
    
    if existing and existing.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "already_processed": True
        }
    
    # Initialize Stripe
    host_url = str(http_request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        update_data = {
            "payment_status": status.payment_status,
            "status": status.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        # If payment successful, mark user as paid in their data
        if status.payment_status == "paid" and existing:
            logger.info(f"Payment successful for session: {session_id}")
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
        
    except Exception as e:
        logger.error(f"Error checking checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification du paiement: {str(e)}")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": "paid",
                    "status": "complete",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"Webhook: Payment confirmed for session {webhook_response.session_id}")
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"received": True}

@api_router.get("/products")
async def get_products():
    """Get available products"""
    return PRODUCTS

@api_router.post("/discount/validate", response_model=DiscountValidationResponse)
async def validate_discount_code(request: DiscountValidationRequest):
    """Validate a discount code"""
    code = request.code.upper().strip()
    
    if code in DISCOUNT_CODES:
        discount = DISCOUNT_CODES[code]
        return DiscountValidationResponse(
            valid=True,
            discount_percent=discount["discount_percent"],
            message=discount["description"]
        )
    
    return DiscountValidationResponse(
        valid=False,
        discount_percent=None,
        message="Code de réduction invalide"
    )

@api_router.post("/access/free")
async def grant_free_access(request: CheckoutRequest):
    """Grant free access with a 100% discount code"""
    
    # Validate discount code
    if not request.discount_code:
        raise HTTPException(status_code=400, detail="Code de réduction requis")
    
    code = request.discount_code.upper().strip()
    
    if code not in DISCOUNT_CODES:
        raise HTTPException(status_code=400, detail="Code de réduction invalide")
    
    discount = DISCOUNT_CODES[code]
    
    if discount["discount_percent"] != 100:
        raise HTTPException(status_code=400, detail="Ce code ne donne pas un accès gratuit")
    
    # Check if code is valid for this product
    allowed_products = discount.get("products", "all")
    if allowed_products != "all" and request.product_id not in allowed_products:
        raise HTTPException(status_code=400, detail="Ce code n'est pas valide pour ce produit")
    
    # Validate product
    if request.product_id not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Produit invalide")
    
    product = PRODUCTS[request.product_id]
    
    # Create a free transaction record
    transaction = PaymentTransaction(
        session_id=f"free_{str(uuid.uuid4())}",
        product_id=request.product_id,
        product_name=product["name"],
        amount=0.0,
        currency=product["currency"],
        user_email=request.user_email,
        user_data=request.user_data,
        payment_status="paid",
        status="complete"
    )
    
    doc = transaction.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    doc['discount_code'] = code
    
    await db.payment_transactions.insert_one(doc)
    
    logger.info(f"Free access granted with code {code} for {request.user_email}")
    
    return {
        "success": True,
        "message": "Accès gratuit accordé",
        "redirect_url": f"{request.origin_url}/paiement/succes?session_id={transaction.session_id}"
    }

# ========== ASTROLOGY API ROUTES ==========

class AstrologyRequest(BaseModel):
    date_naissance: str  # Format: YYYY-MM-DD
    heure_naissance: str  # Format: HH:MM
    ville: Optional[str] = "Paris"
    pays: Optional[str] = "France"

class HoroscopeRequest(BaseModel):
    zodiac_sign: str

@api_router.post("/astrology/horoscope")
async def get_western_horoscope(request: AstrologyRequest):
    """Get complete western horoscope data"""
    try:
        service = get_astrology_service()
        
        # Get geo details for the city (default to Paris coordinates)
        lat, lon, tz = 48.8566, 2.3522, 1.0
        
        if request.ville:
            geo_data = await service.get_geo_details(f"{request.ville}, {request.pays}")
            if geo_data and len(geo_data) > 0:
                place = geo_data[0] if isinstance(geo_data, list) else geo_data.get('geonames', [{}])[0]
                lat = float(place.get('latitude', lat))
                lon = float(place.get('longitude', lon))
                tz = float(place.get('timezone', tz))
        
        # Get western horoscope
        horoscope_data = await service.get_western_horoscope(
            request.date_naissance,
            request.heure_naissance,
            lat, lon, tz
        )
        
        if not horoscope_data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer les données astrologiques")
        
        # Also get the zodiac sign
        zodiac_sign = service.get_zodiac_sign_from_date(request.date_naissance)
        zodiac_french = service.get_zodiac_french_name(zodiac_sign)
        
        return {
            "success": True,
            "zodiac_sign": zodiac_sign,
            "zodiac_french": zodiac_french,
            "data": horoscope_data
        }
        
    except Exception as e:
        logger.error(f"Astrology API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.post("/astrology/planets")
async def get_planets(request: AstrologyRequest):
    """Get tropical planet positions"""
    try:
        service = get_astrology_service()
        
        lat, lon, tz = 48.8566, 2.3522, 1.0
        
        if request.ville:
            geo_data = await service.get_geo_details(f"{request.ville}, {request.pays}")
            if geo_data and len(geo_data) > 0:
                place = geo_data[0] if isinstance(geo_data, list) else geo_data.get('geonames', [{}])[0]
                lat = float(place.get('latitude', lat))
                lon = float(place.get('longitude', lon))
                tz = float(place.get('timezone', tz))
        
        planets_data = await service.get_planets_tropical(
            request.date_naissance,
            request.heure_naissance,
            lat, lon, tz
        )
        
        if not planets_data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer les positions planétaires")
        
        return {
            "success": True,
            "data": planets_data
        }
        
    except Exception as e:
        logger.error(f"Planets API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.get("/astrology/daily/{zodiac_sign}")
async def get_daily_horoscope(zodiac_sign: str):
    """Get daily horoscope for a zodiac sign"""
    try:
        service = get_astrology_service()
        
        data = await service.get_daily_horoscope(zodiac_sign)
        
        if not data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer l'horoscope du jour")
        
        return {
            "success": True,
            "zodiac_sign": zodiac_sign,
            "zodiac_french": service.get_zodiac_french_name(zodiac_sign),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Daily horoscope error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.get("/astrology/weekly/{zodiac_sign}")
async def get_weekly_horoscope(zodiac_sign: str):
    """Get weekly horoscope for a zodiac sign"""
    try:
        service = get_astrology_service()
        
        data = await service.get_weekly_horoscope(zodiac_sign)
        
        if not data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer l'horoscope de la semaine")
        
        return {
            "success": True,
            "zodiac_sign": zodiac_sign,
            "zodiac_french": service.get_zodiac_french_name(zodiac_sign),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Weekly horoscope error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.get("/astrology/monthly/{zodiac_sign}")
async def get_monthly_horoscope(zodiac_sign: str):
    """Get monthly horoscope for a zodiac sign"""
    try:
        service = get_astrology_service()
        
        data = await service.get_monthly_horoscope(zodiac_sign)
        
        if not data:
            raise HTTPException(status_code=500, detail="Impossible de récupérer l'horoscope du mois")
        
        return {
            "success": True,
            "zodiac_sign": zodiac_sign,
            "zodiac_french": service.get_zodiac_french_name(zodiac_sign),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Monthly horoscope error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.get("/astrology/zodiac/{date}")
async def get_zodiac_from_date(date: str):
    """Get zodiac sign from a birth date (format: YYYY-MM-DD)"""
    try:
        service = get_astrology_service()
        zodiac_sign = service.get_zodiac_sign_from_date(date)
        
        return {
            "success": True,
            "date": date,
            "zodiac_sign": zodiac_sign,
            "zodiac_french": service.get_zodiac_french_name(zodiac_sign)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Format de date invalide: {str(e)}")

# ========== PDF GENERATION ROUTES ==========

from fastapi.responses import Response

class PDFRequest(BaseModel):
    user_data: Dict
    
class BookOrderRequest(BaseModel):
    product_id: str = "livre"
    origin_url: str
    user_email: str
    user_data: Dict
    shipping_address: Dict  # Required for book orders

@api_router.post("/pdf/generate")
async def generate_pdf(request: PDFRequest):
    """Generate PDF manuscript"""
    try:
        user_data = request.user_data
        
        # Get astrology data if possible
        planets_data = None
        horoscope_data = None
        chart_svg_url = None
        
        if user_data.get('dateNaissance') and user_data.get('heureNaissance'):
            try:
                service = get_astrology_service()
                
                lat, lon, tz = 48.8566, 2.3522, 1.0
                if user_data.get('ville'):
                    geo_data = await service.get_geo_details(f"{user_data['ville']}")
                    if geo_data and len(geo_data) > 0:
                        place = geo_data[0]
                        lat = float(place.get('latitude', lat))
                        lon = float(place.get('longitude', lon))
                
                planets_data = await service.get_planets_tropical(
                    user_data['dateNaissance'],
                    user_data['heureNaissance'],
                    lat, lon, tz
                )
                
                horoscope_data = await service.get_western_horoscope(
                    user_data['dateNaissance'],
                    user_data['heureNaissance'],
                    lat, lon, tz
                )
                
                chart_svg_url = await service.get_natal_wheel_chart(
                    user_data['dateNaissance'],
                    user_data['heureNaissance'],
                    lat, lon, tz
                )
            except Exception as e:
                logger.warning(f"Could not fetch astrology data: {e}")
        
        # Generate PDF
        pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data, chart_svg_url=chart_svg_url)
        
        # Return PDF as downloadable file
        filename = f"manuscrit_plume_{user_data.get('prenom', 'celestial')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du PDF: {str(e)}")

@api_router.post("/order/book")
async def order_physical_book(request: BookOrderRequest, http_request: Request):
    """Create order for physical book with shipping address"""
    
    # Validate shipping address
    required_fields = ['name', 'street', 'city', 'postal_code', 'country']
    for field in required_fields:
        if not request.shipping_address.get(field):
            raise HTTPException(status_code=400, detail=f"Champ obligatoire manquant: {field}")
    
    product = PRODUCTS.get("livre")
    if not product:
        raise HTTPException(status_code=400, detail="Produit livre non trouvé")
    
    # Build URLs
    success_url = f"{request.origin_url}/commande/succes?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.origin_url}/livre"
    
    # Initialize Stripe
    host_url = str(http_request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    checkout_request = CheckoutSessionRequest(
        amount=product["amount"],
        currency=product["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product_id": "livre",
            "product_name": product["name"],
            "user_email": request.user_email,
            "delivery_days": str(product.get("delivery_days", 5))
        }
    )
    
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create book order record
        order_id = str(uuid.uuid4())
        order = {
            "id": order_id,
            "session_id": session.session_id,
            "product_id": "livre",
            "product_name": product["name"],
            "amount": product["amount"],
            "currency": product["currency"],
            "user_email": request.user_email,
            "user_data": request.user_data,
            "shipping_address": request.shipping_address,
            "payment_status": "pending",
            "order_status": "awaiting_payment",
            "estimated_delivery_days": product.get("delivery_days", 5),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.book_orders.insert_one(order)
        
        logger.info(f"Book order created: {order_id}")
        
        return {
            "url": session.url,
            "session_id": session.session_id,
            "order_id": order_id
        }
        
    except Exception as e:
        logger.error(f"Error creating book order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@api_router.get("/order/book/{session_id}")
async def get_book_order_status(session_id: str, http_request: Request):
    """Get book order status"""
    
    order = await db.book_orders.find_one({"session_id": session_id}, {"_id": 0})
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    # Check payment status if pending
    if order.get("payment_status") == "pending":
        try:
            host_url = str(http_request.base_url)
            webhook_url = f"{host_url}api/webhook/stripe"
            stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
            
            status = await stripe_checkout.get_checkout_status(session_id)
            
            if status.payment_status == "paid":
                await db.book_orders.update_one(
                    {"session_id": session_id},
                    {"$set": {
                        "payment_status": "paid",
                        "order_status": "processing",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                order["payment_status"] = "paid"
                order["order_status"] = "processing"
                
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
    
    return order


# ========== DAILY CONTENT ROUTES ==========

@api_router.get("/daily/{zodiac_sign}")
async def get_daily_horoscope(zodiac_sign: str):
    """Get daily horoscope, advice, and spiritual phrase for a zodiac sign"""
    valid_signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    if zodiac_sign not in valid_signs:
        raise HTTPException(status_code=400, detail=f"Signe invalide. Signes valides: {', '.join(valid_signs)}")
    
    content = get_daily_content(zodiac_sign)
    
    # Enrich with moon phase from API
    try:
        service = get_astrology_service()
        moon_data = await service.get_moon_phase_report()
        if moon_data and not moon_data.get('status') == False:
            moon_phases_fr = {
                "New Moon": "Nouvelle Lune",
                "Waxing Crescent": "Premier Croissant",
                "First Quarter": "Premier Quartier",
                "Gibbous Moon": "Lune Gibbeuse",
                "Full Moon": "Pleine Lune",
                "Disseminating Moon": "Lune Disséminante",
                "Last Quarter": "Dernier Quartier",
                "Balsamic Moon": "Lune Balsamique",
                "Waning Crescent": "Dernier Croissant",
            }
            moon_conseils_fr = {
                "New Moon": "C'est le moment ideal pour planter de nouvelles intentions et commencer de nouveaux projets. Prenez le temps de vous recentrer sur vos desirs profonds.",
                "Waxing Crescent": "L'energie de croissance commence a se manifester. Nourrissez vos projets avec determination et patience. Les premiers signes de progres apparaissent.",
                "First Quarter": "Un tournant se presente. Des decisions importantes doivent etre prises. Agissez avec courage et faites confiance a votre elan interieur.",
                "Gibbous Moon": "Restez concentre(e) et determine(e) dans la poursuite de vos objectifs. Votre esprit analytique est a son apogee. Peaufinez vos projets avec passion et precision.",
                "Full Moon": "La lumiere de la Pleine Lune eclaire tout ce qui etait cache. C'est un moment de revelation, de culmination et de gratitude. Celebrez vos reussites.",
                "Disseminating Moon": "Partagez votre sagesse et vos realisations avec les autres. C'est le moment de transmettre et d'enseigner ce que vous avez appris.",
                "Last Quarter": "Temps de reflexion et de lacher-prise. Liberez-vous de ce qui ne vous sert plus. Faites de la place pour le nouveau cycle qui approche.",
                "Balsamic Moon": "Phase de repos et d'introspection profonde. Ecoutez vos reves et votre intuition. Preparez-vous en silence pour le renouveau imminent.",
                "Waning Crescent": "Le cycle se termine doucement. Prenez du recul, reposez-vous et laissez partir ce qui doit partir. La renaissance est proche.",
            }
            phase = moon_data.get('moon_phase', '')
            content['phase_lunaire'] = {
                'phase': moon_phases_fr.get(phase, phase),
                'phase_en': phase,
                'signification': moon_data.get('significance', ''),
                'conseil': moon_conseils_fr.get(phase, moon_data.get('report', '')),
                'date': moon_data.get('considered_date', '')
            }
    except Exception as e:
        logger.warning(f"Could not fetch moon phase: {e}")
    
    return content

@api_router.get("/moon-phase")
async def get_moon_phase():
    """Get current moon phase from AstrologyAPI"""
    try:
        service = get_astrology_service()
        moon_data = await service.get_moon_phase_report()
        if moon_data and not moon_data.get('status') == False:
            moon_phases_fr = {
                "New Moon": "Nouvelle Lune",
                "Waxing Crescent": "Premier Croissant",
                "First Quarter": "Premier Quartier",
                "Gibbous Moon": "Lune Gibbeuse",
                "Full Moon": "Pleine Lune",
                "Disseminating Moon": "Lune Disséminante",
                "Last Quarter": "Dernier Quartier",
                "Balsamic Moon": "Lune Balsamique",
                "Waning Crescent": "Dernier Croissant",
            }
            phase = moon_data.get('moon_phase', '')
            return {
                "success": True,
                "phase": moon_phases_fr.get(phase, phase),
                "phase_en": phase,
                "signification": moon_data.get('significance', ''),
                "conseil": moon_data.get('report', ''),
                "date": moon_data.get('considered_date', '')
            }
        raise HTTPException(status_code=500, detail="Données lunaires indisponibles")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Moon phase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== NUMEROLOGY ROUTES ==========

class NumerologyRequest(BaseModel):
    prenom: str
    dateNaissance: str
    heureNaissance: str = "12:00"
    ville: str = "Paris"

@api_router.post("/numerology/complete")
async def get_numerology(request: NumerologyRequest):
    """Get complete numerology profile with French translation"""
    try:
        service = get_astrology_service()
        
        lat, lon, tz = 48.8566, 2.3522, 1.0
        if request.ville:
            geo_data = await service.get_geo_details(request.ville)
            if geo_data and len(geo_data) > 0:
                place = geo_data[0]
                lat = float(place.get('latitude', lat))
                lon = float(place.get('longitude', lon))
        
        # Fetch numerology from API
        numero_data = await service.get_numerological_numbers(
            date_str=request.dateNaissance,
            time_str=request.heureNaissance,
            name=request.prenom,
            lat=lat, lon=lon, timezone=tz
        )
        
        if not numero_data or numero_data.get('status') == False:
            # API blocked - use local calculation as fallback
            return await _local_numerology(request.prenom, request.dateNaissance)
        
        # Translate API response to French
        translated = {}
        for key, value in numero_data.items():
            if isinstance(value, dict) and 'meaning' in value:
                meaning_fr = await translate_to_french(value['meaning'])
                translated[key] = {**value, 'meaning_fr': meaning_fr}
            elif isinstance(value, str) and len(value) > 20:
                translated[key] = await translate_to_french(value)
            else:
                translated[key] = value
        
        return {"success": True, "source": "api", "data": translated}
        
    except Exception as e:
        logger.error(f"Numerology error: {e}")
        return await _local_numerology(request.prenom, request.dateNaissance)


async def _local_numerology(prenom: str, date_naissance: str):
    """Fallback local numerology calculation"""
    try:
        parts = date_naissance.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except:
        year, month, day = 1990, 1, 1
    
    def reduce(n):
        while n > 9 and n not in [11, 22, 33]:
            n = sum(int(d) for d in str(n))
        return n
    
    life_path = reduce(day + month + year)
    
    # Expression number from name
    letter_values = {
        'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
        'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
        's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
    }
    vowels = set('aeiouy')
    name_lower = prenom.lower()
    
    expression = reduce(sum(letter_values.get(c, 0) for c in name_lower if c.isalpha()))
    soul_urge = reduce(sum(letter_values.get(c, 0) for c in name_lower if c in vowels))
    personality = reduce(sum(letter_values.get(c, 0) for c in name_lower if c.isalpha() and c not in vowels))
    personal_year = reduce(day + month + 2026)
    personal_month = reduce(personal_year + 2)  # February 2026
    personal_day = reduce(personal_year + 2 + 28)
    birthday_number = reduce(day)
    
    titles = {
        1: "Le Pionnier", 2: "Le Diplomate", 3: "L'Artiste",
        4: "Le Batisseur", 5: "L'Aventurier", 6: "Le Guerisseur",
        7: "Le Sage", 8: "Le Leader", 9: "L'Humanitaire",
        11: "L'Inspirateur", 22: "Le Maitre Batisseur", 33: "Le Guide Spirituel"
    }
    
    descriptions = {
        1: "Vous etes ne(e) pour mener, innover et ouvrir de nouveaux chemins. Votre independance et votre courage sont vos plus grands atouts.",
        2: "Votre mission est de creer l'harmonie et de faciliter la cooperation. Votre sensibilite et votre diplomatie sont des dons precieux.",
        3: "Vous etes ici pour exprimer votre creativite et inspirer les autres par votre joie de vivre. L'art sous toutes ses formes est votre langage.",
        4: "Votre mission est de construire des fondations solides et durables. Votre discipline et votre fiabilite sont admirables.",
        5: "Vous etes ne(e) pour explorer, experimenter et embrasser le changement. La liberte est votre oxygene vital.",
        6: "Votre mission est de nourrir, guerir et creer de la beaute autour de vous. L'amour et la responsabilite guident vos pas.",
        7: "Vous etes ici pour approfondir la connaissance et chercher la verite. Votre intuition et votre sagesse sont vos guides interieurs.",
        8: "Votre mission est de manifester l'abondance et d'exercer un pouvoir responsable. Votre ambition peut transformer le monde.",
        9: "Vous etes ne(e) pour servir l'humanite et incarner la compassion universelle. Votre vision transcende les frontieres.",
        11: "Votre mission est d'inspirer et d'illuminer les autres par votre vision spirituelle. Vous etes un(e) messager(e) de lumiere.",
        22: "Vous etes ici pour batir des structures qui servent l'humanite. Votre potentiel de realisation est immense.",
        33: "Votre mission est d'enseigner par l'exemple et de guerir par l'amour inconditionnel. Vous incarnez la compassion en action.",
    }
    
    return {
        "success": True,
        "source": "local",
        "data": {
            "chemin_de_vie": {
                "nombre": life_path,
                "titre": titles.get(life_path, "Le Voyageur"),
                "description": descriptions.get(life_path, "")
            },
            "nombre_expression": {
                "nombre": expression,
                "titre": titles.get(expression, ""),
                "description": f"Votre nombre d'expression {expression} revele comment vous vous presentez au monde et quels talents vous portez naturellement."
            },
            "nombre_ame": {
                "nombre": soul_urge,
                "titre": titles.get(soul_urge, ""),
                "description": f"Votre nombre d'ame {soul_urge} revele vos desirs les plus profonds et ce qui motive vraiment votre coeur."
            },
            "nombre_personnalite": {
                "nombre": personality,
                "titre": titles.get(personality, ""),
                "description": f"Votre nombre de personnalite {personality} montre l'image que vous projetez aux autres et la premiere impression que vous laissez."
            },
            "nombre_anniversaire": {
                "nombre": birthday_number,
                "description": f"Ne(e) un {day}, votre nombre d'anniversaire {birthday_number} vous confere des talents specifiques qui colorent votre chemin de vie."
            },
            "annee_personnelle_2026": {
                "nombre": personal_year,
                "theme": titles.get(personal_year, "Evolution"),
                "description": f"Votre annee personnelle {personal_year} en 2026 vous invite a explorer le theme de {titles.get(personal_year, 'evolution').lower()}."
            },
            "mois_personnel": {
                "nombre": personal_month,
                "description": f"Ce mois personnel {personal_month} met l'accent sur {titles.get(personal_month, 'evolution').lower()}."
            }
        }
    }


# ========== TRANSLATION ROUTE ==========

@api_router.post("/translate")
async def translate_content(request: Request):
    """Translate astrological content to French"""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    translated = await translate_to_french(text)
    return {"success": True, "original": text, "translated": translated}



# ========== TAROT OUI/NON ROUTES ==========

class TarotOuiNonRequest(BaseModel):
    question: str

@api_router.post("/tarot/oui-non")
async def tarot_oui_non_endpoint(request: TarotOuiNonRequest):
    """Tirage Tarot Oui/Non - API Growth Plan avec fallback local"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Veuillez poser une question")
    
    # Try API first (Growth Plan)
    try:
        service = get_astrology_service()
        api_result = await service.get_yes_no_tarot()
        if api_result and api_result.get('name'):
            # Translate description to French
            description_fr = await translate_to_french(api_result.get('description', ''))
            # Determine orientation from API value
            api_value = str(api_result.get('value', '')).lower().strip()
            if api_value == 'yes':
                orientation = 'oui'
            elif api_value == 'no':
                orientation = 'non'
            else:
                orientation = 'neutre'
            return {
                "question": request.question,
                "carte": {
                    "numero": 1,
                    "nom": api_result.get('name', ''),
                    "energie": api_result.get('name', ''),
                    "image": "",
                },
                "orientation": orientation,
                "reponse": description_fr,
                "source": "api",
                "date": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.warning(f"Yes/No Tarot API fallback: {e}")
    
    # Fallback to local
    result = tirage_oui_non(request.question)
    result["source"] = "local"
    return result


# ========== TAROT PREDICTIONS (Growth Plan) ==========

@api_router.get("/tarot/predictions")
async def tarot_predictions_endpoint():
    """Get tarot predictions for Love, Career, Finance from AstrologyAPI Growth Plan"""
    try:
        service = get_astrology_service()
        api_result = await service.get_tarot_predictions()
        if not api_result:
            raise HTTPException(status_code=503, detail="Service de predictions indisponible")
        
        # Translate each category
        translated = {}
        for category in ['love', 'career', 'finance']:
            cat_data = api_result.get(category, {})
            if isinstance(cat_data, dict):
                total_text = cat_data.get('total', '')
                score = cat_data.get('score', 0)
                translated_text = await translate_to_french(total_text) if total_text else ''
                translated[category] = {
                    "score": score,
                    "texte": translated_text,
                }
            elif isinstance(cat_data, str):
                translated[category] = {
                    "score": 0,
                    "texte": await translate_to_french(cat_data),
                }
        
        return {"success": True, "source": "api", "predictions": translated}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tarot predictions error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur predictions: {str(e)}")


# ========== TAROLOGIE MEDIUMNITE ROUTES ==========

class MediumniteRequest(BaseModel):
    prenom: str
    date_naissance: str

@api_router.post("/tarologie/tirage")
async def tarologie_tirage(request: MediumniteRequest):
    """Tirage en croix - 5 cartes avec interprétations"""
    if not request.prenom.strip():
        raise HTTPException(status_code=400, detail="Prénom requis")
    
    result = tirage_en_croix(request.prenom, request.date_naissance)
    return result

@api_router.post("/tarologie/pdf")
async def tarologie_pdf(request: MediumniteRequest):
    """Generate PDF for tarologie en croix reading"""
    from fastapi.responses import Response
    
    tirage_data = tirage_en_croix(request.prenom, request.date_naissance)
    pdf_bytes = generate_mediumnite_pdf(tirage_data)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tarologie_croix_{request.prenom}.pdf"}
    )


# ========== PDF PREVIEW ROUTE ==========

@api_router.post("/pdf/preview")
async def generate_pdf_preview(request: Request):
    """Generate preview images of the first pages of the PDF manuscript"""
    import base64
    
    body = await request.json()
    user_data = body.get("user_data", {})
    
    # Generate the full PDF first
    astrology_service = get_astrology_service()
    planets_data = None
    horoscope_data = None
    chart_svg_url = None
    
    if astrology_service:
        try:
            date_naissance = user_data.get('dateNaissance', '1990-01-01')
            heure_naissance = user_data.get('heureNaissance', '12:00')
            
            lat, lon, tz = 48.8566, 2.3522, 1.0
            if user_data.get('ville'):
                geo_data = await astrology_service.get_geo_details(user_data['ville'])
                if geo_data and len(geo_data) > 0:
                    place = geo_data[0]
                    lat = float(place.get('latitude', lat))
                    lon = float(place.get('longitude', lon))
            
            planets_data = await astrology_service.get_planets_tropical(
                date_str=date_naissance, time_str=heure_naissance,
                lat=lat, lon=lon, timezone=tz
            )
            horoscope_data = await astrology_service.get_western_horoscope(
                date_str=date_naissance, time_str=heure_naissance,
                lat=lat, lon=lon, timezone=tz
            )
            chart_svg_url = await astrology_service.get_natal_wheel_chart(
                date_str=date_naissance, time_str=heure_naissance,
                lat=lat, lon=lon, timezone=tz
            )
        except Exception as e:
            logger.error(f"Error fetching astrology data for preview: {e}")
    
    pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data, chart_svg_url=chart_svg_url)
    
    # Convert first pages to preview images using pdf2image or fitz
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        previews = []
        total_pages = len(doc)
        for page_num in range(min(3, total_pages)):
            page = doc[page_num]
            # Render at 150 DPI for good quality preview
            mat = fitz.Matrix(150/72, 150/72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("jpeg", jpg_quality=70)
            b64 = base64.b64encode(img_bytes).decode('utf-8')
            previews.append(f"data:image/jpeg;base64,{b64}")
        doc.close()
        
        return {"previews": previews, "total_pages": total_pages}
    except ImportError:
        logger.warning("PyMuPDF not installed, returning PDF size only")
        return {"previews": [], "total_pages": 0, "pdf_size": len(pdf_bytes)}


# ========== SHARE CARD ROUTE ==========

@api_router.post("/share/generate-card")
async def generate_share_card_endpoint(request: Request):
    """Generate a shareable astrological profile card image (PNG)"""
    from fastapi.responses import Response
    
    body = await request.json()
    user_data = body.get("user_data", {})
    
    astrology_service = get_astrology_service()
    planets_data = None
    
    if astrology_service:
        try:
            date_naissance = user_data.get('dateNaissance', '1990-01-01')
            heure_naissance = user_data.get('heureNaissance', '12:00')
            
            lat, lon, tz = 48.8566, 2.3522, 1.0
            if user_data.get('ville'):
                geo_data = await astrology_service.get_geo_details(user_data['ville'])
                if geo_data and len(geo_data) > 0:
                    place = geo_data[0]
                    lat = float(place.get('latitude', lat))
                    lon = float(place.get('longitude', lon))
            
            planets_data = await astrology_service.get_planets_tropical(
                date_str=date_naissance, time_str=heure_naissance,
                lat=lat, lon=lon, timezone=tz
            )
        except Exception as e:
            logger.error(f"Error fetching astrology data for share card: {e}")
    
    # Calculate life path
    chemin_vie = 1
    try:
        date_str = user_data.get('dateNaissance', '1990-01-01')
        parts = date_str.split('-')
        t = int(parts[2]) + int(parts[1]) + int(parts[0])
        while t > 9 and t not in [11, 22, 33]:
            t = sum(int(x) for x in str(t))
        chemin_vie = t
    except Exception:
        pass
    
    card_bytes = generate_share_card(user_data, planets_data, chemin_vie)
    
    prenom = user_data.get('prenom', 'astral')
    return Response(
        content=card_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="profil_astral_{prenom}.png"'
        }
    )



# ========== PRO HOROSCOPE PDF ROUTE ==========

class ProPdfRequest(BaseModel):
    name: str
    gender: str
    day: int
    month: int
    year: int
    hour: int
    minute: int
    lat: float = 48.8566
    lon: float = 2.3522
    timezone: float = 1.0
    place: str = "Paris, France"

@api_router.post("/pdf/pro-horoscope")
async def get_pro_horoscope_pdf(request: ProPdfRequest):
    """Generate professional horoscope PDF in French with Plume Astrale design"""
    from fastapi.responses import Response

    # Build user_data dict for the PDF generator
    user_data = {
        "prenom": request.name,
        "dateNaissance": f"{request.year}-{request.month:02d}-{request.day:02d}",
        "heureNaissance": f"{request.hour:02d}:{request.minute:02d}",
        "ville": request.place,
        "genre": request.gender,
    }

    # Fetch real planet data from AstrologyAPI JSON endpoint
    planets_data = None
    horoscope_data = None
    chart_svg_url = None
    try:
        astro_service = get_astrology_service()
        date_str = f"{request.year}-{request.month:02d}-{request.day:02d}"
        time_str = f"{request.hour:02d}:{request.minute:02d}"
        planets_data = await astro_service.get_planets_tropical(
            date_str, time_str, request.lat, request.lon, request.timezone
        )
        horoscope_data = await astro_service.get_western_horoscope(
            date_str, time_str, request.lat, request.lon, request.timezone
        )
        chart_svg_url = await astro_service.get_natal_wheel_chart(
            date_str, time_str, request.lat, request.lon, request.timezone
        )
    except Exception as e:
        logger.warning(f"Could not fetch API data, generating with defaults: {e}")

    # Generate our own beautiful French PDF
    pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data, chart_svg_url=chart_svg_url)
    filename = f"theme_astral_pro_{request.name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ========== COMPATIBILITY / MATCH MAKING ROUTE ==========

class PersonData(BaseModel):
    first_name: str
    last_name: str = ""
    gender: str
    day: int
    month: int
    year: int
    hour: int
    minute: int
    lat: float = 48.8566
    lon: float = 2.3522
    timezone: float = 1.0
    place: str = "Paris, France"

class CompatibilityRequest(BaseModel):
    person1: PersonData
    person2: PersonData
    question: str = ""

@api_router.post("/compatibility/generate")
async def generate_compatibility(request: CompatibilityRequest):
    """Génère un rapport de compatibilité astrale complet en PDF enrichi avec l'API."""
    from services.compatibility_pdf_generator import generate_compatibility_pdf
    import base64 as b64
    
    p1 = {
        "first_name": request.person1.first_name,
        "last_name": request.person1.last_name or request.person1.first_name,
        "day": request.person1.day, "month": request.person1.month, "year": request.person1.year,
    }
    p2 = {
        "first_name": request.person2.first_name,
        "last_name": request.person2.last_name or request.person2.first_name,
        "day": request.person2.day, "month": request.person2.month, "year": request.person2.year,
    }
    
    # Fetch real API data for enrichment
    api_data = {}
    try:
        service = get_premium_astrology_service()
        if not service.mock_mode:
            from services.compatibility_pdf_generator import _get_zodiac
            s1_en = _zodiac_to_english(_get_zodiac(p1['day'], p1['month']))
            s2_en = _zodiac_to_english(_get_zodiac(p2['day'], p2['month']))
            
            import asyncio
            zodiac_compat, romantic1, romantic2 = await asyncio.gather(
                service.get_zodiac_compatibility(s1_en, s2_en),
                service.get_romantic_personality_report(
                    f"{p1['year']}-{p1['month']:02d}-{p1['day']:02d}", "12:00",
                    request.person1.lat, request.person1.lon, request.person1.timezone
                ),
                service.get_romantic_personality_report(
                    f"{p2['year']}-{p2['month']:02d}-{p2['day']:02d}", "12:00",
                    request.person2.lat, request.person2.lon, request.person2.timezone
                ),
            )
            api_data = {
                "zodiac_compat": zodiac_compat,
                "romantic_p1": romantic1,
                "romantic_p2": romantic2,
            }
    except Exception as e:
        logger.warning(f"API enrichment failed (using local data): {e}")
    
    pdf_bytes = generate_compatibility_pdf(p1, p2, request.question, api_data)
    
    pdf_b64 = b64.b64encode(pdf_bytes).decode()
    pdf_url = f"data:application/pdf;base64,{pdf_b64}"
    
    return {"pdf_url": pdf_url}


def _zodiac_to_english(fr_sign):
    """Convertit un signe français en anglais pour l'API"""
    mapping = {
        "Bélier": "aries", "Taureau": "taurus", "Gémeaux": "gemini",
        "Cancer": "cancer", "Lion": "leo", "Vierge": "virgo",
        "Balance": "libra", "Scorpion": "scorpio", "Sagittaire": "sagittarius",
        "Capricorne": "capricorn", "Verseau": "aquarius", "Poissons": "pisces"
    }
    return mapping.get(fr_sign, "aries")


# ========== PREMIUM EXPERIENCE ROUTES ==========

from services.premium_service import generate_premium_content
from services.premium_pdf_generator import generate_premium_pdf

class PremiumRequest(BaseModel):
    prenom: str
    dateNaissance: str
    heureNaissance: str = "12:00"
    ville: str = "Paris"

@api_router.post("/premium/generate")
async def premium_generate(request: PremiumRequest):
    """Generate the 5-step premium content using LLM"""
    try:
        user_data = {
            "prenom": request.prenom,
            "dateNaissance": request.dateNaissance,
            "heureNaissance": request.heureNaissance,
            "ville": request.ville,
        }
        content = await generate_premium_content(user_data)
        return {"success": True, "data": content}
    except Exception as e:
        logger.error(f"Premium generate error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la generation du contenu premium: {str(e)}")

@api_router.post("/premium/pdf")
async def premium_pdf(request: Request):
    """Generate the Premium PDF from the full premium data"""
    from fastapi.responses import Response
    try:
        body = await request.json()
        premium_data = body.get("data", {})
        if not premium_data:
            raise HTTPException(status_code=400, detail="Donnees premium manquantes")
        pdf_bytes = generate_premium_pdf(premium_data)
        prenom = premium_data.get("prenom", "premium")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=cartographie_premium_{prenom}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Premium PDF error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur PDF: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS PREMIUM - ASTROLOGY API PLAN GROWTH
# ═══════════════════════════════════════════════════════════════════════════════

class PersonData(BaseModel):
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    lat: float
    lon: float
    timezone: float = 1.0
    name: Optional[str] = ""

class LoveAnalysisRequest(BaseModel):
    """Requête pour l'analyse Amour Premium (49€)"""
    person1: PersonData
    person2: PersonData

class CircleDailyRequest(BaseModel):
    """Requête pour le contenu quotidien Le Cercle"""
    zodiac_sign: str
    user_id: Optional[str] = None

class UserProfileRequest(BaseModel):
    """Requête pour le profil utilisateur complet"""
    date: str
    time: str
    lat: float
    lon: float
    timezone: float = 1.0
    name: Optional[str] = ""

@api_router.post("/premium/love-analysis")
async def premium_love_analysis(request: LoveAnalysisRequest):
    """
    🌹 OFFRE AMOUR PREMIUM (49€)
    Analyse complète de compatibilité amoureuse:
    - Compatibilité zodiacale
    - Synastrie (aspects inter-charts)
    - Profils romantiques des deux personnes
    - Synthèse et conseils
    """
    try:
        service = get_premium_astrology_service()
        
        person1 = request.person1.model_dump()
        person2 = request.person2.model_dump()
        
        result = await service.get_love_compatibility_full(person1, person2)
        
        return {
            "success": True,
            "product": "amour_premium",
            "data": result
        }
    except Exception as e:
        logger.error(f"Love analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur analyse amour: {str(e)}")


@api_router.post("/premium/circle-daily")
async def premium_circle_daily(request: CircleDailyRequest):
    """
    🌙 LE CERCLE - Contenu Quotidien (14,90€/mois)
    Contenu personnalisé chaque jour:
    - Tarot du jour
    - Métriques lunaires
    - Horoscope premium
    - Message quotidien personnalisé
    """
    try:
        service = get_premium_astrology_service()
        
        result = await service.get_circle_daily_content(request.zodiac_sign)
        
        return {
            "success": True,
            "product": "cercle_mensuel",
            "data": result
        }
    except Exception as e:
        logger.error(f"Circle daily error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur contenu cercle: {str(e)}")


@api_router.post("/premium/user-profile")
async def premium_user_profile(request: UserProfileRequest):
    """
    ⭐ PROFIL UTILISATEUR COMPLET (39€)
    Rapports complets:
    - Karma et Destinée
    - Personnalité (système tropical)
    - Numérologie complète (si nom fourni)
    """
    try:
        service = get_premium_astrology_service()
        
        user_data = request.model_dump()
        result = await service.get_full_user_profile(user_data)
        
        return {
            "success": True,
            "product": "profil_complet",
            "data": result
        }
    except Exception as e:
        logger.error(f"User profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur profil utilisateur: {str(e)}")


@api_router.get("/premium/natal-chart/{date}/{time}/{lat}/{lon}")
async def premium_natal_chart(date: str, time: str, lat: float, lon: float, timezone: float = 1.0):
    """
    🌌 CARTE DU CIEL VISUELLE
    Génère la carte natale en SVG
    """
    try:
        service = get_premium_astrology_service()
        
        # time is URL encoded, replace - with :
        time_formatted = time.replace("-", ":")
        
        result = await service.get_natal_wheel_chart(date, time_formatted, lat, lon, timezone)
        
        if result:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=404, detail="Impossible de générer la carte du ciel")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Natal chart error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur carte du ciel: {str(e)}")


@api_router.get("/premium/lunar-metrics")
async def premium_lunar_metrics():
    """
    🌙 MÉTRIQUES LUNAIRES
    Phase actuelle, énergie, rituels recommandés
    """
    try:
        service = get_premium_astrology_service()
        result = await service.get_lunar_metrics()
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Lunar metrics error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur métriques lunaires: {str(e)}")


@api_router.get("/premium/tarot-daily")
async def premium_tarot_daily():
    """
    🎴 TAROT DU JOUR
    Carte tirée, signification, conseil
    """
    try:
        service = get_premium_astrology_service()
        result = await service.get_tarot_predictions()
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Tarot daily error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur tarot quotidien: {str(e)}")


class NumerologyRequest(BaseModel):
    date: str
    name: str

@api_router.post("/premium/numerology")
async def premium_numerology(request: NumerologyRequest):
    """
    🔢 PROFIL NUMÉROLOGIQUE COMPLET
    Chemin de vie, Âme, Expression, Défis
    """
    try:
        service = get_premium_astrology_service()
        result = await service.get_full_numerology_profile(request.date, request.name)
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Numerology error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur numérologie: {str(e)}")


@api_router.get("/premium/horoscope/{zodiac_sign}")
async def premium_horoscope(zodiac_sign: str):
    """
    ♈ HOROSCOPE PREMIUM
    Prévisions détaillées par domaine
    """
    try:
        service = get_premium_astrology_service()
        result = await service.get_daily_horoscope_premium(zodiac_sign)
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Horoscope error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur horoscope: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# RAPPORTS PLANÉTAIRES & CARTE DU CIEL
# ═══════════════════════════════════════════════════════════════════════════════

@api_router.get("/premium/planet-reports/{date}/{time}/{lat}/{lon}")
async def get_planet_reports(date: str, time: str, lat: float, lon: float, timezone: float = 1.0):
    """Rapports planétaires complets (sign + house) pour toutes les planètes"""
    try:
        service = get_premium_astrology_service()
        result = await service.get_all_planet_reports(date, time, lat, lon, timezone)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Planet reports error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/premium/personality/{date}/{time}/{lat}/{lon}")
async def get_personality(date: str, time: str, lat: float, lon: float, timezone: float = 1.0):
    """Rapport de personnalité tropical"""
    try:
        service = get_premium_astrology_service()
        result = await service.get_personality_report_tropical(date, time, lat, lon, timezone)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Personality report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/premium/romantic/{date}/{time}/{lat}/{lon}")
async def get_romantic(date: str, time: str, lat: float, lon: float, timezone: float = 1.0):
    """Rapport de personnalité romantique"""
    try:
        service = get_premium_astrology_service()
        result = await service.get_romantic_personality_report(date, time, lat, lon, timezone)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Romantic report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/premium/zodiac-compat/{sign1}/{sign2}")
async def get_zodiac_compat(sign1: str, sign2: str):
    """Compatibilité entre deux signes du zodiaque (données API réelles)"""
    try:
        service = get_premium_astrology_service()
        result = await service.get_zodiac_compatibility(sign1, sign2)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Zodiac compat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS TAROT PREMIUM - Tirages avec Question
# ═══════════════════════════════════════════════════════════════════════════════

from services.tarot_premium import (
    tirage_marseille_question, 
    tirage_croix_celtique, 
    tirage_du_jour,
    DOMAINES_QUESTIONS,
    ARCANES_MAJEURS
)

class TarotQuestionRequest(BaseModel):
    """Requête pour tirage tarot avec question"""
    question: str
    domaine: str = "general"  # amour, travail, argent, sante, spirituel, general

@api_router.get("/tarot/domaines")
async def get_domaines_tarot():
    """
    📋 DOMAINES DE QUESTIONS
    Liste des domaines disponibles pour les tirages
    """
    return {
        "success": True,
        "domaines": DOMAINES_QUESTIONS
    }

@api_router.get("/tarot/jour")
async def get_tirage_du_jour():
    """
    🌟 TIRAGE DU JOUR - GRATUIT
    Une carte par jour, la même pour tous les utilisateurs
    Message personnalisé, affirmation et rituel suggéré
    """
    try:
        result = tirage_du_jour()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Tirage du jour error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur tirage du jour: {str(e)}")

@api_router.post("/tarot/marseille")
async def tarot_marseille(request: TarotQuestionRequest):
    """
    🎴 TIRAGE TAROT DE MARSEILLE (19€)
    3 cartes: Passé - Présent - Futur
    Avec votre question personnalisée
    """
    try:
        if not request.question or len(request.question) < 5:
            raise HTTPException(status_code=400, detail="Veuillez formuler une question d'au moins 5 caractères")
        
        result = tirage_marseille_question(
            question=request.question,
            domaine=request.domaine
        )
        
        return {
            "success": True,
            "product": "tarot_marseille",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tarot Marseille error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur tirage Marseille: {str(e)}")

@api_router.post("/tarot/celtique")
async def tarot_celtique(request: TarotQuestionRequest):
    """
    🔮 TIRAGE CROIX CELTIQUE (29€)
    10 cartes - Le tirage le plus complet
    Analyse approfondie de votre situation
    """
    try:
        if not request.question or len(request.question) < 5:
            raise HTTPException(status_code=400, detail="Veuillez formuler une question d'au moins 5 caractères")
        
        result = tirage_croix_celtique(
            question=request.question,
            domaine=request.domaine
        )
        
        return {
            "success": True,
            "product": "tarot_celtique",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tarot Celtique error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur tirage Celtique: {str(e)}")

@api_router.get("/tarot/arcanes")
async def get_arcanes_majeurs():
    """
    📖 ARCANES MAJEURS
    Liste complète des 22 arcanes avec descriptions
    """
    arcanes_list = []
    for num, arcane in ARCANES_MAJEURS.items():
        arcanes_list.append({
            "numero": num,
            "nom": arcane["nom"],
            "mots_cles": arcane["mots_cles"],
            "element": arcane["element"],
            "planete": arcane["planete"],
            "description": arcane["description"]
        })
    
    return {
        "success": True,
        "arcanes": arcanes_list
    }


# Include the router in the main app
# Mount static assets for tarot/zodiac images
app.mount("/api/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Include the API router
app.include_router(api_router)

# Health check endpoint for Kubernetes
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global exception handler ─────────────────────────────────────────────────
# Garantit que le header CORS est toujours présent, même sur les erreurs 500,
# afin que le navigateur puisse lire la réponse et afficher un message lisible.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    origin = request.headers.get("origin", "*")
    allowed_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
    cors_origin = origin if ("*" in allowed_origins or origin in allowed_origins) else allowed_origins[0]
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur. Veuillez réessayer."},
        headers={
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Credentials": "true",
        },
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
