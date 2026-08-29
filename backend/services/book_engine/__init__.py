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

__all__ = [
    'Manuscript', 'Chapter', 'ChapterBlock', 'BlockKind',
    'BirthData', 'PrintSpecs', 'Edition', 'EditionMeta', 'EDITIONS',
]
