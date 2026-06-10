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
    """Tirage deterministe base sur prenom+date pour ce jour donne."""
    today = datetime.now().strftime('%Y-%m-%d')
    seed = hash(f"{first_name}|{birth_date}|{today}") % 22
    return _TAROT_22[abs(seed)]


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
    """Enregistre l'email dans la table oracle_leads pour la sequence mail."""
    email = (payload.email or '').strip().lower()
    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail='Email invalide')

    try:
        sb = get_admin_client()
        sb.table('oracle_leads').upsert({
            'email': email,
            'first_name': (payload.first_name or '').strip()[:80] or None,
            'birth_date': payload.birth_date or None,
            'source': 'hero_oracle',
        }, on_conflict='email').execute()
    except Exception as e:
        # Table peut ne pas exister encore - log mais on ne casse pas le funnel
        print(f'[oracle.capture] {e}')

    return {'success': True, 'email': email}
