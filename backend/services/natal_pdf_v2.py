"""
natal_pdf_v2 — Thème Natal Plume Astrale (rendu standard uniforme).

Refactor 2026-02-22 :
  - PLUS AUCUNE page 1-ligne (glyph/waouh/teaser séparés supprimés).
  - CHAQUE page planétaire = 1 page DENSE : header + image planète + dialogue + analyse.
  - Grilles 2×2 de photos comme séparateurs thématiques (personnelles / sociales / générationnelles).
  - Rendu UNIFORME peu importe si l'AI a rempli 5 ou 12 sections (fallback statique dense).
  - Suit strictement les données de l'API v3 astrology-api.io : les positions viennent
    de `planets_data` (dict par clé anglaise sun/moon/…) et les interprétations viennent
    de `natal_data['planets'][*].analysis` (rempli par natal_pdf_adapter à partir de
    natal_ai_enrichment.enrich_natal_ultra OU fallback statique par signe).
"""
from __future__ import annotations
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from services.pdf_luxury_theme import (
    luxury_styles, luxury_bg,
    cover_page, chapter_illustration, chart_wheel_page,
    planet_dense_page, emotional_ending,
)
from services.pdf_book_pages import (
    copyright_page, table_of_contents_page,
    element_dominant_page, modality_dominant_page,
    trio_cross_analysis_page, aspects_group_page, house_detail_page,
    colophon_page,
    # Nouvelles pages — refonte "Thème Natal 50 pages" (Lot 2 — Feb 2026)
    method_intro_page, birth_data_page, chart_legend_page, personal_synthesis_page,
    transversal_synthesis_page, conclusion_page, glossary_technical_page,
    aspects_opening_page, section_divider_page,
)
from services.natal_ex_libris import ex_libris_page
from services import library_images as libimg
from services.natal_fallback_texts import with_fallback as _wf, headline_with_fallback as _hf

# Métadonnées visuelles par planète : glyphe + dialogue psychologique + slug image
PLANET_META = {
    'Soleil':    {'glyph': '☉', 'dialogue': "As-tu remarqué que tu donnes énormément aux autres ? Mais acceptes-tu vraiment de recevoir ?"},
    'Lune':      {'glyph': '☽', 'dialogue': "Il y a une émotion qui revient depuis l'enfance. Tu la reconnais, n'est-ce pas ?"},
    'Mercure':   {'glyph': '☿', 'dialogue': "Tu réfléchis souvent à voix basse, comme si tu essayais d'organiser un monde intérieur trop vaste pour un seul cerveau."},
    'Vénus':     {'glyph': '♀', 'dialogue': "Tu attires les personnes qui ont besoin d'être sauvées. Et si, cette fois, tu choisissais quelqu'un qui te comble sans effort ?"},
    'Mars':      {'glyph': '♂', 'dialogue': "Il y a une colère ancienne en toi. Elle n'est pas ta faiblesse — c'est ton carburant sacré."},
    'Jupiter':   {'glyph': '♃', 'dialogue': "Tu doutes de ta chance. Et pourtant, chaque fois que tu t'ouvres à l'inconnu, le ciel s'aligne."},
    'Saturne':   {'glyph': '♄', 'dialogue': "Ce que tu prends pour un plafond, c'est en réalité une fondation."},
    'Uranus':    {'glyph': '♅', 'dialogue': "Ce que tu appelles instabilité, tes ancêtres l'appelaient génie. C'est ta manière de mettre le monde à jour."},
    'Neptune':   {'glyph': '♆', 'dialogue': "Tu as cette sensibilité : sentir avant de voir. Ce n'est pas de la fuite — c'est une intuition qui n'a pas encore trouvé ses mots."},
    'Pluton':    {'glyph': '♇', 'dialogue': "Ce que tu as traversé de plus dur te prépare à voir ce que personne ne veut regarder. C'est ta force silencieuse."},
    'Ascendant': {'glyph': '⇑', 'dialogue': "Les autres perçoivent en toi une force plus grande que celle que tu ressens. Et cette impression n'est pas fausse."},
}

_PLANET_NAMES_FR = {
    'sun': 'Soleil', 'moon': 'Lune', 'mercury': 'Mercure', 'venus': 'Vénus',
    'mars': 'Mars', 'jupiter': 'Jupiter', 'saturn': 'Saturne',
    'uranus': 'Uranus', 'neptune': 'Neptune', 'pluto': 'Pluton', 'ascendant': 'Ascendant',
    'mean_node': 'Nœud moyen', 'true_node': 'Nœud vrai',
    'part_of_fortune': 'Part de Fortune', 'part_of_spirit': "Part d'Esprit",
}
_ASPECT_NAMES_FR = {
    'conjunction': 'conjonction', 'opposition': 'opposition', 'trine': 'trigone',
    'square': 'carré', 'sextile': 'sextile', 'quincunx': 'quinconce',
}
_LUNAR_PHASES_FR = {
    'new moon': 'Nouvelle Lune', 'waxing crescent': 'Premier croissant',
    'first quarter': 'Premier quartier', 'waxing gibbous': 'Gibbeuse croissante',
    'full moon': 'Pleine Lune', 'waning gibbous': 'Gibbeuse décroissante',
    'last quarter': 'Dernier quartier', 'waning crescent': 'Dernier croissant',
}
_HOUSE_NAMES_FR = {
    'first_house': 'Maison I', 'second_house': 'Maison II', 'third_house': 'Maison III',
    'fourth_house': 'Maison IV', 'fifth_house': 'Maison V', 'sixth_house': 'Maison VI',
    'seventh_house': 'Maison VII', 'eighth_house': 'Maison VIII', 'ninth_house': 'Maison IX',
    'tenth_house': 'Maison X', 'eleventh_house': 'Maison XI', 'twelfth_house': 'Maison XII',
}


def _enhanced_personal_analysis_sections(analysis: Optional[dict], no_birth_time: bool = False) -> list[tuple[str, str]]:
    """Build concise factual French sections from Astrology API enrichment data."""
    if not isinstance(analysis, dict):
        return []

    from html import escape
    from services.astrology_io_service import sign_to_fr

    def safe(value) -> str:
        return escape(str(value), quote=False)

    def sign(value) -> str:
        from services.astrology_io_service import expand_sign
        return safe(sign_to_fr(expand_sign(str(value or ''))))

    def degree(value) -> str:
        try:
            return f'{float(value):.2f}'.replace('.', ',') + '°'
        except (TypeError, ValueError):
            return ''

    def planet_name(value) -> str:
        key = str(value or '').strip().lower().replace(' ', '_')
        return _PLANET_NAMES_FR.get(key, safe(value or ''))

    def house_name(value) -> str:
        key = str(value or '').strip().lower().replace(' ', '_')
        return _HOUSE_NAMES_FR.get(key, safe(str(value or '').replace('_', ' ')))

    cycles = []
    lunar = analysis.get('lunar_phase') or {}
    if lunar:
        phase_name = str(lunar.get('phase_name') or '')
        phase = _LUNAR_PHASES_FR.get(phase_name.lower(), safe(phase_name))
        metrics = []
        if lunar.get('illumination_percent') is not None:
            metrics.append(f"{safe(lunar['illumination_percent'])} % éclairée")
        if lunar.get('moon_age_days') is not None and not no_birth_time:
            metrics.append(f"âge lunaire : {safe(lunar['moon_age_days'])} jours")
        label = 'Phase lunaire estimée pour la date' if no_birth_time else 'Phase lunaire à la naissance'
        cycles.append(f"<b>{label} :</b> {phase}" + (f" ({', '.join(metrics)})" if metrics else ''))

    chronocrator = analysis.get('chronocrator') or {}
    if chronocrator and not no_birth_time:
        method = str(chronocrator.get('method') or '')
        method_fr = 'Profection annuelle' if 'profection' in method.lower() else safe(method or 'Cycle annuel')
        details = []
        if chronocrator.get('sign'):
            details.append(f"signe activé : {sign(chronocrator['sign'])}")
        if chronocrator.get('ruler'):
            details.append(f"maître : {planet_name(chronocrator['ruler'])}")
        themes = [_PLANET_NAMES_FR.get(str(theme).lower(), safe(str(theme).replace('_', ' ')))
                  for theme in (chronocrator.get('house_themes') or [])[:4]]
        if themes:
            details.append(f"thèmes : {', '.join(themes)}")
        if details:
            cycles.append(f"<b>{method_fr} :</b> {' ; '.join(details)}")

    life_areas_fr = {
        'career_success': 'réussite professionnelle', 'creative_expression': 'expression créative',
        'leadership': 'leadership', 'relationships': 'relations', 'family': 'famille',
        'personal_growth': 'évolution personnelle', 'spirituality': 'spiritualité',
    }
    life_areas = [life_areas_fr.get(str(area).lower(), safe(str(area).replace('_', ' ')))
                  for area in (analysis.get('life_areas') or [])[:5]]
    if life_areas:
        cycles.append(f"<b>Domaines mis en relief :</b> {', '.join(life_areas)}")

    placements = []
    for point in analysis.get('planets') or []:
        if not isinstance(point, dict):
            continue
        key = str(point.get('name') or '').strip().lower().replace(' ', '_')
        if key not in _PLANET_NAMES_FR:
            continue
        details = []
        if point.get('sign'):
            details.append(sign(point['sign']))
        position = degree(point.get('position'))
        if position:
            details.append(position)
        if not no_birth_time and point.get('house'):
            details.append(house_name(point['house']))
        if point.get('retrograde') is True:
            details.append('rétrograde')
        if details:
            placements.append(f"{planet_name(key)} : {' · '.join(details)}")
    if placements:
        cycles.append(f"<b>Positions précises :</b> {' ; '.join(placements[:14])}")

    signatures = []
    for aspect in (analysis.get('aspects') or [])[:6]:
        if not isinstance(aspect, dict):
            continue
        aspect_points = {
            str(aspect.get('planet_a') or '').strip().lower(),
            str(aspect.get('planet_b') or '').strip().lower(),
        }
        if no_birth_time and aspect_points.intersection({'moon', 'ascendant'}):
            continue
        aspect_type = _ASPECT_NAMES_FR.get(
            str(aspect.get('aspect_type') or '').lower(), safe(aspect.get('aspect_type') or 'aspect'),
        )
        parts = [f"{planet_name(aspect.get('planet_a'))} {aspect_type} {planet_name(aspect.get('planet_b'))}"]
        orb = degree(aspect.get('orb'))
        if orb:
            parts.append(f'orbe {orb}')
        if aspect.get('applying') is True:
            parts.append('en formation')
        elif aspect.get('applying') is False:
            parts.append('séparant')
        signatures.append(' — '.join(parts))
    if signatures:
        signatures.insert(0, '<b>Aspects les plus précis :</b>')

    condition_labels = {
        'domicile': 'en domicile', 'exaltation': 'en exaltation',
        'exile': 'en exil', 'fall': 'en chute', 'retrograde': 'rétrograde',
        'combust': 'combuste', 'cazimi': 'en cazimi',
    }
    conditions = []
    for point in analysis.get('planets') or []:
        if not isinstance(point, dict):
            continue
        active = []
        for section in ('dignities', 'debilities', 'conditions'):
            for key, value in (point.get(section) or {}).items():
                if value is True and key in condition_labels:
                    active.append(condition_labels[key])
        if active:
            conditions.append(f"{planet_name(point.get('name'))} : {', '.join(active)}")
    if conditions:
        signatures.append('<b>Conditions planétaires :</b>')
        signatures.extend(conditions[:5])

    fixed_stars = []
    for star in (analysis.get('fixed_stars') or [])[:3]:
        if not isinstance(star, dict):
            continue
        if no_birth_time and str(star.get('planet') or '').strip().lower() in {'moon', 'ascendant'}:
            continue
        orb = degree(star.get('orb'))
        detail = f"{safe(star.get('star') or 'Étoile fixe')} en lien avec {planet_name(star.get('planet'))}"
        fixed_stars.append(detail + (f' (orbe {orb})' if orb else ''))
    if fixed_stars:
        signatures.append(f"<b>Étoiles fixes proches :</b> {' ; '.join(fixed_stars)}")

    pages = []
    if cycles:
        pages.append(('Les rythmes de ton ciel', '<br/>'.join(cycles)))
    if signatures:
        pages.append(('Les signatures précises', '<br/>'.join(signatures)))
    return pages


def _planet_image_path(planet_fr: str) -> Optional[str]:
    """Retourne le chemin local de l'image de la planète (bibliothèque Supabase).

    Pour l'Ascendant → on prend l'image du signe zodiacal correspondant (fallback à ciel_zodiaque).
    """
    if planet_fr == 'Ascendant':
        return None  # traité côté grille (avec le signe)
    return libimg.planet(planet_fr, size=512)


def _sign_image_path(sign_fr: str) -> Optional[str]:
    """Retourne le chemin local de l'image du signe zodiacal."""
    return libimg.sign(sign_fr, size=512)


def _grid_cells_from_planets(planets: list, indices: list) -> list:
    """Construit 4 cellules {image, label, sublabel} à partir de la liste de planètes."""
    cells = []
    for i in indices:
        if i >= len(planets):
            cells.append({'image': None, 'label': '', 'sublabel': ''})
            continue
        p = planets[i]
        name = p.get('name', '')
        sign = p.get('sign', '')
        img_path = _planet_image_path(name) if name != 'Ascendant' else _sign_image_path(sign)
        cells.append({'image': img_path, 'label': name, 'sublabel': sign})
    return cells


def build_natal_pdf_v2(prenom: str, birth_date: str, natal_data: dict,
                        chart_png_bytes: bytes | None = None,
                        book_data: Optional[dict] = None,
                        referral_code: Optional[str] = None,
                        referral_link: Optional[str] = None,
                        ex_libris_citation: Optional[str] = None,
                        birth_time_fr: Optional[str] = None,
                        birth_place: Optional[str] = None) -> bytes:
    """Génère le Thème Natal Plume Astrale — VERSION LIVRE (38-46 pages).

    natal_data attend :
        {
          'sun_sign': 'Cancer', 'moon_sign': 'Poissons', 'ascendant_sign': 'Vierge',
          'planets': [
            {'name': 'Soleil', 'sign': 'Cancer', 'analysis': '...long texte...'},
            ...11 planètes en mode Ultra, 5 en mode Legacy...
          ],
          'synthese_aspects': '<optionnel, texte AI sur les aspects>',
          'tier': 'ultra' | 'legacy',
        }
    chart_png_bytes : PNG binaire de la carte du ciel.
    book_data : dict retourné par natal_book_enrichment.enrich_book_chapters
                — si présent, ajoute front matter + parties + maisons + épilogue.
    referral_code / referral_link : injectés dans le colophon final."""
    styles = luxury_styles()

    from services.pdf_multipass_toc import build_with_toc, chapter_marker

    def _build_story(page_map):
        story = []
        def _pg(cid, fb=None):
            return page_map.get(cid, fb) if page_map is not None else fb

        planets = natal_data.get('planets', []) or []
        sun_sign = natal_data.get('sun_sign', '')
        moon_sign = natal_data.get('moon_sign', '')
        asc_sign = natal_data.get('ascendant_sign', '')
        # §V audit marque : édition sans ascendant/maisons quand l'heure est absente
        no_birth_time = bool(natal_data.get('no_birth_time'))

        # Format FR de la date (utilisé plusieurs fois)
        _MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        try:
            _y, _m, _d = birth_date.split('-')
            date_fr = f"{int(_d)} {_MOIS_FR[int(_m) - 1]} {_y}"
            _birth_month = int(_m)
        except Exception:
            date_fr = birth_date
            _birth_month = None

        bd = bool(book_data and book_data.get('_source') in ('gpt', 'cache'))

        # §V audit marque Feb 2026 : sans heure de naissance, on désactive le
        # mode livre riche qui repose sur Ascendant, Trio, 12 Maisons — toutes
        # ces sections seraient fausses. On garde uniquement les 10 planètes
        # commentées (Soleil, Lune, Mercure, Vénus, Mars, Jupiter, Saturne,
        # Uranus, Neptune, Pluton) et le colophon "Édition des Planètes".
        if no_birth_time:
            bd = False

        # ══════════════════════════════════════════════════════════════
        # REFONTE Feb 2026 — Colonne vertébrale "Thème Natal 50 pages"
        # ----------------------------------------------------------------
        # Section 1 (p.1–4)   : Couverture, mentions, sommaire, méthode
        # Section 2 (p.5–8)   : Données naissance, roue, légende, synthèse perso
        # Section 3 (p.9–12)  : Trio Soleil-Lune-Asc, élément, modalité, croisés
        # Section 4 (p.13–26) : Ouverture + 11 planètes + Nœuds/Chiron
        # Section 5 (p.27–36) : Ouverture + 12 maisons
        # Section 6 (p.37–44) : Ouverture + 3 groupes d'aspects + signatures
        # Section 7 (p.45–48) : 4 pages Synthèse transversale
        # Section 8 (p.49–50) : Conclusion + Glossaire & repères techniques
        # ══════════════════════════════════════════════════════════════

        # ── Section 1 — Page 1 : Couverture ──────────────────────────
        cover_page(story, styles, prenom=prenom,
                   subtitle='Ton ciel de naissance, dévoilé.',
                   illustration_slug='ciel_zodiaque',
                   sun_sign=sun_sign,
                   birth_month=_birth_month)

        # Compteurs utilitaires pour la synthèse personnelle (page 8)
        _aspect_count = len(natal_data.get('aspects') or []) or (0 if not natal_data.get('synthese_aspects') else 0)
        _active_houses = 0
        for _h in (natal_data.get('houses') or []):
            if (_h or {}).get('planets_in_house'):
                _active_houses += 1
        _dominant_element = (book_data or {}).get('_em', {}).get('dominant_element') if bd else None
        _dominant_modality = (book_data or {}).get('_em', {}).get('dominant_modality') if bd else None
        _birth_time = natal_data.get('birth_time') or natal_data.get('birth_hour') or ''
        _birth_place = (natal_data.get('birth_place')
                        or natal_data.get('birth_city')
                        or natal_data.get('location') or '')

        if bd:
            # ── Section 1 — Page 2 : Mentions légales + éphéméride ───
            copyright_page(story, styles, prenom, date_fr)

            # ── Section 1 — Page 3 : Ex-Libris (signature bibliophile) ─
            # Citation GPT-6 Luna (~60 mots) + illustration bibliothèque.
            # Fallback vers citation statique si la citation Luna est absente.
            ex_libris_page(
                story,
                prenom=prenom,
                birth_date=birth_date,
                sun_sign=sun_sign,
                moon_sign=moon_sign,
                asc_sign=None if no_birth_time else asc_sign,
                no_birth_time=no_birth_time,
                citation=ex_libris_citation or None,
                birth_time_fr=birth_time_fr,
                birth_place=birth_place,
            )

            # ── Section 1 — Page 4 : Sommaire dynamique (1 page) ────
            toc_entries = [
                {'type': 'part', 'label': 'Section 1 — Ouverture',                 'page': _pg('sec1', 1)},
                {'type': 'part', 'label': 'Section 2 — Ton ciel en ouverture',     'page': _pg('sec2')},
                {'type': 'part', 'label': 'Section 3 — Les piliers',               'page': _pg('sec3')},
                {'type': 'part', 'label': 'Section 4 — Tes planètes',              'page': _pg('sec4')},
                {'type': 'part', 'label': 'Section 5 — Tes douze maisons',         'page': _pg('sec5')},
                {'type': 'part', 'label': 'Section 6 — Tes aspects calculés',      'page': _pg('sec6')},
                {'type': 'part', 'label': 'Section 7 — Synthèse transversale',     'page': _pg('sec7')},
                {'type': 'part', 'label': 'Section 8 — Conclusion & repères',      'page': _pg('sec8')},
            ]
            table_of_contents_page(story, styles, toc_entries)

            # ── Section 1 — Page 4 : Méthode / Comment lire ce livre ─
            method_intro_page(story, styles, prenom)

            # ═══════════════ SECTION 2 — p.5–8 ═══════════════════════
            story.append(chapter_marker('sec2'))
            # Page 5 — Données de naissance
            birth_data_page(
                story, styles, prenom=prenom, birth_date_fr=date_fr,
                birth_time_fr=_birth_time, birth_place=_birth_place,
                sun_sign=sun_sign, moon_sign=moon_sign,
                asc_sign='' if no_birth_time else asc_sign,
                planet_count=len(planets),
                aspect_count=_aspect_count,
                house_count=0 if no_birth_time else len(natal_data.get('houses') or []),
                dominant_element=_dominant_element,
                dominant_modality=_dominant_modality,
            )
            # Page 6 — Roue céleste
            if chart_png_bytes:
                chart_wheel_page(story, styles, chart_png_bytes,
                                 prenom=prenom, birth_date_fr=date_fr,
                                 sun_sign=sun_sign, moon_sign=moon_sign, asc_sign=asc_sign)
            else:
                _wheel_intro = (
                    "La roue de ton ciel est la cartographie de l'instant exact "
                    "où tu es née. Chaque secteur, chaque placement y est "
                    "irremplaçable. Les prochaines pages vont décoder cette "
                    "roue signe après signe, planète après planète."
                )
                chapter_illustration(story, styles,
                                     chapter_tag='✦ La roue de ton ciel ✦',
                                     title='Ton empreinte céleste',
                                     illustration_slug='roue_zodiaque',
                                     intro_text=_wheel_intro)
            # Page 7 — Légende de la roue
            chart_legend_page(story, styles)
            # Page 8 — Synthèse personnelle en un regard
            personal_synthesis_page(
                story, styles, prenom=prenom,
                sun_sign=sun_sign, moon_sign=moon_sign,
                asc_sign='' if no_birth_time else asc_sign,
                dominant_element=_dominant_element,
                dominant_modality=_dominant_modality,
                aspect_count=_aspect_count,
                active_house_count=_active_houses,
                synthese_text=(book_data.get('executive_synthesis')
                               or book_data.get('synthese_executive')
                               or ''),
            )

            # ═══════════════ SECTION 3 — p.9–12 ══════════════════════
            story.append(chapter_marker('sec3'))
            # Page 9 — Trio Soleil × Lune × Ascendant
            trio_cross_analysis_page(story, styles,
                                     sun_sign=sun_sign, moon_sign=moon_sign, asc_sign=asc_sign,
                                     body_html=_wf(book_data.get('trio_synthesis'),
                                                   'trio_synthesis', prenom=prenom))
            # Page 10 — Élément dominant
            em = book_data.get('_em') or {}
            element_dominant_page(story, styles,
                                  dominant_element=em.get('dominant_element', '—'),
                                  planet_count=em.get('dominant_element_count', 0),
                                  body_html=_wf(book_data.get('element_analysis'),
                                                'element_analysis', prenom=prenom,
                                                element=em.get('dominant_element', '—')))
            # Page 11 — Modalité dominante
            modality_dominant_page(story, styles,
                                   dominant_modality=em.get('dominant_modality', '—'),
                                   planet_count=em.get('dominant_modality_count', 0),
                                   body_html=_wf(book_data.get('modality_analysis'),
                                                 'modality_analysis', prenom=prenom,
                                                 modality=em.get('dominant_modality', '—')))
            # Page 12 — Interprétations croisées (élément × modalité × luminaires)
            _crossed_body = _wf(book_data.get('crossed_interpretations'),
                                'crossed_interpretations', prenom=prenom,
                                element=em.get('dominant_element', '—'),
                                modality=em.get('dominant_modality', '—'),
                                sun=sun_sign, moon=moon_sign) if book_data.get('crossed_interpretations') else (
                f"Ton <b>{em.get('dominant_element', '—')}</b> dominant croise ta modalité "
                f"<b>{em.get('dominant_modality', '—')}</b> et tes luminaires "
                f"<b>Soleil en {sun_sign}</b> × <b>Lune en {moon_sign}</b>. "
                f"<br/><br/>Cette combinaison dessine une signature : "
                f"la manière spécifique dont ton élément dominant s'incarne dans "
                f"ta modalité d'action, et dont tes deux luminaires orchestrent cet "
                f"équilibre entre identité consciente (Soleil) et monde intérieur (Lune). "
                f"<br/><br/>C'est l'une des clés les plus personnelles de ta carte : "
                f"là où deux grandes forces se rencontrent pour composer ton tempérament unique."
            )
            planet_dense_page(story, styles,
                              planet_name='Interprétations croisées',
                              sign=f'{em.get("dominant_element", "—")} × {em.get("dominant_modality", "—")}',
                              body_html=_crossed_body,
                              image_local_path=libimg.style_ref('wheel_ref'),
                              dialogue_question=None, glyph='⚹')

            # ═══════════════ SECTION 4 — p.13–26 : Planètes ══════════
            story.append(chapter_marker('sec4'))
            section_divider_page(story, styles, '4', 'Tes planètes',
                                 subtitle='Soleil, Lune, Ascendant, Mercure, Vénus, Mars, Jupiter, Saturne, Uranus, Neptune, Pluton, Chiron, Nœuds.',
                                 illustration_local_path=libimg.planet('Soleil', size=512))

        # Section 4 corps : une page dense par planète (y compris en mode no_birth_time)
        for planet in planets:
            name = planet.get('name', '')
            sign = planet.get('sign', '')
            analysis = (planet.get('analysis') or '').strip() or (
                f'Ton {name} en {sign} raconte une facette essentielle de ton histoire.'
            )
            meta = PLANET_META.get(name, {'glyph': '✦', 'dialogue': None})
            img_path = _planet_image_path(name) if name != 'Ascendant' else _sign_image_path(sign)
            planet_dense_page(
                story, styles,
                planet_name=name, sign=sign,
                body_html=analysis,
                image_local_path=img_path,
                dialogue_question=meta.get('dialogue'),
                glyph=meta.get('glyph'),
            )

        if bd:
            # Chiron + Nœuds lunaires — pages de signature karmique
            _chiron_body = book_data.get('chiron_body') or (
                f"Chiron, la planète-blessure, pose dans ton ciel la cicatrice qui t'enseigne. "
                f"Elle marque le lieu où tu as reçu une morsure précoce — physique, affective, symbolique — "
                f"et qui aujourd'hui te rend particulièrement sensible, et étonnamment aidante pour les autres. "
                f"<br/><br/>Chiron ne guérit pas en effaçant la blessure : il transforme la plaie en savoir, "
                f"en main tendue, en présence. C'est la part de toi qui console sans en avoir l'air."
            )
            planet_dense_page(story, styles,
                              planet_name='Chiron',
                              sign='La blessure devenue savoir',
                              body_html=_chiron_body,
                              image_local_path=libimg.tarot('pendu', size=512),
                              dialogue_question=None, glyph='⚷')
            _nodes_body = book_data.get('nodes_body') or (
                f"Les Nœuds lunaires tracent dans ton ciel l'axe karmique : le Nœud Sud raconte "
                f"ce que tu portes déjà, souvent trop facilement, parfois en excès ; "
                f"le Nœud Nord indique ta direction d'évolution, ce vers quoi ta vie te pousse "
                f"— même quand cela te semble étranger. "
                f"<br/><br/>Ton axe nodal est une boussole : ne cherche pas à abandonner le Sud, "
                f"mais à oser le Nord. C'est le chemin de croissance que ton incarnation vient prendre."
            )
            planet_dense_page(story, styles,
                              planet_name='Nœuds lunaires',
                              sign='Ton axe d\'évolution',
                              body_html=_nodes_body,
                              image_local_path=libimg.tarot('etoile', size=512),
                              dialogue_question=None, glyph='☊')

            # ═══════════════ SECTION 5 — p.27–38 : Maisons ═══════════
            # Refonte Feb 2026 : 12 maisons sur 12 pages (une par maison),
            # sans divider ni intro séparés (contenus intégrés via la roue p.6
            # et le sommaire p.3). Cela permet de respecter la cible de 50 pages
            # strictes tout en gardant une page dédiée par maison.
            story.append(chapter_marker('sec5'))
            # 12 pages — une par maison
            houses_data = natal_data.get('houses') or []
            houses_by_num = {h.get('num'): h for h in houses_data if h.get('num')}
            for n in range(1, 13):
                h = houses_by_num.get(n, {})
                house_detail_page(story, styles,
                                  house_num=n,
                                  sign=h.get('sign', ''),
                                  planets_in_house=h.get('planets_in_house') or [],
                                  body_html=book_data.get(f'house_{n}') or '')

            # ═══════════════ SECTION 6 — p.37–44 : Aspects ═══════════
            story.append(chapter_marker('sec6'))
            section_divider_page(story, styles, '6', 'Tes aspects calculés',
                                 subtitle='La conversation précise de tes planètes.',
                                 illustration_local_path=libimg.tarot('amoureux', size=512))
            # Table des aspects (page d'ouverture dense)
            aspects_opening_page(story, styles, aspects=natal_data.get('aspects') or [])
            # 3 groupes thématiques
            aspects_group_page(story, styles,
                               category='Aspects harmonieux',
                               headline=_hf(book_data.get('aspects_harmonieux_headline'),
                                            'aspects_harmonieux_headline'),
                               body_html=_wf(book_data.get('aspects_harmonieux_body'),
                                             'aspects_harmonieux_body', prenom=prenom),
                               tarot_slug='soleil')
            aspects_group_page(story, styles,
                               category='Aspects de tension',
                               headline=_hf(book_data.get('aspects_tensions_headline'),
                                            'aspects_tensions_headline'),
                               body_html=_wf(book_data.get('aspects_tensions_body'),
                                             'aspects_tensions_body', prenom=prenom),
                               tarot_slug='force')
            aspects_group_page(story, styles,
                               category='Aspect signature',
                               headline=_hf(book_data.get('rare_aspect_headline'),
                                            'rare_aspect_headline'),
                               body_html=_wf(book_data.get('rare_aspect_body'),
                                             'rare_aspect_body', prenom=prenom),
                               tarot_slug='etoile')
            # Synthèse aspects texte retirée (Feb 2026) : son contenu est déjà
            # couvert par les 3 pages d'interprétation thématique ci-dessus.
            # Pages d'astrologie enrichie si dispo
            for section_title, section_body in _enhanced_personal_analysis_sections(
                natal_data.get('enhanced_personal_analysis'), no_birth_time=no_birth_time,
            ):
                planet_dense_page(
                    story, styles,
                    planet_name=section_title,
                    sign='Astrologie enrichie',
                    body_html=section_body,
                    image_local_path=None,
                    dialogue_question=None, glyph=None,
                )

            # ═══════════════ SECTION 7 — p.45–48 : Synthèse transversale ═
            story.append(chapter_marker('sec7'))
            _transv_axes = [
                ('Relations', 'ta manière d\'aimer et de te relier',
                 book_data.get('transversal_relations')
                 or f"Tes planètes personnelles (Vénus, Lune, Soleil) et ton axe maisons 1/7 "
                    f"dessinent ta signature relationnelle. "
                    f"<br/><br/>Tu abordes l'autre avec une sensibilité particulière, où la fidélité, "
                    f"la tendresse et la lucidité se croisent. Tes relations majeures ne sont jamais "
                    f"anodines : chacune te révèle une facette de toi que tu ne voyais pas en solitaire. "
                    f"Dans l'intimité, tu cherches moins la facilité qu'une forme de vérité partagée.",
                 'amoureux'),
                ('Activité & vocation', 'où tu déposes ton énergie dans le monde',
                 book_data.get('transversal_activity')
                 or f"L'axe Mars × Saturne × Maison 10 raconte comment tu agis et où tu construis. "
                    f"<br/><br/>Ton énergie d'action n'est pas la plus visible, mais elle est tenace : "
                    f"tu reviens, tu polis, tu finis. Ta vocation se dessine moins dans une étiquette "
                    f"professionnelle que dans une couleur — ce que tu laisses derrière toi, ce que tu "
                    f"transformes dans les lieux où tu passes.",
                 'bateleur'),
                ('Ressources', 'ce qui te nourrit et ce que tu offres',
                 book_data.get('transversal_resources')
                 or f"Vénus, Jupiter et tes maisons 2 et 8 cartographient tes ressources — intérieures "
                    f"comme matérielles. "
                    f"<br/><br/>Tu as un rapport subtil à ce qui soutient : argent, affection, temps, savoir. "
                    f"Tes dons les plus précieux sont souvent ceux que tu offres sans compter — mais apprends "
                    f"à les nommer : ce que tu donnes sans effort peut valoir immensément pour ceux qui en manquent.",
                 'etoile'),
                ('Tensions & croissance', 'les frottements qui te font grandir',
                 book_data.get('transversal_tensions')
                 or f"Tes carrés et oppositions majeurs ne sont pas des défauts : "
                    f"ce sont les lieux où ton âme a choisi de forger sa complexité. "
                    f"<br/><br/>Chaque tension interne t'oblige à inventer un troisième chemin — "
                    f"ni l'un ni l'autre des deux pôles, mais une architecture intérieure qui "
                    f"n'existerait pas sans la friction. C'est ainsi que ta profondeur se construit.",
                 'force'),
            ]
            for _title, _kicker, _body, _tarot in _transv_axes:
                transversal_synthesis_page(story, styles,
                                           title=_title, kicker=_kicker,
                                           body_html=_body, tarot_slug=_tarot)

            # ═══════════════ SECTION 8 — p.49–50 : Conclusion & glossaire ═
            story.append(chapter_marker('sec8'))
            _conclusion_body = (
                book_data.get('cloture_body')
                or book_data.get('conclusion')
                or f"Ce livre n'est pas une fin, {prenom}, c'est un seuil. "
                   f"Tu peux y revenir à toute saison, aux heures claires comme aux heures troubles. "
                   f"Les planètes ne cessent de parler — à toi désormais d'écouter avec l'oreille "
                   f"affûtée qui s'est aiguisée page après page. "
                   f"<br/><br/>Souviens-toi : ton ciel n'est pas un destin fixé, c'est une partition. "
                   f"Et la musicienne, c'est toi."
            )
            conclusion_page(story, styles, prenom=prenom, body_html=_conclusion_body)
            glossary_technical_page(story, styles)

        # Mode no_birth_time (sans heure) : flow simplifié — on sort juste les planètes
        # (déjà faites plus haut hors du bloc bd) + colophon.
        if not bd:
            # Fin émotionnelle (signée Plume Astrale)
            emotional_ending(story, styles, prenom=prenom, signature='Plume Astrale')

        # Colophon final (toujours présent)
        _product_name = 'Thème Natal — Édition des Planètes' if no_birth_time else 'Thème Natal'
        colophon_page(story, styles, prenom, referral_code, referral_link,
                      product_name=_product_name, signature='Plume Astrale')

        return story

    # Double-passe : 1re passe (dry-run) capture les numéros de page,
    # 2e passe injecte les vraies pages dans le sommaire livre.
    return build_with_toc(
        _build_story,
        doc_kwargs=dict(
            pagesize=A4, title=f'Thème Natal — {prenom}',
            leftMargin=2.2 * cm, rightMargin=2.2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        ),
        on_first_page=luxury_bg,
        on_later_pages=luxury_bg,
    )
