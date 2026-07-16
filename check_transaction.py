"""Script pour vérifier et reparer la transaction de paiement."""
import os
import sys
from datetime import datetime, timedelta

# Add backend to path
backend_path = 'c:\\Users\\neofo\\AppData\\Local\\Temp\\plume-astrale\\backend'
sys.path.insert(0, backend_path)

from services.supabase_client import get_admin_client
from routes.fenetre_rencontre import _generate_and_email_pdf
import asyncio

async def check_and_repair():
    sb = get_admin_client()
    
    # 1. Chercher les transactions 'fenetre_rencontre_avancee' des 24 dernières heures
    print("🔍 Searching for recent fenetre_rencontre transactions...")
    txs = sb.table('payment_transactions').select('*').eq('pack_id', 'fenetre_rencontre_avancee').order('created_at', desc=True).limit(10).execute()
    
    print(f"Found {len(txs.data)} recent fenetre_rencontre transactions:\n")
    for tx in txs.data:
        print(f"  ID: {tx['id']}")
        print(f"  Session: {tx.get('session_id', 'N/A')}")
        print(f"  Email: {tx.get('user_email', 'N/A')}")
        print(f"  Status: {tx.get('status')} / {tx.get('payment_status')}")
        print(f"  Amount: {tx.get('amount')} {tx.get('currency')}")
        print(f"  Metadata: {tx.get('metadata', {})}")
        print(f"  Created: {tx.get('created_at')}")
        print()
    
    # 2. Si rien trouvé, chercher toutes les transactions récentes
    if not txs.data:
        print("❌ No fenetre_rencontre found! Searching ALL recent transactions...")
        all_txs = sb.table('payment_transactions').select('*').order('created_at', desc=True).limit(20).execute()
        
        for tx in all_txs.data[:5]:
            print(f"  {tx.get('pack_id')} - {tx.get('user_email')} - {tx.get('status')}")
    
    # 3. Para cada transaction pending, tentar gerar PDF
    for tx in txs.data:
        if tx.get('status') == 'pending' and tx.get('payment_status') == 'paid':
            print(f"\n⚠️  Found PAID transaction with PENDING status!")
            print(f"   Session: {tx['session_id']}")
            print(f"   Email: {tx['user_email']}")
            print(f"\n🔧 Triggering PDF generation...")
            
            try:
                pdf_ctx = tx.get('metadata', {}).get('pdf_ctx', {})
                if pdf_ctx:
                    await _generate_and_email_pdf(tx['user_email'], pdf_ctx)
                    print(f"✅ PDF generation triggered!")
                else:
                    print(f"⚠️  No pdf_ctx in metadata!")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    asyncio.run(check_and_repair())
