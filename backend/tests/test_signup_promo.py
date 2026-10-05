from datetime import datetime, timezone
from unittest.mock import MagicMock
from services import signup_promo as sp

def _sb(created, done=False):
    sb = MagicMock()
    def table(name):
        t = MagicMock()
        if name == 'profiles':
            t.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = {'created_at': created}
        elif name == 'credit_transactions':
            t.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = [{'id': 1}] if done else []
        return t
    sb.table.side_effect = table
    return sb

def test_window():
    assert sp.is_active(datetime(2026, 10, 4, tzinfo=timezone.utc))
    assert not sp.is_active(datetime(2026, 10, 6, tzinfo=timezone.utc))
    assert not sp.is_active(datetime(2026, 10, 1, tzinfo=timezone.utc))

def test_grant_once(monkeypatch):
    monkeypatch.setattr(sp, 'is_active', lambda now=None: True)
    sp._checked.clear()
    assert sp.grant_if_eligible(_sb('2026-10-04T10:00:00+00:00'), 'u1', 20) == 100
    assert sp.grant_if_eligible(_sb('2026-10-04T10:00:00+00:00'), 'u1', 20) == 0

def test_old_account_and_already_done(monkeypatch):
    monkeypatch.setattr(sp, 'is_active', lambda now=None: True)
    sp._checked.clear()
    assert sp.grant_if_eligible(_sb('2026-01-01T00:00:00+00:00'), 'u2', 20) == 0
    assert sp.grant_if_eligible(_sb('2026-10-04T10:00:00+00:00', done=True), 'u3', 20) == 0
