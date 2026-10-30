"""Tests unitaires services/slack_notify."""
import os
import pytest
from unittest.mock import AsyncMock, patch

from services import slack_notify


def test_is_configured_true(monkeypatch):
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/XXX')
    assert slack_notify.is_configured() is True


def test_is_configured_false(monkeypatch):
    monkeypatch.delenv('SLACK_WEBHOOK_URL', raising=False)
    assert slack_notify.is_configured() is False


@pytest.mark.asyncio
async def test_send_slack_alert_no_webhook(monkeypatch):
    """Fail-silent : pas de webhook → retourne False, aucune exception."""
    monkeypatch.delenv('SLACK_WEBHOOK_URL', raising=False)
    r = await slack_notify.send_slack_alert(title='test', summary='x')
    assert r is False


@pytest.mark.asyncio
async def test_send_slack_alert_success(monkeypatch):
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/X')
    fake_resp = AsyncMock()
    fake_resp.status_code = 200
    fake_resp.text = 'ok'
    with patch('httpx.AsyncClient') as cli:
        cli.return_value.__aenter__.return_value.post = AsyncMock(return_value=fake_resp)
        r = await slack_notify.send_slack_alert(
            title='stuck sessions',
            summary='3 sessions',
            fields=[('session', 'cs_x'), ('amount', '24€')],
            url='https://plume-astrale.fr/admin/payments-health',
        )
    assert r is True


@pytest.mark.asyncio
async def test_send_slack_alert_timeout(monkeypatch):
    """Timeout httpx → return False, no raise."""
    import httpx
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/X')
    with patch('httpx.AsyncClient') as cli:
        cli.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.TimeoutException('slow slack'),
        )
        r = await slack_notify.send_slack_alert(title='test', summary='x')
    assert r is False


@pytest.mark.asyncio
async def test_send_slack_alert_non_2xx(monkeypatch):
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/X')
    fake_resp = AsyncMock()
    fake_resp.status_code = 403
    fake_resp.text = 'invalid webhook'
    with patch('httpx.AsyncClient') as cli:
        cli.return_value.__aenter__.return_value.post = AsyncMock(return_value=fake_resp)
        r = await slack_notify.send_slack_alert(title='test', summary='x')
    assert r is False
