"""
Route /api/subscriptions/cercle-solena — abonnement mensuel 19€/mois.

Business logic :
  - 3 crédits offerts au 1er paiement + à chaque renouvellement mensuel
  - Accès à la communauté "Cercle Soléna" (Discord/DM) — booléen dans profiles
  - Résiliable à tout moment via le Portail Client Stripe

Endpoints :
  POST /api/subscriptions/cercle-solena/checkout  → Session Stripe (mode='subscription')
  GET  /api/subscriptions/cercle-solena/status    → statut abonnement de l'utilisateur
  POST /api/subscriptions/portal                  → lien portail Stripe pour gérer l'abo

Webhook events consommés (Stripe → /api/webhook/stripe) :
  customer.subscription.created  → active + crédite +3
  invoice.payment_succeeded      → crédite +3 (renouvellement mensuel)
  customer.subscription.updated  → sync status
  customer.subscription.deleted  → passe status=canceled (accès jusqu'à period_end)

⚠️  Le PRICE_ID recurring doit être créé côté Dashboard Stripe :
    Products → New product → "Cercle Soléna" → Recurring 19€ EUR/mois
    Puis coller price_XXX dans .env : STRIPE_CERCLE_SOLENA_PRICE_ID=price_...
"""
from __future__ import annotations
import os
import logging
from typing import Optional
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from config import get_settings
from services.supabase_client import get_admin_client
from middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/subscriptions', tags=['subscriptions'])

# Config Stripe global (partagé, thread-safe pour le SDK python)
_settings = get_settings()
stripe.api_key = _settings.STRIPE_API_KEY

# Constantes métier
CERCLE_MONTHLY_CREDITS = 3
CERCLE_PRODUCT_KEY = 'cercle_solena'


class CheckoutPayload(BaseModel):
    origin_url: str  # ex: 'https://plume-astrale.fr'


def _get_price_id() -> str:
    price_id = os.environ.get('STRIPE_CERCLE_SOLENA_PRICE_ID', '').strip()
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=(
                "L'abonnement n'est pas encore configuré. Merci de configurer "
                "STRIPE_CERCLE_SOLENA_PRICE_ID dans les variables d'environnement."
            ),
        )
    return price_id


@router.post('/cercle-solena/checkout')
async def cercle_solena_checkout(
    payload: CheckoutPayload,
    user: dict = Depends(get_current_user),
):
    """Crée une session Stripe en mode 'subscription' pour l'utilisateur connecté."""
    price_id = _get_price_id()
    origin = payload.origin_url.rstrip('/')
    supabase = get_admin_client()

    # Récupère/crée un customer Stripe lié à ce user Supabase (persisté dans profiles.stripe_customer_id)
    prof_resp = supabase.table('profiles').select('id, email, stripe_customer_id').eq('id', user['id']).limit(1).execute()
    profile = (prof_resp.data or [None])[0]
    if not profile:
        raise HTTPException(status_code=404, detail='Profil introuvable')

    customer_id = profile.get('stripe_customer_id')
    if not customer_id:
        customer = stripe.Customer.create(
            email=profile.get('email') or user.get('email'),
            metadata={'supabase_user_id': user['id'], 'source': 'cercle_solena'},
        )
        customer_id = customer.id
        supabase.table('profiles').update({'stripe_customer_id': customer_id}).eq('id', user['id']).execute()

    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            customer=customer_id,
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=f"{origin}/cercle-solena/succes?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{origin}/cercle-solena",
            metadata={
                'product': CERCLE_PRODUCT_KEY,
                'supabase_user_id': user['id'],
            },
            subscription_data={
                'metadata': {
                    'product': CERCLE_PRODUCT_KEY,
                    'supabase_user_id': user['id'],
                },
            },
            locale='fr',
            allow_promotion_codes=True,
        )
    except stripe.error.StripeError as e:
        logger.error(f'[cercle_solena] Stripe error: {e}')
        raise HTTPException(status_code=502, detail=f'Erreur Stripe: {e.user_message or str(e)}')

    return {'url': session.url, 'session_id': session.id}


@router.get('/cercle-solena/status')
async def cercle_solena_status(user: dict = Depends(get_current_user)):
    """Retourne le statut de l'abonnement Cercle Soléna de l'utilisateur."""
    supabase = get_admin_client()
    resp = (
        supabase.table('subscriptions')
        .select('id, stripe_subscription_id, status, current_period_end, cancel_at_period_end, created_at')
        .eq('user_id', user['id'])
        .eq('product', CERCLE_PRODUCT_KEY)
        .order('created_at', desc=True)
        .limit(1)
        .execute()
    )
    sub = (resp.data or [None])[0]
    if not sub:
        return {'active': False, 'subscription': None}

    active = sub.get('status') in ('active', 'trialing', 'past_due')
    return {'active': active, 'subscription': sub}


@router.post('/portal')
async def create_portal_session(payload: CheckoutPayload, user: dict = Depends(get_current_user)):
    """Génère un lien vers le Portail Client Stripe (gestion / résiliation d'abo)."""
    supabase = get_admin_client()
    prof = supabase.table('profiles').select('stripe_customer_id').eq('id', user['id']).limit(1).execute()
    customer_id = ((prof.data or [{}])[0] or {}).get('stripe_customer_id')
    if not customer_id:
        raise HTTPException(status_code=404, detail='Pas de client Stripe associé à ce profil')

    try:
        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=payload.origin_url.rstrip('/') + '/mon-compte',
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=f'Erreur Stripe portal: {e.user_message or str(e)}')
    return {'url': portal.url}


# ─── Webhook helpers (appelés depuis le webhook /api/webhook/stripe) ──────────

async def handle_subscription_event(event: dict) -> Optional[str]:
    """Traite les événements Stripe liés à Cercle Soléna.

    Retourne un log message si l'event a été traité, None sinon.
    """
    ev_type = event.get('type', '')
    obj = event.get('data', {}).get('object', {}) or {}
    supabase = get_admin_client()

    # customer.subscription.* → sync la ligne subscriptions
    if ev_type in ('customer.subscription.created', 'customer.subscription.updated', 'customer.subscription.deleted'):
        product = (obj.get('metadata') or {}).get('product')
        if product != CERCLE_PRODUCT_KEY:
            return None  # pas notre produit

        user_id = (obj.get('metadata') or {}).get('supabase_user_id')
        if not user_id:
            logger.warning(f'[cercle_solena] {ev_type} sans supabase_user_id')
            return None

        status = obj.get('status', 'unknown')
        current_period_end = obj.get('current_period_end')
        current_period_end_iso = (
            datetime.fromtimestamp(current_period_end, tz=timezone.utc).isoformat()
            if current_period_end else None
        )
        cancel_at_period_end = bool(obj.get('cancel_at_period_end'))

        row = {
            'user_id': user_id,
            'product': CERCLE_PRODUCT_KEY,
            'stripe_subscription_id': obj.get('id'),
            'stripe_customer_id': obj.get('customer'),
            'status': 'canceled' if ev_type == 'customer.subscription.deleted' else status,
            'current_period_end': current_period_end_iso,
            'cancel_at_period_end': cancel_at_period_end,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }

        # Upsert sur stripe_subscription_id (unique)
        supabase.table('subscriptions').upsert(row, on_conflict='stripe_subscription_id').execute()

        # Sur .created : marque le profil comme membre Cercle
        if ev_type == 'customer.subscription.created':
            supabase.table('profiles').update({'is_cercle_member': True}).eq('id', user_id).execute()
        elif ev_type == 'customer.subscription.deleted':
            supabase.table('profiles').update({'is_cercle_member': False}).eq('id', user_id).execute()

        return f'[cercle_solena] {ev_type} handled for user {user_id}'

    # invoice.payment_succeeded → crédite +3 (mensuel + 1er paiement)
    if ev_type == 'invoice.payment_succeeded':
        sub_id = obj.get('subscription')
        if not sub_id:
            return None
        # Retrouve le user_id via la table subscriptions
        sub_resp = supabase.table('subscriptions').select('user_id, product').eq('stripe_subscription_id', sub_id).limit(1).execute()
        sub_row = (sub_resp.data or [None])[0]
        if not sub_row or sub_row.get('product') != CERCLE_PRODUCT_KEY:
            return None
        user_id = sub_row['user_id']

        # Idempotence : évite de créditer 2× le même invoice
        invoice_id = obj.get('id')
        existing = supabase.table('credit_grants').select('id').eq('external_id', invoice_id).eq('reason', 'cercle_solena').limit(1).execute()
        if existing.data:
            return f'[cercle_solena] invoice {invoice_id} déjà crédité (idempotent)'

        # Récupère les crédits actuels + ajoute 3
        prof = supabase.table('profiles').select('credits').eq('id', user_id).limit(1).execute()
        current = ((prof.data or [{}])[0] or {}).get('credits', 0) or 0
        new_credits = current + CERCLE_MONTHLY_CREDITS
        supabase.table('profiles').update({'credits': new_credits}).eq('id', user_id).execute()

        # Trace le grant (idempotence + audit)
        supabase.table('credit_grants').insert({
            'user_id': user_id,
            'amount': CERCLE_MONTHLY_CREDITS,
            'reason': 'cercle_solena',
            'external_id': invoice_id,
            'granted_at': datetime.now(timezone.utc).isoformat(),
        }).execute()

        return f'[cercle_solena] +{CERCLE_MONTHLY_CREDITS} crédits pour user {user_id} (invoice {invoice_id})'

    return None
