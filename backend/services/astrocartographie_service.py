"""
Orchestrateur post-paiement pour le pack "astrocartographie" (49 EUR).
Fetch /astrocartography/map + /location-analysis (×3) + génère bonus IA + PDF + email.
"""
from __future__ import annotations
import asyncio
import base64
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import httpx

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio
from services import astrocartographie_ai as aiai
from services.pdf_luxury_wrap import generate_astrocartographie_pdf_luxury as generate_astrocartographie_pdf

logger = logging.getLogger(__name__)
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


async def handle_astrocartographie_webhook(session_id: str) -> None:
    """Génère le PDF astrocartographie + envoi email (idempotent, best-effort)."""
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[astrocarto] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        logger.warning(f"[astrocarto] tx not found for {session_id}")
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'astrocartographie':
        return

    # Marquer paiement complété
    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed', 'payment_status': 'paid', 'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence
    if md.get('pdf_path'):
        logger.info(f"[astrocarto] PDF already exists for {session_id}")
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Ami(e)'
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    birth_data = pdf_ctx.get('birth_data') or {}
    chosen_locations: List[Dict[str, Any]] = pdf_ctx.get('chosen_locations') or []

    if not birth_data or len(chosen_locations) < 1:
        logger.error(f"[astrocarto] missing birth_data or locations for {session_id}")
        return

    # 1) Fetch carte SVG mondiale + données lignes brutes
    map_svg = None
    lines_data = []
    try:
        r = await aio.astrocartography(birth_data, name=first_name, language='fr')
        if r:
            map_svg = r.get('svg_content') or r.get('svg') or ''
            # v3 renvoie parfois les lignes directement dans /map (sinon on refetch)
            lines_data = r.get('lines') or []
    except Exception as e:
        logger.warning(f"[astrocarto] map fetch failed: {e}")
    if not lines_data:
        try:
            r2 = await aio.astrocartography_lines(birth_data, name=first_name, language='fr')
            if r2:
                lines_data = r2.get('lines') or []
        except Exception as e:
            logger.warning(f"[astrocarto] lines fetch failed: {e}")

    # 2) Fetch analysis pour chaque ville choisie + enrichissement IA
    chosen_analyses: List[Dict[str, Any]] = []
    for loc in chosen_locations[:3]:
        raw = None
        try:
            raw = await aio.astrocartography_location_analysis(
                birth_data, location=loc, name=first_name, language='fr')
        except Exception as e:
            logger.warning(f"[astrocarto] location-analysis failed for {loc.get('city')}: {e}")
        raw = raw or {}
        summary = raw.get('summary') or ''
        life_areas = raw.get('life_area_ratings') or {}
        planetary = (raw.get('detailed_analysis') or {}).get('planetary_influences') or {}
        nearby = raw.get('nearby_lines') or []
        # Enrichir en FR
        enriched = await aiai.enrich_city_analysis(
            city=loc.get('city', ''),
            country=loc.get('country', loc.get('country_code', '')),
            raw_summary=summary,
            life_area_ratings=life_areas,
            planetary_influences=planetary,
            first_name=first_name,
        )
        chosen_analyses.append({
            'city': loc.get('city'),
            'country': loc.get('country', loc.get('country_code', '')),
            'country_code': loc.get('country_code', ''),
            'raw': raw,
            'enriched': enriched,
            'nearby_lines': nearby,
        })

    # 3) Générer 2 villes bonus par Soléna
    natal_summary = f"Naissance le {birth_date_iso} à {birth_data.get('city', '?')}, {birth_data.get('country_code', '?')}."
    bonus_raw = await aiai.generate_bonus_destinations(
        first_name=first_name,
        natal_summary=natal_summary,
        already_chosen_cities=[l.get('city', '') for l in chosen_locations],
    )
    bonus_analyses = []
    for b in bonus_raw[:2]:
        # b vient de l'IA — pas d'API call, juste réutiliser le contenu comme "enriched"
        enriched = {
            'headline': b.get('promise', ''),
            'ambiance': b.get('why', ''),
            'career': b.get('why', ''),
            'love': b.get('why', ''),
            'spirituality': b.get('why', ''),
            'body': b.get('why', ''),
            'advice': b.get('promise', ''),
            'why': b.get('why', ''),
            'promise': b.get('promise', ''),
        }
        # Enrichir plus finement en réappelant l'IA
        try:
            deep = await aiai.enrich_city_analysis(
                city=b.get('city', ''), country=b.get('country', ''),
                raw_summary=b.get('why', ''),
                life_area_ratings={}, planetary_influences={},
                first_name=first_name,
            )
            enriched.update(deep)
            # Réinjecter why/promise
            enriched['why'] = b.get('why', '')
            enriched['promise'] = b.get('promise', '')
        except Exception:
            pass
        bonus_analyses.append({
            'city': b.get('city'), 'country': b.get('country'),
            'country_code': b.get('country_code'),
            'enriched': enriched,
            'nearby_lines': [],
        })

    # 4) Synthèse Soléna
    synth = await aiai.write_synthesis(
        first_name=first_name,
        cities_analyses=chosen_analyses + bonus_analyses,
    )

    # 5) Générer PDF
    pdf_bytes = None
    filename = f'astrocarto_{session_id[-16:]}.pdf'
    try:
        pdf_bytes = generate_astrocartographie_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            map_svg=map_svg,
            chosen_cities=chosen_analyses,
            bonus_cities=bonus_analyses,
            synthesis_text=synth,
            lines_data=lines_data,
        )
        out_dir = ASSETS_DIR / 'astrocartographie'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/astrocartographie/{filename}'
        # SEC-003 : token opaque + URL signée pour le download
        from services.pdf_download import new_pdf_token, build_signed_pdf_url
        pdf_token = new_pdf_token()
        md['pdf_token'] = pdf_token
        md['pdf_path'] = build_signed_pdf_url(session_id, pdf_token)
        md['pdf_static_path_legacy'] = pdf_path
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[astrocarto] PDF generated (signed): {md['pdf_path']}")
    except Exception as e:
        logger.error(f"[astrocarto] PDF gen failed for {session_id}: {e}", exc_info=True)
        return

    # 6) Envoi email
    if email and pdf_bytes:
        try:
            await _send_astrocarto_email(email, first_name, pdf_bytes, filename, session_id=session_id)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[astrocarto] email failed for {session_id}: {e}")


async def _send_astrocarto_email(email: str, first_name: str, pdf_bytes: bytes, filename: str, session_id: str | None = None) -> None:
    from services.email_journal import log_send_attempt, log_send_response

    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    subject = "Ton Astrocartographie est prête ✦"
    if not api_key:
        log_send_response(None, http_status=0, body='RESEND_API_KEY missing',
                          to_email=email, subject=subject, product='astrocartographie', session_id=session_id)
        return

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='astrocartographie',
        from_email=sender, session_id=session_id,
    )

    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    fn = (first_name or 'ami(e)').strip()

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;">
          ✦ Plume Astrale · Astrocartographie ✦
        </div>
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#F5EEE0;margin:0 0 14px;line-height:1.25;">
          {fn.title()},<br>
          <em style="color:#D4AF37;font-style:italic;">ta carte du monde</em><br>
          est prête.
        </h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Un document intime de 18 pages, tracé pour toi seule. Il révèle la géographie de ton ciel projetée sur la Terre —
          les villes que tu as choisies et deux destinations bonus que j'ai sélectionnées selon ton thème.
        </p>
        <ul style="color:#E3D7FF;line-height:1.9;font-size:14px;padding-left:20px;">
          <li>Ta <strong>carte du monde</strong> avec toutes tes lignes planétaires</li>
          <li>Analyse détaillée de <strong>tes 3 villes choisies</strong> (carrière, amour, spiritualité, corps)</li>
          <li><strong>2 destinations bonus</strong> que Soléna te dédie personnellement</li>
          <li>Une <strong>synthèse</strong> pour t'aider à choisir + un rituel d'ancrage</li>
        </ul>
        <div style="margin-top:24px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
          <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:8px;">
            ✦ Ton document est en pièce jointe ✦
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#E3D7FF;">
            Une tasse de thé, une carte du monde ouverte à côté.<br>
            La géographie de ton âme t'attend.
          </div>
        </div>
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">
            — Soléna
          </div>
          <div style="font-size:11px;color:#9089B5;margin-top:4px;">Astrologue &amp; guide chez Plume Astrale</div>
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
                'from': sender, 'to': [email], 'subject': subject, 'html': html,
                'attachments': [{'filename': filename, 'content': pdf_b64}],
            },
        )
        resend_id = None
        try:
            resend_id = r.json().get('id') if r.status_code < 300 else None
        except Exception:
            pass
        log_send_response(
            row_id, http_status=r.status_code, resend_id=resend_id,
            body=None if r.status_code < 300 else r.text,
            to_email=email, subject=subject, product='astrocartographie', session_id=session_id,
        )
        if r.status_code >= 400:
            logger.warning(f"[astrocarto] Resend error {r.status_code}: {r.text[:300]}")
        else:
            logger.info(f"[astrocarto] Email sent to {email}")
