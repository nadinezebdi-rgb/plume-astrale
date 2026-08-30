"""Tests pytest pour services/book_composer_pricing.py + routes/composer.py

Verrouille la règle de pricing serveur : +29€ 1er chapitre, +19€ suivants,
plafond 99€. L'édition (24/69/119) inclut déjà le Thème Natal base.
"""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from services.book_composer_pricing import (
    compute_quote,
    load_active_chapters,
    EDITIONS,
    FIRST_CHAPTER_PRICE_EUR,
    NEXT_CHAPTER_PRICE_EUR,
    CHAPTERS_TOTAL_CAP_EUR,
)


# ═══════════════════════════════════════════════════════════════
# Tests unitaires du moteur de pricing (offline, fallback local)
# ═══════════════════════════════════════════════════════════════
def test_editions_catalog_has_three_tiers():
    """Les 3 éditions Numérique/Broché/Relié doivent exister."""
    assert set(EDITIONS.keys()) == {'numerique', 'brochee', 'reliee'}
    assert EDITIONS['numerique']['price_eur'] == 24
    assert EDITIONS['brochee']['price_eur'] == 69
    assert EDITIONS['reliee']['price_eur'] == 119


def test_pricing_rules_locked():
    """Verrous des constantes de règle métier."""
    assert FIRST_CHAPTER_PRICE_EUR == 29
    assert NEXT_CHAPTER_PRICE_EUR == 19
    assert CHAPTERS_TOTAL_CAP_EUR == 99


def test_numerique_no_chapter_equals_24():
    q = compute_quote(edition='numerique', chapter_slugs=[])
    assert q.total_eur == 24
    assert q.chapters_price_eur == 0
    assert q.chapters == []
    assert q.total_pages == 49


def test_numerique_one_chapter_equals_53():
    q = compute_quote(edition='numerique', chapter_slugs=['arbre_de_vie'])
    assert q.total_eur == 24 + 29
    assert q.chapters_price_eur == 29
    assert q.chapters_subtotal_eur == 29
    assert q.chapters_cap_applied is False


def test_numerique_two_chapters_equals_72():
    """24 + 29 + 19 = 72€ — le 2e chapitre à 19€, pas 29€."""
    q = compute_quote(edition='numerique', chapter_slugs=['arbre_de_vie', 'astrocartographie'])
    assert q.total_eur == 72
    assert q.chapters_price_eur == 48
    assert len(q.chapters) == 2
    # Le 1er chapitre est à 29€, le 2e à 19€
    assert q.chapters[0]['unit_eur'] == 29
    assert q.chapters[1]['unit_eur'] == 19


def test_broche_three_chapters_equals_136():
    """69 + 29 + 19 + 19 = 136€"""
    q = compute_quote(
        edition='brochee',
        chapter_slugs=['arbre_de_vie', 'astrocartographie', 'karma_destin'],
    )
    assert q.total_eur == 136
    assert q.chapters_price_eur == 67


def test_relie_six_chapters_hits_cap():
    """Plafond 99€ appliqué : 6 chapitres = min(29 + 5*19, 99) = min(124, 99) = 99.
    Total Relié = 119 + 99 = 218€. Cap flag doit être TRUE."""
    q = compute_quote(
        edition='reliee',
        chapter_slugs=[
            'arbre_de_vie', 'astrocartographie', 'karma_destin',
            'etoiles_fixes', 'symboles_sabiens',
            'heure_retrouvee',
        ],
        no_birth_time=True,  # active heure_retrouvee
    )
    # 5 chapitres visibles (heure_retrouvee inclus si no_birth_time=True)
    assert q.chapters_subtotal_eur == 29 + 5 * 19  # 124
    assert q.chapters_price_eur == 99
    assert q.chapters_cap_applied is True
    assert q.total_eur == 119 + 99


def test_five_chapters_below_cap():
    """5 chapitres = 29 + 4*19 = 105€ → plafonné à 99€."""
    q = compute_quote(
        edition='numerique',
        chapter_slugs=['arbre_de_vie', 'astrocartographie', 'karma_destin',
                       'etoiles_fixes', 'symboles_sabiens'],
    )
    assert q.chapters_subtotal_eur == 29 + 4 * 19  # 105
    assert q.chapters_price_eur == 99
    assert q.chapters_cap_applied is True
    assert q.total_eur == 24 + 99


def test_four_chapters_exactly_at_boundary():
    """4 chapitres = 29 + 3*19 = 86€ (sous le plafond)."""
    q = compute_quote(
        edition='numerique',
        chapter_slugs=['arbre_de_vie', 'astrocartographie', 'karma_destin', 'etoiles_fixes'],
    )
    assert q.chapters_subtotal_eur == 86
    assert q.chapters_price_eur == 86
    assert q.chapters_cap_applied is False


def test_dedup_preserves_order():
    """Un slug dupliqué ne compte qu'une fois."""
    q = compute_quote(
        edition='numerique',
        chapter_slugs=['arbre_de_vie', 'arbre_de_vie', 'astrocartographie'],
    )
    assert len(q.chapters) == 2
    assert q.total_eur == 72


def test_unknown_slug_is_ignored_with_warning():
    q = compute_quote(edition='numerique', chapter_slugs=['unknown_chapter'])
    assert q.total_eur == 24
    assert q.chapters == []
    assert any('indisponible' in w for w in q.warnings)


def test_invalid_edition_raises():
    with pytest.raises(ValueError):
        compute_quote(edition='premium', chapter_slugs=[])


def test_heure_retrouvee_hidden_when_birth_time_provided():
    """Le chapitre L'Heure Retrouvée n'est disponible que si no_birth_time=True."""
    catalog_with_time = {c.slug for c in load_active_chapters(no_birth_time=False)}
    catalog_no_time = {c.slug for c in load_active_chapters(no_birth_time=True)}
    assert 'heure_retrouvee' not in catalog_with_time
    assert 'heure_retrouvee' in catalog_no_time


def test_heure_retrouvee_dropped_when_birth_time_provided():
    """Si le user coche 'heure_retrouvee' mais fournit une heure, le chapitre est
    ignoré (warning) — cohérence avec le catalogue filtré."""
    q = compute_quote(
        edition='numerique',
        chapter_slugs=['heure_retrouvee'],
        no_birth_time=False,
    )
    assert q.chapters == []
    assert q.total_eur == 24
    assert any('heure_retrouvee' in w for w in q.warnings)


def test_pages_total_accumulate():
    """Les pages ajoutées s'accumulent au-dessus des 49 pages du Thème Natal."""
    q = compute_quote(
        edition='numerique',
        chapter_slugs=['arbre_de_vie', 'astrocartographie'],
    )
    # base 49 + arbre 12 + astrocarto 14 = 75
    assert q.total_pages == 75


# ═══════════════════════════════════════════════════════════════
# Tests HTTP via TestClient (endpoint /api/composer/*)
# ═══════════════════════════════════════════════════════════════
@pytest.fixture(scope='module')
def client():
    from server import app
    return TestClient(app)


def test_endpoint_chapters(client):
    r = client.get('/api/composer/chapters')
    assert r.status_code == 200
    data = r.json()
    assert 'editions' in data and len(data['editions']) == 3
    assert 'chapters' in data
    assert data['pricing_rules']['first_chapter_eur'] == 29
    assert data['pricing_rules']['next_chapter_eur'] == 19
    assert data['pricing_rules']['chapters_cap_eur'] == 99


def test_endpoint_quote_numerique_alone(client):
    r = client.post('/api/composer/quote', json={
        'edition': 'numerique',
        'chapter_slugs': [],
    })
    assert r.status_code == 200
    q = r.json()
    assert q['total_eur'] == 24
    assert q['chapters'] == []


def test_endpoint_quote_broche_two_chapters(client):
    r = client.post('/api/composer/quote', json={
        'edition': 'brochee',
        'chapter_slugs': ['arbre_de_vie', 'astrocartographie'],
    })
    assert r.status_code == 200
    q = r.json()
    assert q['total_eur'] == 69 + 29 + 19  # 117
    assert q['edition_label'] == 'Édition Brochée'


def test_endpoint_quote_rejects_invalid_edition(client):
    r = client.post('/api/composer/quote', json={
        'edition': 'ultra_premium',
        'chapter_slugs': [],
    })
    # Pydantic pattern → 422
    assert r.status_code == 422
