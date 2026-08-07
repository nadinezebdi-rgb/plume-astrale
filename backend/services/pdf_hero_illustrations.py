"""
pdf_hero_illustrations.py — 5 illustrations SVG uniques pour la couverture
de chaque rapport prestige Plume Astrale.

Chaque fonction retourne un SVG (str) prêt à être rasterisé et injecté en
couverture. Palette V3 : navy #0F1A3C, or #C9A24B, crème #F7F5F0.

Illustrations :
  - `tree_of_life_svg()`      → Arbre séphirotique kabbalistique (10 séphirot + 22 chemins)
  - `karmic_nodes_svg()`      → Nœuds karmiques (Nord + Sud reliés par l'axe des temps)
  - `entwined_hearts_svg()`   → Deux cœurs entrelacés (synastrie)
  - `natal_wheel_svg()`       → Roue natale zodiacale 12 maisons
  - `life_path_svg()`         → Chemin de vie 9 nombres reliés en spirale
"""
from __future__ import annotations
from typing import Optional


# ═══════════════════════════════════════════════════════════════
#  Enveloppe commune : fond navy + halo doré + cadre pointillé
# ═══════════════════════════════════════════════════════════════
def _wrap(inner_svg: str, subtitle: Optional[str] = None) -> str:
    """Enveloppe commune 400×400 : fond nuit + halo + cadre + inner content."""
    sub = subtitle or ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="1200" height="1200">
<defs>
  <radialGradient id="ph-halo" cx="50%" cy="45%" r="60%">
    <stop offset="0%" stop-color="#C9A24B" stop-opacity="0.20"/>
    <stop offset="40%" stop-color="#C9A24B" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#0F1A3C" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="ph-gold-line" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#C9A24B" stop-opacity="0.3"/>
    <stop offset="50%" stop-color="#C9A24B" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#C9A24B" stop-opacity="0.3"/>
  </linearGradient>
  <filter id="ph-glow"><feGaussianBlur stdDeviation="1.6"/></filter>
</defs>
<rect width="400" height="400" fill="#0F1A3C"/>
<ellipse cx="200" cy="180" rx="220" ry="200" fill="url(#ph-halo)"/>
<rect x="16" y="16" width="368" height="368" fill="none" stroke="url(#ph-gold-line)" stroke-width="0.7" stroke-dasharray="1 3" opacity="0.7"/>
{inner_svg}
{f'<text x="200" y="378" text-anchor="middle" font-family="Helvetica" font-size="7.5" letter-spacing="3" fill="#C9A24B" opacity="0.75">{sub.upper()}</text>' if sub else ''}
</svg>'''


# ═══════════════════════════════════════════════════════════════
#  1. Arbre de vie séphirotique (Kabbale)
# ═══════════════════════════════════════════════════════════════
def tree_of_life_svg() -> str:
    """Arbre séphirotique : 10 sephirot + 22 chemins reliants."""
    # Positions des 10 sephirot (Kether en haut, Malkuth en bas)
    seph = {
        1: (200, 80),   # Kether
        2: (280, 130),  # Chokmah
        3: (120, 130),  # Binah
        4: (280, 200),  # Chesed
        5: (120, 200),  # Geburah
        6: (200, 200),  # Tiphereth (centre)
        7: (280, 270),  # Netzach
        8: (120, 270),  # Hod
        9: (200, 300),  # Yesod
        10:(200, 350),  # Malkuth
    }
    # 22 chemins (paires)
    paths = [
        (1,2),(1,3),(1,6),(2,3),(2,4),(2,6),(3,5),(3,6),
        (4,5),(4,6),(4,7),(5,6),(5,8),(6,7),(6,8),(6,9),
        (7,8),(7,9),(7,10),(8,9),(8,10),(9,10),
    ]
    inner = ['<g opacity="0.55" stroke="#C9A24B" stroke-width="0.7">']
    for a,b in paths:
        x1,y1 = seph[a]; x2,y2 = seph[b]
        inner.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    inner.append('</g>')
    inner.append('<g>')
    for i,(x,y) in seph.items():
        r = 15 if i in (1,6,10) else 12
        inner.append(f'<circle cx="{x}" cy="{y}" r="{r+3}" fill="#C9A24B" opacity="0.20"/>')
        inner.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.2"/>')
        inner.append(f'<text x="{x}" y="{y+3}" text-anchor="middle" font-family="Helvetica" font-size="8" font-weight="600" fill="#C9A24B">{i}</text>')
    inner.append('</g>')
    return _wrap('\n'.join(inner), subtitle='arbre séphirotique')


# ═══════════════════════════════════════════════════════════════
#  2. Nœuds karmiques (Karma & Destin)
# ═══════════════════════════════════════════════════════════════
def karmic_nodes_svg() -> str:
    """Deux nœuds ☊ ☋ reliés par l'axe des temps + spirale karmique."""
    inner = []
    # Spirale karmique douce
    inner.append('<g fill="none" stroke="#C9A24B" opacity="0.35" stroke-width="0.7">')
    for i, r in enumerate([40, 70, 100, 130, 160]):
        opacity = 0.5 - i*0.08
        inner.append(f'<circle cx="200" cy="200" r="{r}" opacity="{opacity}"/>')
    inner.append('</g>')

    # Axe vertical (temps)
    inner.append('<line x1="200" y1="60" x2="200" y2="340" stroke="#C9A24B" stroke-width="0.8" stroke-dasharray="2 4" opacity="0.65"/>')

    # Nœud Nord (☊) — en haut
    inner.append('<g transform="translate(200,110)">')
    inner.append('<circle r="42" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.5"/>')
    inner.append('<circle r="46" fill="none" stroke="#C9A24B" stroke-width="0.5" opacity="0.5"/>')
    inner.append('<path d="M -20 15 C -25 -5, -8 -20, 0 -8 C 8 -20, 25 -5, 20 15 M -15 15 A 5 5 0 0 0 -5 15 M 15 15 A 5 5 0 0 0 5 15" fill="none" stroke="#C9A24B" stroke-width="2.2" stroke-linecap="round"/>')
    inner.append('<text x="0" y="55" text-anchor="middle" font-family="Helvetica" font-size="7" fill="#C9A24B" opacity="0.75">NŒUD NORD</text>')
    inner.append('</g>')

    # Nœud Sud (☋) — en bas
    inner.append('<g transform="translate(200,290)">')
    inner.append('<circle r="42" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.5"/>')
    inner.append('<circle r="46" fill="none" stroke="#C9A24B" stroke-width="0.5" opacity="0.5"/>')
    inner.append('<path d="M -20 -15 C -25 5, -8 20, 0 8 C 8 20, 25 5, 20 -15 M -15 -15 A 5 5 0 0 1 -5 -15 M 15 -15 A 5 5 0 0 1 5 -15" fill="none" stroke="#C9A24B" stroke-width="2.2" stroke-linecap="round"/>')
    inner.append('<text x="0" y="-52" text-anchor="middle" font-family="Helvetica" font-size="7" fill="#C9A24B" opacity="0.75">NŒUD SUD</text>')
    inner.append('</g>')

    # Étoile centrale (âme)
    inner.append('<g transform="translate(200,200)">')
    inner.append('<circle r="10" fill="#C9A24B"/>')
    inner.append('<circle r="16" fill="none" stroke="#C9A24B" stroke-width="0.5" opacity="0.6"/>')
    inner.append('</g>')
    return _wrap('\n'.join(inner), subtitle='axe des vies antérieures')


# ═══════════════════════════════════════════════════════════════
#  3. Cœurs entrelacés (Synastrie)
# ═══════════════════════════════════════════════════════════════
def entwined_hearts_svg() -> str:
    """Deux cœurs entrelacés reliés par un fil doré."""
    heart_path = 'M 0 -18 C -18 -34, -40 -20, -40 0 C -40 20, -20 30, 0 44 C 20 30, 40 20, 40 0 C 40 -20, 18 -34, 0 -18 Z'
    inner = []
    # Halo cœur
    inner.append('<circle cx="200" cy="200" r="130" fill="#C9A24B" opacity="0.05"/>')
    inner.append('<circle cx="200" cy="200" r="90" fill="#C9A24B" opacity="0.06"/>')

    # Cœur 1 (à gauche, contour or)
    inner.append('<g transform="translate(155,195) rotate(-8)">')
    inner.append(f'<path d="{heart_path}" fill="#0F1A3C" stroke="#C9A24B" stroke-width="2.5"/>')
    inner.append('</g>')

    # Cœur 2 (à droite, contour or plus clair)
    inner.append('<g transform="translate(245,205) rotate(12)">')
    inner.append(f'<path d="{heart_path}" fill="#0F1A3C" stroke="#DDB966" stroke-width="2.5" opacity="0.95"/>')
    inner.append('</g>')

    # Fil doré qui relie
    inner.append('<path d="M 155 220 C 175 235, 225 235, 245 220" fill="none" stroke="#C9A24B" stroke-width="1.4" stroke-linecap="round" opacity="0.8"/>')

    # 3 étoiles au-dessus
    for i, x in enumerate([170, 200, 230]):
        y = 130 - abs(i-1)*4
        inner.append(f'<g transform="translate({x},{y})"><path d="M 0 -6 L 1.5 -2 L 6 -2 L 2.5 1 L 3.5 6 L 0 3 L -3.5 6 L -2.5 1 L -6 -2 L -1.5 -2 Z" fill="#C9A24B"/></g>')
    return _wrap('\n'.join(inner), subtitle='rencontre astrale')


# ═══════════════════════════════════════════════════════════════
#  4. Roue natale (Thème Natal)
# ═══════════════════════════════════════════════════════════════
import math

def natal_wheel_svg() -> str:
    """Roue zodiacale 12 maisons + 12 signes (abréviations, safe pour rasterisation)."""
    inner = []
    # Abréviations françaises des 12 signes (cairosvg n'a pas les glyphes Unicode astrologie)
    signs = ['BÉ','TA','GÉ','CN','LI','VI','BA','SC','SG','CP','VE','PI']
    R_outer = 150
    R_inner = 110
    R_planet = 80
    # Cercle extérieur
    inner.append(f'<circle cx="200" cy="200" r="{R_outer+8}" fill="none" stroke="#C9A24B" stroke-width="0.6" opacity="0.5"/>')
    inner.append(f'<circle cx="200" cy="200" r="{R_outer}" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.2"/>')
    inner.append(f'<circle cx="200" cy="200" r="{R_inner}" fill="none" stroke="#C9A24B" stroke-width="0.8"/>')
    inner.append(f'<circle cx="200" cy="200" r="45" fill="none" stroke="#C9A24B" stroke-width="0.5" opacity="0.6"/>')

    # 12 axes maisons
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = 200 + R_inner * math.cos(angle)
        y1 = 200 + R_inner * math.sin(angle)
        x2 = 200 + R_outer * math.cos(angle)
        y2 = 200 + R_outer * math.sin(angle)
        inner.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#C9A24B" stroke-width="0.5" opacity="0.7"/>')

    # Symboles zodiaux (au milieu des secteurs)
    for i, sym in enumerate(signs):
        angle = math.radians(i * 30 - 90 + 15)  # +15° pour centrer dans le secteur
        r = (R_outer + R_inner) / 2
        x = 200 + r * math.cos(angle)
        y = 200 + r * math.sin(angle) + 3
        inner.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="Helvetica" font-size="9" font-weight="600" letter-spacing="1" fill="#C9A24B">{sym}</text>')

    # Quelques "planètes" décoratives placées sur des points
    planet_positions = [(35, 4), (95, 5), (175, 3), (245, 4), (300, 4)]
    for angle_deg, r_offset in planet_positions:
        angle = math.radians(angle_deg - 90)
        r = R_planet
        x = 200 + r * math.cos(angle)
        y = 200 + r * math.sin(angle)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_offset}" fill="#DDB966"/>')

    # Croix centrale (AC/DC/MC/IC)
    inner.append(f'<line x1="{200-R_outer}" y1="200" x2="{200+R_outer}" y2="200" stroke="#DDB966" stroke-width="1.1"/>')
    inner.append(f'<line x1="200" y1="{200-R_outer}" x2="200" y2="{200+R_outer}" stroke="#DDB966" stroke-width="1.1"/>')
    inner.append('<circle cx="200" cy="200" r="4" fill="#C9A24B"/>')
    return _wrap('\n'.join(inner), subtitle='roue natale complète')


# ═══════════════════════════════════════════════════════════════
#  5. Chemin de vie (Numérologie)
# ═══════════════════════════════════════════════════════════════
def life_path_svg() -> str:
    """Spirale numérique 1→9 reliée par un ruban doré."""
    inner = []
    # 9 nombres disposés en spirale
    # Utilise une spirale d'Archimède
    positions = []
    for i in range(1, 10):
        # Spirale : angle croissant, rayon croissant
        angle = math.radians(i * 40 - 90)
        r = 40 + i * 12
        x = 200 + r * math.cos(angle)
        y = 200 + r * math.sin(angle)
        positions.append((x, y, i))

    # Ruban connectant (courbe passant par les points)
    d_parts = [f'M {positions[0][0]:.1f} {positions[0][1]:.1f}']
    for i in range(1, len(positions)):
        prev = positions[i-1]
        cur = positions[i]
        cx = (prev[0] + cur[0]) / 2
        cy = (prev[1] + cur[1]) / 2 - 8
        d_parts.append(f'Q {cx:.1f} {cy:.1f} {cur[0]:.1f} {cur[1]:.1f}')
    ribbon_d = ' '.join(d_parts)
    inner.append(f'<path d="{ribbon_d}" fill="none" stroke="#C9A24B" stroke-width="1.6" stroke-linecap="round" opacity="0.75"/>')
    inner.append(f'<path d="{ribbon_d}" fill="none" stroke="#DDB966" stroke-width="0.6" stroke-dasharray="2 3" opacity="0.9"/>')

    # 9 disques numérotés
    for x, y, n in positions:
        r = 15 if n == 9 else 13
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+3}" fill="#C9A24B" opacity="0.18"/>')
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.1"/>')
        inner.append(f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-family="Helvetica" font-size="11" font-weight="700" fill="#C9A24B">{n}</text>')

    # Étoile au centre (soi)
    inner.append('<g transform="translate(200,200)">')
    inner.append('<circle r="14" fill="#0F1A3C" stroke="#C9A24B" stroke-width="1.5"/>')
    inner.append('<path d="M 0 -8 L 2 -2.5 L 8 -2 L 3.5 1.5 L 5 8 L 0 4 L -5 8 L -3.5 1.5 L -8 -2 L -2 -2.5 Z" fill="#C9A24B"/>')
    inner.append('</g>')
    return _wrap('\n'.join(inner), subtitle='chemin de vie')
