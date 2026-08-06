"""Capture 9:16 portrait screenshots of plume-astrale.fr for TikTok demo.

Flow:
1. Landing page (public, portrait cropped)
2. Créer un compte (signup form)
3. Login as test user
4. Mon Accueil (personalized dashboard)
5. Chat with Soléna
6. Horoscope du jour
7. Tools accessible after login (numérologie, tarot, etc.)
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/app/backend/cache/plume_shots')
OUT.mkdir(parents=True, exist_ok=True)

BASE = 'https://consultation-astro.preview.emergentagent.com'
EMAIL = 'test@plume-astrale.fr'
PWD = 'TestPlume2026!'


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={'width': 720, 'height': 1280},
            device_scale_factor=2,  # retina for sharpness
            locale='fr-FR',
        )
        page = await ctx.new_page()

        # 1. Landing top
        await page.goto(f'{BASE}/', wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_timeout(4000)
        # dismiss cookie banner if present
        try:
            await page.click('button:has-text("Accepter")', timeout=3000)
            await page.wait_for_timeout(600)
        except Exception:
            pass
        await page.screenshot(path=str(OUT / '01_landing_hero.png'), full_page=False)
        print('01 landing hero')

        # 2. Landing scrolled — 5 lectures section
        await page.evaluate('window.scrollBy(0, 1400)')
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / '02_landing_offer.png'), full_page=False)
        print('02 landing offer')

        # 3. Scroll to testimonials
        await page.evaluate('window.scrollBy(0, 2600)')
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT / '03_landing_testimonials.png'), full_page=False)
        print('03 testimonials')

        # 4. Créer un compte
        await page.goto(f'{BASE}/inscription', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(2500)
        await page.screenshot(path=str(OUT / '04_signup_form.png'), full_page=False)
        print('04 signup')

        # 5. Connexion login
        await page.goto(f'{BASE}/connexion', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(2000)
        # fill login form
        try:
            await page.fill('input[type="email"]', EMAIL)
            await page.fill('input[type="password"]', PWD)
            await page.screenshot(path=str(OUT / '05_login_filled.png'), full_page=False)
            print('05 login filled')
            # submit
            btn = page.locator('button[type="submit"], button:has-text("Se connecter"), button:has-text("Connexion")').first
            await btn.click()
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f'  ⚠ login fill error: {e}')

        # 6. Mon Accueil (after login)
        await page.goto(f'{BASE}/mon-accueil', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3500)
        await page.screenshot(path=str(OUT / '06_mon_accueil.png'), full_page=False)
        print('06 mon accueil')

        # 7. Chat avec Soléna
        await page.goto(f'{BASE}/chat-astral', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '07_chat_solena.png'), full_page=False)
        print('07 chat')

        # 8. Type a message in the chat
        try:
            input_box = page.locator('textarea, input[type="text"]').first
            await input_box.fill('Bonjour Soléna, je suis Bélier ascendant Cancer')
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(OUT / '08_chat_typing.png'), full_page=False)
            print('08 chat typing')
        except Exception as e:
            print(f'  ⚠ chat typing: {e}')

        # 9. Horoscope du jour (via outils)
        await page.goto(f'{BASE}/outils/horoscope', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '09_horoscope_jour.png'), full_page=False)
        print('09 horoscope')

        # 10. Numérologie tool
        await page.goto(f'{BASE}/outils/numerologie', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '10_numerologie.png'), full_page=False)
        print('10 numérologie')

        # 11. Tarot croix celtique
        await page.goto(f'{BASE}/outils/tarot', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '11_tarot.png'), full_page=False)
        print('11 tarot')

        # 12. Bibliothèque
        await page.goto(f'{BASE}/bibliotheque', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '12_bibliotheque.png'), full_page=False)
        print('12 bibliothèque')

        # 13. Quotidien / cercle
        await page.goto(f'{BASE}/quotidien', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUT / '13_quotidien.png'), full_page=False)
        print('13 quotidien')

        await browser.close()
        print(f'\n✅ done in {OUT}')


if __name__ == '__main__':
    asyncio.run(main())
