# Seed helper: create/confirm two Supabase test users (with & without birth_date) for Ex Libris tests
import os, sys, json, requests
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
URL = os.environ['SUPABASE_URL']
SR = os.environ['SUPABASE_SERVICE_ROLE_KEY']
ANON = os.environ['SUPABASE_ANON_KEY']
H = {'apikey': SR, 'Authorization': f'Bearer {SR}', 'Content-Type': 'application/json'}

USERS = [
    ('test_exlibris_full@plumetest.com', 'TestExLibris#2026', {'prenom': 'Camille', 'birth_date': '1990-06-15', 'birth_time': '14:30', 'birth_place': 'Paris', 'birth_country': 'France', 'latitude': 48.8566, 'longitude': 2.3522}),
    ('test_exlibris_nobd@plumetest.com', 'TestExLibris#2026', {'prenom': 'Nora'}),
]

for email, pwd, prof in USERS:
    r = requests.post(f'{URL}/auth/v1/admin/users', headers=H, json={'email': email, 'password': pwd, 'email_confirm': True})
    print('create', email, r.status_code, r.text[:120])
    t = requests.post(f'{URL}/auth/v1/token?grant_type=password', headers={'apikey': ANON, 'Content-Type': 'application/json'}, json={'email': email, 'password': pwd})
    print('login', t.status_code)
    tok = t.json()['access_token']
    base = open('/app/frontend/.env').read().split('REACT_APP_BACKEND_URL=')[1].split()[0]
    p = requests.put(f'{base}/api/auth/profile', headers={'Authorization': f'Bearer {tok}'}, json=prof)
    print('profile', p.status_code, p.text[:200])
