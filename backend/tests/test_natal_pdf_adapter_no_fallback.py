"""Regression test — Bug Nadine (Feb 2026)

Le PDF de Nadine (17/07/1968, Saint Avold) affichait :
- Lune Poissons (vraie : Bélier)
- Ascendant Vierge (vraie : Gémeaux)
- Vénus/Mars/Ascendant → 'Inconnu' dans les chapitres

Cause : quand `planets_data` était vide/incomplet, `natal_pdf_adapter` utilisait
des fallbacks HARDCODÉS ('Cancer'/'Poissons'/'Vierge'/'Inconnu') qui produisaient
un PDF avec fausses positions astrologiques.

Fix : `generate_manuscrit_pdf` doit lever `RuntimeError` si `_find_sign()` ne
trouve pas au moins Soleil + Lune. Aucune valeur trompeuse ne doit être insérée.
"""
import os
import sys

sys.path.insert(0, '/app/backend')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'test_db')


def test_generate_manuscrit_pdf_raises_when_planets_empty():
    """Sans planets_data et sans AI, la fonction doit lever RuntimeError."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    import pytest

    user_data = {
        'prenom': 'Nadine',
        'birth_date': '1968-07-17',
        # Aucun sun_sign/moon_sign/etc dans user_data
        # Aucun ai_interpretations
    }
    with pytest.raises(RuntimeError) as exc_info:
        generate_manuscrit_pdf(
            user_data=user_data,
            planets_data=None,      # <— pas de data API
            chart_png_bytes=None,
        )
    err = str(exc_info.value)
    assert 'signes manquants' in err.lower() or 'planets_data' in err.lower(), (
        f'Le message doit être explicite. Reçu: {err}'
    )


def test_generate_manuscrit_pdf_raises_when_planets_data_empty_list():
    """planets_data=[] (API OK mais 0 planètes) doit aussi lever."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    import pytest

    user_data = {'prenom': 'Nadine', 'birth_date': '1968-07-17'}
    with pytest.raises(RuntimeError):
        generate_manuscrit_pdf(user_data=user_data, planets_data=[], chart_png_bytes=None)


def test_no_hardcoded_fallback_signs_in_source():
    """
    Vérifie que le code source ne contient plus les fallbacks trompeurs :
    'Cancer' / 'Poissons' / 'Vierge' / 'Inconnu' comme valeurs statiques.
    """
    src = open('/app/backend/services/natal_pdf_adapter.py').read()
    # Les patterns bugués retirés lors du fix Nadine Feb 2026
    forbidden_patterns = [
        "or 'Cancer'",
        "or 'Poissons'",
        "or 'Vierge'",
        "or 'Inconnu'",
    ]
    found = [p for p in forbidden_patterns if p in src]
    assert not found, (
        f'Fallbacks hardcodés détectés dans natal_pdf_adapter.py : {found}. '
        f'Ils avaient causé le bug Nadine (Feb 2026) — ne pas les réintroduire.'
    )


def test_theme_natal_oneshot_guards_planets_dict():
    """
    Vérifie que theme_natal_oneshot_service refuse de générer un PDF si
    astrology-api.io ne renvoie pas au moins 5 planètes core.
    """
    src = open('/app/backend/services/theme_natal_oneshot_service.py').read()
    # Marqueurs de la garde ajoutée pour le bug Nadine
    assert '_CORE_PLANETS' in src, 'Garde _CORE_PLANETS absente'
    assert '_alert_empty_planets' in src, 'Alerte email admin absente'
    assert 'planets_core_missing' in src or "core manquantes" in src, (
        'Diag core_missing manquant'
    )


def test_normalize_birth_data_converts_country_name_to_code():
    """Bug Nadine : birth_data contenait country_code='France' → HTTP 422.
    Vérifie que normalize_birth_data corrige toutes les variantes.
    """
    from services.astrology_io_service import normalize_birth_data
    # Cas Nadine exact
    bd = {'year': 1968, 'month': 7, 'day': 17, 'country_code': 'France'}
    out = normalize_birth_data(bd)
    assert out['country_code'] == 'FR', f'Expected FR, got {out["country_code"]}'
    # Autres cas
    assert normalize_birth_data({'country_code': 'FR'})['country_code'] == 'FR'
    assert normalize_birth_data({'country_code': 'fr'})['country_code'] == 'FR'
    assert normalize_birth_data({'country_code': 'Belgium'})['country_code'] == 'BE'
    assert normalize_birth_data({'country_code': 'Royaume-Uni'})['country_code'] == 'GB'
    # Cast numériques (webhook parfois envoie des strings)
    out2 = normalize_birth_data({'year': '1990', 'month': '5', 'hour': '14', 'latitude': '48.85'})
    assert out2['year'] == 1990
    assert out2['month'] == 5
    assert out2['hour'] == 14
    assert out2['latitude'] == 48.85
