"""
Service pour générer un texte mystérieux et attractif sur un couple basé sur les prénoms.
Utilise OpenAI pour un paragraphe captivant qui donne envie de découvrir plus.
"""
import logging
from integrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


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


# Fallback si OpenAI ne répond pas
FALLBACK_TEXTS = {
    "fr": """Entre {p1} et {p2}, les prénoms eux-mêmes murmurent une histoire. 
    Les vibrations numériques qui dansent sous ces lettres ne sont jamais neutres. 
    Certaines énergies s'appellent, d'autres se révèlent seulement quand on sait les écouter.
    L'astrologie relationnelle révèle ce que les prénoms seuls ne peuvent qu'insinuer :
    la profondeur de ce lien, ses couleurs cachées, les défis qui le façonnent, 
    et surtout, le ciel qui veille sur vous deux."""
}


def get_fallback_text(prenom1: str, prenom2: str, lang: str = "fr") -> str:
    """Retourne un texte de secours formaté avec les prénoms."""
    template = FALLBACK_TEXTS.get(lang, FALLBACK_TEXTS["fr"])
    return template.format(p1=prenom1, p2=prenom2)
