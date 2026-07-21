"""
Routes d'aperçu PDF pour la Bibliothèque Plume Astrale.

Endpoint public (pas d'auth) qui retourne un PDF 3 pages statique par livre.
Utilisé sur `/nos-livres` pour rassurer les visiteurs avant achat.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from services.apercu_pdf import build_apercu, BOOK_PREVIEWS

router = APIRouter()


@router.get('/apercus/{book_key}.pdf')
async def download_apercu(book_key: str):
    """Retourne l'aperçu PDF 3 pages du livre demandé (public, sans auth).

    book_key ∈ {natal, synastry, kabbale, astrocarto, karmique}
    """
    if book_key not in BOOK_PREVIEWS:
        raise HTTPException(status_code=404, detail='Aperçu inconnu')
    pdf = build_apercu(book_key)
    if not pdf:
        raise HTTPException(status_code=500, detail='Génération de l\'aperçu échouée')

    filename = f'apercu-plume-astrale-{book_key}.pdf'
    return Response(
        content=pdf,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="{filename}"',
            # 1h de cache navigateur (les aperçus sont statiques)
            'Cache-Control': 'public, max-age=3600',
        },
    )
