"""Tests unitaires de services.promo_bypass.try_consume_promo (SEC-004)."""
import os
import sys
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import types

import pytest

_stub = types.ModuleType('services.supabase_client')
_stub.get_admin_client = lambda: None
sys.modules.setdefault('services.supabase_client', _stub)

from services import promo_bypass  # noqa: E402


class FakeQuery:
    def __init__(self, sb, table):
        self.sb, self.table, self.op, self.filters = sb, table, 'select', {}

    def select(self, *_):
        return self

    def update(self, _):
        self.op = 'update'
        self.update_data = _
        return self

    def insert(self, row):
        self.sb.redemptions.append(row)
        return self

    def eq(self, k, v):
        self.filters[k] = v
        return self

    def maybe_single(self):
        return self

    def execute(self):
        r = MagicMock()
        if self.table == 'profiles':
            r.data = {'is_admin': self.sb.is_admin}
        elif self.table == 'promo_codes':
            if self.op == 'select':
                self.sb.queried.append(self.filters.get('code'))
                assert self.filters.get('active') is True
                r.data = (
                    {'code': self.filters.get('code'), 'max_uses': self.sb.max_uses,
                     'used_count': self.sb.used_count}
                    if self.sb.active else None
                )
            else:
                self.sb.updates.append((self.update_data, self.filters.copy()))
                r.data = [{}] if self.sb.cas_success else []
        else:
            r.data = None
        return r


class FakeSB:
    def __init__(self, is_admin=False, active=True, max_uses=None, used_count=0,
                 cas_success=True):
        self.is_admin = is_admin
        self.active, self.max_uses = active, max_uses
        self.used_count, self.cas_success = used_count, cas_success
        self.redemptions, self.queried = [], []
        self.updates = []

    def table(self, name):
        return FakeQuery(self, name)


@pytest.fixture
def make_sb(monkeypatch):
    def _make(is_admin=False, **kwargs):
        sb = FakeSB(is_admin, **kwargs)
        monkeypatch.setattr(promo_bypass, 'get_admin_client', lambda: sb)
        return sb
    monkeypatch.delenv('PROMO_BYPASS_CODE', raising=False)
    monkeypatch.delenv('PROMO_BYPASS_ALLOWED_EMAILS', raising=False)
    return _make


def test_admin_ok(make_sb):
    sb = make_sb(is_admin=True)
    assert promo_bypass.try_consume_promo('TOUT2026', {'id': 'u1', 'email': 'a@x.fr'}, 'p')
    assert sb.redemptions[0]['user_id'] == 'u1'


def test_allowed_email_ok_case_insensitive(make_sb, monkeypatch):
    make_sb(is_admin=False)
    monkeypatch.setenv('PROMO_BYPASS_ALLOWED_EMAILS', 'Friend@Example.com, other@x.fr')
    assert promo_bypass.try_consume_promo('TOUT2026', {'id': 'u2', 'email': 'friend@example.COM'})


def test_unauthorized_user_rejected(make_sb, monkeypatch):
    make_sb(is_admin=False)
    monkeypatch.setenv('PROMO_BYPASS_ALLOWED_EMAILS', 'friend@example.com')
    assert not promo_bypass.try_consume_promo('TOUT2026', {'id': 'u3', 'email': 'nobody@x.fr'})


def test_guest_rejected_even_with_allowed_email(make_sb, monkeypatch):
    make_sb(is_admin=True)
    monkeypatch.setenv('PROMO_BYPASS_ALLOWED_EMAILS', 'friend@example.com')
    assert not promo_bypass.try_consume_promo('TOUT2026', None)
    assert not promo_bypass.try_consume_promo('TOUT2026', {'email': 'friend@example.com'})


def test_sentinel_resolved_via_env(make_sb, monkeypatch):
    sb = make_sb(is_admin=True)
    monkeypatch.setenv('PROMO_BYPASS_CODE', 'secret-code')
    assert promo_bypass.try_consume_promo('__ADMIN_BYPASS__', {'id': 'u1'})
    assert sb.queried == ['SECRET-CODE']


def test_sentinel_default_code(make_sb):
    sb = make_sb(is_admin=True)
    assert promo_bypass.try_consume_promo('__ADMIN_BYPASS__', {'id': 'u1'})
    assert sb.queried == ['TOUT2026']


def test_sentinel_rejected_for_unauthorized(make_sb):
    sb = make_sb(is_admin=False)
    assert not promo_bypass.try_consume_promo('__ADMIN_BYPASS__', {'id': 'u9', 'email': 'z@x.fr'})
    assert sb.queried == []


@pytest.mark.parametrize('kwargs', [
    {'active': False},
    {'max_uses': 2, 'used_count': 2},
    {'max_uses': 0},
])
def test_inactive_or_exhausted_promo_rejected(make_sb, kwargs):
    sb = make_sb(is_admin=True, **kwargs)
    assert not promo_bypass.try_consume_promo('__ADMIN_BYPASS__', {'id': 'u1'})
    assert sb.updates == []
    assert sb.redemptions == []


def test_cas_conflict_does_not_log_redemption(make_sb):
    sb = make_sb(is_admin=True, used_count=3, cas_success=False)
    assert not promo_bypass.try_consume_promo('__ADMIN_BYPASS__', {'id': 'u1'})
    assert sb.updates == [({'used_count': 4}, {'code': 'TOUT2026', 'used_count': 3})]
    assert sb.redemptions == []


def test_cas_success_logs_authenticated_user_and_product(make_sb):
    sb = make_sb(is_admin=True, used_count=3, max_uses=5)
    user = {'id': 'u1', 'email': 'admin@example.com'}
    assert promo_bypass.try_consume_promo('__ADMIN_BYPASS__', user, 'composer_book')
    assert sb.updates == [({'used_count': 4}, {'code': 'TOUT2026', 'used_count': 3})]
    assert sb.redemptions == [{
        'code': 'TOUT2026', 'user_id': 'u1', 'user_email': user['email'],
        'product': 'composer_book',
    }]


def test_client_admin_flag_is_not_authoritative(make_sb):
    sb = make_sb(is_admin=False)
    assert not promo_bypass.is_bypass_authorized({'id': 'u1', 'is_admin': True})
    assert sb.queried == []


@pytest.fixture
def composer_client(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    for key in ('SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_ANON_KEY',
                'SUPABASE_JWT_SECRET'):
        monkeypatch.setenv(key, 'offline-test-placeholder')
    from routes import composer
    from middleware import auth

    monkeypatch.setattr(auth, 'verify_supabase_token',
                        lambda token: {'sub': 'u1', 'email': 'friend@example.com'})
    app = FastAPI()
    app.include_router(composer.router, prefix='/api')
    with TestClient(app) as client:
        yield client


def test_composer_imports_and_restored_public_endpoints(composer_client):
    from services import promo_bootstrap
    assert promo_bootstrap.get_bypass_code is promo_bypass.get_bypass_code
    paths = {route.path for route in composer_client.app.routes}
    assert {
        '/api/composer/chapters', '/api/composer/quote', '/api/composer/apply-promo',
        '/api/composer/checkout', '/api/composer/status/{session_id}',
    } <= paths
    catalog = composer_client.get('/api/composer/chapters')
    assert catalog.status_code == 200
    assert 'TOUT2026' not in catalog.text
    assert '__ADMIN_BYPASS__' not in catalog.text
    quote = composer_client.post('/api/composer/quote', json={
        'edition': 'numerique', 'chapter_slugs': [],
    })
    assert quote.status_code == 200
    assert quote.json()['total_eur'] == 24


@pytest.mark.parametrize('authenticated,admin,allowlisted,valid', [
    (False, True, True, False),
    (True, False, False, False),
    (True, True, False, True),
    (True, False, True, True),
])
def test_composer_promo_requires_authenticated_authorization(
    composer_client, make_sb, monkeypatch, authenticated, admin, allowlisted, valid,
):
    make_sb(is_admin=admin)
    monkeypatch.setenv('PROMO_BYPASS_CODE', 'backend-secret-code')
    if allowlisted:
        monkeypatch.setenv('PROMO_BYPASS_ALLOWED_EMAILS', ' FRIEND@EXAMPLE.COM ')
    token = 'offline-test-token'
    headers = {'Authorization': '{} {}'.format('Bearer', token)} if authenticated else {}
    response = composer_client.post('/api/composer/apply-promo', json={
        'code': '__ADMIN_BYPASS__', 'edition': 'numerique', 'chapter_slugs': [],
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()['valid'] is valid
    assert response.json()['total_eur'] == (0 if valid else 24)
    assert 'BACKEND-SECRET-CODE' not in response.text
    if valid:
        assert response.json()['code'] == '__ADMIN_BYPASS__'


def test_composer_never_returns_real_bypass_code(composer_client, make_sb, monkeypatch):
    make_sb(is_admin=True)
    monkeypatch.setenv('PROMO_BYPASS_CODE', 'backend-secret-code')
    token = 'offline-test-token'
    response = composer_client.post('/api/composer/apply-promo', json={
        'code': 'backend-secret-code', 'edition': 'numerique', 'chapter_slugs': [],
    }, headers={'Authorization': '{} {}'.format('Bearer', token)})
    assert response.json()['valid'] is True
    assert response.json()['code'] == '__ADMIN_BYPASS__'
    assert 'BACKEND-SECRET-CODE' not in response.text


@pytest.mark.parametrize('authenticated,admin,allowlisted,promo_options,bypassed', [
    (False, True, True, {}, False),
    (True, False, False, {}, False),
    (True, True, False, {}, True),
    (True, False, True, {}, True),
    (True, True, False, {'active': False}, False),
    (True, True, False, {'max_uses': 1, 'used_count': 1}, False),
    (True, True, False, {'cas_success': False}, False),
])
def test_composer_checkout_preserves_auth_quota_and_cas(
    composer_client, make_sb, monkeypatch, authenticated, admin, allowlisted,
    promo_options, bypassed,
):
    from routes import composer

    sb = make_sb(is_admin=admin, **promo_options)
    if allowlisted:
        monkeypatch.setenv('PROMO_BYPASS_ALLOWED_EMAILS', 'friend@example.com')
    transactions = MagicMock()
    monkeypatch.setattr(composer, 'get_admin_client', lambda: transactions)
    stripe_checkout = MagicMock()
    stripe_checkout.create_checkout_session = AsyncMock(
        return_value=types.SimpleNamespace(session_id='cs_paid', url='https://stripe.example')
    )
    monkeypatch.setattr(composer, 'StripeCheckout', lambda **_: stripe_checkout)
    pipeline = types.ModuleType('services.book_engine.pipeline')
    pipeline.build_book_pdf_for_session = AsyncMock()
    monkeypatch.setitem(sys.modules, 'services.book_engine.pipeline', pipeline)
    token = 'offline-test-token'
    headers = {'Authorization': '{} {}'.format('Bearer', token)} if authenticated else {}
    response = composer_client.post('/api/composer/checkout', json={
        'edition': 'numerique', 'chapter_slugs': [], 'email': 'recipient@example.com',
        'first_name': 'Test', 'birth_date': '1990-01-01', 'birth_time': '10:00',
        'birth_city': 'Paris', 'origin_url': 'https://example.com',
        'promo_code': '__ADMIN_BYPASS__',
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data.get('promo_applied', False) is bypassed
    assert data['quote']['total_eur'] == (0 if bypassed else 24)
    assert bool(sb.redemptions) is bypassed
    tx = transactions.table.return_value.insert.call_args.args[0]
    assert tx['amount'] == (0 if bypassed else 24)
    assert tx['payment_status'] == ('paid' if bypassed else 'unpaid')
    if bypassed:
        stripe_checkout.create_checkout_session.assert_not_awaited()
        assert sb.redemptions[0]['user_email'] == 'friend@example.com'
        assert sb.redemptions[0]['product'] == 'composer_book'
        assert tx['user_email'] == 'recipient@example.com'
        assert data['session_id'].startswith('promo_')
    else:
        stripe_checkout.create_checkout_session.assert_awaited_once()
        assert data['session_id'] == 'cs_paid'
