from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import Dict
import uuid

# Import des services
from services.astrology_api import get_astrology_service
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_en_croix
from services.auth_service import hash_password, verify_password, create_token
from services.tarot_premium import (
    tirage_marseille_question, tirage_croix_celtique, tirage_du_jour,
    DOMAINES_QUESTIONS
)

# Configuration Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ─── DB SIMULATION ───
fake_db = {"users": {}, "wallets": {}}

# ─── CONFIG ───
ASSETS_DIR = Path(__file__).parent / "assets"
app = FastAPI()

# 1. INITIALISATION DU ROUTER
api_router = APIRouter(prefix="/api")

class RegisterRequest(BaseModel):
    email: str
    password: str
    birth_date: str
    birth_time: str
    birth_place: str
    birth_country: str = "France"

# ─── ROUTES AUTHENTIFICATION ───

@api_router.post("/auth/register")
async def register(req: RegisterRequest):
    email = req.email.strip().lower()
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(req.password),
        "is_premium": True,
        "birth_date": req.birth_date
    }
    fake_db["users"][email] = user_doc
    fake_db["wallets"][user_id] = {"credit_balance": 1000}
    token = create_token(user_id, email)
    return {"token": token, "user": user_doc, "credit_balance": 1000}

@api_router.post("/auth/login")
async def login(req: BaseModel): # Simplifié pour le test
    # Logique de login si nécessaire
    return {"status": "ok"}

# ─── ROUTES TAROT (VRAIS SERVICES RECONNECTÉS) ───

@api_router.get("/tarot/domaines")
async def get_domaines():
    return {"success": True, "domaines": DOMAINES_QUESTIONS}

@api_router.get("/tarot/jour")
async def get_jour():
    return {"success": True, "data": tirage_du_jour()}

@api_router.post("/tarot/oui-non")
async def tarot_oui_non_endpoint(request: Request):
    body = await request.json()
    return tirage_oui_non(body.get("question", ""))

@api_router.post("/tarot/marseille")
async def tarot_marseille_endpoint(request: Request):
    body = await request.json()
    # Utilise le vrai service premium
    result = tirage_marseille_question(body.get("question", ""), body.get("domaine", "general"))
    return {"success": True, "data": result}

@api_router.post("/tarot/celtique")
async def tarot_celtique_endpoint(request: Request):
    body = await request.json()
    # Utilise le vrai service premium
    result = tirage_croix_celtique(body.get("question", ""), body.get("domaine", "general"))
    return {"success": True, "data": result}

@api_router.post("/tarologie/tirage")
async def tirage_croix_endpoint(request: Request):
    body = await request.json()
    return tirage_en_croix(body.get("prenom", "Ami"), "1990-01-01")

# ─── ROUTES ASTROLOGIE (VRAIS SERVICES) ───

@api_router.get("/daily/{zodiac_sign}")
async def get_daily(zodiac_sign: str):
    # Reconnexion au service de contenu quotidien
    return get_daily_content(zodiac_sign)

@api_router.post("/credits/use")
async def use_credits(request: Request):
    return {"success": True, "credit_balance": 990}
# --- ROUTE POUR LE CHAT ASTRO IA ---

@api_router.post("/astro-chat")
async def astro_chat_endpoint(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "")
        user_data = body.get("user_data", {}) # Données de naissance

        # On récupère tes clés depuis les variables d'environnement Render
        user_id = os.environ.get('ASTROLOGY_API_USER_ID')
        api_key = os.environ.get('ASTROLOGY_API_KEY')

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://json-chat.astrologyapi.com/api/chat",
                auth=(user_id, api_key),
                json={
                    "language": "fr",
                    "question": user_message,
                    "name": user_data.get("name", "Utilisateur"),
                    "day": int(user_data.get("day", 1)),
                    "month": int(user_data.get("month", 1)),
                    "year": int(user_data.get("year", 1990)),
                    "hour": int(user_data.get("hour", 12)),
                    "min": int(user_data.get("min", 0)),
                    "lat": float(user_data.get("lat", 48.8566)),
                    "lon": float(user_data.get("lon", 2.3522)),
                    "tzone": 1.0,
                    "gender": "female"
                },
                timeout=30.0
            )
            
            data = response.json()
            # On renvoie la réponse de l'IA au frontend
            return {"success": True, "answer": data.get("response", "L'astrologue réfléchit...")}

    except Exception as e:
        logger.error(f"Erreur Chat API: {e}")
        return {"success": False, "message": "Désolé, l'astrologue est occupé."}
# ─── CONFIGURATION FINALE ───

# On inclut le router UNE SEULE FOIS
app.include_router(api_router)

# Middlewares CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if ASSETS_DIR.exists():
    app.mount("/api/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
