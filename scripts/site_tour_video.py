#!/usr/bin/env python3
"""Screencast automatisé du site Plume Astrale — Playwright.

Navigue à travers les pages clés (accueil, livres, 6 pages produit) avec
des scrolls lents, capturés en vidéo WebM puis converti en MP4.
"""
import asyncio
import subprocess
import time
from pathlib import Path
from playwright.async_api import async_playwright

BASE = 'https://consultation-astro.preview.emergentagent.com'
OUT_DIR = Path('/app/scripts/videos')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Pages à visiter avec un titre affiché et durée de scroll (secondes)
TOUR = [
    { 'url': '/',                 'label': 'Bienvenue',              'scroll_sec': 8 },
    { 'url': '/theme-natal',      'label': 'Thème Natal · 29€',      'scroll_sec': 6 },
    { 'url': '/kabbale',          'label': 'Arbre de Vie · 39€',     'scroll_sec': 6 },
    { 'url': '/astrocartographie','label': 'Astrocartographie · 49€','scroll_sec': 6 },
    { 'url': '/karma-destin',     'label': 'Karma & Destin · 29€',   'scroll_sec': 6 },
    { 'url': '/numerologie',      'label': 'Numérologie · 29€',      'scroll_sec': 5 },
    { 'url': '/synastrie',        'label': 'Astrologie relationnelle · 49€', 'scroll_sec': 6 },
    { 'url': '/credits',          'label': 'Comment ça marche',      'scroll_sec': 5 },
]

async def slow_scroll(page, duration_sec):
    """Scroll doucement du haut jusqu'en bas de la page."""
    height = await page.evaluate('document.body.scrollHeight')
    viewport = await page.evaluate('window.innerHeight')
    total_scroll = max(0, height - viewport)
    if total_scroll < 50:
        await page.wait_for_timeout(int(duration_sec * 1000))
        return
    steps = max(30, int(duration_sec * 20))  # ~20 pas/sec
    step_delay = (duration_sec * 1000) / steps
    for i in range(steps + 1):
        pct = i / steps
        y = int(total_scroll * pct)
        await page.evaluate(f'window.scrollTo({{ top: {y}, behavior: "instant" }})')
        await page.wait_for_timeout(int(step_delay))

async def show_label(page, text):
    """Injecte un titre stylisé pendant 2 sec au chargement de chaque page."""
    await page.evaluate(f'''() => {{
        const banner = document.createElement('div');
        banner.id = 'tour-banner';
        banner.textContent = {text!r};
        Object.assign(banner.style, {{
            position: 'fixed',
            top: '90px', left: '50%',
            transform: 'translateX(-50%) translateY(-20px)',
            padding: '10px 22px',
            maxWidth: '85%',
            background: 'rgba(15, 26, 60, 0.95)',
            color: '#C9A24B',
            fontFamily: '"Playfair Display", serif',
            fontStyle: 'italic',
            fontSize: '17px',
            letterSpacing: '0.02em',
            textAlign: 'center',
            borderRadius: '999px',
            border: '1px solid rgba(201, 162, 75, 0.4)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
            zIndex: 99999,
            opacity: '0',
            transition: 'opacity 500ms ease, transform 500ms ease',
        }});
        document.body.appendChild(banner);
        requestAnimationFrame(() => {{
            banner.style.opacity = '1';
            banner.style.transform = 'translateX(-50%) translateY(0)';
        }});
        setTimeout(() => {{
            banner.style.opacity = '0';
            banner.style.transform = 'translateX(-50%) translateY(-10px)';
            setTimeout(() => banner.remove(), 500);
        }}, 2200);
    }}''')

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path='/pw-browsers/chromium_headless_shell-1208/chrome-linux/headless_shell',
        )
        ctx = await browser.new_context(
            viewport={'width': 720, 'height': 1280},
            record_video_dir=str(OUT_DIR),
            record_video_size={'width': 720, 'height': 1280},
            device_scale_factor=1,
            is_mobile=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        )
        page = await ctx.new_page()

        for step in TOUR:
            print(f"→ {step['url']}  ({step['label']})")
            await page.goto(f'{BASE}{step["url"]}', wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1200)
            await show_label(page, step['label'])
            await page.wait_for_timeout(2500)
            await slow_scroll(page, step['scroll_sec'])
            await page.wait_for_timeout(800)

        await ctx.close()
        await browser.close()

    # Récupère la vidéo générée
    videos = sorted(OUT_DIR.glob('*.webm'), key=lambda p: p.stat().st_mtime)
    if not videos:
        print('Aucune vidéo générée')
        return
    latest = videos[-1]
    print(f'\nWebM brut : {latest} ({latest.stat().st_size // 1024} KB)')

    # Convertit en MP4 (H.264) plus universellement lisible
    mp4_path = OUT_DIR / f'plume-astrale-tour-{int(time.time())}.mp4'
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', str(latest),
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
         '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(mp4_path)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f'MP4 final : {mp4_path} ({mp4_path.stat().st_size // 1024} KB)')
    else:
        print('FFmpeg error:', result.stderr[-500:])

if __name__ == '__main__':
    asyncio.run(main())
