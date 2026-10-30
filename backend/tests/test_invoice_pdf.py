"""Tests de la facture PDF FR (invoice_pdf.py) — Feb 2026."""
from __future__ import annotations
import io
from datetime import datetime, timezone

import pymupdf
import pytest

from services.invoice_pdf import build_invoice_pdf, make_invoice_number


@pytest.fixture
def sample_invoice_bytes() -> bytes:
    paid_at = datetime(2026, 2, 27, 14, 30, tzinfo=timezone.utc)
    return build_invoice_pdf(
        invoice_number='2602-0838',
        customer_email='nadine.zebdi@gmail.com',
        customer_name='Nadine Zebdi',
        product_label='Thème Natal personnalisé',
        amount_cents=4900,
        payment_method_label='Carte Visa …4242',
        paid_at=paid_at,
        session_id='cs_live_abc123_0838',
    )


def _text(pdf_bytes: bytes) -> str:
    doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
    return '\n'.join(p.get_text() for p in doc)


def test_invoice_contains_siret(sample_invoice_bytes):
    assert 'SIRET : 87860206900022' in _text(sample_invoice_bytes)


def test_invoice_contains_vat_number(sample_invoice_bytes):
    assert 'FR96878602069' in _text(sample_invoice_bytes)


def test_invoice_contains_franchise_tva_notice(sample_invoice_bytes):
    """Mention OBLIGATOIRE pour auto-entrepreneurs en franchise de TVA."""
    assert 'TVA non applicable, art. 293 B du CGI' in _text(sample_invoice_bytes)


def test_invoice_contains_customer_info(sample_invoice_bytes):
    t = _text(sample_invoice_bytes)
    assert 'Nadine Zebdi' in t
    assert 'nadine.zebdi@gmail.com' in t


def test_invoice_contains_amount(sample_invoice_bytes):
    t = _text(sample_invoice_bytes)
    # 49,00 € formaté FR
    assert '49,00' in t
    assert 'TOTAL TTC' in t


def test_invoice_contains_payment_method(sample_invoice_bytes):
    assert 'Carte Visa …4242' in _text(sample_invoice_bytes)


def test_invoice_contains_product_label(sample_invoice_bytes):
    assert 'Thème Natal personnalisé' in _text(sample_invoice_bytes)


def test_invoice_contains_french_date(sample_invoice_bytes):
    assert '27 février 2026' in _text(sample_invoice_bytes)


def test_invoice_contains_session_reference(sample_invoice_bytes):
    assert 'cs_live_abc123_0838' in _text(sample_invoice_bytes)


def test_invoice_number_format():
    """Format AAMM-XXXX : préfixe année/mois + 4 derniers caractères session."""
    n = make_invoice_number('cs_live_abc123_0838', datetime(2026, 2, 27))
    assert n == '2602-0838'


def test_invoice_number_handles_short_session():
    # Vérif simple : termine par 4 chars du session_id (upper)
    n2 = make_invoice_number('cs_live_very_long_abc_ZZZZ', datetime(2026, 12, 15))
    assert n2.endswith('ZZZZ')
    # Session plus courte : padding avec '0'
    n3 = make_invoice_number('ab', datetime(2026, 12, 15))
    assert n3 == '2612-00AB'


def test_invoice_single_page(sample_invoice_bytes):
    doc = pymupdf.open(stream=sample_invoice_bytes, filetype='pdf')
    assert len(doc) == 1


def test_invoice_a4_portrait(sample_invoice_bytes):
    doc = pymupdf.open(stream=sample_invoice_bytes, filetype='pdf')
    rect = doc[0].rect
    # A4 ≈ 595×842 pts
    assert 590 <= rect.width <= 600
    assert 835 <= rect.height <= 850
