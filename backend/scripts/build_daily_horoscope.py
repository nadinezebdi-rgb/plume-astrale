"""
Génère le PDF horoscope journalier POUR UN SIGNE DONNE avec les VRAIS transits du jour.

Différence avec build_12_horoscopes.py :
  - Récupère les transits du jour depuis astrology-api.io v3 (`/horoscope/sign/daily`)
  - Enrichit le contenu brut avec GPT-5.4 pour parler le ton "Soléna" (poétique, sans astérisque)
  - Injecte ce contenu dynamique dans le template PDF existant

Usage :
  python3 backend/scripts/build_daily_horoscope.py sagittaire
  python3 backend/scripts/build_daily_horoscope.py --all  # les 12 signes
"""
from __future__ import annotations
import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_settings  # noqa: F401 (side-effect load_dotenv)
from services.astrology_io_service import horoscope_sign
from scripts.build_12_horoscopes import SIGNES, build_pdf_for_signe

logger = logging.getLogger(__name__)

# Mapping slug FR → nom EN utilisé par l'API
_FR_TO_EN = {
    'belier': 'Aries', 'taureau': 'Taurus', 'gemeaux': 'Gemini',
    'cancer': 'Cancer', 'lion': 'Leo', 'vierge': 'Virgo',
    'balance': 'Libra', 'scorpion': 'Scorpio', 'sagittaire': 'Sagittarius',
    'capricorne': 'Capricorn', 'verseau': 'Aquarius', 'poissons': 'Pisces',
}


async def _enrich_with_solena(base_signe: dict, api_data: dict) -> dict:
    """Reformule les prédictions API en ton Soléna via GPT-5.4.
    Retourne un dict conforme au format attendu par build_pdf_for_signe."""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    api_key = os.environ.get('EMERGENT_LLM_KEY', '').strip()
    if not api_key:
        logger.warning('[daily_horoscope] EMERGENT_LLM_KEY manquante — fallback contenu statique')
        return base_signe

    # Extrait les areas de l'API dans un dict {area: {prediction, reasoning, rating}}
    areas = {}
    for a in api_data.get('life_areas', []):
        areas[a.get('area')] = {
            'prediction': a.get('prediction', ''),
            'reasoning': a.get('reasoning', ''),
            'rating': a.get('rating', 3),
        }

    overall = api_data.get('overall_theme', '')
    date_iso = api_data.get('date', '')

    system_prompt = (
        "Tu es Soléna, guide astrologique haut de gamme francophone. "
        "Tu réécris des prédictions brutes en langue poétique, tutoyée, à la 2ème personne, "
        "sans jamais utiliser d'astérisque (*), de markdown, d'emoji, ni de mots anglais. "
        "Ton style est intime, sensuel, spirituel — jamais mystique de bazar. "
        "Chaque phrase doit tenir en 1-2 lignes maximum. "
        "Renvoie STRICTEMENT un JSON valide, aucun texte en dehors."
    )

    user_prompt = f"""Voici les données astrologiques brutes du {date_iso} pour le signe {base_signe['nom']}, dont le maître planétaire est {'Jupiter' if base_signe['slug']=='sagittaire' else 'sa planète associée'}.

THÈME GLOBAL : {overall}

AMOUR : {areas.get('love',{}).get('prediction','')} — {areas.get('love',{}).get('reasoning','')}
CARRIÈRE : {areas.get('career',{}).get('prediction','')} — {areas.get('career',{}).get('reasoning','')}
SANTÉ : {areas.get('health',{}).get('prediction','')} — {areas.get('health',{}).get('reasoning','')}
IDENTITÉ : {areas.get('identity',{}).get('prediction','')} — {areas.get('identity',{}).get('reasoning','')}

Renvoie un JSON strict avec ces 7 clés (chaque valeur en français, style Soléna) :
{{
  "ouverture": "Une phrase d'ouverture (Aujourd'hui, ...) qui capte le thème du jour, 1 ligne",
  "energie": "L'énergie planétaire dominante en 2-3 phrases, avec mention des vrais transits (Uranus, Jupiter, etc.) tirés des reasoning ci-dessus",
  "amour": "Le message amour reformulé en ton Soléna, 1-2 phrases",
  "carriere": "Le message carrière reformulé en ton Soléna, 1-2 phrases",
  "bien_etre": "Le message santé/bien-être reformulé, 1-2 phrases",
  "guidance": "Une phrase guidance/mantra, poétique, 15-25 mots",
  "question": "Une question introspective en 1 phrase (peut inclure <br/> pour saut de ligne)"
}}"""

    chat = LlmChat(api_key=api_key, session_id=f'horoscope-{base_signe["slug"]}', system_message=system_prompt).with_model('openai', 'gpt-5.2')
    resp = await chat.send_message(UserMessage(text=user_prompt))
    text = (resp or '').strip()

    # Extraction JSON robuste (retire éventuels ```json wrappers)
    if '```' in text:
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    text = text.strip()

    try:
        enrichment = json.loads(text)
    except Exception as e:
        logger.warning(f'[daily_horoscope] JSON parse fail : {e}. Text: {text[:300]}')
        return base_signe

    # Merge dans base_signe (garde pierre/couleur/aromate/heure/chiffre statiques)
    enriched = dict(base_signe)
    for k in ('ouverture', 'energie', 'amour', 'carriere', 'bien_etre', 'guidance', 'question'):
        v = enrichment.get(k, '').strip()
        if v:
            # Purge éventuels astérisques (safety net)
            v = v.replace('*', '')
            enriched[k] = v
    return enriched


async def build_daily_for_sign(slug: str) -> Path:
    """Génère le PDF du jour pour un signe donné (slug FR)."""
    base = next((s for s in SIGNES if s['slug'] == slug), None)
    if not base:
        raise ValueError(f'Signe inconnu : {slug}. Valeurs valides : {[s["slug"] for s in SIGNES]}')

    en_sign = _FR_TO_EN.get(slug)
    if not en_sign:
        raise ValueError(f'Mapping FR→EN manquant pour {slug}')

    logger.info(f'[daily_horoscope] Fetch API pour {en_sign}...')
    api_data = await horoscope_sign(en_sign, 'daily', 'fr')
    if not api_data:
        logger.warning(f'[daily_horoscope] API a renvoyé None pour {en_sign} — fallback contenu statique')
        return build_pdf_for_signe(base)

    logger.info(f'[daily_horoscope] Enrichissement GPT pour {slug}...')
    enriched = await _enrich_with_solena(base, api_data)

    logger.info(f'[daily_horoscope] Génération PDF pour {slug}...')
    path = build_pdf_for_signe(enriched)
    return path


async def build_all() -> list[Path]:
    """Génère les 12 PDFs du jour en parallèle (rate limit friendly = séquentiel)."""
    paths = []
    for s in SIGNES:
        try:
            p = await build_daily_for_sign(s['slug'])
            paths.append(p)
            print(f'✓ {p.name}  ({p.stat().st_size // 1024} KB)')
        except Exception as e:
            print(f'✗ {s["slug"]} : {e}')
    return paths


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('slug', nargs='?', help='Slug FR du signe (belier, sagittaire, etc.)')
    parser.add_argument('--all', action='store_true', help='Génère les 12 signes')
    args = parser.parse_args()

    if args.all:
        asyncio.run(build_all())
    elif args.slug:
        p = asyncio.run(build_daily_for_sign(args.slug))
        print(f'✓ {p}')
        print(f'  URL prod : https://plume-astrale.fr/marketing/horoscopes/{p.name}')
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
