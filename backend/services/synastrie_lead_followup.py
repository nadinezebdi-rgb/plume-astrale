"""Relance J+2 des leads synastrie non convertis.

Logique :
1. Boucle toutes les 6h, cible fenêtre J+2 ± 6h (donc 42h à 54h depuis
   l'inscription du lead) pour viser le pic d'ouverture email.
2. Pour chaque lead dans `oracle_leads` reçu dans cette fenêtre, vérifier :
   - Qu'il n'a pas déjà acheté la synastrie (table `synastrie_purchases`).
   - Qu'on ne lui a pas déjà envoyé la relance (table `synastrie_lead_followups`).
3. Si les 2 conditions sont OK → envoyer email Resend "Code -10% SYNEXT10" +
   marquer dans `synastrie_lead_followups`.

Note : le code promo SYNEXT10 (-10% sur Stripe) doit être créé côté
Stripe Dashboard. Si pas encore créé, l'email reste pertinent (le lien
mène à /synastrie où le visiteur peut acheter au prix normal).
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Fenêtre d'envoi : J+2 ± 6h
WINDOW_MIN_HOURS = 42
WINDOW_MAX_HOURS = 54
CHECK_INTERVAL_SECONDS = 6 * 60 * 60  # 6h


async def _already_purchased(sb, email: str) -> bool:
    """True si cet email figure dans synastrie_purchases avec status paid."""
    try:
        r = sb.table('synastrie_purchases').select('id, status').eq('email', email).execute()
        for row in (r.data or []):
            if (row.get('status') or '').lower() in ('paid', 'completed', 'success'):
                return True
    except Exception as e:
        logger.warning(f'[syn_followup] purchase check failed for {email}: {e}')
    return False


async def _already_followed_up(sb, email: str) -> bool:
    """True si on a déjà envoyé la relance (table synastrie_lead_followups)."""
    try:
        r = sb.table('synastrie_lead_followups').select('id').eq('email', email).limit(1).execute()
        return bool(r.data)
    except Exception as e:
        msg = str(e)
        if 'synastrie_lead_followups' in msg and ('schema cache' in msg or 'does not exist' in msg):
            # Table absente → treat as not-yet-followed-up (but will fail to persist later).
            return False
        logger.warning(f'[syn_followup] followup check failed for {email}: {e}')
        # Prudent : on considère qu'on a déjà envoyé pour éviter spam en cas d'erreur transitoire.
        return True


async def _mark_followup_sent(sb, email: str, lead_id: Optional[str], resend_id: Optional[str]) -> None:
    try:
        sb.table('synastrie_lead_followups').upsert({
            'email': email,
            'lead_id': lead_id,
            'resend_id': resend_id,
        }, on_conflict='email').execute()
    except Exception as e:
        msg = str(e)
        if 'synastrie_lead_followups' in msg and ('schema cache' in msg or 'does not exist' in msg):
            logger.warning(
                '[syn_followup] Table `synastrie_lead_followups` absente. Exécuter '
                '/app/backend/migrations/2026_02_synastrie_lead_followups.sql dans le SQL Editor Supabase.'
            )
        else:
            logger.warning(f'[syn_followup] mark sent failed for {email}: {msg[:200]}')


async def _run_once() -> None:
    """Un cycle : scan + envoi."""
    from services.supabase_client import get_admin_client
    from services.resend_service import send_synastrie_lead_followup_email
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    window_start = (now - timedelta(hours=WINDOW_MAX_HOURS)).isoformat()
    window_end = (now - timedelta(hours=WINDOW_MIN_HOURS)).isoformat()

    try:
        r = sb.table('oracle_leads').select('id, email, first_name, created_at')\
            .gte('created_at', window_start)\
            .lte('created_at', window_end)\
            .execute()
    except Exception as e:
        logger.warning(f'[syn_followup] oracle_leads query failed: {e}')
        return

    leads = r.data or []
    if not leads:
        logger.info('[syn_followup] fenêtre J+2 vide — rien à envoyer')
        return

    sent_count = 0
    skipped_purchased = 0
    skipped_already_sent = 0
    for lead in leads:
        email = (lead.get('email') or '').strip().lower()
        if not email:
            continue
        if await _already_purchased(sb, email):
            skipped_purchased += 1
            continue
        if await _already_followed_up(sb, email):
            skipped_already_sent += 1
            continue
        first_name = lead.get('first_name') or 'Voyageur'
        try:
            eid = await send_synastrie_lead_followup_email(email, first_name)
        except Exception as e:
            logger.warning(f'[syn_followup] send failed for {email}: {e}')
            continue
        await _mark_followup_sent(sb, email, lead.get('id'), eid)
        sent_count += 1
    logger.info(
        f'[syn_followup] cycle terminé — envoyés={sent_count}, '
        f'skipped(déjà_acheté)={skipped_purchased}, skipped(déjà_relancé)={skipped_already_sent}, '
        f'total_leads_fenêtre={len(leads)}'
    )


async def synastrie_lead_followup_loop() -> None:
    """Boucle infinie : grace period 180s puis cycle toutes les 6h."""
    logger.info(f'[syn_followup] boucle démarrée — relance J+2 toutes les {CHECK_INTERVAL_SECONDS//3600}h')
    try:
        await asyncio.sleep(180)
    except asyncio.CancelledError:
        raise
    while True:
        try:
            await _run_once()
        except Exception as e:
            logger.exception(f'[syn_followup] loop iteration failed: {e}')
        try:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            logger.info('[syn_followup] boucle arrêtée (CancelledError)')
            raise
