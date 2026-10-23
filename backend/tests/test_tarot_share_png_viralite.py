# Iteration 95: PNG shareable tarot card + Admin "Viralité Tarot" endpoint
import os, json, re, io
import pytest, requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    for line in open('/app/frontend/.env'):
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.split('=', 1)[1].strip().rstrip('/')

SHARE_ID = '6b4205ccbd85'


def _admin_token():
    p = '/tmp/admin_session.json'
    if not os.path.exists(p):
        pytest.skip('no admin session (run _admin_token_helper.py)')
    return json.load(open(p))['access_token']


# --- PNG card endpoint ---
class TestSharedCardPng:
    def test_png_ok(self):
        r = requests.get(f'{BASE_URL}/api/tarot/shared/{SHARE_ID}/card.png', timeout=60)
        assert r.status_code == 200
        assert r.headers['content-type'].startswith('image/png')
        assert len(r.content) > 20_000
        assert r.content[:8] == b'\x89PNG\r\n\x1a\n'
        cd = r.headers.get('content-disposition', '')
        assert 'tirage-' in cd
        open('/tmp/card_sample.png', 'wb').write(r.content)
        from PIL import Image
        assert Image.open(io.BytesIO(r.content)).size == (1080, 1350)

    def test_png_uppercase_id_normalized(self):
        r = requests.get(f'{BASE_URL}/api/tarot/shared/{SHARE_ID.upper()}/card.png', timeout=60)
        assert r.status_code == 200

    def test_png_bad_id(self):
        r = requests.get(f'{BASE_URL}/api/tarot/shared/badID12345x/card.png', timeout=30)
        assert r.status_code == 400

    def test_png_not_found(self):
        r = requests.get(f'{BASE_URL}/api/tarot/shared/0000000000ff/card.png', timeout=30)
        assert r.status_code == 404


# --- Admin viralité endpoint ---
class TestAdminTarotShareTop:
    def test_no_auth(self):
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top', timeout=30)
        assert r.status_code in (401, 403)

    def test_garbage_token(self):
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top', headers={'Authorization': 'Bearer abc'}, timeout=30)
        assert r.status_code == 401

    def test_admin_ok(self):
        tok = _admin_token()
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top?limit=50',
                         headers={'Authorization': f'Bearer {tok}'}, timeout=30)
        assert r.status_code == 200, r.text
        d = r.json()
        assert 'error' not in d, d
        assert isinstance(d['total_shares'], int) and d['total_shares'] >= 1
        assert isinstance(d['total_views'], int)
        assert isinstance(d['avg_views_per_share'], (int, float))
        items = d['items']
        assert len(items) >= 1 and len(items) <= 50
        vc = [i.get('view_count') or 0 for i in items]
        assert vc == sorted(vc, reverse=True)
        for it in items:
            assert re.fullmatch(r'[0-9a-f]{12}', it['share_id'])
            assert '_id' not in it
            for k in ('type', 'question', 'first_name', 'view_count', 'created_at'):
                assert k in it, (k, it)

    def test_limit_validation(self):
        tok = _admin_token()
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top?limit=0',
                         headers={'Authorization': f'Bearer {tok}'}, timeout=30)
        assert r.status_code == 422
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top?limit=1',
                         headers={'Authorization': f'Bearer {tok}'}, timeout=30)
        assert r.status_code == 200 and len(r.json()['items']) == 1

    def test_non_admin_forbidden(self):
        sb = os.environ.get('REACT_APP_SUPABASE_URL')
        anon = None
        for line in open('/app/frontend/.env'):
            if line.startswith('REACT_APP_SUPABASE_URL='):
                sb = line.split('=', 1)[1].strip()
            if line.startswith('REACT_APP_SUPABASE_ANON_KEY='):
                anon = line.split('=', 1)[1].strip()
        lr = requests.post(f'{sb}/auth/v1/token?grant_type=password', headers={'apikey': anon},
                           json={'email': 'concours@plume-astrale.fr', 'password': 'ConcoursPlume2026!'}, timeout=30)
        if lr.status_code != 200:
            pytest.skip('demo login failed')
        tok = lr.json()['access_token']
        r = requests.get(f'{BASE_URL}/api/admin/tarot-share/top', headers={'Authorization': f'Bearer {tok}'}, timeout=30)
        assert r.status_code == 403
