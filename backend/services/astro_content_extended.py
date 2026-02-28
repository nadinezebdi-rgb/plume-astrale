"""
Contenu astrologique etendu pour le manuscrit enrichi
Planetes en signe, aspects, retrogrades, Chiron, Noeud Nord, elements
"""

# ============= MERCURE EN SIGNE =============
MERCURE_EN_SIGNE = {
    "Aries": "Votre esprit fonctionne a grande vitesse. Vous pensez vite, parlez vite et decidez vite. Votre communication est directe, parfois tranchante, mais toujours honnete. Vous etes un(e) pionnier(e) intellectuel(le), souvent le(la) premier(e) a avoir une idee originale. Le defi est d'apprendre a ecouter avant de repondre.",
    "Taurus": "Votre pensee est methodique et pragmatique. Vous aimez prendre le temps de reflechir avant de parler, et vos mots ont du poids. Votre memoire est remarquable et votre bon sens legendaire. Vous apprenez par la pratique et la repetition. Votre voix et votre facon de communiquer ont quelque chose d'apaisant.",
    "Gemini": "Mercure est chez lui en Gemeaux, ce qui vous confere un esprit vif, curieux et polyvalent. Vous etes un(e) communicant(e) ne(e), capable de jongler entre plusieurs sujets avec aisance. L'information circule en vous comme un courant electrique. Votre defi est de canaliser cette vivacite mentale vers des objectifs concrets.",
    "Cancer": "Votre intelligence est profondement emotionnelle et intuitive. Vous pensez avec le coeur autant qu'avec la tete. Votre memoire est photographique, surtout pour les souvenirs charges d'emotion. Vous communiquez avec douceur et empathie, mais pouvez vous replier dans le silence si vous vous sentez blesse(e).",
    "Leo": "Votre esprit est creatif et expressif. Vous communiquez avec chaleur, enthousiasme et une certaine theatralite. Vos idees sont grandes et ambitieuses. Vous avez le don de captiver un auditoire et de rendre passionnant n'importe quel sujet. Votre fierte intellectuelle vous pousse a toujours approfondir vos connaissances.",
    "Virgo": "Mercure est egalement chez lui en Vierge, vous dotant d'un esprit analytique exceptionnel. Vous remarquez les details que les autres manquent, et votre pensee est structuree et logique. Vous etes un(e) excellent(e) resolveur(se) de problemes. Le defi est d'eviter la suranalyse et la critique excessive.",
    "Libra": "Votre esprit cherche naturellement l'equilibre et l'harmonie dans les idees. Vous etes doue(e) pour voir les deux cotes d'une question et excellez dans la negociation et la diplomatie. Votre communication est elegante et raffinee. Le defi est de prendre des decisions sans chercher eternellement le compromis parfait.",
    "Scorpio": "Votre pensee est penetrante et investigatrice. Vous n'acceptez jamais les apparences et creusez toujours plus profond. Votre intuition intellectuelle est remarquable : vous devinez les non-dits et percez les secrets. Vos mots ont un pouvoir de transformation. Vous communiquez avec intensite et precision chirurgicale.",
    "Sagittarius": "Votre esprit vise les grands horizons. Vous pensez en termes de philosophie, de sens et de vision globale. Les details vous ennuient, mais les grandes idees vous enflamment. Vous etes un(e) conteur(se) ne(e), capable de transmettre votre enthousiasme. Le defi est de rester ancre(e) dans les faits concrets.",
    "Capricorn": "Votre pensee est strategique et disciplinee. Vous planifiez a long terme et communiquez avec autorite et serieux. Votre esprit est structure comme une architecture solide. Vous n'aimez pas les bavardages inutiles et privilegiez la substance sur le style. Votre sagesse intellectuelle s'approfondit avec l'age.",
    "Aquarius": "Votre esprit est original, visionnaire et parfois revolutionnaire. Vous pensez en dehors des cadres etablis et vos idees sont souvent en avance sur leur temps. Votre communication est surprenante et stimulante. Vous etes attire(e) par les nouvelles technologies et les concepts avant-gardistes.",
    "Pisces": "Votre pensee est intuitive, poetique et receptive. Votre esprit fonctionne par images, symboles et impressions plutot que par logique pure. Vous etes doue(e) pour comprendre les nuances emotionnelles et les courants invisibles. Votre imagination est votre plus grand outil intellectuel."
}

# ============= VENUS EN SIGNE =============
VENUS_EN_SIGNE = {
    "Aries": "En amour, vous etes passionnee(e) et spontane(e). Vous aimez la conquete et les debuts electrisants. Votre facon d'aimer est directe, impulsive et courageuse. Vous avez besoin d'excitement et de nouveaute dans vos relations. Votre plus grand defi amoureux est la patience et la constance.",
    "Taurus": "Venus est chez elle en Taureau, vous offrant un sens inegalable de la beaute et du plaisir. Vous aimez avec fidelite, sensualite et profondeur. Votre amour est stable et nourrissant, comme un jardin bien entretenu. Vous cherchez la securite dans vos relations et savez apprecier les plaisirs simples de la vie.",
    "Gemini": "Votre facon d'aimer passe par la communication et la complicite intellectuelle. Vous tombez amoureux(se) de l'esprit avant le corps. La variete et la stimulation mentale sont essentielles dans vos relations. Vous exprimez votre amour par les mots, les messages et le partage d'idees.",
    "Cancer": "Vous aimez avec une profondeur emotionnelle immense. Prendre soin de l'autre est votre langage amoureux. Vous creez des nids douillets et cherchez une connexion intime et securisante. Votre amour est maternel, protecteur et infiniment tendre. La famille et le foyer sont au coeur de votre bonheur.",
    "Leo": "Votre amour est genereux, theatral et lumineux. Vous aimez etre admiree(e) et admirer en retour. Vos gestes romantiques sont grands et memorables. Vous cherchez un(e) partenaire qui vous fait sentir special(e) et que vous pouvez mettre sur un piedestal. La loyaute et la fierte sont vos valeurs amoureuses.",
    "Virgo": "Vous exprimez votre amour par les actes de service et l'attention aux details. Votre facon d'aimer est discrete mais profondement devouee. Vous remarquez les petits besoins de l'autre et y repondez avec precision. Le defi est d'accepter l'imperfection chez l'autre et en vous-meme.",
    "Libra": "Venus est chez elle en Balance, faisant de vous un(e) amoureux(se) de l'amour lui-meme. Vous etes ne(e) pour les relations harmonieuses, la beaute partagee et les partenariats equilibres. Votre charme est irresistible. Vous avez besoin d'un(e) partenaire qui soit aussi un(e) ami(e) et un(e) egal(e).",
    "Scorpio": "Votre amour est intense, transformateur et absolu. Vous ne connaissez pas les demi-mesures en amour : c'est tout ou rien. La passion et la profondeur emotionnelle sont vos carburants relationnels. Vous cherchez la fusion totale avec l'etre aime. La jalousie peut etre un defi a transcender.",
    "Sagittarius": "Vous aimez avec enthousiasme, generosite et un esprit d'aventure. La liberte dans la relation est essentielle pour vous. Vous etes attire(e) par les personnes qui partagent votre soif de decouverte et d'apprentissage. L'humour et la philosophie sont au coeur de vos relations.",
    "Capricorn": "Votre facon d'aimer est serieuse, engagee et orientee vers le long terme. Vous ne vous engagez pas a la legere, mais quand vous le faites, c'est pour la vie. Vous construisez vos relations comme des edifices solides. Le temps renforce vos liens plutot que de les affaiblir.",
    "Aquarius": "Votre amour est original, libre et humaniste. Vous cherchez un(e) partenaire qui soit aussi votre meilleur(e) ami(e) et un(e) allie(e) intellectuel(le). La liberte individuelle au sein du couple est essentielle. Vous aimez avec detachement, ce qui peut derouter les natures plus emotionnelles.",
    "Pisces": "Venus est exaltee en Poissons, vous offrant la capacite d'aimer de maniere inconditionnelle et transcendante. Votre amour est poetique, sacrificiel et spirituel. Vous idealisez souvent vos partenaires et vos relations. Votre plus grand don est votre compassion infinie, votre defi est de garder les pieds sur terre."
}

# ============= MARS EN SIGNE =============
MARS_EN_SIGNE = {
    "Aries": "Mars est chez lui en Belier, vous conferant une energie d'action formidable. Vous foncez tete baissee vers vos objectifs avec un courage indomptable. Votre colere est explosive mais de courte duree. Vous excellez dans la competition et les debuts de projets. Votre energie physique est remarquable.",
    "Taurus": "Votre energie d'action est lente a demarrer mais implacable une fois lancee. Vous agissez avec methode, perseverance et determination. Votre patience est une arme redoutable. Quand vous vous mettez en colere, c'est un tremblement de terre qui couvait depuis longtemps. Vos resultats sont durables.",
    "Gemini": "Votre energie s'exprime a travers la communication et la stimulation mentale. Vous agissez vite, changez de strategie facilement et jonglez entre plusieurs projets. Votre force est dans votre adaptabilite et votre vivacite. Le defi est de maintenir la concentration sur un seul objectif a la fois.",
    "Cancer": "Votre energie d'action est guidee par vos emotions et votre instinct protecteur. Vous vous battez ferocicment pour ceux que vous aimez et pour votre securite. Votre motivation fluctue avec vos humeurs. Quand vous etes emotionnellement investi(e), votre determination est inbreakable.",
    "Leo": "Votre energie est rayonnante, creative et theatrale. Vous agissez avec panache et generosite. Vous etes motive(e) par la reconnaissance et le desir de laisser votre empreinte. Votre leadership naturel inspire les autres a agir. Votre colere est royale et impressionnante.",
    "Virgo": "Votre energie s'exprime a travers le service, l'analyse et le perfectionnement. Vous agissez avec precision et methode, preferant la strategie a la force brute. Vous etes motive(e) par le desir d'ameliorer et d'organiser. Votre productivite est remarquable quand vous canalisez votre energie.",
    "Libra": "Votre energie d'action cherche l'equilibre et la justice. Vous agissez de maniere diplomatique et cooperative. La confrontation directe vous met mal a l'aise, mais vous vous battez avec elegance pour ce qui est juste. Vous excellez dans les negociations et les partenariats strategiques.",
    "Scorpio": "Mars est puissant en Scorpion, vous dotant d'une intensite et d'une determination hors du commun. Votre energie est strategique, penetrante et transformatrice. Vous n'abandonnez jamais et votre volonte est d'acier. Votre force reside dans votre capacite a vous regenerer apres chaque epreuve.",
    "Sagittarius": "Votre energie est expansive, optimiste et aventuriere. Vous agissez avec enthousiasme et vision. Votre motivation vient de votre quete de sens et de liberte. Vous excellez dans les entreprises qui demandent de l'audace et une vision large. L'immobilisme est votre pire ennemi.",
    "Capricorn": "Mars est exalte en Capricorne, vous conferant une discipline et une endurance exceptionnelles. Votre energie est strategique, patiente et orientee vers des objectifs a long terme. Vous grimpez les montagnes pas a pas, sans jamais perdre de vue le sommet. Votre ambition est votre moteur le plus puissant.",
    "Aquarius": "Votre energie d'action est originale, independante et humaniste. Vous agissez pour des causes qui depassent votre interet personnel. Votre approche est non conventionnelle et parfois revolutionnaire. Vous etes motive(e) par le desir de changer le monde et de defendre la liberte.",
    "Pisces": "Votre energie s'exprime de maniere fluide, intuitive et compassionnelle. Vous agissez guide(e) par votre intuition et votre empathie. La creativite et la spiritualite sont des moteurs puissants pour vous. Le defi est de transformer vos reves en actions concretes et de poser des limites saines."
}

# ============= JUPITER EN SIGNE =============
JUPITER_EN_SIGNE = {
    "Aries": "Votre chance et votre expansion se manifestent quand vous prenez l'initiative et osez etre le(la) premier(e). L'audace et le courage sont recompenses. Les opportunites affluent quand vous agissez avec confiance et independance.",
    "Taurus": "L'abondance vient a vous par la patience et la constance. Vous avez un talent naturel pour attirer la prosperite materielle. Les plaisirs de la vie vous nourrissent et votre sens des affaires est excellent.",
    "Gemini": "Votre expansion passe par la communication, les echanges et l'apprentissage. Les voyages courts, les contacts et le partage d'idees sont des sources de chance. Votre curiosite vous ouvre des portes inattendues.",
    "Cancer": "Votre chance reside dans le domaine familial et emotionnel. La generosite envers vos proches vous est rendue au centuple. Votre intuition est un guide fiable pour saisir les bonnes opportunites.",
    "Leo": "L'abondance afflue quand vous exprimez votre creativite et votre generosite. Votre charisme naturel attire les opportunites. Les arts, le divertissement et le leadership sont des domaines favorises.",
    "Virgo": "Votre expansion se manifeste par le service, le travail consciencieux et l'attention aux details. La sante et le bien-etre sont des domaines ou la chance vous sourit. Votre humilite est paradoxalement votre plus grand atout.",
    "Libra": "Les partenariats et les collaborations sont vos plus grandes sources d'abondance. La justice, l'art et la diplomatie sont favorises. Votre sens de l'equilibre attire naturellement l'harmonie et la prosperite.",
    "Scorpio": "Votre expansion passe par les transformations profondes et les crises qui revelent votre force. Les heritages, les investissements et la regeneration sont favorises. Votre capacite a renaître de vos cendres est votre plus grande chance.",
    "Sagittarius": "Jupiter est chez lui en Sagittaire, amplificant votre chance naturelle. Les voyages, les etudes superieures et la quete de sens sont des domaines benis. Votre optimisme et votre foi en la vie attirent les miracles.",
    "Capricorn": "Votre expansion est lente mais solide. La discipline, l'ambition et la patience finissent toujours par payer. Les recompenses viennent avec le temps et la maturite. Votre sens des responsabilites est votre meilleur investissement.",
    "Aquarius": "Votre chance se manifeste dans les domaines de l'innovation, de la technologie et de l'humanisme. Les projets collectifs et les idees originales sont favorises. Votre vision du futur attire les opportunites avant-gardistes.",
    "Pisces": "Jupiter est exalte en Poissons, vous conferant une grace et une protection spirituelle particulieres. Votre compassion et votre foi sont recompensees. Les domaines artistiques et spirituels sont des sources d'abondance naturelles."
}

# ============= SATURNE EN SIGNE =============
SATURNE_EN_SIGNE = {
    "Aries": "Votre lecon karmique concerne l'autonomie et l'affirmation de soi. Vous devez apprendre a prendre des initiatives sans crainte. Les defis vous enseignent le courage authentique, different de l'impulsivite.",
    "Taurus": "Votre lecon touche la securite materielle et l'estime de soi. Vous devez construire votre propre stabilite sans vous accrocher excessivement aux possessions. La vraie richesse vient de l'interieur.",
    "Gemini": "Votre lecon concerne la communication et la pensee structuree. Vous devez apprendre a approfondir vos connaissances plutot que de les survoler. La discipline mentale est votre chemin vers la maitrise.",
    "Cancer": "Votre lecon porte sur les emotions et la famille. Vous devez etablir des limites saines dans vos relations proches tout en restant ouvert(e) a la vulnerabilite. La maturite emotionnelle est votre objectif.",
    "Leo": "Votre lecon concerne la creativite et la reconnaissance. Vous devez apprendre a briller sans dependre des applaudissements des autres. La vraie confiance vient de l'authenticite, non de la validation externe.",
    "Virgo": "Votre lecon touche le perfectionnisme et le service. Vous devez apprendre que l'excellence ne signifie pas la perfection. L'acceptation de vos limites humaines est une forme de sagesse superieure.",
    "Libra": "Votre lecon porte sur les relations et l'equilibre. Vous devez apprendre a etre juste sans sacrifier vos propres besoins. L'engagement authentique demande parfois de faire des choix difficiles.",
    "Scorpio": "Votre lecon concerne le pouvoir et la transformation. Vous devez apprendre a lacher prise et a faire confiance au processus de la vie. Le controle est une illusion ; la veritable force est dans la reddition consciente.",
    "Sagittarius": "Votre lecon touche la liberte et la quete de sens. Vous devez structurer votre enthousiasme et transformer vos visions en realites concretes. La discipline dans la foi est votre chemin.",
    "Capricorn": "Saturne est chez lui en Capricorne, renforçant votre sens des responsabilites et votre ambition. Votre lecon est d'equilibrer le travail avec la chaleur humaine. Le succes sans amour est une reussite incomplete.",
    "Aquarius": "Saturne est egalement chez lui en Verseau, vous dotant d'une vision structuree du progres collectif. Votre lecon est d'incarner le changement que vous voulez voir dans le monde, pas seulement de le theoriser.",
    "Pisces": "Votre lecon concerne la spiritualite et les limites. Vous devez apprendre a transformer votre compassion en action concrete sans vous noyer dans la souffrance des autres. La discipline spirituelle est votre ancre."
}

# ============= DESCRIPTIONS DES ASPECTS =============
ASPECTS_TYPES = {
    "Conjunction": {
        "nom_fr": "Conjonction",
        "symbole": "0 deg",
        "nature": "fusion",
        "description": "Les energies de ces deux planetes fusionnent, creant une force concentree et puissante. Cette union amplifie les qualites des deux astres, pour le meilleur et le plus intense.",
    },
    "Sextile": {
        "nom_fr": "Sextile",
        "symbole": "60 deg",
        "nature": "harmonieux",
        "description": "Un aspect d'opportunite et de fluidite. Les energies de ces planetes cooperent naturellement, offrant des talents et des possibilites qui demandent juste un leger effort pour etre actives.",
    },
    "Square": {
        "nom_fr": "Carre",
        "symbole": "90 deg",
        "nature": "tendu",
        "description": "Un aspect de tension creatrice et de croissance. Ces deux energies se confrontent, creant des defis qui vous poussent a evoluer. C'est souvent la source de vos plus grandes realisations.",
    },
    "Trine": {
        "nom_fr": "Trigone",
        "symbole": "120 deg",
        "nature": "harmonieux",
        "description": "Un aspect de grace naturelle et de talent inne. Les energies de ces planetes coulent ensemble avec aisance, revelant des dons qui semblent presque magiques.",
    },
    "Opposition": {
        "nom_fr": "Opposition",
        "symbole": "180 deg",
        "nature": "tendu",
        "description": "Un aspect de conscience et d'equilibre. Ces deux energies se font face, vous invitant a integrer des forces apparemment opposees. La cle est de trouver le point d'equilibre.",
    }
}

# Interpretations specifiques des aspects entre planetes majeures
ASPECTS_PLANETES = {
    ("Sun", "Moon"): {
        "harmonieux": "Votre volonte et vos emotions sont en harmonie. Vous etes en paix avec vous-meme, ce qui vous donne une stabilite interieure remarquable. Vos besoins emotionnels et vos aspirations conscientes s'alignent naturellement.",
        "tendu": "Une tension existe entre votre identite consciente et vos besoins emotionnels profonds. Ce que vous voulez et ce dont vous avez besoin ne coincident pas toujours. Cette dualite, une fois comprise, devient une source de richesse interieure.",
        "fusion": "Votre ego et vos emotions sont fusionnes, creant une personnalite intense et entiere. Vous vivez tout avec une grande sincerite. Votre defi est de distinguer entre ce que vous etes et ce que vous ressentez."
    },
    ("Sun", "Mercury"): {
        "harmonieux": "Votre intellect sert parfaitement votre identite. Vous vous exprimez avec clarte et authenticite.",
        "tendu": "Votre mental peut parfois entrer en conflit avec votre veritable nature, creant une tension entre ce que vous pensez et qui vous etes.",
        "fusion": "Votre esprit et votre identite ne font qu'un. Vous etes profondement identifie(e) a vos idees et a votre facon de communiquer."
    },
    ("Sun", "Venus"): {
        "harmonieux": "Votre identite est naturellement liee a l'amour et a la beaute. Vous degagez un charme naturel et savez creer l'harmonie autour de vous.",
        "tendu": "Des tensions entre votre desir d'etre aime(e) et votre besoin d'etre vous-meme. L'apprentissage est de ne pas sacrifier votre identite pour plaire aux autres.",
        "fusion": "Votre identite est intimement liee a votre capacite d'aimer. Vous etes naturellement charmant(e) et attirant(e)."
    },
    ("Sun", "Mars"): {
        "harmonieux": "Votre volonte et votre energie d'action travaillent main dans la main. Vous realisez vos projets avec efficacite et determination. Votre vitalite est forte.",
        "tendu": "Une tension entre votre ego et votre maniere d'agir. Parfois votre energie se retourne contre vous sous forme d'agressivite ou de frustration. Canalisez cette force creatrice.",
        "fusion": "Votre identite et votre energie sont fusionnees, creant une personnalite dynamique et proactive. L'action est au coeur de votre etre."
    },
    ("Sun", "Jupiter"): {
        "harmonieux": "La chance et l'expansion accompagnent votre chemin de vie. Vous inspirez confiance et attirez naturellement les opportunites. Votre optimisme est contagieux.",
        "tendu": "Tendance a l'exces et a la surestimation de vos capacites. L'apprentissage est de canaliser votre enthousiasme sans disperser vos energies.",
        "fusion": "Votre personnalite est naturellement expansive et optimiste. Vous avez une foi profonde en la vie et en vos capacites."
    },
    ("Sun", "Saturn"): {
        "harmonieux": "Votre discipline et votre sens des responsabilites soutiennent vos ambitions. Vous batissez des reussites durables avec patience et maturite.",
        "tendu": "Des blocages et des limitations marquent votre parcours, mais chaque obstacle vous forge. La maturite et la perseverance sont vos allies. Le succes vient avec le temps.",
        "fusion": "Votre identite est profondement liee au sens du devoir et de la structure. Vous etes ne(e) pour assumer de grandes responsabilites."
    },
    ("Moon", "Venus"): {
        "harmonieux": "Vos emotions et votre capacite d'aimer sont en parfaite harmonie. Vous creez des relations douces et nourrissantes. Votre sensibilite est un atout dans l'amour.",
        "tendu": "Des tensions entre vos besoins emotionnels et vos desirs amoureux. Ce que vous ressentez et ce que vous desirez ne coincident pas toujours.",
        "fusion": "Vos emotions et votre amour sont fusionnes. Vous aimez avec tout votre etre et creez des liens profondement intimes."
    },
    ("Moon", "Mars"): {
        "harmonieux": "Vos emotions alimentent votre energie d'action. Vous agissez avec passion et instinct. Votre courage emotionnel est remarquable.",
        "tendu": "Vos emotions peuvent declencher des reactions impulsives. L'apprentissage est de canaliser votre energie emotionnelle de maniere constructive.",
        "fusion": "Vos emotions et votre energie sont fusionnees, creant des reactions intenses et immediates. Votre passion est votre moteur."
    },
    ("Venus", "Mars"): {
        "harmonieux": "L'amour et le desir coulent naturellement ensemble. Vous avez un magnetisme naturel et savez equilibrer tendresse et passion dans vos relations.",
        "tendu": "Tension entre ce que vous desirez et ce que vous aimez. La passion peut creer des conflits dans vos relations. L'integration de ces forces vous rend irresistible.",
        "fusion": "Amour et desir sont fusionnes, creant un magnetisme puissant. Votre passion amoureuse est votre signature energetique."
    },
    ("Jupiter", "Saturn"): {
        "harmonieux": "L'expansion et la structure travaillent ensemble. Vous savez quand accelerer et quand consolider. Vos reussites sont a la fois ambitieuses et solides.",
        "tendu": "Tension entre le desir d'expansion et le besoin de structure. Vous oscillez entre optimisme et prudence. L'equilibre entre les deux est votre sagesse.",
        "fusion": "La chance et la discipline se rencontrent, creant un potentiel remarquable pour des realisations majeures et durables."
    },
}

# ============= RETROGRADES =============
RETROGRADE_DESCRIPTIONS = {
    "Mercury": "Mercure retrograde dans votre theme natal indique que votre processus de pensee est introspectif et profond. Vous revisitez souvent vos idees et vos communications. Cette position vous donne une capacite exceptionnelle de reflexion et d'analyse retrospective. Vous apprenez souvent davantage des revisions que des premieres tentatives.",
    "Venus": "Venus retrograde suggere que votre relation a l'amour et a la beaute est interiorisee. Vous avez un sens unique de l'esthetique et de la valeur qui ne correspond pas toujours aux normes sociales. En amour, vous avez besoin de temps pour comprendre vos sentiments. Les relations karmiques font partie de votre parcours.",
    "Mars": "Mars retrograde indique que votre energie d'action est dirigee vers l'interieur. Vous pouvez avoir du mal a exprimer directement votre colere ou votre desir. Votre force est plus subtile et strategique que frontale. Apprenez a canaliser cette energie interieure de maniere constructive.",
    "Jupiter": "Jupiter retrograde signifie que votre croissance et votre expansion se font d'abord interieurement. La chance vient de votre monde interieur avant de se manifester exterieurement. Vous trouvez la sagesse en vous-meme plutot que dans les enseignements exterieurs.",
    "Saturn": "Saturne retrograde suggere que vos lecons karmiques sont profondement interiorisees. Vous etes souvent plus dur(e) avec vous-meme qu'avec les autres. La structure que vous devez construire est d'abord interieure. Avec le temps, votre autodiscipline devient votre plus grande force.",
    "Uranus": "Uranus retrograde indique que votre originalite et votre rebellion se vivent interieurement. Vous remettez en question les normes de maniere privee avant de les defier publiquement. Votre revolution personnelle est un processus intime et profond.",
    "Neptune": "Neptune retrograde signifie que votre spiritualite et votre imagination sont tournees vers l'interieur. Vos reves sont particulierement significatifs et vous avez une capacite naturelle de meditation. La frontiere entre reve et realite est fluide pour vous.",
    "Pluto": "Pluton retrograde indique que vos transformations les plus profondes se font dans l'intimite de votre etre. Vous possedez un pouvoir interieur immense. Les renaissances que vous vivez sont silencieuses mais radicales."
}

# ============= ELEMENTS =============
ELEMENTS_DOMINANTS = {
    "Feu": {
        "dominant": "Votre theme est domine par l'element Feu, ce qui vous confere une energie vitale exceptionnelle, de l'enthousiasme et un esprit d'initiative. Vous etes naturellement optimiste, passionne(e) et tourne(e) vers l'action. Votre defi est d'apprendre la patience et la constance.",
        "faible": "Avec peu de Feu dans votre theme, vous pouvez manquer parfois d'initiative spontanee ou de confiance en vous. Cultivez l'audace et l'action pour equilibrer votre theme."
    },
    "Terre": {
        "dominant": "Votre theme est domine par l'element Terre, vous ancrant solidement dans la realite. Vous etes pragmatique, fiable et perseverant(e). Les realisations concretes et la securite materielle sont importantes pour vous. Votre defi est de ne pas trop vous attacher au monde materiel.",
        "faible": "Avec peu de Terre dans votre theme, vous pouvez avoir du mal a concretiser vos idees ou a maintenir une stabilite materielle. Cultivez l'ancrage et la discipline pratique."
    },
    "Air": {
        "dominant": "Votre theme est domine par l'element Air, faisant de vous un(e) penseur(se) et communicant(e) ne(e). Les idees, les relations sociales et les echanges intellectuels sont votre oxygene. Votre defi est de rester connecte(e) a vos emotions et a votre corps.",
        "faible": "Avec peu d'Air dans votre theme, la communication abstraite et les relations sociales peuvent etre un defi. Cultivez l'ecoute, l'objectivite et le detachement sain."
    },
    "Eau": {
        "dominant": "Votre theme est domine par l'element Eau, vous conferant une sensibilite et une intuition profondes. Vous percevez les courants emotionnels invisibles et ressentez ce que les autres ne voient pas. Votre defi est de ne pas vous laisser submerger par les emotions.",
        "faible": "Avec peu d'Eau dans votre theme, l'acces a vos emotions profondes peut etre difficile. Cultivez l'empathie, l'intuition et la connexion emotionnelle avec les autres."
    }
}

MODALITES_DESCRIPTIONS = {
    "Cardinal": "Energie d'initiation et de leadership. Vous etes un(e) lanceur(se) de projets et un(e) moteur de changement.",
    "Fixe": "Energie de stabilite et de perseverance. Vous etes fiable, determine(e) et resistant(e) au changement.",
    "Mutable": "Energie d'adaptation et de flexibilite. Vous excellez dans les transitions et les ajustements."
}

# ============= CHIRON EN SIGNE =============
CHIRON_EN_SIGNE = {
    "Aries": "Votre blessure profonde touche votre identite et votre droit d'exister. Vous guerissez en apprenant a vous affirmer avec authenticite et en aidant les autres a trouver leur propre voix.",
    "Taurus": "Votre blessure concerne la securite et l'estime de soi. Vous guerissez en construisant une valeur interieure qui ne depend pas des possessions materielles.",
    "Gemini": "Votre blessure touche la communication et la pensee. Vous guerissez en apprenant que vos idees ont de la valeur et en partageant votre sagesse unique.",
    "Cancer": "Votre blessure concerne la famille et la securite emotionnelle. Vous guerissez en creant la famille emotionnelle que vous meritez et en offrant aux autres le soin que vous avez cherche.",
    "Leo": "Votre blessure touche l'expression de soi et la creativite. Vous guerissez en osant briller malgre la peur du rejet et en encourageant les autres a faire de meme.",
    "Virgo": "Votre blessure concerne le perfectionnisme et le service. Vous guerissez en acceptant votre humanite imparfaite et en decouvrant que vous etes utile tel(le) que vous etes.",
    "Libra": "Votre blessure touche les relations et l'equilibre. Vous guerissez en trouvant votre propre centre plutot que de vous definir a travers les autres.",
    "Scorpio": "Votre blessure concerne le pouvoir et la transformation. Vous guerissez en apprenant a faire confiance apres la trahison et en transformant votre douleur en sagesse profonde.",
    "Sagittarius": "Votre blessure touche le sens et la foi. Vous guerissez en trouvant votre propre verite plutot que de suivre les croyances des autres.",
    "Capricorn": "Votre blessure concerne l'autorite et la reussite. Vous guerissez en definissant le succes selon vos propres termes plutot que ceux de la societe.",
    "Aquarius": "Votre blessure touche l'appartenance et l'originalite. Vous guerissez en acceptant que votre difference est votre contribution unique au monde.",
    "Pisces": "Votre blessure concerne la connexion spirituelle et les limites. Vous guerissez en trouvant l'equilibre entre la compassion universelle et la protection de votre espace interieur."
}

# ============= NOEUD NORD EN SIGNE =============
NOEUD_NORD_EN_SIGNE = {
    "Aries": "Votre destinee vous appelle vers l'autonomie et le courage. Vous devez apprendre a prendre des decisions seul(e) et a vous affirmer, meme si cela derange l'equilibre.",
    "Taurus": "Votre destinee vous guide vers la simplicite, la stabilite et l'appreciation des plaisirs terrestres. Apprenez a construire quelque chose de durable plutot que de chercher l'intensite.",
    "Gemini": "Votre destinee vous appelle vers la communication, la curiosite et l'ouverture d'esprit. Echangez, ecoutez, apprenez des autres plutot que de rester dans vos certitudes.",
    "Cancer": "Votre destinee vous guide vers la vulnerabilite, la famille et la connexion emotionnelle. Apprenez a nourrir les liens intimes plutot que de tout sacrifier pour la reussite.",
    "Leo": "Votre destinee vous appelle a briller, a exprimer votre creativite et a rayonner de votre lumiere unique. Cessez de vous fondre dans le groupe.",
    "Virgo": "Votre destinee vous guide vers le service concret, la precision et l'humilite. Transformez vos reves en actions pratiques qui ameliorent le quotidien.",
    "Libra": "Votre destinee vous appelle vers les relations, la cooperation et la recherche d'harmonie. Apprenez l'art du compromis et de la diplomatie.",
    "Scorpio": "Votre destinee vous guide vers la profondeur, la transformation et l'intimite authentique. N'ayez pas peur des zones d'ombre, c'est la que se trouve votre pouvoir.",
    "Sagittarius": "Votre destinee vous appelle vers l'expansion, la philosophie et les grands horizons. Osez voir plus loin que votre environnement immediat.",
    "Capricorn": "Votre destinee vous guide vers la maitrise, la responsabilite et la construction d'un heritage durable. Assumez votre autorite naturelle.",
    "Aquarius": "Votre destinee vous appelle vers l'innovation, la communaute et la vision du futur. Votre role est d'amener des idees nouvelles au service du collectif.",
    "Pisces": "Votre destinee vous guide vers la spiritualite, la compassion et la dissolution de l'ego. Apprenez a faire confiance au flux de la vie et a servir quelque chose de plus grand que vous."
}

# ============= LILITH EN SIGNE =============
LILITH_EN_SIGNE = {
    "Aries": "Lilith Noire en Belier revele une puissance brute d'affirmation de soi. Vous portez en vous une rage creatrice qui, une fois apprivoisee, devient une force de liberation.",
    "Taurus": "Lilith en Taureau pointe vers des enjeux de possessivite et de rapport au plaisir. Votre defi est de profiter de l'abondance sans vous y attacher de maniere obsessionnelle.",
    "Gemini": "Lilith en Gemeaux revele un pouvoir lie a la parole et a la connaissance. Vos mots peuvent guerir ou blesser avec une force inhabituelle.",
    "Cancer": "Lilith en Cancer met en lumiere des enjeux emotionnels profonds lies a la mere et au foyer. Votre pouvoir reside dans votre capacite a transformer les blessures familiales en sagesse.",
    "Leo": "Lilith en Lion revele un pouvoir creatif intense et un magnetisme hors du commun. Votre defi est d'utiliser ce charisme pour inspirer plutot que pour dominer.",
    "Virgo": "Lilith en Vierge pointe vers la perfection comme instrument de pouvoir. Votre defi est d'accepter l'imperfection comme une forme de beaute et de liberation.",
    "Libra": "Lilith en Balance revele des enjeux de pouvoir dans les relations. Votre defi est de trouver l'equilibre entre independance et intimite sans manipulation.",
    "Scorpio": "Lilith est puissante en Scorpion, amplifiant votre magnetisme et votre capacite de transformation. Vous pouvez acceder a des profondeurs psychiques que peu de personnes osent explorer.",
    "Sagittarius": "Lilith en Sagittaire revele un pouvoir lie a la liberte et a la verite. Votre defi est de vivre selon vos propres croyances sans imposer votre vision aux autres.",
    "Capricorn": "Lilith en Capricorne met en lumiere des enjeux d'autorite et d'ambition. Votre defi est d'utiliser votre pouvoir de maniere ethique et au service du bien commun.",
    "Aquarius": "Lilith en Verseau revele un pouvoir de rebellion et d'originalite. Votre defi est de rester fidele a votre vision unique tout en restant connecte(e) aux autres.",
    "Pisces": "Lilith en Poissons revele un pouvoir spirituel et psychique profond. Votre defi est de canaliser cette sensibilite sans vous perdre dans les illusions."
}

# Helper function to get aspect interpretation
def get_aspect_interpretation(planet1, planet2, aspect_type):
    """Get interpretation for an aspect between two planets"""
    # Try both orders
    key = (planet1, planet2)
    if key not in ASPECTS_PLANETES:
        key = (planet2, planet1)
    if key not in ASPECTS_PLANETES:
        return None
    
    aspect_info = ASPECTS_TYPES.get(aspect_type, {})
    nature = aspect_info.get("nature", "harmonieux")
    
    interpretations = ASPECTS_PLANETES.get(key, {})
    return interpretations.get(nature, None)


# Helper to categorize element from sign
SIGNE_ELEMENT = {
    "Aries": "Feu", "Taurus": "Terre", "Gemini": "Air", "Cancer": "Eau",
    "Leo": "Feu", "Virgo": "Terre", "Libra": "Air", "Scorpio": "Eau",
    "Sagittarius": "Feu", "Capricorn": "Terre", "Aquarius": "Air", "Pisces": "Eau"
}

SIGNE_MODALITE = {
    "Aries": "Cardinal", "Taurus": "Fixe", "Gemini": "Mutable", "Cancer": "Cardinal",
    "Leo": "Fixe", "Virgo": "Mutable", "Libra": "Cardinal", "Scorpio": "Fixe",
    "Sagittarius": "Mutable", "Capricorn": "Cardinal", "Aquarius": "Fixe", "Pisces": "Mutable"
}
