"""
Orchestrateur post-paiement pour le pack "pack_karmique_kabbale" (89 EUR).
Fetch /analysis/karmic + /kabbalah/tree-of-life-chart, synthese GPT-4o-mini,
genere le PDF ~40 pages + envoie l'email via Resend.
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
from services.pack_karmique_pdf import generate_pack_karmique_pdf

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'

_SYNTH_SYSTEM = (
    "Tu es Solena, astrologue et kabbaliste francaise chez Plume Astrale. Tu rediges les pages de "
    "synthese d'un document premium (89 EUR) qui croise l'analyse karmique et l'Arbre de Vie kabbalistique "
    "d'une meme personne. Exigences : francais soutenu, poetique mais precis, jamais fataliste. "
    "Entre 280 et 400 mots. Cite explicitement les donnees fournies (Noeud Nord, Sephirah dominante, etc.). "
    "Aucune salutation, aucun emoji, aucune liste a puces. Deux ou trois paragraphes fluides, "
    "separes par une ligne vide. Termine par une image evocatrice."
)


async def _gpt(prompt: str, session_id: str) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        return ''
    try:
        chat = LlmChat(api_key=api_key, session_id=session_id, system_message=_SYNTH_SYSTEM).with_model('openai', 'gpt-4o-mini')
        r = await chat.send_message(UserMessage(text=prompt))
        return (r or '').strip()
    except Exception as e:
        logger.warning(f'[pack_karmique] gpt failed: {e}')
        return ''


def _karmic_highlights(karmic: dict) -> str:
    """Extrait les sections-cles du rapport karmique pour les prompts GPT."""
    interps = (karmic or {}).get('interpretations') or []
    keys = ('Nœud Nord', 'Nœud Sud', 'Noeud Nord', 'Noeud Sud', 'Saturne', 'Chiron', 'Pluton', 'Lilith')
    lines = []
    seen = set()
    for it in interps:
        title = (it.get('title') or '').strip()
        if title in seen:
            continue
        if any(title.startswith(k) for k in keys):
            seen.add(title)
            lines.append(f"- {title} : {(it.get('text') or '')[:350]}")
        if len(lines) >= 10:
            break
    return '\n'.join(lines) or 'donnees karmiques non disponibles'


def _tree_highlights(tree: dict) -> str:
    t = (tree or {}).get('data', tree) or {}
    parts = []
    if t.get('dominant_sephirah'):
        parts.append(f"Sephirah dominante : {t['dominant_sephirah']}")
    if t.get('spiritual_focus'):
        parts.append(f"Focus spirituel : {t['spiritual_focus']}")
    pb = t.get('pillar_balance') or {}
    if pb:
        parts.append(
            f"Equilibre des piliers : Rigueur={pb.get('severity_count', '?')}, "
            f"Misericorde={pb.get('mercy_count', '?')}, Milieu={pb.get('middle_count', '?')}, "
            f"dominant={pb.get('dominant_pillar', '?')}"
        )
    if t.get('synthesis'):
        parts.append(f"Synthese de l'Arbre : {str(t['synthesis'])[:400]}")
    return '\n'.join(parts) or "donnees kabbalistiques non disponibles"


async def _build_synthesis(first_name: str, karmic: dict, tree: dict, session_id: str) -> dict:
    kh = _karmic_highlights(karmic)
    th = _tree_highlights(tree)
    base = f"Prenom : {first_name}\n\nDONNEES KARMIQUES CLES :\n{kh}\n\nDONNEES KABBALISTIQUES :\n{th}\n\n"
    prompts = {
        'essence': base + (
            "Redige la page 'Ton essence karmique' : montre ou la memoire d'ame (Noeud Sud, Saturne, Chiron) "
            "et l'Arbre de Vie (Sephirah dominante, pilier dominant) racontent la meme histoire. "
            "Identifie LE fil rouge de cette incarnation."),
        'mission': base + (
            "Redige la page 'Ta mission d'ame' : croise la direction du Noeud Nord avec le focus spirituel "
            "kabbalistique. Decris concretement a quoi ressemble une vie alignee sur cette mission."),
        'pratiques': base + (
            "Redige la page 'Tes pratiques d'integration' : propose 3 pratiques concretes et personnalisees "
            "(une karmique, une kabbalistique, une croisee), chacune presentee dans un paragraphe fluide "
            "en expliquant pourquoi elle repond precisement a ce theme."),
    }
    keys = list(prompts.keys())
    results = await asyncio.gather(*[_gpt(prompts[k], f'{session_id}-{k}') for k in keys], return_exceptions=True)
    return {k: (r if isinstance(r, str) else '') for k, r in zip(keys, results)}


async def handle_pack_karmique_webhook(session_id: str) -> None:
    """Genere le PDF Pack Karmique + Kabbale et envoie l'email (idempotent, best-effort)."""
    if not session_id:
        return
    sb = get_admin_client()
    try:
        tx_res = sb.table('payment_transactions').select('*').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[pack_karmique] tx fetch failed: {e}')
        return
    if not tx_res or not tx_res.data:
        logger.warning(f'[pack_karmique] tx not found for {session_id}')
        return
    tx = tx_res.data
    md = tx.get('metadata') or {}
    if md.get('kind') != 'pack_karmique_kabbale':
        return

    if tx.get('status') != 'completed':
        sb.table('payment_transactions').update({
            'status': 'completed',
            'payment_status': 'paid',
            'credits_granted': True,
        }).eq('session_id', session_id).execute()

    if md.get('pdf_path'):
        logger.info(f'[pack_karmique] PDF already generated for {session_id}')
        return

    email = tx.get('user_email')
    pdf_ctx = md.get('pdf_ctx') or {}
    first_name = pdf_ctx.get('first_name') or 'Ami(e)'
    birth_date_iso = pdf_ctx.get('birth_date_iso') or ''
    birth_data = pdf_ctx.get('birth_data') or {}

    if not birth_data:
        logger.error(f'[pack_karmique] no birth_data for {session_id}')
        return

    # 1) Fetch karmic + tree en parallele
    karmic, tree = await asyncio.gather(
        aio.karmic_analysis(birth_data, name=first_name, language='fr'),
        aio.tree_of_life_chart(birth_data, system='modern_halevi', tradition='psychological', language='fr'),
        return_exceptions=True,
    )
    karmic = karmic if isinstance(karmic, dict) else None
    tree = tree if isinstance(tree, dict) else None
    if not karmic or not tree:
        logger.error(f'[pack_karmique] missing data (karmic={bool(karmic)}, tree={bool(tree)}) for {session_id}')
        return

    # 2) Synthese croisee GPT
    synthesis = await _build_synthesis(first_name, karmic, tree, session_id[-12:])

    # 3) PDF
    filename = f'pack_karmique_{session_id[-16:]}.pdf'
    try:
        pdf_bytes = generate_pack_karmique_pdf(
            first_name=first_name,
            birth_date_iso=birth_date_iso,
            karmic=karmic,
            tree_of_life=tree,
            synthesis=synthesis,
        )
        out_dir = ASSETS_DIR / 'pack_karmique'
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / filename, 'wb') as f:
            f.write(pdf_bytes)
        pdf_path = f'/api/assets/pack_karmique/{filename}'
        md['pdf_path'] = pdf_path
        md['pdf_generated_at'] = datetime.now(timezone.utc).isoformat()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        logger.info(f'[pack_karmique] PDF generated: {pdf_path}')
    except Exception as e:
        logger.error(f'[pack_karmique] PDF gen failed for {session_id}: {e}', exc_info=True)
        return

    # 4) Email best-effort
    if email:
        try:
            await _send_email(email, first_name, pdf_bytes, filename)
            md['email_sent_at'] = datetime.now(timezone.utc).isoformat()
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
        except Exception as e:
            logger.warning(f'[pack_karmique] email failed for {session_id}: {e}')


async def _send_email(email: str, first_name: str, pdf_bytes: bytes, filename: str) -> None:
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Solena · Plume Astrale <contact@plume-astrale.fr>')
    if not api_key:
        logger.warning('[pack_karmique] RESEND_API_KEY missing')
        return

    pdf_b64 = base64.b64encode(pdf_bytes).decode('ascii')
    fn = (first_name or 'ami(e)').strip()

    html = f"""
    <div style="max-width:600px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:40px 24px;">
      <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:11px;letter-spacing:0.32em;text-transform:uppercase;color:#D4AF37;">
          ✦ Plume Astrale · Edition Prestige ✦
        </div>
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:36px 28px;">
        <h1 style="font-family:'Cormorant Garamond',serif;font-weight:300;font-size:28px;color:#F5EEE0;margin:0 0 14px;line-height:1.25;">
          {fn.title()},<br>
          <em style="color:#D4AF37;font-style:italic;">ton Pack Karmique + Kabbale</em><br>
          est prêt.
        </h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Le document le plus complet que nous ayons jamais trace : environ 40 pages qui croisent
          la memoire karmique de ton ame et ton Arbre de Vie kabbalistique.
        </p>
        <ul style="color:#E3D7FF;line-height:1.9;font-size:14px;padding-left:20px;">
          <li>Tes <strong>points karmiques</strong> : Noeuds Lunaires, Lilith, Chiron, Vertex</li>
          <li>Les 80 sections de ton <strong>analyse karmique</strong> complete</li>
          <li>Tes <strong>10 Sephiroth</strong> et 22 chemins kabbalistiques</li>
          <li>Une <strong>synthese croisee</strong> unique, redigee pour toi seul(e)</li>
        </ul>
        <div style="margin-top:24px;padding:20px;background:#1A2035;border:1px solid rgba(212,175,55,0.15);border-radius:12px;text-align:center;">
          <div style="font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:8px;">
            ✦ Ton document est en pièce jointe ✦
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-style:italic;color:#E3D7FF;">
            Ne le lis pas d'une traite.<br>
            Laisse chaque partie infuser plusieurs jours.
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
                'subject': 'Ton Pack Karmique + Kabbale est prêt ✦',
                'html': html,
                'attachments': [{'filename': filename, 'content': pdf_b64}],
            },
        )
        if r.status_code >= 400:
            logger.warning(f'[pack_karmique] Resend error {r.status_code}: {r.text[:300]}')
        else:
            logger.info(f'[pack_karmique] Email sent to {email}')
