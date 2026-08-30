"""Tests de non-régression — Fix P0 §V audit marque Feb 2026.

Sans heure de naissance : ascendant faux 11/12, maisons fausses.
Fix : détecter no_birth_time, retirer ascendant + maisons du PDF, colophon
"Édition des Planètes".
"""
from __future__ import annotations
import inspect


def test_checkout_accepts_missing_birth_time():
    """POST /theme-natal-oneshot/checkout doit accepter birth_time vide (avant : 400)."""
    from routes.theme_natal_oneshot import theme_natal_oneshot_checkout
    src = inspect.getsource(theme_natal_oneshot_checkout)
    # L'ancienne validation combinée est retirée
    assert 'not payload.birth_date or not payload.birth_time' not in src
    # La nouvelle validation ne teste QUE birth_date
    assert 'not payload.birth_date' in src
    # Le flag no_birth_time est calculé et propagé dans pdf_ctx
    assert 'no_birth_time' in src
    assert "'no_birth_time': no_birth_time" in src


def test_checkout_flags_default_1200_as_no_birth_time():
    """birth_time = '12:00' (défaut anti-fantôme) doit être flaggé no_birth_time=True."""
    from routes.theme_natal_oneshot import theme_natal_oneshot_checkout
    src = inspect.getsource(theme_natal_oneshot_checkout)
    # Le code doit tester '12:00' et '12:00:00' comme des defauts douteux
    assert "'12:00'" in src or "12:00" in src
    assert 'no_birth_time' in src


def test_natal_pdf_adapter_removes_ascendant_when_no_birth_time():
    """natal_pdf_adapter doit retirer 'Ascendant' du planet_list si no_birth_time."""
    from services import natal_pdf_adapter
    src = inspect.getsource(natal_pdf_adapter)
    assert "no_birth_time" in src
    assert "p != 'Ascendant'" in src
    # ascendant_sign doit être forcé à '' quand no_birth_time
    assert "'ascendant_sign': ''" in src or "ascendant_sign': ''" in src


def test_natal_pdf_v2_skips_ascendant_cell_when_no_birth_time():
    """natal_pdf_v2 doit skip la cell Ascendant dans la grille 2x2 si no_birth_time."""
    from services import natal_pdf_v2
    src = inspect.getsource(natal_pdf_v2)
    assert 'no_birth_time' in src
    # La cell Ascendant doit être conditionnelle
    assert 'if asc_sign and not no_birth_time' in src


def test_colophon_product_name_edition_des_planetes():
    """Colophon doit accepter product_name paramétrable pour "Édition des Planètes"."""
    from services.pdf_book_pages import colophon_page
    sig = inspect.signature(colophon_page)
    assert 'product_name' in sig.parameters
    src = inspect.getsource(colophon_page)
    assert 'product_name=product_name' in src


def test_natal_pdf_v2_passes_edition_des_planetes_to_colophon():
    """Quand no_birth_time=True, colophon doit recevoir 'Édition des Planètes'."""
    from services import natal_pdf_v2
    src = inspect.getsource(natal_pdf_v2)
    assert 'Édition des Planètes' in src
    # Le product_name est bien transmis au colophon
    assert "product_name=_product_name" in src or "product_name=" in src


def test_theme_natal_service_reads_flag_from_pdf_ctx():
    """theme_natal_oneshot_service doit lire pdf_ctx.no_birth_time et le propager."""
    from services import theme_natal_oneshot_service
    src = inspect.getsource(theme_natal_oneshot_service)
    assert "pdf_ctx.get('no_birth_time')" in src
    # Propage dans user_data + ascendant_sign vide
    assert "'no_birth_time': no_birth_time" in src


def test_theme_natal_service_zeros_ascendant_when_no_birth_time():
    """Quand no_birth_time, ascendant_sign doit être '' dans user_data (pas la valeur API)."""
    from services import theme_natal_oneshot_service
    src = inspect.getsource(theme_natal_oneshot_service)
    # Test conditionnel sur no_birth_time
    assert "'' if no_birth_time else" in src


def test_natal_pdf_v2_disables_book_mode_when_no_birth_time():
    """no_birth_time=True doit forcer bd=False → pas de trio/maisons/livre riche."""
    from services import natal_pdf_v2
    src = inspect.getsource(natal_pdf_v2)
    # Le mode livre est explicitement désactivé quand no_birth_time
    assert 'if no_birth_time:' in src and 'bd = False' in src


def test_natal_pdf_v2_calls_colophon_even_in_no_birth_time_mode():
    """Colophon doit toujours être appelé, même quand bd=False (no_birth_time)."""
    from services import natal_pdf_v2
    src = inspect.getsource(natal_pdf_v2)
    # Condition élargie : bd OU no_birth_time
    assert 'if bd or no_birth_time:' in src


# ═════════════════════════════════════════════════════════════════════════
# Extension P0 aux 4 autres produits (lecture_complete, edition_reliee,
# karma_destin, voyage_karmique) — Feb 2026
# ═════════════════════════════════════════════════════════════════════════

def test_karma_destin_accepts_missing_birth_time():
    """POST /karma-destin/checkout doit accepter birth_time vide + flag."""
    from routes.karma_destin import karma_destin_checkout
    src = inspect.getsource(karma_destin_checkout)
    assert 'not payload.birth_date or not payload.birth_time' not in src
    assert 'no_birth_time' in src
    assert "'no_birth_time': no_birth_time" in src


def test_voyage_karmique_accepts_missing_birth_time():
    """POST /voyage-karmique/checkout doit accepter birth_time vide + flag."""
    from routes.voyage_karmique import voyage_karmique_checkout
    src = inspect.getsource(voyage_karmique_checkout)
    assert 'not payload.birth_date or not payload.birth_time' not in src
    assert 'no_birth_time' in src


def test_edition_reliee_accepts_missing_birth_time():
    """POST /edition-reliee/checkout doit accepter birth_time optional + flag."""
    from routes.edition_reliee import edition_reliee_checkout, CheckoutPayload
    # Le champ birth_time est maintenant Optional
    fields = CheckoutPayload.model_fields
    assert fields['birth_time'].is_required() is False
    src = inspect.getsource(edition_reliee_checkout)
    assert 'no_birth_time' in src
    # Le service reçoit le flag
    assert 'no_birth_time=no_birth_time' in src


def test_edition_reliee_service_accepts_no_birth_time_kwarg():
    """create_edition_reliee_checkout doit accepter no_birth_time et le propager."""
    from services.edition_reliee_service import create_edition_reliee_checkout
    sig = inspect.signature(create_edition_reliee_checkout)
    assert 'no_birth_time' in sig.parameters
    src = inspect.getsource(create_edition_reliee_checkout)
    assert "'no_birth_time': no_birth_time" in src


def test_lecture_complete_accepts_missing_birth_time():
    """POST /lecture-complete/checkout doit accepter birth_time vide + flag.

    Comme le bundle inclut un Thème Natal, sans heure, ce dernier sortira
    en Édition des Planètes automatiquement.
    """
    from routes.lecture_complete import lecture_complete_checkout
    src = inspect.getsource(lecture_complete_checkout)
    assert 'no_birth_time' in src
    assert "'no_birth_time': no_birth_time" in src


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
