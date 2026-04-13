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

# Import des services (assure-toi que ces fichiers existent dans ton dossier services)
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

# Configuration Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ─── DB SIMULATION ───
fake_db = {
    "users": {},
    "wallets": {},
}

# ─── CONFIG ───
ASSETS_DIR = Path(__file__).parent / "assets"

app = FastAPI()

# 1. CONFIGURATION DU ROUTER (Toutes ces routes seront préfixées par /api)
api_router = APIRouter(prefix="/api")

class RegisterRequest(BaseModel):
    email: str
    password: str
    birth_date: str
    birth_time: str
    birth_place: str
    birth_country: str = "France"

@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    email = req.email.strip().lower()
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(req.password),
        "is_premium": True, # On force le premium pour tes tests
        "birth_date": req.birth_date
    }
    fake_db["users"][email] = user_doc
    fake_db["wallets"][user_id] = {"credit_balance": 1000}
    token = create_token(user_id, email)
    return {"token": token, "user": user_doc, "credit_balance": 1000}

@api_router.get("/tarot/jour")
async def get_jour():
    # Route appelée par ton frontend
    return {"success": True, "data": tirage_du_jour()}

@api_router.get("/tarot/domaines")
async def get_domaines():
    return {"success": True, "domaines": DOMAINES_QUESTIONS}

@api_router.post("/tarot/oui-non")
async def tarot_oui_non_endpoint(request: Request):
    body = await request.json()
    question = body.get("question", "")
    return tirage_oui_non(question)

@api_router.get("/daily/{zodiac_sign}")
async def get_daily(zodiac_sign: str):
    return get_daily_content(zodiac_sign)

# 2. INCLUSION DU ROUTER DANS L'APP
app.include_router(api_router)

# 3. ROUTES DE SANTÉ (Hors /api)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "in-memory"}

# 4. MIDDLEWARES (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage des assets
if ASSETS_DIR.exists():
    app.mount("/api/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
