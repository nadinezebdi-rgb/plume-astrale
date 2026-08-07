"""
pdf_multipass_toc.py — sommaire dynamique à double passage pour les PDFs Plume Astrale.

reportlab n'expose pas nativement les numéros de page depuis les flowables. On
utilise donc un mécanisme éprouvé :

  1. Chaque chapitre est précédé d'un `ChapterMarker(chapter_id)` — un flowable
     invisible (`wrap()` retourne (0,0)).
  2. On sous-classe `SimpleDocTemplate` avec un `afterFlowable(flow)` qui, quand
     il rencontre un `ChapterMarker`, appelle `self.notify('TOCEntry', ...)` pour
     enregistrer (chapter_id, self.page).
  3. On fait un premier build vers /dev/null (buffer temporaire) : à la fin, on
     dispose d'un mapping {chapter_id → page_number}.
  4. On reconstruit le story en remplaçant les entrées TOC avec les vraies
     valeurs, puis un second build final vers le buffer de sortie.

Utilisation :

    from services.pdf_multipass_toc import build_with_toc, chapter_marker

    def build_story(page_map=None):
        story = []
        # ... cover, TOC (avec page_map si dispo)
        story.append(chapter_marker('chap_intro'))
        # ... intro
        return story

    pdf_bytes = build_with_toc(build_story, doc_kwargs, bg_callback)

Fallback : si le premier passage échoue, on retourne le second passage sans
numéros — jamais d'erreur bloquante.
"""
from __future__ import annotations
import logging
from io import BytesIO
from typing import Callable, Dict, Optional
from reportlab.platypus import SimpleDocTemplate, Flowable, PageBreak
from reportlab.lib.pagesizes import A4

logger = logging.getLogger(__name__)


class ChapterMarker(Flowable):
    """Flowable invisible qui déclare la position d'un chapitre dans le doc."""

    def __init__(self, chapter_id: str):
        super().__init__()
        self.chapter_id = chapter_id
        self._chapter_id = chapter_id  # accès direct pour afterFlowable

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        pass

    def __repr__(self):
        return f'<ChapterMarker {self.chapter_id}>'


def chapter_marker(chapter_id: str) -> ChapterMarker:
    """Alias fonctionnel : préférer cet import dans les modules PDF."""
    return ChapterMarker(chapter_id)


class _TrackingDoc(SimpleDocTemplate):
    """SimpleDocTemplate qui capte les positions de chapter_marker."""

    def __init__(self, *args, page_map: Optional[Dict[str, int]] = None, **kw):
        super().__init__(*args, **kw)
        self._page_map: Dict[str, int] = {} if page_map is None else page_map

    def afterFlowable(self, flow):
        cid = getattr(flow, '_chapter_id', None)
        if cid:
            # self.page = numéro de la page où le marker apparaît
            self._page_map[cid] = self.page


def build_with_toc(
    build_story: Callable[[Optional[Dict[str, int]]], list],
    doc_kwargs: dict,
    on_first_page: Optional[Callable] = None,
    on_later_pages: Optional[Callable] = None,
) -> bytes:
    """Effectue les 2 passes reportlab et retourne le PDF final.

    Args:
        build_story : fonction qui, appelée avec un dict {chapter_id → page_number}
                      (ou None pour la 1ère passe), retourne la liste de flowables.
        doc_kwargs  : kwargs pour SimpleDocTemplate (pagesize, margins, title, ...)
        on_first_page / on_later_pages : callbacks pour doc.build()

    Returns:
        Les bytes du PDF final (2e passe).
    """
    # ─── PASSE 1 : dry-run pour capturer les pages ───
    page_map: Dict[str, int] = {}
    try:
        dry_buffer = BytesIO()
        dry_doc = _TrackingDoc(dry_buffer, page_map=page_map, **doc_kwargs)
        dry_story = build_story(None)  # None = passe 1
        dry_doc.build(
            dry_story,
            onFirstPage=on_first_page or (lambda c, d: None),
            onLaterPages=on_later_pages or (lambda c, d: None),
        )
    except Exception as e:
        logger.warning(f'[multipass_toc] first pass failed: {e} — fallback single-pass')
        page_map = {}

    # ─── PASSE 2 : build final avec le mapping ───
    final_buffer = BytesIO()
    final_doc = SimpleDocTemplate(final_buffer, **doc_kwargs)
    final_story = build_story(page_map or None)
    final_doc.build(
        final_story,
        onFirstPage=on_first_page or (lambda c, d: None),
        onLaterPages=on_later_pages or (lambda c, d: None),
    )
    final_buffer.seek(0)
    return final_buffer.getvalue()
