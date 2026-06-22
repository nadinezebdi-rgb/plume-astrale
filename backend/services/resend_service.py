"""Service Resend — envoi des emails de la sequence Plume Astrale.

Sequence (cahier des charges):
  E1  J0   - livraison teaser
  E2  J+1  - valeur Lune (0 vente)
  E3  J+3  - 1re offre Cercle
  E4  J+7  - intro Synastrie + apercu
  E5  J+10 - offre Synastrie + PayPal 4x
  E6  J+14 - relance douce finale

Tous les envois sont idempotents grace a `oracle_leads.last_email_sent_at` + step.
"""
from __future__ import annotations
import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta, date
from typing import Optional, Any

import resend
from dotenv import load_dotenv

from services.supabase_client import get_admin_client

load_dotenv(dotenv_path='/app/backend/.env')
logger = logging.getLogger(__name__)

resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'Plume Astrale <contact.plume@gmail.com>')
DAILY_JOURNAL_SENDER_EMAIL = os.environ.get('DAILY_JOURNAL_SENDER_EMAIL', SENDER_EMAIL)


SITE_URL = 'https://plume-astrale.fr'

# ───────────────────── HTML helpers ─────────────────────

def _wrap(inner_html: str, preview: str = '') -> str:
    """Enrobe le contenu d'un email dans un layout editorial sombre cohérent avec la marque."""
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Plume Astrale</title></head>
<body style="margin:0;padding:0;background:#0C0918;font-family:Georgia,'Cormorant Garamond',serif;color:#F0E6D3;">
<div style="display:none;max-height:0;overflow:hidden;color:transparent;">{preview}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0C0918;">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="max-width:560px;background:#15112A;border:1px solid rgba(212,180,106,0.18);border-radius:18px;overflow:hidden;">
      <tr><td style="padding:32px 36px 8px;text-align:center;border-bottom:1px solid rgba(212,180,106,0.12);">
        <p style="margin:0;font-size:11px;letter-spacing:0.3em;color:#D4B46A;text-transform:uppercase;font-family:Georgia,serif;">Plume Astrale</p>
        <p style="margin:6px 0 0;font-size:10px;color:rgba(184,176,200,0.5);letter-spacing:0.05em;">Sanctuaire numérique</p>
      </td></tr>
      <tr><td style="padding:36px 36px 32px;">
        {inner_html}
      </td></tr>
      <tr><td style="padding:24px 36px 32px;border-top:1px solid rgba(212,180,106,0.1);text-align:center;color:rgba(184,176,200,0.55);font-size:11px;line-height:1.7;">
        Plume Astrale · <a href="{SITE_URL}" style="color:#D4B46A;text-decoration:none;">plume-astrale.fr</a><br>
        Tu reçois cet email parce que tu as découvert ta lecture sur Plume Astrale.<br>
        <a href="{SITE_URL}/desabonnement?email={{email}}" style="color:rgba(184,176,200,0.6);text-decoration:underline;">Me désabonner</a> ·
        <a href="{SITE_URL}/notre-cadre" style="color:rgba(184,176,200,0.6);text-decoration:underline;">Notre cadre</a>
      </td></tr>
    </table>
  </td></tr>
</table></body></html>"""


def _btn(text: str, href: str) -> str:
    return f"""<table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px auto;">
<tr><td style="background:linear-gradient(135deg,#D4B46A 0%,#C5A059 100%);border-radius:999px;">
<a href="{href}" style="display:inline-block;padding:14px 32px;color:#0C0918;text-decoration:none;font-weight:700;font-size:13px;letter-spacing:0.14em;text-transform:uppercase;font-family:Arial,sans-serif;">
{text}</a></td></tr></table>"""


def _h2(text: str) -> str:
    return f'<h2 style="font-family:Georgia,serif;font-size:24px;font-weight:300;color:#F0E6D3;margin:0 0 18px;line-height:1.3;">{text}</h2>'


def _p(text: str) -> str:
    return f'<p style="font-size:16px;line-height:1.75;color:rgba(240,230,211,0.88);margin:0 0 16px;font-family:Georgia,serif;">{text}</p>'


# ───────────────────── Templates des 6 emails ─────────────────────

def _email_e1(first_name: str, lifepath: dict, moon_phase: dict, tarot: dict) -> tuple[str, str, str]:
    """E1 J0 — livraison teaser."""
    subject = f"{first_name}, ton éclairage est arrivé ✦"
    preview = f"Ton chemin de vie {lifepath.get('number')}, la Lune et ta carte du jour t'attendent."
    body = _h2(f"{first_name}, voici ce que les étoiles murmurent…") + \
        _p("Comme promis, ta lecture symbolique est arrivée. Voici ce que ta carte révèle aujourd'hui :") + \
        f"""<div style="background:rgba(212,180,106,0.06);border:1px solid rgba(212,180,106,0.2);border-radius:14px;padding:20px;margin:20px 0;">
<p style="margin:0 0 6px;font-size:10px;letter-spacing:0.2em;color:#D4B46A;text-transform:uppercase;">Chemin de vie</p>
<p style="margin:0;font-size:20px;font-family:Georgia,serif;color:#F0E6D3;">{lifepath.get('number')} · {lifepath.get('archetype', '')}</p></div>""" + \
        f"""<div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.2);border-radius:14px;padding:20px;margin:0 0 20px;">
<p style="margin:0 0 6px;font-size:10px;letter-spacing:0.2em;color:#A78BFA;text-transform:uppercase;">Phase lunaire</p>
<p style="margin:0 0 8px;font-size:18px;font-family:Georgia,serif;color:#F0E6D3;">{moon_phase.get('phase', '')}</p>
<p style="margin:0;font-size:14px;color:rgba(184,176,200,0.85);">{moon_phase.get('message', '')}</p></div>""" + \
        f"""<div style="background:rgba(74,222,128,0.04);border:1px solid rgba(74,222,128,0.2);border-radius:14px;padding:20px;margin:0 0 24px;">
<p style="margin:0 0 6px;font-size:10px;letter-spacing:0.2em;color:#4ADE80;text-transform:uppercase;">Tirage du jour</p>
<p style="margin:0 0 8px;font-size:18px;font-family:Georgia,serif;color:#F0E6D3;">{tarot.get('card_name', '')}</p>
<p style="margin:0;font-size:14px;color:rgba(184,176,200,0.85);font-style:italic;">« {tarot.get('answer', '')} »</p></div>""" + \
        _p("Demain, je t'envoie une lecture spéciale sur ta Lune — ce qu'elle dit vraiment de tes émotions. Ce sera plus profond que tout ce que tu as déjà lu.") + \
        _p("D'ici là, prends soin de toi.<br><em>— Plume</em>")
    return subject, _wrap(body, preview), f"{first_name}, ton éclairage est arrivé. Visite : {SITE_URL}"


def _email_e2(first_name: str) -> tuple[str, str, str]:
    """E2 J+1 — valeur pure, 0 vente."""
    subject = "Ce que ta Lune dit de tes émotions 🌙"
    preview = "Quelques minutes pour comprendre ce qui te traverse vraiment."
    body = _h2("Ta Lune, ton paysage intérieur") + \
        _p(f"{first_name}, la Lune dans ton thème est le miroir de ton monde émotionnel. Elle révèle comment tu te ressources, ce dont tu as besoin pour te sentir en sécurité, et la façon dont tu accueilles l'amour.") + \
        _p("Les jours où tu te sens fragile sans raison apparente, c'est souvent ta Lune qui parle. Pas un déséquilibre — un appel.") + \
        _p("Aujourd'hui, je voudrais juste te poser une question :") + \
        '<p style="font-size:18px;font-family:Georgia,serif;font-style:italic;color:#D4B46A;text-align:center;margin:24px 0;border-left:2px solid #D4B46A;padding:0 0 0 16px;text-align:left;">Quelle émotion as-tu repoussée cette semaine, sans même t\'en rendre compte ?</p>' + \
        _p("Pas besoin de répondre. Juste sentir.") + \
        _p("Si tu veux explorer ta Lune en profondeur — ton signe lunaire, ta maison lunaire, comment elle dialogue avec le reste de ton ciel — je te montre comment dans quelques jours.") + \
        _p("Pour aujourd'hui, écoute simplement.<br><em>— Plume</em>")
    return subject, _wrap(body, preview), preview


def _email_e3(first_name: str) -> tuple[str, str, str]:
    """E3 J+3 — 1re offre Cercle."""
    subject = "Et si chaque matin commençait par toi ?"
    preview = "Un rituel quotidien pour habiter ta vie avec plus de clarté. Sans engagement."
    body = _h2(f"{first_name}, un rituel pour t'écouter") + \
        _p("Tu sais ce moment, le matin, où tu n'as pas encore vraiment commencé la journée mais déjà tu cours ?") + \
        _p("Le Cercle existe pour te ramener à toi — quelques minutes, le matin et le soir, pour te poser une question, écouter ton ciel du jour, déposer ce que tu portes.") + \
        """<div style="background:rgba(212,180,106,0.06);border:1px solid rgba(212,180,106,0.2);border-radius:14px;padding:22px;margin:20px 0;">
<p style="margin:0 0 14px;font-size:11px;letter-spacing:0.18em;color:#D4B46A;text-transform:uppercase;font-family:Georgia,serif;">Chaque jour, dans Le Cercle</p>
<ul style="margin:0;padding:0;list-style:none;color:rgba(240,230,211,0.85);">
<li style="padding:6px 0 6px 22px;position:relative;font-family:Georgia,serif;">· Le Conseil de la Plume (matin)</li>
<li style="padding:6px 0 6px 22px;position:relative;font-family:Georgia,serif;">· Tes énergies en temps réel</li>
<li style="padding:6px 0 6px 22px;position:relative;font-family:Georgia,serif;">· Un check-in 1 tap</li>
<li style="padding:6px 0 6px 22px;position:relative;font-family:Georgia,serif;">· La Réflexion du soir (journal privé)</li>
<li style="padding:6px 0 6px 22px;position:relative;font-family:Georgia,serif;">· Compatibilités illimitées</li>
</ul>
</div>""" + \
        _p("<strong style=\"color:#D4B46A;\">14,90€/mois.</strong> Sans engagement. Annulable en 1 clic.") + \
        _p("Et ce que je trouve important : pas de notifications culpabilisantes, un jour d'oubli par mois t'est offert. C'est ta présence à toi qui compte, pas ta performance.") + \
        _btn("✦ Rejoindre Le Cercle", f"{SITE_URL}/cercle") + \
        _p('<a href="' + SITE_URL + '/notre-cadre" style="color:rgba(184,176,200,0.7);text-decoration:underline;">Lire Notre cadre</a> · <a href="' + SITE_URL + '/cercle" style="color:rgba(184,176,200,0.7);text-decoration:underline;">Voir le détail</a>')
    return subject, _wrap(body, preview), preview


def _email_e4(first_name: str) -> tuple[str, str, str]:
    """E4 J+7 — intro Synastrie + apercu."""
    subject = "Il y a quelqu'un dont tu aimerais comprendre l'énergie ?"
    preview = "L'analyse de votre alchimie astrologique, page après page."
    body = _h2("L'Alchimie a un langage") + \
        _p(f"{first_name}, on me demande souvent : « Est-ce qu'on est compatibles avec quelqu'un ? »") + \
        _p("La vraie question n'est pas <em>est-ce qu'on est compatibles</em>. C'est <em>comment nos énergies dialoguent</em>. Parce qu'aucune relation n'est sans tension. Et chaque tension cache un chemin de croissance.") + \
        _p("J'ai créé pour toi un rapport unique : <strong style=\"color:#D4B46A;\">L'Analyse Alchimique</strong>. 23 pages qui révèlent :") + \
        """<ul style="font-family:Georgia,serif;font-size:15px;color:rgba(240,230,211,0.85);line-height:1.9;padding-left:20px;">
<li>Vos profils amoureux croisés</li>
<li>Le dialogue Soleil/Lune (votre identité face à ses émotions)</li>
<li>L'axe Vénus/Mars (votre alchimie sensuelle)</li>
<li>Les terrains de croissance — ce qui peut devenir grand entre vous</li>
<li>Le rituel à deux que je vous propose</li>
</ul>""" + \
        _p("Tu peux voir les <strong>2 premières pages gratuitement</strong> avant de décider.") + \
        _btn("👁 Voir l'aperçu", f"{SITE_URL}/synastrie") + \
        _p("Pas pressée. Reviens quand c'est le bon moment.<br><em>— Plume</em>")
    return subject, _wrap(body, preview), preview


def _email_e5(first_name: str) -> tuple[str, str, str]:
    """E5 J+10 — offre Synastrie + PayPal 4x."""
    subject = "Votre alchimie, page après page (49€ ou 4× sans frais)"
    preview = "L'Analyse Alchimique complète. Aujourd'hui, payable en 4 fois sans frais."
    body = _h2("23 pages pour décoder votre lien") + \
        _p(f"{first_name}, je voulais te montrer la structure exacte du rapport — pour que tu saches précisément ce que tu reçois.") + \
        """<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(212,180,106,0.15);border-radius:14px;padding:20px;margin:18px 0;font-family:Georgia,serif;font-size:14px;line-height:1.8;color:rgba(240,230,211,0.88);">
<strong style="color:#D4B46A;">Page 1–2</strong> · Couverture + Votre alchimie en un regard<br>
<strong style="color:#D4B46A;">Page 3–6</strong> · Compatibilité fondamentale<br>
<strong style="color:#D4B46A;">Page 7–14</strong> · Aspects Soleil, Lune, Vénus, Mars, Mercure, Saturne<br>
<strong style="color:#D4B46A;">Page 15–20</strong> · Vos profils amoureux croisés<br>
<strong style="color:#D4B46A;">Page 21–25</strong> · Forces, terrains de croissance, rituel à deux
</div>""" + \
        _p("L'équivalent d'une consultation à 120€ chez une astrologue. <strong style=\"color:#D4B46A;\">49€</strong> chez moi.") + \
        _p("Et parce que c'est un investissement réel, <strong>tu peux payer en 4 fois 12,25€ sans frais</strong> via PayPal — sans dossier, sans intérêts.") + \
        _btn("✦ Révéler notre alchimie", f"{SITE_URL}/synastrie") + \
        _p('<span style="color:rgba(184,176,200,0.6);font-size:13px;">Aperçu gratuit · Stripe sécurisé · PayPal 4× sans frais</span>')
    return subject, _wrap(body, preview), preview


def _email_e6(first_name: str) -> tuple[str, str, str]:
    """E6 J+14 — relance douce finale."""
    subject = "On garde ta place au chaud ✦"
    preview = "Au cas où tu reviendrais — voici le chemin le plus court."
    body = _h2(f"{first_name}, je te laisse tranquille.") + \
        _p("Tu as découvert ta lecture il y a deux semaines. Si tu n'as pas eu envie d'aller plus loin, c'est parfaitement bien. Le rythme est le tien.") + \
        _p("Je ne vais plus te déranger. Mais avant de m'en aller, je voulais te laisser deux portes ouvertes :") + \
        f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
<tr><td style="padding:12px 0;border-bottom:1px solid rgba(212,180,106,0.12);font-family:Georgia,serif;">
<p style="margin:0 0 4px;font-size:11px;letter-spacing:0.15em;color:#D4B46A;text-transform:uppercase;">Si tu veux un rituel quotidien</p>
<a href="{SITE_URL}/cercle" style="color:#F0E6D3;font-size:17px;text-decoration:none;">Le Cercle · 14,90€/mois →</a>
</td></tr>
<tr><td style="padding:12px 0;font-family:Georgia,serif;">
<p style="margin:0 0 4px;font-size:11px;letter-spacing:0.15em;color:#D4B46A;text-transform:uppercase;">Si quelqu'un compte pour toi</p>
<a href="{SITE_URL}/synastrie" style="color:#F0E6D3;font-size:17px;text-decoration:none;">L'Analyse Alchimique · 49€ →</a>
</td></tr></table>""" + \
        _p("Sinon, prends bien soin de toi. Ta vie est ta plus belle œuvre.") + \
        _p("<em>— Plume</em>")
    return subject, _wrap(body, preview), preview


# ───────────────────── Dispatcher ─────────────────────

EMAIL_BUILDERS = {
    1: _email_e1,
    2: _email_e2,
    3: _email_e3,
    4: _email_e4,
    5: _email_e5,
    6: _email_e6,
}


async def send_email(
    to_email: str,
    subject: str,
    html: str,
    text: str = '',
    from_email: Optional[str] = None,
) -> Optional[str]:
    """Envoi non-bloquant. Retourne l'email_id ou None si echec."""
    if not resend.api_key:
        logger.warning('RESEND_API_KEY non configure — email non envoye.')
        return None
    params = {
        'from': from_email or SENDER_EMAIL,
        'to': [to_email],
        'subject': subject,
        'html': html,
    }
    if text:
        params['text'] = text
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        eid = result.get('id') if isinstance(result, dict) else None
        logger.info(f'[resend] sent to {to_email} subject="{subject[:50]}" id={eid}')
        return eid
    except Exception as e:
        logger.error(f'[resend] FAIL to={to_email} subject="{subject[:50]}" err={e}')
        return None


async def send_e1_teaser_now(email: str, first_name: str, lifepath: dict, moon_phase: dict, tarot: dict) -> bool:
    """E1 envoye immediatement apres capture email (livraison teaser)."""
    subject, html, text = _email_e1(first_name or 'Voyageur', lifepath, moon_phase, tarot)
    html = html.replace('{email}', email)
    eid = await send_email(email, subject, html, text)
    if eid:
        try:
            sb = get_admin_client()
            sb.table('oracle_leads').update({
                'email_sequence_step': 1,
                'last_email_sent_at': datetime.now(timezone.utc).isoformat(),
            }).eq('email', email.lower().strip()).execute()
        except Exception as e:
            logger.warning(f'[resend] failed to update lead step: {e}')
    return bool(eid)


# Planning J+1, J+3, J+7, J+10, J+14 (en jours depuis lead creation)
SEQUENCE_SCHEDULE = {
    2: timedelta(days=1),
    3: timedelta(days=3),
    4: timedelta(days=7),
    5: timedelta(days=10),
    6: timedelta(days=14),
}


async def process_sequence_step(lead: dict) -> int:
    """Envoie l'email correspondant a l'etape suivante si la date est atteinte.
    Retourne le nouveau step (0 si rien envoye)."""
    if lead.get('unsubscribed_at'):
        return 0
    if not lead.get('consent_marketing', True):
        return 0

    current_step = int(lead.get('email_sequence_step') or 0)
    next_step = current_step + 1
    if next_step not in SEQUENCE_SCHEDULE:
        return 0

    created_at = lead.get('created_at')
    if not created_at:
        return 0
    try:
        created_dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
    except Exception:
        return 0

    expected_send = created_dt + SEQUENCE_SCHEDULE[next_step]
    if datetime.now(timezone.utc) < expected_send:
        return 0

    first_name = (lead.get('first_name') or 'Voyageur')
    builder = EMAIL_BUILDERS.get(next_step)
    if not builder:
        return 0

    if next_step == 1:
        # E1 ne devrait pas etre envoye par le scheduler
        return 0

    subject, html, text = builder(first_name)
    html = html.replace('{email}', lead.get('email', ''))
    eid = await send_email(lead['email'], subject, html, text)
    if not eid:
        return 0

    try:
        sb = get_admin_client()
        sb.table('oracle_leads').update({
            'email_sequence_step': next_step,
            'last_email_sent_at': datetime.now(timezone.utc).isoformat(),
        }).eq('email', lead['email']).execute()
    except Exception as e:
        logger.warning(f'[resend] failed to update step after send: {e}')

    return next_step



# ═══════════════════════════════════════════════════════════════
# Email Synastrie 49€ (Phase 3)
# ═══════════════════════════════════════════════════════════════
async def send_synastrie_email(to_email: str, prenom1: str, prenom2: str, pdf_path: str) -> Optional[str]:
    """Envoie le lien de telechargement du rapport Synastrie apres paiement."""
    base = os.environ.get('PUBLIC_APP_URL', 'https://plume-astrale.fr').rstrip('/')
    download_url = f"{base}{pdf_path}" if pdf_path.startswith('/') else pdf_path
    subject = f"Votre Synastrie {prenom1} & {prenom2} est prete"
    inner = (
        _h2('Votre rapport est arrive') +
        _p(f"Cher voyageur, votre rapport de synastrie pour <strong>{prenom1}</strong> et <strong>{prenom2}</strong> a ete soigneusement compose.") +
        _p("Vous y decouvrirez les aspects planetaires entre vos deux themes, les dynamiques relationnelles a l'oeuvre, les points de croissance et des invitations concretes pour nourrir votre lien.") +
        _btn('Telecharger mon rapport (PDF)', download_url) +
        _p("Ce lien restera actif. Sauvegardez le PDF dans un endroit precieux — il vous accompagnera dans votre chemin a deux.") +
        _p("<em>Avec douceur,<br>Plume</em>")
    )
    html = _wrap(inner, preview=f'Synastrie {prenom1} & {prenom2}')
    text = f"Votre rapport Synastrie {prenom1} & {prenom2} est pret : {download_url}"
    return await send_email(to_email, subject, html, text)
def _extract_sign_from_birth_date(value: str) -> str:
    """Convertit YYYY-MM-DD en signe zodiacal occidental (EN)."""
    y, m, d = [int(x) for x in str(value).split('-')]
    if (m == 3 and d >= 21) or (m == 4 and d <= 19):
        return 'Aries'
    if (m == 4 and d >= 20) or (m == 5 and d <= 20):
        return 'Taurus'
    if (m == 5 and d >= 21) or (m == 6 and d <= 20):
        return 'Gemini'
    if (m == 6 and d >= 21) or (m == 7 and d <= 22):
        return 'Cancer'
    if (m == 7 and d >= 23) or (m == 8 and d <= 22):
        return 'Leo'
    if (m == 8 and d >= 23) or (m == 9 and d <= 22):
        return 'Virgo'
    if (m == 9 and d >= 23) or (m == 10 and d <= 22):
        return 'Libra'
    if (m == 10 and d >= 23) or (m == 11 and d <= 21):
        return 'Scorpio'
    if (m == 11 and d >= 22) or (m == 12 and d <= 21):
        return 'Sagittarius'
    if (m == 12 and d >= 22) or (m == 1 and d <= 19):
        return 'Capricorn'
    if (m == 1 and d >= 20) or (m == 2 and d <= 18):
        return 'Aquarius'
    return 'Pisces'


def _to_birth_data(profile: dict) -> dict:
    """Normalise le profil vers la structure attendue par daily_ritual.get_daily_insight."""
    bd = str(profile.get('birth_date') or '')
    bt = str(profile.get('birth_time') or '12:00')
    try:
        year, month, day = [int(x) for x in bd.split('-')]
    except Exception:
        year, month, day = 1990, 1, 1
    hour = 12
    minute = 0
    try:
        parts = bt.split(':')
        if len(parts) >= 2:
            hour = int(parts[0])
            minute = int(parts[1])
    except Exception:
        pass
    return {
        'name': profile.get('prenom') or 'Voyageur',
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'min': minute,
        'lat': float(profile.get('latitude') or 48.8566),
        'lon': float(profile.get('longitude') or 2.3522),
        'city': profile.get('birth_place') or 'Paris',
        'country_code': 'FR',
    }


def _build_daily_journal_email(first_name: str, daily: dict, plume_insight: str) -> tuple[str, str, str]:
    today_fr = datetime.now().strftime('%d/%m/%Y')
    subject = f"{first_name}, ton journal astrologique du {today_fr} ✦"
    preview = f"{daily.get('signe_fr', '')} · Horoscope du jour + Conseil de la Plume"

    love = (((daily.get('horoscope') or {}).get('amour')) or {})
    career = (((daily.get('horoscope') or {}).get('carriere')) or {})
    health = (((daily.get('horoscope') or {}).get('sante')) or {})

    body = (
        _h2(f"Ton journal du jour, {first_name}")
        + _p(f"Signe du jour : <strong>{daily.get('signe_fr', '')}</strong> ({daily.get('element', '')})")
        + f"""<div style=\"background:rgba(212,180,106,0.06);border:1px solid rgba(212,180,106,0.2);border-radius:14px;padding:20px;margin:20px 0;\">
<p style=\"margin:0 0 8px;font-size:10px;letter-spacing:0.2em;color:#D4B46A;text-transform:uppercase;\">Conseil de la Plume</p>
<p style=\"margin:0;font-size:16px;line-height:1.7;color:rgba(240,230,211,0.9);\">{plume_insight}</p>
</div>"""
        + f"""<div style=\"background:rgba(255,255,255,0.03);border:1px solid rgba(184,176,200,0.25);border-radius:14px;padding:20px;margin:0 0 16px;\">
<p style=\"margin:0 0 8px;font-size:10px;letter-spacing:0.2em;color:#A78BFA;text-transform:uppercase;\">Horoscope amour ({love.get('score', '-')}/10)</p>
<p style=\"margin:0;color:rgba(240,230,211,0.9);line-height:1.7;\">{love.get('texte', '')}</p>
</div>"""
        + f"""<div style=\"background:rgba(255,255,255,0.03);border:1px solid rgba(184,176,200,0.25);border-radius:14px;padding:20px;margin:0 0 16px;\">
<p style=\"margin:0 0 8px;font-size:10px;letter-spacing:0.2em;color:#A78BFA;text-transform:uppercase;\">Horoscope carrière ({career.get('score', '-')}/10)</p>
<p style=\"margin:0;color:rgba(240,230,211,0.9);line-height:1.7;\">{career.get('texte', '')}</p>
</div>"""
        + f"""<div style=\"background:rgba(255,255,255,0.03);border:1px solid rgba(184,176,200,0.25);border-radius:14px;padding:20px;margin:0 0 16px;\">
<p style=\"margin:0 0 8px;font-size:10px;letter-spacing:0.2em;color:#A78BFA;text-transform:uppercase;\">Horoscope santé ({health.get('score', '-')}/10)</p>
<p style=\"margin:0;color:rgba(240,230,211,0.9);line-height:1.7;\">{health.get('texte', '')}</p>
</div>"""
        + _p(f"Phrase du jour : <em>\"{daily.get('phrase_du_jour', '')}\"</em>")
        + _p(f"Couleur : <strong>{daily.get('couleur_du_jour', '-')}</strong> · Numéros chance : <strong>{', '.join(str(n) for n in (daily.get('numeros_chance') or []))}</strong>")
    )
    html = _wrap(body, preview)
    text = (
        f"Ton journal astrologique du {today_fr}\n"
        f"Signe: {daily.get('signe_fr', '')}\n\n"
        f"Conseil de la Plume: {plume_insight}\n\n"
        f"Amour ({love.get('score', '-')}/10): {love.get('texte', '')}\n"
        f"Carriere ({career.get('score', '-')}/10): {career.get('texte', '')}\n"
        f"Sante ({health.get('score', '-')}/10): {health.get('texte', '')}\n\n"
        f"Phrase du jour: {daily.get('phrase_du_jour', '')}\n"
    )
    return subject, html, text


async def send_daily_journal_for_profile(profile: dict, target_day: Optional[date] = None) -> bool:
    """Envoie le journal quotidien a un profil utilisateur (si donnees suffisantes)."""
    from services.daily_content import get_daily_content
    from services.daily_ritual import get_daily_insight

    email = (profile.get('email') or '').strip().lower()
    birth_date = str(profile.get('birth_date') or '').strip()
    user_id = profile.get('id')
    if not email or '@' not in email or not birth_date or not user_id:
        return False

    run_day = target_day or date.today()
    sign = _extract_sign_from_birth_date(birth_date)
    daily = get_daily_content(sign, run_day)
    birth_data = _to_birth_data(profile)
    insight_data = await get_daily_insight(str(user_id), birth_data=birth_data, mood=None)
    plume_insight = (insight_data or {}).get('insight') or daily.get('conseil_du_jour', '')

    first_name = profile.get('prenom') or 'Voyageur'
    subject, html, text = _build_daily_journal_email(first_name, daily, plume_insight)
    email_id = await send_email(
        email,
        subject,
        html.replace('{email}', email),
        text,
        from_email=DAILY_JOURNAL_SENDER_EMAIL,
    )
    return bool(email_id)


async def process_daily_journal_batch(limit: int = 250, target_day: Optional[date] = None) -> dict[str, Any]:
    """Envoie le journal du jour a tous les profils premium eligibles, 1 fois/jour max."""
    sb = get_admin_client()
    run_day = target_day or date.today()
    run_iso = run_day.isoformat()

    profiles_res = sb.table('profiles').select(
        'id,email,prenom,birth_date,birth_time,birth_place,birth_country,latitude,longitude,premium_status'
    ).eq('premium_status', 'active').limit(limit).execute()
    profiles = profiles_res.data or []

    eligible = [p for p in profiles if p.get('email') and p.get('birth_date')]
    if not eligible:
        return {'processed': len(profiles), 'eligible': 0, 'sent': 0, 'skipped': 0, 'failed': 0, 'date': run_iso}

    user_ids = [p.get('id') for p in eligible if p.get('id')]
    sent_today = set()
    if user_ids:
        try:
            sent_res = sb.table('daily_journal_email_logs').select('user_id').eq('send_date', run_iso).eq('status', 'sent').in_('user_id', user_ids).execute()
            sent_today = {row.get('user_id') for row in (sent_res.data or []) if row.get('user_id')}
        except Exception as e:
            logger.warning(f'[daily-journal] read log failed: {e}')

    sent = 0
    skipped = 0
    failed = 0

    for profile in eligible:
        user_id = profile.get('id')
        if user_id in sent_today:
            skipped += 1
            continue
        ok = False
        err_msg = None
        try:
            ok = await send_daily_journal_for_profile(profile, target_day=run_day)
        except Exception as e:
            ok = False
            err_msg = str(e)

        try:
            sb.table('daily_journal_email_logs').upsert({
                'user_id': user_id,
                'email': profile.get('email'),
                'send_date': run_iso,
                'status': 'sent' if ok else 'failed',
                'error': None if ok else (err_msg or 'send_failed'),
                'sent_at': datetime.now(timezone.utc).isoformat() if ok else None,
            }, on_conflict='user_id,send_date').execute()
        except Exception as e:
            logger.warning(f'[daily-journal] write log failed for {user_id}: {e}')

        if ok:
            sent += 1
        else:
            failed += 1

    return {
        'processed': len(profiles),
        'eligible': len(eligible),
        'sent': sent,
        'skipped': skipped,
        'failed': failed,
        'date': run_iso,
    }
