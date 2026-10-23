# Helper: obtain a real Supabase session for an admin via service-role generate_link + verify_otp (test-only)
import os, json, sys, requests
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
URL = os.environ['SUPABASE_URL']; SR = os.environ['SUPABASE_SERVICE_ROLE_KEY']; ANON = os.environ['SUPABASE_ANON_KEY']
email = sys.argv[1] if len(sys.argv) > 1 else 'nadine.zebdi@gmail.com'
r = requests.post(f'{URL}/auth/v1/admin/generate_link', headers={'apikey': SR, 'Authorization': f'Bearer {SR}'},
                  json={'type': 'magiclink', 'email': email})
r.raise_for_status()
d = r.json()
otp = d.get('hashed_token') or d.get('properties', {}).get('hashed_token')
v = requests.post(f'{URL}/auth/v1/verify', headers={'apikey': ANON}, json={'type': 'magiclink', 'token_hash': otp})
v.raise_for_status()
s = v.json()
json.dump(s, open('/tmp/admin_session.json', 'w'))
print('OK', s['user']['id'], s['access_token'][:20])
