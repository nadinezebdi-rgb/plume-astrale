"""routes/admin_preview_v3.py — endpoints admin pour prévisualiser le PDF Thème Natal V3
================================================================================

Nouveau pipeline Thème Natal V3 (préface AI + sommaire + 6 chapitres).
Permet au founder de pré-visualiser le PDF enrichi avant envoi aux clientes.

Route :
  GET /api/admin/preview/theme-natal-v3?prenom=X&date=YYYY-MM-DD&tier=ultra&ville=Paris
    → génère un PDF complet avec données réelles (astrology-api) + prose IA
      ou fallback démo si l'API Astro est absente.

Protection : require_admin (JWT admin Supabase).
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import Response

from routes.admin import require_admin

router = APIRouter(prefix="/admin/preview", tags=["admin-preview"])
logger = logging.getLogger(__name__)


# ─── Jeu de données de secours (fallback démo) ──────────────────────
def _demo_data(prenom: str) -> dict:
    """Fallback démo si l'API Astrology n'est pas disponible — garde la préface AI."""
    return {
        'user_data': {
            'prenom': prenom,
            'birth_date': '1990-09-15',
            'ascendant_sign': 'Lion',
            'ai_interpretations': {
                '_source': 'preview',
                'soleil': (
                    "Votre Soleil en Vierge dessine une précision rare — vous voyez ce que personne ne voit, "
                    "et vous rangez. Vos gestes ordinaires ont une précision d'orfèvre. Prendre soin, chez vous, "
                    "c'est une forme d'amour.\n\n"
                    "Vous arrivez à faire avec peu, à transformer l'ordinaire en beauté discrète. Cette terre "
                    "humide qui vous habite est fertile — tout ce que vous plantez pousse."
                ),
                'lune': (
                    "Votre Lune en Capricorne porte une sagesse ancienne — vous êtes née avec quelque chose à transmettre. "
                    "Les émotions vous atteignent lentement mais profondément.\n\n"
                    "Vous construisez vos tendresses comme on bâtit une maison : patiemment, pierre après pierre. "
                    "Vos silences ont du poids. Vos refuges sont des cabanes solides."
                ),
                'mercure': (
                    "Mercure en Vierge rend votre pensée affûtée, méticuleuse. Vous parlez juste. Vous écrivez clair. "
                    "Les détails ne vous échappent jamais — ils vous nourrissent.\n\n"
                    "Dans vos échanges, vous préférez la précision à la brillance. Vos mots sont comme des outils "
                    "qu'on choisit avant chaque tâche. Rien ne traîne, rien ne dépasse."
                ),
                'venus': (
                    "Vénus en Lion colore votre manière d'aimer d'une générosité ample, presque royale. "
                    "Vous aimez à voix haute. Vous offrez des gestes grands, des mots qui restent.\n\n"
                    "Dans vos amours, vous êtes la scène et le projecteur à la fois. Vous donnez beaucoup, "
                    "et vous attendez qu'on le remarque."
                ),
                'mars': (
                    "Mars en Scorpion donne à vos désirs une intensité secrète. Vous ne vous battez pas en surface — "
                    "vous transformez en profondeur.\n\n"
                    "Vos colères, quand elles sortent, laissent des traces. Vos désirs sont rarement légers : "
                    "ils vous engagent entièrement."
                ),
                'jupiter': (
                    "Jupiter en Taureau rétrograde élargit votre rapport au concret, à l'argent, à la beauté sensorielle. "
                    "Votre chance se construit lentement — mais elle dure.\n\n"
                    "La croissance, chez vous, prend le temps du végétal : une saison pour germer, une autre "
                    "pour fleurir. Pas de raccourci."
                ),
                'saturne': (
                    "Saturne en Capricorne vous met face à vos propres exigences. C'est la planète qui vous apprend "
                    "la souveraineté — pierre par pierre.\n\n"
                    "Ce que vous construisez est fait pour tenir. Vous n'avez pas peur du long terme ; c'est le "
                    "court terme qui vous paraît fragile."
                ),
                'uranus': (
                    "Uranus en Verseau fait de vous une pionnière discrète. Vous sentez l'avenir avant tout le monde — "
                    "vous ne l'imposez pas, vous le laissez venir.\n\n"
                    "Vos intuitions sur le futur se vérifient avec les années. Ne les taisez pas : elles sont une "
                    "boussole pour les autres."
                ),
                'neptune': (
                    "Neptune en Poissons amplifie votre monde intérieur. Vous rêvez éveillée. Vos intuitions sont "
                    "parfois des visions.\n\n"
                    "Attention à ne pas confondre vos brumes avec le réel. Prenez des notes de vos rêves — ils vous "
                    "parlent avec plus de justesse qu'ils ne le paraissent."
                ),
                'pluton': (
                    "Pluton en Scorpion creuse en vous un puits de transformation permanent. Vous mourrez à "
                    "vous-même plusieurs fois dans votre vie — et renaissez chaque fois plus vraie.\n\n"
                    "Ces mues sont douloureuses sur le moment, puis évidentes avec le recul. Ne les redoutez pas : "
                    "elles sont votre moteur profond."
                ),
                'ascendant': (
                    "Votre Ascendant Lion vous donne une présence lumineuse immédiate. Les autres vous remarquent — "
                    "même si l'intérieur reste pudique.\n\n"
                    "Vous entrez dans les pièces comme la lumière entre dans les salons. Cultivez cette présence : "
                    "c'est une bénédiction qui ne doit pas vous écraser."
                ),
                'synthese_aspects': (
                    "Deux dynamiques se dessinent dans votre thème. D'un côté, un trigone Soleil-Lune qui donne à "
                    "votre identité une cohérence rare entre ce que vous êtes et ce que vous ressentez.\n\n"
                    "De l'autre, un carré Vénus-Mars qui vous fait aimer avec une intensité qui frôle parfois le combat. "
                    "Ces deux forces se nourrissent : la douceur du trigone enveloppe la friction du carré, et le carré "
                    "empêche le trigone de devenir confortable. C'est ce frottement qui vous rend vivante."
                ),
            },
        },
        'planets_data': {
            'sun':      {'name': 'Sun',     'sign': 'virgo',       'house': 2, 'degree': 22.5},
            'moon':     {'name': 'Moon',    'sign': 'capricorn',   'house': 6, 'degree': 10.3},
            'mercury':  {'name': 'Mercury', 'sign': 'virgo',       'house': 2, 'degree': 8.1},
            'venus':    {'name': 'Venus',   'sign': 'leo',         'house': 1, 'degree': 15.8},
            'mars':     {'name': 'Mars',    'sign': 'scorpio',     'house': 4, 'degree': 3.2},
            'jupiter':  {'name': 'Jupiter', 'sign': 'taurus',      'house': 10, 'degree': 18.9, 'retrograde': True},
            'saturn':   {'name': 'Saturn',  'sign': 'capricorn',   'house': 6, 'degree': 25.0},
            'uranus':   {'name': 'Uranus',  'sign': 'aquarius',    'house': 7, 'degree': 5.5},
            'neptune':  {'name': 'Neptune', 'sign': 'pisces',      'house': 8, 'degree': 12.1},
            'pluto':    {'name': 'Pluto',   'sign': 'scorpio',     'house': 4, 'degree': 20.9},
            'ascendant': {'name': 'Ascendant', 'sign': 'leo',      'house': 1, 'degree': 7.0},
        },
        'aspects_raw': [
            {'aspecting_planet': 'Sun',     'aspected_planet': 'Moon',    'type': 'trine',       'orb': 2.1},
            {'aspecting_planet': 'Venus',   'aspected_planet': 'Mars',    'type': 'square',      'orb': 1.2},
            {'aspecting_planet': 'Jupiter', 'aspected_planet': 'Saturn',  'type': 'opposition',  'orb': 3.5},
            {'aspecting_planet': 'Mars',    'aspected_planet': 'Pluto',   'type': 'conjunction', 'orb': 4.0},
            {'aspecting_planet': 'Mercury', 'aspected_planet': 'Venus',   'type': 'sextile',     'orb': 3.1},
            {'aspecting_planet': 'Sun',     'aspected_planet': 'Mercury', 'type': 'conjunction', 'orb': 7.3},
            {'aspecting_planet': 'Mars',    'aspected_planet': 'Neptune', 'type': 'trine',       'orb': 2.4},
            {'aspecting_planet': 'Moon',    'aspected_planet': 'Saturn',  'type': 'conjunction', 'orb': 2.2},
        ],
        'cusps_raw': [
            {'house': i, 'sign': s, 'degree': (i * 7) % 30}
            for i, s in enumerate(
                ['Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn',
                 'Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini', 'Cancer'],
                start=1,
            )
        ],
    }


@router.get("/theme-natal-v3")
async def preview_theme_natal_v3(
    request: Request,
    prenom: str = Query('Amélie', description="Prénom pour la couverture"),
    date: Optional[str] = Query(None, description="Date de naissance ISO YYYY-MM-DD (facultatif)"),
    download: bool = Query(False, description="true → attachment; false → inline"),
    _admin: dict = Depends(require_admin),
):
    """Génère un PDF Thème Natal V3 (préface AI + sommaire + 6 chapitres) pour relecture.

    Utilise toujours des données de démo (jeu Amélie) pour la rapidité ; la préface
    AI reste réelle (Claude Sonnet via EMERGENT_LLM_KEY) ou fallback statique.
    """
    try:
        import os
        os.environ['USE_V2_NATAL_ENGINE'] = '1'
        from services.natal_pdf_adapter import generate_manuscrit_pdf

        d = _demo_data(prenom)
        d['user_data']['prenom'] = prenom
        if date:
            d['user_data']['birth_date'] = date

        pdf_bytes = generate_manuscrit_pdf(
            user_data=d['user_data'],
            planets_data=d['planets_data'],
            aspects_raw=d['aspects_raw'],
            house_cusps_raw=d['cusps_raw'],
        )
    except Exception as e:
        logger.exception('[admin_preview_v3] generation failed')
        raise HTTPException(status_code=500, detail=f"Génération impossible : {e}")

    disposition = (
        f'attachment; filename="apercu-theme-natal-v3-{prenom}.pdf"' if download
        else f'inline; filename="apercu-theme-natal-v3-{prenom}.pdf"'
    )
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': disposition, 'Cache-Control': 'no-store'},
    )
