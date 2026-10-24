"""admin_illustrations — Audit admin des Ex Libris Nano Banana générés.

Endpoints :
  - GET  /api/admin/natal-illustrations
      Liste paginée des Ex Libris générés (collection `natal_illustrations_log`).
      Pour chaque ligne : prenom, signature astrale, user_id, created_at,
      storage_path, et une URL de miniature `thumbnail_url`.
  - GET  /api/admin/natal-illustrations/{signature_hash}/image
      Sert les bytes JPEG depuis Emergent Storage (passe par le backend car
      l'img tag ne peut pas envoyer de header auth).
  - POST /api/admin/natal-illustrations/{signature_hash}/regenerate
      Supprime le cache local + storage et re-déclenche la génération
      Nano Banana (coût ~0.02€). Pratique si une illustration déçoit.
"""
from __future__ import annotations
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from motor.motor_asyncio import AsyncIOMotorClient

from routes.admin import require_admin
from services.natal_book_illustrations import (
    EX_LIBRIS_CACHE,
    _STORAGE_PREFIX,
    get_or_generate_ex_libris_illustration,
)
from services.emergent_storage import get_object as storage_get

router = APIRouter(prefix='/admin/natal-illustrations', tags=['admin', 'illustrations'])
logger = logging.getLogger(__name__)


def _db():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    if not mongo_url or not db_name:
        raise HTTPException(status_code=500, detail='MONGO_URL/DB_NAME manquants')
    return AsyncIOMotorClient(mongo_url)[db_name]


@router.get('')
async def list_illustrations(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    _admin: dict = Depends(require_admin),
):
    """Liste paginée des Ex Libris générés, du plus récent au plus ancien."""
    db = _db()
    cursor = db.natal_illustrations_log.find(
        {'kind': 'ex_libris'},
        projection={'_id': 0},
    ).sort('last_generated_at', -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(doc)
    total = await db.natal_illustrations_log.count_documents({'kind': 'ex_libris'})
    return {
        'items': items,
        'total': total,
        'skip': skip,
        'limit': limit,
    }


@router.get('/{signature_hash}/image')
async def get_illustration_image(
    signature_hash: str,
    _admin: dict = Depends(require_admin),
):
    """Sert les bytes JPEG d'un Ex Libris (local hot → Emergent Storage)."""
    local = EX_LIBRIS_CACHE / f'{signature_hash}.png'
    data: bytes | None = None
    if local.exists():
        try:
            data = local.read_bytes()
        except Exception:
            data = None
    if not data:
        remote_path = f'{_STORAGE_PREFIX}/ex_libris/{signature_hash}.jpg'
        data = await storage_get(remote_path)
    if not data:
        raise HTTPException(status_code=404, detail='Illustration introuvable')
    return Response(content=data, media_type='image/jpeg')


@router.post('/{signature_hash}/regenerate')
async def regenerate_illustration(
    signature_hash: str,
    _admin: dict = Depends(require_admin),
):
    """Force une nouvelle génération Nano Banana pour la signature donnée.

    Lit la ligne Mongo pour récupérer prenom + triade (sinon on ne peut pas
    rejouer le prompt), supprime le cache local, et appelle le pipeline avec
    `force_refresh=True`. Le nouveau fichier écrase le remote (idempotent).
    """
    db = _db()
    doc = await db.natal_illustrations_log.find_one({'signature_hash': signature_hash})
    if not doc:
        raise HTTPException(status_code=404, detail='Signature inconnue')
    # Wipe local cache so even a cache HIT local serait by-passé.
    try:
        (EX_LIBRIS_CACHE / f'{signature_hash}.png').unlink(missing_ok=True)
    except Exception:
        pass

    png = await get_or_generate_ex_libris_illustration(
        user_id=doc.get('user_id') or '',
        prenom=doc.get('prenom') or '',
        sun_sign=doc.get('sun_sign') or '',
        moon_sign=doc.get('moon_sign') or '',
        asc_sign=doc.get('asc_sign') or '',
        force_refresh=True,
    )
    if not png:
        raise HTTPException(status_code=502, detail='Nano Banana a échoué')
    return {'ok': True, 'size_bytes': len(png), 'signature_hash': signature_hash}
