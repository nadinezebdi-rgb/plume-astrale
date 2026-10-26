"""Tests pour natal_pdf_qa (Lot 4 — Feb 2026)."""
import io

import pymupdf
import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from services.natal_pdf_qa import (
    QAReport, assert_natal_pdf_quality, NatalPdfQAError, qa_check_natal_pdf,
)


def _make_minimal_pdf(pages_content: list[str]) -> bytes:
    """Fabrique un PDF simple avec le texte donné (une page par entrée).

    Si une ligne dépasse la largeur utile, on la découpe en morceaux de
    ~80 caractères pour que ReportLab écrive bien tout le texte visible
    (sinon la partie hors page n'est pas extraite par pymupdf).
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for content in pages_content:
        y = 800
        for raw_line in content.split('\n'):
            # Découpe les lignes trop longues en segments de 80 chars
            words = raw_line.split(' ')
            current = ''
            lines = []
            for w in words:
                if len(current) + 1 + len(w) > 80:
                    lines.append(current)
                    current = w
                else:
                    current = f'{current} {w}'.strip()
            if current:
                lines.append(current)
            for line in lines:
                if y < 50:
                    break
                c.drawString(50, y, line)
                y -= 15
        c.showPage()
    c.save()
    return buf.getvalue()


def test_qa_report_dataclass_defaults():
    r = QAReport()
    assert r.passed is True
    assert r.blocking_issues == []
    assert r.warnings == []
    d = r.to_dict()
    assert set(d.keys()) >= {'passed', 'mode', 'page_count', 'word_count'}


def test_qa_detects_missing_cover_title():
    pdf = _make_minimal_pdf(['Hello world ' * 500])
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('Thème Natal' in i for i in r.blocking_issues)


def test_qa_detects_missing_prenom():
    pdf = _make_minimal_pdf(['Thème Natal\n' + 'contenu ' * 500])
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('Clara' in i for i in r.blocking_issues)


def test_qa_detects_solena_contamination():
    # 20 pages pour passer le seuil min_pages ; 2500+ mots ; prénom + titre + Ex-Libris
    heavy = 'mot ' * 500
    pages = [f'Thème Natal\nClara\n{heavy}'] + [
        f'Page {i}\n{heavy}' for i in range(2, 20)
    ] + [f'EX LIBRIS\nClara\nP-ASTRAL-00042\nPlume Astrale\nPar Soléna\n{heavy}']
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('Soléna' in i for i in r.blocking_issues)


def test_qa_detects_missing_ex_libris_in_rich():
    heavy = 'mot ' * 300
    pages = [f'Thème Natal\nClara\n{heavy}'] + [f'Page {i}\n{heavy}' for i in range(2, 25)]
    pdf = _make_minimal_pdf(pages + ['Plume Astrale\n' + heavy])
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('Ex-Libris' in i for i in r.blocking_issues)


def test_qa_passes_on_well_formed_pdf():
    heavy = 'contenu riche ' * 200
    pages = [f'Thème Natal\nClara\n{heavy}']
    for i in range(2, 20):
        pages.append(f'Page {i}\n{heavy}')
    pages.append(f'EX LIBRIS\nClara\nP-ASTRAL-00042\nComposé sous le ciel du 14 juillet 1992\nPlume Astrale')
    pages.append(f'Fin\nPlume Astrale\n{heavy}')
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert r.passed, f'QA aurait dû passer : {r.blocking_issues}'
    assert r.page_count >= 20
    assert r.word_count >= 2500
    assert r.sections_found['cover']
    assert r.sections_found['ex_libris']


def test_qa_planets_mode_relaxed_thresholds():
    """Mode planets : min_pages=10, min_words=800, pas d'Ex-Libris requis."""
    heavy = 'planète astre ' * 60
    pages = [f'Thème Natal\nAlex\n{heavy}']
    for i in range(2, 12):
        pages.append(f'Planète {i}\n{heavy}')
    pages.append('Plume Astrale')
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Alex', mode='planets')
    assert r.passed, f'QA planets devrait passer : {r.blocking_issues}'


def test_assert_natal_pdf_quality_raises_on_fail():
    pdf = _make_minimal_pdf(['tiny'])
    with pytest.raises(NatalPdfQAError) as excinfo:
        assert_natal_pdf_quality(pdf, prenom='X', mode='rich')
    assert excinfo.value.report.passed is False


def test_qa_on_real_natal_pdf():
    """Smoke test : le PDF natal généré en vrai doit passer le QA en mode rich."""
    from services.natal_pdf_v2 import build_natal_pdf_v2

    natal_data = {
        'sun_sign': 'Cancer', 'moon_sign': 'Poissons', 'ascendant_sign': 'Vierge',
        'no_birth_time': False, 'tier': 'ultra',
        'planets': [
            {'name': n, 'sign': 'Lion', 'analysis': 'Analyse. ' * 40}
            for n in ['Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars', 'Jupiter',
                     'Saturne', 'Uranus', 'Neptune', 'Pluton', 'Ascendant']
        ],
        'synthese_aspects': 'Synthèse. ' * 80,
        'houses': [{'num': i, 'sign': 'Vierge', 'planets_in_house': []} for i in range(1, 13)],
        'enhanced_personal_analysis': {},
    }
    book_data = {
        '_source': 'cache',
        '_em': {'dominant_element': 'Eau', 'dominant_element_count': 5,
                'dominant_modality': 'Fixe', 'dominant_modality_count': 4},
        'dedication': 'Dédicace. ' * 20,
        'element_analysis': 'Eau. ' * 60,
        'modality_analysis': 'Fixe. ' * 60,
        'trio_synthesis': 'Trio. ' * 60,
        'aspects_harmonieux_body': 'Harm. ' * 60,
        'aspects_tensions_body': 'Tens. ' * 60,
        'rare_aspect_body': 'Rare. ' * 60,
        'houses_intro': 'Intro. ' * 60,
        'year_ahead': 'Année. ' * 60,
        **{f'house_{i}': f'Maison {i}. ' * 40 for i in range(1, 13)},
    }
    pdf = build_natal_pdf_v2(prenom='Clara', birth_date='1992-07-14',
                             natal_data=natal_data, book_data=book_data)
    # Important : simuler le strip_blanks que fait natal_book_service
    from services.pdf_strip_blanks import strip_blank_pages
    pdf = strip_blank_pages(pdf)

    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert r.passed, f'QA du vrai PDF natal doit passer. Issues : {r.blocking_issues}'
    assert r.sections_found['cover']
    assert r.sections_found['ex_libris']
    assert r.sections_found['plume_astrale_signature']



# ─── Spec Feb 2026 : règles éditoriales strictes ───────────────────

def test_qa_rejects_forbidden_complet_in_cover():
    """Le mot « complet » doit être banni du titre de couverture."""
    heavy = 'contenu riche ' * 200
    pages = [f'Thème Natal Complet\nClara\n{heavy}']
    for i in range(2, 22):
        pages.append(f'Page {i}\n{heavy}')
    pages.append('EX LIBRIS\nClara\nP-ASTRAL-00042\n14 juillet 1992\nPlume Astrale')
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('complet' in i.lower() for i in r.blocking_issues)


def test_qa_rejects_interior_page_below_40_words():
    """Une page intérieure non-structurelle sous 40 mots doit faire échouer la QA."""
    heavy = 'contenu riche ' * 200
    pages = [f'Thème Natal\nClara\n{heavy}']
    for i in range(2, 20):
        pages.append(f'Page {i}\n{heavy}')
    # Insertion d'une page très clairsemée (10 mots) au milieu
    pages[10] = 'Un titre bref sans contenu suffisant pour la zone utile'  # 10 mots
    pages.append('EX LIBRIS\nClara\nP-ASTRAL-00042\n14 juillet 1992\nPlume Astrale')
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('sous-remplie' in i for i in r.blocking_issues)
    assert len(r.low_density_pages) >= 1


def test_qa_exempts_structural_page_divider_from_density_check():
    """Une page part-divider « Partie I — » est exemptée du check densité."""
    heavy = 'contenu riche ' * 200
    pages = [f'Thème Natal\nClara\n{heavy}']
    # Insère un part divider très court
    pages.append('Partie I — Fondations')
    for i in range(3, 22):
        pages.append(f'Page {i}\n{heavy}')
    pages.append('EX LIBRIS\nClara\nP-ASTRAL-00042\n14 juillet 1992\nPlume Astrale')
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert r.passed, f'Un part-divider ne doit pas déclencher le check densité : {r.blocking_issues}'


def test_qa_ex_libris_requires_birth_year():
    """L'ex-libris doit contenir une année de naissance (4 chiffres)."""
    heavy = 'contenu riche ' * 200
    pages = [f'Thème Natal\nClara\n{heavy}']
    for i in range(2, 20):
        pages.append(f'Page {i}\n{heavy}')
    pages.append('EX LIBRIS\nClara\nP-ASTRAL-00042\nPlume Astrale')  # pas d'année
    pdf = _make_minimal_pdf(pages)
    r = qa_check_natal_pdf(pdf, prenom='Clara', mode='rich')
    assert not r.passed
    assert any('date de naissance' in i for i in r.blocking_issues)
