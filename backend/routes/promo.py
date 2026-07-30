"""
Route publique de validation de code promo.
POST /api/promo/validate { code, product?, amount? } → { valid, discount_amount, discount_percent, final_amount, message }

Ne facture rien, ne consomme rien : renvoie uniquement les infos de réduction pour affichage front.
La vraie application de la réduction se fait côté Stripe lors de la création de la session checkout.
"""
from __future__ import annotations
import logging
import os
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
import stripe

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/promo', tags=['promo'])
stripe.api_key = os.environ.get('STRIPE_API_KEY', '')


class ValidatePayload(BaseModel):
    code: str
    product: Optional[str] = None   # ex: 'theme_natal_pdf_oneshot'
    amount: Optional[float] = None  # montant original en EUR


@router.post('/validate')
async def validate_promo(payload: ValidatePayload):
    code = (payload.code or '').strip().upper()
    if not code:
        return {'valid': False, 'message': 'Code vide.'}

    # ─── 1) Cherche d'abord dans la table promo_codes locale (bypass admin) ───
    sb = get_admin_client()
    try:
        r = sb.table('promo_codes').select('code, active, max_uses, used_count').eq('code', code).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[promo/validate] DB lookup failed: {e}')
        r = None

    if r and r.data and r.data.get('active'):
        row = r.data
        # Vérifie quota
        max_uses = row.get('max_uses')
        used = row.get('used_count') or 0
        if max_uses is not None and used >= max_uses:
            return {'valid': False, 'message': 'Ce code a atteint son quota d\u2019utilisation.'}
        # Bypass admin 100% : la réduction réelle ne s'applique QUE si l'utilisateur
        # est admin authentifié au checkout. On indique 100% en affichage + admin_only=True.
        original = float(payload.amount or 0)
        return {
            'valid': True, 'source': 'local',
            'discount_percent': 100, 'discount_amount': original, 'final_amount': 0,
            'message': 'Code administrateur reconnu — bypass appliqué au paiement si tu es connecté en admin.',
            'admin_only': True,
        }

    # ─── 2) Sinon, tente Stripe Promotion Codes ───
    if not stripe.api_key:
        return {'valid': False, 'message': 'Code invalide ou expiré.'}
    try:
        result = stripe.PromotionCode.list(code=code, active=True, limit=1)
        promos = result.data if result and hasattr(result, 'data') else []
        if not promos:
            return {'valid': False, 'message': 'Code invalide ou expiré.'}
        promo = promos[0]
        coupon = promo.coupon
        original = float(payload.amount or 0)
        if coupon.percent_off:
            pct = float(coupon.percent_off)
            discount = round(original * pct / 100, 2)
            final = max(0, original - discount)
            return {'valid': True, 'source': 'stripe', 'stripe_promo_id': promo.id, 'discount_percent': pct, 'discount_amount': discount, 'final_amount': final, 'message': f'Code valide — réduction de {int(pct)}% appliquée par Stripe au paiement.'}
        if coupon.amount_off:
            amt = float(coupon.amount_off) / 100.0  # cents → EUR
            final = max(0, original - amt)
            return {'valid': True, 'source': 'stripe', 'stripe_promo_id': promo.id, 'discount_amount': amt, 'final_amount': final, 'message': f'Code valide — réduction de {amt:.2f}€ appliquée par Stripe au paiement.'}
        return {'valid': False, 'message': 'Code Stripe sans réduction paramétrée.'}
    except Exception as e:
        logger.warning(f'[promo/validate] Stripe lookup failed: {e}')
        return {'valid': False, 'message': 'Code invalide ou expiré.'}
