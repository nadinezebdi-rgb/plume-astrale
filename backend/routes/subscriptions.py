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
# ─── Cercle Soléna : 2 tiers (Gary Vee refonte 2026-02) ────────────────
# Normal   : 14,99€/mo → +100 chat_credits/mois (chat-only)
# Premium  : 29€/mo    → +250 chat_credits/mois + accès communauté renforcé
CERCLE_MONTHLY_CHAT_CREDITS = 100          # tier normal (F500 2026-02: 50→100, alignement Pack Régulier)
CERCLE_PREMIUM_MONTHLY_CHAT_CREDITS = 250  # tier premium (F500 2026-02: 150→250, alignement Pack Généreux)
CERCLE_PRODUCT_KEY = 'cercle_solena'
CERCLE_PREMIUM_PRODUCT_KEY = 'cercle_solena_premium'


class CheckoutPayload(BaseModel):
    origin_url: str  # ex: 'https://plume-astrale.fr'
    with_trial: bool = False  # True → premier mois offert (trial_period_days=30)
    tier: str = 'normal'      # 'normal' | 'premium'


def _get_price_id(tier: str = 'normal') -> str:
    env_key = 'STRIPE_CERCLE_SOLENA_PRICE_ID' if tier == 'normal' else 'STRIPE_CERCLE_SOLENA_PREMIUM_PRICE_ID'
    price_id = os.environ.get(env_key, '').strip()
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail=(
                f"L'abonnement '{tier}' n'est pas encore configuré. Merci de configurer "
                f"{env_key} dans les variables d'environnement."
            ),
        )
    return price_id


def _product_key_for_tier(tier: str) -> str:
    return CERCLE_PREMIUM_PRODUCT_KEY if tier == 'premium' else CERCLE_PRODUCT_KEY


def _monthly_chat_credits_for_tier(tier: str) -> int:
    return CERCLE_PREMIUM_MONTHLY_CHAT_CREDITS if tier == 'premium' else CERCLE_MONTHLY_CHAT_CREDITS


@router.post('/cercle-solena/checkout')
async def cercle_solena_checkout(
    payload: CheckoutPayload,
    user: dict = Depends(get_current_user),
):
    """Crée une session Stripe en mode 'subscription' pour l'utilisateur connecté.
    tier='normal' (14,99€/mo, 50 chat cr) ou 'premium' (29€/mo, 150 chat cr).
    """
    tier = payload.tier if payload.tier in ('normal', 'premium') else 'normal'
    price_id = _get_price_id(tier)
    product_key = _product_key_for_tier(tier)
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
            metadata={'supabase_user_id': user['id'], 'source': product_key},
        )
        customer_id = customer.id
        supabase.table('profiles').update({'stripe_customer_id': customer_id}).eq('id', user['id']).execute()

    try:
        subscription_data = {
            'metadata': {
                'product': product_key,
                'tier': tier,
                'supabase_user_id': user['id'],
            },
        }
        # Trial 30 jours (offert après un achat PDF — 1 seul par utilisateur, tous tiers confondus)
        if payload.with_trial:
            grant_check = supabase.table('credit_grants').select('id').eq(
                'user_id', user['id']
            ).eq('reason', 'cercle_solena_trial_used').limit(1).execute()
            if not grant_check.data:
                subscription_data['trial_period_days'] = 30
                supabase.table('credit_grants').insert({
                    'user_id': user['id'],
                    'amount': 0,
                    'reason': 'cercle_solena_trial_used',
                    'external_id': f'trial_grant_{user["id"]}',
                    'granted_at': datetime.now(timezone.utc).isoformat(),
                }).execute()

        session = stripe.checkout.Session.create(
            mode='subscription',
            customer=customer_id,
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=f"{origin}/cercle-solena/succes?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{origin}/cercle-solena",
            metadata={
                'product': product_key,
                'tier': tier,
                'supabase_user_id': user['id'],
                'trial': 'true' if payload.with_trial else 'false',
            },
            subscription_data=subscription_data,
            locale='fr',
            allow_promotion_codes=True,
        )
    except stripe.error.StripeError as e:
        logger.error(f'[{product_key}] Stripe error: {e}')
        raise HTTPException(status_code=502, detail=f'Erreur Stripe: {e.user_message or str(e)}')

    return {'url': session.url, 'session_id': session.id, 'tier': tier}


@router.get('/cercle-solena/status')
async def cercle_solena_status(user: dict = Depends(get_current_user)):
    """Retourne le statut de l'abonnement Cercle Soléna (tous tiers) de l'utilisateur.
    Fallback safe si la migration Feb 2026 (subscriptions.product, subscriptions.tier) n'est pas appliquée.
    """
    supabase = get_admin_client()
    try:
        resp = (
            supabase.table('subscriptions')
            .select('id, stripe_subscription_id, status, current_period_end, cancel_at_period_end, created_at, product')
            .eq('user_id', user['id'])
            .in_('product', [CERCLE_PRODUCT_KEY, CERCLE_PREMIUM_PRODUCT_KEY])
            .order('created_at', desc=True)
            .limit(1)
            .execute()
        )
    except Exception as e:
        # Colonne 'product' pas encore migrée en base : contrat safe
        logger.warning(f"[cercle_solena/status] fallback (migration missing?): {e}")
        return {'active': False, 'subscription': None, 'tier': None}

    sub = (resp.data or [None])[0]
    if not sub:
        return {'active': False, 'subscription': None, 'tier': None}

    active = sub.get('status') in ('active', 'trialing', 'past_due')
    tier = 'premium' if sub.get('product') == CERCLE_PREMIUM_PRODUCT_KEY else 'normal'
    return {'active': active, 'subscription': sub, 'tier': tier}


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
        md = obj.get('metadata') or {}
        product = md.get('product')
        if product not in (CERCLE_PRODUCT_KEY, CERCLE_PREMIUM_PRODUCT_KEY):
            return None  # pas notre produit

        user_id = md.get('supabase_user_id')
        if not user_id:
            logger.warning(f'[{product}] {ev_type} sans supabase_user_id')
            return None

        tier = md.get('tier') or ('premium' if product == CERCLE_PREMIUM_PRODUCT_KEY else 'normal')
        status = obj.get('status', 'unknown')
        current_period_end = obj.get('current_period_end')
        current_period_end_iso = (
            datetime.fromtimestamp(current_period_end, tz=timezone.utc).isoformat()
            if current_period_end else None
        )
        cancel_at_period_end = bool(obj.get('cancel_at_period_end'))

        row = {
            'user_id': user_id,
            'product': product,
            'stripe_subscription_id': obj.get('id'),
            'stripe_customer_id': obj.get('customer'),
            'status': 'canceled' if ev_type == 'customer.subscription.deleted' else status,
            'current_period_end': current_period_end_iso,
            'cancel_at_period_end': cancel_at_period_end,
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }

        # Upsert sur stripe_subscription_id (unique)
        try:
            supabase.table('subscriptions').upsert(row, on_conflict='stripe_subscription_id').execute()
        except Exception as e:
            # Colonnes product/tier pas encore migrées → retry sans ces champs
            logger.warning(f'[{product}] upsert subscriptions échec (migration missing?) : {e}. Retry sans product/tier.')
            fallback = {k: v for k, v in row.items() if k not in ('product',)}
            try:
                supabase.table('subscriptions').upsert(fallback, on_conflict='stripe_subscription_id').execute()
            except Exception as e2:
                logger.error(f'[{product}] upsert subscriptions échec définitif : {e2}')

        # Sur .created : marque le profil comme membre Cercle + trace le tier
        if ev_type == 'customer.subscription.created':
            update_data = {'is_cercle_member': True}
            try:
                # cercle_tier peut ne pas exister avant la migration Feb 2026
                update_data['cercle_tier'] = tier
                supabase.table('profiles').update(update_data).eq('id', user_id).execute()
            except Exception:
                supabase.table('profiles').update({'is_cercle_member': True}).eq('id', user_id).execute()
        elif ev_type == 'customer.subscription.deleted':
            supabase.table('profiles').update({'is_cercle_member': False}).eq('id', user_id).execute()

        return f'[{product}] {ev_type} handled for user {user_id} (tier={tier})'

    # invoice.payment_succeeded → crédite chat_credits selon le tier
    if ev_type == 'invoice.payment_succeeded':
        sub_id = obj.get('subscription')
        if not sub_id:
            return None
        # Retrouve le user_id via la table subscriptions
        try:
            sub_resp = supabase.table('subscriptions').select('user_id, product').eq('stripe_subscription_id', sub_id).limit(1).execute()
        except Exception as e:
            logger.warning(f'[invoice.payment_succeeded] fetch subscriptions échec (migration missing?) : {e}')
            return None
        sub_row = (sub_resp.data or [None])[0]
        if not sub_row or sub_row.get('product') not in (CERCLE_PRODUCT_KEY, CERCLE_PREMIUM_PRODUCT_KEY):
            return None
        user_id = sub_row['user_id']
        product = sub_row['product']
        tier = 'premium' if product == CERCLE_PREMIUM_PRODUCT_KEY else 'normal'
        chat_credits_to_grant = _monthly_chat_credits_for_tier(tier)

        # Idempotence : évite de créditer 2× le même invoice
        invoice_id = obj.get('id')
        existing = supabase.table('credit_grants').select('id').eq('external_id', invoice_id).eq('reason', product).limit(1).execute()
        if existing.data:
            return f'[{product}] invoice {invoice_id} déjà crédité (idempotent)'

        # Crédite chat_credit_balance via le wallet_service (fallback safe si migration pas encore appliquée)
        try:
            from services.wallet_service import add_chat_credits
            new_balance = await add_chat_credits(user_id, chat_credits_to_grant, f'Renouvellement {product}')
            logger.info(f'[{product}] chat_credits crédités user {user_id} : +{chat_credits_to_grant} → total {new_balance}')
        except Exception as e:
            logger.warning(f'[{product}] add_chat_credits failed (migration missing?): {e}')

        # Trace le grant (idempotence + audit)
        supabase.table('credit_grants').insert({
            'user_id': user_id,
            'amount': chat_credits_to_grant,
            'reason': product,
            'external_id': invoice_id,
            'granted_at': datetime.now(timezone.utc).isoformat(),
        }).execute()

        return f'[{product}] +{chat_credits_to_grant} chat_credits pour user {user_id} (invoice {invoice_id})'

    return None
