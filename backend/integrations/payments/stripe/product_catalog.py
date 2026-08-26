"""
Catalogue centralisé des produits Plume Astrale pour la page Stripe Checkout.

Chaque entrée mappe un slug (celui envoyé dans `metadata.product` des routes)
vers les données affichées sur la page de paiement Stripe :
  - name         : titre principal (max 250 chars)
  - description  : sous-titre commercial (max 500 chars)
  - image_url    : cover 1080×1080 hébergée en HTTPS public (max 8 par produit)
  - submit_label : verbe du bouton de paiement Stripe (défaut : "auto")
  - custom_text  : message affiché sous le bouton "Payer"

Le fallback (produit inconnu) utilise `metadata.pack_name` comme name simple.

Toutes les images pointent vers le bucket public Supabase `library` déjà
utilisé par les PDFs — ce sont donc des URLs publiques stables.
"""
from __future__ import annotations
from typing import Dict, Any, Optional


_BUCKET = 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library'


def _tarot_img(slug: str) -> str:
    return f'{_BUCKET}/tarot/{slug}_1080.png'


# ═══════════════════════════════════════════════════════════════
# Catalogue produits
# ═══════════════════════════════════════════════════════════════
CATALOG: Dict[str, Dict[str, Any]] = {

    'lecture_complete': {
        'name': "Lecture Complète — Le Bundle Signature",
        'description': (
            "Ta cartographie céleste complète : Thème Natal détaillé + Karma & Destin + "
            "Numérologie + Kabbale (Arbre de Vie) + Tirage Symbolique. "
            "5 PDFs livrés instantanément par email, dans la voix de Soléna. "
            "Environ 90 pages personnalisées avec ta date et ton prénom."
        ),
        'image_url': _tarot_img('19_le_soleil'),
        'submit_label': 'auto',
        'custom_message': (
            "Livraison instantanée par email — sous 5 min. "
            "Pense à vérifier tes spams si tu ne le vois pas."
        ),
    },

    'karma_destin_analysis': {
        'name': "Karma & Destin — La Mémoire de ton Âme",
        'description': (
            "Ton axe karmique Nord/Sud, Saturne, Chiron, Pluton, karma générationnel "
            "et dates-clés de ta vie. PDF ~15 pages, dans la voix de Soléna."
        ),
        'image_url': _tarot_img('13_la_mort'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'numerologie_code': {
        'name': "Numérologie Sacrée — Ta Signature Vibratoire",
        'description': (
            "Chemin de vie, destinée, nombre d'âme et de personnalité, année personnelle, "
            "grille Lo-Shu et biorythmes. PDF ~15 pages personnalisées par Soléna."
        ),
        'image_url': _tarot_img('10_la_roue_de_fortune'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'kabbale_arbre_de_vie': {
        'name': "Kabbale & Arbre de Vie — La Lecture Sacrée",
        'description': (
            "Tes 3 séphiroth dominantes, ton chemin kabbalistique, la Gematria de ton "
            "nom et les 3 lettres hébraïques qui vibrent avec toi. PDF luxe ~13 pages."
        ),
        'image_url': _tarot_img('17_l_etoile'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'pack_karmique_kabbale': {
        'name': "Pack Karmique — Le Duo Signature (Karma + Kabbale)",
        'description': (
            "L'union des deux lectures les plus profondes : ton empreinte karmique "
            "(Nord/Sud, dates-clés) croisée avec ton Arbre de Vie kabbalistique. "
            "PDF ~14 pages, dans la voix de Soléna."
        ),
        'image_url': _tarot_img('03_l_imperatrice'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'mediumnite': {
        'name': "Tirage Symbolique — La Croix qui te Parle",
        'description': (
            "Un tirage complet à 5 arcanes pour éclairer tes dynamiques intérieures : "
            "ce qui t'anime, ce qui te freine, tes ressources. Une lecture symbolique, "
            "comme matière à réflexion. PDF illustré, ~12 pages."
        ),
        'image_url': _tarot_img('02_la_papesse'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'croix_celtique': {
        'name': "Croix Celtique — 10 Arcanes qui Répondent",
        'description': (
            "Ta question posée à la Croix Celtique : 10 cartes tirées, interprétées "
            "position par position, puis 7 chapitres narratifs Soléna pour relier les "
            "fils. PDF luxe ~23 pages."
        ),
        'image_url': _tarot_img('01_le_bateleur'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'theme_natal_pdf_oneshot': {
        'name': "Thème Natal Illustré — Ta Carte du Ciel",
        'description': (
            "Ta carte du ciel de naissance dessinée, expliquée maison par maison, "
            "planète par planète. PDF luxe illustré ~30 pages."
        ),
        'image_url': _tarot_img('19_le_soleil'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'theme_natal': {
        'name': "Thème Natal Illustré — Ta Carte du Ciel",
        'description': (
            "Ta carte du ciel de naissance dessinée, expliquée maison par maison, "
            "planète par planète. PDF luxe illustré ~30 pages."
        ),
        'image_url': _tarot_img('19_le_soleil'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'synastrie_oneshot': {
        'name': "Synastrie — La Danse de Deux Thèmes",
        'description': (
            "L'analyse croisée de deux thèmes natals : compatibilités, tensions, "
            "aspects karmiques du couple. PDF ~20 pages."
        ),
        'image_url': _tarot_img('06_les_amoureux'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'synastrie': {
        'name': "Synastrie — La Danse de Deux Thèmes",
        'description': (
            "L'analyse croisée de deux thèmes natals : compatibilités, tensions, "
            "aspects karmiques du couple. PDF ~20 pages."
        ),
        'image_url': _tarot_img('06_les_amoureux'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'fenetre_rencontre_avancee': {
        'name': "Fenêtre de Rencontre — Le Calendrier de l'Amour",
        'description': (
            "Les 12 prochains mois cartographiés : quand tes transits favorisent la "
            "rencontre amoureuse, quand ils invitent à la solitude fertile. PDF ~15 pages."
        ),
        'image_url': _tarot_img('06_les_amoureux'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'fenetre_rencontre': {
        'name': "Fenêtre de Rencontre — Le Calendrier de l'Amour",
        'description': (
            "Les 12 prochains mois cartographiés : quand tes transits favorisent la "
            "rencontre amoureuse, quand ils invitent à la solitude fertile. PDF ~15 pages."
        ),
        'image_url': _tarot_img('06_les_amoureux'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'astrocartographie': {
        'name': "Astrocartographie — Les Lieux qui te Ressemblent",
        'description': (
            "La carte du monde superposée à ton thème natal : où tes lignes planétaires "
            "favorisent la carrière, l'amour, la spiritualité, le repos. PDF ~18 pages."
        ),
        'image_url': _tarot_img('07_le_chariot'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'consultation_ultime': {
        'name': "Consultation Ultime — L'Analyse Signature de Soléna",
        'description': (
            "La lecture la plus complète : thème natal + karma + kabbale + numérologie "
            "+ tarot natal + astrocartographie, avec 8 chapitres narratifs Soléna. "
            "Le grand œuvre astrologique."
        ),
        'image_url': _tarot_img('19_le_soleil'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'duo_completion': {
        'name': "Duo Découverte — 2 Lectures Combinées",
        'description': (
            "Deux lectures Plume Astrale au prix de l'audace : combine ce qui te parle "
            "le plus (Karma, Kabbale, Numéro, Tarot ou Lecture Symbolique)."
        ),
        'image_url': _tarot_img('10_la_roue_de_fortune'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'duo_decouverte': {
        'name': "Duo Découverte — 2 Lectures Combinées",
        'description': (
            "Deux lectures Plume Astrale au prix de l'audace : combine ce qui te parle "
            "le plus (Karma, Kabbale, Numéro, Tarot ou Lecture Symbolique)."
        ),
        'image_url': _tarot_img('10_la_roue_de_fortune'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },

    'trio_decouverte': {
        'name': "Trio Découverte — 3 Lectures Combinées",
        'description': (
            "Trois lectures Plume Astrale pour une exploration en profondeur : la "
            "triple perspective Karma + Kabbale + Numérologie (au choix)."
        ),
        'image_url': _tarot_img('10_la_roue_de_fortune'),
        'submit_label': 'auto',
        'custom_message': "Livraison instantanée par email — vérifie tes spams.",
    },
}


def get_product_info(slug: Optional[str], fallback_name: str = 'Plume Astrale') -> Dict[str, Any]:
    """Retourne un dict {name, description, image_url, custom_message, submit_label}
    à partir d'un slug produit. Fallback minimal si slug inconnu."""
    entry = CATALOG.get(slug or '')
    if not entry:
        return {
            'name': fallback_name,
            'description': None,
            'image_url': None,
            'submit_label': 'auto',
            'custom_message': "Livraison instantanée par email — vérifie tes spams.",
        }
    return entry
