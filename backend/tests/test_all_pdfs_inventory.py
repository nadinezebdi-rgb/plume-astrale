"""
test_all_pdfs_inventory.py — Audit UNITAIRE de chaque générateur PDF du site.
Exécution directe (pas pytest) :  python -m tests.test_all_pdfs_inventory

Teste chaque générateur avec les données standard "Marie, 14 avril 1990, 14h32, Paris".
N'envoie aucun email, ne déclenche aucun paiement, ne génère pas d'impression Lulu.
Mock des appels AI pour isoler la couche PDF.

Produit un rapport texte en fin d'exécution.
"""
from __future__ import annotations
import asyncio
import os
import sys
import time
import traceback
from pathlib import Path

# Unused import guards for mocks
from unittest.mock import patch, AsyncMock, MagicMock  # noqa

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

OUT_DIR = Path('/tmp/pdf_audit_2026_02')
OUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS = []

# ───── Donnée de test standard ──────────────────────────────────
MARIE = {
    'prenom': 'Marie',
    'first_name': 'Marie',
    'name': 'Marie',
    'dateNaissance': '1990-04-14',
    'birth_date': '1990-04-14',
    'heureNaissance': '14:32',
    'birth_time': '14:32',
    'birth_hour': 14, 'birth_minute': 32,
    'lieuNaissance': 'Paris, France',
    'birth_place': 'Paris, France',
    'city': 'Paris', 'country': 'France',
    'lat': 48.8566, 'lon': 2.3522, 'lng': 2.3522,
    'tz': 'Europe/Paris', 'timezone': 'Europe/Paris',
    'email': 'test-marie@plume-astrale.local',
    'no_birth_time': False,
}

FAKE_PLANETS_EN = {
    'sun':       {'sign': 'aries',     'degree': 24.3, 'house': 10},
    'moon':      {'sign': 'cancer',    'degree': 12.1, 'house': 1},
    'mercury':   {'sign': 'aries',     'degree': 8.7,  'house': 9},
    'venus':     {'sign': 'taurus',    'degree': 29.4, 'house': 11},
    'mars':      {'sign': 'capricorn', 'degree': 15.8, 'house': 7},
    'jupiter':   {'sign': 'cancer',    'degree': 2.2,  'house': 1},
    'saturn':    {'sign': 'capricorn', 'degree': 23.9, 'house': 7},
    'uranus':    {'sign': 'capricorn', 'degree': 8.5,  'house': 7},
    'neptune':   {'sign': 'capricorn', 'degree': 14.3, 'house': 7},
    'pluto':     {'sign': 'scorpio',   'degree': 17.6, 'house': 5},
    'ascendant': {'sign': 'cancer',    'degree': 5.0,  'house': 1},
}

FAKE_PLANETS = {
    'Soleil': {'sign': 'Bélier', 'degree': 24.3, 'house': 10},
    'Lune': {'sign': 'Cancer', 'degree': 12.1, 'house': 1},
    'Mercure': {'sign': 'Bélier', 'degree': 8.7, 'house': 9},
    'Vénus': {'sign': 'Taureau', 'degree': 29.4, 'house': 11},
    'Mars': {'sign': 'Capricorne', 'degree': 15.8, 'house': 7},
    'Jupiter': {'sign': 'Cancer', 'degree': 2.2, 'house': 1},
    'Saturne': {'sign': 'Capricorne', 'degree': 23.9, 'house': 7},
    'Uranus': {'sign': 'Capricorne', 'degree': 8.5, 'house': 7},
    'Neptune': {'sign': 'Capricorne', 'degree': 14.3, 'house': 7},
    'Pluton': {'sign': 'Scorpion', 'degree': 17.6, 'house': 5},
    'Ascendant': {'sign': 'Cancer', 'degree': 5.0, 'house': 1},
}

FAKE_AI_INTERPS = {
    # Clés attendues par _AI_KEY du natal_pdf_adapter (minuscules FR)
    'soleil':    "Marie, ton Soleil en Bélier éclaire une volonté neuve. "
                 "Un feu décidé qui n'attend pas la permission.",
    'lune':      "Ta Lune en Cancer protège une tendresse profonde. "
                 "Tu portes la mémoire des tiens comme un trésor.",
    'mercure':   "Mercure en Bélier te donne une parole directe. "
                 "Tu penses vite et tu dis tout haut ce que d'autres taisent.",
    'venus':     "Vénus en Taureau t'ancre dans un amour patient et sensuel. "
                 "Tu aimes la durée, les textures, les répétitions tendres.",
    'mars':      "Mars en Capricorne structure ton action en stratégie. "
                 "Tu avances par paliers, chaque effort compte.",
    'jupiter':   "Jupiter en Cancer t'inonde de ressources émotionnelles. "
                 "Ta générosité trouve son terreau dans l'intime.",
    'saturne':   "Saturne en Capricorne te structure pour les responsabilités. "
                 "Tu construis solide, pour la durée.",
    'uranus':    "Uranus en Capricorne te pousse à inventer dans la tradition. "
                 "Révolution lente mais inexorable.",
    'neptune':   "Neptune en Capricorne tempère ton imaginaire par la rigueur. "
                 "Rêves ancrés dans le réel.",
    'pluton':    "Pluton en Scorpion t'invite à mourir à ce qui ne vit plus. "
                 "Transformation sans retour.",
    'ascendant': "Ton Ascendant Cancer te fait aborder le monde par le soin. "
                 "On te lit souvent plus douce que ton Bélier intérieur.",
    'synthese_aspects': "Les aspects de ton thème dessinent un paysage de "
                       "contrastes assumés : la volonté solaire soutient la "
                       "tendresse lunaire sans jamais l'écraser.",
}

def _record(name, status, pages, elapsed_s, engine, path, note=''):
    RESULTS.append({
        'name': name, 'status': status, 'pages': pages,
        'elapsed_s': round(elapsed_s, 2), 'engine': engine,
        'path': str(path) if path else '', 'note': note,
    })
    icon = '✅' if status == 'OK' else '❌'
    print(f"{icon}  {name:<42s} | {status:6s} | {pages:>4} pg | {elapsed_s:5.1f}s | {engine:12s} | {note}")

def _pdf_pages(pdf_bytes: bytes) -> int:
    """Count PDF pages without pypdf dependency (fast)."""
    if not pdf_bytes: return 0
    # Count /Type /Page occurrences (not /Pages). Approximation suffisante pour l'audit.
    import re
    return len(re.findall(rb'/Type\s*/Page[^s]', pdf_bytes))

def _save_and_record(name, pdf_bytes, elapsed, engine, min_pages=1, note=''):
    try:
        if not pdf_bytes or len(pdf_bytes) < 1000:
            return _record(name, 'FAIL', 0, elapsed, engine, None, f'bytes trop petits ({len(pdf_bytes or b"")}B)')
        pages = _pdf_pages(pdf_bytes)
        safe = name.replace('/', '_').replace(' ', '_')[:60]
        out = OUT_DIR / f'{safe}.pdf'
        out.write_bytes(pdf_bytes)
        if pages < min_pages:
            return _record(name, 'WARN', pages, elapsed, engine, out, f'pages insuffisantes (<{min_pages})')
        return _record(name, 'OK', pages, elapsed, engine, out, note or f'{len(pdf_bytes)//1024}KB')
    except Exception as e:
        _record(name, 'FAIL', 0, elapsed, engine, None, f'exception save: {e!r}')

def _timed_sync(name, fn, engine, min_pages=1, note=''):
    t0 = time.time()
    try:
        pdf = fn()
    except Exception as e:
        return _record(name, 'FAIL', 0, time.time()-t0, engine, None, f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record(name, pdf, time.time()-t0, engine, min_pages, note)

async def _timed_async(name, coro_fn, engine, min_pages=1, note=''):
    t0 = time.time()
    try:
        pdf = await coro_fn()
    except Exception as e:
        return _record(name, 'FAIL', 0, time.time()-t0, engine, None, f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record(name, pdf, time.time()-t0, engine, min_pages, note)

# ───── Tests ─────────────────────────────────────────────────────

def test_01_apercu_natal():
    from services.apercu_pdf import build_apercu
    _timed_sync('01_apercu_natal_3p', lambda: build_apercu('natal'), 'ReportLab', min_pages=3)

def test_02_apercu_synastry():
    from services.apercu_pdf import build_apercu
    _timed_sync('02_apercu_synastry_3p', lambda: build_apercu('synastry'), 'ReportLab', min_pages=3)

def test_03_apercu_kabbale():
    from services.apercu_pdf import build_apercu
    _timed_sync('03_apercu_kabbale_3p', lambda: build_apercu('kabbale'), 'ReportLab', min_pages=3)

def test_04_apercu_astrocarto():
    from services.apercu_pdf import build_apercu
    _timed_sync('04_apercu_astrocarto_3p', lambda: build_apercu('astrocarto'), 'ReportLab', min_pages=3)

def test_05_apercu_karmique():
    from services.apercu_pdf import build_apercu
    _timed_sync('05_apercu_karmique_3p', lambda: build_apercu('karmique'), 'ReportLab', min_pages=3)

def test_06_pdf_preview_astrocarto():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('06_pdf_preview_astrocarto', lambda: _build_preview_pdf('astrocartographie'), 'ReportLab', min_pages=3)

def test_07_pdf_preview_kabbale():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('07_pdf_preview_kabbale', lambda: _build_preview_pdf('kabbale'), 'ReportLab', min_pages=3)

def test_08_pdf_preview_karma():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('08_pdf_preview_karma', lambda: _build_preview_pdf('karma-destin'), 'ReportLab', min_pages=3)

def test_09_pdf_preview_numero():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('09_pdf_preview_numero', lambda: _build_preview_pdf('numerologie'), 'ReportLab', min_pages=3)

def test_10_pdf_preview_natal():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('10_pdf_preview_natal', lambda: _build_preview_pdf('theme-natal'), 'ReportLab', min_pages=3)

def test_11_pdf_preview_synastrie():
    from routes.pdf_preview import _build_preview_pdf
    _timed_sync('11_pdf_preview_synastrie', lambda: _build_preview_pdf('synastrie'), 'ReportLab', min_pages=3)

def test_12_natal_digital_v2():
    """Thème Natal digital 24€ — via natal_pdf_adapter (natal_pdf_v2 ReportLab)."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    user = {**MARIE, 'ai_interpretations': {
        **{k: v for k, v in FAKE_AI_INTERPS.items()},
    }}
    _timed_sync('12_theme_natal_digital_ULTRA',
                lambda: generate_manuscrit_pdf(user, planets_data=FAKE_PLANETS_EN),
                'natal_pdf_v2 (ReportLab)', min_pages=30)

def test_13_natal_digital_legacy_no_ai():
    """Thème Natal digital sans IA (fallback 5 planètes)."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    _timed_sync('13_theme_natal_digital_LEGACY',
                lambda: generate_manuscrit_pdf(MARIE, planets_data=FAKE_PLANETS_EN),
                'natal_pdf_v2 (ReportLab)', min_pages=10)

def test_13b_natal_digital_no_birth_time():
    """Thème Natal digital sans heure de naissance."""
    from services.natal_pdf_adapter import generate_manuscrit_pdf
    user = {**MARIE, 'no_birth_time': True, 'ai_interpretations': {
        **{k: v for k, v in FAKE_AI_INTERPS.items()},
    }}
    _timed_sync('13b_theme_natal_sans_heure',
                lambda: generate_manuscrit_pdf(user, planets_data=FAKE_PLANETS_EN),
                'natal_pdf_v2 (ReportLab)', min_pages=10)

def test_14_karma_destin():
    from services.karma_destin_pdf import generate_karma_destin_pdf
    karmic_data = {
        'interpretations': [
            {'theme': 'noeud_nord', 'title': 'Nœud Nord en Capricorne',
             'text': 'Ta mission : structurer ta vie avec patience.'},
            {'theme': 'saturne', 'title': 'Retour de Saturne à 29 ans',
             'text': 'Un cap de maturité qui te consolide.'},
        ] * 3,
        'synthesis': 'Ton chemin karmique t\'invite à structurer.',
    }
    _timed_sync('14_karma_destin', lambda: generate_karma_destin_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        karmic_data=karmic_data, ai_sections=None,
    ), 'ReportLab', min_pages=5)

def test_15_kabbale_legacy():
    from services.kabbale_pdf import generate_kabbale_pdf
    tree = {
        'sephiroth': {
            'keter': {'planet': 'Soleil', 'strength': 0.9, 'interpretation': 'La couronne.'},
            'tiphereth': {'planet': 'Soleil', 'strength': 0.85, 'interpretation': 'La beauté.'},
            'yesod': {'planet': 'Lune', 'strength': 0.7, 'interpretation': 'La fondation.'},
            'malkuth': {'planet': 'Terre', 'strength': 0.6, 'interpretation': 'Le royaume.'},
        },
        'paths': [{'number': 11, 'letter': 'Aleph', 'from': 'keter', 'to': 'hochma',
                   'interpretation': 'Le souffle originel.'}] * 3,
        'daat': {'reveal': 'Un seuil silencieux au cœur de ton Arbre.'},
        'pillar_balance': {'severity': 3, 'mercy': 4, 'equilibrium': 3},
        'dominant_sephirah': 'tiphereth',
        'spiritual_focus': 'La beauté comme chemin.',
        'synthesis': 'Ton Arbre penche vers la lumière douce.',
    }
    # Force legacy en désactivant le flag v2
    os.environ.pop('USE_V2_KABBALE_ENGINE', None)
    _timed_sync('15_kabbale_legacy', lambda: generate_kabbale_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        tree_of_life=tree, ai_sections=None,
    ), 'ReportLab (legacy)', min_pages=5)

def test_15b_kabbale_v2():
    from services.kabbale_pdf import generate_kabbale_pdf
    tree = {
        'sephiroth': {
            'keter': {'planet': 'Soleil', 'strength': 0.9, 'interpretation': 'La couronne.'},
            'tiphereth': {'planet': 'Soleil', 'strength': 0.85, 'interpretation': 'La beauté.'},
            'yesod': {'planet': 'Lune', 'strength': 0.7, 'interpretation': 'La fondation.'},
            'malkuth': {'planet': 'Terre', 'strength': 0.6, 'interpretation': 'Le royaume.'},
        },
        'paths': [{'number': 11, 'letter': 'Aleph', 'interpretation': 'Le souffle originel.'}] * 3,
        'daat': {'reveal': 'Un seuil silencieux.'},
        'pillar_balance': {'severity': 3, 'mercy': 4, 'equilibrium': 3},
        'dominant_sephirah': 'tiphereth',
        'spiritual_focus': 'La beauté comme chemin.',
        'synthesis': 'Ton Arbre penche vers la lumière douce.',
    }
    os.environ['USE_V2_KABBALE_ENGINE'] = '1'
    _timed_sync('15b_kabbale_v2_chromium', lambda: generate_kabbale_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        tree_of_life=tree, ai_sections=None,
    ), 'Chromium/book_engine_v2', min_pages=5)
    os.environ.pop('USE_V2_KABBALE_ENGINE', None)

def test_16_astrocarto_legacy():
    from services.astrocartographie_pdf import generate_astrocartographie_pdf
    chosen_cities = [{
        'city': 'Lisbonne', 'country': 'Portugal', 'country_code': 'PT',
        'raw': {'lines_count': 2}, 'nearby_lines': [],
        'enriched': {
            'planet': 'Vénus', 'line_type': 'MC',
            'why': 'Terre d\'amour profond pour toi.',
            'promise': 'Ton Vénus y respire librement.',
            'opening_scene': 'Imagine-toi marchant au bord du Tage.',
            'daily_life': 'Un café au soleil, le linge au balcon.',
            'risks': 'La douceur peut t\'endormir.',
            'signature_cm': 'VNS/MC',
        },
    }] * 3
    bonus_cities = [{
        'city': 'Marrakech', 'country': 'Maroc', 'country_code': 'MA',
        'nearby_lines': [],
        'enriched': {'why': 'Terre de racines.', 'promise': 'Un Mars qui respire.'},
    }] * 2
    os.environ.pop('USE_V2_ASTROCARTO_ENGINE', None)
    _timed_sync('16_astrocarto_legacy', lambda: generate_astrocartographie_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        map_svg=None, chosen_cities=chosen_cities, bonus_cities=bonus_cities,
        synthesis_text='Trois lignes majeures te guident vers le Sud.',
    ), 'ReportLab (legacy)', min_pages=5)

def test_16b_astrocarto_v2():
    from services.astrocartographie_pdf import generate_astrocartographie_pdf
    chosen_cities = [{
        'city': 'Lisbonne', 'country': 'Portugal', 'country_code': 'PT',
        'raw': {'lines_count': 2}, 'nearby_lines': [],
        'enriched': {
            'planet': 'Vénus', 'line_type': 'MC', 'why': 'Terre d\'amour.',
            'promise': 'Ton Vénus y respire.', 'opening_scene': 'Imagine le Tage.',
            'daily_life': 'Un café au soleil.', 'risks': 'La douceur endort.',
            'signature_cm': 'VNS/MC',
        },
    }] * 3
    bonus_cities = [{'city': 'Marrakech', 'country': 'Maroc', 'country_code': 'MA',
                     'nearby_lines': [], 'enriched': {'why': 'Terre.', 'promise': 'Mars.'}}] * 2
    os.environ['USE_V2_ASTROCARTO_ENGINE'] = '1'
    _timed_sync('16b_astrocarto_v2_chromium', lambda: generate_astrocartographie_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        map_svg=None, chosen_cities=chosen_cities, bonus_cities=bonus_cities,
        synthesis_text='Trois lignes majeures te guident.',
    ), 'Chromium/book_engine_v2', min_pages=5)
    os.environ.pop('USE_V2_ASTROCARTO_ENGINE', None)

def test_17_numerologie():
    from services.numerologie_pdf import generate_numerologie_pdf
    num_data = {
        'life_path': {'number': 1, 'meaning': 'L\'initiateur solitaire.'},
        'expression': {'number': 5, 'meaning': 'La liberté comme oxygène.'},
        'soul_urge': {'number': 7, 'meaning': 'Chercheur silencieux.'},
        'personality': {'number': 9, 'meaning': 'L\'empathe universel.'},
        'personal_year': {'number': 3},
    }
    _timed_sync('17_numerologie', lambda: generate_numerologie_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        numerology_data=num_data,
    ), 'ReportLab', min_pages=5)

def test_18_compatibility():
    from services.compatibility_pdf_generator import generate_compatibility_pdf
    p1 = {'first_name': 'Marie', 'last_name': 'Durand',
          'day': 14, 'month': 4, 'year': 1990,
          'birth_date': '1990-04-14', 'birth_time': '14:32',
          'birth_place': 'Paris, France', 'lat': 48.86, 'lng': 2.35, 'tz': 'Europe/Paris'}
    p2 = {'first_name': 'Thomas', 'last_name': 'Léger',
          'day': 20, 'month': 7, 'year': 1988,
          'birth_date': '1988-07-20', 'birth_time': '09:15',
          'birth_place': 'Lyon, France', 'lat': 45.75, 'lng': 4.85, 'tz': 'Europe/Paris'}
    _timed_sync('18_compatibilite', lambda: generate_compatibility_pdf(
        person1=p1, person2=p2, question='Allons-nous construire ensemble ?',
    ), 'ReportLab', min_pages=5)

def test_19_fenetre_rencontre():
    from services.fenetre_rencontre_pdf import generate_fenetre_rencontre_pdf
    windows_data = [{
        'start_date': '2026-04-01', 'end_date': '2026-04-15', 'score': 0.82,
        'description': 'Une fenêtre vénusienne majeure.',
        'planet_transits': ['Vénus trigone Lune natale'],
    }] * 3
    _timed_sync('19_fenetre_rencontre', lambda: generate_fenetre_rencontre_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        windows_data=windows_data,
    ), 'ReportLab', min_pages=3)

def test_20_rencontres_ultime():
    from services.rencontres_ultime_pdf import generate_rencontres_ultime_pdf
    _timed_sync('20_rencontres_ultime', lambda: generate_rencontres_ultime_pdf(
        birth_date_iso='1990-04-14', first_name='Marie',
        m7_sign='Taureau', venus_sign='Taureau', mars_sign='Capricorne',
    ), 'ReportLab', min_pages=3)

def test_21_mediumnite():
    from services.mediumnite_pdf import generate_mediumnite_pdf
    tirage = {
        'first_name': 'Marie', 'question': 'Que me dit ton silence ?',
        'cards': [{'position': 'Présent', 'card_name': 'La Lune',
                   'interpretation': 'Un voile se lève.'}] * 10,
        'synthesis': 'Ton tirage parle de dévoilements.',
    }
    _timed_sync('21_mediumnite', lambda: generate_mediumnite_pdf(tirage), 'ReportLab', min_pages=3)

def test_22_tarot_synthese():
    from services.tarot_synthese_pdf import build_tarot_pdf
    data = {
        'cards': [{'name': 'Le Pape', 'position': 'Passé',
                   'interpretation': 'La transmission reçue.',
                   'reversed': False}] * 3,
        'synthesis': 'Ton tirage parle de transmission.',
    }
    _timed_sync('22_tarot_synthese', lambda: build_tarot_pdf(
        tirage_type='celtique', question='Dois-je changer de voie ?',
        domaine='carriere', data=data, prenom='Marie',
    ), 'ReportLab', min_pages=3)

def test_23_tarot_v2():
    from services.tarot_pdf_v2 import build_croix_celtique_pdf_v2
    _timed_sync('23_tarot_croix_v2', lambda: build_croix_celtique_pdf_v2(
        question='Que vient-il ?', prenom='Marie',
        tirage=[{'position': i, 'card': 'La Lune', 'reversed': False} for i in range(10)],
        synthese='Ton tirage est lumineux.',
    ), 'ReportLab', min_pages=5)

def test_24_premium():
    from services.premium_pdf_generator import generate_premium_pdf
    step = {
        'title': 'Les fondements',
        'subtitle': 'Soleil · Lune · Ascendant',
        'content': 'Ton socle astral est un dialogue entre le feu bélier '
                   'et la tendresse cancer. ' * 5,
        'phrase_clef': 'Avancer avec douceur.',
        'affirmation': 'Je choisis mon rythme.',
    }
    data = {
        'prenom': 'Marie', 'signe': 'Bélier', 'date_naissance': '14/04/1990',
        'steps': {
            'step_1_fondement':  step,
            'step_2_chemin_ame': {**step, 'title': 'Chemin de l\'âme'},
            'step_3_cycle':      {**step, 'title': 'Cycles actuels'},
            'step_4_schemas':    {**step, 'title': 'Schémas récurrents'},
            'step_5_projection': {**step, 'title': 'Projection 12 mois'},
        },
    }
    _timed_sync('24_premium', lambda: generate_premium_pdf(data), 'ReportLab', min_pages=5)

def test_25_pack_karmique():
    from services.pack_karmique_pdf import generate_pack_karmique_pdf
    karmic = {
        'interpretations': [
            {'theme': 'noeud_nord', 'title': 'Nœud Nord', 'text': 'Direction : structurer.'},
            {'theme': 'saturne', 'title': 'Saturne', 'text': 'Maturité à 29 ans.'},
        ] * 3,
        'synthesis': 'Ton chemin karmique.',
    }
    tree = {
        'sephiroth': {
            'keter': {'planet': 'Soleil', 'strength': 0.9, 'interpretation': 'Couronne.'},
            'tiphereth': {'planet': 'Soleil', 'strength': 0.85, 'interpretation': 'Beauté.'},
        },
        'daat': {'reveal': 'Un seuil.'},
        'paths': [], 'pillar_balance': {'severity': 3, 'mercy': 4, 'equilibrium': 3},
        'dominant_sephirah': 'tiphereth', 'spiritual_focus': 'Beauté.',
        'synthesis': 'Lumière douce.',
    }
    synthesis = {
        'synthesis': 'Un écrin complet d\'âme.',
        'axe_karmique_principal': 'Structurer avec patience.',
        'liens_karmiques': 'Tes nœuds parlent de maturation.',
        'invitation_finale': 'Avance avec confiance.',
    }
    _timed_sync('25_pack_karmique', lambda: generate_pack_karmique_pdf(
        first_name='Marie', birth_date_iso='1990-04-14',
        karmic=karmic, tree_of_life=tree, synthesis=synthesis,
    ), 'ReportLab', min_pages=5)

def test_26_synastrie():
    from services.synastrie_pdf_generator import generate_synastrie_pdf
    p1 = {**MARIE, 'last_name': 'Durand', 'planets': FAKE_PLANETS}
    p2 = {'first_name': 'Thomas', 'last_name': 'Léger', 'birth_date': '1988-07-20',
          'birth_time': '09:15', 'birth_place': 'Lyon, France',
          'lat': 45.75, 'lng': 4.85, 'tz': 'Europe/Paris', 'planets': FAKE_PLANETS}
    _timed_sync('26_synastrie', lambda: generate_synastrie_pdf(
        person1=p1, person2=p2,
    ), 'ReportLab', min_pages=5)

def test_27_lead_magnet():
    from services.lead_magnet_pdf import build_lead_magnet_pdf
    _timed_sync('27_lead_magnet', lambda: build_lead_magnet_pdf(
        email='marie@test.local', first_name='Marie',
        birth_date_iso='1990-04-14', birth_time='14:32',
        birth_place='Paris, France',
    ), 'ReportLab', min_pages=3)

async def test_28_gift_card():
    from services.gift_card_service import _generate_gift_pdf
    url = await _generate_gift_pdf(
        product_kind='theme_natal', first_name='Marie',
        birth_date='1990-04-14', birth_time='14:32',
        birth_place='Paris, France',
        recipient_email='beneficiaire@test.local',
        code='GIFT-TEST-2026',
    )
    # Le résultat est une URL — on vérifie le fichier généré sur disque
    from services.lead_magnet_pdf import LEAD_DIR
    try:
        files = sorted(LEAD_DIR.glob('gift_GIFT-TEST-2026_*.pdf'))
        if files:
            pdf_bytes = files[-1].read_bytes()
            _save_and_record('28_gift_card', pdf_bytes, 0.0, 'ReportLab (lead_magnet)', min_pages=1,
                             note=f'url={url[:50]}')
        else:
            _record('28_gift_card', 'FAIL', 0, 0, 'ReportLab', None, f'fichier non trouvé — url={url[:60]}')
    except Exception as e:
        _record('28_gift_card', 'FAIL', 0, 0, 'ReportLab', None, f'{e!r}')

def test_29_cercle_monthly():
    from services.cercle_monthly_report import generate_monthly_pdf
    _timed_sync('29_cercle_monthly', lambda: generate_monthly_pdf(
        first_name='Marie', sign_name='Bélier', sign_element='Feu',
        month_index=2, year=2026,
    ), 'ReportLab', min_pages=3)

# ───── Composer book_engine_v2 (Chromium) — orchestration DB-aware ─────
# Note : build_book_pdf_for_session requires a real session_id in Mongo.
# On ne peut pas le tester sans monter une session complète. On teste à la
# place le renderer directement avec un manuscrit synthétique.
async def test_30_book_engine_v2_renderer():
    """Teste services.book_engine_v2.render_manuscript_to_pdf_v2 avec un Manuscript stub."""
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    from services.book_engine_shared.domain import (
        Manuscript, Chapter, ChapterBlock, BlockKind, Edition, BirthData,
    )
    birth = BirthData(
        date_iso='1990-04-14', time_hhmm='14:32',
        city='Paris', country_code='FR',
        latitude=48.8566, longitude=2.3522,
    )
    def chapter(order, slug, title):
        return Chapter(
            slug=slug, title=title, kicker='Un sous-titre poétique.',
            roman_num='I' if order == 1 else 'II', order=order,
            blocks=[
                ChapterBlock(BlockKind.CHAPTER_OPENING, {
                    'tag': f'CHAPITRE {order}', 'title': title,
                    'kicker': 'Un sous-titre poétique.',
                }),
                ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {
                    'text': 'Marie, ton ciel natal te révèle un chemin singulier. '
                            'Ton Soleil en Bélier éclaire une volonté neuve, '
                            'et ta Lune en Cancer protège une tendresse profonde. ' * 2,
                }),
                ChapterBlock(BlockKind.PARAGRAPH, {
                    'text': 'Les planètes se parlent dans ton thème avec une '
                            'douceur qu\'on rencontre rarement. ' * 3,
                }),
            ] * 2,
        )
    manuscript = Manuscript(
        session_id='test_session_marie',
        user_email='marie@test.local', first_name='Marie',
        birth_data=birth, astro_data={},
        edition=Edition.NUMERIQUE, selected_add_ons=[],
        chapters=[chapter(1, 'ta_carte_du_ciel', 'Votre ciel de naissance'),
                  chapter(2, 'trio_identitaire', 'Les trois voix de votre identité')],
    )
    t0 = time.time()
    try:
        pdf = render_manuscript_to_pdf_v2(manuscript, profile='print')
    except Exception as e:
        traceback.print_exc()
        return _record('30_book_engine_v2_renderer', 'FAIL', 0, time.time()-t0,
                       'Chromium/book_engine_v2', None, f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record('30_book_engine_v2_renderer', pdf, time.time()-t0,
                     'Chromium/book_engine_v2', min_pages=5)

# ───── Composer — chaque addon individuellement (renderer-level) ─────
def _build_manuscript_with_addon(addon_slug: str, addon_title: str,
                                   addon_order: int, edition_val=None):
    """Construit un Manuscript stub : socle 2 chapitres + 1 addon."""
    from services.book_engine_shared.domain import (
        Manuscript, Chapter, ChapterBlock, BlockKind, Edition, BirthData,
    )
    birth = BirthData(
        date_iso='1990-04-14', time_hhmm='14:32',
        city='Paris', country_code='FR',
        latitude=48.8566, longitude=2.3522,
    )
    def _chapter(order, slug, title, roman):
        return Chapter(
            slug=slug, title=title, kicker='Un sous-titre.',
            roman_num=roman, order=order,
            blocks=[
                ChapterBlock(BlockKind.CHAPTER_OPENING, {
                    'tag': f'CHAPITRE {roman}', 'title': title, 'kicker': 'Un sous-titre.',
                }),
                ChapterBlock(BlockKind.PARAGRAPH_DROPCAP, {
                    'text': f'Marie, ce chapitre « {title} » te révèle une facette '
                            'nouvelle de ton ciel. ' * 3,
                }),
                ChapterBlock(BlockKind.PARAGRAPH, {
                    'text': 'Les planètes dessinent ici un paysage particulier. ' * 4,
                }),
            ],
        )
    return Manuscript(
        session_id=f'test_addon_{addon_slug}',
        user_email='marie@test.local', first_name='Marie',
        birth_data=birth, astro_data={},
        edition=edition_val or Edition.NUMERIQUE,
        selected_add_ons=[addon_slug],
        chapters=[
            _chapter(1, 'ta_carte_du_ciel', 'Votre ciel de naissance', 'I'),
            _chapter(2, 'trio_identitaire', 'Les trois voix', 'II'),
            _chapter(addon_order, addon_slug, addon_title, 'A'),
        ],
    )

ADDON_TESTS = [
    ('heure_retrouvee',   'L\'Heure Retrouvée',       103),
    ('etoiles_fixes',     'Étoiles Fixes',             104),
    ('symboles_sabiens',  'Symboles Sabiens',          105),
    ('arbre_de_vie',      'L\'Arbre de Vie',           100),
    ('astrocartographie', 'L\'Ailleurs qui t\'appelle', 101),
    ('karma_destin',      'Voyage Karmique',           102),
    ('maisons_detaillees','Les douze maisons',         106),
]

def test_31_addons_composer():
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    for idx, (slug, title, order) in enumerate(ADDON_TESTS, start=1):
        name = f'31.{idx}_composer_addon_{slug}'
        m = _build_manuscript_with_addon(slug, title, order)
        t0 = time.time()
        try:
            pdf = render_manuscript_to_pdf_v2(m, profile='print')
        except Exception as e:
            _record(name, 'FAIL', 0, time.time()-t0,
                    'Chromium/book_engine_v2', None,
                    f'{type(e).__name__}: {e!s}'[:120])
            continue
        _save_and_record(name, pdf, time.time()-t0,
                         'Chromium/book_engine_v2', min_pages=3)

def test_32_composer_pack_complet():
    """Pack Complet : 5 addons dans un seul manuscrit."""
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    from services.book_engine_shared.domain import (
        Manuscript, Chapter, ChapterBlock, BlockKind, Edition, BirthData,
    )
    birth = BirthData(date_iso='1990-04-14', time_hhmm='14:32',
                      city='Paris', country_code='FR',
                      latitude=48.8566, longitude=2.3522)
    def _c(order, slug, title, roman):
        return Chapter(
            slug=slug, title=title, kicker='Un sous-titre.',
            roman_num=roman, order=order,
            blocks=[
                ChapterBlock(BlockKind.CHAPTER_OPENING, {
                    'tag': f'CHAPITRE {roman}', 'title': title, 'kicker': 'Un sous-titre.'}),
                ChapterBlock(BlockKind.PARAGRAPH, {
                    'text': 'Marie, ce chapitre te révèle. ' * 10}),
            ],
        )
    socle = [_c(i, f'socle_{i}', f'Chapitre {i}', str(i)) for i in range(1, 4)]
    addons = [_c(100+i, slug, title, 'A') for i, (slug, title, _) in enumerate(ADDON_TESTS[:5])]
    manuscript = Manuscript(
        session_id='test_pack_complet', user_email='marie@test.local',
        first_name='Marie', birth_data=birth, astro_data={},
        edition=Edition.NUMERIQUE,
        selected_add_ons=[s for s, _, _ in ADDON_TESTS[:5]],
        chapters=socle + addons,
    )
    t0 = time.time()
    try:
        pdf = render_manuscript_to_pdf_v2(manuscript, profile='print')
    except Exception as e:
        return _record('32_composer_pack_complet', 'FAIL', 0, time.time()-t0,
                       'Chromium/book_engine_v2', None,
                       f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record('32_composer_pack_complet', pdf, time.time()-t0,
                     'Chromium/book_engine_v2', min_pages=10)

def test_33_composer_edition_brochee():
    """Thème Natal édition BROCHÉE (print)."""
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    from services.book_engine_shared.domain import Edition
    m = _build_manuscript_with_addon('arbre_de_vie', 'L\'Arbre de Vie', 100,
                                       edition_val=Edition.BROCHEE)
    t0 = time.time()
    try:
        pdf = render_manuscript_to_pdf_v2(m, profile='print')
    except Exception as e:
        return _record('33_composer_edition_brochee', 'FAIL', 0, time.time()-t0,
                       'Chromium/book_engine_v2', None,
                       f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record('33_composer_edition_brochee', pdf, time.time()-t0,
                     'Chromium/book_engine_v2', min_pages=5)

def test_34_composer_edition_reliee():
    """Thème Natal édition RELIÉE (print)."""
    from services.book_engine_v2 import render_manuscript_to_pdf_v2
    from services.book_engine_shared.domain import Edition
    m = _build_manuscript_with_addon('karma_destin', 'Voyage Karmique', 102,
                                       edition_val=Edition.RELIEE)
    t0 = time.time()
    try:
        pdf = render_manuscript_to_pdf_v2(m, profile='print')
    except Exception as e:
        return _record('34_composer_edition_reliee', 'FAIL', 0, time.time()-t0,
                       'Chromium/book_engine_v2', None,
                       f'{type(e).__name__}: {e!s}'[:120])
    _save_and_record('34_composer_edition_reliee', pdf, time.time()-t0,
                     'Chromium/book_engine_v2', min_pages=5)

# ───── Main ─────────────────────────────────────────────────────
async def main():
    print(f"\n{'='*110}\nAUDIT PDFS — Marie, 14 avril 1990, 14h32, Paris FR\n{'='*110}\n")
    print(f"{'Nom':<42s} | {'Statut':6s} | pages | {'temps':>6s} | {'Moteur':12s} | note")
    print('-' * 110)

    # Sync tests
    sync_tests = [
        test_01_apercu_natal, test_02_apercu_synastry, test_03_apercu_kabbale,
        test_04_apercu_astrocarto, test_05_apercu_karmique,
        test_06_pdf_preview_astrocarto, test_07_pdf_preview_kabbale,
        test_08_pdf_preview_karma, test_09_pdf_preview_numero,
        test_10_pdf_preview_natal, test_11_pdf_preview_synastrie,
        test_12_natal_digital_v2, test_13_natal_digital_legacy_no_ai,
        test_13b_natal_digital_no_birth_time,
        test_14_karma_destin, test_15_kabbale_legacy, test_15b_kabbale_v2,
        test_16_astrocarto_legacy, test_16b_astrocarto_v2,
        test_17_numerologie, test_18_compatibility, test_19_fenetre_rencontre,
        test_20_rencontres_ultime, test_21_mediumnite, test_22_tarot_synthese,
        test_23_tarot_v2, test_24_premium, test_25_pack_karmique,
        test_26_synastrie, test_27_lead_magnet, test_29_cercle_monthly,
    ]
    for t in sync_tests:
        try:
            t()
        except Exception as e:
            print(f'❌  TEST SETUP FAIL on {t.__name__}: {e!r}')
            _record(t.__name__, 'FAIL', 0, 0, '?', None, f'setup: {e!r}'[:80])

    # Async tests
    await test_28_gift_card()
    await test_30_book_engine_v2_renderer()
    test_31_addons_composer()
    test_32_composer_pack_complet()
    test_33_composer_edition_brochee()
    test_34_composer_edition_reliee()

    # Rapport final
    print('\n' + '=' * 110)
    print('RAPPORT FINAL')
    print('=' * 110)
    ok = sum(1 for r in RESULTS if r['status'] == 'OK')
    warn = sum(1 for r in RESULTS if r['status'] == 'WARN')
    fail = sum(1 for r in RESULTS if r['status'] == 'FAIL')
    print(f"✅ OK:   {ok}   ⚠️  WARN: {warn}   ❌ FAIL: {fail}   / {len(RESULTS)} tests\n")
    print(f"PDFs sauvegardés dans : {OUT_DIR}\n")

if __name__ == '__main__':
    asyncio.run(main())
