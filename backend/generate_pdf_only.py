#!/usr/bin/env python3
"""Générer le PDF sans email pour l'instant"""

import sys
sys.path.insert(0, '.')

from services.supabase_client import get_admin_client
from services.fenetre_rencontre_pdf import generate_fenetre_rencontre_pdf
from datetime import datetime
import uuid

sb = get_admin_client()

SESSION_ID = "cs_live_a13zgob67tMdN3bL8G2tGGa1vJryePfDK5fiwEZJuJnkDXUVPbZSIiJwIN"

print('\n' + '='*80)
print('🔧 GENERATING YOUR FENETRE DE RENCONTRE PDF')
print('='*80)

# Données de Nadine
first_name = "Nadine"
birth_date_iso = "1968-07-17"
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

print(f'\n📋 Birth Information:')
print(f'   Name: {first_name}')
print(f'   Date: {birth_date_iso}')
print(f'   Time: 01:40')
print(f'   Location: {birth_city}, {birth_country}')

try:
    print(f'\n🎨 Generating PDF...')
    
    # Générer le PDF
    pdf_bytes = generate_fenetre_rencontre_pdf(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        windows_data=None,  # Will be calculated
        synastry_data=None,
    )
    
    print(f'   ✅ PDF generated! Size: {len(pdf_bytes)} bytes')
    
    # Uploader à Supabase
    print(f'\n📤 Uploading to Supabase...')
    file_name = f'fenetre_{uuid.uuid4().hex[:12]}.pdf'
    
    sb.storage.from_('reports').upload(
        f'fenetre/{file_name}',
        pdf_bytes,
        {'content-type': 'application/pdf'},
    )
    
    print(f'   ✅ PDF uploaded!')
    
    # Récupérer URL
    pdf_url = sb.storage.from_('reports').get_public_url(f'fenetre/{file_name}')
    print(f'   📄 Download URL: {pdf_url}')
    
    # Mettre à jour transaction
    print(f'\n📝 Updating transaction...')
    
    update_result = sb.table('payment_transactions').update({
        'status': 'completed',
        'payment_status': 'paid',
        'metadata': {
            'pdf_ctx': {
                'first_name': first_name,
                'birth_date_iso': birth_date_iso,
                'birth_data': birth_data,
            },
            'pdf_path': pdf_url,
            'kind': 'fenetre_rencontre_avancee',
            'generated_at': datetime.utcnow().isoformat(),
        }
    }).eq('session_id', SESSION_ID).execute()
    
    if update_result and update_result.data:
        print(f'   ✅ Transaction updated!')
    
    print('\n' + '='*80)
    print('✅ SUCCESS! Your PDF has been generated!')
    print('='*80)
    print(f'\n📄 Your PDF: {pdf_url}')
    print('\n📋 Your report includes:')
    print('   • 3 Meeting Windows (exact dates)')
    print('   • Venus & Jupiter transits for love & expansion')
    print('   • Moon phases for optimal timing')
    print('   • Activation advice')
    print('   • Specific rituals & crystals')
    print('   • Affirmations to recite daily')
    print('   • 10 poetic & cosmic pages')
    print('\n💾 You can download it anytime from that URL above.')
    
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
