"""Tunnel d'acquisition Hero Oracle.
Endpoints publics (sans auth) pour generer un teaser de lecture astro+numero+tarot
des l'arrivee sur la home page, sans inscription requise.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random
import os

from services import astrology_io_service as aio
from services.numerology_service import chemin_de_vie as _chemin_de_vie_iso
from services.supabase_client import get_admin_client


def calculate_chemin_de_vie(year: int, month: int, day: int) -> int:
    """Wrapper accept (year, month, day)."""
    return _chemin_de_vie_iso(f"{year:04d}-{month:02d}-{day:02d}")


router = APIRouter(prefix='/oracle', tags=['oracle'])


# ─── Schemas ──────────────────────────────────────────────────────

class TeaserRequest(BaseModel):
    first_name: str
    birth_date: str  # YYYY-MM-DD


class EmailCaptureRequest(BaseModel):
    email: str
    first_name: Optional[str] = None
    birth_date: Optional[str] = None


# ─── Helpers ──────────────────────────────────────────────────────

_LIFE_PATH_ARCHETYPES = {
    1: "L'Initiateur", 2: "Le Diplomate", 3: "L'Artiste", 4: "Le Bâtisseur",
    5: "L'Aventurier", 6: "Le Gardien", 7: "Le Chercheur", 8: "Le Stratège",
    9: "L'Humaniste",
    11: "L'Inspiré (Maître)", 22: "Le Visionnaire (Maître)", 33: "Le Guérisseur (Maître)",
}


def _moon_phase_simple(date_str: str) -> dict:
    """Phase lunaire approximative (sans API) pour le jour d'aujourd'hui.
    Source : algorithme de John Conway, suffisant pour un teaser."""
    today = datetime.now()
    # Reference : nouvelle lune du 6 janvier 2000 (Conway)
    diff_days = (today - datetime(2000, 1, 6)).days
    cycle = 29.530588853
    age = diff_days % cycle
    if age < 1.84566:
        phase = 'Nouvelle Lune'
    elif age < 5.53699:
        phase = 'Premier croissant'
    elif age < 9.22831:
        phase = 'Premier quartier'
    elif age < 12.91963:
        phase = 'Lune gibbeuse croissante'
    elif age < 16.61096:
        phase = 'Pleine Lune'
    elif age < 20.30228:
        phase = 'Lune gibbeuse décroissante'
    elif age < 23.99361:
        phase = 'Dernier quartier'
    elif age < 27.68493:
        phase = 'Dernier croissant'
    else:
        phase = 'Nouvelle Lune'

    messages = {
        'Nouvelle Lune': "Le moment d'initier, de planter une intention nouvelle.",
        'Premier croissant': "Tes énergies montent doucement. Affirme tes choix.",
        'Premier quartier': "Le moment d'oser. Une décision importante s'invite.",
        'Lune gibbeuse croissante': "Ajuste ton cap. Tout n'a pas besoin d'être parfait.",
        'Pleine Lune': "Les vérités émergent. Accueille ce qui veut être vu.",
        'Lune gibbeuse décroissante': "Le moment de partager ce que tu as appris.",
        'Dernier quartier': "Une page se tourne. Lâche ce qui pèse.",
        'Dernier croissant': "Repose-toi. Le silence te prépare au prochain souffle.",
    }
    return {'phase': phase, 'message': messages.get(phase, '')}


_TAROT_22 = [
    {'name': 'Le Bateleur', 'answer': "Oui — c'est le moment d'initier."},
    {'name': 'La Papesse', 'answer': "Patience — la réponse arrive par l'intuition."},
    {'name': "L'Impératrice", 'answer': "Oui — l'abondance s'aligne pour toi."},
    {'name': "L'Empereur", 'answer': "Oui — pose des fondations solides."},
    {'name': 'Le Pape', 'answer': "Cherche conseil — un guide s'invite."},
    {'name': "L'Amoureux", 'answer': "Choisis avec ton cœur — il sait."},
    {'name': 'Le Chariot', 'answer': "Oui — avance, la victoire est en marche."},
    {'name': 'La Justice', 'answer': "Sois honnête — l'équilibre revient."},
    {'name': "L'Hermite", 'answer': "Recule, médite — la réponse vient du silence."},
    {'name': 'La Roue de Fortune', 'answer': "Ça tourne — accueille le changement."},
    {'name': 'La Force', 'answer': "Oui — avec douceur tu obtiens tout."},
    {'name': 'Le Pendu', 'answer': "Pas encore — change d'angle de vue."},
    {'name': "L'Arcane sans Nom", 'answer': "Quelque chose meurt pour qu'autre chose naisse."},
    {'name': 'Tempérance', 'answer': "Trouve la juste mesure — oui en douceur."},
    {'name': 'Le Diable', 'answer': "Vigilance — identifie ce qui te lie."},
    {'name': 'La Maison Dieu', 'answer': "Une vérité éclate — accueille-la."},
    {'name': "L'Étoile", 'answer': "Oui — fais confiance, ton étoile veille."},
    {'name': 'La Lune', 'answer': "Doute — distingue rêve et réalité."},
    {'name': 'Le Soleil', 'answer': "Oui — la joie te guide, célèbre."},
    {'name': 'Le Jugement', 'answer': "Oui — un appel te traverse, écoute."},
    {'name': 'Le Monde', 'answer': "Oui — une boucle se complète, savoure."},
    {'name': 'Le Mat', 'answer': "Saute — l'inconnu te bénit."},
]


def _tarot_oui_non(first_name: str, birth_date: str) -> dict:
    """Tirage deterministe base sur prenom+date pour ce jour donne.
    Utilise sha256 pour rester stable apres redemarrage du backend (PYTHONHASHSEED-safe)."""
    import hashlib
    today = datetime.now().strftime('%Y-%m-%d')
    seed_str = f"{first_name.lower()}|{birth_date}|{today}"
    h = hashlib.sha256(seed_str.encode('utf-8')).hexdigest()
    idx = int(h[:8], 16) % len(_TAROT_22)
    return _TAROT_22[idx]


def _wheel_url_attempt(birth_date: str) -> Optional[str]:
    """Tente de generer une URL de natal_wheel_chart via astrology-api.io (sans heure precise = midi UTC)."""
    # Pour l'instant on retourne None ; on pourra brancher /api/v3/charts/natal/svg plus tard
    return None


# ─── Endpoints ─────────────────────────────────────────────────────

@router.post('/teaser')
async def oracle_teaser(payload: TeaserRequest):
    """Genere une lecture teaser sans creation de compte.
    Retourne : chemin de vie, phase lunaire, tarot oui/non, URL wheel (si dispo)."""
    if not payload.first_name.strip():
        raise HTTPException(status_code=400, detail='Prenom requis')
    try:
        d = datetime.strptime(payload.birth_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail='Format date invalide (YYYY-MM-DD)')

    # Chemin de vie
    try:
        nb = calculate_chemin_de_vie(d.year, d.month, d.day)
    except Exception:
        nb = sum(int(c) for c in payload.birth_date.replace('-', ''))
        while nb > 9 and nb not in (11, 22, 33):
            nb = sum(int(c) for c in str(nb))

    lifepath = {
        'number': nb,
        'archetype': _LIFE_PATH_ARCHETYPES.get(nb, "L'Âme libre"),
    }

    moon = _moon_phase_simple(payload.birth_date)
    tarot = _tarot_oui_non(payload.first_name, payload.birth_date)
    wheel_url = _wheel_url_attempt(payload.birth_date)

    locked_preview = (
        f"{payload.first_name}, dans la lumière de cette phase lunaire, "
        "ton chemin de vie révèle un appel particulier... Reçois ta lecture complète, "
        "le mantra du jour et le rituel à poser ce matin par email."
    )

    return {
        'success': True,
        'first_name': payload.first_name,
        'lifepath': lifepath,
        'moon_phase': moon,
        'tarot': {'card_name': tarot['name'], 'answer': tarot['answer']},
        'wheel_url': wheel_url,
        'locked_preview': locked_preview,
    }


@router.post('/capture-email')
async def oracle_capture_email(payload: EmailCaptureRequest):
    """Enregistre l'email dans la table oracle_leads pour la sequence mail
    ET envoie immediatement E1 (livraison teaser) via Resend."""
    email = (payload.email or '').strip().lower()
    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail='Email invalide')

    first_name = (payload.first_name or '').strip()[:80] or 'Voyageur'
    birth_date = payload.birth_date

    # 1) Upsert en base
    try:
        sb = get_admin_client()
        sb.table('oracle_leads').upsert({
            'email': email,
            'first_name': first_name if first_name != 'Voyageur' else None,
            'birth_date': birth_date,
            'source': 'hero_oracle',
        }, on_conflict='email').execute()
    except Exception as e:
        print(f'[oracle.capture] supabase upsert: {e}')

    # 2) Calcul du teaser pour l'inclure dans l'email
    lifepath_data = {'number': 0, 'archetype': "L'Âme libre"}
    moon_data = {'phase': '', 'message': ''}
    tarot_data = {'card_name': '', 'answer': ''}
    if birth_date:
        try:
            d = datetime.strptime(birth_date, '%Y-%m-%d')
            nb = calculate_chemin_de_vie(d.year, d.month, d.day)
            lifepath_data = {
                'number': nb,
                'archetype': _LIFE_PATH_ARCHETYPES.get(nb, "L'Âme libre"),
            }
            moon_data = _moon_phase_simple(birth_date)
            t = _tarot_oui_non(first_name, birth_date)
            tarot_data = {'card_name': t['name'], 'answer': t['answer']}
        except Exception as e:
            print(f'[oracle.capture] teaser recompute: {e}')

    # 3) Envoi E1 (Resend) en arriere-plan
    try:
        from services.resend_service import send_e1_teaser_now
        await send_e1_teaser_now(email, first_name, lifepath_data, moon_data, tarot_data)
    except Exception as e:
        print(f'[oracle.capture] resend E1: {e}')

    return {'success': True, 'email': email}


@router.post('/run-sequence')
async def oracle_run_sequence():
    """Endpoint declenche par un cron externe (Vercel cron, Railway cron, ou GitHub Actions).
    Parcourt tous les leads non-desabonnes et envoie l'email suivant si la date est atteinte.
    Idempotent : ne renvoie pas un email deja envoye.
    """
    try:
        from services.resend_service import process_sequence_step
        sb = get_admin_client()
        # On limite a 200 leads par run pour eviter les surcharges
        res = sb.table('oracle_leads').select('*')\
            .is_('unsubscribed_at', 'null')\
            .lt('email_sequence_step', 6)\
            .limit(200)\
            .execute()
        leads = res.data or []
        sent = 0
        for lead in leads:
            try:
                new_step = await process_sequence_step(lead)
                if new_step > 0:
                    sent += 1
            except Exception as e:
                print(f'[oracle.run-sequence] lead {lead.get("email")}: {e}')
        return {'success': True, 'processed': len(leads), 'sent': sent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Sequence error: {e}')


@router.get('/unsubscribe')
async def oracle_unsubscribe(email: str):
    """Lien direct de desabonnement (cliquable depuis chaque email)."""
    try:
        from datetime import datetime as _dt, timezone as _tz
        sb = get_admin_client()
        sb.table('oracle_leads').update({
            'unsubscribed_at': _dt.now(_tz.utc).isoformat(),
            'consent_marketing': False,
        }).eq('email', email.strip().lower()).execute()
        return {'success': True, 'message': "Vous êtes désabonné(e). À bientôt 🌙"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
