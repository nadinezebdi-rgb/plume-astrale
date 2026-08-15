"""
V2 : 60s vertical 1080x1920 avec ajout /mon-compte + réduction Chat.

Séquence :
  0-12s   → Hero home (scroll cinématique lent)
  12-27s  → Horoscope quotidien (/horoscope + clic Lion + contenu)
  27-33s  → Chat Soléna (juste aperçu 6s)
  33-46s  → Espace personnel /mon-compte (avec login test)
  46-60s  → Cercle Soléna (offre abonnement)
"""
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path("/app/tmp_video")
OUT_DIR.mkdir(exist_ok=True, parents=True)

# On tourne sur PREVIEW (login test disponible), UI identique à prod
BASE_URL = "https://consultation-astro.preview.emergentagent.com"

TEST_EMAIL = "test@plume-astrale.fr"
TEST_PASSWORD = "TestPlume2026!"

VIEWPORT = {"width": 390, "height": 844}
RECORD_SIZE = {"width": 390, "height": 844}

SCENES = [
    {
        "name": "hero",
        "url": "/",
        "wait_load": 3500,
        "actions": [
            {"scroll_to": 0, "duration": 500},
            {"scroll_to": 300, "duration": 3500},
            {"scroll_to": 700, "duration": 3000},
            {"scroll_to": 1100, "duration": 2500},
        ],
    },
    {
        "name": "horoscope",
        "url": "/horoscope",
        "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 400, "duration": 3000},
            {"click_selector": "a[href*='/horoscope/lion']", "wait_after": 3000},
            {"scroll_to": 300, "duration": 3200},
            {"scroll_to": 700, "duration": 2500},
        ],
    },
    {
        "name": "chat",
        "url": "/chat-ia",
        "wait_load": 2000,
        # Court : juste apercu
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 300, "duration": 2500},
            {"scroll_to": 600, "duration": 2000},
        ],
    },
    {
        "name": "mon-compte",
        "url": "/mon-compte",  # ira via login d'abord (handler special)
        "wait_load": 3000,
        "login_first": True,
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 300, "duration": 3000},
            {"scroll_to": 700, "duration": 3000},
            {"scroll_to": 1100, "duration": 3000},
            {"scroll_to": 500, "duration": 2500},
        ],
    },
    {
        "name": "cercle",
        "url": "/cercle-solena",
        "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 1000},
            {"scroll_to": 500, "duration": 3500},
            {"scroll_to": 1000, "duration": 3500},
            {"scroll_to": 1500, "duration": 3000},
        ],
    },
]


async def smooth_scroll(page, target, duration_ms):
    await page.evaluate(
        """([target, duration]) => new Promise((resolve) => {
          const start = window.scrollY;
          const distance = target - start;
          const startTime = performance.now();
          function step(now) {
            const t = Math.min(1, (now - startTime) / duration);
            const ease = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t + 2, 2)/2;
            window.scrollTo(0, start + distance * ease);
            if (t < 1) requestAnimationFrame(step); else resolve();
          }
          requestAnimationFrame(step);
        })""",
        [target, duration_ms],
    )


async def do_login(page):
    """Login flow via /connexion."""
    print("  ▸ login…")
    await page.goto(f"{BASE_URL}/connexion", wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(1200)
    # Handle cookies if visible
    try:
        btn = page.locator('[data-testid="cookie-accept"]')
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(300)
    except Exception:
        pass

    # Fill form
    email_sel = 'input[type="email"], input[name="email"], [data-testid="login-email"]'
    pw_sel = 'input[type="password"], input[name="password"], [data-testid="login-password"]'
    try:
        await page.locator(email_sel).first.fill(TEST_EMAIL)
        await page.locator(pw_sel).first.fill(TEST_PASSWORD)
        # Click submit
        submit = page.locator(
            '[data-testid="login-submit"], button[type="submit"], button:has-text("Se connecter")'
        ).first
        await submit.click()
        # Wait for redirect off /connexion
        await page.wait_for_url(lambda u: "/connexion" not in u, timeout=15000)
        print("  ✓ logged in")
        return True
    except Exception as e:
        print(f"  ⚠ login failed: {e}")
        return False


async def record_scenes():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path="/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(OUT_DIR / "raw"),
            record_video_size=RECORD_SIZE,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        page = await context.new_page()

        logged_in = False
        for scene in SCENES:
            if scene.get("login_first") and not logged_in:
                logged_in = await do_login(page)

            url = f"{BASE_URL}{scene['url']}"
            print(f"▸ Scene {scene['name']} → {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                try:
                    await page.goto(url, wait_until="load", timeout=25000)
                except Exception as e:
                    print(f"  ⚠ goto failed: {e}")
                    continue
            await page.wait_for_timeout(scene.get("wait_load", 2000))

            # Cookies (only relevant before login on 1st scene)
            try:
                btn = page.locator('[data-testid="cookie-accept"]')
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_timeout(300)
            except Exception:
                pass

            for act in scene["actions"]:
                if "scroll_to" in act:
                    await smooth_scroll(page, act["scroll_to"], act["duration"])
                elif "click_selector" in act:
                    try:
                        el = page.locator(act["click_selector"]).first
                        if await el.count() > 0:
                            await el.scroll_into_view_if_needed()
                            await page.wait_for_timeout(400)
                            await el.click(timeout=5000)
                            await page.wait_for_timeout(act.get("wait_after", 1500))
                    except Exception as e:
                        print(f"  ⚠ click failed: {e}")

            await page.wait_for_timeout(500)

        await context.close()
        await browser.close()

        webms = sorted((OUT_DIR / "raw").glob("*.webm"))
        return webms


def postprocess(webms):
    if not webms:
        raise RuntimeError("Aucune vidéo webm produite")
    concat_txt = OUT_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{w.resolve()}'" for w in webms))
    merged = OUT_DIR / "merged.webm"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c", "copy", str(merged),
    ], check=True, capture_output=True)

    final = OUT_DIR / "plume_astrale_60s.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(merged),
        "-vf", "scale=1080:1920:flags=lanczos,fade=t=in:st=0:d=0.8,fade=t=out:st=58.5:d=1.5",
        "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        str(final),
    ], check=True, capture_output=True)
    return final


async def main():
    webms = await record_scenes()
    print(f"▸ {len(webms)} webm(s)")
    final = postprocess(webms)
    print(f"✓ FINAL: {final} ({final.stat().st_size/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    asyncio.run(main())
