"""
Visuel d'apercu de la couverture Synastrie au format Instagram (1080x1080 PNG).

Utilise la meme image de fond (lunaire.png) que le PDF + voile sombre + branding dore.
Destine au partage sur Instagram (story / post carre).
"""
import io
import os
from typing import Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Palette identique au PDF
DEEP_PURPLE = (12, 9, 24)
GOLD = (212, 180, 106)
GOLD_LIGHT = (244, 217, 140)
CREAM = (245, 239, 224)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'synastrie_pdf')
COVER_BG_PATH = os.path.join(ASSETS_DIR, 'page-01.png')

# Fonts systeme
_FONT_SERIF = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
_FONT_SERIF_BOLD = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
_FONT_SERIF_ITALIC = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"

# Glyphs zodiaque (memes que PDF)
ZODIAC_GLYPHS = {
    "Bélier": "♈", "Taureau": "♉", "Gémeaux": "♊", "Cancer": "♋",
    "Lion": "♌", "Vierge": "♍", "Balance": "♎", "Scorpion": "♏",
    "Sagittaire": "♐", "Capricorne": "♑", "Verseau": "♒", "Poissons": "♓",
}


def _font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _center_text(draw, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((1080 - w) / 2, y), text, font=font, fill=fill)


def generate_instagram_card(prenom1: str, prenom2: str,
                            sign1: Optional[str] = None,
                            sign2: Optional[str] = None) -> bytes:
    """Genere une carte 1080x1080 PNG prete pour Instagram."""
    W, H = 1080, 1080
    canvas = Image.new('RGB', (W, H), DEEP_PURPLE)

    # 1) Background : lunaire.png si dispo, plein cadre crop center
    if os.path.exists(COVER_BG_PATH):
        try:
            bg = Image.open(COVER_BG_PATH).convert('RGB')
            # crop carre centre
            bw, bh = bg.size
            s = min(bw, bh)
            bg = bg.crop(((bw - s) // 2, (bh - s) // 2, (bw + s) // 2, (bh + s) // 2))
            bg = bg.resize((W, H), Image.LANCZOS)
            # Leger blur pour mettre le texte en valeur
            bg = bg.filter(ImageFilter.GaussianBlur(radius=1.2))
            canvas.paste(bg, (0, 0))
        except Exception:
            pass

    # 2) Voile sombre central (radial-ish) pour le contraste du texte
    veil = Image.new('RGBA', (W, H), (12, 9, 24, 0))
    vd = ImageDraw.Draw(veil)
    # Voile uniforme 55% sombre
    vd.rectangle([0, 0, W, H], fill=(12, 9, 24, 130))
    # Vignettage haut et bas
    for i in range(160):
        alpha = int(130 - i * 0.6)
        vd.rectangle([0, i, W, i + 1], fill=(12, 9, 24, max(alpha, 0)))
    for i in range(200):
        alpha = int(60 + i * 0.5)
        vd.rectangle([0, H - i, W, H - i + 1], fill=(12, 9, 24, min(alpha, 220)))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), veil).convert('RGB')

    draw = ImageDraw.Draw(canvas)

    # 3) Brand header
    y = 110
    f_brand = _font(_FONT_SERIF, 28)
    _center_text(draw, y, "✦  PLUME ASTRALE  ✦", f_brand, GOLD)
    y += 50

    # Filet dore
    line_w = 180
    draw.rectangle([(W - line_w) // 2, y, (W + line_w) // 2, y + 1], fill=GOLD)
    y += 60

    # 4) Zodiac glyphs
    f_zod = _font(_FONT_SERIF, 130)
    g1 = ZODIAC_GLYPHS.get(sign1 or "", "")
    g2 = ZODIAC_GLYPHS.get(sign2 or "", "")
    if g1 or g2:
        glyphs_text = f"{g1}      {g2}".strip()
        _center_text(draw, y, glyphs_text, f_zod, GOLD_LIGHT)
        y += 180

    # 5) Titre "Astrologie Relationnelle"
    f_title = _font(_FONT_SERIF_BOLD, 78)
    _center_text(draw, y, "Astrologie", f_title, CREAM)
    y += 90
    _center_text(draw, y, "Relationnelle", f_title, CREAM)
    y += 100

    # 6) Subtitle
    f_sub = _font(_FONT_SERIF_ITALIC, 40)
    _center_text(draw, y, "le rapport de votre lien", f_sub, GOLD_LIGHT)
    y += 100

    # 7) Filet dore mince
    draw.rectangle([(W - 100) // 2, y, (W + 100) // 2, y + 1], fill=GOLD)
    y += 40

    # 8) Noms
    p1 = (prenom1 or "").strip().title() or "L'un"
    p2 = (prenom2 or "").strip().title() or "L'autre"
    f_names = _font(_FONT_SERIF_BOLD, 70)
    f_amp = _font(_FONT_SERIF_ITALIC, 50)
    _center_text(draw, y, p1, f_names, GOLD)
    y += 80
    _center_text(draw, y, "&", f_amp, CREAM)
    y += 70
    _center_text(draw, y, p2, f_names, GOLD)

    # 9) Footer
    f_foot = _font(_FONT_SERIF_ITALIC, 22)
    _center_text(draw, H - 70, "plume-astrale.fr", f_foot, (200, 195, 215))

    buf = io.BytesIO()
    canvas.save(buf, format='PNG', optimize=True)
    buf.seek(0)
    return buf.getvalue()
