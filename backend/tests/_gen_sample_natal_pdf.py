"""Génère un échantillon PDF Thème Natal avec enrichissement AI RÉEL.

Usage :
    cd /app/backend && python tests/_gen_sample_natal_pdf.py
    cd /app/backend && python tests/_gen_sample_natal_pdf.py --force   # invalide le cache GPT

Produit :
    /app/backend/assets/theme_natal/sample_lot1_50pages.pdf

Pipeline :
    1. Profil fictif (Clara, 14/07/1992, Paris)
    2. enrich_book_chapters (GPT-5.4) → dédicace, trio, maisons, année, ex-libris
    3. _gen_planet_analyses (GPT-5.4) → 11 narratifs planète-en-signe
    4. build_natal_pdf_v2 → PDF luxe
"""
from __future__ import annotations
import asyncio
import json
import os
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

from services.natal_pdf_v2 import build_natal_pdf_v2
from services.natal_book_enrichment import enrich_book_chapters, enrich_ex_libris_citation
from services.natal_ai_enrichment import _call_gpt, _parse_json_response


# ────────────────────────────────────────────────────────────────────────
# Profil fictif réaliste
# ────────────────────────────────────────────────────────────────────────
PRENOM = 'Clara'
BIRTH_DATE_ISO = '1992-07-14'
BIRTH_DATA = {
    'year': 1992, 'month': 7, 'day': 14,
    'hour': 15, 'minute': 42,
    'latitude': 48.8566, 'longitude': 2.3522,
    'timezone': 'Europe/Paris', 'city': 'Paris',
}

PLANETS = [
    {'name': 'Soleil',   'sign': 'Cancer'},
    {'name': 'Lune',     'sign': 'Poissons'},
    {'name': 'Mercure',  'sign': 'Cancer'},
    {'name': 'Vénus',    'sign': 'Lion'},
    {'name': 'Mars',     'sign': 'Taureau'},
    {'name': 'Jupiter',  'sign': 'Scorpion'},
    {'name': 'Saturne',  'sign': 'Verseau'},
    {'name': 'Uranus',   'sign': 'Capricorne'},
    {'name': 'Neptune',  'sign': 'Capricorne'},
    {'name': 'Pluton',   'sign': 'Scorpion'},
    {'name': 'Ascendant','sign': 'Vierge'},
]

ASPECTS = [
    {'planet1': 'Lune',    'planet2': 'Jupiter',  'type': 'trigone',     'orb': 2.4},
    {'planet1': 'Soleil',  'planet2': 'Saturne',  'type': 'carré',       'orb': 1.8},
    {'planet1': 'Vénus',   'planet2': 'Neptune',  'type': 'sextile',     'orb': 3.1},
    {'planet1': 'Mars',    'planet2': 'Pluton',   'type': 'trigone',     'orb': 2.0},
    {'planet1': 'Mercure', 'planet2': 'Uranus',   'type': 'opposition',  'orb': 4.2},
]

HOUSES_SIGNS = ['Vierge','Balance','Scorpion','Sagittaire','Capricorne','Verseau',
                'Poissons','Bélier','Taureau','Gémeaux','Cancer','Lion']


# ────────────────────────────────────────────────────────────────────────
# Génération des narratifs planète-en-signe via GPT (une seule requête)
# ────────────────────────────────────────────────────────────────────────
_PLANET_SYSTEM = """Tu écris pour Plume Astrale, maison française d'astrologie éditoriale.
Style : entre Christiane Singer, Fabienne Verdier, et Anne Dufourmantelle.
Voix : intime, sensorielle, jamais moralisatrice, jamais new-age caricatural.
Registre : soutenu littéraire — pas de jargon astro, pas d'anglicismes.
Tu tutoies toujours la personne.
Interdits : « en tant que », « il est important de », « n'oublie pas que », émojis.
"""

_PLANET_CACHE = ROOT / 'cache' / 'natal_sample_planets'
_PLANET_CACHE.mkdir(parents=True, exist_ok=True)


def _planet_cache_key() -> str:
    import hashlib
    sig = PRENOM + '|' + '|'.join(f"{p['name']}:{p['sign']}" for p in PLANETS)
    return 'sample-' + hashlib.sha256(sig.encode()).hexdigest()[:16]


async def _gen_planet_analyses(force: bool = False) -> dict[str, str]:
    """Un seul appel GPT retournant JSON {clef_fr: narratif_html}."""
    key = _planet_cache_key()
    cache_file = _PLANET_CACHE / f'{key}.json'
    if not force and cache_file.exists():
        try:
            return json.loads(cache_file.read_text('utf-8'))
        except Exception:
            pass

    planet_lines = '\n'.join(f"- {p['name']} en {p['sign']}" for p in PLANETS)
    prompt = f"""Personne : {PRENOM}
Trio : Soleil Cancer · Lune Poissons · Ascendant Vierge
Planètes à analyser :
{planet_lines}

Pour chaque planète ci-dessus, écris une analyse personnalisée en voix Plume Astrale.
Chaque analyse comprend EXACTEMENT 2 paragraphes séparés par <br/><br/>.
Longueur par analyse : 90 à 130 mots au total.
Ancre les images dans le réel (sensations, gestes, saisons, mémoire).
Pas de listes, pas de titres. Prose directe au tutoiement.

Retourne STRICTEMENT un JSON valide (aucun texte hors JSON, pas de fence markdown) avec exactement ces clés :

{{
  "soleil":    "...",
  "lune":      "...",
  "mercure":   "...",
  "venus":     "...",
  "mars":      "...",
  "jupiter":   "...",
  "saturne":   "...",
  "uranus":    "...",
  "neptune":   "...",
  "pluton":    "...",
  "ascendant": "..."
}}
"""
    resp = await _call_gpt(_PLANET_SYSTEM, prompt,
                            session_id=f'sample-planets-{key}', timeout_s=120.0)
    if not resp:
        raise RuntimeError('GPT ne répond pas pour les narratifs planétaires')
    parsed = _parse_json_response(resp)
    if not parsed:
        raise RuntimeError(f'JSON invalide (raw: {resp[:200]!r})')
    # Nettoyage : les analyses dans natal_pdf_v2 attendent du \n\n (pas de <br/>)
    cleaned = {}
    for k, v in parsed.items():
        if not isinstance(v, str):
            continue
        txt = v.strip()
        txt = re.sub(r'<br\s*/?>\s*<br\s*/?>', '\n\n', txt, flags=re.IGNORECASE)
        txt = re.sub(r'<br\s*/?>', '\n', txt, flags=re.IGNORECASE)
        txt = re.sub(r'</?p>', '\n\n', txt, flags=re.IGNORECASE)
        txt = re.sub(r'</?[a-z][^>]*>', '', txt, flags=re.IGNORECASE)  # strip html
        txt = re.sub(r'\n{3,}', '\n\n', txt).strip()
        cleaned[k.lower()] = txt
    cache_file.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), 'utf-8')
    return cleaned


# ────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────
_FR_KEY = {
    'Soleil': 'soleil', 'Lune': 'lune', 'Mercure': 'mercure',
    'Vénus': 'venus', 'Mars': 'mars', 'Jupiter': 'jupiter',
    'Saturne': 'saturne', 'Uranus': 'uranus',
    'Neptune': 'neptune', 'Pluton': 'pluton', 'Ascendant': 'ascendant',
}


async def main() -> int:
    force = '--force' in sys.argv

    # ── 1) book_data (dédicace + élément + modalité + trio + maisons + année + ex-libris)
    print(f'→ enrich_book_chapters({PRENOM}, force={force})… (peut prendre 60-120s au premier run)')
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
    src = book_data.get('_source', 'none')
    print(f'   book_data._source = {src}')
    if src not in ('gpt', 'cache'):
        print(f'   ⚠️  enrichissement livre incomplet (_source={src}) — rendu dégradé.')

    # ── 2) narratifs planète-en-signe
    print(f'→ _gen_planet_analyses(force={force})… (peut prendre 30-60s au premier run)')
    planet_texts = await _gen_planet_analyses(force=force)
    print(f'   {len(planet_texts)} analyses générées : {sorted(planet_texts.keys())}')

    # ── 3) narratif Ex-Libris 60 mots via GPT-6 Luna
    print(f'→ enrich_ex_libris_citation (GPT-6 Luna, force={force})…')
    ex_libris_text = await enrich_ex_libris_citation(
        prenom=PRENOM, birth_data=BIRTH_DATA,
        sun_sign_fr='Cancer', moon_sign_fr='Poissons', asc_sign_fr='Vierge',
        force_refresh=force,
    )
    if ex_libris_text:
        print(f'   ex_libris_text = {ex_libris_text[:80]}…')
    else:
        print(f'   ⚠️  Luna n\'a pas répondu — fallback citation statique.')

    # ── 4) construction du natal_data pour le PDF
    planets_with_analysis = []
    for p in PLANETS:
        key = _FR_KEY[p['name']]
        planets_with_analysis.append({
            'name': p['name'], 'sign': p['sign'],
            'analysis': planet_texts.get(key, ''),
        })

    natal_data = {
        'sun_sign': 'Cancer',
        'moon_sign': 'Poissons',
        'ascendant_sign': 'Vierge',
        'no_birth_time': False,
        'tier': 'ultra',
        'planets': planets_with_analysis,
        'synthese_aspects': (
            book_data.get('aspects_harmonieux_body', '')
            + '\n\n' + book_data.get('aspects_tensions_body', '')
        ).strip(),
        'houses': [{'num': i + 1, 'sign': HOUSES_SIGNS[i], 'planets_in_house': []}
                   for i in range(12)],
        'enhanced_personal_analysis': {},
    }

    # ── 5) rendu PDF
    print('→ build_natal_pdf_v2…')
    pdf_bytes = build_natal_pdf_v2(
        prenom=PRENOM,
        birth_date=BIRTH_DATE_ISO,
        natal_data=natal_data,
        chart_png_bytes=None,
        book_data=book_data,
        referral_code='PLUME-CLARA-25',
        referral_link='https://plume-astrale.fr/parrainage/PLUME-CLARA-25',
        ex_libris_citation=ex_libris_text,
        birth_time_fr=f"{BIRTH_DATA['hour']}h{BIRTH_DATA['minute']:02d}",
        birth_place=BIRTH_DATA.get('city'),
    )
    out_dir = ROOT / 'assets' / 'theme_natal'
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / 'sample_lot1_50pages.pdf'
    out.write_bytes(pdf_bytes)
    print(f'OK ({len(pdf_bytes) / 1024:.1f} KB) → {out}')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
