"""natal_manuscript_builder — Thème Natal en vrai livre (préface + sommaire + chapitres)
================================================================================

Produit un Manuscript multi-chapitres pour le PDF Thème Natal (A5 print blanc).

Structure éditoriale :
  Chapitre I   — Préface « Comment lire ce livre » (AI-générée, ~3 pages)
  Chapitre II  — Votre ciel en synthèse (trio + roue + synthèse exécutive)
  Chapitre III — Vos planètes (10 planètes, 2 par page = 5 pages)
  Chapitre IV  — Vos douze maisons (12 maisons, 3 par page = 4 pages)
  Chapitre V   — Vos aspects (5 groupes = 5 pages)
  Chapitre VI  — Synthèse — ce que votre ciel vous dit (voix Soléna, 1-2 pages)

Chaque chapitre a sa belle page recto. Le renderer book_engine_v2 ajoute :
  - Couverture, blanche, titre, blanche
  - Sommaire (nouveau — voir `_toc.html`)
  - Pour le Ch. II : roue céleste + tableaux positions/aspects
  - Colophon final + blanches pour multiple de 4

L'appelant fournit `natal_data` (positions, aspects, cuspides, prose IA) via
`natal_pdf_adapter.generate_manuscrit_pdf`. Les helpers d'extraction
viennent de `natal_chart_extract.py`.
"""
from __future__ import annotations
import base64
import logging
import re
import unicodedata
from datetime import datetime, timezone

from services.book_engine_shared.domain import (
    BirthData, BlockKind, Chapter, ChapterBlock, Edition, Manuscript,
)
from services import natal_manuscript_extract as nce

logger = logging.getLogger(__name__)


# Supprime toute signature résiduelle « Soléna » issue d'anciens caches ou
# de prompts legacy. La seule signature autorisée dans le PDF visible est
# « Plume Astrale ».
_SOLENA_SIG_RE = re.compile(
    r'''(
            [—\-–]\s*Sol[eé]na[^.\n<]*     # « — Soléna, pour Plume Astrale. »
            |Sol[eé]na\s+vous\s+parle[^.\n<]*\.?     # « Soléna vous parle. »
            |Sol[eé]na\s+speaks[^.\n<]*\.?           # EN
            |Signé[\s:]+Sol[eé]na[^.\n<]*\.?         # « Signé Soléna »
            |Signed[\s:]+Sol[eé]na[^.\n<]*\.?        # EN
        )
    ''',
    re.VERBOSE | re.IGNORECASE,
)
_SOLENA_WORD_RE = re.compile(r'Sol[eé]na', re.IGNORECASE)


def _strip_solena(text: str) -> str:
    """Nettoie toute mention visible de « Soléna » (défense de dernier recours
    pour les textes IA issus d'anciens caches)."""
    if not text or 'olen' not in text.lower() and 'oléna' not in text.lower():
        return text
    cleaned = _SOLENA_SIG_RE.sub('', text)
    cleaned = _SOLENA_WORD_RE.sub('Plume Astrale', cleaned)
    # Nettoie les doublons de ponctuation / espaces créés par les suppressions.
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)
    cleaned = re.sub(r'\s+([,.;:!?])', r'\1', cleaned)
    return cleaned.strip()


# ─── i18n FR/EN pour TOUS les titres de chapitres, kickers, intros ──
# Ces strings étaient hardcodés en français ; la table ci-dessous permet au
# renderer anglais (print_book_renderer, language='en') d'avoir un livre 100%
# EN même quand l'IA de contenu génère déjà de l'anglais.
_I18N: dict[str, dict[str, str | list | dict]] = {
    'fr': {
        'months': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                   'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
        'born_on': 'Né·e le {date}.',
        # Chapitres principaux
        'ch_preface_title': "Comment lire ce livre",
        'ch_preface_kicker': "Un mode d'emploi tendre, pour les années à venir.",
        'ch_preface_short_kicker': "Un mode d'emploi tendre.",
        'ch_synthese_title': 'Le Ciel de {name}',
        'ch_synthese_kicker': 'Trois signatures qui composent votre identité céleste.',
        'ch_synthese_short_kicker': 'Vos trois signatures.',
        'ch_synthese_glance': "Synthèse en un coup d'œil",
        'sun_label': 'Soleil', 'moon_label': 'Lune', 'asc_label': 'Ascendant',
        'natal_chart_alt': 'Roue du ciel de {name}',
        'sun_para': ("Votre Soleil brille en <b>{sign}</b> — c'est le cœur de votre identité, "
                     "ce que vous rayonnez quand vous êtes pleinement vous-même."),
        'moon_para': ("Votre Lune se love en <b>{sign}</b> — c'est votre monde intérieur, "
                      "la façon dont vous vous apaisez, dont vous aimez, dont vous ressentez."),
        'asc_para': ("Votre Ascendant lève en <b>{sign}</b> — c'est le masque que votre âme "
                     "a choisi, la première note que vous donnez au monde."),
        'aspects_count': ("Votre thème compte <b>{n} aspects majeurs</b> entre vos planètes — "
                          "autant de dialogues célestes qui composent votre nuance unique."),
        'houses_count': ("<b>{n} des douze maisons</b> accueillent au moins une planète — "
                         "ce sont vos domaines de vie les plus actifs, ceux où le ciel vous appelle à vivre."),
        # Planètes
        'ch_planets_title': 'Vos planètes',
        'ch_planets_kicker': 'Dix forces qui composent votre palette intérieure.',
        'ch_planets_short_kicker': 'Dix forces, dix couleurs.',
        'ch_planets_intro': ("Dix forces habitent votre ciel. Chacune vit dans un signe, à un degré précis, "
                             "et occupe un territoire de votre vie — une maison. Ce chapitre les présente une à une, "
                             "dans l'ordre où elles tissent votre complexité."),
        'house_prefix': 'maison',
        'retrograde': 'rétrograde ℞',
        'planet_fallback': ("{planet} en {sign} parle de {hint}. "
                             "C'est une couleur à part entière de votre palette intérieure."),
        # Maisons
        'ch_houses_title': 'Vos douze maisons',
        'ch_houses_kicker': 'Les scènes de votre vie, telles que le ciel les éclaire.',
        'ch_houses_short_kicker': 'Douze scènes, douze théâtres.',
        'ch_houses_intro': ("Si les planètes sont vos acteurs intérieurs, les maisons sont les scènes où ils se produisent. "
                            "Douze territoires, douze théâtres de vie. Chaque maison tient un domaine : votre apparence, "
                            "votre foyer, vos liens, votre travail, vos rêves — et davantage. Celles où séjournent une "
                            "ou plusieurs planètes sont vos foyers actifs ; les autres, vous les habitez plus discrètement."),
        'house_planet_singular': 'planète',
        'house_planet_plural': 'planètes',
        'house_cusp_full': 'La cuspide de la <b>{name}</b> tombe en <b>{sign}</b> à {cusp}.',
        'house_cusp_no_deg': 'La cuspide de la <b>{name}</b> tombe en <b>{sign}</b>.',
        'house_no_sign': '<b>{name}</b> — {theme}.',
        'house_governs': 'Cette maison gouverne {desc}.',
        'house_one_planet': "Une planète y séjourne : <b>{planet}</b>. Elle colore ce domaine de son énergie propre.",
        'house_many_planets': "Plusieurs planètes y séjournent — {planets}. Ce secteur est un foyer actif de votre thème.",
        'house_empty': "Aucune planète n'y séjourne : vous l'habitez à votre rythme, sans projecteur astral permanent.",
        'conj_and': ' et ',
        # Aspects
        'ch_aspects_title': 'Vos aspects',
        'ch_aspects_kicker': 'La danse invisible entre vos planètes.',
        'ch_aspects_short_kicker': 'Vos planètes se parlent.',
        'ch_aspects_intro': ("Les planètes se parlent. Certaines se renforcent (<i>conjonction</i>, <i>trigone</i>, "
                             "<i>sextile</i>), d'autres se frottent (<i>opposition</i>, <i>carré</i>). Chaque dialogue "
                             "laisse une empreinte dans votre caractère. Voici les plus marquants, groupés par nature."),
        'aspect_fallback': "<b>{a} {type} {b}</b> — ce dialogue planétaire laisse sa marque dans votre thème.",
        'aspect_orb': 'orbe {orb:.1f}°',
        'aspect_groups': [
            ('Conjonction', "Les conjonctions fusionnent deux forces en une seule note — elles amplifient."),
            ('Opposition', "Les oppositions mettent deux pôles face à face — elles cherchent l'équilibre."),
            ('Trigone', "Les trigones font circuler l'énergie en douceur — ce sont vos talents naturels."),
            ('Carré', "Les carrés provoquent la friction nécessaire au mouvement — ce sont vos moteurs."),
            ('Sextile', "Les sextiles sont des opportunités discrètes — elles s'ouvrent si vous les saisissez."),
        ],
        # Chapitre final + sections éditoriales
        'ch_closing_title': 'Ce que votre ciel vous dit',
        'ch_closing_kicker': 'Synthèse — à relire en période de doute.',
        'ch_closing_short_kicker': 'Plume Astrale vous parle.',
        'editorial_titles': {
            'element_analysis': 'Votre élément dominant',
            'modality_analysis': 'Votre manière de vous mettre en mouvement',
            'trio_synthesis': 'Votre signature personnelle',
            'aspects_harmonieux_body': 'Vos ressources et vos harmonies',
            'aspects_tensions_body': 'Vos tensions et vos chemins d\u2019évolution',
            'rare_aspect_body': 'Votre note singulière',
            'year_ahead': 'Mettre votre thème en perspective',
        },
        'ex_libris_title': 'Ex Libris · Signature astrale de {name}',
        # Hints courts par planète (fallback si l'IA n'a pas de prose)
        'planet_hints': {
            'Soleil':   "le cœur de votre identité, ce que vous rayonnez quand vous êtes vous-même",
            'Lune':     "votre monde intérieur, vos réflexes émotionnels, vos tendresses secrètes",
            'Mercure':  "votre façon de penser, de parler, d'apprendre",
            'Vénus':    "votre manière d'aimer, de goûter, d'embellir",
            'Mars':     "votre élan, votre colère, ce qui vous met en mouvement",
            'Jupiter':  "votre zone d'expansion, ce qui vous fait grandir et avoir confiance",
            'Saturne':  "votre colonne vertébrale, les leçons qui bâtissent votre souveraineté",
            'Uranus':   "votre liberté, vos coups de pied dans la table, vos éclats visionnaires",
            'Neptune':  "vos rêves, votre spiritualité, ce qui dissout vos contours",
            'Pluton':   "votre pouvoir, ce qui vous transforme en profondeur, votre part de nuit",
            'Ascendant': "le masque que votre âme a choisi — ce que les autres voient en premier",
        },
        # Table de traduction nom-planète FR→EN (utilisée par la version EN)
        'planet_names_fr_to_local': {},  # identité en FR
    },
    'en': {
        'months': ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'],
        'born_on': 'Born on {date}.',
        'ch_preface_title': 'How to read this book',
        'ch_preface_kicker': 'A tender user guide, for the years ahead.',
        'ch_preface_short_kicker': 'A tender user guide.',
        'ch_synthese_title': "{name}'s Sky",
        'ch_synthese_kicker': 'Three signatures that compose your celestial identity.',
        'ch_synthese_short_kicker': 'Your three signatures.',
        'ch_synthese_glance': 'Synthesis at a glance',
        'sun_label': 'Sun', 'moon_label': 'Moon', 'asc_label': 'Ascendant',
        'natal_chart_alt': "{name}'s sky wheel",
        'sun_para': ('Your Sun shines in <b>{sign}</b> — it is the heart of your identity, '
                     'what you radiate when you are fully yourself.'),
        'moon_para': ('Your Moon rests in <b>{sign}</b> — it is your inner world, '
                      'how you soothe yourself, how you love, how you feel.'),
        'asc_para': ('Your Ascendant rises in <b>{sign}</b> — it is the mask your soul has chosen, '
                     'the first note you give to the world.'),
        'aspects_count': ('Your chart holds <b>{n} major aspects</b> between your planets — '
                          'as many celestial dialogues as there are nuances in you.'),
        'houses_count': ('<b>{n} of the twelve houses</b> host at least one planet — '
                         'these are your most active life areas, where the sky calls you to live.'),
        'ch_planets_title': 'Your planets',
        'ch_planets_kicker': 'Ten forces that compose your inner palette.',
        'ch_planets_short_kicker': 'Ten forces, ten colours.',
        'ch_planets_intro': ('Ten forces inhabit your sky. Each lives in a sign, at a precise degree, '
                             'and occupies a territory of your life — a house. This chapter introduces them one by one, '
                             'in the order they weave your complexity.'),
        'house_prefix': 'house',
        'retrograde': 'retrograde ℞',
        'planet_fallback': ('{planet} in {sign} speaks of {hint}. '
                             'It is a full colour of your inner palette.'),
        'ch_houses_title': 'Your twelve houses',
        'ch_houses_kicker': 'The scenes of your life, lit by the sky.',
        'ch_houses_short_kicker': 'Twelve scenes, twelve theatres.',
        'ch_houses_intro': ('If planets are your inner actors, houses are the stages they perform on. '
                            'Twelve territories, twelve theatres of life. Each house holds a domain: your appearance, '
                            'your home, your bonds, your work, your dreams — and more. Those where one or more planets '
                            'reside are your active hearths; the others, you inhabit more quietly.'),
        'house_planet_singular': 'planet',
        'house_planet_plural': 'planets',
        'house_cusp_full': 'The cusp of the <b>{name}</b> falls in <b>{sign}</b> at {cusp}.',
        'house_cusp_no_deg': 'The cusp of the <b>{name}</b> falls in <b>{sign}</b>.',
        'house_no_sign': '<b>{name}</b> — {theme}.',
        'house_governs': 'This house governs {desc}.',
        'house_one_planet': 'One planet dwells here: <b>{planet}</b>. It colours this domain with its own energy.',
        'house_many_planets': 'Several planets dwell here — {planets}. This sector is an active hearth of your chart.',
        'house_empty': 'No planet dwells here: you inhabit it at your own pace, without a permanent astral spotlight.',
        'conj_and': ' and ',
        'ch_aspects_title': 'Your aspects',
        'ch_aspects_kicker': 'The invisible dance between your planets.',
        'ch_aspects_short_kicker': 'Your planets speak to each other.',
        'ch_aspects_intro': ('Planets speak to each other. Some reinforce one another (<i>conjunction</i>, <i>trine</i>, '
                             '<i>sextile</i>), others rub against each other (<i>opposition</i>, <i>square</i>). Each dialogue '
                             'leaves an imprint in your character. Here are the most striking, grouped by nature.'),
        'aspect_fallback': '<b>{a} {type} {b}</b> — this planetary dialogue leaves its mark on your chart.',
        'aspect_orb': 'orb {orb:.1f}°',
        'aspect_groups': [
            ('Conjonction', 'Conjunctions merge two forces into a single note — they amplify.'),
            ('Opposition', 'Oppositions place two poles face to face — they seek balance.'),
            ('Trigone', 'Trines let energy flow gently — these are your natural talents.'),
            ('Carré', 'Squares provoke the friction needed for movement — these are your engines.'),
            ('Sextile', 'Sextiles are discreet opportunities — they open if you seize them.'),
        ],
        'aspect_group_labels': {
            'Conjonction': 'Conjunction',
            'Opposition': 'Opposition',
            'Trigone': 'Trine',
            'Carré': 'Square',
            'Sextile': 'Sextile',
        },
        'ch_closing_title': 'What your sky tells you',
        'ch_closing_kicker': 'Synthesis — to reread in times of doubt.',
        'ch_closing_short_kicker': 'Plume Astrale speaks to you.',
        'editorial_titles': {
            'element_analysis': 'Your dominant element',
            'modality_analysis': 'Your way of setting things in motion',
            'trio_synthesis': 'Your personal signature',
            'aspects_harmonieux_body': 'Your resources and harmonies',
            'aspects_tensions_body': 'Your tensions and paths of growth',
            'rare_aspect_body': 'Your singular note',
            'year_ahead': 'Putting your chart into perspective',
        },
        'ex_libris_title': 'Ex Libris · Astral signature of {name}',
        'planet_hints': {
            'Soleil':   'the core of your identity, what you radiate when you are yourself',
            'Lune':     'your inner world, your emotional reflexes, your secret tendernesses',
            'Mercure':  'your way of thinking, speaking, learning',
            'Vénus':    'your way of loving, savouring, beautifying',
            'Mars':     'your drive, your anger, what sets you in motion',
            'Jupiter':  'your zone of expansion, what helps you grow and trust',
            'Saturne':  'your backbone, the lessons that build your sovereignty',
            'Uranus':   'your freedom, your daring moves, your visionary flashes',
            'Neptune':  'your dreams, your spirituality, what dissolves your contours',
            'Pluton':   'your power, what transforms you deeply, your night-side',
            'Ascendant': 'the mask your soul has chosen — what others see first',
        },
        'planet_names_fr_to_local': {
            'Soleil': 'Sun', 'Lune': 'Moon', 'Mercure': 'Mercury',
            'Vénus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter',
            'Saturne': 'Saturn', 'Uranus': 'Uranus',
            'Neptune': 'Neptune', 'Pluton': 'Pluto',
            'Ascendant': 'Ascendant',
        },
        'house_names_fr_to_local': {
            'Première maison': 'First house', 'Deuxième maison': 'Second house',
            'Troisième maison': 'Third house', 'Quatrième maison': 'Fourth house',
            'Cinquième maison': 'Fifth house', 'Sixième maison': 'Sixth house',
            'Septième maison': 'Seventh house', 'Huitième maison': 'Eighth house',
            'Neuvième maison': 'Ninth house', 'Dixième maison': 'Tenth house',
            'Onzième maison': 'Eleventh house', 'Douzième maison': 'Twelfth house',
        },
        'house_themes_fr_to_local': {
            'Le Soi': 'The Self', 'Les Ressources': 'Resources',
            'La Pensée': 'The Mind', 'Les Racines': 'Roots',
            'La Créativité': 'Creativity', 'Le Quotidien': 'Daily Life',
            'Les Partenariats': 'Partnerships', 'Les Transformations': 'Transformations',
            'Les Horizons': 'Horizons', 'La Vocation': 'Vocation',
            'Les Amitiés': 'Friendships', "L'Inconscient": 'The Unconscious',
        },
    },
}


def _T(language: str, key: str, **kwargs):
    """Récupère une string i18n, formate si kwargs, fallback FR en dernier recours."""
    language = (language or 'fr').lower()
    if language not in _I18N:
        language = 'fr'
    bundle = _I18N[language]
    val = bundle.get(key)
    if val is None:
        val = _I18N['fr'].get(key, '')
    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except (KeyError, IndexError):
            return val
    return val


def _tr_planet(name: str, language: str) -> str:
    """Traduit un nom de planète FR vers la locale (identité en FR)."""
    if language == 'fr':
        return name
    return _I18N['en']['planet_names_fr_to_local'].get(name, name)


def _tr_house_name(name: str, language: str) -> str:
    """Traduit un nom de maison FR vers la locale."""
    if language == 'fr':
        return name
    return _I18N['en'].get('house_names_fr_to_local', {}).get(name, name)


# Signes zodiacaux FR→EN (ne couvre pas les variantes avec accents multiples)
_SIGN_FR_TO_EN = {
    'Bélier': 'Aries', 'Taureau': 'Taurus', 'Gémeaux': 'Gemini',
    'Cancer': 'Cancer', 'Lion': 'Leo', 'Vierge': 'Virgo',
    'Balance': 'Libra', 'Scorpion': 'Scorpio', 'Sagittaire': 'Sagittarius',
    'Capricorne': 'Capricorn', 'Verseau': 'Aquarius', 'Poissons': 'Pisces',
}


def _tr_sign(sign: str, language: str) -> str:
    """Traduit un signe FR vers la locale."""
    if not sign or language == 'fr':
        return sign
    return _SIGN_FR_TO_EN.get(sign, sign)


# Templates d'interprétation d'aspect EN (miroir de _ASPECT_INTERP_TEMPLATES)
_ASPECT_INTERP_EN = {
    'Conjonction': 'Fusion. {a} and {b} play the same note. You feel their qualities as one and the same energy — amplified.',
    'Opposition':  'Tension. {a} and {b} face each other. You swing between the two poles — balance lies at the centre, not in one or the other.',
    'Trigone':     'Harmony. {a} and {b} get on effortlessly. This talent flows, sometimes too easily — it is yours to engage.',
    'Carré':       'Friction. {a} and {b} each want to impose their rhythm. It is uncomfortable, but it is your engine — nothing propels you more than this rubbing.',
    'Sextile':     'Opportunity. {a} and {b} signal to each other. Seize the moment and the energy opens — it never forces anything.',
}


def _interpret_aspect_i18n(aspect: dict, language: str) -> str:
    """Même rôle que nce.interpret_aspect, mais localisé."""
    if language == 'en':
        tmpl = _ASPECT_INTERP_EN.get(aspect.get('type_fr', ''), '')
        if tmpl:
            a = _tr_planet(aspect.get('planet_a', '?'), 'en')
            b = _tr_planet(aspect.get('planet_b', '?'), 'en')
            return tmpl.format(a=a, b=b)
    return nce.interpret_aspect(aspect) or ''


# Thèmes des 12 maisons en anglais : nom court + description « ce que la maison gouverne ».
# Clé = nom FR tel qu'il arrive de HOUSE_THEMES dans natal_chart_extract.
_HOUSE_THEME_EN = {
    'Le Soi':              ('The Self',           'your appearance, your vital drive, your mask'),
    'Les Ressources':      ('Resources',          'your values, your money, your relationship to the body'),
    'La Pensée':           ('The Mind',           'the mind, siblings, short-form learning'),
    'Les Racines':         ('Roots',              'home, origins, family memory'),
    'La Créativité':       ('Creativity',         'love affairs, children, play, creation'),
    'Le Quotidien':        ('Daily Life',         'work, health, service to others'),
    'Les Partenariats':    ('Partnerships',       'the other, contracts, marriage'),
    'Les Transformations': ('Transformations',    'death, sex, regenerative crises'),
    'Les Horizons':        ('Horizons',           'far travels, philosophy, faith'),
    'La Vocation':         ('Vocation',           'career, public recognition'),
    'Les Amitiés':         ('Friendships',        'the collective, projects, causes'),
    "L'Inconscient":       ('The Unconscious',    'secrets, retreat, karma'),
}


def _parse_birth_date(birth_date: str) -> BirthData:
    return BirthData(
        date_iso=birth_date or '',
        time_hhmm=None,
        city='',
        country_code='FR',
    )


# ─── Templates courts : les hints par planète sont désormais dans _I18N ─
# (voir _I18N['fr']['planet_hints'] et _I18N['en']['planet_hints']).


def _house_sentence(house: dict, language: str = 'fr') -> str:
    """Phrase courte pour une maison : cuspide + occupants + thème."""
    name = _tr_house_name(house['name'], language)
    sign_raw = house.get('sign') or ''
    sign = _tr_sign(sign_raw, language)
    cusp = house.get('cusp_degree_str') or ''
    theme = house.get('theme') or ''
    desc = house.get('theme_desc') or ''
    # Pour l'EN, on remplace le theme/desc par la version localisée si disponible
    if language == 'en':
        en_pair = _HOUSE_THEME_EN.get(theme)
        if en_pair:
            theme = en_pair[0]
            desc = en_pair[1]
        else:
            # Essai par matching d'un desc_fr vers son equivalent EN via lookup inversé
            for en_key, (en_theme, en_desc) in _HOUSE_THEME_EN.items():
                if desc and (desc in en_key or en_desc in desc):
                    theme, desc = en_theme, en_desc
                    break
    planets = house.get('planets') or []

    parts = []
    if sign and cusp:
        parts.append(_T(language, 'house_cusp_full', name=name.lower(), sign=sign, cusp=cusp))
    elif sign:
        parts.append(_T(language, 'house_cusp_no_deg', name=name.lower(), sign=sign))
    else:
        parts.append(_T(language, 'house_no_sign', name=name, theme=theme.lower()))

    parts.append(_T(language, 'house_governs', desc=desc))

    if planets:
        tr_planets = [_tr_planet(p, language) for p in planets]
        if len(tr_planets) == 1:
            parts.append(_T(language, 'house_one_planet', planet=tr_planets[0]))
        else:
            noms = ', '.join(f'<b>{p}</b>' for p in tr_planets[:-1]) + f'{_T(language, "conj_and")}<b>{tr_planets[-1]}</b>'
            parts.append(_T(language, 'house_many_planets', planets=noms))
    else:
        parts.append(_T(language, 'house_empty'))

    return ' '.join(parts)


def _aspect_group_paragraphs(aspects: list, nature_hint: str, language: str = 'fr') -> list[str]:
    paras: list[str] = [nature_hint]
    for a in aspects:
        a_name = _tr_planet(a.get('planet_a', '?'), language)
        b_name = _tr_planet(a.get('planet_b', '?'), language)
        # type_fr est toujours en FR ; on le traduit en EN si demandé
        type_label = a.get('type_fr', '').lower()
        if language == 'en':
            labels = _I18N['en'].get('aspect_group_labels') or {}
            canonical = a.get('type_fr', '')
            type_label = labels.get(canonical, canonical).lower()
        interp = _interpret_aspect_i18n(a, language) or _T(language, 'aspect_fallback',
                                                           a=a_name, b=b_name, type=type_label)
        orb = a.get('orb_degrees')
        orb_part = ''
        if isinstance(orb, (int, float)):
            orb_part = f' <i>({_T(language, "aspect_orb", orb=orb)})</i>'
        paras.append(f"<b>{a_name} — {b_name}</b>{orb_part}. {interp}")
    return paras


# ─── Builders de chapitres individuels ──────────────────────────────
def _chapter_preface(preface_blocks: list[dict], prenom: str, language: str = 'fr') -> Chapter:
    """Chapitre I — Comment lire ce livre (préface AI-générée ou statique)."""
    title = _T(language, 'ch_preface_title')
    kicker = _T(language, 'ch_preface_kicker')
    short_k = _T(language, 'ch_preface_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'I',
        'title': title,
        'kicker': kicker,
    }))
    for b in preface_blocks:
        kind = (b.get('kind') or '').lower()
        text = (b.get('text') or '').strip()
        if not text:
            continue
        if kind == 'h2':
            blocks.append(ChapterBlock(BlockKind.H2, {'text': text}))
        else:
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': text, 'raw': True}))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_preface', title=title,
        kicker=short_k, roman_num='I', order=1, blocks=blocks,
    )


def _chapter_synthese(
    prenom: str, birth_date_fr: str, sun_sign: str, moon_sign: str,
    asc_sign: str, no_birth_time: bool, aspects_norm: list, houses: list,
    chart_png_bytes: bytes | None, language: str = 'fr',
) -> Chapter:
    """Chapitre II — Votre ciel en synthèse (trio + roue + highlights)."""
    title = _T(language, 'ch_synthese_title', name=prenom)
    kicker = _T(language, 'ch_synthese_kicker')
    short_k = _T(language, 'ch_synthese_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'II',
        'title': title,
        'kicker': kicker,
    }))

    if birth_date_fr:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': f'<span class="lede-date">{_T(language, "born_on", date=birth_date_fr)}</span>',
            'raw': True,
        }))

    # Trio cards (labels localisés)
    trio: list[dict] = []
    if sun_sign:
        trio.append({'label': _T(language, 'sun_label'), 'sign': _tr_sign(sun_sign, language)})
    if moon_sign:
        trio.append({'label': _T(language, 'moon_label'), 'sign': _tr_sign(moon_sign, language)})
    if asc_sign and not no_birth_time:
        trio.append({'label': _T(language, 'asc_label'), 'sign': _tr_sign(asc_sign, language)})
    if trio:
        blocks.append(ChapterBlock(BlockKind.TRIO_CARDS, {'items': trio}))

    # Chart wheel — toujours sur sa propre page, pleine, sans texte autour
    # (reproductible comme affiche téléchargeable / vendue séparément).
    if chart_png_bytes:
        try:
            b64 = base64.b64encode(chart_png_bytes).decode('ascii')
            blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
            blocks.append(ChapterBlock(BlockKind.NATAL_CHART, {
                'src': f'data:image/png;base64,{b64}',
                'alt': _T(language, 'natal_chart_alt', name=prenom),
                'full_page': True,
            }))
        except Exception as e:
            logger.warning(f'[natal_manuscript] chart encoding failed: {e}')

    # Synthèse exécutive sur page suivante
    blocks.append(ChapterBlock(BlockKind.PAGE_BREAK, {}))
    blocks.append(ChapterBlock(BlockKind.H2, {'text': _T(language, 'ch_synthese_glance')}))
    if sun_sign:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _T(language, 'sun_para', sign=_tr_sign(sun_sign, language)),
            'raw': True,
        }))
    if moon_sign:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _T(language, 'moon_para', sign=_tr_sign(moon_sign, language)),
            'raw': True,
        }))
    if asc_sign and not no_birth_time:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _T(language, 'asc_para', sign=_tr_sign(asc_sign, language)),
            'raw': True,
        }))
    nb_aspects = len(aspects_norm)
    nb_houses = sum(1 for h in houses if h.get('planets'))
    if nb_aspects:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _T(language, 'aspects_count', n=nb_aspects),
            'raw': True,
        }))
    if nb_houses:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _T(language, 'houses_count', n=nb_houses),
            'raw': True,
        }))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_synthese', title=title,
        kicker=short_k, roman_num='II', order=2, blocks=blocks,
    )


def _planet_illust_block(planet_name_fr: str, illustrations: dict | None) -> ChapterBlock | None:
    """Retourne un bloc IMAGE vignette pour une planète si l'illustration existe."""
    if not illustrations:
        return None
    planets_imgs = illustrations.get('planets') or {}
    key = unicodedata.normalize('NFKD', str(planet_name_fr or ''))\
        .encode('ascii', 'ignore').decode('ascii')
    key = re.sub(r'[^a-z0-9]+', '', key.lower())
    png = planets_imgs.get(key)
    if not png:
        return None
    b64 = base64.b64encode(png).decode('ascii')
    return ChapterBlock(BlockKind.IMAGE, {
        'src': f'data:image/png;base64,{b64}',
        'max_width_mm': 65,
        'max_height_mm': 65,
        'alt': f'Vignette {planet_name_fr}',
    })


def _chapter_planets(planets_narr: list, pos_by_name: dict, no_birth_time: bool, language: str = 'fr',
                     illustrations: dict | None = None) -> Chapter:
    """Chapitre III — Vos planètes (2 planètes par page = 5 pages pleines)."""
    title = _T(language, 'ch_planets_title')
    kicker = _T(language, 'ch_planets_kicker')
    short_k = _T(language, 'ch_planets_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'III',
        'title': title,
        'kicker': kicker,
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': _T(language, 'ch_planets_intro'),
    }))

    hints_bundle = _I18N.get(language, _I18N['fr']).get('planet_hints', {}) or {}
    # Flux continu type livre : les planètes s'enchaînent naturellement avec
    # séparateur (ornement/hairline) entre chaque bloc. ReportLab gère les
    # sauts de page sans laisser de blancs forcés.
    valid_planets = [p for p in planets_narr
                     if (p.get('name') or '').strip() and (p.get('sign') or '').strip()]
    for i, p in enumerate(valid_planets):
        name_fr = p['name'].strip()
        name_display = _tr_planet(name_fr, language)
        sign_raw = p['sign'].strip()
        sign = _tr_sign(sign_raw, language)
        analysis = (p.get('analysis') or '').strip()
        # Séparateur décoratif entre deux planètes (pas de PAGE_BREAK forcé)
        if i > 0:
            blocks.append(ChapterBlock(BlockKind.HAIRLINE, {}))
        det = pos_by_name.get(name_fr) or {}
        in_word = 'in' if language == 'en' else 'en'
        parts = [f'{name_display} {in_word} {sign}']
        deg_str = det.get('degree_in_sign_str') or ''
        if deg_str:
            parts.append(deg_str)
        house_num = det.get('house')
        if isinstance(house_num, int) and 1 <= house_num <= 12 and not no_birth_time:
            parts.append(f'{_T(language, "house_prefix")} {house_num}')
        if det.get('retrograde'):
            parts.append(_T(language, 'retrograde'))
        blocks.append(ChapterBlock(BlockKind.H2, {'text': ' · '.join(parts)}))
        if not analysis:
            hint = hints_bundle.get(name_fr, '')
            if hint:
                analysis = _T(language, 'planet_fallback',
                               planet=name_display, sign=sign, hint=hint)
        if analysis:
            paras = [pp.strip() for pp in analysis.split('\n\n') if pp.strip()] or [analysis]
            for para in paras:
                blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))
        # Vignette IA de fin de section planétaire (cache générique partagé)
        illust_block = _planet_illust_block(name_fr, illustrations)
        if illust_block is not None:
            blocks.append(illust_block)

    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_planets', title=title,
        kicker=short_k, roman_num='III', order=3, blocks=blocks,
    )


def _chapter_houses(houses: list, language: str = 'fr') -> Chapter:
    """Chapitre IV — Vos douze maisons (3 par page = 4 pages pleines)."""
    title = _T(language, 'ch_houses_title')
    kicker = _T(language, 'ch_houses_kicker')
    short_k = _T(language, 'ch_houses_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'IV',
        'title': title,
        'kicker': kicker,
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': _T(language, 'ch_houses_intro'),
    }))
    for idx, h in enumerate(houses):
        # Flux continu : séparateur discret entre maisons, ReportLab gère les pages.
        if idx > 0:
            blocks.append(ChapterBlock(BlockKind.HAIRLINE, {}))
        h2 = _tr_house_name(h['name'], language)
        if h.get('sign'):
            h2 += f" · {_tr_sign(h['sign'], language)}"
        if h.get('planets'):
            n = len(h['planets'])
            word_singular = _T(language, 'house_planet_singular')
            word_plural = _T(language, 'house_planet_plural')
            h2 += f" ({n} {word_plural if n > 1 else word_singular})"
        blocks.append(ChapterBlock(BlockKind.H2, {'text': h2}))
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
            'text': _house_sentence(h, language=language), 'raw': True,
        }))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_houses', title=title,
        kicker=short_k, roman_num='IV', order=4, blocks=blocks,
    )


def _chapter_aspects(aspects_norm: list, language: str = 'fr') -> Chapter:
    """Chapitre V — Vos aspects (5 groupes = 5 pages ou moins si certains vides)."""
    title = _T(language, 'ch_aspects_title')
    kicker = _T(language, 'ch_aspects_kicker')
    short_k = _T(language, 'ch_aspects_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'V',
        'title': title,
        'kicker': kicker,
    }))
    blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {
        'text': _T(language, 'ch_aspects_intro'),
        'raw': True,
    }))
    groups = _T(language, 'aspect_groups')
    labels_map = _I18N.get(language, _I18N['fr']).get('aspect_group_labels') or {}
    # Flux continu entre familles d'aspects ; séparateur ornemental entre blocs.
    rendered_groups = 0
    for type_fr, hint in groups:
        sub = [a for a in aspects_norm if a.get('type_fr') == type_fr]
        if not sub:
            continue
        if rendered_groups > 0:
            blocks.append(ChapterBlock(BlockKind.HAIRLINE, {}))
        rendered_groups += 1
        type_label = labels_map.get(type_fr, type_fr)
        blocks.append(ChapterBlock(BlockKind.H2, {'text': f'{type_label}s — {len(sub)}'}))
        for para in _aspect_group_paragraphs(sub, hint, language=language):
            blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para, 'raw': True}))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_aspects', title=title,
        kicker=short_k, roman_num='V', order=5, blocks=blocks,
    )


def _chapter_synthese_finale(synthese_text: str, language: str = 'fr',
                              closing_png: bytes | None = None) -> Chapter:
    """Chapitre VI — Synthèse finale voix Soléna."""
    title = _T(language, 'ch_closing_title')
    kicker = _T(language, 'ch_closing_kicker')
    short_k = _T(language, 'ch_closing_short_kicker')
    blocks: list[ChapterBlock] = []
    blocks.append(ChapterBlock(BlockKind.CHAPTER_OPENING, {
        'roman_num': 'VI',
        'title': title,
        'kicker': kicker,
    }))
    paras = [p.strip() for p in synthese_text.split('\n\n') if p.strip()] or [synthese_text]
    for para in paras:
        blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': para}))
    # Vignette de clôture IA — remplit la demi-page vide en fin de chapitre
    if closing_png:
        b64 = base64.b64encode(closing_png).decode('ascii')
        blocks.append(ChapterBlock(BlockKind.IMAGE, {
            'src': f'data:image/png;base64,{b64}',
            'max_width_mm': 90,
            'max_height_mm': 90,
            'alt': 'Illustration de clôture',
        }))
    blocks.append(ChapterBlock(BlockKind.FEATHER, {}))
    return Chapter(
        slug='natal_closing', title=title,
        kicker=short_k, roman_num='VI', order=6, blocks=blocks,
    )


# ─── Builder principal ──────────────────────────────────────────────
def build_natal_manuscript(
    *,
    prenom: str,
    birth_date: str,
    natal_data: dict,
    chart_png_bytes: bytes | None = None,
    user_email: str = '',
    session_id: str = '',
    preface_blocks: list[dict] | None = None,
    book_data: dict | None = None,
    language: str = 'fr',
    illustrations: dict | None = None,
) -> Manuscript:
    """Construit un Manuscript multi-chapitres prêt à être rendu en PDF print blanc.

    `preface_blocks` optionnel : blocs AI-générés (list of {'kind', 'text'}).
    Si absent, un fallback statique de qualité est utilisé.

    `language` : 'fr' (défaut) ou 'en' — tous les titres de chapitres, kickers,
    intros structurels et dates sont alors localisés.

    `natal_data` attendus :
      sun_sign, moon_sign, ascendant_sign, no_birth_time
      planets[]        — [{name, sign, analysis}]  (per-planet AI prose)
      planets_detail[] — [{name, sign, degree_in_sign, house, retrograde}]  (facultatif)
      aspects[]        — [{planet_a, planet_b, type, orb}]  (facultatif, format API)
      house_cusps      — {num: {sign, degree}}  (facultatif)
      synthese_aspects — paragraphe Soléna optionnel
      tier             — 'ultra' ou 'legacy'
    """
    prenom = (prenom or 'Voyageuse').strip() or 'Voyageuse'
    language = (language or 'fr').lower()
    if language not in _I18N:
        language = 'fr'

    def _fmt_date_local(date_iso: str) -> str:
        if not date_iso:
            return ''
        try:
            y, mo, d = date_iso.split('-')[:3]
            months = _T(language, 'months') or _I18N['fr']['months']
            if language == 'en':
                return f'{months[int(mo) - 1]} {int(d)}, {y}'
            return f'{int(d)} {months[int(mo) - 1]} {y}'
        except Exception:
            return date_iso or ''
    birth_date_fr = _fmt_date_local(birth_date)

    no_birth_time = bool(natal_data.get('no_birth_time'))

    # Extraction/normalisation via natal_chart_extract
    extract_input = {
        'planets': natal_data.get('planets_detail') or natal_data.get('planets') or [],
        'aspects': natal_data.get('aspects') or [],
        'house_cusps': natal_data.get('house_cusps') or {},
    }
    planet_positions = nce.extract_planet_positions(extract_input)
    houses = nce.extract_houses(extract_input, planets=planet_positions) if not no_birth_time else []
    aspects_norm = nce.extract_aspects(extract_input, planets=planet_positions)
    pos_by_name = {p['name']: p for p in planet_positions}

    sun_sign = natal_data.get('sun_sign') or ''
    moon_sign = natal_data.get('moon_sign') or ''
    asc_sign = natal_data.get('ascendant_sign') or ''

    # Préface — AI blocks ou fallback statique
    if not preface_blocks:
        # Import local pour permettre un stub des tests sans réseau
        try:
            from services.natal_preface_generator import _static_fallback
            preface_blocks = _static_fallback(prenom, language=language)
        except Exception:
            preface_blocks = []

    book_data = book_data or {}

    def editorial(slug, title, text):
        blocks = [ChapterBlock(BlockKind.PARAGRAPH, {'text': paragraph})
                  for paragraph in str(text or '').split('\n\n') if paragraph.strip()]
        return Chapter(slug=slug, title=title, blocks=blocks)

    # Construction des chapitres
    chapters: list[Chapter] = []
    chapters.append(_chapter_preface(preface_blocks or [], prenom, language=language))
    chapters.append(_chapter_synthese(
        prenom, birth_date_fr, sun_sign, moon_sign, asc_sign,
        no_birth_time, aspects_norm, houses, chart_png_bytes, language=language,
    ))

    editorial_titles = _I18N.get(language, _I18N['fr']).get('editorial_titles') or {}
    for key in ('element_analysis', 'modality_analysis', 'trio_synthesis'):
        if str(book_data.get(key) or '').strip():
            title = editorial_titles.get(key) or key
            chapters.append(editorial(key, title, book_data[key]))

    planets_narr = natal_data.get('planets') or []
    if planets_narr:
        chapters.append(_chapter_planets(planets_narr, pos_by_name, no_birth_time,
                                         language=language, illustrations=illustrations))

    if houses and not no_birth_time:
        house_chapter = _chapter_houses(houses, language=language)
        # Insert the actual personalised prose after its corresponding house title.
        enriched = []
        if book_data.get('houses_intro'):
            enriched.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': book_data['houses_intro']}))
        house_index = 0
        for block in house_chapter.blocks:
            enriched.append(block)
            if block.kind == BlockKind.H2:
                house_index += 1
            if block.kind == BlockKind.PARAGRAPH and house_index:
                text = str(book_data.get(f'house_{house_index}') or '').strip()
                if text:
                    enriched.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': text}))
        house_chapter.blocks = enriched
        chapters.append(house_chapter)

    if aspects_norm:
        chapters.append(_chapter_aspects(aspects_norm, language=language))

    synthese = (natal_data.get('synthese_aspects') or '').strip()
    closing_png = (illustrations or {}).get('closing')
    if synthese:
        chapters.append(_chapter_synthese_finale(synthese, language=language,
                                                 closing_png=closing_png))

    # Sections éditoriales de fin (headlines personnalisables côté book_data,
    # sinon fallback localisé).
    for key in ('aspects_harmonieux_body', 'aspects_tensions_body', 'rare_aspect_body', 'year_ahead'):
        if not str(book_data.get(key) or '').strip():
            continue
        headline_key = {
            'aspects_harmonieux_body': 'aspects_harmonieux_headline',
            'aspects_tensions_body': 'aspects_tensions_headline',
            'rare_aspect_body': 'rare_aspect_headline',
        }.get(key)
        title = (book_data.get(headline_key) if headline_key else None) or editorial_titles.get(key) or key
        chapters.append(editorial(key, title, book_data[key]))

    # Page Signature · Ex Libris
    ex_libris_text = str(book_data.get('ex_libris') or '').strip()
    ex_libris_png = (illustrations or {}).get('ex_libris')
    if ex_libris_text or ex_libris_png:
        ex_blocks: list[ChapterBlock] = []
        if ex_libris_png:
            # Illustration dominante sur la page Ex Libris (découpable).
            # Pas de full_page : on garde le titre, l'illustration et la
            # signature calligraphique sur la même page A5.
            b64 = base64.b64encode(ex_libris_png).decode('ascii')
            ex_blocks.append(ChapterBlock(BlockKind.IMAGE, {
                'src': f'data:image/png;base64,{b64}',
                'max_width_mm': 95,
                'max_height_mm': 95,
                'alt': _T(language, 'ex_libris_title', name=prenom),
            }))
        for paragraph in str(ex_libris_text or '').split('\n\n'):
            if paragraph.strip():
                ex_blocks.append(ChapterBlock(BlockKind.PARAGRAPH, {'text': paragraph}))
        chapters.append(Chapter(
            slug='ex_libris',
            title=_T(language, 'ex_libris_title', name=prenom),
            blocks=ex_blocks,
        ))

    # Renumérote le roman_num en fonction de l'ordre réel
    _ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII'}
    for i, ch in enumerate(chapters, start=1):
        ch.order = i
        new_rn = _ROMAN.get(i, str(i))
        if ch.roman_num != new_rn:
            ch.roman_num = new_rn
            if ch.blocks and ch.blocks[0].kind == BlockKind.CHAPTER_OPENING:
                ch.blocks[0].data['roman_num'] = new_rn

    manuscript = Manuscript(
        session_id=session_id or f'natal-{prenom.lower()}-{int(datetime.now(timezone.utc).timestamp())}',
        user_email=user_email,
        first_name=prenom,
        birth_data=BirthData(date_iso=birth_date or '', time_hhmm=natal_data.get('birth_time'),
                             city=natal_data.get('birth_city') or '', country_code='FR'),
        astro_data={
            'sun_sign': sun_sign,
            'moon_sign': moon_sign,
            'ascendant_sign': asc_sign,
            'tier': natal_data.get('tier', 'legacy'),
            'planet_count': len(planets_narr),
            'house_count': len(houses),
            'aspect_count': len(aspects_norm),
            'has_toc': True,
            'planets': planet_positions,
            'aspects': aspects_norm,
            'houses': houses,
            'no_birth_time': no_birth_time,
        },
        edition=Edition.NUMERIQUE,
        chapters=chapters,
        design_version='plume-book-flow-2026-10',
        created_at=datetime.now(timezone.utc),
    )
    return manuscript
