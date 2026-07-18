"""
Auto-réparation des produits one-shot : si le webhook Stripe n'atteint pas le
backend (non configuré côté Stripe, ou down au moment du paiement), les pages
succès pollent /status — on en profite pour vérifier le paiement DIRECTEMENT
auprès de Stripe et déclencher la génération/livraison manquante.
"""
from __future__ import annotations
import logging
import os

logger = logging.getLogger(__name__)

_inflight: set = set()


async def self_heal_if_paid(session_id: str, already_delivered: bool, handler) -> None:
    """Si la session Stripe est payée mais rien n'a été livré, lance le handler produit.
    Idempotent (garde in-flight + les handlers vérifient pdf_path)."""
    if already_delivered or not session_id or not session_id.startswith('cs_'):
        return
    if session_id in _inflight:
        return
    _inflight.add(session_id)
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        sc = StripeCheckout(api_key=os.environ['STRIPE_API_KEY'], webhook_url='')
        st = await sc.get_checkout_status(session_id)
        if getattr(st, 'payment_status', '') == 'paid':
            logger.info(f'[self_heal] paiement confirmé via polling Stripe → livraison déclenchée ({session_id})')
            await handler(session_id)
    except Exception as e:
        logger.warning(f'[self_heal] {session_id}: {e}')
    finally:
        _inflight.discard(session_id)
