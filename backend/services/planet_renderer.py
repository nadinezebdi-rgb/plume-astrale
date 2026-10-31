"""planet_renderer — Génère une planète 3D "nuit étoilée + or" en PIL.

Lot 2 du refactor PDF Thème Natal (demande user 2026-02-28) :
Couverture avec une planète 3D personnalisée selon le signe solaire du
destinataire (via sa planète maîtresse). Rendu purement local (PIL),
sans appel IA, 100 % déterministe.
"""
from __future__ import annotations

import hashlib
import io
import random
from typing import Dict, Tuple

from PIL import Image, ImageDraw, ImageFilter


SIGN_TO_RULER: Dict[str, str] = {
    'Bélier': 'Mars', 'Taureau': 'Vénus', 'Gémeaux': 'Mercure',
    'Cancer': 'Lune', 'Lion': 'Soleil', 'Vierge': 'Mercure',
    'Balance': 'Vénus', 'Scorpion': 'Pluton', 'Sagittaire': 'Jupiter',
    'Capricorne': 'Saturne', 'Verseau': 'Uranus', 'Poissons': 'Neptune',
}

PLANET_PALETTES: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    'Soleil':  {'base': (212, 175,  55), 'hl': (255, 238, 176), 'sh': ( 86,  62,   0), 'rim': (255, 220, 120)},
    'Lune':    {'base': (216, 220, 230), 'hl': (255, 255, 255), 'sh': ( 70,  78,  96), 'rim': (240, 240, 250)},
    'Mercure': {'base': (176, 176, 184), 'hl': (240, 240, 250), 'sh': ( 58,  58,  70), 'rim': (210, 210, 220)},
    'Vénus':   {'base': (120, 180, 142), 'hl': (205, 240, 212), 'sh': ( 24,  70,  48), 'rim': (170, 220, 185)},
    'Mars':    {'base': (178,  70,  50), 'hl': (255, 176, 128), 'sh': ( 76,  12,   8), 'rim': (220, 130,  90)},
    'Jupiter': {'base': (142,  91, 199), 'hl': (212, 184, 240), 'sh': ( 48,  22,  80), 'rim': (190, 150, 230)},
    'Saturne': {'base': (201, 160,  80), 'hl': (245, 221, 159), 'sh': ( 88,  60,  22), 'rim': (230, 196, 128)},
    'Uranus':  {'base': (127, 200, 212), 'hl': (213, 240, 245), 'sh': ( 22,  74,  86), 'rim': (190, 230, 240)},
    'Neptune': {'base': ( 46, 106, 168), 'hl': (128, 176, 224), 'sh': (  8,  22,  68), 'rim': (120, 180, 220)},
    'Pluton':  {'base': (109,  60, 128), 'hl': (164, 114, 176), 'sh': ( 20,   6,  28), 'rim': (150, 100, 170)},
}


# ═══════════════════════════════════════════════════════════════════
# ÉDITION SAISONNIÈRE (Lot 5 — Feb 2026)
# Teinte le fond "ciel nuit" de la planète selon la saison de naissance,
# pour créer un effet "collection" : hiver bleu nuit, printemps vert tendre,
# été ambré, automne cuivré. L'hémisphère référent est le Nord (France).
# ═══════════════════════════════════════════════════════════════════

SEASON_LABELS_FR: Dict[str, str] = {
    'hiver': 'Hiver', 'printemps': 'Printemps', 'ete': 'Été', 'automne': 'Automne',
}

SEASON_SKY: Dict[str, Tuple[int, int, int]] = {
    # Ciel de fond RGB — tons profonds pour rester lisible derrière les étoiles.
    'hiver':    ( 10,  16,  38),  # bleu nuit profond (défaut historique)
    'printemps': ( 20,  34,  44),  # vert d'eau nocturne
    'ete':      ( 34,  22,  12),  # ambré/brun chaud
    'automne':  ( 42,  22,  14),  # cuivré profond
}

SEASON_STAR_WARMTH: Dict[str, float] = {
    # Proportion d'étoiles "chaudes" (dorées) vs "froides" (blanches).
    'hiver':    0.12,
    'printemps': 0.20,
    'ete':      0.40,
    'automne':  0.55,
}


def month_to_season(month: int) -> str:
    """Mappe un mois (1-12, hémisphère Nord) à sa saison astronomique.

    Approximation calendaire simple : les équinoxes/solstices sont
    arrondis au premier du mois concerné. Suffisant pour l'effet édition.
    """
    if month in (12, 1, 2):
        return 'hiver'
    if month in (3, 4, 5):
        return 'printemps'
    if month in (6, 7, 8):
        return 'ete'
    return 'automne'


def _add_starfield(img: Image.Image, rng: random.Random, density: int = 180,
                   warmth: float = 0.15) -> None:
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(density):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        size = rng.choice([1, 1, 1, 2, 2, 3])
        brightness = rng.randint(140, 255)
        if rng.random() < warmth:
            c = (brightness, int(brightness * 0.82), int(brightness * 0.4), 255)
        else:
            c = (brightness, brightness, brightness, 255)
        draw.ellipse((x - size, y - size, x + size, y + size), fill=c)


def _render_sphere_layer(size: int, radius: int, cx: int, cy: int,
                         palette: Dict[str, Tuple[int, int, int]]) -> Image.Image:
    """Construit une sphère 3D complète dans une couche RGBA (fond transparent).

    Composition :
      1. Dégradé radial base→shadow (lumière venant du haut-droite)
      2. Highlight spéculaire haut-droite
      3. Rim light en arc sur l'hémisphère éclairé
    Toute la couche finale est clippée au disque de la sphère.
    """
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # 1) Dégradé radial : construit en superposant des disques concentriques
    #    décalés vers le point d'ombre (bas-gauche).
    base_c = palette['base']
    shadow_c = palette['sh']
    g = ImageDraw.Draw(layer)
    steps = 80
    for i in range(steps, 0, -1):
        t = i / steps
        # Chaque disque se décale vers l'ombre à mesure qu'il rétrécit
        off = int((1 - t) * radius * 0.35)
        r = int(radius * t)
        mix = (1 - t) ** 1.5
        c = tuple(int(base_c[k] * (1 - mix) + shadow_c[k] * mix) for k in range(3)) + (255,)
        g.ellipse((cx - off - r, cy + off - r, cx - off + r, cy + off + r), fill=c)

    # 2) Highlight spéculaire — ellipse brillante unique fortement floutée
    hl_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    hld = ImageDraw.Draw(hl_layer)
    hx = cx + int(radius * 0.32)
    hy = cy - int(radius * 0.38)
    hr = int(radius * 0.40)
    hld.ellipse((hx - hr, hy - hr, hx + hr, hy + hr),
                fill=(*palette['hl'], 170))
    # Second petit point très lumineux au centre du highlight
    hr2 = int(radius * 0.16)
    hld.ellipse((hx - hr2, hy - hr2, hx + hr2, hy + hr2),
                fill=(*palette['hl'], 230))
    hl_layer = hl_layer.filter(ImageFilter.GaussianBlur(max(6.0, radius * 0.09)))
    layer.alpha_composite(hl_layer)

    # 3) Rim light — dessiné comme un trait fin sur une couche séparée,
    #    masqué pour ne garder que l'hémisphère éclairé (haut-droite).
    rim_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rimd = ImageDraw.Draw(rim_layer)
    rim_width = max(2, int(radius * 0.025))
    rimd.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                 outline=(*palette['rim'], 230), width=rim_width)
    # Masque hémisphérique haut-droite (pie slice ouvert de -80° à +50°)
    rim_mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(rim_mask).pieslice(
        (cx - radius - 2, cy - radius - 2, cx + radius + 2, cy + radius + 2),
        start=-80, end=50, fill=255,
    )
    # Flou pour un rim light doux
    rim_mask = rim_mask.filter(ImageFilter.GaussianBlur(2))
    rim_only = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rim_only.paste(rim_layer, (0, 0), rim_mask)
    layer.alpha_composite(rim_only)

    # 4) Clipping final : ne garder que le disque de la sphère
    sphere_mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(sphere_mask).ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius), fill=255,
    )
    clipped = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    clipped.paste(layer, (0, 0), sphere_mask)
    return clipped


def _draw_saturn_rings(base_img: Image.Image,
                       cx: int, cy: int, radius: int,
                       palette: Dict[str, Tuple[int, int, int]],
                       which: str) -> None:
    """Dessine les anneaux de Saturne (demi-arc arrière ou avant)."""
    size = base_img.size[0]
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    start, end = (180, 360) if which == 'back' else (0, 180)
    # Ellipse plate type Saturn (ry ≈ 0.14*radius → forte perspective)
    for w_mult, alpha in [(1.00, 200), (1.14, 130), (1.26, 70), (1.38, 40)]:
        rx = int(radius * 2.0 * w_mult)
        ry = int(radius * 0.14 * w_mult)
        draw.arc((cx - rx, cy - ry, cx + rx, cy + ry),
                 start=start, end=end,
                 fill=(*palette['rim'], alpha),
                 width=max(2, int(radius * 0.020)))
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    base_img.alpha_composite(layer)


def _draw_sun_halo(base_img: Image.Image, cx: int, cy: int, radius: int) -> None:
    size = base_img.size[0]
    halo = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(halo)
    for i in range(1, 30):
        alpha = int(50 * (1 - i / 30) ** 2)
        rr = radius + i * int(size * 0.004)
        hdraw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                      outline=(255, 220, 120, alpha), width=2)
    halo = halo.filter(ImageFilter.GaussianBlur(size * 0.005))
    base_img.alpha_composite(halo)


def generate_planet_png(sun_sign: str, size: int = 1200,
                        with_rings: bool = None,
                        birth_month: int = None) -> bytes:
    """Génère la planète maîtresse du signe solaire au format PNG.

    Si `birth_month` est fourni (1-12), le fond "ciel nuit" est teinté selon
    la saison correspondante (hiver bleu, printemps vert, été ambré, automne
    cuivré) pour l'effet « édition saisonnière » / collection.
    """
    ruler = SIGN_TO_RULER.get(sun_sign, 'Soleil')
    palette = PLANET_PALETTES[ruler]
    if with_rings is None:
        with_rings = (ruler == 'Saturne')

    # Fond + chaleur des étoiles selon la saison (défaut hiver = historique).
    season = month_to_season(birth_month) if birth_month else 'hiver'
    sky_rgb = SEASON_SKY[season]
    star_warmth = SEASON_STAR_WARMTH[season]

    # Seed déterministe inclut la saison → signatures distinctes par édition.
    # hashlib (et non hash()) : hash() varie à chaque redémarrage du process
    # (PYTHONHASHSEED), ce qui rendait la couverture non reproductible.
    _seed = int.from_bytes(hashlib.sha256(f'{ruler}|{season}'.encode('utf-8')).digest()[:4], 'big')
    rng = random.Random(_seed)
    img = Image.new('RGBA', (size, size), (*sky_rgb, 255))
    _add_starfield(img, rng, density=max(80, size // 7), warmth=star_warmth)

    cx, cy = size // 2, size // 2
    radius = int(size * 0.36)

    # Halo doré pour le Soleil (sous la sphère)
    if ruler == 'Soleil':
        _draw_sun_halo(img, cx, cy, radius)

    # Anneaux arrière de Saturne (avant la sphère car doivent être dessinés
    # avant pour que la sphère les recouvre au premier plan)
    if with_rings:
        _draw_saturn_rings(img, cx, cy, radius, palette, 'back')

    # Sphère 3D
    sphere = _render_sphere_layer(size, radius, cx, cy, palette)
    img.alpha_composite(sphere)

    # Anneaux avant de Saturne (devant la sphère)
    if with_rings:
        _draw_saturn_rings(img, cx, cy, radius, palette, 'front')

    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return buf.getvalue()


__all__ = ['generate_planet_png', 'SIGN_TO_RULER', 'PLANET_PALETTES',
           'month_to_season', 'SEASON_LABELS_FR', 'SEASON_SKY']
