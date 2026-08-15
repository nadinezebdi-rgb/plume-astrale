"""
V7 — Slideshow "sales deck" 60s vertical 1080x1920.

10 screenshots stratégiques (les moments qui vendent), assemblés en slideshow
avec Ken Burns (zoom lent), captions synchronisés, fondus.

Structure : 10 slides × 6s = 60s
  1. Hero home           → "COMPRENDRE VOTRE PARCOURS"
  2. TrustBar home       → "GARANTIE 14 JOURS · PAIEMENT SÉCURISÉ"
  3. /decouvrir          → "UNE SITUATION, UNE LECTURE"
  4. Sales hero natal    → "49 PAGES PERSONNALISÉES · 29,99€"
  5. Trust block sales   → "SATISFAIT OU REMBOURSÉ"
  6. Includes natal      → "CE QUE VOUS RECEVEZ"
  7. Horoscope Lion      → "TON HOROSCOPE, CHAQUE JOUR"
  8. Cercle ROI          → "15 % MOINS CHER À L'UNITÉ"
  9. Mon Espace          → "TON ESPACE PERSONNEL"
 10. CTA final           → "20 CRÉDITS OFFERTS · plume-astrale.fr"
"""
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path("/app/tmp_video")
SHOTS_DIR = OUT_DIR / "shots_v7"
SHOTS_DIR.mkdir(exist_ok=True, parents=True)
FINAL = OUT_DIR / "plume_astrale_slideshow_60s.mp4"

BASE_URL = "https://consultation-astro.preview.emergentagent.com"
TEST_EMAIL = "test@plume-astrale.fr"
TEST_PASSWORD = "TestPlume2026!"

FONT_SERIF = "/app/backend/assets/fonts/CormorantGaramond-Bold.ttf"
FONT_ANTON = "/app/backend/assets/fonts/tiktok/Anton-Regular.ttf"

VIEWPORT = {"width": 1080, "height": 1920}  # capture directe en résolution finale

# Chaque shot : URL, action éventuelle (scroll ou click), caption
SHOTS = [
    {"file": "01_hero.jpg", "url": "/", "scroll": 0, "wait": 3500,
     "caption": "COMPRENDRE", "caption2": "VOTRE PARCOURS."},
    {"file": "02_trust.jpg", "url": "/", "scroll": 1600, "wait": 2000,
     "caption": "GARANTIE 14 JOURS.", "caption2": "PAIEMENT SÉCURISÉ."},
    {"file": "03_decouvrir.jpg", "url": "/decouvrir", "scroll": 0, "wait": 2500,
     "caption": "UNE SITUATION.", "caption2": "UNE LECTURE."},
    {"file": "04_natal_hero.jpg", "url": "/theme-natal-luxe", "scroll": 0, "wait": 2500,
     "caption": "49 PAGES.", "caption2": "PERSONNALISÉES."},
    {"file": "05_trust_sales.jpg", "url": "/theme-natal-luxe", "scroll": 2400, "wait": 1500,
     "caption": "SATISFAIT OU", "caption2": "REMBOURSÉ."},
    {"file": "06_includes.jpg", "url": "/theme-natal-luxe", "scroll": 3600, "wait": 1500,
     "caption": "CE QUE", "caption2": "VOUS RECEVEZ."},
    {"file": "07_horoscope.jpg", "url": "/horoscope/lion", "scroll": 800, "wait": 2500,
     "caption": "TON HOROSCOPE.", "caption2": "CHAQUE JOUR."},
    {"file": "08_cercle_roi.jpg", "url": "/cercle-solena", "scroll": 700, "wait": 2500,
     "caption": "15 % MOINS CHER.", "caption2": "QU'À L'UNITÉ."},
    {"file": "09_mon_compte.jpg", "url": "/mon-compte", "scroll": 400, "wait": 3000,
     "caption": "TON ESPACE.", "caption2": "TES CRÉDITS.", "login_first": True},
    {"file": "10_cta.jpg", "url": "/", "scroll": 300, "wait": 2500,
     "caption": "20 CRÉDITS OFFERTS", "caption2": "plume-astrale.fr", "cta_slide": True},
]


async def take_shots():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path="/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport={"width": 540, "height": 960},  # mobile CSS breakpoint
            device_scale_factor=2,  # 2x = 1080x1920 output
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = await context.new_page()

        logged_in = False
        for shot in SHOTS:
            if shot.get("login_first") and not logged_in:
                print(f"  ▸ login…")
                await page.goto(f"{BASE_URL}/connexion", wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(1000)
                try:
                    btn = page.locator('[data-testid="cookie-accept"]')
                    if await btn.count() > 0:
                        await btn.first.click()
                        await page.wait_for_timeout(400)
                except Exception:
                    pass
                try:
                    await page.locator('input[type="email"], input[name="email"]').first.fill(TEST_EMAIL)
                    await page.locator('input[type="password"], input[name="password"]').first.fill(TEST_PASSWORD)
                    submit = page.locator('button[type="submit"], button:has-text("Se connecter")').first
                    await submit.click()
                    await page.wait_for_url(lambda u: "/connexion" not in u, timeout=15000)
                    logged_in = True
                    print("  ✓ logged in")
                except Exception as e:
                    print(f"  ⚠ login: {e}")

            url = f"{BASE_URL}{shot['url']}"
            print(f"▸ {shot['file']} → {url} (scroll={shot['scroll']})")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                try:
                    await page.goto(url, wait_until="load", timeout=20000)
                except Exception as e:
                    print(f"  ⚠ goto: {e}")
                    continue
            await page.wait_for_timeout(shot["wait"])

            # Dismiss cookies
            try:
                btn = page.locator('[data-testid="cookie-accept"]')
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_timeout(300)
            except Exception:
                pass

            # Scroll
            if shot["scroll"] > 0:
                await page.evaluate(f"window.scrollTo({{top: {shot['scroll']}, behavior: 'instant'}})")
                await page.wait_for_timeout(700)

            # Hide mobile tabbar for cleaner screenshot
            await page.evaluate("""() => {
              const tb = document.querySelector('.plume-tabbar');
              if (tb) tb.style.display = 'none';
              const cookie = document.querySelector('[data-testid="cookie-consent"]');
              if (cookie) cookie.style.display = 'none';
              const chat = document.querySelector('[data-testid="support-chat-bubble"]');
              if (chat) chat.style.display = 'none';
            }""")
            await page.wait_for_timeout(200)

            path = SHOTS_DIR / shot["file"]
            await page.screenshot(path=str(path), full_page=False, quality=85, type="jpeg")

        await context.close()
        await browser.close()


def build_video():
    """Assemble les 10 shots en 60s avec Ken Burns + captions + fondus."""
    slide_dur = 6.0
    fade_dur = 0.4

    # Chaque slide : zoompan progressive (Ken Burns)
    # scale 1080x1920, zoom de 1.0 → 1.06 sur toute la durée
    inputs = []
    filter_parts = []
    for i, shot in enumerate(SHOTS):
        path = SHOTS_DIR / shot["file"]
        if not path.exists():
            print(f"⚠ missing {path}, skipping")
            continue
        inputs.extend(["-loop", "1", "-t", str(slide_dur), "-i", str(path)])

    # Filter graph : chaque input → scale 1080x1920 → zoompan → drawtext caption
    for i, shot in enumerate(SHOTS):
        # Ken Burns : zoom lent 1.0→1.06, léger pan vers le centre
        zp = (
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,setsar=1,"
            f"zoompan=z='min(zoom+0.0006,1.06)':d={int(slide_dur*25)}:s=1080x1920:fps=25"
        )

        # Captions Anton bold : blanc + or
        c_start = 0.5
        c_end = slide_dur - 0.3
        # Position des captions : haut ou centre selon slide
        # CTA slide (10) : plein centre géant
        is_cta = shot.get("cta_slide")
        c_size = 90 if is_cta else 72
        c1_y = 0.30 if is_cta else 0.08
        c2_y = 0.41 if is_cta else 0.16
        c1_color = "0xD4AF37" if is_cta else "white"
        c2_color = "white" if is_cta else "0xD4AF37"

        alpha = (
            f"if(lt(t,{c_start}+0.3),(t-{c_start})/0.3,"
            f"if(gt(t,{c_end}-0.3),({c_end}-t)/0.3,1))"
        )

        cap_filter = (
            # Line 1 shadow + text
            f"drawtext=fontfile={FONT_ANTON}:text='{shot['caption']}':fontsize={c_size}:"
            f"fontcolor=black@0.7:x=(w-text_w)/2+5:y=h*{c1_y}+6:"
            f"enable='between(t,{c_start},{c_end})':alpha='{alpha}',"
            f"drawtext=fontfile={FONT_ANTON}:text='{shot['caption']}':fontsize={c_size}:"
            f"fontcolor={c1_color}:x=(w-text_w)/2:y=h*{c1_y}:"
            f"enable='between(t,{c_start},{c_end})':alpha='{alpha}',"
            # Line 2 shadow + text
            f"drawtext=fontfile={FONT_ANTON}:text='{shot['caption2']}':fontsize={c_size}:"
            f"fontcolor=black@0.7:x=(w-text_w)/2+5:y=h*{c2_y}+6:"
            f"enable='between(t,{c_start+0.15},{c_end})':alpha='{alpha}',"
            f"drawtext=fontfile={FONT_ANTON}:text='{shot['caption2']}':fontsize={c_size}:"
            f"fontcolor={c2_color}:x=(w-text_w)/2:y=h*{c2_y}:"
            f"enable='between(t,{c_start+0.15},{c_end})':alpha='{alpha}'"
        )

        # Fondu in/out sauf premier/dernier (gérés en global)
        fades = f"fade=t=in:st=0:d={fade_dur}:alpha=1,fade=t=out:st={slide_dur-fade_dur}:d={fade_dur}:alpha=1"

        filter_parts.append(f"{zp},{cap_filter},{fades}[v{i}]")

    # Concat all slides
    concat_inputs = "".join(f"[v{i}]" for i in range(len(SHOTS)))
    concat = f"{concat_inputs}concat=n={len(SHOTS)}:v=1:a=0[out]"

    filter_complex = ";".join(filter_parts) + f";{concat}"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-t", "60",
        "-r", "25",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        str(FINAL),
    ]
    print("▸ Rendering slideshow 60s…")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-2500:])
        raise SystemExit("ffmpeg failed")
    print(f"✓ {FINAL} ({FINAL.stat().st_size/(1024*1024):.1f} MB)")


async def main():
    await take_shots()
    print(f"✓ {len(list(SHOTS_DIR.glob('*.jpg')))} screenshots pris")
    build_video()


if __name__ == "__main__":
    asyncio.run(main())
