"""
pdf_prestige.py — charte "livre prestige" partagée pour tous les rapports Plume Astrale.

Éléments fournis :
  - `prestige_bg(canv, doc, product_name)` : fond nuit + halo + étoiles + cadre or
    pointillé + soleil ornemental en haut + footer éditorial (chapitre + page)
  - `ornament(story, kind)` : ✦ ◆ · séparateurs décoratifs centrés
  - `chapter_opener(story, styles, roman, title, subtitle)` : page d'ouverture
    de chapitre avec numérotation romaine
  - `toc_page(story, styles, chapters)` : sommaire éditorial
  - `simple_world_map_svg(planet_lines, cities)` : carte du monde SVG de secours
    pour le PDF Astrocartographie (si l'API renvoie rien)

Palette et polices : voir services.pdf_theme.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import Paragraph, Spacer, PageBreak

from services.pdf_theme import NIGHT, GOLD, GOLD_LIGHT, CREAM, MUTED, LAVENDER, font


# ═══════════════════════════════════════════════════════════
#   Ornements & séparateurs
# ═══════════════════════════════════════════════════════════
_ORNAMENT_STYLE = ParagraphStyle(
    'prestige_ornament', fontName='Helvetica', fontSize=9,
    alignment=TA_CENTER, leading=12, spaceBefore=6, spaceAfter=6,
)


def ornament(story: list, kind: str = 'star') -> None:
    """Insère un séparateur décoratif doré centré (3 glyphes)."""
    glyph = {'star': '✦', 'diamond': '◆', 'dot': '·'}.get(kind, '✦')
    text = f'<font color="#D4AF37">{glyph}&nbsp;&nbsp;&nbsp;{glyph}&nbsp;&nbsp;&nbsp;{glyph}</font>'
    story.append(Paragraph(text, _ORNAMENT_STYLE))


# ═══════════════════════════════════════════════════════════
#   Fond de page prestige (cadre or + soleil + footer)
# ═══════════════════════════════════════════════════════════
def prestige_bg(canv, doc, product_name: str = 'Plume Astrale',
                chapter_getter=None) -> None:
    """Fond de page prestige unifié — à passer en onFirstPage / onLaterPages.

    - Nuit profonde + halo + étoiles stables
    - Cadre or pointillé sur toute la page
    - Petit soleil ornemental en haut au centre
    - Footer éditorial : nom du produit à gauche, chapitre (si fourni) au centre, page à droite

    `chapter_getter(page_num) -> str | None` peut être passé pour afficher le titre
    du chapitre courant dans le footer.
    """
    import random
    canv.saveState()
    W, H = A4

    # Nuit profonde
    canv.setFillColor(NIGHT)
    canv.rect(0, 0, W, H, fill=1, stroke=0)

    # Halo doré radial en haut
    for i, alpha in enumerate([0.02, 0.015, 0.01]):
        canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
        canv.circle(W / 2, H, (i + 1) * 6 * cm, fill=1, stroke=0)

    # 30 étoiles seed-based (stable par page)
    r = random.Random(hash((doc.page,)))
    for _ in range(30):
        x = r.uniform(1 * cm, W - 1 * cm)
        y = r.uniform(1 * cm, H - 1 * cm)
        s = r.choice([0.4, 0.5, 0.6, 0.8])
        canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
        canv.circle(x, y, s, fill=1, stroke=0)

    # Cadre or pointillé
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(0.35)
    canv.setDash([0.6, 2.4], 0)
    canv.rect(1.2 * cm, 1.2 * cm, W - 2.4 * cm, H - 2.4 * cm, fill=0, stroke=1)
    canv.setDash([], 0)

    # Soleil ornemental en haut (petit disque + deux tirets)
    canv.setFillColor(GOLD)
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(0.4)
    canv.circle(W / 2, H - 1.55 * cm, 0.10 * cm, fill=1, stroke=0)
    canv.line(W / 2 - 1.4 * cm, H - 1.55 * cm, W / 2 - 0.3 * cm, H - 1.55 * cm)
    canv.line(W / 2 + 0.3 * cm, H - 1.55 * cm, W / 2 + 1.4 * cm, H - 1.55 * cm)

    # Footer éditorial
    product_upper = str(product_name).upper()
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 6.5)
    canv.drawString(2 * cm, 0.75 * cm, f"PLUME ASTRALE · {product_upper}")

    chapter_str = None
    if callable(chapter_getter):
        try:
            chapter_str = chapter_getter(doc.page)
        except Exception:
            chapter_str = None
    if chapter_str:
        canv.drawCentredString(W / 2, 0.75 * cm, str(chapter_str))

    canv.drawRightString(W - 2 * cm, 0.75 * cm, f"— {doc.page} —")
    canv.restoreState()


# ═══════════════════════════════════════════════════════════
#   Chapter opener (page d'ouverture numérotée)
# ═══════════════════════════════════════════════════════════
_ROMAN_MAP = [
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
]


def to_roman(n: int) -> str:
    """Convertit un entier positif en chiffre romain (1..~20)."""
    if n <= 0:
        return ''
    result = ''
    for value, numeral in _ROMAN_MAP:
        while n >= value:
            result += numeral
            n -= value
    return result


def chapter_opener(story: list, styles: dict, roman: str,
                   title: str, subtitle: Optional[str] = None) -> None:
    """Page d'ouverture de chapitre — numérotation romaine centrée + titre."""
    story.append(Spacer(1, 5.5 * cm))
    p_roman = ParagraphStyle(
        'chapter_roman', fontName=styles['title'].fontName,
        fontSize=18, textColor=GOLD_LIGHT, alignment=TA_CENTER,
        letterSpacing=6, leading=22, spaceAfter=6,
    )
    story.append(Paragraph(f"CHAPITRE&nbsp;&nbsp;{roman}", p_roman))
    ornament(story, 'diamond')
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(f"<i>{title}</i>", styles['title']))
    if subtitle:
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(subtitle, styles['subtitle']))
    story.append(Spacer(1, 1.0 * cm))
    ornament(story, 'star')
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════
#   Sommaire éditorial
# ═══════════════════════════════════════════════════════════
def toc_page(story: list, styles: dict, chapters: List[Dict[str, Any]]) -> None:
    """Sommaire éditorial simple.

    `chapters` : liste de dicts { 'roman': 'I', 'title': 'La carte du monde',
                                  'page': 4 (optionnel, sinon "···") }
    """
    story.append(Spacer(1, 1.4 * cm))
    story.append(Paragraph("Sommaire", styles['caption']))
    ornament(story, 'star')
    story.append(Paragraph("<i>Le voyage en 7 chapitres</i>", styles['h2']))
    story.append(Spacer(1, 0.8 * cm))

    row_style = ParagraphStyle(
        'toc_row', fontName=font('Cormorant', 'Helvetica'),
        fontSize=12, textColor=CREAM, alignment=TA_LEFT,
        leading=18, spaceAfter=6,
    )
    for ch in chapters:
        roman = ch.get('roman') or ''
        title = ch.get('title') or ''
        page = ch.get('page')
        page_str = str(page) if page is not None else '·'
        # Format : "I  ·  Titre .......... 12"
        line = (
            f'<font color="#D4AF37">{roman}</font>'
            f'&nbsp;&nbsp;·&nbsp;&nbsp;<i>{title}</i>'
            f'&nbsp;&nbsp;<font color="#9089B5">····</font>&nbsp;&nbsp;'
            f'<font color="#D4AF37">{page_str}</font>'
        )
        story.append(Paragraph(line, row_style))

    story.append(Spacer(1, 0.8 * cm))
    ornament(story, 'diamond')
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════
#   Carte du monde de secours (SVG statique)
# ═══════════════════════════════════════════════════════════
def simple_world_map_svg(city_names: Optional[List[str]] = None) -> str:
    """Retourne un SVG de secours — carte du monde stylisée avec 7 lignes planétaires
    + jusqu'à 3 marqueurs de villes. Réplique du composant frontend AstroCartoHero.

    Utilisée quand l'API astrocartographique ne retourne pas de SVG (fallback).
    """
    if city_names is None:
        city_names = []
    cx = [(88, 138), (198, 108), (285, 165)]
    city_labels = list(city_names[:3])
    while len(city_labels) < 3:
        city_labels.append('')

    planets = [
        ('#C9A24B', 'M 20 190 Q 200 40 380 210',            'Soleil',   ''),
        ('#7A8AB0', 'M 30 60 Q 200 260 380 90',             'Lune',     '4 3'),
        ('#D4A574', 'M 40 240 Q 200 100 370 260',           'Vénus',    ''),
        ('#B0533F', 'M 20 130 C 120 40 300 320 380 150',    'Mars',     '4 3'),
        ('#8B7A4E', 'M 30 280 C 140 200 260 60 380 240',    'Jupiter',  ''),
        ('#4E5B7A', 'M 40 40 C 160 200 240 120 380 300',    'Saturne',  '4 3'),
        ('#6A8FA6', 'M 20 300 Q 200 200 380 40',            'Neptune',  ''),
    ]

    parts: List[str] = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 340" width="1600" height="1360">')
    parts.append('<defs>')
    parts.append('<filter id="acg-grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>')
    parts.append('<feColorMatrix values="0 0 0 0 0.06  0 0 0 0 0.10  0 0 0 0 0.24  0 0 0 0.04 0"/></filter>')
    parts.append('<linearGradient id="acg-gold" x1="0%" y1="0%" x2="100%" y2="0%">')
    parts.append('<stop offset="0%" stop-color="#C9A24B" stop-opacity="0.35"/>')
    parts.append('<stop offset="50%" stop-color="#C9A24B" stop-opacity="0.85"/>')
    parts.append('<stop offset="100%" stop-color="#C9A24B" stop-opacity="0.35"/>')
    parts.append('</linearGradient></defs>')
    # Fond crème
    parts.append('<rect width="400" height="340" fill="#F7F5F0"/>')
    parts.append('<rect width="400" height="340" fill="url(#acg-grain)" opacity="0.55"/>')
    parts.append('<rect x="12" y="12" width="376" height="316" fill="none" stroke="url(#acg-gold)" stroke-width="0.8" stroke-dasharray="1 3" opacity="0.65"/>')

    # Grille discrète
    for y in (80, 130, 170, 210, 260):
        parts.append(f'<line x1="24" y1="{y}" x2="376" y2="{y}" stroke="#0F1A3C" stroke-width="0.35" opacity="0.14"/>')
    for x in (80, 140, 200, 260, 320):
        parts.append(f'<line x1="{x}" y1="24" x2="{x}" y2="316" stroke="#0F1A3C" stroke-width="0.35" opacity="0.14"/>')

    # Silhouettes continents
    continents = [
        'M 40 90 Q 55 75, 78 82 Q 100 88, 108 110 L 105 145 Q 85 155, 70 148 Q 55 142, 48 130 Q 40 118, 42 100 Z',
        'M 100 170 Q 118 168, 125 185 L 128 220 Q 122 245, 108 250 Q 95 245, 92 225 Q 90 200, 98 178 Z',
        'M 175 95 Q 190 88, 210 92 Q 220 98, 218 112 Q 210 122, 195 122 Q 180 118, 172 108 Z',
        'M 185 135 Q 210 130, 225 145 Q 232 175, 225 200 Q 215 230, 200 245 Q 185 240, 178 220 Q 170 190, 175 160 Z',
        'M 225 82 Q 260 78, 300 88 Q 322 102, 320 122 Q 305 138, 275 138 Q 240 132, 225 118 Z',
        'M 290 195 Q 310 190, 320 205 Q 325 220, 315 232 Q 300 235, 290 225 Q 285 210, 290 198 Z',
    ]
    parts.append('<g fill="#0F1A3C" opacity="0.10">')
    for p in continents:
        parts.append(f'<path d="{p}"/>')
    parts.append('</g>')

    # Lignes planétaires
    parts.append('<g fill="none" stroke-linecap="round">')
    for i, (color, d, name, dash) in enumerate(planets):
        w = 1.6 if i == 0 else 1.2
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
        parts.append(f'<path d="{d}" stroke="{color}" stroke-width="{w}"{dash_attr} opacity="0.85"/>')
    parts.append('</g>')

    # Marqueurs de villes
    for i, ((x, y), label) in enumerate(zip(cx, city_labels)):
        parts.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#C9A24B" opacity="0.35"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#C9A24B"/>')
        if label:
            parts.append(
                f'<text x="{x + 8}" y="{y + 3}" font-family="Helvetica" font-size="8" '
                f'font-weight="600" fill="#0F1A3C" opacity="0.75">{label}</text>'
            )

    # Compass N
    parts.append('<g transform="translate(345, 285)">')
    parts.append('<circle r="16" fill="none" stroke="#C9A24B" stroke-width="0.6" opacity="0.7"/>')
    parts.append('<path d="M 0 -12 L 2 0 L 0 12 L -2 0 Z" fill="#C9A24B"/>')
    parts.append('<path d="M -12 0 L 0 2 L 12 0 L 0 -2 Z" fill="#C9A24B" opacity="0.5"/>')
    parts.append('<text x="0" y="-19" font-family="Helvetica" font-size="6" font-weight="600" fill="#C9A24B" text-anchor="middle">N</text>')
    parts.append('</g>')

    # Étiquette
    parts.append('<text x="24" y="322" font-family="Helvetica" font-size="8" letter-spacing="1.6" fill="#0F1A3C" opacity="0.55">CARTE ASTRALE PLANÉTAIRE · PLUME ASTRALE</text>')

    parts.append('</svg>')
    return ''.join(parts)
