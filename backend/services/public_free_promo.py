"""Promotion publique « Thème Natal offert » (limitée dans le temps).

Contrairement à `promo_bypass` (codes admin uniquement, SEC-004), ce code est
volontairement ouvert à tous, mais strictement encadré :
  - un seul produit (Thème Natal one-shot) ;
  - une date de fin (après quoi le code est refusé) ;
  - une commande gratuite par e-mail ;
  - un plafond global de commandes (coût IA/API).

Réglages par variables d'environnement (valeurs par défaut ci-dessous) :
  FREE_NATAL_PROMO_CODE   code à saisir          (NATALOFFERT)
  FREE_NATAL_PROMO_UNTIL  fin ISO 8601 avec fuseau (lundi 5 oct. 2026, 23:59 Paris)
  FREE_NATAL_PROMO_MAX    plafond de commandes    (500)
  FREE_NATAL_PROMO_ENABLED=false pour couper la promo immédiatement.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

PRODUCT = 'theme_natal_pdf_oneshot'
_DEFAULT_CODE = 'NATALOFFERT'
_DEFAULT_UNTIL = '2026-10-05T23:59:59+02:00'
_DEFAULT_MAX = 500


def _cfg_code() -> str:
    return (os.environ.get('FREE_NATAL_PROMO_CODE') or _DEFAULT_CODE).strip().upper()


def _cfg_until() -> datetime:
    raw = os.environ.get('FREE_NATAL_PROMO_UNTIL') or _DEFAULT_UNTIL
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        dt = datetime.fromisoformat(_DEFAULT_UNTIL)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _cfg_max() -> int:
    try:
        return int(os.environ.get('FREE_NATAL_PROMO_MAX') or _DEFAULT_MAX)
    except ValueError:
        return _DEFAULT_MAX


def is_active_code(code: Optional[str], product: Optional[str] = PRODUCT, now: Optional[datetime] = None) -> bool:
    """Le code est-il celui de la promo, dans sa fenêtre de validité, pour le bon produit ?"""
    if os.environ.get('FREE_NATAL_PROMO_ENABLED', 'true').lower() in ('false', '0', 'no'):
        return False
    if not code or code.strip().upper() != _cfg_code():
        return False
    if product and product != PRODUCT:
        return False
    return (now or datetime.now(timezone.utc)) <= _cfg_until()


def _redemptions(email: Optional[str] = None):
    from services.supabase_client import get_admin_client
    sb = get_admin_client()
    q = sb.table('payment_transactions').select('session_id', count='exact') \
        .eq('pack_id', PRODUCT).contains('metadata', {'public_free_promo': True})
    if email:
        q = q.eq('user_email', email)
    return q.limit(1).execute()


def check_redeemable(code: Optional[str], email: str) -> tuple[bool, str]:
    """(ok, message). Vérifie fenêtre, plafond global et unicité par e-mail."""
    if not is_active_code(code):
        return False, 'Code invalide ou expiré.'
    email = (email or '').strip().lower()
    try:
        if _redemptions(email).count:
            return False, 'Ce code a déjà été utilisé avec cette adresse e-mail.'
        if (_redemptions().count or 0) >= _cfg_max():
            return False, 'La promotion a atteint son nombre maximum de thèmes offerts.'
    except Exception as e:
        # En cas de doute on refuse : un échec de comptage ne doit pas ouvrir la promo.
        logger.warning(f'[public_free_promo] redemption check failed: {e}')
        return False, 'Vérification impossible pour le moment, réessaie dans un instant.'
    return True, 'Thème Natal offert — aucun paiement demandé.'
