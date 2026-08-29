"""
edition_reliee_service.py — Achat de l'Édition Reliée Plume Astrale (149 €)
================================================================================

Flow produit (2026-02-27) :
  1. Cliente remplit /edition-reliee : ses infos + prénom/date/heure/lieu de la
     destinataire + dédicace optionnelle.
  2. POST /api/edition-reliee/checkout → session Stripe (14900 cents).
  3. Webhook `checkout.session.completed` avec metadata.kind='edition_reliee' :
       - Met la row `payment_transactions` en `completed/paid`.
       - Génère le PDF 49 pages (réutilise `theme_natal_oneshot_service`).
       - Appelle `print_approval_service.create_print_approval()` qui envoie
         l'email 72h avec liens 1-clic approuver/refuser.
  4. Cliente reçoit l'email, approuve → l'admin lance l'impression manuellement.

⚠ L'impression, la reliure et l'expédition sont **hors périmètre logiciel** :
   Nadine (fondatrice) reçoit une notification admin après approbation et gère
   ces étapes en atelier. Le logiciel s'arrête à `status='approved'`.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import stripe

from config import get_settings
from services.print_approval_service import create_print_approval
from services.supabase_client import get_admin_client
from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook

logger = logging.getLogger(__name__)


# ── Checkout ──────────────────────────────────────────────────

async def create_edition_reliee_checkout(
    *,
    purchaser_email: str,
    purchaser_first_name: str,
    recipient_first_name: str,
    birth_date_iso: str,        # 'YYYY-MM-DD'
    birth_time: str,            # 'HH:MM' — 12:00 par défaut si no_birth_time=True
    birth_city: str,
    birth_country: str = 'FR',
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    dedication: Optional[str] = None,
    origin: str,
    no_birth_time: bool = False,  # §V audit marque Feb 2026
) -> dict:
    """Crée la session Stripe checkout pour un achat Édition Reliée 149 €.

    La ligne `payment_transactions` est écrite en `initiated/unpaid` avec
    toutes les données nécessaires à la génération PDF. Le webhook la marquera
    `completed/paid` et lancera la génération.
    """
    settings = get_settings()
    pack = settings.PACKS.get('edition_reliee')
    if not pack:
        raise ValueError('Produit edition_reliee introuvable dans la config.')

    stripe.api_key = settings.STRIPE_API_KEY

    # Prépare birth_data v3 (même format que theme_natal_oneshot)
    try:
        y, m, d = birth_date_iso[:10].split('-')
        h, mi = birth_time[:5].split(':')
        birth_data: dict[str, Any] = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
        }
        if latitude is not None:
            birth_data['latitude'] = float(latitude)
        if longitude is not None:
            birth_data['longitude'] = float(longitude)
        if birth_city:
            birth_data['city'] = birth_city
        if birth_country:
            birth_data['country_code'] = birth_country
    except Exception as e:
        raise ValueError(f'Format date/heure invalide : {e}')

    pdf_ctx = {
        'first_name': (recipient_first_name or '').strip() or 'Ami(e)',
        'birth_date_iso': birth_date_iso,
        'birth_data': birth_data,
        'no_birth_time': no_birth_time,  # §V audit marque
    }

    # Stripe checkout — 149 EUR
    origin = origin.rstrip('/')
    success_url = f'{origin}/edition-reliee/merci?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/edition-reliee'

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': pack['currency'],
                'product_data': {
                    'name': pack['name'],
                    'description': (
                        f"Livre personnalisé pour {recipient_first_name} — "
                        "imprimé, cousu, numéroté à la main. "
                        "Vous relisez le PDF avant impression (garantie 72h)."
                    ),
                },
                'unit_amount': int(pack['amount'] * 100),
            },
            'quantity': 1,
        }],
        customer_email=purchaser_email,
        success_url=success_url,
        cancel_url=cancel_url,
        # Note : Stripe metadata caps at ~500 chars total, on garde donc court.
        metadata={
            'product': 'edition_reliee',
            'kind': 'edition_reliee',
            'purchaser_first_name': (purchaser_first_name or '')[:80],
            'recipient_first_name': (recipient_first_name or '')[:80],
            'has_dedication': '1' if dedication else '0',
        },
    )

    # Persist all context in payment_transactions (métadata riche, pas Stripe)
    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.id,
            'user_email': purchaser_email,
            'pack_id': 'edition_reliee',
            'amount': float(pack['amount']),
            'currency': pack['currency'],
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'product': 'edition_reliee',
                'kind': 'edition_reliee',
                'pdf_ctx': pdf_ctx,
                'purchaser_first_name': (purchaser_first_name or '').strip() or None,
                'recipient_first_name': (recipient_first_name or '').strip() or None,
                'dedication': (dedication or '').strip()[:800] or None,
                'birth_city': birth_city,
                'birth_country': birth_country,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[edition_reliee] payment_transactions insert failed: {e}')

    return {'url': session.url, 'session_id': session.id}


# ── Webhook handler ───────────────────────────────────────────

async def handle_edition_reliee_webhook(session_id: str) -> dict:
    """Post-paiement Édition Reliée : marque completed → génère PDF → crée print_approval.

    Idempotent : si `pdf_path` déjà présent, on skip la génération et on tente
    juste la création de print_approval (skip aussi si déjà créé pour ce order_ref).
    """
    diag: dict[str, Any] = {'session_id': session_id, 'skipped': False}

    if not session_id:
        diag['error'] = 'session_id vide'
        return diag

    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[edition_reliee] tx fetch failed: {e}')
        diag['error'] = f'tx fetch failed: {e}'
        return diag
    if not tx_res or not tx_res.data:
        diag['error'] = 'tx not found'
        return diag

    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'edition_reliee':
        diag['error'] = 'kind mismatch'
        return diag

    # 1. Marque paiement confirmé (idempotent)
    if tx.get('status') != 'completed':
        try:
            sb.table('payment_transactions').update({
                'status': 'completed',
                'payment_status': 'paid',
                'credits_granted': True,
            }).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f'[edition_reliee] tx status update failed: {e}')

    # 2. Génère le PDF 49 pages (réutilise theme_natal_oneshot — même moteur/template)
    # ⚠ le service theme_natal_oneshot lit `metadata.kind == 'theme_natal_pdf_oneshot'`.
    # On patche temporairement `kind` pour piloter la génération, puis on restaure.
    original_kind = md.get('kind')
    diag['pdf_generated'] = False
    if not md.get('pdf_path'):
        try:
            md_patched = {**md, 'kind': 'theme_natal_pdf_oneshot'}
            sb.table('payment_transactions').update({'metadata': md_patched}).eq('session_id', session_id).execute()
            gen_result = await handle_theme_natal_oneshot_webhook(session_id)
            diag['pdf_gen'] = gen_result
            # Recharge md pour récupérer le pdf_path
            tx_res2 = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
            md = (tx_res2.data.get('metadata') if tx_res2 and tx_res2.data else md_patched) or md_patched
            # Restaure kind='edition_reliee' pour que les prochains handlers (admin/analytics) filtrent bien
            md['kind'] = original_kind
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
            diag['pdf_generated'] = bool(md.get('pdf_path'))
        except Exception as e:
            logger.exception(f'[edition_reliee] PDF gen failed: {e}')
            diag['pdf_error'] = str(e)
            # Rétablit le kind pour ne pas bloquer les analytics
            try:
                sb.table('payment_transactions').update({'metadata': {**md, 'kind': original_kind}}).eq('session_id', session_id).execute()
            except Exception:
                pass
            return diag
    else:
        diag['skipped'] = True
        diag['reason'] = 'pdf already generated'

    pdf_path = md.get('pdf_path')
    if not pdf_path:
        diag['error'] = 'pdf_path missing after generation'
        return diag

    # Construit l'URL complète (pdf_path est relatif : /api/pdf/download?...)
    site_url = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
    pdf_full_url = pdf_path if pdf_path.startswith('http') else f'{site_url}{pdf_path}'

    # 3. Crée le print_approval si pas déjà fait pour ce session_id
    try:
        existing = sb.table('print_approvals').select('id').eq('order_ref', session_id).limit(1).execute()
        if existing and existing.data:
            diag['print_approval_skipped'] = 'already exists'
            return diag
    except Exception as e:
        # Table absente → soft fail : la migration Supabase n'a pas encore été jouée.
        # On log un warning actionnable et on retourne sans planter.
        logger.warning(f'[edition_reliee] print_approvals table check failed: {e}')
        diag['warning'] = 'print_approvals table missing — run migrations/2026_02_print_approvals.sql'
        return diag

    try:
        approval = await create_print_approval(
            order_ref=session_id,
            purchaser_email=tx.get('user_email') or md.get('purchaser_email') or '',
            purchaser_first_name=md.get('purchaser_first_name'),
            recipient_first_name=md.get('recipient_first_name'),
            pdf_url=pdf_full_url,
            product_kind='edition_reliee',
        )
        diag['print_approval_id'] = approval.get('id')
        diag['email_sent'] = approval.get('email_sent')
        # Trace le lien dans metadata pour l'admin
        try:
            sb.table('payment_transactions').update({
                'metadata': {**md, 'print_approval_id': approval.get('id'),
                             'print_approval_deadline_at': approval.get('deadline_at')},
            }).eq('session_id', session_id).execute()
        except Exception:
            pass
    except Exception as e:
        logger.exception(f'[edition_reliee] create_print_approval failed: {e}')
        diag['print_approval_error'] = str(e)

    return diag
