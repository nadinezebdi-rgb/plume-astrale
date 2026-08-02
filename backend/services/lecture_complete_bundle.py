"""
Orchestrateur post-paiement pour le bundle "lecture_complete" (97 EUR).

Apres paiement Stripe (ou bypass admin), declenche EN PARALLELE la generation
des 5 PDFs bundles + un email de bienvenue :
  1. Theme Natal complet (theme_natal_pdf_oneshot)
  2. Karma & Destinee (karma_destin_analysis)
  3. Arbre de Vie Kabbale (kabbale_arbre_de_vie)
  4. Fenetres de Rencontre (fenetre_rencontre_avancee)
  5. Guide Ultime des Rencontres / Cycles (rencontres_ultime)

Chaque PDF est traite via son propre handler existant, en creant une
sous-transaction payment_transactions avec le bon `kind` + `pdf_ctx`.

Le Cercle Solena 90j n'est PAS active automatiquement ici (pas de PDF —
livraison manuelle ou via subscription grant).
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def _build_birth_data(order_ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convertit order_ctx (email/birth_date/birth_time/…) en birth_data v3."""
    birth_date = (order_ctx.get('birth_date') or '')[:10]
    birth_time = (order_ctx.get('birth_time') or '12:00')[:5]
    if not birth_date:
        return None
    try:
        y, m, d = birth_date.split('-')
        h, mi = birth_time.split(':') if ':' in birth_time else ('12', '00')
        bd = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
        }
        if order_ctx.get('birth_city'):
            bd['city'] = order_ctx['birth_city']
        if order_ctx.get('birth_country'):
            bd['country_code'] = order_ctx['birth_country']
        return bd
    except Exception as e:
        logger.warning(f'[lecture_complete] birth_data parse fail: {e}')
        return None


def _insert_child_tx(sb, parent_session_id: str, suffix: str, kind: str,
                     email: str, pdf_ctx: Dict[str, Any]) -> str:
    """Insere une sous-transaction et renvoie son session_id."""
    child_session_id = f'{parent_session_id}--{suffix}'
    try:
        sb.table('payment_transactions').insert({
            'session_id': child_session_id,
            'user_email': email,
            'pack_id': kind,
            'amount': 0.0,
            'currency': 'eur',
            'credits': 0,
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
            'metadata': {
                'product': kind,
                'kind': kind,
                'pdf_ctx': pdf_ctx,
                'parent_bundle': parent_session_id,
                'lecture_complete_bundle': True,
                'pdf_status': 'pending',
                'pending_started_at': datetime.now(timezone.utc).isoformat(),
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] child tx insert failed ({suffix}): {e}')
    return child_session_id


async def handle_lecture_complete_webhook(session_id: str) -> Dict[str, Any]:
    """Orchestre la generation des 5 PDFs bundles apres paiement.

    Idempotent : si le bundle a deja ete traite (metadata.bundle_dispatched=True),
    on ne relance pas.
    """
    diag: Dict[str, Any] = {'session_id': session_id, 'dispatched': []}
    if not session_id:
        diag['error'] = 'session_id vide'
        return diag

    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq(
            'session_id', session_id
        ).maybe_single().execute()
    except Exception as e:
        diag['error'] = f'tx fetch failed: {e}'
        return diag

    if not tx_res or not tx_res.data:
        diag['error'] = 'tx not found'
        return diag

    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'lecture_complete':
        diag['error'] = 'kind mismatch'
        return diag

    if md.get('bundle_dispatched'):
        diag['already_dispatched'] = True
        return diag

    order_ctx = md.get('order_ctx') or {}
    email = tx.get('user_email') or order_ctx.get('email')
    first_name = (order_ctx.get('first_name') or 'Ami(e)').strip()
    birth_date_iso = order_ctx.get('birth_date') or ''
    birth_data = _build_birth_data(order_ctx)

    if not email or not birth_data:
        diag['error'] = 'missing email or birth_data'
        # marque l'erreur cote parent tx pour visibility admin
        md['bundle_error'] = diag['error']
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        return diag

    pdf_ctx = {
        'first_name': first_name,
        'birth_date_iso': birth_date_iso,
        'birth_data': birth_data,
    }

    # Envoi email de bienvenue immediat (best-effort)
    async def _send_welcome():
        try:
            from services.resend_service import send_email
            html = f"""
            <div style="font-family: Georgia, serif; color:#1a1030; line-height:1.6;">
              <h2 style="color:#d9b26a;">✦ Merci {first_name}</h2>
              <p>Ta Lecture Complete du Ciel est en cours de composition.</p>
              <p>Solena prepare pour toi 5 lectures profondes :</p>
              <ul>
                <li>✦ Ton Theme Natal decode</li>
                <li>✦ Ta Lecture Karmique &amp; Destinee</li>
                <li>✦ Ton Arbre de Vie Kabbale</li>
                <li>✦ Tes 12 Fenetres de Rencontre 2026</li>
                <li>✦ Ton Guide de Cycles Amoureux</li>
              </ul>
              <p>Tu recevras chaque lecture par email au fur et a mesure qu'elle est prete,
                dans les prochaines heures.</p>
              <p>Tes 4 presents (Rituel du Soir, Carte des Liens, Calendrier 12 fenetres,
                Question longue) te seront envoyes personnellement par Solena.</p>
              <p style="color:#6a5acd;font-style:italic;">Prends une grande respiration.
                La suite arrive.</p>
              <p>— Solena, Plume Astrale</p>
            </div>
            """
            await send_email(email, 'Ta Lecture Complete arrive · Plume Astrale', html)
        except Exception as e:
            logger.warning(f'[lecture_complete] welcome email failed: {e}')

    asyncio.create_task(_send_welcome())

    # 1. Theme Natal complet (theme_natal_pdf_oneshot)
    natal_sid = _insert_child_tx(sb, session_id, 'natal', 'theme_natal_pdf_oneshot',
                                 email, pdf_ctx)
    async def _do_natal():
        try:
            from services.theme_natal_oneshot_service import handle_theme_natal_oneshot_webhook
            await handle_theme_natal_oneshot_webhook(natal_sid)
        except Exception as e:
            logger.error(f'[lecture_complete] natal PDF failed: {e}')
    asyncio.create_task(_do_natal())
    diag['dispatched'].append('theme_natal')

    # 2. Karma & Destinee
    karma_sid = _insert_child_tx(sb, session_id, 'karma', 'karma_destin_analysis',
                                 email, pdf_ctx)
    async def _do_karma():
        try:
            from routes.karma_destin import _generate_and_email_pdf as karma_gen
            await karma_gen(email, pdf_ctx, karma_sid)
        except Exception as e:
            logger.error(f'[lecture_complete] karma PDF failed: {e}')
    asyncio.create_task(_do_karma())
    diag['dispatched'].append('karma_destin')

    # 3. Arbre de Vie Kabbale
    kabbale_sid = _insert_child_tx(sb, session_id, 'kabbale', 'kabbale_arbre_de_vie',
                                   email, pdf_ctx)
    async def _do_kabbale():
        try:
            from services.kabbale_service import handle_kabbale_webhook
            await handle_kabbale_webhook(kabbale_sid)
        except Exception as e:
            logger.error(f'[lecture_complete] kabbale PDF failed: {e}')
    asyncio.create_task(_do_kabbale())
    diag['dispatched'].append('kabbale')

    # 4. Fenetres de Rencontre 2026
    fenetre_sid = _insert_child_tx(sb, session_id, 'fenetre', 'fenetre_rencontre_avancee',
                                   email, pdf_ctx)
    async def _do_fenetre():
        try:
            from routes.fenetre_rencontre import _generate_and_email_pdf as fenetre_gen
            await fenetre_gen(email, pdf_ctx, fenetre_sid)
        except Exception as e:
            logger.error(f'[lecture_complete] fenetre PDF failed: {e}')
    asyncio.create_task(_do_fenetre())
    diag['dispatched'].append('fenetre_rencontre')

    # 5. Guide de Cycles / Rencontres Ultime
    # rencontres_ultime attend un pdf_ctx enrichi (m7_sign, venus_sign, mars_sign,
    # partner). Sans ces champs, l'handler fallback sur des valeurs par defaut
    # (Balance/vide). Acceptable pour un bundle — l'astro API fournira les signes reels.
    rencontres_sid = _insert_child_tx(sb, session_id, 'rencontres', 'rencontres_ultime',
                                      email, {**pdf_ctx, 'user_birth_data': birth_data})
    async def _do_rencontres():
        try:
            from services.rencontres_ultime_service import handle_rencontres_ultime_webhook
            await handle_rencontres_ultime_webhook(rencontres_sid)
        except Exception as e:
            logger.error(f'[lecture_complete] rencontres PDF failed: {e}')
    asyncio.create_task(_do_rencontres())
    diag['dispatched'].append('rencontres_ultime')

    # Marque le bundle comme dispatched (ne relance pas si retry webhook)
    md['bundle_dispatched'] = True
    md['bundle_dispatched_at'] = datetime.now(timezone.utc).isoformat()
    md['bundle_children'] = {
        'theme_natal': natal_sid,
        'karma_destin': karma_sid,
        'kabbale': kabbale_sid,
        'fenetre_rencontre': fenetre_sid,
        'rencontres_ultime': rencontres_sid,
    }
    try:
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete] update parent metadata: {e}')

    logger.info(f'[lecture_complete] bundle dispatched for {session_id}: {diag["dispatched"]}')
    return diag


# ═══════════════════════════════════════════════════════════════
# Compteur de rareté honnête (lectures restantes ce cycle lunaire)
# ═══════════════════════════════════════════════════════════════

MONTHLY_QUOTA = 12  # 12 lectures completes offertes par cycle (~28 jours)


def _current_lunar_cycle_bounds() -> tuple[datetime, datetime]:
    """Retourne le debut du cycle lunaire courant (jour 1 du mois calendaire)
    et son fin (jour 1 du mois suivant). Simplification pragmatique :
    on utilise le mois calendaire comme proxy du cycle lunaire.
    """
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Fin = jour 1 du mois suivant
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def get_scarcity_status() -> Dict[str, Any]:
    """Retourne {remaining, sold, quota, cycle_end_iso} pour le bandeau homepage.

    Compte les lectures completes vendues (status=completed, pack_id=lecture_complete,
    hors bypass admin) depuis le debut du mois calendaire courant.
    """
    start, end = _current_lunar_cycle_bounds()
    sb = get_admin_client()
    sold = 0
    try:
        r = sb.table('payment_transactions').select(
            'session_id, metadata, payment_status'
        ).eq('pack_id', 'lecture_complete').eq('payment_status', 'paid').gte(
            'created_at', start.isoformat()
        ).lt('created_at', end.isoformat()).execute()
        rows = (r.data or []) if r else []
        # Exclure les bypass admin (ne consomment pas le quota reel)
        sold = sum(
            1 for row in rows
            if not ((row.get('metadata') or {}).get('admin_bypass'))
        )
    except Exception as e:
        logger.warning(f'[lecture_complete] scarcity count failed: {e}')

    remaining = max(0, MONTHLY_QUOTA - sold)
    return {
        'remaining': remaining,
        'sold': sold,
        'quota': MONTHLY_QUOTA,
        'cycle_end': end.isoformat(),
        'sold_out': remaining == 0,
    }
