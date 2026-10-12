"""fulfillment.py — Livraison des livres commandés via /composer.

Appelé à la fin de `pipeline.build_book_pdf_for_session` quand le PDF est prêt.

  - Édition numérique  → email à la cliente avec le lien de téléchargement.
  - Édition brochée / reliée →
        1. flow « Vous lisez avant qu'on imprime » (print_approvals, email 72h) ;
        2. alerte admin immédiate avec l'adresse de livraison, pour ne jamais
           laisser passer une commande imprimée.

Idempotent : les drapeaux `delivery_email_sent`, `print_approval_id` et
`admin_order_alert_sent` dans payment_transactions.metadata empêchent les doublons
(ex. régénération avec force=True).
"""
from __future__ import annotations

import html as _html
import logging
import os
from typing import Any, Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

SITE_URL = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr')
PRINTED_EDITIONS = {'brochee', 'reliee'}
EDITION_LABELS = {
    'numerique': 'Édition Numérique',
    'brochee': 'Édition Brochée',
    'reliee': 'Édition Reliée',
}


def _get(obj: Any, key: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def extract_shipping(session_obj: Any) -> Optional[dict]:
    """Extrait l'adresse de livraison d'une Checkout Session Stripe.

    Compatible anciennes API (`shipping_details`) et récentes
    (`collected_information.shipping_details`).
    """
    details = _get(_get(session_obj, 'collected_information'), 'shipping_details') \
        or _get(session_obj, 'shipping_details')
    if not details:
        return None
    addr = _get(details, 'address') or {}
    customer = _get(session_obj, 'customer_details') or {}
    out = {
        'name': _get(details, 'name'),
        'line1': _get(addr, 'line1'),
        'line2': _get(addr, 'line2'),
        'postal_code': _get(addr, 'postal_code'),
        'city': _get(addr, 'city'),
        'state': _get(addr, 'state'),
        'country': _get(addr, 'country'),
        'phone': _get(customer, 'phone'),
    }
    return out if out.get('line1') else None


def _pdf_full_url(md: dict) -> Optional[str]:
    pdf_path = md.get('pdf_path')
    if not pdf_path:
        return md.get('pdf_supabase_url')
    return pdf_path if pdf_path.startswith('http') else f'{SITE_URL}{pdf_path}'


def _save_md(session_id: str, md: dict) -> None:
    try:
        get_admin_client().table('payment_transactions').update({'metadata': md}).eq(
            'session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[fulfillment] metadata save failed for {session_id}: {e}')


def _delivery_email_html(first_name: str, pdf_url: str, edition_label: str) -> str:
    fn = _html.escape(first_name or '')
    hello = f'Bonjour {fn},' if fn else 'Bonjour,'
    url = _html.escape(pdf_url, quote=True)
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0C0918;font-family:Georgia,'Cormorant Garamond',serif;color:#F0E6D3;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0C0918;">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="580" cellpadding="0" cellspacing="0" style="max-width:580px;background:#15112A;border:1px solid rgba(212,180,106,0.22);border-radius:12px;">
      <tr><td style="padding:36px 40px 12px;text-align:center;border-bottom:1px solid rgba(212,180,106,0.14);">
        <p style="margin:0;font-size:11px;letter-spacing:0.32em;color:#D4B46A;text-transform:uppercase;">Plume Astrale · {edition_label}</p>
        <h1 style="margin:16px 0 0;font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#F5EEE0;font-weight:400;line-height:1.2;">Votre livre est prêt.</h1>
      </td></tr>
      <tr><td style="padding:32px 40px;font-size:16px;line-height:1.7;">
        <p style="margin:0 0 16px;">{hello}</p>
        <p style="margin:0 0 24px;">Votre livre de thème natal vient d'être composé. Vous pouvez le télécharger dès maintenant :</p>
        <p style="margin:0 0 28px;text-align:center;">
          <a href="{url}" style="display:inline-block;padding:14px 28px;background:#D4B46A;color:#0C0918;text-decoration:none;border-radius:999px;font-family:Arial,sans-serif;font-size:14px;letter-spacing:0.08em;">TÉLÉCHARGER MON LIVRE</a>
        </p>
        <p style="margin:0 0 12px;font-size:14px;color:rgba(240,230,211,0.75);">Conservez cet email : le lien reste accessible. Une question ? Répondez simplement à ce message ou écrivez à contact@plume-astrale.fr.</p>
        <p style="margin:0;font-size:14px;color:rgba(240,230,211,0.75);">Garantie satisfaction 14 jours.</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


def _admin_alert_html(session_id: str, tx: dict, md: dict, pdf_url: Optional[str]) -> str:
    ctx = md.get('pdf_ctx') or {}
    ship = md.get('shipping') or {}
    esc = lambda v: _html.escape(str(v)) if v else '—'
    addr = '<br>'.join(esc(x) for x in [
        ship.get('name'), ship.get('line1'), ship.get('line2'),
        f"{ship.get('postal_code') or ''} {ship.get('city') or ''}".strip(),
        ship.get('country'),
    ] if x) or '<b style="color:#B00020;">ADRESSE MANQUANTE — contacter la cliente</b>'
    chapters = ', '.join(md.get('chapters') or []) or 'aucun'
    return f"""<html><body style="font-family:Georgia,serif;color:#0F1A3C;padding:20px;">
<h2 style="color:#B8860B;">Nouvelle commande imprimée — {esc(EDITION_LABELS.get(md.get('edition'), md.get('edition')))}</h2>
<p><b>Cliente :</b> {esc(ctx.get('first_name'))} — {esc(tx.get('user_email'))} — tél. {esc(ship.get('phone'))}</p>
<p><b>Destinataire :</b> {esc(ctx.get('recipient_first_name'))}</p>
<p><b>Dédicace :</b> {esc(ctx.get('dedication'))}</p>
<p><b>Chapitres :</b> {esc(chapters)}</p>
<p><b>Montant :</b> {esc(tx.get('amount'))} €</p>
<p><b>Adresse de livraison :</b><br>{addr}</p>
<p><b>PDF :</b> {f'<a href="{_html.escape(pdf_url, quote=True)}">ouvrir</a>' if pdf_url else '—'}</p>
<p>Référence : <code>{esc(session_id)}</code></p>
<p><b>Étapes :</b> la cliente a 72h pour relire. Tu recevras un email « Approuvé » : c'est le signal pour lancer l'impression.</p>
</body></html>"""


async def deliver_book(*, session_id: str, tx: dict, md: dict) -> dict:
    """Envoie le livre (numérique) ou lance la relecture 72h (imprimé)."""
    from services.resend_service import send_email

    result: dict = {}
    edition = md.get('edition') or 'numerique'
    ctx = md.get('pdf_ctx') or {}
    email = (tx.get('user_email') or ctx.get('email') or '').strip().lower()
    first_name = ctx.get('first_name') or ''
    pdf_url = _pdf_full_url(md)
    changed = False

    if not email or not pdf_url:
        result['error'] = 'email ou pdf_url manquant'
        logger.warning(f'[fulfillment] {session_id}: {result["error"]}')
        return result

    if edition in PRINTED_EDITIONS:
        # 1) Alerte admin immédiate (avec adresse)
        if not md.get('admin_order_alert_sent'):
            eid = await send_email(
                ADMIN_ALERT_EMAIL,
                f'[Plume Astrale] Commande {EDITION_LABELS.get(edition, edition)} · {email}',
                _admin_alert_html(session_id, tx, md, pdf_url),
            )
            if eid:
                md['admin_order_alert_sent'] = True
                changed = True
            result['admin_alert'] = bool(eid)

        # 2) Relecture 72h (envoie l'email à la cliente avec approuver / refuser)
        if not md.get('print_approval_id'):
            try:
                from services.print_approval_service import create_print_approval
                sb = get_admin_client()
                existing = sb.table('print_approvals').select('id').eq(
                    'order_ref', session_id).limit(1).execute()
                if existing and existing.data:
                    md['print_approval_id'] = existing.data[0]['id']
                else:
                    approval = await create_print_approval(
                        order_ref=session_id,
                        purchaser_email=email,
                        purchaser_first_name=first_name,
                        recipient_first_name=ctx.get('recipient_first_name'),
                        pdf_url=pdf_url,
                        product_kind=f'composer_{edition}',
                    )
                    md['print_approval_id'] = approval.get('id')
                    md['print_approval_deadline_at'] = approval.get('deadline_at')
                    result['print_approval_email_sent'] = approval.get('email_sent')
                changed = True
            except Exception as e:
                logger.warning(f'[fulfillment] print approval failed for {session_id}: {e}')
                result['print_approval_error'] = str(e)
    else:
        if not md.get('delivery_email_sent'):
            eid = await send_email(
                email,
                'Votre livre Plume Astrale est prêt ✦',
                _delivery_email_html(first_name, pdf_url, EDITION_LABELS['numerique']),
            )
            if eid:
                md['delivery_email_sent'] = True
                changed = True
            result['delivery_email_sent'] = bool(eid)

    if changed:
        _save_md(session_id, md)
    return result
