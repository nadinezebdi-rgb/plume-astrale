"""natal_book_service — Pipeline unifié de génération du PDF Thème Natal.

Produit un PDF « Livre Astral » de 45 à 50 pages, de qualité identique quel que
soit le point d'entrée commercial :

- 24 € oneshot (`services.theme_natal_oneshot_service`)
- 80 cr `/api/astrology/v3/natal/pdf`
- 80 cr `/api/reports/theme-natal/pdf`

Ce service se charge uniquement de PRODUIRE les octets du PDF. Le caller
(route ou webhook) gère la persistance Supabase, les transactions wallet,
l'envoi email, et les métriques métier.

Pipeline :
    1. normalize_birth_data + fetch /charts/natal + /analysis/natal-report
    2. anti-slop guard : refuser si <5 planètes core
    3. enhanced_personal_analysis (aspects/fixed stars, best-effort)
    4. enrich_natal_ultra (11 planètes + synthèse aspects, voix Plume Astrale)
    5. enrich_book_chapters (élément/modalité/trio/12 maisons/aspects/année)
    6. chart wheel SVG → PNG compressé (optionnel)
    7. generate_manuscrit_pdf (ReportLab) via thread pool
    8. output='print' → lulu_interior A5 + bleed 3.175mm
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from services import astrology_io_service as aio

logger = logging.getLogger(__name__)

# Planètes minimales exigées pour qu'un PDF soit livrable sans fallbacks
# trompeurs (bug Nadine Feb 2026 : Lune Poissons alors que réelle en Bélier).
_CORE_PLANETS = ('sun', 'moon', 'mercury', 'venus', 'mars')

_AI_PLANET_KEYS = (
    'soleil', 'lune', 'mercure', 'venus', 'mars',
    'jupiter', 'saturne', 'uranus', 'neptune', 'pluton', 'ascendant',
)

_BOOK_PLANETS_FR_EN = (
    ('Soleil', 'sun'), ('Lune', 'moon'), ('Mercure', 'mercury'),
    ('Vénus', 'venus'), ('Mars', 'mars'), ('Jupiter', 'jupiter'),
    ('Saturne', 'saturn'), ('Uranus', 'uranus'),
    ('Neptune', 'neptune'), ('Pluton', 'pluto'),
)


class IncompleteNatalDataError(RuntimeError):
    """Levée quand astrology-api.io renvoie trop peu de planètes pour générer un PDF honnête."""

    def __init__(
        self,
        msg: str,
        *,
        planets_count: int = 0,
        core_missing: list[str] | None = None,
    ) -> None:
        super().__init__(msg)
        self.planets_count = planets_count
        self.core_missing = core_missing or []


async def generate_enriched_natal_pdf(
    name: str,
    birth_data: dict,
    *,
    no_birth_time: bool = False,
    require_complete: bool = True,
    output: str = 'digital',
    force_refresh: bool = False,
    referral_code: str | None = None,
    referral_link: str | None = None,
    birth_date_iso: str = '',
    language: str = 'fr',
) -> dict:
    """Génère le PDF Thème Natal enrichi (45-50 pages).

    `language`: 'fr' (défaut) ou 'en'. Propagé à astrology-api.io, aux prompts
    GPT (natal_ai_enrichment + natal_book_enrichment) et au renderer.
    """
    if output not in ('digital', 'print'):
        raise ValueError(f"output must be 'digital' or 'print', got {output!r}")

    lang = (language or 'fr').lower()
    if not lang.startswith('en'):
        lang = 'fr'
    else:
        lang = 'en'

    bd = aio.normalize_birth_data(birth_data)
    diag: dict[str, Any] = {
        'name': name,
        'no_birth_time': no_birth_time,
        'output': output,
        'language': lang,
    }

    # 1) Positions planétaires + rapport natal + interprétations
    chart = await aio.natal_chart(bd, name=name, language=lang)
    planets_dict = aio.extract_planets(chart) or {}
    asc_sign_en = aio.extract_ascendant_sign_en(chart)
    natal_report_data = await aio.natal_report(bd, name=name, language=lang)
    interpretations: list = []
    if isinstance(natal_report_data, dict):
        interpretations = (
            natal_report_data.get('interpretations')
            or natal_report_data.get('data', {}).get('interpretations')
            or []
        )
    diag['planets_from_chart'] = len(planets_dict)
    diag['interpretations_count'] = len(interpretations)

    # 2) Anti-slop guard : refuser si <5 planètes core
    core_ok = sum(1 for k in _CORE_PLANETS if k in planets_dict)
    core_missing = [k for k in _CORE_PLANETS if k not in planets_dict]
    diag['planets_core_ok'] = core_ok
    diag['planets_core_missing'] = core_missing
    if core_ok < 5:
        raise IncompleteNatalDataError(
            f'astrology-api.io a retourné {len(planets_dict)} planètes '
            f'(core manquantes: {core_missing}). '
            f'Refus de générer un PDF avec fallbacks trompeurs.',
            planets_count=len(planets_dict),
            core_missing=core_missing,
        )

    # 3) Enhanced analysis (aspects + fixed stars) — best-effort
    enhanced_analysis = await _fetch_enhanced_analysis(bd, name)
    diag['enhanced_aspects_count'] = len((enhanced_analysis or {}).get('aspects') or [])
    diag['enhanced_fixed_stars_count'] = len((enhanced_analysis or {}).get('fixed_stars') or [])

    # 4) Enrichissement AI planétaire (11 planètes + synthèse aspects, voix Plume Astrale)
    ai_result = await _enrich_ai_ultra(name, bd, interpretations, force_refresh, lang)
    diag['ai_source'] = ai_result.get('_source', 'none')
    diag['ai_planet_count'] = sum(1 for k in _AI_PLANET_KEYS if ai_result.get(k))
    diag['v3_raw_count'] = len(ai_result.get('_raw_v3_by_planet') or {})
    diag['is_ultra'] = diag['ai_planet_count'] >= 7 or diag['v3_raw_count'] >= 7

    # 5) Enrichissement livre (élément/modalité/trio/12 maisons/aspects/année)
    # Aspects + maisons réels (chart_data → natal_report → calcul local) : sans eux,
    # le livre racontait « aucun aspect fourni » et les pages maisons restaient vides.
    from services.natal_chart_extract import extract_aspects, extract_houses
    chart_aspects = extract_aspects(chart, natal_report_data, planets_dict)
    chart_houses = [] if no_birth_time else extract_houses(chart, planets_dict)
    diag['chart_aspects_count'] = len(chart_aspects)
    diag['chart_houses_count'] = len(chart_houses)

    book_data = await _build_book_data(
        name, bd, planets_dict, asc_sign_en, chart_aspects, chart_houses, force_refresh, lang,
    )
    diag['book_source'] = (book_data or {}).get('_source', 'none')
    diag['book_element'] = (book_data or {}).get('_em', {}).get('dominant_element')
    diag['book_modality'] = (book_data or {}).get('_em', {}).get('dominant_modality')

    # 6) Chart wheel SVG → PNG compressé — best-effort
    chart_png_bytes = await _render_chart_png(bd, name)
    diag['chart_png_bytes'] = len(chart_png_bytes) if chart_png_bytes else 0

    # 6bis) Illustrations IA (Nano Banana / Gemini) — best-effort, caches on disk.
    # - Ex Libris unique par signature astrale (Soleil / Lune / Asc + prénom)
    # - Vignettes planètes (cache global partagé, 1 génération totale par planète)
    # - Vignette de clôture (cache global)
    from services.natal_book_illustrations import (
        get_or_generate_ex_libris_illustration,
        get_all_planet_illustrations,
        get_or_generate_closing_illustration,
    )
    _sun_fr = aio.sign_to_fr(planets_dict.get('sun', {}).get('sign') or '') or ''
    _moon_fr = aio.sign_to_fr(planets_dict.get('moon', {}).get('sign') or '') or ''
    _asc_fr = ('' if no_birth_time
               else (aio.sign_to_fr(asc_sign_en) if asc_sign_en else ''))
    _user_id = str(birth_data.get('user_id') or '')
    illustrations: dict = {}
    try:
        results = await asyncio.gather(
            get_or_generate_ex_libris_illustration(
                user_id=_user_id, prenom=name,
                sun_sign=_sun_fr, moon_sign=_moon_fr, asc_sign=_asc_fr,
            ),
            get_all_planet_illustrations(),
            get_or_generate_closing_illustration(),
            return_exceptions=True,
        )
        ex_png = results[0] if not isinstance(results[0], Exception) else None
        pl_imgs = results[1] if not isinstance(results[1], Exception) else {}
        cl_png = results[2] if not isinstance(results[2], Exception) else None
        if ex_png:
            illustrations['ex_libris'] = ex_png
        if pl_imgs:
            illustrations['planets'] = pl_imgs
        if cl_png:
            illustrations['closing'] = cl_png
    except Exception as e:
        logger.warning(f'[natal_book_service] illustrations IA KO: {e}')
    diag['illust_ex_libris'] = bool(illustrations.get('ex_libris'))
    diag['illust_closing'] = bool(illustrations.get('closing'))
    diag['illust_planets'] = sorted((illustrations.get('planets') or {}).keys())

    # 7) Normalisation aspects/houses/cusps pour le manuscript builder
    aspects_adapter, houses_adapter, cusps_adapter = _normalize_report_data(
        natal_report_data, chart, enhanced_analysis,
    )
    diag['aspects_count'] = len(aspects_adapter)
    diag['houses_count'] = len(houses_adapter)
    diag['cusps_count'] = len(cusps_adapter)

    # 8) Construction user_data pour l'adaptateur
    def _sign_fr(key: str) -> str:
        p = planets_dict.get(key)
        return aio.sign_to_fr(p.get('sign') or '') if p else ''

    hour = int(bd.get('hour') or 0)
    minute = int(bd.get('minute') or bd.get('min') or 0)
    user_data = {
        'prenom': name,
        'require_complete_book': require_complete,
        'birth_time': '' if no_birth_time else f'{hour:02d}:{minute:02d}',
        'birth_city': str(bd.get('city') or bd.get('location') or ''),
        'birth_date': birth_date_iso,
        'sun_sign': _sign_fr('sun'),
        'moon_sign': _sign_fr('moon'),
        'venus_sign': _sign_fr('venus'),
        'mars_sign': _sign_fr('mars'),
        'ascendant_sign': ''
            if no_birth_time
            else (aio.sign_to_fr(asc_sign_en) if asc_sign_en else ''),
        'no_birth_time': no_birth_time,
        'ai_interpretations': ai_result,
        'enhanced_personal_analysis': enhanced_analysis,
        'houses': chart_houses,
        'language': lang,
    }

    # 9) Génération PDF luxe (ReportLab CPU-bound → thread pool)
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    pdf_bytes = await asyncio.to_thread(
        generate_manuscrit_pdf,
        user_data=user_data,
        planets_data=list(planets_dict.values()),
        chart_png_bytes=chart_png_bytes,
        book_data=book_data,
        referral_code=referral_code,
        referral_link=referral_link,
        aspects_raw=aspects_adapter or None,
        houses_raw=houses_adapter or None,
        house_cusps_raw=cusps_adapter or None,
        illustrations=illustrations or None,
    )

    diag['pdf_bytes'] = len(pdf_bytes)
    pdf_bytes_print = pdf_bytes  # conserve la version avec respirations recto/verso

    # 9.b) Nettoyage des pages vides (pattern "page recto obligatoire" en
    # typographie livre, inutile et laid en export numérique). Appliqué
    # UNIQUEMENT à la version numérique — la version print Lulu garde
    # les pages de respiration nécessaires à l'impression recto/verso.
    try:
        from services.pdf_strip_blanks import strip_blank_pages
        pdf_bytes = await asyncio.to_thread(strip_blank_pages, pdf_bytes)
        diag['pdf_bytes_stripped'] = len(pdf_bytes)
    except Exception as _e:
        logger.warning(f'[natal_book_service] strip_blank_pages skipped: {_e}')

    # 9.c) Contrôle qualité automatique (Lot 4 — Feb 2026) :
    # On vérifie structure, pages vides, prénom en couverture, Ex-Libris
    # et compteur de mots avant envoi. Les échecs bloquants sont loggés
    # en ERROR mais le PDF part quand même — c'est un filet de sécurité,
    # pas un hard-block (évite de rendre le livre indisponible pour un
    # faux positif de QA). Le diag[`qa`] permet aux admins de monitorer.
    try:
        from services.natal_pdf_qa import qa_check_natal_pdf
        qa_mode = 'rich' if book_data and book_data.get('_source') in ('gpt', 'cache') and not no_birth_time else 'planets'
        qa_report = await asyncio.to_thread(
            qa_check_natal_pdf, pdf_bytes, prenom=name, mode=qa_mode,
        )
        diag['qa'] = qa_report.to_dict()
        if not qa_report.passed:
            logger.error(
                f'[natal_book_service] QA FAIL (mode={qa_mode}) '
                f'blocking={qa_report.blocking_issues} warnings={qa_report.warnings}'
            )
        elif qa_report.warnings:
            logger.warning(
                f'[natal_book_service] QA warnings (mode={qa_mode}): {qa_report.warnings}'
            )
    except Exception as _e:
        logger.warning(f'[natal_book_service] qa_check skipped: {_e}')
        diag['qa'] = {'error': str(_e)}

    try:
        # Pattern reconnu par ReportLab pour compter les pages sans parser le PDF.
        diag['pdf_pages'] = (
            pdf_bytes.count(b'/Type /Page') or pdf_bytes.count(b'/Type/Page')
        )
    except Exception:
        diag['pdf_pages'] = None

    result: dict[str, Any] = {'pdf_bytes': pdf_bytes, 'diag': diag}

    # 10) Variante print (Lulu A5 avec bleed) si demandée — part de la
    # version AVEC pages de respiration (nécessaires au recto/verso Lulu).
    if output == 'print':
        from services.print_book_renderer import lulu_interior
        interior_bytes = await asyncio.to_thread(lulu_interior, pdf_bytes_print)
        result['interior_bytes'] = interior_bytes
        diag['interior_bytes'] = len(interior_bytes)
        try:
            from pypdf import PdfReader
            import io
            diag['interior_pages'] = len(PdfReader(io.BytesIO(interior_bytes)).pages)
        except Exception:
            diag['interior_pages'] = None

    return result


# ─── Helpers internes ─────────────────────────────────────────────────────────


async def _fetch_enhanced_analysis(bd: dict, name: str) -> dict | None:
    """Récupère l'analyse enrichie (aspects + fixed stars) — best-effort."""
    try:
        res = await aio.enhanced_personal_analysis(bd, name=name)
        return res if isinstance(res, dict) else None
    except Exception as e:
        logger.warning(f'[natal_book] enhanced analysis unavailable: {e}')
        return None


async def _enrich_ai_ultra(
    name: str, bd: dict, interpretations: list, force_refresh: bool,
    language: str = 'fr',
) -> dict:
    """Appel GPT ULTRA (11 planètes + synthèse aspects) — fallback texte v3 brut si GPT échoue."""
    if not interpretations:
        return {}
    try:
        from services.natal_ai_enrichment import enrich_natal_ultra
        result = await enrich_natal_ultra(
            prenom=name,
            birth_data=bd,
            api_interpretations=interpretations,
            tier='ultra',
            force_refresh=force_refresh,
            language=language,
        )
        return result or {}
    except Exception as e:
        logger.warning(f'[natal_book] AI ultra enrichment failed: {e}')
        return {}


async def _build_book_data(
    name: str,
    bd: dict,
    planets_dict: dict,
    asc_sign_en: str,
    chart_aspects: list,
    chart_houses: list,
    force_refresh: bool,
    language: str = 'fr',
) -> dict | None:
    """Enrichit avec `enrich_book_chapters` : élément/modalité/trio/12 maisons/aspects/année."""
    try:
        from services.natal_book_enrichment import enrich_book_chapters

        aspects_for_book: list[dict] = list(chart_aspects or [])
        houses_for_book: list[dict] = list(chart_houses or [])

        planets_book: list[dict] = []
        for pfr, pen in _BOOK_PLANETS_FR_EN:
            p = planets_dict.get(pen) or {}
            sign = aio.sign_to_fr(p.get('sign', '')) if p.get('sign') else ''
            if sign:
                planets_book.append({'name': pfr, 'sign': sign})

        natal_data_for_book = {
            'prenom': name,
            'sun_sign': aio.sign_to_fr((planets_dict.get('sun') or {}).get('sign', '')),
            'moon_sign': aio.sign_to_fr((planets_dict.get('moon') or {}).get('sign', '')),
            'asc_sign': aio.sign_to_fr(asc_sign_en) if asc_sign_en else '',
            'planets': planets_book,
            'aspects': aspects_for_book,
            'houses': houses_for_book,
        }
        return await enrich_book_chapters(
            prenom=name,
            birth_data=bd,
            natal_data=natal_data_for_book,
            force_refresh=force_refresh,
            language=language,
        )
    except Exception as e:
        logger.warning(f'[natal_book] book enrichment failed: {e}')
        return None


async def _render_chart_png(bd: dict, name: str) -> bytes | None:
    """Rend la carte du ciel SVG → PNG → JPEG compressé (via thread, CPU-bound)."""
    try:
        svg_str = await aio.chart_svg_render(bd, name=name, theme='light', language='fr')
        if not svg_str:
            return None
        from services.svg_utils import resolve_svg_css_vars, force_parchment_background
        import cairosvg
        # Ordre critique : force_parchment_background doit s'exécuter AVANT
        # resolve_svg_css_vars (sinon les variables Kerykeion ont déjà été
        # inlined et il n'y a plus rien à ré-écrire).
        svg_resolved = resolve_svg_css_vars(force_parchment_background(svg_str))
        png_bytes = await asyncio.to_thread(
            cairosvg.svg2png,
            bytestring=svg_resolved.encode('utf-8'),
            output_width=1600,
        )
        if png_bytes:
            from services.pdf_luxury_helpers import compress_image_bytes
            png_bytes = await asyncio.to_thread(
                compress_image_bytes, png_bytes, 1400, 90, True,
            )
        return png_bytes
    except Exception as e:
        logger.warning(f'[natal_book] chart wheel unavailable: {e}')
        return None


def _normalize_report_data(
    natal_report_data: Any,
    chart: Any,
    enhanced_analysis: dict | None,
) -> tuple[list, list, list]:
    """Normalise aspects/houses/cusps pour le manuscript builder.

    Garantit :
      - aspects : clés `aspecting_planet`, `aspected_planet`, `type`, `orb`
      - houses : clés `number`, `sign` (FR), `planets`
      - cusps : clés `house`, `sign` (nom long FR), `degree`
    """
    aspects_adapter: list[dict] = []
    houses_adapter: list[dict] = []
    cusps_adapter: list[dict] = []
    try:
        if isinstance(natal_report_data, dict):
            aspects_src = (
                natal_report_data.get('aspects')
                or natal_report_data.get('data', {}).get('aspects')
                or []
            )
            for a in aspects_src[:40]:
                if isinstance(a, dict):
                    aspects_adapter.append({
                        'aspecting_planet': (
                            a.get('planet1') or a.get('p1') or a.get('aspecting_planet')
                        ),
                        'aspected_planet': (
                            a.get('planet2') or a.get('p2') or a.get('aspected_planet')
                        ),
                        'type': a.get('aspect') or a.get('type') or a.get('name'),
                        'orb': a.get('orb') or a.get('orb_deg') or a.get('degree'),
                    })
            houses_src = (
                natal_report_data.get('houses')
                or natal_report_data.get('data', {}).get('houses')
                or []
            )
            for i, h in enumerate(houses_src[:12]):
                if isinstance(h, dict):
                    houses_adapter.append({
                        'number': h.get('number') or h.get('num') or (i + 1),
                        'sign': aio.sign_to_fr(h.get('sign') or '') if h.get('sign') else '',
                        'planets': h.get('planets') or h.get('planets_in_house') or [],
                    })
        cusps_src = ((chart or {}).get('chart_data') or {}).get('house_cusps') or []
        for i, c in enumerate(cusps_src[:12]):
            if isinstance(c, dict):
                cusps_adapter.append({
                    'house': c.get('house') or (i + 1),
                    'sign': aio.expand_sign(c.get('sign') or ''),
                    'degree': c.get('degree') or c.get('normDegree'),
                })
    except Exception as e:
        logger.warning(f'[natal_book] normalize report data failed: {e}')

    # Fallback aspects via enhanced_analysis si l'API report ne renvoie rien
    if not aspects_adapter and enhanced_analysis:
        for a in (enhanced_analysis.get('aspects') or [])[:40]:
            if isinstance(a, dict):
                aspects_adapter.append({
                    'aspecting_planet': a.get('planet1') or a.get('aspecting_planet'),
                    'aspected_planet': a.get('planet2') or a.get('aspected_planet'),
                    'type': a.get('aspect') or a.get('type') or a.get('name'),
                    'orb': a.get('orb') or a.get('orb_deg'),
                })

    return aspects_adapter, houses_adapter, cusps_adapter
