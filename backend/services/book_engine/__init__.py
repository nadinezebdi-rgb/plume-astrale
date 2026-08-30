"""Plume Astrale Book Rendering Engine.

Sépare strictement :
  - le CONTENU (`domain`)       : dataclasses typées, JSON-serializable, source de vérité
  - le RENDU (`document`)       : ReportLab BookDocument (à venir)
  - l'IMPRESSION (`providers`)  : PrintProvider interface + LuluPrintProvider (à venir)

Ce package est indépendant :
  - de Stripe (le webhook lui délègue la construction du Manuscript)
  - de Lulu/Bookelis (le provider est injecté)
  - du design courant (design_version stocké dans DB permet re-rendu)
"""
from .domain import (
    Manuscript,
    Chapter,
    ChapterBlock,
    BlockKind,
    BirthData,
    PrintSpecs,
    Edition,
    EditionMeta,
    EDITIONS,
)
from .registry import (
    ChapterSpec, Formule,
    SOCLE, ADDONS, FORMULES,
    get_socle, get_addons, get_addon_by_slug, get_formule,
    all_chapters_for_manuscript,
    DEUXIEME_PARTIE_LABEL, DEUXIEME_PARTIE_TITLE, DEUXIEME_PARTIE_KICKER,
)

__all__ = [
    'Manuscript', 'Chapter', 'ChapterBlock', 'BlockKind',
    'BirthData', 'PrintSpecs', 'Edition', 'EditionMeta', 'EDITIONS',
    'ChapterSpec', 'Formule', 'SOCLE', 'ADDONS', 'FORMULES',
    'get_socle', 'get_addons', 'get_addon_by_slug', 'get_formule',
    'all_chapters_for_manuscript',
    'DEUXIEME_PARTIE_LABEL', 'DEUXIEME_PARTIE_TITLE', 'DEUXIEME_PARTIE_KICKER',
]
