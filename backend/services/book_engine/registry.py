"""ChapterRegistry — structure verrouillée des chapitres du Livre Astral.

Contient :
  - Les 12 chapitres du SOCLE (obligatoires, présents dans tous les livres)
  - Les 6 chapitres OPTIONNELS (add-on /composer, Deuxième partie)
  - Les 5 FORMULES thématiques (bundles pré-configurés)

Chaque `ChapterSpec` définit la METADATA d'un chapitre (titre, kicker, roman num,
page count target, focus astral). Le CONTENU (blocks ChapterBlock) est produit
par le pipeline enrich() séparément, à partir de l'astro_data.

Séparation stricte contenu / structure — cohérent avec la Section 26 du brief.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# ChapterSpec — la spec figée d'un chapitre
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class ChapterSpec:
    slug: str
    title: str                        # h1 serif noir
    kicker: str                       # sous-titre manuscrit Allura
    roman_num: Optional[str]          # 'I' à 'XII' ou None (add-on ou colophon)
    order: int                        # ordre global dans le livre
    target_pages: int                 # cible indicative, jamais forcée
    is_addon: bool = False            # True pour les 6 chapitres optionnels
    requires_no_birth_time: bool = False  # ex: L'Heure Retrouvée
    astro_focus: str = ''             # documentation interne : quelles données astro drainer
    api_endpoint: Optional[str] = None  # endpoint astrology-api v3 (add-on)


# ═══════════════════════════════════════════════════════════════
# LES 12 CHAPITRES DU SOCLE — VERROUILLÉS
# ═══════════════════════════════════════════════════════════════
SOCLE: tuple[ChapterSpec, ...] = (
    ChapterSpec(
        slug='ciel_naissance',
        title='Votre ciel de naissance',
        kicker='Le portrait fixé par les étoiles ce matin-là…',
        roman_num='I', order=1, target_pages=8,
        astro_focus='Cadran natal + méta naissance + trio Soleil/Lune/Ascendant',
    ),
    ChapterSpec(
        slug='grandes_lignes',
        title='Les grandes lignes de vous',
        kicker='Ce que votre ciel raconte avant même que vous parliez.',
        roman_num='II', order=2, target_pages=8,
        astro_focus='Élément dominant · mode dominant · hémisphères N/S/E/O',
    ),
    ChapterSpec(
        slug='trio_identitaire',
        title='Votre trio identitaire',
        kicker='Soleil, Lune, Ascendant — les trois voix qui vous composent.',
        roman_num='III', order=3, target_pages=14,
        astro_focus='Soleil (signe/maison/aspects) · Lune (idem) · Ascendant + décan',
    ),
    ChapterSpec(
        slug='facon_aimer',
        title="Votre façon d'aimer",
        kicker='Ce que Vénus murmure de vous…',
        roman_num='IV', order=4, target_pages=10,
        astro_focus='Vénus (signe/maison/aspects/rétro) · Maison V · Lune vs Vénus',
    ),
    ChapterSpec(
        slug='facons_relations',
        title="Vos façons d'entrer en relation",
        kicker='Comment vous tendez la main — et à qui.',
        roman_num='V', order=5, target_pages=10,
        astro_focus='Maison VII (descendant) · Mars en amour · aspects Lune-Vénus',
    ),
    ChapterSpec(
        slug='forces_naturelles',
        title='Vos forces naturelles',
        kicker='Ce que vous savez faire sans y penser.',
        roman_num='VI', order=6, target_pages=10,
        astro_focus='Jupiter · planètes en dignité · aspects harmoniques (trigones, sextiles)',
    ),
    ChapterSpec(
        slug='passages_etroits',
        title='Vos passages étroits',
        kicker='Les endroits où votre ciel vous demande courage.',
        roman_num='VII', order=7, target_pages=12,
        astro_focus='Saturne · Chiron · carrés majeurs · oppositions',
    ),
    ChapterSpec(
        slug='travail_monde',
        title='Votre travail dans le monde',
        kicker='Ce que vous êtes venue faire ici.',
        roman_num='VIII', order=8, target_pages=10,
        astro_focus='Maison X · Milieu du Ciel · Saturne/Jupiter en X · maître MC',
    ),
    ChapterSpec(
        slug='dynamiques_vie',
        title='Vos grandes dynamiques de vie',
        kicker="Les axes qui traversent chacune de vos années.",
        roman_num='IX', order=9, target_pages=10,
        astro_focus='Axes Nœuds Sud/Nord · axe ASC-DSC · axe MC-FC · aspects majeurs',
    ),
    ChapterSpec(
        slug='temps_traverse',
        title='Le temps qui vous traverse',
        kicker="Les cycles que vous n'avez pas choisis, mais que vous habitez.",
        roman_num='X', order=10, target_pages=10,
        astro_focus='Retour de Saturne · cycles Jupiter · retour lunaire · progressions',
    ),
    ChapterSpec(
        slug='chemin_personnel',
        title='Votre chemin personnel',
        kicker='Ce vers quoi votre âme incline.',
        roman_num='XI', order=11, target_pages=10,
        astro_focus='Nœud Nord · Chiron · Pluton évolutif',
    ),
    ChapterSpec(
        slug='synthese_portrait',
        title='Portrait astral',
        kicker='Trois pages pour se souvenir de tout ceci…',
        roman_num='XII', order=12, target_pages=8,
        astro_focus='Synthèse des 3-4 signatures fortes du thème',
    ),
)


# ═══════════════════════════════════════════════════════════════
# LES 6 CHAPITRES ADD-ON — Deuxième partie /composer
# ═══════════════════════════════════════════════════════════════
ADDONS: tuple[ChapterSpec, ...] = (
    ChapterSpec(
        slug='arbre_de_vie',
        title="L'Arbre de Vie",
        kicker="Les dix stations où votre âme s'arrête.",
        roman_num='I', order=100, target_pages=12,  # order 100+ = deuxième partie
        is_addon=True,
        astro_focus='Séphiroth kabbalistiques appliquées aux 10 planètes du thème',
    ),
    ChapterSpec(
        slug='astrocartographie',
        title="L'Ailleurs qui vous appelle",
        kicker="Là où votre ciel s'allume dans le monde.",
        roman_num='II', order=101, target_pages=14,
        is_addon=True,
        astro_focus='Lignes MC/IC/AC/DSC planétaires · villes de résonance',
        api_endpoint='/api/astrology-v3/astrocartography',
    ),
    ChapterSpec(
        slug='karma_destin',
        title='Voyage Karmique',
        kicker='Ce que vous avez apporté avec vous en naissant.',
        roman_num='III', order=102, target_pages=16,
        is_addon=True,
        astro_focus='Nœuds lunaires · Saturne · Chiron · Pluton',
        api_endpoint='/api/astrology-v3/karma',
    ),
    ChapterSpec(
        slug='heure_retrouvee',
        title="L'Heure Retrouvée",
        kicker="Chercher l'écho de votre heure dans votre vie.",
        roman_num='IV', order=103, target_pages=10,
        is_addon=True,
        requires_no_birth_time=True,
        astro_focus='Rectification symbolique — jamais présentée comme calcul exact',
        api_endpoint='/api/astrology-v3/rectification',
    ),
    ChapterSpec(
        slug='etoiles_fixes',
        title='Étoiles Fixes',
        kicker='Les étoiles millénaires qui vous touchent.',
        roman_num='V', order=104, target_pages=10,
        is_addon=True,
        astro_focus='Regulus · Sirius · Aldébaran · Antarès · étoiles conjointes aux planètes',
        api_endpoint='/api/astrology-v3/fixed-stars',
    ),
    ChapterSpec(
        slug='symboles_sabiens',
        title='Symboles Sabiens',
        kicker='Une image pour chaque degré de votre ciel.',
        roman_num='VI', order=105, target_pages=12,
        is_addon=True,
        astro_focus='360 symboles Sabiens — images pour les 10 planètes + AC/MC',
        api_endpoint='/api/astrology-v3/sabian-symbols',
    ),
)


# ═══════════════════════════════════════════════════════════════
# LES 5 FORMULES THÉMATIQUES — bundles /composer
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Formule:
    slug: str
    label: str                        # nom marketing
    tagline: str                      # à qui elle s'adresse (phrase du client)
    addon_slugs: tuple[str, ...] = ()
    is_cap: bool = False              # True = tout compris plafond 99€


FORMULES: tuple[Formule, ...] = (
    Formule(
        slug='essentiel',
        label="L'Essentiel",
        tagline='Je veux comprendre mon ciel, sans plus.',
        addon_slugs=(),
    ),
    Formule(
        slug='traversee_interieure',
        label='La Traversée intérieure',
        tagline="Je me cherche, je veux savoir d'où je viens et où je vais.",
        addon_slugs=('karma_destin', 'arbre_de_vie'),
    ),
    Formule(
        slug='ailleurs',
        label="L'Ailleurs qui appelle",
        tagline="J'hésite entre plusieurs lieux, plusieurs vies.",
        addon_slugs=('astrocartographie',),
    ),
    Formule(
        slug='heure_retrouvee',
        label="L'Heure Retrouvée",
        tagline="Je n'ai pas mon heure exacte, mais je veux un vrai livre.",
        addon_slugs=('heure_retrouvee', 'symboles_sabiens'),
    ),
    Formule(
        slug='complet',
        label='Le Livre Complet',
        tagline='Je veux tout, sans compromis.',
        addon_slugs=('arbre_de_vie', 'astrocartographie', 'karma_destin',
                     'etoiles_fixes', 'symboles_sabiens'),
        is_cap=True,
    ),
)


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════
def get_socle() -> tuple[ChapterSpec, ...]:
    return SOCLE

def get_addons() -> tuple[ChapterSpec, ...]:
    return ADDONS

def get_addon_by_slug(slug: str) -> Optional[ChapterSpec]:
    return next((c for c in ADDONS if c.slug == slug), None)

def get_formule(slug: str) -> Optional[Formule]:
    return next((f for f in FORMULES if f.slug == slug), None)

def all_chapters_for_manuscript(addon_slugs: list[str]) -> list[ChapterSpec]:
    """Retourne le socle complet + les add-on choisis, dans l'ordre du livre."""
    ordered_addons = [c for c in ADDONS if c.slug in addon_slugs]
    return list(SOCLE) + ordered_addons


# ═══════════════════════════════════════════════════════════════
# Page de séparation Deuxième partie
# ═══════════════════════════════════════════════════════════════
DEUXIEME_PARTIE_LABEL = 'DEUXIÈME PARTIE'
DEUXIEME_PARTIE_TITLE = 'Vos chapitres choisis'
DEUXIEME_PARTIE_KICKER = 'Les lectures que vous avez ajoutées à votre livre.'
