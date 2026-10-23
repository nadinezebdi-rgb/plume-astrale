"""shared_tirage_png_renderer — Carte PNG partageable d'un tirage de tarot.

Permet aux utilisateurs de télécharger leur tirage sous forme d'une image
1080×1350 (format Instagram portrait 4:5, qui s'affiche aussi parfaitement
sur WhatsApp et en Story IG recadrée en 9:16).

Zero appel réseau : la fonction attend les données du tirage en entrée.
"""
from __future__ import annotations
import io
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = ROOT / 'assets' / 'book' / 'fonts'

# Dimensions : Instagram portrait 4:5 (1080×1350), aussi utilisable
# en Story 9:16 avec recadrage haut/bas automatique.
WIDTH, HEIGHT = 1080, 1350

# Palette alignée sur la charte Plume Astrale (navy + or).
NAVY = (15, 26, 60)         # #0F1A3C
NAVY_DEEP = (11, 20, 46)
GOLD = (201, 162, 75)       # #C9A24B
GOLD_SOFT = (184, 143, 63)
PARCHMENT = (248, 241, 227) # #F8F1E3
INK = (248, 241, 227)
MUTED = (184, 169, 232)     # #B8A9E8 — violet pour les cartes renversées

TYPE_LABELS = {
    'marseille': 'Tirage Marseille',
    'celtique': 'Croix Celtique',
    'complet': 'Tirage Complet · 78 arcanes',
}


# Symboles par arcane majeur (clé = nom tel qu'il arrive du deck).
# Fallback : ☉ (Soleil universel). Permet d'éviter que toutes les cartes
# majeures affichent le même glyphe par défaut.
_MAJOR_SYMBOLS = {
    'Le Mat': '✦',
    'Le Bateleur': '⚚',
    'La Papesse': '☽',
    "L'Impératrice": '♀',
    "L'Empereur": '♂',
    'Le Pape': '✝',
    "L'Amoureux": '♥',
    'Le Chariot': '✪',
    'La Justice': '⚖',
    "L'Hermite": '✧',
    'La Roue de Fortune': '☸',
    'La Force': '∞',
    'Le Pendu': '⌛',
    "La Mort": '☠',
    "L'Arcane sans Nom": '☠',
    'Tempérance': '♒',
    'Le Diable': '⚡',
    'La Maison Dieu': '⚡',
    'La Tour': '⚡',
    "L'Étoile": '✧',
    'La Lune': '☽',
    'Le Soleil': '☉',
    'Le Jugement': '✠',
    'Le Monde': '◉',
}


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS_DIR / f'CormorantGaramond-{name}.ttf'
    if path.is_file():
        return ImageFont.truetype(str(path), size)
    # Fallback : police PIL par défaut (ne devrait pas arriver)
    return ImageFont.load_default()


def _symbol_font(size: int) -> ImageFont.FreeTypeFont:
    """Police dédiée aux glyphes Unicode (☉, ☽, ✦, ♥, ◆, ✧...).

    NotoSansSymbols2 couvre ☉ U+2609 et la majorité des symboles ésotériques
    utilisés par le deck ; NotoSansSymbols couvre ☽ U+263D et ↑ U+2191.
    """
    path = FONTS_DIR / 'NotoSansSymbols2-Regular.ttf'
    if path.is_file():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


_SYMBOLS_V1_CODEPOINTS = {0x263D, 0x263E, 0x2191, 0x2192, 0x2193, 0x2190, 0x2605}


def _symbol_font_for_glyph(glyph: str, size: int) -> ImageFont.FreeTypeFont:
    """Choisit la bonne font Noto selon le codepoint du premier char."""
    if not glyph:
        return _symbol_font(size)
    cp = ord(glyph[0])
    noto1 = FONTS_DIR / 'NotoSansSymbols-Regular.ttf'
    noto2 = FONTS_DIR / 'NotoSansSymbols2-Regular.ttf'
    if cp in _SYMBOLS_V1_CODEPOINTS and noto1.is_file():
        return ImageFont.truetype(str(noto1), size)
    if noto2.is_file():
        return ImageFont.truetype(str(noto2), size)
    if noto1.is_file():
        return ImageFont.truetype(str(noto1), size)
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int,
               draw: ImageDraw.ImageDraw) -> list[str]:
    """Découpe `text` en lignes qui tiennent dans `max_width` pixels."""
    if not text:
        return []
    words = text.split()
    lines: list[str] = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_dotted_border(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                        color: tuple[int, int, int], step: int = 8, radius: int = 1):
    """Trace un rectangle en pointillés."""
    x1, y1, x2, y2 = box
    for x in range(x1, x2, step):
        draw.ellipse((x - radius, y1 - radius, x + radius, y1 + radius), fill=color)
        draw.ellipse((x - radius, y2 - radius, x + radius, y2 + radius), fill=color)
    for y in range(y1, y2, step):
        draw.ellipse((x1 - radius, y - radius, x1 + radius, y + radius), fill=color)
        draw.ellipse((x2 - radius, y - radius, x2 + radius, y + radius), fill=color)


def _draw_card_placeholder(img: Image.Image, draw: ImageDraw.ImageDraw,
                            carte: dict, x: int, y: int, w: int, h: int):
    """Dessine une représentation stylisée d'une carte (sans image réelle).

    Design : rectangle à bords arrondis, cadre or, symbole central + nom au-dessous.
    Les cartes mineures utilisent leur couleur de suite, les majeurs un fond navy.
    """
    is_minor = carte.get('is_major') is False
    is_reversed = (carte.get('orientation') or '').lower() == 'renverse'

    # Fond de carte
    if is_minor:
        # Couleur de suite légèrement dégradée vers crème
        bg = PARCHMENT
    else:
        bg = NAVY_DEEP

    # Rectangle arrondi (approximation)
    radius = 14
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=bg,
                            outline=GOLD, width=3)

    # Symbole central
    if is_minor:
        symbol = carte.get('symbole') or '✦'
    else:
        # Carte majeure : symbole spécifique si connu, sinon ☉ par défaut
        symbol = _MAJOR_SYMBOLS.get((carte.get('nom') or '').strip(), '☉')
    sym_font = _symbol_font_for_glyph(symbol, 72)
    sym_color = GOLD if not is_minor else GOLD  # Gold or sur navy + or doux sur crème
    bbox = draw.textbbox((0, 0), symbol, font=sym_font)
    sw, sh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - sw) // 2 - bbox[0], y + h // 3 - sh // 2 - bbox[1]),
              symbol, font=sym_font, fill=sym_color)

    # Nom de carte (sous le symbole)
    nom = (carte.get('nom') or '').strip()
    if nom:
        name_font = _font('Semibold' if (FONTS_DIR / 'CormorantGaramond-Semibold.ttf').is_file() else 'Bold', 22)
        text_color = GOLD if not is_minor else NAVY
        lines = _wrap_text(nom, name_font, w - 20, draw)
        line_y = y + int(h * 0.60)
        for ln in lines[:2]:
            bbox = draw.textbbox((0, 0), ln, font=name_font)
            lw = bbox[2] - bbox[0]
            draw.text((x + (w - lw) // 2 - bbox[0], line_y - bbox[1]),
                      ln, font=name_font, fill=text_color)
            line_y += (bbox[3] - bbox[1]) + 4

    # Indicateur orientation (petit pavé en bas) — contrast fort sur chaque fond
    label = 'Renversée' if is_reversed else 'Droite'
    if is_minor:
        # Fond crème → encre navy pour contraste max
        label_color = NAVY if not is_reversed else (90, 60, 140)
    else:
        # Fond navy → or pour droit, violet pâle pour renversé
        label_color = GOLD if not is_reversed else MUTED
    try:
        label_font = _font('Italic', 16)
    except Exception:
        label_font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=label_font)
    lw = bbox[2] - bbox[0]
    draw.text((x + (w - lw) // 2 - bbox[0], y + h - 32 - bbox[1]),
              label, font=label_font, fill=label_color)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    try:
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore
    except Exception:
        return GOLD


def render_shared_tirage_png(tirage: dict, share_url: str = '') -> bytes:
    """Génère un PNG 1080×1350 partageable depuis un tirage.

    `tirage` = structure stockée dans `shared_tirages` (type, question, domaine,
    first_name, data{cartes[], synthese{}, conseil_final}).
    """
    img = Image.new('RGB', (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(img)

    # ────────── Fond dégradé navy ──────────
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(NAVY[0] + (NAVY_DEEP[0] - NAVY[0]) * t)
        g = int(NAVY[1] + (NAVY_DEEP[1] - NAVY[1]) * t)
        b = int(NAVY[2] + (NAVY_DEEP[2] - NAVY[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # ────────── Cadre pointillé or ──────────
    _draw_dotted_border(draw, (40, 40, WIDTH - 40, HEIGHT - 40), GOLD, step=10, radius=2)

    # ────────── Header ──────────
    try:
        header_font = _font('Italic', 28)
        kicker_font = _font('Bold', 22)
    except Exception:
        header_font = kicker_font = ImageFont.load_default()
    sym_small_font = _symbol_font_for_glyph('✦', 22)

    # Header : symboles + mot "PLUME ASTRALE"
    label = 'PLUME ASTRALE'
    bbox_label = draw.textbbox((0, 0), label, font=kicker_font)
    lw = bbox_label[2] - bbox_label[0]
    bbox_sym = draw.textbbox((0, 0), '✦', font=sym_small_font)
    sw = bbox_sym[2] - bbox_sym[0]
    gap = 18
    total_w = sw + gap + lw + gap + sw
    start_x = (WIDTH - total_w) // 2
    y_header = 90
    draw.text((start_x - bbox_sym[0], y_header - bbox_sym[1]), '✦', font=sym_small_font, fill=GOLD)
    draw.text((start_x + sw + gap - bbox_label[0], y_header - bbox_label[1]),
              label, font=kicker_font, fill=GOLD)
    draw.text((start_x + sw + gap + lw + gap - bbox_sym[0], y_header - bbox_sym[1]),
              '✦', font=sym_small_font, fill=GOLD)

    tirage_type = (tirage.get('type') or 'marseille').lower()
    type_label = TYPE_LABELS.get(tirage_type, 'Tirage de Tarot')
    bbox = draw.textbbox((0, 0), type_label, font=header_font)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2 - bbox[0], 140 - bbox[1]), type_label,
              font=header_font, fill=PARCHMENT)

    # ────────── Titre principal ──────────
    try:
        title_font = _font('Bold', 68)
    except Exception:
        title_font = ImageFont.load_default()
    prenom = (tirage.get('first_name') or 'Voyageur').strip()
    title = f'Le tirage de {prenom}'
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    if tw > WIDTH - 100:
        # Si le prénom déborde, on tronque
        title = f'Le tirage de {prenom[:14]}'
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2 - bbox[0], 210 - bbox[1]), title, font=title_font, fill=INK)

    # Filet or sous le titre
    draw.rectangle((WIDTH // 2 - 60, 310, WIDTH // 2 + 60, 313), fill=GOLD)

    # ────────── Question ──────────
    try:
        q_font = _font('Italic', 26)
    except Exception:
        q_font = ImageFont.load_default()
    question = (tirage.get('question') or '').strip()
    if question:
        q_text = f'« {question} »'
        q_lines = _wrap_text(q_text, q_font, WIDTH - 180, draw)[:2]
        q_y = 340
        for ln in q_lines:
            bbox = draw.textbbox((0, 0), ln, font=q_font)
            lw = bbox[2] - bbox[0]
            draw.text(((WIDTH - lw) // 2 - bbox[0], q_y - bbox[1]),
                      ln, font=q_font, fill=PARCHMENT)
            q_y += 42

    # ────────── Cartes (3 max) ──────────
    cartes = (tirage.get('data') or {}).get('cartes') or []
    display_cartes = cartes[:3]
    if display_cartes:
        n = len(display_cartes)
        card_w, card_h = 220, 320
        gap = 28
        total_w = n * card_w + (n - 1) * gap
        start_x = (WIDTH - total_w) // 2
        card_y = 460
        for i, c in enumerate(display_cartes):
            x = start_x + i * (card_w + gap)
            # Position tag au-dessus
            pos = (c.get('position') or '').strip()
            if pos:
                try:
                    pos_font = _font('Bold', 16)
                except Exception:
                    pos_font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), pos.upper(), font=pos_font)
                lw = bbox[2] - bbox[0]
                draw.text((x + (card_w - lw) // 2 - bbox[0], card_y - 28 - bbox[1]),
                          pos.upper(), font=pos_font, fill=GOLD)
            _draw_card_placeholder(img, draw, c, x, card_y, card_w, card_h)

    # ────────── Teaser synthèse ──────────
    try:
        teaser_font = _font('Regular', 24)
    except Exception:
        teaser_font = ImageFont.load_default()
    synth = (tirage.get('data') or {}).get('synthese') or {}
    teaser = (synth.get('fil_conducteur') or
              (tirage.get('data') or {}).get('conseil_final') or '')
    teaser = teaser.strip().replace('\n', ' ')
    if teaser:
        # Max 220 chars pour tenir en ~4 lignes
        if len(teaser) > 220:
            teaser = teaser[:217].rsplit(' ', 1)[0] + '…'
        teaser_lines = _wrap_text(teaser, teaser_font, WIDTH - 180, draw)[:4]
        teaser_y = 830
        for ln in teaser_lines:
            bbox = draw.textbbox((0, 0), ln, font=teaser_font)
            lw = bbox[2] - bbox[0]
            draw.text(((WIDTH - lw) // 2 - bbox[0], teaser_y - bbox[1]),
                      ln, font=teaser_font, fill=PARCHMENT)
            teaser_y += 36

    # ────────── Footer / CTA ──────────
    # Filet or
    draw.rectangle((WIDTH // 2 - 100, HEIGHT - 230, WIDTH // 2 + 100, HEIGHT - 227), fill=GOLD)

    try:
        cta_font = _font('Italic', 24)
        cta_main = _font('Bold', 30)
        url_font = _font('Regular', 20)
    except Exception:
        cta_font = cta_main = url_font = ImageFont.load_default()

    cta1 = 'Et vous, qu\'est-ce que les arcanes vous diraient ?'
    bbox = draw.textbbox((0, 0), cta1, font=cta_font)
    lw = bbox[2] - bbox[0]
    draw.text(((WIDTH - lw) // 2 - bbox[0], HEIGHT - 195 - bbox[1]), cta1,
              font=cta_font, fill=PARCHMENT)

    cta2 = 'plume-astrale.fr'
    bbox = draw.textbbox((0, 0), cta2, font=cta_main)
    lw = bbox[2] - bbox[0]
    draw.text(((WIDTH - lw) // 2 - bbox[0], HEIGHT - 140 - bbox[1]), cta2,
              font=cta_main, fill=GOLD)

    if share_url:
        # URL courte (affiche jusqu'au short id)
        short = share_url.split('/tirage-partage/', 1)
        display_url = f'/tirage-partage/{short[1][:12]}' if len(short) == 2 else share_url[:40]
        bbox = draw.textbbox((0, 0), display_url, font=url_font)
        lw = bbox[2] - bbox[0]
        draw.text(((WIDTH - lw) // 2 - bbox[0], HEIGHT - 85 - bbox[1]),
                  display_url, font=url_font, fill=MUTED)

    # Export PNG optimisé
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    buf.seek(0)
    return buf.getvalue()
