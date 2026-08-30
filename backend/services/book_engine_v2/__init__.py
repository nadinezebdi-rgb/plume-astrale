"""book_engine_v2 — Nouveau moteur PDF Chromium/HTML/CSS (LOT 4, guide 2026-02).

Point d'entrée principal : `render_manuscript_to_pdf_v2(manuscript, profile='print')`.
Reste iso-signature avec le moteur v1 pour permettre un feature-flag facile.
"""
from .renderer import (
    render_manuscript_to_html,
    render_manuscript_to_pdf_v2,
)

__all__ = ['render_manuscript_to_html', 'render_manuscript_to_pdf_v2']
