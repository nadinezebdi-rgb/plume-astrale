"""Génère le vrai PDF concours avec IA GPT en anglais pour Camille."""
import sys, asyncio, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

from services import astrology_io_service as aio
from services.natal_book_service import generate_enriched_natal_pdf

bd = aio.make_birth_data(
    year=1992, month=4, day=23, hour=9, minute=15,
    latitude=45.7640, longitude=4.8357,
    city='Lyon', country_code='FR',
)

async def main():
    print('\n[GENERATION PDF ANGLAIS CAMILLE — PIPELINE IA RÉEL]\n')
    print('Étapes attendues dans les logs:')
    print('  1. [astrology_io] POST /charts/natal (lang=en)')
    print('  2. [astrology_io] POST /analysis/natal-report (lang=en)')
    print('  3. [natal_ai] Calling GPT for Camille (lang=en)')
    print('  4. [natal_book] Calling GPT for Camille (lang=en)')
    print('  5. [astrology_io] POST /chart/svg (lang=en)')
    print()
    t0 = time.time()
    r = await generate_enriched_natal_pdf(
        name='Camille',
        birth_data=bd,
        no_birth_time=False,
        require_complete=False,
        output='digital',
        birth_date_iso='1992-04-23',
        force_refresh=True,  # Force régénération IA
        language='en',
    )
    pdf = r['pdf_bytes']
    diag = r['diag']
    elapsed = time.time() - t0
    print(f'\n→ PDF: {len(pdf)/1024:.1f} KB · pages={diag.get("pdf_pages")} · {elapsed:.1f}s')
    print(f'→ ai_source={diag.get("ai_source")} · book_source={diag.get("book_source")}')
    print(f'→ ai_planet_count={diag.get("ai_planet_count")} · language={diag.get("language")}')
    OUT = '/app/frontend/public/demos/contest-natal-english.pdf'
    with open(OUT, 'wb') as f:
        f.write(pdf)
    print(f'\n✅ Sauvegardé : {OUT}')

asyncio.run(main())
