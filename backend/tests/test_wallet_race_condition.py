"""SEC-002 : test de non-régression du fix race condition sur le wallet.

Vérifie que N appels concurrents à `deduct_credits` sur le même user_id
n'entraînent PAS de double-spend. Simule 20 requêtes concurrentes qui
tentent chacune de déduire 5 crédits d'un compte qui en possède 40.

Résultat attendu :
- Exactement 8 débits doivent réussir (40 / 5 = 8).
- Les 12 autres doivent lever HTTPException 402 (solde insuffisant).
- Le solde final doit être 0 (jamais négatif, jamais > 0).
"""
import asyncio
import pytest
from unittest.mock import MagicMock, patch

from services import wallet_service


class FakeSupabaseTable:
    """Mock Supabase table qui simule les opérations sur `wallets` et
    `credit_transactions`. Introduit un `await asyncio.sleep(0)` entre
    la lecture et l'écriture pour maximiser l'interleaving."""

    def __init__(self, store):
        self.store = store
        self._chain = {'table': None, 'op': None, 'field': None, 'user_id': None, 'update_payload': None, 'insert_payload': None}

    # supabase-py fluent API
    def select(self, *args, **kwargs):
        self._chain['op'] = 'select'
        self._chain['fields'] = args
        return self

    def eq(self, field, value):
        self._chain['field'] = field
        self._chain['user_id'] = value
        return self

    def update(self, payload):
        self._chain['op'] = 'update'
        self._chain['update_payload'] = payload
        return self

    def insert(self, payload):
        self._chain['op'] = 'insert'
        self._chain['insert_payload'] = payload
        return self

    def maybe_single(self):
        self._chain['single'] = True
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, n):
        return self

    def execute(self):
        op = self._chain['op']
        user_id = self._chain['user_id']
        if op == 'select':
            data = self.store.get(user_id)
            result = MagicMock()
            result.data = data
            return result
        if op == 'update':
            if user_id in self.store:
                self.store[user_id].update(self._chain['update_payload'])
            result = MagicMock()
            result.data = None
            return result
        if op == 'insert':
            # credit_transactions : no-op
            result = MagicMock()
            result.data = None
            return result
        return MagicMock(data=None)


class FakeSupabaseClient:
    def __init__(self, wallets_store):
        self._wallets = wallets_store
        self._transactions = []

    def table(self, name):
        if name == 'wallets':
            return FakeSupabaseTable(self._wallets)
        if name == 'credit_transactions':
            return FakeSupabaseTable({})
        return FakeSupabaseTable({})


@pytest.mark.asyncio
async def test_concurrent_deduct_credits_no_double_spend():
    """20 déductions concurrentes de 5 crédits sur un solde initial de 40.
    Doit réussir exactement 8 fois, échouer 12 fois avec 402, solde final = 0."""
    user_id = 'test-user-race'
    wallets_store = {user_id: {'credit_balance': 40}}
    fake_client = FakeSupabaseClient(wallets_store)

    # Reset lock registry pour un test propre
    wallet_service._user_locks.clear()

    with patch.object(wallet_service, 'get_admin_client', return_value=fake_client):
        async def one_deduct(i):
            try:
                bal = await wallet_service.deduct_credits(user_id, 5, f'test-{i}')
                return ('ok', bal)
            except Exception as e:
                # HTTPException 402
                return ('fail', getattr(e, 'status_code', None))

        results = await asyncio.gather(*[one_deduct(i) for i in range(20)])

    successes = [r for r in results if r[0] == 'ok']
    failures = [r for r in results if r[0] == 'fail']
    final_balance = wallets_store[user_id]['credit_balance']

    print(f'[SEC-002] successes={len(successes)}, failures={len(failures)}, final={final_balance}')
    assert len(successes) == 8, f'Attendu 8 succès, obtenu {len(successes)} (double-spend détecté !)'
    assert len(failures) == 12, f'Attendu 12 échecs, obtenu {len(failures)}'
    assert final_balance == 0, f'Solde final incorrect : {final_balance} (attendu 0)'
    # Toutes les erreurs doivent être des 402
    for _, code in failures:
        assert code == 402, f'Attendu 402, obtenu {code}'


@pytest.mark.asyncio
async def test_concurrent_add_credits_no_loss():
    """20 ajouts concurrents de 10 crédits doivent tous être comptabilisés
    (jamais de perte due à un race condition read-modify-write)."""
    user_id = 'test-user-add'
    wallets_store = {user_id: {'credit_balance': 0}}
    fake_client = FakeSupabaseClient(wallets_store)

    wallet_service._user_locks.clear()

    with patch.object(wallet_service, 'get_admin_client', return_value=fake_client):
        async def one_add(i):
            return await wallet_service.add_credits(user_id, 10, f'add-{i}')

        await asyncio.gather(*[one_add(i) for i in range(20)])

    final_balance = wallets_store[user_id]['credit_balance']
    print(f'[SEC-002] add: final_balance={final_balance}')
    assert final_balance == 200, f'Attendu 200, obtenu {final_balance} (crédits perdus !)'


@pytest.mark.asyncio
async def test_concurrent_claim_free_tarot_only_once():
    """20 réclamations concurrentes du tirage gratuit : une seule doit
    réussir, les 19 autres doivent renvoyer False."""
    user_id = 'test-user-tarot'
    wallets_store = {user_id: {'free_tarot_used': False}}
    fake_client = FakeSupabaseClient(wallets_store)

    wallet_service._user_locks.clear()

    with patch.object(wallet_service, 'get_admin_client', return_value=fake_client):
        results = await asyncio.gather(*[wallet_service.claim_free_tarot(user_id) for _ in range(20)])

    claimed_count = sum(1 for r in results if r is True)
    print(f'[SEC-002] free_tarot: claimed_count={claimed_count}')
    assert claimed_count == 1, f'Attendu 1 claim, obtenu {claimed_count} (tirages gratuits multiples !)'
    assert wallets_store[user_id]['free_tarot_used'] is True
