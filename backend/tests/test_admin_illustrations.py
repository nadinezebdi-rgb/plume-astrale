# Iteration 96: Admin "Illustrations IA" endpoints, admin_viralite extraction, two-tier illustration cache
import os
import sys
import json
import asyncio
import hashlib
import pytest
import requests

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')


def _base_url():
    for line in open('/app/frontend/.env'):
        if line.startswith('REACT_APP_BACKEND_URL='):
            return line.split('=', 1)[1].strip().rstrip('/')
    raise RuntimeError('REACT_APP_BACKEND_URL missing')


BASE_URL = _base_url()
SEED_HASH = '0bb28a346271411e6ebd6608'
UNKNOWN_HASH = 'ffffffffffffffffffffffff'


def _admin_headers():
    p = '/tmp/admin_session.json'
    if not os.path.exists(p):
        pytest.skip('no admin session (run tests/_admin_token_helper.py)')
    return {'Authorization': f"Bearer {json.load(open(p))['access_token']}"}


def _non_admin_token():
    sb = anon = None
    for line in open('/app/frontend/.env'):
        if line.startswith('REACT_APP_SUPABASE_URL='):
            sb = line.split('=', 1)[1].strip()
        if line.startswith('REACT_APP_SUPABASE_ANON_KEY='):
            anon = line.split('=', 1)[1].strip()
    r = requests.post(f'{sb}/auth/v1/token?grant_type=password', headers={'apikey': anon},
                      json={'email': 'concours@plume-astrale.fr', 'password': 'ConcoursPlume2026!'}, timeout=30)
    if r.status_code != 200:
        pytest.skip('demo login failed')
    return r.json()['access_token']


def _mongo_doc(h):
    from motor.motor_asyncio import AsyncIOMotorClient

    async def _f():
        db = AsyncIOMotorClient(os.environ['MONGO_URL'])[os.environ['DB_NAME']]
        return await db.natal_illustrations_log.find_one({'signature_hash': h}, {'_id': 0})
    return asyncio.run(_f())


# --- Auth guards ---
class TestAuthGuards:
    @pytest.mark.parametrize('method,path', [
        ('get', '/api/admin/natal-illustrations'),
        ('get', f'/api/admin/natal-illustrations/{SEED_HASH}/image'),
        ('post', f'/api/admin/natal-illustrations/{SEED_HASH}/regenerate'),
        ('get', '/api/admin/tarot-share/top'),
    ])
    def test_no_token_401(self, method, path):
        r = getattr(requests, method)(f'{BASE_URL}{path}', timeout=30)
        assert r.status_code in (401, 403), r.text

    def test_non_admin_403(self):
        tok = _non_admin_token()
        h = {'Authorization': f'Bearer {tok}'}
        for method, path in [('get', '/api/admin/natal-illustrations'),
                             ('get', f'/api/admin/natal-illustrations/{SEED_HASH}/image'),
                             ('post', f'/api/admin/natal-illustrations/{SEED_HASH}/regenerate')]:
            r = getattr(requests, method)(f'{BASE_URL}{path}', headers=h, timeout=30)
            assert r.status_code == 403, (path, r.status_code, r.text)


# --- List endpoint ---
class TestList:
    def test_list_shape(self):
        r = requests.get(f'{BASE_URL}/api/admin/natal-illustrations', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert set(['items', 'total', 'skip', 'limit']) <= set(d)
        assert d['skip'] == 0 and d['limit'] == 50
        assert d['total'] >= 1
        row = next((i for i in d['items'] if i['signature_hash'] == SEED_HASH), None)
        assert row, 'seeded Alix row missing'
        for k in ['signature_hash', 'user_id', 'prenom', 'sun_sign', 'moon_sign', 'asc_sign',
                  'storage_path', 'size_bytes', 'generation_count', 'last_generated_at',
                  'first_generated_at', 'kind']:
            assert k in row, k
        assert row['kind'] == 'ex_libris'
        assert row['prenom'] == 'Alix' and row['sun_sign'] == 'Taureau'
        assert row['moon_sign'] == 'Vierge' and row['asc_sign'] == 'Capricorne'
        assert '_id' not in row

    def test_list_pagination_validation(self):
        h = _admin_headers()
        r = requests.get(f'{BASE_URL}/api/admin/natal-illustrations?limit=1&skip=0', headers=h, timeout=30)
        assert r.status_code == 200 and len(r.json()['items']) <= 1 and r.json()['limit'] == 1
        assert requests.get(f'{BASE_URL}/api/admin/natal-illustrations?limit=0', headers=h, timeout=30).status_code == 422
        assert requests.get(f'{BASE_URL}/api/admin/natal-illustrations?limit=500', headers=h, timeout=30).status_code == 422
        assert requests.get(f'{BASE_URL}/api/admin/natal-illustrations?skip=-1', headers=h, timeout=30).status_code == 422


# --- Image endpoint ---
class TestImage:
    def test_image_seed(self):
        r = requests.get(f'{BASE_URL}/api/admin/natal-illustrations/{SEED_HASH}/image', headers=_admin_headers(), timeout=60)
        assert r.status_code == 200, r.text
        assert r.headers['content-type'].startswith('image/jpeg')
        assert r.content[:3] == b'\xff\xd8\xff', 'not JPEG magic bytes'
        assert len(r.content) > 5000

    def test_image_unknown_404(self):
        r = requests.get(f'{BASE_URL}/api/admin/natal-illustrations/{UNKNOWN_HASH}/image', headers=_admin_headers(), timeout=60)
        assert r.status_code == 404


# --- Regenerate endpoint ---
class TestRegenerate:
    def test_regenerate_unknown_404(self):
        r = requests.post(f'{BASE_URL}/api/admin/natal-illustrations/{UNKNOWN_HASH}/regenerate', headers=_admin_headers(), timeout=60)
        assert r.status_code == 404

    def test_regenerate_seed_changes_content(self):
        h = _admin_headers()
        before_doc = _mongo_doc(SEED_HASH)
        before_img = requests.get(f'{BASE_URL}/api/admin/natal-illustrations/{SEED_HASH}/image', headers=h, timeout=60).content
        r = requests.post(f'{BASE_URL}/api/admin/natal-illustrations/{SEED_HASH}/regenerate', headers=h, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d['ok'] is True and d['signature_hash'] == SEED_HASH
        assert isinstance(d['size_bytes'], int) and d['size_bytes'] > 5000
        after_doc = _mongo_doc(SEED_HASH)
        assert after_doc['generation_count'] == before_doc['generation_count'] + 1
        assert after_doc['last_generated_at'] > before_doc['last_generated_at']
        assert after_doc['first_generated_at'] == before_doc['first_generated_at']
        assert after_doc['size_bytes'] == d['size_bytes']
        after_img = requests.get(f'{BASE_URL}/api/admin/natal-illustrations/{SEED_HASH}/image', headers=h, timeout=60).content
        assert len(after_img) == d['size_bytes']
        assert hashlib.md5(after_img).hexdigest() != hashlib.md5(before_img).hexdigest()


# --- admin_viralite extraction (regression) ---
class TestViralite:
    def test_top_shape(self):
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top?limit=5', headers=_admin_headers(), timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        for k in ['items', 'total_shares', 'total_views', 'avg_views_per_share']:
            assert k in d
        assert len(d['items']) <= 5
        views = [i.get('view_count') or 0 for i in d['items']]
        assert views == sorted(views, reverse=True)


# --- Two-tier cache (pure python) ---
class TestTwoTierCache:
    def test_soleil_from_storage_and_backfill(self, monkeypatch):
        from services import natal_book_illustrations as nbi
        calls = []

        async def _no_gen(prompt, session_id):
            calls.append(session_id)
            return None
        monkeypatch.setattr(nbi, '_generate_image_bytes', _no_gen)
        local = nbi.PLANET_CACHE / 'soleil.png'
        backup = local.read_bytes() if local.exists() else None
        try:
            local.unlink(missing_ok=True)
            assert not local.exists()
            data = asyncio.run(nbi.get_or_generate_planet_illustration('Soleil'))
            assert data and len(data) > 5000
            assert data[:3] == b'\xff\xd8\xff'
            assert calls == [], 'Nano Banana was called despite remote storage hit'
            assert local.exists() and local.read_bytes() == data, 'local cache not backfilled'
        finally:
            if not local.exists() and backup:
                local.write_bytes(backup)
