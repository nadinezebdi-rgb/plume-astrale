"""Aspects / maisons du thème natal + garde-fous typographiques des PDF."""
import os

os.environ.setdefault('SUPABASE_URL', 'http://localhost')

from services.natal_chart_extract import compute_aspects, extract_aspects, extract_houses
from services.pdf_theme import format_date_fr, ornament_safe

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def _point(name, lon):
    return {'name': name, 'sign': SIGNS[int(lon // 30)], 'degree': lon % 30,
            'absolute_longitude': lon, 'house': None}


PLANETS = {
    'sun': _point('Sun', 116.5), 'moon': _point('Moon', 12.0),
    'mercury': _point('Mercury', 110.0), 'mars': _point('Mars', 296.5),
    'ascendant': _point('Ascendant', 70.0),
}


def test_compute_aspects_finds_conjunction_and_opposition():
    aspects = compute_aspects(PLANETS)
    pairs = {(a['planet1'], a['planet2'], a['type']) for a in aspects}
    assert ('Soleil', 'Mercure', 'conjonction') in pairs
    assert ('Soleil', 'Mars', 'opposition') in pairs
    assert all('Ascendant' not in (a['planet1'], a['planet2']) for a in aspects)


def test_extract_aspects_prefers_api_then_falls_back_to_local():
    chart = {'chart_data': {'aspects': [
        {'point1': 'Sun', 'point2': 'Moon', 'aspect_type': 'Trine', 'orb': 1.2},
    ]}}
    api = extract_aspects(chart, None, PLANETS)
    assert api == [{'planet1': 'Soleil', 'planet2': 'Lune', 'type': 'trigone',
                    'orb': 1.2, 'nature': 'harmonieux'}]
    assert extract_aspects(None, None, PLANETS)


def test_extract_houses_places_planets_by_longitude():
    chart = {'chart_data': {'house_cusps': [
        {'house': i + 1, 'sign': SIGNS[((70 // 30) + i) % 12], 'absolute_longitude': (70 + 30 * i) % 360}
        for i in range(12)
    ]}}
    houses = extract_houses(chart, PLANETS)
    assert [h['num'] for h in houses] == list(range(1, 13))
    assert houses[0]['sign'] == 'Gémeaux'
    assert 'Soleil' in houses[1]['planets_in_house']


def test_extract_houses_empty_without_cusps():
    assert extract_houses({'chart_data': {}}, PLANETS) == []
    assert extract_houses(None, PLANETS) == []


def test_format_date_fr_is_french():
    from datetime import datetime
    assert format_date_fr(datetime(2026, 7, 31)) == '31 juillet 2026'


def test_ornament_safe_never_leaves_bare_glyph():
    out = ornament_safe('✦ TEST ✦')
    assert out != '✦ TEST ✦'
