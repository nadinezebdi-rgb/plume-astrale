"""
voyage_karmique_service — Fusion Kabbale + Karma Destin (49€).

Orchestrateur post-paiement Nocturne Éditorial (Feb 2026).
Génère les deux PDFs (Kabbale Arbre de Vie + Analyse Karmique) et livre les deux
liens de téléchargement dans un seul email éditorial signé Soléna.

Aucun retraitement — on réutilise les générateurs éprouvés (idempotents).
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio
from services.pdf_luxury_wrap import generate_kabbale_pdf_luxury as generate_kabbale_pdf
from services.karma_destin_pdf import generate_karma_destin_pdf
from services.pdf_download import (
    new_pdf_token, build_signed_pdf_url, upload_pdf_to_reports_bucket,
)

logger = logging.getLogger(__name__)
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


async def handle_voyage_karmique_webhook(session_id: str, force: bool = False) -> dict:
    """Génère les deux PDFs (Kabbale + Karma Destin) et envoie un email fusion."""
    diag = {'session_id': session_id, 'force': force}
    if not session_id:
        diag['error'] = 'no session_id'
        return diag

    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[voyage_karmique] tx fetch failed: {e}')
        diag['error'] = f'tx fetch: {e}'
        return diag
    if not tx_res or not tx_res.data:
        diag['error'] = 'tx not found'
        return diag
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'voyage_karmique':
        diag['error'] = 'kind mismatch'
        return diag

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence — les deux PDFs déjà générés
    already = md.get('kabbale_pdf_path') and md.get('karma_pdf_path')
    if already and not force:
        diag['skipped'] = True
        return diag

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = (pdf_ctx.get('first_name') or 'Ami·e').strip()
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    birth_data = pdf_ctx.get('birth_data') or {}

    if not birth_data:
        diag['error'] = 'no birth_data'
        return diag

    # ─── 1) Générer le PDF Kabbale ───
    kabbale_link_signed = md.get('kabbale_pdf_path')
    kabbale_supabase = md.get('kabbale_supabase_url')
    if not kabbale_link_signed or force:
        try:
            tree_data = await aio.tree_of_life_chart(
                birth_data, system='modern_halevi', tradition='psychological', language='fr'
            )
            try:
                from services.report_ai_enrichment import enrich_report
                ai_sections = await enrich_report(
                    report_type='kabbale',
                    prenom=first_name,
                    birth_date_iso=birth_date_iso,
                    context={'tree_of_life': tree_data},
                )
            except Exception as e:
                logger.warning(f'[voyage_karmique] kabbale enrich fail: {e}')
                ai_sections = None
            pdf_bytes = await asyncio.to_thread(
                generate_kabbale_pdf,
                first_name=first_name,
                birth_date_iso=birth_date_iso,
                tree_of_life=tree_data,
                ai_sections=ai_sections,
            )
            filename = f'voyage_karmique_kabbale_{session_id[-16:]}.pdf'
            out_dir = ASSETS_DIR / 'voyage_karmique'
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, 'wb') as f:
                f.write(pdf_bytes)
            kabbale_token = new_pdf_token()
            md['kabbale_pdf_token'] = kabbale_token
            md['kabbale_pdf_path'] = build_signed_pdf_url(session_id, kabbale_token)
            kabbale_supabase = await asyncio.to_thread(
                upload_pdf_to_reports_bucket, pdf_bytes, session_id, 'voyage_karmique_kabbale', filename,
            )
            if kabbale_supabase:
                md['kabbale_supabase_url'] = kabbale_supabase
            diag['kabbale_bytes'] = len(pdf_bytes)
        except Exception as e:
            logger.error(f'[voyage_karmique] kabbale PDF gen fail: {e}', exc_info=True)
            diag['kabbale_error'] = str(e)[:200]

    # ─── 2) Générer le PDF Karma Destin ───
    karma_link_signed = md.get('karma_pdf_path')
    karma_supabase = md.get('karma_supabase_url')
    if not karma_link_signed or force:
        try:
            # Fetch données karma astro (nœuds, Saturne, Chiron, Pluton)
            karma_data = await aio.natal_chart(birth_data, name=first_name, language='fr')
            pdf_bytes = await asyncio.to_thread(
                generate_karma_destin_pdf,
                first_name=first_name,
                birth_date_iso=birth_date_iso,
                natal_data=karma_data,
            )
            filename = f'voyage_karmique_karma_{session_id[-16:]}.pdf'
            out_dir = ASSETS_DIR / 'voyage_karmique'
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(out_dir / filename, 'wb') as f:
                f.write(pdf_bytes)
            karma_token = new_pdf_token()
            md['karma_pdf_token'] = karma_token
            md['karma_pdf_path'] = build_signed_pdf_url(session_id, karma_token)
            karma_supabase = await asyncio.to_thread(
                upload_pdf_to_reports_bucket, pdf_bytes, session_id, 'voyage_karmique_karma', filename,
            )
            if karma_supabase:
                md['karma_supabase_url'] = karma_supabase
            diag['karma_bytes'] = len(pdf_bytes)
        except Exception as e:
            logger.error(f'[voyage_karmique] karma PDF gen fail: {e}', exc_info=True)
            diag['karma_error'] = str(e)[:200]

    md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
    md['pdf_status'] = 'success' if (md.get('kabbale_pdf_path') and md.get('karma_pdf_path')) else 'partial'
    try:
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[voyage_karmique] md persist fail: {e}')

    # ─── 3) Email fusion (Nocturne Éditorial) ───
    if email and (md.get('kabbale_pdf_path') or md.get('karma_pdf_path')):
        try:
            await _send_voyage_karmique_email(
                email=email, first_name=first_name,
                kabbale_link=md.get('kabbale_supabase_url') or md.get('kabbale_pdf_path'),
                karma_link=md.get('karma_supabase_url') or md.get('karma_pdf_path'),
                session_id=session_id,
            )
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f'[voyage_karmique] email fail: {e}')

    return diag


async def _send_voyage_karmique_email(
    email: str, first_name: str, kabbale_link: Optional[str],
    karma_link: Optional[str], session_id: str,
) -> None:
    """Email Nocturne Éditorial avec les deux liens de téléchargement."""
    from services.email_journal import log_send_attempt, log_send_response
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    subject = f"{first_name}, votre Voyage Karmique est prêt"
    if not api_key:
        logger.warning('[voyage_karmique] RESEND_API_KEY missing')
        return

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='voyage_karmique',
        from_email=sender, session_id=session_id,
    )

    fn = first_name.strip().title()
    kabbale_html = ""
    if kabbale_link:
        kabbale_html = f"""
        <a href="{kabbale_link}"
           style="display:block;padding:20px 24px;background:#141B2E;border:1px solid rgba(184,147,90,0.35);border-radius:2px;text-decoration:none;margin-bottom:12px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.28em;text-transform:uppercase;color:#B8935A;margin-bottom:8px;">Livre I</div>
          <div style="font-family:'Fraunces',Georgia,serif;font-size:22px;color:#F5F0E6;font-weight:400;">Arbre de Vie Kabbalistique</div>
          <div style="font-family:'Inter Tight',sans-serif;font-size:12px;color:#B8935A;margin-top:8px;">Télécharger →</div>
        </a>
        """
    karma_html = ""
    if karma_link:
        karma_html = f"""
        <a href="{karma_link}"
           style="display:block;padding:20px 24px;background:#141B2E;border:1px solid rgba(184,147,90,0.35);border-radius:2px;text-decoration:none;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.28em;text-transform:uppercase;color:#B8935A;margin-bottom:8px;">Livre II</div>
          <div style="font-family:'Fraunces',Georgia,serif;font-size:22px;color:#F5F0E6;font-weight:400;">Lignée Karmique &amp; Destinée</div>
          <div style="font-family:'Inter Tight',sans-serif;font-size:12px;color:#B8935A;margin-top:8px;">Télécharger →</div>
        </a>
        """

    html = f"""
    <div style="max-width:600px;margin:0 auto;background:#0B1A2E;padding:48px 32px;">
      <div style="text-align:center;margin-bottom:32px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:0.32em;text-transform:uppercase;color:#B8935A;">
          Voyage Karmique &middot; Édition Nocturne
        </div>
      </div>
      <div style="background:#141B2E;border:1px solid rgba(184,147,90,0.22);border-radius:4px;padding:44px 32px;">
        <h1 style="font-family:'Fraunces',Georgia,serif;font-weight:400;font-size:34px;color:#F5F0E6;margin:0 0 20px;line-height:1.15;letter-spacing:-0.02em;">
          {fn},<br>
          <em style="color:#B8935A;font-style:italic;font-weight:300;">votre voyage</em><br>
          en deux livres.
        </h1>
        <hr style="border:0;border-top:1px solid #B8935A;width:48px;margin:24px 0;">
        <p style="font-family:'Inter Tight','Inter',sans-serif;color:rgba(245,240,230,0.86);line-height:1.7;font-size:15px;">
          Deux textes composés pour vous seul(e). Votre Arbre de Vie Kabbalistique — dix Sephiroth,
          vingt-deux chemins — et votre Lignée Karmique — Nœuds lunaires, Saturne, Chiron, Pluton.
          Un livre parle de votre <em>essence</em>. L&rsquo;autre, de votre <em>direction</em>.
        </p>
        <div style="margin-top:32px;">
          {kabbale_html}
          {karma_html}
        </div>
        <div style="margin-top:32px;padding:20px;background:#0B1A2E;border-left:2px solid #B8935A;">
          <div style="font-family:'Fraunces',Georgia,serif;font-style:italic;color:rgba(245,240,230,0.82);font-size:16px;line-height:1.55;">
            Prenez le temps. Une lecture, un thé, une soirée.<br>
            Ce voyage ne se parcourt pas — se contemple.
          </div>
        </div>
        <div style="margin-top:40px;padding-top:24px;border-top:1px solid rgba(184,147,90,0.18);text-align:center;">
          <div style="font-family:'Fraunces',Georgia,serif;font-style:italic;color:#F5F0E6;font-size:20px;font-weight:300;">— Soléna</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.28em;color:rgba(184,147,90,0.7);margin-top:8px;text-transform:uppercase;">
            Plume Astrale &middot; 2026
          </div>
        </div>
      </div>
    </div>
    """

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
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
                to_email=email, subject=subject, product='voyage_karmique', session_id=session_id,
            )
            if r.status_code >= 400:
                logger.warning(f'[voyage_karmique] Resend {r.status_code}: {r.text[:200]}')
    except Exception as e:
        logger.warning(f'[voyage_karmique] email exception: {e}')
