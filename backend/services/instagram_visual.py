"""Instagram visual generator — mini-visuel 1080x1350 (portrait 4:5).

Attaché à chaque envoi de rapport mensuel Cercle Soléna : chaque abonnée
reçoit une image partageable au format IG feed, avec la citation "accent"
personnalisée par son signe pour le mois en cours. Objectif : transformer
les abonnées en ambassadrices organiques (elles postent, on gagne en
visibilité sans dépenser en pub).

Composition (charte Plume Astrale) :
  • Fond bleu nuit (#0A1128) avec dégradé et étoiles semi-aléatoires
  • Croissant doré filigrane en fond
  • Kicker or : "L'humeur de {mois} · {sign}"
  • Citation centrale en Playfair italic (or #C9A24B)
  • Signature : "plume-astrale.fr"
"""
from __future__ import annotations
import logging
import random
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Charte
IG_WIDTH = 1080
IG_HEIGHT = 1350
NIGHT_BLUE = (10, 17, 40)
INK_BLUE = (15, 26, 60)
GOLD = (184, 147, 90)
GOLD_LIGHT = (201, 162, 75)
IVORY = (247, 245, 240)
IVORY_DIM = (215, 210, 195)

FONT_SERIF_ITALIC = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
FONT_SERIF_REGULAR = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
FONT_SANS_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FONT_SANS = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    words = text.split()
    lines, current = [], ''
    for w in words:
        test = f'{current} {w}'.strip()
        if font.getlength(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def _draw_starfield(draw: ImageDraw.ImageDraw, rng: random.Random, count: int = 80):
    for _ in range(count):
        x = rng.randint(0, IG_WIDTH)
        y = rng.randint(0, IG_HEIGHT)
        r = rng.uniform(0.6, 2.2)
        alpha = rng.randint(60, 210)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(*IVORY, alpha))


def _draw_gold_crescent(img: Image.Image):
    """Croissant doré filigrane en haut à droite (opacité douce)."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = int(IG_WIDTH * 0.82), int(IG_HEIGHT * 0.16), 180
    # Halo (concentrique)
    for i in range(6, 0, -1):
        d.ellipse(
            [cx - r * (1 + i * 0.15), cy - r * (1 + i * 0.15),
             cx + r * (1 + i * 0.15), cy + r * (1 + i * 0.15)],
            fill=(*GOLD, int(6 * i)),
        )
    # Corps de lune
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*IVORY, 90))
    # Ombre pour croissant
    off = int(r * 0.28)
    d.ellipse([cx - r + off, cy - r - 12, cx + r + off, cy + r - 12], fill=(*NIGHT_BLUE, 220))
    img.alpha_composite(layer)


def _draw_bottom_gradient(img: Image.Image):
    """Fondu vers le bleu profond en bas pour lisibilité de la signature."""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(400):
        y = IG_HEIGHT - 400 + i
        alpha = int(230 * (i / 400) ** 2)
        d.line([(0, y), (IG_WIDTH, y)], fill=(*NIGHT_BLUE, alpha))
    img.alpha_composite(layer)


def generate_ig_visual(sign_name: str, month_name: str, quote: str,
                       seed: int | None = None) -> bytes:
    """Génère un PNG 1080x1350 à partir du sign, mois et citation accent.
    Renvoie les bytes PNG."""
    rng = random.Random(seed or hash((sign_name, month_name)))

    img = Image.new('RGBA', (IG_WIDTH, IG_HEIGHT), (*NIGHT_BLUE, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Dégradé subtil de haut en bas (encre → nuit)
    for y in range(IG_HEIGHT):
        t = y / IG_HEIGHT
        r = int(NIGHT_BLUE[0] * (1 - t) + INK_BLUE[0] * t)
        g = int(NIGHT_BLUE[1] * (1 - t) + INK_BLUE[1] * t)
        b = int(NIGHT_BLUE[2] * (1 - t) + INK_BLUE[2] * t)
        if y % 3 == 0:  # sparse fill pour perf (visuel ~identique)
            draw.line([(0, y), (IG_WIDTH, y)], fill=(r, g, b, 255))

    # Étoiles + croissant doré
    _draw_starfield(draw, rng)
    _draw_gold_crescent(img)

    # Redraw sur le nouveau composite
    draw = ImageDraw.Draw(img, 'RGBA')

    # ─── Kicker : "L'HUMEUR DE {MOIS} · {SIGN}"
    kicker = f"L'HUMEUR DE {month_name.upper()}  ·  {sign_name.upper()}"
    kfont = _font(FONT_SANS_BOLD, 26)
    # Letter-spacing manuel
    letters = list(kicker)
    total_w = sum(kfont.getlength(l) for l in letters) + (len(letters) - 1) * 5
    x = (IG_WIDTH - total_w) / 2
    y = 200
    for l in letters:
        draw.text((x, y), l, font=kfont, fill=(*GOLD, 255))
        x += kfont.getlength(l) + 5

    # ─── Trait doré séparateur
    draw.line([(IG_WIDTH / 2 - 60, 260), (IG_WIDTH / 2 + 60, 260)], fill=(*GOLD, 200), width=1)

    # ─── Citation centrale (Playfair italic)
    qfont_size = 52
    qfont = _font(FONT_SERIF_ITALIC, qfont_size)
    max_line_w = IG_WIDTH - 180
    # Adapte la taille pour tenir en 5 lignes max
    while True:
        qfont = _font(FONT_SERIF_ITALIC, qfont_size)
        lines = _wrap(quote, qfont, max_line_w)
        if len(lines) <= 6 or qfont_size <= 34:
            break
        qfont_size -= 2

    line_h = qfont_size + 14
    total_h = len(lines) * line_h
    y = (IG_HEIGHT - total_h) / 2 - 40
    for line in lines:
        w = qfont.getlength(line)
        # Guillemets sur la 1re et dernière ligne uniquement (façon citation)
        if line is lines[0]:
            display = f'« {line}'
        elif line is lines[-1]:
            display = f'{line} »'
        else:
            display = line
        wd = qfont.getlength(display)
        draw.text(((IG_WIDTH - wd) / 2, y), display, font=qfont, fill=(*IVORY, 255))
        y += line_h

    # Gradient bas pour lisibilité signature
    _draw_bottom_gradient(img)

    # ─── Signature Playfair : "Plume Astrale"
    sfont = _font(FONT_SERIF_ITALIC, 42)
    signature = 'Plume Astrale'
    w = sfont.getlength(signature)
    draw.text(((IG_WIDTH - w) / 2, IG_HEIGHT - 200), signature, font=sfont, fill=(*GOLD_LIGHT, 255))

    # URL sous la signature
    ufont = _font(FONT_SANS, 22)
    url = 'plume-astrale.fr'
    w = ufont.getlength(url)
    letters = list(url)
    total_w = sum(ufont.getlength(l) for l in letters) + (len(letters) - 1) * 3
    x = (IG_WIDTH - total_w) / 2
    y = IG_HEIGHT - 145
    for l in letters:
        draw.text((x, y), l, font=ufont, fill=(*IVORY_DIM, 200))
        x += ufont.getlength(l) + 3

    # Petit trait doré en bas
    draw.line([(IG_WIDTH / 2 - 40, IG_HEIGHT - 100), (IG_WIDTH / 2 + 40, IG_HEIGHT - 100)],
              fill=(*GOLD, 180), width=1)

    # Export PNG bytes
    buf = BytesIO()
    img.convert('RGB').save(buf, format='PNG', optimize=True)
    return buf.getvalue()


def save_ig_visual(path: str | Path, sign_name: str, month_name: str, quote: str) -> Path:
    """Génère + écrit sur disque. Renvoie le Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(generate_ig_visual(sign_name, month_name, quote))
    return p
