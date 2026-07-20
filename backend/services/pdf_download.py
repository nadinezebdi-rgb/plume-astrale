"""
SEC-003 : Téléchargement sécurisé des PDFs personnels.

Approche : token opaque (32 octets aléatoires) stocké dans
`payment_transactions.metadata.pdf_token`. Le PDF n'est plus servi
en statique — il faut connaître (session_id, pdf_token) pour y accéder.

Le token est généré au moment de la génération du PDF. Le status endpoint
renvoie une URL signée `/api/pdf/download?session_id=X&token=Y`.
"""
from __future__ import annotations
import hmac
import logging
import secrets
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

# Racine où sont écrits les PDFs personnels (dans backend/assets/{product}/)
# Ces sous-dossiers ne sont PLUS mountés en statique.
ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'

# Produits qui utilisent le download sécurisé + leur sous-dossier
_PROTECTED_PRODUCTS = {
    'kabbale_arbre_de_vie': 'kabbale',
    'astrocartographie': 'astrocartographie',
    'pack_karmique_kabbale': 'pack_karmique',
    'synastrie_oneshot': 'synastrie_pdf',
    'rencontres_ultime': 'rencontres_ultime',
}


def new_pdf_token() -> str:
    """Génère un token opaque cryptographiquement sûr (32 octets base64url)."""
    return secrets.token_urlsafe(32)


def build_signed_pdf_url(session_id: str, token: str) -> str:
    """Retourne l'URL relative que le frontend appellera pour télécharger."""
    return f'/api/pdf/download?session_id={session_id}&token={token}'


def _resolve_pdf_file(product_kind: str, session_id: str) -> Optional[Path]:
    """Retrouve le fichier PDF sur disque à partir de la clé produit + session."""
    subdir = _PROTECTED_PRODUCTS.get(product_kind)
    if not subdir:
        return None
    folder = ASSETS_DIR / subdir
    if not folder.exists():
        return None
    # Les fichiers sont nommés {product}_{session_id[-16:]}.pdf
    suffix = session_id[-16:]
    for f in folder.glob(f'*{suffix}*.pdf'):
        return f
    return None


async def download_pdf(session_id: str, token: str):
    """Endpoint handler : valide (session_id, token) et streame le fichier.

    Aucune auth Bearer requise — mais le token opaque de 32 octets fait
    office de credential (URL secrète transmise à l'acheteur par email + succès).
    """
    if not session_id or not token:
        raise HTTPException(status_code=400, detail='session_id et token requis')

    from services.supabase_client import get_admin_client
    try:
        sb = get_admin_client()
        r = sb.table('payment_transactions').select('metadata, pack_id, payment_status').eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[pdf_download] db fetch failed for {session_id}: {e}')
        raise HTTPException(status_code=500, detail='Erreur base de données')

    if not r or not r.data:
        raise HTTPException(status_code=404, detail='Transaction introuvable')

    tx = r.data
    md = tx.get('metadata') or {}
    stored_token = md.get('pdf_token')
    if not stored_token:
        raise HTTPException(status_code=404, detail='PDF pas encore prêt')
    # comparaison constante (anti-timing attack)
    if not hmac.compare_digest(str(stored_token), token):
        logger.warning(f'[pdf_download] invalid token for {session_id}')
        raise HTTPException(status_code=403, detail='Token invalide')

    if tx.get('payment_status') not in ('paid', 'completed'):
        raise HTTPException(status_code=402, detail='Paiement requis')

    product_kind = tx.get('pack_id') or md.get('kind') or ''
    pdf_file = _resolve_pdf_file(product_kind, session_id)
    if not pdf_file or not pdf_file.exists():
        logger.warning(f'[pdf_download] file missing for {session_id} ({product_kind})')
        raise HTTPException(status_code=404, detail='Fichier introuvable')

    return FileResponse(
        path=str(pdf_file),
        media_type='application/pdf',
        filename=pdf_file.name,
    )
