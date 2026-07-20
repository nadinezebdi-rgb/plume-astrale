"""Route /api/astrosexo/personal — analyse personnalisée AstroSexo.

Utilise Vénus / Mars natales pour générer une lecture relationnelle intime
enrichie via GPT-5.4 (avec question finale).
"""
from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import astrology_io_service as aio
from services.enrich_narrative import enrich_and_ask

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/astrosexo', tags=['astrosexo'])


class AstroSexoRequest(BaseModel):
    first_name: str = ''
    birth_date: str   # 'YYYY-MM-DD'
    birth_time: str   # 'HH:MM'
    latitude: float
    longitude: float
    city: str = ''
    country_code: str = 'FR'


@router.post('/personal')
async def astrosexo_personal(payload: AstroSexoRequest):
    """Analyse personnalisée basée sur Vénus/Mars + Lune."""
    if not payload.birth_date or not payload.birth_time:
        raise HTTPException(400, 'Date et heure de naissance requises.')
    try:
        y, m, d = payload.birth_date[:10].split('-')
        h, mi = payload.birth_time[:5].split(':')
        bd = {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': int(h), 'minute': int(mi),
            'latitude': float(payload.latitude), 'longitude': float(payload.longitude),
        }
        if payload.city:
            bd['city'] = payload.city
        if payload.country_code:
            bd['country_code'] = payload.country_code
    except Exception as e:
        raise HTTPException(400, f'Format date/heure invalide : {e}')

    first_name = (payload.first_name or 'toi').strip() or 'toi'

    # Récupère l'analyse relationnelle (aio.love_languages est déjà @fr_polish)
    love_data = None
    perso_data = None
    try:
        love_data = await aio.love_languages(bd, name=first_name, language='fr')
    except Exception as e:
        logger.warning(f'[astrosexo] love_languages failed: {e}')
    try:
        perso_data = await aio.personality_analysis(bd, name=first_name, language='fr')
    except Exception as e:
        logger.warning(f'[astrosexo] personality failed: {e}')

    # Extraire les infos Vénus / Mars
    natal = None
    try:
        natal = await aio.natal_chart(bd, name=first_name, language='fr')
    except Exception:
        pass

    venus_sign = mars_sign = moon_sign = None
    if natal:
        planets = aio.extract_planets(natal)
        venus = planets.get('venus') or {}
        mars = planets.get('mars') or {}
        moon = planets.get('moon') or {}
        venus_sign = venus.get('sign_fr') or venus.get('sign')
        mars_sign = mars.get('sign_fr') or mars.get('sign')
        moon_sign = moon.get('sign_fr') or moon.get('sign')

    # Composer un texte de base à enrichir (fusion des insights)
    base_parts = []
    if venus_sign:
        base_parts.append(f"Ta Vénus en {venus_sign} révèle ta façon d'aimer et de séduire.")
    if mars_sign:
        base_parts.append(f"Ton Mars en {mars_sign} montre ton feu, ton désir, ta manière d'aborder l'autre.")
    if moon_sign:
        base_parts.append(f"Ta Lune en {moon_sign} raconte tes besoins émotionnels profonds dans l'intimité.")

    if isinstance(love_data, dict):
        summary = love_data.get('summary') or love_data.get('description') or ''
        if isinstance(summary, str) and len(summary) > 30:
            base_parts.append(summary)

    if not base_parts:
        raise HTTPException(502, 'Impossible de générer ton analyse pour le moment.')

    base_text = ' '.join(base_parts)

    # Enrichir avec la couche narrative (long + question finale)
    enriched = await enrich_and_ask(
        base_text,
        context=f'astrosexo_personal_{venus_sign}_{mars_sign}',
        first_name=first_name,
        target_length='long',
    )

    return {
        'success': True,
        'first_name': first_name,
        'venus_sign': venus_sign,
        'mars_sign': mars_sign,
        'moon_sign': moon_sign,
        'analysis': enriched,
        'enrichi': True,
    }
