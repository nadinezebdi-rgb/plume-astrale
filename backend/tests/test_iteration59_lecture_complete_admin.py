"""Iteration 59 — Lecture Complete admin endpoints, cache, cercle-status, sequence loop."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')


class TestAdminOrdersAuth:
    def test_admin_orders_no_auth_returns_401(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/admin/orders", timeout=15)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text[:200]}"

    def test_admin_orders_invalid_token_401(self):
        r = requests.get(
            f"{BASE_URL}/api/lecture-complete/admin/orders",
            headers={'Authorization': 'Bearer invalid_token_xxx'},
            timeout=15,
        )
        assert r.status_code == 401, f"Expected 401 with bad token, got {r.status_code}"


class TestAdminRedispatchAuth:
    def test_redispatch_no_auth_401(self):
        r = requests.post(f"{BASE_URL}/api/lecture-complete/admin/redispatch/some-sid", timeout=15)
        assert r.status_code == 401


class TestCercleStatus:
    def test_cercle_status_no_auth_returns_inactive(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/cercle-status", timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get('active') is False
        assert data.get('reason') == 'not_authenticated'


class TestScarcityCache:
    def test_scarcity_returns_valid_structure(self):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/scarcity", timeout=15)
        assert r.status_code == 200
        data = r.json()
        for k in ('remaining', 'sold', 'quota', 'cycle_end', 'sold_out'):
            assert k in data, f"missing key {k}"
        assert isinstance(data['remaining'], int)
        assert isinstance(data['sold_out'], bool)

    def test_scarcity_cache_returns_identical_object(self):
        """Cache TTL 60s → 2 appels consecutifs = donnees strictement identiques."""
        r1 = requests.get(f"{BASE_URL}/api/lecture-complete/scarcity", timeout=15).json()
        time.sleep(0.5)
        r2 = requests.get(f"{BASE_URL}/api/lecture-complete/scarcity", timeout=15).json()
        assert r1 == r2, f"Cache should return identical data:\n{r1}\n!=\n{r2}"


class TestSequenceLoopStructure:
    def test_sequence_module_importable(self):
        """Structural check: _process_transaction + loop exist."""
        import sys
        sys.path.insert(0, '/app/backend')
        from services import lecture_complete_sequence as seq
        assert hasattr(seq, '_process_transaction')
        assert hasattr(seq, 'lecture_complete_sequence_loop')
        assert hasattr(seq, '_run_once')

    def test_server_startup_registers_loop(self):
        """server.py must schedule lecture_complete_sequence_loop at startup."""
        with open('/app/backend/server.py') as f:
            src = f.read()
        assert 'lecture_complete_sequence_loop' in src
        assert 'create_task(lecture_complete_sequence_loop' in src.replace(' ', '')

    def test_scarcity_cache_uses_monotonic(self):
        with open('/app/backend/services/lecture_complete_bundle.py') as f:
            src = f.read()
        assert '_SCARCITY_CACHE' in src
        assert 'time.monotonic()' in src
        assert '_SCARCITY_CACHE_TTL_S' in src


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
