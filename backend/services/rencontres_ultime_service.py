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

# ── Synastrie 12 domaines de vie (traduction + redaction FR via GPT) ──
_AREA_FR = {
    'Communication & Understanding': 'Communication & Compréhension',
    'Love & Romance': 'Amour & Romance',
    'Passion & Sexuality': 'Passion & Sexualité',
    'Emotional Security': 'Sécurité émotionnelle',
    'Shared Values & Goals': 'Valeurs & Objectifs partagés',
    'Adventure & Growth': 'Aventure & Croissance',
    'Stability & Commitment': 'Stabilité & Engagement',
    'Creativity & Fun': 'Créativité & Légèreté',
    'Home & Family': 'Foyer & Famille',
    'Independence & Freedom': 'Indépendance & Liberté',
    'Spiritual Connection': 'Connexion spirituelle',
    'Transformation & Healing': 'Transformation & Guérison',
}

_SYN_SYSTEM = (
    "Tu es Solena, astrologue francaise chez Plume Astrale. Tu rediges les passages d'un rapport de "
    "compatibilite premium. Francais poetique mais precis, tutoiement, jamais fataliste. "
    "Aucune salutation, aucun emoji, aucune liste. Un seul paragraphe fluide."
)


async def _gpt_syn(prompt: str, session_id: str) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return ''
    try:
        chat = LlmChat(api_key=api_key, session_id=session_id, system_message=_SYN_SYSTEM).with_model('openai', 'gpt-4o-mini')
        r = await chat.send_message(UserMessage(text=prompt))
        return (r or '').strip()
    except Exception as e:
        logger.warning(f'[rencontres_ultime] gpt syn failed: {e}')
        return ''


async def build_synastry_chapter(user_bd: dict, partner_bd: dict, n1: str, n2: str, session_id: str) -> Optional[dict]:
    """Fetch /analysis/synastry-report + francise les 12 domaines de vie via GPT.
    Retourne {'overall_score', 'dynamic_type', 'harmony', 'tension', 'summary_fr', 'areas': [...]}."""
    import asyncio
    from services import astrology_io_service as aio

    report = await aio.synastry_report(user_bd, partner_bd, name_1=n1, name_2=n2, language='fr')
    if not report:
        return None

    areas = report.get('life_area_compatibility') or []
    dynamics = report.get('dynamics') or {}
    overall = report.get('overall_compatibility_score')

    def _pct(v) -> int:
        try:
            f = float(v)
            return int(round(f * 100)) if f <= 1.0 else int(round(f))
        except Exception:
            return 0

    area_prompts = []
    for a in areas[:12]:
        name_en = a.get('area') or ''
        name_fr = _AREA_FR.get(name_en, name_en)
        score = _pct(a.get('compatibility_score'))
        prompt = (
            f"Domaine de vie : {name_fr}. Couple : {n1} et {n2}. Score de compatibilite : {score}/100. "
            f"Facteurs astrologiques cles : {', '.join(a.get('key_factors') or [])}. "
            f"Analyse originale (en anglais, a franciser et enrichir) : {a.get('description') or ''}. "
            "Redige 80 a 110 mots en francais sur ce domaine pour ce couple : ce qui coule de source, "
            "ce qui demande de l'attention, et une invitation concrete."
        )
        area_prompts.append((name_fr, score, prompt))

    dyn_prompt = (
        f"Couple : {n1} et {n2}. Score global : {_pct(overall)}/100. "
        f"Harmonie : {dynamics.get('harmony_percentage', '?')}% · Tension : {dynamics.get('tension_percentage', '?')}%. "
        f"Type de dynamique : {dynamics.get('dynamic_type') or ''}. "
        f"Forces (EN) : {'; '.join(dynamics.get('key_strengths') or [])}. "
        f"Axes de croissance (EN) : {'; '.join(dynamics.get('growth_areas') or [])}. "
        f"Resume (EN) : {dynamics.get('summary') or ''}. "
        "Redige 120 a 160 mots en francais : le portrait vibratoire de ce lien, ses forces principales "
        "et ses axes de croissance, sans jargon anglais."
    )

    tasks = [_gpt_syn(p, f'ult-{session_id}-a{i}') for i, (_, _, p) in enumerate(area_prompts)]
    tasks.append(_gpt_syn(dyn_prompt, f'ult-{session_id}-dyn'))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    out_areas = []
    for (name_fr, score, _), r in zip(area_prompts, results[:-1]):
        text = r if isinstance(r, str) and r else ''
        out_areas.append({'name_fr': name_fr, 'score': score, 'text_fr': text})

    summary_fr = results[-1] if isinstance(results[-1], str) else ''
    return {
        'overall_score': _pct(overall),
        'dynamic_type': dynamics.get('dynamic_type') or '',
        'harmony': int(round(float(dynamics.get('harmony_percentage') or 0))),
        'tension': int(round(float(dynamics.get('tension_percentage') or 0))),
        'summary_fr': summary_fr,
        'areas': out_areas,
    }


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

    # ── Synastrie 12 domaines (si donnees partenaire + user disponibles) ──
    partner = pdf_ctx.get('partner') or {}
    partner_name = partner.get('first_name') or ''
    user_bd = pdf_ctx.get('user_birth_data') or {}
    synastry = None
    if partner.get('birth_data') and user_bd:
        try:
            synastry = await build_synastry_chapter(
                user_bd, partner['birth_data'],
                first_name or 'Toi', partner_name or 'Ton partenaire',
                session_id[-12:],
            )
            logger.info(f"[rencontres_ultime] synastry chapter ready ({len((synastry or {}).get('areas', []))} domaines)")
        except Exception as e:
            logger.warning(f'[rencontres_ultime] synastry chapter failed: {e}')

    # Generation PDF best-effort
    pdf_path = None
    try:
        pdf_bytes = generate_rencontres_ultime_pdf(
            birth_date_iso=birth_date_iso,
            first_name=first_name,
            m7_sign=m7_sign,
            venus_sign=venus_sign,
            mars_sign=mars_sign,
            partner_name=partner_name,
            synastry=synastry,
        )
        out_dir = ASSETS_DIR / 'rencontres_ultime'
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f'ultime_{session_id[-16:]}.pdf'
        out_path = out_dir / filename
        with open(out_path, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/rencontres_ultime/{filename}'

        # SEC-003 : token opaque + URL signée
        from services.pdf_download import new_pdf_token, build_signed_pdf_url, upload_pdf_to_reports_bucket
        pdf_token = new_pdf_token()
        md['pdf_token'] = pdf_token
        md['pdf_path'] = build_signed_pdf_url(session_id, pdf_token)
        md['pdf_static_path_legacy'] = pdf_path
        supabase_url = upload_pdf_to_reports_bucket(pdf_bytes, session_id, 'rencontres_ultime', filename)
        if supabase_url:
            md['pdf_supabase_url'] = supabase_url
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f"[rencontres_ultime] PDF generated (signed): {md['pdf_path']}")
    except Exception as e:
        logger.error(f"[rencontres_ultime] PDF gen failed for {session_id}: {e}", exc_info=True)
        return

    # Envoi email best-effort
    if email and pdf_path:
        try:
            await _send_ultime_email(email, first_name, pdf_bytes, filename, pdf_url=md.get('pdf_supabase_url', ''))
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f"[rencontres_ultime] email send failed for {session_id}: {e}")


async def _send_ultime_email(email: str, first_name: str, pdf_bytes: bytes, filename: str, pdf_url: str = '') -> None:
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

    pdf_url = pdf_url or ''
    if pdf_url:
        _btn = f'<div style="text-align:center;margin:24px 0;"><a href="{pdf_url}" style="display:inline-block;background:#D4AF37;color:#111625;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none;font-family:Arial,sans-serif;">Télécharger ton document →</a></div>'
        _i = html.rfind('</div>')
        html = (html[:_i] + _btn + html[_i:]) if _i != -1 else (html + _btn)

    MAX_ATTACH = 30 * 1024 * 1024  # marge sous la limite Resend (40 Mo)
    payload = {'from': sender, 'to': [email], 'subject': 'Ton Guide de Compatibilité Ultime est prêt ✦', 'html': html}
    if pdf_bytes and len(pdf_bytes) <= MAX_ATTACH:
        payload['attachments'] = [{'filename': filename, 'content': pdf_b64}]

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            'https://api.resend.com/emails',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json=payload,
        )
        if r.status_code >= 400:
            logger.warning(f"[rencontres_ultime] Resend error {r.status_code}: {r.text[:300]}")
        else:
            logger.info(f"[rencontres_ultime] Email sent to {email}")
