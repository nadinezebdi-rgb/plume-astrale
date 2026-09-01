"""Tests pour LuluPrintProvider (LOT 4.4)."""
from __future__ import annotations
from datetime import datetime, timezone

import pytest

from services.book_engine.domain import BirthData, Edition, Manuscript
from services.print.lulu_provider import (
    build_cover_spec, calculate_spine_mm, estimate_retail_price_eur,
    validate_manuscript_for_print,
)


def _empty_manuscript(edition: Edition = Edition.BROCHEE) -> Manuscript:
    return Manuscript(
        session_id='t', user_email='', first_name='',
        birth_data=BirthData(date_iso='1990-01-01', time_hhmm='12:00', city='Paris'),
        astro_data={}, chapters=[], edition=edition,
        created_at=datetime.now(timezone.utc),
    )


def test_spine_scales_linearly_with_pages():
    s32 = calculate_spine_mm(32)
    s200 = calculate_spine_mm(200)
    assert 1.8 <= s32 <= 1.9        # ~1.83 mm sur 32 pages
    assert 11.0 <= s200 <= 11.5     # ~11.44 mm sur 200 pages
    # Linéarité
    ratio = s200 / s32
    assert abs(ratio - 200 / 32) < 0.05


def test_cover_spec_includes_bleed():
    spec = build_cover_spec(100)
    # 2×148 + spine ~5.72 + 2×3 = 307.72 mm
    w, h = spec['cover_total_mm']
    assert 305 <= w <= 310
    assert h == 216.0
    assert spec['bleed_mm'] == 3.0


def test_validate_brochee_min_pages():
    m = _empty_manuscript(Edition.BROCHEE)
    v = validate_manuscript_for_print(m, Edition.BROCHEE, pages_hint=20)
    assert v.ok is False
    assert any('32' in i for i in v.issues)
    v2 = validate_manuscript_for_print(m, Edition.BROCHEE, pages_hint=40)
    assert v2.ok is True


def test_validate_multiple_of_4():
    m = _empty_manuscript()
    v = validate_manuscript_for_print(m, Edition.BROCHEE, pages_hint=33)
    # 33 → arrondi à 36 (multiple de 4)
    assert v.pages == 36


def test_price_brochee_reasonable():
    p = estimate_retail_price_eur(40, Edition.BROCHEE, quantity=1)
    # ~14 EUR prix Plume + 3.90 EUR livraison ≈ 18 EUR
    assert 15 <= p['total_eur'] <= 25
    assert p['production_cost_eur'] < p['plume_price_eur']  # marge positive


def test_price_reliee_higher_than_brochee():
    p_b = estimate_retail_price_eur(80, Edition.BROCHEE)
    p_r = estimate_retail_price_eur(80, Edition.RELIEE)
    assert p_r['total_eur'] > p_b['total_eur']


def test_price_scales_with_quantity():
    p1 = estimate_retail_price_eur(40, Edition.BROCHEE, quantity=1)
    p3 = estimate_retail_price_eur(40, Edition.BROCHEE, quantity=3)
    # Quantité 3 doit être plus chère mais pas 3× (shipping fixe)
    assert p3['plume_price_eur'] > p1['plume_price_eur']
    assert p3['total_eur'] > p1['total_eur']
    assert p3['total_eur'] < 3 * p1['total_eur']
