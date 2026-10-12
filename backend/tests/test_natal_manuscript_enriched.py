"""Smoke test — build_natal_manuscript enrichi (préface + sommaire + chapitres)."""
from services.natal_manuscript_builder import build_natal_manuscript
from services.natal_preface_generator import _static_fallback
from services.book_engine_shared.domain import BlockKind


# Jeu de données complet simulant la sortie de theme_natal_oneshot_service
_PLANETS_DETAIL = [
    {'name': 'Soleil',   'sign': 'Vierge',    'house': 2, 'degree': 15.5},
    {'name': 'Lune',     'sign': 'Capricorne', 'house': 6, 'degree': 23.1},
    {'name': 'Mercure',  'sign': 'Vierge',    'house': 2, 'degree': 8.2},
    {'name': 'Vénus',    'sign': 'Lion',      'house': 1, 'degree': 11.4},
    {'name': 'Mars',     'sign': 'Scorpion',  'house': 4, 'degree': 2.7},
    {'name': 'Jupiter',  'sign': 'Taureau',   'house': 10, 'degree': 18.0, 'retrograde': True},
    {'name': 'Saturne',  'sign': 'Capricorne', 'house': 6, 'degree': 25.3},
    {'name': 'Uranus',   'sign': 'Verseau',   'house': 7, 'degree': 5.5},
    {'name': 'Neptune',  'sign': 'Poissons',  'house': 8, 'degree': 12.1},
    {'name': 'Pluton',   'sign': 'Scorpion',  'house': 4, 'degree': 20.9},
]

_PLANETS_NARRATIVE = [
    {'name': p['name'], 'sign': p['sign'],
     'analysis': f"Analyse pour {p['name']} en {p['sign']} — un paragraphe un peu long pour simuler la prose IA."}
    for p in _PLANETS_DETAIL
]

_ASPECTS = [
    {'aspecting_planet': 'Soleil',   'aspected_planet': 'Lune',     'type': 'trine',       'orb': 2.1},
    {'aspecting_planet': 'Soleil',   'aspected_planet': 'Mercure',  'type': 'conjunction', 'orb': 7.3},
    {'aspecting_planet': 'Vénus',    'aspected_planet': 'Mars',     'type': 'square',      'orb': 1.2},
    {'aspecting_planet': 'Jupiter',  'aspected_planet': 'Saturne',  'type': 'opposition',  'orb': 3.5},
    {'aspecting_planet': 'Mars',     'aspected_planet': 'Pluton',   'type': 'conjunction', 'orb': 4.0},
    {'aspecting_planet': 'Mercure',  'aspected_planet': 'Vénus',    'type': 'sextile',     'orb': 3.1},
]

_HOUSE_CUSPS = [
    {'house': i, 'sign': s, 'degree': (i * 30 + 5) % 30}
    for i, s in enumerate(
        ['Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne',
         'Verseau', 'Poissons', 'Bélier', 'Taureau', 'Gémeaux', 'Cancer'], start=1
    )
]


def _natal_data(no_birth_time: bool = False) -> dict:
    return {
        'sun_sign': 'Vierge', 'moon_sign': 'Capricorne',
        'ascendant_sign': '' if no_birth_time else 'Lion',
        'no_birth_time': no_birth_time,
        'planets': _PLANETS_NARRATIVE,
        'planets_detail': _PLANETS_DETAIL,
        'aspects': _ASPECTS,
        'house_cusps': _HOUSE_CUSPS,
        'tier': 'ultra',
        'synthese_aspects': 'Deux dynamiques se dessinent dans votre thème.\n\nUne tension créatrice.',
    }


def test_manuscript_has_multiple_chapters():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    assert len(m.chapters) >= 5, f"Attendu au moins 5 chapitres, trouvé {len(m.chapters)}"
    slugs = [c.slug for c in m.chapters]
    assert 'natal_preface' in slugs
    assert 'natal_synthese' in slugs
    assert 'natal_planets' in slugs
    assert 'natal_houses' in slugs
    assert 'natal_aspects' in slugs
    assert 'natal_closing' in slugs


def test_manuscript_chapters_have_openings():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    for ch in m.chapters:
        assert ch.blocks, f'Chapitre {ch.slug} vide'
        assert ch.blocks[0].kind == BlockKind.CHAPTER_OPENING, f'{ch.slug} ne commence pas par un chapter_opening'


def test_manuscript_roman_numerals_renumbered():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    expected = ['I', 'II', 'III', 'IV', 'V', 'VI']
    actual = [c.roman_num for c in m.chapters]
    assert actual == expected[:len(actual)], f"Numérotation incorrecte: {actual}"


def test_preface_fallback_is_substantial():
    blocks = _static_fallback('Amélie')
    assert len(blocks) >= 6, f"Préface trop courte: {len(blocks)} blocs"
    paras = [b for b in blocks if b['kind'] == 'paragraph']
    assert len(paras) >= 4, f"Pas assez de paragraphes: {len(paras)}"
    # Doit mentionner le prénom au moins une fois
    assert any('Amélie' in b['text'] for b in blocks)
    # Doit évoquer la vie longue
    all_text = ' '.join(b['text'] for b in blocks).lower()
    assert any(w in all_text for w in ('années', 'étapes', 'longtemps', 'vie'))


def test_manuscript_includes_degrees_and_houses_in_planet_titles():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    planets_chapter = next(c for c in m.chapters if c.slug == 'natal_planets')
    h2_texts = [b.data['text'] for b in planets_chapter.blocks if b.kind == BlockKind.H2]
    soleil = next((t for t in h2_texts if t.startswith('Soleil en')), None)
    assert soleil, f"Pas de H2 Soleil, trouvé: {h2_texts[:10]}"
    assert '°' in soleil, f"Degré manquant: {soleil}"
    assert 'maison' in soleil.lower(), f"Maison manquante: {soleil}"


def test_manuscript_lists_12_houses():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    houses_chapter = next(c for c in m.chapters if c.slug == 'natal_houses')
    h2_texts = [b.data['text'] for b in houses_chapter.blocks if b.kind == BlockKind.H2]
    house_names = ('Première maison', 'Deuxième maison', 'Troisième maison', 'Quatrième maison',
                    'Cinquième maison', 'Sixième maison', 'Septième maison', 'Huitième maison',
                    'Neuvième maison', 'Dixième maison', 'Onzième maison', 'Douzième maison')
    house_h2s = [t for t in h2_texts if any(t.startswith(hn) for hn in house_names)]
    assert len(house_h2s) == 12, f"Attendu 12 maisons, trouvé {len(house_h2s)}: {house_h2s}"


def test_manuscript_groups_aspects_by_type():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    aspects_chapter = next(c for c in m.chapters if c.slug == 'natal_aspects')
    h2_texts = [b.data['text'] for b in aspects_chapter.blocks if b.kind == BlockKind.H2]
    types_found = []
    for prefix in ('Conjonctions', 'Oppositions', 'Trigones', 'Carrés', 'Sextiles'):
        if any(t.startswith(prefix) for t in h2_texts):
            types_found.append(prefix)
    assert len(types_found) == 5, f"Attendu 5 groupes d'aspects, trouvé {types_found}"


def test_manuscript_no_birth_time_skips_houses_chapter():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data(no_birth_time=True))
    slugs = [c.slug for c in m.chapters]
    assert 'natal_houses' not in slugs
    assert 'natal_aspects' in slugs  # aspects restent calculables sans heure


def test_manuscript_fallback_sans_aspects_ni_maisons():
    data = _natal_data()
    data['aspects'] = []
    data['house_cusps'] = []
    data['planets_detail'] = []
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=data)
    all_text = ''
    for ch in m.chapters:
        for b in ch.blocks:
            all_text += ' ' + (b.data.get('text') or '')
    assert 'faute d' not in all_text.lower()
    assert 'manquant' not in all_text.lower()


def test_manuscript_astro_data_has_toc_flag():
    m = build_natal_manuscript(prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data())
    assert m.astro_data['has_toc'] is True
    assert m.astro_data['planet_count'] == 10
    assert m.astro_data['house_count'] == 12
    assert m.astro_data['aspect_count'] >= 5


def test_preface_blocks_accepted():
    """Les preface_blocks fournis doivent être utilisés au lieu du fallback."""
    custom = [
        {'kind': 'paragraph', 'text': 'Ceci est une préface sur mesure.'},
        {'kind': 'h2', 'text': 'Un titre custom'},
        {'kind': 'paragraph', 'text': 'Autre paragraphe custom.'},
    ]
    m = build_natal_manuscript(
        prenom='Amélie', birth_date='1990-09-15', natal_data=_natal_data(),
        preface_blocks=custom,
    )
    preface_ch = next(c for c in m.chapters if c.slug == 'natal_preface')
    texts = [b.data.get('text', '') for b in preface_ch.blocks]
    assert any('préface sur mesure' in t for t in texts)
    assert any('titre custom' in t for t in texts)
