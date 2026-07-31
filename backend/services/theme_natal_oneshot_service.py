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


async def handle_theme_natal_oneshot_webhook(session_id: str, force: bool = False) -> dict:
    """Wrapper qui garantit que TOUTE exception non prévue marque
    `metadata.pdf_status = 'failed'` (sinon l'UI reste en spinner infini).
    Le vrai travail est dans `_impl_handle_theme_natal_oneshot`.
    """
    try:
        return await _impl_handle_theme_natal_oneshot(session_id, force)
    except Exception as e:
        logger.exception(f'[theme_natal_oneshot] UNCAUGHT exception for {session_id}: {e}')
        # Best-effort : marque le failure côté base pour que le front sorte du spinner
        try:
            sb = get_admin_client()
            r = sb.table('payment_transactions').select('metadata').eq('session_id', session_id).maybe_single().execute()
            if r and r.data:
                md = r.data.get('metadata') or {}
                md['pdf_status'] = 'failed'
                md['pdf_error'] = f'uncaught: {type(e).__name__}: {str(e)[:300]}'
                md['pdf_failed_at'] = datetime.now(timezone.utc).isoformat()
                sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception:
            pass
        return {'session_id': session_id, 'force': force, 'error': f'uncaught: {e}'}


async def _impl_handle_theme_natal_oneshot(session_id: str, force: bool = False) -> dict:
    """Génère le PDF Thème Natal complet + envoie l'email au client (idempotent).

    Si force=True, régénère même si un PDF a déjà été produit (utile après
    refonte du template pour rafraîchir une session existante).

    Retourne un dict diagnostic (nb pages, mode ultra/legacy, source AI, taille…)
    afin que l'admin regenerate expose les métriques réelles pour debug.
    """
    diag: dict = {'session_id': session_id, 'force': force, 'skipped': False}
    if not session_id:
        diag['error'] = 'session_id vide'
        return diag
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f"[theme_natal_oneshot] tx fetch failed: {e}")
        diag['error'] = f'tx fetch failed: {e}'
        return diag
    if not tx_res or not tx_res.data:
        logger.warning(f"[theme_natal_oneshot] tx not found for {session_id}")
        diag['error'] = 'tx not found'
        return diag
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'theme_natal_pdf_oneshot':
        diag['error'] = 'kind mismatch'
        return diag

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    # Idempotence — sautée si force=True (régénération explicite admin)
    if md.get('pdf_path') and not force:
        logger.info(f"[theme_natal_oneshot] PDF already generated for {session_id}")
        diag['skipped'] = True
        diag['reason'] = 'pdf_path exists (use force=True)'
        return diag
    if force:
        logger.info(f"[theme_natal_oneshot] FORCE regeneration for {session_id}")

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    name = (pdf_ctx.get('first_name') or 'Ami(e)').strip()
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    bd = pdf_ctx.get('birth_data') or {}

    if not bd:
        logger.error(f"[theme_natal_oneshot] no birth_data for {session_id}")
        diag['error'] = 'no birth_data in metadata.pdf_ctx'
        return diag
    diag['birth_data'] = {
        'first_name': name, 'birth_date_iso': birth_date_iso,
        'city': bd.get('city') or bd.get('location'),
        'lat': bd.get('latitude'), 'lon': bd.get('longitude'),
        'tz': bd.get('timezone'),
    }

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
        diag['error'] = f'astrology-api fetch failed: {e}'
        return diag
    diag['planets_from_chart'] = len(planets_dict or {})
    diag['interpretations_count'] = len(interpretations or [])

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
            diag['ai_error'] = str(e)[:200]
    diag['ai_source'] = (ai_result or {}).get('_source', 'none')
    diag['ai_planet_count'] = sum(1 for k in ('soleil','lune','mercure','venus','mars','jupiter','saturne','uranus','neptune','pluton','ascendant') if (ai_result or {}).get(k))
    diag['v3_raw_count'] = len((ai_result or {}).get('_raw_v3_by_planet') or {})
    diag['is_ultra'] = diag['ai_planet_count'] >= 7 or diag['v3_raw_count'] >= 7

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
    #    cairosvg est CPU-bound (blocke le event loop) → on l'exécute dans un thread.
    chart_png_bytes: bytes | None = None
    try:
        svg_str = await aio.chart_svg_render(bd, name=name, theme='dark', language='fr')
        if svg_str:
            from services.svg_utils import resolve_svg_css_vars
            import cairosvg, asyncio as _asyncio
            svg_resolved = resolve_svg_css_vars(svg_str)
            chart_png_bytes = await _asyncio.to_thread(
                cairosvg.svg2png,
                bytestring=svg_resolved.encode('utf-8'),
                output_width=1600,
            )
    except Exception as e:
        logger.warning(f"[theme_natal_oneshot] chart wheel unavailable: {e}")

    # 4.5) Enrichissement narratif LIVRE — front matter, éléments, aspects,
    #      maisons, épilogue. 1 seul appel GPT-5.4 (cache filesystem).
    #      Best-effort : si échec, le PDF sort en version "standard" (20 pages).
    book_data = None
    try:
        from services.natal_book_enrichment import enrich_book_chapters
        # Prépare la data astro pour le prompt (aspects + maisons si dispo dans natal_report_data)
        aspects_for_book = []
        houses_for_book = []
        try:
            if isinstance(natal_report_data, dict):
                aspects_raw = (natal_report_data.get('aspects')
                               or natal_report_data.get('data', {}).get('aspects') or [])
                for a in aspects_raw[:20]:
                    aspects_for_book.append({
                        'planet1': a.get('planet1') or a.get('p1') or a.get('body1'),
                        'planet2': a.get('planet2') or a.get('p2') or a.get('body2'),
                        'type': a.get('type') or a.get('aspect') or a.get('name'),
                        'orb': a.get('orb') or a.get('orb_deg') or a.get('degree'),
                    })
                houses_raw = (natal_report_data.get('houses')
                              or natal_report_data.get('data', {}).get('houses') or [])
                for i, h in enumerate(houses_raw[:12]):
                    houses_for_book.append({
                        'num': h.get('number') or h.get('num') or (i + 1),
                        'sign': aio.sign_to_fr(h.get('sign', '')) if h.get('sign') else '',
                        'planets_in_house': h.get('planets') or h.get('planets_in_house') or [],
                    })
        except Exception:
            pass
        # planets pour analyse éléments/modalités (nécessite noms FR + signes FR)
        planets_book = []
        for _pfr, _en in (('Soleil', 'sun'), ('Lune', 'moon'), ('Mercure', 'mercury'),
                           ('Vénus', 'venus'), ('Mars', 'mars'), ('Jupiter', 'jupiter'),
                           ('Saturne', 'saturn'), ('Uranus', 'uranus'),
                           ('Neptune', 'neptune'), ('Pluton', 'pluto')):
            p = planets_dict.get(_en) or {}
            _sign = aio.sign_to_fr(p.get('sign', '')) if p.get('sign') else ''
            if _sign:
                planets_book.append({'name': _pfr, 'sign': _sign})
        natal_data_for_book = {
            'prenom': name,
            'sun_sign': aio.sign_to_fr((planets_dict.get('sun') or {}).get('sign', '')),
            'moon_sign': aio.sign_to_fr((planets_dict.get('moon') or {}).get('sign', '')),
            'asc_sign': aio.sign_to_fr(asc_sign_en) if asc_sign_en else '',
            'planets': planets_book,
            'aspects': aspects_for_book,
            'houses': houses_for_book,
        }
        book_data = await enrich_book_chapters(
            prenom=name, birth_data=bd, natal_data=natal_data_for_book,
        )
        diag['book_source'] = book_data.get('_source')
        diag['book_element'] = book_data.get('_em', {}).get('dominant_element')
        diag['book_modality'] = book_data.get('_em', {}).get('dominant_modality')
    except Exception as e:
        logger.warning(f"[theme_natal_oneshot] book enrichment failed: {e}")
        diag['book_error'] = str(e)[:200]

    # 4.6) Récupère le code parrainage de l'utilisateur pour le colophon final
    referral_code_book = None
    referral_link_book = None
    try:
        user_id = md.get('user_id') or tx.get('user_id')
        if user_id:
            from services.referral_service import ensure_referral_code
            import os
            referral_code_book = await ensure_referral_code(user_id)
            _base = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
            referral_link_book = f'{_base}/?ref={referral_code_book}'
    except Exception as e:
        logger.info(f'[theme_natal_oneshot] referral code lookup skipped: {e}')

    # 5) Génération PDF luxe — reportlab + kerykeion sont CPU-bound (30-60s).
    #    On délègue à un thread pour ne pas bloquer le event loop (sinon /auth/me
    #    et le polling /inspect timeout → Cloudflare 524).
    pdf_bytes = None
    filename = f'theme_natal_{session_id[-16:]}.pdf'
    try:
        from services.natal_pdf_adapter import generate_manuscrit_pdf
        import asyncio as _asyncio
        pdf_bytes = await _asyncio.to_thread(
            generate_manuscrit_pdf,
            user_data=user_data,
            planets_data=list(planets_dict.values()),
            chart_png_bytes=chart_png_bytes,
            book_data=book_data,
            referral_code=referral_code_book,
            referral_link=referral_link_book,
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
        # Upload Supabase = HTTP sync bloquant → thread pour ne pas geler l'event loop
        import asyncio as _asyncio
        supabase_url = await _asyncio.to_thread(
            upload_pdf_to_reports_bucket,
            pdf_bytes, session_id, 'theme_natal', filename,
            str(int(datetime.now(timezone.utc).timestamp())),
        )
        if supabase_url:
            md['pdf_supabase_url'] = supabase_url
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        md['pdf_status'] = 'success'
        md.pop('pdf_error', None)
        md.pop('pdf_failed_at', None)
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[theme_natal_oneshot] PDF generated (signed): {md['pdf_path']}")
        # Diagnostic : mesure la taille + tente de compter les pages pour le retour
        diag['pdf_bytes'] = len(pdf_bytes)
        diag['pdf_supabase_url'] = md.get('pdf_supabase_url')
        try:
            # Compte des pages via pattern PDF (fiable pour ReportLab)
            diag['pdf_pages'] = pdf_bytes.count(b'/Type /Page') or pdf_bytes.count(b'/Type/Page')
        except Exception:
            diag['pdf_pages'] = None
    except Exception as e:
        logger.error(f"[theme_natal_oneshot] PDF gen failed: {e}", exc_info=True)
        diag['error'] = f'PDF gen failed: {e}'
        # Marque explicitement l'échec côté base pour que l'UI arrête de spinner à l'infini.
        # `status` reste 'completed' (le paiement est bien confirmé), mais `pdf_status: failed`
        # signale au front qu'il faut afficher une erreur et proposer de régénérer.
        try:
            md['pdf_status'] = 'failed'
            md['pdf_error'] = str(e)[:400]
            md['pdf_failed_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception:
            pass
        return diag

    # 6) Email best-effort
    if email and pdf_bytes:
        try:
            # On envoie un LIEN Supabase (persisté, versionné) au lieu d'une pièce jointe.
            # Le PDF fait ~27 Mo — Resend limite à 40 Mo, Gmail à 25 Mo côté destinataire.
            # Le lien évite tout risque de rebond email.
            pdf_link = md.get('pdf_supabase_url') or md.get('pdf_path')
            await _send_theme_natal_email(email, name, pdf_link=pdf_link, session_id=session_id)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[theme_natal_oneshot] email failed: {e}")
    return diag


async def _send_theme_natal_email(email: str, first_name: str, pdf_link: str, session_id: str | None = None) -> None:
    """Envoie l'email de livraison avec un lien de téléchargement (pas de pièce jointe).

    Le PDF est stocké de manière persistante sur Supabase Storage (bucket `reports`),
    avec un chemin versionné par timestamp. Le lien reste valide indéfiniment.
    """
    from services.email_journal import log_send_attempt, log_send_response
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    subject = "Ton Thème Natal Complet est prêt ✦"
    if not api_key:
        logger.warning("[theme_natal_oneshot] RESEND_API_KEY missing")
        return
    if not pdf_link:
        logger.warning("[theme_natal_oneshot] pdf_link missing, email skipped")
        return

    row_id = log_send_attempt(
        to_email=email, subject=subject, product='theme_natal_oneshot',
        from_email=sender, session_id=session_id,
    )
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
          Un document intime de 40 à 50 pages, tracé pour toi seul(e). Il révèle tes 11 planètes,
          ton ascendant, tes maisons, tes aspects — et surtout la façon dont ils composent
          ta signature unique dans le ciel.
        </p>
        <div style="text-align:center;margin:36px 0 10px;">
          <a href="{pdf_link}"
             style="display:inline-block;padding:16px 36px;background:linear-gradient(135deg,#D4AF37 0%,#E8C766 100%);color:#111625;text-decoration:none;border-radius:999px;font-family:'Cinzel',serif;font-size:13px;letter-spacing:0.15em;text-transform:uppercase;font-weight:500;">
            Télécharger mon Thème Natal
          </a>
        </div>
        <div style="text-align:center;margin-top:8px;">
          <div style="font-size:11px;color:rgba(227,215,255,0.55);font-style:italic;">
            Ton document reste accessible à ce lien à tout moment.
          </div>
        </div>
        <div style="margin-top:36px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
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
