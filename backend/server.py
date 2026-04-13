from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import asyncio
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone

# Import des services locaux
from services.astrology_api import get_astrology_service
from services.astrology_api_premium import get_premium_astrology_service
from services.pdf_generator_v2 import generate_manuscrit_complet
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_en_croix, ARCANES_TAROT, TAROT_IMAGE_MAP
from services.mediumnite_pdf import generate_mediumnite_pdf
from services.share_card_generator import generate_share_card
from services.translation_service import translate_to_french
from services.auth_service import hash_password, verify_password, create_token
from services.tarot_premium import (
    tirage_marseille_question, tirage_croix_celtique, tirage_du_jour,
    DOMAINES_QUESTIONS, ARCANES_MAJEURS
)
from integrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Configuration Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ─── SIMULATION DE BASE DE DONNÉES (Remplaçant MongoDB) ──────────────────────
# Note: Ces données sont perdues à chaque redémarrage du serveur Render
fake_db = {
    "users": {},
    "wallets": {},
    "transactions": [],
    "status_checks": []
}

# ─── CONFIGURATION STRIPE & ASSETS ──────────────────────────────────────────
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
ASSETS_DIR = Path(__file__).parent / "assets"

PRODUCTS = {
    "manuscrit": {"name": "Thème Astral Professionnel", "amount": 29.90, "currency": "eur"},
    "journal_quotidien": {"name": "Journal Astral Quotidien", "amount": 15.99, "currency": "eur", "subscription": True},
    # ... (les autres produits restent identiques à votre liste originale)
}

# ─── FASTAPI APP ──────────────────────────────────────────────────────────────
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    birth_date: str
    birth_time: str
    birth_place: str
    birth_country: str = "France"

class LoginRequest(BaseModel):
    email: str
    password: str

# ─── AUTH ROUTES (Version In-Memory) ──────────────────────────────────────────

@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    email = req.email.strip().lower()
    if email in fake_db["users"]:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(req.password),
        "birth_date": req.birth_date,
        "birth_time": req.birth_time,
        "birth_place": req.birth_place,
        "birth_country": req.birth_country
    }
    fake_db["users"][email] = user_doc
    fake_db["wallets"][user_id] = {"credit_balance": 20} # Bonus de bienvenue
    
    token = create_token(user_id, email)
    return {"token": token, "user": user_doc, "credit_balance": 20}

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    email = req.email.strip().lower()
    user = fake_db["users"].get(email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_token(user["id"], email)
    wallet = fake_db["wallets"].get(user["id"], {"credit_balance": 0})
    return {"token": token, "user": user, "credit_balance": wallet["credit_balance"]}

# ─── ASTROLOGY & TAROT ROUTES (Fonctionnent sans DB) ──────────────────────────

@api_router.get("/astrology/daily/{zodiac_sign}")
async def get_daily_horoscope_api(zodiac_sign: str):
    service = get_astrology_service()
    data = await service.get_daily_horoscope(zodiac_sign)
    return {"success": True, "data": data}

@api_router.post("/tarot/oui-non")
async def tarot_oui_non_endpoint(request: Dict):
    question = request.get("question", "")
    return tirage_oui_non(question)

# ─── MIDDLEWARES & CONFIG ─────────────────────────────────────────────────────

app.mount("/api/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "in-memory-mode"}

# Gestionnaire d'erreurs pour éviter les plantages CORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne. Le service tourne en mode limité (sans base de données)."},
    )

app.include_router(api_router)
