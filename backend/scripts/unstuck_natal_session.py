"""Débloque une session PDF Theme Natal stuck en pending → relance la génération."""
import asyncio, sys, os
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

SESSION_ID = 'admin-natal-45998476e0a2425c'

async def main():
    from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
    print(f'[unstuck] Relance {SESSION_ID}...')
    diag = await handle_theme_natal_oneshot_webhook(SESSION_ID, force=True)
    print(f'[unstuck] DONE diag={diag}')

asyncio.run(main())
