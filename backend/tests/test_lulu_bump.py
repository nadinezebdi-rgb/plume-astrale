"""Smoke test — Lulu bump client + service (mode mock)."""
import os
import pytest

os.environ.setdefault('LULU_MOCK', '1')


def test_lulu_is_mock():
    from services.lulu_client import is_mock
    assert is_mock() is True


def test_lulu_mock_quote_fr():
    from services.lulu_client import mock_quote
    q = mock_quote({'country_code': 'FR'}, page_count=42)
    assert q['currency'] == 'EUR'
    assert q['total_cost_incl_tax'] > 0
    assert q['shipping_cost'] == 8.5
    assert q['estimated_shipping_days'] == 7
    assert q['mock'] is True


def test_lulu_mock_quote_us_more_expensive():
    from services.lulu_client import mock_quote
    fr = mock_quote({'country_code': 'FR'}, page_count=42)
    us = mock_quote({'country_code': 'US'}, page_count=42)
    assert us['shipping_cost'] > fr['shipping_cost']


def test_compute_client_price_minimum_fr():
    from services.natal_lulu_bump_service import compute_client_price_eur, BASE_PRICE_FR_EUR
    quote_fr = {'total_cost_incl_tax': 27.0}  # mock FR
    price = compute_client_price_eur(quote_fr)
    # Prix FR : max(79, 27 + 35=62) = 79€
    assert price == BASE_PRICE_FR_EUR


def test_compute_client_price_above_base_for_expensive_destinations():
    from services.natal_lulu_bump_service import compute_client_price_eur
    # Simule une destination très chère
    quote = {'total_cost_incl_tax': 80.0}  # coût Lulu 80€
    price = compute_client_price_eur(quote)
    # Prix = max(79, 80+35=115) = 115
    assert price >= 115.0


def test_verify_webhook_signature_mock_mode_passes():
    from services.lulu_client import verify_webhook_signature
    # En mode mock, tous les webhooks sont acceptés
    assert verify_webhook_signature(b'{"foo":1}', None) is True


def test_cover_pdf_renders_single_landscape_page(tmp_path):
    from services.natal_cover_pdf import render_cover_pdf
    pdf = render_cover_pdf(first_name='Amélie', birth_date_fr='15 septembre 1990', page_count=42)
    assert pdf.startswith(b'%PDF')
    assert len(pdf) > 50_000  # au moins 50 KB (plume SVG + CSS + roue)


def test_cover_pdf_no_solena_mention(tmp_path):
    """Le user a explicitement demandé AUCUNE mention de Soléna sur la couverture."""
    from services.natal_cover_pdf import build_cover_html
    html = build_cover_html(first_name='Amélie', birth_date_fr='15 septembre 1990', page_count=42)
    low = html.lower()
    assert 'soléna' not in low
    assert 'solena' not in low


def test_cover_html_mentions_plume_astrale():
    from services.natal_cover_pdf import build_cover_html
    html = build_cover_html(first_name='Amélie', birth_date_fr='', page_count=42)
    assert 'Plume Astrale' in html


def test_spine_width_scales_with_pages():
    from services.natal_cover_pdf import _spine_width_mm
    assert _spine_width_mm(42) < _spine_width_mm(200)
    assert _spine_width_mm(32) >= 5.0  # au moins le carton
