from fastapi import FastAPI, APIRouter, HTTPException, Request
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
from services.pdf_generator import generate_manuscrit_pdf


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Fixed product packages - prices defined server-side only
PRODUCTS = {
    "manuscrit": {
        "name": "Le Manuscrit de la Plume",
        "amount": 29.90,
        "currency": "eur",
        "description": "Votre guide spirituel personnel à conserver précieusement (PDF)"
    },
    "livre": {
        "name": "Le Livre de la Plume",
        "amount": 49.90,
        "currency": "eur",
        "description": "Votre manuscrit imprimé en livre relié - Livraison sous 5 jours",
        "requires_address": True,
        "delivery_days": 5
    }
}

# Discount codes - defined server-side only for security
DISCOUNT_CODES = {
    "ASTRO100": {
        "discount_percent": 100,
        "description": "Accès gratuit complet"
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
        pdf_bytes = generate_manuscrit_pdf(user_data, planets_data, horoscope_data)
        
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

# Include the router in the main app
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