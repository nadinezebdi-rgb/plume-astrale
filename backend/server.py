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
    fake_db["wallets"][user_id] = {"credit_balance": 50}
    token = create_token(user_id, email)
    return {"token": token, "user": user_doc, "credit_balance": 50}

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
    """
    Chat IA astrologique en français via AstrologyAPI / AstroChat
    Endpoint: https://json-chat.astrologyapi.com/api/chat
    Doc: https://astrologyapi.com/developers/v1/chat-api

    Body attendu (flexible) :
      { "message": "...", "user_data": {...} }
      OU
      { "message": "...", "name": "...", "day": ..., "month": ..., ... }
    """
    try:
        body = await request.json()
        user_message = (body.get("message") or body.get("q") or "").strip()
        if not user_message:
            return {"success": False, "message": "Question vide."}

        # Supporte les deux formats : nested user_data OU champs à plat
        ud = body.get("user_data") or body

        # Données de naissance avec fallback français (Paris)
        name = str(ud.get("name") or "Voyageur")
        day = int(ud.get("day") or 1)
        month = int(ud.get("month") or 1)
        year = int(ud.get("year") or 1990)
        hour = int(ud.get("hour") or 12)
        minute = int(ud.get("min") or ud.get("minute") or 0)
        lat = str(ud.get("lat") or "48.8566")
        lon = str(ud.get("lon") or "2.3522")
        tzone = str(ud.get("tzone") or "1")
        gender = str(ud.get("gender") or "female").lower()
        if gender not in ("male", "female"):
            gender = "female"
        place = str(ud.get("place") or ud.get("birth_place") or "Paris")
        country = str(ud.get("country") or "FR")
        lang = str(ud.get("language") or body.get("lang") or "fr")

        # Niveau d'expertise et tradition (Western pour audience française)
        ep = str(body.get("ep") or "STANDARD").upper()
        ac = str(body.get("ac") or "WESTERN").upper()
        sid = str(body.get("sid") or "astro-6")

        # Authentification : Access Token prioritaire, fallback Basic Auth
        access_token = os.environ.get('ASTROLOGY_API_ACCESS_TOKEN')
        user_id = os.environ.get('ASTROLOGY_API_USER_ID')
        api_key = os.environ.get('ASTROLOGY_API_KEY')

        payload = {
            "language": lang,
            "name": name,
            "day": day,
            "month": month,
            "year": year,
            "hour": hour,
            "min": minute,
            "place": place,
            "lat": lat,
            "lon": lon,
            "tzone": tzone,
            "gender": gender,
            "country": country,
            "ap": "KUNDLI",
            "sid": sid,
            "ep": ep,
            "ac": ac,
            "q": user_message,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept-Language": lang,
        }

        import httpx
        async with httpx.AsyncClient(timeout=45.0) as client:
            if access_token:
                headers["x-astrologyapi-key"] = access_token
                response = await client.post(
                    "https://json-chat.astrologyapi.com/api/chat",
                    json=payload,
                    headers=headers,
                )
            else:
                # Fallback Basic Auth
                response = await client.post(
                    "https://json-chat.astrologyapi.com/api/chat",
                    auth=(user_id or "", api_key or ""),
                    json=payload,
                    headers=headers,
                )

        try:
            data = response.json()
        except Exception:
            logger.error(f"AstroChat non-JSON response: {response.status_code} {response.text[:300]}")
            return {"success": False, "message": "Reponse invalide de l'oracle. Reessaie dans un instant."}

        # Format de reponse officiel : { status: true, message: "...", response: {...} }
        # Fallbacks pour les variantes
        answer = (
            data.get("message")
            or data.get("answer")
            or (data.get("response") if isinstance(data.get("response"), str) else None)
        )

        if data.get("status") is True and answer:
            return {"success": True, "answer": answer, "raw": {"sid": sid, "ep": ep, "ac": ac}}

        # Erreurs côté API (insufficient credit, invalid creds, etc.)
        err = data.get("error") or data.get("msg") or data.get("message")
        logger.warning(f"AstroChat API returned non-success: {data}")
        if err and "credit" in str(err).lower():
            return {
                "success": False,
                "code": "API_CREDIT",
                "message": "Le service de chat n'est pas active sur le compte AstrologyAPI. Verifie l'activation d'AstroChat dans ton dashboard.",
            }
        return {"success": False, "message": str(err) if err else "L'oracle est momentanement indisponible."}

    except httpx.TimeoutException:
        logger.error("AstroChat timeout")
        return {"success": False, "message": "L'oracle prend trop de temps a repondre. Reessaie."}
    except Exception as e:
        logger.error(f"Erreur Chat API: {e}", exc_info=True)
        return {"success": False, "message": "Une perturbation cosmique empeche la connexion."}
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
