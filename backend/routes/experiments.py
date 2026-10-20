"""Routes /api/experiments/* — lecture publique de variantes verrouillées."""
import logging
from fastapi import APIRouter

from services.experiment_auto_lock import get_locked_variant

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/experiments', tags=['experiments'])


@router.get('/{experiment}/variant')
async def experiment_variant(experiment: str):
    """Retourne {variant: str|null, locked: bool}.

    Si une variante gagnante a été verrouillée pour `experiment`, le frontend
    doit l'utiliser au lieu de picker aléatoirement. Sinon, pick random (fallback).
    """
    locked = await get_locked_variant(experiment)
    return {'experiment': experiment, 'variant': locked, 'locked': locked is not None}
