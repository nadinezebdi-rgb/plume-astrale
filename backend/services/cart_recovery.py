"""
Relance panier — emails automatiques pour les paiements Stripe abandonnés.

Boucle background (démarrée au startup) : toutes les 30 min, cherche les
payment_transactions 'initiated'/'pending' âgées de 3h à 48h, sans relance
déjà envoyée, et envoie un email de rappel avec lien vers la page produit.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
import httpx

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 30 * 60
MIN_AGE_H = 3
MAX_AGE_H = 48

# pack_id -> (nom affiché, url produit)
PRODUCT_INFO = {
    'pack_karmique_kabbale': ('Pack Karmique + Kabbale (89€)', '/pack-karmique'),
    'kabbale_arbre_de_vie': ('Ton Arbre de Vie Kabbalistique (39€)', '/kabbale'),
    'rencontres_ultime': ('Guide de Compatibilité Ultime (29,99€)', '/rencontres-astrales'),
    'numerologie_code': ('Ton Code Numérologique (19€)', '/numerologie-pdf'),
    'karma_destin_analysis': ('Ton Analyse Karmique & Destinée (24€)', '/karma-destin-pdf'),
    'fenetre_rencontre_avancee': ('Tes Fenêtres de Rencontre (29€)', '/rencontres-astrales'),  # deprecated 2026-02 — redirige vers Rencontres Ultime
    'theme_natal_pdf_oneshot': ('Ton Thème Natal Complet (29€)', '/theme-natal'),
    'comete': ('Pack Comète — 30 crédits (7,99€)', '/acheter-credits'),
    'nebuleuse': ('Pack Nébuleuse — 80 crédits (17,99€)', '/acheter-credits'),
    'constellation': ('Pack Constellation — 180 crédits (34,99€)', '/acheter-credits'),
    'voie_lactee': ('Pack Voie Lactée — 350 crédits (59,99€)', '/acheter-credits'),
}

SITE_URL = 'https://www.plume-astrale.fr'


def _email_html(product_name: str, product_url: str) -> str:
    return f"""
    <div style="max-width:560px;margin:0 auto;font-family:'Cormorant Garamond',Georgia,serif;color:#F5EEE0;background:#111625;padding:36px 24px;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.3em;text-transform:uppercase;color:#D4AF37;margin-bottom:20px;">
        ✦ Plume Astrale ✦
      </div>
      <div style="background:rgba(26,32,53,0.65);border:1px solid rgba(212,175,55,0.22);border-radius:16px;padding:32px 26px;">
        <h1 style="font-weight:300;font-size:26px;color:#F5EEE0;margin:0 0 14px;line-height:1.3;">
          Les astres t'ont vu <em style="color:#D4AF37;">hésiter</em>…
        </h1>
        <p style="color:#E3D7FF;line-height:1.65;font-size:15px;">
          Tu étais à un souffle de recevoir <strong style="color:#D4AF37;">{product_name}</strong>,
          puis quelque chose t'a interrompu(e). Ta lecture t'attend toujours —
          il ne manque que toi.
        </p>
        <div style="text-align:center;margin:26px 0;">
          <a href="{SITE_URL}{product_url}" style="display:inline-block;background:#D4AF37;color:#111625;font-weight:700;padding:14px 30px;border-radius:999px;text-decoration:none;letter-spacing:0.08em;">
            Terminer ma commande →
          </a>
        </div>
        <p style="color:#9089B5;font-size:12px;text-align:center;">
          Livraison par email en quelques minutes · Paiement sécurisé Stripe
        </p>
      </div>
      <div style="text-align:center;margin-top:20px;font-size:10px;color:#666;">
        <a href="{SITE_URL}" style="color:#D4AF37;text-decoration:none;">plume-astrale.fr</a>
      </div>
    </div>
    """


async def _run_once() -> int:
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    sender = os.environ.get('SENDER_EMAIL', 'Soléna · Plume Astrale <contact@plume-astrale.fr>')
    if not resend_key:
        return 0
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    r = (
        sb.table('payment_transactions').select('session_id, user_email, pack_id, metadata, created_at')
        .in_('status', ['initiated', 'pending'])
        .neq('payment_status', 'paid')
        .gte('created_at', (now - timedelta(hours=MAX_AGE_H)).isoformat())
        .lte('created_at', (now - timedelta(hours=MIN_AGE_H)).isoformat())
        .limit(100)
        .execute()
    )
    sent = 0
    for tx in (r.data or []):
        md = tx.get('metadata') or {}
        email = (tx.get('user_email') or '').strip()
        session_id = tx.get('session_id') or ''
        if not email or md.get('relance_sent_at') or not session_id.startswith('cs_'):
            continue
        product_name, product_url = PRODUCT_INFO.get(tx.get('pack_id') or '', ('ta lecture Plume Astrale', '/'))
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    'https://api.resend.com/emails',
                    headers={'Authorization': f'Bearer {resend_key}', 'Content-Type': 'application/json'},
                    json={
                        'from': sender,
                        'to': [email],
                        'subject': 'Ta commande t\'attend toujours ✦',
                        'html': _email_html(product_name, product_url),
                    },
                )
            md['relance_sent_at'] = now.isoformat()
            md['relance_status'] = resp.status_code
            sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
            if resp.status_code < 400:
                sent += 1
                logger.info(f'[cart_recovery] relance envoyée à {email} ({product_name})')
            else:
                logger.warning(f'[cart_recovery] Resend {resp.status_code} pour {email}: {resp.text[:150]}')
        except Exception as e:
            logger.warning(f'[cart_recovery] échec pour {session_id}: {e}')
    return sent


async def cart_recovery_loop() -> None:
    logger.info('[cart_recovery] boucle démarrée (toutes les 30 min, fenêtre 3h-48h)')
    while True:
        try:
            sent = await _run_once()
            if sent:
                logger.info(f'[cart_recovery] {sent} relance(s) envoyée(s)')
        except Exception as e:
            logger.warning(f'[cart_recovery] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
