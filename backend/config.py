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

    # Astrology API
    ASTROLOGY_API_USER_ID = os.environ.get('ASTROLOGY_API_USER_ID', '')
    ASTROLOGY_API_KEY = os.environ.get('ASTROLOGY_API_KEY', '')
    ASTROLOGY_API_ACCESS_TOKEN = os.environ.get('ASTROLOGY_API_ACCESS_TOKEN', '')

    # Stripe (sk_test_emergent en dev, sk_live_... en prod sur Railway)
    STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')

    # LLM
    EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

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
            'name': 'Astro-Amour',
            'credits': 40,
            'bonus': 10,
            'amount': 12.99,
            'currency': 'eur',
            'badge': 'Le plus choisi',
            'tagline': '1 séance complète, ta prochaine fenêtre de rencontre décodée.',
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
    }

    SERVICE_COSTS = {
        'tarot_oui_non': 2,
        'tarot_marseille': 10,
        'tarot_celtique': 10,
        'tarologie': 10,
        'numerologie': 10,
        'cartographie': 60,
        'cartographie_premium': 60,
        'chat_astral': 10,       # 10 cr par question — grille "Special Lancement"
        'karma_destin': 20,
        'lecture_astrologique': 20,
        'lecture_tarot': 10,
        'synastrie': 20,
        'theme_natal_pdf': 20,
        'revolution_solaire': 20,
        'love_languages': 10,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
