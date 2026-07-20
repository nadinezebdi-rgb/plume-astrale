"""
Email cross-sell J+7 : après achat Kabbale ou Pack Karmique, propose
l'Astrocartographie 49€ avec réduction "clients Plume" (15%).

Boucle background (6h). Idempotence via metadata.crosssell_astrocarto_sent_at.
Skip si l'utilisateur a déjà acheté l'astrocartographie.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
import httpx

from services.supabase_client import get_admin_client
from services.email_journal import log_send_attempt, log_send_response

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 6 * 3600  # toutes les 6h
SITE_URL = 'https://www.plume-astrale.fr'
ELIGIBLE_PACKS = ('kabbale_arbre_de_vie', 'pack_karmique_kabbale', 'karma_destin')
DISCOUNT_CODE = 'PLUME15'   # 15% off → 49€ * 0.85 = 41.65€


def _wrap(inner: str) -> str:
    return f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;margin-bottom:22px;">
        ✦ Plume Astrale · Une invitation ✦
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        {inner}
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">— Soléna</div>
          <div style="font-size:11px;color:#9089B5;margin-top:4px;">Astrologue &amp; guide chez Plume Astrale</div>
        </div>
      </div>
      <div style="text-align:center;margin-top:20px;font-size:10px;color:#666;letter-spacing:0.15em;">
        <a href="{SITE_URL}" style="color:#D4AF37;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """


def _email_crosssell(first_name: str, previous_product_label: str) -> tuple[str, str]:
    cta_url = f"{SITE_URL}/astrocartographie?discount={DISCOUNT_CODE}"
    inner = f"""
      <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;line-height:1.3;">
        {first_name}, <em style="color:#D4AF37;font-style:italic;">et si tu allais un cran plus loin ?</em>
      </h1>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        Il y a une semaine, tu as reçu ton <strong style="color:#D4AF37;">{previous_product_label}</strong>.
        J'espère qu'il t'accompagne encore, entre deux relectures.
      </p>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        Beaucoup de mes lectrices, après avoir exploré leur ciel intérieur, se posent une
        question évidente : <em>et si je vivais ailleurs ? Où serais-je vraiment moi-même ?</em>
      </p>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        C'est exactement ce que révèle l'<strong style="color:#D4AF37;">Astrocartographie</strong> —
        ta carte du monde avec toutes tes lignes planétaires, l'analyse détaillée de 3 villes
        que tu choisis, et 2 destinations bonus que je sélectionne rien que pour toi.
      </p>
      <div style="margin:26px 0;padding:22px 20px;background:rgba(212,175,55,0.08);border:1px solid rgba(212,175,55,0.3);border-radius:12px;text-align:center;">
        <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:6px;">
          ✦ Offre clientes Plume ✦
        </div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:20px;color:#F5EEE0;margin-bottom:8px;">
          15% de réduction — 41,65€ au lieu de 49€
        </div>
        <div style="font-size:12px;color:#9089B5;margin-bottom:14px;">
          Code : <strong style="color:#D4AF37;letter-spacing:0.2em;">{DISCOUNT_CODE}</strong> · valable 7 jours
        </div>
        <a href="{cta_url}"
           style="display:inline-block;background:#D4AF37;color:#111625;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none;">
          Découvrir ma carte du monde →
        </a>
      </div>
      <p style="color:#E3D7FF;line-height:1.7;font-size:14px;font-style:italic;">
        Cette réduction est réservée à celles qui m'ont déjà fait confiance. Elle ne s'applique
        qu'à travers ce lien.
      </p>
    """
    subject = f"{first_name}, une carte du monde t'attend"
    return subject, _wrap(inner)


PRODUCT_LABELS = {
    'kabbale_arbre_de_vie': "Arbre de Vie Kabbalistique",
    'pack_karmique_kabbale': "Pack Karmique + Kabbale",
    'karma_destin': "Rapport Karma & Destin",
}


async def _send(email: str, subject: str, html: str, session_id: str | None) -> bool:
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='crosssell_astrocarto_j7',
        from_email=sender, session_id=session_id,
    )
    if not resend_key:
        log_send_response(row_id, http_status=0, body='RESEND_API_KEY missing',
                          to_email=email, subject=subject, product='crosssell_astrocarto_j7', session_id=session_id)
        return False
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [email], 'subject': subject, 'html': html},
            )
            resend_id = None
            try:
                resend_id = r.json().get('id') if r.status_code < 300 else None
            except Exception:
                pass
            log_send_response(
                row_id, http_status=r.status_code, resend_id=resend_id,
                body=None if r.status_code < 300 else r.text,
                to_email=email, subject=subject, product='crosssell_astrocarto_j7', session_id=session_id,
            )
            if r.status_code >= 400:
                logger.warning(f'[crosssell_astrocarto] Resend {r.status_code}: {r.text[:150]}')
                return False
            return True
    except Exception as e:
        logger.warning(f'[crosssell_astrocarto] envoi échoué pour {email}: {e}')
        return False


def _has_bought_astrocarto(sb, email: str) -> bool:
    try:
        r = (
            sb.table('payment_transactions').select('session_id')
            .eq('user_email', email).eq('pack_id', 'astrocartographie')
            .eq('payment_status', 'paid').limit(1).execute()
        )
        return bool(r.data)
    except Exception:
        return False


async def _run_once() -> int:
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    since = (now - timedelta(days=45)).isoformat()
    until = (now - timedelta(days=7)).isoformat()

    try:
        r = (
            sb.table('payment_transactions').select('session_id,user_email,pack_id,metadata,created_at')
            .in_('pack_id', list(ELIGIBLE_PACKS))
            .eq('payment_status', 'paid')
            .gte('created_at', since)
            .lte('created_at', until)
            .limit(200)
            .execute()
        )
    except Exception as e:
        logger.warning(f'[crosssell_astrocarto] fetch failed: {e}')
        return 0

    sent = 0
    seen_emails: set[str] = set()   # 1 seul email par utilisateur, même si plusieurs achats
    for tx in (r.data or []):
        md = tx.get('metadata') or {}
        email = (tx.get('user_email') or '').strip().lower()
        session_id = tx.get('session_id')
        pack_id = tx.get('pack_id')

        if not email or '@' not in email:
            continue
        if md.get('crosssell_astrocarto_sent_at'):
            continue
        if email in seen_emails:
            continue
        if _has_bought_astrocarto(sb, email):
            # marquer skip pour ne plus refaire la vérif
            md['crosssell_astrocarto_sent_at'] = now.isoformat()
            md['crosssell_astrocarto_skipped_reason'] = 'already_owns_astrocarto'
            try:
                sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
            except Exception:
                pass
            continue

        pdf_ctx = md.get('pdf_ctx') or {}
        first_name = (pdf_ctx.get('first_name') or 'Voyageur').strip().title() or 'Voyageur'
        prev_label = PRODUCT_LABELS.get(pack_id, "rapport Plume")

        subject, html = _email_crosssell(first_name, prev_label)
        ok = await _send(email, subject, html, session_id=session_id)

        md['crosssell_astrocarto_sent_at'] = now.isoformat()
        md['crosssell_astrocarto_ok'] = bool(ok)
        try:
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f'[crosssell_astrocarto] update failed for {session_id}: {e}')
        seen_emails.add(email)
        if ok:
            sent += 1
            logger.info(f'[crosssell_astrocarto] J+7 envoyé à {email} ({pack_id})')
    return sent


async def crosssell_astrocarto_loop() -> None:
    logger.info('[crosssell_astrocarto] boucle démarrée (toutes les 6h — J+7 cross-sell)')
    while True:
        try:
            sent = await _run_once()
            if sent:
                logger.info(f'[crosssell_astrocarto] {sent} email(s) cross-sell envoyé(s)')
        except Exception as e:
            logger.warning(f'[crosssell_astrocarto] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
