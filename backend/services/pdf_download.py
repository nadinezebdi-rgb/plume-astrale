"""
SEC-003 : Téléchargement sécurisé des PDFs personnels.

Approche : token opaque (32 octets aléatoires) stocké dans
`payment_transactions.metadata.pdf_token`. Le PDF n'est plus servi
en statique — il faut connaître (session_id, pdf_token) pour y accéder.

Le token est généré au moment de la génération du PDF. Le status endpoint
renvoie une URL signée `/api/pdf/download?session_id=X&token=Y`.

Extension 2026-02-26 : support multi-PDF par session pour Voyage Karmique
(deux tokens : `kabbale_pdf_token` + `karma_pdf_token`) et pour Synastrie
(table `synastrie_purchases` séparée avec son propre token).
"""
from __future__ import annotations
import hmac
import logging
import secrets
from pathlib import Path
from typing import Optional, Tuple

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
    # Fallback local si l'upload Supabase échoue — le PDF reste téléchargeable
    # depuis le disque du pod pendant sa durée de vie. Supabase reste la source
    # canonique pour la persistence après redeploy.
    'theme_natal_pdf_oneshot': 'theme_natal',
    'theme_natal_pdf': 'theme_natal',
    # Multi-PDF (2026-02-26) : Voyage Karmique génère deux livrets. La variante
    # est encodée dans le préfixe du filename (`voyage_karmique_kabbale_...pdf`
    # ou `voyage_karmique_karma_...pdf`), pas dans le pack_id.
    'voyage_karmique': 'voyage_karmique',
}

# Multi-token map : {product_kind: {token_key: filename_prefix}}
# Utilisé pour authentifier chaque PDF individuellement et retrouver le bon fichier.
_MULTI_PDF_PRODUCTS = {
    'voyage_karmique': {
        'kabbale_pdf_token': 'voyage_karmique_kabbale',
        'karma_pdf_token': 'voyage_karmique_karma',
    },
}


def new_pdf_token() -> str:
    """Génère un token opaque cryptographiquement sûr (32 octets base64url)."""
    return secrets.token_urlsafe(32)


def build_signed_pdf_url(session_id: str, token: str) -> str:
    """Retourne l'URL relative que le frontend appellera pour télécharger."""
    return f'/api/pdf/download?session_id={session_id}&token={token}'


def upload_pdf_to_reports_bucket(
    pdf_bytes: bytes,
    session_id: str,
    product_kind: str,
    filename: Optional[str] = None,
    version: Optional[str] = None,
) -> Optional[str]:
    """Upload le PDF sur Supabase Storage bucket 'reports/{product_kind}/{session_id}.pdf'.
    Retourne l'URL publique du PDF, ou None si l'upload échoue.

    Cette URL reste valide après redeploy (contrairement aux fichiers locaux
    stockés dans /app/backend/assets/ qui sont perdus au restart du pod).
    Créé 2026-02 pour l'onglet admin "PDFs envoyés".

    Si version est fourni (ex: timestamp de régénération), le path est suffixé
    par -v{version} → nouvelle URL unique, immune à tout cache CDN sur l'ancienne.
    """
    try:
        from services.supabase_client import get_admin_client
        sb = get_admin_client()
        # Path stable et unique dans le bucket
        clean_kind = (product_kind or 'other').replace('/', '_').strip('_') or 'other'
        clean_sid = (session_id or '').replace('/', '_')[-40:]
        # Suffixe de version pour forcer une URL fraîche (bypass CDN cache Supabase)
        suffix = f'-v{version}' if version else ''
        path = f'pdfs/{clean_kind}/{clean_sid}{suffix}.pdf'

        # Cache-control court (60s) pour que les futurs replaces se propagent vite
        # via le CDN Supabase si jamais on réutilise le même path.
        cache_ctrl = '60'
        # Upsert : override si déjà présent (régénération admin, etc.)
        try:
            sb.storage.from_('reports').upload(
                path, pdf_bytes,
                {'content-type': 'application/pdf', 'cache-control': cache_ctrl, 'upsert': 'true'},
            )
        except Exception:
            # Fallback : delete + upload si upsert non supporté par la SDK
            try:
                sb.storage.from_('reports').remove([path])
            except Exception:
                pass
            sb.storage.from_('reports').upload(
                path, pdf_bytes,
                {'content-type': 'application/pdf', 'cache-control': cache_ctrl},
            )

        # Génère l'URL publique (bucket doit être public sur Supabase)
        public_url = sb.storage.from_('reports').get_public_url(path)
        # supabase-py retourne parfois avec un trailing '?', normalise
        if isinstance(public_url, str):
            public_url = public_url.rstrip('?')
        logger.info(f'[pdf_upload] {clean_kind}/{clean_sid}{suffix} → {public_url}')
        return public_url
    except Exception as e:
        logger.warning(f'[pdf_upload] échec upload Supabase pour {product_kind}/{session_id}: {e}')
        return None


def _resolve_pdf_file(product_kind: str, session_id: str,
                       filename_prefix: Optional[str] = None) -> Optional[Path]:
    """Retrouve le fichier PDF sur disque à partir de la clé produit + session.

    Si `filename_prefix` est fourni (Voyage Karmique multi-PDF), on cible le
    fichier dont le nom commence par ce préfixe. Sinon on prend le premier
    fichier qui contient le suffixe du session_id.
    """
    subdir = _PROTECTED_PRODUCTS.get(product_kind)
    if not subdir:
        return None
    folder = ASSETS_DIR / subdir
    if not folder.exists():
        return None
    # Les fichiers sont nommés {product}_{session_id[-16:]}.pdf
    suffix = session_id[-16:]
    pattern = f'{filename_prefix}_*{suffix}*.pdf' if filename_prefix else f'*{suffix}*.pdf'
    for f in folder.glob(pattern):
        return f
    # Fallback synastrie : filename basé sur l'ID d'achat (voir _trigger_synastrie_pdf_email)
    if product_kind == 'synastrie_oneshot' and not filename_prefix:
        for f in folder.glob('synastrie_*.pdf'):
            return f
    return None


def _match_token_and_resolve(
    tx_metadata: dict, product_kind: str, token: str, session_id: str,
) -> Tuple[Optional[Path], Optional[str], Optional[str]]:
    """Vérifie le token présenté vs ceux stockés dans metadata.

    Retourne (pdf_file, matched_token_key, supabase_url_for_fallback).
    - `matched_token_key` est ex. 'pdf_token' ou 'kabbale_pdf_token' → utilisé
      pour retrouver l'URL Supabase correspondante en fallback.
    - `supabase_url_for_fallback` : l'URL persistée liée à ce token (si dispo).
    """
    # Multi-PDF (Voyage Karmique) : on essaie chaque token candidat
    multi = _MULTI_PDF_PRODUCTS.get(product_kind)
    if multi:
        for tok_key, filename_prefix in multi.items():
            stored = tx_metadata.get(tok_key)
            if stored and hmac.compare_digest(str(stored), token):
                # Supabase URL correspondante suit la convention {variant}_supabase_url
                variant = tok_key.split('_')[0]  # 'kabbale' | 'karma'
                sb_url = tx_metadata.get(f'{variant}_supabase_url')
                pdf_file = _resolve_pdf_file(product_kind, session_id, filename_prefix)
                return pdf_file, tok_key, sb_url
        return None, None, None

    # Single-PDF classique
    stored = tx_metadata.get('pdf_token')
    if stored and hmac.compare_digest(str(stored), token):
        pdf_file = _resolve_pdf_file(product_kind, session_id)
        return pdf_file, 'pdf_token', tx_metadata.get('pdf_supabase_url')
    return None, None, None


async def download_pdf(session_id: str, token: str):
    """Endpoint handler : valide (session_id, token) et streame le fichier.

    Aucune auth Bearer requise — mais le token opaque de 32 octets fait
    office de credential (URL secrète transmise à l'acheteur par email + succès).

    Supporte 3 flux :
      1. Single-PDF standard (Thème Natal, Kabbale, Astrocarto, Pack Karmique) :
         `payment_transactions.metadata.pdf_token`.
      2. Multi-PDF (Voyage Karmique) : deux tokens
         (`kabbale_pdf_token`, `karma_pdf_token`) dans la même session.
      3. Synastrie (table `synastrie_purchases` séparée) : fallback lookup
         par `stripe_session_id` + colonne `pdf_token`.
    """
    if not session_id or not token:
        raise HTTPException(status_code=400, detail='session_id et token requis')

    from services.supabase_client import get_admin_client
    try:
        sb = get_admin_client()
        r = sb.table('payment_transactions').select(
            'metadata, pack_id, payment_status',
        ).eq('session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[pdf_download] db fetch failed for {session_id}: {e}')
        raise HTTPException(status_code=500, detail='Erreur base de données')

    if not r or not r.data:
        # Fallback : lookup dans synastrie_purchases (session Stripe séparée)
        return await _download_synastrie_pdf(session_id, token, sb)

    tx = r.data
    md = tx.get('metadata') or {}
    if tx.get('payment_status') not in ('paid', 'completed'):
        raise HTTPException(status_code=402, detail='Paiement requis')

    product_kind = tx.get('pack_id') or md.get('kind') or ''
    pdf_file, matched_key, supabase_url = _match_token_and_resolve(
        md, product_kind, token, session_id,
    )
    if not matched_key:
        logger.warning(f'[pdf_download] invalid token for {session_id} ({product_kind})')
        raise HTTPException(status_code=403, detail='Token invalide')

    if not pdf_file or not pdf_file.exists():
        # Fallback : si le PDF est stocké sur Supabase Storage (survit aux redeploys),
        # redirige vers l'URL publique persistante au lieu de renvoyer une 404 brute.
        if supabase_url:
            from fastapi.responses import RedirectResponse
            logger.info(f'[pdf_download] {session_id}/{matched_key} local manquant → redirect Supabase')
            resp = RedirectResponse(url=supabase_url, status_code=302)
            # Empêche le navigateur de cacher le redirect (l'URL cible peut changer sur régénération)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            return resp
        # Aucun fallback disponible : message clair au lieu d'un JSON brut
        logger.warning(f'[pdf_download] file missing for {session_id} ({product_kind})')
        raise HTTPException(
            status_code=404,
            detail=(
                "Ton PDF n'est plus disponible via ce lien direct (fichier temporaire expiré). "
                "Rendez-vous dans « Mon Compte → Mes Rapports » pour le retrouver, ou contacte "
                "contact@plume-astrale.fr avec ton numéro de commande."
            ),
        )

    return FileResponse(
        path=str(pdf_file),
        media_type='application/pdf',
        filename=pdf_file.name,
    )


async def _download_synastrie_pdf(session_id: str, token: str, sb):
    """Lookup dans `synastrie_purchases` (table séparée, session Stripe distincte).

    Le token est stocké encodé dans la colonne `pdf_path` sous forme
    `/api/pdf/download?session_id=X&token=Y`. On l'extrait par parse d'URL,
    ce qui évite d'ajouter une colonne dédiée à la table Supabase.

    Compat legacy : si `pdf_path` a été écrit AVANT la migration token
    (format `/api/assets/synastrie/synastrie_{id}.pdf`), on accepte le
    session_id comme credential (identique à l'ancien flux static file :
    anyone with the stripe_session_id could access — same trust boundary).
    """
    from urllib.parse import urlparse, parse_qs

    try:
        r = sb.table('synastrie_purchases').select(
            'id, pdf_path, status',
        ).eq('stripe_session_id', session_id).maybe_single().execute()
    except Exception as e:
        logger.warning(f'[pdf_download/synastrie] db fetch failed for {session_id}: {e}')
        raise HTTPException(status_code=500, detail='Erreur base de données')

    if not r or not r.data:
        raise HTTPException(status_code=404, detail='Transaction introuvable')

    rec = r.data
    pdf_path_stored = rec.get('pdf_path') or ''
    if rec.get('status') and rec['status'] not in ('paid', 'completed'):
        raise HTTPException(status_code=402, detail='Paiement requis')

    # Legacy : ancien flux static file → on autorise si session_id présent
    # (le token argument est ignoré, cohérent avec l'ancienne surface d'attaque).
    is_legacy = pdf_path_stored.startswith('/api/assets/')
    if not is_legacy:
        q = parse_qs(urlparse(pdf_path_stored).query)
        stored_token = (q.get('token') or [''])[0]
        if not stored_token:
            raise HTTPException(status_code=404, detail='PDF pas encore prêt')
        if not hmac.compare_digest(str(stored_token), token):
            logger.warning(f'[pdf_download/synastrie] invalid token for {session_id}')
            raise HTTPException(status_code=403, detail='Token invalide')

    # Le fichier local suit la convention synastrie_{purchase_id}.pdf
    local_file = ASSETS_DIR / 'synastrie' / f'synastrie_{rec["id"]}.pdf'
    if local_file.exists():
        return FileResponse(
            path=str(local_file), media_type='application/pdf', filename=local_file.name,
        )

    raise HTTPException(
        status_code=404,
        detail=(
            "Ton PDF Synastrie n'est plus disponible via ce lien direct. "
            "Contacte contact@plume-astrale.fr avec ton numéro de commande."
        ),
    )
