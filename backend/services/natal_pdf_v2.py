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
import io
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, chapter_illustration, chart_wheel_page,
    planet_dense_page, photos_grid_2x2, emotional_ending,
)
from services.pdf_book_pages import (
    half_title_page, copyright_page, dedication_page, table_of_contents_page,
    part_divider_page, element_dominant_page, modality_dominant_page,
    trio_cross_analysis_page, aspects_group_page, house_detail_page,
    year_ahead_page, colophon_page,
)
from services import library_images as libimg

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
    'Pluton':    {'glyph': '♇', 'dialogue': "Ce que tu as traversé de plus dur t'a préparée à voir ce que personne ne veut regarder. C'est ta force silencieuse."},
    'Ascendant': {'glyph': '⇑', 'dialogue': "Les autres te trouvent parfois plus forte que tu ne te sens. Et cette impression n'est pas fausse."},
}

_PLANET_NAMES_FR = {
    'sun': 'Soleil', 'moon': 'Lune', 'mercury': 'Mercure', 'venus': 'Vénus',
    'mars': 'Mars', 'jupiter': 'Jupiter', 'saturn': 'Saturne',
    'uranus': 'Uranus', 'neptune': 'Neptune', 'pluto': 'Pluton',
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
        return safe(sign_to_fr(str(value or '')))

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

    extra_points = []
    classic_points = {'sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'ascendant'}
    for point in analysis.get('planets') or []:
        if not isinstance(point, dict):
            continue
        key = str(point.get('name') or '').strip().lower().replace(' ', '_')
        if key not in _PLANET_NAMES_FR or key in classic_points:
            continue
        details = [sign(point.get('sign'))] if point.get('sign') else []
        position = degree(point.get('position'))
        if position:
            details.append(position)
        if not no_birth_time and point.get('house'):
            details.append(house_name(point['house']))
        extra_points.append(f"{planet_name(key)} : {' · '.join(details)}")
    if extra_points:
        cycles.append(f"<b>Points complémentaires :</b> {' ; '.join(extra_points[:5])}")

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
                        referral_link: Optional[str] = None) -> bytes:
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
    buf = io.BytesIO()
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
        except Exception:
            date_fr = birth_date

        bd = bool(book_data and book_data.get('_source') in ('gpt', 'cache'))

        # §V audit marque Feb 2026 : sans heure de naissance, on désactive le
        # mode livre riche qui repose sur Ascendant, Trio, 12 Maisons — toutes
        # ces sections seraient fausses. On garde uniquement les 10 planètes
        # commentées (Soleil, Lune, Mercure, Vénus, Mars, Jupiter, Saturne,
        # Uranus, Neptune, Pluton) et le colophon "Édition des Planètes".
        if no_birth_time:
            bd = False

        # ══════════════════════════════════════════════════════════════
        # FRONT MATTER (uniquement si book_data disponible)
        # ══════════════════════════════════════════════════════════════
        # ── 1. COUVERTURE ──────────────────────────────────────────────
        cover_page(story, styles, prenom=prenom,
                   subtitle='Ton ciel de naissance, dévoilé.',
                   illustration_slug='ciel_zodiaque')

        if bd:
            # ── 2. Faux-titre ──
            half_title_page(story, styles, 'Thème Natal')
            # ── 3. Copyright + éphéméride ──
            copyright_page(story, styles, prenom, date_fr)
            # ── 4. Dédicace personnalisée (GPT) ──
            dedication_page(story, styles, prenom, book_data.get('dedication'))
            # ── 5. Table des matières ──
            toc_entries = [
                {'type': 'part',    'label': 'Partie I — Fondations',                                        'page': _pg('part1')},
                {'type': 'chapter', 'label': 'Ouverture'},
                {'type': 'chapter', 'label': 'Ton empreinte céleste'},
                {'type': 'chapter', 'label': 'Les 4 clés de qui tu es'},
                {'type': 'chapter', 'label': f"Ton élément dominant : {book_data['_em']['dominant_element']}"},
                {'type': 'chapter', 'label': f"Ta modalité dominante : {book_data['_em']['dominant_modality']}"},
                {'type': 'part',    'label': 'Partie II — Planètes intimes',                                 'page': _pg('part2')},
                {'type': 'chapter', 'label': 'Ton triangle intime — Soleil × Lune × Ascendant'},
                {'type': 'chapter', 'label': 'Soleil, Lune, Mercure, Vénus, Mars, Ascendant'},
                {'type': 'chapter', 'label': 'Grille : tes énergies quotidiennes'},
                {'type': 'part',    'label': 'Partie III — Planètes générationnelles',                       'page': _pg('part3')},
                {'type': 'chapter', 'label': 'Jupiter, Saturne, Uranus, Neptune, Pluton'},
                {'type': 'chapter', 'label': 'Grille : tes strates profondes'},
                {'type': 'part',    'label': 'Partie IV — La danse des aspects',                             'page': _pg('part4')},
                {'type': 'chapter', 'label': 'Tes aspects harmonieux'},
                {'type': 'chapter', 'label': 'Tes aspects de tension'},
                {'type': 'chapter', 'label': 'Ton aspect signature'},
                {'type': 'chapter', 'label': 'Synthèse psychologique globale'},
                {'type': 'part',    'label': 'Partie V — Les douze maisons',                                 'page': _pg('part5')},
                {'type': 'chapter', 'label': 'Introduction aux maisons'},
                {'type': 'chapter', 'label': 'Maisons I à XII (une par une)'},
                {'type': 'part',    'label': 'Épilogue',                                                     'page': _pg('part6')},
                {'type': 'chapter', 'label': 'Ton année à venir'},
                {'type': 'chapter', 'label': 'Fin émotionnelle'},
                {'type': 'chapter', 'label': 'Colophon'},
            ]
            table_of_contents_page(story, styles, toc_entries)
            # ── DIVISEUR PARTIE I ──
            story.append(chapter_marker('part1'))
            part_divider_page(story, styles, 'I', 'Fondations',
                              subtitle='Ton empreinte céleste, ton élément, ta cadence.',
                              illustration_local_path=libimg.style_ref('wheel_ref'))

        # ══════════════════════════════════════════════════════════════
        # PARTIE I — FONDATIONS
        # ══════════════════════════════════════════════════════════════
        # Ouverture
        opening_page(story, styles, prenom=prenom,
                     first_line="Ton ciel n'a jamais été aussi clair.")

        # Roue céleste
        if chart_png_bytes:
            chart_wheel_page(story, styles, chart_png_bytes,
                              prenom=prenom, birth_date_fr=date_fr,
                              sun_sign=sun_sign, moon_sign=moon_sign, asc_sign=asc_sign)
        else:
            chapter_illustration(story, styles,
                                  chapter_tag='✦ La roue de ton ciel ✦',
                                  title='Ton empreinte céleste',
                                  illustration_slug='roue_zodiaque')

        # Grille identité 2×2
        id_cells = [
            {'image': _planet_image_path('Soleil'), 'label': 'Soleil', 'sublabel': sun_sign},
            {'image': _planet_image_path('Lune'), 'label': 'Lune', 'sublabel': moon_sign},
        ]
        # §V audit marque : ascendant seulement si heure connue (sinon faux 11/12)
        if asc_sign and not no_birth_time:
            id_cells.append({'image': _sign_image_path(asc_sign), 'label': 'Ascendant', 'sublabel': asc_sign})
        fourth = next((p for p in planets if p.get('name') == 'Vénus'),
                      planets[3] if len(planets) > 3 else None)
        if fourth:
            id_cells.append({
                'image': _planet_image_path(fourth.get('name', '')) or _sign_image_path(fourth.get('sign', '')),
                'label': fourth.get('name', ''),
                'sublabel': fourth.get('sign', ''),
            })
        photos_grid_2x2(story, styles,
                        chapter_tag='✦ Ta signature astrale ✦',
                        title='Les 4 clés de qui tu es',
                        cells=id_cells)

        # Élément + modalité (livre uniquement)
        if bd:
            em = book_data['_em']
            element_dominant_page(story, styles,
                                  dominant_element=em['dominant_element'],
                                  planet_count=em['dominant_element_count'],
                                  body_html=book_data.get('element_analysis') or '')
            modality_dominant_page(story, styles,
                                    dominant_modality=em['dominant_modality'],
                                    planet_count=em['dominant_modality_count'],
                                    body_html=book_data.get('modality_analysis') or '')

            # ── DIVISEUR PARTIE II ──
            story.append(chapter_marker('part2'))
            part_divider_page(story, styles, 'II', 'Planètes intimes',
                              subtitle='Ce qui t\'anime jour et nuit.',
                              illustration_local_path=libimg.planet('Vénus', size=512))

            # Trio synthèse Soleil × Lune × Ascendant
            trio_cross_analysis_page(story, styles,
                                      sun_sign=sun_sign, moon_sign=moon_sign, asc_sign=asc_sign,
                                      body_html=book_data.get('trio_synthesis') or '')

        # ══════════════════════════════════════════════════════════════
        # ACTE III PILOTE — Ton âme (5 chapitres éditoriaux : cœur / esprit
        # / blessures / désirs / talents). Ne s'active QUE si book_data
        # contient acte3_chapters. Utilise EXCLUSIVEMENT les 9 templates
        # éditoriaux de pdf_editorial_templates.py.
        # ══════════════════════════════════════════════════════════════
        acte3 = (book_data or {}).get('acte3_chapters') if bd else None
        if acte3 and isinstance(acte3, dict):
            from services.pdf_editorial_templates import (
                t_chapter_opening, t_quote, t_portrait, t_analysis, t_callout,
                t_ritual, t_journal, t_synthesis, t_double_illustration,
            )
            # Ouverture d'Acte III — double page monumentale
            t_chapter_opening(story, roman='III', title='Ton âme',
                              kicker='Cinq chapitres pour te rencontrer plus profondément.',
                              illustration_path=libimg.tarot('etoile', size=512))
            _CHAPTER_META = [
                ('coeur',     'Ton cœur',      libimg.planet('Vénus', size=512),   libimg.tarot('amoureux', size=512)),
                ('esprit',    'Ton esprit',    libimg.planet('Mercure', size=512), libimg.tarot('bateleur', size=512)),
                ('blessures', 'Tes blessures', libimg.planet('Saturne', size=512), libimg.tarot('pendu',    size=512)),
                ('desirs',    'Tes désirs',    libimg.planet('Mars', size=512),    libimg.tarot('chariot',  size=512)),
                ('talents',   'Tes talents',   libimg.planet('Soleil', size=512),  libimg.tarot('etoile',   size=512)),
            ]
            for key, chapter_title, planet_img, tarot_img in _CHAPTER_META:
                c = acte3.get(key) or {}
                if not c:
                    continue
                # Structure récurrente stricte pour chaque chapitre d'âme :
                #  1. double illustration (rythme aéré avant le dense)
                #  2. quote (citation d'ouverture)
                #  3. portrait (question + analyse + image)
                #  4. analysis (colonnes texte + illustration + citation encadrée)
                #  5. callout (3 conseils + phrase mémorable)
                #  6. ritual (rituel + pierre + couleur + respiration)
                #  7. journal (question + espace d'écriture)
                #  8. synthesis (forces / défis / mission)
                if planet_img:
                    t_double_illustration(story, planet_img, caption=chapter_title)
                t_quote(story, c.get('citation_ouverture', ''), attribution='Soléna')
                t_portrait(story,
                           chapter_tag=chapter_title,
                           title=chapter_title,
                           question=c.get('question_emotionnelle', ''),
                           body_html=c.get('analyse_html', ''),
                           illustration_path=planet_img)
                t_analysis(story,
                           title=f'Approfondir : {chapter_title.lower()}',
                           body_html=c.get('analyse_html', ''),
                           illustration_path=tarot_img,
                           inset_quote=c.get('phrase_memorable', ''))
                t_callout(story,
                          title=f'{chapter_title} — À retenir',
                          tips=c.get('conseils') or [],
                          memorable_line=c.get('phrase_memorable', ''))
                t_ritual(story,
                         title=c.get('rituel_titre') or f'Rituel — {chapter_title}',
                         steps=c.get('rituel_etapes') or [],
                         duration=c.get('rituel_duree', '10 min'),
                         stone=c.get('rituel_pierre', '—'),
                         color=c.get('rituel_couleur', '—'),
                         breathing=c.get('rituel_respiration', '—'),
                         illustration_path=tarot_img)
                t_journal(story,
                          question=c.get('question_journal', ''),
                          context_line=f'Un instant pour écouter {chapter_title.lower()}.')
                t_synthesis(story,
                            title=f'{chapter_title} — Synthèse',
                            forces=c.get('forces') or [],
                            defis=c.get('defis') or [],
                            mission=c.get('mission', ''),
                            closing_quote=c.get('phrase_memorable'))

        # ══════════════════════════════════════════════════════════════
        # PARTIE II — PLANÈTES (denses, 1 page par planète)
        # ══════════════════════════════════════════════════════════════
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

        # Grille 2×2 planètes sociales (mode Ultra ≥ 7 planètes)
        if len(planets) >= 7:
            social_names = ('Mercure', 'Vénus', 'Mars', 'Jupiter')
            social_planets = [p for p in planets if p.get('name') in social_names]
            if len(social_planets) >= 3:
                photos_grid_2x2(story, styles,
                                chapter_tag='✦ Tes énergies quotidiennes ✦',
                                title='Comment tu penses, aimes, agis, grandis',
                                cells=[{
                                    'image': _planet_image_path(p.get('name', '')),
                                    'label': p.get('name', ''),
                                    'sublabel': p.get('sign', ''),
                                } for p in social_planets[:4]])

        # ── DIVISEUR PARTIE III ──
        if bd:
            story.append(chapter_marker('part3'))
            part_divider_page(story, styles, 'III', 'Planètes générationnelles',
                              subtitle='Ce qui te structure au long cours.',
                              illustration_local_path=libimg.planet('Saturne', size=512))

        # Grille 2×2 planètes générationnelles (mode Ultra ≥ 10 planètes)
        if len(planets) >= 10:
            gen_names = ('Saturne', 'Uranus', 'Neptune', 'Pluton')
            gen_planets = [p for p in planets if p.get('name') in gen_names]
            if len(gen_planets) >= 3:
                photos_grid_2x2(story, styles,
                                chapter_tag='✦ Tes strates profondes ✦',
                                title='Ce qui te structure au long cours',
                                cells=[{
                                    'image': _planet_image_path(p.get('name', '')),
                                    'label': p.get('name', ''),
                                    'sublabel': p.get('sign', ''),
                                } for p in gen_planets[:4]])

        # ══════════════════════════════════════════════════════════════
        # PARTIE IV — ASPECTS
        # ══════════════════════════════════════════════════════════════
        if bd:
            story.append(chapter_marker('part4'))
            part_divider_page(story, styles, 'IV', 'La danse des aspects',
                              subtitle='Comment tes planètes s\'appellent, se cherchent, s\'écoutent.',
                              illustration_local_path=libimg.tarot('amoureux', size=512))

            aspects_group_page(story, styles,
                                category='Aspects harmonieux',
                                headline=book_data.get('aspects_harmonieux_headline') or 'La grâce en toi',
                                body_html=book_data.get('aspects_harmonieux_body') or '',
                                tarot_slug='soleil')
            aspects_group_page(story, styles,
                                category='Aspects de tension',
                                headline=book_data.get('aspects_tensions_headline') or 'Le nœud qui te forge',
                                body_html=book_data.get('aspects_tensions_body') or '',
                                tarot_slug='force')
            aspects_group_page(story, styles,
                                category='Aspect signature',
                                headline=book_data.get('rare_aspect_headline') or 'Ta note rare',
                                body_html=book_data.get('rare_aspect_body') or '',
                                tarot_slug='etoile')

        # Synthèse aspects (existante)
        synthese = (natal_data.get('synthese_aspects') or '').strip()
        if synthese:
            planet_dense_page(
                story, styles,
                planet_name='Aspects',
                sign='La danse de tes planètes',
                body_html=synthese,
                image_local_path=None,
                dialogue_question="Tes planètes se parlent — certaines s'aiment, d'autres se cherchent. Écoute leur conversation.",
                glyph=None,
            )

        for section_title, section_body in _enhanced_personal_analysis_sections(
            natal_data.get('enhanced_personal_analysis'), no_birth_time=no_birth_time,
        ):
            planet_dense_page(
                story, styles,
                planet_name=section_title,
                sign='Astrologie enrichie',
                body_html=section_body,
                image_local_path=None,
                dialogue_question=None,
                glyph=None,
            )

        # ══════════════════════════════════════════════════════════════
        # PARTIE V — MAISONS (livre uniquement)
        # ══════════════════════════════════════════════════════════════
        if bd:
            story.append(chapter_marker('part5'))
            part_divider_page(story, styles, 'V', 'Les douze maisons',
                              subtitle='Les pièces intérieures de ta demeure.',
                              illustration_local_path=libimg.house(1, size=512))
            # Introduction maisons
            planet_dense_page(story, styles,
                               planet_name='Les maisons',
                               sign='Ta demeure intérieure',
                               body_html=book_data.get('houses_intro') or '',
                               image_local_path=libimg.style_ref('wheel_ref'),
                               dialogue_question=None,
                               glyph=None)
            # 12 pages — une par maison
            # NB : on n'a pas toujours les données cuspide/planètes, on affiche quand même l'analyse
            houses_data = natal_data.get('houses') or []
            houses_by_num = {h.get('num'): h for h in houses_data if h.get('num')}
            for n in range(1, 13):
                h = houses_by_num.get(n, {})
                house_detail_page(story, styles,
                                   house_num=n,
                                   sign=h.get('sign', ''),
                                   planets_in_house=h.get('planets_in_house') or [],
                                   body_html=book_data.get(f'house_{n}') or '')

        # ══════════════════════════════════════════════════════════════
        # ÉPILOGUE
        # ══════════════════════════════════════════════════════════════
        if bd:
            story.append(chapter_marker('part6'))
            part_divider_page(story, styles, 'VI', 'Épilogue',
                              subtitle='Ce que le ciel murmure pour la suite.',
                              illustration_local_path=libimg.tarot('etoile', size=512))
            year_ahead_page(story, styles, prenom,
                            body_html=book_data.get('year_ahead') or '')

        # Fin émotionnelle Soléna (existante)
        emotional_ending(story, styles, prenom=prenom)

        # Colophon final avec code parrainage
        # §V audit marque : mention "Édition des Planètes" si sans heure
        # (colophon appelé aussi en no_birth_time bien que bd=False)
        _product_name = 'Thème Natal — Édition des Planètes' if no_birth_time else 'Thème Natal'
        if bd or no_birth_time:
            colophon_page(story, styles, prenom, referral_code, referral_link, product_name=_product_name)

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
