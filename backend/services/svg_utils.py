"""
Utilitaire : résoudre les CSS variables inline dans un SVG Kerykeion.

Contexte : l'endpoint astrology-api.io v3 /render/{natal,synastry,...} renvoie
un SVG Kerykeion qui utilise `var(--kerykeion-color-*)` pour toutes ses
couleurs. CairoSVG (et beaucoup d'autres moteurs légers) ne supportent pas
les CSS variables → tout devient noir/transparent.

`resolve_svg_css_vars()` extrait les définitions `--name: value;` du bloc
style intégré, résout les alias (2-3 passes), puis substitue chaque
`var(--name)` par sa valeur réelle.

`force_parchment_background()` réécrit les 15 variables fondamentales
Kerykeion (base-100/200/300, base-content, neutral, accents) vers une
palette **parchemin lisible** avant la résolution — ce qui transforme
l'ensemble de la roue sombre (navy + gris pâle, invendable au print) en
une roue claire or/ink sur crème, parfaitement lisible dans le livre.
"""
from __future__ import annotations
import re

_VAR_DEF_RE = re.compile(r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+?);')
_VAR_USE_RE = re.compile(r'var\(\s*--([a-zA-Z0-9_-]+)\s*\)')


def resolve_svg_css_vars(svg: str, max_depth: int = 5) -> str:
    """Inline all CSS `var(--x)` references in the SVG so basic SVG renderers
    (CairoSVG, resvg, weasyprint minimal) can render the chart correctly.

    - Extracts all `--name: value;` declarations found anywhere in the SVG
      (they usually live in an embedded `:root { ... }` <style> block).
    - Resolves nested aliases up to `max_depth` levels.
    - Returns a new SVG string with all `var(...)` substituted.
    """
    if not svg or 'var(' not in svg:
        return svg

    var_map: dict[str, str] = {}
    for m in _VAR_DEF_RE.finditer(svg):
        var_map[m.group(1).strip()] = m.group(2).strip()
    if not var_map:
        return svg

    def _resolve(value: str, depth: int = 0) -> str:
        if depth >= max_depth or 'var(' not in value:
            return value
        def sub(mo: re.Match) -> str:
            key = mo.group(1).strip()
            if key in var_map:
                return _resolve(var_map[key], depth + 1)
            return mo.group(0)
        return _VAR_USE_RE.sub(sub, value)

    resolved_map = {k: _resolve(v) for k, v in var_map.items()}

    def outer_sub(mo: re.Match) -> str:
        key = mo.group(1).strip()
        return resolved_map.get(key, mo.group(0))
    return _VAR_USE_RE.sub(outer_sub, svg)


# ─── Palette parchemin « livre d'astrologie » ─────────────────────────────
# Objectif : tout ce qui est sombre côté Kerykeion (base-100/200/300 et
# base-content en gris pâle sur fond navy) doit basculer en teintes claires
# et contrastées sur fond crème. Les accents colorés sont assombris pour
# rester lisibles sur parchemin (CYMK-safe).
_LIGHT_OVERRIDES: dict[str, str] = {
    # Fond principal (grande rect `background-rectangle` + zone roue) → parchemin
    'kerykeion-color-base-100': '#F7F2E6',
    # Anneaux zodiacaux alternés → crèmes à peine différenciés
    'kerykeion-color-base-200': '#EFE5CF',
    'kerykeion-color-base-300': '#E7DABB',
    # Textes et traits structurants (numéros maison, cuspides, aspects) → encre
    'kerykeion-color-base-content': '#243047',
    'kerykeion-color-neutral-content': '#3A3F55',
    # Anneau périmétrique zodiac + lignes neutres → or Hermès
    'kerykeion-color-neutral': '#A78140',
    # Noir / blanc : on les laisse (texte signé noir ou blanc complet)
    'kerykeion-color-black': '#1A1F2E',
    'kerykeion-color-white': '#FFFFFF',
    # Palette accents : versions "print-ready" (contraste minimal 4:1 sur crème)
    'kerykeion-color-primary': '#1E6FA8',    # bleus (Mercure, Jupiter, Neptune, …)
    'kerykeion-color-secondary': '#5A4FC1',  # indigos (Lune, Saturne, Pluton, …)
    'kerykeion-color-accent': '#C13A82',     # magentas (Vénus, Uranus, Vesta, …)
    'kerykeion-color-warning': '#B8863B',    # ors (Soleil, Mars, Nœud, maisons angulaires)
    'kerykeion-color-success': '#2A8F7A',    # verts (trigones, sextiles)
    'kerykeion-color-error': '#C13346',      # rouges (carrés, oppositions)
    'kerykeion-color-info': '#1E6FA8',
    'kerykeion-color-info-content': '#1A1F2E',
}

_PAPER_HEX = '#F7F2E6'


def force_parchment_background(svg: str) -> str:
    """Rewrite the SVG so every dark Kerykeion foundation color maps to a
    parchment-tuned equivalent **before** `resolve_svg_css_vars` substitutes
    the usages.

    Trois transformations :
      1. On remplace la valeur de chaque variable `--kerykeion-color-*`
         listée dans `_LIGHT_OVERRIDES` (base-100, base-200, base-300,
         base-content, neutral, accents) → palette parchemin.
      2. On force la `fill` du `<rect class='background-rectangle' ...>` à
         `_PAPER_HEX` (sécurité : certaines versions Kerykeion attachent la
         couleur en inline-style au lieu de la variable).
      3. On supprime les éventuels `fill="#0f172a"` codés en dur sur le
         premier rect pleine page.
    """
    if not svg:
        return svg

    # 1) Réécrit la valeur de chaque variable connue, quel que soit son format
    #    (`--name: #xxx;`, `--name: var(--autre);`, `--name:#xxx ;`, etc.)
    def _replace_var_def(mo: re.Match) -> str:
        key = mo.group(1).strip()
        override = _LIGHT_OVERRIDES.get(key)
        if override is None:
            return mo.group(0)
        return f'--{key}: {override};'
    out = _VAR_DEF_RE.sub(_replace_var_def, svg)

    # 2) Force le rect de fond identifié par sa class (robuste même si Kerykeion
    #    change le format de ses variables à l'avenir).
    def _bg_rect(mo: re.Match) -> str:
        attrs = mo.group(1)
        # Remplace les fills `style="fill:...;"` et `fill="..."`
        attrs = re.sub(
            r'(style\s*=\s*"[^"]*fill\s*:\s*)[^;"]+',
            lambda m: f'{m.group(1)}{_PAPER_HEX}',
            attrs,
        )
        attrs = re.sub(
            r'fill\s*=\s*"[^"]*"',
            f'fill="{_PAPER_HEX}"',
            attrs,
        )
        if 'fill' not in attrs:
            attrs = attrs.rstrip() + f' fill="{_PAPER_HEX}"'
        return f'<rect{attrs}/>'
    out = re.sub(
        r"<rect([^>]*?class\s*=\s*['\"]background-rectangle['\"][^>]*?)/>",
        _bg_rect,
        out,
    )

    # 3) Sécurité : premier rect pleine page sans class
    def _rect_fallback(mo: re.Match) -> str:
        attrs = mo.group(1)
        if 'fill=' in attrs:
            attrs = re.sub(r'fill\s*=\s*"[^"]*"', f'fill="{_PAPER_HEX}"', attrs, count=1)
            attrs = re.sub(r"fill\s*=\s*'[^']*'", f"fill='{_PAPER_HEX}'", attrs, count=1)
        else:
            attrs = attrs.rstrip() + f' fill="{_PAPER_HEX}"'
        return f'<rect{attrs}/>'
    out = re.sub(
        r'<rect([^>]*?width\s*=\s*"100%"[^>]*?height\s*=\s*"100%"[^>]*?)/>',
        _rect_fallback,
        out,
        count=1,
    )
    return out
