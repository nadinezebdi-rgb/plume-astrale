"""Iteration 61 — bundle Lecture Complete 4 features complementaires.

Tests :
  1. GET /admin/orders retourne stats {total_paid, total_refunded, refund_rate_pct}
  2. POST /admin/refund/{sid} : 401/403/404/200
  3. GET /cercle-status pour refunded user
  4. Batch fetch admin/orders utilise .in_('metadata->>parent_bundle', ...)
  5. services/lecture_complete_sequence.py contient _email_j30 + stage j30
  6. services/journal_email_service.py contient get_bundle_guests_for_daily_journal + scheduler
  7. Logs backend contiennent 'scheduler demarre' et 'batch quotidien'
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://consultation-astro.preview.emergentagent.com').rstrip('/')
ADMIN_EMAIL = 'admin@plume-astrale.fr'
ADMIN_PASSWORD = 'PlumeAdmin2026'
TEST_SID = 'e2e-admin-lecture-001'


@pytest.fixture(scope='module')
def admin_token():
    """Login admin via Supabase auth (frontend approach)."""
    # Try direct backend login endpoint first
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD,
    }, timeout=15)
    if r.status_code == 200:
        data = r.json()
        tok = data.get('access_token') or data.get('token') or (data.get('session') or {}).get('access_token')
        if tok:
            return tok

    # Fallback: use Supabase directly
    import os as _os
    sb_url = _os.environ.get('SUPABASE_URL')
    sb_anon = _os.environ.get('SUPABASE_ANON_KEY')
    if not sb_url:
        # Try read backend .env
        try:
            with open('/app/backend/.env') as f:
                for line in f:
                    if line.startswith('SUPABASE_URL='):
                        sb_url = line.split('=', 1)[1].strip().strip('"')
                    if line.startswith('SUPABASE_ANON_KEY='):
                        sb_anon = line.split('=', 1)[1].strip().strip('"')
        except Exception:
            pass
    if not sb_url or not sb_anon:
        pytest.skip('No supabase creds available for admin login')
    r2 = requests.post(
        f"{sb_url}/auth/v1/token?grant_type=password",
        headers={'apikey': sb_anon, 'Content-Type': 'application/json'},
        json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD},
        timeout=15,
    )
    assert r2.status_code == 200, f"admin login fail: {r2.status_code} {r2.text[:200]}"
    return r2.json()['access_token']


@pytest.fixture
def admin_headers(admin_token):
    return {'Authorization': f'Bearer {admin_token}'}


# ---------- 1. admin/orders retourne stats ----------
class TestAdminOrdersStats:
    def test_admin_orders_returns_stats_object(self, admin_headers):
        r = requests.get(f"{BASE_URL}/api/lecture-complete/admin/orders",
                         headers=admin_headers, timeout=20)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        assert 'orders' in data
        assert 'stats' in data, "stats key missing"
        stats = data['stats']
        assert isinstance(stats, dict), "stats must be an object"
        for k in ('total_paid', 'total_refunded', 'refund_rate_pct'):
            assert k in stats, f"{k} missing in stats"
        assert isinstance(stats['refund_rate_pct'], float), \
            f"refund_rate_pct must be float, got {type(stats['refund_rate_pct'])}"
        assert isinstance(stats['total_paid'], int)
        assert isinstance(stats['total_refunded'], int)


# ---------- 2. POST /admin/refund/{sid} ----------
class TestAdminRefund:
    def test_refund_no_auth_401(self):
        r = requests.post(f"{BASE_URL}/api/lecture-complete/admin/refund/{TEST_SID}",
                          json={}, timeout=15)
        assert r.status_code == 401, r.text[:200]

    def test_refund_invalid_token_401(self):
        r = requests.post(f"{BASE_URL}/api/lecture-complete/admin/refund/{TEST_SID}",
                          headers={'Authorization': 'Bearer garbage'},
                          json={}, timeout=15)
        assert r.status_code == 401

    def test_refund_admin_nonexistent_404(self, admin_headers):
        r = requests.post(
            f"{BASE_URL}/api/lecture-complete/admin/refund/does-not-exist-999",
            headers=admin_headers, json={'reason': 'test'}, timeout=15,
        )
        assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text[:200]}"

    def test_refund_admin_existing_200_and_cleanup(self, admin_headers):
        """Full flow: refund → verify persisted → cercle-status returns refunded → cleanup."""
        # 1) Refund
        r = requests.post(
            f"{BASE_URL}/api/lecture-complete/admin/refund/{TEST_SID}",
            headers=admin_headers, json={'reason': 'iter61-test'}, timeout=15,
        )
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        assert d.get('refunded') is True
        assert d.get('session_id') == TEST_SID
        refunded_at = d.get('refunded_at')
        assert refunded_at and re.match(r'^\d{4}-\d{2}-\d{2}T', refunded_at), \
            f"refunded_at not ISO: {refunded_at}"

        # 2) Verify persistence via admin orders
        r2 = requests.get(f"{BASE_URL}/api/lecture-complete/admin/orders",
                          headers=admin_headers, timeout=15)
        assert r2.status_code == 200
        orders = r2.json().get('orders') or []
        matching = [o for o in orders if o['session_id'] == TEST_SID]
        assert matching, f"TEST_SID {TEST_SID} not in orders"
        assert matching[0].get('refunded_at'), "refunded_at not persisted in metadata"

        # 3) Cleanup — clear refunded_at
        try:
            import sys
            sys.path.insert(0, '/app/backend')
            from services.supabase_client import get_admin_client
            sb = get_admin_client()
            rr = sb.table('payment_transactions').select('metadata').eq(
                'session_id', TEST_SID).maybe_single().execute()
            md = rr.data.get('metadata') or {}
            for k in ('refunded_at', 'refund_reason', 'refunded_by'):
                md.pop(k, None)
            sb.table('payment_transactions').update({'metadata': md}).eq(
                'session_id', TEST_SID).execute()
            print('[cleanup] restored metadata for', TEST_SID)
        except Exception as e:
            print(f'[cleanup] WARNING failed to restore: {e}')


# ---------- 3. cercle-status handles refund ----------
class TestCercleStatusRefund:
    def test_cercle_status_after_refund_returns_refunded(self, admin_token, admin_headers):
        """Refund admin's own order, then check cercle-status returns refunded=true."""
        # Get admin's own cercle status first (may be active)
        r0 = requests.get(f"{BASE_URL}/api/lecture-complete/cercle-status",
                          headers=admin_headers, timeout=15)
        assert r0.status_code == 200

        # Refund
        rr = requests.post(f"{BASE_URL}/api/lecture-complete/admin/refund/{TEST_SID}",
                           headers=admin_headers, json={}, timeout=15)
        assert rr.status_code == 200

        try:
            r = requests.get(f"{BASE_URL}/api/lecture-complete/cercle-status",
                             headers=admin_headers, timeout=15)
            assert r.status_code == 200
            data = r.json()
            assert data.get('active') is False, f"expected active=false, got {data}"
            assert data.get('refunded') is True, f"expected refunded=true, got {data}"
            assert data.get('refunded_at'), "refunded_at missing"
        finally:
            # Cleanup
            try:
                import sys
                sys.path.insert(0, '/app/backend')
                from services.supabase_client import get_admin_client
                sb = get_admin_client()
                rr2 = sb.table('payment_transactions').select('metadata').eq(
                    'session_id', TEST_SID).maybe_single().execute()
                md = rr2.data.get('metadata') or {}
                for k in ('refunded_at', 'refund_reason', 'refunded_by'):
                    md.pop(k, None)
                sb.table('payment_transactions').update({'metadata': md}).eq(
                    'session_id', TEST_SID).execute()
            except Exception as e:
                print(f'[cleanup] {e}')


# ---------- 4. Batch fetch structural ----------
class TestBatchFetchStructural:
    def test_admin_orders_uses_in_filter(self):
        with open('/app/backend/routes/lecture_complete.py') as f:
            src = f.read()
        # Check .in_('metadata->>parent_bundle', parent_sids) is present
        assert ".in_('metadata->>parent_bundle'" in src or \
               '.in_("metadata->>parent_bundle"' in src, \
               "batch .in_('metadata->>parent_bundle', ...) missing"

    def test_no_n_plus_one_in_main_path(self):
        """Verify N+1 pattern removed from main path (should be fallback only)."""
        with open('/app/backend/routes/lecture_complete.py') as f:
            src = f.read()
        # Fallback with .like('session_id', f'{sid}--%') can exist inside except
        # but the primary path must use .in_
        idx_in = src.find(".in_('metadata->>parent_bundle'")
        idx_except = src.find('except Exception as e:\n        logger.warning(f\'[lecture_complete/admin] batch children fetch fail')
        assert idx_in > 0
        assert idx_in < idx_except, "batch .in_ must be before fallback except block"


# ---------- 5. J+30 sequence structural ----------
class TestJ30SequenceStructural:
    def test_email_j30_exists(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services import lecture_complete_sequence as seq
        assert hasattr(seq, '_email_j30')
        subject, body = seq._email_j30('TestPrenom')
        assert 'TestPrenom' in subject
        assert '19€/mois pendant 6 mois' in body, \
            f"J+30 email must mention '19€/mois pendant 6 mois', got: {body[:200]}"

    def test_process_transaction_handles_j30(self):
        with open('/app/backend/services/lecture_complete_sequence.py') as f:
            src = f.read()
        assert "stage = 'j30'" in src
        assert "sequence_j30_sent_at" in src
        assert "age_h >= 24 * 30" in src

    def test_run_once_fetches_32d_range(self):
        with open('/app/backend/services/lecture_complete_sequence.py') as f:
            src = f.read()
        assert 'timedelta(days=32)' in src, "must fetch 32d range for J+30 margin"


# ---------- 6. Journal email guests + scheduler ----------
class TestJournalEmailGuests:
    def test_module_exports(self):
        import sys
        sys.path.insert(0, '/app/backend')
        from services import journal_email_service as jes
        assert hasattr(jes, 'get_bundle_guests_for_daily_journal')
        assert hasattr(jes, 'send_daily_journal_batch')
        assert hasattr(jes, 'daily_journal_scheduler_loop')

    def test_batch_returns_expected_keys(self):
        """Structural: send_daily_journal_batch returns {sent, users, guests, ...}"""
        with open('/app/backend/services/journal_email_service.py') as f:
            src = f.read()
        # Check batch function returns all required keys
        assert "'users': " in src
        assert "'guests': " in src
        assert "'sent': " in src

    def test_startup_launches_scheduler(self):
        with open('/app/backend/server.py') as f:
            src = f.read()
        assert 'daily_journal_scheduler_loop' in src
        assert 'create_task(daily_journal_scheduler_loop' in src.replace(' ', '')


# ---------- 7. Backend logs contain scheduler messages ----------
class TestBackendLogs:
    def test_scheduler_started_in_logs(self):
        import glob
        found_start = False
        found_batch = False
        for path in glob.glob('/var/log/supervisor/backend*.log'):
            try:
                with open(path, errors='ignore') as f:
                    src = f.read()
            except Exception:
                continue
            if 'scheduler demarre (verifie toutes les heures)' in src:
                found_start = True
            if 'batch quotidien:' in src:
                found_batch = True
        assert found_start, "backend logs missing 'scheduler demarre'"
        assert found_batch, "backend logs missing 'batch quotidien'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
