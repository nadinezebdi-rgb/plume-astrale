"""lulu_provider — Calcul des specs d'impression et estimation prix Lulu.com.

Formules dérivées de la doc officielle Lulu (2025) :
  - Spine width (papier standard cream 60 lb, ~110 gsm) :
       spine_mm = pages_count * 0.0572   (arrondi ± 0.5 mm)
  - Cover total width (A5) = 2 × 148 mm (couvertures) + spine + 3 mm bleed × 2
  - Bleed : 3 mm sur les 4 côtés (§1 du guide)
  - Safety margin : 5 mm depuis le bord rogné (§1 du guide)

Endpoint d'estimation de prix : simplifié via table barème (prod / distrib /
reliure). Pour un vrai devis, l'utilisateur passe par l'API Lulu Print Fulfillment
en production — hors périmètre de ce lot.

Signature publique :
  - `calculate_spine_mm(pages_count, paper_type='cream_60') -> float`
  - `validate_manuscript_for_print(manuscript, edition) -> LuluValidation`
  - `estimate_retail_price_eur(pages, edition, quantity=1) -> float`
  - `build_cover_spec(pages, trim_size='a5') -> dict` (specs à envoyer à Lulu)
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from services.book_engine.domain import Edition, Manuscript

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Constantes Lulu (2025)
# ═══════════════════════════════════════════════════════════════════
# Épaisseur par page en mm selon le type de papier Lulu
PAPER_THICKNESS_MM = {
    'cream_60':      0.0572,   # 60 lb cream (standard offset) — recommandé
    'white_60':      0.0572,
    'white_80':      0.0736,   # 80 lb white (premium)
    'photo_100':     0.1000,   # coated 100 lb (photo book)
}

# Minimum pages pour la reliure Lulu
MIN_PAGES_PERFECT_BINDING = 32      # Broché
MIN_PAGES_CASE_WRAP = 24            # Relié cartonné

# Coûts de base Lulu (2025, retail Europe, EUR TTC estimé)
# Modèle : cost = base + per_page * pages
COST_MODEL = {
    Edition.BROCHEE: {
        'base_eur':    4.20,
        'per_page':    0.055,
        'shipping':    3.90,       # Colissimo France, colis unitaire
    },
    Edition.RELIEE: {
        'base_eur':    9.80,
        'per_page':    0.070,
        'shipping':    5.90,
    },
}

# Marge Plume Astrale (multiplicateur retail)
PLUME_MARGIN = 2.2


# ═══════════════════════════════════════════════════════════════════
# API publique
# ═══════════════════════════════════════════════════════════════════
@dataclass
class LuluValidation:
    ok: bool
    edition: str
    pages: int
    spine_mm: float
    cover_width_mm: float
    cover_height_mm: float
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'ok': self.ok,
            'edition': self.edition,
            'pages': self.pages,
            'spine_mm': round(self.spine_mm, 2),
            'cover_width_mm': round(self.cover_width_mm, 2),
            'cover_height_mm': round(self.cover_height_mm, 2),
            'issues': self.issues,
            'warnings': self.warnings,
        }


def calculate_spine_mm(pages_count: int, paper_type: str = 'cream_60') -> float:
    """Retourne la largeur du dos en mm pour une reliure parfaite/cartonnée."""
    if pages_count < 1:
        return 0.0
    thick = PAPER_THICKNESS_MM.get(paper_type, PAPER_THICKNESS_MM['cream_60'])
    return round(pages_count * thick, 2)


def build_cover_spec(pages: int, trim_mm: tuple[float, float] = (148.0, 210.0),
                     paper_type: str = 'cream_60',
                     bleed_mm: float = 3.0) -> dict:
    """Retourne les dimensions à envoyer à Lulu pour la couverture complète.

    Couverture Lulu = dos + verso + recto + bleeds latéraux.
    """
    trim_w, trim_h = trim_mm
    spine = calculate_spine_mm(pages, paper_type)
    cover_w = 2 * trim_w + spine + 2 * bleed_mm
    cover_h = trim_h + 2 * bleed_mm
    return {
        'trim_mm': trim_mm,
        'spine_mm': spine,
        'cover_total_mm': (round(cover_w, 2), round(cover_h, 2)),
        'bleed_mm': bleed_mm,
        'paper_type': paper_type,
    }


def validate_manuscript_for_print(
    manuscript: Manuscript,
    edition: Edition,
    *,
    pages_hint: Optional[int] = None,
) -> LuluValidation:
    """Vérifie qu'un manuscrit peut être imprimé selon l'édition demandée.

    `pages_hint` = nombre de pages du PDF final (à passer si connu, sinon
    approximation depuis le nombre de chapitres × pages moyennes).
    """
    if pages_hint is None:
        # Approximation : 30 pages fixes (cover/blanches/colophon) + 10 pages/chapitre
        pages_hint = 30 + sum(10 for _ in manuscript.chapters)
    # Arrondir au multiple de 4 supérieur (§1 du guide)
    if pages_hint % 4 != 0:
        pages_hint = pages_hint + (4 - pages_hint % 4)

    spine = calculate_spine_mm(pages_hint)
    spec = build_cover_spec(pages_hint)

    issues: list[str] = []
    warnings: list[str] = []

    if edition == Edition.BROCHEE and pages_hint < MIN_PAGES_PERFECT_BINDING:
        issues.append(
            f'Broché nécessite ≥ {MIN_PAGES_PERFECT_BINDING} pages, {pages_hint} détectées'
        )
    if edition == Edition.RELIEE and pages_hint < MIN_PAGES_CASE_WRAP:
        issues.append(
            f'Relié cartonné nécessite ≥ {MIN_PAGES_CASE_WRAP} pages, {pages_hint} détectées'
        )
    if pages_hint > 800:
        issues.append(f'Lulu ne relie pas au-delà de 800 pages ({pages_hint})')
    if spine < 3.0:
        warnings.append(f'Dos très mince ({spine} mm) — pas de titre sur la tranche')
    if pages_hint % 4 != 0:
        issues.append(f'Pages doit être multiple de 4 (actuel : {pages_hint})')

    return LuluValidation(
        ok=len(issues) == 0,
        edition=edition.value if isinstance(edition, Edition) else str(edition),
        pages=pages_hint,
        spine_mm=spine,
        cover_width_mm=spec['cover_total_mm'][0],
        cover_height_mm=spec['cover_total_mm'][1],
        issues=issues,
        warnings=warnings,
    )


def estimate_retail_price_eur(
    pages: int, edition: Edition, quantity: int = 1,
) -> dict:
    """Estimation prix TTC pour l'utilisateur final (marge Plume Astrale incluse)."""
    if edition not in COST_MODEL:
        raise ValueError(f'Edition non imprimable: {edition}')
    m = COST_MODEL[edition]
    prod_cost = m['base_eur'] + m['per_page'] * pages
    subtotal = prod_cost * PLUME_MARGIN * quantity
    total = subtotal + m['shipping']
    return {
        'edition': edition.value if isinstance(edition, Edition) else edition,
        'pages': pages,
        'quantity': quantity,
        'production_cost_eur': round(prod_cost, 2),
        'plume_price_eur': round(subtotal, 2),
        'shipping_eur': round(m['shipping'], 2),
        'total_eur': round(total, 2),
    }
