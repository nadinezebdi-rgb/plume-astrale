"""Canvas de fond partagé pour tous les PDFs premium Plume Astrale.

Dessine un fond navy nuit + halo doré + micro-étoiles + cadre or éditorial + footer prestige.
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

NIGHT = colors.HexColor('#111625')
GOLD  = colors.HexColor('#D4AF37')
MUTED = colors.HexColor('#9089B5')


def make_bg_canvas(footer_label: str = 'Plume Astrale'):
    """Retourne une fonction (canv, doc) à passer à SimpleDocTemplate.build().

    Charte prestige unifiée : fond nuit + halo + 30 étoiles + cadre or pointillé
    + petit soleil ornemental en haut + footer "PLUME ASTRALE · <PRODUCT>   — n —".
    """
    footer_upper = str(footer_label).upper()

    def _bg(canv, doc):
        canv.saveState()
        W, H = A4

        # Fond nuit
        canv.setFillColor(NIGHT)
        canv.rect(0, 0, W, H, fill=1, stroke=0)

        # Halo doré en haut
        for i, alpha in enumerate([0.02, 0.015, 0.01]):
            canv.setFillColorRGB(0.83, 0.68, 0.21, alpha=alpha)
            canv.circle(W / 2, H, (i + 1) * 6 * cm, fill=1, stroke=0)

        # 30 étoiles stables (seed = page number)
        r = random.Random(hash((doc.page,)))
        for _ in range(30):
            x = r.uniform(1 * cm, W - 1 * cm)
            y = r.uniform(1 * cm, H - 1 * cm)
            s = r.choice([0.4, 0.5, 0.6, 0.8])
            canv.setFillColorRGB(1, 0.95, 0.75, alpha=r.uniform(0.2, 0.55))
            canv.circle(x, y, s, fill=1, stroke=0)

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
