"""Génère le PDF échantillon public de synastrie avec filigrane 'EXTRAIT'.

Usage: python3 -m backend.scripts.add_synastrie_sample_watermark
Sortie: /app/frontend/public/demos/synastrie-sample.pdf
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


OUT_PATH = Path('/app/frontend/public/demos/synastrie-sample.pdf')
WIDTH, HEIGHT = A5


# Deux personnes demo (anonymisees)
PERSON1 = {
    'prenom': 'Lou',
    'birth_date': '1993-06-21',
    'birth_time': '08:15',
    'birth_place': 'Paris, France',
    'latitude': 48.8566,
    'longitude': 2.3522,
    'gender': 'F',
}
PERSON2 = {
    'prenom': 'Noe',
    'birth_date': '1991-10-07',
    'birth_time': '21:40',
    'birth_place': 'Lyon, France',
    'latitude': 45.7640,
    'longitude': 4.8357,
    'gender': 'M',
}


def build_watermark_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    c.saveState()
    c.translate(WIDTH / 2, HEIGHT / 2)
    c.rotate(30)
    c.setFillColor(HexColor('#B8935A'))
    c.setFillAlpha(0.12)
    c.setFont('Helvetica-Bold', 72)
    c.drawCentredString(0, 0, 'EXTRAIT')
    c.restoreState()
    c.setFillColor(HexColor('#0B1A2E'))
    c.setFillAlpha(0.55)
    c.setFont('Helvetica', 7)
    c.drawCentredString(
        WIDTH / 2,
        14,
        'EXTRAIT — Plume Astrale · Votre rapport synastrie complet contiendra ~32 pages',
    )
    c.showPage()
    c.save()
    return buf.getvalue()


def generate_source_pdf() -> bytes:
    """Genere l'extrait synastrie 3 pages sans enrichissement LLM (demo rapide)."""
    from services.synastrie_pdf_generator import generate_synastrie_extract  # noqa: WPS433
    return generate_synastrie_extract(PERSON1, PERSON2, enriched=None)


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
    print('[synastrie-watermark] generating demo extract PDF…')
    source = generate_source_pdf()
    print(f'[synastrie-watermark] source: {len(source)} bytes')
    wm = build_watermark_pdf()
    print(f'[synastrie-watermark] overlay: {len(wm)} bytes')
    merged = apply_watermark(source, wm)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(merged)
    print(f'[synastrie-watermark] wrote {len(merged)} bytes → {OUT_PATH}')


if __name__ == '__main__':
    main()
