"""Adaptateur legacy → natal_pdf_v2.

Mode ULTRA (Option B) : si `user_data.ai_interpretations` contient
les 10 planètes + Ascendant + synthese_aspects (dict rempli par
`natal_ai_enrichment.enrich_natal_ultra`), le PDF affiche les 11 blocs
planétaires + une page synthèse d'aspects. Sinon fallback 5 planètes classiques.
"""
import logging
from services.natal_pdf_v2 import build_natal_pdf_v2

logger = logging.getLogger(__name__)

# Fallback rich content par signe — utilisé quand l'AI n'a rien remonté.
FALLBACK_SIGN = {
    'Bélier':     'un feu qui prend vite, tu déclenches, tu inities. Ton défi : la constance.',
    'Taureau':    'une nature stable et sensuelle. Tu ancres ce que les autres ne font qu\'imaginer.',
    'Gémeaux':    'un esprit curieux et fragmenté. Tu vis plusieurs vies dans une seule journée.',
    'Cancer':     'une sensibilité rare. Tu ressens avant de comprendre.',
    'Lion':       'un rayonnement naturel. Tu es née pour être vue — sans avoir besoin de le prouver.',
    'Vierge':     'une précision quasi sacrée. Tu remarques ce que personne ne voit.',
    'Balance':    'un besoin d\'harmonie viscéral. Tu pèses avant de trancher, tu embellis avant d\'agir.',
    'Scorpion':   'une profondeur magnétique. Rien ne t\'échappe, tout te transforme.',
    'Sagittaire': 'un horizon toujours plus loin. Tu chasses le sens, pas la sécurité.',
    'Capricorne': 'une patience de bâtisseuse. Tu construis lentement ce qui durera longtemps.',
    'Verseau':    'un esprit libre et visionnaire. Tu vois demain avant tout le monde.',
    'Poissons':   'un monde intérieur immense. Tu rêves éveillée, tu absorbes tout.',
}


def _sign_analysis(planet_name: str, sign: str) -> str:
    """Fallback statique par planète-signe si l'AI n'a pas fourni le texte."""
    intro = FALLBACK_SIGN.get(sign, f'une énergie unique en {sign}.')
    if planet_name == 'Soleil':
        return f'Ton Soleil en {sign} raconte {intro}\n\nC\'est le cœur de ton identité — ce que tu es en train de devenir, pas seulement ce que tu es.'
    if planet_name == 'Lune':
        return f'Ta Lune en {sign} révèle {intro}\n\nElle raconte tes réflexes émotionnels, tes tendresses cachées, ta manière secrète de te consoler.'
    if planet_name == 'Vénus':
        return f'Vénus en {sign} colore ta manière d\'aimer : {intro}\n\nDans tes relations, tu cherches ce que tu portes déjà en toi.'
    if planet_name == 'Mars':
        return f'Mars en {sign} donne à ton action {intro}\n\nC\'est le carburant sacré de tes désirs et de tes combats.'
    if planet_name == 'Ascendant':
        return f'Ton Ascendant en {sign} est le masque que ton âme a choisi : {intro}\n\nLes autres te perçoivent souvent ainsi — mais l\'intérieur est parfois tout autre.'
    if planet_name == 'Mercure':
        return f'Mercure en {sign} façonne ta pensée : {intro}\n\nC\'est ton style de parole, d\'écriture, de connexion.'
    if planet_name == 'Jupiter':
        return f'Jupiter en {sign} indique ta zone d\'expansion : {intro}\n\nOù tu grandis, où tu prends confiance, où la chance te trouve.'
    if planet_name == 'Saturne':
        return f'Saturne en {sign} te met face à {intro}\n\nC\'est la leçon que tu dois intégrer pour bâtir ta souveraineté.'
    if planet_name == 'Uranus':
        return f'Uranus en {sign} allume {intro}\n\nC\'est ta zone de rupture, de libération, d\'innovation.'
    if planet_name == 'Neptune':
        return f'Neptune en {sign} dissout {intro}\n\nOù tu rêves, où tu t\'inspires, où tu perds les repères.'
    if planet_name == 'Pluton':
        return f'Pluton en {sign} transforme {intro}\n\nC\'est l\'endroit de ta mutation profonde et non négociable.'
    return f'{planet_name} en {sign} : {intro}'


_ULTRA_PLANETS = [
    'Soleil', 'Lune', 'Mercure', 'Vénus', 'Mars',
    'Jupiter', 'Saturne', 'Uranus', 'Neptune', 'Pluton',
    'Ascendant',
]
_LEGACY_PLANETS = ['Soleil', 'Lune', 'Vénus', 'Mars', 'Ascendant']

_AI_KEY = {
    'Soleil': 'soleil', 'Lune': 'lune', 'Mercure': 'mercure',
    'Vénus': 'venus', 'Mars': 'mars', 'Jupiter': 'jupiter',
    'Saturne': 'saturne', 'Uranus': 'uranus',
    'Neptune': 'neptune', 'Pluton': 'pluton', 'Ascendant': 'ascendant',
}

_SIGN_EN_TO_FR = {
    'aries': 'Bélier', 'taurus': 'Taureau', 'gemini': 'Gémeaux',
    'cancer': 'Cancer', 'leo': 'Lion', 'virgo': 'Vierge',
    'libra': 'Balance', 'scorpio': 'Scorpion', 'sagittarius': 'Sagittaire',
    'capricorn': 'Capricorne', 'aquarius': 'Verseau', 'pisces': 'Poissons',
}

_EN_TO_KEY = {
    'Soleil': 'sun', 'Lune': 'moon', 'Mercure': 'mercury',
    'Vénus': 'venus', 'Mars': 'mars', 'Jupiter': 'jupiter',
    'Saturne': 'saturn', 'Uranus': 'uranus',
    'Neptune': 'neptune', 'Pluton': 'pluto',
    'Ascendant': 'ascendant',
}


def generate_manuscrit_pdf(user_data: dict, planets_data=None, horoscope_data: dict = None,
                            chart_png_bytes: bytes | None = None,
                            book_data: dict = None,
                            referral_code: str = None,
                            referral_link: str = None,
                            aspects_raw: list = None,
                            houses_raw: list = None,
                            house_cusps_raw: list = None) -> bytes:
    """DROP-IN REPLACEMENT du générateur legacy `generate_manuscrit_pdf`.

    Mode ULTRA activé si `user_data['ai_interpretations']` contient au moins
    7 planètes remplies (Soléna a répondu). Sinon fallback 5 planètes classiques.
    """
    prenom = user_data.get('prenom') or user_data.get('first_name') or user_data.get('name') or 'Voyageuse'
    birth_date = user_data.get('dateNaissance') or user_data.get('birth_date') or ''
    ai = user_data.get('ai_interpretations') or {}
    # Table planète→signe EN exposée par natal_ai_enrichment (fallback quand
    # /charts/natal ne retourne pas Uranus/Neptune/Pluton).
    ai_signs = ai.get('_signs_by_planet') or {}
    _PLANET_FR_TO_EN = {
        'Soleil': 'Sun', 'Lune': 'Moon', 'Mercure': 'Mercury',
        'Vénus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter',
        'Saturne': 'Saturn', 'Uranus': 'Uranus',
        'Neptune': 'Neptune', 'Pluton': 'Pluto',
        'Ascendant': 'Ascendant',
    }

    ai_planet_count = sum(1 for k in _AI_KEY.values() if ai.get(k))
    # Le fallback `api_v3_only` (quand GPT échoue) fournit les textes bruts
    # de l'API v3. Il faut aussi les considérer pour activer Ultra 11 planètes
    # (sinon on tombait en Legacy 5 planètes alors que la data v3 est complète).
    v3_raw_count = len(ai.get('_raw_v3_by_planet') or {})
    is_ultra = ai_planet_count >= 7 or v3_raw_count >= 7
    planet_list = _ULTRA_PLANETS if is_ultra else _LEGACY_PLANETS

    # §V audit marque Feb 2026 : sans heure de naissance, l'ascendant est faux
    # 11 fois sur 12 (parcourt 12 signes en 24h). On le retire explicitement
    # de la liste des planètes commentées.
    no_birth_time = bool(user_data.get('no_birth_time'))
    if no_birth_time:
        planet_list = [p for p in planet_list if p != 'Ascendant']

    def _find_sign(planet_name_fr: str) -> str:
        if planets_data:
            if isinstance(planets_data, dict):
                key = _EN_TO_KEY.get(planet_name_fr)
                if key and key in planets_data:
                    sign_en = (planets_data[key].get('sign') or '').lower()
                    if sign_en in _SIGN_EN_TO_FR:
                        return _SIGN_EN_TO_FR[sign_en]
                    if sign_en:
                        return sign_en.title()
            elif isinstance(planets_data, list):
                target_key = (_EN_TO_KEY.get(planet_name_fr) or '').lower()
                for p in planets_data:
                    p_name = (p.get('name', '') or p.get('planete', '')).lower()
                    if p_name == planet_name_fr.lower() or p_name == target_key:
                        sign_en = (p.get('sign') or p.get('signe') or '').lower()
                        if sign_en in _SIGN_EN_TO_FR:
                            return _SIGN_EN_TO_FR[sign_en]
                        if sign_en:
                            return sign_en.title()
        # Fallback : signes exposés par l'AI enrichment (parsés depuis /analysis/natal-report)
        planet_en = _PLANET_FR_TO_EN.get(planet_name_fr)
        if planet_en and planet_en in ai_signs:
            sign_en = ai_signs[planet_en].lower()
            if sign_en in _SIGN_EN_TO_FR:
                return _SIGN_EN_TO_FR[sign_en]
            if sign_en:
                return sign_en.title()
        # Dernier fallback : signes explicitement passés dans user_data (legacy)
        key_map = {
            'Soleil': ['sun_sign', 'signe', 'signe_solaire'],
            'Lune': ['moon_sign', 'signe_lune'],
            'Vénus': ['venus_sign', 'signe_venus'],
            'Mars': ['mars_sign', 'signe_mars'],
            'Ascendant': ['ascendant_sign', 'ascendant'],
        }
        for k in key_map.get(planet_name_fr, []):
            if user_data.get(k):
                return user_data[k]
        return ''

    planets = []
    ai_raw_v3 = ai.get('_raw_v3_by_planet') or {}
    _PLANET_FR_TO_EN_KEY = {  # pour matcher les clés v3
        'Soleil': 'Sun', 'Lune': 'Moon', 'Mercure': 'Mercury',
        'Vénus': 'Venus', 'Mars': 'Mars', 'Jupiter': 'Jupiter',
        'Saturne': 'Saturn', 'Uranus': 'Uranus',
        'Neptune': 'Neptune', 'Pluton': 'Pluto', 'Ascendant': 'Ascendant',
    }
    # ⚠️ Anti-slop v2 : on refuse de générer un PDF avec des positions
    # bidon. Si _find_sign() ne trouve rien pour une planète, on lève une
    # RuntimeError explicite plutôt que d'insérer un fallback trompeur
    # (ex. 'Inconnu' ou 'Cancer' hardcodé). L'appelant (theme_natal_oneshot_service)
    # doit valider planets_dict >=5 planètes AVANT d'appeler ce générateur.
    missing_signs: list[str] = []
    for planet in planet_list:
        sign = _find_sign(planet)
        if not sign:
            missing_signs.append(planet)
            continue
        ai_text = (ai.get(_AI_KEY[planet], '') or '').strip()
        if ai_text:
            analysis = ai_text
        else:
            # Fallback #1 : texte BRUT de l'API v3 (source de vérité, jamais IA générique)
            v3_key = _PLANET_FR_TO_EN_KEY.get(planet)
            v3_text = (ai_raw_v3.get(v3_key, '') or '').strip() if v3_key else ''
            if v3_text:
                analysis = v3_text
            else:
                # Fallback #2 (extrême — jamais atteint si l'API v3 répond) : texte statique
                analysis = _sign_analysis(planet, sign)
        planets.append({
            'name': planet,
            'sign': sign,
            'analysis': analysis,
        })

    synthese = (ai.get('synthese_aspects') or '').strip() if is_ultra else ''

    # ⚠️ Anti-slop v2 : si des planètes CORE (Soleil/Lune) manquent de signe,
    # on refuse net. Pour les autres (Vénus/Mars/…), on lève aussi car
    # afficher 'Inconnu' est trompeur pour un livre payé 24 EUR.
    if missing_signs:
        core_missing = [p for p in missing_signs if p in ('Soleil', 'Lune', 'Ascendant')]
        raise RuntimeError(
            f'natal_pdf_adapter: signes manquants pour {missing_signs!r} '
            f'(core_missing={core_missing!r}) — planets_data vide ou incomplet. '
            f'Refus de générer un PDF avec fallbacks trompeurs. '
            f'Vérifier astrology-api.io (crédits, 401, timeout) côté appelant.'
        )

    natal_data = {
        'sun_sign': _find_sign('Soleil'),
        'moon_sign': _find_sign('Lune'),
        # §V audit marque : ascendant vide si no_birth_time (sinon faux 11/12)
        'ascendant_sign': '' if no_birth_time else _find_sign('Ascendant'),
        'no_birth_time': no_birth_time,
        'planets': planets,
        'synthese_aspects': synthese,
        'enhanced_personal_analysis': user_data.get('enhanced_personal_analysis') or {},
        'houses': [] if no_birth_time else (user_data.get('houses') or []),
        'tier': 'ultra' if is_ultra else 'legacy',
    }

    # Détails positions (degré, maison, retrograde) depuis planets_data brut.
    # Permet au builder d'enrichir les titres H2 et les maisons.
    planets_detail: list[dict] = []
    _PLANET_EN_TO_FR = {v: k for k, v in _PLANET_FR_TO_EN.items()}
    if planets_data:
        iter_src = []
        if isinstance(planets_data, dict):
            iter_src = list(planets_data.values())
        elif isinstance(planets_data, list):
            iter_src = planets_data
        for p in iter_src:
            if not isinstance(p, dict):
                continue
            name_raw = (p.get('name') or p.get('planete') or '').strip()
            name_fr = _PLANET_EN_TO_FR.get(name_raw) or _PLANET_EN_TO_FR.get(name_raw.title()) or name_raw
            if not name_fr:
                continue
            sign_src = (p.get('sign') or p.get('signe') or '').strip()
            sign_fr = _SIGN_EN_TO_FR.get(sign_src.lower(), sign_src.title() if sign_src else '')
            planets_detail.append({
                'name': name_fr,
                'sign': sign_fr,
                'house': p.get('house') or p.get('house_number'),
                'degree': p.get('degree') or p.get('normDegree') or p.get('norm_degree'),
                'absolute_degree': p.get('fullDegree') or p.get('absolute_degree') or p.get('longitude'),
                'retrograde': bool(p.get('retrograde') or p.get('is_retro')),
            })
    if planets_detail:
        natal_data['planets_detail'] = planets_detail

    # Aspects normalisés (format API astrology-io v3)
    if aspects_raw:
        natal_data['aspects'] = aspects_raw

    # House cusps (format {num: {sign, degree}} ou liste 12 items)
    if house_cusps_raw:
        natal_data['house_cusps'] = house_cusps_raw
    if houses_raw:
        # Compat : certaines API retournent 'houses' avec sign+planets, pas de cuspide
        natal_data.setdefault('houses', houses_raw)

    # Feb 2026 — Nouveau pipeline unifié : book_engine_v2 Chromium print A5.
    # L'ancien natal_pdf_v2 (dark luxury) reste en fallback silencieux pour
    # éviter de casser la génération en cas de problème Chromium (prod sans
    # chromium installé → fallback nécessaire).
    try:
        import os
        if os.environ.get('USE_V2_NATAL_ENGINE', '1') == '1':
            from services.natal_manuscript_builder import build_natal_manuscript
            from services.book_engine_v2 import render_manuscript_to_pdf_v2
            # Génère la préface AI (Claude Sonnet) ou fallback statique.
            # On tente une boucle courte si on est en contexte sync (adapter appelé
            # depuis asyncio.to_thread dans theme_natal_oneshot_service).
            preface_blocks = None
            try:
                import asyncio
                from services.natal_preface_generator import generate_preface_blocks
                try:
                    _loop = asyncio.get_event_loop()
                    if _loop.is_running():
                        _loop = None
                except RuntimeError:
                    _loop = None
                if _loop is None:
                    _loop = asyncio.new_event_loop()
                    try:
                        preface_blocks = _loop.run_until_complete(generate_preface_blocks(
                            first_name=prenom,
                            sun_sign=natal_data.get('sun_sign') or '',
                            moon_sign=natal_data.get('moon_sign') or '',
                            asc_sign=natal_data.get('ascendant_sign') or '',
                            session_id=f'natal-preface-{prenom.lower()}',
                        ))
                    finally:
                        _loop.close()
            except Exception as _pe:
                logger.info(f'[natal_pdf_adapter] preface AI skipped (fallback static): {_pe}')
                preface_blocks = None
            manuscript = build_natal_manuscript(
                prenom=prenom, birth_date=birth_date, natal_data=natal_data,
                chart_png_bytes=chart_png_bytes,
                preface_blocks=preface_blocks,
            )
            pdf_bytes = render_manuscript_to_pdf_v2(manuscript, profile='print')
            try:
                from services.pipeline_metrics import track_pipeline_event
                track_pipeline_event(
                    'natal_pdf_generated', source='book_engine_v2_print',
                    tier=natal_data['tier'], bytes=len(pdf_bytes),
                    ai_planet_count=ai_planet_count,
                )
            except Exception:
                pass
            return pdf_bytes
    except Exception as be2_err:
        logger.warning(f'[natal_pdf_adapter] book_engine_v2 fail, fallback natal_pdf_v2: {be2_err}')

    try:
        pdf_bytes = build_natal_pdf_v2(prenom=prenom, birth_date=birth_date, natal_data=natal_data,
                                       chart_png_bytes=chart_png_bytes,
                                       book_data=book_data,
                                       referral_code=referral_code,
                                       referral_link=referral_link)
        # Track pipeline health
        try:
            from services.pipeline_metrics import track_pipeline_event
            track_pipeline_event(
                'natal_pdf_generated',
                source='natal_pdf_v2_dark_fallback_' + (
                    ai.get('_source') or 'none'
                ),
                tier=natal_data['tier'],
                bytes=len(pdf_bytes),
                ai_planet_count=ai_planet_count,
            )
        except Exception:
            pass

        return pdf_bytes

    except Exception as e:
        logger.exception(
            '[natal_pdf_adapter] enriched PDF rendering failed'
        )
        raise RuntimeError(
            'Le PDF enrichi n’a pas pu être rendu. '
            'Aucun PDF générique de remplacement ne sera livré.'
        ) from e
