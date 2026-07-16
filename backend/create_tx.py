#!/usr/bin/env python3
"""Créer la transaction manquante pour nadine."""

import sys
sys.path.insert(0, '.')

from services.supabase_client import get_admin_client
from datetime import datetime

sb = get_admin_client()

SESSION_ID = "cs_live_a13zgob67tMdN3bL8G2tGGa1vJryePfDK5fiwEZJuJnkDXUVPbZSIiJwIN"

print('\n📝 Creating transaction in database...\n')

# Verify it doesn't exist yet
check = sb.table('payment_transactions').select('*').eq('session_id', SESSION_ID).maybe_single().execute()
if check and check.data:
    print(f'✅ Transaction already exists:')
    print(f'   Status: {check.data.get("status")}')
    print(f'   Email: {check.data.get("user_email")}')
else:
    print(f'Creating NEW transaction for Stripe session: {SESSION_ID}')
    
    # Create transaction (with placeholder birth data - will be updated)
    new_tx = {
        'session_id': SESSION_ID,
        'user_email': 'nadine.zebdi@gmail.com',
        'pack_id': 'fenetre_rencontre_avancee',
        'amount': 29.0,
        'currency': 'eur',
        'credits': 0,
        'status': 'pending',  # Mark as pending - we'll complete once we have real birth data
        'payment_status': 'paid',
        'metadata': {
            'kind': 'fenetre_rencontre_avancee',
            'repaired': True,
            'repaired_at': datetime.utcnow().isoformat(),
            'note': 'Awaiting real birth data from user'
        }
    }
    
    try:
        result = sb.table('payment_transactions').insert(new_tx).execute()
        if result.data:
            print(f'\n✅ Transaction created successfully!')
            print(f'   DB ID: {result.data[0].get("id")}')
            print(f'   Session: {SESSION_ID}')
            print(f'   Email: nadine.zebdi@gmail.com')
            print(f'   Amount: 29.00 EUR')
            print(f'   Status: PENDING (awaiting birth data)')
        else:
            print(f'❌ Failed to insert')
    except Exception as e:
        print(f'Error: {e}')
