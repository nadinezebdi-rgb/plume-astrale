"""
Burn les titres d'outils en lower-third doré sur chaque frame,
puis remonte la vidéo TikTok 40 sec.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

FRAMES_IN = Path('/tmp/tiktok_frames')
FRAMES_OUT = Path('/tmp/tiktok_frames_titled')
FRAMES_OUT.mkdir(exist_ok=True)

# Titre par slug (correspond à PAGES dans tiktok_outils_montage.py)
TITLES = {
    '01_tarot': 'TAROT',
    '02_ouinon': 'TAROT OUI / NON',
    '03_oracle': 'ORACLE DES ANGES',
    '04_theme_natal': 'THÈME NATAL',
    '05_horoscope': 'HOROSCOPE',
    '06_compatibilite': 'COMPATIBILITÉ',
    '07_revolution': 'RÉVOLUTION SOLAIRE',
    '08_numerologie': 'NUMÉROLOGIE',
    '09_archetype': 'ARCHÉTYPE',
    '10_love_languages': 'LOVE LANGUAGES',
    '11_energie': 'ÉNERGIE DU JOUR',
    '12_rituel': 'RITUELS PERSONNELS',
    '13_consultation': 'DISCUSSION AVEC SOLÉNA',
    '14_astrosexo': 'ÉNERGIES AMOUREUSES',
    '15_kabbale': 'ARBRE DE VIE KABBALE',
    '16_astrocarto': 'ASTROCARTOGRAPHIE',
    '17_natal_29': 'THÈME NATAL COMPLET',
    '18_rencontres': 'GUIDE DES RENCONTRES',
    '19_pack_karmique': 'PACK KARMIQUE',
    '20_cercle': 'CERCLE SOLÉNA',
}

FONT_TITLE = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
FONT_SUB = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'

# Couleurs Plume Astrale
GOLD = (212, 175, 55, 255)
GOLD_SOFT = (232, 199, 102, 255)
IVORY = (245, 238, 224, 255)
DARK = (17, 22, 37, 220)

def burn_title(img_path: Path, title: str, out_path: Path):
    img = Image.open(img_path).convert('RGBA')
    W, H = img.size

    # Overlay layer for the lower-third band
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bande sombre en bas (barre gradient effect via 3 rectangles)
    band_h = 260
    band_top = H - band_h - 120
    # Fond semi-transparent
    draw.rectangle([(0, band_top), (W, band_top + band_h)], fill=(11, 15, 30, 200))
    # Fine ligne dorée en haut de la bande
    draw.rectangle([(0, band_top), (W, band_top + 3)], fill=GOLD)
    # Fine ligne dorée en bas
    draw.rectangle([(0, band_top + band_h - 3), (W, band_top + band_h)], fill=GOLD)

    # Titre principal — Liberation Serif Bold, letter-spacing large
    font_title = ImageFont.truetype(FONT_TITLE, 74)
    # Letter-spacing manuel : on décompose en lettres et on les dessine espacées
    spaced = '  '.join(list(title))
    bbox = draw.textbbox((0, 0), spaced, font=font_title)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (W - text_w) // 2
    y = band_top + (band_h - text_h) // 2 - 10
    # Ombre douce
    draw.text((x + 2, y + 2), spaced, font=font_title, fill=(0, 0, 0, 180))
    # Titre or
    draw.text((x, y), spaced, font=font_title, fill=GOLD_SOFT)

    # Sous-titre "plume-astrale.fr" en italique ivoire
    font_sub = ImageFont.truetype(FONT_SUB, 32)
    subtitle = '✦ plume-astrale.fr ✦'
    bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
    sub_w = bbox2[2] - bbox2[0]
    draw.text(((W - sub_w) // 2, band_top + band_h - 55), subtitle, font=font_sub, fill=IVORY)

    # Compose et sauve
    out = Image.alpha_composite(img, overlay).convert('RGB')
    out.save(out_path, 'JPEG', quality=90)


print(f'=== Burn titres sur {len(TITLES)} frames ===')
for slug, title in TITLES.items():
    src = FRAMES_IN / f'{slug}.jpg'
    dst = FRAMES_OUT / f'{slug}.jpg'
    if not src.exists():
        print(f'  ✗ {slug} : source manquante')
        continue
    burn_title(src, title, dst)
    print(f'  ✓ {slug} → « {title} »')

print('\n=== Reconstruction MP4 40 sec ===')
out_mp4 = Path('/app/frontend/public/marketing/tiktok_outils_montage.mp4')
if out_mp4.exists():
    out_mp4.unlink()

cmd = [
    'ffmpeg', '-y',
    '-framerate', '0.5', '-pattern_type', 'glob', '-i', str(FRAMES_OUT / '*.jpg'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-crf', '22', '-preset', 'medium',
    '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1',
    '-movflags', '+faststart',
    str(out_mp4),
]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print('FFMPEG ERR:', r.stderr[-1500:])
else:
    size_mb = out_mp4.stat().st_size / 1024 / 1024
    print(f'✓ MP4 généré : {out_mp4} ({size_mb:.2f} MB)')
