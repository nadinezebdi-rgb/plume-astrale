"""
Wrapper luxe pour les PDFs existants (Kabbale, Astrocarto).

Approche : ajouter les 3 signatures luxe (couverture spectaculaire,
ouverture, fin émotionnelle Soléna) en cover_pages/ending_pages
autour du contenu métier existant, SANS toucher aux 500 lignes qui
ont été validées et qui affichent les vraies données.

Résultat : les PDFs Kabbale et Astrocarto héritent immédiatement de
la charte "livre de luxe" tout en gardant leur contenu spécifique.
"""
from __future__ import annotations
import io
import logging
from typing import Callable

logger = logging.getLogger(__name__)

# Slugs adaptés à chaque produit
KABBALE_SLUGS = {
    'cover': 'astral_mandala',
    'ending': 'astral_silhouette',
}
ASTROCARTO_SLUGS = {
    'cover': 'ciel_zodiaque',
    'ending': 'astral_silhouette',
}
KARMIQUE_SLUGS = {
    'cover': 'astral_planete',
    'ending': 'astral_silhouette',
}


def _prepend_luxury_cover(pdf_bytes: bytes, prenom: str, subtitle: str, cover_slug: str,
                          grid_cells: list = None, grid_title: str = None, grid_tag: str = None) -> bytes:
    """Ajoute 2–3 pages luxe (cover + ouverture + grille 2×2 optionnelle) devant un PDF existant.

    Utilise pypdf pour merger. Robuste : si merge fail, retourne le PDF original
    intact (jamais casser une vente).
    """
    try:
        from services.pdf_luxury_theme import (
            build_luxury_doc, luxury_styles, luxury_bg,
            cover_page, opening_page, photos_grid_2x2,
        )

        # 1. Générer les pages luxe en PDF
        buf = io.BytesIO()
        doc = build_luxury_doc(buf, title=f'Plume Astrale — {prenom}')
        styles = luxury_styles()
        story = []
        cover_page(story, styles, prenom=prenom, subtitle=subtitle, illustration_slug=cover_slug)
        opening_page(story, styles, prenom=prenom, first_line="Voici ce que tu as attiré à toi.")
        if grid_cells and grid_title:
            photos_grid_2x2(story, styles,
                            chapter_tag=grid_tag or '✦ Ton empreinte ✦',
                            title=grid_title,
                            cells=grid_cells)
        doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
        cover_bytes = buf.getvalue()

        # 2. Merger cover + PDF original
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()
        for pg in PdfReader(io.BytesIO(cover_bytes)).pages:
            writer.add_page(pg)
        for pg in PdfReader(io.BytesIO(pdf_bytes)).pages:
            writer.add_page(pg)
        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception as e:
        logger.warning(f'[pdf_luxury_wrap] cover merge failed, returning original: {e}')
        return pdf_bytes


def _append_luxury_ending(pdf_bytes: bytes, prenom: str, ending_slug: str) -> bytes:
    """Ajoute la fin émotionnelle Soléna (1 page dense) à la fin d'un PDF existant.

    Refactor 2026-02-22 : suppression de la page `waouh_quote_page` qui n'avait
    qu'une phrase (« Ton plus grand défi… »). Le contenu poétique est déjà porté
    par `emotional_ending`.
    """
    try:
        from services.pdf_luxury_theme import (
            build_luxury_doc, luxury_styles, luxury_bg, emotional_ending,
        )

        buf = io.BytesIO()
        doc = build_luxury_doc(buf, title=f'Plume Astrale — {prenom} — Épilogue')
        styles = luxury_styles()
        story = []
        emotional_ending(story, styles, prenom=prenom)
        doc.build(story, onFirstPage=luxury_bg, onLaterPages=luxury_bg)
        ending_bytes = buf.getvalue()

        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()
        for pg in PdfReader(io.BytesIO(pdf_bytes)).pages:
            writer.add_page(pg)
        for pg in PdfReader(io.BytesIO(ending_bytes)).pages:
            writer.add_page(pg)
        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception as e:
        logger.warning(f'[pdf_luxury_wrap] ending merge failed, returning original: {e}')
        return pdf_bytes


SYNASTRY_SLUGS = {
    'cover': 'couple',           # Image "front contre front" — bibliothèque interne
    'ending': 'astral_silhouette',
}

# Fallback si le slug demandé n'est pas encore présent sur Supabase
_SYNASTRY_FALLBACK_SLUG = 'amoureux'


def apply_luxury_wrap(pdf_bytes: bytes, prenom: str, subtitle: str, product: str = 'kabbale') -> bytes:
    """Enveloppe complète : cover + ouverture + grille 2×2 thématique + [contenu existant] + fin Soléna."""
    from services import library_images as libimg

    if product == 'astrocarto':
        slugs = ASTROCARTO_SLUGS
        grid_tag = '✦ Tes lignes-monde ✦'
        grid_title = 'Les 4 planètes qui tracent ta géographie sacrée'
        grid_cells = [
            {'image': libimg.planet('Soleil'), 'label': 'Soleil', 'sublabel': 'Ta vitalité'},
            {'image': libimg.planet('Vénus'), 'label': 'Vénus', 'sublabel': 'Ton amour'},
            {'image': libimg.planet('Mars'), 'label': 'Mars', 'sublabel': 'Ta puissance'},
            {'image': libimg.planet('Jupiter'), 'label': 'Jupiter', 'sublabel': 'Ta chance'},
        ]
    elif product == 'karmique':
        slugs = KARMIQUE_SLUGS
        grid_tag = '✦ Ton empreinte d\'âme ✦'
        grid_title = 'Les 4 piliers de ton chemin karmique'
        grid_cells = [
            {'image': libimg.planet('Saturne'), 'label': 'Saturne', 'sublabel': 'Tes leçons'},
            {'image': libimg.planet('Pluton'), 'label': 'Pluton', 'sublabel': 'Tes mues'},
            {'image': libimg.planet('Neptune'), 'label': 'Neptune', 'sublabel': 'Tes visions'},
            {'image': libimg.planet('Lune'), 'label': 'Lune', 'sublabel': 'Ta mémoire'},
        ]
    elif product == 'synastry':
        slugs = SYNASTRY_SLUGS
        grid_tag = '✦ Vos 4 langages ✦'
        grid_title = 'Les planètes qui gouvernent votre lien'
        grid_cells = [
            {'image': libimg.planet('Soleil'), 'label': 'Soleil', 'sublabel': 'Votre identité'},
            {'image': libimg.planet('Lune'), 'label': 'Lune', 'sublabel': 'Votre émotion'},
            {'image': libimg.planet('Vénus'), 'label': 'Vénus', 'sublabel': 'Votre amour'},
            {'image': libimg.planet('Mars'), 'label': 'Mars', 'sublabel': 'Votre désir'},
        ]
    else:  # kabbale
        slugs = KABBALE_SLUGS
        grid_tag = '✦ Les 4 mondes ✦'
        grid_title = 'Les Sephiroth qui te structurent'
        grid_cells = [
            {'image': libimg.planet('Soleil'), 'label': 'Tiphereth', 'sublabel': 'La Beauté'},
            {'image': libimg.planet('Lune'), 'label': 'Yesod', 'sublabel': 'Le Fondement'},
            {'image': libimg.planet('Vénus'), 'label': 'Netzach', 'sublabel': 'La Victoire'},
            {'image': libimg.planet('Mercure'), 'label': 'Hod', 'sublabel': 'La Splendeur'},
        ]

    try:
        wrapped = _prepend_luxury_cover(
            pdf_bytes, prenom=prenom, subtitle=subtitle, cover_slug=slugs['cover'],
            grid_cells=grid_cells, grid_title=grid_title, grid_tag=grid_tag,
        )
    except Exception:
        # Fallback vers un slug garanti présent, sans grille
        wrapped = _prepend_luxury_cover(pdf_bytes, prenom=prenom, subtitle=subtitle,
                                        cover_slug=_SYNASTRY_FALLBACK_SLUG)
    wrapped = _append_luxury_ending(wrapped, prenom=prenom, ending_slug=slugs['ending'])
    return wrapped


# ─── Adaptateurs prêts à l'emploi ─────────────────────────────────

def generate_kabbale_pdf_luxury(
    first_name: str,
    birth_date_iso: str,
    tree_of_life: dict,
    ai_sections: dict | None = None,
) -> bytes:
    """Kabbale luxe = ancien PDF + cover luxe + fin Soléna.

    Si `ai_sections` est fourni (dict enrichi via enrich_report), il est
    passé au générateur legacy qui insère les paragraphes narratifs avant
    les rituels finaux.
    """
    from services.kabbale_pdf import generate_kabbale_pdf as _legacy
    inner = _legacy(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        tree_of_life=tree_of_life,
        ai_sections=ai_sections,
    )
    return apply_luxury_wrap(
        inner,
        prenom=first_name,
        subtitle='Ton Arbre de Vie kabbalistique',
        product='kabbale',
    )


def generate_astrocartographie_pdf_luxury(*args, **kwargs) -> bytes:
    """Astrocarto luxe = ancien PDF + cover luxe + fin Soléna. Passe-plat pour args."""
    from services.astrocartographie_pdf import generate_astrocartographie_pdf as _legacy
    inner = _legacy(*args, **kwargs)
    # Le premier arg positionnel ou 'first_name' contient le prénom
    prenom = kwargs.get('first_name') or (args[0] if args else 'Voyageuse')
    if isinstance(prenom, dict):
        prenom = prenom.get('first_name', 'Voyageuse')
    return apply_luxury_wrap(
        inner,
        prenom=str(prenom),
        subtitle='Où vivre ta meilleure vie ?',
        product='astrocarto',
    )


def generate_pack_karmique_pdf_luxury(
    first_name: str,
    birth_date_iso: str,
    karmic: dict,
    tree_of_life: dict,
    synthesis: dict,
    ai_sections: dict | None = None,
) -> bytes:
    """Pack Karmique luxe (89€) = ancien PDF ~40 pages + cover luxe + fin Soléna.

    Si `ai_sections` est fourni (dict enrichi via enrich_report), il est
    passé au générateur legacy qui insère les paragraphes narratifs avant
    la clôture Soléna.
    """
    from services.pack_karmique_pdf import generate_pack_karmique_pdf as _legacy
    inner = _legacy(
        first_name=first_name,
        birth_date_iso=birth_date_iso,
        karmic=karmic,
        tree_of_life=tree_of_life,
        synthesis=synthesis,
        ai_sections=ai_sections,
    )
    return apply_luxury_wrap(
        inner,
        prenom=first_name or 'Voyageuse',
        subtitle='Ton empreinte karmique · Ton Arbre de Vie',
        product='karmique',
    )
