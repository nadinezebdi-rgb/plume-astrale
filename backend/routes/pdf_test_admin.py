"""
routes/pdf_test_admin.py — endpoints admin pour prévisualiser chaque PDF
avec des données factices avant impression prestige.

Route :
  GET /api/admin/pdf-test/{product}?first_name=Léa&partner_name=Adrien
    → génère et renvoie le PDF complet du produit avec des données factices,
      permettant de vérifier le rendu (dorure du prénom, sommaire numéroté,
      couvertures illustrées) avant d'aller en imprimerie.

Aucune authentification stricte pour l'instant (le path /admin/ est déjà
signalé — à protéger via auth si expose publique). Le PDF est régénéré
à chaque appel (pas de cache) pour refléter les changements de code en dev.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import Response

from routes.admin import require_admin

router = APIRouter(prefix="/admin/pdf-test", tags=["admin-pdf-test"])
logger = logging.getLogger(__name__)


async def _log_generation(admin_email: str, product: str, first_name: str,
                           partner_name: Optional[str], tier: Optional[str],
                           pdf_size: int, ip: str) -> None:
    """Trace la génération dans Mongo — non-bloquant, silencieux si Mongo indispo."""
    try:
        from services.mongo import get_db  # type: ignore
        db = get_db()
        if db is not None:
            await db.admin_pdf_test_logs.insert_one({
                'admin_email': admin_email,
                'product': product,
                'first_name': first_name,
                'partner_name': partner_name,
                'tier': tier,
                'pdf_size': pdf_size,
                'ip': ip,
                'created_at': datetime.now(timezone.utc).isoformat(),
            })
    except Exception as e:
        logger.debug(f'[admin_pdf_test] Mongo log skipped: {e}')


def _fixture(product: str, first_name: str, partner_name: Optional[str] = None,
              tier: Optional[str] = None) -> bytes:
    """Génère un PDF complet du produit demandé avec des données factices réalistes.

    `tier='ultra'` sur theme-natal enrichit le natal_data avec book_data mocké
    (comme GPT le produirait) pour tester le TOC complet 25+ pages.
    """
    if product == 'astrocartographie':
        from services.astrocartographie_pdf import generate_astrocartographie_pdf
        chosen = [
            {'city': 'Lisbonne', 'country': 'Portugal', 'nearby_lines': [
                {'planet': 'Venus', 'line_type': 'AC', 'distance_km': 240},
                {'planet': 'Sun', 'line_type': 'MC', 'distance_km': 610},
            ], 'enriched': {
                'headline': "La beauté douce t'attend au bord du Tage",
                'ambiance': "Lisbonne t'offre une lumière tendre, une architecture patinée par les siècles. La ville respire lentement et t'invite à faire pareil.",
                'career': "Ton élan créatif y trouve un terreau fertile. Les projets artistiques y prennent racine facilement.",
                'love': "La ville accueille les rencontres qui prennent le temps. On y aime sans presse.",
                'spirituality': "Le silence bleu de l'océan y devient un compagnon quotidien. Ta méditation trouve sa cadence.",
                'body': "Le climat doux libère les tensions accumulées. Ta respiration s'approfondit naturellement.",
                'advice': "Prends ton temps. Marche dans les quartiers plusieurs jours d'affilée avant d'y poser tes bagages définitivement.",
            }},
        ]
        bonus = [
            {'city': 'Bali', 'country': 'Indonésie', 'enriched': {
                'headline': "Une pause verte pour ton âme",
                'ambiance': "Bali t'offre la végétation luxuriante et le rythme lent des rituels quotidiens.",
                'why': "Tu portes en toi une ligne Neptune tenace. Bali est l'endroit du monde où cette énergie s'exprime avec le plus de grâce.",
                'promise': "L'île te rendra ta poésie perdue.",
                'career': "La créativité y explose sans effort. On y écrit, on y peint, on y compose comme jamais ailleurs.",
                'love': "Les liens y deviennent contemplatifs. Les silences y sont amoureux.",
                'spirituality': "Le sacré est partout — dans une offrande, un sourire, une lumière.",
                'body': "Ton corps se déploie. Yoga, danse, marche pieds nus : tout y devient possible.",
            }},
        ]
        return generate_astrocartographie_pdf(
            first_name=first_name,
            birth_date_iso='1990-05-15',
            map_svg=None,
            chosen_cities=chosen,
            bonus_cities=bonus,
            synthesis_text="Tu as reçu la carte du monde selon toi. Prends le temps de laisser infuser. Le vrai voyage commence après avoir refermé ce livre.",
            lines_data=None,
        )

    if product == 'kabbale':
        from services.kabbale_pdf import generate_kabbale_pdf
        tree_data = {
            'sephiroth': [{'english': 'Tiphareth', 'planet': {'modern_halevi': 'Sun'}}],
            'daat': {},
            'paths': [],
            'pillar_balance': {'severity': 3, 'mercy': 4, 'equilibrium': 3},
            'dominant_sephirah': 'Tiphareth',
            'spiritual_focus': 'Le cœur rayonne. La beauté est ta boussole.',
            'synthesis': "Ton chemin passe par Tiphareth — la sphère du Soleil, du cœur, de la beauté juste. Tu es appelé(e) à rayonner sans forcer, à briller avec justesse.",
        }
        return generate_kabbale_pdf(first_name, '1990-05-15', tree_data, None)

    if product == 'karma-destin':
        from services.karma_destin_pdf import generate_karma_destin_pdf
        karma_data = {
            'karmic_analysis': 'Ton karma parle par les nœuds : chemin vers la lumière, héritage à honorer.',
            'planets': [],
            'noeud_nord_sign': 'Poissons',
            'noeud_sud_sign': 'Vierge',
        }
        return generate_karma_destin_pdf(first_name, '1990-05-15', karma_data, None)

    if product == 'numerologie':
        from services.numerologie_pdf import generate_numerologie_pdf
        num_data = {
            'chemin_de_vie': {'nombre': 7, 'interpretation': 'Le chercheur — quête intérieure', 'description': 'Ton chemin est celui de la sagesse patiente.'},
            'nombre_expression': {'nombre': 3, 'interpretation': 'Créatif', 'description': ''},
            'nombre_ame': {'nombre': 9, 'interpretation': "L'humaniste", 'description': ''},
            'nombre_personnalite': {'nombre': 6, 'interpretation': "Protecteur", 'description': ''},
        }
        return generate_numerologie_pdf(first_name, '1990-05-15', num_data, None, None, None)

    if product == 'theme-natal':
        from services.natal_pdf_v2 import build_natal_pdf_v2
        natal_data = {
            'sun_sign': 'Taureau', 'moon_sign': 'Poissons', 'ascendant_sign': 'Vierge',
            'planets': [
                {'name': 'Soleil',    'sign': 'Taureau',  'analysis': 'Ton Soleil en Taureau te donne une stabilité rassurante et un goût prononcé pour la beauté sensorielle. Tu construis lentement mais durablement.'},
                {'name': 'Lune',      'sign': 'Poissons', 'analysis': 'Ta Lune en Poissons ouvre ton monde émotionnel à une sensibilité rare, presque médiumnique. Tu ressens ce que les autres cachent.'},
                {'name': 'Mercure',   'sign': 'Gémeaux',  'analysis': 'Mercure en Gémeaux — ton esprit vif jongle avec les idées et les mots. La curiosité est ton moteur.'},
                {'name': 'Vénus',     'sign': 'Bélier',   'analysis': "Vénus en Bélier — tu aimes avec passion et immédiateté. L'attente t'ennuie."},
                {'name': 'Mars',      'sign': 'Cancer',   'analysis': 'Mars en Cancer — tu défends les tiens avec ferveur, mais évites la confrontation directe.'},
                {'name': 'Jupiter',   'sign': 'Sagittaire', 'analysis': 'Jupiter en Sagittaire — un horizon s\'ouvre. La foi et le voyage te grandissent.'},
                {'name': 'Saturne',   'sign': 'Verseau',  'analysis': "Saturne en Verseau — tes leçons passent par l'engagement collectif."},
            ],
            'tier': tier or 'flash',
        }
        # Tier ultra : injecte book_data mocké (comme GPT enrichi) pour déclencher
        # le rendu du sommaire complet 25+ pages avec toutes les parties/chapitres
        if tier == 'ultra':
            # Chapitre-âme complet (5 clés × ~10 blocs) — mock 'GPT enrichi'
            def _acte3_chapter(title: str) -> dict:
                return {
                    'citation_ouverture': "Il y a en toi une lumière que le monde n'a pas encore vue — et pourtant, elle éclaire déjà tout ce que tu touches.",
                    'question_emotionnelle': f"Quelle part de {title.lower()} laisses-tu vraiment respirer ?",
                    'analyse_html': (
                        "<p>Ton thème natal dessine une architecture rare : une sensibilité mouvante habite "
                        "chaque décision, chaque geste, chaque silence. Tu portes une manière d'aimer qui refuse "
                        "les compromis tièdes — elle veut du vrai, du profond, du durable.</p>"
                        "<p>Là où d'autres cherchent la clarté rapide, tu prends le temps de laisser mûrir. "
                        "Cette lenteur n'est pas de la peur : c'est une forme d'intelligence lente, presque "
                        "végétale, qui distingue ce qui compte de ce qui passe.</p>"
                        "<p>Ta trajectoire s'écrit dans la fidélité aux liens choisis, dans la construction "
                        "patiente d'un monde intérieur riche. C'est ta signature — reconnais-la.</p>"
                    ),
                    'phrase_memorable': "Tu n'as jamais eu besoin d'être vue pour exister. C'est peut-être pour cela qu'on te remarque.",
                    'conseils': [
                        "Nomme une chose que tu portes en secret depuis trop longtemps.",
                        "Choisis un rituel qui honore ta lenteur — sans culpabilité.",
                        "Laisse quelqu'un t'aider cette semaine, sans t'excuser d'exister.",
                    ],
                    'rituel_titre': f"Rituel — Ouvrir {title.lower()}",
                    'rituel_body': (
                        "À la nuit tombée, allume une bougie ivoire et pose une main sur ton cœur. "
                        "Respire lentement, sept fois. À chaque expiration, prononce à voix basse un mot "
                        "qui décrit ce que tu veux libérer. Laisse la flamme se consumer."
                    ),
                    'pierre': 'Quartz rose',
                    'couleur': 'Or vieilli',
                    'respiration': '4-7-8 (inspire 4, retiens 7, expire 8) × 5 cycles',
                    'question_journal': f"Écris pendant 12 minutes sans t'arrêter : que veut me dire {title.lower()} aujourd'hui ?",
                    'forces': ['Loyauté profonde', 'Sensibilité fine', 'Constance'],
                    'defis': ['Difficulté à demander', 'Attente longue', 'Perfectionnisme silencieux'],
                    'mission': f"Habiter {title.lower()} sans jamais te trahir — et laisser les autres apprendre de ton exemple.",
                }
            _long_html = (
                "<p>Ton thème raconte une histoire précise : celle d'une âme qui a choisi cette incarnation "
                "pour apprendre à conjuguer intensité et douceur. Les planètes de ton ciel s'accordent en "
                "une mélodie unique, ni entièrement paisible ni entièrement tumultueuse.</p>"
                "<p>Ce livre déplie chaque note de cette mélodie — les évidences, les nuances, les "
                "silences. Prends ton temps pour l'écouter.</p>"
            )
            natal_data['book_data'] = {
                '_source': 'gpt',
                'chapter_intro': "Ce livre s'ouvre comme une carte du ciel — la tienne. Chaque planète y raconte une part de qui tu es, et l'ensemble compose une mélodie unique au monde. Prends le temps de lire chaque page comme on lit une lettre longtemps attendue.",
                'dedication': "Pour toi, qui as ouvert ce livre un soir où le ciel semblait vouloir te parler.",
                'triangle_intime_intro': "Ton Soleil, ta Lune et ton Ascendant forment un triangle d'or — l'essence de ta signature intérieure.",
                'planets_intimate_intro': "Voici les cinq planètes qui composent ton quotidien intime — celles qui vibrent chaque jour à ton contact.",
                'planets_generational_intro': "Ces planètes plus lentes marquent les strates profondes de ta génération. Elles racontent l'époque à travers toi.",
                'aspects_intro': "Les aspects sont la danse invisible entre tes planètes — parfois harmonieuse, parfois électrique. Tout y est mouvement.",
                'houses_intro': "Les douze maisons sont les scènes de ta vie. Chacune met en lumière un domaine — l'amour, le travail, les racines, l'invisible.",
                'year_ahead': _long_html + "<p>Regarde vers avril : quelque chose y bascule doucement, sans bruit. Un projet trouve sa forme. Un lien se dénoue ou s'approfondit. Fais confiance à ce tempo.</p>",
                'emotional_ending': "Referme ce livre avec douceur. Tu portais déjà en toi tout ce qu'il révèle. Il n'a fait que rendre visible ce que le ciel avait tracé pour toi.",
                'colophon': "Ce livre a été composé en Cinzel et Cormorant Garamond, sur papier crème virtuel, pour Plume Astrale, en février 2026.",
                # ── Element / modality synthèse (Acte II)
                '_em': {
                    'dominant_element': 'Terre',
                    'dominant_modality': 'Fixe',
                    'dominant_element_count': 4,
                    'dominant_modality_count': 5,
                },
                'element_analysis': _long_html + "<p>Ta dominante Terre te donne une assise rare — un rapport concret au réel, à la beauté sensorielle, au corps.</p>",
                'modality_analysis': _long_html + "<p>Ta dominante Fixe raconte ta capacité à tenir, à approfondir, à ne pas céder à la mode du moment.</p>",
                'trio_synthesis': _long_html + "<p>Soleil-Lune-Ascendant se répondent en écho : une identité qui construit, une émotion qui rêve, une manière d'apparaître qui rassure.</p>",
                # ── Aspects (Acte II fin)
                'aspects_harmonieux_headline': "La grâce en toi",
                'aspects_harmonieux_body': _long_html,
                'aspects_tensions_headline': "Le nœud qui te forge",
                'aspects_tensions_body': _long_html,
                'rare_aspect_headline': "Ta note rare",
                'rare_aspect_body': _long_html,
                # ── Acte III : les 5 chapitres d'âme
                'acte3_chapters': {
                    'coeur':     _acte3_chapter('Ton cœur'),
                    'esprit':    _acte3_chapter('Ton esprit'),
                    'blessures': _acte3_chapter('Tes blessures'),
                    'desirs':    _acte3_chapter('Tes désirs'),
                    'talents':   _acte3_chapter('Tes talents'),
                },
                # ── 12 maisons (Acte IV)
                **{f'house_{n}': _long_html for n in range(1, 13)},
            }
        # book_data doit être passé comme kwarg explicite à build_natal_pdf_v2
        book_data = natal_data.pop('book_data', None)
        return build_natal_pdf_v2(first_name, '1990-05-15', natal_data, book_data=book_data)

    if product == 'synastrie':
        from services.synastrie_pdf_generator import generate_synastrie_pdf
        p1 = {'prenom': first_name, 'birth_date': '1990-05-15', 'birth_city': 'Paris',
              'birth_time': '12:00', 'sun_sign': 'Taureau'}
        p2 = {'prenom': partner_name or 'Adrien', 'birth_date': '1988-11-22', 'birth_city': 'Lyon',
              'birth_time': '18:30', 'sun_sign': 'Sagittaire'}
        return generate_synastrie_pdf(p1, p2, None)

    raise HTTPException(status_code=404, detail=f"Produit '{product}' inconnu")


@router.get("/{product}")
async def generate_test_pdf(
    product: str,
    request: Request,
    first_name: str = Query('Léa', description="Prénom factice pour la couverture"),
    partner_name: Optional[str] = Query(None, description="Prénom partenaire (synastrie)"),
    tier: Optional[str] = Query(None, description="'ultra' pour Thème Natal 25+ pages"),
    download: bool = Query(False),
    _admin: dict = Depends(require_admin),
):
    """Génère et retourne le PDF complet du produit avec des données factices."""
    key = product.lower().strip()
    valid = {'astrocartographie', 'kabbale', 'karma-destin', 'numerologie', 'theme-natal', 'synastrie'}
    if key not in valid:
        raise HTTPException(status_code=404, detail=f"Produit '{product}' inconnu — options : {sorted(valid)}")

    try:
        pdf_bytes = _fixture(key, first_name=first_name, partner_name=partner_name, tier=tier)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f'[admin_pdf_test] gen {key} failed')
        raise HTTPException(status_code=500, detail=f"Génération impossible : {e}")

    # Trace analytics (non-bloquant)
    admin_email = (_admin or {}).get('email') or 'unknown'
    ip = (request.client.host if request.client else '') or ''
    await _log_generation(admin_email, key, first_name, partner_name, tier, len(pdf_bytes), ip)

    disposition = (
        f'attachment; filename="test-{key}-{first_name}.pdf"' if download
        else f'inline; filename="test-{key}.pdf"'
    )
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': disposition, 'Cache-Control': 'no-store'},
    )


@router.get("/_logs/recent")
async def get_recent_generations(_admin: dict = Depends(require_admin), limit: int = Query(20, ge=1, le=100)):
    """Retourne les N dernières générations admin (pour le mini-widget analytics)."""
    try:
        from services.mongo import get_db  # type: ignore
        db = get_db()
        if db is None:
            return {'logs': [], 'total': 0}
        cursor = db.admin_pdf_test_logs.find({}, {'_id': 0}).sort('created_at', -1).limit(limit)
        logs = [doc async for doc in cursor]
        # Agrégation par produit (les 30 derniers jours)
        pipeline = [
            {'$sort': {'created_at': -1}},
            {'$limit': 500},
            {'$group': {'_id': '$product', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
        ]
        stats = [doc async for doc in db.admin_pdf_test_logs.aggregate(pipeline)]
        return {'logs': logs, 'total': len(logs), 'stats': stats}
    except Exception as e:
        logger.warning(f'[admin_pdf_test] recent logs fetch failed: {e}')
        return {'logs': [], 'total': 0, 'stats': []}
