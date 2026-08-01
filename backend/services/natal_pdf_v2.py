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
    'Neptune':   {'glyph': '♆', 'dialogue': "Tu as ce don rare : sentir avant de voir. Ce n'est pas de la fuite — c'est de la clairvoyance qui n'a pas trouvé ses mots."},
    'Pluton':    {'glyph': '♇', 'dialogue': "Ce que tu as traversé de plus dur t'a préparée à voir ce que personne ne veut regarder. C'est ta force silencieuse."},
    'Ascendant': {'glyph': '⇑', 'dialogue': "Les autres te trouvent parfois plus forte que tu ne te sens. Et cette impression n'est pas fausse."},
}


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
    doc = build_luxury_doc(buf, title=f'Thème Natal — {prenom}')
    styles = luxury_styles()
    story = []

    planets = natal_data.get('planets', []) or []
    sun_sign = natal_data.get('sun_sign', '')
    moon_sign = natal_data.get('moon_sign', '')
    asc_sign = natal_data.get('ascendant_sign', '')

    # Format FR de la date (utilisé plusieurs fois)
    _MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    try:
        _y, _m, _d = birth_date.split('-')
        date_fr = f"{int(_d)} {_MOIS_FR[int(_m) - 1]} {_y}"
    except Exception:
        date_fr = birth_date

    bd = bool(book_data and book_data.get('_source') in ('gpt', 'cache'))

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
            {'type': 'part', 'label': 'Partie I — Fondations'},
            {'type': 'chapter', 'label': 'Ouverture'},
            {'type': 'chapter', 'label': 'Ton empreinte céleste'},
            {'type': 'chapter', 'label': 'Les 4 clés de qui tu es'},
            {'type': 'chapter', 'label': f"Ton élément dominant : {book_data['_em']['dominant_element']}"},
            {'type': 'chapter', 'label': f"Ta modalité dominante : {book_data['_em']['dominant_modality']}"},
            {'type': 'part', 'label': 'Partie II — Planètes intimes'},
            {'type': 'chapter', 'label': 'Ton triangle intime — Soleil × Lune × Ascendant'},
            {'type': 'chapter', 'label': 'Soleil, Lune, Mercure, Vénus, Mars, Ascendant'},
            {'type': 'chapter', 'label': 'Grille : tes énergies quotidiennes'},
            {'type': 'part', 'label': 'Partie III — Planètes générationnelles'},
            {'type': 'chapter', 'label': 'Jupiter, Saturne, Uranus, Neptune, Pluton'},
            {'type': 'chapter', 'label': 'Grille : tes strates profondes'},
            {'type': 'part', 'label': 'Partie IV — La danse des aspects'},
            {'type': 'chapter', 'label': 'Tes aspects harmonieux'},
            {'type': 'chapter', 'label': 'Tes aspects de tension'},
            {'type': 'chapter', 'label': 'Ton aspect signature'},
            {'type': 'chapter', 'label': 'Synthèse psychologique globale'},
            {'type': 'part', 'label': 'Partie V — Les douze maisons'},
            {'type': 'chapter', 'label': 'Introduction aux maisons'},
            {'type': 'chapter', 'label': 'Maisons I à XII (une par une)'},
            {'type': 'part', 'label': 'Épilogue'},
            {'type': 'chapter', 'label': 'Ton année à venir'},
            {'type': 'chapter', 'label': 'Fin émotionnelle'},
            {'type': 'chapter', 'label': 'Colophon'},
        ]
        table_of_contents_page(story, styles, toc_entries)
        # ── DIVISEUR PARTIE I ──
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
        {'image': _sign_image_path(asc_sign) if asc_sign else None, 'label': 'Ascendant', 'sublabel': asc_sign},
    ]
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

    # ══════════════════════════════════════════════════════════════
    # PARTIE V — MAISONS (livre uniquement)
    # ══════════════════════════════════════════════════════════════
    if bd:
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
        part_divider_page(story, styles, 'VI', 'Épilogue',
                          subtitle='Ce que le ciel murmure pour la suite.',
                          illustration_local_path=libimg.tarot('etoile', size=512))
        year_ahead_page(story, styles, prenom,
                        body_html=book_data.get('year_ahead') or '')

    # Fin émotionnelle Soléna (existante)
    emotional_ending(story, styles, prenom=prenom)

    # Colophon final avec code parrainage
    if bd:
        colophon_page(story, styles, prenom, referral_code, referral_link)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()
