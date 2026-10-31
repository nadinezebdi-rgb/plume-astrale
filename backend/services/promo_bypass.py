"""
<<<<<<< HEAD
SEC-004 — Bypass Stripe via code promo 100% remise.
=======
SEC-004 — Bypass Stripe via code promo 100% remise (comptes autorisés uniquement).
>>>>>>> origin/main

Avant : n'importe qui pouvant deviner un code (ADMIN26, PLUME15…) obtenait
un PDF premium gratuit via un guest checkout.

Après :
1. Le bypass exige un Bearer token JWT valide dont le compte est `is_admin=true`.
2. Décrément atomique de `used_count` via update filtré (conditional CAS).
3. Trace de chaque redemption dans `promo_code_redemptions` (best-effort).

Sentinelle `__ADMIN_BYPASS__` : le frontend ne connaît pas le vrai code ; le
backend le lit dans `PROMO_BYPASS_CODE` (défaut `TOUT2026`) et ne le renvoie jamais.

Les codes % (KABBALE20, etc.) ne sont PAS concernés : ils passent toujours
par Stripe avec la remise appliquée, aucun bypass.

TEST CODES (2026-02) : liste blanche de codes qui bypass la check admin.
Chaque code a un max_uses court en base (hard cap) pour limiter les dégâts
si leaké. À ne JAMAIS étendre sans accord admin.
"""
from __future__ import annotations
import logging
import os
from typing import Optional
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# Codes qui autorisent le bypass sans check is_admin.
# Hard cap côté base (max_uses) + revocable instantanément via /admin/promo.
_TEST_CODES_NO_ADMIN_CHECK = frozenset({
    'TESTPDF2026',  # Nadine — essais PDFs sans compte admin (max 20 usages)
})


def _is_admin(user_id: str) -> bool:
    """Vérifie is_admin=true sur le profil (source de vérité)."""
    try:
        sb = get_admin_client()
        r = sb.table('profiles').select('is_admin').eq('id', user_id).maybe_single().execute()
        return bool(r and r.data and r.data.get('is_admin'))
    except Exception as e:
        logger.warning(f'[promo_bypass] is_admin check failed for {user_id}: {e}')
        return False


ADMIN_BYPASS_SENTINEL = '__ADMIN_BYPASS__'


def get_bypass_code() -> str:
    """Vrai code de bypass (env `PROMO_BYPASS_CODE`, défaut TOUT2026), normalisé."""
    return (os.environ.get('PROMO_BYPASS_CODE') or 'TOUT2026').strip().upper()


def _allowed_emails() -> set:
    raw = os.environ.get('PROMO_BYPASS_ALLOWED_EMAILS') or ''
    return {e.strip().lower() for e in raw.split(',') if e.strip()}


def is_bypass_authorized(user: Optional[dict]) -> bool:
    """Utilisateur authentifié ET (is_admin=true OU email dans la liste autorisée)."""
    if not user or not user.get('id'):
        return False
    email = (user.get('email') or '').strip().lower()
    if email and email in _allowed_emails():
        return True
    return _is_admin(user['id'])


def try_consume_promo(
    code: Optional[str],
    admin_user: Optional[dict] = None,
    product: Optional[str] = None,
) -> bool:
    """Consomme un code promo 100% remise.

    Retourne True uniquement si :
<<<<<<< HEAD
      1. Code dans la liste blanche test (TESTPDF2026, …) → bypass admin check.
         OU `admin_user` authentifié avec `is_admin=true`.
=======
      1. Un utilisateur authentifié est fourni ET (`is_admin=true` en base OU
         email dans `PROMO_BYPASS_ALLOWED_EMAILS`).
>>>>>>> origin/main
      2. Le code existe, actif, quota non atteint.
      3. Le décrément atomique a réussi (CAS).

    Trace la redemption dans `promo_code_redemptions` (best-effort).
    """
    if not code or not code.strip():
        return False

<<<<<<< HEAD
    normalized = code.strip().upper()

    # SEC-004 bypass : les codes de test (whitelist) sautent le check admin.
    is_test_code = normalized in _TEST_CODES_NO_ADMIN_CHECK
    if not is_test_code:
        if not admin_user or not admin_user.get('id'):
            logger.info(f'[promo_bypass] REJECT {code!r} — no admin user (guest bypass blocked)')
            return False
        if not _is_admin(admin_user['id']):
            logger.warning(f'[promo_bypass] REJECT {code!r} — user {admin_user["id"]} not admin')
            return False
=======
    # SEC-004 : bypass réservé aux comptes authentifiés autorisés.
    if not admin_user or not admin_user.get('id'):
        logger.info('[promo_bypass] REJECT — no authenticated user (guest bypass blocked)')
        return False
    if not is_bypass_authorized(admin_user):
        logger.warning(f'[promo_bypass] REJECT — user {admin_user["id"]} not authorized')
        return False

    normalized = code.strip().upper()
    if normalized == ADMIN_BYPASS_SENTINEL:
        normalized = get_bypass_code()
>>>>>>> origin/main
    try:
        sb = get_admin_client()
        r = sb.table('promo_codes').select('*').eq('code', normalized).eq('active', True).maybe_single().execute()
        if not r or not r.data:
            return False
        d = r.data
        max_uses = d.get('max_uses')
        used = d.get('used_count', 0) or 0
        if max_uses is not None and used >= max_uses:
            logger.info(f'[promo_bypass] REJECT promo — quota atteint ({used}/{max_uses})')
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
                'user_id': (admin_user or {}).get('id') or 'guest-test',
                'user_email': (admin_user or {}).get('email'),
                'product': product or '',
            }).execute()
        except Exception as e:
            logger.info(f'[promo_bypass] redemption log skipped for {normalized}: {e}')

<<<<<<< HEAD
        who = admin_user.get('id') if admin_user else 'test-guest'
        logger.info(f'[promo_bypass] OK — {who} consumed {normalized} ({used + 1}/{max_uses})')
=======
        logger.info(f'[promo_bypass] OK — user {admin_user["id"]} consumed {normalized} ({used + 1}/{max_uses})')
>>>>>>> origin/main
        return True
    except Exception as e:
        logger.warning(f'[promo_bypass] validation failed: {e}')
        return False
