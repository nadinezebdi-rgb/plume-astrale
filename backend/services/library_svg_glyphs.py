"""
Bibliotheque SVG — glyphes vectoriels des 12 signes + 10 planetes.

Chaque glyphe est un SVG 512x512 avec fond nuit + symbole or centre.
On utilise le caractere Unicode + une police web-safe pour rester leger.
"""
from __future__ import annotations

from pathlib import Path

SVG_DIR = Path("/app/backend/assets/library/glyphs-svg")

# Table Unicode des glyphes astro
GLYPHS = [
    # SIGNES (12)
    ("aries",       "\u2648", "Belier"),
    ("taurus",      "\u2649", "Taureau"),
    ("gemini",      "\u264A", "Gemeaux"),
    ("cancer",      "\u264B", "Cancer"),
    ("leo",         "\u264C", "Lion"),
    ("virgo",       "\u264D", "Vierge"),
    ("libra",       "\u264E", "Balance"),
    ("scorpio",     "\u264F", "Scorpion"),
    ("sagittarius", "\u2650", "Sagittaire"),
    ("capricorn",   "\u2651", "Capricorne"),
    ("aquarius",    "\u2652", "Verseau"),
    ("pisces",      "\u2653", "Poissons"),
    # PLANETES (10)
    ("sun",     "\u2609", "Soleil"),
    ("moon",    "\u263D", "Lune"),
    ("mercury", "\u263F", "Mercure"),
    ("venus",   "\u2640", "Venus"),
    ("mars",    "\u2642", "Mars"),
    ("jupiter", "\u2643", "Jupiter"),
    ("saturn",  "\u2644", "Saturne"),
    ("uranus",  "\u2645", "Uranus"),
    ("neptune", "\u2646", "Neptune"),
    ("pluto",   "\u2647", "Pluton"),
]


SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#1a1f4a"/>
      <stop offset="70%" stop-color="#0a0d2b"/>
      <stop offset="100%" stop-color="#050716"/>
    </radialGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#f7e08a"/>
      <stop offset="50%" stop-color="#d4a744"/>
      <stop offset="100%" stop-color="#8a6b1e"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- fond -->
  <rect width="512" height="512" fill="url(#bg)"/>

  <!-- cercle ornemental exterieur -->
  <circle cx="256" cy="256" r="238" fill="none" stroke="url(#gold)" stroke-width="1.5" opacity="0.55"/>
  <circle cx="256" cy="256" r="220" fill="none" stroke="url(#gold)" stroke-width="0.7" opacity="0.35"/>

  <!-- etoiles decoratives -->
  <g fill="url(#gold)" opacity="0.6">
    <circle cx="256"  cy="34"  r="2"/>
    <circle cx="256"  cy="478" r="2"/>
    <circle cx="34"   cy="256" r="2"/>
    <circle cx="478"  cy="256" r="2"/>
    <circle cx="98"   cy="98"  r="1.4"/>
    <circle cx="414"  cy="98"  r="1.4"/>
    <circle cx="98"   cy="414" r="1.4"/>
    <circle cx="414"  cy="414" r="1.4"/>
  </g>

  <!-- glyphe -->
  <text x="256" y="256"
        font-family="'Noto Sans Symbols 2', 'Symbola', 'DejaVu Sans', 'Segoe UI Symbol', sans-serif"
        font-size="260"
        fill="url(#gold)"
        text-anchor="middle"
        dominant-baseline="central"
        filter="url(#glow)">__GLYPH__</text>

  <!-- label discret bas -->
  <text x="256" y="490"
        font-family="'Cormorant Garamond', 'Playfair Display', serif"
        font-size="16"
        fill="#f7e08a"
        text-anchor="middle"
        opacity="0.75"
        letter-spacing="4">__LABEL__</text>
</svg>
"""


def generate_all_svg() -> list[dict]:
    """Genere les 22 SVG sur disque et retourne l'index."""
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    index = []
    for slug, glyph, label in GLYPHS:
        svg = (
            SVG_TEMPLATE
            .replace("__GLYPH__", glyph)
            .replace("__LABEL__", label.upper())
        )
        out = SVG_DIR / f"{slug}.svg"
        out.write_text(svg, encoding="utf-8")
        index.append({
            "slug": slug,
            "label": label,
            "path": str(out),
            "url": f"/api/library/file/glyphs-svg/{slug}.svg",
        })
    return index


if __name__ == "__main__":
    idx = generate_all_svg()
    print(f"Generated {len(idx)} SVG glyphs into {SVG_DIR}")
    for it in idx[:3]:
        print(" -", it["slug"], "→", it["url"])
