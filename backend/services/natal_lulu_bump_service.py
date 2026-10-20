"""natal_lulu_bump_service — Livre relié via Lulu Print-on-Demand (79 €)
================================================================================

Nouveau produit "livre relié" en bump après l'achat du Thème Natal PDF.
Différent de l'Édition Reliée 149 € (impression artisanale manuelle Nadine).

Flow :
  1. Cliente achète le PDF (Stripe → PDF généré → email envoyé)
  2. Email contient CTA "Ajoute ton exemplaire relié - 79€" avec un token
  3. Clic → /natal-print-bump?token=... → formulaire adresse + devis Lulu live
  4. Soumission → Stripe Checkout (prix basé sur devis)
  5. Webhook `checkout.session.completed` avec metadata.kind='natal_lulu_bump' :
       - rend la cover PDF
       - upload intérieur + cover sur Supabase Storage
       - crée le print job Lulu
       - envoie email confirmation
  6. Webhook Lulu `PRINT_JOB_STATUS_CHANGED` SHIPPED → envoi tracking email

Prix de base : 79€ TTC FR (impression + livraison + marge). Les destinations
hors FR voient leur prix recalculé en live via `/api/natal-print-bump/quote`.
"""
from __future__ import annotations
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import stripe

from services.lulu_client import quote_print_job, is_mock
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


# ─── Pricing ────────────────────────────────────────────────────────
# Prix TTC EUR par pays. Variable selon destination.
BASE_PRICE_FR_EUR = 79.0  # prix affiché / de référence France

# Marge minimale au-delà des coûts Lulu (impression + livraison)
MIN_MARGIN_EUR = 35.0


def compute_client_price_eur(quote: Dict[str, Any]) -> float:
    """Calcule le prix TTC à facturer à la cliente à partir du devis Lulu.

    Règle : max(prix_FR_base, coût_Lulu + marge_min), arrondi au 1€ supérieur.
    """
    try:
        total_cost = float(quote.get('total_cost_incl_tax') or 0)
    except (TypeError, ValueError):
        total_cost = 0.0
    with_margin = total_cost + MIN_MARGIN_EUR
    price = max(BASE_PRICE_FR_EUR, with_margin)
    # Arrondi euro supérieur pour un prix "propre"
    return float(int(price + 0.999))


# ─── Stripe checkout ───────────────────────────────────────────────
async def create_bump_checkout(
    *,
    purchaser_email: str,
    first_name: str,
    birth_date_iso: str,
    source_session_id: str,     # session_id du PDF d'origine (pour tracer)
    address: Dict[str, Any],    # destination Lulu validée côté client
    origin: str,
) -> Dict[str, Any]:
    """Crée la session Stripe pour le bump livre relié. Prix basé sur devis Lulu."""
    stripe_key = os.environ.get('STRIPE_SECRET_KEY', '').strip()
    if not stripe_key:
        raise RuntimeError('STRIPE_SECRET_KEY manquant')
    stripe.api_key = stripe_key

    # Devis Lulu live
    source = _lookup_print_artifacts(source_session_id)
    if not source.get('pdf_lulu_interior_url') or not source.get('pdf_lulu_page_count'):
        raise RuntimeError('Régénérez le livre avant de commander son impression')
    # Preflight before collecting payment, not only after checkout completion.
    from services.lulu_client import validate_print_files
    prepared_cover = await _generate_and_upload_cover(
        first_name=first_name, birth_date_iso=birth_date_iso,
        session_id=f'{source_session_id}-proof', page_count=int(source['pdf_lulu_page_count']))
    await validate_print_files(source['pdf_lulu_interior_url'], prepared_cover,
                               int(source['pdf_lulu_page_count']))
    quote = await quote_print_job(address, page_count=int(source['pdf_lulu_page_count']))
    client_price_eur = compute_client_price_eur(quote)

    success_url = f'{origin}/natal-print/merci?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/natal-print?token={source_session_id}'

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        locale='fr',
        line_items=[{
            'quantity': 1,
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f'Livre relié — Thème Natal de {first_name}',
                    'description': (
                        'Édition reliée hardcover A5 de votre Thème Natal. '
                        'Impression & livraison via notre partenaire d\'impression. '
                        f'Prix TTC incluant impression, reliure et livraison vers '
                        f'{(address.get("country_code") or "FR").upper()}.'
                    ),
                },
                'unit_amount': int(client_price_eur * 100),
            },
        }],
        customer_email=purchaser_email,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'product': 'natal_lulu_bump',
            'kind': 'natal_lulu_bump',
            'source_session_id': source_session_id,
            'first_name': first_name[:50],
            'birth_date_iso': birth_date_iso,
            'ship_name': (address.get('name') or '')[:60],
            'ship_street1': (address.get('street1') or '')[:80],
            'ship_street2': (address.get('street2') or '')[:60],
            'ship_city': (address.get('city') or '')[:40],
            'ship_postcode': (address.get('postcode') or '')[:16],
            'ship_country': (address.get('country_code') or 'FR').upper()[:2],
            'ship_phone': (address.get('phone_number') or '')[:24],
            'quote_total_cost': str(quote.get('total_cost_incl_tax') or 0),
            'quote_mocked': '1' if quote.get('mock') else '0',
        },
    )

    # Journalise la session dans Supabase pour suivi
    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'id': session.id,
            'stripe_session_id': session.id,
            'email': purchaser_email,
            'amount_cents': int(client_price_eur * 100),
            'currency': 'EUR',
            'status': 'initiated',
            'payment_status': 'unpaid',
            'kind': 'natal_lulu_bump',
            'product_id': 'natal_lulu_bump',
            'metadata': {
                'first_name': first_name,
                'source_session_id': source_session_id,
                'address': address,
                'quote': quote,
                'client_price_eur': client_price_eur,
            },
            'created_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        logger.warning(f'[natal_lulu_bump] insert payment_transactions failed: {e}')

    return {
        'checkout_url': session.url,
        'session_id': session.id,
        'client_price_eur': client_price_eur,
        'quote': quote,
    }


# ─── Webhook handler ───────────────────────────────────────────────
async def handle_bump_webhook(session_id: str, *, force: bool = False) -> Dict[str, Any]:
    """Traite le webhook Stripe `checkout.session.completed` pour le bump.

    Idempotent : si déjà traité (status='fulfilled'), retourne sans refaire.
    """
    import stripe as _stripe
    _stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '').strip()
    sb = get_admin_client()

    # Récupère la row
    r = sb.table('payment_transactions').select('*').eq('stripe_session_id', session_id).limit(1).execute()
    rows = r.data or []
    if not rows:
        logger.warning(f'[natal_lulu_bump] session {session_id} not found in payment_transactions')
        return {'ok': False, 'error': 'not_found'}
    row = rows[0]

    if row.get('status') == 'fulfilled' and not force:
        return {'ok': True, 'already_fulfilled': True}

    md = row.get('metadata') or {}
    first_name = md.get('first_name') or 'Voyageuse'
    source_session_id = md.get('source_session_id') or ''
    address = md.get('address') or {}
    client_price_eur = md.get('client_price_eur') or 79.0

    # 1. Récupère le PDF intérieur (déjà généré via theme_natal_oneshot)
    source = _lookup_print_artifacts(source_session_id)
    interior_url = source.get('pdf_lulu_interior_url')
    page_count = int(source.get('pdf_lulu_page_count') or 0)
    if not interior_url:
        logger.error(f'[natal_lulu_bump] interior PDF URL missing for source {source_session_id}')
        return {'ok': False, 'error': 'interior_pdf_missing'}

    # 2. Génère + upload la couverture PDF
    cover_url = await _generate_and_upload_cover(
        first_name=first_name, birth_date_iso=md.get('birth_date_iso') or '',
        session_id=session_id, page_count=page_count,
    )

    # 3. Crée le print job Lulu
    from services.lulu_client import create_print_job, validate_print_files
    await validate_print_files(interior_url, cover_url, page_count)
    external_id = f'natal_bump_{session_id}'
    job = await create_print_job(
        external_id=external_id, address=address,
        interior_url=interior_url, cover_url=cover_url,
    )

    # 4. Marque fulfilled
    try:
        sb.table('payment_transactions').update({
            'status': 'fulfilled',
            'payment_status': 'paid',
            'fulfilled_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {**md, 'lulu_job': job, 'cover_url': cover_url},
        }).eq('stripe_session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[natal_lulu_bump] update failed: {e}')

    # 5. Email de confirmation (best effort)
    try:
        await _send_bump_confirmation_email(
            email=row.get('email') or '', first_name=first_name,
            price_eur=client_price_eur, country=address.get('country_code') or 'FR',
        )
    except Exception as e:
        logger.warning(f'[natal_lulu_bump] confirmation email failed: {e}')

    return {'ok': True, 'lulu_job': job, 'cover_url': cover_url}


# ─── Helpers internes ──────────────────────────────────────────────
def _lookup_print_artifacts(source_session_id: str) -> dict:
    if not source_session_id:
        return {}
    response = get_admin_client().table('payment_transactions').select('metadata').eq(
        'session_id', source_session_id).limit(1).execute()
    rows = response.data or []
    return (rows[0].get('metadata') or {}) if rows else {}


async def _generate_and_upload_cover(
    *, first_name: str, birth_date_iso: str, session_id: str, page_count: int,
) -> str:
    """Génère la couverture PDF et l'upload sur Supabase Storage.

    En mode mock Lulu, renvoie une URL fictive si l'upload échoue.
    """
    from services.print_book_renderer import lulu_cover
    from services.lulu_client import cover_dimensions
    from types import SimpleNamespace
    import asyncio as _a
    import json

    # Rectangles must match the selected binding's official template. Hardcover
    # hinges/folds cannot be inferred from page count or total width alone.
    template = json.loads(os.environ.get('LULU_COVER_TEMPLATE_JSON') or '{}')
    if not all(template.get(key) for key in ('front_box_mm', 'back_box_mm', 'width_mm', 'height_mm')):
        raise RuntimeError('Gabarit Lulu exact requis : LULU_COVER_TEMPLATE_JSON (front_box_mm, back_box_mm)')
    dimensions = await cover_dimensions(page_count)
    if dimensions.get('unit') != 'mm':
        raise RuntimeError('Dimensions de couverture Lulu non métriques')
    if abs(float(template['height_mm']) - float(dimensions['height'])) > .1:
        raise RuntimeError('Hauteur du gabarit incompatible avec le produit Lulu sélectionné')
    # The back remains anchored left. A different page count moves the front
    # panel right by the exact API width delta; no estimated spine thickness.
    front = list(map(float, template['front_box_mm']))
    front[0] += float(dimensions['width']) - float(template['width_mm'])
    pdf_bytes = await _a.to_thread(
        lulu_cover, SimpleNamespace(first_name=first_name, astro_data={}),
        width_mm=float(dimensions['width']), height_mm=float(dimensions['height']),
        front_box_mm=front, back_box_mm=list(map(float, template['back_box_mm'])),
    )

    # Upload Supabase Storage
    try:
        sb = get_admin_client()
        path = f'natal_lulu_bump/{session_id}/cover.pdf'
        try:
            sb.storage.from_('reports').remove([path])
        except Exception:
            pass
        sb.storage.from_('reports').upload(
            path, pdf_bytes,
            {'content-type': 'application/pdf', 'upsert': 'true'},
        )
        pub = sb.storage.from_('reports').get_public_url(path)
        return (pub or '').rstrip('?')
    except Exception as e:
        logger.warning(f'[natal_lulu_bump] cover upload failed: {e}')
        raise


async def _send_bump_confirmation_email(
    *, email: str, first_name: str, price_eur: float, country: str,
) -> None:
    """Email de confirmation après achat bump — statut 'en production'."""
    import html as _html
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>')
    if not (api_key and email):
        return
    # SEC-005 hardening : échappe strictement les champs utilisateur dans le HTML.
    fn = _html.escape((first_name or 'ami(e)').strip().title())
    country_safe = _html.escape((country or 'FR').upper())
    subject = f"Votre livre relié est en route, {fn} ✦"
    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#1C1B26;background:#F0E6D2;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#A8823F;">
          ✦ Plume Astrale ✦
        </div>
      </div>
      <div style="background:#FBF5E8;border:1px solid rgba(168,130,63,0.22);border-radius:16px;padding:36px 28px;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#1C1B26;margin:0 0 14px;line-height:1.25;">
          {fn}, <em style="color:#A8823F;font-style:italic;">votre exemplaire relié</em><br>est en préparation.
        </h1>
        <p style="color:#3A3022;line-height:1.65;font-size:15px;">
          Merci pour votre achat. Votre livre hardcover A5 — reliure cartonnée, intérieur
          imprimé en haute qualité — vient d'entrer en production chez notre partenaire d'impression.
        </p>
        <p style="color:#3A3022;line-height:1.65;font-size:15px;">
          <strong>Délai estimé :</strong> impression 3-5 jours + livraison vers {country_safe}.<br/>
          Nous vous enverrons le numéro de suivi dès l'expédition.
        </p>
        <div style="margin-top:28px;padding:16px;background:#F0E6D2;border-radius:12px;">
          <div style="font-size:12px;color:#8B7355;letter-spacing:0.08em;text-transform:uppercase;">Montant payé</div>
          <div style="font-size:22px;font-family:'Cormorant Garamond',serif;color:#1C1B26;">
            {price_eur:.0f} € TTC
          </div>
        </div>
      </div>
      <div style="text-align:center;margin-top:24px;font-size:11px;color:#8B7355;">
        Plume Astrale · Édition personnelle
      </div>
    </div>
    """
    import httpx
    async with httpx.AsyncClient(timeout=30) as c:
        try:
            await c.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [email], 'subject': subject, 'html': html},
            )
        except Exception:
            pass


__all__ = ['create_bump_checkout', 'handle_bump_webhook',
            'compute_client_price_eur', 'BASE_PRICE_FR_EUR']
