"""Migration script — upload /app/backend/assets/library/* to Supabase Storage bucket 'library'.

Preserves the folder structure : signs/, planets/, houses/, tarot/, glyphs-svg/, style-refs/.
Idempotent : reuploade avec upsert=true.
Sortie : liste des URLs publiques ecrite dans /app/backend/assets/library/manifest_supabase.json
"""
from __future__ import annotations
import os
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / '.env')

from services.supabase_client import get_admin_client  # noqa: E402

LIBRARY_ROOT = Path('/app/backend/assets/library')
BUCKET = 'library'
ALLOWED_EXT = {'.png', '.svg', '.jpg', '.jpeg', '.webp'}

CONTENT_TYPES = {
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
}


def main():
    sb = get_admin_client()
    if not LIBRARY_ROOT.exists():
        print(f'❌ {LIBRARY_ROOT} n\'existe pas')
        return
    files = [p for p in LIBRARY_ROOT.rglob('*') if p.is_file() and p.suffix.lower() in ALLOWED_EXT]
    print(f'📦 {len(files)} fichiers a uploader depuis {LIBRARY_ROOT}')
    urls: dict[str, str] = {}
    ok = 0
    err = 0
    for i, f in enumerate(files, 1):
        rel = f.relative_to(LIBRARY_ROOT).as_posix()  # ex: 'tarot/00_le_mat_1080.png'
        ct = CONTENT_TYPES.get(f.suffix.lower(), 'application/octet-stream')
        try:
            with open(f, 'rb') as fh:
                sb.storage.from_(BUCKET).upload(
                    path=rel,
                    file=fh.read(),
                    file_options={'content-type': ct, 'upsert': 'true', 'cache-control': '31536000'},
                )
            pub = sb.storage.from_(BUCKET).get_public_url(rel)
            urls[rel] = pub
            ok += 1
            if i % 20 == 0 or i == len(files):
                print(f'  [{i}/{len(files)}] {rel} ✓')
        except Exception as e:
            err += 1
            print(f'  [{i}/{len(files)}] {rel} ❌ {str(e)[:150]}')
        time.sleep(0.05)  # tres leger throttle
    # Save manifest
    out = LIBRARY_ROOT / 'manifest_supabase.json'
    out.write_text(json.dumps({'bucket': BUCKET, 'count': len(urls), 'files': urls}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\n✅ OK: {ok}   ❌ ERR: {err}   → manifest ecrit dans {out}')
    print(f'Total taille locale: {sum(f.stat().st_size for f in files)/1024/1024:.1f} MB')


if __name__ == '__main__':
    main()
