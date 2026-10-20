"""Tests unitaires : origin_guard, payment_verification, accès legacy synastrie (audit points 1-3)."""
import asyncio
import os
import sys
import types
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi import HTTPException

from services import origin_guard
from services.payment_verification import verify_session_matches_transaction


# ── origin_guard ────────────────────────────────────────────────
@pytest.mark.parametrize('origin', [
    'https://plume-astrale.fr',
    'https://plume-astrale.fr/',
    'https://www.plume-astrale.fr',
    'http://localhost:3000',
    'HTTPS://Plume-Astrale.FR',
])
def test_origin_allowed(origin):
    assert origin_guard.validate_origin(origin).startswith(('https://', 'http://'))


@pytest.mark.parametrize('origin', [
    'https://evil.example',
    'https://plume-astrale.fr.evil.example',
    'https://plume-astrale.fr@evil.example',
    'http://plume-astrale.fr',
    'javascript:alert(1)',
    '//evil.example',
    '',
])
def test_origin_rejected(origin):
    with pytest.raises(HTTPException) as exc:
        origin_guard.validate_origin(origin)
    assert exc.value.status_code == 400


def test_origin_env_extension_ignores_wildcard(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', '*, https://preview.example.com')
    monkeypatch.setenv('FRONTEND_URL', 'https://front.example.com/')
    assert origin_guard.validate_origin('https://preview.example.com') == 'https://preview.example.com'
    assert origin_guard.validate_origin('https://front.example.com') == 'https://front.example.com'
    with pytest.raises(HTTPException):
        origin_guard.validate_origin('https://evil.example')


def test_redirect_url_validation():
    assert origin_guard.validate_redirect_url('https://plume-astrale.fr/ok?session_id={CHECKOUT_SESSION_ID}')
    with pytest.raises(HTTPException):
        origin_guard.validate_redirect_url('https://evil.example/ok')


# ── payment_verification ────────────────────────────────────────
TX = {'amount': 29.0, 'currency': 'eur'}


def _session(**kw):
    base = {'payment_status': 'paid', 'amount_total': 2900, 'currency': 'eur'}
    base.update(kw)
    return base


def test_verify_ok():
    assert verify_session_matches_transaction(_session(), TX) == (True, 'ok')


def test_verify_accepts_truncated_cents():
    # 19.99 * 100 = 1998.99999… → int() donne 1998, round() donne 1999
    tx = {'amount': 19.99, 'currency': 'eur'}
    assert verify_session_matches_transaction(_session(amount_total=1998), tx)[0]
    assert verify_session_matches_transaction(_session(amount_total=1999), tx)[0]


@pytest.mark.parametrize('session, tx', [
    (_session(), None),
    (_session(payment_status='unpaid'), TX),
    (_session(amount_total=100), TX),
    (_session(amount_total=None), TX),
    (_session(currency='usd'), TX),
])
def test_verify_rejects(session, tx):
    ok, reason = verify_session_matches_transaction(session, tx)
    assert not ok and reason


# ── accès legacy synastrie ──────────────────────────────────────
def _sb_with(record):
    sb = MagicMock()
    sb.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = (
        types.SimpleNamespace(data=record)
    )
    return sb


def _download(session_id, token, record):
    from services import pdf_download
    return asyncio.run(pdf_download._download_synastrie_pdf(session_id, token, _sb_with(record)))


LEGACY = {'id': 'abc', 'status': 'paid', 'pdf_path': '/api/assets/synastrie/synastrie_abc.pdf'}
REAL_SESSION = 'cs_live_' + 'a1B2c3D4e5F6g7H8i9J0k1L2'


def test_legacy_rejects_non_stripe_session_id():
    with pytest.raises(HTTPException) as exc:
        _download('admin-synastrie-0123456789abcdef', 'x', LEGACY)
    assert exc.value.status_code == 403


def test_legacy_kill_switch(monkeypatch):
    monkeypatch.setenv('SYNASTRIE_LEGACY_DOWNLOAD', '0')
    with pytest.raises(HTTPException) as exc:
        _download(REAL_SESSION, 'x', LEGACY)
    assert exc.value.status_code == 403


def test_tokenized_record_requires_matching_token():
    rec = {'id': 'abc', 'status': 'paid',
           'pdf_path': f'/api/pdf/download?session_id={REAL_SESSION}&token=goodtoken'}
    with pytest.raises(HTTPException) as exc:
        _download(REAL_SESSION, 'badtoken', rec)
    assert exc.value.status_code == 403
