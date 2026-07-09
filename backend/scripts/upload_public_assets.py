"""Migration script — upload heavy static assets to Supabase 'public-assets' bucket.

- Backend tarot images : /app/backend/assets/tarot/*.png → public-assets/tarot/*
- Frontend public heavy assets → public-assets/{videos, images, brand}/*
Sortie : /app/backend/assets/public_supabase_manifest.json
"""
from __future__ import annotations
import sys, os, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / '.env')

from services.supabase_client import get_admin_client  # noqa: E402

BUCKET = 'public-assets'
CT = {'.png':'image/png','.svg':'image/svg+xml','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.mp4':'video/mp4','.mov':'video/quicktime'}

# Sources : (chemin_source_absolu, prefix_dans_bucket)
SOURCES = [
    ('/app/backend/assets/tarot', 'tarot'),
    ('/app/frontend/public/videos', 'videos'),
    ('/app/frontend/public/images/tarot', 'images/tarot'),
    ('/app/frontend/public/images/compatibilite', 'images/compatibilite'),
    ('/app/frontend/public/brand', 'brand'),
]

MIN_SIZE_KB = 200  # ne migre que les fichiers > 200KB (les petits restent locaux)


def main():
    sb = get_admin_client()
    urls: dict[str, str] = {}
    total_files = 0
    total_bytes = 0
    ok = err = 0

    for src_dir, prefix in SOURCES:
        src = Path(src_dir)
        if not src.exists():
            print(f'⏭  {src_dir} n\'existe pas, skip')
            continue
        files = [p for p in src.rglob('*') if p.is_file() and p.suffix.lower() in CT and p.stat().st_size >= MIN_SIZE_KB * 1024]
        print(f'\n📁 {src_dir} → {prefix}/  ({len(files)} fichiers >= {MIN_SIZE_KB}KB)')
        for f in files:
            rel = f.relative_to(src).as_posix()
            key = f'{prefix}/{rel}'
            ct = CT.get(f.suffix.lower(), 'application/octet-stream')
            try:
                with open(f,'rb') as fh:
                    sb.storage.from_(BUCKET).upload(
                        path=key, file=fh.read(),
                        file_options={'content-type': ct, 'upsert':'true', 'cache-control':'31536000'},
                    )
                pub = sb.storage.from_(BUCKET).get_public_url(key)
                urls[key] = pub
                ok += 1
                total_bytes += f.stat().st_size
                print(f'  ✓ {key} ({f.stat().st_size/1024:.0f}KB)')
            except Exception as e:
                err += 1
                print(f'  ❌ {key} : {str(e)[:150]}')
            time.sleep(0.05)
        total_files += len(files)

    out = Path('/app/backend/assets/public_supabase_manifest.json')
    out.write_text(json.dumps({'bucket': BUCKET, 'count': len(urls), 'files': urls}, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\n══════════════════════════')
    print(f'✅ OK: {ok}   ❌ ERR: {err}   total: {total_bytes/1024/1024:.1f} MB')
    print(f'Manifest: {out}')


if __name__ == '__main__':
    main()
