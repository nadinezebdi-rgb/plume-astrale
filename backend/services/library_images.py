"""
Helper centralisé pour charger les images de la bibliothèque Supabase Storage
(`bucket = library`) et les mettre en cache local pour ReportLab.

Usage :
    from services.library_images import sign, planet, house, tarot

    # ReportLab drawImage / Image() acceptent un chemin local :
    path = sign('aries', size=1080)                # → /app/backend/assets/library/signs/aries_1080.png
    c.drawImage(path, x, y, w, h, mask='auto')

Toutes les fonctions retournent le chemin local (téléchargé si absent) OU None
en cas d'erreur (les callers doivent gérer le None → skip image sans crash).
"""
from __future__ import annotations
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent / 'assets' / 'library'
_MANIFEST_PATH = _BASE_DIR / 'manifest_supabase.json'
_BUCKET_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library'

# Alias FR → slug bibliothèque
_SIGN_ALIASES = {
    'belier': 'aries', 'bélier': 'aries', 'aries': 'aries',
    'taureau': 'taurus', 'taurus': 'taurus',
    'gemeaux': 'gemini', 'gémeaux': 'gemini', 'gemini': 'gemini',
    'cancer': 'cancer',
    'lion': 'leo', 'leo': 'leo',
    'vierge': 'virgo', 'virgo': 'virgo',
    'balance': 'libra', 'libra': 'libra',
    'scorpion': 'scorpio', 'scorpio': 'scorpio',
    'sagittaire': 'sagittarius', 'sagittarius': 'sagittarius',
    'capricorne': 'capricorn', 'capricorn': 'capricorn',
    'verseau': 'aquarius', 'aquarius': 'aquarius',
    'poissons': 'pisces', 'pisces': 'pisces',
}

_PLANET_ALIASES = {
    'soleil': 'sun', 'sun': 'sun',
    'lune': 'moon', 'moon': 'moon',
    'mercure': 'mercury', 'mercury': 'mercury',
    'venus': 'venus', 'vénus': 'venus',
    'mars': 'mars',
    'jupiter': 'jupiter',
    'saturne': 'saturn', 'saturn': 'saturn',
    'uranus': 'uranus',
    'neptune': 'neptune',
    'pluton': 'pluto', 'pluto': 'pluto',
}

# Slug tarot → clé bibliothèque (les 22 arcanes majeurs)
_TAROT_ALIASES = {
    'mat': '00_le_mat', 'fou': '00_le_mat',
    'bateleur': '01_le_bateleur', 'magicien': '01_le_bateleur',
    'papesse': '02_la_papesse',
    'imperatrice': '03_l_imperatrice', 'impératrice': '03_l_imperatrice',
    'empereur': '04_l_empereur',
    'pape': '05_le_pape', 'hierophante': '05_le_pape',
    'amoureux': '06_les_amoureux',
    'chariot': '07_le_chariot',
    'force': '08_la_force', 'justice': '11_la_justice',
    'hermite': '09_l_hermite', 'ermite': '09_l_hermite',
    'roue': '10_la_roue_de_fortune', 'roue_fortune': '10_la_roue_de_fortune',
    'pendu': '12_le_pendu',
    'mort': '13_la_mort', 'sans_nom': '13_la_mort',
    'temperance': '14_la_temperance', 'tempérance': '14_la_temperance',
    'diable': '15_le_diable',
    'maison_dieu': '16_la_maison_dieu', 'tour': '16_la_maison_dieu',
    'etoile': '17_l_etoile', 'étoile': '17_l_etoile',
    'lune': '18_la_lune',
    'soleil': '19_le_soleil',
    'jugement': '20_le_jugement',
    'monde': '21_le_monde',
}


def _normalize(s: str) -> str:
    import unicodedata
    # Retire les accents (é → e, ç → c, etc.)
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9_]', '', s.lower().strip().replace(' ', '_').replace('-', '_'))


def _download(remote_url: str, local_path: Path) -> bool:
    """Télécharge un fichier vers local_path. Retourne True si succès."""
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with httpx.stream('GET', remote_url, timeout=20, follow_redirects=True) as r:
            if r.status_code != 200:
                logger.warning(f'[library_images] {remote_url} → HTTP {r.status_code}')
                return False
            with open(local_path, 'wb') as f:
                for chunk in r.iter_bytes(chunk_size=32768):
                    f.write(chunk)
        return True
    except Exception as e:
        logger.warning(f'[library_images] download failed {remote_url}: {e}')
        return False


def _resolve(category: str, slug: str, size: int = 1080) -> Optional[str]:
    """Retourne un chemin local vers l'image (téléchargé si nécessaire).
    Retourne None si l'image n'existe pas dans le manifest."""
    filename = f'{slug}_{size}.png'
    key = f'{category}/{filename}'
    local_path = _BASE_DIR / category / filename

    if local_path.exists() and local_path.stat().st_size > 0:
        return str(local_path)

    # Vérifier le manifest si dispo
    remote_url = None
    try:
        if _MANIFEST_PATH.exists():
            with open(_MANIFEST_PATH) as f:
                mf = json.load(f)
            remote_url = (mf.get('files') or {}).get(key)
    except Exception as e:
        logger.debug(f'[library_images] manifest read error: {e}')

    if not remote_url:
        # Fallback : URL directe (construite depuis _BUCKET_URL)
        remote_url = f'{_BUCKET_URL}/{key}'

    if _download(remote_url, local_path):
        return str(local_path)
    return None


# ─────────────────────────────────────────────────────────────
# API publique
# ─────────────────────────────────────────────────────────────

def sign(name: str, size: int = 1080) -> Optional[str]:
    """Image d'un signe zodiacal. Accepte FR/EN. Ex: sign('bélier') → aries_1080.png"""
    slug = _SIGN_ALIASES.get(_normalize(name))
    if not slug:
        return None
    return _resolve('signs', slug, size)


def planet(name: str, size: int = 1080) -> Optional[str]:
    """Image d'une planète. Accepte FR/EN. Ex: planet('vénus') → venus_1080.png"""
    slug = _PLANET_ALIASES.get(_normalize(name))
    if not slug:
        return None
    return _resolve('planets', slug, size)


def house(n: int, size: int = 1080) -> Optional[str]:
    """Image d'une maison astrologique (1-12)."""
    if not (1 <= int(n) <= 12):
        return None
    return _resolve('houses', f'house{int(n)}', size)


def tarot(name: str, size: int = 1080) -> Optional[str]:
    """Image d'un arcane majeur. Accepte 'amoureux', '06_les_amoureux', 'étoile', etc."""
    norm = _normalize(name)
    # Direct slug (déjà au format 06_les_amoureux)
    if re.match(r'^\d{2}_', norm):
        return _resolve('tarot', norm, size)
    slug = _TAROT_ALIASES.get(norm)
    if not slug:
        return None
    return _resolve('tarot', slug, size)


def style_ref(name: str) -> Optional[str]:
    """Références de style (wheel_ref, flowers_ref, cancer_ref) — taille unique."""
    slug = _normalize(name)
    if not slug.endswith('_ref'):
        slug = f'{slug}_ref'
    # style-refs n'a qu'une taille (pas de suffixe)
    filename = f'{slug}.png'
    local_path = _BASE_DIR / 'style-refs' / filename
    if local_path.exists() and local_path.stat().st_size > 0:
        return str(local_path)
    remote = f'{_BUCKET_URL}/style-refs/{filename}'
    if _download(remote, local_path):
        return str(local_path)
    return None


# ─────────────────────────────────────────────────────────────
# Utilitaires métier
# ─────────────────────────────────────────────────────────────

# Bornes des signes tropicaux (mois, jour_début inclus)
_ZODIAC_BOUNDS = [
    ('capricorn', (12, 22)), ('aquarius', (1, 20)), ('pisces', (2, 19)),
    ('aries', (3, 21)), ('taurus', (4, 20)), ('gemini', (5, 21)),
    ('cancer', (6, 21)), ('leo', (7, 23)), ('virgo', (8, 23)),
    ('libra', (9, 23)), ('scorpio', (10, 23)), ('sagittarius', (11, 22)),
    ('capricorn', (12, 22)),
]


def sun_slug_from_date(birth_iso: str) -> Optional[str]:
    """Retourne le slug EN du signe solaire à partir d'une date ISO 'YYYY-MM-DD'."""
    if not birth_iso or len(birth_iso) < 10:
        return None
    try:
        m = int(birth_iso[5:7])
        d = int(birth_iso[8:10])
    except Exception:
        return None
    # Trouver le signe : (mois, jour) >= borne signe
    current = 'capricorn'
    for slug, (bm, bd) in _ZODIAC_BOUNDS:
        if (m, d) >= (bm, bd):
            current = slug
    return current


def sign_from_date(birth_iso: str, size: int = 1080) -> Optional[str]:
    """Raccourci : image du signe solaire à partir d'une date ISO."""
    slug = sun_slug_from_date(birth_iso)
    if not slug:
        return None
    return _resolve('signs', slug, size)
