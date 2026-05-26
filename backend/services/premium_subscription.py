"""Premium subscription — Stripe Subscriptions (mode=subscription)."""
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import stripe
from fastapi import HTTPException

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

PREMIUM_PRICE_EUR = 14.99
PREMIUM_PLAN_NAME = 'Plume Astrale Premium'
PREMIUM_PLAN_DESCRIPTION = "Accès illimité aux cycles, compatibilités, journal et énergies quotidiennes complètes."

_PRICE_ID_CACHE: Optional[str] = None


def _get_or_create_price() -> str:
    global _PRICE_ID_CACHE
    if _PRICE_ID_CACHE:
        return _PRICE_ID_CACHE
    stripe.api_key = os.environ.get('STRIPE_API_KEY')

    env_price = os.environ.get('STRIPE_PREMIUM_PRICE_ID')
    if env_price:
        _PRICE_ID_CACHE = env_price
        return env_price

    try:
        existing = stripe.Price.list(lookup_keys=['plume_premium_monthly_eur'], limit=1)
        if existing.data:
            _PRICE_ID_CACHE = existing.data[0].id
            return _PRICE_ID_CACHE
    except Exception as e:
        logger.warning(f'Cannot lookup price: {e}')

    product = stripe.Product.create(
        name=PREMIUM_PLAN_NAME,
        description=PREMIUM_PLAN_DESCRIPTION,
        metadata={'plan': 'premium_monthly'},
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=int(PREMIUM_PRICE_EUR * 100),
        currency='eur',
        recurring={'interval': 'month'},
        lookup_key='plume_premium_monthly_eur',
        metadata={'plan': 'premium_monthly'},
    )
    _PRICE_ID_CACHE = price.id
    logger.info(f'Created Stripe Premium price: {price.id}')
    return price.id


async def create_premium_checkout(user_id: str, user_email: str, origin_url: str) -> Dict[str, Any]:
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    price_id = _get_or_create_price()

    sb = get_admin_client()
    profile = sb.table('profiles').select('stripe_customer_id').eq('id', user_id).maybe_single().execute()
    customer_id = profile.data.get('stripe_customer_id') if profile and profile.data else None
    if not customer_id:
        customer = stripe.Customer.create(email=user_email, metadata={'supabase_user_id': user_id})
        customer_id = customer.id
        try:
            sb.table('profiles').update({'stripe_customer_id': customer_id}).eq('id', user_id).execute()
        except Exception as e:
            logger.warning(f'Cannot save customer_id: {e}')

    origin = origin_url.rstrip('/')
    session = stripe.checkout.Session.create(
        mode='subscription',
        customer=customer_id,
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=f'{origin}/premium/succes?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{origin}/premium',
        metadata={'user_id': user_id, 'plan': 'premium_monthly'},
        subscription_data={
            'metadata': {'user_id': user_id},
            'trial_period_days': 7,  # 7 jours gratuits, annulable a tout moment
        },
        locale='fr',
    )
    return {'url': session.url, 'session_id': session.id}


async def get_subscription_status(user_id: str) -> Dict[str, Any]:
    sb = get_admin_client()
    profile = sb.table('profiles').select('premium_status,premium_until,stripe_subscription_id').eq('id', user_id).maybe_single().execute()
    if not profile or not profile.data:
        return {'is_premium': False, 'status': 'free'}
    p = profile.data
    until = p.get('premium_until')
    is_active = p.get('premium_status') == 'active'
    if until:
        try:
            until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            is_active = is_active and until_dt > datetime.now(timezone.utc)
        except Exception:
            pass
    return {
        'is_premium': is_active,
        'status': p.get('premium_status', 'free'),
        'premium_until': until,
        'subscription_id': p.get('stripe_subscription_id'),
    }


async def create_billing_portal(user_id: str, return_url: str) -> str:
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    sb = get_admin_client()
    profile = sb.table('profiles').select('stripe_customer_id').eq('id', user_id).maybe_single().execute()
    customer_id = profile.data.get('stripe_customer_id') if profile and profile.data else None
    if not customer_id:
        raise HTTPException(status_code=404, detail='Aucun abonnement actif')
    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return session.url


def handle_subscription_webhook(event: Any) -> None:
    sb = get_admin_client()
    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})

    if event_type == 'checkout.session.completed':
        if data.get('mode') != 'subscription':
            return
        user_id = (data.get('metadata') or {}).get('user_id')
        subscription_id = data.get('subscription')
        customer_id = data.get('customer')
        if user_id and subscription_id:
            sb.table('profiles').update({
                'premium_status': 'active',
                'stripe_subscription_id': subscription_id,
                'stripe_customer_id': customer_id,
            }).eq('id', user_id).execute()

    elif event_type in ('customer.subscription.updated', 'customer.subscription.created'):
        user_id = (data.get('metadata') or {}).get('user_id')
        if not user_id:
            return
        status = data.get('status')
        period_end = data.get('current_period_end')
        period_end_iso = datetime.fromtimestamp(period_end, tz=timezone.utc).isoformat() if period_end else None
        is_active = status == 'active'
        sb.table('profiles').update({
            'premium_status': 'active' if is_active else status,
            'premium_until': period_end_iso,
            'stripe_subscription_id': data.get('id'),
        }).eq('id', user_id).execute()
        try:
            sb.table('subscriptions').upsert({
                'user_id': user_id,
                'stripe_subscription_id': data.get('id'),
                'stripe_customer_id': data.get('customer'),
                'status': status,
                'current_period_start': datetime.fromtimestamp(data.get('current_period_start'), tz=timezone.utc).isoformat() if data.get('current_period_start') else None,
                'current_period_end': period_end_iso,
                'cancel_at_period_end': data.get('cancel_at_period_end', False),
            }, on_conflict='stripe_subscription_id').execute()
        except Exception as e:
            logger.warning(f'Cannot upsert subscription: {e}')

    elif event_type == 'customer.subscription.deleted':
        user_id = (data.get('metadata') or {}).get('user_id')
        if user_id:
            sb.table('profiles').update({'premium_status': 'canceled'}).eq('id', user_id).execute()
