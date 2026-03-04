"""
Contenu astrologique étendu pour le manuscrit enrichi
Planètes en signe, aspects, rétrogrades, Chiron, Nœud Nord, éléments
"""

# ============= MERCURE EN SIGNE =============
MERCURE_EN_SIGNE = {
    "Aries": "Votre esprit fonctionne à grande vitesse. Vous pensez vite, parlez vite et décidez vite. Votre communication est directe, parfois tranchante, mais toujours honnête. Vous êtes un(e) pionnier(e) intellectuel(le), souvent le(la) premier(e) à avoir une idée originale. Le défi est d'apprendre à écouter avant de répondre.",
    "Taurus": "Votre pensee est méthodique et pragmatique. Vous aiméz prendre le temps de réfléchir avant de parler, et vos mots ont du poids. Votre mémoire est remarquable et votre bon sens légendaire. Vous apprenez par la pratique et la répétition. Votre voix et votre façon de communiquer ont quelque chose d'apaisant.",
    "Gemini": "Mercure est chez lui en Gémeaux, ce qui vous confère un esprit vif, curieux et polyvalent. Vous êtes un(e) communicant(e) né(e), capable de jongler entre plusieurs sujets avec aisance. L'information circule en vous comme un courant électrique. Votre défi est de canaliser cette vivacité mentale vers des objectifs concrets.",
    "Cancer": "Votre intelligence est profondement émotionnelle et intuitive. Vous pensez avec le cœur autant qu'avec la tête. Votre mémoire est photographique, surtout pour les souvenirs chargés d'émotion. Vous communiquez avec douceur et empathie, mais pouvez vous replier dans le silence si vous vous sentez blessé(e).",
    "Leo": "Votre esprit est créatif et expressif. Vous communiquez avec chaleur, enthousiasme et une certaine théâtralité. Vos idées sont grandes et ambitieuses. Vous avez le don de captiver un auditoire et de rendre passionnant n'importe quel sujet. Votre fierté intellectuelle vous pousse à toujours approfondir vos connaissances.",
    "Virgo": "Mercure est également chez lui en Vierge, vous dotant d'un esprit analytique exceptionnel. Vous remarquez les détails que les autres manquent, et votre pensee est structurée et logique. Vous êtes un(e) excellent(e) résolveur(se) de problèmes. Le défi est d'éviter la suranalyse et la critique excessive.",
    "Libra": "Votre esprit cherche naturellement l'équilibre et l'harmonie dans les idées. Vous êtes doué(e) pour voir les deux côtés d'une question et excellez dans la négociation et la diplomatie. Votre communication est élégante et raffinée. Le défi est de prendre des décisions sans chercher éternellement le compromis parfait.",
    "Scorpio": "Votre pensee est pénétrante et investigatrice. Vous n'acceptez jamais les apparences et creusez toujours plus profond. Votre intuition intellectuelle est remarquable : vous devinez les non-dits et percez les secrets. Vos mots ont un pouvoir de transformation. Vous communiquez avec intensité et précision chirurgicale.",
    "Sagittarius": "Votre esprit vise les grands horizons. Vous pensez en termes de philosophie, de sens et de vision globale. Les détails vous ennuient, mais les grandes idées vous enflamment. Vous êtes un(e) conteur(se) né(e), capable de transmettre votre enthousiasme. Le défi est de rester ancré(e) dans les faits concrets.",
    "Capricorn": "Votre pensee est stratégique et disciplinée. Vous planifiez à long terme et communiquez avec autorité et sérieux. Votre esprit est structuré comme une architecture solide. Vous n'aiméz pas les bavardages inutiles et privilégiez la substance sur le style. Votre sagesse intellectuelle s'approfondit avec l'age.",
    "Aquarius": "Votre esprit est original, visionnaire et parfois révolutionnaire. Vous pensez en dehors des cadres établis et vos idées sont souvent en avance sur leur temps. Votre communication est surprenante et stimulante. Vous êtes attiré(e) par les nouvelles technologies et les concepts avant-gardistes.",
    "Pisces": "Votre pensee est intuitive, poétique et réceptive. Votre esprit fonctionne par images, symboles et impressions plutôt que par logique pure. Vous êtes doué(e) pour comprendre les nuances émotionnelles et les courants invisibles. Votre imagination est votre plus grand outil intellectuel."
}

# ============= VENUS EN SIGNE =============
VENUS_EN_SIGNE = {
    "Aries": "En amour, vous êtes passionnée(e) et spontané(e). Vous aiméz la conquête et les débuts électrisants. Votre façon d'aimér est directe, impulsive et courageuse. Vous avez besoin d'excitement et de nouveauté dans vos relations. Votre plus grand défi amoureux est la patience et la constance.",
    "Taurus": "Venus est chez elle en Taureau, vous offrant un sens inégalable de la beauté et du plaisir. Vous aiméz avec fidélité, sensualité et profondeur. Votre amour est stable et nourrissant, comme un jardin bien entretenu. Vous cherchez la sécurité dans vos relations et savez apprécier les plaisirs simples de la vie.",
    "Gemini": "Votre façon d'aimér passe par la communication et la complicité intellectuelle. Vous tombez amoureux(se) de l'esprit avant le corps. La variété et la stimulation mentale sont essentielles dans vos relations. Vous exprimez votre amour par les mots, les messages et le partage d'idées.",
    "Cancer": "Vous aiméz avec une profondeur émotionnelle immense. Prendre soin de l'autre est votre langage amoureux. Vous créez des nids douillets et cherchez une connexion intime et sécurisante. Votre amour est maternel, protecteur et infiniment tendre. La famille et le foyer sont au cœur de votre bonheur.",
    "Leo": "Votre amour est généreux, théâtral et lumineux. Vous aiméz être admirée(e) et admirér en retour. Vos gestes romantiques sont grands et mémorables. Vous cherchez un(e) partenaire qui vous fait sentir special(e) et que vous pouvez mettre sur un piédestal. La loyauté et la fierté sont vos valeurs amoureuses.",
    "Virgo": "Vous exprimez votre amour par les actes de service et l'attention aux détails. Votre façon d'aimér est discrete mais profondement dévouée. Vous remarquez les petits besoins de l'autre et y répondez avec précision. Le défi est d'accepter l'imperfection chez l'autre et en vous-meme.",
    "Libra": "Venus est chez elle en Balance, faisant de vous un(e) amoureux(se) de l'amour lui-meme. Vous êtes né(e) pour les relations harmonieuses, la beauté partagee et les partenariats équilibres. Votre charme est irrésistible. Vous avez besoin d'un(e) partenaire qui soit aussi un(e) ami(e) et un(e) égal(e).",
    "Scorpio": "Votre amour est intense, transformateur et absolu. Vous ne connaissez pas les demi-mesures en amour : c'est tout ou rien. La passion et la profondeur émotionnelle sont vos carburants relationnels. Vous cherchez la fusion totale avec l'être aimé. La jalousie peut être un défi à transcender.",
    "Sagittarius": "Vous aiméz avec enthousiasme, générosité et un esprit d'aventure. La liberté dans la relation est essentielle pour vous. Vous êtes attiré(e) par les personnes qui partagent votre soif de découverte et d'apprentissage. L'humour et la philosophie sont au cœur de vos relations.",
    "Capricorn": "Votre façon d'aimér est sérieuse, engagée et orientée vers le long terme. Vous ne vous engagez pas à la légère, mais quand vous le faites, c'est pour la vie. Vous construisez vos relations comme des édifices solides. Le temps renforce vos liens plutôt que de les affaiblir.",
    "Aquarius": "Votre amour est original, libre et humaniste. Vous cherchez un(e) partenaire qui soit aussi votre meilleur(e) ami(e) et un(e) allié(e) intellectuel(le). La liberté individuelle au sein du couple est essentielle. Vous aiméz avec détachement, ce qui peut dérouter les natures plus émotionnelles.",
    "Pisces": "Venus est exaltée en Poissons, vous offrant la capacité d'aimér de maniere inconditionnelle et transcendante. Votre amour est poétique, sacrificiel et spirituel. Vous idéalisez souvent vos partenaires et vos relations. Votre plus grand don est votre compassion infinie, votre défi est de garder les pieds sur terre."
}

# ============= MARS EN SIGNE =============
MARS_EN_SIGNE = {
    "Aries": "Mars est chez lui en Bélier, vous conférant une énergie d'action formidable. Vous foncez tête baissée vers vos objectifs avec un courage indomptable. Votre colère est explosive mais de courte durée. Vous excellez dans la compétition et les débuts de projets. Votre énergie physique est remarquable.",
    "Taurus": "Votre énergie d'action est lente à démarrer mais implacable une fois lancée. Vous agissez avec méthode, persévérance et détermination. Votre patience est une arme redoutable. Quand vous vous mettez en colère, c'est un tremblement de terre qui couvait depuis longtemps. Vos résultats sont durables.",
    "Gemini": "Votre énergie s'exprime à travers la communication et la stimulation mentale. Vous agissez vite, changez de stratégie facilement et jonglez entre plusieurs projets. Votre force est dans votre adaptabilité et votre vivacité. Le défi est de maintenir la concentration sur un seul objectif à la fois.",
    "Cancer": "Votre énergie d'action est guidée par vos émotions et votre instinct protecteur. Vous vous battez férocement pour ceux que vous aiméz et pour votre sécurité. Votre motivation fluctue avec vos humeurs. Quand vous êtes émotionnellement investi(e), votre détermination est inébranlable.",
    "Leo": "Votre énergie est rayonnante, créative et théâtrale. Vous agissez avec panache et générosité. Vous êtes motivé(e) par la reconnaissance et le désir de laisser votre empreinte. Votre leadership naturel inspire les autres à agir. Votre colère est royale et impressionnante.",
    "Virgo": "Votre énergie s'exprime à travers le service, l'analyse et le perfectionnement. Vous agissez avec précision et méthode, preferant la stratégie à la force brute. Vous êtes motivé(e) par le désir d'améliorer et d'organiser. Votre productivité est remarquable quand vous canalisez votre énergie.",
    "Libra": "Votre énergie d'action cherche l'équilibre et la justice. Vous agissez de maniere diplomatique et coopérative. La confrontation directe vous met mal à l'aise, mais vous vous battez avec élégance pour ce qui est juste. Vous excellez dans les négociations et les partenariats stratégiques.",
    "Scorpio": "Mars est puissant en Scorpion, vous dotant d'une intensité et d'une détermination hors du commun. Votre énergie est stratégique, pénétrante et transformatrice. Vous n'abandonnez jamais et votre volonté est d'acier. Votre force réside dans votre capacité à vous régénérer apres chaque épreuve.",
    "Sagittarius": "Votre énergie est expansive, optimiste et aventurière. Vous agissez avec enthousiasme et vision. Votre motivation vient de votre quête de sens et de liberté. Vous excellez dans les entreprises qui demandent de l'audace et une vision large. L'immobilisme est votre pire ennemi.",
    "Capricorn": "Mars est exalté en Capricorne, vous conférant une discipline et une endurance exceptionnelles. Votre énergie est stratégique, patiente et orientée vers des objectifs à long terme. Vous grimpez les montagnes pas à pas, sans jamais perdre de vue le sommet. Votre ambition est votre moteur le plus puissant.",
    "Aquarius": "Votre énergie d'action est originale, indépendante et humaniste. Vous agissez pour des causes qui depassent votre intérêt personnel. Votre approche est non conventionnelle et parfois révolutionnaire. Vous êtes motivé(e) par le désir de changer le monde et de défendre la liberté.",
    "Pisces": "Votre énergie s'exprime de maniere fluide, intuitive et compassionnélle. Vous agissez guidé(e) par votre intuition et votre empathie. La créativité et la spiritualité sont des moteurs puissants pour vous. Le défi est de transformer vos rêves en actions concrêtes et de poser des limites saines."
}

# ============= JUPITER EN SIGNE =============
JUPITER_EN_SIGNE = {
    "Aries": "Votre chance et votre expansion se manifestent quand vous prenez l'initiative et osez être le(la) premier(e). L'audace et le courage sont récompensées. Les opportunités affluent quand vous agissez avec confiance et independance.",
    "Taurus": "L'abondance vient à vous par la patience et la constance. Vous avez un talent naturel pour attirér la prospérité matérielle. Les plaisirs de la vie vous nourrissent et votre sens des affaires est excellent.",
    "Gemini": "Votre expansion passe par la communication, les échanges et l'apprentissage. Les voyages courts, les contacts et le partage d'idées sont des sources de chance. Votre curiosité vous ouvre des portes inattendues.",
    "Cancer": "Votre chance réside dans le domaine familial et émotionnel. La générosité envers vos proches vous est rendue au centuple. Votre intuition est un guidé fiable pour saisir les bonnes opportunités.",
    "Leo": "L'abondance afflue quand vous exprimez votre créativité et votre générosité. Votre charisme naturel attiré les opportunités. Les arts, le divertissement et le leadership sont des domaines favorisés.",
    "Virgo": "Votre expansion se manifeste par le service, le travail consciencieux et l'attention aux détails. La sante et le bien-être sont des domaines ou la chance vous sourit. Votre humilité est paradoxalement votre plus grand atout.",
    "Libra": "Les partenariats et les collaborations sont vos plus grandes sources d'abondance. La justice, l'art et la diplomatie sont favorisés. Votre sens de l'équilibre attiré naturellement l'harmonie et la prospérité.",
    "Scorpio": "Votre expansion passe par les transformations profondes et les crises qui revelent votre force. Les heritages, les investissements et la régénération sont favorisés. Votre capacité à renaître de vos cendres est votre plus grande chance.",
    "Sagittarius": "Jupiter est chez lui en Sagittaire, amplificant votre chance naturelle. Les voyages, les études supérieures et la quête de sens sont des domaines benis. Votre optimisme et votre foi en la vie attirént les miracles.",
    "Capricorn": "Votre expansion est lente mais solide. La discipline, l'ambition et la patience finissent toujours par payer. Les récompensées viennent avec le temps et la maturité. Votre sens des responsabilites est votre meilleur investissement.",
    "Aquarius": "Votre chance se manifeste dans les domaines de l'innovation, de la technologie et de l'humanisme. Les projets collectifs et les idées originales sont favorisés. Votre vision du futur attiré les opportunités avant-gardistes.",
    "Pisces": "Jupiter est exalté en Poissons, vous conférant une grâce et une protection spirituelle particulières. Votre compassion et votre foi sont récompensées. Les domaines artistiques et spirituels sont des sources d'abondance naturelles."
}

# ============= SATURNE EN SIGNE =============
SATURNE_EN_SIGNE = {
    "Aries": "Votre leçon karmique concerne l'autonomie et l'affirmation de soi. Vous devez apprendre à prendre des initiatives sans crainte. Les défis vous enseignent le courage authentique, different de l'impulsivité.",
    "Taurus": "Votre leçon touche la sécurité matérielle et l'estime de soi. Vous devez construire votre propre stabilité sans vous accrocher excessivement aux possessions. La vraie richesse vient de l'intérieur.",
    "Gemini": "Votre leçon concerne la communication et la pensee structurée. Vous devez apprendre à approfondir vos connaissances plutôt que de les survoler. La discipline mentale est votre chemin vers la maitrise.",
    "Cancer": "Votre leçon porte sur les émotions et la famille. Vous devez etablir des limites saines dans vos relations proches tout en restant ouvert(e) à la vulnérabilité. La maturité émotionnelle est votre objectif.",
    "Leo": "Votre leçon concerne la créativité et la reconnaissance. Vous devez apprendre à briller sans dependre des applaudissements des autres. La vraie confiance vient de l'authenticité, non de la validation externe.",
    "Virgo": "Votre leçon touche le perfectionnisme et le service. Vous devez apprendre que l'excellence ne signifie pas la perfection. L'acceptation de vos limites humaines est une forme de sagesse supérieure.",
    "Libra": "Votre leçon porte sur les relations et l'équilibre. Vous devez apprendre à être juste sans sacrifier vos propres besoins. L'engagement authentique demande parfois de faire des choix difficiles.",
    "Scorpio": "Votre leçon concerne le pouvoir et la transformation. Vous devez apprendre à lacher prise et à faire confiance au processus de la vie. Le controle est une illusion ; la veritable force est dans la reddition consciente.",
    "Sagittarius": "Votre leçon touche la liberté et la quête de sens. Vous devez structurér votre enthousiasme et transformer vos visions en realites concrêtes. La discipline dans la foi est votre chemin.",
    "Capricorn": "Saturne est chez lui en Capricorne, renforçant votre sens des responsabilites et votre ambition. Votre leçon est d'équilibrer le travail avec la chaleur humaine. Le succes sans amour est une reussite incomplete.",
    "Aquarius": "Saturne est également chez lui en Verseau, vous dotant d'une vision structurée du progres collectif. Votre leçon est d'incarner le changement que vous voulez voir dans le monde, pas seulement de le théoriser.",
    "Pisces": "Votre leçon concerne la spiritualité et les limites. Vous devez apprendre à transformer votre compassion en action concrete sans vous noyer dans la souffrance des autres. La discipline spirituelle est votre ancré."
}

# ============= DESCRIPTIONS DES ASPECTS =============
ASPECTS_TYPES = {
    "Conjunction": {
        "nom_fr": "Conjonction",
        "symbole": "0 deg",
        "nature": "fusion",
        "description": "Les énergies de ces deux planêtes fusionnent, creant une force concentree et puissante. Cette union amplifie les qualites des deux astres, pour le meilleur et le plus intense.",
    },
    "Sextile": {
        "nom_fr": "Sextile",
        "symbole": "60 deg",
        "nature": "harmonieux",
        "description": "Un aspect d'opportunite et de fluidite. Les énergies de ces planêtes cooperent naturellement, offrant des talents et des possibilites qui demandent juste un leger effort pour être actives.",
    },
    "Square": {
        "nom_fr": "Carre",
        "symbole": "90 deg",
        "nature": "tendu",
        "description": "Un aspect de tension creatrice et de croissance. Ces deux énergies se confrontent, creant des défis qui vous poussent à evoluer. C'est souvent la source de vos plus grandes realisations.",
    },
    "Trine": {
        "nom_fr": "Trigone",
        "symbole": "120 deg",
        "nature": "harmonieux",
        "description": "Un aspect de grâce naturelle et de talent inne. Les énergies de ces planêtes coulent ensemble avec aisance, revelant des dons qui semblent presque magiques.",
    },
    "Opposition": {
        "nom_fr": "Opposition",
        "symbole": "180 deg",
        "nature": "tendu",
        "description": "Un aspect de conscience et d'équilibre. Ces deux énergies se font face, vous invitant à integrer des forces apparemment opposees. La cle est de trouver le point d'équilibre.",
    }
}

# Interpretations specifiques des aspects entre planêtes majeures
ASPECTS_PLANETES = {
    ("Sun", "Moon"): {
        "harmonieux": "Votre volonté et vos émotions sont en harmonie. Vous êtes en paix avec vous-meme, ce qui vous donne une stabilité intérieure remarquable. Vos besoins émotionnels et vos aspirations conscientes s'alignent naturellement.",
        "tendu": "Une tension existe entre votre identite consciente et vos besoins émotionnels profonds. Ce que vous voulez et ce dont vous avez besoin ne coincident pas toujours. Cette dualite, une fois comprise, devient une source de richesse intérieure.",
        "fusion": "Votre ego et vos émotions sont fusionnes, creant une personnalite intense et entiere. Vous vivez tout avec une grande sincerite. Votre défi est de distinguer entre ce que vous êtes et ce que vous ressentez."
    },
    ("Sun", "Mercury"): {
        "harmonieux": "Votre intellect sert parfaitement votre identite. Vous vous exprimez avec clarte et authenticité.",
        "tendu": "Votre mental peut parfois entrer en conflit avec votre veritable nature, creant une tension entre ce que vous pensez et qui vous êtes.",
        "fusion": "Votre esprit et votre identite ne font qu'un. Vous êtes profondement identifie(e) à vos idées et à votre façon de communiquer."
    },
    ("Sun", "Venus"): {
        "harmonieux": "Votre identite est naturellement liee à l'amour et à la beauté. Vous degagez un charme naturel et savez creer l'harmonie autour de vous.",
        "tendu": "Des tensions entre votre désir d'être aimé(e) et votre besoin d'être vous-meme. L'apprentissage est de ne pas sacrifier votre identite pour plaire aux autres.",
        "fusion": "Votre identite est intimement liee à votre capacité d'aimér. Vous êtes naturellement charmant(e) et attirant(e)."
    },
    ("Sun", "Mars"): {
        "harmonieux": "Votre volonté et votre énergie d'action travaillent main dans la main. Vous realisez vos projets avec efficacite et détermination. Votre vitalite est forte.",
        "tendu": "Une tension entre votre ego et votre maniere d'agir. Parfois votre énergie se retourne contre vous sous forme d'agressivite ou de frustration. Canalisez cette force creatrice.",
        "fusion": "Votre identite et votre énergie sont fusionnees, creant une personnalite dynamique et proactive. L'action est au cœur de votre être."
    },
    ("Sun", "Jupiter"): {
        "harmonieux": "La chance et l'expansion accompagnent votre chemin de vie. Vous inspirez confiance et attiréz naturellement les opportunités. Votre optimisme est contagieux.",
        "tendu": "Tendance à l'exces et à la surestimation de vos capacités. L'apprentissage est de canaliser votre enthousiasme sans disperser vos énergies.",
        "fusion": "Votre personnalite est naturellement expansive et optimiste. Vous avez une foi profonde en la vie et en vos capacités."
    },
    ("Sun", "Saturn"): {
        "harmonieux": "Votre discipline et votre sens des responsabilites soutiennent vos ambitions. Vous batissez des reussites durables avec patience et maturité.",
        "tendu": "Des blocages et des limitations marquent votre parcours, mais chaque obstacle vous forge. La maturité et la persévérance sont vos alliés. Le succes vient avec le temps.",
        "fusion": "Votre identite est profondement liee au sens du devoir et de la structuré. Vous êtes né(e) pour assumer de grandes responsabilites."
    },
    ("Moon", "Venus"): {
        "harmonieux": "Vos émotions et votre capacité d'aimér sont en parfaite harmonie. Vous créez des relations douces et nourrissantes. Votre sensibilite est un atout dans l'amour.",
        "tendu": "Des tensions entre vos besoins émotionnels et vos désirs amoureux. Ce que vous ressentez et ce que vous désirez ne coincident pas toujours.",
        "fusion": "Vos émotions et votre amour sont fusionnes. Vous aiméz avec tout votre être et créez des liens profondement intimes."
    },
    ("Moon", "Mars"): {
        "harmonieux": "Vos émotions alimentent votre énergie d'action. Vous agissez avec passion et instinct. Votre courage émotionnel est remarquable.",
        "tendu": "Vos émotions peuvent declencher des reactions impulsives. L'apprentissage est de canaliser votre énergie émotionnelle de maniere constructive.",
        "fusion": "Vos émotions et votre énergie sont fusionnees, creant des reactions intenses et immediates. Votre passion est votre moteur."
    },
    ("Venus", "Mars"): {
        "harmonieux": "L'amour et le désir coulent naturellement ensemble. Vous avez un magnetisme naturel et savez équilibrer tendresse et passion dans vos relations.",
        "tendu": "Tension entre ce que vous désirez et ce que vous aiméz. La passion peut creer des conflits dans vos relations. L'integration de ces forces vous rend irrésistible.",
        "fusion": "Amour et désir sont fusionnes, creant un magnetisme puissant. Votre passion amoureuse est votre signature energetique."
    },
    ("Jupiter", "Saturn"): {
        "harmonieux": "L'expansion et la structuré travaillent ensemble. Vous savez quand accelerer et quand consolider. Vos reussites sont à la fois ambitieuses et solides.",
        "tendu": "Tension entre le désir d'expansion et le besoin de structuré. Vous oscillez entre optimisme et prudence. L'équilibre entre les deux est votre sagesse.",
        "fusion": "La chance et la discipline se rencontrent, creant un potentiel remarquable pour des realisations majeures et durables."
    },
}

# ============= RETROGRADES =============
RETROGRADE_DESCRIPTIONS = {
    "Mercury": "Mercure retrograde dans votre theme natal indique que votre processus de pensee est introspectif et profond. Vous revisitez souvent vos idées et vos communications. Cette position vous donne une capacité exceptionnelle de reflexion et d'analyse retrospective. Vous apprenez souvent davantage des revisions que des premieres tentatives.",
    "Venus": "Venus retrograde suggere que votre relation à l'amour et à la beauté est interiorisee. Vous avez un sens unique de l'esthetique et de la valeur qui ne correspond pas toujours aux normes sociales. En amour, vous avez besoin de temps pour comprendre vos sentiments. Les relations karmiques font partie de votre parcours.",
    "Mars": "Mars retrograde indique que votre énergie d'action est dirigee vers l'intérieur. Vous pouvez avoir du mal à exprimer directement votre colère ou votre désir. Votre force est plus subtile et stratégique que frontale. Apprenez à canaliser cette énergie intérieure de maniere constructive.",
    "Jupiter": "Jupiter retrograde signifie que votre croissance et votre expansion se font d'abord intérieurement. La chance vient de votre monde intérieur avant de se manifester exterieurement. Vous trouvez la sagesse en vous-meme plutôt que dans les enseignements exterieurs.",
    "Saturn": "Saturne retrograde suggere que vos leçons karmiques sont profondement interiorisees. Vous êtes souvent plus dur(e) avec vous-meme qu'avec les autres. La structuré que vous devez construire est d'abord intérieure. Avec le temps, votre autodiscipline devient votre plus grande force.",
    "Uranus": "Uranus retrograde indique que votre originalite et votre rebellion se vivent intérieurement. Vous remettez en question les normes de maniere privee avant de les défier publiquement. Votre revolution personnelle est un processus intime et profond.",
    "Neptune": "Neptune retrograde signifie que votre spiritualité et votre imagination sont tournees vers l'intérieur. Vos rêves sont particulierement significatifs et vous avez une capacité naturelle de meditation. La frontiere entre reve et realite est fluide pour vous.",
    "Pluto": "Pluton retrograde indique que vos transformations les plus profondes se font dans l'intimite de votre être. Vous possedez un pouvoir intérieur immense. Les renaissances que vous vivez sont silencieuses mais radicales."
}

# ============= ELEMENTS =============
ELEMENTS_DOMINANTS = {
    "Feu": {
        "dominant": "Votre theme est domine par l'element Feu, ce qui vous confère une énergie vitale exceptionnelle, de l'enthousiasme et un esprit d'initiative. Vous êtes naturellement optimiste, passionné(e) et tourné(e) vers l'action. Votre défi est d'apprendre la patience et la constance.",
        "faible": "Avec peu de Feu dans votre theme, vous pouvez manquer parfois d'initiative spontanée ou de confiance en vous. Cultivez l'audace et l'action pour équilibrer votre theme."
    },
    "Terre": {
        "dominant": "Votre theme est domine par l'element Terre, vous ancrant solidement dans la realite. Vous êtes pragmatique, fiable et perseverant(e). Les realisations concrêtes et la sécurité matérielle sont importantes pour vous. Votre défi est de ne pas trop vous attacher au monde materiel.",
        "faible": "Avec peu de Terre dans votre theme, vous pouvez avoir du mal à concretiser vos idées ou à maintenir une stabilité matérielle. Cultivez l'ancrage et la discipline pratique."
    },
    "Air": {
        "dominant": "Votre theme est domine par l'element Air, faisant de vous un(e) penseur(se) et communicant(e) né(e). Les idées, les relations sociales et les échanges intellectuels sont votre oxygene. Votre défi est de rester connecte(e) à vos émotions et à votre corps.",
        "faible": "Avec peu d'Air dans votre theme, la communication abstraite et les relations sociales peuvent être un défi. Cultivez l'ecoute, l'objectivite et le détachement sain."
    },
    "Eau": {
        "dominant": "Votre theme est domine par l'element Eau, vous conférant une sensibilite et une intuition profondes. Vous percevez les courants émotionnels invisibles et ressentez ce que les autres ne voient pas. Votre défi est de ne pas vous laisser submerger par les émotions.",
        "faible": "Avec peu d'Eau dans votre theme, l'acces à vos émotions profondes peut être difficile. Cultivez l'empathie, l'intuition et la connexion émotionnelle avec les autres."
    }
}

MODALITES_DESCRIPTIONS = {
    "Cardinal": "Energie d'initiation et de leadership. Vous êtes un(e) lanceur(se) de projets et un(e) moteur de changement.",
    "Fixe": "Energie de stabilité et de persévérance. Vous êtes fiable, determiné(e) et resistant(e) au changement.",
    "Mutable": "Energie d'adaptation et de flexibilite. Vous excellez dans les transitions et les ajustements."
}

# ============= CHIRON EN SIGNE =============
CHIRON_EN_SIGNE = {
    "Aries": "Votre blessure profonde touche votre identite et votre droit d'exister. Vous guerissez en apprenant à vous affirmer avec authenticité et en aidant les autres à trouver leur propre voix.",
    "Taurus": "Votre blessure concerne la sécurité et l'estime de soi. Vous guerissez en construisant une valeur intérieure qui ne depend pas des possessions matérielles.",
    "Gemini": "Votre blessure touche la communication et la pensee. Vous guerissez en apprenant que vos idées ont de la valeur et en partageant votre sagesse unique.",
    "Cancer": "Votre blessure concerne la famille et la sécurité émotionnelle. Vous guerissez en creant la famille émotionnelle que vous meritez et en offrant aux autres le soin que vous avez cherche.",
    "Leo": "Votre blessure touche l'expression de soi et la créativité. Vous guerissez en osant briller malgre la peur du rejet et en encourageant les autres à faire de meme.",
    "Virgo": "Votre blessure concerne le perfectionnisme et le service. Vous guerissez en acceptant votre humanite imparfaite et en decouvrant que vous êtes utile tel(le) que vous êtes.",
    "Libra": "Votre blessure touche les relations et l'équilibre. Vous guerissez en trouvant votre propre centre plutôt que de vous définir à travers les autres.",
    "Scorpio": "Votre blessure concerne le pouvoir et la transformation. Vous guerissez en apprenant à faire confiance apres la trahison et en transformant votre douleur en sagesse profonde.",
    "Sagittarius": "Votre blessure touche le sens et la foi. Vous guerissez en trouvant votre propre verite plutôt que de suivre les croyances des autres.",
    "Capricorn": "Votre blessure concerne l'autorité et la reussite. Vous guerissez en définissant le succes selon vos propres termes plutôt que ceux de la societe.",
    "Aquarius": "Votre blessure touche l'appartenance et l'originalite. Vous guerissez en acceptant que votre difference est votre contribution unique au monde.",
    "Pisces": "Votre blessure concerne la connexion spirituelle et les limites. Vous guerissez en trouvant l'équilibre entre la compassion universelle et la protection de votre espace intérieur."
}

# ============= NOEUD NORD EN SIGNE =============
NOEUD_NORD_EN_SIGNE = {
    "Aries": "Votre destinee vous appelle vers l'autonomie et le courage. Vous devez apprendre à prendre des décisions seul(e) et à vous affirmer, meme si cela derange l'équilibre.",
    "Taurus": "Votre destinee vous guidé vers la simplicite, la stabilité et l'appreciation des plaisirs terrestres. Apprenez à construire quelque chose de durable plutôt que de chercher l'intensité.",
    "Gemini": "Votre destinee vous appelle vers la communication, la curiosité et l'ouverture d'esprit. Echangez, ecoutez, apprenez des autres plutôt que de rester dans vos certitudes.",
    "Cancer": "Votre destinee vous guidé vers la vulnérabilité, la famille et la connexion émotionnelle. Apprenez à nourrir les liens intimes plutôt que de tout sacrifier pour la reussite.",
    "Leo": "Votre destinee vous appelle à briller, à exprimer votre créativité et à rayonner de votre lumiere unique. Cessez de vous fondre dans le groupe.",
    "Virgo": "Votre destinee vous guidé vers le service concret, la précision et l'humilité. Transformez vos rêves en actions pratiques qui ameliorent le quotidien.",
    "Libra": "Votre destinee vous appelle vers les relations, la cooperation et la recherche d'harmonie. Apprenez l'art du compromis et de la diplomatie.",
    "Scorpio": "Votre destinee vous guidé vers la profondeur, la transformation et l'intimite authentique. N'ayez pas peur des zones d'ombre, c'est la que se trouve votre pouvoir.",
    "Sagittarius": "Votre destinee vous appelle vers l'expansion, la philosophie et les grands horizons. Osez voir plus loin que votre environnement immediat.",
    "Capricorn": "Votre destinee vous guidé vers la maitrise, la responsabilite et la construction d'un heritage durable. Assumez votre autorité naturelle.",
    "Aquarius": "Votre destinee vous appelle vers l'innovation, la communaute et la vision du futur. Votre role est d'amener des idées nouvelles au service du collectif.",
    "Pisces": "Votre destinee vous guidé vers la spiritualité, la compassion et la dissolution de l'ego. Apprenez à faire confiance au flux de la vie et à servir quelque chose de plus grand que vous."
}

# ============= LILITH EN SIGNE =============
LILITH_EN_SIGNE = {
    "Aries": "Lilith Noire en Bélier revele une puissance brute d'affirmation de soi. Vous portez en vous une rage creatrice qui, une fois apprivoisee, devient une force de liberation.",
    "Taurus": "Lilith en Taureau pointe vers des enjeux de possessivite et de rapport au plaisir. Votre défi est de profiter de l'abondance sans vous y attacher de maniere obsessionnelle.",
    "Gemini": "Lilith en Gémeaux revele un pouvoir lie à la parole et à la connaissance. Vos mots peuvent guerir ou blessér avec une force inhabituelle.",
    "Cancer": "Lilith en Cancer met en lumiere des enjeux émotionnels profonds lies à la mere et au foyer. Votre pouvoir réside dans votre capacité à transformer les blessures familiales en sagesse.",
    "Leo": "Lilith en Lion revele un pouvoir créatif intense et un magnetisme hors du commun. Votre défi est d'utiliser ce charisme pour inspirer plutôt que pour dominer.",
    "Virgo": "Lilith en Vierge pointe vers la perfection comme instrument de pouvoir. Votre défi est d'accepter l'imperfection comme une forme de beauté et de liberation.",
    "Libra": "Lilith en Balance revele des enjeux de pouvoir dans les relations. Votre défi est de trouver l'équilibre entre independance et intimite sans manipulation.",
    "Scorpio": "Lilith est puissante en Scorpion, amplifiant votre magnetisme et votre capacité de transformation. Vous pouvez acceder à des profondeurs psychiques que peu de personnes osent explorer.",
    "Sagittarius": "Lilith en Sagittaire revele un pouvoir lie à la liberté et à la verite. Votre défi est de vivre selon vos propres croyances sans imposer votre vision aux autres.",
    "Capricorn": "Lilith en Capricorne met en lumiere des enjeux d'autorité et d'ambition. Votre défi est d'utiliser votre pouvoir de maniere ethique et au service du bien commun.",
    "Aquarius": "Lilith en Verseau revele un pouvoir de rebellion et d'originalite. Votre défi est de rester fidele à votre vision unique tout en restant connecte(e) aux autres.",
    "Pisces": "Lilith en Poissons revele un pouvoir spirituel et psychique profond. Votre défi est de canaliser cette sensibilite sans vous perdre dans les illusions."
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
