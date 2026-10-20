"""Print validation must complete before sending a paid production order."""
import asyncio
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
import pytest
from services.lulu_client import cover_dimensions, validate_print_files, is_mock


def test_production_is_default(monkeypatch):
    monkeypatch.delenv('LULU_MOCK',raising=False)
    assert not is_mock()


def test_mock_cannot_pass_real_preflight(monkeypatch):
    monkeypatch.setenv('LULU_MOCK','1')
    with pytest.raises(RuntimeError,match='réelle'):
        asyncio.run(validate_print_files('https://example.org/i.pdf','https://example.org/c.pdf',48))


@pytest.mark.parametrize('pages', [42, 150])
def test_cover_request_uses_real_page_count(monkeypatch, pages):
    monkeypatch.setenv('LULU_MOCK','0')
    monkeypatch.setenv('LULU_BASE_URL','https://api.sandbox.lulu.com')
    monkeypatch.setenv('LULU_POD_PACKAGE_ID','A5-binding')
    response=SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'width':'320','height':'230','unit':'mm'})
    client=AsyncMock(); client.post.return_value=response
    context=AsyncMock(); context.__aenter__.return_value=client
    with patch('services.lulu_client._get_token',AsyncMock(return_value='test-token')), patch('services.lulu_client.httpx.AsyncClient',return_value=context):
        result=asyncio.run(cover_dimensions(pages))
    assert result['unit']=='mm'
    assert client.post.call_args.kwargs['json']['interior_page_count']==pages
