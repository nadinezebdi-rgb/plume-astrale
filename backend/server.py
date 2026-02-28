from fastapi import FastAPI, APIRouter, HTTPException, Request
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
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from services.astrology_api import get_astrology_service, AstrologyAPIService
from services.pdf_generator_v2 import generate_manuscrit_complet
from services.daily_content import get_daily_content
from services.tarot_service import tirage_oui_non, tirage_mediumnite_complet, tirage_en_croix
from services.mediumnite_pdf import generate_mediumnite_pdf
from services.astrology_pdf_api import generate_pro_horoscope_pdf, generate_match_making_pdf


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
        "name": "Theme Astral Professionnel",
        "amount": 29.90,
        "currency": "eur",
        "description": "Votre theme astral professionnel complet - 28+ pages enrichies (PDF)"
    },
    "chemin_ame": {
        "name": "Le Chemin d'Ame",
        "amount": 24.90,
        "currency": "eur",
        "description": "Votre chemin d'ame personnalise - Numerologie, previsions et guidance (PDF)"
    },
    "livre": {
        "name": "Le Livre de la Plume",
        "amount": 49.90,
        "currency": "eur",
        "description": "Votre manuscrit imprime en livre relie - Livraison sous 5 jours",
        "requires_address": True,
        "delivery_days": 5
    },
    "tarot_oui_non": {
        "name": "Tarot Oui/Non",
        "amount": 4.99,
        "currency": "eur",
        "description": "Tirage d'un Arcane Majeur pour repondre a votre question"
    },
    "tarologie_mediumnite": {
        "name": "Tarologie & Mediumnite",
        "amount": 35.00,
        "currency": "eur",
        "description": "Tirage complet 7 cartes + lecture mediumnique en PDF"
    },
    "compatibilite": {
        "name": "Compatibilite Astrale",
        "amount": 29.90,
        "currency": "eur",
        "description": "Analyse de compatibilite amoureuse complete - 24 pages (PDF)"
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

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Payment Models
class CheckoutRequest(BaseModel):
    product_id: str
    origin_url: str
    user_email: Optional[str] = None
    user_data: Optional[Dict] = None
    discount_code: Optional[str] = None
    shipping_address: Optional[Dict] = None  # For physical book

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
            except Exception as e:
                logger.warning(f"Could not fetch astrology data: {e}")
        
        # Generate PDF
        pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data)
        
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
    return content


# ========== TAROT OUI/NON ROUTES ==========

class TarotOuiNonRequest(BaseModel):
    question: str

@api_router.post("/tarot/oui-non")
async def tarot_oui_non_endpoint(request: TarotOuiNonRequest):
    """Tirage Tarot Oui/Non - tire un arcane majeur"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Veuillez poser une question")
    
    result = tirage_oui_non(request.question)
    return result


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
        except Exception as e:
            logger.error(f"Error fetching astrology data for preview: {e}")
    
    pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data)
    
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
    except Exception as e:
        logger.warning(f"Could not fetch API data, generating with defaults: {e}")

    # Generate our own beautiful French PDF
    pdf_bytes = generate_manuscrit_complet(user_data, planets_data, horoscope_data)
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

@api_router.post("/compatibility/generate")
async def generate_compatibility(request: CompatibilityRequest):
    """Generate a 24-page compatibility/match making PDF"""
    
    # Determine male/female roles based on gender
    if request.person1.gender.lower() in ["male", "homme", "m"]:
        male_data = request.person1
        female_data = request.person2
    else:
        male_data = request.person2
        female_data = request.person1
    
    pdf_url = await generate_match_making_pdf(
        male_data={
            "first_name": male_data.first_name,
            "last_name": male_data.last_name or male_data.first_name,
            "day": male_data.day, "month": male_data.month, "year": male_data.year,
            "hour": male_data.hour, "minute": male_data.minute,
            "lat": male_data.lat, "lon": male_data.lon,
            "timezone": male_data.timezone, "place": male_data.place,
        },
        female_data={
            "first_name": female_data.first_name,
            "last_name": female_data.last_name or female_data.first_name,
            "day": female_data.day, "month": female_data.month, "year": female_data.year,
            "hour": female_data.hour, "minute": female_data.minute,
            "lat": female_data.lat, "lon": female_data.lon,
            "timezone": female_data.timezone, "place": female_data.place,
        },
    )
    
    if not pdf_url:
        raise HTTPException(status_code=500, detail="Erreur lors de la generation du rapport de compatibilite")
    
    return {"pdf_url": pdf_url}


# Include the router in the main app
# Mount static assets for tarot/zodiac images
app.mount("/api/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Include the API router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
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