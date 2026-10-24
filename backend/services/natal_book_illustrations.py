"""natal_book_illustrations — Illustrations IA (Nano Banana / Gemini Image)
pour les pages pleines du livre natal Plume Astrale.

Deux usages dans le livre :
  1. **Ex Libris** — une illustration unique par signature astrale (Soleil +
     Lune + Ascendant + prénom). Mise en cache déterministe par hash, re-
     servie pour chaque régénération du PDF sans ré-appeler le modèle.
  2. **Vignettes de fin de chapitre planétaire** — une illustration par
     planète du socle (Soleil, Lune, Mercure, Vénus, Mars, Jupiter, Saturne,
     Uranus, Neptune, Pluton). Cache générique partagé entre tous les
     utilisateurs (coût amorti).

Toutes les générations utilisent `EMERGENT_LLM_KEY` + `emergentintegrations`
avec le modèle `gemini-2.5-flash-image-preview` (Nano Banana).
"""
from __future__ import annotations
import asyncio
import base64
import hashlib
import logging
import os
import re
import unicodedata
from pathlib import Path
from typing import Optional

from .emergent_storage import get_object as storage_get, put_object as storage_put

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
# Fast local tier (ephemeral — survives request bursts, not container restarts)
EX_LIBRIS_CACHE = ROOT / 'cache' / 'natal_illustrations' / 'ex_libris'
PLANET_CACHE = ROOT / 'cache' / 'natal_illustrations' / 'planets'
EX_LIBRIS_CACHE.mkdir(parents=True, exist_ok=True)
PLANET_CACHE.mkdir(parents=True, exist_ok=True)

# Persistent tier — Emergent Object Storage prefix
_STORAGE_PREFIX = 'plume-astrale/natal-illustrations'

_NANO_BANANA_MODEL = 'gemini-3.1-flash-image-preview'


async def _read_cached(local_file: Path, remote_path: str) -> Optional[bytes]:
    """Two-tier cache read: local disk → remote storage. Backfills local on hit."""
    if local_file.exists():
        try:
            data = local_file.read_bytes()
            if data:
                return data
        except Exception:
            pass
    remote = await storage_get(remote_path)
    if remote:
        try:
            local_file.write_bytes(remote)
        except Exception:
            pass
        return remote
    return None


async def _write_cached(local_file: Path, remote_path: str, data: bytes) -> None:
    """Two-tier cache write: local disk + remote storage (best effort)."""
    try:
        local_file.write_bytes(data)
    except Exception as e:
        logger.warning(f'[natal_illust] local write fail: {e}')
    uploaded = await storage_put(remote_path, data, content_type='image/jpeg')
    if uploaded:
        logger.info(f'[natal_illust] persisted to emergent storage: {remote_path}')

# Palette normative livre Plume Astrale (parchemin + encre + or)
_STYLE_CONSTRAINTS = (
    "Style : illustration éditoriale fine, à la plume et aquarelle légère, "
    "palette strictement limitée au parchemin crème (#F7F2E6), encre (#243047) "
    "et or Hermès (#A78140). Aucun texte, aucune lettre, aucun chiffre. "
    "Fond crème clair, lignes nettes, cadrage centré, "
    "composition verticale A5, respiration généreuse. "
    "Pas de signature, pas de watermark, pas de logo."
)


def _slug(value: str) -> str:
    """Normalise un signe/prénom pour clé de cache stable."""
    v = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '', v.lower())


def _signature_hash(prenom: str, sun: str, moon: str, asc: str) -> str:
    """Clé de cache déterministe pour une signature astrale complète."""
    key = f'{_slug(prenom)}|{_slug(sun)}|{_slug(moon)}|{_slug(asc)}'
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]


async def _generate_image_bytes(prompt: str, session_id: str) -> Optional[bytes]:
    """Appel Nano Banana → PNG bytes compressés. Renvoie None en cas d'échec.

    Nano Banana retourne de grosses PNG (~700 Ko) ; on les ré-encode en PNG
    compressé 600×600 (optimize=True) pour maintenir un PDF ≤ 10 Mo.
    """
    api_key = os.getenv('EMERGENT_LLM_KEY')
    if not api_key:
        logger.warning('[natal_illust] EMERGENT_LLM_KEY absente')
        return None
    try:
        # Import local pour éviter de charger emergentintegrations si inutile
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = (
            LlmChat(api_key=api_key, session_id=session_id,
                    system_message='You generate single refined editorial illustrations.')
            .with_model('gemini', _NANO_BANANA_MODEL)
            .with_params(modalities=['image', 'text'])
        )
        msg = UserMessage(text=prompt)
        _text, images = await chat.send_message_multimodal_response(msg)
        if not images:
            logger.warning(f'[natal_illust] no image returned for session {session_id}')
            return None
        img0 = images[0]
        data_b64 = img0.get('data') or ''
        if not data_b64:
            return None
        raw = base64.b64decode(data_b64)
        return _compress_png(raw)
    except Exception as e:
        logger.warning(f'[natal_illust] generation failed ({session_id}): {e}')
        return None


def _compress_png(raw: bytes, max_side: int = 600) -> bytes:
    """Compresse l'illustration : redimensionne + sortie JPEG qualité 85.

    Les illustrations éditoriales n'ont pas besoin de transparence ; JPEG
    permet de passer un livre entier (12 illustrations) de 23 Mo à ~5 Mo.
    La clé reste `_compress_png` par cohérence historique mais retourne du
    JPEG — ReportLab détecte le format via les octets magiques.
    """
    try:
        from PIL import Image as PILImage
        import io as _io
        im = PILImage.open(_io.BytesIO(raw))
        im = im.convert('RGB')
        if max(im.size) > max_side:
            im.thumbnail((max_side, max_side), PILImage.LANCZOS)
        out = _io.BytesIO()
        im.save(out, format='JPEG', quality=85, optimize=True, progressive=True)
        return out.getvalue()
    except Exception:
        return raw


# ─── Ex Libris : illustration unique par signature astrale ─────────────────

def _ex_libris_prompt(sun: str, moon: str, asc: str) -> str:
    """Prompt riche basé sur la triade Soleil/Lune/Ascendant."""
    sun = (sun or '').strip() or 'inconnu'
    moon = (moon or '').strip() or 'inconnue'
    asc = (asc or '').strip() or 'inconnu'
    return (
        "Illustration personnelle unique pour la page Ex Libris d'un livre "
        f"d'astrologie reliée. Trois symboles astrologiques entrelacés : "
        f"un soleil levant pour le Soleil en {sun} (centre, en haut), "
        f"un croissant lunaire pour la Lune en {moon} (gauche), "
        f"une porte ouverte sur un paysage pour l'Ascendant en {asc} (droite). "
        "Les trois éléments se tiennent dans une composition harmonieuse, "
        "enlacés par un fin trait d'or qui dessine une constellation. "
        + _STYLE_CONSTRAINTS
    )


async def get_or_generate_ex_libris_illustration(
    *,
    user_id: str,
    prenom: str,
    sun_sign: str,
    moon_sign: str,
    asc_sign: str,
    force_refresh: bool = False,
) -> Optional[bytes]:
    """Retourne une illustration PNG Ex Libris propre à la signature.

    Mise en cache sur disque par hash(prenom|sun|moon|asc). `user_id` est
    conservé pour tracer l'usage mais n'intervient pas dans la clé — deux
    personnes avec la même triade partagent la même illustration (coût
    amorti, résultat esthétique identique).
    """
    key = _signature_hash(prenom, sun_sign, moon_sign, asc_sign)
    cache_file = EX_LIBRIS_CACHE / f'{key}.png'
    remote_path = f'{_STORAGE_PREFIX}/ex_libris/{key}.jpg'
    if not force_refresh:
        cached = await _read_cached(cache_file, remote_path)
        if cached:
            logger.info(f'[ex_libris_illust] cache HIT {key} (user={user_id})')
            return cached

    prompt = _ex_libris_prompt(sun_sign, moon_sign, asc_sign)
    logger.info(f'[ex_libris_illust] generating {key} (user={user_id})')
    png = await _generate_image_bytes(prompt, session_id=f'exlibris-{key}')
    if not png:
        return None
    await _write_cached(cache_file, remote_path, png)
    # Trace l'Ex Libris généré en Mongo (collection d'audit admin).
    await _log_ex_libris(
        user_id=user_id, signature_hash=key, prenom=prenom,
        sun=sun_sign, moon=moon_sign, asc=asc_sign,
        storage_path=remote_path, size=len(png),
    )
    return png


async def _log_ex_libris(*, user_id: str, signature_hash: str, prenom: str,
                         sun: str, moon: str, asc: str,
                         storage_path: str, size: int) -> None:
    """Insert/upsert d'une trace Ex Libris pour l'audit admin.

    Ne bloque jamais la génération si Mongo indisponible.
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from datetime import datetime, timezone
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        if not mongo_url or not db_name:
            return
        db = AsyncIOMotorClient(mongo_url)[db_name]
        now = datetime.now(timezone.utc)
        await db.natal_illustrations_log.update_one(
            {'signature_hash': signature_hash},
            {
                '$set': {
                    'user_id': user_id or '',
                    'prenom': prenom or '',
                    'sun_sign': sun or '',
                    'moon_sign': moon or '',
                    'asc_sign': asc or '',
                    'storage_path': storage_path,
                    'size_bytes': size,
                    'last_generated_at': now.isoformat(),
                },
                '$inc': {'generation_count': 1},
                '$setOnInsert': {
                    'signature_hash': signature_hash,
                    'first_generated_at': now.isoformat(),
                    'kind': 'ex_libris',
                },
            },
            upsert=True,
        )
    except Exception as e:
        logger.warning(f'[ex_libris_illust] mongo log skipped: {e}')


# ─── Vignettes de fin de chapitre planétaire ───────────────────────────────

_PLANET_PROMPTS: dict[str, str] = {
    'soleil': (
        "Soleil éditorial stylisé, disque or Hermès avec huit rayons droits "
        "alternés longs et courts, légère auréole or sur fond crème. "
        "Petite constellation du Lion suggérée en pointillés or discrets."
    ),
    'lune': (
        "Croissant de Lune ascendant finement dessiné en encre, avec un "
        "léger halo nacré argenté, trois étoiles filantes dorées autour. "
        "Composition verticale, poésie du soir."
    ),
    'mercure': (
        "Caducée de Mercure traité en gravure moderne : deux fils entrelacés "
        "d'or autour d'un bâton d'encre, deux ailes miniatures en haut, "
        "symbole d'échange et de pensée."
    ),
    'venus': (
        "Vénus représentée par une rose ouverte vue du dessus, pétales en "
        "aquarelle terracotta et or, tige fine d'encre. Composition pure."
    ),
    'mars': (
        "Lance ascendante stylisée pour Mars, fer de lance or sur une hampe "
        "d'encre, deux flammes miniatures autour. Dynamique, verticale."
    ),
    'jupiter': (
        "Jupiter évoqué par un cercle doré circulaire majestueux, foudre "
        "stylisée centrale en or, deux arcs ouverts autour comme des "
        "anneaux de pensée. Grandeur, générosité."
    ),
    'saturne': (
        "Saturne : anneau sombre en encre entourant une petite sphère d'or, "
        "faux ancienne stylisée en bas, suspendue. Rigueur et noblesse."
    ),
    'uranus': (
        "Uranus : éclair bifide d'or jaillissant entre deux cercles concentriques "
        "d'encre, étoile stylisée en haut. Rupture graphique maîtrisée."
    ),
    'neptune': (
        "Neptune représenté par un trident d'or stylisé, vagues en encre "
        "ondulantes à sa base, perle nacrée centrale. Rêve et profondeur."
    ),
    'pluton': (
        "Pluton : petite planète d'encre entourée d'un anneau d'or éclaté, "
        "racine qui plonge vers le bas comme un fil végétal. Transformation discrète."
    ),
}


async def get_or_generate_planet_illustration(planet_name_fr: str) -> Optional[bytes]:
    """Illustration vignette pour la fin de chapitre d'une planète.

    Cache global (une seule par planète pour tout Plume Astrale). Première
    génération → coût de ~0.02€, toutes les suivantes → fichier local.
    """
    key = _slug(planet_name_fr)
    if key not in _PLANET_PROMPTS:
        return None
    cache_file = PLANET_CACHE / f'{key}.png'
    remote_path = f'{_STORAGE_PREFIX}/planets/{key}.jpg'
    cached = await _read_cached(cache_file, remote_path)
    if cached:
        return cached
    prompt = _PLANET_PROMPTS[key] + '\n\n' + _STYLE_CONSTRAINTS
    logger.info(f'[planet_illust] generating {key}')
    png = await _generate_image_bytes(prompt, session_id=f'planet-{key}')
    if not png:
        return None
    await _write_cached(cache_file, remote_path, png)
    return png


async def get_all_planet_illustrations() -> dict[str, bytes]:
    """Pré-génère ou récupère toutes les vignettes planètes du socle.

    Appelé une seule fois au boot du build PDF ; les hits suivants sont
    instantanés (fichiers locaux). Les échecs individuels sont tolérés.
    """
    out: dict[str, bytes] = {}
    for name in ('Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars',
                 'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton'):
        png = await get_or_generate_planet_illustration(name)
        if png:
            out[_slug(name)] = png
    return out


# ─── Vignette de clôture (page « Pour poursuivre votre lecture ») ──────────

_CLOSING_PROMPT = (
    "Illustration de clôture pour un livre d'astrologie : une plume ouverte "
    "posée sur un livre entrouvert, une étoile filante d'or qui part vers le "
    "haut de la page, trois petits astres dispersés en pointillés or. "
    "Composition contemplative, vide maîtrisé. "
) + _STYLE_CONSTRAINTS


async def get_or_generate_closing_illustration() -> Optional[bytes]:
    cache_file = PLANET_CACHE / 'closing.png'
    remote_path = f'{_STORAGE_PREFIX}/planets/closing.jpg'
    cached = await _read_cached(cache_file, remote_path)
    if cached:
        return cached
    png = await _generate_image_bytes(_CLOSING_PROMPT, session_id='natal-closing')
    if not png:
        return None
    await _write_cached(cache_file, remote_path, png)
    return png
