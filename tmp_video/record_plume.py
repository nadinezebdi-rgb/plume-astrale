"""
Génère un screencast vertical 1080x1920 (60s) de plume-astrale.fr en production.

Séquence :
  0-13s   → Hero home (scroll lent cinématique)
  13-28s  → Horoscope quotidien (page /horoscope + clic sur un signe)
  28-45s  → Chat Soléna (page /chat-ia — landing seulement, car pas d'auth)
  45-60s  → Cercle Soléna (page /cercle-solena)

Playwright enregistre en .webm, puis ffmpeg convertit en .mp4 1080x1920 H.264
avec upscale lanczos depuis 390x844 (viewport mobile natif) → qualité premium.
"""
import asyncio
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

OUT_DIR = Path("/app/tmp_video")
OUT_DIR.mkdir(exist_ok=True, parents=True)

BASE_URL = "https://plume-astrale.fr"

# Viewport mobile natif (déclenche les media queries mobile)
VIEWPORT = {"width": 390, "height": 844}
# Video size : Playwright enregistre à la taille du viewport
RECORD_SIZE = {"width": 390, "height": 844}

# Chaque scène décrit une navigation + un scroll animé
SCENES = [
    {
        "name": "hero",
        "url": "/",
        "wait_load": 3500,       # attente pour hero image + fade-in
        "actions": [
            {"scroll_to": 0, "duration": 500},     # stay at top
            {"scroll_to": 350, "duration": 4000},  # slow scroll into content
            {"scroll_to": 800, "duration": 3500},
            {"scroll_to": 1200, "duration": 2500},
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
            {"scroll_to": 300, "duration": 3000},
            {"scroll_to": 700, "duration": 2500},
        ],
    },
    {
        "name": "chat",
        "url": "/chat-ia",
        "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 1500},
            {"scroll_to": 300, "duration": 3500},
            {"scroll_to": 700, "duration": 4000},
            {"scroll_to": 1100, "duration": 3500},
        ],
    },
    {
        "name": "cercle",
        "url": "/cercle-solena",
        "wait_load": 2500,
        "actions": [
            {"scroll_to": 0, "duration": 1500},
            {"scroll_to": 400, "duration": 3500},
            {"scroll_to": 900, "duration": 3500},
            {"scroll_to": 1400, "duration": 3000},
        ],
    },
]


async def smooth_scroll(page, target, duration_ms):
    """Scroll smooth via JS (requestAnimationFrame) — mieux qu'un scroll instantané."""
    await page.evaluate(
        """([target, duration]) => {
          return new Promise((resolve) => {
            const start = window.scrollY;
            const distance = target - start;
            const startTime = performance.now();
            function step(now) {
              const t = Math.min(1, (now - startTime) / duration);
              // easeInOutQuad
              const ease = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t + 2, 2)/2;
              window.scrollTo(0, start + distance * ease);
              if (t < 1) requestAnimationFrame(step);
              else resolve();
            }
            requestAnimationFrame(step);
          });
        }""",
        [target, duration_ms],
    )


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

        # Cache le bandeau cookies systématiquement en cliquant "Accepter" si présent
        for scene in SCENES:
            url = f"{BASE_URL}{scene['url']}"
            print(f"▸ Scene {scene['name']} → {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception:
                # networkidle can time out; fall back to load
                try:
                    await page.goto(url, wait_until="load", timeout=30000)
                except Exception as e:
                    print(f"  ⚠ goto failed: {e}")
                    continue
            await page.wait_for_timeout(scene.get("wait_load", 2000))
            # Accept cookies once (on first scene)
            try:
                btn = page.locator('[data-testid="cookie-accept"]')
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_timeout(400)
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
                            await page.wait_for_timeout(500)
                            await el.click(timeout=5000)
                            await page.wait_for_timeout(act.get("wait_after", 1500))
                    except Exception as e:
                        print(f"  ⚠ click failed {act['click_selector']}: {e}")

            # Small hold at end of scene
            await page.wait_for_timeout(500)

        await context.close()
        await browser.close()

        # Playwright saves ONE .webm per page across the context lifetime
        webms = sorted((OUT_DIR / "raw").glob("*.webm"))
        return webms


def postprocess(webms):
    """Concatène (si besoin) et upscale à 1080x1920 en H.264."""
    if not webms:
        raise RuntimeError("Aucune vidéo webm produite")

    # Fusionne les webms via concat demuxer
    concat_txt = OUT_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{w.resolve()}'" for w in webms))

    merged = OUT_DIR / "merged.webm"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(merged),
    ], check=True, capture_output=True)

    # Upscale 390x844 → 1080x1920 avec lanczos + fade in/out + H.264 mobile-friendly
    final = OUT_DIR / "plume_astrale_60s.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(merged),
        "-vf",
        # scale upscale + trim to 60s + fade in/out
        "scale=1080:1920:flags=lanczos,fade=t=in:st=0:d=0.8,fade=t=out:st=58.5:d=1.5",
        "-t", "60",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",  # silent — user can add music
        str(final),
    ], check=True, capture_output=True)

    return final


async def main():
    webms = await record_scenes()
    print(f"▸ {len(webms)} webm(s) enregistré(s)")
    final = postprocess(webms)
    size_mb = final.stat().st_size / (1024 * 1024)
    print(f"✓ VIDÉO FINALE : {final} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    asyncio.run(main())
