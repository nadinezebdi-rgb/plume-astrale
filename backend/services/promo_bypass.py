"""
SEC-004 — Bypass Stripe via code promo 100% remise (STRICT ADMIN ONLY).

Avant : n'importe qui pouvant deviner un code (ADMIN26, PLUME15…) obtenait
un PDF premium gratuit via un guest checkout.

Après :
1. Le bypass exige un Bearer token JWT valide dont le compte est `is_admin=true`.
2. Décrément atomique de `used_count` via update filtré (conditional CAS).
3. Trace de chaque redemption dans `promo_code_redemptions` (best-effort).

Les codes % (KABBALE20, etc.) ne sont PAS concernés : ils passent toujours
par Stripe avec la remise appliquée, aucun bypass.
"""
from __future__ import annotations
import logging
from typing import Optional
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def _is_admin(user_id: str) -> bool:
    """Vérifie is_admin=true sur le profil (source de vérité)."""
    try:
        sb = get_admin_client()
        r = sb.table('profiles').select('is_admin').eq('id', user_id).maybe_single().execute()
        return bool(r and r.data and r.data.get('is_admin'))
    except Exception as e:
        logger.warning(f'[promo_bypass] is_admin check failed for {user_id}: {e}')
        return False


def try_consume_promo(
    code: Optional[str],
    admin_user: Optional[dict] = None,
    product: Optional[str] = None,
) -> bool:
    """Consomme un code promo 100% remise.

    Retourne True uniquement si :
      1. Un `admin_user` authentifié est fourni ET `is_admin=true` en base.
      2. Le code existe, actif, quota non atteint.
      3. Le décrément atomique a réussi (CAS).

    Trace la redemption dans `promo_code_redemptions` (best-effort).
    """
    if not code or not code.strip():
        return False

    # SEC-004 : bypass réservé à l'admin authentifié.
    if not admin_user or not admin_user.get('id'):
        logger.info(f'[promo_bypass] REJECT {code!r} — no admin user (guest bypass blocked)')
        return False
    if not _is_admin(admin_user['id']):
        logger.warning(f'[promo_bypass] REJECT {code!r} — user {admin_user["id"]} not admin')
        return False

    normalized = code.strip().upper()
    try:
        sb = get_admin_client()
        r = sb.table('promo_codes').select('*').eq('code', normalized).eq('active', True).maybe_single().execute()
        if not r or not r.data:
            return False
        d = r.data
        max_uses = d.get('max_uses')
        used = d.get('used_count', 0) or 0
        if max_uses is not None and used >= max_uses:
            logger.info(f'[promo_bypass] REJECT {normalized} — quota atteint ({used}/{max_uses})')
            return False

        # Décrément atomique via CAS : on ne met à jour que si used_count == used.
        upd = (
            sb.table('promo_codes')
            .update({'used_count': used + 1})
            .eq('code', normalized)
            .eq('used_count', used)
            .execute()
        )
        if not upd or not upd.data:
            logger.warning(f'[promo_bypass] CAS conflict for {normalized} — concurrent redemption')
            return False

        # Log la redemption (best-effort — table peut ne pas exister, on ne casse pas)
        try:
            sb.table('promo_code_redemptions').insert({
                'code': normalized,
                'user_id': admin_user['id'],
                'user_email': admin_user.get('email'),
                'product': product or '',
            }).execute()
        except Exception as e:
            logger.info(f'[promo_bypass] redemption log skipped for {normalized}: {e}')

        logger.info(f'[promo_bypass] OK — admin {admin_user["id"]} consumed {normalized} ({used + 1}/{max_uses})')
        return True
    except Exception as e:
        logger.warning(f'[promo_bypass] validation failed for {code!r}: {e}')
        return False
