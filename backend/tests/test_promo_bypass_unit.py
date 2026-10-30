"""Tests unitaires de services.promo_bypass.try_consume_promo (SEC-004)."""
import os
import sys
from unittest.mock import MagicMock

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
                r.data = {'code': self.filters.get('code'), 'max_uses': None, 'used_count': 0}
            else:
                r.data = [{}]
        else:
            r.data = None
        return r


class FakeSB:
    def __init__(self, is_admin=False):
        self.is_admin = is_admin
        self.redemptions, self.queried = [], []

    def table(self, name):
        return FakeQuery(self, name)


@pytest.fixture
def make_sb(monkeypatch):
    def _make(is_admin=False):
        sb = FakeSB(is_admin)
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
