"""Validation live GPT de la page Ex Libris (chapitre Signature Astrale).

Appelle réellement `enrich_book_chapters` avec un profil factice réaliste
pour vérifier le rendu éditorial du prompt :
- 110-140 mots
- Terminé par un verbe à l'infinitif
- Pas d'exclamation, pas de clichés "en tant que", pas de "Soléna" en toutes lettres
- Voix 2e personne du singulier
- Fluide et offrable

Coût : 1 appel GPT (~0.01$) + cache invalidé (force_refresh=True).

Usage :
    cd /app/backend && python scripts/validate_ex_libris_live.py
"""
from __future__ import annotations
import asyncio
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Charge .env comme le backend (uvicorn le fait automatiquement, pas python standalone)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except Exception:
    pass

from services.natal_book_enrichment import enrich_book_chapters


# Profil test : Amélie, 15/09/1990 14h30 Paris
PROFILE = {
    'prenom': 'Amélie',
    'birth_data': {
        'year': 1990, 'month': 9, 'day': 15,
        'hour': 14, 'minute': 30,
        'latitude': 48.8566, 'longitude': 2.3522,
        'timezone': 'Europe/Paris', 'city': 'Paris',
    },
    'natal_data': {
        'prenom': 'Amélie',
        'sun_sign': 'Vierge',
        'moon_sign': 'Capricorne',
        'asc_sign': 'Lion',
        'planets': [
            {'name': 'Soleil',  'sign': 'Vierge'},
            {'name': 'Lune',    'sign': 'Capricorne'},
            {'name': 'Mercure', 'sign': 'Vierge'},
            {'name': 'Vénus',   'sign': 'Lion'},
            {'name': 'Mars',    'sign': 'Scorpion'},
            {'name': 'Jupiter', 'sign': 'Taureau'},
            {'name': 'Saturne', 'sign': 'Capricorne'},
            {'name': 'Uranus',  'sign': 'Verseau'},
            {'name': 'Neptune', 'sign': 'Poissons'},
            {'name': 'Pluton',  'sign': 'Scorpion'},
        ],
        'aspects': [
            {'planet1': 'Soleil',  'planet2': 'Lune',    'type': 'trine',       'orb': 2.1},
            {'planet1': 'Vénus',   'planet2': 'Mars',    'type': 'square',      'orb': 1.2},
            {'planet1': 'Jupiter', 'planet2': 'Saturne', 'type': 'opposition',  'orb': 3.5},
        ],
        'houses': [
            {'num': 1, 'sign': 'Lion',       'planets_in_house': ['Vénus']},
            {'num': 2, 'sign': 'Vierge',     'planets_in_house': ['Soleil', 'Mercure']},
            {'num': 6, 'sign': 'Capricorne', 'planets_in_house': ['Lune', 'Saturne']},
            {'num': 10, 'sign': 'Taureau',   'planets_in_house': ['Jupiter']},
        ],
    },
}


_INFINITIFS_COMMUNS = {
    'habiter', 'oser', 'souvenir', 'vivre', 'avancer', 'écouter', 'écrire', 'aimer',
    'créer', 'danser', 'tenir', 'respirer', 'partir', 'apprendre', 'devenir',
    'laisser', 'offrir', 'retrouver', 'traverser', 'continuer', 'ouvrir', 'veiller',
    'accueillir', 'accepter', 'espérer', 'rêver', 'bâtir', 'guérir', 'reconnaître',
    'poser', 'commencer', 'faire', 'être', 'nommer', 'choisir',
}


def _count_words(text: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÖØ-öø-ÿ'’-]+\b", text or ''))


def _last_token(text: str) -> str:
    cleaned = re.sub(r'[.!?…"»"\s]+$', '', text or '')
    tokens = re.findall(r"[\wÀ-ÖØ-öø-ÿ'’-]+", cleaned)
    return tokens[-1].lower() if tokens else ''


def _looks_like_infinitif(token: str) -> bool:
    if not token:
        return False
    return token in _INFINITIFS_COMMUNS or token.endswith((
        'er', 'ir', 'oir', 're',
    ))


async def main() -> int:
    print('🔮 Validation Ex Libris live — appel GPT réel')
    print(f'   Profil : {PROFILE["prenom"]} ({PROFILE["natal_data"]["sun_sign"]}'
          f' · {PROFILE["natal_data"]["moon_sign"]} · {PROFILE["natal_data"]["asc_sign"]})')

    result = await enrich_book_chapters(
        prenom=PROFILE['prenom'],
        birth_data=PROFILE['birth_data'],
        natal_data=PROFILE['natal_data'],
        force_refresh=True,
    )

    source = result.get('_source', 'none')
    print(f'   Source : {source}')
    if source not in ('gpt', 'cache'):
        print(f'❌ Échec GPT : {result}')
        return 1

    ex_libris = str(result.get('ex_libris') or '').strip()
    if not ex_libris:
        print('❌ La clé `ex_libris` est absente du JSON GPT')
        return 2

    # Nettoyage HTML pour les contrôles
    text = re.sub(r'<[^>]+>', '', ex_libris)
    text = re.sub(r'\s+', ' ', text).strip()
    word_count = _count_words(text)
    last_word = _last_token(text)
    is_infinitif = _looks_like_infinitif(last_word)
    forbidden = [m.group(0) for m in re.finditer(
        r'\b(Soléna|en tant que|il est important|n\'oublie pas)\b', text,
    )]
    has_exclamation = '!' in text

    print()
    print('=' * 72)
    print('📜 Ex Libris généré')
    print('=' * 72)
    print(text)
    print('=' * 72)
    print()
    print(f'   Nombre de mots       : {word_count}  (cible 110-140)')
    print(f'   Dernier mot          : "{last_word}"  → infinitif ? {is_infinitif}')
    print(f'   Interdits détectés   : {forbidden if forbidden else "aucun"}')
    print(f'   Point d\'exclamation  : {"✗ présent" if has_exclamation else "✓ aucun"}')
    print()

    ok = (
        110 <= word_count <= 160
        and is_infinitif
        and not forbidden
        and not has_exclamation
    )
    if ok:
        print('✅ Validation OK — rendu conforme au cahier des charges')
        return 0
    print('⚠️  Validation partielle — contraintes à affiner')
    return 3


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
