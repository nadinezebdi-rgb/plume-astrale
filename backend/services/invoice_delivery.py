"""invoice_delivery — Envoie la facture PDF FR à chaque paiement Stripe réussi.

Hook appelé depuis le webhook Stripe principal (`_process_stripe_event`) sur
`checkout.session.completed` avec `payment_status=paid`.

Idempotence : la table `invoices_sent` (créée on-demand dans Supabase) empêche
le double-envoi en cas de replay webhook.
"""
from __future__ import annotations

import base64
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx
import stripe

from services.invoice_counter import allocate_or_get as allocate_invoice_number
from services.invoice_pdf import build_invoice_pdf, make_invoice_number

logger = logging.getLogger(__name__)

# Table Supabase pour l'idempotence (créée on-demand par maybe_init_table)
_IDEMPOTENCY_TABLE = 'invoices_sent'

# Libellés produits (metadata.kind / metadata.product → label FR facturable)
_PRODUCT_LABELS = {
    'natal':             'Thème Natal personnalisé',
    'natal_pdf':         'Thème Natal — édition numérique',
    'natal_luxury':      'Thème Natal — édition reliée',
    'edition_reliee':    'Thème Natal — édition reliée',
    'theme_natal':       'Thème Natal personnalisé',
    'composer':          'Livre Astral personnalisé',
    'book':              'Livre Astral personnalisé',
    'synastrie':         'Rapport Synastrie — compatibilité amoureuse',
    'synastrie_full':    'Rapport Synastrie — rapport complet',
    'kabbale':           'Voyage Karmique — PDF',
    'karma':             'Voyage Karmique — PDF',
    'karma_destin':      'Voyage Karmique — PDF',
    'voyage_karmique':   'Voyage Karmique — PDF',
    'astrocarto':        'Astrocartographie personnalisée',
    'astrocartographie': 'Astrocartographie personnalisée',
    'pack_karmique':     'Pack Karmique complet',
    'numerologie':       'Lecture numérologique — PDF',
    'numerologie_pdf':   'Lecture numérologique — PDF',
    'rencontres':        'Rencontres Astrales — fenêtre personnalisée',
    'rencontres_astrales': 'Rencontres Astrales — fenêtre personnalisée',
    'trio_decouverte':   'Trio Découverte',
    'consultation':      'Consultation Ultime',
    'cercle_solena':     'Abonnement Cercle Soléna',
    'credits':           'Pack de crédits Plume Astrale',
    'carte_cadeau':      'Carte cadeau Plume Astrale',
}


def _label_for(session_data: dict) -> str:
    md = session_data.get('metadata') or {}
    kind = (md.get('kind') or md.get('product') or '').lower()
    label = _PRODUCT_LABELS.get(kind)
    if label:
        return label
    # Fallback : line items first description
    items = session_data.get('line_items', {}).get('data') if session_data.get('line_items') else None
    if items:
        desc = (items[0] or {}).get('description') or ''
        if desc:
            return desc.strip()
    # Fallback plus générique
    return 'Produit Plume Astrale'


def _payment_method_label(session_data: dict) -> Optional[str]:
    """Reconstruit « Carte Visa …4242 » depuis le PaymentIntent."""
    pi_id = session_data.get('payment_intent')
    if not pi_id:
        return None
    try:
        pi = stripe.PaymentIntent.retrieve(pi_id, expand=['latest_charge'])
        charge = pi.get('latest_charge') if isinstance(pi, dict) else getattr(pi, 'latest_charge', None)
        if hasattr(charge, 'to_dict'):
            charge = charge.to_dict()
        if not charge:
            return None
        pmd = charge.get('payment_method_details') or {}
        if 'card' in pmd:
            brand = (pmd['card'].get('brand') or '').title()
            last4 = pmd['card'].get('last4') or ''
            return f'Carte {brand} …{last4}' if last4 else f'Carte {brand}'
        # Autres moyens : SEPA, Link, etc.
        type_name = pmd.get('type') or ''
        return type_name.replace('_', ' ').title() if type_name else None
    except Exception as e:
        logger.info(f'[invoice] cannot retrieve PI card details: {e}')
        return None


def _check_idempotent(sb, session_id: str) -> bool:
    """Renvoie True si une facture a déjà été envoyée pour cette session."""
    try:
        r = sb.table(_IDEMPOTENCY_TABLE).select('session_id').eq('session_id', session_id).maybe_single().execute()
        return bool(r and r.data)
    except Exception:
        return False  # Si la table n'existe pas, on continue (fail-open)


def _mark_sent(sb, session_id: str, invoice_number: str, email: str) -> None:
    try:
        sb.table(_IDEMPOTENCY_TABLE).insert({
            'session_id': session_id,
            'invoice_number': invoice_number,
            'email': email,
            'sent_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        # Première exécution : la table peut ne pas exister → on log mais on ne bloque pas
        logger.info(f'[invoice] cannot mark {session_id} sent (table missing?): {e}')


async def send_invoice_for_session(session_data: dict) -> bool:
    """Génère + envoie la facture PDF FR par email. Idempotent.

    Retourne True si l'email a été envoyé (ou déjà envoyé précédemment).
    """
    session_id = session_data.get('id')
    if not session_id:
        logger.warning('[invoice] session sans id, abort')
        return False

    # Idempotence
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        if _check_idempotent(sb, session_id):
            logger.info(f'[invoice] déjà envoyée pour {session_id}, skip')
            return True
    except Exception:
        sb = None

    # Email destinataire
    customer_email = (
        session_data.get('customer_email')
        or (session_data.get('customer_details') or {}).get('email')
    )
    if not customer_email:
        logger.warning(f'[invoice] pas d\'email client pour {session_id}, abort')
        return False
    customer_name = (session_data.get('customer_details') or {}).get('name')

    amount_cents = session_data.get('amount_total') or 0
    currency = (session_data.get('currency') or 'eur').upper()
    product_label = _label_for(session_data)

    # Date de paiement
    created_ts = session_data.get('created')
    paid_at = datetime.fromtimestamp(created_ts, tz=timezone.utc) if created_ts else datetime.now(timezone.utc)

    # Numéro de facture : séquentiel strict (FACT-AAAA-NNNNNN, exigence
    # comptable FR), avec fallback AAMM-XXXX si Mongo est down.
    invoice_number = await allocate_invoice_number(session_id, paid_at)
    if not invoice_number:
        invoice_number = make_invoice_number(session_id, paid_at)

    # Moyen de paiement (Carte …4242)
    pay_label = _payment_method_label(session_data)

    # Génération PDF
    pdf_bytes = build_invoice_pdf(
        invoice_number=invoice_number,
        customer_email=customer_email,
        customer_name=customer_name,
        product_label=product_label,
        amount_cents=amount_cents,
        currency=currency,
        payment_method_label=pay_label,
        paid_at=paid_at,
        session_id=session_id,
    )

    # Envoi par email avec pièce jointe PDF
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not api_key:
        logger.warning('[invoice] RESEND_API_KEY absent, abort')
        return False
    sender = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>')
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    filename = f'facture-plume-astrale-{invoice_number}.pdf'
    amount_display = f'{amount_cents / 100:.2f}'.replace('.', ',') + ' €'

    subject = f'Votre facture Plume Astrale — n° {invoice_number}'
    html = f"""
<div style="font-family:'Helvetica Neue',Arial,sans-serif;background:#0B1A2E;padding:40px 0;">
  <div style="max-width:560px;margin:0 auto;background:#F5EEE0;padding:40px 32px;border-radius:14px;">
    <h1 style="font-family:'Georgia',serif;color:#0B1A2E;font-size:26px;margin:0 0 8px;">
      Merci {customer_name or ''},
    </h1>
    <p style="font-size:15px;line-height:1.6;color:#0B1A2E;">
      Votre paiement de <strong>{amount_display}</strong> a bien été reçu pour :
      <br><em>{product_label}</em>.
    </p>
    <p style="font-size:15px;line-height:1.6;color:#0B1A2E;">
      Vous trouverez en pièce jointe votre <strong>facture n° {invoice_number}</strong> au format PDF,
      conforme aux mentions légales françaises (SIRET, franchise de TVA).
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
            logger.error(f'[invoice] Resend fail {r.status_code}: {r.text[:200]}')
            return False
        logger.info(f'[invoice] sent to {customer_email} invoice={invoice_number} session={session_id}')
    except Exception as e:
        logger.error(f'[invoice] send fail for {session_id}: {e}')
        return False

    # Marque comme envoyé (idempotence)
    if sb is not None:
        _mark_sent(sb, session_id, invoice_number, customer_email)
    return True


__all__ = ['send_invoice_for_session']
