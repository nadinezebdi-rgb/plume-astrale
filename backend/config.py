"""Configuration centrale — toutes les variables d'environnement."""
import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')


class Settings:
    # Supabase
    SUPABASE_URL = os.environ['SUPABASE_URL']
    SUPABASE_SERVICE_ROLE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    SUPABASE_ANON_KEY = os.environ['SUPABASE_ANON_KEY']
    SUPABASE_JWT_SECRET = os.environ['SUPABASE_JWT_SECRET']
    SUPABASE_JWT_ALGORITHM = 'HS256'

    # Astrology API (astrology-api.io v3)
    ASTROLOGY_API_IO_KEY = os.environ.get('ASTROLOGY_API_IO_KEY', '')

    # Stripe (sk_test_emergent en dev, sk_live_... en prod sur Railway)
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

    # LLM
    EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

    # Credit packs (montants serveur — JAMAIS depuis le frontend)
    # Grille "Special Lancement" — 10 cr par question de chat, avec bonus offerts.
    PACKS = {
        'initiation': {
            'name': 'Initiation',
            'credits': 15,
            'bonus': 0,
            'amount': 4.99,
            'currency': 'eur',
            'tagline': "L'achat impulsif pour continuer la conversation.",
        },
        'astro_amour': {
            'name': 'Clarté',
            'credits': 50,
            'bonus': 10,
            'amount': 14.99,
            'currency': 'eur',
            'badge': 'Le plus choisi',
            'tagline': 'Ton Thème Natal complet (60 cr) accessible en 1 clic.',
        },
        'flammes_jumelles': {
            'name': 'Flammes Jumelles',
            'credits': 100,
            'bonus': 30,
            'amount': 29.99,
            'currency': 'eur',
            'badge': 'Meilleure valeur',
            'tagline': 'Explore ton thème en profondeur, ton karma, tes futures relations.',
        },
        # ═══════════════════════════════════════════════════════════
        # Produits one-shot (achats uniques, pas des crédits)
        # ═══════════════════════════════════════════════════════════
        'rencontres_ultime': {
            'name': 'Guide de Compatibilité Ultime & Calendrier de Rencontres',
            'credits': 0,   # one-shot, pas de crédit
            'bonus': 0,
            'amount': 29.99,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'rencontres_ultime',
            'tagline': 'Ton portrait partenaire ideal + 3 fenetres de rencontre + rituels energetiques.',
        },
        'kabbale_arbre_de_vie': {
            'name': 'Ton Arbre de Vie Kabbalistique',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 39.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'kabbale_arbre_de_vie',
            'tagline': "Les 10 Sephiroth + 22 chemins de ton theme natal — PDF 15 pages unique en francais.",
        },
        'numerologie_code': {
            'name': 'Ton Code Numérologique',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 19.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'numerologie_code',
            'tagline': 'Nombre de Destin + Expression + Année Personnelle — PDF 12 pages complet.',
        },
        'karma_destin_analysis': {
            'name': 'Analyse Karmique & Destinée',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 24.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'karma_destin_analysis',
            'tagline': 'Nœuds lunaires + Saturne + Chiron + Pluton — PDF 15 pages guide spirituel.',
        },
        'fenetre_rencontre_avancee': {
            'name': 'Fenêtres de Rencontre Avancées',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 29.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'fenetre_rencontre_avancee',
            'tagline': '3 fenêtres de rencontre calculées + synastrie optionnelle — PDF 10 pages.',
        },
        'pack_karmique_kabbale': {
            'name': 'Pack Karmique + Kabbale',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 89.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'pack_karmique_kabbale',
            'tagline': "Analyse karmique complete + Arbre de Vie + synthese croisee IA — PDF ~40 pages.",
        },
    }

    # Grille GaryVee — tous les services sont des multiples/fractions de 10 cr (unité = 1 question)
    SERVICE_COSTS = {
        # Produits d'appel — micro-conversion
        'tarot_oui_non': 5,          # demi-question — flash & indolore
        'archetype': 15,             # Ton Archetype — micro-produit viral 4,99€ equivalent
        # Chat — l'unite de base
        'chat_astral': 10,           # 1 question = 10 cr
        'lecture_tarot': 10,
        'love_languages': 10,
        # Services approfondis (3-4 questions)
        'tarot_marseille': 30,       # Lecture Tarot approfondie
        'tarot_celtique': 30,
        'tarologie': 30,
        'numerologie': 30,           # Année perso / Chemin de vie
        'lecture_astrologique': 40,  # Cycle actuel : transits, Mercure retrograde
        # Rapports premium (6 questions equivalentes)
        'theme_natal_pdf': 60,       # Theme Natal complet — le produit "phare"
        'cartographie': 60,
        'cartographie_premium': 60,
        'synastrie': 60,
        'revolution_solaire': 60,
        'karma_destin': 60,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
