"""
natal_pdf_v2 — Thème Natal Plume Astrale style "livre de luxe".

Suit le brief Nathalie (2026-02-20) :
  1. Ouverture spectaculaire
  2. Netflix effect (teasers entre chapitres)
  3. Double pages par planète (glyph pleine page + analyse)
  4. Phrases "waouh" par chapitre
  5. Dialogue psychologique
  6. Fin émotionnelle Soléna
"""
from __future__ import annotations
import io
from services.pdf_luxury_theme import (
    build_luxury_doc, luxury_styles, luxury_bg,
    cover_page, opening_page, teaser_page, waouh_quote_page,
    chapter_illustration, planet_glyph_page, planet_analysis_page, emotional_ending,
)

# Personnage poétique de chaque planète
PLANET_PERSONA = {
    'Soleil':   {'glyph': '☉', 'tagline': 'Le roi de ton thème.',           'illus': 'astral_planete'},
    'Lune':     {'glyph': '☽', 'tagline': 'La mémoire de tes émotions.',    'illus': 'astral_ciel'},
    'Mercure':  {'glyph': '☿', 'tagline': 'La voix de ton mental.',         'illus': 'astral_mandala'},
    'Vénus':    {'glyph': '♀', 'tagline': 'Ce qui t\'attire, ce que tu aimes.', 'illus': 'fleurs_or'},
    'Mars':     {'glyph': '♂', 'tagline': 'Ton feu, ta manière d\'agir.',   'illus': 'chapitre_bleu'},
    'Jupiter':  {'glyph': '♃', 'tagline': 'Ta chance, ton expansion.',      'illus': 'astral_fruits'},
    'Saturne':  {'glyph': '♄', 'tagline': 'Ton architecte intérieur.',      'illus': 'astral_mandala'},
    'Ascendant':{'glyph': 'Asc', 'tagline': 'Le masque que ton âme a choisi.', 'illus': 'ciel_zodiaque'},
}

PLANET_DIALOGUE = {
    'Soleil':  'As-tu remarqué que tu donnes énormément aux autres ? Mais acceptes-tu vraiment de recevoir ?',
    'Lune':    'Il y a une émotion qui revient depuis l\'enfance. Tu la reconnais, n\'est-ce pas ?',
    'Mercure': 'Tu réfléchis souvent à voix basse, comme si tu essayais d\'organiser un monde intérieur trop vaste pour un seul cerveau.',
    'Vénus':   'Tu attires les personnes qui ont besoin d\'être sauvées. Et si, cette fois, tu choisissais quelqu\'un qui te comble sans effort ?',
    'Mars':    'Il y a une colère ancienne en toi. Elle n\'est pas ta faiblesse — c\'est ton carburant sacré.',
    'Jupiter': 'Tu doutes de ta chance. Et pourtant, chaque fois que tu t\'ouvres à l\'inconnu, le ciel s\'aligne.',
    'Saturne': 'Ce que tu prends pour un plafond, c\'est en réalité une fondation.',
    'Ascendant': 'Les autres te trouvent parfois plus forte que tu ne te sens. Et cette impression n\'est pas fausse.',
}

CHAPTER_TEASERS = [
    "Ton Soleil est en {sun_sign}. Mais ce n'est qu'une infime partie de ton histoire…",
    "Ce que ta Lune raconte est plus intime encore.",
    "Mais ce n'est pas ce qui m'a le plus surprise…",
    "La planète qui influence le plus tes relations est celle que personne ne regarde.",
    "Il reste une clé — celle qui structure tout le reste.",
]

WAOUH_QUOTES = [
    "Tu n'es pas née pour vivre une vie ordinaire.",
    "Certaines rencontres étaient écrites avant même ta naissance.",
    "Ton plus grand défi deviendra ton plus grand pouvoir.",
    "Ta lumière ne dérange que ceux qui n'ont pas encore trouvé la leur.",
    "Il y a quelque chose en toi que le monde attend.",
]


def build_natal_pdf_v2(prenom: str, birth_date: str, natal_data: dict) -> bytes:
    """Génère le Thème Natal luxe.

    natal_data attend :
        {
          'sun_sign': 'Cancer',
          'moon_sign': 'Poissons',
          'ascendant_sign': 'Vierge',
          'planets': [
            {'name': 'Soleil', 'sign': 'Cancer', 'analysis': '...long texte...'},
            ...
          ]
        }
    """
    buf = io.BytesIO()
    doc = build_luxury_doc(buf, title=f'Thème Natal — {prenom}')
    styles = luxury_styles()
    story = []

    # ─── 1. Couverture ────────────────────────────────────────────────
    cover_page(story, styles, prenom=prenom,
               subtitle='Ton ciel de naissance, dévoilé.',
               illustration_slug='ciel_zodiaque')

    # ─── 2. Ouverture spectaculaire ──────────────────────────────────
    opening_page(story, styles, prenom=prenom,
                 first_line="Ton ciel n'a jamais été aussi clair.")

    # ─── 3. Teaser Soleil ─────────────────────────────────────────────
    sun_sign = natal_data.get('sun_sign', 'ton signe solaire')
    teaser_page(story, styles,
                CHAPTER_TEASERS[0].format(sun_sign=sun_sign))

    # ─── 4. Illustration roue astrologique ────────────────────────────
    chapter_illustration(story, styles,
                          chapter_tag='✦ La roue de ton ciel ✦',
                          title='Ton empreinte céleste',
                          illustration_slug='roue_zodiaque')

    # ─── 5. Boucle sur les planètes (double page chacune) ─────────────
    planets = natal_data.get('planets', [])
    for i, planet in enumerate(planets):
        name = planet.get('name', '')
        sign = planet.get('sign', '')
        analysis = planet.get('analysis', '') or f'Ton {name} en {sign} raconte une facette essentielle de ton histoire.'

        persona = PLANET_PERSONA.get(name, {'glyph': '✦', 'tagline': f'{name}, ton alliée intérieure.',
                                             'illus': 'astral_planete'})
        # (a) Page glyph
        planet_glyph_page(story, styles, glyph=persona['glyph'],
                           planet_name=name, tagline=persona['tagline'])
        # (b) Page analyse avec dialogue psychologique
        planet_analysis_page(story, styles, planet_name=name, sign=sign,
                              body_html=analysis,
                              dialogue_question=PLANET_DIALOGUE.get(name))

        # (c) Waouh quote entre planètes (sauf la dernière)
        if i < len(planets) - 1 and i < len(WAOUH_QUOTES):
            waouh_quote_page(story, styles, quote=WAOUH_QUOTES[i],
                              illustration_slug=persona['illus'])
            # Teaser pour la suivante
            if i + 1 < len(CHAPTER_TEASERS):
                teaser_text = CHAPTER_TEASERS[min(i + 1, len(CHAPTER_TEASERS) - 1)]
                if '{sun_sign}' not in teaser_text:
                    teaser_page(story, styles, teaser_text)

    # ─── 6. Fin émotionnelle Soléna ──────────────────────────────────
    emotional_ending(story, styles, prenom=prenom)

    doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
    return buf.getvalue()
