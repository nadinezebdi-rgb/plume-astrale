"""
Séquence email post-achat pour Astrocartographie (49€).

Envoie un email J+3 après achat pour :
  - Prendre des nouvelles ("Que penses-tu de ton rapport ?")
  - Solliciter un avis / témoignage
  - Créer une relation de confiance (pas de vente)

Boucle background démarrée au startup FastAPI (toutes les 6h).
Idempotence : marque `metadata.followup_j3_sent_at` sur la transaction.
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


def _wrap(first_name: str, inner: str, email: str) -> str:
    return f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;margin-bottom:22px;">
        ✦ Plume Astrale · Un mot de Soléna ✦
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        {inner}
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">
            — Soléna
          </div>
          <div style="font-size:11px;color:#9089B5;margin-top:4px;">Astrologue &amp; guide chez Plume Astrale</div>
        </div>
      </div>
      <div style="text-align:center;margin-top:20px;font-size:10px;color:#666;letter-spacing:0.15em;">
        <a href="{SITE_URL}" style="color:#D4AF37;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """


def _email_astrocarto_j3(first_name: str, email: str) -> tuple[str, str]:
    inner = f"""
      <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;line-height:1.3;">
        {first_name}, <em style="color:#D4AF37;font-style:italic;">as-tu ouvert ta carte du monde ?</em>
      </h1>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        Trois jours que ton astrocartographie t'attend dans ta boîte mail.
        Je pense à toi. J'aime savoir ce que mes lecteurs ressentent quand ils lisent leur rapport
        pour la première fois — quelle ville les fait vibrer, laquelle ils écartent d'instinct.
      </p>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        Est-ce qu'une destination a résonné plus fort que les autres ? Est-ce qu'un passage t'a fait
        sourire, ou t'a serré le cœur ?
      </p>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;">
        <strong style="color:#D4AF37;">Réponds-moi simplement à cet email</strong> — un mot,
        une phrase, ton ressenti. Je lis chaque réponse personnellement. Et si tu as envie de partager
        ton expérience publiquement, ton témoignage aiderait d'autres âmes à oser demander leur propre
        carte.
      </p>
      <p style="color:#E3D7FF;line-height:1.7;font-size:15px;font-style:italic;">
        Prends soin de toi, où que tu sois.
      </p>
    """
    subject = f"{first_name}, ta carte du monde t'a-t-elle parlé ?"
    return subject, _wrap(first_name, inner, email)


async def _send(email: str, subject: str, html: str, session_id: str | None) -> bool:
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='astrocartographie_followup_j3',
        from_email=sender, session_id=session_id,
    )
    if not resend_key:
        log_send_response(row_id, http_status=0, body='RESEND_API_KEY missing',
                          to_email=email, subject=subject, product='astrocartographie_followup_j3', session_id=session_id)
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
                to_email=email, subject=subject, product='astrocartographie_followup_j3', session_id=session_id,
            )
            if r.status_code >= 400:
                logger.warning(f'[astrocarto_followup] Resend {r.status_code}: {r.text[:150]}')
                return False
            return True
    except Exception as e:
        logger.warning(f'[astrocarto_followup] envoi échoué pour {email}: {e}')
        return False


async def _run_once() -> int:
    """Envoie l'email J+3 aux achats astrocarto payés il y a ≥3 jours et ≤14 jours."""
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    since = (now - timedelta(days=14)).isoformat()
    until = (now - timedelta(days=3)).isoformat()

    try:
        r = (
            sb.table('payment_transactions').select('session_id,user_email,metadata,updated_at,created_at')
            .eq('pack_id', 'astrocartographie')
            .eq('payment_status', 'paid')
            .gte('created_at', since)
            .lte('created_at', until)
            .limit(100)
            .execute()
        )
    except Exception as e:
        logger.warning(f'[astrocarto_followup] fetch failed: {e}')
        return 0

    sent = 0
    for tx in (r.data or []):
        md = tx.get('metadata') or {}
        # Idempotence : skip si déjà envoyé
        if md.get('followup_j3_sent_at'):
            continue
        # Skip si le PDF n'a pas été livré (rare cas d'erreur)
        if not md.get('pdf_path'):
            continue
        email = (tx.get('user_email') or '').strip()
        if not email or '@' not in email:
            continue
        pdf_ctx = md.get('pdf_ctx') or {}
        first_name = (pdf_ctx.get('first_name') or 'Voyageur').strip().title() or 'Voyageur'
        session_id = tx.get('session_id')

        subject, html = _email_astrocarto_j3(first_name, email)
        ok = await _send(email, subject, html, session_id=session_id)

        # Marquer comme envoyé (idempotence) même si Resend a échoué
        # → évite spam en cas de retry loop
        md['followup_j3_sent_at'] = now.isoformat()
        md['followup_j3_ok'] = bool(ok)
        try:
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f'[astrocarto_followup] mark sent failed for {session_id}: {e}')
        if ok:
            sent += 1
            logger.info(f'[astrocarto_followup] J+3 envoyé à {email} ({session_id})')
    return sent


async def astrocarto_followup_loop() -> None:
    """Boucle background démarrée au startup FastAPI."""
    logger.info('[astrocarto_followup] boucle démarrée (toutes les 6h — J+3 relance)')
    while True:
        try:
            sent = await _run_once()
            if sent:
                logger.info(f'[astrocarto_followup] {sent} email(s) J+3 envoyé(s)')
        except Exception as e:
            logger.warning(f'[astrocarto_followup] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
