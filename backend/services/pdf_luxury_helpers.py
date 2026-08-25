"""
pdf_luxury_helpers.py — helpers premium/luxueux partagés pour tous les PDFs Plume Astrale.

Fournit :
  - `compress_image_bytes(img_bytes, ...)` — compresse un PNG lourd en JPEG optimisé
    (chart wheels 1600px → ~200 Ko au lieu de 15-45 Mo).
  - `ORN_STAR`, `ORN_DIAMOND`, `ORN_FLEUR`, `ORN_HDIVIDER` — glyphes ornementaux
    pré-wrappés dans la police `Symbol` (FreeSerif) pour un rendu net sans carrés vides.
  - `orn(glyph)` / `wrap_ornaments(text)` — helpers pour intégrer les ornements dans
    du texte Paragraph existant sans modifier le rendu texte principal.

Root cause du "carré vide" : Cormorant Garamond et Cinzel ne fournissent PAS les
glyphes de symboles décoratifs (U+2726 ✦, U+269C ⚜, U+25C6 ◆…). ReportLab affiche
alors un rectangle vide (.notdef). En enregistrant FreeSerif comme police `Symbol`
et en wrappant chaque glyphe en `<font name="OrnamentSerif">…</font>`, le rendu retrouve
son étoile dorée.
"""
from __future__ import annotations
import logging
from io import BytesIO
from typing import Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#   COMPRESSION D'IMAGES (chart wheels, world maps, hero SVG)
# ═══════════════════════════════════════════════════════════
def compress_image_bytes(
    img_bytes: bytes,
    max_width: int = 1400,
    quality: int = 88,
    force_jpeg: bool = True,
) -> bytes:
    """Compresse une image PNG/JPEG pour l'embed PDF sans perte visuelle notable.

    - Convertit RGBA → RGB (fond blanc pour les charts sombres, transparent → blanc).
      Note : les charts astrologiques ont un fond dark encodé DANS l'image ; le seul
      RGBA→RGB flatten ajoute un fond BLANC autour uniquement si l'image est semi-
      transparente, ce qui n'arrive pas pour nos SVG2PNG.
    - Redimensionne à `max_width` px si l'image est plus large (LANCZOS).
    - Sauvegarde en JPEG optimisé (quality=88 par défaut → ratio 40-100× vs PNG brut).

    Retourne les bytes compressés. En cas d'échec, retourne `img_bytes` intact
    (best-effort : jamais casser une génération de PDF).

    Réduction typique observée sur Plume Astrale :
      - Chart wheel natal 1600×1600 PNG : 15 Mo → 180 Ko (~85× moins lourd)
      - World map astrocarto 1600×1360 PNG : 8 Mo → 90 Ko (~90× moins lourd)
    """
    if not img_bytes:
        return img_bytes
    try:
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))

        # Flatten transparency sur fond blanc (JPEG ne supporte pas l'alpha)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            rgba = img.convert('RGBA')
            bg.paste(rgba, mask=rgba.split()[-1])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Redimensionne si l'image excède max_width
        if img.width > max_width:
            new_h = int(img.height * max_width / img.width)
            img = img.resize((max_width, new_h), Image.LANCZOS)

        out = BytesIO()
        if force_jpeg:
            img.save(out, format='JPEG', quality=quality, optimize=True, progressive=True)
        else:
            img.save(out, format='PNG', optimize=True, compress_level=9)
        result = out.getvalue()
        if len(result) < len(img_bytes):
            return result
        return img_bytes
    except Exception as e:
        logger.warning(f'[pdf_luxury_helpers] compress fail (returning original): {e}')
        return img_bytes


# ═══════════════════════════════════════════════════════════
#   ORNEMENTS DÉCORATIFS (FreeSerif via police "Symbol")
# ═══════════════════════════════════════════════════════════
# Ces constantes doivent être utilisées à l'intérieur de Paragraphes ReportLab.
# Elles incluent le wrapping <font name="OrnamentSerif"> pour éviter le rendu en carré vide.
# Prérequis : pdf_theme.register_fonts() doit avoir été appelé (idempotent, s'auto-
# initialise dans make_styles()).
ORN_STAR      = '<font name="OrnamentSerif">✦</font>'
ORN_STAR_HOLLOW = '<font name="OrnamentSerif">✧</font>'
ORN_DIAMOND   = '<font name="OrnamentSerif">◆</font>'
ORN_FLEUR     = '<font name="OrnamentSerif">⚜</font>'
ORN_HDIVIDER  = '<font name="OrnamentSerif">─</font>'
ORN_LEAF      = '<font name="OrnamentSerif">❖</font>'
ORN_SPARK     = '<font name="OrnamentSerif">✷</font>'


# Map char → wrap-html. Utilisé par sanitize_ornaments pour transformer
# automatiquement le texte source ("✦ Titre ✦") en HTML valide.
_ORNAMENT_CHARS = {
    '✦': ORN_STAR,
    '✧': ORN_STAR_HOLLOW,
    '✤': '<font name="OrnamentSerif">✤</font>',
    '★': '<font name="OrnamentSerif">★</font>',
    '◆': ORN_DIAMOND,
    '◇': '<font name="OrnamentSerif">◇</font>',
    '⚜': ORN_FLEUR,
    '❖': ORN_LEAF,
    '✷': ORN_SPARK,
    '─': ORN_HDIVIDER,
}


def sanitize_ornaments(text: str) -> str:
    """Remplace les glyphes ornementaux par leur wrap Symbol dans un texte HTML.

    Sans effet si les glyphes ne sont pas présents. Idempotent : ne double-wrappe
    pas un glyphe déjà entouré de `<font name="OrnamentSerif">` (heuristique simple).

    Usage :
        Paragraph(sanitize_ornaments("✦ Ton empreinte ✦"), style)

    → produit un rendu net (étoile dorée) au lieu d'un carré vide.
    """
    if not text:
        return text
    # Détecte si déjà wrappé : on saute pour éviter les doubles
    if '<font name="OrnamentSerif">' in text:
        return text
    out = text
    for ch, replacement in _ORNAMENT_CHARS.items():
        if ch in out:
            out = out.replace(ch, replacement)
    return out


def orn(glyph: str = '✦') -> str:
    """Retourne un glyphe unique wrappé en `<font name="OrnamentSerif">` prêt à insérer."""
    return f'<font name="OrnamentSerif">{glyph}</font>'


# ═══════════════════════════════════════════════════════════
#   CMYK PRINT-READY — BleedBox / TrimBox (post-processing)
# ═══════════════════════════════════════════════════════════
def add_print_boxes(pdf_bytes: bytes, bleed_mm: float = 3.0) -> bytes:
    """Ajoute les boîtes BleedBox et TrimBox à chaque page d'un PDF existant.

    Les imprimeurs professionnels exigent trois boîtes distinctes :
      - MediaBox  : le format physique de la page (papier réel, avec fond perdu)
      - BleedBox  : la zone jusqu'où le fond perdu se prolonge (MediaBox par défaut)
      - TrimBox   : la zone finale après rognage (MediaBox - bleed_mm de chaque côté)

    Sans ces boîtes, l'imprimeur ne sait pas où couper — il refuse le fichier
    ou coupe à l'aveugle. Cette fonction post-traite un PDF ReportLab standard
    (généré en A4 216x297 mm) et ajoute :
      - BleedBox = MediaBox (le fond perdu est déjà dans le design Nocturne)
      - TrimBox  = MediaBox rétrécie de `bleed_mm` mm de chaque côté

    Best-effort : si pypdf échoue, retourne le PDF original intact.

    Note : ReportLab ne sait pas embed un profil ICC CMYK — le PDF reste RGB.
    Une conversion RGB→CMYK vraie doit être faite par l'imprimeur (Ghostscript
    ou Photoshop). Mais BleedBox/TrimBox suffisent pour le workflow print.
    """
    if not pdf_bytes or not pdf_bytes.startswith(b'%PDF-'):
        return pdf_bytes
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import RectangleObject
        from io import BytesIO
        reader = PdfReader(BytesIO(pdf_bytes))
        writer = PdfWriter()

        # 1 mm = 2.834645669 points
        bleed_pts = bleed_mm * 2.834645669

        for page in reader.pages:
            # MediaBox est déjà présente
            media = page.mediabox
            left, bottom, right, top = float(media.left), float(media.bottom), float(media.right), float(media.top)
            # BleedBox = MediaBox (aucun ajout, notre design va jusqu'au bord)
            page.bleedbox = RectangleObject((left, bottom, right, top))
            # TrimBox = MediaBox - bleed_mm de chaque côté
            page.trimbox = RectangleObject((
                left + bleed_pts, bottom + bleed_pts,
                right - bleed_pts, top - bleed_pts,
            ))
            # ArtBox = TrimBox (contenu visible identique)
            page.artbox = page.trimbox
            writer.add_page(page)

        # Metadata print-ready
        writer.add_metadata({
            '/Producer': 'Plume Astrale · Nocturne print-ready',
            '/Trapped': '/False',
        })

        out = BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception as e:
        logger.warning(f'[pdf_luxury_helpers] add_print_boxes failed (returning original): {e}')
        return pdf_bytes
