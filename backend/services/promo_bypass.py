"""
SEC-004 — Bypass Stripe via code promo 100% remise (STRICT ADMIN + allowlist-only).

Avant :
- n'importe qui pouvant deviner un code pouvait obtenir un PDF premium gratuit via un guest checkout.

Après :
1. Le bypass exige un utilisateur authentifié.
2. L'accès est autorisé si :
   - user.is_admin = true, ou
   - user.email est présent dans PROMO_BYPASS_ALLOWED_EMAILS
3. Le vrai code est lu dans PROMO_BYPASS_CODE (fallback: TOUT2026) et n'est JAMAIS exposé au front.
4. Une sentinelle `__ADMIN_BYPASS__` peut être utilisée par le front pour déclencher le bypass côté backend.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

BYPASS_SENTINEL = "__ADMIN_BYPASS__"


def _get_bypass_code() -> str:
    return (os.getenv("PROMO_BYPASS_CODE") or "TOUT2026").strip().upper()


def _get_allowed_emails() -> set[str]:
    raw = os.getenv("PROMO_BYPASS_ALLOWED_EMAILS", "")
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def _is_allowed_email(email: Optional[str]) -> bool:
    if not email:
        return False
    return email.strip().lower() in _get_allowed_emails()


def _is_admin(user_id: str) -> bool:
    """Vérifie is_admin=true sur le profil (source de vérité)."""
    try:
        sb = get_admin_client()
        r = sb.table("profiles").select("is_admin").eq("id", user_id).maybe_single().execute()
        return bool(r and r.data and r.data.get("is_admin"))
    except Exception as e:
        logger.warning(f"[promo_bypass] is_admin check failed for {user_id}: {e}")
        return False


def _user_is_authorized(admin_user: Optional[dict]) -> bool:
    """Autorise le bypass si l'utilisateur est admin ou dans la allowlist."""
    if not admin_user or not admin_user.get("id"):
        return False

    if _is_admin(admin_user["id"]):
        return True

    email = (admin_user.get("email") or "").strip()
    return _is_allowed_email(email)


def try_consume_promo(
    code: Optional[str],
    admin_user: Optional[dict] = None,
    product: Optional[str] = None,
) -> bool:
    """Consomme un code promo 100% remise.

    Retourne True uniquement si :
      1. Un `admin_user` authentifié est fourni.
      2. L'utilisateur est autorisé (`is_admin=true` ou email allowlisté).
      3. Le code existe, est actif, quota non atteint.
      4. Le CAS a réussi en base.
    """
    if not code or not code.strip():
        return False

    # Frontend can send sentinel instead of exposing the real code.
    if code.strip() == BYPASS_SENTINEL:
        normalized = _get_bypass_code()
    else:
        normalized = code.strip().upper()

    if not admin_user or not admin_user.get("id"):
        logger.info(f"[promo_bypass] REJECT {normalized!r} — no authenticated user")
        return False

    if not _user_is_authorized(admin_user):
        logger.warning(
            f"[promo_bypass] REJECT {normalized!r} — user {admin_user['id']} not admin / not allowlisted"
        )
        return False

    try:
        sb = get_admin_client()
        r = sb.table("promo_codes").select("*").eq("code", normalized).eq("active", True).maybe_single().execute()
        if not r or not r.data:
            logger.info(f"[promo_bypass] REJECT {normalized} — code missing or inactive")
            return False

        d = r.data
        max_uses = d.get("max_uses")
        used = d.get("used_count", 0) or 0

        if max_uses is not None and used >= max_uses:
            logger.info(f"[promo_bypass] REJECT {normalized} — quota reached ({used}/{max_uses})")
            return False

        upd = (
            sb.table("promo_codes")
            .update({"used_count": used + 1})
            .eq("code", normalized)
            .eq("used_count", used)
            .execute()
        )
        if not upd or not upd.data:
            logger.warning(f"[promo_bypass] CAS conflict for {normalized} — concurrent redemption")
            return False

        try:
            sb.table("promo_code_redemptions").insert({
                "code": normalized,
                "user_id": admin_user["id"],
                "user_email": admin_user.get("email"),
                "product": product or "",
            }).execute()
        except Exception as e:
            logger.info(f"[promo_bypass] redemption log skipped for {normalized}: {e}")

        logger.info(
            f"[promo_bypass] OK — user {admin_user['id']} consumed {normalized} "
            f"({used + 1}/{max_uses})"
        )
        return True

    except Exception as e:
        logger.warning(f"[promo_bypass] validation failed for {code!r}: {e}")
        return False
