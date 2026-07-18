"""
Service pour générer un texte mystérieux et attractif sur un couple basé sur les prénoms.
Utilise OpenAI + numérologie de astrology-api.io pour une analyse riche et personnalisée.
"""
import logging
from integrations.llm.chat import LlmChat, UserMessage
from services.astrology_io_service import numerology_compatibility, numerology_name
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_numerology_compatibility(prenom1: str, prenom2: str, current_year: int = None) -> dict:
    """
    Calcule le chiffre de compatibilité numérologique et l'année universelle.
    
    Méthode:
    1. Compter les lettres de chaque prénom
    2. Additionner les deux résultats
    3. Ajouter l'année universelle (réduite à un chiffre)
    4. Réduire le total à un chiffre unique (1-9)
    
    Returns:
        {
            "letters_prenom1": int,
            "letters_prenom2": int,
            "total_letters": int,
            "universal_year": int,
            "compatibility_number": int (1-9),
            "year": int,
        }
    """
    if current_year is None:
        current_year = datetime.now().year
    
    # Compter les lettres (ignorer les accents et espaces)
    def count_letters(name: str) -> int:
        return len([c for c in name.lower() if c.isalpha()])
    
    letters1 = count_letters(prenom1)
    letters2 = count_letters(prenom2)
    total_letters = letters1 + letters2
    
    # Calculer l'année universelle
    year_sum = sum(int(d) for d in str(current_year))
    universal_year = year_sum if year_sum < 10 else sum(int(d) for d in str(year_sum))
    
    # Calculer le chiffre de compatibilité
    compat_number = total_letters + universal_year
    compat_number = compat_number if compat_number < 10 else sum(int(d) for d in str(compat_number))
    
    return {
        "letters_prenom1": letters1,
        "letters_prenom2": letters2,
        "total_letters": total_letters,
        "universal_year": universal_year,
        "compatibility_number": compat_number,
        "year": current_year,
    }


def get_compatibility_interpretation(compat_number: int) -> dict:
    """Retourne l'interprétation du chiffre de compatibilité."""
    interpretations = {
        1: {
            "title": "Renouveau et Nouveaux Départs",
            "element": "L'Initiateur",
            "energy": "énergie, indépendance, nouveauté",
            "strengths": "Leadership naturel, ambition commune, capacité à transformer ensemble. Cette année est idéale pour lancer des projets à deux, sortir des sentiers battus.",
            "challenges": "Attention à l'ego individuel. Trouver l'équilibre entre indépendance personnelle et engagement couple.",
            "theme": "Une année de renouveau où les couples trouvent ensemble une nouvelle direction.",
        },
        2: {
            "title": "Harmonie et Partenariat",
            "element": "Le Médiateur",
            "energy": "équilibre, douceur, collaboration",
            "strengths": "Extraordinaire harmonie émotionnelle, intuition mutuelle, soutien sans faille. Le couple fonctionne comme un seul organisme.",
            "challenges": "Risque de fusion excessive, perte d'individualité. Cultiver l'espace personnel et la communication claire.",
            "theme": "Le couple marche d'un même pas, en parfaite synchronisation.",
        },
        3: {
            "title": "Créativité et Expression",
            "element": "L'Artiste",
            "energy": "joie, créativité, communication",
            "strengths": "Beaucoup de rires, d'humour et de légèreté. Créativité débordante ensemble. Communication fluide et joyeuse.",
            "challenges": "Risque de superficialité ou de fuite face aux vraies épreuves. Apprendre à gérer les conflits avec profondeur.",
            "theme": "Une relation colorée, vivante et remplie de créativité partagée.",
        },
        4: {
            "title": "Stabilité et Fondations",
            "element": "Le Constructeur",
            "energy": "solidité, responsabilité, construction",
            "strengths": "Fondations solides, engagement profond, capacité à construire ensemble sur le long terme. Fiabilité mutuelle.",
            "challenges": "Attention à la rigidité. Ne pas laisser la routine étouffer la passion et le romance.",
            "theme": "Le couple bâtit ensemble quelque chose de durable et de concret.",
        },
        5: {
            "title": "Liberté, Changement et Aventure",
            "element": "L'Aventurier",
            "energy": "liberté, magnétisme, dynamisme",
            "strengths": "Immense complicité, beaucoup de rires et d'énergie. Capacité à s'adapter à toutes les situations. Une relation jamais ennuyeuse.",
            "challenges": "Trouver l'équilibre entre besoin d'indépendance et stabilité long terme. Attention à agir sur des coups de tête.",
            "theme": "Un tourbillon d'énergie où le couple vit intensément chaque moment.",
        },
        6: {
            "title": "Amour et Responsabilité",
            "element": "L'Harmonie",
            "energy": "tendresse, dévouement, harmonie",
            "strengths": "Amour profond et tendre, capacité à s'occuper l'un de l'autre. Couple modèle avec grande maturité affective.",
            "challenges": "Attention à ne pas devenir possessif ou étouffant. Cultiver l'indépendance émotionnelle.",
            "theme": "Un amour fort et bienveillant qui nourrit chacun.",
        },
        7: {
            "title": "Spiritualité et Profondeur",
            "element": "Le Penseur",
            "energy": "introspection, mystère, compréhension",
            "strengths": "Connection spirituelle ou intellectuelle profonde. Compréhension mutuelle sans paroles. Lien ancien ou karmique senti.",
            "challenges": "Attention au repli sur soi. Cultiver l'ouverture vers le monde extérieur ensemble.",
            "theme": "Un couple qui explore ensemble les mystères de l'existence.",
        },
        8: {
            "title": "Pouvoir et Prospérité",
            "element": "Le Puissance",
            "energy": "ambition, succès, matérialité",
            "strengths": "Force et détermination partagées. Capacité à réussir ensemble, créer richesse (matérielle et immatérielle). Couple puissant.",
            "challenges": "Attention au matérialisme ou au culte de la réussite. Garder la connexion humaine et émotionnelle vivante.",
            "theme": "Un couple qui monte ensemble les échelons et réalise ses ambitions.",
        },
        9: {
            "title": "Compassion et Transcendance",
            "element": "Le Sage",
            "energy": "compassion, universalité, achèvement",
            "strengths": "Grand cœur collectif, capacité à aimer sans frontières. Couple humanitaire ou idéaliste. Sagesse et compréhension mutuelle.",
            "challenges": "Ne pas perdre le couple dans une cause plus grande. Garder l'intimité et la priorité à la relation.",
            "theme": "Un couple qui transcende l'égo pour aimer plus grand.",
        },
    }
    return interpretations.get(compat_number, {})



async def generate_couple_mystery_text(prenom1: str, prenom2: str) -> str:
    """
    Génère un paragraphe mystérieux et attractif basé sur les prénoms d'un couple.
    Gratuit (coûts OpenAI gérés côté backend).
    
    Args:
        prenom1: Prénom de la première personne
        prenom2: Prénom de la deuxième personne (optionnel)
        
    Returns:
        Paragraphe mystérieux en français (150-200 mots)
    """
    try:
        if not prenom1 or not prenom2:
            return ""
        
        prompt = f"""Tu es un astrologue français mystérieux et captivant. Tu viens de recevoir les prénoms de deux personnes : {prenom1} et {prenom2}.

Sans connaître leur date de naissance, génère un court paragraphe (150-200 mots) qui :
1. Est mystérieux et poétique
2. Souligne des complémentarités numériques/énergétiques subtiles basées sur les prénoms
3. Donne ENVIE de découvrir l'étude de compatibilité complète
4. Utilise un ton raffiné, jamais trop commercial
5. Évite les clichés (pas de "âmes sœurs", pas de "destiné")

Le paragraphe commence par : "Entre {prenom1} et {prenom2}..."

Génère UNIQUEMENT le paragraphe, sans en-tête ni signature."""

        chat = LlmChat()
        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip() if response else ""
        
    except Exception as e:
        logger.error(f"[couple_mystery] error: {e}")
        return ""


# Fallback si OpenAI ne répond pas - Textes spécifiques par chiffre vibratoire
FALLBACK_TEXTS_BY_NUMBER = {
    1: """Vous incarnez l'énergie du renouveau et de l'initiative. Ensemble, vous tracez une voie nouvelle, portés par une ambition commune et une volonté de transformer ce qui vous entoure. C'est une année de conquête et de commencement pour votre couple.""",
    
    2: """Vous respirez l'harmonie et la complémentarité. Vos énergies se répondent dans une danse silencieuse où l'intuition prime sur la parole. C'est une année de perfectionnement mutuel et de profonde synchronisation.""",
    
    3: """Vous dégagez la joie et la créativité débordante. Votre relation s'épanouit dans la légèreté, l'humour et l'expression authentique. C'est une année colorée, vivante, où le rire scelle votre complicité.""",
    
    4: """Vous bâtissez sur des fondations solides et durables. Votre couple se fortifie par la responsabilité partagée et l'engagement profond. C'est une année de consolidation où la stabilité devient votre atout.""",
    
    5: """Vous vibrez à la liberté et à l'aventure constante. Votre relation se nourrit du changement, de l'adaptabilité et d'une énergie débordante. C'est une année d'intensité où rien ne vous ennuie.""",
    
    6: """Vous incarnez l'amour bienveillant et la tendresse responsable. Votre couple s'épanouit dans le soin mutuel et la maturité affective. C'est une année d'harmonie empreinte de grande douceur.""",
    
    7: """Vous explorez ensemble les mystères et les profondeurs. Votre connexion transcende le visible, guidée par une compréhension spirituelle et intellectuelle. C'est une année de contemplation et de sagesse partagée.""",
    
    8: """Vous rayonnez de puissance et d'ambition partagée. Votre couple se construit dans la force, le succès et la réalisation concrète de vos rêves. C'est une année de réussite et de manifestation.""",
    
    9: """Vous incarnez la compassion et la vision universelle. Votre amour transcende l'égo personnel pour s'élever vers quelque chose de plus grand. C'est une année d'achèvement et de sagesse collective.""",
}

FALLBACK_TEXTS = {
    "fr": """Entre {p1} et {p2}, les prénoms eux-mêmes murmurent une histoire. 
    Les vibrations numériques qui dansent sous ces lettres ne sont jamais neutres. 
    Certaines énergies s'appellent, d'autres se révèlent seulement quand on sait les écouter.
    L'astrologie relationnelle révèle ce que les prénoms seuls ne peuvent qu'insinuer :
    la profondeur de ce lien, ses couleurs cachées, les défis qui le façonnent, 
    et surtout, le ciel qui veille sur vous deux."""
}


def get_fallback_text(prenom1: str, prenom2: str, compat_number: int = None, lang: str = "fr") -> str:
    """Retourne un texte de secours formaté avec les prénoms et adapté au chiffre de compatibilité."""
    # Si on a un chiffre de compatibilité, utiliser le texte spécifique
    if compat_number and compat_number in FALLBACK_TEXTS_BY_NUMBER:
        return FALLBACK_TEXTS_BY_NUMBER[compat_number]
    # Sinon, utiliser le texte générique
    template = FALLBACK_TEXTS.get(lang, FALLBACK_TEXTS["fr"])
    return template.format(p1=prenom1, p2=prenom2)


async def generate_couple_detailed_analysis(prenom1: str, prenom2: str) -> dict:
    """
    Génère une analyse détaillée d'un couple basée sur:
    1. Calcul numérologique des prénoms et de l'année (TOUJOURS)
    2. Numérologie des prénoms (astrology-api.io) - OPTIONNEL
    3. Compatibilité numérique (astrology-api.io) - OPTIONNEL
    4. Texte enrichi généré par OpenAI - OPTIONNEL
    
    GARANTIT: Les données numériques calculées sont TOUJOURS retournées même si les APIs échouent.
    
    Returns:
        {
            "prenom1": str,
            "prenom2": str,
            "compatibility_number": int (1-9),  ✓ TOUJOURS
            "universal_year": int,               ✓ TOUJOURS
            "letters_prenom1": int,              ✓ TOUJOURS
            "letters_prenom2": int,              ✓ TOUJOURS
            "total_letters": int,                ✓ TOUJOURS
            "year": int,                         ✓ TOUJOURS
            "interpretation": dict,              ✓ TOUJOURS
            "numerology_1": dict,                (optionnel si astrology-api.io fail)
            "numerology_2": dict,                (optionnel si astrology-api.io fail)
            "compatibility": dict,               (optionnel si astrology-api.io fail)
            "personal_year": int,                ✓ TOUJOURS
            "mystery_text": str,                 (optionnel si OpenAI fail)
        }
    """
    try:
        if not prenom1 or not prenom2:
            return {}
        
        # 1. Calculer la compatibilité numérique (TOUJOURS - pas d'API externe)
        compat_calc = calculate_numerology_compatibility(prenom1, prenom2)
        compat_number = compat_calc["compatibility_number"]
        universal_year = compat_calc["universal_year"]
        letters1 = compat_calc["letters_prenom1"]
        letters2 = compat_calc["letters_prenom2"]
        total_letters = compat_calc["total_letters"]
        current_year = compat_calc["year"]
        
        # 2. Récupérer l'interprétation (TOUJOURS - données locales)
        interpretation = get_compatibility_interpretation(compat_number)
        
        # Préparer le résultat de base (GARANTIS même si APIs externes échouent)
        result = {
            "prenom1": prenom1,
            "prenom2": prenom2,
            "compatibility_number": compat_number,
            "universal_year": universal_year,
            "letters_prenom1": letters1,
            "letters_prenom2": letters2,
            "total_letters": total_letters,
            "year": current_year,
            "interpretation": interpretation,
            "personal_year": universal_year,
            "numerology_1": {},
            "numerology_2": {},
            "compatibility": {},
            "mystery_text": None,
        }
        
        # 3. Récupérer la numérologie de chaque prénom (OPTIONNEL - si API disponible)
        try:
            numer1 = await numerology_name(prenom1, 'fr')
            if numer1:
                result["numerology_1"] = numer1
                logger.info(f"[couple_detailed_analysis] numerology_name({prenom1}) OK")
        except Exception as e:
            logger.warning(f"[couple_detailed_analysis] numerology_name({prenom1}) failed: {e}")
        
        try:
            numer2 = await numerology_name(prenom2, 'fr')
            if numer2:
                result["numerology_2"] = numer2
                logger.info(f"[couple_detailed_analysis] numerology_name({prenom2}) OK")
        except Exception as e:
            logger.warning(f"[couple_detailed_analysis] numerology_name({prenom2}) failed: {e}")
        
        # 4. Récupérer la compatibilité (OPTIONNEL - si API disponible)
        try:
            compatibility = await numerology_compatibility(prenom1, prenom2, 'fr')
            if compatibility:
                result["compatibility"] = compatibility
                logger.info(f"[couple_detailed_analysis] numerology_compatibility OK")
        except Exception as e:
            logger.warning(f"[couple_detailed_analysis] numerology_compatibility failed: {e}")
        
        # 5. Générer le texte OpenAI (OPTIONNEL - si API disponible)
        try:
            prompt = f"""Tu es un astrologue français expert en numérologie amoureuse. 

Génère un texte court, élégant et raffiné (5-8 lignes maximum) basé sur le chiffre vibratoire du couple.

Couple: {prenom1} et {prenom2}
Chiffre vibratoire: {compat_number}
Signification: {interpretation.get('title', '')}
Énergie: {interpretation.get('energy', '')}
Points forts: {interpretation.get('strengths', '')}
Défi du couple: {interpretation.get('challenges', '')}

Le texte DOIT être:
- Poétique et inspirant
- Sans markdown (pas d'astérisques, pas de tirets)
- Sans emojis
- Raffiné et élégant
- Axé sur la vibration du chiffre {compat_number} et sa signification pour ce couple
- Parlé à la deuxième personne ("Vous", "Votre")
- Basé sur les forces et défis fournis

Génère un texte qui résonance avec la beauté du chiffre {compat_number}."""
            
            chat = LlmChat()
            response = await chat.send_message(UserMessage(text=prompt))
            mystery_text = response.strip() if response else None
            result["mystery_text"] = mystery_text or get_fallback_text(prenom1, prenom2, compat_number)
            logger.info(f"[couple_detailed_analysis] OpenAI text generation OK")
        except Exception as e:
            logger.warning(f"[couple_detailed_analysis] OpenAI generation failed: {e}")
            result["mystery_text"] = get_fallback_text(prenom1, prenom2, compat_number)
        
        return result
        
    except Exception as e:
        logger.error(f"[couple_detailed_analysis] CRITICAL error: {e}")
        # Calculer le chiffre même en cas d'erreur pour le fallback
        compat_calc = calculate_numerology_compatibility(prenom1, prenom2)
        compat_number = compat_calc.get("compatibility_number", 0)
        return {
            "prenom1": prenom1,
            "prenom2": prenom2,
            "mystery_text": get_fallback_text(prenom1, prenom2, compat_number),
            "error": str(e),
        }
