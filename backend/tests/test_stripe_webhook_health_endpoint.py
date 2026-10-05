"""Regression test — Stripe Webhook Health endpoint (Feb 2026)

Endpoint : GET /api/admin/stripe-webhook-health

Contrats critiques :
1. Ne DOIT JAMAIS retourner la valeur du secret (`whsec_...`) dans la réponse.
2. DOIT retourner un flag `ready: true` uniquement si secret + api_key sont OK.
3. DOIT donner des `hints` actionnables quand la config est incomplète.
4. DOIT être protégé (require_admin).
"""
import importlib
import os
import sys

sys.path.insert(0, '/app/backend')
os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'test_db')


def _get_endpoint():
    mod = importlib.import_module('routes.admin_payments')
    return mod.admin_stripe_webhook_health


def test_endpoint_is_registered_and_protected():
    """L'endpoint doit exister et exiger require_admin (via Depends)."""
    from routes import admin_payments
    src = open(admin_payments.__file__).read()
    assert "@router.get('/stripe-webhook-health')" in src, (
        'Route /stripe-webhook-health absente'
    )
    # Contexte de la ligne de l'endpoint : require_admin doit être en dépendance
    idx = src.find("/stripe-webhook-health")
    snippet = src[idx:idx + 400]
    assert 'require_admin' in snippet, (
        'require_admin manquant sur la route /stripe-webhook-health — '
        'l\'endpoint doit être protégé par l\'auth admin.'
    )


def test_endpoint_never_returns_raw_secret(monkeypatch):
    """Même quand le secret est configuré, la réponse ne doit PAS le contenir."""
    import asyncio
    from routes import admin_payments

    fake_secret = 'whsec_super_secret_do_not_leak_12345'
    monkeypatch.setenv('STRIPE_WEBHOOK_SECRET', fake_secret)
    monkeypatch.setenv('STRIPE_API_KEY', 'sk_test_dummy_1234')

    # Mock get_admin_client pour ne pas taper Supabase
    class _FakeTable:
        def select(self, *a, **k): return self
        def gte(self, *a, **k): return self
        def limit(self, *a, **k): return self
        def execute(self): return type('R', (), {'data': []})()
    class _FakeClient:
        def table(self, *a, **k): return _FakeTable()
    monkeypatch.setattr(admin_payments, 'get_admin_client', lambda: _FakeClient())

    endpoint = admin_payments.admin_stripe_webhook_health
    result = asyncio.run(endpoint(_admin={'email': 'admin@test'}))
    serialized = str(result)

    assert fake_secret not in serialized, (
        'Le secret Stripe complet a été retourné par l\'endpoint — LEAK CRITIQUE'
    )
    # Le secret entier ne doit jamais apparaître ; le fingerprint (8 chars) OK
    assert result['secret']['configured'] is True
    assert result['secret']['format_valid'] is True
    assert result['secret']['length'] == len(fake_secret)
    assert result['secret']['fingerprint'] and len(result['secret']['fingerprint']) == 8
    assert 'fingerprint' in result['secret']


def test_endpoint_reports_not_ready_when_secret_missing(monkeypatch):
    """Sans STRIPE_WEBHOOK_SECRET : ready=False + hint actionnable."""
    import asyncio
    from routes import admin_payments

    monkeypatch.delenv('STRIPE_WEBHOOK_SECRET', raising=False)
    monkeypatch.setenv('STRIPE_API_KEY', 'sk_test_dummy')

    class _FakeTable:
        def select(self, *a, **k): return self
        def gte(self, *a, **k): return self
        def limit(self, *a, **k): return self
        def execute(self): return type('R', (), {'data': []})()
    class _FakeClient:
        def table(self, *a, **k): return _FakeTable()
    monkeypatch.setattr(admin_payments, 'get_admin_client', lambda: _FakeClient())

    result = asyncio.run(
        admin_payments.admin_stripe_webhook_health(_admin={'email': 'admin@test'})
    )
    assert result['ready'] is False
    assert result['secret']['configured'] is False
    # Hint actionnable pour l'admin
    assert any('STRIPE_WEBHOOK_SECRET' in h for h in result['hints']), (
        f"Hint manquant sur secret absent. Hints reçus: {result['hints']}"
    )


def test_endpoint_flags_malformed_secret(monkeypatch):
    """Secret présent mais pas préfixé whsec_ → format_valid=False + hint."""
    import asyncio
    from routes import admin_payments

    monkeypatch.setenv('STRIPE_WEBHOOK_SECRET', '"whsec_avec_guillemet_faux"')
    monkeypatch.setenv('STRIPE_API_KEY', 'sk_live_dummy')

    class _FakeTable:
        def select(self, *a, **k): return self
        def gte(self, *a, **k): return self
        def limit(self, *a, **k): return self
        def execute(self): return type('R', (), {'data': []})()
    class _FakeClient:
        def table(self, *a, **k): return _FakeTable()
    monkeypatch.setattr(admin_payments, 'get_admin_client', lambda: _FakeClient())

    result = asyncio.run(
        admin_payments.admin_stripe_webhook_health(_admin={'email': 'admin@test'})
    )
    assert result['secret']['configured'] is True
    assert result['secret']['format_valid'] is False
    assert result['ready'] is False
    assert any('whsec_' in h for h in result['hints'])
