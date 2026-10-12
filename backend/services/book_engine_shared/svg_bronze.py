"""svg_bronze — Reskin post-traitement d'une roue céleste SVG.

Prend un SVG produit par astrology-api.io (thème natal, moteur Kerykeion) et
remplace son ambiance sombre par la palette éditoriale Plume Astrale :

  - Fond : sombre → ivoire clair `#FBF7EE`
  - Traits (cercles, lignes de maisons, aspects) : bronze `#B8935A`
  - Glyphes planètes / signes : bronze `#A17840`
  - Textes (degrés, labels) : anthracite `#1C1B26`

Stratégie kerykeion-aware : le SVG Kerykeion utilise un système de CSS custom
properties (`--kerykeion-color-*`) référencées via `var(...)`. Il suffit
d'injecter un `<style>` en fin de SVG qui override ces variables — c'est
robuste, non destructif, et gère tous les paths d'un coup.

Fallback pour les SVGs sans variables Kerykeion : rewrite par regex des
`stroke`/`fill` hex sombres.

Idempotent : la seconde passe ne modifie plus rien.
"""
from __future__ import annotations
import re
from io import BytesIO
from typing import Optional


# Palette éditoriale (miroir du BookDocument)
BRONZE = '#B8935A'
BRONZE_DARK = '#A17840'
BRONZE_LIGHT = '#D4B481'
INK = '#1C1B26'
IVORY = '#FBF7EE'
IVORY_DARK = '#F1EBDD'


# Override CSS injecté en fin de SVG. Redéfinit les 20+ variables Kerykeion
# pour aligner la roue sur la palette Plume Astrale (bronze sur ivoire).
KERYKEION_OVERRIDE_CSS = f"""
<style type="text/css"><![CDATA[
:root, svg, .kerykeion-chart {{
  --kerykeion-color-black: {INK};
  --kerykeion-color-white: {IVORY};
  --kerykeion-color-neutral-content: {INK};
  --kerykeion-color-base-content: {INK};
  --kerykeion-color-primary: {BRONZE};
  --kerykeion-color-secondary: {BRONZE_DARK};
  --kerykeion-color-accent: {BRONZE_DARK};
  --kerykeion-color-neutral: {BRONZE};
  --kerykeion-color-base-100: {IVORY};
  --kerykeion-color-info: {BRONZE};
  --kerykeion-color-info-content: {INK};
  --kerykeion-color-success: {BRONZE};
  --kerykeion-color-warning: {BRONZE_DARK};
  --kerykeion-color-error: {BRONZE_DARK};
  --kerykeion-color-base-200: {IVORY};
  --kerykeion-color-base-300: {IVORY_DARK};

  --kerykeion-chart-color-paper-0: {IVORY};
  --kerykeion-chart-color-paper-1: {IVORY};

  /* Bandes des signes : alternance très douce pour ne pas bruiter le PDF */
  --kerykeion-chart-color-zodiac-bg-0: {IVORY};
  --kerykeion-chart-color-zodiac-bg-1: {IVORY_DARK};
  --kerykeion-chart-color-zodiac-bg-2: {IVORY};
  --kerykeion-chart-color-zodiac-bg-3: {IVORY_DARK};
  --kerykeion-chart-color-zodiac-bg-4: {IVORY};
  --kerykeion-chart-color-zodiac-bg-5: {IVORY_DARK};
  --kerykeion-chart-color-zodiac-bg-6: {IVORY};
  --kerykeion-chart-color-zodiac-bg-7: {IVORY_DARK};
  --kerykeion-chart-color-zodiac-bg-8: {IVORY};
  --kerykeion-chart-color-zodiac-bg-9: {IVORY_DARK};
  --kerykeion-chart-color-zodiac-bg-10: {IVORY};
  --kerykeion-chart-color-zodiac-bg-11: {IVORY_DARK};

  /* Anneaux et lignes : bronze filet fin */
  --kerykeion-chart-color-zodiac-radix-ring-0: {BRONZE};
  --kerykeion-chart-color-zodiac-radix-ring-1: {BRONZE};
  --kerykeion-chart-color-zodiac-radix-ring-2: {BRONZE};
  --kerykeion-chart-color-zodiac-transit-ring-0: {BRONZE};
  --kerykeion-chart-color-zodiac-transit-ring-1: {BRONZE};
  --kerykeion-chart-color-zodiac-transit-ring-2: {BRONZE};
  --kerykeion-chart-color-zodiac-transit-ring-3: {BRONZE};

  /* Aspects : bronze plus discret (couleur nuit → bronze foncé) */
  --kerykeion-chart-color-conjunction: {BRONZE_DARK};
  --kerykeion-chart-color-semi-sextile: {BRONZE};
  --kerykeion-chart-color-semi-square: {BRONZE_DARK};
  --kerykeion-chart-color-sextile: {BRONZE};
  --kerykeion-chart-color-quintile: {BRONZE};
  --kerykeion-chart-color-square: {BRONZE_DARK};
  --kerykeion-chart-color-trine: {BRONZE};
  --kerykeion-chart-color-sesquiquadrate: {BRONZE_DARK};
  --kerykeion-chart-color-biquintile: {BRONZE};
  --kerykeion-chart-color-quincunx: {BRONZE};
  --kerykeion-chart-color-opposition: {BRONZE_DARK};

  /* Planètes : toutes en bronze (identité visuelle premium unifiée) */
  --kerykeion-chart-color-sun: {BRONZE_DARK};
  --kerykeion-chart-color-moon: {BRONZE};
  --kerykeion-chart-color-mercury: {BRONZE};
  --kerykeion-chart-color-venus: {BRONZE_DARK};
  --kerykeion-chart-color-mars: {BRONZE_DARK};
  --kerykeion-chart-color-jupiter: {BRONZE};
  --kerykeion-chart-color-saturn: {BRONZE};
  --kerykeion-chart-color-uranus: {BRONZE};
  --kerykeion-chart-color-neptune: {BRONZE};
  --kerykeion-chart-color-pluto: {BRONZE_DARK};
  --kerykeion-chart-color-true-node: {BRONZE};
  --kerykeion-chart-color-mean-node: {BRONZE};
  --kerykeion-chart-color-chiron: {BRONZE};
  --kerykeion-chart-color-mean-lilith: {BRONZE_DARK};
  --kerykeion-chart-color-ceres: {BRONZE};
  --kerykeion-chart-color-pallas: {BRONZE};
  --kerykeion-chart-color-juno: {BRONZE};
  --kerykeion-chart-color-vesta: {BRONZE};
  --kerykeion-chart-color-vertex: {BRONZE};

  /* Angles majeurs (AS, MC, DS, IC) : bronze plus intense */
  --kerykeion-chart-color-first-house: {BRONZE_DARK};
  --kerykeion-chart-color-tenth-house: {BRONZE_DARK};
  --kerykeion-chart-color-seventh-house: {BRONZE_DARK};
  --kerykeion-chart-color-fourth-house: {BRONZE_DARK};

  /* Glyphes zodiaque */
  --kerykeion-chart-color-zodiac-icon-0: {BRONZE_DARK};
  --kerykeion-chart-color-zodiac-icon-1: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-2: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-3: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-4: {BRONZE_DARK};
  --kerykeion-chart-color-zodiac-icon-5: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-6: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-7: {BRONZE_DARK};
  --kerykeion-chart-color-zodiac-icon-8: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-9: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-10: {BRONZE};
  --kerykeion-chart-color-zodiac-icon-11: {BRONZE};
}}

/* Fallback texte : forcé anthracite */
text, tspan {{
  fill: {INK} !important;
}}
]]></style>
""".strip()


# Regex compilés (perf). Supportent guillemets simples ET doubles.
_HEX_RE = re.compile(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})')
_STROKE_ATTR = re.compile(r'''stroke\s*=\s*(["'])([^"']+)\1''')
_FILL_ATTR = re.compile(r'''fill\s*=\s*(["'])([^"']+)\1''')
_STYLE_ATTR = re.compile(r'''style\s*=\s*(["'])([^"']+)\1''')
_FILTER_ATTR = re.compile(r'''\sfilter\s*=\s*(?:["'])[^"']+(?:["'])''')
_STYLE_STROKE = re.compile(r'stroke\s*:\s*([^;"]+)')
_STYLE_FILL = re.compile(r'fill\s*:\s*([^;"]+)')


def _luminance(hex6: str) -> float:
    """Luminance approx d'une couleur hex (0-255 par canal)."""
    hex6 = hex6.lstrip('#')
    if len(hex6) == 3:
        hex6 = ''.join(c * 2 for c in hex6)
    try:
        r = int(hex6[0:2], 16)
        g = int(hex6[2:4], 16)
        b = int(hex6[4:6], 16)
        return 0.299 * r + 0.587 * g + 0.114 * b
    except ValueError:
        return 128.0


def _map_color(color: str, *, is_text_like: bool = False) -> str:
    """Retourne la couleur bronze/ink équivalente pour une couleur d'origine.

    - Couleurs sombres / noires / bleu nuit → bronze (trait) ou ink (texte)
    - Couleurs claires → gardent leur luminance mais forcées bronze si trait
    - Named colors gérées via mapping court
    """
    c = (color or '').strip().lower()
    if not c or c in ('none', 'transparent'):
        return color
    named = {
        'black': INK if is_text_like else BRONZE,
        'white': IVORY,
        'gray': BRONZE,
        'grey': BRONZE,
        'red': BRONZE_DARK,
        'orange': BRONZE_DARK,
        'yellow': BRONZE,
        'green': BRONZE,
        'blue': BRONZE,
        'purple': BRONZE_DARK,
        'pink': BRONZE_DARK,
        'brown': BRONZE_DARK,
    }
    if c in named:
        return named[c]
    m = _HEX_RE.fullmatch(c)
    if m:
        lum = _luminance(c)
        # Sombre : trait principal → bronze, texte → ink
        if lum < 90:
            return INK if is_text_like else BRONZE
        # Mi-teinte : bronze
        if lum < 180:
            return BRONZE
        # Clair (fond) : garde clair, mais force ivoire pour lisibilité
        return IVORY
    # rgb(), rgba(), currentColor, url(#…) → laisse tel quel
    return color


def _rewrite_style(style_body: str) -> str:
    def repl_stroke(m: re.Match) -> str:
        return f'stroke:{_map_color(m.group(1))}'
    def repl_fill(m: re.Match) -> str:
        return f'fill:{_map_color(m.group(1), is_text_like=True)}'
    out = _STYLE_STROKE.sub(repl_stroke, style_body)
    out = _STYLE_FILL.sub(repl_fill, out)
    return out


def _kerykeion_bronze_palette() -> dict[str, str]:
    """Retourne la table des noms de variables Kerykeion → couleur bronze/ivoire.

    Ce mapping DOIT couvrir toutes les `--kerykeion-*` référencées via `var(…)`
    dans les SVGs Kerykeion. Sert au substitueur `_resolve_kerykeion_vars`.
    """
    B, BD, BL, I, ID, K = BRONZE, BRONZE_DARK, BRONZE_LIGHT, IVORY, IVORY_DARK, INK
    p: dict[str, str] = {
        # Base colors
        'color-black': K, 'color-white': I,
        'color-neutral-content': K, 'color-base-content': K,
        'color-primary': B, 'color-secondary': BD, 'color-accent': BD,
        'color-neutral': B, 'color-base-100': I, 'color-info': B,
        'color-info-content': K,
        'color-success': B, 'color-warning': BD, 'color-error': BD,
        'color-base-200': I, 'color-base-300': ID,
        # Chart papers & bands
        'chart-color-paper-0': I, 'chart-color-paper-1': I,
        # Aspects
        'chart-color-conjunction': BD, 'chart-color-semi-sextile': B,
        'chart-color-semi-square': BD, 'chart-color-sextile': B,
        'chart-color-quintile': B, 'chart-color-square': BD,
        'chart-color-trine': B, 'chart-color-sesquiquadrate': BD,
        'chart-color-biquintile': B, 'chart-color-quincunx': B,
        'chart-color-opposition': BD,
        # Planets
        'chart-color-sun': BD, 'chart-color-moon': B, 'chart-color-mercury': B,
        'chart-color-venus': BD, 'chart-color-mars': BD, 'chart-color-jupiter': B,
        'chart-color-saturn': B, 'chart-color-uranus': B, 'chart-color-neptune': B,
        'chart-color-pluto': BD, 'chart-color-true-node': B, 'chart-color-mean-node': B,
        'chart-color-chiron': B, 'chart-color-mean-lilith': BD,
        'chart-color-ceres': B, 'chart-color-pallas': B, 'chart-color-juno': B,
        'chart-color-vesta': B, 'chart-color-vertex': B,
        # Angles
        'chart-color-first-house': BD, 'chart-color-tenth-house': BD,
        'chart-color-seventh-house': BD, 'chart-color-fourth-house': BD,
        # Lignes maisons
        'chart-color-houses-radix-line': B,
        'chart-color-houses-transit-line': B,
        # Lunar phase
        'chart-color-lunar-phase-0': BD, 'chart-color-lunar-phase-1': B,
        'chart-color-lunar-phase-2': ID,
    }
    # Zodiac bands (0-11) : alterne ivoire clair / ivoire moyen
    for i in range(12):
        p[f'chart-color-zodiac-bg-{i}'] = I if i % 2 == 0 else ID
    # Anneaux
    for i in range(6):
        p[f'chart-color-zodiac-radix-ring-{i}'] = B
        p[f'chart-color-zodiac-transit-ring-{i}'] = B
    # Glyphes zodiaque (0-11)
    for i in range(12):
        p[f'chart-color-zodiac-icon-{i}'] = B if i % 3 else BD
    return p


_KERYKEION_PALETTE = _kerykeion_bronze_palette()
_VAR_RE = re.compile(r'var\(\s*--kerykeion-([a-z0-9\-]+)(?:\s*,\s*[^)]*)?\s*\)')


def _resolve_kerykeion_vars(text: str) -> str:
    """Substitue toutes les occurrences `var(--kerykeion-*)` par du hex direct.

    Nécessaire pour cairosvg qui n'implémente pas les CSS custom properties.
    Les variables inconnues sont remplacées par bronze (défaut sûr).
    """
    def _sub(m: re.Match) -> str:
        var_name = m.group(1)
        return _KERYKEION_PALETTE.get(var_name, BRONZE)
    return _VAR_RE.sub(_sub, text)


def reskin_svg_bronze(svg: str) -> str:
    """Applique le reskin bronze sur ivoire à un SVG Kerykeion ou générique.

    Stratégie (kerykeion-aware) :
      1. Neutralise le `background-color` inline sur `<svg>` root → ivoire
      2. Injecte un `<rect fill=ivory>` full-canvas comme fond dur
      3. Résout tous les `var(--kerykeion-*)` en hex direct (cairosvg-safe)
      4. Fallback regex pour les rares hex sombres restants
      5. Marqueur `data-plume-bronze="1"` pour l'idempotence
    """
    if not svg or '<svg' not in svg[:400]:
        return svg
    if 'data-plume-bronze="1"' in svg:
        return svg

    # 1. Neutralise le background-color inline sur la racine SVG + marqueur
    def _svg_root_repl(m: re.Match) -> str:
        head = m.group(0)
        head = re.sub(
            r"style\s*=\s*'[^']*'",
            f"style='background-color: {IVORY};'", head, count=1,
        )
        head = re.sub(
            r'style\s*=\s*"[^"]*"',
            f'style="background-color: {IVORY};"', head, count=1,
        )
        return head.replace('<svg', '<svg data-plume-bronze="1"', 1)

    svg = re.sub(r'<svg[^>]*>', _svg_root_repl, svg, count=1)

    # 2. Nettoie filtres shadow/glow
    svg = _FILTER_ATTR.sub('', svg)

    # 3. Injecte un rect full-canvas ivoire comme fond dur
    m = re.search(r'<svg[^>]*>', svg)
    if m:
        insert_at = m.end()
        svg = (
            svg[:insert_at]
            + f'\n<rect x="0" y="0" width="100%" height="100%" fill="{IVORY}"/>\n'
            + svg[insert_at:]
        )

    # 4. Résout var(--kerykeion-*) → hex (cairosvg-compatible)
    svg = _resolve_kerykeion_vars(svg)

    # 5. Fallback regex pour hex sombres sur SVGs non-Kerykeion
    svg = _STROKE_ATTR.sub(
        lambda m: f'stroke={m.group(1)}{_map_color(m.group(2))}{m.group(1)}', svg
    )
    svg = _FILL_ATTR.sub(
        lambda m: f'fill={m.group(1)}{_map_color(m.group(2), is_text_like=True)}{m.group(1)}',
        svg,
    )
    svg = _STYLE_ATTR.sub(
        lambda m: f'style={m.group(1)}{_rewrite_style(m.group(2))}{m.group(1)}', svg
    )

    return svg


def svg_bronze_to_png_bytes(svg: str, target_px: int = 1200) -> Optional[bytes]:
    """Convertit un SVG (déjà reskin ou pas) en PNG bytes via cairosvg.

    Retourne None si cairosvg n'est pas installé ou si la conversion échoue.
    Le PNG résultant peut être injecté tel quel dans ReportLab via RLImage.
    """
    if not svg:
        return None
    reskinned = reskin_svg_bronze(svg)
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return None
    try:
        buf = BytesIO()
        cairosvg.svg2png(
            bytestring=reskinned.encode('utf-8'),
            write_to=buf,
            output_width=target_px,
            background_color='white',
        )
        return buf.getvalue()
    except Exception:
        return None
