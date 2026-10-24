"""Debug enrichissement GPT pour Nadine — comprend pourquoi Soleil/Lune/Vénus sont vides."""
import asyncio, sys, logging
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(message)s')
logger = logging.getLogger('debug_enrich')

async def main():
    from services import astrology_io_service as aio
    from services.natal_ai_enrichment import enrich_natal_ultra
    raw_bd = {'day': 17, 'city': 'SAINT AVOLD', 'hour': 1, 'year': 1968, 'month': 7, 'minute': 40, 'country_code': 'France'}
    bd = aio.normalize_birth_data(raw_bd)
    print(f'=== normalized bd: {bd}')

    # 1. Appel direct astro API
    chart = await aio.natal_chart(bd, name='Nadine', language='fr')
    planets = aio.extract_planets(chart) or {}
    print(f'=== API returned {len(planets)} planets')
    for p, data in planets.items():
        print(f'   {p}: sign={data.get("sign")}, deg={data.get("degree")}')

    # 2. Check interpretations via natal_report
    natal_report = await aio.natal_report(bd, name='Nadine', language='fr')
    interpretations = []
    if isinstance(natal_report, dict):
        interpretations = (
            natal_report.get('interpretations')
            or natal_report.get('data', {}).get('interpretations')
            or []
        )
    print(f'\n=== natal_report keys: {list((natal_report or {}).keys()) if isinstance(natal_report, dict) else "N/A"}')
    print(f'=== Interpretations: {len(interpretations)} items')
    if interpretations:
        print(f'   sample: {str(interpretations[0])[:400]}')

    # 3. Appel enrich_natal_ultra
    print(f'\n=== Appel enrich_natal_ultra ===')
    try:
        enriched = await asyncio.wait_for(
            enrich_natal_ultra(prenom='Nadine', birth_data=bd, api_interpretations=interpretations, language='fr', force_refresh=True),
            timeout=90,
        )
        print(f'enriched source: {enriched.get("_source")}')
        print(f'enriched keys: {sorted(k for k in enriched.keys() if not k.startswith("_"))[:20]}')
        print(f'enriched["soleil"]: {(enriched.get("soleil") or "")[:150]!r}')
        print(f'enriched["lune"]: {(enriched.get("lune") or "")[:150]!r}')
        print(f'enriched["venus"]: {(enriched.get("venus") or "")[:150]!r}')
        print(f'enriched["mercure"]: {(enriched.get("mercure") or "")[:150]!r}')
        print(f'_signs_by_planet: {enriched.get("_signs_by_planet")}')
        print(f'_raw_v3_by_planet keys: {list((enriched.get("_raw_v3_by_planet") or {}).keys())}')
    except asyncio.TimeoutError:
        print(f'TIMEOUT après 90s')
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {str(e)[:400]}')

asyncio.run(main())
