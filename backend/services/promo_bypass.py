"""
Helper : bypass Stripe checkout quand un code promo 100% remise est fourni.
Utilise par les produits one-shot (Kabbale, Rencontres Ultime).

Logique :
- Valide le code promo dans promo_codes (active=true, used_count < max_uses).
- Incrémente used_count immédiatement (best-effort).
- Retourne True si le code est valide, False sinon.

Note : le tracking par utilisateur (promo_code_redemptions) n'est PAS fait ici
car ces checkouts sont publics (guest checkouts). On protège via max_uses global.
"""
from __future__ import annotations
import logging
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def try_consume_promo(code: str | None) -> bool:
    """Vérifie et consomme un code promo pour un checkout one-shot.
    Retourne True si le code est valide (100% remise), False sinon."""
    if not code or not code.strip():
        return False
    normalized = code.strip().upper()
    try:
        sb = get_admin_client()
        res = sb.table('promo_codes').select('*').eq('code', normalized).eq('active', True).maybe_single().execute()
        if not res or not res.data:
            return False
        d = res.data
        max_uses = d.get('max_uses')
        used = d.get('used_count', 0) or 0
        if max_uses is not None and used >= max_uses:
            return False
        # Incrémenter le compteur (best-effort, non-atomique — acceptable pour codes internes)
        try:
            sb.table('promo_codes').update({'used_count': used + 1}).eq('code', normalized).execute()
        except Exception as e:
            logger.warning(f'[promo_bypass] could not increment used_count for {normalized}: {e}')
        return True
    except Exception as e:
        logger.warning(f'[promo_bypass] validation failed for {code!r}: {e}')
        return False
