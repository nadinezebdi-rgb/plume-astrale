from datetime import date

from services.numerologie_cycles import build_cycles, karmic_debts, parse_birth, reduce_number

TODAY = date(2026, 10, 3)


def test_reduce_keeps_master_numbers():
    assert reduce_number(29) == 11
    assert reduce_number(29, keep_master=False) == 2
    assert reduce_number(38) == 11


def test_cycles_for_known_birth_date():
    c = build_cycles('1990-05-15', TODAY)
    assert c['life_path'] == 3
    assert c['personal_year'] == 3
    assert [p['number'] for p in c['pinnacles']] == [11, 7, 9, 6]
    assert [x['number'] for x in c['challenges']] == [1, 5, 4, 4]
    assert len(c['months']) == 12
    assert c['months'][0]['label'] == 'Octobre 2026'
    assert c['months'][-1]['label'] == 'Septembre 2027'


def test_lo_shu_missing_and_repeated_digits():
    lo = build_cycles('1990-05-15', TODAY)['lo_shu']
    assert lo['repeated'] == [1, 5, 9]
    assert [m['number'] for m in lo['missing']] == [2, 3, 4, 6, 7, 8]


def test_karmic_debt_detected_on_birthday():
    assert [d['number'] for d in karmic_debts(date(1989, 4, 13))] == [13]


def test_invalid_date_returns_none():
    assert parse_birth('nope') is None
    assert build_cycles('nope') is None
