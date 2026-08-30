"""book_composer_pricing.py — moteur de prix L'Atelier /composer (2026-03).

Contexte pivot : le Thème Natal devient l'UNIQUE base ; les autres rapports
sont des "chapitres" optionnels ajoutés à un livre unifié. La règle métier
est stricte côté serveur (source de vérité) — le front est décoratif :

    +29€ pour le 1er chapitre choisi
    +19€ pour chaque chapitre suivant
    Plafond 99€ pour la totalité des chapitres (pack "tout compris")

L'édition (Numérique 24€ / Broché 69€ / Relié 119€) est un tier séparé
qui inclut déjà le Thème Natal base — les chapitres s'ajoutent par-dessus.

Exemples :
    Numérique + 0 chapitre                    = 24€
    Numérique + 1 chapitre                    = 24 + 29 = 53€
    Numérique + 2 chapitres                   = 24 + 29 + 19 = 72€
    Numérique + 6 chapitres (plafond)         = 24 + 99 = 123€
    Broché + 3 chapitres                      = 69 + 29 + 19 + 19 = 136€
    Relié + 6 chapitres                       = 119 + 99 = 218€
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from services.supabase_client import get_admin_client

logger = logging.getLogger(__name__)

# ── Règles de pricing (immuables — verrouillées par tests) ──────
FIRST_CHAPTER_PRICE_EUR = 29
NEXT_CHAPTER_PRICE_EUR = 19
CHAPTERS_TOTAL_CAP_EUR = 99  # plafond sur la SOMME des chapitres uniquement

# Éditions (miroir de config.PACKS ; centralisé ici pour éviter le doublon logique)
EDITIONS = {
    'numerique': {
        'pack_id': 'theme_natal_pdf_oneshot',
        'label': 'Édition Numérique',
        'price_eur': 24,
        'delivery': 'PDF luxe livré en 5 minutes',
        'pages_base': 49,
    },
    'brochee': {
        'pack_id': 'edition_brochee',
        'label': 'Édition Brochée',
        'price_eur': 69,
        'delivery': 'Livre broché imprimé, expédié sous 7 jours',
        'pages_base': 49,
    },
    'reliee': {
        'pack_id': 'edition_reliee',
        'label': 'Édition Reliée',
        'price_eur': 119,
        'delivery': 'Livre cousu, numéroté à la main, approbation 72h avant impression',
        'pages_base': 49,
    },
}


# ── Modèles typés ────────────────────────────────────────────────
@dataclass
class Chapter:
    slug: str
    name: str
    subtitle: Optional[str]
    price_unit_eur: int
    pages_added: int
    is_active: bool
    requires_no_birth_time: bool
    sort_order: int
    tagline: Optional[str]
    api_endpoint: Optional[str] = None


@dataclass
class Quote:
    edition: str                  # 'numerique' | 'brochee' | 'reliee'
    edition_label: str
    edition_price_eur: int
    chapters: List[dict] = field(default_factory=list)   # [{slug, name, unit_eur}]
    chapters_subtotal_eur: int = 0                       # avant plafond
    chapters_price_eur: int = 0                          # après plafond
    chapters_cap_applied: bool = False
    total_eur: int = 0
    total_pages: int = 49
    currency: str = 'eur'
    warnings: List[str] = field(default_factory=list)


# ── Chargement chapitres depuis Supabase (avec fallback local) ──
def load_active_chapters(no_birth_time: bool = False) -> List[Chapter]:
    """Charge les chapitres actifs, filtre ceux réservés au flag no_birth_time.

    Si le flag `no_birth_time=False`, on exclut les chapitres avec
    `requires_no_birth_time=True` (ex: L'Heure Retrouvée).
    Si Supabase est indisponible, retombe sur le seed hard-codé (safe fallback).
    """
    try:
        sb = get_admin_client()
        r = sb.table('book_chapters').select('*').eq('is_active', True).order('sort_order').execute()
        rows = r.data or []
    except Exception as e:
        logger.warning(f'[composer_pricing] Supabase fetch failed, using local fallback: {e}')
        rows = _LOCAL_FALLBACK_CHAPTERS

    chapters: List[Chapter] = []
    for row in rows:
        ch = Chapter(
            slug=row['slug'],
            name=row['name'],
            subtitle=row.get('subtitle'),
            price_unit_eur=int(row.get('price_unit_eur') or FIRST_CHAPTER_PRICE_EUR),
            pages_added=int(row.get('pages_added') or 12),
            is_active=bool(row.get('is_active', True)),
            requires_no_birth_time=bool(row.get('requires_no_birth_time', False)),
            sort_order=int(row.get('sort_order') or 0),
            tagline=row.get('tagline'),
            api_endpoint=row.get('api_endpoint'),
        )
        if not ch.is_active:
            continue
        # Filtre "requires_no_birth_time"
        if ch.requires_no_birth_time and not no_birth_time:
            continue
        chapters.append(ch)
    return chapters


def compute_quote(
    *,
    edition: str,
    chapter_slugs: List[str],
    no_birth_time: bool = False,
) -> Quote:
    """Calcule la quote — SOURCE DE VÉRITÉ SERVEUR.

    Règles :
      - `edition` obligatoire, dans {numerique, brochee, reliee}
      - `chapter_slugs` : liste de slugs actifs (dédupliqués, ordre préservé)
      - Prix : 1er = 29€, suivants = 19€, plafond 99€ (chapitres uniquement)
      - Total = edition_price + chapters_price
    """
    if edition not in EDITIONS:
        raise ValueError(f"Édition inconnue : {edition!r}. Valeurs autorisées : {list(EDITIONS.keys())}")

    edition_meta = EDITIONS[edition]

    # Dédup en préservant l'ordre
    seen = set()
    dedup_slugs: List[str] = []
    for slug in chapter_slugs or []:
        if slug and slug not in seen:
            seen.add(slug)
            dedup_slugs.append(slug)

    # Charge le catalogue et indexe par slug
    catalog = load_active_chapters(no_birth_time=no_birth_time)
    by_slug = {c.slug: c for c in catalog}

    warnings: List[str] = []
    selected: List[Chapter] = []
    for slug in dedup_slugs:
        ch = by_slug.get(slug)
        if not ch:
            warnings.append(f"Chapitre '{slug}' indisponible et ignoré.")
            continue
        selected.append(ch)

    # Calcul prix chapitres avec règle 29/19 + plafond 99
    if not selected:
        chapters_subtotal = 0
    else:
        chapters_subtotal = FIRST_CHAPTER_PRICE_EUR + NEXT_CHAPTER_PRICE_EUR * (len(selected) - 1)
    chapters_price = min(chapters_subtotal, CHAPTERS_TOTAL_CAP_EUR)
    cap_applied = chapters_subtotal > CHAPTERS_TOTAL_CAP_EUR

    total = edition_meta['price_eur'] + chapters_price
    total_pages = edition_meta['pages_base'] + sum(c.pages_added for c in selected)

    return Quote(
        edition=edition,
        edition_label=edition_meta['label'],
        edition_price_eur=edition_meta['price_eur'],
        chapters=[
            {
                'slug': c.slug,
                'name': c.name,
                'subtitle': c.subtitle,
                'pages_added': c.pages_added,
                # Prix marginal réel de CE chapitre à sa position (utile UI)
                'unit_eur': FIRST_CHAPTER_PRICE_EUR if i == 0 else NEXT_CHAPTER_PRICE_EUR,
            }
            for i, c in enumerate(selected)
        ],
        chapters_subtotal_eur=chapters_subtotal,
        chapters_price_eur=chapters_price,
        chapters_cap_applied=cap_applied,
        total_eur=total,
        total_pages=total_pages,
        currency='eur',
        warnings=warnings,
    )


# ── Fallback local (si Supabase KO au boot) ─────────────────────
_LOCAL_FALLBACK_CHAPTERS = [
    {'slug': 'arbre_de_vie', 'name': "L'Arbre de Vie",
     'subtitle': 'Les 10 Séphiroth appliquées à votre ciel',
     'price_unit_eur': 29, 'pages_added': 12, 'is_active': True,
     'requires_no_birth_time': False, 'sort_order': 10,
     'tagline': "La kabbale hébraïque traduit votre thème en dix stations d'âme.",
     'api_endpoint': None},
    {'slug': 'astrocartographie', 'name': 'Astrocartographie',
     'subtitle': "Où votre ciel s'allume dans le monde",
     'price_unit_eur': 29, 'pages_added': 14, 'is_active': True,
     'requires_no_birth_time': False, 'sort_order': 20,
     'tagline': 'Vos lignes planétaires tracées sur la carte du monde, ville par ville.',
     'api_endpoint': '/api/astrology-v3/astrocartography'},
    {'slug': 'karma_destin', 'name': 'Voyage Karmique',
     'subtitle': 'Nœuds lunaires, Saturne, Chiron, Pluton',
     'price_unit_eur': 29, 'pages_added': 16, 'is_active': True,
     'requires_no_birth_time': False, 'sort_order': 30,
     'tagline': "Ce que votre âme a apporté avec elle — et ce qu'elle vient dénouer.",
     'api_endpoint': '/api/astrology-v3/karma'},
    {'slug': 'heure_retrouvee', 'name': "L'Heure Retrouvée",
     'subtitle': 'Rectification symbolique de votre heure de naissance',
     'price_unit_eur': 29, 'pages_added': 10, 'is_active': True,
     'requires_no_birth_time': True, 'sort_order': 40,
     'tagline': "Vous n'avez pas votre heure exacte ? Nous cherchons son écho dans votre biographie.",
     'api_endpoint': '/api/astrology-v3/rectification'},
    {'slug': 'etoiles_fixes', 'name': 'Étoiles Fixes',
     'subtitle': 'Les étoiles millénaires qui touchent vos planètes',
     'price_unit_eur': 29, 'pages_added': 10, 'is_active': True,
     'requires_no_birth_time': False, 'sort_order': 50,
     'tagline': 'Régulus, Sirius, Aldébaran… lesquelles vous éclairent, et où.',
     'api_endpoint': '/api/astrology-v3/fixed-stars'},
    {'slug': 'symboles_sabiens', 'name': 'Symboles Sabiens',
     'subtitle': '360 images pour lire chaque degré de votre thème',
     'price_unit_eur': 29, 'pages_added': 12, 'is_active': True,
     'requires_no_birth_time': False, 'sort_order': 60,
     'tagline': 'Chaque degré du zodiaque porte une image. Voici celles qui vous concernent.',
     'api_endpoint': '/api/astrology-v3/sabian-symbols'},
]
