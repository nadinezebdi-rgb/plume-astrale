"""L'humeur du mois — contenu Python miroir de config/monthlyMoods.js.

12 climats universels x 4 éléments = 48 accents uniques. Utilisé par le
rapport PDF mensuel envoyé aux abonnés Cercle Soléna le 1er de chaque mois.
"""
from __future__ import annotations
from datetime import date
from typing import Optional, Tuple


MONTH_NAMES_FR = [
    'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
]

UNIVERSAL_CLIMATES = [
    {
        'title': 'Un mois pour poser des fondations',
        'body': "Le début d'année invite à la clarté. Ce n'est pas le moment de tout révolutionner — c'est celui d'écrire, doucement, ce que vous voulez que cette année porte pour vous.",
    },
    {
        'title': 'Un mois pour approfondir',
        'body': "Février resserre. On y regarde ce qui compte vraiment : les liens, les priorités, les gestes du quotidien. Une période idéale pour trier sans brusquer.",
    },
    {
        'title': 'Un mois de bascule',
        'body': "L'équinoxe rouvre l'horizon. Ce mois-ci, quelque chose que vous portez depuis l'hiver demande à voir le jour. Écoutez ce qui frémit — c'est rarement anodin.",
    },
    {
        'title': 'Un mois pour oser',
        'body': "Le printemps ne demande pas la perfection : il demande l'élan. Une conversation reportée, un projet mis de côté, un pas simple à franchir — c'est le mois pour.",
    },
    {
        'title': 'Un mois pour incarner',
        'body': "Mai concrétise. Ce que vous avez semé en début d'année prend forme, doucement. Cherchez la beauté dans les gestes ordinaires : ils portent plus que vous ne croyez.",
    },
    {
        'title': 'Un mois pour relier',
        'body': "Juin ouvre l'espace des rencontres et des retrouvailles. Les liens qui comptent se réactivent. Prenez le temps de choisir ceux à qui vous donnez le vôtre.",
    },
    {
        'title': 'Un mois pour respirer',
        'body': "L'été invite au ralentissement. La pause n'est pas une fuite — c'est une méthode. Ce que vous laissez décanter maintenant reviendra plus juste ensuite.",
    },
    {
        'title': 'Un mois pour rêver plus grand',
        'body': "Août élargit la perspective. Prenez de la hauteur sur les six premiers mois : qu'avez-vous appris ? qu'aimeriez-vous transformer pour la rentrée ?",
    },
    {
        'title': 'Un mois pour se remettre en mouvement',
        'body': "La rentrée rassemble l'énergie éparse de l'été. Un cap se dessine à nouveau. Ne forcez rien — laissez le rythme naturel se réinstaller.",
    },
    {
        'title': 'Un mois pour trancher',
        'body': "Octobre confronte aux choix qu'on a évités. Le mois demande de la clarté, pas du drame. Une décision posée maintenant libère beaucoup plus que vous n'imaginez.",
    },
    {
        'title': 'Un mois pour se recentrer',
        'body': "Novembre invite à revenir à soi. Moins d'agitation, plus d'écoute intérieure. Ce que vous entendez dans le silence de ce mois éclaire souvent l'année à venir.",
    },
    {
        'title': 'Un mois pour clore et intégrer',
        'body': "Décembre rassemble le fil de l'année. Ce n'est pas le moment des grands départs — c'est celui des remerciements et de la préparation intérieure.",
    },
]

ELEMENT_ACCENTS = {
    'Feu': [
        "Pour vous, signe de Feu, la retenue est votre discipline du mois : posez un pas à la fois.",
        "Votre énergie de Feu gagne à s'orienter vers l'intime plutôt que le spectaculaire ce mois-ci.",
        "Le Feu se réveille avec l'équinoxe : suivez l'impulsion, mais choisissez sa direction.",
        "Votre nature de Feu aime les commencements — avril vous rend particulièrement à l'aise.",
        "Le Feu apprend l'incarnation en mai : passez de l'idée au geste concret.",
        "En juin, votre Feu communique. C'est le moment d'exposer clairement ce que vous portez.",
        "Le Feu apprend le repos en juillet : ce n'est pas une trahison de votre nature, c'est sa maturation.",
        "Août redonne à votre Feu une vision large. Rêvez sans vous censurer.",
        "Septembre canalise votre Feu vers un cap précis. Ne l'éparpillez pas.",
        "Votre Feu tranche mieux qu'aucun autre en octobre. Utilisez ce clair-obscur.",
        "Novembre demande à votre Feu la nuance. Contenance ne veut pas dire renoncement.",
        "Décembre veut de votre Feu une chaleur qui rassemble, plus qu'une flamme qui perce.",
    ],
    'Terre': [
        "Pour vous, signe de Terre, janvier ressemble à un début parfait : lente, méthodique, ancrée.",
        "Votre Terre affine ses priorités en février. Ce que vous décidez de garder aura du poids.",
        "La Terre s'ouvre à la vibration du printemps en mars : laissez la sève monter.",
        "Avril demande à votre Terre un peu de spontanéité. Sortez d'un plan pour voir ce qui apparaît.",
        "Mai est votre mois par excellence, signe de Terre : récoltez ce que vous avez patiemment cultivé.",
        "Juin invite votre Terre à s'ouvrir aux liens. Ne restez pas seul avec vos réussites.",
        "La Terre se régénère en juillet : mangez lentement, marchez sans but, dormez profondément.",
        "Août réoxygène votre Terre. Autorisez-vous une pensée plus ample que le quotidien.",
        "Votre Terre reprend son sillon en septembre. Elle sait exactement quoi faire.",
        "Octobre récolte vraiment pour vous. Ce que vous décidez porte des fruits durables.",
        "Novembre est un mois riche pour votre Terre : elle sait bien vieillir ce qui compte.",
        "Décembre demande à votre Terre de se laisser inspirer. Écoutez plutôt qu'organisez.",
    ],
    'Air': [
        "Votre Air structure ses idées en janvier. Écrivez plus que d'habitude.",
        "Février resserre les liens et vous invite, signe d'Air, à choisir la profondeur.",
        "L'Air adore mars : les échanges se multiplient. Sélectionnez ceux qui nourrissent.",
        "En avril, votre Air passe de la pensée à l'action. Ne restez pas au stade du concept.",
        "Mai demande à votre Air un peu de patience. La lenteur ouvre parfois de nouvelles idées.",
        "Juin est votre mois : votre Air relie, présente, ouvre des ponts. Profitez-en.",
        "L'Air prend de la hauteur en juillet. Un voyage, un livre, une pause changent tout.",
        "Août élargit encore votre horizon d'Air. Osez les questions qui font vraiment bouger.",
        "La rentrée met votre Air en mouvement. Les projets à plusieurs vous portent particulièrement.",
        "Octobre demande à votre Air une décision claire — pas une nouvelle option.",
        "Novembre invite votre Air à écouter plus qu'à formuler. Une intuition mérite d'être suivie.",
        "Décembre récolte les idées semées : notez tout ce qui remonte, même flou.",
    ],
    'Eau': [
        "Janvier apaise votre Eau. Suivez le rythme intérieur, il porte des choses justes.",
        "Février creuse pour vous. Ce que vous ressentez ce mois-ci révèle ce qui compte vraiment.",
        "L'Eau se renouvelle avec mars. Les émotions bougent — accompagnez-les sans les figer.",
        "Avril demande à votre Eau du courage. Une émotion prête à se dire mérite un espace clair.",
        "En mai, votre Eau s'incarne. Traduisez le ressenti en geste concret ou en art.",
        "Juin ouvre votre Eau aux autres. Les liens du cœur reprennent de la place.",
        "Juillet est votre mois par excellence, signe d'Eau : la lenteur régénère profondément.",
        "Août prolonge votre Eau vers l'imaginaire. Rêvez, écrivez, dessinez.",
        "Septembre demande à votre Eau de reprendre un cap sans se disperser dans l'émotion.",
        "Octobre confronte vos zones d'ombre. Votre Eau sait s'y aventurer avec grâce.",
        "Novembre est riche pour votre Eau : intuition, guidance, silences habités.",
        "Décembre invite votre Eau à intégrer, remercier, préparer l'année à venir doucement.",
    ],
}

# Journal prompts by element — 3 prompts per element, appended to the PDF
JOURNAL_PROMPTS = {
    'Feu': [
        "Quelle est LA chose que je meurs d'envie de commencer ce mois-ci ?",
        "Où est-ce que mon impatience m'a coûté quelque chose récemment ?",
        "Sur quoi vais-je concentrer mon feu pour qu'il éclaire plutôt qu'il consume ?",
    ],
    'Terre': [
        "Qu'est-ce qui, dans mon quotidien actuel, mérite d'être solidifié ?",
        "Où est-ce que je résiste à un changement qui, au fond, m'apporterait ?",
        "Quel geste concret puis-je poser cette semaine pour incarner ma vision ?",
    ],
    'Air': [
        "Quelle idée revient sans cesse dans mes pensées — qu'est-ce qu'elle veut me dire ?",
        "À qui pourrais-je parler cette semaine pour clarifier ce qui me traverse ?",
        "Qu'est-ce que je pense trop et que je ne mets pas assez en pratique ?",
    ],
    'Eau': [
        "Quelle émotion revient souvent en ce moment — que porte-t-elle vraiment ?",
        "À quoi mon intuition essaie-t-elle de m'ouvrir depuis quelques semaines ?",
        "Qu'est-ce qui, dans ma vie actuelle, mérite d'être ressenti plus lentement ?",
    ],
}


# Zodiac ranges (mois, jour de début) — chaque signe part de son jour de début et
# se termine la veille du signe suivant. Capricorne enjambe le nouvel an.
_ZODIAC_RANGES = [
    ('Capricorne', 'Terre', (12, 22), (1, 19)),   # 22 déc → 19 jan
    ('Verseau', 'Air', (1, 20), (2, 18)),
    ('Poissons', 'Eau', (2, 19), (3, 20)),
    ('Bélier', 'Feu', (3, 21), (4, 19)),
    ('Taureau', 'Terre', (4, 20), (5, 20)),
    ('Gémeaux', 'Air', (5, 21), (6, 20)),
    ('Cancer', 'Eau', (6, 21), (7, 22)),
    ('Lion', 'Feu', (7, 23), (8, 22)),
    ('Vierge', 'Terre', (8, 23), (9, 22)),
    ('Balance', 'Air', (9, 23), (10, 22)),
    ('Scorpion', 'Eau', (10, 23), (11, 21)),
    ('Sagittaire', 'Feu', (11, 22), (12, 21)),
]


def get_sign_from_birthdate(birth_date_iso: str) -> Optional[Tuple[str, str]]:
    """Depuis une date ISO (YYYY-MM-DD), renvoie (sign_name, element) ou None."""
    try:
        d = date.fromisoformat(birth_date_iso[:10])
    except Exception:
        return None
    md = (d.month, d.day)
    # Capricorne : 22/12 → 31/12 OU 01/01 → 19/01
    if md >= (12, 22) or md <= (1, 19):
        return ('Capricorne', 'Terre')
    for name, element, start, end in _ZODIAC_RANGES[1:]:
        if start <= md <= end:
            return (name, element)
    return None


def get_monthly_mood(sign_element: str, month_index: int) -> dict:
    """month_index : 0..11 (0 = janvier)."""
    month_index = max(0, min(11, int(month_index)))
    climate = UNIVERSAL_CLIMATES[month_index]
    accents = ELEMENT_ACCENTS.get(sign_element, ELEMENT_ACCENTS['Air'])
    prompts = JOURNAL_PROMPTS.get(sign_element, JOURNAL_PROMPTS['Air'])
    return {
        'month_name': MONTH_NAMES_FR[month_index],
        'month_number': month_index + 1,
        'title': climate['title'],
        'body': climate['body'],
        'accent': accents[month_index],
        'prompts': prompts,
    }
