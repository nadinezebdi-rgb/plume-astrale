from datetime import datetime, timezone

from services import public_free_promo as pfp


def _dt(s):
    return datetime.fromisoformat(s)


def test_code_valid_before_deadline(monkeypatch):
    monkeypatch.delenv('FREE_NATAL_PROMO_ENABLED', raising=False)
    assert pfp.is_active_code('natalOffert', now=_dt('2026-10-04T12:00:00+02:00'))


def test_code_rejected_after_monday(monkeypatch):
    monkeypatch.delenv('FREE_NATAL_PROMO_ENABLED', raising=False)
    assert not pfp.is_active_code('NATALOFFERT', now=_dt('2026-10-06T00:00:01+02:00'))


def test_wrong_code_or_product_rejected():
    now = _dt('2026-10-04T12:00:00+02:00')
    assert not pfp.is_active_code('AUTRE', now=now)
    assert not pfp.is_active_code('NATALOFFERT', product='synastrie', now=now)
    assert not pfp.is_active_code('', now=now)


def test_kill_switch(monkeypatch):
    monkeypatch.setenv('FREE_NATAL_PROMO_ENABLED', 'false')
    assert not pfp.is_active_code('NATALOFFERT', now=_dt('2026-10-04T12:00:00+02:00'))


def test_env_override(monkeypatch):
    monkeypatch.setenv('FREE_NATAL_PROMO_CODE', 'LUNDI')
    monkeypatch.setenv('FREE_NATAL_PROMO_UNTIL', '2026-10-10T00:00:00+00:00')
    assert pfp.is_active_code('lundi', now=datetime(2026, 10, 9, tzinfo=timezone.utc))
    assert not pfp.is_active_code('NATALOFFERT', now=datetime(2026, 10, 9, tzinfo=timezone.utc))


def test_redeemable_limits(monkeypatch):
    monkeypatch.delenv('FREE_NATAL_PROMO_ENABLED', raising=False)
    monkeypatch.setattr(pfp, 'is_active_code', lambda *a, **k: True)

    class R:
        def __init__(self, c): self.count = c

    monkeypatch.setattr(pfp, '_redemptions', lambda email=None: R(1 if email else 0))
    ok, msg = pfp.check_redeemable('X', 'a@b.fr')
    assert not ok and 'déjà' in msg

    monkeypatch.setattr(pfp, '_redemptions', lambda email=None: R(0 if email else 9999))
    ok, msg = pfp.check_redeemable('X', 'a@b.fr')
    assert not ok and 'maximum' in msg

    monkeypatch.setattr(pfp, '_redemptions', lambda email=None: R(0))
    assert pfp.check_redeemable('X', 'a@b.fr')[0]

    def boom(email=None): raise RuntimeError('db down')
    monkeypatch.setattr(pfp, '_redemptions', boom)
    assert not pfp.check_redeemable('X', 'a@b.fr')[0]
