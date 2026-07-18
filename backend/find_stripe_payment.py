#!/usr/bin/env python3
"""Cherche le paiement 29€ dans Stripe pour nadine.zebdi@gmail.com"""

import sys
sys.path.insert(0, '.')

from config import get_settings
import stripe

settings = get_settings()
stripe.api_key = settings.STRIPE_API_KEY

print('\n🔍 Searching Stripe for 29 EUR payments by nadine.zebdi@gmail.com...\n')

# Chercher checkout sessions avec ~29 EUR
sessions = stripe.checkout.Session.list(limit=100)

found_29eur = []
for session in sessions.data:
    # Chercher si c'est un payment de 29 EUR
    if session.amount_total and session.amount_total >= 2800 and session.amount_total <= 3000:
        # Chercher l'email
        email = session.customer_email or session.customer_details.email if session.customer_details else None
        if email and 'nadine' in email.lower():
            found_29eur.append(session)
            print(f"✅ FOUND: {session.id}")
            print(f"   Email: {email}")
            print(f"   Amount: {session.amount_total / 100} EUR")
            print(f"   Status: {session.payment_status}")
            print(f"   Mode: {session.mode}")
            print(f"   Created: {session.created}")
            print(f"   Metadata: {session.metadata}")
            print()

if not found_29eur:
    print("❌ No 29 EUR payment found for nadine")
    print("\nSearching all recent checkout sessions...\n")
    for i, session in enumerate(sessions.data[:10]):
        email = session.customer_email or (session.customer_details.email if session.customer_details else None)
        amount = session.amount_total / 100 if session.amount_total else 0
        print(f"  {session.id[:30]:30} | {email:30} | {amount:6.2f} EUR | {session.payment_status}")
else:
    print(f"\n✅ Found {len(found_29eur)} payments matching your search")
