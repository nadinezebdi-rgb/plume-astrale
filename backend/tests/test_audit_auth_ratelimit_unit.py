"""Tests unitaires : JWT, rate limit, checkout legacy, URL signée, session_id admin (audit points 4-8)."""
import asyncio
import os
import sys
import time
import types
from unittest.mock import MagicMock

os.environ.setdefault('SUPABASE_URL', 'http://supabase.test')
os.environ.setdefault('SUPABASE_SERVICE_ROLE_KEY', 'x')
os.environ.setdefault('SUPABASE_ANON_KEY', 'x')
os.environ.setdefault('SUPABASE_JWT_SECRET', 'unit-test-secret-unit-test-secret-32b')
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from middleware import auth
from services import rate_limit as rl

SECRET = os.environ['SUPABASE_JWT_SECRET']


# ── JWT ─────────────────────────────────────────────────────────
def _token(alg='HS256', **claims):
    payload = {'sub': 'user-1', 'aud': 'authenticated', 'exp': int(time.time()) + 600, 'email': 'a@b.fr'}
    payload.update(claims)
    payload = {k: v for k, v in payload.items() if v is not None}
    return jwt.encode(payload, SECRET, algorithm=alg)


def test_jwt_valid():
    assert auth.verify_supabase_token(_token())['sub'] == 'user-1'


@pytest.mark.parametrize('token', [
    _token(aud='anon'),
    _token(aud=None),
    _token(sub=None),
    _token(exp=int(time.time()) - 10),
    _token(alg='HS384'),
    'not-a-jwt',
    jwt.encode({'sub': 'u', 'aud': 'authenticated', 'exp': int(time.time()) + 60}, '', algorithm='none'),
])
def test_jwt_rejected(token):
    with pytest.raises(HTTPException) as exc:
        auth.verify_supabase_token(token)
    assert exc.value.status_code == 401


# ── rate limit ──────────────────────────────────────────────────
def _app(max_calls=3):
    app = FastAPI()

    @app.get('/x', dependencies=[Depends(rl.rate_limit('t', max_calls))])
    async def x():
        return {'ok': True}
    return app


def test_rate_limit_blocks_after_max():
    rl._HITS.clear()
    c = TestClient(_app(3))
    assert [c.get('/x').status_code for _ in range(5)] == [200, 200, 200, 429, 429]
    assert 'retry-after' in c.get('/x').headers


def test_rate_limit_window_expires(monkeypatch):
    rl._HITS.clear()
    assert rl._check(('w', '1.1.1.1'), 1, 0.05) == 0
    assert rl._check(('w', '1.1.1.1'), 1, 0.05) > 0
    time.sleep(0.07)
    assert rl._check(('w', '1.1.1.1'), 1, 0.05) == 0


def _req(headers):
    return Request({'type': 'http', 'headers': [(k.lower().encode(), v.encode()) for k, v in headers.items()],
                    'client': ('9.9.9.9', 1)})


def test_client_ip_reads_from_the_right(monkeypatch):
    monkeypatch.delenv('TRUSTED_PROXY_HOPS', raising=False)
    # la valeur de gauche est contrôlée par le client ; le proxy ajoute la vraie IP à droite
    assert rl.client_ip(_req({'x-forwarded-for': '6.6.6.6, 1.2.3.4'})) == '1.2.3.4'
    monkeypatch.setenv('TRUSTED_PROXY_HOPS', '2')
    assert rl.client_ip(_req({'x-forwarded-for': '6.6.6.6, 1.2.3.4, 10.0.0.1'})) == '1.2.3.4'
    assert rl.client_ip(_req({})) == '9.9.9.9'


# ── URL signée Supabase ─────────────────────────────────────────
def _sb_signing(result=None, exc=None):
    sb = MagicMock()
    bucket = sb.storage.from_.return_value
    if exc:
        bucket.create_signed_url.side_effect = exc
    else:
        bucket.create_signed_url.return_value = result
    return sb


PUBLIC = 'https://p.supabase.co/storage/v1/object/public/reports/pdfs/kabbale/abc.pdf'


def test_signed_url_used(monkeypatch):
    from services import pdf_download
    stub = types.ModuleType('services.supabase_client')
    stub.get_admin_client = lambda: _sb_signing({'signedURL': 'https://p.supabase.co/storage/v1/object/sign/reports/x?token=t'})
    monkeypatch.setitem(sys.modules, 'services.supabase_client', stub)
    assert pdf_download._short_lived_url(PUBLIC).endswith('?token=t')


def test_signed_url_relative_result(monkeypatch):
    from services import pdf_download
    stub = types.ModuleType('services.supabase_client')
    stub.get_admin_client = lambda: _sb_signing({'signedURL': '/object/sign/reports/x?token=t'})
    monkeypatch.setitem(sys.modules, 'services.supabase_client', stub)
    assert pdf_download._short_lived_url(PUBLIC) == 'https://p.supabase.co/storage/v1/object/sign/reports/x?token=t'


def test_signed_url_falls_back_to_public(monkeypatch):
    from services import pdf_download
    stub = types.ModuleType('services.supabase_client')
    stub.get_admin_client = lambda: _sb_signing(exc=RuntimeError('boom'))
    monkeypatch.setitem(sys.modules, 'services.supabase_client', stub)
    assert pdf_download._short_lived_url(PUBLIC) == PUBLIC
    assert pdf_download._short_lived_url('https://other.example/file.pdf') == 'https://other.example/file.pdf'


# ── admin_book : session_id ─────────────────────────────────────
def test_admin_book_session_id_pattern():
    import re
    from routes import admin_book
    ok = re.compile(admin_book._SID_PATTERN)
    assert ok.match('cs_live_AbC123-xyz')
    for bad in ('../etc/passwd', 'a/b', 'a b', '', 'x' * 101, 'a\\b'):
        assert not ok.match(bad)
