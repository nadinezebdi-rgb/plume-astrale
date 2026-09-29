import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import astrology_io_service as aio
from services.natal_pdf_v2 import _enhanced_personal_analysis_sections


def test_enhanced_analysis_uses_requested_astrology_options(monkeypatch):
    captured = {}

    async def fake_call(path, payload):
        captured['path'] = path
        captured['payload'] = payload
        return {'lunar_phase': {'phase_name': 'Full Moon'}}

    monkeypatch.setattr(aio, '_call', fake_call)
    result = asyncio.run(aio.enhanced_personal_analysis({
        'year': 1985, 'month': 5, 'day': 11, 'hour': 18, 'minute': 15,
        'city': 'Paris', 'country_code': 'France',
    }, name='Ada'))

    assert result['lunar_phase']['phase_name'] == 'Full Moon'
    assert captured['path'] == '/enhanced/personal-analysis'
    assert captured['payload']['subject']['name'] == 'Ada'
    assert captured['payload']['subject']['birth_data']['country_code'] == 'FR'
    assert captured['payload']['options']['house_system'] == 'W'
    assert captured['payload']['options']['zodiac_type'] == 'Tropic'
    assert 'Part_of_Fortune' in captured['payload']['options']['active_points']
    assert captured['payload']['orbs'] == {'major_aspects_deg': 2, 'minor_aspects_deg': 1}


def test_enhanced_pdf_sections_include_features_and_respect_missing_birth_time():
    analysis = {
        'lunar_phase': {
            'phase_name': 'Waxing Gibbous',
            'illumination_percent': 85.2,
            'moon_age_days': 10.7,
        },
        'chronocrator': {
            'method': 'Annual Profection',
            'sign': 'Can',
            'ruler': 'Moon',
            'house_themes': ['home', 'family'],
        },
        'life_areas': ['career_success'],
        'planets': [
            {'name': 'Mean_Node', 'sign': 'Can', 'position': 4.125, 'house': 'Tenth_House'},
            {'name': 'Part_of_Fortune', 'sign': 'Tau', 'position': 12.5, 'house': 'Second_House'},
            {'name': 'Sun', 'dignities': {'domicile': True}},
        ],
        'aspects': [{
            'planet_a': 'Sun', 'planet_b': 'Moon', 'aspect_type': 'trine',
            'orb': 1.25, 'applying': True,
        }],
        'fixed_stars': [{'star': 'Aldebaran', 'planet': 'Moon', 'orb': 0.8}],
    }

    sections = _enhanced_personal_analysis_sections(analysis)
    assert [title for title, _ in sections] == ['Les rythmes de ton ciel', 'Les signatures précises']
    all_text = '\n'.join(body for _, body in sections)
    assert 'Gibbeuse croissante' in all_text
    assert 'Nœud moyen' in all_text
    assert 'Soleil trigone Lune' in all_text
    assert 'en formation' in all_text
    assert 'Aldebaran' in all_text
    assert 'Maison X' in all_text

    no_time_sections = _enhanced_personal_analysis_sections(analysis, no_birth_time=True)
    no_time_text = '\n'.join(body for _, body in no_time_sections)
    assert 'Profection annuelle' not in no_time_text
    assert 'Maison' not in no_time_text
    assert 'Soleil trigone Lune' not in no_time_text
    assert 'Aldebaran' not in no_time_text
    assert 'estimée pour la date' in no_time_text


def test_enhanced_pdf_sections_are_optional():
    assert _enhanced_personal_analysis_sections(None) == []
    assert _enhanced_personal_analysis_sections({}) == []
