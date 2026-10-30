"""Tests de services/stuck_sessions_alert — alerte admin > 1h."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from services import stuck_sessions_alert


def _row(session_id, status, payment_status, email='cliente@gmail.com',
         amount=24.0, created_minutes_ago=90, pack_id='natal'):
    created = datetime.now(timezone.utc) - timedelta(minutes=created_minutes_ago)
    return {
        'session_id': session_id,
        'user_email': email,
        'pack_id': pack_id,
        'amount': amount,
        'currency': 'eur',
        'status': status,
        'payment_status': payment_status,
        'metadata': {},
        'created_at': created.isoformat(),
    }


def _patch_sb(rows):
    """Patch supabase client pour renvoyer `rows` lors du select."""
    exec_result = MagicMock(data=rows)
    builder = MagicMock()
    builder.select.return_value = builder
    builder.gte.return_value = builder
    builder.order.return_value = builder
    builder.limit.return_value = builder
    builder.execute.return_value = exec_result
    sb = MagicMock()
    sb.table.return_value = builder
    return patch('services.stuck_sessions_alert.get_admin_client', return_value=sb)


def test_fresh_session_not_alerted():
    rows = [_row('cs_live_fresh', 'initiated', 'unpaid', created_minutes_ago=5)]
    stuck_sessions_alert._alerted.clear()
    with _patch_sb(rows):
        stuck = stuck_sessions_alert._collect_stuck_sessions(threshold_min=60)
    assert stuck == []


def test_old_session_is_stuck():
    rows = [_row('cs_live_old', 'initiated', 'unpaid', created_minutes_ago=90)]
    stuck_sessions_alert._alerted.clear()
    with _patch_sb(rows):
        stuck = stuck_sessions_alert._collect_stuck_sessions(threshold_min=60)
    assert len(stuck) == 1
    assert stuck[0]['session_id'] == 'cs_live_old'
    assert stuck[0]['_age_min'] >= 60


def test_test_emails_filtered_out():
    rows = [
        _row('cs_live_test', 'initiated', 'unpaid',
             email='contact@plume-astrale.fr', created_minutes_ago=120),
        _row('cs_live_real', 'initiated', 'unpaid',
             email='cliente@gmail.com', created_minutes_ago=120),
    ]
    stuck_sessions_alert._alerted.clear()
    with _patch_sb(rows):
        stuck = stuck_sessions_alert._collect_stuck_sessions(threshold_min=60)
    assert len(stuck) == 1
    assert stuck[0]['user_email'] == 'cliente@gmail.com'


def test_paid_sessions_not_flagged():
    """Si une ligne `paid` existe pour la même session, elle n'est pas bloquée."""
    rows = [
        _row('cs_live_mixed', 'initiated', 'unpaid', created_minutes_ago=120),
        _row('cs_live_mixed', 'paid', 'paid', created_minutes_ago=100),
    ]
    stuck_sessions_alert._alerted.clear()
    with _patch_sb(rows):
        stuck = stuck_sessions_alert._collect_stuck_sessions(threshold_min=60)
    assert stuck == []


def test_already_alerted_sessions_filtered():
    """Après avoir alerté, le cooldown Mongo filtre au scan suivant.
    Note : le filtre a été déplacé dans `check_once` (async), donc
    `_collect_stuck_sessions` renvoie désormais TOUS les candidats bloqués ;
    la dédup se fait côté `check_once` via `services.alert_cooldown`.
    """
    rows = [_row('cs_live_old', 'initiated', 'unpaid', created_minutes_ago=90)]
    with _patch_sb(rows):
        stuck = stuck_sessions_alert._collect_stuck_sessions(threshold_min=60)
    # Candidat renvoyé — le filtrage se fait maintenant au niveau cooldown
    assert len(stuck) == 1
    assert stuck[0]['session_id'] == 'cs_live_old'


@pytest.mark.asyncio
async def test_check_once_sends_email(monkeypatch):
    """Scenario e2e : 2 sessions bloquées → 1 email envoyé, cooldown mocké True."""
    rows = [
        _row('cs_live_a', 'initiated', 'unpaid', created_minutes_ago=90, amount=29.0),
        _row('cs_live_b', 'initiated', 'unpaid', created_minutes_ago=120, amount=49.0,
             email='autre@gmail.com'),
    ]
    monkeypatch.setenv('ADMIN_ALERT_EMAIL', 'admin@test.local')
    mock_send = AsyncMock(return_value='resend_fake_id')
    mock_acquire = AsyncMock(return_value=True)  # cooldown ouvert
    with _patch_sb(rows), \
         patch('services.stuck_sessions_alert.send_email', mock_send), \
         patch('services.alert_cooldown.try_acquire', mock_acquire):
        n = await stuck_sessions_alert.check_once()
    assert n == 2
    mock_send.assert_awaited_once()
    args, _kwargs = mock_send.call_args
    subject = args[1]
    html = args[2]
    assert '2 sessions' in subject.lower() or '2 session' in subject.lower()
    assert 'cs_live_a' in html
    assert 'cs_live_b' in html
    # Les 2 sessions ont acquis le lock
    assert mock_acquire.await_count == 2


@pytest.mark.asyncio
async def test_check_once_cooldown_blocks(monkeypatch):
    """Si le cooldown bloque toutes les sessions, aucun email ne part."""
    rows = [_row('cs_live_locked', 'initiated', 'unpaid', created_minutes_ago=90)]
    monkeypatch.setenv('ADMIN_ALERT_EMAIL', 'admin@test.local')
    mock_send = AsyncMock(return_value='x')
    mock_acquire = AsyncMock(return_value=False)
    with _patch_sb(rows), \
         patch('services.stuck_sessions_alert.send_email', mock_send), \
         patch('services.alert_cooldown.try_acquire', mock_acquire):
        n = await stuck_sessions_alert.check_once()
    assert n == 0
    mock_send.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_once_empty_no_email(monkeypatch):
    monkeypatch.setenv('ADMIN_ALERT_EMAIL', 'admin@test.local')
    mock_send = AsyncMock(return_value='x')
    with _patch_sb([]), patch('services.stuck_sessions_alert.send_email', mock_send):
        n = await stuck_sessions_alert.check_once()
    assert n == 0
    mock_send.assert_not_awaited()
