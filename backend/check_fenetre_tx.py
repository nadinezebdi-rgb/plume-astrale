#!/usr/bin/env python3
"""Check for fenetre_rencontre transactions in Supabase."""

import sys
sys.path.insert(0, '.')

from services.supabase_client import get_admin_client

sb = get_admin_client()

# Get recent transactions
txs = sb.table('payment_transactions').select('*').order('created_at', desc=True).limit(50).execute()

print(f'\nFound {len(txs.data)} recent transactions\n')
print('=' * 120)

fenetre_txs = [tx for tx in txs.data if tx.get('pack_id') == 'fenetre_rencontre_avancee']

if fenetre_txs:
    print(f'\n✅ FOUND {len(fenetre_txs)} FENETRE_RENCONTRE TRANSACTIONS!\n')
    for tx in fenetre_txs:
        print(f"ID: {tx['id']}")
        print(f"Session: {tx.get('session_id')}")
        print(f"Email: {tx.get('user_email')}")
        print(f"Amount: {tx.get('amount')} {tx.get('currency')}")
        print(f"Status: {tx.get('status')} / Payment: {tx.get('payment_status')}")
        print(f"Created: {tx.get('created_at')}")
        metadata = tx.get('metadata', {})
        print(f"Has PDF context: {'pdf_ctx' in metadata}")
        print('-' * 120)
else:
    print('\n❌ NO FENETRE_RENCONTRE TRANSACTIONS FOUND\n')
    print('Recent transactions by product:')
    for tx in txs.data[:15]:
        print(f"  {tx.get('pack_id', 'N/A'):30} | {tx.get('user_email', 'N/A'):25} | {tx.get('status', '?'):8} | {tx.get('amount', 0)}")
