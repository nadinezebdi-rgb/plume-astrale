"""
pdf_book_intro.py — helpers partagés pour l'ouverture prestige de chaque PDF.

Fournit :
  - `svg_to_png(svg: str) -> bytes` : convertit un SVG en PNG (via cairosvg)
  - `render_hero_image(story, svg_str, width_cm, height_cm)` : injecte l'illustration hero
  - `render_book_toc(story, styles, product_name, chapters)` : sommaire éditorial
    partagé (déjà fourni par pdf_prestige.toc_page mais utile en shortcut)

Utilisation typique dans un PDF :

    from services.pdf_hero_illustrations import tree_of_life_svg
    from services.pdf_book_intro import render_hero_image
    from services.pdf_prestige import toc_page, chapter_opener, ornament

    # ─── Couverture illustrée ───
    render_hero_image(story, tree_of_life_svg(), width_cm=9, height_cm=9)
    # + titre, sous-titre, prénom, ornements → cf pdf_prestige._cover
    # ─── Sommaire ───
    toc_page(story, styles, [{'roman':'I','title':'...'}, ...])
    # ─── Chapitres ───
    chapter_opener(story, styles, 'I', 'Titre', 'Sous-titre')
"""
from __future__ import annotations
import logging
from io import BytesIO
from typing import Optional
from reportlab.lib.units import cm
from reportlab.platypus import Image

logger = logging.getLogger(__name__)


def svg_to_png(svg_str: str) -> Optional[bytes]:
    """Convertit un SVG en PNG via cairosvg, puis compresse en JPEG optimisé.

    Retourne None en cas d'échec. Les bytes retournés sont un JPEG (magic 0xFFD8),
    qui reste parfaitement accepté par `reportlab.platypus.Image` — pas de changement
    d'API en aval.
    """
    if not svg_str:
        return None
    try:
        import cairosvg
        raw = cairosvg.svg2png(bytestring=svg_str.encode('utf-8'),
                                output_width=1200, output_height=1200)
        # Compression drastique (PNG 1200x1200 ~ 3-8 Mo → JPEG ~ 80-150 Ko)
        try:
            from services.pdf_luxury_helpers import compress_image_bytes
            return compress_image_bytes(raw, max_width=1200, quality=90, force_jpeg=True)
        except Exception:
            return raw
    except Exception as e:
        logger.warning(f"[pdf_book_intro] svg_to_png failed: {e}")
        return None


def render_hero_image(story: list, svg_str: str,
                       width_cm: float = 9, height_cm: float = 9) -> bool:
    """Convertit et insère l'illustration hero SVG dans le PDF. Retourne True si OK."""
    png_bytes = svg_to_png(svg_str)
    if not png_bytes:
        return False
    try:
        img = Image(BytesIO(png_bytes), width=width_cm * cm, height=height_cm * cm)
        img.hAlign = 'CENTER'
        story.append(img)
        return True
    except Exception as e:
        logger.warning(f"[pdf_book_intro] Image insert failed: {e}")
        return False
