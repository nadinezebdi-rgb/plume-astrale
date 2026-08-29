"""Domain model — dataclasses typées, source de vérité pour un livre.

Aucune dépendance à ReportLab, à Supabase, à Stripe.
Tout est JSON-serializable pour persistance dans `book_manuscripts.chapters` (JSONB)
et régénérable après un changement de design (`design_version`).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Données de naissance (immuables)
# ═══════════════════════════════════════════════════════════════
@dataclass
class BirthData:
    date_iso: str                  # 'YYYY-MM-DD'
    time_hhmm: Optional[str]       # 'HH:MM' ou None
    city: str
    country_code: str = 'FR'
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @property
    def no_birth_time(self) -> bool:
        """True si l'heure exacte est absente — active L'Heure Retrouvée et
        supprime le calcul de l'Ascendant / Maisons dans l'analyse."""
        return not self.time_hhmm or self.time_hhmm.strip() in ('', '12:00', '12:00:00')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'BirthData':
        return cls(
            date_iso=d['date_iso'],
            time_hhmm=d.get('time_hhmm'),
            city=d['city'],
            country_code=d.get('country_code', 'FR'),
            latitude=d.get('latitude'),
            longitude=d.get('longitude'),
        )


# ═══════════════════════════════════════════════════════════════
# Bloc éditorial — l'unité de composition d'un chapitre
# ═══════════════════════════════════════════════════════════════
class BlockKind(str, Enum):
    """Types de blocs autorisés dans un chapitre.

    Le RENDERER (BookDocument) sait dessiner chaque type. Chaque bloc est
    JSON-persistable et self-describing.
    """
    CHAPTER_OPENING = 'chapter_opening'    # tag + h1 + kicker manuscrit + plume — TOUJOURS page droite
    H2 = 'h2'                              # sous-titre serif noir
    PARAGRAPH = 'paragraph'                # corps texte justifié
    PARAGRAPH_DROPCAP = 'paragraph_dropcap'  # premier paragraphe du chapitre avec capitale ornée
    KICKER_SCRIPT = 'kicker_script'        # Allura manuscrit (ex: 'Ce que Vénus murmure...')
    NATAL_META = 'natal_meta'              # ligne meta (POISSONS · MAISON X · 11° 08′ RÉTROGRADE)
    TRIO_CARDS = 'trio_cards'              # trio Soleil/Lune/Ascendant sur ligne
    NATAL_CHART = 'natal_chart'            # roue du ciel — SVG astrology-api v3 bronze sur blanc
    ENCART = 'encart'                      # Votre Force / Défi / Clé — label + texte italique + filets
    QUOTE_LITERARY = 'quote_literary'      # citation en italique + source (Ptolémée)
    QUOTE_BREATH = 'quote_breath'          # respiration : 1 phrase + beaucoup de blanc
    DEDICATION_SCRIPT = 'dedication_script'  # dédicace Allura (ex: 'écrit pour vous,')
    FEATHER = 'feather'                    # emblème plume (petit ornement de respiration)
    HAIRLINE = 'hairline'                  # filet fin bronze — · —
    PAGE_BREAK = 'page_break'              # force nouvelle page
    IMAGE = 'image'                        # illustration (nom slug référencé dans la bibliothèque)


@dataclass
class ChapterBlock:
    """Un bloc éditorial : type + payload libre.

    Contract avec le renderer : le renderer connaît la structure attendue par
    chaque `kind`. Aucun rendu HTML ici, juste des chaînes brutes.

    Exemples :
      ChapterBlock(BlockKind.H2, {'text': 'Le langage secret de votre Vénus'})
      ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {'text': 'Vous n\\'aimez pas...'})
      ChapterBlock(BlockKind.ENCART, {'label': 'VOTRE FORCE', 'text': 'Vous sentez...'})
      ChapterBlock(BlockKind.NATAL_META, {'sign': 'POISSONS', 'house': 'MAISON X',
                                          'degree': '11° 08′', 'note': 'RÉTROGRADE'})
    """
    kind: BlockKind
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {'kind': self.kind.value, 'data': self.data}

    @classmethod
    def from_dict(cls, d: dict) -> 'ChapterBlock':
        return cls(kind=BlockKind(d['kind']), data=d.get('data', {}))


# ═══════════════════════════════════════════════════════════════
# Chapitre
# ═══════════════════════════════════════════════════════════════
@dataclass
class Chapter:
    """Un chapitre = un ensemble ordonné de blocs.

    `slug` correspond à l'identifiant du chapitre dans le ChapterRegistry.
    Les 12 chapitres du socle Thème Natal ont des slugs prédéfinis, et les
    chapitres optionnels /composer réutilisent les slugs de book_chapters.

    `roman_num` est utilisé pour le tag "CHAPITRE IV" en petites caps.
    """
    slug: str                              # ex: 'ta_carte_du_ciel', 'trio_identitaire', 'arbre_de_vie'
    title: str                             # ex: 'Votre ciel de naissance'
    kicker: Optional[str] = None           # sous-titre Allura (peut être None)
    roman_num: Optional[str] = None        # 'I' à 'XII' ou None (pour ouverture, colophon)
    order: int = 0                         # ordre dans le livre
    blocks: list[ChapterBlock] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'slug': self.slug,
            'title': self.title,
            'kicker': self.kicker,
            'roman_num': self.roman_num,
            'order': self.order,
            'blocks': [b.to_dict() for b in self.blocks],
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'Chapter':
        return cls(
            slug=d['slug'],
            title=d['title'],
            kicker=d.get('kicker'),
            roman_num=d.get('roman_num'),
            order=int(d.get('order', 0)),
            blocks=[ChapterBlock.from_dict(b) for b in d.get('blocks', [])],
        )


# ═══════════════════════════════════════════════════════════════
# Édition (Numérique / Brochée / Reliée) — pricing tier
# ═══════════════════════════════════════════════════════════════
class Edition(str, Enum):
    NUMERIQUE = 'numerique'
    BROCHEE = 'brochee'
    RELIEE = 'reliee'


@dataclass(frozen=True)
class EditionMeta:
    slug: Edition
    label: str
    price_eur: int
    delivery: str


EDITIONS: dict[Edition, EditionMeta] = {
    Edition.NUMERIQUE: EditionMeta(
        Edition.NUMERIQUE, 'Édition Numérique', 24,
        'PDF luxe livré en 5 minutes',
    ),
    Edition.BROCHEE: EditionMeta(
        Edition.BROCHEE, 'Édition Brochée', 69,
        'Livre broché imprimé, expédié sous 7 jours',
    ),
    Edition.RELIEE: EditionMeta(
        Edition.RELIEE, 'Édition Reliée', 119,
        'Livre cousu, numéroté à la main, approbation 72 h avant impression',
    ),
}


# ═══════════════════════════════════════════════════════════════
# Spécifications d'impression — négociées avec le PrintProvider
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class PrintSpecs:
    """Contrat que le PrintProvider expose au moteur pour produire un PDF PRINT.

    L'unité est le mm. Le PDF numérique est produit AVANT ces specs
    (MediaBox = trim). Le PDF PRINT applique ensuite bleed + TrimBox.
    """
    page_width_mm: float = 148.0           # A5 net
    page_height_mm: float = 210.0
    bleed_mm: float = 3.0                  # bord perdu (Lulu standard)
    inner_margin_mm: float = 20.0          # gouttière reliure
    outer_margin_mm: float = 16.0
    top_margin_mm: float = 22.0
    bottom_margin_mm: float = 22.0
    min_dpi: int = 300                     # DPI minimum accepté par l'imprimeur
    colorspace: str = 'sRGB'               # sRGB (Lulu convertit en CMYK)
    paper: str = 'creme_60'                # papier crème 60 lb (Lulu)
    binding: str = 'perfect'               # 'perfect' (broché) | 'casewrap' (relié)


# ═══════════════════════════════════════════════════════════════
# Manuscrit — l'objet livre complet
# ═══════════════════════════════════════════════════════════════
@dataclass
class Manuscript:
    """Un manuscrit = un livre destiné à une personne.

    Persisté dans `book_manuscripts`. Régénérable depuis les données JSONB
    sans réappeler le LLM — c'est le point clef de la séparation contenu/design.
    """
    id: Optional[str] = None               # UUID Supabase (None avant persistance)
    session_id: Optional[str] = None       # Stripe session
    user_email: str = ''
    first_name: str = ''
    birth_data: Optional[BirthData] = None
    astro_data: dict = field(default_factory=dict)  # positions v3, aspects, houses
    edition: Edition = Edition.NUMERIQUE
    selected_add_ons: list[str] = field(default_factory=list)  # slugs book_chapters
    chapters: list[Chapter] = field(default_factory=list)
    design_version: str = 'plume-astrale-v1'
    total_pages: Optional[int] = None
    total_price_eur: Optional[int] = None
    created_at: Optional[datetime] = None

    def add_chapter(self, chapter: Chapter) -> 'Manuscript':
        self.chapters.append(chapter)
        return self

    def chapter_by_slug(self, slug: str) -> Optional[Chapter]:
        return next((c for c in self.chapters if c.slug == slug), None)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_email': self.user_email,
            'first_name': self.first_name,
            'birth_data': self.birth_data.to_dict() if self.birth_data else None,
            'astro_data': self.astro_data,
            'edition': self.edition.value if isinstance(self.edition, Edition) else self.edition,
            'selected_add_ons': list(self.selected_add_ons),
            'chapters': [c.to_dict() for c in self.chapters],
            'design_version': self.design_version,
            'total_pages': self.total_pages,
            'total_price_eur': self.total_price_eur,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'Manuscript':
        bd = d.get('birth_data')
        created_at = d.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return cls(
            id=d.get('id'),
            session_id=d.get('session_id'),
            user_email=d.get('user_email', ''),
            first_name=d.get('first_name', ''),
            birth_data=BirthData.from_dict(bd) if bd else None,
            astro_data=d.get('astro_data', {}),
            edition=Edition(d.get('edition', 'numerique')),
            selected_add_ons=list(d.get('selected_add_ons', [])),
            chapters=[Chapter.from_dict(c) for c in d.get('chapters', [])],
            design_version=d.get('design_version', 'plume-astrale-v1'),
            total_pages=d.get('total_pages'),
            total_price_eur=d.get('total_price_eur'),
            created_at=created_at,
        )
