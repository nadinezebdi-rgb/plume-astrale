"""Test fonctionnel du middleware d'attribution."""
import os, sys
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def app(monkeypatch):
    captured = {}

    def fake_persist(session_id, signals):
        captured['session_id'] = session_id
        captured['signals'] = signals

    from middleware import meta_attribution
    monkeypatch.setattr(meta_attribution, '_persist', fake_persist)

    application = FastAPI()
    application.middleware('http')(meta_attribution.meta_attribution_middleware)

    @application.post('/api/kabbale/checkout')
    async def kabbale_checkout():
        return {'url': 'https://stripe.test/pay', 'session_id': 'cs_test_123'}

    @application.get('/api/health')
    async def health():
        return {'ok': True}

    application.state.captured = captured
    return application


def test_reponse_intacte(app):
    r = TestClient(app).post('/api/kabbale/checkout')
    assert r.status_code == 200
    assert r.json() == {'url': 'https://stripe.test/pay', 'session_id': 'cs_test_123'}
    assert int(r.headers['content-length']) == len(r.content)


def test_attribution_captee(app):
    TestClient(app).post('/api/kabbale/checkout', headers={
        'X-Meta-Event-Id': 'evt-42',
        'X-Meta-Fbp': 'fb.1.1700000000.1234567890',
        'X-Meta-Fbc': 'fb.1.1700000000.AbCdEf',
        'X-Forwarded-For': '203.0.113.7, 10.0.0.1',
        'User-Agent': 'Mozilla/5.0 (test)',
        'Origin': 'https://plume-astrale.fr',
    })
    cap = app.state.captured
    assert cap['session_id'] == 'cs_test_123'
    s = cap['signals']
    assert s['event_id'] == 'evt-42'
    assert s['fbp'] == 'fb.1.1700000000.1234567890'
    assert s['client_ip'] == '203.0.113.7'
    assert s['event_source_url'] == 'https://plume-astrale.fr'


def test_sans_entetes_aucun_identifiant(app):
    TestClient(app).post('/api/kabbale/checkout')
    s = app.state.captured['signals']
    assert s['event_id'] is None and s['fbp'] is None and s['fbc'] is None


def test_routes_hors_checkout_ignorees(app):
    client = TestClient(app)
    client.post('/api/kabbale/checkout')
    app.state.captured.clear()
    r = client.get('/api/health')
    assert r.json() == {'ok': True}
    assert app.state.captured == {}
