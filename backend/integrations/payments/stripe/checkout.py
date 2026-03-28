"""Remplacement natif de emergentintegrations.payments.stripe.checkout"""
import stripe
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class CheckoutSessionRequest:
    amount: float
    currency: str
    success_url: str
    cancel_url: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class CheckoutSessionResponse:
    session_id: str
    url: str


@dataclass
class CheckoutStatusResponse:
    status: str          # "paid", "unpaid", "no_payment_required"
    payment_status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str = None):
        self.api_key = api_key
        self.webhook_url = webhook_url
        stripe.api_key = api_key

    async def create_checkout_session(self, req: CheckoutSessionRequest) -> CheckoutSessionResponse:
        amount_cents = int(req.amount * 100)
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": req.currency,
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": req.metadata.get("pack_name", "Plume Astrale"),
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata=req.metadata,
        )
        return CheckoutSessionResponse(session_id=session.id, url=session.url)

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        session = stripe.checkout.Session.retrieve(session_id)
        return CheckoutStatusResponse(
            status=session.payment_status,
            payment_status=session.payment_status,
            metadata=dict(session.metadata or {}),
        )

    async def handle_webhook(self, body: bytes, signature: str) -> Dict[str, Any]:
        webhook_secret = None  # optionnel
        try:
            event = stripe.Webhook.construct_event(body, signature, webhook_secret) if webhook_secret else stripe.Event.construct_from(
                __import__('json').loads(body), stripe.api_key
            )
            return {"event_type": event["type"], "data": event["data"]["object"]}
        except Exception as e:
            raise ValueError(f"Webhook error: {e}")
