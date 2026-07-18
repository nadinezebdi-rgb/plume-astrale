"""
Séquence de nurturing des leads « extrait gratuit karmique » → conversion Pack 89€.

Boucle background (startup) : toutes les 6h,
  - étape 0 + lead âgé de ≥ 2 jours → email J+2 (rappel doux, ce qu'il a aimé)
  - étape 1 + lead âgé de ≥ 5 jours → email J+5 (dernière invitation)
Skips : lead désinscrit, lead ayant déjà acheté le pack (marqué converti).
Lien de désinscription : GET /api/oracle/unsubscribe?email= (backend public).
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone
import httpx

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 6 * 3600
SITE_URL = 'https://www.plume-astrale.fr'


def _backend_url() -> str:
    return os.environ.get('PUBLIC_BACKEND_URL', 'https://plume-astrale-production.up.railway.app').rstrip('/')


def _wrap(first_name: str, inner: str, email: str) -> str:
    unsub = f'{_backend_url()}/api/oracle/unsubscribe?email={email}'
    return f"""
    <div style="max-width:560px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:36px 24px;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:20px;">✦ Plume Astrale ✦</div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:32px 26px;">
        {inner}
        <div style="text-align:center;margin:26px 0 8px;">
          <a href="{SITE_URL}/pack-karmique" style="display:inline-block;background:#D4AF37;color:#111625;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none;">
            Débloquer mes 40 pages — 89€ →
          </a>
        </div>
        <p style="text-align:center;font-style:italic;color:#9089B5;font-size:13px;">— Soléna</p>
      </div>
      <div style="text-align:center;margin-top:18px;font-size:10px;color:#666;">
        <a href="{SITE_URL}" style="color:#D4AF37;text-decoration:none;">plume-astrale.fr</a>
        &nbsp;·&nbsp;
        <a href="{unsub}" style="color:#666;">se désinscrire</a>
      </div>
    </div>
    """


def _email_j2(first_name: str, email: str) -> tuple:
    inner = f"""
      <h1 style="font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;">
        {first_name}, tes Nœuds Lunaires <em style="color:#D4AF37;">n'étaient que le début</em>
      </h1>
      <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
        Il y a deux jours, tu as lu trois pages de ta mémoire karmique. Ce que ton extrait ne
        t'a pas encore montré : <strong style="color:#D4AF37;">les 77 autres sections</strong> —
        Lilith, Chiron, tes maisons de vie, chaque dialogue de ton ciel — et ton
        <strong style="color:#D4AF37;">Arbre de Vie kabbalistique</strong> complet.
      </p>
      <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
        Le document complet fait environ 40 pages, avec une synthèse croisée rédigée pour toi
        seul(e). C'est le genre de lecture qu'on garde toute une vie.
      </p>
    """
    return (f'{first_name}, la suite de ton extrait t\'attend ✦', _wrap(first_name, inner, email))


def _email_j5(first_name: str, email: str) -> tuple:
    inner = f"""
      <h1 style="font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;">
        {first_name}, une dernière chose <em style="color:#D4AF37;">avant que je referme ton dossier</em>
      </h1>
      <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
        J'ai tracé ton extrait il y a cinq jours et je repense à ce que ton Nœud Nord esquissait.
        La plupart des gens s'arrêtent aux trois premières pages — puis passent des années à
        chercher ailleurs ce que leur ciel disait déjà.
      </p>
      <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
        Si tu sens que c'est le moment, ton <strong style="color:#D4AF37;">Pack Karmique + Kabbale</strong>
        complet est prêt à être tracé : ~40 pages, livrées en quelques minutes.
        Sinon, aucun souci — ton extrait reste à toi, et je te souhaite une très belle route.
      </p>
    """
    return (f'{first_name}, avant que je referme ton dossier karmique…', _wrap(first_name, inner, email))


async def _send(email: str, subject: str, html: str) -> bool:
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    if not resend_key:
        return False
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                json={'from': sender, 'to': [email], 'subject': subject, 'html': html},
            )
            if r.status_code >= 400:
                logger.warning(f'[lead_nurture] Resend {r.status_code} pour {email}: {r.text[:150]}')
                return False
            return True
    except Exception as e:
        logger.warning(f'[lead_nurture] envoi échoué pour {email}: {e}')
        return False


def _has_bought_pack(sb, email: str) -> bool:
    try:
        r = (
            sb.table('payment_transactions').select('session_id')
            .eq('user_email', email).eq('pack_id', 'pack_karmique_kabbale')
            .eq('payment_status', 'paid').limit(1).execute()
        )
        return bool(r.data)
    except Exception:
        return False


async def _run_once() -> int:
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    r = (
        sb.table('oracle_leads').select('id, email, first_name, created_at, email_sequence_step')
        .eq('source', 'extrait_karmique')
        .is_('unsubscribed_at', 'null')
        .lt('email_sequence_step', 2)
        .limit(200)
        .execute()
    )
    sent = 0
    for lead in (r.data or []):
        email = (lead.get('email') or '').strip()
        if not email:
            continue
        try:
            created = datetime.fromisoformat(str(lead['created_at']).replace('Z', '+00:00'))
        except Exception:
            continue
        age_days = (now - created).total_seconds() / 86400
        step = lead.get('email_sequence_step') or 0
        first_name = (lead.get('first_name') or 'Voyageur').strip().title() or 'Voyageur'

        if _has_bought_pack(sb, email):
            sb.table('oracle_leads').update({'email_sequence_step': 2}).eq('id', lead['id']).execute()
            continue

        target = None
        if step == 0 and age_days >= 2:
            target = (_email_j2(first_name, email), 1)
        elif step == 1 and age_days >= 5:
            target = (_email_j5(first_name, email), 2)
        if not target:
            continue

        (subject, html), new_step = target
        ok = await _send(email, subject, html)
        sb.table('oracle_leads').update({
            'email_sequence_step': new_step,
            'last_email_sent_at': now.isoformat(),
        }).eq('id', lead['id']).execute()
        if ok:
            sent += 1
            logger.info(f'[lead_nurture] email J+{2 if new_step == 1 else 5} envoyé à {email}')
    return sent


async def lead_nurture_loop() -> None:
    logger.info('[lead_nurture] boucle démarrée (toutes les 6h — séquence J+2 / J+5)')
    while True:
        try:
            sent = await _run_once()
            if sent:
                logger.info(f'[lead_nurture] {sent} email(s) de séquence envoyé(s)')
        except Exception as e:
            logger.warning(f'[lead_nurture] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
