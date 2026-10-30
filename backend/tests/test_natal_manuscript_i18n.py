# Natal manuscript i18n (EN/FR) — iteration 94
import dataclasses
import json
import re

from services.natal_manuscript_builder import build_natal_manuscript
from services.natal_preface_generator import _static_fallback
from tests.test_natal_manuscript_enriched import _PLANETS_DETAIL, _ASPECTS, _HOUSE_CUSPS


def _natal(lang):
    narr = [{'name': p['name'], 'sign': p['sign'],
             'analysis': ('Analysis text for this planet.' if lang == 'en' else 'Analyse.')}
            for p in _PLANETS_DETAIL]
    return {
        'sun_sign': 'Vierge', 'moon_sign': 'Capricorne', 'ascendant_sign': 'Lion',
        'no_birth_time': False, 'planets': narr, 'planets_detail': _PLANETS_DETAIL,
        'aspects': _ASPECTS, 'house_cusps': _HOUSE_CUSPS, 'tier': 'ultra',
        'synthese_aspects': ('Two dynamics.' if lang == 'en' else 'Deux dynamiques.'),
    }


def _dump(m):
    out = []
    for ch in m.chapters:
        out.append(ch.title or '')
        out.append(ch.kicker or '')
        for b in ch.blocks:
            d = dataclasses.asdict(b) if dataclasses.is_dataclass(b) else vars(b)
            out.append(json.dumps(d, default=str, ensure_ascii=False))
    return '\n'.join(out)


FR_LEAKS = ['Première maison', 'Soleil', 'Lune', 'Né·e', 'Comment lire', 'maison ',
            'planète', 'Conjonction', 'rétrograde', 'Vos planètes', 'Vos douze maisons', 'Le Ciel de']


def test_en_titles():
    m = build_natal_manuscript(prenom='Camille', birth_date='1992-04-23', natal_data=_natal('en'),
                               language='en')
    titles = [c.title for c in m.chapters]
    print(titles)
    for t in ['How to read this book', "Camille's Sky", 'Your planets', 'Your twelve houses',
              'What your sky tells you']:
        assert any(t.lower() in (x or '').lower() for x in titles), f'missing {t} in {titles}'


def test_en_no_french_leaks():
    m = build_natal_manuscript(prenom='Camille', birth_date='1992-04-23', natal_data=_natal('en'),
                               language='en')
    txt = _dump(m)
    leaks = [w for w in FR_LEAKS if w in txt]
    ctx = {w: txt[max(0, txt.find(w) - 80): txt.find(w) + 80] for w in leaks}
    assert not leaks, f'French leaks: {ctx}'


def test_fr_titles_regression():
    m = build_natal_manuscript(prenom='Camille', birth_date='1992-04-23', natal_data=_natal('fr'),
                               language='fr')
    titles = [c.title for c in m.chapters]
    print(titles)
    for t in ['Comment lire ce livre', 'Le Ciel de Camille', 'Tes planètes', 'Tes douze maisons']:
        assert any(t.lower() in (x or '').lower() for x in titles), f'missing {t} in {titles}'


def test_static_fallback_en():
    blocks = _static_fallback('Camille', language='en')
    assert blocks and len(blocks) >= 3
    txt = json.dumps(blocks, ensure_ascii=False, default=str)
    for w in [' vous ', ' votre ', 'Soleil', ' Lune ', ' est ']:
        assert w not in txt, f'French in EN fallback: {w}'
