"""Test de régression pour le refactor webhook Stripe (Feb 2026, incident P0).

Vérifie les 3 pièges classiques audités par ChatGPT :
  1. Raw body (bytes) passé à `construct_event`
  2. Réponse 200 rapide + traitement en background (< 1s)
  3. Idempotence globale via `stripe_webhook_events.event_id`
"""
from __future__ import annotations
import asyncio
import inspect
import re

import pytest


def test_endpoint_uses_raw_body():
    """L'endpoint doit lire `await request.body()` (bytes), pas parser en JSON."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert 'await request.body()' in src, 'endpoint doit lire le body en bytes'
    # Ne doit pas passer par un parsing pydantic ou request.json()
    assert 'await request.json()' not in src


def test_endpoint_verifies_signature_with_construct_event():
    """L'endpoint doit valider la signature via `stripe.Webhook.construct_event`."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert 'stripe.Webhook.construct_event' in src
    # Doit passer les 3 args (body, sig, secret) — pas d'autre appel
    assert re.search(r'stripe\.Webhook\.construct_event\(body,\s*sig,\s*webhook_secret\)', src)


def test_endpoint_returns_before_processing():
    """L'endpoint doit spawn le processing via `asyncio.create_task` avant de return."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    # Pattern : create_task(_process_stripe_event(...))  puis  return {...}
    assert 'asyncio.create_task(_process_stripe_event' in src
    # Le return final doit être un dict qui contient 'queued'
    assert re.search(r"return\s*\{[^}]*'queued'", src)


def test_processor_wrapper_catches_exceptions():
    """`_process_stripe_event` wrappe le routing dans try/except + marque failed."""
    from server import _process_stripe_event, _mark_webhook_failed
    src = inspect.getsource(_process_stripe_event)
    assert 'try:' in src
    assert 'except Exception' in src
    assert '_mark_webhook_failed' in src
    assert '_mark_webhook_done' in src
    # mark_webhook_failed doit exister comme helper
    assert callable(_mark_webhook_failed)


def test_processor_wrapper_no_raise_on_inner_failure():
    """Le wrapper capture les erreurs — ne doit JAMAIS raise vers l'appelant."""
    from unittest.mock import patch, AsyncMock
    from server import _process_stripe_event

    async def _failing(event, event_type, data_obj):
        raise ValueError('boom')

    with patch('server._process_stripe_event_inner', side_effect=_failing):
        # Ne doit pas raise (le wrapper capture)
        asyncio.run(_process_stripe_event({}, 'test.type', {}, 'evt_regr_001'))


def test_idempotence_table_insert_in_endpoint():
    """L'endpoint doit tenter un INSERT dans `stripe_webhook_events` pour la garde."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert "stripe_webhook_events" in src
    # Doit gérer le PK conflict → return idempotent
    assert re.search(r"'idempotent'\s*:\s*True", src)


def test_processor_inner_signature():
    """`_process_stripe_event_inner` doit accepter (event, event_type, data_obj)."""
    from server import _process_stripe_event_inner
    sig = inspect.signature(_process_stripe_event_inner)
    assert list(sig.parameters.keys()) == ['event', 'event_type', 'data_obj']


def test_asyncio_imported_at_module_level():
    """`asyncio` doit être importé au niveau module (utilisé par create_task)."""
    import server
    assert 'asyncio' in dir(server)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
