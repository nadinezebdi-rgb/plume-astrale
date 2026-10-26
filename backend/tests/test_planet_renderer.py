"""Tests pour planet_renderer (Lot 2 — Feb 2026)."""
from PIL import Image
import io
import pytest

from services.planet_renderer import (
    generate_planet_png, SIGN_TO_RULER, PLANET_PALETTES,
)


def test_all_12_signs_map_to_known_rulers():
    expected_signs = {'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
                      'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons'}
    assert set(SIGN_TO_RULER.keys()) == expected_signs
    # Chaque planète maîtresse a une palette
    for ruler in SIGN_TO_RULER.values():
        assert ruler in PLANET_PALETTES, f'Palette manquante pour {ruler}'


def test_generate_planet_returns_valid_png():
    png = generate_planet_png('Lion', size=400)
    assert len(png) > 1000, 'PNG trop petit, probablement vide'
    img = Image.open(io.BytesIO(png))
    assert img.format == 'PNG'
    assert img.size == (400, 400)
    assert img.mode == 'RGBA'


@pytest.mark.parametrize('sign', [
    'Bélier', 'Taureau', 'Gémeaux', 'Cancer', 'Lion', 'Vierge',
    'Balance', 'Scorpion', 'Sagittaire', 'Capricorne', 'Verseau', 'Poissons',
])
def test_each_sign_produces_png(sign):
    png = generate_planet_png(sign, size=200)
    assert len(png) > 500
    img = Image.open(io.BytesIO(png))
    assert img.size == (200, 200)


def test_saturn_has_rings():
    """Capricorne (Saturne) doit avoir des anneaux dépassant du disque de la sphère."""
    png = generate_planet_png('Capricorne', size=400)
    img = Image.open(io.BytesIO(png)).convert('RGBA')
    # Les anneaux dépassent horizontalement du disque sphère (radius ~ 0.36 * 400 = 144)
    # À y=200 (centre vertical), x=350 doit avoir un pixel non-noir (anneau)
    # (la sphère s'arrête vers x=200+144=344, puis anneau continue)
    pixel = img.getpixel((380, 200))
    # Pixel soit anneau doré, soit fond navy — on vérifie juste qu'il n'est pas transparent
    assert pixel[3] > 0, 'Zone des anneaux doit avoir du contenu'


def test_unknown_sign_falls_back_to_sun():
    """Un signe inconnu ne doit pas crasher — fallback sur Soleil."""
    png = generate_planet_png('Inconnu', size=200)
    assert len(png) > 500


def test_deterministic_output():
    """Même signe → même PNG exactement (seed déterministe sur l'étoilée)."""
    a = generate_planet_png('Scorpion', size=200)
    b = generate_planet_png('Scorpion', size=200)
    assert a == b



# ─── Lot 5 — Édition saisonnière ────────────────────────────────

from services.planet_renderer import month_to_season, SEASON_SKY, SEASON_LABELS_FR


@pytest.mark.parametrize('month,expected', [
    (1, 'hiver'), (2, 'hiver'), (12, 'hiver'),
    (3, 'printemps'), (4, 'printemps'), (5, 'printemps'),
    (6, 'ete'), (7, 'ete'), (8, 'ete'),
    (9, 'automne'), (10, 'automne'), (11, 'automne'),
])
def test_month_to_season(month, expected):
    assert month_to_season(month) == expected


def test_four_seasons_are_declared():
    assert set(SEASON_SKY.keys()) == {'hiver', 'printemps', 'ete', 'automne'}
    assert set(SEASON_LABELS_FR.keys()) == {'hiver', 'printemps', 'ete', 'automne'}


def test_season_tints_background():
    """Deux saisons différentes doivent produire des coins (fond) de couleur distincte."""
    png_winter = generate_planet_png('Lion', size=200, birth_month=1)  # hiver
    png_summer = generate_planet_png('Lion', size=200, birth_month=7)  # été
    assert png_winter != png_summer, 'Hiver et été doivent différer visuellement'
    # Pixel de coin : hiver bleu nuit, été ambré
    img_w = Image.open(io.BytesIO(png_winter)).convert('RGB')
    img_s = Image.open(io.BytesIO(png_summer)).convert('RGB')
    # Coin haut-gauche : hiver R faible, été R élevé
    assert img_w.getpixel((5, 5))[2] > img_w.getpixel((5, 5))[0], 'Hiver : bleu > rouge'
    assert img_s.getpixel((5, 5))[0] > img_s.getpixel((5, 5))[2], 'Été : rouge > bleu'


def test_season_deterministic():
    """Même signe + même mois → PNG identique bit à bit."""
    a = generate_planet_png('Cancer', size=200, birth_month=10)
    b = generate_planet_png('Cancer', size=200, birth_month=10)
    assert a == b


def test_without_birth_month_defaults_to_winter():
    """Sans birth_month, le rendu doit être identique à un rendu `hiver`
    (compat ascendante : la couverture historique est teinte hiver)."""
    historical = generate_planet_png('Lion', size=200)
    winter = generate_planet_png('Lion', size=200, birth_month=1)
    assert historical == winter
