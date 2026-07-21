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
    cover_page, opening_page, chapter_illustration,
    planet_dense_page, photos_grid_2x2, emotional_ending,
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
    return libimg.planet(planet_fr, size=1080)


def _sign_image_path(sign_fr: str) -> Optional[str]:
    """Retourne le chemin local de l'image du signe zodiacal."""
    return libimg.sign(sign_fr, size=1080)


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


def build_natal_pdf_v2(prenom: str, birth_date: str, natal_data: dict) -> bytes:
    """Génère le Thème Natal Plume Astrale — rendu standard uniforme.

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
    """
    buf = io.BytesIO()
    doc = build_luxury_doc(buf, title=f'Thème Natal — {prenom}')
    styles = luxury_styles()
    story = []

    planets = natal_data.get('planets', []) or []
    sun_sign = natal_data.get('sun_sign', '')
    moon_sign = natal_data.get('moon_sign', '')
    asc_sign = natal_data.get('ascendant_sign', '')

    # ── 1. COUVERTURE (image cover + prénom) ────────────────────────
    cover_page(story, styles, prenom=prenom,
               subtitle='Ton ciel de naissance, dévoilé.',
               illustration_slug='ciel_zodiaque')

    # ── 2. OUVERTURE (accueil dense — plus 1-liner) ────────────────
    opening_page(story, styles, prenom=prenom,
                 first_line="Ton ciel n'a jamais été aussi clair.")

    # ── 3. INTRO ROUE CÉLESTE (image + titre) ──────────────────────
    chapter_illustration(story, styles,
                          chapter_tag='✦ La roue de ton ciel ✦',
                          title='Ton empreinte céleste',
                          illustration_slug='roue_zodiaque')

    # ── 4. GRILLE 2×2 : Trio identitaire + Aspect dominant ──────────
    #  Soleil + Lune + Ascendant + 1er signe présent (généralement Vénus)
    id_cells = [
        {'image': _planet_image_path('Soleil'), 'label': 'Soleil', 'sublabel': sun_sign},
        {'image': _planet_image_path('Lune'), 'label': 'Lune', 'sublabel': moon_sign},
        {'image': _sign_image_path(asc_sign) if asc_sign else None, 'label': 'Ascendant', 'sublabel': asc_sign},
    ]
    # 4e cellule : Vénus si présente, sinon la 4e planète du thème
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

    # ── 5. PLANÈTES — 1 page DENSE par planète (jamais de page 1-ligne) ─
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

    # ── 6. GRILLE 2×2 : Planètes sociales (seulement si Ultra ≥ 7 pl.) ──
    if len(planets) >= 7:
        social_names = ('Mercure', 'Vénus', 'Mars', 'Jupiter')
        social_planets = [p for p in planets if p.get('name') in social_names]
        if len(social_planets) >= 3:
            photos_grid_2x2(
                story, styles,
                chapter_tag='✦ Tes énergies quotidiennes ✦',
                title='Comment tu penses, aimes, agis, grandis',
                cells=[
                    {
                        'image': _planet_image_path(p.get('name', '')),
                        'label': p.get('name', ''),
                        'sublabel': p.get('sign', ''),
                    }
                    for p in social_planets[:4]
                ],
            )

    # ── 7. GRILLE 2×2 : Planètes générationnelles (Ultra ≥ 10 pl.) ──
    if len(planets) >= 10:
        gen_names = ('Saturne', 'Uranus', 'Neptune', 'Pluton')
        gen_planets = [p for p in planets if p.get('name') in gen_names]
        if len(gen_planets) >= 3:
            photos_grid_2x2(
                story, styles,
                chapter_tag='✦ Tes strates profondes ✦',
                title='Ce qui te structure au long cours',
                cells=[
                    {
                        'image': _planet_image_path(p.get('name', '')),
                        'label': p.get('name', ''),
                        'sublabel': p.get('sign', ''),
                    }
                    for p in gen_planets[:4]
                ],
            )

    # ── 8. SYNTHÈSE ASPECTS (Ultra only, page dense unique) ──────────
    synthese = (natal_data.get('synthese_aspects') or '').strip()
    if synthese:
        planet_dense_page(
            story, styles,
            planet_name='Aspects',
            sign='La danse de tes planètes',
            body_html=synthese,
            image_local_path=None,
            dialogue_question="Tes planètes se parlent — certaines s'aiment, d'autres se cherchent. Écoute leur conversation.",
            glyph='✦',
        )

    # ── 9. FIN ÉMOTIONNELLE SOLÉNA ──────────────────────────────────
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()
