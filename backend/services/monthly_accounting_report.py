"""monthly_accounting_report — Agrège factures + avoirs d'un mois en un PDF.

Généré à la demande depuis `/admin/payments-health` → bouton
« Rapport comptable {mois}.pdf ». Format A4 FR, 1 clic, pour l'expert-comptable.

Structure du PDF :
  1. En-tête : identité émetteur (SIRET, TVA, adresse), période (ex. Oct 2026)
  2. Résumé : nb factures, nb avoirs, total encaissé, total remboursé, CA net
  3. Table factures : date | n° | email | pack | montant
  4. Table avoirs : date | n° | email | motif | montant (négatif)
  5. Mention franchise TVA
"""
from __future__ import annotations

import io
import logging
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from services.invoice_pdf import (
    LEGAL_NAME, LEGAL_SIRET, LEGAL_VAT, LEGAL_ADDRESS, LEGAL_EMAIL,
    VAT_EXEMPT_NOTICE, INK, GOLD, CREAM, MUTED, _register_fonts, _euros, _fmt_date,
)

logger = logging.getLogger(__name__)

W, H = A4

FR_MONTHS = [
    '', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
]


async def _fetch_invoices_for_month(year: int, month: int) -> List[Dict[str, Any]]:
    """Liste les factures émises dans le mois donné (via invoice_numbers Mongo)."""
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return []
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    try:
        rows = []
        async for d in db['invoice_numbers'].find({
            'allocated_at': {'$gte': start, '$lte': end},
        }).sort('allocated_at', 1):
            rows.append({
                'number': d.get('number', '—'),
                'date': d.get('allocated_at'),
                'session_id': d.get('session_id'),
            })
        return rows
    except Exception as e:
        logger.warning(f'[monthly_report] invoices fetch: {e}')
        return []


async def _fetch_credit_notes_for_month(year: int, month: int) -> List[Dict[str, Any]]:
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return []
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    try:
        rows = []
        async for d in db['credit_note_numbers'].find({
            'allocated_at': {'$gte': start, '$lte': end},
        }).sort('allocated_at', 1):
            rows.append({
                'number': d.get('number', '—'),
                'date': d.get('allocated_at'),
                'refund_id': d.get('refund_id'),
            })
        return rows
    except Exception as e:
        logger.warning(f'[monthly_report] credit notes fetch: {e}')
        return []


def _enrich_from_supabase(invoices: List[Dict[str, Any]], credit_notes: List[Dict[str, Any]]) -> None:
    """Enrichit chaque ligne avec email + pack_id + montant depuis payment_transactions."""
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
    except Exception as e:
        logger.info(f'[monthly_report] supabase: {e}')
        return
    session_ids = [r['session_id'] for r in invoices if r.get('session_id')]
    refund_ids = [r['refund_id'] for r in credit_notes if r.get('refund_id')]
    tx_by_sid: Dict[str, Dict[str, Any]] = {}
    tx_by_refund: Dict[str, Dict[str, Any]] = {}
    try:
        if session_ids:
            r = sb.table('payment_transactions').select(
                'session_id, user_email, pack_id, amount, metadata'
            ).in_('session_id', session_ids[:200]).execute()
            for row in (r.data or []):
                tx_by_sid[row['session_id']] = row
    except Exception as e:
        logger.info(f'[monthly_report] fetch tx by sid: {e}')
    try:
        if refund_ids:
            # Recherche par metadata.refund_id (JSON)
            r = sb.table('payment_transactions').select(
                'session_id, user_email, pack_id, amount, metadata'
            ).limit(500).execute()
            for row in (r.data or []):
                rid = (row.get('metadata') or {}).get('refund_id')
                if rid in refund_ids:
                    tx_by_refund[rid] = row
    except Exception as e:
        logger.info(f'[monthly_report] fetch tx by refund: {e}')

    for inv in invoices:
        tx = tx_by_sid.get(inv.get('session_id'))
        if tx:
            inv['email'] = tx.get('user_email', '—')
            inv['pack_id'] = tx.get('pack_id', '—')
            inv['amount'] = float(tx.get('amount') or 0)
        else:
            inv.setdefault('email', '—')
            inv.setdefault('pack_id', '—')
            inv.setdefault('amount', 0.0)
    for cn in credit_notes:
        tx = tx_by_refund.get(cn.get('refund_id'))
        if tx:
            cn['email'] = tx.get('user_email', '—')
            cn['pack_id'] = tx.get('pack_id', '—')
            md = tx.get('metadata') or {}
            cn['reason'] = md.get('refund_reason') or '—'
            cn['amount'] = float(tx.get('amount') or 0)
        else:
            cn.setdefault('email', '—')
            cn.setdefault('reason', '—')
            cn.setdefault('amount', 0.0)


async def build_monthly_report_pdf(year: int, month: int) -> Tuple[bytes, Dict[str, Any]]:
    """Génère le PDF et renvoie (bytes, résumé_dict)."""
    _register_fonts()
    base_font = 'InvoiceSerif' if 'InvoiceSerif' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    bold_font = f'{base_font}-Bold' if f'{base_font}-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    italic_font = f'{base_font}-Italic' if f'{base_font}-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

    invoices = await _fetch_invoices_for_month(year, month)
    credit_notes = await _fetch_credit_notes_for_month(year, month)
    _enrich_from_supabase(invoices, credit_notes)

    total_in = sum(float(r.get('amount') or 0) for r in invoices)
    total_out = sum(float(r.get('amount') or 0) for r in credit_notes)
    net = total_in - total_out

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ─── En-tête ───
    c.setFillColor(INK)
    c.setFont(bold_font, 20)
    c.drawString(20 * mm, H - 25 * mm, 'PLUME ASTRALE')
    c.setFillColor(GOLD)
    c.setFont(italic_font, 10)
    c.drawString(20 * mm, H - 30 * mm, 'Rapport comptable mensuel')

    period_label = f'{FR_MONTHS[month].capitalize()} {year}'
    c.setFillColor(INK)
    c.setFont(bold_font, 16)
    c.drawRightString(W - 20 * mm, H - 25 * mm, period_label)
    c.setFont(base_font, 9)
    c.setFillColor(MUTED)
    c.drawRightString(W - 20 * mm, H - 32 * mm,
                      f'Généré le {datetime.now(timezone.utc):%d/%m/%Y %H:%M} UTC')

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(20 * mm, H - 37 * mm, W - 20 * mm, H - 37 * mm)

    # ─── Identité émetteur (compact) ───
    y = H - 45 * mm
    c.setFillColor(INK)
    c.setFont(base_font, 9)
    for line in [LEGAL_NAME, f'SIRET : {LEGAL_SIRET}', f'TVA : {LEGAL_VAT}', LEGAL_ADDRESS or '', LEGAL_EMAIL]:
        if line:
            c.drawString(20 * mm, y, line)
            y -= 4 * mm

    # ─── Résumé en 4 blocs ───
    y_summary = y - 8 * mm
    blocks = [
        ('Factures émises', str(len(invoices)), GOLD),
        ('CA brut', _euros(int(total_in * 100)), '#4ADE80'),
        ('Avoirs émis', str(len(credit_notes)), '#FCA5A5'),
        ('CA net', _euros(int(net * 100)), '#D4AF37'),
    ]
    bw = (W - 50 * mm) / 4
    for i, (label, value, color) in enumerate(blocks):
        bx = 20 * mm + i * (bw + 3 * mm)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.3)
        c.rect(bx, y_summary - 20 * mm, bw, 20 * mm, stroke=1, fill=0)
        c.setFillColor(MUTED)
        c.setFont(base_font, 8)
        c.drawString(bx + 4, y_summary - 6 * mm, label.upper())
        c.setFillColor(color)
        c.setFont(bold_font, 16)
        c.drawString(bx + 4, y_summary - 15 * mm, value)

    # ─── Table factures ───
    y_inv = y_summary - 28 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 12)
    c.drawString(20 * mm, y_inv, f'Factures émises ({len(invoices)})')

    styles_cell = ParagraphStyle('cell', fontName=base_font, fontSize=8, leading=10, textColor=INK)
    styles_bold = ParagraphStyle('cell_b', fontName=bold_font, fontSize=8, leading=10, textColor=INK)

    rows_inv = [[
        Paragraph('<b>Date</b>', styles_bold),
        Paragraph('<b>Numéro</b>', styles_bold),
        Paragraph('<b>Email</b>', styles_bold),
        Paragraph('<b>Pack</b>', styles_bold),
        Paragraph('<b>Montant TTC</b>', styles_bold),
    ]]
    for r in invoices:
        rows_inv.append([
            Paragraph(_fmt_date(r.get('date')), styles_cell),
            Paragraph(r.get('number', '—'), styles_cell),
            Paragraph(r.get('email', '—'), styles_cell),
            Paragraph(r.get('pack_id', '—'), styles_cell),
            Paragraph(_euros(int(float(r.get('amount') or 0) * 100)), styles_cell),
        ])
    if len(rows_inv) == 1:
        rows_inv.append([Paragraph('<i>Aucune facture ce mois-ci</i>', styles_cell), '', '', '', ''])

    table_inv = Table(rows_inv, colWidths=[22 * mm, 32 * mm, 55 * mm, 35 * mm, 25 * mm])
    table_inv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CREAM),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GOLD),
        ('LINEBELOW', (0, 1), (-1, -1), 0.2, MUTED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
    ]))
    tw, th_inv = table_inv.wrap(W - 40 * mm, 150 * mm)
    table_inv.drawOn(c, 20 * mm, y_inv - 4 * mm - th_inv)

    # ─── Table avoirs ───
    y_cn = y_inv - 10 * mm - th_inv
    if y_cn < 60 * mm:
        c.showPage()
        y_cn = H - 25 * mm
    c.setFillColor(INK)
    c.setFont(bold_font, 12)
    c.drawString(20 * mm, y_cn, f'Avoirs émis ({len(credit_notes)})')

    rows_cn = [[
        Paragraph('<b>Date</b>', styles_bold),
        Paragraph('<b>Numéro</b>', styles_bold),
        Paragraph('<b>Email</b>', styles_bold),
        Paragraph('<b>Motif</b>', styles_bold),
        Paragraph('<b>Montant</b>', styles_bold),
    ]]
    for r in credit_notes:
        rows_cn.append([
            Paragraph(_fmt_date(r.get('date')), styles_cell),
            Paragraph(r.get('number', '—'), styles_cell),
            Paragraph(r.get('email', '—'), styles_cell),
            Paragraph(r.get('reason', '—'), styles_cell),
            Paragraph(f"-{_euros(int(float(r.get('amount') or 0) * 100))}", styles_cell),
        ])
    if len(rows_cn) == 1:
        rows_cn.append([Paragraph('<i>Aucun avoir ce mois-ci</i>', styles_cell), '', '', '', ''])

    table_cn = Table(rows_cn, colWidths=[22 * mm, 35 * mm, 55 * mm, 32 * mm, 25 * mm])
    table_cn.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#FFE5E5'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, '#EF4444'),
        ('LINEBELOW', (0, 1), (-1, -1), 0.2, MUTED),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
    ]))
    tw2, th_cn = table_cn.wrap(W - 40 * mm, 150 * mm)
    table_cn.drawOn(c, 20 * mm, y_cn - 4 * mm - th_cn)

    # ─── Mention franchise TVA ───
    c.setFillColor(INK)
    c.setFont(italic_font, 8)
    c.drawString(20 * mm, 18 * mm, VAT_EXEMPT_NOTICE)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, 12 * mm,
                        'Rapport généré automatiquement par Plume Astrale pour l\'expert-comptable')

    c.showPage()
    c.save()

    summary = {
        'period': period_label,
        'invoices_count': len(invoices),
        'credit_notes_count': len(credit_notes),
        'total_in_eur': round(total_in, 2),
        'total_out_eur': round(total_out, 2),
        'net_eur': round(net, 2),
    }
    return buf.getvalue(), summary


__all__ = ['build_monthly_report_pdf']
