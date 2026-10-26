"""Tests pour pdf_strip_blanks — suppression des pages vides en export numérique.

Fixtures PDF générées à la volée via reportlab pour garder le test
hermétique (pas de dépendance aux assets).
"""
from __future__ import annotations
import io
import pytest
from pypdf import PdfReader
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

from services.pdf_strip_blanks import strip_blank_pages, MIN_TEXT_CHARS


def _make_pdf(pages: list[str]) -> bytes:
    """Génère un PDF A5 avec les textes donnés — chaîne vide = page vraiment blanche."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    for text in pages:
        if text:
            c.setFont('Helvetica', 12)
            c.drawString(50, 400, text)
        c.showPage()
    c.save()
    return buf.getvalue()


# ─── Cas de base ──────────────────────────────────────────────────────

def test_strip_removes_blank_pages():
    pdf = _make_pdf([
        'Page de contenu riche numéro un avec plein de mots.',
        '',  # VRAIMENT vide
        'Autre page de contenu riche numéro trois.',
    ])
    out = strip_blank_pages(pdf)
    assert len(PdfReader(io.BytesIO(out)).pages) == 2


def test_strip_keeps_rich_pages():
    pages = [f'Section {i} — contenu riche sur cette page {i}.' for i in range(1, 6)]
    pdf = _make_pdf(pages)
    out = strip_blank_pages(pdf)
    # Rien à retirer → PDF original renvoyé tel quel
    assert out == pdf
    assert len(PdfReader(io.BytesIO(out)).pages) == 5


def test_strip_removes_multiple_blanks():
    pdf = _make_pdf([
        'Section I avec contenu riche de plus de trente caractères visibles.',
        '',
        'Section II avec contenu riche aussi largement au-dessus du seuil.',
        '',
        '',
        'Section III finale avec contenu riche sur plus de trente chars.',
    ])
    out = strip_blank_pages(pdf)
    assert len(PdfReader(io.BytesIO(out)).pages) == 3


# ─── Garde-fous ───────────────────────────────────────────────────────

def test_strip_short_doc_untouched():
    pdf = _make_pdf(['', ''])  # 2 pages vides
    out = strip_blank_pages(pdf)
    # Garde-fou : docs ≤ 2 pages jamais touchés
    assert out == pdf


def test_strip_drop_guard_restores_original():
    """Si plus de 20% des pages sont jugées vides, on garde l'original."""
    # 10 pages dont 6 vides = 60% > 20% → drop guard déclenche
    pdf = _make_pdf([
        'Page 1 avec contenu suffisamment long pour passer le seuil.', '',
        'Page 3 avec contenu suffisamment long pour passer le seuil.', '', '',
        'Page 6 avec contenu suffisamment long pour passer le seuil.', '', '',
        'Page 9 avec contenu suffisamment long pour passer le seuil.', '',
    ])
    out = strip_blank_pages(pdf)
    assert out == pdf, 'Drop guard devrait avoir restauré l\'original'


def test_strip_empty_bytes_passthrough():
    assert strip_blank_pages(b'') == b''


def test_strip_corrupted_pdf_passthrough():
    """Si l'analyse pypdf échoue, on retourne l'input tel quel."""
    bad = b'not a pdf at all, just garbage'
    out = strip_blank_pages(bad)
    assert out == bad


# ─── Threshold ────────────────────────────────────────────────────────

def test_strip_threshold_boundary():
    """Un texte très court (header-only) est considéré vide."""
    short = 'A' * (MIN_TEXT_CHARS - 1)   # juste sous le seuil
    long  = 'A' * (MIN_TEXT_CHARS + 10)  # juste au-dessus
    pdf = _make_pdf([long, short, long])
    out = strip_blank_pages(pdf)
    assert len(PdfReader(io.BytesIO(out)).pages) == 2
