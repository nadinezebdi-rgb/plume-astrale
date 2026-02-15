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
        "description": "Votre guide spirituel personnel à conserver précieusement"
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