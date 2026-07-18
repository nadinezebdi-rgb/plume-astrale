#!/usr/bin/env python3
"""Mettre à jour la transaction avec vraies données + générer PDF"""

import sys
import asyncio
from datetime import datetime

sys.path.insert(0, '.')

from services.supabase_client import get_admin_client
from routes.fenetre_rencontre import _generate_and_email_pdf

sb = get_admin_client()

SESSION_ID = "cs_live_a13zgob67tMdN3bL8G2tGGa1vJryePfDK5fiwEZJuJnkDXUVPbZSIiJwIN"

print('\n' + '='*80)
print('🔧 GENERATING YOUR FENETRE DE RENCONTRE PDF')
print('='*80)

# Données de Nadine
first_name = "Nadine"
birth_date_iso = "1968-07-17"
birth_time = "01:40"
birth_city = "Saint-Avold"
birth_country = "FR"

# Construire birth_data pour API astrologie
birth_data = {
    'year': 1968,
    'month': 7,
    'day': 17,
    'hour': 1,
    'minute': 40,
    'city': birth_city,
    'country_code': birth_country,
}

# Préparer pdf_ctx
pdf_ctx = {
    'first_name': first_name,
    'birth_date_iso': birth_date_iso,
    'birth_data': birth_data,
}

print(f'\n📋 Birth Information:')
print(f'   Name: {first_name}')
print(f'   Date: {birth_date_iso}')
print(f'   Time: {birth_time}')
print(f'   Location: {birth_city}, {birth_country}')

# Mettre à jour transaction
print(f'\n📝 Updating transaction in database...')
update_result = sb.table('payment_transactions').update({
    'status': 'completed',
    'metadata': {
        'pdf_ctx': pdf_ctx,
        'kind': 'fenetre_rencontre_avancee',
        'repaired': True,
        'repaired_at': datetime.utcnow().isoformat(),
        'birth_info': f'{birth_date_iso} {birth_time} {birth_city}, {birth_country}'
    }
}).eq('session_id', SESSION_ID).execute()

if update_result and update_result.data:
    print(f'   ✅ Transaction updated!')
else:
    print(f'   ⚠️  Update result: {update_result}')

# Générer PDF
print(f'\n🎨 Generating PDF...')

async def generate_and_send():
    try:
        await _generate_and_email_pdf('nadine.zebdi@gmail.com', pdf_ctx)
        print(f'   ✅ PDF generated and email sent!')
        print(f'   📧 Email sent to: nadine.zebdi@gmail.com')
        return True
    except Exception as e:
        print(f'   ❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(generate_and_send())

print('\n' + '='*80)
if success:
    print('✅ SUCCESS! Your Fenêtres de Rencontre PDF has been generated!')
    print('='*80)
    print('\n📧 Check your email: nadine.zebdi@gmail.com')
    print('\n📋 Your report includes:')
    print('   • 3 Meeting Windows (exact dates)')
    print('   • Venus & Jupiter transits for love & expansion')
    print('   • Moon phases for optimal timing')
    print('   • Activation advice')
    print('   • Specific rituals & crystals')
    print('   • Affirmations to recite daily')
    print('   • 10 poetic & cosmic pages')
else:
    print('⚠️  There was an issue generating the PDF')
    print('='*80)
    print('\nPlease contact support@plume-astrale.fr for assistance')
