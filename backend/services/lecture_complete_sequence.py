"""
Sequence email post-achat Lecture Complete 97€ — 3 emails de suivi sur 14 jours.

Objectif : maximiser la valeur percue, augmenter les taux d'ouverture et
reduire les refunds de la garantie 14j.

Emails :
  - J+1 : "As-tu ouvert ta lecture ?"     (metadata.sequence_j1_sent_at)
  - J+7 : "Qu'est-ce qui resonne ?"        (metadata.sequence_j7_sent_at)
  - J+13 : "Clarte ou remboursee — dernier appel doux" (metadata.sequence_j13_sent_at)

Boucle background lancee au startup, s'execute toutes les 30 min.
Ne renvoie jamais 2 fois le meme email (idempotent via metadata).
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from services.supabase_client import get_admin_client
from services.resend_service import send_email

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 30 * 60  # 30 min


def _email_template(subject: str, prenom: str, body_html: str, cta_label: str,
                    cta_href: str = 'https://plume-astrale.fr/mon-compte') -> str:
    return f"""
    <div style="max-width:560px;margin:0 auto;font-family:Georgia,'Times New Roman',serif;
                color:#e8e6f0;background:#0b1020;padding:36px 24px;line-height:1.6;">
      <div style="text-align:center;font-size:11px;letter-spacing:0.3em;
                  text-transform:uppercase;color:#d9b26a;margin-bottom:22px;">
        ✦ Plume Astrale ✦
      </div>
      <div style="background:#141a33;border:1px solid #ffffff14;border-radius:16px;
                  padding:32px 26px;">
        <h1 style="font-weight:400;font-size:24px;color:#d9b26a;margin:0 0 16px;
                   font-family:Georgia,serif;">
          {subject}
        </h1>
        <p style="color:#e8e6f0;margin:0 0 16px;font-size:15px;">
          {prenom},
        </p>
        {body_html}
        <div style="text-align:center;margin:26px 0 10px;">
          <a href="{cta_href}"
             style="display:inline-block;background:#d9b26a;color:#1a1030;
                    padding:14px 28px;border-radius:40px;text-decoration:none;
                    font-weight:bold;letter-spacing:.5px;text-transform:uppercase;
                    font-size:14px;">
            {cta_label}
          </a>
        </div>
        <p style="color:#b8b4c9;font-size:12px;margin:22px 0 0;text-align:center;">
          Solena · Plume Astrale
        </p>
      </div>
      <p style="font-size:11px;color:#7d7a90;text-align:center;margin-top:20px;">
        Tu recois cet email parce que tu as commande une Lecture Complete du Ciel.
        Pour ne plus recevoir de suivi,
        <a href="https://plume-astrale.fr/mon-compte" style="color:#d9b26a;">gere tes preferences</a>.
      </p>
    </div>
    """


def _email_j1(prenom: str) -> tuple[str, str]:
    subject = 'As-tu ouvert ta lecture, {p} ?'.format(p=prenom)
    body = """
      <p>Ta Lecture Complete est arrivee dans ta boite hier.</p>
      <p>Si tu ne l'as pas encore ouverte, c'est normal — on repousse toujours
        les vraies choses.</p>
      <p style="font-style:italic;color:#d9b26a;">Je te propose une chose : ouvre
        seulement <strong>la premiere page de ton Theme Natal</strong>. Rien de plus.
        Regarde ce que ton ciel dit de ton Soleil.</p>
      <p>Cinq minutes. C'est tout ce que tu dois a cette voix qui, hier, avait besoin
        d'une reponse.</p>
    """
    return subject, body


def _email_j7(prenom: str) -> tuple[str, str]:
    subject = 'Qu\'est-ce qui resonne, {p} ?'.format(p=prenom)
    body = """
      <p>Une semaine s'est ecoulee depuis que tu as recu ta lecture.</p>
      <p>Je me demande : <em>qu'est-ce qui a fait mouche</em> ?</p>
      <p>Une phrase ? Un aspect ? Une fenetre 2026 que tu attends ?</p>
      <p>Prends 10 minutes ce soir pour relire un chapitre — celui que tu avais
        survole. Souvent, c'est la que se cache le vrai message.</p>
      <p style="font-style:italic;color:#d9b26a;">Et si tu veux me raconter,
        <a href="mailto:solena@plume-astrale.fr" style="color:#d9b26a;">ecris-moi</a>.
        Je lis chaque message.</p>
    """
    return subject, body


def _email_j13(prenom: str) -> tuple[str, str]:
    subject = 'Clarte ou remboursee — {p}, une derniere fois'.format(p=prenom)
    body = """
      <p>Il te reste 24h dans la fenetre de garantie 14 jours.</p>
      <p>Si ta lecture ne t'a pas apporte au moins une <em>vraie</em> clarte sur
        ce que tu traverses, tu me le dis et on te rembourse. Integralement.
        Sans avoir a te justifier.</p>
      <p>Mais avant ca, je te pose une question :</p>
      <p style="font-style:italic;color:#d9b26a;text-align:center;font-size:17px;">
        « Qu'est-ce qui a le plus bouge en toi, cette semaine ? »
      </p>
      <p>Souvent, la valeur d'une lecture ne se voit pas tout de suite.
        Elle infuse. Elle se pose. Puis, un matin, un choix devient evident.</p>
      <p>Prends 5 minutes. Relis ta lecture karmique. Et decide en conscience.</p>
      <p style="font-size:13px;color:#b8b4c9;">Pour le remboursement, il te suffit
        de repondre a ce mail avec le mot <strong>remboursement</strong>.</p>
    """
    return subject, body


def _email_j30(prenom: str, variant: str = 'question') -> tuple[str, str]:
    """J+30 upsell : offre Cercle Solena longue duree a tarif preferentiel.

    A/B test sur le subject :
      - 'question' : question ouverte "veux-tu aller plus loin ?"
      - 'invitation' : invitation directe "une place dans le Cercle"
    """
    if variant == 'invitation':
        subject = '{p}, ta place dans le Cercle Solena t\'attend'.format(p=prenom)
    else:
        subject = '{p}, veux-tu aller plus loin ?'.format(p=prenom)
    body = """
      <p>Il y a un mois, tu as ouvert la porte.</p>
      <p>Ta Lecture Complete t'a montre les cartes. Le sens des cycles, les
        heritages, les fenetres a venir. C'est un debut.</p>
      <p style="font-style:italic;color:#d9b26a;">Mais un ciel ne se lit pas une fois.
        Il se lit chaque saison, chaque nouvelle lune, chaque tournant.</p>
      <p>Je t'invite dans le <strong>Cercle Solena longue duree</strong> — un
        accompagnement continu, pas un abonnement de plus. Tu y trouves :</p>
      <ul>
        <li>Ton horoscope personnel chaque matin</li>
        <li>Une lecture approfondie une fois par mois</li>
        <li>Un canal direct avec moi pour tes questions urgentes</li>
      </ul>
      <p>Prix regulier : 29€/mois. Pour toi, parce que tu as deja fait le pas,
        <strong style="color:#d9b26a;">19€/mois pendant 6 mois</strong> puis 29€.</p>
      <p style="font-size:13px;color:#b8b4c9;">Offre valable 7 jours seulement. Sans engagement,
        arret possible a tout moment.</p>
    """
    return subject, body


async def _process_transaction(tx: Dict[str, Any]) -> int:
    """Envoie l'email applicable pour cette transaction (J+1, J+7, J+13 ou J+30).
    Retourne 1 si un email a ete envoye, 0 sinon."""
    session_id = tx.get('session_id')
    md = tx.get('metadata') or {}
    # Skip si refunded
    if md.get('refunded_at'):
        return 0
    email = tx.get('user_email') or (md.get('order_ctx') or {}).get('email')
    if not email:
        return 0

    prenom = ((md.get('order_ctx') or {}).get('first_name') or 'Ami(e)').strip() or 'Ami(e)'
    created_at = tx.get('created_at')
    if not created_at:
        return 0
    try:
        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except Exception:
        return 0
    age_h = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600.0

    # Determine l'email a envoyer (max un par run) — priorite au plus ancien non-envoye
    stage: str | None = None
    if age_h >= 24 and not md.get('sequence_j1_sent_at'):
        stage = 'j1'
    elif age_h >= 24 * 7 and not md.get('sequence_j7_sent_at'):
        stage = 'j7'
    elif age_h >= 24 * 13 and not md.get('sequence_j13_sent_at'):
        stage = 'j13'
    elif age_h >= 24 * 30 and not md.get('sequence_j30_sent_at'):
        stage = 'j30'
    if not stage:
        return 0

    if stage == 'j1':
        subject, body = _email_j1(prenom)
        cta_label = 'Ouvrir ma lecture'
    elif stage == 'j7':
        subject, body = _email_j7(prenom)
        cta_label = 'Relire ma lecture'
    elif stage == 'j13':
        subject, body = _email_j13(prenom)
        cta_label = 'Acceder a mes documents'
    else:
        # A/B test J+30 : variant deterministe sur session_id (50/50)
        # Override admin possible via app_settings.forced_j30_variant
        try:
            from services.app_settings import get_setting as _get_setting
            forced = _get_setting('forced_j30_variant')
        except Exception:
            forced = None
        if forced in ('question', 'invitation'):
            variant = forced
        else:
            import hashlib
            h = int(hashlib.md5((session_id or '').encode('utf-8')).hexdigest(), 16)
            variant = 'invitation' if (h % 2 == 0) else 'question'
        subject, body = _email_j30(prenom, variant=variant)
        cta_label = 'Rejoindre le Cercle · 19€/mois'
        md['sequence_j30_variant'] = variant

    html = _email_template(subject, prenom, body, cta_label)
    try:
        eid = await send_email(email, subject, html)
    except Exception as e:
        logger.warning(f'[lecture_complete_seq] send fail {session_id} stage={stage}: {e}')
        return 0
    if not eid:
        return 0

    # Marque envoye (idempotent)
    md[f'sequence_{stage}_sent_at'] = datetime.now(timezone.utc).isoformat()
    md[f'sequence_{stage}_email_id'] = eid
    try:
        sb = get_admin_client()
        sb.table('payment_transactions').update({'metadata': md}).eq('session_id', session_id).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete_seq] metadata update fail {session_id}: {e}')

    logger.info(f'[lecture_complete_seq] {stage} envoye a {email} (session {session_id})')
    return 1


async def _run_once() -> int:
    """Cherche les tx lecture_complete payes de moins de 32j, envoie l'email applicable."""
    sb = get_admin_client()
    now = datetime.now(timezone.utc)
    min_dt = now - timedelta(days=32)  # J+30 + marge
    try:
        r = sb.table('payment_transactions').select(
            'session_id, user_email, created_at, metadata, payment_status, pack_id'
        ).eq('pack_id', 'lecture_complete').eq('payment_status', 'paid').gte(
            'created_at', min_dt.isoformat()
        ).limit(500).execute()
    except Exception as e:
        logger.warning(f'[lecture_complete_seq] fetch fail: {e}')
        return 0
    rows = (r.data or []) if r else []
    sent = 0
    for tx in rows:
        try:
            sent += await _process_transaction(tx)
        except Exception as e:
            logger.warning(f'[lecture_complete_seq] process fail {tx.get("session_id")}: {e}')
    return sent


async def lecture_complete_sequence_loop() -> None:
    """Boucle background — tourne toutes les 30 min. Envoie J+1, J+7, J+13, J+30."""
    logger.info('[lecture_complete_seq] boucle demarree (J+1, J+7, J+13, J+30, toutes les 30 min)')
    while True:
        try:
            n = await _run_once()
            if n:
                logger.info(f'[lecture_complete_seq] {n} email(s) envoye(s) ce cycle')
        except Exception as e:
            logger.warning(f'[lecture_complete_seq] erreur boucle: {e}')
        await asyncio.sleep(CHECK_INTERVAL_S)
