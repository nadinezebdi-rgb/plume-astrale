"""Génère un échantillon PDF Thème Natal MANUSCRIT PRODUCTION (pipeline impression).

Diffère de `_gen_sample_natal_pdf.py` qui utilise `build_natal_pdf_v2` (moteur digital).
Ici on passe par `natal_pdf_adapter.generate_manuscrit_pdf` qui déclenche
`natal_manuscript_builder.build_natal_manuscript` + `print_book_renderer.render_book_pdf`
— soit exactement la chaîne utilisée en production pour la version imprimée A5.

Usage :
    cd /app/backend && python tests/_gen_sample_natal_manuscript.py
    cd /app/backend && python tests/_gen_sample_natal_manuscript.py --force

Produit :
    /app/backend/assets/theme_natal/sample_manuscript_production.pdf

Pipeline :
    1. Profil fictif (Clara, 14/07/1992, Paris) — même que _gen_sample_natal_pdf.py
    2. enrich_book_chapters (GPT) → dédicace, trio, maisons, année, ex-libris
    3. _gen_planet_analyses (GPT) → 11 narratifs planète-en-signe
    4. enrich_ex_libris_citation (GPT-6 Luna) → 60 mots ex-libris
    5. generate_manuscrit_pdf (production) → PDF A5 luxe
"""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except Exception:
    pass

# Réutilise la logique d'enrichissement du sample digital (même profil Clara,
# même cache GPT → pas de double appel LLM si déjà exécuté).
from tests._gen_sample_natal_pdf import (  # type: ignore
    PRENOM, BIRTH_DATE_ISO, BIRTH_DATA, PLANETS, ASPECTS, HOUSES_SIGNS,
    _gen_planet_analyses, _FR_KEY,
)
from services.natal_book_enrichment import enrich_book_chapters, enrich_ex_libris_citation
from services.natal_pdf_adapter import generate_manuscrit_pdf


# Mapping FR → EN pour alimenter planets_data_list attendu par l'adaptateur.
_SIGN_FR_TO_EN = {
    'Bélier': 'Aries', 'Taureau': 'Taurus', 'Gémeaux': 'Gemini',
    'Cancer': 'Cancer', 'Lion': 'Leo', 'Vierge': 'Virgo',
    'Balance': 'Libra', 'Scorpion': 'Scorpio', 'Sagittaire': 'Sagittarius',
    'Capricorne': 'Capricorn', 'Verseau': 'Aquarius', 'Poissons': 'Pisces',
}
_PLANET_FR_TO_EN = {
    'Soleil': 'Sun', 'Lune': 'Moon', 'Mercure': 'Mercury',
    'Vénus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter',
    'Saturne': 'Saturn', 'Uranus': 'Uranus',
    'Neptune': 'Neptune', 'Pluton': 'Pluto', 'Ascendant': 'Ascendant',
}


async def main() -> int:
    force = '--force' in sys.argv

    # ── 1) book_data
    print(f'→ enrich_book_chapters({PRENOM}, force={force})…')
    natal_data_for_book = {
        'prenom': PRENOM,
        'sun_sign': 'Cancer', 'moon_sign': 'Poissons', 'asc_sign': 'Vierge',
        'planets': [{'name': p['name'], 'sign': p['sign']} for p in PLANETS],
        'aspects': ASPECTS,
        'houses': [{'num': i + 1, 'sign': HOUSES_SIGNS[i], 'planets_in_house': []}
                   for i in range(12)],
    }
    book_data = await enrich_book_chapters(
        prenom=PRENOM, birth_data=BIRTH_DATA,
        natal_data=natal_data_for_book,
        force_refresh=force, language='fr',
    )
    print(f'   book_data._source = {book_data.get("_source", "none")}')

    # ── 2) 11 narratifs planète-en-signe (via le cache partagé)
    print(f'→ _gen_planet_analyses(force={force})…')
    planet_texts = await _gen_planet_analyses(force=force)
    print(f'   {len(planet_texts)} analyses')

    # ── 3) ex-libris 60 mots Luna
    print('→ enrich_ex_libris_citation (GPT-6 Luna)…')
    ex_libris_text = await enrich_ex_libris_citation(
        prenom=PRENOM, birth_data=BIRTH_DATA,
        sun_sign_fr='Cancer', moon_sign_fr='Poissons', asc_sign_fr='Vierge',
        force_refresh=force,
    )
    print(f'   ex_libris = {(ex_libris_text or "")[:80]}…')

    # ── 4) user_data (format attendu par generate_manuscrit_pdf)
    #   On fournit `ai_interpretations` avec les 11 clés FR pour activer
    #   le tier ULTRA (seuil ≥7 planètes).
    ai_interpretations = {
        '_source': 'sample-manuscript',
        'synthese_aspects': (
            book_data.get('aspects_harmonieux_body', '')
            + '\n\n' + book_data.get('aspects_tensions_body', '')
        ).strip(),
    }
    for p in PLANETS:
        ai_interpretations[_FR_KEY[p['name']]] = planet_texts.get(_FR_KEY[p['name']], '')

    user_data = {
        'prenom': PRENOM,
        'birth_date': BIRTH_DATE_ISO,
        'birth_time': f"{BIRTH_DATA['hour']}h{BIRTH_DATA['minute']:02d}",
        'birth_city': BIRTH_DATA.get('city'),
        'sun_sign': 'Cancer',
        'moon_sign': 'Poissons',
        'ascendant_sign': 'Vierge',
        'no_birth_time': False,
        'require_complete_book': True,
        'ai_interpretations': ai_interpretations,
        'enhanced_personal_analysis': {},
        'language': 'fr',
    }

    # ── 5) planets_data (format API v3 avec signes EN)
    planets_data_list = []
    for p in PLANETS:
        planets_data_list.append({
            'name': _PLANET_FR_TO_EN[p['name']],
            'sign': _SIGN_FR_TO_EN.get(p['sign'], p['sign']),
            'house': 1,
            'degree': 15.0,
        })

    # ── 6) aspects (format aspecting_planet / aspected_planet / type EN)
    _TYPE_FR_TO_EN = {
        'trigone': 'trine', 'carré': 'square', 'sextile': 'sextile',
        'opposition': 'opposition', 'conjonction': 'conjunction',
    }
    aspects_raw = []
    for a in ASPECTS:
        aspects_raw.append({
            'aspecting_planet': _PLANET_FR_TO_EN.get(a['planet1'], a['planet1']),
            'aspected_planet': _PLANET_FR_TO_EN.get(a['planet2'], a['planet2']),
            'type': _TYPE_FR_TO_EN.get(a['type'], a['type']),
            'orb': a['orb'],
        })

    houses_raw = [
        {'number': i + 1, 'sign': HOUSES_SIGNS[i], 'planets': []}
        for i in range(12)
    ]
    house_cusps_raw = [
        {'house': i + 1, 'sign': HOUSES_SIGNS[i], 'degree': (i * 7) % 30}
        for i in range(12)
    ]

    # ── 7) rendu PDF production
    print('→ generate_manuscrit_pdf (production pipeline)…')
    pdf_bytes = generate_manuscrit_pdf(
        user_data=user_data,
        planets_data=planets_data_list,
        book_data=book_data,
        aspects_raw=aspects_raw,
        houses_raw=houses_raw,
        house_cusps_raw=house_cusps_raw,
        referral_code='PLUME-CLARA-25',
        referral_link='https://plume-astrale.fr/parrainage/PLUME-CLARA-25',
        ex_libris_citation=ex_libris_text,
    )

    out_dir = ROOT / 'assets' / 'theme_natal'
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / 'sample_manuscript_production.pdf'
    out.write_bytes(pdf_bytes)
    print(f'OK ({len(pdf_bytes) / 1024:.1f} KB) → {out}')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
