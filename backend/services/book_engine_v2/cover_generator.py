"""cover_generator — Génération de couverture personnalisée via Gemini Nano Banana.

Pour chaque livre, on crée une illustration cosmique bronze/ivoire personnalisée
selon la signature astrale (Soleil, Lune, Ascendant). L'image est ensuite
overlayed avec le texte Cormorant Garamond au moment du rendu HTML.

Le prompt est déterministe et normatif — pas de "invitation cosmique" IA-slop,
palette imposée strictement.

Modèle : gemini-3.1-flash-image-preview via EMERGENT_LLM_KEY.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

COVER_CACHE_DIR = Path('/app/backend/assets/book/covers_cache')
COVER_CACHE_DIR.mkdir(parents=True, exist_ok=True)


COVER_PROMPT_TEMPLATE = """Create a premium, editorial book cover illustration for "Le Livre Astral", a French personal development book by Plume Astrale.

CRITICAL VISUAL CONSTRAINTS:
- Ivory background: #FBF7F0 (warm off-white paper tone)
- ONLY bronze/gold tones for all illustration elements: #A8823F (main gold), #C9AE7C (soft gold), #E3D6BC (pale gold)
- NO other colors permitted. NO purple, blue, red, green, pink, orange.
- NO text, NO letters, NO numbers, NO signatures in the image.
- NO photorealism. Line-art / editorial illustration style, thin lines, refined engraving quality.
- Vertical A5 composition (portrait, ratio 148:210).

SUBJECT — a "cosmic dial" (cadran cosmique) centered on the page, evoking:
- A stylized zodiac wheel with 12 subtle divisions, thin bronze rays
- The three astral signatures of this person: Sun in {sun_sign}, Moon in {moon_sign}, Ascendant {asc_sign}
- Constellations of {sun_sign} and {moon_sign} rendered as very faint dot-and-line pattern in the background
- A single thin plume feather (silhouette, filled bronze) placed at the bottom third as a signature ornament
- Subtle rays emerging from a central point, evoking a compass or astrolabe
- Generous ivory white space, minimal composition, almost architectural

STYLE REFERENCE: Editorial illustration in the tradition of Hermès catalogs and Aesop packaging — restraint, luxury paper feel, no ornament for ornament's sake. NO digital glow, NO gradients, NO drop shadows, NO watercolor bleeds. Sharp thin lines, bronze on ivory, that's all.

Return ONLY the illustration (no text, no borders, no watermark)."""


def _cache_key(sun_sign: str, moon_sign: str, asc_sign: str, first_name: str) -> str:
    """Clé de cache déterministe sur la signature + prénom (les prénoms différents
    n'affectent PAS l'illustration, mais on garde first_name pour éviter les
    collisions entre livres qui partageraient une signature astrale)."""
    raw = f'{sun_sign.lower()}|{moon_sign.lower()}|{asc_sign.lower()}|{first_name.lower()}'
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


async def generate_cover_image(
    *,
    first_name: str,
    sun_sign: str,
    moon_sign: str,
    asc_sign: str,
    force: bool = False,
) -> Optional[bytes]:
    """Génère l'illustration de couverture personnalisée.

    Retourne les bytes PNG ou None si la génération échoue (le renderer bascule
    alors sur un fallback SVG statique — pas de crash).
    Idempotent : cache local sur la signature.
    """
    cache_key = _cache_key(sun_sign, moon_sign, asc_sign, first_name)
    cache_path = COVER_CACHE_DIR / f'{cache_key}.png'
    if cache_path.exists() and not force:
        return cache_path.read_bytes()

    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        logger.warning('[cover_gen] EMERGENT_LLM_KEY absent — skip')
        return None

    prompt = COVER_PROMPT_TEMPLATE.format(
        sun_sign=sun_sign, moon_sign=moon_sign, asc_sign=asc_sign,
    )

    def _sync_gen() -> Optional[bytes]:
        import asyncio as _a
        loop = _a.new_event_loop()
        try:
            chat = (
                LlmChat(api_key=api_key, session_id=f'cover_{cache_key}',
                        system_message='You are an editorial illustrator for a French premium publishing house.')
                .with_model('gemini', 'gemini-3.1-flash-image-preview')
                .with_params(modalities=['image', 'text'])
            )
            _, images = loop.run_until_complete(
                chat.send_message_multimodal_response(UserMessage(text=prompt))
            )
            if not images:
                logger.warning(f'[cover_gen] Gemini returned no image for {cache_key}')
                return None
            img = images[0]
            data_b64 = img.get('data') if isinstance(img, dict) else None
            if not data_b64:
                logger.warning('[cover_gen] no `data` field in gemini image response')
                return None
            return base64.b64decode(data_b64)
        finally:
            loop.close()

    try:
        import asyncio as _a
        png_bytes = await _a.to_thread(_sync_gen)
        if not png_bytes:
            return None
        cache_path.write_bytes(png_bytes)
        logger.info(f'[cover_gen] cover generated : {len(png_bytes)} bytes → {cache_path.name}')
        return png_bytes
    except Exception as exc:
        logger.error(f'[cover_gen] Gemini call failed: {exc}')
        return None


def resolve_signs_fr(astro: dict) -> tuple[str, str, str]:
    """Extrait ('Lion', 'Cancer', 'Vierge') depuis un dict astro standard."""
    from .wheel import _SIGN_EN_FR, _to_longitude_deg, _SIGN_ORDER

    def sign_of(p):
        s = (p or {}).get('sign', '')
        return _SIGN_EN_FR.get(s.lower(), s.title() if s else '')

    planets = astro.get('planets') or {}
    sun = sign_of(planets.get('sun'))
    moon = sign_of(planets.get('moon'))
    # Ascendant : depuis houses[0]
    houses = astro.get('houses') or []
    asc = ''
    if isinstance(houses, list) and houses:
        h0 = houses[0]
        asc_lon = _to_longitude_deg(h0)
        if asc_lon is not None:
            asc = _SIGN_ORDER[int(asc_lon // 30) % 12]
    return sun or 'Balance', moon or 'Cancer', asc or 'Vierge'
