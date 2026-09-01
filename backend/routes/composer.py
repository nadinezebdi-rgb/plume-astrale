"""Route /api/composer — L'Atelier (pivot livre unifié, 2026-03).

Endpoints :
  POST /api/composer/quote     → calcul dynamique (source de vérité serveur)
  GET  /api/composer/chapters  → catalogue des chapitres actifs (public)
  POST /api/composer/checkout  → session Stripe pour Numérique / Broché / Relié
                                  avec metadata.chapters (jsonl) + calcul re-vérifié

Le prix N'EST JAMAIS accepté depuis le client. Le client envoie l'édition et
la liste de slugs — le serveur recalcule avec la règle 29/19/99.
"""
from __future__ import annotations
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from config import get_settings
from services.book_composer_pricing import (
    EDITIONS,
    compute_quote,
    load_active_chapters,
)
from services.supabase_client import get_admin_client
from integrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/composer', tags=['composer'])


# ── Schémas Pydantic ────────────────────────────────────────────
class QuotePayload(BaseModel):
    edition: str = Field(pattern=r'^(numerique|brochee|reliee)$')
    chapter_slugs: List[str] = Field(default_factory=list, max_length=20)
    no_birth_time: bool = False


class CheckoutPayload(BaseModel):
    edition: str = Field(pattern=r'^(numerique|brochee|reliee)$')
    chapter_slugs: List[str] = Field(default_factory=list, max_length=20)
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=80)
    birth_date: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    birth_time: Optional[str] = Field(default=None, pattern=r'^\d{2}:\d{2}$')
    birth_city: str = Field(min_length=2, max_length=120)
    birth_country: Optional[str] = Field(default='FR', max_length=4)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    origin_url: str = Field(min_length=8, max_length=200)
    # Optionnels (uniquement pour Broché/Relié — dédicace + destinataire)
    recipient_first_name: Optional[str] = Field(default=None, max_length=80)
    dedication: Optional[str] = Field(default=None, max_length=800)
    # Code promo (universel, dispo pour n'importe qui, pas admin only)
    promo_code: Optional[str] = Field(default=None, max_length=40)


# Codes promo actifs — TOUT2026 offre 100% de réduction (test/friends)
# Étendable via table Supabase promo_codes plus tard.
_PROMO_CODES = {
    'TOUT2026': {'discount_pct': 100, 'active': True, 'label': 'Offert 2026'},
}


class ApplyPromoPayload(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    edition: str = Field(pattern=r'^(numerique|brochee|reliee)$')
    chapter_slugs: List[str] = Field(default_factory=list, max_length=20)
    no_birth_time: bool = False


def _validate_promo(code: Optional[str]) -> Optional[dict]:
    """Retourne le dict du promo si valide, sinon None."""
    if not code:
        return None
    normalized = code.strip().upper()
    promo = _PROMO_CODES.get(normalized)
    if promo and promo.get('active'):
        return {'code': normalized, **promo}
    return None


# ── Endpoints ───────────────────────────────────────────────────
@router.get('/chapters')
async def composer_chapters(no_birth_time: bool = False):
    """Catalogue des chapitres actifs (utilisé par l'étape 2 du wizard)."""
    catalog = load_active_chapters(no_birth_time=no_birth_time)
    return {
        'editions': [
            {
                'slug': slug,
                'label': meta['label'],
                'price_eur': meta['price_eur'],
                'delivery': meta['delivery'],
                'pages_base': meta['pages_base'],
            }
            for slug, meta in EDITIONS.items()
        ],
        'chapters': [
            {
                'slug': c.slug,
                'name': c.name,
                'subtitle': c.subtitle,
                'pages_added': c.pages_added,
                'tagline': c.tagline,
                'requires_no_birth_time': c.requires_no_birth_time,
                'sort_order': c.sort_order,
            }
            for c in catalog
        ],
        'pricing_rules': {
            'first_chapter_eur': 29,
            'next_chapter_eur': 19,
            'chapters_cap_eur': 99,
        },
    }


@router.post('/quote')
async def composer_quote(payload: QuotePayload):
    """Calcul dynamique du prix pour affichage live dans le wizard."""
    try:
        q = compute_quote(
            edition=payload.edition,
            chapter_slugs=payload.chapter_slugs,
            no_birth_time=payload.no_birth_time,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        'edition': q.edition,
        'edition_label': q.edition_label,
        'edition_price_eur': q.edition_price_eur,
        'chapters': q.chapters,
        'chapters_subtotal_eur': q.chapters_subtotal_eur,
        'chapters_price_eur': q.chapters_price_eur,
        'chapters_cap_applied': q.chapters_cap_applied,
        'total_eur': q.total_eur,
        'total_pages': q.total_pages,
        'currency': q.currency,
        'warnings': q.warnings,
    }


@router.post('/apply-promo')
async def composer_apply_promo(payload: ApplyPromoPayload):
    """Valide un code promo et retourne le prix réduit — jamais 402 (le code peut juste être invalide).
    Réponse : {valid, discount_pct, label, total_eur, quote}
    """
    promo = _validate_promo(payload.code)
    try:
        q = compute_quote(edition=payload.edition, chapter_slugs=payload.chapter_slugs,
                          no_birth_time=payload.no_birth_time)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not promo:
        return {'valid': False, 'total_eur': q.total_eur, 'discount_pct': 0}
    discounted = max(0, q.total_eur * (100 - promo['discount_pct']) // 100)
    return {
        'valid': True,
        'code': promo['code'],
        'label': promo['label'],
        'discount_pct': promo['discount_pct'],
        'original_total_eur': q.total_eur,
        'total_eur': discounted,
    }


@router.post('/checkout')
async def composer_checkout(payload: CheckoutPayload, request: Request):
    """Crée la session Stripe pour la commande /composer avec pricing serveur re-vérifié.

    Si un `promo_code` 100% est fourni et valide, court-circuite Stripe :
    crée une transaction payée en base et retourne l'URL de succès directement.
    """
    settings = get_settings()

    # Détection heure absente (voir §V audit marque Feb 2026)
    no_birth_time = (
        not payload.birth_time
        or payload.birth_time.strip() in ('', '12:00', '12:00:00')
    )
    birth_time_effective = payload.birth_time or '12:00'

    # RECALCUL SERVEUR — jamais accepter un prix client
    try:
        q = compute_quote(
            edition=payload.edition,
            chapter_slugs=payload.chapter_slugs,
            no_birth_time=no_birth_time,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Prépare birth_data v3 (miroir de theme_natal_oneshot)
    try:
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = birth_time_effective[:5].split(':')
        birth_data = {'year': int(y), 'month': int(m), 'day': int(d), 'hour': int(h), 'minute': int(mi)}
        if payload.latitude is not None:
            birth_data['latitude'] = float(payload.latitude)
        if payload.longitude is not None:
            birth_data['longitude'] = float(payload.longitude)
        if payload.birth_city:
            birth_data['city'] = payload.birth_city
        if payload.birth_country:
            birth_data['country_code'] = payload.birth_country.upper()
    except Exception as e:
        raise HTTPException(400, f'Format date/heure invalide : {e}')

    pdf_ctx = {
        'first_name': payload.first_name.strip(),
        'birth_date_iso': payload.birth_date,
        'birth_data': birth_data,
        'no_birth_time': no_birth_time,
        # Composer-specific
        'edition': q.edition,
        'chapters': [c['slug'] for c in q.chapters],
        'recipient_first_name': (payload.recipient_first_name or '').strip() or None,
        'dedication': (payload.dedication or '').strip() or None,
    }

    # ── Bypass Stripe pour code promo 100% ──────────────────────
    promo = _validate_promo(payload.promo_code)
    if promo and promo.get('discount_pct') == 100:
        import uuid as _uuid
        fake_session_id = f'promo_{promo["code"].lower()}_{_uuid.uuid4().hex[:16]}'
        origin = payload.origin_url.rstrip('/')
        # Trace transaction comme "payée" (offerte) directement
        try:
            sb = get_admin_client()
            sb.table('payment_transactions').insert({
                'session_id': fake_session_id,
                'user_email': payload.email.lower(),
                'pack_id': f'composer_{q.edition}',
                'amount': 0.0,
                'currency': q.currency,
                'credits': 0,
                'status': 'complete',
                'payment_status': 'paid',
                'credits_granted': True,
                'metadata': {
                    'kind': 'composer_book',
                    'product': 'composer_book',
                    'edition': q.edition,
                    'chapters': pdf_ctx['chapters'],
                    'promo_code': promo['code'],
                    'promo_label': promo['label'],
                    'quote': {
                        'edition_price_eur': q.edition_price_eur,
                        'chapters_price_eur': q.chapters_price_eur,
                        'total_eur': q.total_eur,      # prix avant réduction (audit)
                        'paid_eur': 0,                  # payé (offert)
                        'total_pages': q.total_pages,
                    },
                    'pdf_ctx': pdf_ctx,
                },
            }).execute()
        except Exception as e:
            logger.warning(f'[composer] promo insert failed: {e}')
        # Déclenche le pipeline de génération PDF en arrière-plan
        try:
            import asyncio as _asyncio
            from services.book_engine.pipeline import build_book_pdf_for_session
            _asyncio.create_task(build_book_pdf_for_session(fake_session_id))
        except Exception as e:
            logger.warning(f'[composer] pipeline schedule failed: {e}')
        logger.info(f'[composer] Promo {promo["code"]} applied for {payload.email} → session {fake_session_id}')
        return {
            'url': f'{origin}/composer/succes?session_id={fake_session_id}&promo=1',
            'session_id': fake_session_id,
            'promo_applied': promo['code'],
            'quote': {
                'edition': q.edition, 'edition_label': q.edition_label,
                'edition_price_eur': q.edition_price_eur,
                'chapters_price_eur': q.chapters_price_eur,
                'total_eur': 0, 'original_total_eur': q.total_eur,
                'total_pages': q.total_pages,
            },
        }

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f'{host_url}/api/webhook/stripe'
    stripe_checkout = StripeCheckout(api_key=settings.STRIPE_API_KEY, webhook_url=webhook_url)

    origin = payload.origin_url.rstrip('/')
    success_url = f'{origin}/composer/succes?session_id={{CHECKOUT_SESSION_ID}}'
    cancel_url = f'{origin}/composer'

    # Metadata Stripe (limitée à ~40 clés, ~500 chars/valeur → on sérialise les chapters en CSV)
    chapters_csv = ','.join(pdf_ctx['chapters'])
    metadata = {
        'kind': 'composer_book',
        'product': 'composer_book',
        'edition': q.edition,
        'chapters': chapters_csv[:450],
        'email': payload.email.lower(),
        'total_eur': str(q.total_eur),
        'no_birth_time': '1' if no_birth_time else '0',
    }

    req = CheckoutSessionRequest(
        amount=float(q.total_eur),
        currency=q.currency,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata,
    )
    session = await stripe_checkout.create_checkout_session(req)

    # Trace payment_transactions (source de vérité pour le webhook)
    try:
        sb = get_admin_client()
        sb.table('payment_transactions').insert({
            'session_id': session.session_id,
            'user_email': payload.email.lower(),
            'pack_id': f'composer_{q.edition}',
            'amount': float(q.total_eur),
            'currency': q.currency,
            'credits': 0,
            'status': 'initiated',
            'payment_status': 'unpaid',
            'credits_granted': False,
            'metadata': {
                'kind': 'composer_book',
                'product': 'composer_book',
                'edition': q.edition,
                'chapters': pdf_ctx['chapters'],
                'quote': {
                    'edition_price_eur': q.edition_price_eur,
                    'chapters_price_eur': q.chapters_price_eur,
                    'chapters_subtotal_eur': q.chapters_subtotal_eur,
                    'chapters_cap_applied': q.chapters_cap_applied,
                    'total_eur': q.total_eur,
                    'total_pages': q.total_pages,
                },
                'pdf_ctx': pdf_ctx,
            },
        }).execute()
    except Exception as e:
        logger.warning(f'[composer] payment_transactions insert failed: {e}')

    return {
        'url': session.url,
        'session_id': session.session_id,
        'quote': {
            'edition': q.edition,
            'edition_label': q.edition_label,
            'edition_price_eur': q.edition_price_eur,
            'chapters_price_eur': q.chapters_price_eur,
            'total_eur': q.total_eur,
            'total_pages': q.total_pages,
        },
    }


@router.get('/status/{session_id}')
async def composer_status(session_id: str):
    """Poll pour la page de succès : renvoie l'état de la génération PDF.

    Réponse : {status, pdf_ready, pdf_url, pdf_pages, edition}
    """
    try:
        sb = get_admin_client()
        row = sb.table('payment_transactions').select('*').eq(
            'session_id', session_id
        ).limit(1).execute()
    except Exception as e:
        raise HTTPException(500, f'Supabase read failed: {e}')
    if not row.data:
        raise HTTPException(404, 'session inconnue')
    tx = row.data[0]
    md = tx.get('metadata') or {}
    pdf_status = md.get('pdf_status')  # None | 'success' | 'failed'
    return {
        'status': tx.get('status'),
        'payment_status': tx.get('payment_status'),
        'pdf_status': pdf_status,
        'pdf_ready': pdf_status == 'success',
        'pdf_url': md.get('pdf_supabase_url') or md.get('pdf_path'),
        'pdf_pages': md.get('pdf_pages'),
        'edition': md.get('edition'),
        'chapters': md.get('chapters') or [],
    }


@router.post('/regenerate/{session_id}')
async def composer_regenerate(session_id: str, wait: bool = False):
    """Force la régénération du PDF.

    Par défaut : lance en tâche de fond et retourne immédiatement (pour éviter
    les 502 de Cloudflare sur les longs appels LLM).
    Avec `?wait=true` : bloquant, utile en local pour debug.
    """
    from services.book_engine.pipeline import build_book_pdf_for_session
    if wait:
        diag = await build_book_pdf_for_session(session_id, force=True)
        return diag
    import asyncio as _asyncio
    _asyncio.create_task(build_book_pdf_for_session(session_id, force=True))
    return {'scheduled': True, 'session_id': session_id}


# ═══════════════════════════════════════════════════════════════════
# FLIPBOOK — Rasterization page par page pour /mon-compte/mon-livre
# ═══════════════════════════════════════════════════════════════════
@router.get('/pages/{session_id}/{page_num}.jpg')
async def composer_page_jpg(session_id: str, page_num: int, dpi: int = 130):
    """Rasterise la page N du PDF v2 d'une session en JPEG pour le flipbook.

    Cache local (`/app/backend/assets/book/flipbook_cache/{session_id}/pN.jpg`).
    Réponse : image/jpeg direct (Content-Type + Cache-Control 24h).
    """
    from fastapi.responses import Response as FResponse
    import subprocess
    from pathlib import Path
    if page_num < 1 or page_num > 999:
        raise HTTPException(400, 'page_num invalide (1..999)')

    cache_dir = Path('/app/backend/assets/book/flipbook_cache') / session_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f'p{page_num:03d}_dpi{dpi}.jpg'
    if out.exists():
        return FResponse(out.read_bytes(), media_type='image/jpeg',
                         headers={'Cache-Control': 'public, max-age=86400'})

    # Retrouve le PDF (Supabase Storage URL depuis payment_transactions.metadata)
    try:
        sb = get_admin_client()
        row = sb.table('payment_transactions').select('metadata').eq(
            'session_id', session_id
        ).limit(1).execute()
    except Exception as e:
        raise HTTPException(500, f'lookup fail: {e}')
    if not row.data:
        raise HTTPException(404, 'session inconnue')
    md = row.data[0].get('metadata') or {}
    pdf_url = md.get('pdf_supabase_url') or md.get('pdf_path')
    local_path = md.get('pdf_local_path')
    if local_path and Path(local_path).exists():
        pdf_src = local_path
    elif pdf_url:
        # Télécharge dans un tmp
        import tempfile, urllib.request
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tf:
            with urllib.request.urlopen(pdf_url, timeout=15) as r:
                tf.write(r.read())
            pdf_src = tf.name
    else:
        raise HTTPException(404, 'PDF non disponible pour cette session')

    # Rasterize page N via pdftoppm
    tmp_prefix = str(cache_dir / f'render_{page_num}')
    rc = subprocess.run(
        ['pdftoppm', '-r', str(dpi), '-f', str(page_num), '-l', str(page_num),
         '-jpeg', '-jpegopt', 'quality=82', pdf_src, tmp_prefix],
        capture_output=True, timeout=25,
    )
    if rc.returncode != 0:
        raise HTTPException(500, f'pdftoppm failed: {rc.stderr.decode()[:200]}')
    # pdftoppm crée : {prefix}-NN.jpg (padding 2-3 digits selon nb pages)
    from glob import glob
    produced = glob(f'{tmp_prefix}-*.jpg')
    if not produced:
        raise HTTPException(500, 'pdftoppm n a produit aucun JPG')
    produced[0]
    Path(produced[0]).rename(out)
    return FResponse(out.read_bytes(), media_type='image/jpeg',
                     headers={'Cache-Control': 'public, max-age=86400'})


# ═══════════════════════════════════════════════════════════════════
# LULU — Specs impression pour la page /mon-compte/mon-livre
# ═══════════════════════════════════════════════════════════════════
@router.get('/print-specs/{session_id}')
async def composer_print_specs(session_id: str,
                                edition: str = 'brochee',
                                quantity: int = 1):
    """Retourne dimensions (dos, cover) + estimation prix pour l'édition demandée."""
    from services.book_engine.domain import Edition
    from services.print.lulu_provider import (
        estimate_retail_price_eur,
        validate_manuscript_for_print,
        build_cover_spec,
    )
    try:
        ed = Edition(edition)
    except ValueError:
        raise HTTPException(400, f'Edition inconnue: {edition}')
    if ed not in (Edition.BROCHEE, Edition.RELIEE):
        raise HTTPException(400, 'Print specs uniquement pour brochée/reliée')
    try:
        sb = get_admin_client()
        row = sb.table('payment_transactions').select('metadata').eq(
            'session_id', session_id).limit(1).execute()
    except Exception as e:
        raise HTTPException(500, f'lookup fail: {e}')
    if not row.data:
        raise HTTPException(404, 'session inconnue')
    md = row.data[0].get('metadata') or {}
    pages = md.get('pdf_pages') or 32

    # Validation via un manuscript minimal (on n'a besoin que du nombre de chapitres)
    from services.book_engine.domain import Manuscript, BirthData
    from datetime import datetime, timezone
    m = Manuscript(
        session_id=session_id, user_email='', first_name='',
        birth_data=BirthData(date_iso='1990-01-01', time_hhmm='12:00', city=''),
        astro_data={}, chapters=[], edition=ed,
        created_at=datetime.now(timezone.utc),
    )
    validation = validate_manuscript_for_print(m, ed, pages_hint=pages)
    price = estimate_retail_price_eur(validation.pages, ed, quantity)
    return {
        'validation': validation.to_dict(),
        'price': price,
        'cover_spec': build_cover_spec(validation.pages),
    }
