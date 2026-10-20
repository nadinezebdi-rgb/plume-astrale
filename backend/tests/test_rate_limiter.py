"""Tests sécurité SEC-001/SEC-002 — rate limiter in-memory."""
import pytest
from unittest.mock import MagicMock

from services.rate_limiter import check_rate_limit, _buckets


def _mock_request(ip: str = '1.2.3.4', xff: str = None):
    """Simule un fastapi.Request avec client.host + éventuel X-Forwarded-For."""
    req = MagicMock()
    headers = {}
    if xff:
        headers['x-forwarded-for'] = xff
    req.headers = headers
    req.client = MagicMock()
    req.client.host = ip
    return req


@pytest.fixture(autouse=True)
def _reset_buckets():
    _buckets.clear()
    yield
    _buckets.clear()


@pytest.mark.asyncio
async def test_rate_limiter_allows_under_cap():
    req = _mock_request('10.0.0.1')
    for _ in range(5):
        await check_rate_limit(req, key='test', max_hits=5, window_seconds=60)


@pytest.mark.asyncio
async def test_rate_limiter_rejects_over_cap():
    from fastapi import HTTPException
    req = _mock_request('10.0.0.2')
    for _ in range(5):
        await check_rate_limit(req, key='test2', max_hits=5, window_seconds=60)
    with pytest.raises(HTTPException) as exc:
        await check_rate_limit(req, key='test2', max_hits=5, window_seconds=60)
    assert exc.value.status_code == 429
    assert 'Retry-After' in exc.value.headers


@pytest.mark.asyncio
async def test_rate_limiter_per_ip_isolation():
    """Deux IP différentes doivent avoir des compteurs indépendants."""
    req1 = _mock_request('10.0.0.3')
    req2 = _mock_request('10.0.0.4')
    for _ in range(5):
        await check_rate_limit(req1, key='test3', max_hits=5, window_seconds=60)
    # req2 ne doit PAS être bloquée par les hits de req1
    await check_rate_limit(req2, key='test3', max_hits=5, window_seconds=60)


@pytest.mark.asyncio
async def test_rate_limiter_respects_xff_header():
    """Le header X-Forwarded-For est utilisé prioritairement."""
    req1 = _mock_request('10.0.0.5', xff='8.8.8.8, 10.0.0.5')
    req2 = _mock_request('10.0.0.5', xff='9.9.9.9, 10.0.0.5')
    # Les 2 req ont la même IP source directe mais XFF différent → compteurs séparés
    for _ in range(5):
        await check_rate_limit(req1, key='test4', max_hits=5, window_seconds=60)
    # req2 (XFF différent) ne doit pas être bloquée
    await check_rate_limit(req2, key='test4', max_hits=5, window_seconds=60)


@pytest.mark.asyncio
async def test_rate_limiter_separate_keys():
    """Deux `key` différentes doivent avoir des compteurs indépendants pour la même IP."""
    req = _mock_request('10.0.0.6')
    for _ in range(5):
        await check_rate_limit(req, key='keyA', max_hits=5, window_seconds=60)
    # keyB doit rester OK
    await check_rate_limit(req, key='keyB', max_hits=5, window_seconds=60)
