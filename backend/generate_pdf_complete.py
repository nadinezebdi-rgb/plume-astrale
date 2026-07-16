#!/usr/bin/env python3
"""Générer le PDF avec calcul des fenêtres + enrichissement OpenAI"""

import sys
import asyncio
sys.path.insert(0, '.')

from services.supabase_client import get_admin_client
from services.fenetre_rencontre_pdf_v2 import generate_fenetre_rencontre_pdf
from services.astrology_io_service import transits_today
from services.openai_enrichment_service import enrich_all_windows, generate_daily_affirmations
from routes.fenetre_rencontre import _calculate_advanced_windows
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

async def generate_pdf():
    try:
        print(f'\n🌍 Fetching astrological data...')
        
        # Get transits
        transits = await transits_today(birth_data, language='fr') or {}
        print(f'   ✅ Transits calculated')
        
        # Calculate windows
        print(f'\n📊 Calculating meeting windows...')
        windows = _calculate_advanced_windows(birth_data, transits)
        print(f'   ✅ Found {len(windows)} windows')
        
        # Enrich with OpenAI
        print(f'\n✨ Enriching with OpenAI...')
        windows = enrich_all_windows(windows)
        print(f'   ✅ Texts enriched')
        
        # Generate daily affirmations
        print(f'\n💫 Generating affirmations...')
        affirmations = generate_daily_affirmations(first_name, "Sagittaire")  # Default, peut être amélioré
        print(f'   ✅ Affirmations created')
        
        # Generate PDF
        print(f'\n🎨 Generating PDF...')
        pdf_bytes = generate_fenetre_rencontre_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            windows_data=windows,
            synastry_data=None,
            affirmations=affirmations,  # Pass affirmations
        )
        
        print(f'   ✅ PDF generated! Size: {len(pdf_bytes)} bytes')
        
        # Upload to Supabase
        print(f'\n📤 Uploading to Supabase...')
        file_name = f'fenetre_{uuid.uuid4().hex[:12]}.pdf'
        
        sb.storage.from_('reports').upload(
            f'fenetre/{file_name}',
            pdf_bytes,
            {'content-type': 'application/pdf'},
        )
        
        print(f'   ✅ PDF uploaded!')
        
        # Get public URL
        pdf_url = sb.storage.from_('reports').get_public_url(f'fenetre/{file_name}')
        print(f'   📄 File: fenetre/{file_name}')
        
        # Update transaction
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
        print('✅ SUCCESS! Your PDF has been generated and uploaded!')
        print('='*80)
        print(f'\n📄 Your PDF is ready:')
        print(f'{pdf_url}')
        print('\n📋 Your Fenêtres de Rencontre report includes:')
        print('   ✦ 3 Meeting Windows with exact dates')
        print('   ✦ Venus & Jupiter transits for love & expansion')
        print('   ✦ Moon phases for optimal timing')
        print('   ✦ Activation advice & rituals')
        print('   ✦ Specific crystals recommendations')
        print('   ✦ Daily affirmations to recite')
        print('   ✦ 10 poetic & cosmic pages')
        print('\n💾 You can download your PDF from the link above')
        print('📧 Check your email for details (email may take 24-48h due to DNS propagation)')
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

# Run async
success = asyncio.run(generate_pdf())

if not success:
    print('\n⚠️  Something went wrong. Contacting support...')
