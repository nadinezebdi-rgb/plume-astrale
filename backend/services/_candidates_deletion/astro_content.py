"""
Contenu astrologique riche pour le manuscrit
Textes détaillés par signe, planète, maison, et prévisions
"""

# ============= SIGNES ZODIACAUX =============

SIGNES_DETAILS = {
    "Aries": {
        "nom_fr": "Bélier",
        "element": "Feu",
        "qualité": "Cardinal",
        "planete": "Mars",
        "symbole": "♈",
        "dates": "21 mars - 19 avril",
        "description_courte": "Premier signe du zodiaque, le Bélier incarne l'énergie primordiale du commencement.",
        "description_longue": """Le Bélier est le pionnier du zodiaque, celui qui ouvre la voie avec audace et détermination. 
Gouverné par Mars, planète de l'action et du courage, vous possédez une énergie vitale exceptionnelle. 
Votre nature impulsive vous pousse à agir plutôt qu'à attendre, à créer plutôt qu'à suivre.

Vous êtes né(e) pour initier, pour être le premier à franchir les obstacles. Cette flamme intérieure 
qui vous anime est votre plus grande force. Elle vous permet de surmonter les défis que d'autres 
jugeraient insurmontables.

Cependant, cette même énergie peut parfois vous pousser à l'impatience. Apprenez à canaliser 
votre feu intérieur : il peut réchauffer ou brûler, selon la façon dont vous le dirigez.""",
        "forces": ["Courage", "Initiative", "Honnêteté", "Enthousiasme", "Leadership"],
        "defis": ["Impatience", "Impulsivité", "Tendance à l'égocentrisme"],
        "conseil_annee": "2026 vous invite à canaliser votre énergie vers des projets durables.",
        "affirmation": "Je suis le feu qui éclaire le chemin. Ma volonté forge ma destinée."
    },
    "Taurus": {
        "nom_fr": "Taureau",
        "element": "Terre",
        "qualité": "Fixe",
        "planete": "Vénus",
        "symbole": "♉",
        "dates": "20 avril - 20 mai",
        "description_courte": "Le Taureau incarne la stabilité, la sensualité et l'ancrage terrestre.",
        "description_longue": """Le Taureau est le bâtisseur du zodiaque, celui qui transforme les rêves en réalités tangibles.
Gouverné par Vénus, planète de l'amour et de la beauté, vous avez un sens inné de l'esthétique 
et une profonde connexion avec les plaisirs de la vie.

Votre force réside dans votre persévérance. Là où d'autres abandonnent, vous continuez, 
pierre après pierre, jusqu'à construire votre cathédrale. Cette ténacité est votre signature cosmique.

Vous avez besoin de sécurité, tant matérielle qu'émotionnelle. Ce n'est pas une faiblesse, 
c'est la fondation sur laquelle vous construisez votre vie. Honorez ce besoin tout en 
restant ouvert au changement quand il se présente.""",
        "forces": ["Persévérance", "Fiabilité", "Sens pratique", "Patience", "Loyauté"],
        "defis": ["Résistance au changement", "Possessivité", "Entêtement"],
        "conseil_annee": "2026 vous encourage à sortir de votre zone de confort en douceur.",
        "affirmation": "Je suis la terre fertile. Ma patience fait fleurir l'abondance."
    },
    "Gemini": {
        "nom_fr": "Gémeaux",
        "element": "Air",
        "qualité": "Mutable",
        "planete": "Mercure",
        "symbole": "♊",
        "dates": "21 mai - 20 juin",
        "description_courte": "Les Gémeaux représentent la dualité, la communication et la curiosité intellectuelle.",
        "description_longue": """Les Gémeaux sont les messagers du zodiaque, porteurs de mots, d'idées et de connexions.
Gouverné par Mercure, planète de la communication et de l'intellect, votre esprit est 
un papillon qui butine le nectar de toutes les connaissances.

Votre curiosité est insatiable. Vous avez besoin de stimulation mentale comme d'autres 
ont besoin d'air pour respirer. Cette soif d'apprendre fait de vous un éternel étudiant de la vie.

La dualité de votre signe n'est pas un défaut, c'est une richesse. Vous pouvez voir 
les deux côtés de chaque situation, comprendre des perspectives opposées. Cette flexibilité 
mentale est un don précieux dans un monde en constante évolution.""",
        "forces": ["Adaptabilité", "Communication", "Curiosité", "Polyvalence", "Sociabilité"],
        "defis": ["Dispersion", "Superficialité", "Inconstance"],
        "conseil_annee": "2026 vous invite à approfondir plutôt qu'à multiplier les intérêts.",
        "affirmation": "Je suis le vent qui porte les idées. Ma versatilité est ma force."
    },
    "Cancer": {
        "nom_fr": "Cancer",
        "element": "Eau",
        "qualité": "Cardinal",
        "planete": "Lune",
        "symbole": "♋",
        "dates": "21 juin - 22 juillet",
        "description_courte": "Le Cancer incarne la sensibilité, la protection et le monde émotionnel.",
        "description_longue": """Le Cancer est le gardien du foyer zodiacal, celui qui crée des refuges de tendresse.
Gouverné par la Lune, astre des émotions et de l'intuition, vous êtes profondément connecté 
aux cycles de la vie et aux marées de l'âme.

Votre sensibilité n'est pas une faiblesse mais un superpouvoir. Vous percevez ce que 
les autres ne voient pas, ressentez ce qui reste non-dit. Cette empathie fait de vous 
un guérisseur naturel, un confident précieux.

Votre carapace protège un cœur immense. N'ayez pas peur de la vulnérabilité : 
c'est elle qui permet les connexions les plus profondes. Votre capacité à nourrir 
les autres est votre plus beau cadeau au monde.""",
        "forces": ["Empathie", "Intuition", "Protection", "Mémoire", "Fidélité"],
        "defis": ["Hypersensibilité", "Tendance à ruminer", "Possessivité émotionnelle"],
        "conseil_annee": "2026 vous encourage à établir des limites saines tout en restant ouvert.",
        "affirmation": "Je suis l'océan qui accueille. Ma sensibilité est ma sagesse."
    },
    "Leo": {
        "nom_fr": "Lion",
        "element": "Feu",
        "qualité": "Fixe",
        "planete": "Soleil",
        "symbole": "♌",
        "dates": "23 juillet - 22 août",
        "description_courte": "Le Lion rayonne de créativité, de générosité et de noblesse d'âme.",
        "description_longue": """Le Lion est le roi du zodiaque, non par domination mais par rayonnement.
Gouverné par le Soleil, centre de notre système solaire, vous êtes destiné à briller 
et à réchauffer ceux qui vous entourent.

Votre générosité est légendaire. Vous donnez sans compter, que ce soit votre temps, 
votre amour ou vos ressources. Cette noblesse de cœur inspire les autres à donner le meilleur d'eux-mêmes.

Le Lion a besoin de reconnaissance, et c'est parfaitement légitime. Vous donnez tellement 
que recevoir des éloges nourrit votre flamme intérieure. N'ayez pas honte de ce besoin : 
il fait partie de votre nature solaire.""",
        "forces": ["Générosité", "Créativité", "Leadership", "Loyauté", "Enthousiasme"],
        "defis": ["Orgueil", "Besoin excessif d'attention", "Dramatisation"],
        "conseil_annee": "2026 vous invite à briller en illuminant les autres plutôt qu'en cherchant la lumière.",
        "affirmation": "Je suis le Soleil qui réchauffe. Ma lumière révèle la beauté en chacun."
    },
    "Virgo": {
        "nom_fr": "Vierge",
        "element": "Terre",
        "qualité": "Mutable",
        "planete": "Mercure",
        "symbole": "♍",
        "dates": "23 août - 22 septembre",
        "description_courte": "La Vierge incarne la précision, le service et la quête de perfection.",
        "description_longue": """La Vierge est l'alchimiste du zodiaque, celui qui transforme le chaos en ordre.
Gouverné par Mercure dans son aspect analytique, vous possédez un esprit remarquablement 
précis et une capacité d'observation hors du commun.

Votre don pour les détails n'est pas de la maniaquerie, c'est de l'artisanat. 
Vous voyez les imperfections non pour critiquer mais pour améliorer, pour raffiner, 
pour élever ce qui vous entoure vers l'excellence.

Le service est votre voie royale vers l'épanouissement. Vous trouvez votre joie 
dans l'utilité, dans la contribution significative. Cette humilité est votre force secrète.""",
        "forces": ["Analyse", "Précision", "Dévouement", "Discernement", "Praticité"],
        "defis": ["Perfectionnisme", "Auto-critique excessive", "Anxiété"],
        "conseil_annee": "2026 vous rappelle que l'imperfection est aussi une forme de beauté.",
        "affirmation": "Je suis la main qui perfectionne. Mon attention aux détails crée l'harmonie."
    },
    "Libra": {
        "nom_fr": "Balance",
        "element": "Air",
        "qualité": "Cardinal",
        "planete": "Vénus",
        "symbole": "♎",
        "dates": "23 septembre - 22 octobre",
        "description_courte": "La Balance recherche l'équilibre, l'harmonie et la beauté des relations.",
        "description_longue": """La Balance est le diplomate du zodiaque, celui qui tisse les liens et apaise les conflits.
Gouverné par Vénus dans son aspect relationnel, vous êtes naturellement attiré par 
la beauté sous toutes ses formes et par l'harmonie dans les rapports humains.

Votre quête d'équilibre n'est pas de l'indécision, c'est de la sagesse. Vous comprenez 
que chaque perspective a sa valeur, que la vérité se trouve souvent au milieu.

Les relations sont votre terrain d'apprentissage. À travers l'autre, vous vous découvrez 
vous-même. Cette interdépendance n'est pas une faiblesse, c'est la reconnaissance 
de notre nature profondément sociale.""",
        "forces": ["Diplomatie", "Sens esthétique", "Équité", "Charme", "Sociabilité"],
        "defis": ["Indécision", "Dépendance relationnelle", "Évitement des conflits"],
        "conseil_annee": "2026 vous encourage à prendre position, même si cela crée des vagues.",
        "affirmation": "Je suis la balance qui harmonise. Mon sens de la justice crée la paix."
    },
    "Scorpio": {
        "nom_fr": "Scorpion",
        "element": "Eau",
        "qualité": "Fixe",
        "planete": "Pluton (Mars)",
        "symbole": "♏",
        "dates": "23 octobre - 21 novembre",
        "description_courte": "Le Scorpion explore les profondeurs, la transformation et le pouvoir de la régénération.",
        "description_longue": """Le Scorpion est le phénix du zodiaque, celui qui meurt et renaît sans cesse de ses cendres.
Gouverné par Pluton, planète de la transformation profonde, vous êtes destiné à explorer 
les mystères de l'existence que d'autres préfèrent ignorer.

Votre intensité n'est pas un défaut, c'est votre façon d'être vivant. Vous ne pouvez pas 
faire les choses à moitié : tout ou rien, c'est votre devise. Cette passion absolue 
est ce qui vous permet de réaliser l'impossible.

La transformation est votre essence même. Chaque épreuve traversée vous rend plus fort, 
plus sage, plus puissant. Vous êtes l'alchimiste qui transforme le plomb en or.""",
        "forces": ["Intensité", "Perspicacité", "Résilience", "Loyauté absolue", "Magnétisme"],
        "defis": ["Jalousie", "Rancune", "Tendance au contrôle"],
        "conseil_annee": "2026 vous invite à libérer ce qui ne vous sert plus pour renaître.",
        "affirmation": "Je suis le phénix qui renaît. Ma transformation inspire le monde."
    },
    "Sagittarius": {
        "nom_fr": "Sagittaire",
        "element": "Feu",
        "qualité": "Mutable",
        "planete": "Jupiter",
        "symbole": "♐",
        "dates": "22 novembre - 21 décembre",
        "description_courte": "Le Sagittaire incarne l'aventure, la philosophie et l'expansion de l'esprit.",
        "description_longue": """Le Sagittaire est l'explorateur du zodiaque, l'archer qui vise toujours plus haut.
Gouverné par Jupiter, planète de l'expansion et de la chance, vous êtes béni d'un 
optimisme naturel et d'une soif d'aventure insatiable.

Votre quête n'est pas seulement géographique, elle est philosophique. Vous cherchez 
le sens de la vie, la vérité universelle, la sagesse qui transcende les cultures.

La liberté est votre oxygène. Vous avez besoin d'espace pour déployer vos ailes, 
d'horizons larges pour nourrir votre âme. Cette indépendance n'est pas de l'égoïsme, 
c'est la condition de votre épanouissement.""",
        "forces": ["Optimisme", "Générosité", "Honnêteté", "Aventure", "Philosophie"],
        "defis": ["Excès", "Impatience", "Manque de tact"],
        "conseil_annee": "2026 vous encourage à trouver l'aventure dans le quotidien.",
        "affirmation": "Je suis la flèche qui vise les étoiles. Ma quête de sens illumine le chemin."
    },
    "Capricorn": {
        "nom_fr": "Capricorne",
        "element": "Terre",
        "qualité": "Cardinal",
        "planete": "Saturne",
        "symbole": "♑",
        "dates": "22 décembre - 19 janvier",
        "description_courte": "Le Capricorne représente l'ambition, la discipline et la maîtrise du temps.",
        "description_longue": """Le Capricorne est l'architecte du zodiaque, celui qui construit des empires durables.
Gouverné par Saturne, planète de la structure et de la discipline, vous comprenez 
que les grandes réalisations demandent du temps, de la patience et de la persévérance.

Votre ambition n'est pas de l'arrivisme, c'est la conscience de votre potentiel. 
Vous savez que vous êtes capable de grandes choses, et vous êtes prêt à fournir 
les efforts nécessaires pour y parvenir.

Le temps est votre allié. Contrairement aux signes impatients, vous comprenez que 
les meilleures choses se construisent lentement. Cette sagesse temporelle est votre avantage secret.""",
        "forces": ["Discipline", "Ambition", "Responsabilité", "Pragmatisme", "Patience"],
        "defis": ["Pessimisme", "Rigidité", "Workaholicisme"],
        "conseil_annee": "2026 vous rappelle d'équilibrer ambition et plaisirs de la vie.",
        "affirmation": "Je suis la montagne qui s'élève. Ma persévérance atteint les sommets."
    },
    "Aquarius": {
        "nom_fr": "Verseau",
        "element": "Air",
        "qualité": "Fixe",
        "planete": "Uranus (Saturne)",
        "symbole": "♒",
        "dates": "20 janvier - 18 février",
        "description_courte": "Le Verseau incarne l'innovation, l'humanisme et la vision du futur.",
        "description_longue": """Le Verseau est le visionnaire du zodiaque, celui qui voit le monde tel qu'il pourrait être.
Gouverné par Uranus, planète de l'innovation et de la révolution, vous êtes en avance 
sur votre temps, porteur d'idées qui ne seront comprises que demain.

Votre différence n'est pas une anomalie, c'est votre mission. Vous êtes ici pour 
bousculer les conventions, pour questionner ce qui semble acquis, pour ouvrir 
des portes que d'autres ne voient même pas.

L'humanité est votre famille. Au-delà des liens du sang, vous ressentez une 
connexion avec l'ensemble de l'espèce humaine. Cette conscience collective 
fait de vous un agent du changement positif.""",
        "forces": ["Originalité", "Humanisme", "Indépendance", "Innovation", "Objectivité"],
        "defis": ["Détachement émotionnel", "Excentricité excessive", "Rébellion gratuite"],
        "conseil_annee": "2026 vous invite à ancrer vos visions dans la réalité concrète.",
        "affirmation": "Je suis l'étoile qui guide. Mon originalité ouvre de nouveaux chemins."
    },
    "Pisces": {
        "nom_fr": "Poissons",
        "element": "Eau",
        "qualité": "Mutable",
        "planete": "Neptune (Jupiter)",
        "symbole": "♓",
        "dates": "19 février - 20 mars",
        "description_courte": "Les Poissons naviguent entre les mondes, porteurs de rêves et de compassion universelle.",
        "description_longue": """Les Poissons sont les mystiques du zodiaque, ceux qui dissolvent les frontières entre visible et invisible.
Gouverné par Neptune, planète des rêves et de la spiritualité, vous avez accès à des 
dimensions de la réalité que d'autres ignorent.

Votre sensibilité est un portail vers l'infini. Vous percevez la beauté cachée, 
entendez la musique des sphères, ressentez les courants invisibles qui relient tous les êtres.

Dernier signe du zodiaque, vous portez en vous la sagesse de tous les signes qui précèdent. 
Cette conscience universelle fait de vous un pont entre les mondes, un guérisseur de l'âme.""",
        "forces": ["Compassion", "Intuition", "Créativité", "Spiritualité", "Adaptabilité"],
        "defis": ["Évasion de la réalité", "Victimisation", "Confusion"],
        "conseil_annee": "2026 vous encourage à ancrer vos rêves dans la matière.",
        "affirmation": "Je suis l'océan qui unit. Ma compassion guérit les âmes blessées."
    }
}

# ============= PLANÈTES =============

PLANETES_DETAILS = {
    "Sun": {
        "nom_fr": "Soleil",
        "symbole": "☉",
        "domaine": "Identité, ego, vitalité, père",
        "cycle": "1 an",
        "description": "Le Soleil représente votre essence fondamentale, qui vous êtes au plus profond de vous-même. Il éclaire votre chemin de vie et révèle votre potentiel le plus lumineux.",
        "en_signe": {
            "Aries": "Votre identité est forgée dans l'action et l'initiative. Vous brillez quand vous êtes le premier, le pionnier.",
            "Taurus": "Votre identité s'ancre dans la stabilité et la sensualité. Vous brillez en construisant des choses durables.",
            "Gemini": "Votre identité s'exprime à travers la communication. Vous brillez quand vous partagez des idées.",
            "Cancer": "Votre identité se nourrit des émotions et du foyer. Vous brillez en prenant soin des autres.",
            "Leo": "Votre identité rayonne naturellement. Vous êtes né(e) pour briller et inspirer.",
            "Virgo": "Votre identité se définit par le service et la précision. Vous brillez dans le perfectionnement.",
            "Libra": "Votre identité s'épanouit dans les relations. Vous brillez en créant l'harmonie.",
            "Scorpio": "Votre identité se forge dans la transformation. Vous brillez en révélant les vérités cachées.",
            "Sagittarius": "Votre identité est celle de l'explorateur. Vous brillez en élargissant les horizons.",
            "Capricorn": "Votre identité se construit avec le temps. Vous brillez en atteignant les sommets.",
            "Aquarius": "Votre identité défie les conventions. Vous brillez en étant unique.",
            "Pisces": "Votre identité transcende les limites. Vous brillez en connectant les mondes."
        }
    },
    "Moon": {
        "nom_fr": "Lune",
        "symbole": "☽",
        "domaine": "Émotions, intuition, mère, besoins",
        "cycle": "28 jours",
        "description": "La Lune révèle votre monde intérieur, vos besoins émotionnels et votre façon instinctive de réagir à la vie.",
        "en_signe": {
            "Aries": "Vos émotions sont vives et immédiates. Vous avez besoin d'action pour vous sentir en vie.",
            "Taurus": "Vos émotions cherchent la sécurité. Vous avez besoin de stabilité pour vous épanouir.",
            "Gemini": "Vos émotions passent par l'intellect. Vous avez besoin de stimulation mentale.",
            "Cancer": "Vos émotions sont profondes et protectrices. Vous avez besoin d'intimité.",
            "Leo": "Vos émotions sont expressives et chaleureuses. Vous avez besoin de reconnaissance.",
            "Virgo": "Vos émotions cherchent l'utilité. Vous avez besoin de vous sentir utile.",
            "Libra": "Vos émotions recherchent l'harmonie. Vous avez besoin d'équilibre relationnel.",
            "Scorpio": "Vos émotions sont intenses et profondes. Vous avez besoin de vérité.",
            "Sagittarius": "Vos émotions sont optimistes et libres. Vous avez besoin d'espace.",
            "Capricorn": "Vos émotions sont contrôlées et responsables. Vous avez besoin de structure.",
            "Aquarius": "Vos émotions sont détachées et universelles. Vous avez besoin de liberté.",
            "Pisces": "Vos émotions sont illimitées et empathiques. Vous avez besoin de connexion spirituelle."
        }
    },
    "Mercury": {
        "nom_fr": "Mercure",
        "symbole": "☿",
        "domaine": "Communication, intellect, apprentissage",
        "cycle": "88 jours",
        "description": "Mercure gouverne votre façon de penser, de communiquer et d'apprendre. Il révèle le fonctionnement de votre esprit."
    },
    "Venus": {
        "nom_fr": "Vénus",
        "symbole": "♀",
        "domaine": "Amour, beauté, valeurs, argent",
        "cycle": "225 jours",
        "description": "Vénus révèle votre façon d'aimer et d'être aimé(e), vos goûts esthétiques et ce que vous valorisez dans la vie."
    },
    "Mars": {
        "nom_fr": "Mars",
        "symbole": "♂",
        "domaine": "Action, désir, énergie, combat",
        "cycle": "687 jours",
        "description": "Mars représente votre énergie vitale, votre façon d'agir et de vous affirmer face aux défis de la vie."
    },
    "Jupiter": {
        "nom_fr": "Jupiter",
        "symbole": "♃",
        "domaine": "Expansion, chance, sagesse, voyages",
        "cycle": "12 ans",
        "description": "Jupiter est la grande bénédiction, indiquant où vous trouvez l'abondance et l'expansion dans votre vie."
    },
    "Saturn": {
        "nom_fr": "Saturne",
        "symbole": "♄",
        "domaine": "Structure, discipline, karma, temps",
        "cycle": "29 ans",
        "description": "Saturne représente vos leçons de vie, les domaines où vous devez développer discipline et maturité."
    },
    "Uranus": {
        "nom_fr": "Uranus",
        "symbole": "♅",
        "domaine": "Innovation, révolution, originalité",
        "cycle": "84 ans",
        "description": "Uranus indique où vous êtes appelé(e) à être unique, à innover et à briser les conventions."
    },
    "Neptune": {
        "nom_fr": "Neptune",
        "symbole": "♆",
        "domaine": "Rêves, spiritualité, illusion, art",
        "cycle": "165 ans",
        "description": "Neptune révèle votre connexion au divin, vos rêves les plus profonds et votre créativité spirituelle."
    },
    "Pluto": {
        "nom_fr": "Pluton",
        "symbole": "♇",
        "domaine": "Transformation, pouvoir, renaissance",
        "cycle": "248 ans",
        "description": "Pluton indique où vous vivrez les transformations les plus profondes et les renaissances les plus puissantes."
    }
}

# ============= MAISONS ASTROLOGIQUES =============

MAISONS_DETAILS = {
    1: {
        "nom": "Maison I - L'Ascendant",
        "domaine": "Personnalité, apparence, approche de la vie",
        "description": "La première maison représente votre masque social, la façon dont vous vous présentez au monde. Une planète ici colore fortement votre personnalité visible."
    },
    2: {
        "nom": "Maison II - Les Ressources",
        "domaine": "Argent, possessions, valeurs personnelles",
        "description": "La deuxième maison révèle votre rapport à l'argent et aux possessions matérielles, ainsi que ce que vous valorisez profondément."
    },
    3: {
        "nom": "Maison III - La Communication",
        "domaine": "Communication, frères/sœurs, déplacements courts",
        "description": "La troisième maison gouverne votre façon de communiquer, votre environnement immédiat et vos relations avec votre fratrie."
    },
    4: {
        "nom": "Maison IV - Le Foyer",
        "domaine": "Famille, racines, foyer, père/mère",
        "description": "La quatrième maison représente vos racines, votre foyer et votre héritage familial. C'est le fondement de votre être."
    },
    5: {
        "nom": "Maison V - La Créativité",
        "domaine": "Créativité, romance, enfants, plaisirs",
        "description": "La cinquième maison est celle de l'expression créative, des romances et de la joie de vivre. Elle révèle comment vous vous amusez."
    },
    6: {
        "nom": "Maison VI - Le Service",
        "domaine": "Travail quotidien, santé, service",
        "description": "La sixième maison concerne votre travail quotidien, votre santé et votre désir de servir. Elle montre votre rapport au devoir."
    },
    7: {
        "nom": "Maison VII - Les Partenariats",
        "domaine": "Mariage, associations, ennemis déclarés",
        "description": "La septième maison représente vos partenariats significatifs, le mariage et la façon dont vous vous reliez aux autres en tête-à-tête."
    },
    8: {
        "nom": "Maison VIII - La Transformation",
        "domaine": "Mort/renaissance, sexualité, ressources partagées",
        "description": "La huitième maison gouverne les transformations profondes, la sexualité et les ressources partagées avec d'autres."
    },
    9: {
        "nom": "Maison IX - L'Expansion",
        "domaine": "Philosophie, voyages lointains, études supérieures",
        "description": "La neuvième maison représente votre quête de sens, les voyages qui élargissent l'esprit et la philosophie de vie."
    },
    10: {
        "nom": "Maison X - La Carrière",
        "domaine": "Carrière, réputation, ambitions, père/mère",
        "description": "La dixième maison révèle vos ambitions professionnelles, votre réputation publique et votre destinée sociale."
    },
    11: {
        "nom": "Maison XI - Les Aspirations",
        "domaine": "Amis, groupes, espoirs, projets humanitaires",
        "description": "La onzième maison concerne vos amitiés, vos espoirs pour l'avenir et votre contribution à la société."
    },
    12: {
        "nom": "Maison XII - L'Inconscient",
        "domaine": "Inconscient, spiritualité, secrets, karmas",
        "description": "La douzième maison représente votre inconscient, vos secrets et votre connexion au divin. C'est la maison du karma."
    }
}

# ============= CHEMINS DE VIE =============

CHEMINS_VIE = {
    1: {
        "titre": "Le Leader",
        "mot_cle": "Indépendance",
        "mission": "Vous êtes venu(e) pour développer votre individualité et votre capacité à diriger. Votre chemin est celui de l'initiative et de l'autonomie.",
        "forces": ["Leadership naturel", "Créativité", "Ambition", "Originalité"],
        "defis": ["Égocentrisme", "Impatience", "Domination"],
        "conseil": "Apprenez à diriger avec compassion plutôt qu'avec autorité.",
        "annee_favorable": [1, 2, 9],
        "couleur": "Rouge, Or",
        "pierre": "Rubis, Diamant"
    },
    2: {
        "titre": "Le Diplomate",
        "mot_cle": "Coopération",
        "mission": "Vous êtes venu(e) pour apprendre l'art de la collaboration et de la médiation. Votre force réside dans votre capacité à unir les opposés.",
        "forces": ["Diplomatie", "Sensibilité", "Patience", "Intuition"],
        "defis": ["Dépendance", "Hypersensibilité", "Indécision"],
        "conseil": "Trouvez l'équilibre entre donner et recevoir.",
        "annee_favorable": [2, 4, 6],
        "couleur": "Blanc, Argent",
        "pierre": "Perle, Pierre de Lune"
    },
    3: {
        "titre": "L'Artiste",
        "mot_cle": "Expression",
        "mission": "Vous êtes venu(e) pour exprimer votre créativité et inspirer les autres par votre joie de vivre et votre talent artistique.",
        "forces": ["Créativité", "Communication", "Optimisme", "Charme"],
        "defis": ["Dispersion", "Superficialité", "Bavardage"],
        "conseil": "Canalisez votre créativité vers des projets qui ont du sens.",
        "annee_favorable": [3, 6, 9],
        "couleur": "Jaune, Orange",
        "pierre": "Topaze, Citrine"
    },
    4: {
        "titre": "Le Bâtisseur",
        "mot_cle": "Stabilité",
        "mission": "Vous êtes venu(e) pour construire des fondations solides et apporter structure et ordre au monde qui vous entoure.",
        "forces": ["Organisation", "Fiabilité", "Persévérance", "Logique"],
        "defis": ["Rigidité", "Obstination", "Limitation"],
        "conseil": "Apprenez à lâcher prise parfois et à faire confiance au flux de la vie.",
        "annee_favorable": [4, 8, 1],
        "couleur": "Vert, Marron",
        "pierre": "Émeraude, Jade"
    },
    5: {
        "titre": "L'Aventurier",
        "mot_cle": "Liberté",
        "mission": "Vous êtes venu(e) pour expérimenter la vie dans toute sa diversité et enseigner aux autres la valeur de la liberté.",
        "forces": ["Adaptabilité", "Curiosité", "Charisme", "Versatilité"],
        "defis": ["Instabilité", "Excès", "Irresponsabilité"],
        "conseil": "Trouvez la liberté intérieure, pas seulement extérieure.",
        "annee_favorable": [5, 7, 3],
        "couleur": "Turquoise, Orange",
        "pierre": "Aigue-marine, Turquoise"
    },
    6: {
        "titre": "Le Protecteur",
        "mot_cle": "Responsabilité",
        "mission": "Vous êtes venu(e) pour apprendre l'amour inconditionnel et prendre soin de ceux qui vous entourent avec compassion.",
        "forces": ["Compassion", "Harmonie", "Dévouement", "Beauté"],
        "defis": ["Sacrifice excessif", "Perfectionnisme", "Anxiété"],
        "conseil": "N'oubliez pas de prendre soin de vous-même aussi.",
        "annee_favorable": [6, 9, 3],
        "couleur": "Bleu, Rose",
        "pierre": "Saphir, Quartz rose"
    },
    7: {
        "titre": "Le Chercheur",
        "mot_cle": "Sagesse",
        "mission": "Vous êtes venu(e) pour développer votre spiritualité et votre sagesse intérieure, et partager vos découvertes avec le monde.",
        "forces": ["Intuition", "Analyse", "Spiritualité", "Profondeur"],
        "defis": ["Isolement", "Scepticisme", "Froideur"],
        "conseil": "Équilibrez la quête intérieure avec les connexions humaines.",
        "annee_favorable": [7, 5, 2],
        "couleur": "Violet, Indigo",
        "pierre": "Améthyste, Lapis-lazuli"
    },
    8: {
        "titre": "Le Manifesteur",
        "mot_cle": "Pouvoir",
        "mission": "Vous êtes venu(e) pour maîtriser le monde matériel et utiliser votre pouvoir pour créer l'abondance et aider les autres.",
        "forces": ["Ambition", "Organisation", "Autorité", "Vision"],
        "defis": ["Matérialisme", "Contrôle", "Workaholisme"],
        "conseil": "Le vrai pouvoir vient du service aux autres.",
        "annee_favorable": [8, 1, 4],
        "couleur": "Noir, Bordeaux",
        "pierre": "Obsidienne, Grenat"
    },
    9: {
        "titre": "L'Humaniste",
        "mot_cle": "Compassion",
        "mission": "Vous êtes venu(e) pour servir l'humanité et apporter guérison et sagesse au monde. Votre amour est universel.",
        "forces": ["Altruisme", "Sagesse", "Créativité", "Tolérance"],
        "defis": ["Idéalisme excessif", "Déception", "Sacrifice"],
        "conseil": "Gardez les pieds sur terre tout en visant les étoiles.",
        "annee_favorable": [9, 3, 6],
        "couleur": "Or, Blanc",
        "pierre": "Diamant, Cristal de roche"
    },
    11: {
        "titre": "L'Illuminateur",
        "mot_cle": "Inspiration",
        "mission": "Nombre maître : Vous êtes venu(e) pour illuminer le chemin des autres et partager votre vision spirituelle unique.",
        "forces": ["Intuition exceptionnelle", "Inspiration", "Charisme", "Vision"],
        "defis": ["Tension nerveuse", "Idéalisme", "Hypersensibilité"],
        "conseil": "Ancrez votre lumière dans la réalité quotidienne.",
        "annee_favorable": [11, 2, 9],
        "couleur": "Argent, Blanc",
        "pierre": "Pierre de Lune, Opale"
    },
    22: {
        "titre": "Le Maître Bâtisseur",
        "mot_cle": "Manifestation",
        "mission": "Nombre maître : Vous êtes venu(e) pour construire des œuvres qui serviront l'humanité pendant des générations.",
        "forces": ["Vision à grande échelle", "Pragmatisme", "Leadership", "Endurance"],
        "defis": ["Pression excessive", "Perfectionnisme", "Impatience"],
        "conseil": "Même les cathédrales se construisent pierre par pierre.",
        "annee_favorable": [22, 4, 8],
        "couleur": "Or, Pourpre",
        "pierre": "Diamant, Rubis"
    },
    33: {
        "titre": "Le Maître Enseignant",
        "mot_cle": "Guidance",
        "mission": "Nombre maître : Vous êtes venu(e) pour enseigner l'amour inconditionnel par l'exemple et guérir les âmes blessées.",
        "forces": ["Amour universel", "Dévotion", "Guérison", "Sacrifice conscient"],
        "defis": ["Martyre", "Épuisement", "Idéalisme"],
        "conseil": "Votre lumière brille plus fort quand vous prenez soin de vous.",
        "annee_favorable": [33, 6, 9],
        "couleur": "Rose, Violet",
        "pierre": "Quartz rose, Améthyste"
    }
}

# ============= PRÉVISIONS PAR ANNÉE PERSONNELLE =============

PREVISIONS_ANNEE_PERSONNELLE = {
    1: {
        "theme": "Nouveaux Départs",
        "resume": "Une année de renouveau et d'initiatives. C'est le moment de planter les graines de vos projets futurs.",
        "domaines": {
            "carriere": "Excellent moment pour lancer de nouveaux projets ou changer de direction professionnelle. Votre énergie d'initiative est à son maximum.",
            "amour": "Si vous êtes célibataire, cette année favorise les nouvelles rencontres. En couple, c'est l'occasion de renouveler votre relation.",
            "sante": "Énergie vitale élevée. Bon moment pour commencer une nouvelle routine de bien-être.",
            "finances": "Investissements et nouvelles sources de revenus favorisés. Prenez des initiatives financières.",
            "spirituel": "Début d'un nouveau cycle spirituel de 9 ans. Définissez vos intentions profondes."
        },
        "mois_forts": [1, 5, 10],
        "conseil_cle": "Osez être le pionnier de votre propre vie. L'univers soutient vos initiatives."
    },
    2: {
        "theme": "Patience & Partenariats",
        "resume": "Année de gestation et de collaboration. Les graines plantées l'année dernière ont besoin de temps pour germer.",
        "domaines": {
            "carriere": "Privilégiez le travail d'équipe et les partenariats. Ce n'est pas le moment de foncer seul(e).",
            "amour": "Année très favorable pour les relations. Approfondissement des liens existants.",
            "sante": "Écoutez votre corps et son besoin de repos. Évitez le surmenage.",
            "finances": "Consolidation plutôt qu'expansion. Économisez et planifiez.",
            "spirituel": "Développement de l'intuition. Méditation et réceptivité favorisées."
        },
        "mois_forts": [2, 6, 11],
        "conseil_cle": "La patience est votre plus grande alliée cette année. Faites confiance au timing divin."
    },
    3: {
        "theme": "Expression & Créativité",
        "resume": "Année d'expression créative et de joie. Vos talents veulent s'exprimer au grand jour.",
        "domaines": {
            "carriere": "Excellente année pour les projets créatifs, la communication et l'auto-promotion.",
            "amour": "Année légère et joyeuse en amour. Flirts, sorties et plaisirs partagés.",
            "sante": "Bonne vitalité. Activités physiques ludiques recommandées.",
            "finances": "Rentrées d'argent possibles grâce à vos talents créatifs.",
            "spirituel": "Expression de votre spiritualité à travers l'art et la créativité."
        },
        "mois_forts": [3, 5, 12],
        "conseil_cle": "Laissez votre lumière intérieure briller. Le monde a besoin de votre joie."
    },
    4: {
        "theme": "Travail & Fondations",
        "resume": "Année de construction et d'efforts soutenus. Bâtissez des fondations solides pour l'avenir.",
        "domaines": {
            "carriere": "Travail acharné et récompenses à la clé. Structurez vos projets avec méthode.",
            "amour": "Année pour solidifier une relation existante. Engagement et stabilité.",
            "sante": "Attention au surmenage. Intégrez des routines de santé régulières.",
            "finances": "Année pour économiser et investir dans le long terme. Budget rigoureux.",
            "spirituel": "Discipline spirituelle bénéfique. Pratiques régulières et ancrées."
        },
        "mois_forts": [4, 8, 10],
        "conseil_cle": "Le travail patient porte ses fruits. Construisez pierre par pierre."
    },
    5: {
        "theme": "Changement & Liberté",
        "resume": "Année de changements et d'aventures. L'inattendu vous apporte de nouvelles opportunités.",
        "domaines": {
            "carriere": "Changements de carrière possibles. Adaptabilité et flexibilité requises.",
            "amour": "Année de passion et peut-être d'instabilité. Nouvelles rencontres excitantes.",
            "sante": "Besoin de mouvement et de variété. Évitez la routine.",
            "finances": "Fluctuations possibles. Évitez les risques excessifs.",
            "spirituel": "Exploration de nouvelles voies spirituelles. Ouverture d'esprit."
        },
        "mois_forts": [5, 7, 9],
        "conseil_cle": "Accueillez le changement comme un cadeau. La liberté est votre droit de naissance."
    },
    6: {
        "theme": "Amour & Responsabilité",
        "resume": "Année centrée sur la famille, l'amour et les responsabilités. Le cœur est au premier plan.",
        "domaines": {
            "carriere": "Équilibre travail-famille important. Possibilités dans les métiers de service.",
            "amour": "Année très favorable pour le mariage, la famille, les réconciliations.",
            "sante": "Prenez soin de vous et de vos proches. Attention au stress familial.",
            "finances": "Dépenses liées au foyer possibles. Budget équilibré nécessaire.",
            "spirituel": "L'amour comme voie spirituelle. Service aux autres."
        },
        "mois_forts": [6, 9, 12],
        "conseil_cle": "L'amour que vous donnez vous revient multiplié. Ouvrez votre cœur."
    },
    7: {
        "theme": "Introspection & Sagesse",
        "resume": "Année de réflexion et de développement intérieur. Retirez-vous pour mieux vous connaître.",
        "domaines": {
            "carriere": "Ralentissement possible. Temps de réflexion sur votre direction professionnelle.",
            "amour": "Besoin de solitude dans la relation. Communication profonde favorisée.",
            "sante": "Repos et régénération nécessaires. Pratiques méditatives bénéfiques.",
            "finances": "Pas le meilleur moment pour les investissements risqués. Prudence.",
            "spirituel": "Année exceptionnelle pour la croissance spirituelle. Études, méditation, retraites."
        },
        "mois_forts": [7, 2, 11],
        "conseil_cle": "Dans le silence, vous trouverez les réponses. Écoutez votre âme."
    },
    8: {
        "theme": "Pouvoir & Abondance",
        "resume": "Année de récolte et de pouvoir personnel. Vos efforts passés portent leurs fruits.",
        "domaines": {
            "carriere": "Succès professionnel et reconnaissance. Promotions et avancement possibles.",
            "amour": "Relations de pouvoir à équilibrer. Engagement profond possible.",
            "sante": "Énergie forte mais attention à ne pas vous épuiser dans le travail.",
            "finances": "Excellente année pour les gains financiers et les investissements.",
            "spirituel": "Intégration du pouvoir et de la spiritualité. Responsabilité karmique."
        },
        "mois_forts": [8, 1, 4],
        "conseil_cle": "Le vrai pouvoir sert le bien de tous. Récoltez avec gratitude."
    },
    9: {
        "theme": "Achèvement & Transformation",
        "resume": "Année de fin de cycle et de lâcher-prise. Préparez-vous au renouveau en libérant le passé.",
        "domaines": {
            "carriere": "Fin de projets ou de cycles professionnels. Préparez la transition.",
            "amour": "Possibles fins de relations qui ne vous servent plus. Guérison émotionnelle.",
            "sante": "Nettoyage et détoxification bénéfiques. Libérez les vieilles blessures.",
            "finances": "Générosité et don favorisés. Ce que vous donnez vous reviendra.",
            "spirituel": "Année de grande sagesse et de compassion universelle. Service aux autres."
        },
        "mois_forts": [9, 3, 6],
        "conseil_cle": "Laissez partir ce qui doit partir. Le vide que vous créez sera comblé par du nouveau."
    }
}

# ============= ARCANES DU TAROT =============

ARCANES_MAJEURS = {
    0: {"nom": "Le Mat", "mot_cle": "Liberté", "message": "Un nouveau voyage commence. Faites confiance à votre instinct."},
    1: {"nom": "Le Bateleur", "mot_cle": "Potentiel", "message": "Tous les outils sont à votre disposition. Passez à l'action."},
    2: {"nom": "La Papesse", "mot_cle": "Intuition", "message": "Écoutez votre voix intérieure. Les réponses sont en vous."},
    3: {"nom": "L'Impératrice", "mot_cle": "Abondance", "message": "La créativité et la fertilité sont favorisées."},
    4: {"nom": "L'Empereur", "mot_cle": "Structure", "message": "Établissez des fondations solides. La discipline paie."},
    5: {"nom": "Le Pape", "mot_cle": "Sagesse", "message": "Cherchez un guide ou devenez-en un. La tradition a du sens."},
    6: {"nom": "L'Amoureux", "mot_cle": "Choix", "message": "Un choix important se présente. Suivez votre cœur."},
    7: {"nom": "Le Chariot", "mot_cle": "Victoire", "message": "Avancez avec détermination. Le succès est proche."},
    8: {"nom": "La Justice", "mot_cle": "Équilibre", "message": "La vérité et l'équité prévaudront. Soyez juste."},
    9: {"nom": "L'Hermite", "mot_cle": "Introspection", "message": "Le temps de la réflexion est venu. Cherchez la lumière intérieure."},
    10: {"nom": "La Roue de Fortune", "mot_cle": "Cycles", "message": "Les changements sont inévitables. Adaptez-vous."},
    11: {"nom": "La Force", "mot_cle": "Courage", "message": "La vraie force vient de la maîtrise de soi."},
    12: {"nom": "Le Pendu", "mot_cle": "Lâcher-prise", "message": "Parfois, ne rien faire est la meilleure action."},
    13: {"nom": "L'Arcane sans Nom", "mot_cle": "Transformation", "message": "Une fin nécessaire pour un nouveau départ."},
    14: {"nom": "Tempérance", "mot_cle": "Harmonie", "message": "L'équilibre et la patience portent leurs fruits."},
    15: {"nom": "Le Diable", "mot_cle": "Attachements", "message": "Examinez ce qui vous retient prisonnier."},
    16: {"nom": "La Maison Dieu", "mot_cle": "Révélation", "message": "Une structure s'effondre pour révéler la vérité."},
    17: {"nom": "L'Étoile", "mot_cle": "Espoir", "message": "L'espoir renaît. Suivez votre étoile."},
    18: {"nom": "La Lune", "mot_cle": "Illusions", "message": "Méfiez-vous des apparences. Faites confiance à votre intuition."},
    19: {"nom": "Le Soleil", "mot_cle": "Succès", "message": "La joie et le succès illuminent votre chemin."},
    20: {"nom": "Le Jugement", "mot_cle": "Renaissance", "message": "L'appel au réveil. Une nouvelle vie commence."},
    21: {"nom": "Le Monde", "mot_cle": "Accomplissement", "message": "Un cycle s'achève dans la plénitude."}
}
