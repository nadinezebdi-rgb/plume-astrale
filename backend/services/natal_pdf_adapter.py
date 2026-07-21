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


def generate_manuscrit_pdf(user_data: dict, planets_data=None, horoscope_data: dict = None) -> bytes:
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
    is_ultra = ai_planet_count >= 7
    planet_list = _ULTRA_PLANETS if is_ultra else _LEGACY_PLANETS

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
    for planet in planet_list:
        sign = _find_sign(planet) or 'Inconnu'
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

    natal_data = {
        'sun_sign': _find_sign('Soleil') or 'Cancer',
        'moon_sign': _find_sign('Lune') or 'Poissons',
        'ascendant_sign': _find_sign('Ascendant') or 'Vierge',
        'planets': planets,
        'synthese_aspects': synthese,
        'tier': 'ultra' if is_ultra else 'legacy',
    }

    try:
        return build_natal_pdf_v2(prenom=prenom, birth_date=birth_date, natal_data=natal_data)
    except Exception as e:
        logger.exception(f'[natal_pdf_v2] fallback to legacy: {e}')
        from services.pdf_generator import generate_manuscrit_pdf as legacy
        legacy_bytes = legacy(user_data=user_data, planets_data=planets_data, horoscope_data=horoscope_data)
        # Wrap luxe même sur le fallback legacy — jamais servir un PDF nu
        try:
            from services.pdf_luxury_wrap import apply_luxury_wrap
            return apply_luxury_wrap(
                legacy_bytes,
                prenom=prenom,
                subtitle='Ton ciel de naissance, dévoilé.',
                product='synastry',  # utilise slugs génériques valides
            )
        except Exception as we:
            logger.warning(f'[natal_pdf_adapter] luxe wrap on legacy failed: {we}')
            return legacy_bytes
