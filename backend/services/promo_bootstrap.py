"""
Bootstrap des codes promo permanents (F500 2026-02).

Insère/met à jour au démarrage backend les codes que l'admin utilise
partout sur le site pour tester l'accès complet aux PDF sans passer
par Stripe.

TOUT2026 : bypass 100% sur TOUS les produits, réservé admin (SEC-004).
"""
from __future__ import annotations
import logging
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def ensure_permanent_promo_codes() -> None:
    """Idempotent : garantit la présence des codes permanents en base."""
    permanent_codes = [
        {
            'code': 'TOUT2026',
            'active': True,
            'max_uses': None,     # illimité
            'used_count': 0,
            'discount_type': 'bypass',
            'discount_value': 100,
            'label': 'Bypass admin 100% — accès à tous les PDF',
            'note': 'F500 2026-02 — admin only via SEC-004 try_consume_promo',
        },
    ]

    try:
        sb = get_admin_client()
        for c in permanent_codes:
            existing = sb.table('promo_codes').select('code, active, max_uses').eq('code', c['code']).maybe_single().execute()
            if existing and existing.data:
                # S'assure qu'il est actif et illimité (idempotent)
                if not existing.data.get('active') or existing.data.get('max_uses') is not None:
                    sb.table('promo_codes').update({'active': True, 'max_uses': None}).eq('code', c['code']).execute()
                    logger.info(f'[promo_bootstrap] réactivé/déplafonné : {c["code"]}')
                else:
                    logger.info(f'[promo_bootstrap] OK : {c["code"]} déjà en base')
            else:
                sb.table('promo_codes').insert(c).execute()
                logger.info(f'[promo_bootstrap] ✓ inséré : {c["code"]}')
    except Exception as e:
        logger.warning(f'[promo_bootstrap] échec bootstrap (non-bloquant) : {e}')
