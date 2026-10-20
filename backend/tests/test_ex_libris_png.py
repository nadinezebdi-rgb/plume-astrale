# Ex Libris PNG endpoint tests (POST /api/astrology/v3/natal/ex-libris/png)
import os, time, pytest, requests
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')
EP = f'{BASE_URL}/api/astrology/v3/natal/ex-libris/png'
SB_URL = os.environ['SUPABASE_URL']
ANON = os.environ['SUPABASE_ANON_KEY']
PWD = 'TestExLibris#2026'


def _token(email):
    r = requests.post(f'{SB_URL}/auth/v1/token?grant_type=password',
                      headers={'apikey': ANON, 'Content-Type': 'application/json'},
                      json={'email': email, 'password': PWD})
    if r.status_code != 200:
        pytest.skip(f'login failed {email}: {r.text[:100]}')
    return r.json()['access_token']


@pytest.fixture(scope='module')
def full_token():
    return _token('test_exlibris_full@plumetest.com')


@pytest.fixture(scope='module')
def nobd_token():
    return _token('test_exlibris_nobd@plumetest.com')


# Auth
def test_no_token_401():
    r = requests.post(EP, json={})
    assert r.status_code == 401


def test_invalid_token_401():
    r = requests.post(EP, json={}, headers={'Authorization': 'Bearer abc.def.ghi'})
    assert r.status_code == 401


def test_get_method_not_allowed():
    r = requests.get(EP)
    assert r.status_code in (401, 405)


# Incomplete natal data
def test_no_birth_date_400(nobd_token):
    r = requests.post(EP, json={}, headers={'Authorization': f'Bearer {nobd_token}'})
    assert r.status_code == 400, r.text
    assert 'naissance' in r.json().get('detail', '')


# Happy path + caching
def test_png_generation_and_cache(full_token):
    h = {'Authorization': f'Bearer {full_token}'}
    t0 = time.time()
    r = requests.post(EP, json={}, headers=h, timeout=180)
    t1 = time.time() - t0
    print(f'first call {t1:.1f}s')
    assert r.status_code == 200, r.text[:300]
    assert r.headers['content-type'].startswith('image/png')
    assert r.content[:4] == b'\x89PNG'
    assert len(r.content) > 50 * 1024, len(r.content)
    assert 'ex-libris-Camille.png' in r.headers.get('content-disposition', '')
    with open('/tmp/ex_libris_test.png', 'wb') as f:
        f.write(r.content)
    t0 = time.time()
    r2 = requests.post(EP, json={}, headers=h, timeout=180)
    t2 = time.time() - t0
    print(f'second call {t2:.1f}s')
    assert r2.status_code == 200
    assert r2.content[:4] == b'\x89PNG'


# Iteration 91 — cold-cache fast path (enrich_ex_libris_only) via explicit person payload
import random, glob
CACHE_DIR = '/app/backend/cache/natal_ex_libris'


def test_cold_cache_under_45s_and_short_cache_created(full_token):
    h = {'Authorization': f'Bearer {full_token}'}
    before = set(glob.glob(f'{CACHE_DIR}/*.txt'))
    person = {'name': 'TESTCold', 'year': random.randint(1950, 2005), 'month': random.randint(1, 12),
              'day': random.randint(1, 28), 'hour': random.randint(0, 23), 'minute': random.randint(0, 59),
              'latitude': 45.764, 'longitude': 4.8357, 'city': 'Lyon', 'country_code': 'FR'}
    t0 = time.time()
    r = requests.post(EP, json={'person': person}, headers=h, timeout=120)
    dt = time.time() - t0
    print(f'cold call {dt:.1f}s status {r.status_code}')
    assert r.status_code == 200, r.text[:300]
    assert dt < 45, f'cold call too slow: {dt:.1f}s'
    assert r.content[:4] == b'\x89PNG'
    assert len(r.content) > 50 * 1024
    assert 'ex-libris-TESTCold.png' in r.headers.get('content-disposition', '')
    with open('/tmp/ex_libris_cold.png', 'wb') as f:
        f.write(r.content)
    after = set(glob.glob(f'{CACHE_DIR}/*.txt'))
    new = after - before
    assert len(new) == 1, f'expected 1 new short cache file, got {new}'
    txt = open(new.pop(), encoding='utf-8').read().strip()
    print('words', len(txt.split()), repr(txt[-80:]))
    assert len(txt.split()) >= 60
    # warm call
    t0 = time.time()
    r2 = requests.post(EP, json={'person': person}, headers=h, timeout=60)
    print(f'warm call {time.time()-t0:.1f}s')
    assert r2.status_code == 200 and time.time() - t0 < 15
