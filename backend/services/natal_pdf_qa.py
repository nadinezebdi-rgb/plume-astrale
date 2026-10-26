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
        'min_words_per_body_page': 120,  # page de texte courant
        'min_words_per_interior_page': 40,   # minimum absolu (page intérieure, hors cover/colophon)
        'min_fill_ratio': 0.60,          # ≥ 60 % de la zone utile remplie
        'require_ex_libris': True,
        'require_dedication': True,
    },
    'planets': {    # Édition "Planètes" (sans heure de naissance : juste les 10 planètes)
        'min_pages': 10,
        'min_words_total': 800,
        'min_words_per_body_page': 80,
        'min_words_per_interior_page': 25,
        'min_fill_ratio': 0.50,
        'require_ex_libris': False,
        'require_dedication': False,
    },
}

# Mots-interdits sur la couverture (titre).
_FORBIDDEN_COVER_WORDS = {'complet'}

# Pages structurelles exemptées des règles de densité minimale (couverture,
# faux-titre, demi-titres, colophon). Index 1-based.
_STRUCTURAL_SPARSE_MARKERS = (
    'EX LIBRIS', 'E X   L I B R I S',  # ex-libris : illustration prédominante
)

# Patterns regex identifiant une page structurelle légitime (demi-titre,
# diviseur de partie, dédicace, copyright, colophon, TOC). Ces pages ont
# un contenu volontairement sparse (respiration éditoriale).
_STRUCTURAL_PAGE_PATTERNS = (
    r'TABLE\s+DES\s+MATIÈRES',          # TOC
    r'Partie\s+[IVX]+\s*—',              # part dividers (Partie I —, II —, III —)
    r'©\s*Plume\s*Astrale',              # page copyright
    r'puisse-t-il devenir compagnon',    # dédicace par défaut
    r'^\s*Thème\s+Natal\s*$',            # half-title (page avec juste le titre)
    r'Plume\s*Astrale\s*·\s*Atelier',   # colophon
    r'Écrit\s+sous\s+les\s+étoiles',    # page éphéméride
    r'^\s*Colophon\s*$',                 # page titre colophon seule
    r'^\s*[A-ZÀ-Ü][A-ZÀ-Ü\-\s]{2,}\s*·\s*·\s*·\s*\d+\s+\w+\s+\d{4}\s*$',  # frontispice (NOM COMPOSÉ · · · DATE FR)
    r'·\s*·\s*·.*ÉDITION\s+PERSONNELLE',  # frontispice fallback (contient "ÉDITION PERSONNELLE")
    r'—\s*Plume\s*Astrale\s*$',          # dédicace signée (texte + — Plume Astrale)
)


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
    low_density_pages: List[dict] = field(default_factory=list)  # [{'page': n, 'words': w, 'fill': f}]
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
            'low_density_pages': self.low_density_pages,
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

        # 2bis) Pages intérieures sous-remplies (règle spec Feb 2026)
        # Zone utile A4 = (595 - 2*marge) × (842 - 2*marge). On estime la densité
        # par la surface des rectangles de texte vs la zone utile.
        import re as _re
        pages_sparse: List[int] = []
        min_fill = thresholds.get('min_fill_ratio', 0)
        min_words_interior = thresholds.get('min_words_per_interior_page', 0)
        structural_regex = _re.compile('|'.join(_STRUCTURAL_PAGE_PATTERNS),
                                       _re.IGNORECASE | _re.MULTILINE)
        for i, page in enumerate(doc):
            # Exempte : couverture (i=0), colophon (dernière)
            if i == 0 or i == report.page_count - 1:
                continue
            txt = pages_text[i] if i < len(pages_text) else ''
            upper_txt = txt.upper()
            if any(mk in upper_txt for mk in _STRUCTURAL_SPARSE_MARKERS):
                continue
            # Exempte les pages structurelles (demi-titre, part divider, copyright, dédicace…)
            if structural_regex.search(txt):
                continue
            n_words = len(txt.split())
            has_images = len(page.get_images()) > 0

            # Fill ratio = extent vertical du contenu / hauteur de page utile.
            # Plus fiable que content_area / useful_area (évite les fausses alertes
            # dues aux espaces inter-paragraphes).
            page_rect = page.rect
            blocks = page.get_text('dict').get('blocks', [])
            if blocks:
                y_min = min((b.get('bbox', (0, 1e9, 0, 0))[1] for b in blocks), default=0)
                y_max = max((b.get('bbox', (0, 0, 0, -1))[3] for b in blocks), default=0)
                content_height = max(0, y_max - y_min)
                useful_height = page_rect.height * 0.80  # marges top/bottom ~10%
                fill_ratio = min(1.0, content_height / max(1.0, useful_height))
            else:
                fill_ratio = 0.0

            # Décisions bloquantes :
            # a) page sans texte (< min_words_interior) ET sans image
            if n_words < min_words_interior and not has_images:
                pages_sparse.append(i + 1)
                report.low_density_pages.append({
                    'page': i + 1, 'words': n_words,
                    'fill': round(fill_ratio, 3), 'reason': 'words_below_min',
                })
                continue
            # b) page texte courant sous le seuil de remplissage ET sans image
            if (fill_ratio < min_fill and
                    n_words < thresholds.get('min_words_per_body_page', 120) and
                    not has_images):
                pages_sparse.append(i + 1)
                report.low_density_pages.append({
                    'page': i + 1, 'words': n_words,
                    'fill': round(fill_ratio, 3), 'reason': 'fill_below_min',
                })

        if pages_sparse:
            report.blocking_issues.append(
                f'{len(pages_sparse)} page(s) intérieure(s) sous-remplie(s) '
                f'(< {int(min_fill*100)} % utile ou < {min_words_interior} mots) : '
                f'{pages_sparse[:10]}'
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

        # 4bis) Aucun mot-interdit sur la couverture (spec Feb 2026 : pas de « complet »)
        cover_lower = cover_text.lower()
        for forbidden in _FORBIDDEN_COVER_WORDS:
            if forbidden in cover_lower:
                report.blocking_issues.append(
                    f'Mot interdit « {forbidden} » détecté sur la couverture'
                )

        # Prénom sur la couverture (robuste aux coupures de ligne)
        cover_normalized = ' '.join(cover_text.split())
        report.sections_found['prenom_on_cover'] = (prenom in cover_normalized)
        if not report.sections_found['prenom_on_cover']:
            report.blocking_issues.append(
                f'Prénom « {prenom} » absent de la couverture'
            )

        # Ex-Libris (uniquement en mode rich) — doit contenir prénom + N° + date naissance
        if thresholds['require_ex_libris']:
            ex_libris_found = False
            ex_libris_valid = False
            ex_libris_missing: List[str] = []
            # On accepte la date au format FR (ex: "14 juillet 1992") ou ISO (1992-07-14).
            # Le QA ne connaît que la date complète via le PDF texte ; on vérifie
            # qu'une année 4 chiffres cohérente apparaît sur la page ex-libris.
            import re as _re
            for txt in pages_text:
                if 'EX LIBRIS' in txt or 'E X   L I B R I S' in txt:
                    ex_libris_found = True
                    has_prenom = prenom in txt
                    has_copy = 'P-ASTRAL-' in txt
                    has_date = bool(_re.search(r'\b(19|20)\d{2}\b', txt))
                    if not has_prenom:
                        ex_libris_missing.append('prénom')
                    if not has_copy:
                        ex_libris_missing.append('numéro d\'exemplaire')
                    if not has_date:
                        ex_libris_missing.append('date de naissance')
                    ex_libris_valid = not ex_libris_missing
                    break
            report.sections_found['ex_libris'] = ex_libris_found
            report.sections_found['ex_libris_valid'] = ex_libris_valid
            if not ex_libris_found:
                report.blocking_issues.append('Page Ex-Libris introuvable')
            elif not ex_libris_valid:
                report.blocking_issues.append(
                    f'Ex-Libris incomplet (manque : {", ".join(ex_libris_missing)})'
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
