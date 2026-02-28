"""
Generateur de carte astrale partageable pour Instagram/WhatsApp
Cree une image PNG 1080x1350 (ratio 4:5 Instagram) avec le profil astrologique
"""
import io
import math
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).parent.parent / "assets"

SIGN_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

SIGNES_FR = {
    'Aries': 'Belier', 'Taurus': 'Taureau', 'Gemini': 'Gemeaux',
    'Cancer': 'Cancer', 'Leo': 'Lion', 'Virgo': 'Vierge',
    'Libra': 'Balance', 'Scorpio': 'Scorpion', 'Sagittarius': 'Sagittaire',
    'Capricorn': 'Capricorne', 'Aquarius': 'Verseau', 'Pisces': 'Poissons'
}

SIGNES_SYMBOLES = {
    'Aries': '\u2648', 'Taurus': '\u2649', 'Gemini': '\u264a',
    'Cancer': '\u264b', 'Leo': '\u264c', 'Virgo': '\u264d',
    'Libra': '\u264e', 'Scorpio': '\u264f', 'Sagittarius': '\u2650',
    'Capricorn': '\u2651', 'Aquarius': '\u2652', 'Pisces': '\u2653'
}

ELEMENTS = {
    "Aries": "Feu", "Taurus": "Terre", "Gemini": "Air", "Cancer": "Eau",
    "Leo": "Feu", "Virgo": "Terre", "Libra": "Air", "Scorpio": "Eau",
    "Sagittarius": "Feu", "Capricorn": "Terre", "Aquarius": "Air", "Pisces": "Eau"
}

# Colors
BG_DARK = (15, 5, 24)
BG_GRADIENT_TOP = (26, 11, 46)
GOLD = (197, 160, 89)
CREAM = (243, 229, 171)
LIGHT_TEXT = (224, 217, 246)
DIM_TEXT = (160, 150, 180)
FIRE = (232, 64, 64)
EARTH = (107, 175, 107)
AIR = (107, 181, 232)
WATER = (74, 120, 208)

ELEMENT_COLORS = {"Feu": FIRE, "Terre": EARTH, "Air": AIR, "Eau": WATER}


def _load_font(size, bold=False):
    """Load a system font with fallback"""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _load_serif_font(size, bold=False):
    """Load a serif font for headers"""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return _load_font(size, bold)


def _draw_stars(draw, width, height, count=80):
    """Draw decorative stars on background"""
    import random
    random.seed(42)
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(1, 2)
        alpha = random.randint(40, 120)
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 255, alpha))


def _draw_mini_chart(draw, cx, cy, radius, planets_data, sun_sign):
    """Draw a mini natal chart wheel"""
    # Outer circle
    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline=GOLD + (180,), width=2)
    # Inner circle
    r_inner = int(radius * 0.7)
    draw.ellipse([cx-r_inner, cy-r_inner, cx+r_inner, cy+r_inner], outline=GOLD + (100,), width=1)

    # Sign dividers and labels
    font_tiny = _load_font(12)
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = cx + r_inner * math.cos(angle)
        y1 = cy + r_inner * math.sin(angle)
        x2 = cx + radius * math.cos(angle)
        y2 = cy + radius * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=GOLD + (60,), width=1)

        # Sign abbreviations
        label_angle = math.radians(i * 30 + 15 - 90)
        lx = cx + (radius + r_inner) / 2 * math.cos(label_angle)
        ly = cy + (radius + r_inner) / 2 * math.sin(label_angle)
        sign = SIGN_ORDER[i]
        abbr = SIGNES_FR[sign][:3]
        color = CREAM + (255,) if sign == sun_sign else DIM_TEXT + (140,)
        draw.text((lx - 8, ly - 6), abbr, fill=color, font=font_tiny)

    # Planet dots
    if planets_data:
        planet_syms = {'Sun': 'S', 'Moon': 'L', 'Mercury': 'Me', 'Venus': 'Ve', 'Mars': 'Ma', 'Jupiter': 'Ju', 'Saturn': 'Sa'}
        r_planet = int(radius * 0.5)
        font_planet = _load_font(11, bold=True)
        placed = 0
        for p in planets_data:
            name = p.get('name', '')
            if name not in planet_syms:
                continue
            sign = p.get('sign', '')
            if sign not in SIGN_ORDER:
                continue
            idx = SIGN_ORDER.index(sign)
            deg = p.get('normDegree', p.get('norm_degree', 15))
            total_angle = math.radians(idx * 30 + deg - 90)
            offset = 8 * (placed % 3)
            px = cx + (r_planet - offset) * math.cos(total_angle)
            py = cy + (r_planet - offset) * math.sin(total_angle)
            draw.text((px - 5, py - 5), planet_syms[name], fill=CREAM + (220,), font=font_planet)
            placed += 1


def generate_share_card(user_data, planets_data=None, chemin_vie=1):
    """Generate a shareable astrological profile card (1080x1350 PNG)"""
    W, H = 1080, 1350
    img = Image.new('RGBA', (W, H), BG_DARK + (255,))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(H):
        ratio = y / H
        r = int(BG_GRADIENT_TOP[0] * (1 - ratio) + BG_DARK[0] * ratio)
        g = int(BG_GRADIENT_TOP[1] * (1 - ratio) + BG_DARK[1] * ratio)
        b = int(BG_GRADIENT_TOP[2] * (1 - ratio) + BG_DARK[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Stars
    _draw_stars(draw, W, H)

    # Border
    draw.rectangle([20, 20, W-20, H-20], outline=GOLD + (50,), width=1)
    draw.rectangle([30, 30, W-30, H-30], outline=GOLD + (30,), width=1)

    # Fonts
    font_title = _load_serif_font(52, bold=True)
    font_subtitle = _load_serif_font(28, bold=True)
    font_name = _load_serif_font(44, bold=True)
    font_label = _load_font(22, bold=True)
    font_value = _load_serif_font(32, bold=True)
    font_small = _load_font(18)
    font_tiny = _load_font(16)
    font_brand = _load_serif_font(24, bold=True)

    # Top branding
    y = 60
    draw.text((W//2, y), "PLUME ASTRALE", fill=GOLD + (255,), font=font_brand, anchor="mt")
    y += 40
    draw.line([(W//2 - 100, y), (W//2 + 100, y)], fill=GOLD + (100,), width=1)
    y += 20
    draw.text((W//2, y), "Votre Profil Astral", fill=DIM_TEXT + (200,), font=font_small, anchor="mt")

    # Name
    y += 55
    prenom = user_data.get('prenom', 'Voyageur Celeste')
    draw.text((W//2, y), prenom, fill=CREAM + (255,), font=font_name, anchor="mt")

    # Sun sign info
    sun_sign = ""
    moon_sign = ""
    asc_sign = ""
    if planets_data:
        sun = next((p for p in planets_data if p.get('name') == 'Sun'), None)
        moon = next((p for p in planets_data if p.get('name') == 'Moon'), None)
        asc = next((p for p in planets_data if p.get('name') == 'Ascendant'), None)
        if sun:
            sun_sign = sun.get('sign', '')
        if moon:
            moon_sign = moon.get('sign', '')
        if asc:
            asc_sign = asc.get('sign', '')

    # Separator
    y += 60
    draw.line([(100, y), (W-100, y)], fill=GOLD + (80,), width=1)

    # Mini natal chart
    y += 30
    chart_cy = y + 160
    _draw_mini_chart(draw, W//2, chart_cy, 150, planets_data, sun_sign)
    y = chart_cy + 175

    # Separator
    draw.line([(100, y), (W-100, y)], fill=GOLD + (80,), width=1)
    y += 35

    # Three columns: Sun, Moon, Ascendant
    col_w = (W - 120) // 3
    col_x = [60 + col_w * i + col_w // 2 for i in range(3)]

    items = [
        ("SOLEIL", sun_sign, (255, 200, 50)),
        ("LUNE", moon_sign, (200, 210, 255)),
        ("ASCENDANT", asc_sign, (255, 180, 120)),
    ]

    for i, (label, sign, color) in enumerate(items):
        x = col_x[i]
        draw.text((x, y), label, fill=GOLD + (200,), font=font_label, anchor="mt")
        sign_fr = SIGNES_FR.get(sign, '?')
        draw.text((x, y + 35), sign_fr, fill=color + (255,), font=font_value, anchor="mt")
        elem = ELEMENTS.get(sign, '')
        if elem:
            elem_color = ELEMENT_COLORS.get(elem, DIM_TEXT)
            draw.text((x, y + 75), f"Element {elem}", fill=elem_color + (180,), font=font_tiny, anchor="mt")

    y += 115

    # Separator
    draw.line([(100, y), (W-100, y)], fill=GOLD + (80,), width=1)
    y += 30

    # Life path
    draw.text((W//2, y), "CHEMIN DE VIE", fill=GOLD + (200,), font=font_label, anchor="mt")
    y += 35

    chemin_titles = {
        1: "Le Pionnier", 2: "Le Diplomate", 3: "L'Artiste",
        4: "Le Batisseur", 5: "L'Aventurier", 6: "Le Guerisseur",
        7: "Le Sage", 8: "Le Leader", 9: "L'Humanitaire",
        11: "L'Inspirateur", 22: "Le Maitre Batisseur", 33: "Le Guide Spirituel"
    }
    chemin_title = chemin_titles.get(chemin_vie, "Le Voyageur")

    # Big number
    font_big = _load_serif_font(72, bold=True)
    draw.text((W//2, y), str(chemin_vie), fill=CREAM + (255,), font=font_big, anchor="mt")
    y += 85
    draw.text((W//2, y), chemin_title, fill=GOLD + (255,), font=font_subtitle, anchor="mt")
    y += 50

    # Additional planet positions (compact)
    if planets_data:
        draw.line([(100, y), (W-100, y)], fill=GOLD + (80,), width=1)
        y += 25
        draw.text((W//2, y), "POSITIONS PLANETAIRES", fill=GOLD + (180,), font=font_label, anchor="mt")
        y += 35

        show_planets = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        names_fr = {'Mercury': 'Mercure', 'Venus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturne'}

        # Two rows of planets
        visible = [p for p in planets_data if p.get('name') in show_planets]
        cols = min(len(visible), 3)
        if visible:
            row1 = visible[:3]
            row2 = visible[3:]

            for row_planets in [row1, row2]:
                if not row_planets:
                    continue
                row_w = W - 120
                item_w = row_w // len(row_planets)
                for j, p in enumerate(row_planets):
                    px = 60 + item_w * j + item_w // 2
                    name = p.get('name', '')
                    sign = p.get('sign', '')
                    draw.text((px, y), names_fr.get(name, name), fill=DIM_TEXT + (220,), font=font_small, anchor="mt")
                    draw.text((px, y + 25), SIGNES_FR.get(sign, sign), fill=LIGHT_TEXT + (200,), font=font_label, anchor="mt")
                y += 60

    # Bottom branding
    y = H - 100
    draw.line([(150, y), (W-150, y)], fill=GOLD + (60,), width=1)
    y += 20
    draw.text((W//2, y), "plume-astrale.fr", fill=GOLD + (200,), font=font_subtitle, anchor="mt")
    y += 35
    draw.text((W//2, y), "Decouvre ton profil astral complet", fill=DIM_TEXT + (160,), font=font_small, anchor="mt")

    # Convert to RGB for JPEG/PNG output
    img_rgb = Image.new('RGB', (W, H), BG_DARK)
    img_rgb.paste(img, mask=img.split()[3])

    buffer = io.BytesIO()
    img_rgb.save(buffer, format='PNG', quality=90)
    buffer.seek(0)
    return buffer.getvalue()
