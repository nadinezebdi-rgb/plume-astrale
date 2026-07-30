"""
Génère un screen recording TikTok montrant les 10 outils principaux.
Format 1080x1920 (9:16), ~8 secondes, effet zoom ken-burns par page.
"""
import asyncio
import subprocess
import sys
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path('/app/frontend/public/marketing')
FRAMES_DIR = Path('/tmp/tiktok_frames')
FRAMES_DIR.mkdir(exist_ok=True)

BASE = 'https://consultation-astro.preview.emergentagent.com'

# 20 pages clés (14 outils + 6 rapports prestige, exclu Trio 79€)
PAGES = [
    ('01_tarot', f'{BASE}/outils/tarot', 'TAROT'),
    ('02_ouinon', f'{BASE}/outils/tarot/oui-non', 'TAROT OUI/NON'),
    ('03_oracle', f'{BASE}/outils/oracle', 'ORACLE DES ANGES'),
    ('04_theme_natal', f'{BASE}/outils/theme-natal', 'THÈME NATAL'),
    ('05_horoscope', f'{BASE}/outils/horoscope', 'HOROSCOPE'),
    ('06_compatibilite', f'{BASE}/outils/compatibilite', 'COMPATIBILITÉ'),
    ('07_revolution', f'{BASE}/outils/revolution-solaire', 'RÉVOLUTION SOLAIRE'),
    ('08_numerologie', f'{BASE}/outils/numerologie', 'NUMÉROLOGIE'),
    ('09_archetype', f'{BASE}/outils/archetype', 'ARCHÉTYPE'),
    ('10_love_languages', f'{BASE}/outils/love-languages', 'LOVE LANGUAGES'),
    ('11_energie', f'{BASE}/outils/energie', 'ÉNERGIE DU JOUR'),
    ('12_rituel', f'{BASE}/outils/rituel', 'RITUELS PERSONNELS'),
    ('13_consultation', f'{BASE}/outils/consultation', 'DISCUSSION SOLÉNA'),
    ('14_astrosexo', f'{BASE}/outils/astrosexo', 'ÉNERGIES AMOUREUSES'),
    ('15_kabbale', f'{BASE}/kabbale', 'ARBRE DE VIE KABBALE'),
    ('16_astrocarto', f'{BASE}/astrocartographie', 'ASTROCARTOGRAPHIE'),
    ('17_natal_29', f'{BASE}/theme-natal', 'THÈME NATAL COMPLET'),
    ('18_rencontres', f'{BASE}/rencontres-astrales', 'GUIDE DES RENCONTRES'),
    ('19_pack_karmique', f'{BASE}/pack-karmique', 'PACK KARMIQUE'),
    ('20_cercle', f'{BASE}/cercle-solena', 'CERCLE SOLÉNA'),
]

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 1080, 'height': 1920})
        page = await context.new_page()
        for slug, url, _label in PAGES:
            try:
                await page.goto(url, wait_until='networkidle', timeout=25000)
                await page.wait_for_timeout(1200)
                # Essaie de dismisser un éventuel banner cookies
                try:
                    await page.get_by_text('ACCEPTER').click(force=True, timeout=1500)
                    await page.wait_for_timeout(500)
                except Exception:
                    pass
                out = FRAMES_DIR / f'{slug}.jpg'
                await page.screenshot(path=str(out), quality=90, full_page=False, type='jpeg')
                print(f'  ✓ {slug} → {out}')
            except Exception as e:
                print(f'  ✗ {slug} : {e}')
        await browser.close()

def build_video():
    """Concatène les JPGs en MP4 avec ken-burns via ffmpeg."""
    # Sortie 1080x1920, 30fps, chaque image ~0.9s avec zoom léger
    frame_duration = 0.9  # sec
    fps = 30
    frames_per_image = int(frame_duration * fps)

    filters = []
    inputs = []
    frames_sorted = sorted(FRAMES_DIR.glob('*.jpg'))
    for i, fp in enumerate(frames_sorted):
        inputs.extend(['-loop', '1', '-t', str(frame_duration), '-i', str(fp)])
        # Ken-burns zoom : commence 1.0, finit 1.08
        filters.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,zoompan=z='min(zoom+0.0018,1.08)':d={frames_per_image}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,setsar=1[v{i}]"
        )
    concat = ''.join(f'[v{i}]' for i in range(len(frames_sorted))) + f'concat=n={len(frames_sorted)}:v=1:a=0[out]'
    filter_complex = ';'.join(filters) + ';' + concat

    output = OUTPUT_DIR / 'tiktok_outils_montage.mp4'
    cmd = ['ffmpeg', '-y', *inputs,
           '-filter_complex', filter_complex, '-map', '[out]',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', str(fps),
           '-preset', 'medium', '-crf', '20', str(output)]
    print(f'\n→ ffmpeg concat {len(frames_sorted)} frames → {output.name}')
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('FFMPEG STDERR:', r.stderr[-2000:])
        sys.exit(1)
    size_mb = output.stat().st_size / 1024 / 1024
    print(f'✓ MP4 généré : {output} ({size_mb:.2f} MB)')
    print(f'  URL preview : {BASE}/marketing/tiktok_outils_montage.mp4')

if __name__ == '__main__':
    print('=== Étape 1 : capture des 10 screenshots ===')
    asyncio.run(capture())
    print('\n=== Étape 2 : montage vidéo ===')
    build_video()
