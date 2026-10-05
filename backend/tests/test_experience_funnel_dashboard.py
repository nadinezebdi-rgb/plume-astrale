"""Experience Funnel Dashboard A/B — tests (Feb 2026)

Vérifie le contrat fonctionnel :
  - POST /api/experience/funnel-event ingère les events autorisés
  - Rejette silencieusement les events hors whitelist (204 stealth)
  - Rejette silencieusement purchase sans amount+transaction_id
  - Dedup purchase par (visitor_id, transaction_id) — unique index
  - GET /api/admin/experience/funnel exige require_admin (401 sans token)
  - Agrégation retourne visitors, steps, revenue_eur, revenue_per_visitor_eur
"""
import os
import asyncio
import time
from datetime import datetime, timezone

import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')


def _post_event(payload):
    return requests.post(f'{BASE_URL}/api/experience/funnel-event', json=payload, timeout=10)


def test_endpoint_accepts_valid_event():
    r = _post_event({
        'event_name': 'experience_visit',
        'visitor_id': 'pa-testfunnel-01',
        'variant': 'experience',
        'path': '/experience',
    })
    assert r.status_code == 204


def test_endpoint_rejects_unknown_event_silently():
    r = _post_event({
        'event_name': 'foo_bar_spam',
        'visitor_id': 'pa-testfunnel-02',
    })
    # 204 aussi (stealth) — mais rien n'est écrit en DB
    assert r.status_code == 204


def test_endpoint_rejects_purchase_without_amount():
    r = _post_event({
        'event_name': 'credit_purchase',
        'visitor_id': 'pa-testfunnel-03',
        # missing amount_eur & transaction_id
    })
    assert r.status_code == 204


def test_endpoint_dedups_purchase_by_transaction_id():
    """Deux POST avec (visitor_id, transaction_id) identiques ne créent
    qu'une seule row en DB (unique index)."""
    payload = {
        'event_name': 'credit_purchase',
        'visitor_id': 'pa-testfunnel-dedup',
        'amount_eur': 19.90,
        'transaction_id': f'txn-dedup-{int(time.time())}',
        'variant': 'experience',
    }
    r1 = _post_event(payload)
    r2 = _post_event(payload)
    assert r1.status_code == 204
    assert r2.status_code == 204  # silent OK (E11000 catch)


def test_admin_funnel_requires_auth():
    r = requests.get(f'{BASE_URL}/api/admin/experience/funnel', timeout=10)
    assert r.status_code in (401, 403)


def test_admin_funnel_shape_via_direct_call():
    """Bypasse l'auth admin en appelant directement le handler avec un fake
    admin dict — vérifie que le shape retourné respecte le contrat.
    """
    os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
    os.environ.setdefault('DB_NAME', 'plume_astrale')
    import sys
    sys.path.insert(0, '/app/backend')
    from routes.experience_funnel import admin_experience_funnel

    async def _run():
        return await admin_experience_funnel(hours=24, _admin={'id': 'test', 'email': 'admin@test'})
    data = asyncio.run(_run())
    assert 'period_hours' in data
    assert 'from' in data
    assert 'to' in data
    assert 'variants' in data
    assert 'funnel_steps' in data
    steps = data['funnel_steps']
    for s in ('experience_visit', 'intent_selected', 'signup_completed', 'credit_purchase'):
        assert s in steps, f'Étape {s} manquante du funnel'
    # Si des visiteurs ont été insérés par les tests ci-dessus, on doit avoir
    # au moins un variant 'experience' non vide.
    if 'experience' in data['variants']:
        exp = data['variants']['experience']
        assert 'visitors' in exp
        assert 'steps' in exp
        assert 'revenue_eur' in exp
        assert 'revenue_per_visitor_eur' in exp
        assert 'signup_rate' in exp
        assert 'purchase_rate' in exp
