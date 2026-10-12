"""natal_cover_pdf — Génère la couverture PDF Lulu A5 hardcover (3 panneaux).
================================================================================

Lulu exige deux PDF séparés pour le livre relié :
  • Intérieur (notre PDF existant, 42 pages A5)
  • Couverture (une seule page landscape qui contient 4e-couv + dos + 1re-couv)

Spec A5 hardcover (casewrap/casebound) :
  • Trim A5 : 148 × 210 mm (portrait final)
  • Bleed : 15 mm sur chaque côté extérieur (hardcover) — zone de retour
  • Spine width : fonction du nombre de pages × 0.0025" (papier 60 lb)
    → ~0.21 inch (5.3 mm) pour 42 pages, mais Lulu fournit la vraie valeur
      via le template calculator. Pour le mock, on utilise une approximation.

Design : couleur sable crème (#F0E6D2), typo Cormorant Garamond, aucune mention
de Soléna, visuel Plume Astrale (plume dorée + roue natale discrète).
"""
from __future__ import annotations
import base64
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

ASSETS_ROOT = Path('/app/backend/assets/book/assets')
COVERS_ROOT = Path('/app/backend/assets/pdf_covers')


def _asset_b64(name: str, root: Path = ASSETS_ROOT) -> str:
    p = root / name
    if not p.exists():
        return ''
    data = p.read_bytes()
    mime = 'image/svg+xml' if name.endswith('.svg') else 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(data).decode('ascii')


def _spine_width_mm(page_count: int, paper_bulk: float = 0.0635) -> float:
    """Calcule la largeur du dos en mm.

    paper_bulk : mm par page recto-verso. 0.0635 mm = 60 lb cream text standard
    Lulu. Pour un hardcover, on ajoute ~3 mm de rigidité carton.
    """
    pages = max(page_count, 32)
    base = pages * paper_bulk
    return round(base + 3.0, 2)


def build_cover_html(
    *, first_name: str, birth_date_fr: str, page_count: int = 42,
    spine_width_mm: float | None = None,
) -> str:
    """Produit l'HTML prêt à être rendu par Chromium en PDF cover.

    Dimensions : A5 hardcover standard Lulu
      trim_w = 148 mm, trim_h = 210 mm
      bleed = 15 mm
      cover width total = 2 × (148 + 15) + spine + 15*2 = 326 + spine + 30
      cover height total = 210 + 15*2 = 240 mm
    """
    spine = spine_width_mm if spine_width_mm is not None else _spine_width_mm(page_count)
    trim_w, trim_h, bleed = 148.0, 210.0, 15.0
    total_w = 2 * trim_w + spine + 2 * bleed
    total_h = trim_h + 2 * bleed

    plume_b64 = _asset_b64('plume.svg')
    plume_fine_b64 = _asset_b64('plume-fine.svg')
    wheel_b64 = _asset_b64('natal_hero.png', root=COVERS_ROOT)

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<title>Couverture — Thème Natal {first_name}</title>
<style>
@page {{
  size: {total_w}mm {total_h}mm;
  margin: 0;
}}
html, body {{ margin: 0; padding: 0; width: {total_w}mm; height: {total_h}mm;
              background: #F0E6D2; font-family: 'Cormorant Garamond', Georgia, serif;
              color: #1C1B26; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.cover-wrap {{
  position: relative; width: {total_w}mm; height: {total_h}mm;
  background: linear-gradient(135deg, #F0E6D2 0%, #E8DBC0 50%, #F0E6D2 100%);
  overflow: hidden;
}}
/* Grain subtil */
.cover-wrap::after {{
  content: ''; position: absolute; inset: 0;
  background-image: radial-gradient(rgba(168,130,63,0.05) 1px, transparent 1px);
  background-size: 3mm 3mm; pointer-events: none;
}}
/* Panneau 4e couverture (dos arrière) : à gauche */
.back {{
  position: absolute; top: 0; left: 0;
  width: {trim_w + bleed}mm; height: {total_h}mm;
  padding: {bleed + 25}mm {bleed + 15}mm {bleed + 25}mm {bleed + 20}mm;
  box-sizing: border-box;
  display: flex; flex-direction: column; justify-content: space-between;
}}
.back__plume {{ width: 16mm; opacity: 0.55; margin-bottom: 10mm; }}
.back__pitch {{ font-size: 13pt; line-height: 1.55; color: #3A3022; font-style: italic;
                max-width: 95mm; }}
.back__pitch em {{ color: #A8823F; font-style: italic; font-weight: 500; }}
.back__footer {{ display: flex; align-items: center; justify-content: space-between;
                 font-size: 8pt; letter-spacing: 0.18em; text-transform: uppercase;
                 color: #8B7355; }}
.back__brand {{ font-family: 'Cinzel', 'Cormorant Garamond', serif; font-weight: 500; }}

/* Dos (spine) : vertical au centre */
.spine {{
  position: absolute; top: 0; left: {trim_w + bleed}mm;
  width: {spine}mm; height: {total_h}mm;
  background: #E8DBC0;
  display: flex; flex-direction: column; align-items: center; justify-content: space-between;
  padding: {bleed + 18}mm 0; box-sizing: border-box;
}}
.spine__title {{
  writing-mode: vertical-rl; transform: rotate(180deg);
  font-family: 'Cinzel', serif; font-size: 10pt; letter-spacing: 0.32em;
  text-transform: uppercase; color: #A8823F; font-weight: 500;
}}
.spine__plume {{ width: {max(spine * 0.6, 4)}mm; opacity: 0.6; }}
.spine__name {{
  writing-mode: vertical-rl; transform: rotate(180deg);
  font-family: 'Cormorant Garamond', serif; font-size: 10pt; color: #3A3022; font-style: italic;
}}

/* 1re couverture : à droite */
.front {{
  position: absolute; top: 0; left: {trim_w + bleed + spine}mm;
  width: {trim_w + bleed}mm; height: {total_h}mm;
  padding: {bleed + 25}mm {bleed + 20}mm {bleed + 25}mm {bleed + 15}mm;
  box-sizing: border-box;
  display: flex; flex-direction: column; align-items: center; text-align: center;
}}
.front__brand {{
  font-size: 8pt; letter-spacing: 0.42em; text-transform: uppercase;
  color: #A8823F; font-family: 'Cinzel', serif; margin-bottom: 10mm;
}}
.front__wheel {{
  width: 80mm; height: 80mm; margin: 2mm auto 8mm; opacity: 0.9;
  border-radius: 50%; overflow: hidden;
  filter: sepia(0.3) hue-rotate(10deg) saturate(0.8) brightness(1.1);
}}
.front__wheel img {{ width: 100%; height: 100%; object-fit: cover; }}
.front__title {{
  font-family: 'Cormorant Garamond', serif; font-weight: 300; font-size: 32pt;
  line-height: 1.08; color: #1C1B26; margin: 0 0 6mm;
}}
.front__title em {{ font-style: italic; color: #A8823F; }}
.front__kicker {{
  font-size: 11pt; color: #3A3022; font-style: italic; max-width: 100mm;
  margin: 0 auto 14mm; line-height: 1.4;
}}
.front__name {{
  margin-top: auto; padding-top: 10mm; border-top: 0.5pt solid #A8823F;
  font-family: 'Cormorant Garamond', serif; font-weight: 400;
  font-size: 16pt; color: #1C1B26;
}}
.front__date {{
  margin-top: 2mm; font-size: 10pt; color: #8B7355; font-style: italic;
}}
.front__plume {{
  position: absolute; bottom: {bleed + 10}mm; left: 50%; transform: translateX(-50%);
  width: 14mm; opacity: 0.7;
}}

/* Trimline markers (invisibles à l'impression - juste pour QA) */
.trim-marker {{ display: none; }}
</style>
</head>
<body>
<div class="cover-wrap">
  <!-- 4e de couverture -->
  <div class="back">
    <div>
      {'<img class="back__plume" src="' + plume_fine_b64 + '" alt=""/>' if plume_fine_b64 else ''}
      <p class="back__pitch">
        Ce livre n'est pas un livre comme les autres. <em>Il n'a été écrit qu'une fois,
        et il n'a été écrit que pour vous.</em>
      </p>
      <p class="back__pitch" style="margin-top: 6mm;">
        Il porte la carte d'un ciel précis — le vôtre — tel qu'il brillait à votre premier souffle.
        Dix planètes, douze maisons, les aspects qui composent votre nuance unique.
      </p>
      <p class="back__pitch" style="margin-top: 6mm;">
        Un objet rare, à poser sur une étagère, à relire aux grandes étapes de votre vie.
      </p>
    </div>
    <div class="back__footer">
      <span class="back__brand">Plume Astrale</span>
      <span>Édition personnelle</span>
    </div>
  </div>

  <!-- Dos (spine) -->
  <div class="spine">
    <div class="spine__title">Thème Natal</div>
    {'<img class="spine__plume" src="' + plume_b64 + '" alt=""/>' if plume_b64 else ''}
    <div class="spine__name">{first_name}</div>
  </div>

  <!-- 1re de couverture -->
  <div class="front">
    <div class="front__brand">Plume Astrale</div>
    {'<div class="front__wheel"><img src="' + wheel_b64 + '" alt=""/></div>' if wheel_b64 else ''}
    <h1 class="front__title">Le Ciel<br/><em>de {first_name}</em></h1>
    <p class="front__kicker">
      Votre thème natal, dévoilé.<br/>
      Un portrait céleste à votre nom.
    </p>
    <div class="front__name">{first_name}</div>
    {'<div class="front__date">Né·e le ' + birth_date_fr + '</div>' if birth_date_fr else ''}
    {'<img class="front__plume" src="' + plume_b64 + '" alt=""/>' if plume_b64 else ''}
  </div>
</div>
</body>
</html>
"""


def _find_chromium() -> str:
    for cand in ('/usr/bin/chromium', '/usr/bin/chromium-browser',
                  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'):
        if os.path.exists(cand):
            return cand
    raise RuntimeError('No Chromium binary found')


def render_cover_pdf(
    *, first_name: str, birth_date_fr: str = '', page_count: int = 42,
) -> bytes:
    """Rend la couverture Lulu A5 hardcover en PDF (une seule page landscape).

    Retourne les bytes PDF prêts à être uploadés sur un stockage pour Lulu.
    """
    html = build_cover_html(
        first_name=first_name, birth_date_fr=birth_date_fr, page_count=page_count,
    )
    chrome = _find_chromium()
    with tempfile.TemporaryDirectory() as td:
        html_path = Path(td) / 'cover.html'
        pdf_path = Path(td) / 'cover.pdf'
        html_path.write_text(html, encoding='utf-8')
        cmd = [
            chrome, '--headless=new', '--no-sandbox', '--disable-gpu',
            '--disable-dev-shm-usage',
            '--no-pdf-header-footer',
            f'--print-to-pdf={pdf_path}',
            f'file://{html_path}',
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=60)
            if r.returncode != 0 or not pdf_path.exists():
                logger.error(f'[cover_pdf] chromium stderr: {r.stderr.decode()[:500]}')
                raise RuntimeError(f'Chromium cover render failed: {r.returncode}')
            return pdf_path.read_bytes()
        except subprocess.TimeoutExpired:
            raise RuntimeError('Chromium timeout (cover render)')


__all__ = ['render_cover_pdf', 'build_cover_html', '_spine_width_mm']
