import asyncio

from services.book_engine.domain import Edition
from services.book_engine.registry import ADDONS, PRINT_INCLUDED_ADDONS
from services.book_engine_v2 import assemble, chapter_prompts as cp

ASTRO = {
    'planets': {'sun': {'sign': 'Leo', 'house': 5, 'degree': 12.3},
                'moon': {'sign': 'Pisces', 'house': 12, 'degree': 3.0}},
    'houses': [{'house': i + 1, 'absolute_longitude': i * 30 + 10} for i in range(12)],
    'fixed_stars': [{'name': 'Regulus', 'planet': 'Soleil', 'orb': 0.4}],
}


def test_houses_block_lists_planets_and_cusps():
    block = cp._houses_block(ASTRO)
    lines = block.split('\n')
    assert len(lines) == 12
    assert 'Soleil' in lines[4]
    assert 'Lune' in lines[11]
    assert 'inconnue' not in block


def test_houses_block_without_birth_time_is_honest():
    assert 'cuspide inconnue' in cp._houses_block({'planets': {}, 'houses': []})


def test_fixed_stars_block():
    assert 'Regulus' in cp._fixed_stars_block(ASTRO)
    assert 'aucun calcul' in cp._fixed_stars_block({})


def test_prompts_format():
    sig = cp.sig_generic(ASTRO, 'Ana')
    sig['houses_block'] = cp._houses_block(ASTRO)
    sig['fixed_stars_block'] = cp._fixed_stars_block(ASTRO)
    for slug in PRINT_INCLUDED_ADDONS:
        assert cp.CHAPTER_PROMPTS[slug].format(**sig)


def test_print_editions_include_chapters(monkeypatch):
    built = []

    async def fake(spec, *a, **k):
        built.append(spec.slug)
        from services.book_engine.domain import Chapter
        return Chapter(slug=spec.slug, title='t', kicker='k', roman_num=None, order=spec.order)

    monkeypatch.setattr(assemble, '_build_one_chapter', fake)
    from services.book_engine.domain import BirthData
    bd = BirthData(date_iso='1990-01-01', time_hhmm=None, city='', country_code='FR')

    def run(ed):
        built.clear()
        asyncio.run(assemble.build_full_manuscript(
            session_id='s', user_email='', first_name='A', birth_data=bd,
            astro_data=ASTRO, edition=ed))
        return set(built)

    assert not set(PRINT_INCLUDED_ADDONS) & run(Edition.NUMERIQUE)
    assert set(PRINT_INCLUDED_ADDONS) <= run(Edition.BROCHEE)
    assert {a.slug for a in ADDONS} >= set(PRINT_INCLUDED_ADDONS)
