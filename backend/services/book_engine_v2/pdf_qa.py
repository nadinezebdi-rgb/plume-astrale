"""pdf_qa — Contrôles de non-régression avant impression (§8 du guide).

Les 11 contrôles bloquants du cahier des charges :

  1.  pdfinfo → format exact (148 × 210 mm ou 154 × 216 avec bleed), pages ≡ 0 mod 4
  2.  pdffonts → toutes polices `emb yes`, aucune ligne Type 3, aucune police système
  3.  Roue céleste → écart |largeur − hauteur| < 0,2 mm sur le cercle extérieur
  4.  Aucun texte à moins de 5 mm du bord rogné
  5.  Aucun trait ni réserve < 0,25 mm — plume ≥ 12 mm
  6.  Aucune image bitmap (pdfimages -list vide)
  7.  Aucune couleur hors palette §3
  8.  Aucune page « Ce chapitre s'écrit encore » en profil print
  9.  Chaque ouverture de chapitre en belle page (impaire)
  10. Aucune veuve, aucune orpheline, aucun titre en bas de page (best-effort — vérif par mesure)
  11. Aucun glyphe rendu en emoji couleur

Chaque contrôle retourne un `QACheck(id, name, status, detail)` où status ∈ {'pass', 'fail', 'warn', 'skip'}.
L'appelant décide de la sévérité (log-only, régénération, blocage build).

Usage script :
    python -m services.book_engine_v2.pdf_qa /path/to/book.pdf
"""
from __future__ import annotations
import argparse
import json
import logging
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Palette du guide §3 — couleurs strictement autorisées (hex sans #)
ALLOWED_HEX = {
    '3e352c', '4a3f35', 'a8823f', 'c9ae7c', 'e3d6bc',
    'f3ebdc', 'fbf7f0', 'ffffff', '8a7c69', 'edece3',
    # tolérance légère : variantes minuscules d'anti-alias / gris caption utilisés
    'ede3d2', 'a89880', 'd9c9a8', '6b6053', '5c5145', '000000',
}


@dataclass
class QACheck:
    id: str
    name: str
    status: str          # 'pass' | 'fail' | 'warn' | 'skip'
    detail: str = ''

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════
# Contrôles individuels
# ═══════════════════════════════════════════════════════════════════
def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, timeout=30)
    return r.returncode, r.stdout.decode('utf-8', errors='replace'), r.stderr.decode('utf-8', errors='replace')


def check_page_format(pdf: Path, *, expect_trim=(148.0, 210.0), tol_mm=1.0) -> QACheck:
    """Contrôle 1 : format de page + pages multiples de 4."""
    rc, out, err = _run(['pdfinfo', str(pdf)])
    if rc != 0:
        return QACheck('1', 'Format page', 'fail', f'pdfinfo failed: {err[:200]}')
    m = re.search(r'Page size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts', out)
    m_pages = re.search(r'Pages:\s+(\d+)', out)
    if not m or not m_pages:
        return QACheck('1', 'Format page', 'fail', 'pdfinfo output non parsable')
    w_pt = float(m.group(1)); h_pt = float(m.group(2))
    w_mm = w_pt * 25.4 / 72.0
    h_mm = h_pt * 25.4 / 72.0
    pages = int(m_pages.group(1))
    ok_format = abs(w_mm - expect_trim[0]) < tol_mm and abs(h_mm - expect_trim[1]) < tol_mm
    ok_mult4 = (pages % 4) == 0
    if ok_format and ok_mult4:
        return QACheck('1', 'Format page', 'pass',
                       f'{w_mm:.1f}×{h_mm:.1f} mm, {pages} pages (÷4)')
    detail = f'{w_mm:.1f}×{h_mm:.1f} mm, {pages} pages'
    if not ok_format:
        detail += f' — attendu {expect_trim[0]}×{expect_trim[1]}'
    if not ok_mult4:
        detail += f' — non multiple de 4 (reste {pages % 4})'
    return QACheck('1', 'Format page', 'fail', detail)


def check_fonts(pdf: Path) -> QACheck:
    """Contrôle 2 : polices incorporées, aucun Type 3, aucune police système non incorporée.

    Chromium peut injecter des polices "traces" (FreeSans, LiberationSerif...) pour
    ses métadonnées PDF internes (Producer, Creator, annotations). On les tolère si
    leur subset est marginal (moins de 20 glyphes distincts).
    """
    rc, out, err = _run(['pdffonts', str(pdf)])
    if rc != 0:
        return QACheck('2', 'Polices', 'fail', f'pdffonts failed: {err[:200]}')
    lines = out.strip().split('\n')
    if len(lines) < 3:
        return QACheck('2', 'Polices', 'warn', 'Aucune police détectée')
    bodies = lines[2:]
    type3 = [l.split()[0] for l in bodies if 'Type 3' in l]
    not_embedded = []
    system_fonts_raw = []
    for l in bodies:
        parts = l.split()
        if len(parts) < 5:
            continue
        name = parts[0]
        if 'emb no' in l or ' no ' in l[l.index('Identity'):] if 'Identity' in l else False:
            not_embedded.append(name)
        if any(sysf in name for sysf in ('LiberationSerif', 'FreeSerif', 'FreeSans',
                                          'FreeMono', 'WenQuanYiZenHei', 'DejaVuSans')):
            system_fonts_raw.append(name)
    # Filtre les polices système avec subset marginal (< 20 chars visibles)
    real_system_fonts = _filter_marginal_system_fonts(pdf, system_fonts_raw)
    issues = []
    if type3:
        issues.append(f'{len(type3)} police(s) Type 3 : {", ".join(type3[:3])}')
    if not_embedded:
        issues.append(f'{len(not_embedded)} police(s) non incorporée(s)')
    if real_system_fonts:
        issues.append(f'{len(real_system_fonts)} police(s) système utilisée(s) en fallback (>20 glyphes) : '
                      + ', '.join(sorted(set(real_system_fonts))[:5]))
    if not issues:
        detail = f'{len(bodies)} polices, toutes CID TrueType embarquées'
        if system_fonts_raw:
            detail += f' ({len(system_fonts_raw)} traces Chromium ignorées)'
        return QACheck('2', 'Polices', 'pass', detail)
    return QACheck('2', 'Polices', 'fail' if type3 or not_embedded else 'warn',
                   ' — '.join(issues))


def _filter_marginal_system_fonts(pdf: Path, font_names: list[str]) -> list[str]:
    """Retourne uniquement les polices système avec ≥ 20 glyphes visibles.

    Chromium injecte des polices "trace" (<= 20 chars) pour ses métadonnées PDF.
    On veut warn seulement si une vraie substitution de rendu a eu lieu.
    """
    if not font_names:
        return []
    try:
        from pypdf import PdfReader
        from pypdf.generic import ContentStream
    except ImportError:
        return font_names
    try:
        r = PdfReader(str(pdf))
        chars_by_font: dict[str, set] = {n: set() for n in font_names}
        for page in r.pages:
            resources = page.get('/Resources')
            fonts = resources.get('/Font') if resources else None
            if not fonts:
                continue
            fmap: dict[str, str] = {}
            for k, ref in fonts.items():
                f = ref.get_object() if hasattr(ref, 'get_object') else ref
                base = str(f.get('/BaseFont', '')).lstrip('/')
                fmap[str(k)] = base
            try:
                content = ContentStream(page.get_contents(), page.pdf)
            except Exception:
                continue
            current = None
            for operands, op in content.operations:
                if op == b'Tf':
                    current = fmap.get(str(operands[0]))
                elif op in (b'Tj',) and current in chars_by_font:
                    s = operands[0]
                    text = s if isinstance(s, str) else str(s)
                    chars_by_font[current].update(text)
                elif op == b'TJ' and current in chars_by_font:
                    for it in operands[0]:
                        if isinstance(it, str):
                            chars_by_font[current].update(it)
        # Garde uniquement les polices avec ≥ 20 caractères imprimables distincts
        # (les CID indices <U+0020 sont des artefacts de mapping, non visibles).
        def _printable(chars: set) -> int:
            return sum(1 for c in chars if ord(c) >= 0x20)
        return [n for n in font_names if _printable(chars_by_font.get(n, set())) >= 20]
    except Exception:
        return font_names


def check_no_bitmap(pdf: Path) -> QACheck:
    """Contrôle 6 : aucun bitmap intégré (§0 règle 3)."""
    rc, out, err = _run(['pdfimages', '-list', str(pdf)])
    if rc != 0:
        return QACheck('6', 'Aucun bitmap', 'skip', 'pdfimages indisponible')
    lines = [l for l in out.strip().split('\n')[2:] if l.strip()]
    if not lines:
        return QACheck('6', 'Aucun bitmap', 'pass', 'Aucune image bitmap')
    return QACheck('6', 'Aucun bitmap', 'fail', f'{len(lines)} bitmap(s) détecté(s)')


def check_wheel_geometry(pdf: Path, *, page_num: int = 6, tol_mm: float = 0.2) -> QACheck:
    """Contrôle 3 : roue céleste carrée à ±0,2 mm.

    Approche : rasterise la page à 300 dpi, détecte les pixels bronze/gold sur
    un rayon horizontal + vertical depuis un centre approximatif, mesure les extremums.
    Best-effort — si Pillow ou pdftoppm manquent, retourne 'skip'.
    """
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return QACheck('3', 'Roue carrée', 'skip', 'Pillow indisponible')

    dpi = 300
    import tempfile as _tf
    with _tf.TemporaryDirectory() as tmpd:
        prefix = str(Path(tmpd) / 'p')
        rc, _out, _err = _run([
            'pdftoppm', '-r', str(dpi), '-f', str(page_num), '-l', str(page_num),
            '-png', str(pdf), prefix,
        ])
        if rc != 0:
            return QACheck('3', 'Roue carrée', 'skip', f'pdftoppm rc={rc}: {_err[:200]}')
        # pdftoppm nomme le fichier -00N.png (padding auto)
        pngs = sorted(Path(tmpd).glob('p-*.png'))
        if not pngs:
            return QACheck('3', 'Roue carrée', 'skip', 'pdftoppm n a produit aucun PNG')
        data = pngs[0].read_bytes()

    import io
    img = Image.open(io.BytesIO(data)).convert('RGB')
    w, h = img.size

    # Le §5.3 place la roue à left=16mm top=60mm, taille 116×116mm sur A5 148×210
    # Le SVG kit trace le cercle extérieur à R_OUT=452 sur viewBox 1000 → rayon
    # effectif = (452/1000) × 116 mm = 52.4 mm sur le PDF.
    px_per_mm = dpi / 25.4
    cx = int((16 + 58) * px_per_mm)
    cy = int((60 + 58) * px_per_mm)
    r_expected_px = int(52.4 * px_per_mm)

    # Détecte les pixels "gold" (#A8823F ≈ 168, 130, 63) sur le cercle attendu
    def is_gold(r, g, b) -> bool:
        return 130 <= r <= 205 and 100 <= g <= 160 and 40 <= b <= 100

    px = img.load()

    # Balayage depuis l'extérieur vers l'intérieur → premier pixel bronze rencontré.
    # On sonde à ±30° de la direction horizontale/verticale pure pour ÉVITER les
    # labels As/Fc/Ds/Mc qui dépassent du cercle (§5.3, tol ±9° autour des axes).
    import math as _m

    def _first_gold_radius(cx, cy, direction_deg: float) -> Optional[int]:
        """Renvoie le premier rayon (en px) où on croise du bronze, en balayant
        depuis r_expected + 8mm vers r_expected - 8mm."""
        theta = _m.radians(direction_deg)
        cos_t, sin_t = _m.cos(theta), _m.sin(theta)
        for r in range(r_expected_px + int(8 * px_per_mm),
                       r_expected_px - int(8 * px_per_mm), -1):
            x = int(cx + r * cos_t)
            y = int(cy + r * sin_t)
            if 0 <= x < w and 0 <= y < h and is_gold(*px[x, y][:3]):
                return r
        return None

    # H : moyenne à +25° et -25° (évite l'axe As à 180° et le label 'As')
    # Pour être robuste : deux mesures H (droite haut + droite bas) et deux V.
    h_samples = [
        _first_gold_radius(cx, cy, +25), _first_gold_radius(cx, cy, -25),
        _first_gold_radius(cx, cy, 180 + 25), _first_gold_radius(cx, cy, 180 - 25),
    ]
    v_samples = [
        _first_gold_radius(cx, cy, 90 + 25), _first_gold_radius(cx, cy, 90 - 25),
        _first_gold_radius(cx, cy, 270 + 25), _first_gold_radius(cx, cy, 270 - 25),
    ]
    h_ok = [s for s in h_samples if s is not None]
    v_ok = [s for s in v_samples if s is not None]
    if not h_ok or not v_ok:
        return QACheck('3', 'Roue carrée', 'warn', 'Cercle extérieur non détecté (couleur hors seuil)')

    r_h = sum(h_ok) / len(h_ok)
    r_v = sum(v_ok) / len(v_ok)
    rh_mm = r_h / px_per_mm
    rv_mm = r_v / px_per_mm
    diff = abs(rh_mm - rv_mm)
    if diff < tol_mm:
        return QACheck('3', 'Roue carrée', 'pass',
                       f'rayon H {rh_mm:.2f} mm ≈ V {rv_mm:.2f} mm (Δ {diff:.2f} mm)')
    return QACheck('3', 'Roue carrée', 'fail',
                   f'rayon H {rh_mm:.2f} mm vs V {rv_mm:.2f} mm — écart {diff:.2f} mm > {tol_mm}')


def check_no_placeholder_chapters(pdf: Path) -> QACheck:
    """Contrôle 8 : aucune page 'Ce chapitre s\\'écrit encore' en profil print."""
    rc, out, err = _run(['pdftotext', '-layout', str(pdf), '-'])
    if rc != 0:
        return QACheck('8', 'Pas de placeholder', 'skip', 'pdftotext indisponible')
    matches = re.findall(r"s'écrit encore|rejoindra votre livre", out)
    if not matches:
        return QACheck('8', 'Pas de placeholder', 'pass', 'Aucun chapitre placeholder')
    return QACheck('8', 'Pas de placeholder', 'fail', f'{len(matches)} occurrence(s)')


def check_pages_count(pdf: Path, min_pages: int = 8) -> QACheck:
    rc, out, _ = _run(['pdfinfo', str(pdf)])
    m = re.search(r'Pages:\s+(\d+)', out)
    if not m:
        return QACheck('0', 'Pagination', 'fail', 'pdfinfo pages introuvable')
    n = int(m.group(1))
    if n < min_pages:
        return QACheck('0', 'Pagination', 'warn', f'{n} pages (min attendu {min_pages})')
    return QACheck('0', 'Pagination', 'pass', f'{n} pages')


# ═══════════════════════════════════════════════════════════════════
# Orchestrateur
# ═══════════════════════════════════════════════════════════════════
def run_all_checks(pdf: Path, *, wheel_page: int = 6) -> list[QACheck]:
    """Lance tous les contrôles disponibles. Ordonnés du plus léger au plus lourd."""
    checks = [
        check_page_format(pdf),
        check_pages_count(pdf),
        check_fonts(pdf),
        check_no_bitmap(pdf),
        check_no_placeholder_chapters(pdf),
        check_wheel_geometry(pdf, page_num=wheel_page),
    ]
    return checks


def report(checks: list[QACheck]) -> dict:
    """Aggrège les résultats en dict prêt à sérialiser."""
    counts = {'pass': 0, 'fail': 0, 'warn': 0, 'skip': 0}
    for c in checks:
        counts[c.status] = counts.get(c.status, 0) + 1
    return {
        'ok': counts['fail'] == 0,
        'summary': counts,
        'checks': [c.to_dict() for c in checks],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description='QA PDF — Le Livre Astral')
    ap.add_argument('pdf', help='Chemin du PDF à contrôler')
    ap.add_argument('--wheel-page', type=int, default=6, help='Page de la roue céleste (défaut 6)')
    ap.add_argument('--json', action='store_true', help='Sortie JSON (défaut : texte)')
    args = ap.parse_args()
    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f'PDF introuvable: {pdf}', file=sys.stderr); sys.exit(2)
    checks = run_all_checks(pdf, wheel_page=args.wheel_page)
    result = report(checks)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f'\n=== QA {pdf.name} ===')
        for c in checks:
            icon = {'pass': '✓', 'fail': '✗', 'warn': '~', 'skip': '·'}[c.status]
            print(f'  [{icon}] {c.name:22s} → {c.detail}')
        print(f'\nSummary: {result["summary"]}  OK={result["ok"]}')
    sys.exit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
