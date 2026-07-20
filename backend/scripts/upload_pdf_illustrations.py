#!/usr/bin/env python3
"""Upload des 13 illustrations Plume Astrale (1200x1200 webp) vers Supabase Storage `library/pdf/`.

Convertit chaque image en 2 tailles PNG (800px, 1200px) pour ReportLab.
"""
import os, sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from supabase import create_client

load_dotenv(Path(__file__).parent.parent / '.env')

SLUGS = {
    '01_image_amoureux3.webp':                       'amoureux',
    '02_astrologica.webp':                           'fleurs_or',
    '03_virginia_astrologica.webp':                  'astrologica_alt',
    '04_roue_astrologique.webp':                     'roue_zodiaque',
    '05_la_photo_dun_couple_front_contre_front.webp': 'couple',
    '06_1.webp':                                     'chapitre_bleu',
    '07_ciel_astrologique.webp':                     'ciel_zodiaque',
    '08_fleurs_violette.webp':                       'fleurs_violette',
    '09_image_astrale_1.webp':                       'astral_fruits',
    '10_image_astrale2.webp':                        'astral_planete',
    '11_image_astrale_3.webp':                       'astral_mandala',
    '12_image_astrale_4.webp':                       'astral_ciel',
    '13_image_astrale_6.webp':                       'astral_silhouette',
}
SIZES = [800, 1200]

def main():
    src_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/pdf_images')
    sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])
    out = Path('/tmp/pdf_images_resized'); out.mkdir(exist_ok=True)
    for src_name, slug in SLUGS.items():
        src = src_dir / src_name
        if not src.exists():
            print(f'❌ Missing: {src_name}'); continue
        img = Image.open(src).convert('RGB')
        w0, h0 = img.size
        for w in SIZES:
            h = int(h0 * (w / w0))
            r = img.resize((w, h), Image.Resampling.LANCZOS)
            p = out / f'{slug}_{w}.png'
            r.save(p, 'PNG', optimize=True)
            with open(p, 'rb') as f:
                sb.storage.from_('library').upload(
                    path=f'pdf/{slug}_{w}.png', file=f.read(),
                    file_options={'content-type': 'image/png', 'upsert': 'true', 'cache-control': 'public, max-age=31536000'},
                )
            print(f'   ✓ {slug}_{w}.png ({p.stat().st_size//1024} KB)')
    print('DONE')

if __name__ == '__main__':
    main()
