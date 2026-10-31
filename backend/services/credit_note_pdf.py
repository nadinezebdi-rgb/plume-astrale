"""credit_note_pdf — Avoir PDF FR, A4, Plume Astrale.

Généré automatiquement à chaque remboursement Stripe exécuté depuis
`/admin/stripe-refund`. Reprend la facture d'origine + motif + montant remboursé.

Mentions légales obligatoires (mêmes que la facture) :
  • SIRET + N° TVA + mention franchise art. 293 B CGI
  • Référence explicite à la facture d'origine (numéro + date)
  • Motif du remboursement
  • Montant TTC remboursé

Pièce jointe au mail de notification au client, nom :
``avoir-plume-astrale-{numero}.pdf``.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from services.invoice_pdf import (
    LEGAL_NAME, LEGAL_SIRET, LEGAL_VAT, LEGAL_ADDRESS, LEGAL_EMAIL, LEGAL_WEBSITE,
    VAT_EXEMPT_NOTICE, INK, GOLD, CREAM, MUTED, _register_fonts, _euros, _fmt_date,
)

W, H = A4

# Libellés motif Stripe → libellé lecteur
REASON_LABELS = {
    'requested_by_customer': 'Remboursement à la demande du client',
    'duplicate':             'Paiement en double (duplicate)',
    'fraudulent':            'Transaction frauduleuse',
}


def build_credit_note_pdf(
    *,
    credit_note_number: str,
    invoice_number: Optional[str],
    invoice_date: Optional[datetime],
    customer_email: str,
    customer_name: Optional[str],
    product_label: str,
    amount_cents: int,
    currency: str = 'EUR',
    reason: str = 'requested_by_customer',
    note: Optional[str] = None,
    refunded_at: Optional[datetime] = None,
    refund_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> bytes:
    """Génère l'avoir PDF A4 FR en bytes.

    Si `invoice_number` est absent, l'avoir mentionne « émis sans facture
    d'origine référencée » (cas rare — recovery / incident).
    """
    _register_fonts()
    base_font = 'InvoiceSerif' if 'InvoiceSerif' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    bold_font = f'{base_font}-Bold' if f'{base_font}-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    italic_font = f'{base_font}-Italic' if f'{base_font}-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ─── 1) Entête ──────────────────────────────────────────────────
    c.setFillColor(INK)
    c.setFont(bold_font, 22)
    c.drawString(20 * mm, H - 30 * mm, 'PLUME ASTRALE')
    c.setFillColor(GOLD)
    c.setFont(italic_font, 10)
    c.drawString(20 * mm, H - 35 * mm, 'L\'astrologie éditoriale')

    # ─── 2) Bloc « Avoir n° / date » à droite ───────────────────────
    c.setFillColor(INK)
    c.setFont(bold_font, 14)
    c.drawRightString(W - 20 * mm, H - 30 * mm, f'Avoir n° {credit_note_number}')
    c.setFont(base_font, 10)
    c.setFillColor(MUTED)
    c.drawRightString(W - 20 * mm, H - 36 * mm, f'Émis le {_fmt_date(refunded_at)}')

    # Filet or
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.line(20 * mm, H - 42 * mm, W - 20 * mm, H - 42 * mm)

    # ─── 3) Identité émetteur + destinataire ────────────────────────
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

    c.setFont(bold_font, 10)
    c.drawString(110 * mm, y, 'DESTINATAIRE')
    c.setFont(base_font, 10)
    recipient_lines = []
    if customer_name:
        recipient_lines.append(customer_name)
    recipient_lines.append(customer_email)
    for i, line in enumerate(recipient_lines, start=1):
        c.drawString(110 * mm, y - 5 * mm * i, line)

    # ─── 4) Référence facture d'origine ─────────────────────────────
    ref_y = y - 35 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 10)
    c.drawString(20 * mm, ref_y, 'FACTURE D\'ORIGINE')
    c.setFont(base_font, 10)
    if invoice_number:
        c.drawString(20 * mm, ref_y - 5 * mm, f'N° {invoice_number} émise le {_fmt_date(invoice_date)}')
    else:
        c.setFont(italic_font, 10)
        c.setFillColor(MUTED)
        c.drawString(20 * mm, ref_y - 5 * mm, 'Émis sans facture d\'origine référencée (recovery administratif).')
        c.setFillColor(INK)

    # ─── 5) Motif ───────────────────────────────────────────────────
    reason_label = REASON_LABELS.get(reason, reason)
    reason_y = ref_y - 15 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 10)
    c.drawString(20 * mm, reason_y, 'MOTIF')
    c.setFont(base_font, 10)
    c.drawString(20 * mm, reason_y - 5 * mm, reason_label)
    if note:
        c.setFont(italic_font, 9)
        c.setFillColor(MUTED)
        c.drawString(20 * mm, reason_y - 10 * mm, note[:200])
        c.setFillColor(INK)

    # ─── 6) Tableau remboursement ───────────────────────────────────
    table_y = reason_y - 22 * mm
    styles_cell = ParagraphStyle('cell', fontName=base_font, fontSize=10, leading=13, textColor=INK)
    styles_cell_bold = ParagraphStyle('cell_b', fontName=bold_font, fontSize=10, leading=13, textColor=INK)

    rows = [
        [Paragraph('<b>Description</b>', styles_cell_bold),
         Paragraph('<b>Qté</b>', styles_cell_bold),
         Paragraph('<b>Montant TTC d\'origine</b>', styles_cell_bold),
         Paragraph('<b>Montant remboursé</b>', styles_cell_bold)],
        [Paragraph(f'Remboursement — {product_label}', styles_cell),
         Paragraph('1', styles_cell),
         Paragraph(_euros(amount_cents), styles_cell),
         Paragraph(f'-{_euros(amount_cents)}', styles_cell)],
    ]
    table = Table(rows, colWidths=[70 * mm, 15 * mm, 40 * mm, 44 * mm])
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

    # ─── 7) Totaux ──────────────────────────────────────────────────
    totals_y = table_y - th - 10 * mm
    c.setFillColor(INK)
    c.setFont(base_font, 10)
    c.drawRightString(W - 55 * mm, totals_y, 'Total HT remboursé')
    c.drawRightString(W - 20 * mm, totals_y, f'-{_euros(amount_cents)}')
    c.drawRightString(W - 55 * mm, totals_y - 6 * mm, 'TVA (non applicable)')
    c.drawRightString(W - 20 * mm, totals_y - 6 * mm, '—')
    c.setFont(bold_font, 12)
    c.setFillColor(GOLD)
    c.drawRightString(W - 55 * mm, totals_y - 14 * mm, 'TOTAL REMBOURSÉ')
    c.drawRightString(W - 20 * mm, totals_y - 14 * mm, f'-{_euros(amount_cents)}')
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(W - 90 * mm, totals_y - 11 * mm, W - 20 * mm, totals_y - 11 * mm)

    # ─── 8) Mention franchise TVA (OBLIGATOIRE) ─────────────────────
    c.setFillColor(INK)
    c.setFont(italic_font, 9)
    c.drawString(20 * mm, totals_y - 28 * mm, VAT_EXEMPT_NOTICE)

    # ─── 9) Références Stripe ───────────────────────────────────────
    pay_y = totals_y - 42 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 10)
    c.drawString(20 * mm, pay_y, 'RÉFÉRENCES')
    c.setFont(base_font, 10)
    c.drawString(20 * mm, pay_y - 5 * mm, f'Statut : remboursé le {_fmt_date(refunded_at)}')
    if refund_id:
        c.setFillColor(MUTED)
        c.setFont(base_font, 8)
        c.drawString(20 * mm, pay_y - 10 * mm, f'Référence remboursement : {refund_id}')
    if session_id:
        c.setFillColor(MUTED)
        c.setFont(base_font, 8)
        c.drawString(20 * mm, pay_y - 14 * mm, f'Référence transaction : {session_id}')

    # ─── 10) Pied de page ───────────────────────────────────────────
    c.setFillColor(MUTED)
    c.setFont(italic_font, 8)
    c.drawCentredString(W / 2, 15 * mm,
                        'Avoir généré automatiquement par Plume Astrale · Pas de signature manuscrite requise')
    c.drawCentredString(W / 2, 11 * mm,
                        f'En cas de question : {LEGAL_EMAIL} · {LEGAL_WEBSITE}')

    c.showPage()
    c.save()
    return buf.getvalue()


__all__ = ['build_credit_note_pdf']
