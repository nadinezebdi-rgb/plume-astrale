"""Tests pour natal_ex_libris (Lot 3 — Feb 2026)."""
import pymupdf
import pytest

from services.natal_ex_libris import ex_libris_page, generate_copy_number


def test_generate_copy_number_is_deterministic():
    """Même prénom + même date → même numéro de copie."""
    a = generate_copy_number('Clara', '1992-07-14')
    b = generate_copy_number('Clara', '1992-07-14')
    assert a == b
    assert a.startswith('P-ASTRAL-')
    assert len(a) == len('P-ASTRAL-00000')


def test_generate_copy_number_varies_with_prenom():
    a = generate_copy_number('Clara', '1992-07-14')
    b = generate_copy_number('Clara', '1992-07-15')
    c = generate_copy_number('Jean', '1992-07-14')
    # Au moins 2 différents sur 3 essais (hash collision possible mais rare)
    assert len({a, b, c}) >= 2


def test_ex_libris_renders_in_natal_pdf():
    """Génère un PDF complet et vérifie que la page ex-libris est présente et bien formée."""
    from services.natal_pdf_v2 import build_natal_pdf_v2

    natal_data = {
        'sun_sign': 'Cancer', 'moon_sign': 'Poissons', 'ascendant_sign': 'Vierge',
        'no_birth_time': False, 'tier': 'ultra',
        'planets': [
            {'name': 'Soleil', 'sign': 'Cancer', 'analysis': 'Analyse soleil.'},
            {'name': 'Lune', 'sign': 'Poissons', 'analysis': 'Analyse lune.'},
            {'name': 'Mercure', 'sign': 'Cancer', 'analysis': 'Analyse mercure.'},
            {'name': 'Vénus', 'sign': 'Lion', 'analysis': 'Analyse vénus.'},
            {'name': 'Mars', 'sign': 'Taureau', 'analysis': 'Analyse mars.'},
        ],
        'synthese_aspects': 'Synthèse des aspects.',
        'houses': [{'num': i, 'sign': 'Vierge', 'planets_in_house': []} for i in range(1, 13)],
        'enhanced_personal_analysis': {},
    }
    book_data = {
        '_source': 'cache',
        '_em': {
            'dominant_element': 'Eau', 'dominant_element_count': 4,
            'dominant_modality': 'Fixe', 'dominant_modality_count': 3,
        },
        'dedication': 'Pour Clara, un livre pour toi.',
        'element_analysis': 'Eau analyse.',
        'modality_analysis': 'Fixe analyse.',
        'trio_synthesis': 'Trio.',
        'aspects_harmonieux_body': 'Harm.',
        'aspects_tensions_body': 'Tens.',
        'rare_aspect_body': 'Rare.',
        'houses_intro': 'Intro maisons.',
        'year_ahead': 'Année.',
        **{f'house_{i}': f'Maison {i}' for i in range(1, 13)},
    }

    pdf_bytes = build_natal_pdf_v2(
        prenom='Clara',
        birth_date='1992-07-14',
        natal_data=natal_data,
        book_data=book_data,
    )

    doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
    try:
        # Page Ex-Libris doit exister et contenir les marqueurs clés
        ex_libris_found = False
        for page in doc:
            txt = page.get_text()
            if 'E X   L I B R I S' in txt or 'EX LIBRIS' in txt.replace(' ', '').upper() or 'LIBRIS' in txt:
                ex_libris_found = True
                assert 'Clara' in txt, "Prénom absent de la page ex-libris"
                assert 'P-ASTRAL-' in txt, "Numéro de copie absent"
                assert 'PLUME' in txt.upper(), "Mention PLUME ASTRALE absente"
                break
        assert ex_libris_found, "Page EX LIBRIS introuvable dans le PDF natal"

        # Aucune mention 'Soléna' nulle part (demande user 2026-02-27)
        for i, page in enumerate(doc):
            low = page.get_text().lower()
            assert 'soléna' not in low and 'solena' not in low, \
                f'Soléna détecté p{i+1} — doit être absent du Thème Natal'
    finally:
        doc.close()


def test_ex_libris_handles_no_birth_time():
    """Sans heure de naissance → ascendant omis du médaillon mais page quand même valide."""
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import A4
    from io import BytesIO

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2.2*72/2.54,
                            rightMargin=2.2*72/2.54, topMargin=2*72/2.54,
                            bottomMargin=2*72/2.54)
    story = []
    ex_libris_page(story, prenom='Alex', birth_date='1990-01-01',
                   sun_sign='Capricorne', moon_sign='Vierge',
                   asc_sign=None, no_birth_time=True)
    doc.build(story)
    assert buf.tell() > 1000  # PDF non vide
