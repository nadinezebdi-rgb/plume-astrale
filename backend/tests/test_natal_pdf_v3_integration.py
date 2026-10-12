"""
Integration test — Thème Natal PDF v3 (Plume Astrale)
Vérifie le rendu PDF A5 complet via book_engine_v2 selon le review request:
- ≥ 30 pages
- 3 parties en français
- Degrés + maisons dans les H2 planètes avec rétrograde ℞
- 12 maisons avec grammaire française correcte ("tombe en Lion", pas "du Lion")
- Aspects groupés par type avec noms français
- no_birth_time omet Partie II mais garde Partie III
- Aucune phrase apologétique
- Adapter accepte les nouveaux kwargs
"""
import subprocess
import tempfile
import os
import re
import pytest

from services.natal_manuscript_builder import build_natal_manuscript
from services.book_engine_v2 import render_manuscript_to_pdf_v2
from services import natal_pdf_adapter


# -- Fixtures de données réalistes ---------------------------------------------
_PLANETS_DETAIL = [
    {'name': 'Soleil',  'sign': 'Vierge',     'house': 2,  'degree': 22.5},
    {'name': 'Lune',    'sign': 'Capricorne', 'house': 6,  'degree': 23.1},
    {'name': 'Mercure', 'sign': 'Vierge',     'house': 2,  'degree': 8.2},
    {'name': 'Vénus',   'sign': 'Lion',       'house': 1,  'degree': 11.4},
    {'name': 'Mars',    'sign': 'Scorpion',   'house': 4,  'degree': 2.7},
    {'name': 'Jupiter', 'sign': 'Taureau',    'house': 10, 'degree': 18.0, 'retrograde': True},
    {'name': 'Saturne', 'sign': 'Capricorne', 'house': 6,  'degree': 25.3},
    {'name': 'Uranus',  'sign': 'Verseau',    'house': 7,  'degree': 5.5},
    {'name': 'Neptune', 'sign': 'Poissons',   'house': 8,  'degree': 12.1},
    {'name': 'Pluton',  'sign': 'Scorpion',   'house': 4,  'degree': 20.9},
]
_PLANETS_NARRATIVE = [
    {'name': p['name'], 'sign': p['sign'],
     'analysis': (f"Analyse détaillée pour {p['name']} en {p['sign']}. " * 25)}
    for p in _PLANETS_DETAIL
]
_ASPECTS = [
    {'aspecting_planet': 'Soleil',  'aspected_planet': 'Lune',    'type': 'trine',       'orb': 2.1},
    {'aspecting_planet': 'Soleil',  'aspected_planet': 'Mercure', 'type': 'conjunction', 'orb': 7.3},
    {'aspecting_planet': 'Vénus',   'aspected_planet': 'Mars',    'type': 'square',      'orb': 1.2},
    {'aspecting_planet': 'Jupiter', 'aspected_planet': 'Saturne', 'type': 'opposition',  'orb': 3.5},
    {'aspecting_planet': 'Mars',    'aspected_planet': 'Pluton',  'type': 'conjunction', 'orb': 4.0},
    {'aspecting_planet': 'Lune',    'aspected_planet': 'Saturne', 'type': 'conjunction', 'orb': 2.2},
    {'aspecting_planet': 'Mercure', 'aspected_planet': 'Vénus',   'type': 'sextile',     'orb': 3.1},
]
_HOUSE_CUSPS = [
    {'house': i, 'sign': s, 'degree': (i * 7) % 30}
    for i, s in enumerate(
        ['Lion', 'Vierge', 'Balance', 'Scorpion', 'Sagittaire', 'Capricorne',
         'Verseau', 'Poissons', 'Bélier', 'Taureau', 'Gémeaux', 'Cancer'], start=1)
]


def _natal_data(no_birth_time=False):
    return {
        'sun_sign': 'Vierge', 'moon_sign': 'Capricorne',
        'ascendant_sign': '' if no_birth_time else 'Lion',
        'no_birth_time': no_birth_time,
        'planets': _PLANETS_NARRATIVE,
        'planets_detail': _PLANETS_DETAIL,
        'aspects': _ASPECTS,
        'house_cusps': _HOUSE_CUSPS,
        'tier': 'ultra',
        'synthese_aspects': 'Synthèse des dynamiques aspectuelles dans ce thème.',
    }


def _render_pdf(no_birth_time=False) -> bytes:
    m = build_natal_manuscript(
        prenom='Amélie', birth_date='1990-09-15',
        natal_data=_natal_data(no_birth_time=no_birth_time),
    )
    return render_manuscript_to_pdf_v2(m, profile='screen')


def _pdf_to_text(pdf_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(pdf_bytes); path = f.name
    try:
        out = subprocess.run(
            ['pdftotext', '-layout', path, '-'],
            capture_output=True, timeout=30,
        )
        return out.stdout.decode('utf-8', errors='ignore')
    finally:
        os.unlink(path)


# -- Fixture partagée (cache rendu PDF) ----------------------------------------
@pytest.fixture(scope="module")
def pdf_bytes():
    return _render_pdf(no_birth_time=False)


@pytest.fixture(scope="module")
def pdf_text(pdf_bytes):
    return _pdf_to_text(pdf_bytes)


# -- Tests ---------------------------------------------------------------------

def test_pdf_has_at_least_30_pages(pdf_bytes):
    pages = pdf_bytes.count(b'/Type /Page') + pdf_bytes.count(b'/Type/Page')
    # Fallback count robuste pour wkhtmltopdf-like outputs
    if pages < 30:
        pages = pdf_bytes.count(b'/Page\n') + pdf_bytes.count(b'/Page ')
    assert pages >= 30, f"Attendu ≥30 pages, trouvé {pages}"


def test_pdf_contains_three_french_parts(pdf_text):
    assert 'Première partie' in pdf_text, "Partie I manquante"
    assert 'Vos planètes' in pdf_text
    assert 'Deuxième partie' in pdf_text, "Partie II manquante"
    assert 'Les douze maisons' in pdf_text
    assert 'Troisième partie' in pdf_text, "Partie III manquante"
    assert 'Vos aspects' in pdf_text


def test_pdf_planet_titles_have_degrees_minutes(pdf_text):
    # Format attendu: `Soleil en Vierge · 22°30' · maison 2`
    # On tolère l'espace fin unicode ou normal
    m = re.search(r"Soleil en Vierge[^\n]*?\d{1,2}°\d{2}['\u2032]", pdf_text)
    assert m, f"Degré minutes manquant pour Soleil. Extrait: {pdf_text[:2000]}"
    # Au moins une mention "maison" dans la ligne du Soleil
    sun_line_match = re.search(r"Soleil en Vierge[^\n]*", pdf_text)
    assert sun_line_match and 'maison' in sun_line_match.group(0).lower()


def test_pdf_retrograde_symbol_for_jupiter(pdf_text):
    # Jupiter est rétrograde dans le jeu de données
    jupiter_line = re.search(r"Jupiter en Taureau[^\n]*", pdf_text)
    assert jupiter_line, "Jupiter non trouvé"
    # Doit contenir ℞ ou le mot "rétrograde"
    line = jupiter_line.group(0)
    assert '℞' in line or 'rétrograde' in line.lower(), f"Marqueur rétrograde manquant: {line}"


def test_pdf_houses_use_tombe_en_grammar(pdf_text):
    # On attend "tombe en Lion", "tombe en Vierge" etc, PAS "du Lion"/"du Vierge"
    # (sauf cas valides comme "du Lion rugissant" - on filtre strictement sur signe suivi d'un délimiteur)
    bad = re.findall(r"\bdu (Lion|Vierge|Balance|Scorpion|Sagittaire|Capricorne|Verseau|Poissons|Bélier|Taureau|Gémeaux|Cancer)\b", pdf_text)
    assert not bad, f"Grammaire incorrecte 'du <signe>' trouvée: {bad[:5]}"
    assert 'tombe en' in pdf_text or 'tombe sur' in pdf_text or 'cuspide en' in pdf_text, \
        "Aucune formule 'tombe en ...' pour les maisons"


def test_pdf_aspects_grouped_with_french_planet_names(pdf_text):
    # Groupes attendus
    for group in ('Conjonctions', 'Oppositions', 'Trigones', 'Carrés', 'Sextiles'):
        assert group in pdf_text, f"Groupe '{group}' absent du PDF"
    # Pas de noms anglais
    for en in ('Sun', 'Moon', 'Venus', 'Mercury', 'Mars conjunction', 'Jupiter opposition'):
        assert en not in pdf_text, f"Nom anglais '{en}' trouvé dans le PDF"
    # Au moins un nom français de planète dans la zone aspects
    aspects_zone = pdf_text.split('Troisième partie', 1)[-1]
    assert any(p in aspects_zone for p in ('Soleil', 'Lune', 'Vénus', 'Mercure')), \
        "Aucune planète française dans la zone aspects"


def test_pdf_no_apologetic_phrases(pdf_text):
    lowered = pdf_text.lower()
    forbidden = ["faute d", "aspects exacts fournis", "non fourni",
                 "manquant", "aucune donnée"]
    hits = [p for p in forbidden if p in lowered]
    assert not hits, f"Phrases apologétiques trouvées: {hits}"


def test_pdf_no_birth_time_omits_houses_keeps_aspects():
    pdf = _render_pdf(no_birth_time=True)
    text = _pdf_to_text(pdf)
    assert 'Deuxième partie' not in text, "Partie II (maisons) devrait être omise sans heure"
    assert 'Troisième partie' in text, "Partie III (aspects) devrait rester présente"
    # Toujours pas d'excuse
    assert 'faute d' not in text.lower()


def test_natal_pdf_adapter_accepts_new_kwargs():
    """L'adapter doit exposer aspects_raw / houses_raw / house_cusps_raw dans sa
    signature et les propager dans natal_data['aspects' / 'house_cusps' / 'houses']."""
    import inspect
    sig = inspect.signature(natal_pdf_adapter.generate_manuscrit_pdf)
    for kw in ('aspects_raw', 'houses_raw', 'house_cusps_raw'):
        assert kw in sig.parameters, f"Kwarg '{kw}' manquant dans la signature"

    # Vérification source: les kwargs sont bien injectés dans natal_data
    src = inspect.getsource(natal_pdf_adapter.generate_manuscrit_pdf)
    assert "natal_data['aspects'] = aspects_raw" in src or "natal_data[\"aspects\"] = aspects_raw" in src
    assert "house_cusps_raw" in src and "natal_data" in src
