"""Génère le PDF échantillon public avec filigrane 'EXTRAIT — Plume Astrale'.

Usage: python3 -m backend.scripts.add_sample_watermark
Sortie: /app/frontend/public/demos/theme-natal-sample.pdf
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


OUT_PATH = Path('/app/frontend/public/demos/theme-natal-sample.pdf')
WIDTH, HEIGHT = A5  # 148×210mm


def build_watermark_pdf() -> bytes:
    """PDF A5 d'une seule page : grand filigrane diagonal 'EXTRAIT' + ligne basse."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    c.saveState()
    # Grand filigrane diagonal centré
    c.translate(WIDTH / 2, HEIGHT / 2)
    c.rotate(30)
    c.setFillColor(HexColor('#B8935A'))
    c.setFillAlpha(0.12)
    c.setFont('Helvetica-Bold', 72)
    c.drawCentredString(0, 0, 'EXTRAIT')
    c.restoreState()
    # Bandeau bas discret
    c.setFillColor(HexColor('#0B1A2E'))
    c.setFillAlpha(0.55)
    c.setFont('Helvetica', 7)
    c.drawCentredString(
        WIDTH / 2,
        14,
        'EXTRAIT — Plume Astrale · Votre livre personnalisé contiendra ~46 pages',
    )
    c.showPage()
    c.save()
    return buf.getvalue()


def regenerate_source_pdf() -> bytes:
    """Regénère le PDF Amélie démo avec le moteur V2."""
    os.environ['USE_V2_NATAL_ENGINE'] = '1'
    from routes.admin_preview_v3 import _demo_data  # noqa: WPS433
    from services.natal_pdf_adapter import generate_manuscrit_pdf  # noqa: WPS433

    d = _demo_data('Amélie')
    return generate_manuscrit_pdf(
        user_data=d['user_data'],
        planets_data=d['planets_data'],
        aspects_raw=d['aspects_raw'],
        house_cusps_raw=d['cusps_raw'],
    )


def apply_watermark(source_pdf: bytes, watermark_pdf: bytes) -> bytes:
    reader = PdfReader(io.BytesIO(source_pdf))
    wm_reader = PdfReader(io.BytesIO(watermark_pdf))
    wm_page = wm_reader.pages[0]
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(wm_page)
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def main() -> None:
    print('[watermark] regenerating source demo PDF…')
    source = regenerate_source_pdf()
    print(f'[watermark] source: {len(source)} bytes')
    wm = build_watermark_pdf()
    print(f'[watermark] overlay: {len(wm)} bytes')
    merged = apply_watermark(source, wm)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(merged)
    print(f'[watermark] wrote {len(merged)} bytes → {OUT_PATH}')


if __name__ == '__main__':
    main()
