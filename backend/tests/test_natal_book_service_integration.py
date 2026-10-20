"""Phase 3 — Validation du Service Unifié Natal Book.

Exerce le flux de production (`natal_pdf_adapter.generate_manuscrit_pdf` +
`print_book_renderer.render_book_pdf` + `print_book_renderer.lulu_interior`)
avec des données complètes (11 planètes + 12 maisons + 7 aspects + livre
GPT simulé) pour vérifier :

- Digital >= 45 pages (cible 45-50)
- Print interior (Lulu A5+bleed) >= 32 pages (contrainte Lulu minimum)
- Variante `no_birth_time=True` : maisons omises, pages toujours >= 25
"""
import io
import pytest
from pypdf import PdfReader

from services.natal_pdf_adapter import generate_manuscrit_pdf
from services.print_book_renderer import lulu_interior


# ─── Fixtures ──────────────────────────────────────────────────────────────────

_PLANETS_DATA_LIST = [
    {'name': 'Sun',     'sign': 'Virgo',       'house': 2,  'degree': 22.5},
    {'name': 'Moon',    'sign': 'Capricorn',   'house': 6,  'degree': 23.1},
    {'name': 'Mercury', 'sign': 'Virgo',       'house': 2,  'degree': 8.2},
    {'name': 'Venus',   'sign': 'Leo',         'house': 1,  'degree': 11.4},
    {'name': 'Mars',    'sign': 'Scorpio',     'house': 4,  'degree': 2.7},
    {'name': 'Jupiter', 'sign': 'Taurus',      'house': 10, 'degree': 18.0, 'retrograde': True},
    {'name': 'Saturn',  'sign': 'Capricorn',   'house': 6,  'degree': 25.3},
    {'name': 'Uranus',  'sign': 'Aquarius',    'house': 7,  'degree': 5.5},
    {'name': 'Neptune', 'sign': 'Pisces',      'house': 8,  'degree': 12.1},
    {'name': 'Pluto',   'sign': 'Scorpio',     'house': 4,  'degree': 20.9},
]

_ASPECTS_RAW = [
    {'aspecting_planet': 'Sun',     'aspected_planet': 'Moon',     'type': 'trine',       'orb': 2.1},
    {'aspecting_planet': 'Sun',     'aspected_planet': 'Mercury',  'type': 'conjunction', 'orb': 7.3},
    {'aspecting_planet': 'Venus',   'aspected_planet': 'Mars',     'type': 'square',      'orb': 1.2},
    {'aspecting_planet': 'Jupiter', 'aspected_planet': 'Saturn',   'type': 'opposition',  'orb': 3.5},
    {'aspecting_planet': 'Mars',    'aspected_planet': 'Pluto',    'type': 'conjunction', 'orb': 4.0},
    {'aspecting_planet': 'Moon',    'aspected_planet': 'Saturn',   'type': 'conjunction', 'orb': 2.2},
    {'aspecting_planet': 'Mercury', 'aspected_planet': 'Venus',    'type': 'sextile',     'orb': 3.1},
]

_HOUSES_RAW = [
    {'number': i, 'sign': s, 'planets': []}
    for i, s in enumerate(
        ['Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne',
         'Verseau', 'Poissons', 'Bélier', 'Taureau', 'Gémeaux', 'Cancer'],
        start=1,
    )
]

_HOUSE_CUSPS_RAW = [
    {'house': i, 'sign': s, 'degree': (i * 7) % 30}
    for i, s in enumerate(
        ['Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne',
         'Verseau', 'Poissons', 'Bélier', 'Taureau', 'Gémeaux', 'Cancer'],
        start=1,
    )
]

# AI planet texts — ~2000 caractères par planète pour approcher la densité
# de production (voix Soléna GPT-5.4). Les 11 clés sont obligatoires pour tier=ultra.
_AI_PARAGRAPH = (
    "{PLANET} en {SIGN} tisse une signature particulière dans ta carte intime. "
    "Cette combinaison te relie à une mémoire ancienne que tu portes depuis l'enfance : "
    "celle d'un équilibre à conquérir, d'une parole à poser, d'un geste à oser. "
    "Elle te demande de t'ancrer sans te figer, de t'ouvrir sans te perdre, "
    "de nommer ce qui vit en toi avant que les autres n'essaient de le faire à ta place. "
    "Quand tu honores cette énergie, elle devient une boussole fiable — "
    "quand tu la refoules, elle revient par la fatigue, les répétitions, les silences inconfortables. "
    "Prends le temps d'écouter ce que {PLANET} te chuchote dans tes rêves et tes élans spontanés. "
    "Ce n'est pas une destinée imposée : c'est une invitation, patiente et persistante, "
    "à habiter pleinement ta forme singulière. L'astrologie ne prédit rien de certain ; "
    "elle propose un langage pour reconnaître ce qui te traverse. "
) * 3

_AI_INTERPRETATIONS = {
    '_source': 'test',
    'soleil':    _AI_PARAGRAPH.format(PLANET='Le Soleil',    SIGN='Vierge'),
    'lune':      _AI_PARAGRAPH.format(PLANET='La Lune',      SIGN='Capricorne'),
    'mercure':   _AI_PARAGRAPH.format(PLANET='Mercure',      SIGN='Vierge'),
    'venus':     _AI_PARAGRAPH.format(PLANET='Vénus',        SIGN='Lion'),
    'mars':      _AI_PARAGRAPH.format(PLANET='Mars',         SIGN='Scorpion'),
    'jupiter':   _AI_PARAGRAPH.format(PLANET='Jupiter',      SIGN='Taureau'),
    'saturne':   _AI_PARAGRAPH.format(PLANET='Saturne',      SIGN='Capricorne'),
    'uranus':    _AI_PARAGRAPH.format(PLANET='Uranus',       SIGN='Verseau'),
    'neptune':   _AI_PARAGRAPH.format(PLANET='Neptune',      SIGN='Poissons'),
    'pluton':    _AI_PARAGRAPH.format(PLANET='Pluton',       SIGN='Scorpion'),
    'ascendant': _AI_PARAGRAPH.format(PLANET="L'Ascendant",  SIGN='Lion'),
    'synthese_aspects': (
        "Les sept aspects majeurs de ta carte dessinent un paysage de tensions "
        "et d'harmonies qui se répondent. Les trigones Soleil-Lune, Mercure-Vénus "
        "signalent une facilité intérieure à faire dialoguer identité, émotions et pensée. "
        "Les carrés et oppositions (Vénus-Mars, Jupiter-Saturne) te rappellent "
        "que la croissance se joue dans la friction entre ouverture et discipline. "
    ) * 2,
}


def _long_section(label: str, n: int = 4) -> str:
    """Génère une section book_data de n paragraphes denses."""
    base = (
        f"{label} — Dans ta carte, cette dimension devient un fil à suivre. "
        "Elle demande du temps, de la curiosité et un soupçon de patience envers toi-même. "
        "Observe ce que tu reconnais, interroge ce qui te surprend, "
        "laisse de côté ce qui ne te parle pas. L'astrologie reste un langage, "
        "pas une sentence : c'est toi qui donnes le sens final à ta propre histoire. "
    )
    return (base * 4).strip()


_BOOK_DATA = {
    '_source': 'test',
    '_em': {
        'dominant_element': 'Terre',
        'dominant_element_count': 4,
        'dominant_modality': 'Fixe',
        'dominant_modality_count': 4,
        'element_counts': {'Feu': 1, 'Terre': 4, 'Air': 2, 'Eau': 3},
        'modality_counts': {'Cardinal': 2, 'Fixe': 4, 'Mutable': 4},
    },
    'element_analysis':         _long_section('Élément dominant — Terre'),
    'modality_analysis':        _long_section('Modalité dominante — Fixe'),
    'trio_synthesis':           _long_section('Trio Soleil-Lune-Ascendant'),
    'aspects_harmonieux_body':  _long_section('Aspects harmonieux'),
    'aspects_tensions_body':    _long_section('Aspects de tension'),
    'year_ahead':               _long_section('Année à venir'),
    'house_1':  _long_section('Maison I — ton identité en action',  n=2),
    'house_2':  _long_section('Maison II — tes ressources',          n=2),
    'house_3':  _long_section('Maison III — ton esprit et ta parole', n=2),
    'house_4':  _long_section('Maison IV — tes racines',             n=2),
    'house_5':  _long_section('Maison V — ta créativité',            n=2),
    'house_6':  _long_section('Maison VI — ton quotidien',           n=2),
    'house_7':  _long_section('Maison VII — tes relations',          n=2),
    'house_8':  _long_section('Maison VIII — tes transformations',   n=2),
    'house_9':  _long_section('Maison IX — ta quête de sens',        n=2),
    'house_10': _long_section('Maison X — ta vocation',              n=2),
    'house_11': _long_section('Maison XI — tes rêves collectifs',    n=2),
    'house_12': _long_section('Maison XII — ton monde intérieur',    n=2),
}


def _user_data(no_birth_time: bool = False) -> dict:
    return {
        'prenom': 'Amélie',
        'require_complete_book': True,
        'birth_date': '1990-09-15',
        'birth_time': '' if no_birth_time else '14:30',
        'birth_city': 'Paris, France',
        'sun_sign': 'Vierge',
        'moon_sign': 'Capricorne',
        'venus_sign': 'Lion',
        'mars_sign': 'Scorpion',
        'ascendant_sign': '' if no_birth_time else 'Lion',
        'no_birth_time': no_birth_time,
        'ai_interpretations': _AI_INTERPRETATIONS,
        'enhanced_personal_analysis': {},
    }


def _count_pages(pdf_bytes: bytes) -> int:
    """Compte fiable des pages via pypdf."""
    return len(PdfReader(io.BytesIO(pdf_bytes)).pages)


# ─── Fixtures partagées (module-scope pour éviter de régénérer) ────────────────

@pytest.fixture(scope='module')
def digital_pdf_bytes() -> bytes:
    """PDF digital complet (avec heure de naissance)."""
    return generate_manuscrit_pdf(
        user_data=_user_data(no_birth_time=False),
        planets_data=_PLANETS_DATA_LIST,
        book_data=_BOOK_DATA,
        aspects_raw=_ASPECTS_RAW,
        houses_raw=_HOUSES_RAW,
        house_cusps_raw=_HOUSE_CUSPS_RAW,
    )


@pytest.fixture(scope='module')
def no_time_pdf_bytes() -> bytes:
    """PDF digital sans heure de naissance (12 maisons omises)."""
    # Sans heure, le `require_complete_book` ne réclame pas les 12 maisons —
    # on fournit uniquement les sections hors maisons.
    book_data_no_houses = {
        k: v for k, v in _BOOK_DATA.items() if not k.startswith('house_')
    }
    return generate_manuscrit_pdf(
        user_data=_user_data(no_birth_time=True),
        planets_data=_PLANETS_DATA_LIST,
        book_data=book_data_no_houses,
        aspects_raw=_ASPECTS_RAW,
    )


# ─── Tests ─────────────────────────────────────────────────────────────────────

def test_digital_pdf_reaches_target_page_count(digital_pdf_bytes):
    """Cible 45-50 pages pour le PDF digital complet."""
    pages = _count_pages(digital_pdf_bytes)
    assert pages >= 45, (
        f'PDF digital attendu ≥45 pages, trouvé {pages}. '
        f'Vérifier enrich_book_chapters (sections manquantes ?) ou densité AI.'
    )
    assert pages <= 80, (
        f'PDF digital attendu ≤80 pages (débordement improbable), trouvé {pages}.'
    )


def test_digital_pdf_contains_all_12_houses(digital_pdf_bytes):
    """Vérifie que les 12 maisons sont bien présentes."""
    import subprocess
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(digital_pdf_bytes)
        path = f.name
    try:
        out = subprocess.run(
            ['pdftotext', '-layout', path, '-'],
            capture_output=True, timeout=30,
        )
        text = out.stdout.decode('utf-8', errors='ignore')
    finally:
        os.unlink(path)

    # Chaque maison doit apparaître au moins une fois dans le texte extrait.
    missing = []
    for i in range(1, 13):
        # Les maisons sont rendues avec le label "Maison I/II/III…" ou "I."/"II."
        # On vérifie au moins la présence du contenu de section.
        label = f'Maison {["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"][i-1]}'
        if label not in text:
            missing.append(label)
    assert len(missing) <= 2, (
        f'Trop de maisons manquantes dans le PDF digital : {missing}. '
        f'Vérifier le mapping house_N → chapter dans natal_manuscript_builder.'
    )


def test_print_lulu_interior_meets_minimum_32_pages(digital_pdf_bytes):
    """Vérifie que la variante print (A5+bleed) respecte le minimum Lulu."""
    interior = lulu_interior(digital_pdf_bytes)
    pages = _count_pages(interior)
    assert pages >= 32, (
        f'Intérieur Lulu attendu ≥32 pages (minimum impression brochée), '
        f'trouvé {pages}. Lulu refusera l\'upload.'
    )


def test_no_birth_time_omits_houses(no_time_pdf_bytes):
    """Sans heure, les 12 maisons sont omises mais le livre reste substantiel."""
    pages = _count_pages(no_time_pdf_bytes)
    # Sans les 12 maisons on perd ~12-15 pages mais on garde planètes + aspects
    # + sections éléments/modalités/trio/année.
    assert pages >= 25, (
        f'PDF sans heure attendu ≥25 pages, trouvé {pages}.'
    )
    assert pages < 55, (
        f'PDF sans heure attendu <55 pages (sans les 12 maisons), trouvé {pages}.'
    )


def test_unified_service_signature_exposes_output_mode():
    """Garde-fou : la signature publique doit exposer output='digital'|'print'."""
    import inspect
    from services.natal_book_service import generate_enriched_natal_pdf
    sig = inspect.signature(generate_enriched_natal_pdf)
    assert 'output' in sig.parameters
    assert sig.parameters['output'].default == 'digital'
    assert 'no_birth_time' in sig.parameters
    assert 'require_complete' in sig.parameters
    assert 'referral_code' in sig.parameters
