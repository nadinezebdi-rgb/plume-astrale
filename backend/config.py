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
    # Resend (envoi d'emails transactionnels)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
    # Credit packs (montants serveur — JAMAIS depuis le frontend)
    # Grille "Special Lancement" — 10 cr par question de chat, avec bonus offerts.
    PACKS = {
        'comete': {
            'name': 'Comète',
            'credits': 30,
            'bonus': 0,
            'amount': 7.99,
            'currency': 'eur',
            'tagline': "L'étincelle rapide pour poser tes premières questions.",
        },
        'nebuleuse': {
            'name': 'Nébuleuse',
            'credits': 80,
            'bonus': 0,
            'amount': 17.99,
            'currency': 'eur',
            'badge': 'Le plus choisi',
            'tagline': 'Ton Thème Natal complet (60 cr) + 2 questions à Plume.',
        },
        'constellation': {
            'name': 'Constellation',
            'credits': 180,
            'bonus': 0,
            'amount': 34.99,
            'currency': 'eur',
            'badge': 'Meilleure valeur',
            'tagline': 'Explore ton thème en profondeur, ton karma, tes relations.',
        },
        'voie_lactee': {
            'name': 'Voie Lactée',
            'credits': 350,
            'bonus': 0,
            'amount': 59.99,
            'currency': 'eur',
            'tagline': "L'expérience complète, sans jamais compter.",
        },
        # ═══════════════════════════════════════════════════════════
        # Produits one-shot (achats uniques, pas des crédits)
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
        # ═══════════════════════════════════════════════════════════
        # Thème Natal one-shot 29€ — flagship (2026-02 Gary Vee refonte)
        'theme_natal_pdf_oneshot': {
            'name': 'Thème Natal Complet',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 29.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'theme_natal_pdf_oneshot',
            'tagline': 'Ton portrait astrologique complet — 11 planètes, ascendant, maisons, aspects — PDF luxe 20 à 40 pages, voix Soléna.',
        },
        # Trio Découverte 79€ — bundle Thème Natal + Numérologie + Kabbale (économie 8€)
        'trio_decouverte': {
            'name': 'Trio Découverte',
            'credits': 0,
            'bonus': 0,
            'amount': 79.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'trio_decouverte',
            'tagline': "Ton Thème Natal + ta Numérologie + ton Arbre de Vie Kabbale — 3 PDFs livrés en 5 minutes. Économise 12€.",
        },
        # Duo Complémentaire 50€ — cross-sell post-Thème Natal (Numérologie + Kabbale, économie 8€)
        'duo_completion': {
            'name': 'Duo Complémentaire',
            'credits': 0,
            'bonus': 0,
            'amount': 50.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'duo_completion',
            'tagline': "Complète ton Thème Natal — Numérologie sacrée + Arbre de Vie Kabbale. Économise 8€ (vs 58€ séparés).",
        },
        # Hyperpremium anchor 149€ — n'est presque jamais vendu, sert d'ancrage
        'consultation_ultime': {
            'name': 'Consultation Ultime — Soléna à tes côtés',
            'credits': 0,
            'bonus': 0,
            'amount': 149.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'consultation_ultime',
            'tagline': "Thème Natal 40 pages + chat illimité 24h + lecture personnalisée enregistrée par Soléna — expérience complète sans limite.",
        },
        # ═══════════════════════════════════════════════════════════
        'rencontres_ultime': {
            'name': 'Guide Ultime du Partenaire Idéal + Calendrier de Rencontres',
            'credits': 0,   # one-shot, pas de crédit
            'bonus': 0,
            'amount': 34.99,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'rencontres_ultime',
            'tagline': 'Portrait de ton partenaire idéal (traits physiques, psychologiques, valeurs) + 3 fenêtres de rencontre calculées + rituels énergétiques — PDF 25 pages.',
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
        'astrocartographie': {
            'name': 'Astrocartographie — Où vivre ta meilleure vie',
            'credits': 0,
            'bonus': 0,
            'amount': 49.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'astrocartographie',
            'tagline': "Carte du monde de tes lignes planétaires + analyse de 3 villes que tu choisis + 2 destinations bonus recommandées par Soléna — PDF ~18 pages.",
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
            'tagline': 'Transits amoureux + phases lunaires + synastrie optionnelle — PDF 10 pages.',
        },
        'lecture_complete': {
            'name': 'Lecture Complète de ton Ciel — Bundle 97€',
            'credits': 0,   # one-shot
            'bonus': 0,
            'amount': 97.00,
            'currency': 'eur',
            'kind': 'oneshot',
            'product': 'lecture_complete',
            'tagline': 'Thème Natal + Fenêtres 2026 + Lecture Karmique + Analyse des liens + Cercle Soléna 90j.',
        },
    }

    # Grille F500 2026-02 — refonte cohérence + réduction "rapports premium" pour forcer conversion PDF
    SERVICE_COSTS = {
        # Produits d'appel — micro-conversion
        'tarot_oui_non': 3,          # micro flash — indolore
        'archetype': 10,             # Ton Archetype — micro-produit
        # Chat — nouvelle unité de base (F500: 10→5 pour augmenter la fréquence d'usage)
        'chat_astral': 5,            # 1 question = 5 cr
        'lecture_tarot': 5,
        'love_languages': 5,
        # Services approfondis (F500: 30→15)
        'tarot_marseille': 15,       # Lecture Tarot approfondie
        'tarot_celtique': 15,
        'tarologie': 15,
        'numerologie': 15,           # Année perso / Chemin de vie
        'lecture_astrologique': 20,  # Cycle actuel : transits, Mercure retrograde
        # Rapports premium (F500: 60→REMOVED — force PDF Signature)
        # Ces IDs restent pour compat, mais coût aligné pour ne PLUS concurrencer les PDF
        # (l'utilisateur est incité vers le PDF Signature via UI)
        'theme_natal_pdf': 15,       # 5 pages flash — descendu de 80→30→15 (F500 2026-02)
        'cartographie': 30,
        'cartographie_premium': 30,
        'synastrie': 30,
        'revolution_solaire': 30,
        'karma_destin': 30,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
