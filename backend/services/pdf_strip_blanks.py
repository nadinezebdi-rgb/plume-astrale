"""pdf_strip_blanks — Supprime les pages véritablement vides d'un PDF.

Contexte : les livres imprimés placent les divisions de parties sur
page recto (impaire) et insèrent une page blanche pour pousser le
divider au bon endroit. Ce pattern est intentionnel en reliure papier
mais parasite en PDF numérique où le lecteur se demande pourquoi des
pages blanches apparaissent entre deux sections.

Ce module :
  1. Analyse chaque page via pypdf (`extract_text()` + `page.images`).
  2. Marque une page comme vide SI ET SEULEMENT SI :
     - le texte extrait fait moins de `MIN_TEXT_CHARS` caractères,
     - ET la page ne contient aucune image.
     Ce double critère évite de retirer par erreur une page de titre
     courte, une page illustration pleine page, ou une queue de texte.
  3. Retire ces pages et renvoie le PDF compacté.
  4. Garde-fou : si > 20% des pages seraient retirées, on restaure
     l'original (seuil mal calibré ou PDF atypique).

Usage :
    from services.pdf_strip_blanks import strip_blank_pages
    cleaned_bytes = strip_blank_pages(pdf_bytes)
"""
from __future__ import annotations

import io
import logging

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

# Une page est jugée VIDE si :
#   (text.strip().length < MIN_TEXT_CHARS) AND (no images)
# Le header "PLUME ASTRALE" + folio fournit ≈ 15 chars → on prend 30 pour
# couvrir aussi les variantes "PLUME ASTRALE  32".
MIN_TEXT_CHARS = 30


def _page_is_blank(page) -> bool:
    """True si la page n'a que le header/footer + aucune image."""
    try:
        text = (page.extract_text() or '').strip()
    except Exception:
        return False  # safe default : garde la page
    if len(text) >= MIN_TEXT_CHARS:
        return False
    # Vérifie absence d'image
    try:
        img_count = len(list(page.images)) if hasattr(page, 'images') else 0
    except Exception:
        img_count = 0
    return img_count == 0


def strip_blank_pages(pdf_bytes: bytes, *,
                     min_text_chars: int = MIN_TEXT_CHARS) -> bytes:
    """Supprime les pages vides (text court + sans image) et retourne le PDF nettoyé.

    Si l'analyse échoue pour une raison quelconque, le PDF original est
    retourné intact — on préfère un PDF avec quelques pages vides plutôt
    qu'un PDF corrompu.
    """
    if not pdf_bytes:
        return pdf_bytes

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        n = len(reader.pages)
        if n <= 2:
            return pdf_bytes

        kept, dropped = [], []
        for i, page in enumerate(reader.pages):
            if _page_is_blank(page):
                dropped.append(i + 1)
            else:
                kept.append(i)

        if not dropped:
            return pdf_bytes

        # Garde-fou : si on retire plus de 20% des pages, quelque chose
        # cloche (seuil mal calibré ou PDF scanné). On restaure.
        if len(dropped) > max(5, n // 5):
            logger.warning(
                f'[strip_blanks] drop guard tripped: {len(dropped)}/{n} pages '
                f'would be removed, keeping original'
            )
            return pdf_bytes

        writer = PdfWriter()
        for i in kept:
            writer.add_page(reader.pages[i])

        buf = io.BytesIO()
        writer.write(buf)
        out = buf.getvalue()

        logger.info(
            f'[strip_blanks] removed {len(dropped)} blank pages '
            f'(positions {dropped}) · {n} → {len(kept)} pages · '
            f'{len(pdf_bytes)} → {len(out)} bytes'
        )
        return out
    except Exception as e:
        logger.exception(f'[strip_blanks] fatal: {e} — returning original')
        return pdf_bytes


__all__ = ['strip_blank_pages', 'MIN_TEXT_CHARS']
