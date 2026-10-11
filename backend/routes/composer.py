# SUPPRIMER CETTE SECTION :
# _PROMO_CODES = {
#     'TOUT2026': {'discount_pct': 100, 'active': True, 'label': 'Offert 2026'},
# }

def _validate_promo(code: Optional[str]) -> Optional[dict]:
    """Retourne le dict du promo si valide, sinon None.

    Le vrai code bypass reste secret et est géré par promo_bypass.py.
    """
    if not code:
        return None

    normalized = code.strip().upper()

    # Security: never expose the real admin bypass code in the public promo catalog.
    # This code is validated only by the backend with auth + allowlist.
    if normalized == "__ADMIN_BYPASS__":
        return None

    # Any public promo code that is not admin-only stays here if needed.
    return None
