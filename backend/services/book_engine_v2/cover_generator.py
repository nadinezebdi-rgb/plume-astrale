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
    max_retries: int = 2,
) -> Optional[bytes]:
    """Génère l'illustration de couverture personnalisée.

    Post-processing OCR (tesseract français) : si l'image contient plus de 5
    caractères imprimables détectés (Gemini triche parfois malgré le prompt
    "no text"), on relance la génération jusqu'à `max_retries` fois.

    Retourne les bytes PNG ou None si la génération échoue.
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

    def _sync_gen(attempt_seed: int) -> Optional[bytes]:
        import asyncio as _a
        loop = _a.new_event_loop()
        try:
            chat = (
                LlmChat(api_key=api_key,
                        session_id=f'cover_{cache_key}_{attempt_seed}',
                        system_message='You are an editorial illustrator for a French premium publishing house.')
                .with_model('gemini', 'gemini-3.1-flash-image-preview')
                .with_params(modalities=['image', 'text'])
            )
            _, images = loop.run_until_complete(
                chat.send_message_multimodal_response(UserMessage(text=prompt))
            )
            if not images:
                return None
            img = images[0]
            data_b64 = img.get('data') if isinstance(img, dict) else None
            return base64.b64decode(data_b64) if data_b64 else None
        finally:
            loop.close()

    for attempt in range(max_retries + 1):
        try:
            import asyncio as _a
            png_bytes = await _a.to_thread(_sync_gen, attempt)
            if not png_bytes:
                logger.warning(f'[cover_gen] attempt {attempt+1} : no image returned')
                continue
            # ── Filtre OCR : rejette si texte parasite détecté ────────
            n_chars, txt = _detect_text_in_image(png_bytes)
            if n_chars > 5:
                logger.warning(
                    f'[cover_gen] attempt {attempt+1}: {n_chars} chars OCR détectés '
                    f'({txt[:60]!r}), retry'
                )
                if attempt < max_retries:
                    continue
                # Dernier essai : on garde quand même l'image (mieux qu'aucune)
                logger.warning('[cover_gen] max retries atteint, image gardée malgré texte')
            cache_path.write_bytes(png_bytes)
            logger.info(
                f'[cover_gen] cover generated : {len(png_bytes)} bytes '
                f'→ {cache_path.name} (attempt {attempt+1}, {n_chars} chars OCR)'
            )
            return png_bytes
        except Exception as exc:
            logger.error(f'[cover_gen] attempt {attempt+1} failed: {exc}')

    return None


def _detect_text_in_image(png_bytes: bytes) -> tuple[int, str]:
    """Retourne (nb_caractères_imprimables_détectés, texte_brut).

    Utilise tesseract-ocr français. Filtre les faux positifs (single chars,
    caractères purement décoratifs) en ne comptant que les chaînes ≥ 3 chars
    alphabétiques.

    Retourne (0, '') si tesseract absent — le filtre devient no-op mais la
    génération continue normalement.
    """
    try:
        import pytesseract  # type: ignore
        from PIL import Image
        import io as _io
    except ImportError:
        return 0, ''
    try:
        img = Image.open(_io.BytesIO(png_bytes))
        raw = pytesseract.image_to_string(img, lang='fra', config='--psm 6')
        # Compte uniquement les mots ≥ 3 chars alphabétiques
        import re
        words = re.findall(r'[A-Za-zÀ-ÿ]{3,}', raw)
        return sum(len(w) for w in words), ' '.join(words[:10])
    except Exception as exc:
        logger.debug(f'[cover_gen] OCR failed (non fatal): {exc}')
        return 0, ''


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
