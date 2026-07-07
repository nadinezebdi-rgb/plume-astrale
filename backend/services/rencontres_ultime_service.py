"""
Orchestrateur post-paiement pour le pack "rencontres_ultime" (29,99 EUR).
Genere le PDF 15 pages + envoie l'email via Resend.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import httpx

from services.supabase_client import get_admin_client
from services.rencontres_ultime_pdf import generate_rencontres_ultime_pdf

logger = logging.getLogger(__name__)

# ASSETS_DIR est aussi utilise dans server.py — on garde la meme convention.
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


async def handle_rencontres_ultime_webhook(session_id: str) -> None:
    """Genere le PDF Ultime et envoie l'email au client. Best-effort (idempotent)."""
    if not session_id:
        return
    sb = get_admin_client()
    tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    if not tx_res or not tx_res.data:
        logger.warning(f"[rencontres_ultime] tx not found for {session_id}")
        return
    tx = tx_res.data

    md = tx.get('metadata') or {}
    if md.get('kind') != 'rencontres_ultime':
        return

    # Marquer le paiement comme complete si pas deja fait
    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,   # meme si pas de credits, on marque comme delivre
        }).eq('session_id', session_id).execute()

    # Idempotence : ne pas regenerer si deja fait
    if md.get('pdf_path'):
        logger.info(f"[rencontres_ultime] PDF already generated for {session_id}")
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Ami(e)'
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    m7_sign = pdf_ctx.get('m7_sign') or 'Balance'
    venus_sign = pdf_ctx.get('venus_sign') or ''
    mars_sign = pdf_ctx.get('mars_sign') or ''

    # Generation PDF best-effort
    pdf_path = None
    try:
        pdf_bytes = generate_rencontres_ultime_pdf(
            birth_date_iso=birth_date_iso,
            first_name=first_name,
            m7_sign=m7_sign,
            venus_sign=venus_sign,
            mars_sign=mars_sign,
        )
        out_dir = ASSETS_DIR / 'rencontres_ultime'
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f'ultime_{session_id[-16:]}.pdf'
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/rencontres_ultime/{filename}'

        # Update metadata avec le path
        md['pdf_path'] = pdf_path
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[rencontres_ultime] PDF generated: {pdf_path}")
    except Exception as e:
        logger.error(f"[rencontres_ultime] PDF gen failed for {session_id}: {e}", exc_info=True)
        return

    # Envoi email best-effort
    if email and pdf_path:
        try:
            await _send_ultime_email(email, first_name, pdf_bytes, filename)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[rencontres_ultime] email send failed for {session_id}: {e}")


async def _send_ultime_email(email: str, first_name: str, pdf_bytes: bytes, filename: str) -> None:
    """Envoie le PDF en piece jointe via Resend."""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    if not api_key:
        logger.warning("[rencontres_ultime] RESEND_API_KEY missing, skipping email")
        return

    import base64
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#333;background:#F7F1E4;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#C5A059;">
          ✦ Plume Astrale ✦
        </div>
      </div>

      <div style="background:#fff;border-radius:16px;padding:32px 28px;box-shadow:0 8px 32px rgba(0,0,0,0.08);">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:26px;color:#0C0918;margin:0 0 12px;line-height:1.2;">
          {first_name.title() if first_name else 'Cher(e) ami(e)'},<br>
          <em style="color:#C5A059;font-style:italic;">ton Guide de Compatibilité Ultime</em><br>
          est prêt.
        </h1>
        <p style="color:#555;line-height:1.6;font-size:15px;">
          15 pages entièrement personnalisées pour toi, sur ton potentiel amoureux des 6 prochains mois.
        </p>
        <ul style="color:#555;line-height:1.8;font-size:14px;padding-left:20px;">
          <li>Ton portrait astral amoureux complet (Soleil · Lune · Vénus · Mars · Maison V et VII)</li>
          <li>Le portrait-robot de ton âme sœur</li>
          <li><strong>Tes 3 fenêtres de rencontre précises</strong> sur les 6 prochains mois</li>
          <li>Les rituels énergétiques d'attraction (lithothérapie, bougies, méditation)</li>
        </ul>

        <div style="margin-top:24px;padding:20px;background:#0C0918;color:#F4E8D2;border-radius:12px;text-align:center;">
          <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#C5A059;margin-bottom:8px;">
            ✦ Ton document est en pièce jointe ✦
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F4E8D2;">
            Prends le temps de le lire dans un moment calme.<br>
            Reviens-y quand ton cœur en aura besoin.
          </div>
        </div>

        <div style="margin-top:32px;padding-top:20px;border-top:1px solid #eee;text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#0C0918;font-size:18px;">
            — Solena
          </div>
          <div style="font-size:11px;color:#888;margin-top:4px;">
            Astrologue &amp; guide chez Plume Astrale
          </div>
        </div>
      </div>

      <div style="text-align:center;margin-top:24px;font-size:10px;color:#aaa;letter-spacing:0.15em;">
        <a href="https://plume-astrale.fr/solena" style="color:#C5A059;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': sender,
                'to': [email],
                'subject': 'Ton Guide de Compatibilité Ultime est prêt ✦',
                'html': html,
                'attachments': [
                    {
                        'filename': filename,
                        'content': pdf_b64,
                    }
                ],
            },
        )
        if r.status_code >= 400:
            logger.warning(f"[rencontres_ultime] Resend error {r.status_code}: {r.text[:300]}")
        else:
            logger.info(f"[rencontres_ultime] Email sent to {email}")
