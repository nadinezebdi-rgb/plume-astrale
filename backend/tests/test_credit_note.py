"""Tests credit_note_counter + credit_note_pdf + credit_note_delivery."""
import os
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from services import credit_note_counter, credit_note_pdf


# ─── credit_note_counter ────────────────────────────────────────────

def test_format_number():
    assert credit_note_counter.format_number(2026, 1) == 'AVOIR-2026-000001'
    assert credit_note_counter.format_number(2026, 42) == 'AVOIR-2026-000042'
    assert credit_note_counter.format_number(2026, 123456) == 'AVOIR-2026-123456'


@pytest.mark.asyncio
async def test_allocate_returns_none_without_mongo(monkeypatch):
    monkeypatch.delenv('MONGO_URL', raising=False)
    with patch('services.mongo._DB', None), patch('services.mongo._CLIENT', None):
        from services import mongo
        mongo._DB = None
        mongo._CLIENT = None
        r = await credit_note_counter.allocate_or_get('re_xyz')
    assert r is None


# ─── credit_note_pdf (smoke test : build bytes non-vides) ───────────

def test_build_credit_note_pdf_minimal():
    pdf = credit_note_pdf.build_credit_note_pdf(
        credit_note_number='AVOIR-2026-000001',
        invoice_number='FACT-2026-000005',
        invoice_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
        customer_email='client@example.com',
        customer_name='Marie Dupont',
        product_label='Thème natal — édition PDF',
        amount_cents=2400,
        currency='EUR',
        reason='requested_by_customer',
        note='Doublon de commande',
        refunded_at=datetime(2026, 2, 3, 14, 30, tzinfo=timezone.utc),
        refund_id='re_xyz123',
        session_id='cs_live_abc456',
    )
    assert isinstance(pdf, bytes)
    assert len(pdf) > 2000           # un PDF A4 minimal fait au moins ~2 KB
    assert pdf.startswith(b'%PDF-')  # magic bytes PDF


def test_build_credit_note_pdf_no_invoice_ref():
    """Cas edge : avoir émis sans facture d'origine (recovery admin)."""
    pdf = credit_note_pdf.build_credit_note_pdf(
        credit_note_number='AVOIR-2026-000099',
        invoice_number=None,
        invoice_date=None,
        customer_email='orphan@example.com',
        customer_name=None,
        product_label='Compensation incident',
        amount_cents=2400,
        reason='duplicate',
    )
    assert isinstance(pdf, bytes)
    assert len(pdf) > 2000


def test_reason_labels_coverage():
    """Les 3 motifs Stripe sont libellés."""
    assert 'requested_by_customer' in credit_note_pdf.REASON_LABELS
    assert 'duplicate' in credit_note_pdf.REASON_LABELS
    assert 'fraudulent' in credit_note_pdf.REASON_LABELS


# ─── credit_note_delivery ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_credit_note_no_resend_key(monkeypatch):
    """Sans RESEND_API_KEY → report.ok=False, reason='resend_key_missing'."""
    monkeypatch.delenv('RESEND_API_KEY', raising=False)
    from services import credit_note_delivery
    # Mock allocate pour éviter dépendance Mongo
    with patch.object(credit_note_delivery, 'allocate_credit_note_number',
                      new=AsyncMock(return_value='AVOIR-2026-000007')), \
         patch.object(credit_note_delivery, '_lookup_invoice_for_session',
                      new=AsyncMock(return_value=None)):
        r = await credit_note_delivery.send_credit_note_for_refund(
            refund_id='re_test',
            session_id='cs_test',
            customer_email='c@example.com',
            amount_cents=2400,
        )
    assert r['ok'] is False
    assert r['reason'] == 'resend_key_missing'
    assert r['credit_note_number'] == 'AVOIR-2026-000007'


@pytest.mark.asyncio
async def test_send_credit_note_resend_success(monkeypatch):
    """Avec RESEND_API_KEY + mock HTTP 200 → report.ok=True."""
    monkeypatch.setenv('RESEND_API_KEY', 'rsnd_test')
    from services import credit_note_delivery

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.text = '{"id":"email_x"}'

    with patch.object(credit_note_delivery, 'allocate_credit_note_number',
                      new=AsyncMock(return_value='AVOIR-2026-000042')), \
         patch.object(credit_note_delivery, '_lookup_invoice_for_session',
                      new=AsyncMock(return_value={'invoice_number': 'FACT-2026-000020',
                                                  'invoice_date': datetime(2026, 1, 10, tzinfo=timezone.utc)})), \
         patch('httpx.AsyncClient') as cli:
        cli.return_value.__aenter__.return_value.post = AsyncMock(return_value=fake_resp)
        r = await credit_note_delivery.send_credit_note_for_refund(
            refund_id='re_test_success',
            session_id='cs_live_success',
            customer_email='c@example.com',
            customer_name='Alice',
            amount_cents=2400,
            product_label='Thème natal',
            reason='requested_by_customer',
        )
    assert r['ok'] is True
    assert r['email_sent'] is True
    assert r['credit_note_number'] == 'AVOIR-2026-000042'
    assert r['invoice_ref'] == 'FACT-2026-000020'


@pytest.mark.asyncio
async def test_send_credit_note_resend_fail(monkeypatch):
    """Resend renvoie 403 → ok=False, reason='resend_403'."""
    monkeypatch.setenv('RESEND_API_KEY', 'rsnd_test')
    from services import credit_note_delivery

    fake_resp = MagicMock()
    fake_resp.status_code = 403
    fake_resp.text = 'invalid key'
    with patch.object(credit_note_delivery, 'allocate_credit_note_number',
                      new=AsyncMock(return_value='AVOIR-2026-000013')), \
         patch.object(credit_note_delivery, '_lookup_invoice_for_session',
                      new=AsyncMock(return_value=None)), \
         patch('httpx.AsyncClient') as cli:
        cli.return_value.__aenter__.return_value.post = AsyncMock(return_value=fake_resp)
        r = await credit_note_delivery.send_credit_note_for_refund(
            refund_id='re_test_fail',
            session_id='cs_test_fail',
            customer_email='c@example.com',
            amount_cents=1500,
        )
    assert r['ok'] is False
    assert r['reason'] == 'resend_403'
    assert r['credit_note_number'] == 'AVOIR-2026-000013'
