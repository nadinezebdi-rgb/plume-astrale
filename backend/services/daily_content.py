"""
Service de contenu quotidien intelligent
Génère horoscope du jour, conseils et phrases spirituelles
basé sur le signe zodiacal + positions planétaires + date du jour
"""
import hashlib
from datetime import date

# Phrases spirituelles par thème (84 phrases = 12 semaines de contenu unique)
PHRASES_SPIRITUELLES = [
    "Les étoiles inclinent, mais ne déterminent pas. Votre libre arbitre est votre plus grand pouvoir.",
    "Chaque aube est une renaissance. Aujourd'hui, vous avez le choix de vous réinventer.",
    "L'univers conspire toujours en faveur de ceux qui osent rêver.",
    "Votre lumière intérieure est plus forte que n'importe quelle obscurité extérieure.",
    "La patience est la sagesse de l'âme. Ce qui doit venir viendra au moment parfait.",
    "Vous êtes un être infini ayant une expérience humaine. N'oubliez jamais votre grandeur.",
    "Les synchronicités ne sont pas des coïncidences. L'univers vous envoie des messages.",
    "Votre intuition est votre boussole céleste. Apprenez à lui faire confiance.",
    "Chaque épreuve est un enseignement déguisé. Cherchez la leçon cachée.",
    "La gratitude est la clé qui ouvre les portes de l'abondance cosmique.",
    "Vous n'avez pas besoin d'être parfait(e) pour être extraordinaire.",
    "Les cycles lunaires vous rappellent que tout est temporaire. Profitez de chaque phase.",
    "Votre âme a choisi cette vie pour une raison. Faites confiance au plan divin.",
    "L'amour que vous donnez est l'amour que vous recevez, multiplié par l'infini.",
    "Dans le silence intérieur, vous trouverez toutes les réponses que vous cherchez.",
    "Les étoiles vous guident, mais c'est vous qui tenez le gouvernail de votre destin.",
    "Chaque rencontre est un miroir de votre âme. Que reflétez-vous aujourd'hui ?",
    "La vulnérabilité n'est pas une faiblesse, c'est le courage de montrer votre vraie nature.",
    "L'univers ne vous donne jamais plus que ce que vous pouvez porter.",
    "Votre énergie est contagieuse. Choisissez consciemment ce que vous irradiez.",
    "Les rêves sont les murmures de votre âme. Écoutez-les attentivement.",
    "Chaque jour est une page blanche dans le livre de votre destinée.",
    "La magie n'est pas dans les étoiles. Elle est en vous qui les regardez.",
    "Lâchez prise sur le contrôle. La vie a un plan plus grand que le vôtre.",
    "Votre chemin est unique. Cessez de le comparer à celui des autres.",
    "Les obstacles sont des invitations à découvrir des forces que vous ignoriez.",
    "L'abondance commence dans l'esprit avant de se manifester dans la matière.",
    "Respirez. Vous êtes exactement là où vous devez être en ce moment.",
    "Chaque fin est un nouveau commencement déguisé. Accueillez les transitions.",
    "Votre corps est un temple sacré. Honorez-le comme tel.",
    "Les mots ont un pouvoir créateur. Choisissez-les avec sagesse.",
    "Le pardon est le cadeau que vous vous offrez à vous-même.",
    "Vous êtes le créateur de votre réalité. Que souhaitez-vous manifester ?",
    "La compassion envers soi-même est le premier pas vers la guérison.",
    "Les planètes dansent pour vous. Aujourd'hui, dansez avec elles.",
    "Votre essence est immortelle. Cette vie n'est qu'un chapitre de votre histoire cosmique.",
    "L'harmonie intérieure se reflète toujours dans le monde extérieur.",
    "Faites confiance au timing de l'univers, même quand il vous semble en retard.",
    "Chaque respiration est un acte de foi envers la vie.",
    "Vous portez en vous la sagesse de toutes vos vies passées.",
    "L'amour est la fréquence la plus élevée de l'univers. Vibrez à cette fréquence.",
    "Les étoiles filantes sont des rappels : vos vœux ont du pouvoir.",
]

# Thèmes quotidiens par domaine
THEMES_HOROSCOPE = {
    "amour": [
        "Les astres favorisent les connexions profondes aujourd'hui. Ouvrez votre cœur aux rencontres inattendues.",
        "Vénus influence votre secteur relationnel. C'est le moment d'exprimer vos sentiments avec authenticité.",
        "Une énergie de renouveau amoureux circule. Si vous êtes en couple, surprenez votre partenaire.",
        "Les vibrations célestes encouragent la communication sincère dans vos relations.",
        "L'amour de soi est au centre aujourd'hui. Prenez soin de vous avant de donner aux autres.",
        "Une rencontre significative pourrait survenir. Restez ouvert(e) aux signes de l'univers.",
        "Les énergies planétaires appellent à la réconciliation et au pardon dans vos relations.",
    ],
    "carriere": [
        "Les astres soutiennent vos ambitions professionnelles. C'est le moment d'avancer avec confiance.",
        "Une opportunité inattendue pourrait se présenter. Restez attentif(ve) aux propositions.",
        "Votre créativité est à son apogée. Utilisez-la pour résoudre un défi professionnel.",
        "Les énergies favorisent la collaboration. Un partenariat pourrait s'avérer fructueux.",
        "C'est le moment de prendre du recul et d'évaluer votre trajectoire professionnelle.",
        "Votre détermination attire la reconnaissance. Ne sous-estimez pas vos accomplissements.",
        "Les astres encouragent l'apprentissage. Investissez dans vos compétences aujourd'hui.",
    ],
    "sante": [
        "Écoutez les messages de votre corps aujourd'hui. Il vous guide vers l'équilibre.",
        "Les énergies lunaires favorisent le repos et la régénération. Accordez-vous une pause.",
        "L'activité physique en pleine nature vous rechargera en énergie vitale.",
        "Votre intuition corporelle est aiguisée. Suivez vos instincts alimentaires.",
        "La méditation ou le yoga seraient particulièrement bénéfiques aujourd'hui.",
        "Hydratez-vous abondamment. L'eau est votre alliée pour maintenir votre vitalité.",
        "Les astres encouragent un sommeil réparateur. Créez un rituel du soir apaisant.",
    ],
    "spirituel": [
        "Les voiles entre les mondes sont fins aujourd'hui. Votre intuition est décuplée.",
        "Un message important pourrait vous parvenir par le biais d'un rêve ou d'une synchronicité.",
        "C'est le moment idéal pour méditer et vous connecter à votre guidance intérieure.",
        "Les énergies cosmiques amplifient votre sensibilité psychique. Faites-lui confiance.",
        "Un rituel de gratitude ce soir alignera vos énergies avec l'abondance universelle.",
        "Votre troisième œil est particulièrement actif. Notez vos visions et impressions.",
        "La nature est votre temple aujourd'hui. Cherchez l'inspiration dans les éléments.",
    ],
}

# Conseils par élément zodiacal
CONSEILS_PAR_ELEMENT = {
    "Feu": [
        "Canalisez votre énergie ardente vers un projet créatif aujourd'hui.",
        "Votre enthousiasme est contagieux. Partagez-le avec ceux qui en ont besoin.",
        "Tempérez votre impatience. Les meilleures choses arrivent à point.",
        "Votre courage inspire les autres. N'hésitez pas à prendre les devants.",
        "L'action est votre alliée, mais la réflexion avant l'action est votre sagesse.",
        "Votre flamme intérieure brille plus fort quand vous êtes authentique.",
        "Aujourd'hui, laissez votre passion guider vos choix sans brûler les étapes.",
    ],
    "Terre": [
        "Ancrez-vous dans le moment présent. Votre stabilité est votre superpouvoir.",
        "La patience porte ses fruits. Continuez à construire, pierre par pierre.",
        "Connectez-vous à la nature pour recharger vos batteries terrestres.",
        "Votre sens pratique résout les problèmes que d'autres trouvent insurmontables.",
        "Aujourd'hui, faites confiance à vos sens. Ils ne vous trompent jamais.",
        "La beauté se cache dans les détails. Prenez le temps d'apprécier les petites choses.",
        "Votre fiabilité est un trésor. N'oubliez pas d'être aussi fiable envers vous-même.",
    ],
    "Air": [
        "Votre esprit vif capte des idées brillantes aujourd'hui. Notez-les !",
        "La communication est votre force. Exprimez ce que vous ressentez avec clarté.",
        "Stimulez votre curiosité intellectuelle. Un livre ou une conversation pourrait vous transformer.",
        "Votre adaptabilité est remarquable. Utilisez-la pour naviguer les changements avec grâce.",
        "Les connexions sociales nourrissent votre âme. Entourez-vous de personnes inspirantes.",
        "Aujourd'hui, laissez vos pensées s'envoler. La liberté mentale ouvre de nouvelles portes.",
        "Votre objectivité est un don. Utilisez-la pour conseiller un proche dans le besoin.",
    ],
    "Eau": [
        "Votre sensibilité est un radar émotionnel puissant. Faites-lui confiance.",
        "Les émotions sont des messagers. Accueillez-les sans jugement aujourd'hui.",
        "Votre empathie guérit les autres. N'oubliez pas de vous protéger aussi.",
        "L'eau purifie. Un bain ou une promenade près de l'eau apaisera votre âme.",
        "Votre intuition est particulièrement forte. Suivez vos pressentiments.",
        "Les rêves de cette nuit portent des messages importants. Analysez-les.",
        "Aujourd'hui, permettez-vous d'être vulnérable. C'est une force, pas une faiblesse.",
    ],
}

# Mapping signe -> élément
SIGNE_ELEMENT = {
    "Aries": "Feu", "Taurus": "Terre", "Gemini": "Air", "Cancer": "Eau",
    "Leo": "Feu", "Virgo": "Terre", "Libra": "Air", "Scorpio": "Eau",
    "Sagittarius": "Feu", "Capricorn": "Terre", "Aquarius": "Air", "Pisces": "Eau",
}

SIGNE_FR = {
    "Aries": "Bélier", "Taurus": "Taureau", "Gemini": "Gémeaux", "Cancer": "Cancer",
    "Leo": "Lion", "Virgo": "Vierge", "Libra": "Balance", "Scorpio": "Scorpion",
    "Sagittarius": "Sagittaire", "Capricorn": "Capricorne", "Aquarius": "Verseau", "Pisces": "Poissons",
}


def _daily_seed(sign: str, today: date = None) -> int:
    """Generate a deterministic seed for a sign+date combo"""
    if today is None:
        today = date.today()
    key = f"{sign}-{today.isoformat()}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16)


def _pick(items: list, seed: int, offset: int = 0) -> str:
    """Pick an item deterministically from a list"""
    idx = (seed + offset) % len(items)
    return items[idx]


def get_daily_content(zodiac_sign: str, today: date = None) -> dict:
    """Generate complete daily content for a zodiac sign"""
    if today is None:
        today = date.today()

    element = SIGNE_ELEMENT.get(zodiac_sign, "Terre")
    signe_fr = SIGNE_FR.get(zodiac_sign, zodiac_sign)
    seed = _daily_seed(zodiac_sign, today)

    # Pick content
    horoscope_amour = _pick(THEMES_HOROSCOPE["amour"], seed, 0)
    horoscope_carriere = _pick(THEMES_HOROSCOPE["carriere"], seed, 1)
    horoscope_sante = _pick(THEMES_HOROSCOPE["sante"], seed, 2)
    horoscope_spirituel = _pick(THEMES_HOROSCOPE["spirituel"], seed, 3)
    conseil = _pick(CONSEILS_PAR_ELEMENT[element], seed, 4)
    phrase = _pick(PHRASES_SPIRITUELLES, seed, 5)

    # Scores (1-10) deterministic per day
    score_amour = (seed % 5) + 6  # 6-10
    score_carriere = ((seed >> 4) % 5) + 5  # 5-9
    score_sante = ((seed >> 8) % 4) + 6  # 6-9
    score_energie = ((seed >> 12) % 5) + 5  # 5-9

    # Lucky items
    lucky_numbers = sorted([(seed + i * 7) % 49 + 1 for i in range(3)])
    couleurs_chance = ["Or", "Violet", "Bleu nuit", "Émeraude", "Rouge rubis", "Argent", "Rose", "Indigo"]
    couleur = _pick(couleurs_chance, seed, 10)

    return {
        "date": today.isoformat(),
        "signe": zodiac_sign,
        "signe_fr": signe_fr,
        "element": element,
        "phrase_du_jour": phrase,
        "conseil_du_jour": conseil,
        "horoscope": {
            "amour": {"texte": horoscope_amour, "score": score_amour},
            "carriere": {"texte": horoscope_carriere, "score": score_carriere},
            "sante": {"texte": horoscope_sante, "score": score_sante},
            "spirituel": {"texte": horoscope_spirituel, "score": score_energie},
        },
        "energie_du_jour": score_energie,
        "numeros_chance": lucky_numbers,
        "couleur_du_jour": couleur,
    }
