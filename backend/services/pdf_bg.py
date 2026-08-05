"""Canvas de fond partagé pour tous les PDFs premium Plume Astrale.

Dessine un fond navy nuit + halo doré + micro-étoiles + footer.
Utilisation :
    from services.pdf_bg import make_bg_canvas
    doc.build(story, onFirstPage=make_bg_canvas('Ton Analyse Karmique'),
                     onLaterPages=make_bg_canvas('Ton Analyse Karmique'))
"""
from __future__ import annotations
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

NIGHT = colors.HexColor('#111625')
MUTED = colors.HexColor('#9089B5')


def make_bg_canvas(footer_label: str = 'Plume Astrale'):
    """Retourne une fonction (canv, doc) à passer à SimpleDocTemplate.build()."""
    def _bg(canv, doc):
        canv.saveState()
        W, H = A4
        canv.setFillColor(NIGHT)
        canv.rect(0, 0, W, H, fill=1, stroke=0)
        for i, alpha in enumerate([0.02, 0.015, 0.01]):
            canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
            canv.circle(W/2, H, (i+1) * 6*cm, fill=1, stroke=0)
        r = random.Random(hash((doc.page,)))
        for _ in range(35):
            x = r.uniform(1*cm, W-1*cm)
            y = r.uniform(1*cm, H-1*cm)
            s = r.choice([0.4, 0.5, 0.6, 0.8])
            canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
            canv.circle(x, y, s, fill=1, stroke=0)
        canv.setFillColor(MUTED)
        canv.setFont('Helvetica', 7)
        canv.drawCentredString(W/2, 0.9*cm, f"Plume Astrale · {footer_label} · page {doc.page}")
        canv.restoreState()
    return _bg
