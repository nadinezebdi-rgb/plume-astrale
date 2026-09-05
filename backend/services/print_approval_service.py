"""
print_approval_service.py — Flow d'approbation 72h "Vous lisez avant qu'on imprime"
====================================================================================

Édition Reliée Plume Astrale (149€) — dépose : /app/backend/migrations/2026_02_print_approvals.sql

Cycle de vie d'une approbation :
    1. Après paiement Stripe → `create_print_approval(...)` :
       - Insert row `print_approvals` (status='awaiting_review', deadline_at=+72h)
       - Envoie l'email initial avec liens 1-clic approuver / refuser.

    2. La cliente clique "Approuver" (GET /r/approve/{token}) :
       - Marque `approved_at` + status='approved'
       - Affiche une page de remerciement + notifie l'admin (email).

    3. La cliente clique "Refuser" ou ne répond pas :
       - Refus explicite → POST /api/print-approval/refuse avec raison optionnelle.
       - Silence → rappels doux à J+1 et J+2 (idempotents). À J+3, status='expired'.

Les tokens sont opaques (uuid.hex, 32 chars). Une seule action possible par token.
"""
from __future__ import annotations
import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# ── Constantes ───────────────────────────────────────────────
DEADLINE_HOURS = 72
REMINDER_24H_AFTER_CREATED_HOURS = 24
REMINDER_48H_AFTER_CREATED_HOURS = 48
LOOP_INTERVAL_SEC = 15 * 60  # 15 min entre chaque check du loop

SITE_URL = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
ADMIN_ALERT_EMAIL = os.environ.get('ADMIN_ALERT_EMAIL', 'contact@plume-astrale.fr')


# ── API métier ────────────────────────────────────────────────

async def create_print_approval(
    *,
    order_ref: str,
    purchaser_email: str,
    purchaser_first_name: Optional[str],
    recipient_first_name: Optional[str],
    pdf_url: str,
    product_kind: str = 'edition_reliee',
) -> dict:
    """Crée une demande d'approbation 72h et envoie l'email initial.

    Args:
        order_ref: identifiant de la commande source (Stripe session_id ou payment_transactions.id).
        purchaser_email: email de la personne qui reçoit et approuve le PDF.
        purchaser_first_name: prénom de l'acheteuse (personnalisation email).
        recipient_first_name: prénom de la destinataire finale du livre imprimé.
        pdf_url: URL secure du PDF à relire (token opaque).
        product_kind: variant produit ('edition_reliee' | 'edition_reliee_deux_vies').

    Returns:
        dict {id, approve_token, refuse_token, deadline_at, email_sent}
    """
    approval_id = uuid.uuid4().hex
    approve_token = uuid.uuid4().hex
    refuse_token = uuid.uuid4().hex

    now = datetime.now(timezone.utc)
    deadline = now + timedelta(hours=DEADLINE_HOURS)

    row = {
        'id': approval_id,
        'order_ref': order_ref,
        'product_kind': product_kind,
        'purchaser_email': purchaser_email.strip().lower(),
        'purchaser_first_name': (purchaser_first_name or '')[:80] or None,
        'recipient_first_name': (recipient_first_name or '')[:80] or None,
        'pdf_url': pdf_url,
        'status': 'awaiting_review',
        'approve_token': approve_token,
        'refuse_token': refuse_token,
        'created_at': now.isoformat(),
        'deadline_at': deadline.isoformat(),
        'updated_at': now.isoformat(),
    }

    sb = get_admin_client()
    try:
        sb.table('print_approvals').insert(row).execute()
    except Exception as e:
        logger.exception(f'[print_approval] insert failed: {e}')
        raise

    email_sent = False
    try:
        email_sent = await _send_initial_email(row)
    except Exception as e:
        logger.warning(f'[print_approval] initial email failed: {e}')

    return {
        'id': approval_id,
        'approve_token': approve_token,
        'refuse_token': refuse_token,
        'deadline_at': deadline.isoformat(),
        'email_sent': email_sent,
    }


def get_by_token(token: str, kind: str = 'approve') -> Optional[dict]:
    """Fetch une approbation par approve_token ou refuse_token."""
    if not token or len(token) < 16 or len(token) > 64:
        return None
    col = 'approve_token' if kind == 'approve' else 'refuse_token'
    sb = get_admin_client()
    try:
        r = sb.table('print_approvals').select('*').eq(col, token).maybe_single().execute()
        return r.data if r and r.data else None
    except Exception as e:
        logger.warning(f'[print_approval] fetch by {kind} token failed: {e}')
        return None


async def approve(token: str) -> Optional[dict]:
    """Approuve la relecture (appelé quand la cliente clique le lien 1-clic)."""
    row = get_by_token(token, kind='approve')
    if not row:
        return None

    if row['status'] == 'approved':
        # Idempotence : deja approuve
        return {**row, 'already': True}
    if row['status'] not in ('awaiting_review', 'expired'):
        return {**row, 'error': 'invalid_status'}

    now = datetime.now(timezone.utc).isoformat()
    sb = get_admin_client()
    sb.table('print_approvals').update({
        'status': 'approved',
        'approved_at': now,
        'updated_at': now,
    }).eq('id', row['id']).execute()

    try:
        await _notify_admin_approval(row, decision='approved')
    except Exception as e:
        logger.warning(f'[print_approval] admin notify failed: {e}')

    return {**row, 'status': 'approved', 'approved_at': now}


async def refuse(token: str, reason: Optional[str] = None) -> Optional[dict]:
    """Refuse la relecture — remboursement intégral, rien imprimé."""
    row = get_by_token(token, kind='refuse')
    if not row:
        return None

    if row['status'] == 'refused':
        return {**row, 'already': True}
    if row['status'] not in ('awaiting_review', 'expired'):
        return {**row, 'error': 'invalid_status'}

    now = datetime.now(timezone.utc).isoformat()
    sb = get_admin_client()
    sb.table('print_approvals').update({
        'status': 'refused',
        'refused_at': now,
        'refused_reason': (reason or '')[:1000] or None,
        'updated_at': now,
    }).eq('id', row['id']).execute()

    try:
        await _notify_admin_approval(row, decision='refused', reason=reason)
    except Exception as e:
        logger.warning(f'[print_approval] admin notify failed: {e}')

    return {**row, 'status': 'refused', 'refused_at': now}


# ── Emails ────────────────────────────────────────────────────

async def _send_initial_email(row: dict) -> bool:
    """Email initial : le PDF est prêt, vous avez 72h pour approuver ou refuser."""
    from services.resend_service import send_email

    approve_link = f'{SITE_URL}/api/print-approval/approve/{row["approve_token"]}'
    refuse_link = f'{SITE_URL}/relecture/{row["refuse_token"]}'  # front page dédiée refus + raison
    pdf_link = row['pdf_url']

    purchaser = row.get('purchaser_first_name') or ''
    hello = f'Bonjour {purchaser},' if purchaser else 'Bonjour,'
    recipient_ref = row.get('recipient_first_name') or 'la destinataire'
    recipient_line = (
        f'Voici le livre destiné à <b>{recipient_ref}</b>, tel qu\'il sera imprimé.'
        if row.get('recipient_first_name')
        else 'Voici le livre tel qu\'il sera imprimé.'
    )

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0C0918;font-family:Georgia,'Cormorant Garamond',serif;color:#F0E6D3;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0C0918;">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="580" cellpadding="0" cellspacing="0" style="max-width:580px;background:#15112A;border:1px solid rgba(212,180,106,0.22);border-radius:12px;overflow:hidden;">
      <tr><td style="padding:36px 40px 12px;text-align:center;border-bottom:1px solid rgba(212,180,106,0.14);">
        <p style="margin:0;font-size:11px;letter-spacing:0.32em;color:#D4B46A;text-transform:uppercase;">Plume Astrale · Édition Reliée</p>
        <h1 style="margin:16px 0 0;font-family:'Playfair Display',Georgia,serif;font-size:26px;color:#F5EEE0;font-weight:400;line-height:1.2;">
          Votre livre est prêt à être relu.
        </h1>
      </td></tr>
      <tr><td style="padding:32px 40px;font-size:16px;line-height:1.7;">
        <p style="margin:0 0 16px;">{hello}</p>
        <p style="margin:0 0 16px;">{recipient_line} Ouvrez-le, prenez le temps qu'il vous faut. <b>Vous avez 72 heures pour décider.</b></p>

        <p style="text-align:center;margin:32px 0;">
          <a href="{pdf_link}" style="display:inline-block;padding:14px 30px;background:transparent;color:#E8C766;border:1px solid #D4AF37;text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:12px;letter-spacing:0.24em;text-transform:uppercase;border-radius:4px;">
            OUVRIR LE PDF
          </a>
        </p>

        <div style="margin:32px 0 16px;padding:20px 22px;background:rgba(212,175,55,0.06);border-left:2px solid #D4AF37;font-size:15px;line-height:1.65;">
          Deux boutons ci-dessous. Un seul geste.
        </div>

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 24px;">
          <tr>
            <td width="50%" style="padding-right:8px;" align="center">
              <a href="{approve_link}" style="display:block;padding:14px 12px;background:linear-gradient(135deg,#D4AF37,#E8C766);color:#0F1A3C;text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:12px;letter-spacing:0.22em;text-transform:uppercase;border-radius:4px;font-weight:600;">
                APPROUVER · IMPRIMEZ
              </a>
              <p style="margin:8px 0 0;font-size:12px;color:rgba(240,230,211,0.6);">Le texte me touche. On lance l'impression.</p>
            </td>
            <td width="50%" style="padding-left:8px;" align="center">
              <a href="{refuse_link}" style="display:block;padding:14px 12px;background:transparent;color:#F0E6D3;border:1px solid rgba(240,230,211,0.35);text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:12px;letter-spacing:0.22em;text-transform:uppercase;border-radius:4px;">
                DIRE POURQUOI ÇA NE VA PAS
              </a>
              <p style="margin:8px 0 0;font-size:12px;color:rgba(240,230,211,0.6);">Remboursement intégral. Rien ne s'imprime.</p>
            </td>
          </tr>
        </table>

        <p style="margin:24px 0 0;font-size:14px;color:rgba(240,230,211,0.7);line-height:1.65;">
          Sans réponse dans 72 heures, je vous relance doucement à J+1 puis J+2.
          Je ne lancerai jamais l'impression sans votre feu vert.
        </p>

        <p style="margin:32px 0 0;font-family:'Playfair Display',Georgia,serif;font-style:italic;font-size:18px;color:#E8C766;text-align:right;">
          — Nadine
        </p>
      </td></tr>
      <tr><td style="padding:20px 40px 28px;border-top:1px solid rgba(212,180,106,0.12);text-align:center;color:rgba(184,176,200,0.55);font-size:11px;line-height:1.7;">
        Plume Astrale · <a href="{SITE_URL}" style="color:#D4B46A;text-decoration:none;">plume-astrale.fr</a><br>
        Cet email a été envoyé à {row['purchaser_email']} suite à votre commande.
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>
"""

    subject = 'Votre livre est prêt à être relu · Plume Astrale'
    email_id = await send_email(row['purchaser_email'], subject, html)
    return bool(email_id)


async def _send_reminder_email(row: dict, kind: str) -> bool:
    """Rappel doux à J+1 ou J+2.

    Args:
        kind: '24h' ou '48h' (affecte le ton et la deadline affichée).
    """
    from services.resend_service import send_email

    approve_link = f'{SITE_URL}/api/print-approval/approve/{row["approve_token"]}'
    refuse_link = f'{SITE_URL}/relecture/{row["refuse_token"]}'
    pdf_link = row['pdf_url']

    purchaser = row.get('purchaser_first_name') or ''
    hello = f'Bonjour {purchaser},' if purchaser else 'Bonjour,'

    if kind == '24h':
        subject = 'Le livre vous attend · plus que 48 h'
        headline = 'Le livre vous attend encore.'
        message = (
            "Vous l'avez reçu hier — je sais, la vie est pleine. "
            "Le PDF est toujours ouvrable ci-dessous, vous avez encore <b>48 heures</b> pour décider."
        )
    else:  # 48h
        subject = 'Dernière relance · votre relecture expire dans 24 h'
        headline = 'Il vous reste 24 heures.'
        message = (
            "Dernière relance douce. Passé demain à la même heure, "
            "l'impression restera en attente et j'attendrai un mot de votre part. "
            "Aucune impression ne partira sans votre accord — je préfère prendre du retard qu'imprimer un livre qui ne vous touche pas."
        )

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0C0918;font-family:Georgia,serif;color:#F0E6D3;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px;">
<table role="presentation" width="560" style="max-width:560px;background:#15112A;border:1px solid rgba(212,180,106,0.22);border-radius:12px;overflow:hidden;">
  <tr><td style="padding:32px 36px 8px;text-align:center;border-bottom:1px solid rgba(212,180,106,0.12);">
    <p style="margin:0;font-size:11px;letter-spacing:0.3em;color:#D4B46A;text-transform:uppercase;">Plume Astrale</p>
    <h1 style="margin:14px 0 0;font-family:'Playfair Display',Georgia,serif;font-size:24px;color:#F5EEE0;font-weight:400;">{headline}</h1>
  </td></tr>
  <tr><td style="padding:30px 36px;font-size:16px;line-height:1.7;">
    <p style="margin:0 0 14px;">{hello}</p>
    <p style="margin:0 0 22px;">{message}</p>
    <p style="text-align:center;margin:24px 0;">
      <a href="{pdf_link}" style="display:inline-block;padding:12px 26px;color:#E8C766;border:1px solid #D4AF37;text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:11.5px;letter-spacing:0.22em;text-transform:uppercase;border-radius:4px;">RE-OUVRIR LE PDF</a>
    </p>
    <table role="presentation" width="100%" style="margin:14px 0;"><tr>
      <td width="50%" style="padding-right:6px;" align="center">
        <a href="{approve_link}" style="display:block;padding:12px 8px;background:linear-gradient(135deg,#D4AF37,#E8C766);color:#0F1A3C;text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:11.5px;letter-spacing:0.22em;text-transform:uppercase;border-radius:4px;font-weight:600;">APPROUVER</a>
      </td>
      <td width="50%" style="padding-left:6px;" align="center">
        <a href="{refuse_link}" style="display:block;padding:12px 8px;color:#F0E6D3;border:1px solid rgba(240,230,211,0.35);text-decoration:none;font-family:'Cinzel',Georgia,serif;font-size:11.5px;letter-spacing:0.22em;text-transform:uppercase;border-radius:4px;">M'EXPRIMER</a>
      </td>
    </tr></table>
    <p style="margin:24px 0 0;font-family:'Playfair Display',Georgia,serif;font-style:italic;font-size:17px;color:#E8C766;text-align:right;">— Nadine</p>
  </td></tr>
</table>
</td></tr></table></body></html>
"""

    email_id = await send_email(row['purchaser_email'], subject, html)
    return bool(email_id)


async def _notify_admin_approval(row: dict, *, decision: str, reason: Optional[str] = None) -> None:
    """Alerte admin quand une décision est prise (approve/refuse)."""
    from services.resend_service import send_email

    if decision == 'approved':
        subject = f'[Plume Astrale] Approuvé · imprimer pour {row["purchaser_email"]}'
        body = f"""<p><b>{row.get('purchaser_first_name') or row['purchaser_email']}</b> a approuvé son Édition Reliée.</p>
<p>Order ref : <code>{row['order_ref']}</code></p>
<p>Destinataire : {row.get('recipient_first_name') or '—'}</p>
<p><b>Prochaine étape : lancer l'impression.</b></p>"""
    else:
        subject = f'[Plume Astrale] REFUS · rembourser {row["purchaser_email"]}'
        body = f"""<p><b>{row.get('purchaser_first_name') or row['purchaser_email']}</b> a refusé son Édition Reliée.</p>
<p>Order ref : <code>{row['order_ref']}</code></p>
<p>Raison : <em>{reason or 'aucune raison précisée'}</em></p>
<p><b>Prochaine étape : rembourser via Stripe. Rien à imprimer.</b></p>"""

    html = f"""<html><body style="font-family:Georgia,serif;color:#0F1A3C;padding:20px;">
<h2 style="color:#D4AF37;">Décision de relecture</h2>
{body}
<p style="margin-top:20px;font-size:12px;color:#666;">— Notification automatique · print_approval_service</p>
</body></html>"""

    await send_email(ADMIN_ALERT_EMAIL, subject, html)


# ── Loop de rappels ───────────────────────────────────────────

async def _process_reminders() -> dict:
    """Envoie les rappels 24h/48h et expire les dossiers > 72h.

    Retourne un compteur {reminded_24h, reminded_48h, expired}.
    """
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    stats = {'reminded_24h': 0, 'reminded_48h': 0, 'expired': 0}

    try:
        r = sb.table('print_approvals').select('*').eq('status', 'awaiting_review').execute()
        rows = r.data or []
    except Exception as e:
        logger.warning(f'[print_approval] loop fetch failed: {e}')
        return stats

    for row in rows:
        try:
            created = _parse_iso(row['created_at'])
            deadline = _parse_iso(row['deadline_at'])
            if not created or not deadline:
                continue
            age_hours = (now - created).total_seconds() / 3600.0

            # Expiration > 72h : marquer status='expired' + notifier admin
            if now >= deadline:
                sb.table('print_approvals').update({
                    'status': 'expired',
                    'expired_at': now.isoformat(),
                    'updated_at': now.isoformat(),
                }).eq('id', row['id']).execute()
                stats['expired'] += 1
                try:
                    await _notify_admin_expired(row)
                except Exception:
                    pass
                continue

            # Rappel 48h (envoyé à J+2, entre 47h et 71h de vie)
            if (age_hours >= REMINDER_48H_AFTER_CREATED_HOURS
                    and not row.get('reminder_48h_sent_at')):
                sent = await _send_reminder_email(row, kind='48h')
                if sent:
                    sb.table('print_approvals').update({
                        'reminder_48h_sent_at': now.isoformat(),
                        'updated_at': now.isoformat(),
                    }).eq('id', row['id']).execute()
                    stats['reminded_48h'] += 1
                continue

            # Rappel 24h (envoyé à J+1, entre 23h et 47h de vie)
            if (age_hours >= REMINDER_24H_AFTER_CREATED_HOURS
                    and not row.get('reminder_24h_sent_at')):
                sent = await _send_reminder_email(row, kind='24h')
                if sent:
                    sb.table('print_approvals').update({
                        'reminder_24h_sent_at': now.isoformat(),
                        'updated_at': now.isoformat(),
                    }).eq('id', row['id']).execute()
                    stats['reminded_24h'] += 1

        except Exception as e:
            logger.warning(f'[print_approval] row {row.get("id")} loop error: {e}')

    return stats


async def _notify_admin_expired(row: dict) -> None:
    """Alerte admin quand un dossier expire sans réponse."""
    from services.resend_service import send_email
    subject = f'[Plume Astrale] Expiré 72h · {row["purchaser_email"]}'
    html = f"""<html><body style="font-family:Georgia,serif;color:#0F1A3C;padding:20px;">
<h2 style="color:#B47562;">Dossier expiré (72h)</h2>
<p><b>{row.get('purchaser_first_name') or row['purchaser_email']}</b> n'a pas répondu dans les 72h.</p>
<p>Order ref : <code>{row['order_ref']}</code></p>
<p><b>Action manuelle requise :</b> écrire un mot personnel avant d'imprimer.</p>
</body></html>"""
    await send_email(ADMIN_ALERT_EMAIL, subject, html)


async def print_approval_loop():
    """Background loop — vérifie les rappels toutes les 15 minutes.

    À démarrer dans server.py startup (`asyncio.create_task(print_approval_loop())`).
    """
    logger.info(f'[print_approval] loop démarré — cycle {LOOP_INTERVAL_SEC}s')
    # Startup grace period : évite de bloquer le boot avec envoi d'emails
    # + génération de PDF de rappel dès le démarrage (Feb 2026).
    try:
        await asyncio.sleep(120)
    except asyncio.CancelledError:
        raise
    while True:
        try:
            stats = await _process_reminders()
            if any(stats.values()):
                logger.info(f'[print_approval] cycle: {stats}')
        except Exception as e:
            logger.exception(f'[print_approval] loop error: {e}')
        try:
            await asyncio.sleep(LOOP_INTERVAL_SEC)
        except asyncio.CancelledError:
            raise


# ── Helpers ───────────────────────────────────────────────────

def _parse_iso(iso: str) -> Optional[datetime]:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def list_pending(limit: int = 50) -> list:
    """Liste admin des dossiers en cours (approbation ou expirés)."""
    sb = get_admin_client()
    try:
        r = (
            sb.table('print_approvals')
            .select('id, order_ref, purchaser_email, purchaser_first_name, recipient_first_name, '
                    'status, created_at, deadline_at, reminder_24h_sent_at, reminder_48h_sent_at, '
                    'approved_at, refused_at, refused_reason, expired_at')
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )
        return r.data or []
    except Exception as e:
        logger.warning(f'[print_approval] list_pending failed: {e}')
        return []
