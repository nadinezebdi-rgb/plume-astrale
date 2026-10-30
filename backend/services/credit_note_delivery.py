"""credit_note_delivery — Génère + envoie l'avoir PDF par email après refund.

Appelé automatiquement par `/admin/stripe-refund` (dry_run=False) une fois
le `stripe.Refund.create` validé. Idempotent par ``refund_id`` grâce à
l'index unique de `credit_note_counter`.

Mail client :
  • Pièce jointe : avoir-plume-astrale-{numero}.pdf
  • Si une facture d'origine existe en base (`invoice_numbers.session_id`),
    on la référence dans le mail et le PDF.
"""
from __future__ import annotations

import base64
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from services.credit_note_counter import allocate_or_get as allocate_credit_note_number
from services.credit_note_pdf import build_credit_note_pdf, REASON_LABELS

logger = logging.getLogger(__name__)


async def _lookup_invoice_for_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrouve `invoice_number` + `allocated_at` depuis la collection
    `invoice_numbers` (si Mongo dispo).
    """
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return None
    try:
        doc = await db['invoice_numbers'].find_one({'session_id': session_id})
        if doc:
            return {
                'invoice_number': doc.get('number'),
                'invoice_date': doc.get('allocated_at'),
            }
    except Exception as e:
        logger.info(f'[credit_note] invoice lookup fail: {e}')
    return None


async def send_credit_note_for_refund(
    *,
    refund_id: str,
    session_id: Optional[str],
    customer_email: str,
    customer_name: Optional[str] = None,
    amount_cents: int,
    currency: str = 'EUR',
    product_label: str = 'Produit Plume Astrale',
    reason: str = 'requested_by_customer',
    note: Optional[str] = None,
    refunded_at: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Génère l'avoir + l'envoie par email. Retourne un rapport.

    Format de retour :
        {
          'ok': bool,
          'credit_note_number': str | None,
          'email_sent': bool,
          'invoice_ref': str | None,
          'reason': str (si échec)
        }
    """
    refunded_at = refunded_at or datetime.now(timezone.utc)
    report: Dict[str, Any] = {
        'ok': False, 'credit_note_number': None,
        'email_sent': False, 'invoice_ref': None, 'reason': None,
    }

    # ─── 1) Allocation numéro avoir (idempotent par refund_id) ───
    number = await allocate_credit_note_number(refund_id, refunded_at)
    if not number:
        # Fallback hors Mongo
        number = f'AVOIR-{refunded_at.year:04d}-{(refund_id or "")[-6:].upper().zfill(6)}'
    report['credit_note_number'] = number

    # ─── 2) Retrouve la facture d'origine ─────────────────────────
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    if session_id:
        inv = await _lookup_invoice_for_session(session_id)
        if inv:
            invoice_number = inv.get('invoice_number')
            inv_dt = inv.get('invoice_date')
            if isinstance(inv_dt, datetime):
                invoice_date = inv_dt
            report['invoice_ref'] = invoice_number

    # ─── 3) Génération PDF ────────────────────────────────────────
    try:
        pdf_bytes = build_credit_note_pdf(
            credit_note_number=number,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            customer_email=customer_email,
            customer_name=customer_name,
            product_label=product_label,
            amount_cents=amount_cents,
            currency=currency,
            reason=reason,
            note=note,
            refunded_at=refunded_at,
            refund_id=refund_id,
            session_id=session_id,
        )
    except Exception as e:
        logger.error(f'[credit_note] PDF build fail refund={refund_id}: {e}')
        report['reason'] = f'pdf_build_fail: {e}'
        return report

    # ─── 4) Envoi email Resend ────────────────────────────────────
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not api_key:
        logger.warning('[credit_note] RESEND_API_KEY absent, PDF non envoyé')
        report['reason'] = 'resend_key_missing'
        return report
    sender = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>')
    filename = f'avoir-plume-astrale-{number}.pdf'
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    amount_display = f'{amount_cents / 100:.2f}'.replace('.', ',') + ' €'
    reason_label = REASON_LABELS.get(reason, reason)
    invoice_ref_html = (
        f'<br>Référence facture d\'origine : <strong>{invoice_number}</strong>.'
        if invoice_number else ''
    )

    subject = f'Avoir Plume Astrale — n° {number}'
    html = f"""
<div style="font-family:'Helvetica Neue',Arial,sans-serif;background:#0B1A2E;padding:40px 0;">
  <div style="max-width:560px;margin:0 auto;background:#F5EEE0;padding:40px 32px;border-radius:14px;">
    <h1 style="font-family:'Georgia',serif;color:#0B1A2E;font-size:26px;margin:0 0 8px;">
      {('Bonjour ' + customer_name) if customer_name else 'Bonjour'},
    </h1>
    <p style="font-size:15px;line-height:1.6;color:#0B1A2E;">
      Nous confirmons le remboursement de <strong>{amount_display}</strong>
      pour <em>{product_label}</em>.
    </p>
    <p style="font-size:15px;line-height:1.6;color:#0B1A2E;">
      Motif : <strong>{reason_label}</strong>.{invoice_ref_html}
    </p>
    <p style="font-size:15px;line-height:1.6;color:#0B1A2E;">
      Vous trouverez en pièce jointe votre <strong>avoir n° {number}</strong> au format PDF,
      conforme aux mentions comptables françaises.
    </p>
    <p style="font-size:14px;color:#4ADE80;margin-top:20px;">
      Le remboursement est en route sur votre moyen de paiement d'origine
      (comptez 3 à 10 jours ouvrés selon votre banque).
    </p>
    <p style="font-size:14px;color:#8891A4;margin-top:28px;">
      Pour toute question : <a href="mailto:{os.environ.get('INVOICE_EMAIL', 'contact@plume-astrale.fr')}">
      {os.environ.get('INVOICE_EMAIL', 'contact@plume-astrale.fr')}</a>
    </p>
    <p style="font-size:12px;color:#8891A4;margin-top:12px;font-style:italic;">
      Plume Astrale — L'astrologie éditoriale
    </p>
  </div>
</div>
"""
    payload = {
        'from': sender,
        'to': [customer_email],
        'subject': subject,
        'html': html,
        'attachments': [{'filename': filename, 'content': pdf_b64}],
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json=payload,
            )
        if r.status_code >= 300:
            logger.error(f'[credit_note] Resend fail {r.status_code}: {r.text[:200]}')
            report['reason'] = f'resend_{r.status_code}'
            return report
        logger.info(f'[credit_note] sent to {customer_email} number={number} refund={refund_id}')
        report['email_sent'] = True
        report['ok'] = True
    except Exception as e:
        logger.error(f'[credit_note] send fail refund={refund_id}: {e}')
        report['reason'] = f'send_fail: {e}'

    # AUDIT (2026-10-30 · Nao) : alerte Slack si trop d'avoirs sur le mois.
    # Signal d'anomalie côté produit (incidents de livraison, qualité, SAV).
    # Seuil configurable via CREDIT_NOTE_SLACK_THRESHOLD (défaut 10/mois).
    # Dédup : un ping unique quand on franchit le seuil (pas à chaque avoir au-dessus).
    try:
        await _maybe_slack_alert_threshold(refunded_at)
    except Exception as e:
        logger.info(f'[credit_note] slack threshold check skip: {e}')

    return report


# ─── Alerte Slack monthly threshold ─────────────────────────────────
async def _maybe_slack_alert_threshold(refunded_at: datetime) -> None:
    """Si on dépasse CREDIT_NOTE_SLACK_THRESHOLD avoirs sur le mois en cours
    (UTC), ping Slack UNE fois par (année, mois). Dédup Mongo-backed via
    services.alert_cooldown (survit aux restarts pod).
    """
    threshold = int(os.environ.get('CREDIT_NOTE_SLACK_THRESHOLD', '10'))
    if threshold <= 0:
        return
    from services.mongo import get_db
    db = get_db()
    if db is None:
        return
    year, month = refunded_at.year, refunded_at.month
    key = f'{year:04d}-{month:02d}'

    # Compte avant d'acquérir le lock — si on n'a pas atteint le seuil,
    # on ne consomme pas le lock (il reste utilisable au prochain franchissement).
    start = refunded_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        count = await db['credit_note_numbers'].count_documents({
            'allocated_at': {'$gte': start},
        })
    except Exception as e:
        logger.info(f'[credit_note] threshold count fail: {e}')
        return

    if count < threshold:
        return

    from services.alert_cooldown import try_acquire
    # TTL 35 jours — couvre tout mois civil + marge
    if not await try_acquire('credit_note_monthly', key, ttl_hours=24 * 35):
        return  # déjà alerté ce mois-ci

    from services.slack_notify import send_slack_alert
    await send_slack_alert(
        title=f'Seuil mensuel d\'avoirs atteint : {count}',
        summary=(
            f'*{count} avoirs émis depuis le 1er {start:%B %Y}* '
            f'(seuil configuré : {threshold}).\n'
            f'Vérifier si c\'est un pic réel (incident livraison, campagne pub, '
            f'bug produit) ou un comportement normal selon le volume de ventes.'
        ),
        fields=[
            ('Mois', f'{start:%B %Y}'),
            ('Avoirs émis', str(count)),
            ('Seuil', str(threshold)),
        ],
        url='https://plume-astrale.fr/admin/payments-health',
        url_label='Ouvrir le dashboard',
        emoji=':warning:',
    )


__all__ = ['send_credit_note_for_refund']
