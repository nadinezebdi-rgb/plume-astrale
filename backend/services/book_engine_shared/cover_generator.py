"""cover_generator.py — Génération de cover Nano Banana par thème natal.

Utilise Gemini 3.1 Flash Image Preview via emergentintegrations.
La cover est générée UNE FOIS par manuscript (idempotence sur session_id),
stockée sur Emergent Object Storage, et son URL persistée dans
`book_manuscripts.cover_image_url`.

En cas d'échec :
  - Fallback sur la cover de référence Plume Astrale (assets/cover_refs/)
  - Log l'erreur mais n'échoue jamais la génération du livre

Cost expected : ~0.05€ par génération (gemini-3.1-flash-image-preview).
"""
from __future__ import annotations
import base64
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Import conditionnel — si emergentintegrations pas dispo, on tombe direct sur fallback
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    _HAS_EMERGENT = True
except Exception as e:  # pragma: no cover
    logger.warning(f'[cover_gen] emergentintegrations unavailable: {e}')
    _HAS_EMERGENT = False

_FALLBACK_COVER = Path('/app/backend/assets/cover_refs/COUVERTURE_PLUME_masked_1400.jpg')
_MODEL = 'gemini-3.1-flash-image-preview'


def _build_prompt(first_name: str, sun_sign: str, moon_sign: str, asc_sign: str) -> str:
    """Prompt calibré pour la charte Plume Astrale.

    Instructions clés :
    - Palette : bleu nuit profond + or vif + starfield doré + nébuleuses discrètes
    - Composition centrale : cadran astrologique complet dessiné à l'or
      (12 signes du zodiaque en anneau extérieur, planètes en glyphes, lignes
      d'aspects fines au centre)
    - Corner ornaments : petits soleils rayonnants aux 4 coins
    - **Zones texte réservées** : haut 33% et bas 20% laissés en fond bleu nuit
      uni (Plume Astrale y superpose la typographie propre en post-processing)
    - Style : gravure d'astrologie de la Renaissance, précieux, intemporel
    """
    return (
        f"A single portrait-oriented book cover illustration, 148x210mm A5 proportions.\n"
        f"DEEP MIDNIGHT NAVY BLUE BACKGROUND (#0A1428), with a subtle scattered "
        f"golden starfield and faint golden nebula glows.\n"
        f"CENTER: a large, ornate, detailed astrological chart wheel drawn entirely "
        f"in luminous GOLD LINE ART. The wheel has:\n"
        f"  - An outer ring with 12 zodiac symbols engraved (Aries through Pisces)\n"
        f"  - A middle ring with degree tick marks\n"
        f"  - Planetary glyphs (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn) "
        f"placed within house sectors\n"
        f"  - Fine geometric ASPECT LINES crisscrossing the interior in gold\n"
        f"  - Marked cardinal points: AC (Ascendant), MC (Midheaven), DSC, IC\n"
        f"  - A radiant central sun at the very center\n"
        f"STYLE: Renaissance astrology engraving, precious, timeless, spectacular, "
        f"museum-quality gold-on-navy composition. Baroque astrologia treatise aesthetic.\n"
        f"FRAME: a thin golden border around the entire cover with a small 4-pointed "
        f"star ornament at each corner.\n"
        f"CRITICAL — RESERVED TEXT ZONES (leave these EMPTY / plain dark navy, no glyphs, "
        f"no stars, no ornaments):\n"
        f"  - TOP 33% of the cover: solid dark navy, empty\n"
        f"  - BOTTOM 20% of the cover: solid dark navy, empty\n"
        f"Do NOT render any text, letters, names, or words anywhere on the cover.\n"
        f"Do NOT include any figures, faces, characters, or landscapes — only the "
        f"astrological chart wheel and starfield.\n"
        f"This is destined for a personalized astrology book: subject Sun in {sun_sign}, "
        f"Moon in {moon_sign}, Ascendant in {asc_sign} — the wheel should hint at these "
        f"placements being emphasized (their glyphs slightly larger or brighter within the "
        f"wheel), while remaining a general astrological composition."
    )


async def generate_cover_image(
    *,
    session_id: str,
    first_name: str,
    sun_sign: str,
    moon_sign: str,
    asc_sign: str,
    output_path: Optional[Path] = None,
) -> Path:
    """Génère la cover et la sauvegarde en JPEG haute qualité.

    Retourne le chemin du fichier généré (ou du fallback en cas d'échec).
    L'appelant persiste ce chemin dans `book_manuscripts.cover_image_url`
    (URL Emergent Object Storage) après upload.
    """
    if output_path is None:
        output_path = Path(f'/tmp/cover_{session_id}.jpg')

    api_key = os.getenv('EMERGENT_LLM_KEY')
    if not api_key or not _HAS_EMERGENT:
        logger.warning(f'[cover_gen] Falling back to reference cover (key or lib missing)')
        return _FALLBACK_COVER

    prompt = _build_prompt(first_name, sun_sign, moon_sign, asc_sign)
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=f'cover_{session_id}',
            system_message='You are an expert astrological illustrator.',
        )
        chat.with_model('gemini', _MODEL).with_params(modalities=['image', 'text'])
        msg = UserMessage(text=prompt)
        _, images = await chat.send_message_multimodal_response(msg)
        if not images:
            logger.warning(f'[cover_gen] No image returned by Nano Banana for {session_id}')
            return _FALLBACK_COVER
        # Décode + sauvegarde (JPEG q92 pour print)
        image_bytes = base64.b64decode(images[0]['data'])
        # Reencode as JPEG via PIL to control quality and format
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(image_bytes)).convert('RGB')
        # Redimensionne à 1400px de large max (proportion A5)
        img.thumbnail((1400, 2000), Image.LANCZOS)
        img.save(str(output_path), 'JPEG', quality=92, optimize=True)
        logger.info(f'[cover_gen] Generated {output_path} ({output_path.stat().st_size // 1024} KB)')
        return output_path
    except Exception as e:
        logger.exception(f'[cover_gen] Failed for {session_id}: {e}')
        return _FALLBACK_COVER
