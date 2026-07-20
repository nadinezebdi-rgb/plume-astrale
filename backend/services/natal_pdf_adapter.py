"""
Adaptateur : convertit les user_data legacy vers le format natal_pdf_v2.

Permet à toutes les routes existantes (/api/pdf/generate, /api/pdf/pro-horoscope,
/api/natal/essentials, etc.) d'utiliser automatiquement le PDF Thème Natal
"livre de luxe" sans changer leur interface d'entrée.
"""
from __future__ import annotations
import logging
from services.natal_pdf_v2 import build_natal_pdf_v2

logger = logging.getLogger(__name__)

# Fallback rich content par signe — utilisé quand l'API v3 n'a pas fourni
# d'analyse détaillée. Court et évocateur (max 3 phrases).
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
    """Fabrique une analyse par défaut si l'API v3 n'a rien remonté."""
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
    return f'{planet_name} en {sign} : {intro}'


def generate_manuscrit_pdf(user_data: dict, planets_data: list = None, horoscope_data: dict = None) -> bytes:
    """DROP-IN REPLACEMENT du générateur legacy `generate_manuscrit_pdf`.

    Convertit les données legacy vers le format natal_pdf_v2 et retourne
    les bytes du PDF style livre de luxe.
    """
    prenom = user_data.get('prenom') or user_data.get('first_name') or user_data.get('name') or 'Voyageuse'
    birth_date = user_data.get('dateNaissance') or user_data.get('birth_date') or ''

    # Récupérer les signes depuis user_data ou planets_data
    def _find_sign(planet_name: str) -> str:
        # Chercher dans planets_data (liste de dicts)
        if planets_data:
            for p in planets_data:
                if p.get('name', '').lower() == planet_name.lower() or p.get('planete', '').lower() == planet_name.lower():
                    return p.get('sign') or p.get('signe') or ''
        # Chercher dans user_data pré-calculé
        key_map = {
            'Soleil': ['sun_sign', 'signe', 'signe_solaire'],
            'Lune': ['moon_sign', 'signe_lune'],
            'Vénus': ['venus_sign', 'signe_venus'],
            'Mars': ['mars_sign', 'signe_mars'],
            'Ascendant': ['ascendant_sign', 'ascendant'],
        }
        for k in key_map.get(planet_name, []):
            if user_data.get(k):
                return user_data[k]
        return ''

    planets = []
    for planet in ['Soleil', 'Lune', 'Vénus', 'Mars', 'Ascendant']:
        sign = _find_sign(planet) or 'Inconnu'
        planets.append({
            'name': planet,
            'sign': sign,
            'analysis': _sign_analysis(planet, sign),
        })

    natal_data = {
        'sun_sign': _find_sign('Soleil') or 'Cancer',
        'moon_sign': _find_sign('Lune') or 'Poissons',
        'ascendant_sign': _find_sign('Ascendant') or 'Vierge',
        'planets': planets,
    }

    try:
        return build_natal_pdf_v2(prenom=prenom, birth_date=birth_date, natal_data=natal_data)
    except Exception as e:
        logger.exception(f'[natal_pdf_v2] fallback to legacy: {e}')
        # Fallback vers l'ancien générateur en cas d'erreur imprévue
        from services.pdf_generator import generate_manuscrit_pdf as legacy
        return legacy(user_data=user_data, planets_data=planets_data, horoscope_data=horoscope_data)
