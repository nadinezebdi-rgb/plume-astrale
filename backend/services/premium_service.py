"""
Service Premium — Experience guidee en 5 etapes
Genere le contenu structure pour le parcours interactif Premium
"""
import logging
from datetime import datetime
from services.translation_service import translate_to_french

logger = logging.getLogger(__name__)


def _reduce(n):
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(d) for d in str(n))
    return n


def _calc_numerology(prenom, date_naissance):
    parts = date_naissance.split('-')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    letter_values = {
        'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
        'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
        's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
    }
    vowels = set('aeiouy')
    name_lower = prenom.lower()
    life_path = _reduce(day + month + year)
    expression = _reduce(sum(letter_values.get(c, 0) for c in name_lower if c.isalpha()))
    soul = _reduce(sum(letter_values.get(c, 0) for c in name_lower if c in vowels))
    personal_year = _reduce(day + month + 2026)
    return life_path, expression, soul, personal_year


def _get_zodiac(date_str):
    parts = date_str.split('-')
    month, day = int(parts[1]), int(parts[2])
    signs = [
        (1,20,'Capricorne'),(2,19,'Verseau'),(3,20,'Poissons'),(4,20,'Belier'),
        (5,21,'Taureau'),(6,21,'Gemeaux'),(7,23,'Cancer'),(8,23,'Lion'),
        (9,23,'Vierge'),(10,23,'Balance'),(11,22,'Scorpion'),(12,22,'Sagittaire'),
        (12,31,'Capricorne')
    ]
    for m, d, sign in signs:
        if month < m or (month == m and day <= d):
            return sign
    return 'Capricorne'


def _get_element(sign):
    elements = {
        'Belier':'Feu','Lion':'Feu','Sagittaire':'Feu',
        'Taureau':'Terre','Vierge':'Terre','Capricorne':'Terre',
        'Gemeaux':'Air','Balance':'Air','Verseau':'Air',
        'Cancer':'Eau','Scorpion':'Eau','Poissons':'Eau'
    }
    return elements.get(sign, 'Feu')


def _get_modality(sign):
    m = {
        'Belier':'Cardinal','Cancer':'Cardinal','Balance':'Cardinal','Capricorne':'Cardinal',
        'Taureau':'Fixe','Lion':'Fixe','Scorpion':'Fixe','Verseau':'Fixe',
        'Gemeaux':'Mutable','Vierge':'Mutable','Sagittaire':'Mutable','Poissons':'Mutable'
    }
    return m.get(sign, 'Cardinal')


CHEMIN_TITLES = {
    1:"Le Pionnier",2:"Le Diplomate",3:"L'Artiste",4:"Le Batisseur",
    5:"L'Aventurier",6:"Le Guerisseur",7:"Le Sage",8:"Le Leader",
    9:"L'Humanitaire",11:"L'Inspirateur",22:"Le Maitre Batisseur",33:"Le Guide Spirituel"
}

SIGN_FORCES = {
    'Belier': {'forces':['Initiative','Courage','Determination'],'tensions':['Impatience','Impulsivite','Besoin de controle']},
    'Taureau': {'forces':['Stabilite','Perseverance','Sensualite'],'tensions':['Resistance au changement','Possessivite','Entêtement']},
    'Gemeaux': {'forces':['Communication','Adaptabilite','Curiosite'],'tensions':['Dispersion','Superficialite','Instabilite']},
    'Cancer': {'forces':['Intuition','Protection','Sensibilite'],'tensions':['Hypersensibilite','Dependance emotionnelle','Repli sur soi']},
    'Lion': {'forces':['Generosite','Creativite','Leadership'],'tensions':['Orgueil','Besoin de reconnaissance','Dramatisation']},
    'Vierge': {'forces':['Analyse','Precision','Service'],'tensions':['Perfectionnisme','Autocritique','Anxiete']},
    'Balance': {'forces':['Harmonie','Diplomatie','Esthetisme'],'tensions':['Indecision','Dependance relationnelle','Evitement du conflit']},
    'Scorpion': {'forces':['Intensite','Transformation','Lucidite'],'tensions':['Obsession','Manipulation','Difficulte a lacher prise']},
    'Sagittaire': {'forces':['Vision','Optimisme','Liberté'],'tensions':['Excès','Impatience','Fuite de la réalité']},
    'Capricorne': {'forces':['Discipline','Ambition','Endurance'],'tensions':['Rigidite','Isolement emotionnel','Pessimisme']},
    'Verseau': {'forces':['Innovation','Independance','Humanisme'],'tensions':['Detachement','Rebellion','Imprevisibilite']},
    'Poissons': {'forces':['Empathie','Creativite','Spiritualite'],'tensions':['Confusion','Fuite','Absorption des emotions d\'autrui']},
}


async def generate_premium_content(user_data: dict) -> dict:
    """Generate the full 5-step premium reading"""
    prenom = user_data.get('prenom', 'Cher voyageur')
    date_naissance = user_data.get('dateNaissance', '1990-01-01')
    heure = user_data.get('heureNaissance', '12:00')
    ville = user_data.get('ville', 'Paris')

    sign = _get_zodiac(date_naissance)
    element = _get_element(sign)
    modality = _get_modality(sign)
    sign_data = SIGN_FORCES.get(sign, SIGN_FORCES['Belier'])
    life_path, expression, soul, personal_year = _calc_numerology(prenom, date_naissance)

    # Generate LLM-powered deep interpretations
    llm_prompts = {
        "fondement": f"En 3 paragraphes poétiques et profonds (150 mots max), ecris une synthèse du thème natal pour un {sign} (element {element}, modalité {modality}) avec ascendant probable base sur l'heure {heure}. Forces: {', '.join(sign_data['forces'])}. Tensions: {', '.join(sign_data['tensions'])}. Prenom: {prenom}. Tutoie le lecteur. Ton: bienveillant, structure, symbolique. Ne mentionne pas que c'est une estimation.",
        "chemin_ame": f"En 3 paragraphes (150 mots max), relie le chemin de vie {life_path} ({CHEMIN_TITLES.get(life_path, '')}) avec le signe {sign} de {prenom}. Explique comment ce nombre influence ses decisions et se manifeste dans ses cycles de vie. Tutoie. Ton: profond, éclairant, pas fataliste.",
        "cycle": f"En 3 paragraphes (150 mots max), analyse le cycle actuel de {prenom} ({sign}, chemin de vie {life_path}, annee personnelle {personal_year}) en mars 2026. Quels sont les transits dominants symboliques? Quel axe clarifier? Quel conseil symbolique? Tutoie. Ton: actuel, concret, responsable.",
        "schemas": f"En 3 paragraphes (150 mots max), identifie les schemas repetitifs typiques d'un {sign} avec chemin de vie {life_path} et nombre d'expression {expression}. Ce qui revient, ce que cela revele, ce que cela invite a transformer. Pour {prenom}. Tutoie. Ton: lucide mais bienveillant.",
        "projection": f"En 4-5 paragraphes (200 mots max), projette les 12 prochains mois (mars 2026 a fevrier 2027) pour {prenom} ({sign}, annee personnelle {personal_year}, chemin de vie {life_path}). Identifie 2-3 periodes sensibles, 2 fenetres d'ouverture, les mouvements progressifs. Tutoie. Ton: responsable, pas predictif, symbolique."
    }

    interpretations = {}
    for key, prompt in llm_prompts.items():
        try:
            result = await translate_to_french(prompt)
            # translate_to_french uses LLM, so actually we call it differently
            # We need a direct LLM call here
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            import os
            chat = LlmChat(
                api_key=os.environ.get("EMERGENT_LLM_KEY"),
                session_id=f"premium_{key}_{prenom[:3]}",
                system_message="Tu es un astrologue expert et bienveillant. Tu rédiges des lectures astrologiques personnalisées pour la plateforme Plume Astrale. Ton style est poétique, structuré, responsable. Tu ne prédis pas l'avenir, tu éclaires des dynamiques. Tu tutoies le lecteur."
            )
            chat.with_model("openai", "gpt-4o-mini")
            msg = UserMessage(text=prompt)
            response = await chat.send_message(msg)
            interpretations[key] = response.strip() if response else ""
        except Exception as e:
            logger.error(f"LLM error for {key}: {e}")
            interpretations[key] = ""

    # Build the 5-step structure
    steps = {
        "step_1_fondement": {
            "title": "Votre Fondement",
            "subtitle": "Les forces et tensions qui vous definissent",
            "signe": sign,
            "element": element,
            "modalite": modality,
            "forces": sign_data['forces'],
            "tensions": sign_data['tensions'],
            "interpretation": interpretations.get("fondement", ""),
            "reflection": "Cela resonne-t-il avec votre vecu actuel ?"
        },
        "step_2_chemin_ame": {
            "title": "Votre Chemin d'Ame",
            "subtitle": "Le nombre qui guide votre trajectoire",
            "chemin_de_vie": life_path,
            "titre_chemin": CHEMIN_TITLES.get(life_path, "Le Voyageur"),
            "nombre_expression": expression,
            "nombre_ame": soul,
            "interpretation": interpretations.get("chemin_ame", ""),
            "reflection": "Comment ce nombre se manifeste-t-il dans vos choix ?"
        },
        "step_3_cycle": {
            "title": "Votre Cycle Actuel",
            "subtitle": "Les mouvements de cette période",
            "annee_personnelle": personal_year,
            "periode": "Mars 2026",
            "interpretation": interpretations.get("cycle", ""),
            "reflection": "Quel element resonne le plus avec votre situation ?"
        },
        "step_4_schemas": {
            "title": "Vos Schemas Repetitifs",
            "subtitle": "Ce qui revient et ce que cela revele",
            "interpretation": interpretations.get("schemas", ""),
            "reflection": "Reconnaissez-vous ces mecanismes dans votre parcours ?"
        },
        "step_5_projection": {
            "title": "Projection 12 Mois",
            "subtitle": "Mars 2026 - Fevrier 2027",
            "interpretation": interpretations.get("projection", ""),
            "reflection": "Quels reperes souhaitez-vous garder en memoire ?"
        }
    }

    return {
        "prenom": prenom,
        "signe": sign,
        "date_naissance": date_naissance,
        "generated_at": datetime.now().isoformat(),
        "steps": steps
    }
