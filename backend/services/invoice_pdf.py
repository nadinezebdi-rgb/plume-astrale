"""invoice_pdf — Facture / reçu PDF FR, A4, Plume Astrale.

Généré à chaque paiement Stripe réussi (`checkout.session.completed`).
Mentions légales obligatoires pour auto-entrepreneur en franchise de TVA :
  • SIRET
  • N° TVA intracommunautaire
  • Mention « TVA non applicable, art. 293 B du CGI »
  • Prix TTC = prix HT (pas de TVA ajoutée)

Pièce jointe au mail de confirmation (base64), nom : « facture-plume-astrale-{numero}.pdf ».
"""
from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

# ─── Identité légale (fournie par la fondatrice) ───
LEGAL_NAME = os.environ.get('INVOICE_LEGAL_NAME', 'Plume Astrale')
LEGAL_SIRET = os.environ.get('INVOICE_SIRET', '87860206900022')
LEGAL_VAT = os.environ.get('INVOICE_VAT', 'FR96878602069')
LEGAL_ADDRESS = os.environ.get('INVOICE_ADDRESS', '')
LEGAL_EMAIL = os.environ.get('INVOICE_EMAIL', 'contact@plume-astrale.fr')
LEGAL_WEBSITE = os.environ.get('INVOICE_WEBSITE', 'plume-astrale.fr')
# Franchise en base TVA (art. 293 B CGI) — pas de TVA appliquée
VAT_EXEMPT_NOTICE = 'TVA non applicable, art. 293 B du CGI'

# Palette Nocturne Éditorial
INK = colors.HexColor('#0B1A2E')
GOLD = colors.HexColor('#C9A24B')
CREAM = colors.HexColor('#F5EEE0')
MUTED = colors.HexColor('#8891A4')

# A4 landscape
W, H = A4


def _register_fonts() -> None:
    directory = Path(__file__).resolve().parent.parent / 'assets' / 'book' / 'fonts'
    for suffix, filename in [('', 'Regular'), ('-Bold', 'Bold'), ('-Italic', 'Italic')]:
        name = 'InvoiceSerif' + suffix
        if name not in pdfmetrics.getRegisteredFontNames():
            path = directory / f'CormorantGaramond-{filename}.ttf'
            if path.exists():
                pdfmetrics.registerFont(TTFont(name, str(path)))


def _euros(cents: int) -> str:
    """Formate un montant Stripe (centimes) en « 29,00 € »."""
    return f'{(cents or 0) / 100:,.2f} €'.replace(',', ' ').replace('.', ',').replace(' ', '\u00a0', 1)


def _fmt_date(dt: Optional[datetime] = None) -> str:
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    d = dt or datetime.now()
    return f'{d.day} {mois[d.month - 1]} {d.year}'


def build_invoice_pdf(
    *,
    invoice_number: str,
    customer_email: str,
    customer_name: Optional[str],
    product_label: str,
    amount_cents: int,
    currency: str = 'EUR',
    payment_method_label: Optional[str] = None,
    paid_at: Optional[datetime] = None,
    session_id: Optional[str] = None,
) -> bytes:
    """Génère la facture PDF A4 FR en bytes.

    `payment_method_label` : ex. « Carte Visa …4242 » (recomposé par l'appelant depuis Stripe)
    """
    _register_fonts()
    base_font = 'InvoiceSerif' if 'InvoiceSerif' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    bold_font = f'{base_font}-Bold' if f'{base_font}-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    italic_font = f'{base_font}-Italic' if f'{base_font}-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ─── 1) Logo texte / entête ─────────────────────────────────────
    c.setFillColor(INK)
    c.setFont(bold_font, 22)
    c.drawString(20 * mm, H - 30 * mm, 'PLUME ASTRALE')
    c.setFillColor(GOLD)
    c.setFont(italic_font, 10)
    c.drawString(20 * mm, H - 35 * mm, 'L\'astrologie éditoriale')

    # ─── 2) Bloc « Facture n° / date » à droite ─────────────────────
    c.setFillColor(INK)
    c.setFont(bold_font, 14)
    c.drawRightString(W - 20 * mm, H - 30 * mm, f'Facture n° {invoice_number}')
    c.setFont(base_font, 10)
    c.setFillColor(MUTED)
    c.drawRightString(W - 20 * mm, H - 36 * mm, f'Émise le {_fmt_date(paid_at)}')

    # Filet or sous l'entête
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(20 * mm, H - 42 * mm, W - 20 * mm, H - 42 * mm)

    # ─── 3) Bloc identité émetteur + destinataire ────────────────────
    y = H - 52 * mm

    c.setFillColor(INK)
    c.setFont(bold_font, 10)
    c.drawString(20 * mm, y, 'ÉMIS PAR')
    c.setFont(base_font, 10)
    issuer_lines = [
        LEGAL_NAME,
        f'SIRET : {LEGAL_SIRET}',
        f'N° TVA intracommunautaire : {LEGAL_VAT}',
    ]
    if LEGAL_ADDRESS:
        issuer_lines.append(LEGAL_ADDRESS)
    issuer_lines.extend([LEGAL_EMAIL, LEGAL_WEBSITE])
    for i, line in enumerate(issuer_lines, start=1):
        c.drawString(20 * mm, y - 5 * mm * i, line)

    # Destinataire (à droite)
    c.setFont(bold_font, 10)
    c.drawString(110 * mm, y, 'FACTURÉ À')
    c.setFont(base_font, 10)
    recipient_lines = []
    if customer_name:
        recipient_lines.append(customer_name)
    recipient_lines.append(customer_email)
    for i, line in enumerate(recipient_lines, start=1):
        c.drawString(110 * mm, y - 5 * mm * i, line)

    # ─── 4) Tableau des articles ─────────────────────────────────────
    table_y = y - 55 * mm
    styles_cell = ParagraphStyle('cell', fontName=base_font, fontSize=10, leading=13,
                                 textColor=INK)
    styles_cell_bold = ParagraphStyle('cell_b', fontName=bold_font, fontSize=10, leading=13,
                                      textColor=INK)

    rows = [
        [Paragraph('<b>Description</b>', styles_cell_bold),
         Paragraph('<b>Qté</b>', styles_cell_bold),
         Paragraph('<b>Prix unitaire</b>', styles_cell_bold),
         Paragraph('<b>Montant</b>', styles_cell_bold)],
        [Paragraph(product_label, styles_cell),
         Paragraph('1', styles_cell),
         Paragraph(_euros(amount_cents), styles_cell),
         Paragraph(_euros(amount_cents), styles_cell)],
    ]

    table = Table(rows, colWidths=[85 * mm, 20 * mm, 32 * mm, 32 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CREAM),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, GOLD),
        ('LINEBELOW', (0, 1), (-1, 1), 0.3, MUTED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    tw, th = table.wrap(W - 40 * mm, 60 * mm)
    table.drawOn(c, 20 * mm, table_y - th)

    # ─── 5) Totaux ───────────────────────────────────────────────────
    totals_y = table_y - th - 10 * mm
    c.setFillColor(INK)
    c.setFont(base_font, 10)
    c.drawRightString(W - 55 * mm, totals_y, 'Total HT')
    c.drawRightString(W - 20 * mm, totals_y, _euros(amount_cents))

    c.drawRightString(W - 55 * mm, totals_y - 6 * mm, 'TVA (non applicable)')
    c.drawRightString(W - 20 * mm, totals_y - 6 * mm, '—')

    c.setFont(bold_font, 12)
    c.setFillColor(GOLD)
    c.drawRightString(W - 55 * mm, totals_y - 14 * mm, 'TOTAL TTC')
    c.drawRightString(W - 20 * mm, totals_y - 14 * mm, _euros(amount_cents))

    # Filet or
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(W - 90 * mm, totals_y - 11 * mm, W - 20 * mm, totals_y - 11 * mm)

    # ─── 6) Mention franchise TVA (OBLIGATOIRE) ──────────────────────
    c.setFillColor(INK)
    c.setFont(italic_font, 9)
    c.drawString(20 * mm, totals_y - 28 * mm, VAT_EXEMPT_NOTICE)

    # ─── 7) Paiement + session ID ────────────────────────────────────
    pay_y = totals_y - 42 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 10)
    c.drawString(20 * mm, pay_y, 'PAIEMENT')
    c.setFont(base_font, 10)
    c.drawString(20 * mm, pay_y - 5 * mm,
                 f'Statut : réglé le {_fmt_date(paid_at)}')
    if payment_method_label:
        c.drawString(20 * mm, pay_y - 10 * mm, f'Moyen : {payment_method_label}')
    if session_id:
        c.setFillColor(MUTED)
        c.setFont(base_font, 8)
        c.drawString(20 * mm, pay_y - 15 * mm, f'Référence transaction : {session_id}')

    # ─── 8) Pied de page ─────────────────────────────────────────────
    c.setFillColor(MUTED)
    c.setFont(italic_font, 8)
    c.drawCentredString(W / 2, 15 * mm,
                        'Facture générée automatiquement par Plume Astrale · Pas de signature manuscrite requise')
    c.drawCentredString(W / 2, 11 * mm,
                        f'En cas de question : {LEGAL_EMAIL} · {LEGAL_WEBSITE}')

    c.showPage()
    c.save()
    return buf.getvalue()


def make_invoice_number(session_id: str, paid_at: Optional[datetime] = None) -> str:
    """Numéro de facture lisible : AAMM-XXXX (préfixe année/mois + 4 derniers digits de session).
    Exemple : 2602-0838 pour une session Stripe terminant par …-0838 en février 2026.
    """
    d = paid_at or datetime.now()
    suffix = (session_id or '').strip()[-4:].zfill(4).upper()
    return f'{d.year % 100:02d}{d.month:02d}-{suffix}'


__all__ = ['build_invoice_pdf', 'make_invoice_number']
