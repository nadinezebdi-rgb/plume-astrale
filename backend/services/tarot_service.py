"""
Service Tarot - Oui/Non et Tarologie Médiumnité
"""
import hashlib
import os
import random
from datetime import datetime

_SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
# Bucket 'library' — 22 arcanes majeurs HD créés par Plume Astrale (2026-02).
# Format des fichiers : {slug}_{width}.png (widths disponibles : 512, 1080, 2048).
# On utilise la variante 1080 (parfaite pour affichage web mobile+desktop).
_TAROT_CDN_BASE = f"{_SUPABASE_URL}/storage/v1/object/public/library/tarot" if _SUPABASE_URL else "/api/assets/tarot"


def _tarot_img_url(filename: str) -> str:
    """URL publique CDN Supabase pour une carte de tarot (variante 1080px)."""
    if not filename:
        return ''
    return f"{_TAROT_CDN_BASE}/{filename}"


# 22 Arcanes Majeurs avec interprétations Oui/Non
ARCANES_TAROT = [
    {
        "numero": 0, "nom": "Le Mat",
        "oui": "Oui ! C'est le moment de faire ce saut de foi. L'univers soutient votre envol vers l'inconnu.",
        "non": "Pas encore. Le Mat vous invite à mieux vous préparer avant de vous lancer dans l'aventure.",
        "neutre": "La réponse est entre vos mains. Le Mat vous dit que le voyage compte plus que la destination.",
        "energie": "Liberté, nouveaux départs, spontanéité"
    },
    {
        "numero": 1, "nom": "Le Bateleur",
        "oui": "Oui, avec conviction ! Vous avez tous les outils en main. C'est le moment d'agir avec assurance.",
        "non": "Attention à ne pas disperser votre énergie. Concentrez-vous sur l'essentiel avant d'avancer.",
        "neutre": "Le Bateleur vous rappelle que votre pouvoir créateur est immense. Utilisez-le consciemment.",
        "energie": "Création, habileté, potentiel"
    },
    {
        "numero": 2, "nom": "La Papesse",
        "oui": "Oui, mais écoutez d'abord votre intuition profonde. La réponse est déjà en vous.",
        "non": "Le silence intérieur vous dit d'attendre. Des informations cachées doivent encore se révéler.",
        "neutre": "La Papesse vous invite à méditer avant de décider. La sagesse intérieure éclairera votre chemin.",
        "energie": "Intuition, mystère, sagesse intérieure"
    },
    {
        "numero": 3, "nom": "L'Impératrice",
        "oui": "Oui ! L'abondance et la créativité coulent vers vous. Accueillez cette bénédiction.",
        "non": "Ce n'est pas le bon moment. L'Impératrice vous demande de nourrir d'abord vos fondations.",
        "neutre": "L'Impératrice sourit. La réponse se révélera quand vous vous connecterez à votre nature profonde.",
        "energie": "Abondance, fertilité, nature"
    },
    {
        "numero": 4, "nom": "L'Empereur",
        "oui": "Oui, avec structure et discipline. Votre autorité naturelle vous mènera au succès.",
        "non": "La rigidité pourrait être un obstacle. L'Empereur vous invite à assouplir votre approche.",
        "neutre": "L'Empereur vous rappelle que le pouvoir véritable vient de la maîtrise de soi.",
        "energie": "Autorité, structure, stabilité"
    },
    {
        "numero": 5, "nom": "Le Pape",
        "oui": "Oui, suivez la voie de la sagesse. Un mentor ou un enseignement vous guidera.",
        "non": "Remettez en question les conventions. Le Pape vous invite à trouver votre propre vérité.",
        "neutre": "Le Pape suggère de chercher conseil auprès d'une personne de confiance avant de décider.",
        "energie": "Sagesse, tradition, guidance spirituelle"
    },
    {
        "numero": 6, "nom": "L'Amoureux",
        "oui": "Oui ! Suivez votre cœur. L'amour et l'harmonie guident cette décision.",
        "non": "Un choix difficile se présente. L'Amoureux vous dit de ne pas agir sous la pression émotionnelle.",
        "neutre": "L'Amoureux vous place face à un choix. La réponse viendra quand votre cœur et votre esprit seront alignés.",
        "energie": "Choix, amour, union"
    },
    {
        "numero": 7, "nom": "Le Chariot",
        "oui": "Oui, foncez ! La victoire vous attend. Votre détermination sera récompensée.",
        "non": "Maîtrisez d'abord vos émotions contradictoires. Le Chariot avance mieux quand les chevaux sont alignés.",
        "neutre": "Le Chariot vous rappelle que la volonté est votre meilleur moteur. Dirigez-la consciemment.",
        "energie": "Victoire, volonté, avancement"
    },
    {
        "numero": 8, "nom": "La Justice",
        "oui": "Oui, si votre conscience est en paix. La Justice favorise les actions équitables.",
        "non": "Quelque chose n'est pas équilibré. La Justice vous invite à rétablir l'harmonie d'abord.",
        "neutre": "La Justice pèse le pour et le contre. Prenez le temps d'évaluer toutes les conséquences.",
        "energie": "Équilibre, vérité, karma"
    },
    {
        "numero": 9, "nom": "L'Hermite",
        "oui": "Oui, mais prenez le temps de la réflexion. La solitude éclairera votre chemin.",
        "non": "L'Hermite vous dit de vous retirer et de méditer. Ce n'est pas le moment d'agir.",
        "neutre": "La lumière de l'Hermite brille dans l'obscurité. Cherchez en vous la réponse que vous attendez.",
        "energie": "Introspection, solitude, illumination"
    },
    {
        "numero": 10, "nom": "La Roue de Fortune",
        "oui": "Oui ! Les cycles tournent en votre faveur. Profitez de cette chance.",
        "non": "Le cycle actuel n'est pas favorable. Patientez, la Roue tourne toujours.",
        "neutre": "La Roue de Fortune tourne. Rien n'est permanent. Agissez en conscience du changement constant.",
        "energie": "Destin, cycles, opportunité"
    },
    {
        "numero": 11, "nom": "La Force",
        "oui": "Oui ! Votre force intérieure est immense. Faites confiance à votre courage silencieux.",
        "non": "Ne forcez rien. La vraie Force est dans la douceur et la patience.",
        "neutre": "La Force vous rappelle que la maîtrise de soi est plus puissante que la force brute.",
        "energie": "Courage, maîtrise, persévérance"
    },
    {
        "numero": 12, "nom": "Le Pendu",
        "oui": "Un oui inattendu ! Mais il demande un changement de perspective total.",
        "non": "Le Pendu vous invite à lâcher prise. Ce que vous voulez n'est peut-être pas ce dont vous avez besoin.",
        "neutre": "Suspendez votre jugement. Le Pendu vous enseigne que voir le monde autrement change tout.",
        "energie": "Lâcher-prise, sacrifice, nouvelle perspective"
    },
    {
        "numero": 13, "nom": "L'Arcane sans Nom",
        "oui": "Oui, à condition d'accepter la transformation profonde qui accompagne ce choix.",
        "non": "Quelque chose doit mourir avant que le nouveau puisse naître. Laissez partir l'ancien.",
        "neutre": "La transformation est inévitable. L'Arcane sans Nom vous dit que la fin est un commencement.",
        "energie": "Transformation, renaissance, fin d'un cycle"
    },
    {
        "numero": 14, "nom": "Tempérance",
        "oui": "Oui, avec modération et patience. L'harmonie est la clé du succès.",
        "non": "L'équilibre n'est pas encore atteint. Tempérance vous demande de modérer vos attentes.",
        "neutre": "Tempérance mélange les contraires. La réponse se trouve dans la voie du milieu.",
        "energie": "Équilibre, patience, guérison"
    },
    {
        "numero": 15, "nom": "Le Diable",
        "oui": "Oui, mais attention aux attachements et aux illusions. Restez lucide.",
        "non": "Le Diable vous met en garde contre une tentation. Libérez-vous de ce qui vous enchaîne.",
        "neutre": "Le Diable vous confronte à vos ombres. La réponse vient quand vous acceptez votre part sombre.",
        "energie": "Tentation, attachement, libération"
    },
    {
        "numero": 16, "nom": "La Maison Dieu",
        "oui": "Oui ! Même si le changement sera radical. La Maison Dieu détruit pour mieux reconstruire.",
        "non": "Un bouleversement se prépare. Ce n'est pas le moment de prendre des risques.",
        "neutre": "La Maison Dieu annonce un éclair de vérité. Préparez-vous à une révélation.",
        "energie": "Révélation, changement radical, vérité"
    },
    {
        "numero": 17, "nom": "L'Étoile",
        "oui": "Oui, absolument ! L'Étoile brille pour vous. Espoir, inspiration et bénédictions vous attendent.",
        "non": "L'espoir est là, mais le timing n'est pas encore parfait. L'Étoile vous dit de garder la foi.",
        "neutre": "L'Étoile vous baigne de lumière. Votre souhait est entendu par l'univers.",
        "energie": "Espoir, inspiration, sérénité"
    },
    {
        "numero": 18, "nom": "La Lune",
        "oui": "Oui, mais naviguez avec prudence. La Lune cache autant qu'elle révèle.",
        "non": "Des illusions brouillent votre vision. La Lune vous dit d'attendre que la brume se dissipe.",
        "neutre": "La Lune éclaire vos rêves. La réponse viendra à travers votre inconscient.",
        "energie": "Illusions, intuition, monde onirique"
    },
    {
        "numero": 19, "nom": "Le Soleil",
        "oui": "OUI ! Le Soleil brille de tout son éclat. Succès, joie et accomplissement vous attendent.",
        "non": "Même le Soleil dit rarement non. Peut-être cherchez-vous au mauvais endroit.",
        "neutre": "Le Soleil illumine tout. La réponse est claire et positive. Avancez avec confiance.",
        "energie": "Succès, joie, vitalité"
    },
    {
        "numero": 20, "nom": "Le Jugement",
        "oui": "Oui ! C'est un appel à l'action. Le Jugement vous libère du passé pour un nouveau chapitre.",
        "non": "Des comptes restent à régler avec le passé. Le Jugement vous demande de faire la paix d'abord.",
        "neutre": "Le Jugement sonne. Écoutez cet appel intérieur. Votre renaissance spirituelle est proche.",
        "energie": "Renaissance, appel, libération du passé"
    },
    {
        "numero": 21, "nom": "Le Monde",
        "oui": "Oui, magnifiquement ! Le Monde vous ouvre toutes les portes. Vous êtes en harmonie avec l'univers.",
        "non": "Vous êtes si proche de l'accomplissement. Le Monde vous dit de terminer ce que vous avez commencé.",
        "neutre": "Le Monde danse pour vous. L'accomplissement total est à portée de main.",
        "energie": "Accomplissement, plénitude, réalisation"
    },
]

# Thèmes de médiumnité pour la tarologie complète
THEMES_MEDIUMNITE = {
    "passe": [
        "Votre passé porte l'empreinte d'une âme ancienne. Les expériences vécues ont forgé une résilience rare.",
        "Des vies antérieures influencent encore vos schémas actuels. Une blessure karmique demande à être guérie.",
        "L'enfant intérieur que vous étiez porte encore des trésors inexploités. Reconnectez-vous à cette innocence.",
        "Un ancêtre veille sur vous depuis l'au-delà. Son énergie protectrice guide vos pas.",
        "Le karma de vos vies passées se résout progressivement. Vous êtes sur la voie de la libération.",
    ],
    "present": [
        "Votre aura vibre à une fréquence de transformation. Les énergies actuelles accélèrent votre évolution.",
        "Un guide spirituel essaie d'entrer en contact avec vous. Soyez attentif(ve) aux signes répétitifs.",
        "Votre chakra du cœur est en pleine expansion. L'amour inconditionnel devient votre vibration naturelle.",
        "Les synchronicités que vous vivez ne sont pas des coïncidences. Elles sont des confirmations de votre chemin.",
        "Une énergie de guérison circule en vous. Vous êtes capable de transmuter la douleur en sagesse.",
    ],
    "futur": [
        "Je vois une porte s'ouvrir dans les prochains mois. Une opportunité alignée avec votre mission d'âme.",
        "Un cycle de 7 ans s'achève. La prochaine phase apportera une croissance spirituelle accélérée.",
        "Une rencontre karmique est inscrite dans votre avenir proche. Elle transformera votre vision du monde.",
        "L'univers prépare un cadeau que vous n'osez même pas imaginer. Gardez votre cœur ouvert.",
        "Votre don médiumnique va se développer naturellement. Acceptez cette évolution avec confiance.",
    ],
    "conseil_ame": [
        "Votre âme vous demande de ralentir et d'écouter. Le silence est votre meilleur conseiller.",
        "Il est temps de poser des limites énergétiques saines. Protégez votre lumière intérieure.",
        "Votre mission dans cette vie est liée au service des autres. Mais servez d'abord votre propre guérison.",
        "L'authenticité est votre chemin de libération. Cessez de porter les masques qui ne vous appartiennent pas.",
        "Votre corps physique est un véhicule sacré. Honorez-le par des pratiques de purification régulières.",
    ],
}


# Mapping numéro d'arcane → nom de fichier CDN Supabase (bucket library/tarot).
# Variante 1080 = parfait équilibre poids/qualité pour affichage web.
TAROT_IMAGE_MAP = {
    0:  "00_le_mat_1080.png",
    1:  "01_le_bateleur_1080.png",
    2:  "02_la_papesse_1080.png",
    3:  "03_l_imperatrice_1080.png",
    4:  "04_l_empereur_1080.png",
    5:  "05_le_pape_1080.png",
    6:  "06_les_amoureux_1080.png",
    7:  "07_le_chariot_1080.png",
    8:  "08_la_justice_1080.png",
    9:  "09_l_hermite_1080.png",
    10: "10_la_roue_de_fortune_1080.png",
    11: "11_la_force_1080.png",
    12: "12_le_pendu_1080.png",
    13: "13_l_arcane_sans_nom_1080.png",
    14: "14_la_temperance_1080.png",
    15: "15_le_diable_1080.png",
    16: "16_la_maison_dieu_1080.png",
    17: "17_l_etoile_1080.png",
    18: "18_la_lune_1080.png",
    19: "19_le_soleil_1080.png",
    20: "20_le_jugement_1080.png",
    21: "21_le_monde_1080.png",
}


def tirage_oui_non(question: str) -> dict:
    """Tirage de tarot Oui/Non - tire une carte des arcanes majeurs"""
    seed = int(hashlib.md5(f"{question}-{datetime.now().isoformat()}".encode(), usedforsecurity=False).hexdigest(), 16)
    carte = ARCANES_TAROT[seed % len(ARCANES_TAROT)]

    # Determine answer type based on seed
    answer_type = seed % 3  # 0=oui, 1=non, 2=neutre
    if answer_type == 0:
        reponse = carte["oui"]
        orientation = "oui"
    elif answer_type == 1:
        reponse = carte["non"]
        orientation = "non"
    else:
        reponse = carte["neutre"]
        orientation = "neutre"

    # Cartes retournées — 35% de chance (le seed le décide)
    # Une carte retournée inverse partiellement le message : le "oui" clair
    # devient "oui mais avec réserve", le "non" devient "non pour l'instant".
    is_reversed = (seed // 7) % 100 < 35
    if is_reversed:
        reponse = _reversed_wrap(reponse, orientation)

    return {
        "question": question,
        "carte": {
            "numero": carte["numero"],
            "nom": carte["nom"],
            "energie": carte["energie"],
            "image": _tarot_img_url(TAROT_IMAGE_MAP.get(carte['numero'], '')),
            "is_reversed": is_reversed,
        },
        "orientation": orientation,
        "reponse": reponse,
        "date": datetime.now().isoformat(),
    }


def _reversed_wrap(base_message: str, orientation: str) -> str:
    """Ajoute une nuance de "carte retournée" au message initial.

    En cartomancie, une carte retournée n'inverse pas le sens (ce serait
    trop binaire) mais indique un blocage, une incarnation partielle,
    ou une leçon en cours d'intégration.
    """
    if orientation == "oui":
        prefix = "🔄 La carte apparaît retournée — un oui qui demande d'abord de lever un blocage intérieur. "
    elif orientation == "non":
        prefix = "🔄 La carte apparaît retournée — un non doux, plutôt qu'un refus catégorique. "
    else:
        prefix = "🔄 La carte apparaît retournée — l'énergie est présente mais latente, en attente d'être pleinement incarnée. "
    return prefix + base_message


def tirage_mediumnite_complet(prenom: str, date_naissance: str) -> dict:
    """Tirage de tarologie médiumnité complet - 7 cartes + lecture médiumnique"""
    seed = int(hashlib.md5(f"{prenom}-{date_naissance}-{datetime.now().date().isoformat()}".encode(), usedforsecurity=False).hexdigest(), 16)
    rng = random.Random(seed)

    # Tirer 7 cartes uniques
    indices = rng.sample(range(len(ARCANES_TAROT)), 7)
    cartes = [ARCANES_TAROT[i] for i in indices]

    positions = [
        "Votre essence profonde",
        "Les influences du passé",
        "Le présent et ses défis",
        "Les obstacles cachés",
        "L'énergie de guidance",
        "Le futur proche",
        "Le message de votre âme",
    ]

    tirage = []
    for i, (carte, position) in enumerate(zip(cartes, positions)):
        orientations = ["oui", "neutre", "non"]
        orient = orientations[rng.randint(0, 2)]
        tirage.append({
            "position": position,
            "carte": {
                "numero": carte["numero"],
                "nom": carte["nom"],
                "energie": carte["energie"],
                "image": _tarot_img_url(TAROT_IMAGE_MAP.get(carte['numero'], '')),
            },
            "message": carte[orient],
        })

    # Lecture médiumnique
    lecture = {
        "passe": rng.choice(THEMES_MEDIUMNITE["passe"]),
        "present": rng.choice(THEMES_MEDIUMNITE["present"]),
        "futur": rng.choice(THEMES_MEDIUMNITE["futur"]),
        "conseil_ame": rng.choice(THEMES_MEDIUMNITE["conseil_ame"]),
    }

    return {
        "prenom": prenom,
        "date_naissance": date_naissance,
        "tirage": tirage,
        "lecture_mediumnique": lecture,
        "date": datetime.now().isoformat(),
    }


def tirage_en_croix(prenom: str, date_naissance: str) -> dict:
    """Tirage en croix - 5 cartes avec interprétations selon la position"""
    from services.tarot_interpretations import INTERPRETATIONS_CROIX

    seed = int(hashlib.md5(f"{prenom}-{date_naissance}-croix-{datetime.now().date().isoformat()}".encode(), usedforsecurity=False).hexdigest(), 16)
    rng = random.Random(seed)

    # Tirer 5 cartes uniques
    indices = rng.sample(range(len(ARCANES_TAROT)), 5)
    cartes = [ARCANES_TAROT[i] for i in indices]

    # Les 5 positions du tirage en croix
    positions = [
        {"id": "centre", "nom": "La Situation Presente", "description": "Ce qui vous definit en ce moment"},
        {"id": "obstacle", "nom": "Ce Qui S'Oppose", "description": "Les obstacles et resistances"},
        {"id": "conseil", "nom": "Le Conseil", "description": "Ce qui peut vous aider"},
        {"id": "futur", "nom": "L'Aboutissement", "description": "Le futur proche et son potentiel"},
        {"id": "synthese", "nom": "La Synthese", "description": "Le fondement cache de la situation"},
    ]

    tirage = []
    for carte, position in zip(cartes, positions):
        numero = carte["numero"]
        interp = INTERPRETATIONS_CROIX.get(numero, {})
        position_id = position["id"]

        tirage.append({
            "position_id": position_id,
            "position_nom": position["nom"],
            "position_description": position["description"],
            "carte": {
                "numero": numero,
                "nom": carte["nom"],
                "energie": carte["energie"],
                "image": _tarot_img_url(TAROT_IMAGE_MAP.get(numero, '')),
                "mots_cles": interp.get("mots_cles", carte["energie"]),
                "description_arcane": interp.get("description", ""),
            },
            "interpretation": interp.get(position_id, ""),
        })

    # Lecture médiumnique complémentaire
    lecture = {
        "passe": rng.choice(THEMES_MEDIUMNITE["passe"]),
        "present": rng.choice(THEMES_MEDIUMNITE["present"]),
        "futur": rng.choice(THEMES_MEDIUMNITE["futur"]),
        "conseil_ame": rng.choice(THEMES_MEDIUMNITE["conseil_ame"]),
    }

    return {
        "prenom": prenom,
        "date_naissance": date_naissance,
        "type": "croix",
        "tirage": tirage,
        "lecture_mediumnique": lecture,
        "date": datetime.now().isoformat(),
    }


# ─── Croix Celtique 10 cartes — tirage complet ─────────────────────────────

# Les 10 positions traditionnelles de la Croix Celtique (Waite/Marseille)
CROIX_CELTIQUE_POSITIONS = [
    {"id": 1,  "nom": "Le Coeur",            "description": "Ta situation présente, ce qui te définit à cet instant."},
    {"id": 2,  "nom": "Le Défi",             "description": "L'obstacle qui traverse ton chemin (lu horizontalement, croise le coeur)."},
    {"id": 3,  "nom": "La Racine",           "description": "Le fondement inconscient qui nourrit cette situation."},
    {"id": 4,  "nom": "Le Passé Récent",     "description": "Ce qui vient de s'achever ou s'apprête à passer."},
    {"id": 5,  "nom": "Le Sommet",           "description": "Ton potentiel conscient — ce que tu peux atteindre."},
    {"id": 6,  "nom": "Le Futur Proche",     "description": "Ce qui approche dans les 3 prochains mois."},
    {"id": 7,  "nom": "Toi-Même",            "description": "Ta position intérieure vis-à-vis de la situation."},
    {"id": 8,  "nom": "L'Entourage",         "description": "L'influence des autres autour de toi."},
    {"id": 9,  "nom": "Espoirs & Craintes",  "description": "Ce que tu désires en secret ou ce que tu redoutes."},
    {"id": 10, "nom": "L'Issue Finale",      "description": "L'aboutissement probable si tu maintiens le cap."},
]


def tirage_croix_celtique(question: str, prenom: str = "") -> dict:
    """Tirage Croix Celtique complet — 10 cartes, chacune avec sa position.

    35% de chance qu'une carte donnée soit retournée (indépendamment).
    Le seed dépend de la question pour un résultat reproductible dans la journée.
    """
    from services.tarot_interpretations import INTERPRETATIONS_CROIX

    seed_str = f"{prenom or 'anon'}-{question}-celtique-{datetime.now().date().isoformat()}"
    seed = int(hashlib.md5(seed_str.encode(), usedforsecurity=False).hexdigest(), 16)
    rng = random.Random(seed)

    # 10 cartes uniques
    indices = rng.sample(range(len(ARCANES_TAROT)), 10)
    cartes = [ARCANES_TAROT[i] for i in indices]

    tirage = []
    for position, carte in zip(CROIX_CELTIQUE_POSITIONS, cartes):
        numero = carte["numero"]
        interp = INTERPRETATIONS_CROIX.get(numero, {})
        # 35% de chance carte retournée
        is_reversed = rng.random() < 0.35

        # Choisir un message : oui/neutre/non tourne selon position (positions 5,6,10 → futur/potentiel → plutôt oui)
        if position["id"] in (5, 6, 10):
            base_msg = carte["oui"] if not is_reversed else carte["neutre"]
        elif position["id"] in (2, 9):
            base_msg = carte["non"] if not is_reversed else carte["neutre"]
        else:
            base_msg = carte["neutre"]

        if is_reversed:
            orient = "neutre" if position["id"] not in (2, 9) else "non"
            base_msg = _reversed_wrap(base_msg, orient)

        tirage.append({
            "position_id": position["id"],
            "position_nom": position["nom"],
            "position_description": position["description"],
            "carte": {
                "numero": numero,
                "nom": carte["nom"],
                "energie": carte["energie"],
                "image": _tarot_img_url(TAROT_IMAGE_MAP.get(numero, '')),
                "mots_cles": interp.get("mots_cles", carte["energie"]),
                "is_reversed": is_reversed,
            },
            "interpretation": base_msg,
        })

    # Synthèse globale (les 3 cartes clés : coeur, sommet, issue)
    coeur = tirage[0]["carte"]["nom"]
    sommet = tirage[4]["carte"]["nom"]
    issue = tirage[9]["carte"]["nom"]
    synthese = (
        f"Ton tirage s'articule autour de {coeur}, éclairé par {sommet} et pointant vers {issue}. "
        f"Chaque carte retournée signale un blocage à lever, pas un mauvais présage — "
        f"la Croix Celtique montre le chemin, pas la destination."
    )

    return {
        "question": question,
        "prenom": prenom,
        "type": "croix_celtique",
        "tirage": tirage,
        "synthese": synthese,
        "date": datetime.now().isoformat(),
    }
