"""Quick smoke test + one-shot backfill for Emergent Object Storage.

Run: `cd /app/backend && python -m scripts.seed_illust_storage`

- Initialises storage key
- Uploads every file in cache/natal_illustrations/{ex_libris,planets}/
  to the Emergent Storage bucket (idempotent — overwrites are fine)
- Reads one back as a round-trip check
"""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / '.env')

from services.emergent_storage import (  # noqa: E402
    ensure_storage_key, put_object, get_object,
)

_PREFIX = 'plume-astrale/natal-illustrations'


async def main():
    key = await ensure_storage_key()
    print(f'storage key initialized: {bool(key)}')
    if not key:
        return

    ex_lib_dir = ROOT / 'cache' / 'natal_illustrations' / 'ex_libris'
    planet_dir = ROOT / 'cache' / 'natal_illustrations' / 'planets'

    seeded = 0
    first_path = None
    for src, remote_folder in [(ex_lib_dir, 'ex_libris'), (planet_dir, 'planets')]:
        for p in sorted(src.glob('*.png')):
            # Note: our cache files are .png extension but contain JPEG bytes
            # (see _compress_png). Upload as .jpg to keep the on-disk format honest.
            remote = f'{_PREFIX}/{remote_folder}/{p.stem}.jpg'
            ok = await put_object(remote, p.read_bytes(), content_type='image/jpeg')
            print(f'  put {remote} → {ok}')
            if ok:
                seeded += 1
                first_path = first_path or remote

    print(f'seeded: {seeded} files')

    if first_path:
        back = await get_object(first_path)
        print(f'round-trip read {first_path}: {len(back) if back else 0} bytes')


if __name__ == '__main__':
    asyncio.run(main())
