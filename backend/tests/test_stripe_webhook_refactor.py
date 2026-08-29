"""Test de régression pour le refactor webhook Stripe (Feb 2026).

Vérifie les 3 pièges classiques audités + les invariants d'idempotence :
  1. Raw body (bytes) passé à `construct_event`
  2. Réponse 200 rapide + traitement en background
  3. Idempotence globale via `stripe_webhook_events.event_id` + reprise `failed`
  4. Whitelist `HANDLED_EVENT_TYPES` bloque les types non gérés
  5. Insert non-23505 remonte (pas d'idempotence silencieuse)
  6. Event `failed` en base est ré-attribué, pas renvoyé comme done
  7. Concurrence : deux claims simultanés → un seul traite
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
    assert 'await request.body()' in src
    assert 'await request.json()' not in src


def test_endpoint_verifies_signature_with_construct_event():
    """L'endpoint doit valider la signature via `stripe.Webhook.construct_event`."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert 'Webhook.construct_event' in src
    assert re.search(r'Webhook\.construct_event\(body,\s*sig,\s*webhook_secret\)', src)


def test_endpoint_400_on_invalid_signature():
    """Signature invalide → HTTP 400 (pas 500 : évite retry loop 3j)."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert re.search(r"status_code\s*=\s*400", src)
    assert 'SignatureVerificationError' in src or '_SigErr' in src


def test_endpoint_returns_before_processing():
    """L'endpoint doit spawn via `_spawn(_process_stripe_event_safe(...))`."""
    from server import stripe_webhook
    src = inspect.getsource(stripe_webhook)
    assert '_spawn(_process_stripe_event_safe' in src
    assert re.search(r"return\s*\{[^}]*'queued'", src)


def test_whitelist_event_types_defined():
    """`HANDLED_EVENT_TYPES` doit exister et contenir les types réellement traités."""
    from server import HANDLED_EVENT_TYPES
    assert isinstance(HANDLED_EVENT_TYPES, (set, frozenset))
    # Types que `_process_stripe_event` sait vraiment traiter (audit Feb 2026)
    required = {
        'checkout.session.completed',
        'charge.refunded',
        'refund.created',
        'refund.updated',
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
        'invoice.payment_succeeded',
    }
    missing = required - HANDLED_EVENT_TYPES
    assert not missing, f'HANDLED_EVENT_TYPES incomplète, manque: {missing}'


def test_processor_wrapper_catches_exceptions():
    """`_process_stripe_event_safe` wrappe le routing dans try/except + mark failed."""
    from server import _process_stripe_event_safe, _mark_webhook
    src = inspect.getsource(_process_stripe_event_safe)
    assert 'try:' in src
    assert 'except Exception' in src
    assert '_mark_webhook' in src


def test_processor_wrapper_no_raise_on_inner_failure():
    """Le wrapper capture les erreurs, ne raise jamais vers l'appelant."""
    from unittest.mock import patch
    from server import _process_stripe_event_safe

    async def _failing(event, event_type, data_obj, event_id=None):
        raise ValueError('boom')

    with patch('server._process_stripe_event', side_effect=_failing):
        # Ne doit pas raise (le wrapper capture + mark failed)
        asyncio.run(_process_stripe_event_safe({}, 'test.type', {}, 'evt_regr_001'))


def test_asyncio_imported_at_module_level():
    """`asyncio` doit être importé au niveau module (utilisé par _spawn)."""
    import server
    assert 'asyncio' in dir(server)


# ═════════════════════════════════════════════════════════════════════════
# Tests d'idempotence — les 3 additions demandées par l'audit externe
# ═════════════════════════════════════════════════════════════════════════

def test_claim_event_reraises_non_23505():
    """Insert qui échoue sur autre chose qu'un 23505 doit LEVER, pas traiter.

    Sans ligne en base, il n'y a plus d'idempotence : mieux vaut 500 → Stripe
    replay que doublon silencieux.
    """
    from unittest.mock import MagicMock
    from server import _claim_event

    sb = MagicMock()
    # Simule une erreur générique (table absente, réseau down, RLS...)
    sb.table.return_value.insert.return_value.execute.side_effect = Exception(
        'ECONNREFUSED — supabase unreachable'
    )

    with pytest.raises(Exception, match='ECONNREFUSED'):
        _claim_event(sb, 'evt_test_reraise_001', 'checkout.session.completed',
                     None, None, {})


def test_claim_event_reclaims_failed_row():
    """Event déjà en base avec status='failed' doit repartir en 'reclaimed'.

    C'est ce qui rend le bouton `Resend` de Stripe et le recovery admin
    réellement utiles.
    """
    from unittest.mock import MagicMock
    from server import _claim_event

    sb = MagicMock()
    # 1er appel INSERT → 23505 (event déjà connu)
    insert_mock = sb.table.return_value.insert.return_value.execute
    insert_mock.side_effect = Exception('duplicate key value violates unique constraint "stripe_webhook_events_pkey" (23505)')

    # 1er UPDATE (status IN failed/received) → touche la ligne
    upd_res = MagicMock()
    upd_res.data = [{'event_id': 'evt_test_reclaim'}]
    sb.table.return_value.update.return_value.eq.return_value.in_.return_value.execute.return_value = upd_res

    result = _claim_event(sb, 'evt_test_reclaim', 'checkout.session.completed',
                          'cs_test', 'theme_natal', {'stub': True})
    assert result == 'reclaimed', f"attendu 'reclaimed', obtenu {result!r}"


def test_claim_event_concurrent_double_call_only_one_processes():
    """Deux claims simultanés sur le même event → un seul obtient 'new', l'autre 'done'.

    Simule : Stripe retry immédiat pendant que le premier traitement tourne
    encore (< 10 min, donc pas orphelin).
    """
    from unittest.mock import MagicMock
    from server import _claim_event

    sb = MagicMock()

    # Premier appel : INSERT réussit → 'new'
    call_state = {'insert_calls': 0}
    def _insert_side_effect():
        call_state['insert_calls'] += 1
        if call_state['insert_calls'] == 1:
            return MagicMock()  # succès
        # 2e appel : 23505
        raise Exception('duplicate key (23505)')

    sb.table.return_value.insert.return_value.execute.side_effect = _insert_side_effect

    # Pour le 2e appel : les UPDATE conditionnels retournent tous data=[]
    # (car status='processing' et pas orphelin)
    empty_res = MagicMock()
    empty_res.data = []
    sb.table.return_value.update.return_value.eq.return_value.in_.return_value.execute.return_value = empty_res
    sb.table.return_value.update.return_value.eq.return_value.eq.return_value.lt.return_value.execute.return_value = empty_res

    # 1er claim → new
    r1 = _claim_event(sb, 'evt_test_concurrent', 'checkout.session.completed', None, None, {})
    assert r1 == 'new'

    # 2e claim (simulation retry Stripe concurrent) → done (pas re-traité)
    r2 = _claim_event(sb, 'evt_test_concurrent', 'checkout.session.completed', None, None, {})
    assert r2 == 'done', f"attendu 'done' (concurrent processing), obtenu {r2!r}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
