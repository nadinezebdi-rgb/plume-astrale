"""
Orchestrateur post-paiement pour le pack "theme_natal_pdf_oneshot" (29 EUR).
Fetch les données natales v3 + enrichit avec GPT-5.4 + génère le PDF luxe + envoie l'email.

Mirror du pattern services/kabbale_service.py.
"""
from __future__ import annotations
import base64
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


async def handle_theme_natal_oneshot_webhook(session_id: str, force: bool = False) -> None:
    """Génère le PDF Thème Natal complet + envoie l'email au client (idempotent).

    Si force=True, régénère même si un PDF a déjà été produit (utile après
    refonte du template pour rafraîchir une session existante).
    """
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[theme_natal_oneshot] tx fetch failed: {e}")
        return
    if not tx_res or not tx_res.data:
        logger.warning(f"[theme_natal_oneshot] tx not found for {session_id}")
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        return

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence — sautée si force=True (régénération explicite admin)
    if md.get('pdf_path') and not force:
        logger.info(f"[theme_natal_oneshot] PDF already generated for {session_id}")
        return
    if force:
        logger.info(f"[theme_natal_oneshot] FORCE regeneration for {session_id}")

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    name = (pdf_ctx.get('first_name') or 'Ami(e)').strip()
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    bd = pdf_ctx.get('birth_data') or {}

    if not bd:
        logger.error(f"[theme_natal_oneshot] no birth_data for {session_id}")
        return

    # 1) Fetch natal_chart + natal_report (astrology-api.io v3)
    try:
        chart = await aio.natal_chart(bd, name=name, language='fr')
        planets_dict = aio.extract_planets(chart)
        asc_sign_en = aio.extract_ascendant_sign_en(chart)
        natal_report_data = await aio.natal_report(bd, name=name, language='fr')
        interpretations = []
        if isinstance(natal_report_data, dict):
            interpretations = (
                natal_report_data.get('interpretations')
                or natal_report_data.get('data', {}).get('interpretations')
                or []
            )
    except Exception as e:
        logger.error(f"[theme_natal_oneshot] astrology fetch failed: {e}", exc_info=True)
        return

    # 2) Enrichissement GPT-5.4 Ultra (11 planètes + synthèse aspects)
    ai_result: dict = {}
    if interpretations:
        try:
            from services.natal_ai_enrichment import enrich_natal_ultra
            ai_result = await enrich_natal_ultra(
                prenom=name, birth_data=bd,
                api_interpretations=interpretations, tier='ultra',
            )
        except Exception as e:
            logger.warning(f"[theme_natal_oneshot] AI enrichment failed: {e}")

    # 3) Adapter au format du générateur luxe
    def _sign_fr(planet_key: str) -> str:
        p = planets_dict.get(planet_key)
        return aio.sign_to_fr(p.get('sign') or '') if p else ''

    user_data = {
        'prenom': name,
        'birth_date': birth_date_iso,
        'sun_sign': _sign_fr('sun'),
        'moon_sign': _sign_fr('moon'),
        'venus_sign': _sign_fr('venus'),
        'mars_sign': _sign_fr('mars'),
        'ascendant_sign': aio.sign_to_fr(asc_sign_en) if asc_sign_en else '',
        'ai_interpretations': ai_result,
    }

    # 4) Chart wheel SVG → PNG (utilise le cache — 0 crédit API si déjà présent)
    chart_png_bytes: bytes | None = None
    try:
        svg_str = await aio.chart_svg_render(bd, name=name, theme='dark', language='fr')
        if svg_str:
            from services.svg_utils import resolve_svg_css_vars
            import cairosvg
            svg_resolved = resolve_svg_css_vars(svg_str)
            chart_png_bytes = cairosvg.svg2png(
                bytestring=svg_resolved.encode('utf-8'), output_width=1600,
            )
    except Exception as e:
        logger.warning(f"[theme_natal_oneshot] chart wheel unavailable: {e}")

    # 5) Génération PDF luxe
    pdf_bytes = None
    filename = f'theme_natal_{session_id[-16:]}.pdf'
    try:
        from services.natal_pdf_adapter import generate_manuscrit_pdf
        pdf_bytes = generate_manuscrit_pdf(
            user_data=user_data,
            planets_data=list(planets_dict.values()),
            chart_png_bytes=chart_png_bytes,
        )
        out_dir = ASSETS_DIR / 'theme_natal'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        # URL signée (SEC-003)
        from services.pdf_download import new_pdf_token, build_signed_pdf_url, upload_pdf_to_reports_bucket
        pdf_token = new_pdf_token()
        md['pdf_token'] = pdf_token
        md['pdf_path'] = build_signed_pdf_url(session_id, pdf_token)
        md['pdf_static_path_legacy'] = f'/api/assets/theme_natal/{filename}'
        supabase_url = upload_pdf_to_reports_bucket(pdf_bytes, session_id, 'theme_natal', filename, version=str(int(datetime.now(timezone.utc).timestamp())))
        if supabase_url:
            md['pdf_supabase_url'] = supabase_url
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[theme_natal_oneshot] PDF generated (signed): {md['pdf_path']}")
    except Exception as e:
        logger.error(f"[theme_natal_oneshot] PDF gen failed: {e}", exc_info=True)
        return

    # 6) Email best-effort
    if email and pdf_bytes:
        try:
            await _send_theme_natal_email(email, name, pdf_bytes, filename, session_id=session_id)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[theme_natal_oneshot] email failed: {e}")


async def _send_theme_natal_email(email: str, first_name: str, pdf_bytes: bytes, filename: str, session_id: str | None = None) -> None:
    from services.email_journal import log_send_attempt, log_send_response
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    subject = "Ton Thème Natal Complet est prêt ✦"
    if not api_key:
        logger.warning("[theme_natal_oneshot] RESEND_API_KEY missing")
        return

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='theme_natal_oneshot',
        from_email=sender, session_id=session_id,
    )
    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    fn = (first_name or 'ami(e)').strip().title()

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;">
          ✦ Plume Astrale · Thème Natal ✦
        </div>
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#F5EEE0;margin:0 0 14px;line-height:1.25;">
          {fn},<br><em style="color:#D4AF37;font-style:italic;">ton portrait céleste</em><br>t'attend.
        </h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Un document intime de 20 à 40 pages, tracé pour toi seul(e). Il révèle tes 11 planètes,
          ton ascendant, tes maisons, tes aspects — et surtout la façon dont ils composent
          ta signature unique dans le ciel.
        </p>
        <div style="margin-top:24px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
          <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:8px;">
            ✦ Ton document est en pièce jointe ✦
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#E3D7FF;">
            Prends le temps. Une lecture par jour, sur une semaine.<br>
            Ce que tu es ne se lit pas — se contemple.
          </div>
        </div>
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">— Solena</div>
        </div>
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
            to_email=email, subject=subject, product='theme_natal_oneshot', session_id=session_id,
        )
        if r.status_code >= 400:
            logger.warning(f"[theme_natal_oneshot] Resend error {r.status_code}: {r.text[:300]}")
