"""Service de parrainage — génération de code, rattachement, récompense.

Un utilisateur partage `plume-astrale.fr/?ref=CODE`. Un filleul crée son compte,
le frontend appelle `POST /api/referral/attach` avec ce code : le filleul est
lié à son parrain via `profiles.referred_by`.

À la première conversion payante du filleul (webhook Stripe), on crée une entrée
`referrals` et on envoie au parrain un horoscope PDF gratuit de son signe.
"""
from __future__ import annotations
import logging
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# Alphabet base32 sans caractères ambigus (0/O, 1/I, L)
_ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


def _generate_code(length: int = 8) -> str:
    """Code de 8 caractères type 'A7X2QH9P' — 30^8 ≈ 6.5 * 10^11 combinaisons."""
    return ''.join(secrets.choice(_ALPHABET) for _ in range(length))


def _sign_from_date(date_str: str) -> Optional[str]:
    """FR sign key matching /marketing/horoscopes/horoscope_journalier_{sign}.pdf."""
    if not date_str:
        return None
    try:
        d = datetime.strptime(date_str[:10], '%Y-%m-%d')
    except Exception:
        return None
    m, day = d.month, d.day
    if (m == 3 and day >= 21) or (m == 4 and day <= 19): return 'belier'
    if (m == 4 and day >= 20) or (m == 5 and day <= 20): return 'taureau'
    if (m == 5 and day >= 21) or (m == 6 and day <= 20): return 'gemeaux'
    if (m == 6 and day >= 21) or (m == 7 and day <= 22): return 'cancer'
    if (m == 7 and day >= 23) or (m == 8 and day <= 22): return 'lion'
    if (m == 8 and day >= 23) or (m == 9 and day <= 22): return 'vierge'
    if (m == 9 and day >= 23) or (m == 10 and day <= 22): return 'balance'
    if (m == 10 and day >= 23) or (m == 11 and day <= 21): return 'scorpion'
    if (m == 11 and day >= 22) or (m == 12 and day <= 21): return 'sagittaire'
    if (m == 12 and day >= 22) or (m == 1 and day <= 19): return 'capricorne'
    if (m == 1 and day >= 20) or (m == 2 and day <= 18): return 'verseau'
    return 'poissons'


_SIGN_LABEL_FR = {
    'belier': 'Bélier', 'taureau': 'Taureau', 'gemeaux': 'Gémeaux',
    'cancer': 'Cancer', 'lion': 'Lion', 'vierge': 'Vierge',
    'balance': 'Balance', 'scorpion': 'Scorpion', 'sagittaire': 'Sagittaire',
    'capricorne': 'Capricorne', 'verseau': 'Verseau', 'poissons': 'Poissons',
}


async def ensure_referral_code(user_id: str) -> str:
    """Retourne le code parrainage du user, en le générant si absent (avec retry sur collision).
    Si la colonne n'existe pas (migration pas encore appliquée), renvoie un code dérivé de l'user_id."""
    sb = get_admin_client()
    try:
        r = sb.table('profiles').select('referral_code').eq('id', user_id).maybe_single().execute()
    except Exception as e:
        msg = str(e).lower()
        if 'does not exist' in msg or '42703' in msg or 'referral_code' in msg:
            logger.warning('[referral] migration non appliquée — fallback code dérivé')
            return user_id.replace('-', '')[:8].upper()
        raise
    if r and r.data and r.data.get('referral_code'):
        return r.data['referral_code']
    # Génère + upsert avec retry sur collision unique
    for _ in range(6):
        code = _generate_code(8)
        try:
            sb.table('profiles').update({'referral_code': code}).eq('id', user_id).execute()
            return code
        except Exception as e:
            msg = str(e).lower()
            if 'unique' in msg or 'duplicate' in msg or '23505' in msg:
                continue
            logger.warning(f'[referral] update code failed: {e}')
            break
    # Fallback catastrophique : préfixe user_id (déjà unique)
    return user_id.replace('-', '')[:8].upper()


async def get_stats(user_id: str) -> Dict[str, Any]:
    """Retourne { code, invited_count, purchased_count, rewards_earned, referrals: [...] }.
    Résilient si la table referrals n'existe pas encore (migration pas appliquée)."""
    code = await ensure_referral_code(user_id)
    sb = get_admin_client()
    invited_count = 0
    rows: list = []
    try:
        invited = sb.table('profiles').select('id', count='exact').eq('referred_by', user_id).execute()
        invited_count = invited.count or 0
    except Exception as e:
        if 'does not exist' not in str(e).lower():
            logger.warning(f'[referral] invited count fail: {e}')
    try:
        refs = sb.table('referrals').select(
            'id, referred_user_id, first_purchase_at, first_purchase_amount_cents, reward_sent_at, reward_horoscope_sign'
        ).eq('referrer_id', user_id).order('created_at', desc=True).execute()
        rows = refs.data or []
    except Exception as e:
        if 'does not exist' not in str(e).lower():
            logger.warning(f'[referral] referrals fetch fail: {e}')
    purchased_count = sum(1 for r in rows if r.get('first_purchase_at'))
    rewards_earned = sum(1 for r in rows if r.get('reward_sent_at'))
    return {
        'code': code,
        'invited_count': invited_count,
        'purchased_count': purchased_count,
        'rewards_earned': rewards_earned,
        'referrals': rows,
    }


async def attach_referrer(user_id: str, code: str) -> Dict[str, Any]:
    """Lie un filleul (user_id) à son parrain via le code partagé.
    Refuse si : code inconnu, code = son propre code, ou filleul déjà rattaché.
    Renvoie { ok: false, error: 'migration_pending' } si la colonne referred_by n'existe pas."""
    code = (code or '').strip().upper()
    if not code:
        return {'ok': False, 'error': 'code vide'}
    sb = get_admin_client()
    try:
        me = sb.table('profiles').select('id, referral_code, referred_by').eq('id', user_id).maybe_single().execute()
    except Exception as e:
        if 'does not exist' in str(e).lower() or '42703' in str(e):
            return {'ok': False, 'error': 'migration_pending'}
        raise
    if not me or not me.data:
        return {'ok': False, 'error': 'profil introuvable'}
    if me.data.get('referred_by'):
        return {'ok': False, 'error': 'déjà rattaché'}
    if me.data.get('referral_code') == code:
        return {'ok': False, 'error': 'code perso interdit'}
    ref = sb.table('profiles').select('id').eq('referral_code', code).maybe_single().execute()
    if not ref or not ref.data:
        return {'ok': False, 'error': 'code invalide'}
    referrer_id = ref.data['id']
    if referrer_id == user_id:
        return {'ok': False, 'error': 'code perso interdit'}
    sb.table('profiles').update({'referred_by': referrer_id}).eq('id', user_id).execute()
    logger.info(f'[referral] user {user_id} rattaché à parrain {referrer_id}')
    return {'ok': True, 'referrer_id': referrer_id}


async def maybe_reward_on_purchase(
    referred_user_id: str,
    session_id: Optional[str],
    amount_cents: Optional[int],
) -> None:
    """Appelé depuis le webhook Stripe après un paiement confirmé.
    Si le user a un parrain et pas encore de conversion enregistrée → crée l'entrée
    referrals + envoie l'email récompense au parrain (best-effort)."""
    try:
        sb = get_admin_client()
        try:
            prof = sb.table('profiles').select('id, referred_by').eq('id', referred_user_id).maybe_single().execute()
        except Exception as e:
            if 'does not exist' in str(e).lower():
                return  # migration pas appliquée : silence
            raise
        if not prof or not prof.data or not prof.data.get('referred_by'):
            return
        referrer_id = prof.data['referred_by']

        # Idempotence : un filleul → une seule entrée referrals (unique referred_user_id)
        existing = sb.table('referrals').select('id, first_purchase_at, reward_sent_at').eq('referred_user_id', referred_user_id).maybe_single().execute()
        if existing and existing.data and existing.data.get('first_purchase_at'):
            return  # déjà comptabilisé, pas de double reward

        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            'referrer_id': referrer_id,
            'referred_user_id': referred_user_id,
            'first_purchase_session_id': session_id,
            'first_purchase_amount_cents': amount_cents,
            'first_purchase_at': now_iso,
        }
        if existing and existing.data:
            sb.table('referrals').update(payload).eq('id', existing.data['id']).execute()
            ref_row_id = existing.data['id']
        else:
            ins = sb.table('referrals').insert(payload).execute()
            ref_row_id = (ins.data or [{}])[0].get('id')

        # Envoi email récompense au parrain
        await _send_reward_email(referrer_id, ref_row_id)
    except Exception as e:
        logger.warning(f'[referral] reward flow fail user={referred_user_id}: {e}')


async def _send_reward_email(referrer_id: str, referral_row_id: Optional[str]) -> None:
    """Envoie au parrain le lien vers son horoscope PDF gratuit + met à jour referrals."""
    from services.resend_service import send_email
    sb = get_admin_client()
    p = sb.table('profiles').select('email, prenom, birth_date').eq('id', referrer_id).maybe_single().execute()
    if not p or not p.data or not p.data.get('email'):
        logger.warning(f'[referral] parrain {referrer_id} sans email — reward non envoyée')
        return
    email = p.data['email']
    prenom = p.data.get('prenom') or 'Voyageur'
    sign_key = _sign_from_date(p.data.get('birth_date') or '') or 'belier'
    sign_label = _SIGN_LABEL_FR.get(sign_key, 'Bélier')

    # URL publique du PDF (servi statiquement par le frontend)
    pdf_url = f'https://plume-astrale.fr/marketing/horoscopes/horoscope_journalier_{sign_key}.pdf'
    account_url = 'https://plume-astrale.fr/mon-compte'

    subject = f'🌙 {prenom}, ton filleul a franchi le pas — ton horoscope {sign_label} t\'attend'
    html = f'''
    <div style="font-family: Georgia, serif; max-width: 560px; margin: 0 auto; padding: 32px 24px; background: #0B0B1F; color: #F5EEE0;">
      <p style="letter-spacing: 0.35em; color: #D4AF37; font-size: 11px; text-transform: uppercase; margin: 0 0 16px;">✦ Merci de ta lumière ✦</p>
      <h1 style="font-family: Georgia, serif; font-weight: 300; font-size: 32px; line-height: 1.15; color: #F5EEE0; margin: 0 0 20px;">
        Ton parrainage a porté ses fruits, {prenom}.
      </h1>
      <p style="color: rgba(227,215,255,0.85); font-size: 16px; line-height: 1.65; margin: 0 0 20px;">
        Un filleul que tu as invité vient d'acheter son premier accompagnement Plume Astrale. En remerciement,
        voici l'<strong style="color:#D4AF37;">horoscope journalier {sign_label}</strong> que Soléna a préparé pour toi.
      </p>
      <div style="text-align:center; margin: 32px 0;">
        <a href="{pdf_url}" style="display:inline-block; padding: 16px 34px; background: linear-gradient(135deg, #D4AF37 0%, #E8C766 100%); color: #0B0B1F; font-weight: 500; text-decoration:none; border-radius: 999px; letter-spacing: 0.12em; text-transform: uppercase; font-size: 13px;">
          Télécharger mon horoscope
        </a>
      </div>
      <p style="color: rgba(227,215,255,0.65); font-size: 14px; line-height: 1.6; margin: 24px 0 0; font-style: italic;">
        Continue de partager ton lien — chaque filleul qui commande son premier PDF t'offre un nouvel horoscope
        du jour. Retrouve ton lien de parrainage sur <a href="{account_url}" style="color:#D4AF37;">ton espace</a>.
      </p>
      <p style="color: rgba(227,215,255,0.4); font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; margin: 36px 0 0; text-align:center;">
        Plume Astrale · plume-astrale.fr
      </p>
    </div>
    '''
    text = (
        f'Merci {prenom} — un filleul vient de faire son premier achat sur Plume Astrale.\n'
        f'Ton cadeau : l\'horoscope journalier {sign_label}.\n'
        f'Télécharge-le ici : {pdf_url}\n\n'
        f'Ton espace : {account_url}\n— Plume Astrale'
    )
    eid = await send_email(email, subject, html, text)
    if eid and referral_row_id:
        try:
            sb.table('referrals').update({
                'reward_sent_at': datetime.now(timezone.utc).isoformat(),
                'reward_horoscope_sign': sign_key,
                'reward_email_id': eid,
            }).eq('id', referral_row_id).execute()
        except Exception as e:
            logger.warning(f'[referral] mark rewarded fail: {e}')
    logger.info(f'[referral] reward email → parrain {referrer_id} ({email}) sign={sign_key} eid={eid}')
