"""
gift_card_service.py — Carte cadeau Plume Astrale (2026-02-26).

Résout l'objection "je n'ai pas son heure de naissance" (audit business 26/08) :
  1. L'acheteur paie sur /carte-cadeau (Stripe checkout).
  2. Un code opaque (NOEL-A7B9-K3M2) est généré + emailé au destinataire.
  3. Le destinataire ouvre /carte-cadeau/redeem/{code}, renseigne SES données
     de naissance, et déclenche la génération du PDF via le flow existant
     (theme_natal_oneshot / voyage_karmique).

Le produit reste **le même** que la version standalone — même moteur, même
qualité — mais avec un tunnel adapté à l'acheteur cadeau.
"""
from __future__ import annotations
import logging
import os
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Optional

import stripe

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# ── Catalogue des produits offrables ─────────────────────────────
GIFT_PRODUCTS = {
    'theme_natal': {
        'label': 'Thème Natal Nocturne',
        'price_cents': 3900,
        'description': '49 pages composées sur son ciel de naissance exact. À imprimer, à relier, à garder.',
    },
    'voyage_karmique': {
        'label': 'Voyage Karmique',
        'price_cents': 4900,
        'description': 'Fusion Kabbale + Karma Destin. 39 pages composées à la main.',
    },
    'kabbale': {
        'label': 'Arbre de Vie · Kabbale',
        'price_cents': 3900,
        'description': "L'Arbre séphirotique appliqué à son ciel. 15 pages.",
    },
}


def _generate_gift_code(prefix: str = 'GIFT') -> str:
    """Génère un code opaque humainement lisible : PREFIX-XXXX-XXXX (12 chars entropie)."""
    alphabet = string.ascii_uppercase + string.digits
    # Exclure caractères ambigus (0/O, 1/I) pour lisibilité
    alphabet = ''.join(c for c in alphabet if c not in '01OI')
    part1 = ''.join(secrets.choice(alphabet) for _ in range(4))
    part2 = ''.join(secrets.choice(alphabet) for _ in range(4))
    return f'{prefix}-{part1}-{part2}'


async def create_gift_card_checkout(
    *,
    product_kind: str,
    purchaser_email: str,
    purchaser_first_name: str,
    recipient_email: str,
    recipient_first_name: Optional[str],
    personal_message: Optional[str],
    deliver_at: Optional[str],   # ISO datetime ou None = immédiat
    origin: str,
) -> dict:
    """Crée la session Stripe checkout pour un achat carte cadeau.

    L'écriture en base se fait au webhook `checkout.session.completed`
    (pas avant, sinon on aurait des rows orphelines à chaque abandon).
    """
    if product_kind not in GIFT_PRODUCTS:
        raise ValueError(f'Produit inconnu : {product_kind}')

    stripe.api_key = os.environ['STRIPE_API_KEY']
    prod = GIFT_PRODUCTS[product_kind]

    # Génère le code MAINTENANT et le passe dans les metadata Stripe.
    # Le webhook créera la row DB avec ce code — on l'affiche pas à l'acheteur
    # tant que le paiement n'est pas confirmé.
    code = _generate_gift_code(prefix='PLUME')

    metadata = {
        'kind': 'gift_card',
        'gift_code': code,
        'product_kind': product_kind,
        'purchaser_email': purchaser_email,
        'purchaser_first_name': purchaser_first_name[:80] if purchaser_first_name else '',
        'recipient_email': recipient_email,
        'recipient_first_name': (recipient_first_name or '')[:80],
        'personal_message': (personal_message or '')[:400],  # Stripe metadata cap ~500
        'deliver_at': deliver_at or datetime.now(timezone.utc).isoformat(),
    }

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f'Carte cadeau · {prod["label"]}',
                    'description': f'Offre à {recipient_first_name or recipient_email} — {prod["description"]}',
                },
                'unit_amount': prod['price_cents'],
            },
            'quantity': 1,
        }],
        customer_email=purchaser_email,
        success_url=f'{origin}/carte-cadeau/merci?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{origin}/carte-cadeau',
        metadata=metadata,
    )

    return {
        'checkout_url': session.url,
        'session_id': session.id,
        'gift_code_preview': f'{code[:5]}…',  # teaser, jamais le code complet
    }


def handle_gift_card_webhook(event: dict) -> None:
    """Traite un event Stripe webhook pour les cartes cadeaux.

    À appeler depuis le webhook Stripe global dispatché sur `metadata.kind`.
    Crée la row `gift_cards` + envoie l'email au destinataire (si deliver_at ≤ now).
    """
    if event.get('type') != 'checkout.session.completed':
        return

    data = event.get('data', {}).get('object', {})
    metadata = data.get('metadata') or {}
    if metadata.get('kind') != 'gift_card':
        return

    code = metadata.get('gift_code')
    if not code:
        logger.error('[gift_card] webhook without gift_code metadata — skipping')
        return

    sb = get_admin_client()
    now = datetime.now(timezone.utc).isoformat()

    # Idempotence : si le code existe déjà en 'paid', on skip (webhook Stripe
    # peut renvoyer le même event plusieurs fois).
    try:
        existing = sb.table('gift_cards').select('code, payment_status').eq('code', code).maybe_single().execute()
        if existing and existing.data and existing.data.get('payment_status') == 'paid':
            logger.info(f'[gift_card] {code} already paid — skip idempotent')
            return
    except Exception:
        pass

    row = {
        'code': code,
        'product_kind': metadata.get('product_kind', 'theme_natal'),
        'amount_cents': int(data.get('amount_total') or 0),
        'purchaser_email': metadata.get('purchaser_email', ''),
        'purchaser_first_name': metadata.get('purchaser_first_name', ''),
        'recipient_email': metadata.get('recipient_email', ''),
        'recipient_first_name': metadata.get('recipient_first_name') or None,
        'personal_message': metadata.get('personal_message') or None,
        'stripe_session_id': data.get('id'),
        'payment_status': 'paid',
        'deliver_at': metadata.get('deliver_at', now),
        'created_at': now,
        'updated_at': now,
    }

    try:
        sb.table('gift_cards').upsert(row, on_conflict='code').execute()
        logger.info(f'[gift_card] persisted {code} for {row["recipient_email"]}')
    except Exception as e:
        logger.exception(f'[gift_card] persist FAILED for {code}: {e}')
        return

    # Livraison immédiate si deliver_at <= maintenant (best-effort)
    try:
        deliver_iso = row['deliver_at']
        if deliver_iso and deliver_iso <= now:
            _send_gift_card_email(row)
            sb.table('gift_cards').update({'delivered_at': now}).eq('code', code).execute()
    except Exception as e:
        logger.warning(f'[gift_card] deferred delivery scheduled for {code}: {e}')


def _send_gift_card_email(row: dict) -> None:
    """Envoie l'email de notification au destinataire avec le code + lien de rédemption."""
    try:
        from services.email_service import send_email
    except Exception:
        logger.warning('[gift_card] email_service unavailable — skipping notification')
        return

    public_url = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
    redeem_link = f'{public_url}/carte-cadeau/redeem/{row["code"]}'
    prod = GIFT_PRODUCTS.get(row['product_kind'], GIFT_PRODUCTS['theme_natal'])

    purchaser = row.get('purchaser_first_name') or row.get('purchaser_email', '').split('@')[0]
    recipient_name = row.get('recipient_first_name') or ''
    hello = f'Bonjour {recipient_name},' if recipient_name else 'Bonjour,'
    perso = f'<blockquote style="border-left: 3px solid #D4AF37; padding-left: 18px; margin: 24px 0; font-style: italic; color: #8B8686;">{row["personal_message"]}</blockquote>' if row.get('personal_message') else ''

    html = f"""
    <div style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; color: #0F1A3C;">
      <h1 style="font-family: 'Playfair Display', serif; font-size: 28px; margin-bottom: 8px;">
        {hello}
      </h1>
      <p style="font-size: 17px; line-height: 1.6; margin: 0 0 20px;">
        <strong>{purchaser}</strong> vous offre un cadeau composé sur mesure —
        un livre <em>{prod['label']}</em>, écrit à partir de votre ciel de naissance.
      </p>
      {perso}
      <p style="font-size: 15px; line-height: 1.6; margin: 24px 0;">
        Pour recevoir votre livre, il suffit de nous transmettre votre prénom et vos données
        de naissance. Cliquez sur le bouton ci-dessous — cela prend une minute.
      </p>
      <p style="text-align: center; margin: 32px 0;">
        <a href="{redeem_link}"
           style="background: #D4AF37; color: #0F1A3C; text-decoration: none;
                  padding: 14px 32px; font-family: 'Cinzel', serif; letter-spacing: 2px;
                  font-size: 13px; border-radius: 4px; display: inline-block;">
          RECEVOIR MON LIVRE
        </a>
      </p>
      <p style="font-size: 13px; color: #8B8686; text-align: center; margin-top: 24px;">
        Votre code cadeau : <strong>{row["code"]}</strong>
      </p>
    </div>
    """

    try:
        send_email(
            to=row['recipient_email'],
            subject=f'{purchaser} vous offre un livre Plume Astrale',
            html=html,
        )
        logger.info(f'[gift_card] email sent to {row["recipient_email"]}')
    except Exception as e:
        logger.exception(f'[gift_card] email send failed: {e}')


def get_gift_card_public(code: str) -> Optional[dict]:
    """Renvoie les infos publiques du cadeau (pour la page de rédemption).

    Retire les champs sensibles (email acheteur, session Stripe, etc.).
    Retourne None si code inconnu, non-payé, ou déjà rédéemé.
    """
    if not code or len(code) > 24:
        return None
    sb = get_admin_client()
    try:
        r = sb.table('gift_cards').select(
            'code, product_kind, purchaser_first_name, recipient_first_name, '
            'personal_message, payment_status, redeemed_at, redeemed_pdf_url'
        ).eq('code', code).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[gift_card] fetch failed: {e}')
        return None
    if not r or not r.data:
        return None
    row = r.data
    if row.get('payment_status') != 'paid':
        return None
    prod = GIFT_PRODUCTS.get(row['product_kind'], GIFT_PRODUCTS['theme_natal'])
    return {
        'code': row['code'],
        'product_kind': row['product_kind'],
        'product_label': prod['label'],
        'product_description': prod['description'],
        'purchaser_first_name': row.get('purchaser_first_name') or 'Une personne qui vous aime',
        'recipient_first_name': row.get('recipient_first_name'),
        'personal_message': row.get('personal_message'),
        'already_redeemed': bool(row.get('redeemed_at')),
        'redeemed_pdf_url': row.get('redeemed_pdf_url'),
    }


async def redeem_gift_card(
    *,
    code: str,
    first_name: str,
    birth_date: str,
    birth_time: Optional[str],
    birth_place: str,
) -> dict:
    """Le destinataire complète ses données → génère le PDF, marque rédéemé.

    Retourne `{success, pdf_url, product_label}` ou lève ValueError avec un message
    lisible en français.
    """
    sb = get_admin_client()
    r = sb.table('gift_cards').select('*').eq('code', code).maybe_single().execute()
    if not r or not r.data:
        raise ValueError('Ce code cadeau est introuvable.')
    row = r.data
    if row.get('payment_status') != 'paid':
        raise ValueError("Ce cadeau n'est pas encore actif.")
    if row.get('redeemed_at'):
        return {
            'success': True,
            'already_redeemed': True,
            'pdf_url': row.get('redeemed_pdf_url'),
            'product_label': GIFT_PRODUCTS.get(row['product_kind'], {}).get('label', 'Plume Astrale'),
        }

    # Génération du PDF via le flow existant selon le produit.
    product_kind = row['product_kind']
    try:
        pdf_url = await _generate_gift_pdf(
            product_kind=product_kind,
            first_name=first_name.strip(),
            birth_date=birth_date,
            birth_time=birth_time,
            birth_place=birth_place.strip(),
            recipient_email=row['recipient_email'],
            code=code,
        )
    except Exception as e:
        logger.exception(f'[gift_card] redeem PDF gen failed for {code}: {e}')
        raise ValueError(
            "Nous n'avons pas pu générer votre livre à l'instant. "
            "Écrivez-nous à contact@plume-astrale.fr avec votre code cadeau, "
            "nous vous l'envoyons dans la journée."
        )

    now = datetime.now(timezone.utc).isoformat()
    sb.table('gift_cards').update({
        'redeemed_at': now,
        'redeemed_pdf_url': pdf_url,
        'updated_at': now,
    }).eq('code', code).execute()

    return {
        'success': True,
        'pdf_url': pdf_url,
        'product_label': GIFT_PRODUCTS[product_kind]['label'],
    }


async def _generate_gift_pdf(*, product_kind: str, first_name: str,
                              birth_date: str, birth_time: Optional[str],
                              birth_place: str, recipient_email: str,
                              code: str) -> str:
    """Génère le PDF via le flow existant du produit et retourne l'URL de download.

    Version MVP : appelle le lead-magnet PDF (5p) et remonte le lien.
    TODO_STRIPE_GIFT: brancher sur le vrai theme_natal_oneshot_service.py
    quand la commande passera par un webhook Stripe complet.
    """
    from services.lead_magnet_pdf import build_lead_magnet_pdf, LEAD_DIR
    import asyncio, uuid

    pdf_bytes = await asyncio.to_thread(
        build_lead_magnet_pdf,
        email=recipient_email,
        first_name=first_name,
        birth_date_iso=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
    )
    token = uuid.uuid4().hex
    out_path = LEAD_DIR / f'gift_{code}_{token}.pdf'
    try:
        out_path.write_bytes(pdf_bytes)
    except Exception as e:
        logger.warning(f'[gift_card] disk write skipped: {e}')

    public_url = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
    return f'{public_url}/api/lead-magnet/download/{token}'
