"""Canvas de fond print partagé pour les PDFs Plume Astrale.

Dessine un papier blanc, un filet bronze discret et un footer à fort contraste.
Utilisation :
    from services.pdf_bg import make_bg_canvas
    doc.build(story, onFirstPage=make_bg_canvas('Ton Analyse Karmique'),
                     onLaterPages=make_bg_canvas('Ton Analyse Karmique'))

Depuis Feb 2026 : ce fond partage la charte "livre prestige" (cadre or pointillé,
soleil ornemental en haut, footer éditorial) définie dans services.pdf_prestige.
"""
from __future__ import annotations
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

PAPER = colors.white
GOLD  = colors.HexColor('#79570F')
MUTED = colors.HexColor('#5E5A63')


def make_bg_canvas(footer_label: str = 'Plume Astrale'):
    """Retourne une fonction (canv, doc) à passer à SimpleDocTemplate.build().

    Charte print : papier blanc + cadre bronze fin + footer "PLUME ASTRALE · <PRODUCT>   — n —".
    """
    footer_upper = str(footer_label).upper()

    def _bg(canv, doc):
        canv.saveState()
        W, H = A4

        # Fond blanc pour impression et lecture.
        canv.setFillColor(PAPER)
        canv.rect(0, 0, W, H, fill=1, stroke=0)

        # Cadre or pointillé
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.35)
        canv.setDash([0.6, 2.4], 0)
        canv.rect(1.2 * cm, 1.2 * cm, W - 2.4 * cm, H - 2.4 * cm, fill=0, stroke=1)
        canv.setDash([], 0)

        # Soleil ornemental (petit disque + 2 tirets)
        canv.setFillColor(GOLD)
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.4)
        canv.circle(W / 2, H - 1.55 * cm, 0.10 * cm, fill=1, stroke=0)
        canv.line(W / 2 - 1.4 * cm, H - 1.55 * cm, W / 2 - 0.3 * cm, H - 1.55 * cm)
        canv.line(W / 2 + 0.3 * cm, H - 1.55 * cm, W / 2 + 1.4 * cm, H - 1.55 * cm)

        # Footer éditorial
        canv.setFillColor(MUTED)
        canv.setFont('Helvetica', 6.5)
        canv.drawString(2 * cm, 0.75 * cm, f"PLUME ASTRALE · {footer_upper}")
        canv.drawRightString(W - 2 * cm, 0.75 * cm, f"— {doc.page} —")
        canv.restoreState()

    return _bg
