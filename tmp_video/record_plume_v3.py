"""
V3 : 60s vertical 1080x1920 avec Blog + captions animés en overlay.

Séquence :
  0-12s   → Hero home
  12-25s  → Horoscope quotidien (Lion)
  25-37s  → Blog articles éditoriaux
  37-49s  → Mon Espace personnel (login test)
  49-60s  → Cercle Soléna + CTA final

Captions overlay (via ffmpeg drawtext) synchronisés :
  0.5-3s   : "Comprendre les périodes de votre vie"
  12.5-15s : "Ton horoscope, chaque jour"
  25.5-28s : "Des articles pour comprendre"
  37.5-40s : "Ton espace personnel"
  49.5-52s : "Un rendez-vous mensuel"
  55-60s   : "plume-astrale.fr · 20 crédits offerts"
"""
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path("/app/tmp_video")
OUT_DIR.mkdir(exist_ok=True, parents=True)
BASE_URL = "https://consultation-astro.preview.emergentagent.com"
TEST_EMAIL = "test@plume-astrale.fr"
TEST_PASSWORD = "TestPlume2026!"

VIEWPORT = {"width": 390, "height": 844}
RECORD_SIZE = {"width": 390, "height": 844}

# Serif élégant pour captions
FONT_SERIF = "/app/backend/assets/fonts/CormorantGaramond-Bold.ttf"
FONT_SANS = "/app/backend/assets/fonts/tiktok/BebasNeue-Regular.ttf"

SCENES = [
    {
        "name": "hero", "url": "/", "wait_load": 3500,
        "actions": [
            {"scroll_to": 0, "duration": 500},
            {"scroll_to": 300, "duration": 3500},
            {"scroll_to": 700, "duration": 3000},
            {"scroll_to": 1100, "duration": 2500},
        ],
    },
    {
        "name": "horoscope", "url": "/horoscope", "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 400, "duration": 2500},
            {"click_selector": "a[href*='/horoscope/lion']", "wait_after": 2500},
            {"scroll_to": 300, "duration": 3000},
            {"scroll_to": 700, "duration": 2500},
        ],
    },
    {
        "name": "blog", "url": "/blog", "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 400, "duration": 3200},
            {"scroll_to": 900, "duration": 3200},
            {"scroll_to": 1400, "duration": 2500},
        ],
    },
    {
        "name": "mon-compte", "url": "/mon-compte", "wait_load": 3000, "login_first": True,
        "actions": [
            {"scroll_to": 0, "duration": 800},
            {"scroll_to": 400, "duration": 3200},
            {"scroll_to": 800, "duration": 3200},
            {"scroll_to": 1200, "duration": 2500},
        ],
    },
    {
        "name": "cercle", "url": "/cercle-solena", "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 1000},
            {"scroll_to": 500, "duration": 3500},
            {"scroll_to": 1000, "duration": 3200},
            {"scroll_to": 1500, "duration": 2500},
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
    print("  ▸ login…")
    await page.goto(f"{BASE_URL}/connexion", wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(1200)
    try:
        btn = page.locator('[data-testid="cookie-accept"]')
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(300)
    except Exception:
        pass
    try:
        await page.locator('input[type="email"], input[name="email"]').first.fill(TEST_EMAIL)
        await page.locator('input[type="password"], input[name="password"]').first.fill(TEST_PASSWORD)
        submit = page.locator('button[type="submit"], button:has-text("Se connecter")').first
        await submit.click()
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
        return sorted((OUT_DIR / "raw").glob("*.webm"))


def build_caption_filters():
    """
    Génère une liste de filtres drawtext pour ffmpeg :
    chaque caption apparaît (fade in), reste, disparaît (fade out).
    """
    # (text, font, size, y_pos_from_top, start_s, end_s, style)
    # style: 'serif' = italic serif or 'hook' = big sans caps
    captions = [
        # HOOK grand — bas du hero
        {"text": "Comprendre les périodes", "font": FONT_SERIF, "size": 62,
         "y_pct": 0.72, "start": 0.8, "end": 4.5, "align": "center",
         "shadow": True, "italic": True},
        {"text": "de votre vie.", "font": FONT_SERIF, "size": 62,
         "y_pct": 0.79, "start": 0.8, "end": 4.5, "align": "center",
         "shadow": True, "italic": True},
        # Horoscope
        {"text": "TON HOROSCOPE, CHAQUE JOUR", "font": FONT_SANS, "size": 50,
         "y_pct": 0.06, "start": 12.5, "end": 16.5, "align": "center",
         "shadow": True, "italic": False},
        # Blog
        {"text": "COMPRENDRE  ·  APPROFONDIR", "font": FONT_SANS, "size": 50,
         "y_pct": 0.06, "start": 25.5, "end": 29.5, "align": "center",
         "shadow": True, "italic": False},
        # Mon espace
        {"text": "TON ESPACE PERSONNEL", "font": FONT_SANS, "size": 54,
         "y_pct": 0.06, "start": 37.5, "end": 41.5, "align": "center",
         "shadow": True, "italic": False},
        # Cercle
        {"text": "UN RENDEZ-VOUS MENSUEL", "font": FONT_SANS, "size": 54,
         "y_pct": 0.06, "start": 49.5, "end": 53.5, "align": "center",
         "shadow": True, "italic": False},
        # CTA final — plein écran
        {"text": "20 CRÉDITS OFFERTS", "font": FONT_SANS, "size": 90,
         "y_pct": 0.40, "start": 55, "end": 60, "align": "center",
         "shadow": True, "italic": False, "color": "0xD4AF37"},
        {"text": "plume-astrale.fr", "font": FONT_SERIF, "size": 60,
         "y_pct": 0.52, "start": 55, "end": 60, "align": "center",
         "shadow": True, "italic": True},
    ]

    # Build filter chain
    filters = []
    for c in captions:
        fade_in = 0.4
        fade_out = 0.4
        # alpha via if/else + fade
        # We use enable='between(t,s,e)' and animate alpha with min/max
        alpha_expr = (
            f"if(lt(t,{c['start']}+{fade_in}),"
            f"(t-{c['start']})/{fade_in},"
            f"if(gt(t,{c['end']}-{fade_out}),"
            f"({c['end']}-t)/{fade_out},1))"
        )
        color = c.get("color", "white")
        y_expr = f"h*{c['y_pct']}"
        # Ombre + texte
        shadow_filter = (
            f"drawtext=fontfile={c['font']}:text='{c['text']}':"
            f"fontsize={c['size']}:fontcolor=black@0.55:"
            f"x=(w-text_w)/2+3:y={y_expr}+4:"
            f"enable='between(t,{c['start']},{c['end']})':"
            f"alpha='{alpha_expr}'"
        )
        text_filter = (
            f"drawtext=fontfile={c['font']}:text='{c['text']}':"
            f"fontsize={c['size']}:fontcolor={color}:"
            f"x=(w-text_w)/2:y={y_expr}:"
            f"enable='between(t,{c['start']},{c['end']})':"
            f"alpha='{alpha_expr}'"
        )
        filters.append(shadow_filter)
        filters.append(text_filter)

    return filters


def postprocess(webms):
    if not webms:
        raise RuntimeError("Aucune vidéo webm")
    concat_txt = OUT_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{w.resolve()}'" for w in webms))
    merged = OUT_DIR / "merged.webm"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_txt), "-c", "copy", str(merged)],
                   check=True, capture_output=True)

    # Build filter graph : scale + captions + fade in/out global
    caption_filters = build_caption_filters()
    vf = (
        "scale=1080:1920:flags=lanczos,"
        + ",".join(caption_filters)
        + ",fade=t=in:st=0:d=0.6,fade=t=out:st=58.5:d=1.5"
    )

    final = OUT_DIR / "plume_astrale_60s_captions.mp4"
    proc = subprocess.run([
        "ffmpeg", "-y", "-i", str(merged),
        "-vf", vf,
        "-t", "60",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
        str(final),
    ], capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-1500:])
        raise RuntimeError("ffmpeg encode failed")
    return final


async def main():
    webms = await record_scenes()
    print(f"▸ {len(webms)} webm(s)")
    final = postprocess(webms)
    print(f"✓ FINAL: {final} ({final.stat().st_size/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    asyncio.run(main())
