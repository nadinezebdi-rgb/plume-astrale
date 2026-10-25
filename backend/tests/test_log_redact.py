"""Tests pour log_redact — assure la non-exposition de PII dans les logs."""
from __future__ import annotations
import pytest
from services.log_redact import redact_email, redact_name, redact_phone, redact_birth_date


# ─── redact_email ─────────────────────────────────────────────────────

def test_redact_email_classic():
    assert redact_email('alice.wonder@gmail.com') == 'a***@gmail.com'


def test_redact_email_single_char():
    assert redact_email('a@plume-astrale.fr') == 'a***@plume-astrale.fr'


def test_redact_email_uppercase_normalized():
    assert redact_email('ALICE@HOTMAIL.COM') == 'a***@hotmail.com'


def test_redact_email_whitespace_stripped():
    assert redact_email('  bob@test.com  ') == 'b***@test.com'


@pytest.mark.parametrize('bad', [None, 123, [], 'not-an-email', '@noloc.com', 'nodomain@'])
def test_redact_email_invalid_inputs(bad):
    out = redact_email(bad)  # type: ignore[arg-type]
    assert out in ('<empty>', '<invalid>')


def test_redact_email_empty_string():
    assert redact_email('') == '<empty>'


# ─── redact_name ──────────────────────────────────────────────────────

def test_redact_name_single():
    assert redact_name('Alice') == 'A***'


def test_redact_name_multiple():
    assert redact_name('Alice Wonder') == 'A*** W***'


def test_redact_name_uppercase_initial():
    assert redact_name('alice wonder') == 'A*** W***'


@pytest.mark.parametrize('bad', [None, '', '   '])
def test_redact_name_empty(bad):
    assert redact_name(bad) == '<empty>'  # type: ignore[arg-type]


# ─── redact_phone ─────────────────────────────────────────────────────

def test_redact_phone_fr():
    # +33612345678 = 12 chars → +33 + 7 stars + 78 = 12 chars (longueur préservée)
    assert redact_phone('+33612345678') == '+33*******78'


def test_redact_phone_national():
    # 0612345678 = 10 chars → 3 + 5 stars + 2 = 10
    assert redact_phone('0612345678') == '061*****78'


def test_redact_phone_with_spaces():
    # Les séparateurs sont strippés avant comptage
    assert redact_phone('06 12 34 56 78') == '061*****78'


@pytest.mark.parametrize('bad', [None, '', '123', 12345])
def test_redact_phone_invalid(bad):
    out = redact_phone(bad)  # type: ignore[arg-type]
    assert out in ('<empty>', '<redacted>')


# ─── redact_birth_date ────────────────────────────────────────────────

def test_redact_birth_date_iso():
    assert redact_birth_date('1990-06-15') == '1990-**-**'


def test_redact_birth_date_with_time():
    assert redact_birth_date('1990-06-15T14:30:00') == '1990-**-**'


@pytest.mark.parametrize('bad', [None, '', 'invalid', '15/06/1990'])
def test_redact_birth_date_invalid(bad):
    out = redact_birth_date(bad)  # type: ignore[arg-type]
    assert out in ('<empty>', '<redacted>')


# ─── Zero-leak guard ──────────────────────────────────────────────────

def test_no_leak_in_any_output():
    """Garantit qu'une entrée vide/invalide ne retourne JAMAIS la PII brute."""
    for fn, bad_values in [
        (redact_email, ['secret@evil.com', 'leak@gmail.com']),
        (redact_name, ['Alice', 'Bob']),
        (redact_phone, ['+33123456789']),
        (redact_birth_date, ['2000-01-01']),
    ]:
        for v in bad_values:
            out = fn(v)
            # L'output DOIT soit retourner la version masquée, soit un placeholder,
            # mais jamais contenir la valeur originale entière
            assert v not in out or out == v and '*' in out, f'{fn.__name__}({v!r}) → {out!r} leaks PII'
