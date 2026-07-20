#!/usr/bin/env python3
"""
Upload des 22 arcanes majeurs (Tarot Marseille) créés par Nathalie
vers Supabase Storage bucket 'library/tarot/'.

Pour chaque carte : génère 3 tailles (512, 1080, 2048) au format PNG
et upload avec le nom standard {slug}_{size}.png.

Mapping fichier source → slug canonique (Marseille tradition, comme
convenu avec Nathalie ; justice=8, force=11, arcane_sans_nom=13).

Usage : python3 /app/backend/scripts/upload_tarot_arcanes.py /tmp/tarot_upload
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from supabase import create_client

# Charge /app/backend/.env
load_dotenv(Path(__file__).parent.parent / '.env')

# Mapping — noms exacts des fichiers source → slug canonique attendu par LibraryImage
NAME_MAP = {
    '00_le_mat_2.png':                       '00_le_mat',
    '01_le_bateleur_final_2.png':            '01_le_bateleur',
    '02_la_papesse_corrected_2.png':         '02_la_papesse',
    '03_l_imperatrice_corrected_2.png':      '03_l_imperatrice',
    '04_l_empereur_corrected_2.png':         '04_l_empereur',
    '05_le_pape_corrected_2.png':            '05_le_pape',
    '06_l_amoureux_corrected_2.png':         '06_les_amoureux',
    '07_le_chariot_corrected_2.png':         '07_le_chariot',
    '08_la_justice_corrected_2.png':         '08_la_justice',
    '09_l_hermite_corrected_2.png':          '09_l_hermite',
    '10_la_roue_de_fortune_corrigee_2.png':  '10_la_roue_de_fortune',
    '11_la_force_corrected_2.png':           '11_la_force',
    '12_le_pendu_corrected_2.png':           '12_le_pendu',
    '13_l_arcane_sans_nom_corrected_2.png':  '13_l_arcane_sans_nom',
    '14_temperance_corrected_2.png':         '14_la_temperance',
    '15_le_diable_corrected_2.png':          '15_le_diable',
    '16_la_maison_dieu_corrected_2.png':     '16_la_maison_dieu',
    '17_l_etoile_corrected_2.png':           '17_l_etoile',
    '18_la_lune_corrected_2.png':            '18_la_lune',
    '19_le_soleil_corrected_1.png':          '19_le_soleil',
    '20_le_jugement_corrected_2.png':        '20_le_jugement',
    '21_le_monde_corrected_2.png':           '21_le_monde',
}

SIZES = [512, 1080, 2048]  # largeurs cibles
BUCKET = 'library'
FOLDER = 'tarot'


def main():
    src_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/tarot_upload')
    supabase_url = os.environ['SUPABASE_URL']
    service_key  = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    supabase = create_client(supabase_url, service_key)

    tmp_out = Path('/tmp/tarot_resized')
    tmp_out.mkdir(exist_ok=True)

    uploaded, failed = [], []

    for file_name, slug in NAME_MAP.items():
        src = src_dir / file_name
        if not src.exists():
            print(f'❌ Missing: {file_name}')
            failed.append((file_name, 'missing source'))
            continue

        print(f'\n📤 {file_name} → {slug}')
        try:
            img = Image.open(src).convert('RGBA')
            orig_w, orig_h = img.size
            print(f'   original: {orig_w}×{orig_h}')

            for w in SIZES:
                # Redimensionne en respectant le ratio (hauteur proportionnelle)
                h = int(orig_h * (w / orig_w))
                resized = img.resize((w, h), Image.Resampling.LANCZOS)
                out_path = tmp_out / f'{slug}_{w}.png'
                # Optimize=True pour compresser (mais garde qualité PNG lossless)
                resized.save(out_path, 'PNG', optimize=True)
                out_size = out_path.stat().st_size

                # Upload vers Supabase Storage — upsert=true pour idempotence
                with open(out_path, 'rb') as f:
                    supabase.storage.from_(BUCKET).upload(
                        path=f'{FOLDER}/{slug}_{w}.png',
                        file=f.read(),
                        file_options={
                            'content-type': 'image/png',
                            'upsert': 'true',
                            'cache-control': 'public, max-age=31536000',
                        },
                    )
                print(f'   ✓ {w}px ({out_size//1024} KB)')

            uploaded.append(slug)
        except Exception as e:
            print(f'   ❌ ERROR: {e}')
            failed.append((file_name, str(e)))

    print(f'\n\n═══════════════════════════════════════════════════')
    print(f'✅ Uploaded: {len(uploaded)}/{len(NAME_MAP)}')
    for s in uploaded:
        print(f'   • {s}')
    if failed:
        print(f'\n❌ Failed: {len(failed)}')
        for f, why in failed:
            print(f'   • {f}: {why}')
    print(f'═══════════════════════════════════════════════════')


if __name__ == '__main__':
    main()
