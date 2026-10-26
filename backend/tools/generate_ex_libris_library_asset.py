"""One-shot script to generate the Ex-Libris library illustration (Nano Banana).

Produces a reusable PNG stored at:
    /app/backend/assets/library/ex_libris_bibliotheque.png

Style demandé par l'utilisateur : "Nuit étoilée + reliures dorées" — ambiance
luxe nocturne à intégrer en fond de l'ex-libris du PDF Thème Natal.

Usage:
    cd /app/backend && python -m tools.generate_ex_libris_library_asset
"""
from __future__ import annotations

import asyncio
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402

OUTPUT = Path('/app/backend/assets/library/ex_libris_bibliotheque.png')

PROMPT = (
    "Luxury illustration of an enchanted celestial library at night, "
    "viewed head-on. Tall wooden bookshelves filled with leather-bound books "
    "with glowing gold spines and gold filigree embossing. The walls fade into "
    "a deep midnight-blue starry sky with faint zodiacal constellations and "
    "soft nebulae drifting between the shelves. A single ornate ladder, a "
    "tiny gold reading lamp on a lectern, and a few floating open books with "
    "pages turning softly. Palette : dark navy #0A1026, gold #D4AF37, warm "
    "cream highlights. Mood : ethereal, bibliophile, art-nouveau. Fine "
    "symmetric vertical composition suitable as a book plate background, "
    "clean negative space at the top-center for a title. Painterly, "
    "high-detail, no text, no watermark, no people. Portrait aspect ratio."
)


async def main() -> int:
    api_key = os.getenv('EMERGENT_LLM_KEY')
    if not api_key:
        print('EMERGENT_LLM_KEY not set', file=sys.stderr)
        return 2

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    chat = (
        LlmChat(
            api_key=api_key,
            session_id='ex-libris-library-asset',
            system_message='You are a luxury book-plate illustrator.',
        )
        .with_model('gemini', 'gemini-3.1-flash-image-preview')
        .with_params(modalities=['image', 'text'])
    )

    text, images = await chat.send_message_multimodal_response(UserMessage(text=PROMPT))
    print(f'Text response (preview): {str(text)[:120]!r}')
    if not images:
        print('No images returned', file=sys.stderr)
        return 3

    img = images[0]
    print(f'Mime: {img.get("mime_type")}  data starts: {str(img.get("data"))[:10]}...')
    OUTPUT.write_bytes(base64.b64decode(img['data']))
    print(f'Saved → {OUTPUT}  ({OUTPUT.stat().st_size // 1024} KB)')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
