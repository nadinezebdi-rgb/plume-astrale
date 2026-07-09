"""
Orchestrateur post-paiement pour le pack "kabbale_arbre_de_vie" (39 EUR).
Fetch les donnees /kabbalah/tree-of-life-chart + genere le PDF + envoie l'email.
"""
from __future__ import annotations
import asyncio
import base64
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio
from services.kabbale_pdf import generate_kabbale_pdf

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


async def handle_kabbale_webhook(session_id: str) -> None:
    """Genere le PDF Kabbale + envoie l'email au client (idempotent, best-effort)."""
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[kabbale] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        logger.warning(f"[kabbale] tx not found for {session_id}")
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'kabbale_arbre_de_vie':
        return

    # Marquer paiement complete
    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence
    if md.get('pdf_path'):
        logger.info(f"[kabbale] PDF already generated for {session_id}")
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Ami(e)'
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    birth_data = pdf_ctx.get('birth_data') or {}

    # 1) Fetch tree-of-life-chart depuis astrology-api.io v3
    tree_data = None
    try:
        if birth_data:
            tree_data = await aio.tree_of_life_chart(
                birth_data, system='modern_halevi', tradition='psychological', language='fr'
            )
    except Exception as e:
        logger.error(f"[kabbale] tree_of_life_chart fetch failed for {session_id}: {e}")

    if not tree_data:
        logger.error(f"[kabbale] no tree data for {session_id} — cannot generate PDF")
        return

    # 2) Generation PDF
    pdf_bytes = None
    pdf_path = None
    filename = f'kabbale_{session_id[-16:]}.pdf'
    try:
        pdf_bytes = generate_kabbale_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            tree_of_life=tree_data,
        )
        out_dir = ASSETS_DIR / 'kabbale'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/kabbale/{filename}'
        md['pdf_path'] = pdf_path
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[kabbale] PDF generated: {pdf_path}")
    except Exception as e:
        logger.error(f"[kabbale] PDF gen failed for {session_id}: {e}", exc_info=True)
        return

    # 3) Envoi email best-effort
    if email and pdf_bytes:
        try:
            await _send_kabbale_email(email, first_name, pdf_bytes, filename)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[kabbale] email failed for {session_id}: {e}")


async def _send_kabbale_email(email: str, first_name: str, pdf_bytes: bytes, filename: str) -> None:
    """Envoi email Resend avec PDF en piece jointe."""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    if not api_key:
        logger.warning("[kabbale] RESEND_API_KEY missing")
        return

    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    fn = (first_name or 'ami(e)').strip()

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;">
          ✦ Plume Astrale · Kabbale ✦
        </div>
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#F5EEE0;margin:0 0 14px;line-height:1.25;">
          {fn.title()},<br>
          <em style="color:#D4AF37;font-style:italic;">ton Arbre de Vie</em><br>
          Kabbalistique est prêt.
        </h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Un document intime de 15 pages, tracé pour toi seul(e). Il révèle ta Sephirah dominante,
          tes 22 chemins activés, l'équilibre de tes trois piliers, et le sens spirituel profond de ton
          incarnation.
        </p>
        <ul style="color:#E3D7FF;line-height:1.9;font-size:14px;padding-left:20px;">
          <li>Les <strong>10 Sephiroth</strong> personnalisées selon ton thème natal</li>
          <li>Les <strong>22 chemins</strong> zodiacaux activés par tes planètes</li>
          <li>Le <strong>Da'at</strong>, ton pont vers la Connaissance intérieure</li>
          <li>Trois <strong>rituels d'intégration</strong> à pratiquer sur 7 jours</li>
        </ul>
        <div style="margin-top:24px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
          <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:8px;">
            ✦ Ton document est en pièce jointe ✦
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#E3D7FF;">
            Un thé, une bougie, quinze minutes de calme.<br>
            L'Arbre parle à ceux qui l'écoutent lentement.
          </div>
        </div>
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">
            — Solena
          </div>
          <div style="font-size:11px;color:#9089B5;margin-top:4px;">
            Astrologue &amp; guide chez Plume Astrale
          </div>
        </div>
      </div>
      <div style="text-align:center;margin-top:24px;font-size:10px;color:#666;letter-spacing:0.15em;">
        <a href="https://plume-astrale.fr" style="color:#D4AF37;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'from': sender,
                'to': [email],
                'subject': "Ton Arbre de Vie Kabbalistique est prêt ✦",
                'html': html,
                'attachments': [{'filename': filename, 'content': pdf_b64}],
            },
        )
        if r.status_code >= 400:
            logger.warning(f"[kabbale] Resend error {r.status_code}: {r.text[:300]}")
        else:
            logger.info(f"[kabbale] Email sent to {email}")
