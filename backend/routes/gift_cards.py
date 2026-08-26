"""Routes carte cadeau — achat + rédemption."""
from __future__ import annotations
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, field_validator

from services.gift_card_service import (
    GIFT_PRODUCTS,
    create_gift_card_checkout,
    get_gift_card_public,
    redeem_gift_card,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/gift-cards', tags=['gift-cards'])


class PurchaseRequest(BaseModel):
    product_kind: str = Field(pattern=r'^(theme_natal|voyage_karmique|kabbale)$')
    purchaser_email: EmailStr
    purchaser_first_name: str = Field(min_length=1, max_length=80)
    recipient_email: EmailStr
    recipient_first_name: Optional[str] = Field(default=None, max_length=80)
    personal_message: Optional[str] = Field(default=None, max_length=800)
    deliver_at: Optional[str] = Field(default=None)  # ISO datetime ou null = immédiat


class RedeemRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    birth_time: Optional[str] = Field(default=None, pattern=r'^\d{2}:\d{2}$')
    birth_place: str = Field(min_length=2, max_length=120)


@router.get('/products')
async def list_gift_products():
    """Catalogue des produits offrables (label + prix + description)."""
    return {
        'products': [
            {'kind': k, **v} for k, v in GIFT_PRODUCTS.items()
        ]
    }


@router.post('/purchase')
async def purchase_gift_card(payload: PurchaseRequest, request: Request):
    """Crée la session Stripe checkout et retourne l'URL de paiement."""
    origin = str(request.base_url).rstrip('/')
    try:
        result = await create_gift_card_checkout(
            product_kind=payload.product_kind,
            purchaser_email=payload.purchaser_email.lower(),
            purchaser_first_name=payload.purchaser_first_name.strip(),
            recipient_email=payload.recipient_email.lower(),
            recipient_first_name=(payload.recipient_first_name or '').strip() or None,
            personal_message=(payload.personal_message or '').strip() or None,
            deliver_at=payload.deliver_at,
            origin=origin,
        )
        return {'success': True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f'[gift_card] purchase failed: {e}')
        raise HTTPException(status_code=500, detail='Erreur lors de la création du paiement.')


@router.get('/{code}')
async def get_gift_card(code: str):
    """Renvoie les infos publiques d'une carte cadeau (pour la page rédemption)."""
    info = get_gift_card_public(code.upper())
    if not info:
        raise HTTPException(status_code=404, detail='Ce code cadeau est introuvable ou pas encore actif.')
    return info


@router.post('/{code}/redeem')
async def redeem(code: str, payload: RedeemRequest):
    """Le destinataire complète ses données et déclenche la génération du PDF."""
    try:
        result = await redeem_gift_card(
            code=code.upper(),
            first_name=payload.first_name.strip(),
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place.strip(),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f'[gift_card] redeem failed: {e}')
        raise HTTPException(status_code=500, detail='Erreur lors de la génération du PDF.')
