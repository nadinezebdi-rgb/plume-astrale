"""
Orchestrateur post-paiement pour le pack "theme_natal_pdf_oneshot" (24 EUR).
Fetch les données natales v3 + enrichit avec GPT-5.4 + génère le PDF luxe + envoie l'email.

Mirror du pattern services/kabbale_service.py.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import httpx

from services.supabase_client import get_admin_client
from services import astrology_io_service as aio

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'


def _resolve_edition(md: dict):
    """Édition demandée dans les métadonnées de la transaction (numérique par défaut)."""
    from services.book_engine_shared.domain import Edition
    try:
        return Edition(md.get('edition') or 'numerique')
    except ValueError:
        return Edition.NUMERIQUE


# ── Alerte admin quand astrology-api.io retourne <5 planètes core ──
# Réutilise le pattern de astrology_io_service._alert_invalid_key (Resend, 1 alerte / 6h)
_last_empty_planets_alert_ts = 0.0


async def _alert_empty_planets(
    session_id: str, user_email: str, first_name: str, err_msg: str,
    planets_count: int, core_missing: list,
) -> None:
    """Envoie une alerte email admin quand un PDF Thème Natal échoue
    faute de planètes retournées par astrology-api.io.

    Rate-limitée à 1 alerte toutes les 6h pour éviter le spam.
    """
    global _last_empty_planets_alert_ts
    now = datetime.now(timezone.utc).timestamp()
    if now - _last_empty_planets_alert_ts < 6 * 3600:
        logger.info(f'[theme_natal_oneshot] alerte empty_planets skipped (rate-limited) session={session_id}')
        return
    _last_empty_planets_alert_ts = now
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    to = os.environ.get('ADMIN_ALERT_EMAIL', '').strip()
    if not resend_key or not to:
        logger.warning(
            f'[theme_natal_oneshot] astrology-api.io a retourné <5 planètes '
            f'MAIS RESEND_API_KEY/ADMIN_ALERT_EMAIL manquant — alerte non envoyée. '
            f'session={session_id} count={planets_count} missing={core_missing}'
        )
        return
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {resend_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'from': os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>'),
                    'to': [to],
                    'subject': '🚨 ALERTE Plume Astrale — Thème Natal échoué (planètes vides)',
                    'html': (
                        "<div style='font-family:sans-serif;max-width:600px;margin:0 auto;'>"
                        "<h2 style='color:#B91C1C;'>🚨 PDF Thème Natal refusé (planètes manquantes)</h2>"
                        "<p>Le webhook <code>theme_natal_pdf_oneshot</code> a détecté un retour "
                        f"d'API incomplet (<b>{planets_count} planètes</b> seulement, core manquantes : "
                        f"<code>{core_missing}</code>).</p>"
                        f"<p><b>Session :</b> <code>{session_id}</code><br>"
                        f"<b>Client :</b> {first_name} &lt;{user_email}&gt;<br>"
                        f"<b>Détail :</b> {err_msg}</p>"
                        "<p><b>Action :</b><br>"
                        "1. Vérifier <a href='https://dashboard.astrology-api.io'>dashboard.astrology-api.io</a> "
                        "(crédits épuisés ? 401 ? plan expiré ?)<br>"
                        "2. Une fois le service rétabli, forcer la régénération : "
                        f"<code>POST /api/admin/regenerate-theme-natal/{session_id}?force=true</code></p>"
                        "<p style='color:#888;font-size:12px;'>Anti-spam : maximum 1 alerte toutes les 6 heures. "
                        "Le client voit un statut 'failed' — l'UI sort du spinner.</p>"
                        "</div>"
                    ),
                },
            )
            if r.status_code < 400:
                logger.info(f'[theme_natal_oneshot] alerte empty_planets envoyée à {to} session={session_id}')
            else:
                logger.error(f'[theme_natal_oneshot] alert email error {r.status_code}: {r.text[:200]}')
    except Exception as e:
        logger.error(f'[theme_natal_oneshot] alert email failed: {e}')


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
    # §V audit marque : heure absente = édition sans ascendant / sans maisons
    no_birth_time = bool(pdf_ctx.get('no_birth_time'))
    diag['no_birth_time'] = no_birth_time

    if not bd:
        logger.error(f"[theme_natal_oneshot] no birth_data for {session_id}")
        diag['error'] = 'no birth_data in metadata.pdf_ctx'
        return diag
    # Normalise le birth_data avant tout appel API (bug Nadine Feb 2026 :
    # country_code arrivait en "France" au lieu de "FR" → HTTP 422 silencieux).
    bd = aio.normalize_birth_data(bd)
    diag['birth_data'] = {
        'first_name': name, 'birth_date_iso': birth_date_iso,
        'city': bd.get('city') or bd.get('location'),
        'lat': bd.get('latitude'), 'lon': bd.get('longitude'),
        'tz': bd.get('timezone'),
    }

    # 1-5) Pipeline unifié : fetch astro + enrichissement AI + livre + PDF digital + Lulu
    # Référentiel partagé avec /api/astrology/v3/natal/pdf et /api/reports/theme-natal/pdf.
    # Le service renvoie à la fois le PDF digital et l'intérieur Lulu A5+bleed en une passe.
    try:
        user_id = md.get('user_id') or tx.get('user_id')
        referral_code_book = None
        referral_link_book = None
        if user_id:
            try:
                from services.referral_service import ensure_referral_code
                referral_code_book = await ensure_referral_code(user_id)
                _base = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
                referral_link_book = f'{_base}/?ref={referral_code_book}'
            except Exception as e:
                logger.info(f'[theme_natal_oneshot] referral code lookup skipped: {e}')

        from services.natal_book_service import (
            generate_enriched_natal_pdf, IncompleteNatalDataError,
        )
        try:
            book_result = await generate_enriched_natal_pdf(
                name=name,
                birth_data=bd,
                no_birth_time=no_birth_time,
                require_complete=True,
                output='print',
                force_refresh=force,
                referral_code=referral_code_book,
                referral_link=referral_link_book,
                birth_date_iso=birth_date_iso,
            )
        except IncompleteNatalDataError as e:
            err_msg = str(e)
            logger.error(f'[theme_natal_oneshot] {err_msg} session={session_id}')
            diag['error'] = err_msg
            diag['planets_core_ok'] = 5 - len(e.core_missing)
            diag['planets_core_missing'] = e.core_missing
            md['pdf_status'] = 'failed'
            md['pdf_error'] = err_msg[:400]
            md['pdf_failed_at'] = datetime.now(timezone.utc).isoformat()
            try:
                sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
            except Exception as _e:
                logger.warning(f'[theme_natal_oneshot] failed to persist pdf_status: {_e}')
            try:
                await _alert_empty_planets(
                    session_id, email or '', name, err_msg,
                    planets_count=e.planets_count, core_missing=e.core_missing,
                )
            except Exception as _e:
                logger.warning(f'[theme_natal_oneshot] admin alert failed: {_e}')
            return diag

        pdf_bytes = book_result['pdf_bytes']
        interior = book_result.get('interior_bytes')
        diag.update(book_result.get('diag') or {})

        # Persist digital PDF — SEC-003 (2026-02) : plus d'écriture disque locale.
        # Les PDFs vivent exclusivement dans Supabase Storage (bucket `reports`)
        # et sont téléchargés via /api/pdf/download?token=... (token opaque).
        # L'ancien chemin /api/assets/theme_natal/*.pdf n'est plus monté.
        filename = f'theme_natal_{session_id[-16:]}.pdf'
        from services.pdf_download import (
            new_pdf_token, build_signed_pdf_url, upload_pdf_to_reports_bucket,
        )
        import asyncio as _asyncio
        pdf_token = new_pdf_token()
        md['pdf_token'] = pdf_token
        md['pdf_path'] = build_signed_pdf_url(session_id, pdf_token)
        supabase_url = await _asyncio.to_thread(
            upload_pdf_to_reports_bucket,
            pdf_bytes, session_id, 'theme_natal', filename,
            str(int(datetime.now(timezone.utc).timestamp())),
        )
        md.pop('pdf_supabase_url', None)
        md.pop('pdf_static_path_legacy', None)
        md.pop('pdf_upload_warning', None)
        if supabase_url:
            md['pdf_supabase_url'] = supabase_url
        else:
            # Pas de fallback disque : SEC-003 a retiré le mount statique.
            # Le client peut re-déclencher la génération via sa session.
            logger.error(
                f'[theme_natal_oneshot] Supabase upload FAILED for {session_id} — '
                f'aucun fallback disque disponible, le client devra retenter.'
            )
            md['pdf_upload_warning'] = 'supabase_upload_failed_no_fallback'

        # Persist Lulu interior (A5 + 3.175mm bleed, prêt impression)
        from services.print_book_renderer import DESIGN_VERSION
        from pypdf import PdfReader
        import io
        md['pdf_design_version'] = DESIGN_VERSION
        md.pop('pdf_lulu_interior_url', None)
        md.pop('pdf_lulu_page_count', None)
        try:
            if interior is None:
                raise RuntimeError('Intérieur Lulu non produit par le service unifié')
            md['pdf_lulu_page_count'] = len(PdfReader(io.BytesIO(interior)).pages)
            interior_url = await _asyncio.to_thread(
                upload_pdf_to_reports_bucket, interior, session_id,
                'theme_natal_lulu', filename, str(int(datetime.now(timezone.utc).timestamp())),
            )
            if not interior_url:
                raise RuntimeError('Stockage intérieur Lulu indisponible')
            md['pdf_lulu_interior_url'] = interior_url
            md['pdf_lulu_status'] = 'ready_for_validation'
            md.pop('pdf_lulu_error', None)
        except Exception as exc:
            md['pdf_lulu_status'] = 'failed'
            md['pdf_lulu_error'] = str(exc)
            logger.exception('[theme_natal_oneshot] Lulu export failed')

        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        md['pdf_status'] = 'success'
        md.pop('pdf_error', None)
        md.pop('pdf_failed_at', None)
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[theme_natal_oneshot] PDF generated (signed): {md['pdf_path']}")
        diag['pdf_bytes'] = len(pdf_bytes)
        diag['pdf_supabase_url'] = md.get('pdf_supabase_url')
    except Exception as e:
        logger.error(f"[theme_natal_oneshot] PDF gen failed: {e}", exc_info=True)
        diag['error'] = f'PDF gen failed: {e}'
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
    # 2026-02-27 : expéditeur spécifique au Thème Natal (sans "Solena"). Les autres
    # produits conservent SENDER_EMAIL de l'env (voix Soléna). Ici on force la marque.
    _env_sender = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact@plume-astrale.fr>')
    # Si l'env contient "Solena/Soléna", on le neutralise pour cet email natal.
    import re as _re
    if _re.search(r'sol[eé]na', _env_sender, flags=_re.IGNORECASE):
        sender = 'Plume Astrale <contact@plume-astrale.fr>'
    else:
        sender = _env_sender
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
    # SEC-005 hardening : échappe strictement les champs utilisateur dans le HTML
    # (prevent stored XSS via first_name manipulé par le client).
    import html as _html
    from urllib.parse import quote as _url_quote
    fn_raw = (first_name or 'ami(e)').strip().title()
    fn = _html.escape(fn_raw)

    # URL de bump "livre relié" — pointe vers la page frontend qui pré-remplit
    # le prénom + session source. Variable d'environnement optionnelle
    # pour l'origin (frontend public), défaut sur l'app.
    _origin = os.environ.get('PUBLIC_ORIGIN', 'https://plume-astrale.fr').rstrip('/')
    # URL-encode le prénom pour la query string (sécurité + encodage correct).
    bump_url = f"{_origin}/natal-print?token={_url_quote(session_id or '', safe='')}&prenom={_url_quote(fn_raw, safe='')}"

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
        <!-- Bump : livre relié 79€ -->
        <div style="margin-top:36px;padding:24px 20px;background:linear-gradient(135deg,#F0E6D2 0%,#E8DBC0 100%);border:1px solid rgba(168,130,63,0.35);border-radius:14px;color:#1C1B26;">
          <div style="font-size:10px;letter-spacing:0.32em;text-transform:uppercase;color:#A8823F;margin-bottom:10px;font-family:'Cinzel',serif;">
            Une option, pour que ton livre dure
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:21px;line-height:1.3;color:#1C1B26;margin-bottom:10px;">
            Reçois <em style="color:#A8823F;">l'exemplaire relié hardcover A5</em> à poser sur ton étagère.
          </div>
          <div style="font-size:14px;line-height:1.55;color:#3A3022;margin-bottom:16px;">
            Impression haute qualité, couverture rigide crème, livraison à domicile.
            Un objet qui traverse les années — à relire aux grandes étapes de ta vie.
          </div>
          <div style="text-align:center;">
            <a href="{bump_url}"
               style="display:inline-block;padding:12px 28px;background:#1C1B26;color:#F0E6D2;text-decoration:none;border-radius:999px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;font-weight:500;">
              Ajouter l'exemplaire relié — 79 €
            </a>
          </div>
          <div style="font-size:10px;color:#8B7355;text-align:center;margin-top:10px;font-style:italic;">
            Prix France ; livraison + impression incluses · Autres destinations devisées en direct.
          </div>
        </div>
        <div style="margin-top:36px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#E3D7FF;">
            Prends le temps. Une lecture par jour, sur une semaine.<br>
            Ce que tu es ne se lit pas — se contemple.
          </div>
        </div>
        <div style="margin-top:32px;padding-top:20px;border-top:1px solid rgba(212,175,55,0.15);text-align:center;">
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#F5EEE0;font-size:20px;">— Plume Astrale</div>
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
