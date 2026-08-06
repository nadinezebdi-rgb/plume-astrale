"""
Routes /api/reports — Gestion des rapports archivés par utilisateur.

  GET  /api/reports               → liste des rapports de l'utilisateur connecté
  GET  /api/reports/{id}/pdf      → re-téléchargement d'un rapport archivé
  POST /api/reports/{type}/pdf    → génération + archivage d'un rapport PDF
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from middleware.auth import get_current_user
from services import wallet_service
from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/reports', tags=['reports'])

# ─── Types supportés ──────────────────────────────────────────────────────────
REPORT_TYPES = {
    'karma-destin':       {'label': 'Karma & Destin',       'credits': 20},
    'numerologie':        {'label': 'Numérologie',           'credits': 15},
    'theme-natal':        {'label': 'Thème Natal',           'credits': 80},
    'revolution-solaire': {'label': 'Révolution Solaire',    'credits': 20},
    'compatibilite':      {'label': 'Compatibilité',         'credits': 20},
    'love-languages':     {'label': "Langages d'Amour",      'credits': 10},
}


# ─── Requête POST ─────────────────────────────────────────────────────────────
class ReportPdfRequest(BaseModel):
    inputs: Optional[dict] = None  # données optionnelles complémentaires


# ─── GET /api/reports ─────────────────────────────────────────────────────────
@router.get('')
async def list_reports(current_user: dict = Depends(get_current_user)):
    """Retourne la liste des rapports archivés de l'utilisateur connecté."""
    try:
        sb = get_admin_client()
        res = (
            sb.table('user_reports')
            .select('id, type, titre, created_at, pdf_path')
            .eq('user_id', current_user['id'])
            .order('created_at', desc=True)
            .execute()
        )
        return {'reports': res.data or []}
    except Exception as e:
        logger.error(f'[reports] list error: {e}')
        raise HTTPException(status_code=500, detail='Erreur lors de la récupération des rapports.')


# ─── GET /api/reports/{id}/pdf ───────────────────────────────────────────────
@router.get('/{report_id}/pdf')
async def get_report_pdf(report_id: str, current_user: dict = Depends(get_current_user)):
    """Re-télécharge le PDF d'un rapport archivé."""
    try:
        sb = get_admin_client()
        res = (
            sb.table('user_reports')
            .select('*')
            .eq('id', report_id)
            .eq('user_id', current_user['id'])
            .maybe_single()
            .execute()
        )
        row = res.data if res else None
    except Exception as e:
        logger.error(f'[reports] fetch error: {e}')
        raise HTTPException(status_code=500, detail='Erreur lors de la récupération du rapport.')

    if not row:
        raise HTTPException(status_code=404, detail='Rapport introuvable.')

    pdf_path = row.get('pdf_path', '')
    if not pdf_path:
        raise HTTPException(status_code=404, detail='PDF non disponible pour ce rapport.')

    try:
        sb = get_admin_client()
        # pdf_path is stored as bucket path like "karma/abc.pdf"
        pdf_bytes = sb.storage.from_('reports').download(pdf_path)
    except Exception as e:
        logger.error(f'[reports] download error: {e}')
        raise HTTPException(status_code=502, detail='Impossible de télécharger le PDF.')

    report_type = row.get('type', 'rapport')
    titre = row.get('titre', 'rapport')
    filename = f"{report_type}-{titre}.pdf".replace(' ', '-').lower()

    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        },
    )


# ─── POST /api/reports/{type}/pdf ────────────────────────────────────────────
@router.post('/{report_type}/pdf')
async def generate_report_pdf(
    report_type: str,
    payload: ReportPdfRequest,
    current_user: dict = Depends(get_current_user),
):
    """Génère un PDF pour le type de rapport demandé, l'archive et le retourne."""
    if report_type not in REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Type de rapport non supporté. Types disponibles : {', '.join(REPORT_TYPES)}",
        )

    meta = REPORT_TYPES[report_type]
    credits_cost = meta['credits']
    titre = meta['label']

    # ── Profil utilisateur ───────────────────────────────────────────────────
    profile = await wallet_service.get_profile(current_user['id'])
    name = profile.get('prenom') or 'Voyageur'
    birth_date_iso = profile.get('birth_date') or profile.get('dateNaissance') or ''

    # ── Paywall ──────────────────────────────────────────────────────────────
    await wallet_service.charge_or_premium(
        current_user['id'], f'report_pdf_{report_type}', credits_cost,
        f'{titre} PDF',
    )

    # ── Génération du PDF selon le type ──────────────────────────────────────
    pdf_bytes: bytes | None = None
    try:
        pdf_bytes = await _generate_pdf(report_type, name, birth_date_iso, profile, payload.inputs or {})
    except Exception as e:
        # Remboursement si échec
        try:
            await wallet_service.add_credits(
                current_user['id'], credits_cost,
                f'Remboursement {titre} PDF (echec)', tx_type='refund',
            )
        except Exception:
            pass
        logger.error(f'[reports] PDF generation error ({report_type}): {e}')
        raise HTTPException(status_code=502, detail=f'Génération PDF échouée : {e}')

    if not pdf_bytes:
        try:
            await wallet_service.add_credits(
                current_user['id'], credits_cost,
                f'Remboursement {titre} PDF (vide)', tx_type='refund',
            )
        except Exception:
            pass
        raise HTTPException(status_code=502, detail='Génération PDF échouée (résultat vide).')

    # ── Stockage Supabase Storage ─────────────────────────────────────────────
    file_name = f'{uuid.uuid4().hex[:16]}.pdf'
    storage_path = f'{report_type}/{file_name}'
    pdf_path_stored = ''
    try:
        sb = get_admin_client()
        sb.storage.from_('reports').upload(
            storage_path,
            pdf_bytes,
            {'content-type': 'application/pdf'},
        )
        pdf_path_stored = storage_path
    except Exception as e:
        logger.warning(f'[reports] storage upload failed (PDF still returned): {e}')

    # ── Persistance en base ───────────────────────────────────────────────────
    try:
        sb = get_admin_client()
        sb.table('user_reports').insert({
            'user_id': current_user['id'],
            'type': report_type,
            'titre': f'{titre} — {name}',
            'inputs': payload.inputs or {},
            'pdf_path': pdf_path_stored,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        logger.warning(f'[reports] DB insert failed: {e}')

    filename = f'{report_type}-{name}.pdf'.lower()
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-store',
        },
    )


# ─── Dispatcher de génération PDF ────────────────────────────────────────────
async def _generate_pdf(
    report_type: str,
    name: str,
    birth_date_iso: str,
    profile: dict,
    inputs: dict,
) -> bytes:
    """Appelle le générateur PDF adapté au type de rapport."""

    if report_type == 'karma-destin':
        from services import astrology_io_service as aio
        from services.karma_destin_pdf import generate_karma_destin_pdf_ai
        bd = aio.parse_profile(profile)
        if not bd:
            raise ValueError('Données natales incomplètes.')
        karmic_data = await aio.karmic_analysis(bd, name=name, language='fr')
        return await generate_karma_destin_pdf_ai(
            first_name=name,
            birth_date_iso=birth_date_iso,
            karmic_data=karmic_data,
        )

    if report_type == 'numerologie':
        from services import astrology_io_service as aio
        from services.numerologie_pdf import generate_numerologie_pdf_ai
        bd = aio.parse_profile(profile)
        if not bd:
            raise ValueError('Données natales incomplètes.')
        num_data = await aio.numerology_core_numbers(bd, name=name, language='fr') or {}
        personal_year = await aio.numerology_personal_year(bd, name=name, language='fr')
        forecast = await aio.numerology_forecast(bd, name=name, language='fr')
        return await generate_numerologie_pdf_ai(
            first_name=name,
            birth_date_iso=birth_date_iso,
            numerology_data=num_data,
            personal_year_data=personal_year,
            forecast_data=forecast,
        )

    if report_type == 'theme-natal':
        from services import astrology_io_service as aio
        from services.natal_pdf_adapter import generate_manuscrit_pdf
        bd = aio.parse_profile(profile)
        if not bd:
            raise ValueError('Données natales incomplètes.')
        chart = await aio.natal_chart(bd, name=name, language='fr')
        planets_dict = aio.extract_planets(chart)
        asc_sign_en = aio.extract_ascendant_sign_en(chart)

        def _sign_fr(planet_key: str) -> str:
            p = planets_dict.get(planet_key)
            return aio.sign_to_fr(p.get('sign') or '') if p else ''

        user_data = {
            'prenom': name,
            'birth_date': birth_date_iso,
            'sun_sign': _sign_fr('sun'),
            'moon_sign': _sign_fr('moon'),
            'venus_sign': _sign_fr('venus'),
            'mars_sign': _sign_fr('mars'),
            'ascendant_sign': aio.sign_to_fr(asc_sign_en) if asc_sign_en else '',
        }
        return generate_manuscrit_pdf(
            user_data=user_data,
            planets_data=list(planets_dict.values()),
        )

    if report_type == 'revolution-solaire':
        from services import astrology_io_service as aio
        from services.natal_pdf_adapter import generate_manuscrit_pdf
        bd = aio.parse_profile(profile)
        if not bd:
            raise ValueError('Données natales incomplètes.')
        ret_year = inputs.get('return_year') or datetime.now(timezone.utc).year
        report = await aio.solar_return_report(bd, ret_year, name=name, language='fr')
        chart = await aio.natal_chart(bd, name=name, language='fr')
        planets_dict = aio.extract_planets(chart)
        user_data = {
            'prenom': name,
            'birth_date': birth_date_iso,
            'sun_sign': '',
            'report_data': report,
        }
        return generate_manuscrit_pdf(
            user_data=user_data,
            planets_data=list(planets_dict.values()),
        )

    if report_type == 'love-languages':
        from services import astrology_io_service as aio
        from services.natal_pdf_adapter import generate_manuscrit_pdf
        bd = aio.parse_profile(profile)
        if not bd:
            raise ValueError('Données natales incomplètes.')
        chart = await aio.natal_chart(bd, name=name, language='fr')
        planets_dict = aio.extract_planets(chart)
        user_data = {
            'prenom': name,
            'birth_date': birth_date_iso,
        }
        return generate_manuscrit_pdf(
            user_data=user_data,
            planets_data=list(planets_dict.values()),
        )

    if report_type == 'compatibilite':
        from services.compatibility_pdf_generator import generate_compatibility_pdf
        person1 = inputs.get('person1', {'name': name, 'sign': ''})
        person2 = inputs.get('person2', {'name': 'Partenaire', 'sign': ''})
        return generate_compatibility_pdf(person1=person1, person2=person2)

    raise ValueError(f'Générateur non implémenté pour : {report_type}')
