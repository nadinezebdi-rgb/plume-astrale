# -*- coding: utf-8 -*-
"""
Roue astrologique — générateur SVG carré, calibré pour l'impression A5.
Sortie : un SVG en viewBox carré 0 0 1000 1000. AUCUNE déformation possible
tant que le conteneur reçoit width == height (voir le guide de mise en page).
"""
import math

# ---------------------------------------------------------------- palette
INK        = "#4A3F35"   # texte
GOLD       = "#A8823F"   # trait principal
GOLD_SOFT  = "#C9AE7C"   # traits secondaires
GOLD_PALE  = "#E3D6BC"   # graduations
BAND       = "#F3EBDC"   # fond de la bande zodiacale (1 sur 2)
PAPER      = "#FBF7F0"

# ---------------------------------------------------------------- rayons (sur 1000)
CX = CY   = 500.0
R_OUT     = 452.0   # cercle extérieur
R_SIGN_IN = 388.0   # bord intérieur de la bande des signes
R_TICK    = 376.0   # fin des graduations de degrés
R_PLANET  = 338.0   # glyphes de planètes
R_PDEG    = 309.0   # degré sous le glyphe
R_IN      = 280.0   # cercle intérieur (les aspects vivent dedans)
R_HNUM    = 262.0   # numéros de maisons
R_SIGNG   = 420.0   # glyphes de signes

SIGNS  = "♈♉♊♋♌♍♎♏♐♑♒♓"
SIGN_FR = ["Bélier","Taureau","Gémeaux","Cancer","Lion","Vierge",
           "Balance","Scorpion","Sagittaire","Capricorne","Verseau","Poissons"]
GLYPH  = {"Soleil":"☉","Lune":"☽","Mercure":"☿","Vénus":"♀","Mars":"♂",
          "Jupiter":"♃","Saturne":"♄","Uranus":"♅","Neptune":"♆","Pluton":"♇",
          "Nœud Nord":"☊","Chiron":"⚷","Lilith":"⚸"}

ASPECTS = [  # (nom, angle, orbe, famille)
    ("Conjonction", 0,   8, "neutre"),
    ("Opposition", 180,  8, "tension"),
    ("Trigone",    120,  7, "flux"),
    ("Carré",       90,  7, "tension"),
    ("Sextile",     60,  5, "flux"),
]

def pt(lon, r, asc):
    a = math.radians(180.0 + (lon - asc))
    return CX + r*math.cos(a), CY - r*math.sin(a)

def arc_path(r, lon1, lon2, asc):
    x1,y1 = pt(lon1,r,asc); x2,y2 = pt(lon2,r,asc)
    return x1,y1,x2,y2

def band_sector(lon1, lon2, asc, r_in, r_out):
    x1,y1 = pt(lon1,r_out,asc); x2,y2 = pt(lon2,r_out,asc)
    x3,y3 = pt(lon2,r_in ,asc); x4,y4 = pt(lon1,r_in ,asc)
    return (f"M {x1:.2f} {y1:.2f} A {r_out} {r_out} 0 0 0 {x2:.2f} {y2:.2f} "
            f"L {x3:.2f} {y3:.2f} A {r_in} {r_in} 0 0 1 {x4:.2f} {y4:.2f} Z")

def spread(lons, minsep=9.0, passes=220):
    """Écarte les glyphes trop proches sans changer leur ordre."""
    v = list(lons)
    n = len(v)
    if n < 2: return v
    order = sorted(range(n), key=lambda i: v[i])
    for _ in range(passes):
        moved = False
        for k in range(n):
            i, j = order[k], order[(k+1) % n]
            d = (v[j] - v[i]) % 360.0
            if 0 <= d < minsep:
                push = (minsep - d) / 2.0
                v[i] = (v[i] - push) % 360.0
                v[j] = (v[j] + push) % 360.0
                moved = True
        if not moved: break
    return v

def deg_label(lon):
    d = int(lon % 30)
    m = int(round(((lon % 30) - d) * 60))
    if m == 60: d, m = d+1, 0
    return f"{d}°{m:02d}"

def build_wheel(planets, cusps, asc=None, minsep=9.0, aspect_set=("Opposition","Trigone","Carré","Sextile")):
    """planets: [(nom, longitude, retrograde_bool)]  cusps: 12 longitudes (maison 1..12)"""
    asc = cusps[0] if asc is None else asc
    o = []
    A = o.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" '
      f'width="1000" height="1000" preserveAspectRatio="xMidYMid meet" '
      f'font-family="DejaVu Sans, Noto Sans Symbols 2, Segoe UI Symbol, serif">')
    A(f'<rect width="1000" height="1000" fill="none"/>')

    # --- bande zodiacale : 1 secteur sur 2 teinté
    A('<g>')
    for i in range(12):
        l1 = i*30.0
        if i % 2 == 0:
            A(f'<path d="{band_sector(l1, l1+30, asc, R_SIGN_IN, R_OUT)}" fill="{BAND}" stroke="none"/>')
    A('</g>')

    # --- cercles
    for r, w, c in ((R_OUT,1.6,GOLD), (R_SIGN_IN,1.1,GOLD), (R_IN,1.0,GOLD_SOFT)):
        A(f'<circle cx="500" cy="500" r="{r}" fill="none" stroke="{c}" stroke-width="{w}"/>')

    # --- graduations de degrés
    A(f'<g stroke="{GOLD_PALE}" stroke-width="0.7">')
    for d in range(360):
        long = d*1.0
        rr = R_TICK if d % 10 == 0 else (R_SIGN_IN-6 if d % 5 == 0 else R_SIGN_IN-3)
        x1,y1 = pt(long, R_SIGN_IN, asc); x2,y2 = pt(long, rr, asc)
        A(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    A('</g>')

    # --- séparations de signes + glyphes
    A(f'<g stroke="{GOLD}" stroke-width="1.0">')
    for i in range(12):
        x1,y1 = pt(i*30.0, R_SIGN_IN, asc); x2,y2 = pt(i*30.0, R_OUT, asc)
        A(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    A('</g>')
    A(f'<g fill="{GOLD}" font-size="32" text-anchor="middle">')
    for i in range(12):
        x,y = pt(i*30.0+15, R_SIGNG, asc)
        A(f'<text x="{x:.2f}" y="{y+12:.2f}">{SIGNS[i]}\ufe0e</text>')
    A('</g>')

    # --- maisons
    ang = {0:"As", 3:"Fc", 6:"Ds", 9:"Mc"}
    for i, c in enumerate(cusps):
        angular = i in ang
        r2 = R_OUT if angular else R_SIGN_IN
        x1,y1 = pt(c, R_IN, asc); x2,y2 = pt(c, r2, asc)
        A(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
          f'stroke="{GOLD if angular else GOLD_SOFT}" stroke-width="{1.5 if angular else 0.8}" '
          + ('' if angular else 'stroke-dasharray="3 4"') + '/>')
        if angular:
            lx,ly = pt(c, R_OUT+20, asc)
            A(f'<text x="{lx:.2f}" y="{ly+5:.2f}" fill="{GOLD}" font-size="20" '
              f'text-anchor="middle" letter-spacing="1">{ang[i]}</text>')
        mid = c + (((cusps[(i+1) % 12] - c) % 360.0)/2.0)
        hx,hy = pt(mid, R_HNUM, asc)
        A(f'<text x="{hx:.2f}" y="{hy+6:.2f}" fill="{GOLD_SOFT}" font-size="17" '
          f'text-anchor="middle">{i+1}</text>')

    # --- aspects
    keep = {n:(a,o_,f) for n,a,o_,f in ASPECTS if n in aspect_set}
    lines = []
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            d = abs(planets[i][1] - planets[j][1]) % 360.0
            d = min(d, 360.0-d)
            for n,(a,orb,fam) in keep.items():
                if abs(d-a) <= orb:
                    lines.append((planets[i][1], planets[j][1], fam, 1.0 - abs(d-a)/orb))
                    break
    A('<g fill="none" stroke-linecap="round">')
    for l1,l2,fam,strength in sorted(lines, key=lambda t: t[3]):
        x1,y1 = pt(l1, R_IN, asc); x2,y2 = pt(l2, R_IN, asc)
        if fam == "tension":
            st, w, dash = GOLD, 0.55+0.55*strength, ''
        else:
            st, w, dash = GOLD_SOFT, 0.5+0.45*strength, ' stroke-dasharray="6 5"'
        A(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
          f'stroke="{st}" stroke-width="{w:.2f}" opacity="{0.45+0.4*strength:.2f}"{dash}/>')
    A('</g>')

    # --- planètes
    disp = spread([p[1] for p in planets], minsep)
    A('<g>')
    for (name, lon, retro), dl in zip(planets, disp):
        # repère exact sur le cercle des degrés
        x1,y1 = pt(lon, R_SIGN_IN, asc); x2,y2 = pt(lon, R_SIGN_IN-14, asc)
        A(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{GOLD}" stroke-width="1.1"/>')
        # trait de rappel vers le glyphe décalé
        gx,gy = pt(dl, R_PLANET+16, asc)
        A(f'<line x1="{x2:.2f}" y1="{y2:.2f}" x2="{gx:.2f}" y2="{gy:.2f}" stroke="{GOLD_PALE}" stroke-width="0.6"/>')
        px,py = pt(dl, R_PLANET, asc)
        A(f'<text x="{px:.2f}" y="{py+11:.2f}" fill="{GOLD}" font-size="29" text-anchor="middle">{GLYPH.get(name,"?")}\ufe0e</text>')
        dx,dy = pt(dl, R_PDEG, asc)
        A(f'<text x="{dx:.2f}" y="{dy+5:.2f}" fill="{INK}" font-size="13" text-anchor="middle" opacity="0.8">'
          f'{deg_label(lon)}{" ℞" if retro else ""}</text>')
    A('</g>')
    A('</svg>')
    return "".join(o)

# ---------------------------------------------------------------- démo
DEMO_PLANETS = [
    ("Soleil",   127.4, False), ("Lune",     18.9,  False), ("Mercure", 141.2, False),
    ("Vénus",    98.6,  False), ("Mars",     282.3, False), ("Jupiter", 55.1,  False),
    ("Saturne",  318.7, True),  ("Uranus",   36.4,  False), ("Neptune", 297.9, True),
    ("Pluton",   264.5, True),  ("Nœud Nord",212.8, True),  ("Chiron",  9.3,   False),
]
DEMO_CUSPS = [172.0, 200.5, 231.0, 262.0, 291.5, 320.0, 352.0, 20.5, 51.0, 82.0, 111.5, 140.0]

if __name__ == "__main__":
    open("/home/claude/plume/wheel.svg","w").write(build_wheel(DEMO_PLANETS, DEMO_CUSPS))
    print("ok")
