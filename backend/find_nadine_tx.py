#!/usr/bin/env python3
"""Cherche et répare la transaction 29€ de nadine.zebdi@gmail.com"""

import sys
import asyncio
sys.path.insert(0, '.')

from services.supabase_client import get_admin_client
from routes.fenetre_rencontre import _generate_and_email_pdf

sb = get_admin_client()

# Chercher TOUTES les transactions de nadine.zebdi@gmail.com
print('\n🔍 Searching for ALL nadine.zebdi@gmail.com transactions...\n')
txs = sb.table('payment_transactions').select('*').eq('user_email', 'nadine.zebdi@gmail.com').order('created_at', desc=True).execute()

print(f'Found {len(txs.data)} transactions for nadine.zebdi@gmail.com:\n')
print('=' * 140)

for i, tx in enumerate(txs.data):
    print(f"\n[{i+1}] {tx.get('pack_id', 'N/A')}")
    print(f"    Session: {tx.get('session_id')}")
    print(f"    Amount: {tx.get('amount')} {tx.get('currency')}")
    print(f"    Status: {tx.get('status')} / Payment: {tx.get('payment_status')}")
    print(f"    Created: {tx.get('created_at')}")
    
    metadata = tx.get('metadata') or {}
    has_pdf_ctx = 'pdf_ctx' in metadata
    print(f"    Has PDF context: {has_pdf_ctx}")
    
    if tx.get('pack_id') == 'fenetre_rencontre_avancee':
        print(f"    ✅ THIS IS YOUR 29€ FENETRE PAYMENT!")
        if tx.get('payment_status') == 'paid' or tx.get('status') == 'completed':
            print(f"    ✅ Payment is confirmed as PAID")
            if has_pdf_ctx:
                print(f"    ✅ PDF context exists - can generate!")
            else:
                print(f"    ⚠️  No PDF context - need to check metadata")
        else:
            print(f"    ⚠️  Payment status is not confirmed: {tx.get('payment_status')}")

print('\n' + '=' * 140)
