"""
Utilitaire : résoudre les CSS variables inline dans un SVG Kerykeion.

Contexte : l'endpoint astrology-api.io v3 /render/{natal,synastry,...} renvoie
un SVG Kerykeion qui utilise `var(--kerykeion-color-*)` pour toutes ses
couleurs. CairoSVG (et beaucoup d'autres moteurs légers) ne supportent pas
les CSS variables → tout devient noir/transparent.

`resolve_svg_css_vars()` extrait les définitions `--name: value;` du bloc
style intégré, résout les alias (2-3 passes), puis substitue chaque
`var(--name)` par sa valeur réelle.
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
