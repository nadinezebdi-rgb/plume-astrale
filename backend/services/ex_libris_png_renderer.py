"""ex_libris_png_renderer — Rend la page « Ex Libris · Signature astrale » en PNG.

Variante offerte : l'acheteur·se d'un Thème Natal peut télécharger sa page Ex
Libris sous forme de carte PNG partageable (iMessage, WhatsApp, impression A5).

Design :
- A5 portrait, 1200×1700 (ratio proche de 148×210 mm à ~200 dpi).
- Fond parchemin crème avec watermark discret issu de la bibliothèque Plume.
- Cadre pointillé or (identique à la page découpable du PDF).
- Pictogramme ciseaux hors cadre « à découper · à offrir · à conserver ».
- Titre « Ex Libris · Signature astrale de {prenom} » (serif Cormorant).
- Filet or sous le titre, puis le paragraphe GPT (111-140 mots), justifié.
- Signature « — Plume Astrale, écrit pour toi » (italique or, centrée).

Zero appel réseau : la fonction attend le texte GPT en entrée.
"""
from __future__ import annotations
import html
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = ROOT / 'assets' / 'book' / 'fonts'
# L'image décorative vient du front-end public (bibliothèque Plume).
LIBRARY_BG = ROOT.parent / 'frontend' / 'public' / 'images' / 'astrale' / 'image-astrale-7.jpg'

# Dimensions (ratio A5 portrait, ~200 dpi).
WIDTH, HEIGHT = 1200, 1700
# Palette alignée sur le PDF (NAVY/INK/GOLD/MUTED).
PARCHMENT = (248, 240, 224)
GOLD = (167, 129, 64)
INK = (36, 48, 71)
MUTED = (82, 96, 119)
CREAM = (246, 234, 210)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS_DIR / f'CormorantGaramond-{name}.ttf'
    if not path.is_file():
        raise RuntimeError(f'Police introuvable : {path.name}')
    return ImageFont.truetype(str(path), size)


_SYMBOL_V1_CODEPOINTS = {
    0x263D,  # ☽ Lune (First Quarter Moon)
    0x263E,  # ☾ Last Quarter Moon
    0x2191,  # ↑ Flèche vers le haut
    0x2192, 0x2193, 0x2190,
    0x2605,  # ★ étoile pleine
}
# Tous les autres glyphes (☉, ✁, ✦, …) vont dans Symbols-2 qui offre un design
# plus détaillé et harmonieux avec la palette Plume Astrale.


def _symbol_font(size: int, codepoint: str = '') -> ImageFont.FreeTypeFont:
    """Police dédiée aux glyphes Unicode (ciseaux, soleil, lune, flèche…).

    Cormorant Garamond ne contient pas les symboles astrologiques, ils
    s'affichaient comme des rectangles vides (tofu). Les deux fichiers Noto
    Sans Symbols sont **complémentaires** (pas superposés) : chaque glyphe
    n'existe que dans l'un des deux. On route explicitement.
    """
    code = ord(codepoint[0]) if codepoint else 0
    use_v1 = code in _SYMBOL_V1_CODEPOINTS
    fname = 'NotoSansSymbols-Regular.ttf' if use_v1 else 'NotoSansSymbols2-Regular.ttf'
    path = FONTS_DIR / fname
    if not path.is_file():
        other = FONTS_DIR / (
            'NotoSansSymbols2-Regular.ttf' if use_v1 else 'NotoSansSymbols-Regular.ttf'
        )
        path = other if other.is_file() else path
    if not path.is_file():
        raise RuntimeError(f'Police symboles introuvable : {path.name}')
    return ImageFont.truetype(str(path), size)


def _plain(text: str) -> str:
    """Nettoie le HTML éventuel (<b>, <i>, <br/>) pour obtenir du texte pur."""
    s = (text or '').replace('<br/>', '\n').replace('<br>', '\n')
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Enroule le texte à la largeur max en pixels, respectant les mots."""
    lines: list[str] = []
    for paragraph in text.split('\n'):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append('')
            continue
        words = paragraph.split()
        current = ''
        for word in words:
            trial = f'{current} {word}'.strip()
            w = font.getbbox(trial)[2]
            if w <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def _draw_dashed_rect(draw: ImageDraw.ImageDraw, box: tuple, color: tuple,
                       width: int = 3, dash: int = 10, gap: int = 10) -> None:
    """Dessine un rectangle à bordure pointillée (PIL n'a pas de support natif)."""
    x1, y1, x2, y2 = box
    # haut + bas
    for y in (y1, y2):
        x = x1
        while x < x2:
            x_end = min(x + dash, x2)
            draw.line([(x, y), (x_end, y)], fill=color, width=width)
            x += dash + gap
    # gauche + droit
    for x in (x1, x2):
        y = y1
        while y < y2:
            y_end = min(y + dash, y2)
            draw.line([(x, y), (x, y_end)], fill=color, width=width)
            y += dash + gap


def _blend_watermark(bg: Image.Image, library_path: Path, alpha: float = 0.08) -> None:
    """Superpose discrètement une image bibliothèque, découpée en ovale fondu,
    positionnée en bas de carte pour servir de frontispice floral.
    """
    if not library_path.is_file():
        return
    wm = Image.open(library_path).convert('RGB')
    target_w = int(WIDTH * 0.62)
    ratio = target_w / wm.width
    wm = wm.resize((target_w, int(wm.height * ratio)), Image.LANCZOS)
    # Désature pour un ton parchemin cohérent avec la palette crème.
    wm = wm.convert('L').convert('RGB')
    # Masque ovale avec dégradé radial doux (évite le carré visible).
    mask = Image.new('L', wm.size, 0)
    md = ImageDraw.Draw(mask)
    cx, cy = wm.width // 2, wm.height // 2
    # Dégradé : plusieurs ellipses concentriques d'alpha croissant vers le centre.
    steps = 12
    for i in range(steps, 0, -1):
        r_x = int(wm.width * 0.48 * i / steps)
        r_y = int(wm.height * 0.48 * i / steps)
        a = int(255 * alpha * (1 - (i / steps) ** 2) * 2)
        md.ellipse([cx - r_x, cy - r_y, cx + r_x, cy + r_y], fill=a)
    pos = ((WIDTH - wm.width) // 2, int(HEIGHT * 0.66) - wm.height // 2)
    bg.paste(wm, pos, mask)


def render_ex_libris_png(
    *,
    prenom: str,
    ex_libris_text: str,
    sun_sign: str = '',
    moon_sign: str = '',
    asc_sign: str = '',
) -> bytes:
    """Rend la carte Ex Libris en PNG (bytes).

    Args:
        prenom : prénom affiché dans le titre.
        ex_libris_text : paragraphe GPT condensé (110-140 mots). Peut contenir
            un peu de HTML (<b>, <i>, <br/>) qui est nettoyé.
        sun_sign / moon_sign / asc_sign : triade affichée en kicker sous le titre.

    Returns :
        bytes PNG RGB prêt à envoyer en réponse HTTP.
    """
    prenom = (prenom or 'Voyageuse').strip() or 'Voyageuse'
    body = _plain(ex_libris_text) or (
        f'Signature astrale de {prenom}. Un paragraphe singulier à venir — '
        'régénérez votre thème natal pour composer votre empreinte.'
    )

    img = Image.new('RGB', (WIDTH, HEIGHT), PARCHMENT)
    # Petit halo plus clair en haut-centre pour la profondeur
    overlay = Image.new('RGB', (WIDTH, HEIGHT), CREAM)
    mask = Image.new('L', (WIDTH, HEIGHT), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-100, -400, WIDTH + 100, 900], fill=70)
    img.paste(overlay, (0, 0), mask)
    _blend_watermark(img, LIBRARY_BG, alpha=0.08)

    draw = ImageDraw.Draw(img)

    # Cadre pointillé or (marge 90 px)
    margin = 90
    _draw_dashed_rect(draw, (margin, margin, WIDTH - margin, HEIGHT - margin),
                      GOLD, width=3, dash=12, gap=10)

    # Pictogramme ciseaux + libellé discret, hors cadre, en haut-gauche
    tip_font = _font('Italic', 22)
    scissors_glyph = '\u2701'
    tip_sym = _symbol_font(22, scissors_glyph)
    sym_w = tip_sym.getbbox(scissors_glyph)[2]
    draw.text((margin + 6, margin - 42), scissors_glyph, fill=MUTED, font=tip_sym)
    draw.text((margin + 6 + sym_w + 10, margin - 42),
              'à découper · à offrir · à conserver',
              fill=MUTED, font=tip_font)

    # ─── Titre centré ────────────────────────────────────────────
    title_font = _font('SemiBold', 56)
    kicker_font = _font('Italic', 28)
    body_font = _font('Regular', 32)
    sig_font = _font('Italic', 26)
    _font('Regular', 20)

    title_main = 'Ex Libris'
    title_sub = f'Signature astrale de {prenom}'
    # Position titre
    y = margin + 120
    tm_w = title_font.getbbox(title_main)[2]
    draw.text(((WIDTH - tm_w) // 2, y), title_main, fill=INK, font=title_font)
    y += 78
    sub_w = kicker_font.getbbox(title_sub)[2]
    draw.text(((WIDTH - sub_w) // 2, y), title_sub, fill=MUTED, font=kicker_font)
    y += 60

    # Filet or sous le titre
    hr_w = 220
    hr_y = y + 10
    draw.line([((WIDTH - hr_w) // 2, hr_y), ((WIDTH + hr_w) // 2, hr_y)],
              fill=GOLD, width=2)
    y = hr_y + 44

    # Trio Soleil · Lune · Ascendant (si fourni) — glyphes rendus avec la police
    # symbole, texte avec la police italique pour un rendu cohérent.
    trio_items: list[tuple[str, str]] = []
    if sun_sign:
        trio_items.append(('\u2609', f'Soleil {sun_sign}'))
    if moon_sign:
        trio_items.append(('\u263D', f'Lune {moon_sign}'))
    if asc_sign:
        trio_items.append(('\u2191', f'Ascendant {asc_sign}'))
    if trio_items:
        trio_txt = _font('Italic', 22)
        sep = '   ·   '
        sep_w = trio_txt.getbbox(sep)[2]
        # Mesure totale (chaque glyphe utilise son propre fichier de police)
        total_w = 0
        parts_sized: list[tuple[str, int, str, int, ImageFont.FreeTypeFont]] = []
        for i, (glyph, label) in enumerate(trio_items):
            trio_sym_i = _symbol_font(22, glyph)
            gw = trio_sym_i.getbbox(glyph)[2]
            lw = trio_txt.getbbox('  ' + label)[2]
            total_w += gw + lw
            parts_sized.append((glyph, gw, '  ' + label, lw, trio_sym_i))
            if i < len(trio_items) - 1:
                total_w += sep_w
        cursor_x = (WIDTH - total_w) // 2
        for i, (glyph, gw, label, lw, trio_sym_i) in enumerate(parts_sized):
            draw.text((cursor_x, y), glyph, fill=GOLD, font=trio_sym_i)
            cursor_x += gw
            draw.text((cursor_x, y), label, fill=GOLD, font=trio_txt)
            cursor_x += lw
            if i < len(parts_sized) - 1:
                draw.text((cursor_x, y), sep, fill=GOLD, font=trio_txt)
                cursor_x += sep_w
        y += 56

    # ─── Corps : paragraphe GPT justifié (approximation) ─────────
    body_max_w = WIDTH - 2 * (margin + 60)
    lines = _wrap_text(body, body_font, body_max_w)
    line_h = 50
    for line in lines:
        if not line:
            y += line_h // 2
            continue
        lw = body_font.getbbox(line)[2]
        draw.text(((WIDTH - lw) // 2, y), line, fill=INK, font=body_font)
        y += line_h

    # ─── Signature en bas ────────────────────────────────────────
    sig = '— Plume Astrale, écrit pour toi'
    sw = sig_font.getbbox(sig)[2]
    draw.text(((WIDTH - sw) // 2, HEIGHT - margin - 80),
              sig, fill=GOLD, font=sig_font)

    # Petit URL d'invitation en pied, hors cadre
    foot_font = _font('Italic', 18)
    foot = 'plume-astrale.com'
    fw = foot_font.getbbox(foot)[2]
    draw.text(((WIDTH - fw) // 2, HEIGHT - margin + 20),
              foot, fill=MUTED, font=foot_font)

    out = io.BytesIO()
    img.save(out, format='PNG', optimize=True)
    return out.getvalue()
