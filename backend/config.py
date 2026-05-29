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
    PACKS = {
        # Packs generiques
        'starter': {'name': 'Starter', 'credits': 20, 'amount': 4.99, 'currency': 'eur'},
        'popular': {'name': 'Populaire', 'credits': 120, 'amount': 19.99, 'currency': 'eur'},
        'premium': {'name': 'Premium', 'credits': 350, 'amount': 49.00, 'currency': 'eur'},
        # Packs Chat IA dedies (2 credits/message)
        'chat_lueur': {'name': 'Lueur', 'credits': 20, 'amount': 4.99, 'currency': 'eur'},
        'chat_constellation': {'name': 'Constellation', 'credits': 60, 'amount': 12.99, 'currency': 'eur'},
        'chat_voie_lactee': {'name': 'Voie Lactee', 'credits': 150, 'amount': 24.99, 'currency': 'eur'},
    }

    SERVICE_COSTS = {
        'tarot_oui_non': 2,
        'tarot_marseille': 10,
        'tarot_celtique': 10,
        'tarologie': 10,
        'numerologie': 10,
        'cartographie': 60,
        'cartographie_premium': 60,
        'chat_astral': 3,
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
