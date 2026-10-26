"""natal_pdf_qa — Contrôle qualité automatique du PDF Thème Natal.

Lot 4 du refactor PDF (demande user 2026-02-28) :
Avant tout envoi client (email ou téléchargement), valider le PDF via
PyMuPDF pour éviter d'envoyer un document cassé. Vérifie :

  - Nombre minimum de pages (≥ 15 pour un livre riche)
  - Absence de pages vides (texte visible non-trivial)
  - Présence des sections structurantes :
      * Couverture : "Thème Natal" + prénom
      * Ex-Libris : "EX LIBRIS" + prénom + numéro de copie
      * Pied : "Plume Astrale"
  - Nombre de mots total minimum (≥ 2 500 pour mode livre riche)
  - Zéro mention "Soléna" (persona retirée Feb 2026)

Usage :
    from services.natal_pdf_qa import qa_check_natal_pdf, QAReport

    report = qa_check_natal_pdf(pdf_bytes, prenom='Clara', mode='rich')
    if not report.passed:
        logger.error(f'PDF QA FAIL: {report.blocking_issues}')
        raise NatalPdfQAError(report)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pymupdf


# Seuils par mode d'édition
_THRESHOLDS = {
    'rich': {       # Livre riche (avec book_data : dédicace + 12 maisons + enrichissement)
        'min_pages': 20,
        'min_words_total': 2500,
        'require_ex_libris': True,
        'require_dedication': True,
    },
    'planets': {    # Édition "Planètes" (sans heure de naissance : juste les 10 planètes)
        'min_pages': 10,
        'min_words_total': 800,
        'require_ex_libris': False,
        'require_dedication': False,
    },
}


class NatalPdfQAError(Exception):
    """Levée quand le PDF ne passe pas le QA (contient le rapport)."""

    def __init__(self, report: 'QAReport'):
        self.report = report
        super().__init__(f'PDF QA failed: {report.blocking_issues}')


@dataclass
class QAReport:
    """Rapport détaillé du contrôle qualité."""
    passed: bool = True
    mode: str = 'rich'
    page_count: int = 0
    word_count: int = 0
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blank_pages: List[int] = field(default_factory=list)  # 1-indexed
    sections_found: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'passed': self.passed,
            'mode': self.mode,
            'page_count': self.page_count,
            'word_count': self.word_count,
            'blocking_issues': self.blocking_issues,
            'warnings': self.warnings,
            'blank_pages': self.blank_pages,
            'sections_found': self.sections_found,
        }


def qa_check_natal_pdf(pdf_bytes: bytes, prenom: str,
                       mode: str = 'rich') -> QAReport:
    """Analyse le PDF et retourne un rapport QA structuré.

    Args:
        pdf_bytes — contenu du PDF Thème Natal
        prenom    — prénom attendu (doit apparaître sur la couverture)
        mode      — 'rich' (livre complet) ou 'planets' (édition planètes seules)

    Returns:
        QAReport : passed=True si aucun blocking_issue, False sinon.
    """
    thresholds = _THRESHOLDS.get(mode, _THRESHOLDS['rich'])
    report = QAReport(mode=mode)

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype='pdf')
    except Exception as e:
        report.passed = False
        report.blocking_issues.append(f'PDF invalide (pymupdf) : {e}')
        return report

    try:
        report.page_count = len(doc)

        # 1) Nombre minimum de pages
        if report.page_count < thresholds['min_pages']:
            report.blocking_issues.append(
                f'Trop peu de pages : {report.page_count} < {thresholds["min_pages"]}'
            )

        # 2) Extraction & analyse par page
        full_text = ''
        pages_text: List[str] = []
        for i, page in enumerate(doc):
            txt = page.get_text() or ''
            pages_text.append(txt)
            full_text += txt + '\n'
            # Détection pages vides (après strip_blank_pages, il ne devrait plus en rester)
            stripped = ''.join(txt.split())
            # Page considérée vide si < 10 caractères visibles ET pas de bitmap
            has_images = len(page.get_images()) > 0
            if len(stripped) < 10 and not has_images:
                report.blank_pages.append(i + 1)

        if report.blank_pages:
            # Pages vides = warning (le strip devrait les enlever ; si en reste, à vérifier)
            report.warnings.append(
                f'Pages vides détectées : {report.blank_pages}'
            )
            # Si > 1 page vide → bloquant
            if len(report.blank_pages) > 1:
                report.blocking_issues.append(
                    f'Plus d\'une page vide ({len(report.blank_pages)}) — '
                    f'le strip_blank_pages n\'a pas fonctionné'
                )

        # 3) Nombre de mots total
        report.word_count = len(full_text.split())
        if report.word_count < thresholds['min_words_total']:
            report.blocking_issues.append(
                f'Contenu insuffisant : {report.word_count} mots < '
                f'{thresholds["min_words_total"]} attendus'
            )

        # 4) Sections structurantes
        cover_text = pages_text[0] if pages_text else ''
        report.sections_found['cover'] = 'Thème Natal' in cover_text
        if not report.sections_found['cover']:
            report.blocking_issues.append(
                'Titre « Thème Natal » absent de la couverture'
            )

        # Prénom sur la couverture
        report.sections_found['prenom_on_cover'] = (prenom in cover_text)
        if not report.sections_found['prenom_on_cover']:
            report.blocking_issues.append(
                f'Prénom « {prenom} » absent de la couverture'
            )

        # Ex-Libris (uniquement en mode rich)
        if thresholds['require_ex_libris']:
            ex_libris_found = False
            ex_libris_valid = False
            for txt in pages_text:
                if 'EX LIBRIS' in txt or 'E X   L I B R I S' in txt:
                    ex_libris_found = True
                    if prenom in txt and 'P-ASTRAL-' in txt:
                        ex_libris_valid = True
                    break
            report.sections_found['ex_libris'] = ex_libris_found
            report.sections_found['ex_libris_valid'] = ex_libris_valid
            if not ex_libris_found:
                report.blocking_issues.append('Page Ex-Libris introuvable')
            elif not ex_libris_valid:
                report.blocking_issues.append(
                    'Ex-Libris incomplet (prénom ou numéro de copie absent)'
                )

        # Pied Plume Astrale
        report.sections_found['plume_astrale_signature'] = (
            'PLUME ASTRALE' in full_text.upper() or 'Plume Astrale' in full_text
        )
        if not report.sections_found['plume_astrale_signature']:
            report.blocking_issues.append(
                'Signature « Plume Astrale » absente du document'
            )

        # 5) Aucune mention Soléna (persona retirée Feb 2026)
        lower = full_text.lower()
        if 'soléna' in lower or 'solena' in lower:
            report.blocking_issues.append(
                'Mention « Soléna » détectée — persona retirée depuis Feb 2026'
            )

        # 6) Décision finale
        report.passed = not report.blocking_issues

    finally:
        doc.close()

    return report


def assert_natal_pdf_quality(pdf_bytes: bytes, prenom: str,
                             mode: str = 'rich',
                             raise_on_fail: bool = True) -> QAReport:
    """Variante stricte qui lève NatalPdfQAError si le QA échoue."""
    report = qa_check_natal_pdf(pdf_bytes, prenom=prenom, mode=mode)
    if not report.passed and raise_on_fail:
        raise NatalPdfQAError(report)
    return report


__all__ = [
    'qa_check_natal_pdf', 'assert_natal_pdf_quality',
    'QAReport', 'NatalPdfQAError',
]
