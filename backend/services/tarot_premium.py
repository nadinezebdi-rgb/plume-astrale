"""
Service Tarot Premium - Tirages Marseille et Croix Celtique
Avec formulaire de question personnalisé
"""
import random
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

# ═══════════════════════════════════════════════════════════════════════════════
# 22 ARCANES MAJEURS DU TAROT DE MARSEILLE - Interprétations complètes
# ═══════════════════════════════════════════════════════════════════════════════

ARCANES_MAJEURS = {
    0: {
        "nom": "Le Mat",
        "nom_en": "The Fool",
        "mots_cles": ["Liberté", "Nouveaux départs", "Spontanéité", "Foi"],
        "element": "Air",
        "planete": "Uranus",
        "couleur": "#7DD3FC",  # Bleu ciel
        "symbole": "✧",
        "description": "Le Mat représente le voyageur de l'âme, celui qui ose partir sans bagage vers l'inconnu. Il incarne la liberté absolue, le potentiel infini et la confiance aveugle en la vie.",
        "droit": {
            "general": "Un nouveau chapitre s'ouvre devant vous. C'est le moment de faire confiance à la vie et d'oser le saut dans l'inconnu. L'univers vous soutient dans cette aventure.",
            "amour": "Une rencontre inattendue ou un renouveau dans votre relation. Laissez-vous surprendre par l'amour sous une forme nouvelle.",
            "travail": "Opportunité de changement radical. Un nouveau projet, une nouvelle direction. Osez sortir des sentiers battus.",
            "conseil": "Faites confiance à votre intuition et lancez-vous. La peur est normale, mais elle ne doit pas vous arrêter."
        },
        "renverse": {
            "general": "Vous fuyez peut-être une situation au lieu de l'affronter. L'impulsivité pourrait vous jouer des tours.",
            "amour": "Attention à l'instabilité émotionnelle. Évitez les décisions précipitées en amour.",
            "travail": "Risque de dispersion ou de projets mal préparés. Prenez le temps de la réflexion.",
            "conseil": "Ralentissez et posez-vous les bonnes questions avant d'agir."
        }
    },
    1: {
        "nom": "Le Bateleur",
        "nom_en": "The Magician",
        "mots_cles": ["Création", "Habileté", "Potentiel", "Action"],
        "element": "Air",
        "planete": "Mercure",
        "description": "Le Bateleur est le magicien créateur qui a tous les outils à sa disposition. Il représente le commencement conscient, la volonté de créer et le pouvoir de manifestation.",
        "droit": {
            "general": "Vous avez tous les atouts en main pour réussir. C'est le moment d'agir avec confiance et créativité. Votre potentiel est immense.",
            "amour": "Communication fluide et connexion intellectuelle forte. Vous savez séduire par votre esprit et votre charme.",
            "travail": "Excellente période pour lancer de nouveaux projets. Votre créativité et votre débrouillardise seront récompensées.",
            "conseil": "Utilisez tous vos talents. Vous êtes plus capable que vous ne le pensez."
        },
        "renverse": {
            "general": "Dispersion d'énergie ou manipulation. Attention à ne pas vous éparpiller ou à abuser de votre influence.",
            "amour": "Méfiez-vous des belles paroles sans substance. Quelqu'un pourrait ne pas être sincère.",
            "travail": "Projets mal planifiés ou manque de concentration. Recentrez-vous sur l'essentiel.",
            "conseil": "Canalisez votre énergie et soyez honnête dans vos intentions."
        }
    },
    2: {
        "nom": "La Papesse",
        "nom_en": "The High Priestess",
        "mots_cles": ["Intuition", "Mystère", "Sagesse", "Secrets"],
        "element": "Eau",
        "planete": "Lune",
        "description": "La Papesse garde les secrets de l'univers. Elle représente l'intuition profonde, la sagesse intérieure et les vérités qui se révèlent dans le silence.",
        "droit": {
            "general": "Écoutez votre voix intérieure. La réponse que vous cherchez est déjà en vous. Faites confiance à votre intuition.",
            "amour": "Des sentiments profonds se cachent sous la surface. Patience et observation révéleront la vérité.",
            "travail": "Période de réflexion nécessaire. Ne vous précipitez pas. Des informations importantes vont se révéler.",
            "conseil": "Méditez, faites silence et écoutez. La sagesse vient de l'intérieur."
        },
        "renverse": {
            "general": "Vous ignorez peut-être des signaux importants. Des secrets ou des non-dits perturbent la situation.",
            "amour": "Manque de communication ou secrets qui pèsent. Il est temps de parler ouvertement.",
            "travail": "Informations cachées qui pourraient vous affecter. Restez vigilant.",
            "conseil": "Sortez du silence et exprimez ce que vous ressentez vraiment."
        }
    },
    3: {
        "nom": "L'Impératrice",
        "nom_en": "The Empress",
        "mots_cles": ["Abondance", "Fertilité", "Créativité", "Nature"],
        "element": "Terre",
        "planete": "Vénus",
        "description": "L'Impératrice incarne la Mère créatrice, l'abondance naturelle et le pouvoir de donner la vie. Elle représente la fertilité sous toutes ses formes.",
        "droit": {
            "general": "Période d'abondance et de croissance. Vos projets portent leurs fruits. La créativité coule en vous.",
            "amour": "Amour nourrissant et épanouissant. Possible grossesse ou naissance d'un nouveau projet à deux.",
            "travail": "Succès dans les domaines créatifs. Vos efforts sont récompensés avec générosité.",
            "conseil": "Nourrissez ce qui compte pour vous. L'abondance vient de l'attention et de l'amour."
        },
        "renverse": {
            "general": "Blocage créatif ou dépendance excessive. Attention à l'étouffement ou à la surprotection.",
            "amour": "Possessivité ou déséquilibre dans le don et la réception. Retrouvez votre indépendance.",
            "travail": "Stagnation ou manque de productivité. Reconnectez-vous à votre inspiration.",
            "conseil": "Lâchez le contrôle et laissez les choses se développer naturellement."
        }
    },
    4: {
        "nom": "L'Empereur",
        "nom_en": "The Emperor",
        "mots_cles": ["Autorité", "Structure", "Stabilité", "Pouvoir"],
        "element": "Feu",
        "planete": "Mars",
        "description": "L'Empereur est le bâtisseur et le protecteur. Il représente l'autorité naturelle, la structure solide et la capacité à construire des fondations durables.",
        "droit": {
            "general": "Temps de prendre le contrôle de votre vie. Structure, discipline et organisation vous mèneront au succès.",
            "amour": "Relation stable et sécurisante. Un partenaire fiable et protecteur. Engagement solide.",
            "travail": "Promotion ou reconnaissance de votre leadership. Vous êtes en position de pouvoir.",
            "conseil": "Assumez votre autorité avec sagesse. La discipline est votre alliée."
        },
        "renverse": {
            "general": "Rigidité excessive ou abus de pouvoir. Le contrôle devient oppressant.",
            "amour": "Domination ou manque de flexibilité dans la relation. Apprenez à lâcher prise.",
            "travail": "Conflits d'autorité ou environnement trop restrictif. Remettez en question les règles.",
            "conseil": "Assouplissez votre approche. Le vrai pouvoir n'a pas besoin de s'imposer."
        }
    },
    5: {
        "nom": "Le Pape",
        "nom_en": "The Hierophant",
        "mots_cles": ["Sagesse", "Tradition", "Enseignement", "Spiritualité"],
        "element": "Terre",
        "planete": "Jupiter",
        "description": "Le Pape est le grand maître spirituel qui transmet la connaissance sacrée. Il représente la tradition, l'enseignement et la quête de sens.",
        "droit": {
            "general": "Cherchez la guidance d'un mentor ou d'une tradition. L'apprentissage et la sagesse éclairent votre chemin.",
            "amour": "Union bénie ou engagement officiel. Mariage, cérémonie ou approfondissement spirituel à deux.",
            "travail": "Formation, mentorat ou évolution dans un cadre institutionnel. Respectez les processus établis.",
            "conseil": "Ouvrez-vous à l'enseignement. La tradition a des trésors à vous offrir."
        },
        "renverse": {
            "general": "Remise en question des dogmes. Il est temps de trouver votre propre vérité.",
            "amour": "Conventions sociales qui étouffent. Osez vivre votre amour différemment.",
            "travail": "Frustration face aux règles ou besoin de liberté créative.",
            "conseil": "Respectez la sagesse du passé mais n'ayez pas peur de tracer votre propre chemin."
        }
    },
    6: {
        "nom": "L'Amoureux",
        "nom_en": "The Lovers",
        "mots_cles": ["Choix", "Amour", "Union", "Harmonie"],
        "element": "Air",
        "planete": "Vénus",
        "description": "L'Amoureux représente le grand choix du cœur. C'est l'arcane de l'amour véritable, de l'union et des décisions qui engagent notre être profond.",
        "droit": {
            "general": "Un choix important se présente. Suivez votre cœur, il connaît le chemin. L'harmonie est possible.",
            "amour": "Amour vrai et connexion profonde. Coup de foudre ou approfondissement d'une relation existante.",
            "travail": "Collaboration harmonieuse ou choix de carrière qui vous passionne.",
            "conseil": "Écoutez votre cœur autant que votre raison. Le bon choix résonne en vous."
        },
        "renverse": {
            "general": "Indécision ou conflit entre le cœur et la raison. Choix difficile à faire.",
            "amour": "Hésitation amoureuse ou relation compliquée. Clarifiez vos sentiments.",
            "travail": "Dilemme professionnel ou partenariat tendu.",
            "conseil": "Ne fuyez pas le choix. L'indécision prolongée est aussi une décision."
        }
    },
    7: {
        "nom": "Le Chariot",
        "nom_en": "The Chariot",
        "mots_cles": ["Victoire", "Volonté", "Avancement", "Triomphe"],
        "element": "Eau",
        "planete": "Lune",
        "description": "Le Chariot est le triomphateur qui avance vers la victoire. Il représente la détermination, la maîtrise des forces opposées et le succès par la volonté.",
        "droit": {
            "general": "Victoire et succès à l'horizon. Votre détermination paiera. Foncez avec confiance !",
            "amour": "Conquête amoureuse ou avancée significative dans la relation. Passion et dynamisme.",
            "travail": "Promotion, réussite d'un projet ou reconnaissance professionnelle.",
            "conseil": "Gardez le cap et ne laissez rien vous arrêter. La victoire est à portée de main."
        },
        "renverse": {
            "general": "Obstacles ou perte de contrôle. L'agressivité ou l'impatience sabotent vos efforts.",
            "amour": "Relation qui avance trop vite ou conflit de pouvoir.",
            "travail": "Projet qui déraille ou ambition mal canalisée.",
            "conseil": "Ralentissez et reprenez le contrôle. La force brute ne suffit pas toujours."
        }
    },
    8: {
        "nom": "La Justice",
        "nom_en": "Justice",
        "mots_cles": ["Équilibre", "Vérité", "Karma", "Décision"],
        "element": "Air",
        "planete": "Vénus",
        "description": "La Justice pèse les actes et tranche avec impartialité. Elle représente l'équilibre, la vérité et la loi universelle de cause à effet.",
        "droit": {
            "general": "La vérité éclate et la justice est rendue. Équilibre retrouvé. Décision juste à prendre.",
            "amour": "Relation équilibrée basée sur le respect mutuel. Engagements honorés.",
            "travail": "Reconnaissance méritée ou résolution d'un conflit. Contrat ou accord favorable.",
            "conseil": "Soyez juste et honnête. Ce que vous semez, vous le récolterez."
        },
        "renverse": {
            "general": "Injustice ou déséquilibre. Des conséquences de choix passés se manifestent.",
            "amour": "Relation déséquilibrée ou sentiment d'injustice.",
            "travail": "Décision injuste ou conflit juridique possible.",
            "conseil": "Examinez la situation avec objectivité. Assumez vos responsabilités."
        }
    },
    9: {
        "nom": "L'Hermite",
        "nom_en": "The Hermit",
        "mots_cles": ["Introspection", "Solitude", "Sagesse", "Recherche"],
        "element": "Terre",
        "planete": "Saturne",
        "description": "L'Hermite marche seul avec sa lanterne, éclairant le chemin pas à pas. Il représente la quête intérieure, la sagesse acquise et la lumière de la conscience.",
        "droit": {
            "general": "Temps de retrait et de réflexion. La solitude est féconde. Cherchez en vous les réponses.",
            "amour": "Besoin d'espace pour mieux comprendre vos sentiments. Relation mature et sage.",
            "travail": "Période de recherche ou de perfectionnement. Mentorat ou expertise reconnue.",
            "conseil": "Prenez du recul. La lumière que vous cherchez brille en vous."
        },
        "renverse": {
            "general": "Isolement excessif ou refus de demander de l'aide. Solitude qui pèse.",
            "amour": "Éloignement émotionnel ou communication rompue.",
            "travail": "Travail solitaire qui vous isole ou manque de guidance.",
            "conseil": "Sortez de votre coquille. La sagesse se partage aussi."
        }
    },
    10: {
        "nom": "La Roue de Fortune",
        "nom_en": "Wheel of Fortune",
        "mots_cles": ["Destin", "Cycles", "Changement", "Chance"],
        "element": "Feu",
        "planete": "Jupiter",
        "description": "La Roue de Fortune tourne sans cesse. Elle représente les cycles de la vie, le destin, la chance et les retournements inattendus.",
        "droit": {
            "general": "La chance tourne en votre faveur. Nouveau cycle positif. Saisissez les opportunités !",
            "amour": "Tournant favorable dans votre vie amoureuse. Rencontre ou évolution positive.",
            "travail": "Opportunité inattendue ou changement de situation favorable.",
            "conseil": "Embrassez le changement. La Roue vous porte vers le haut."
        },
        "renverse": {
            "general": "Période de turbulence ou résistance au changement. La roue peut aussi descendre.",
            "amour": "Instabilité relationnelle ou cycle difficile à traverser.",
            "travail": "Revers de fortune ou changement non désiré.",
            "conseil": "Acceptez les cycles. Ce qui descend remontera. Restez flexible."
        }
    },
    11: {
        "nom": "La Force",
        "nom_en": "Strength",
        "mots_cles": ["Courage", "Maîtrise", "Douceur", "Persévérance"],
        "element": "Feu",
        "planete": "Soleil",
        "description": "La Force dompte le lion par la douceur. Elle représente le courage intérieur, la maîtrise des instincts et la puissance tranquille.",
        "droit": {
            "general": "Votre force intérieure est immense. Domptez vos peurs avec douceur. Le courage silencieux triomphe.",
            "amour": "Passion maîtrisée et amour mature. Force du lien qui résiste aux épreuves.",
            "travail": "Persévérance récompensée. Vous surmonterez les obstacles avec grâce.",
            "conseil": "La vraie force est dans la douceur. Domptez, ne dominez pas."
        },
        "renverse": {
            "general": "Manque de confiance ou instincts mal contrôlés. Doute de soi.",
            "amour": "Passion débridée ou peur de s'engager pleinement.",
            "travail": "Épuisement ou sentiment d'impuissance face aux défis.",
            "conseil": "Reconnectez-vous à votre force intérieure. Elle est toujours là."
        }
    },
    12: {
        "nom": "Le Pendu",
        "nom_en": "The Hanged Man",
        "mots_cles": ["Lâcher-prise", "Sacrifice", "Suspension", "Révélation"],
        "element": "Eau",
        "planete": "Neptune",
        "description": "Le Pendu est suspendu entre ciel et terre, voyant le monde à l'envers. Il représente le lâcher-prise, le sacrifice volontaire et l'illumination par le changement de perspective.",
        "droit": {
            "general": "Lâchez prise et changez de perspective. Ce qui semble un blocage est une bénédiction déguisée.",
            "amour": "Voir la relation sous un nouvel angle. Sacrifice nécessaire pour évoluer ensemble.",
            "travail": "Pause nécessaire ou projet en attente. La patience porte ses fruits.",
            "conseil": "Arrêtez de lutter. La reddition consciente ouvre de nouvelles portes."
        },
        "renverse": {
            "general": "Résistance au changement ou sacrifice inutile. Blocage prolongé.",
            "amour": "Stagnation ou attachement à une situation qui ne sert plus.",
            "travail": "Situation bloquée par votre propre résistance.",
            "conseil": "Cessez de vous accrocher. Ce que vous retenez vous retient."
        }
    },
    13: {
        "nom": "L'Arcane sans Nom",
        "nom_en": "Death",
        "mots_cles": ["Transformation", "Fin", "Renaissance", "Renouveau"],
        "element": "Eau",
        "planete": "Pluton",
        "description": "L'Arcane sans Nom fauche ce qui doit partir pour que le nouveau puisse naître. Elle représente la transformation radicale, la fin nécessaire et la renaissance.",
        "droit": {
            "general": "Une fin ouvre un nouveau commencement. Transformation profonde en cours. Laissez partir l'ancien.",
            "amour": "Fin d'un cycle relationnel ou transformation profonde du lien. Renaissance possible.",
            "travail": "Changement radical de direction. Fin d'un projet pour en commencer un meilleur.",
            "conseil": "Acceptez la fin pour accueillir le renouveau. La mort est une porte, pas un mur."
        },
        "renverse": {
            "general": "Résistance à une transformation nécessaire. Peur du changement qui paralyse.",
            "amour": "Incapacité à tourner la page ou à laisser partir ce qui est mort.",
            "travail": "Stagnation par peur de l'inconnu. Changement retardé.",
            "conseil": "Ce que vous refusez de laisser partir vous empêche d'avancer."
        }
    },
    14: {
        "nom": "Tempérance",
        "nom_en": "Temperance",
        "mots_cles": ["Équilibre", "Harmonie", "Patience", "Guérison"],
        "element": "Feu",
        "planete": "Jupiter",
        "description": "Tempérance verse l'eau entre deux coupes, mêlant les contraires. Elle représente l'équilibre, la modération, la guérison et l'alchimie intérieure.",
        "droit": {
            "general": "Harmonie et équilibre retrouvés. Guérison en cours. La patience est votre alliée.",
            "amour": "Relation harmonieuse et équilibrée. Réconciliation ou apaisement des tensions.",
            "travail": "Collaboration fluide et projets qui avancent sereinement.",
            "conseil": "Trouvez le juste milieu. La modération apporte la paix intérieure."
        },
        "renverse": {
            "general": "Déséquilibre ou excès. Impatience qui perturbe l'harmonie.",
            "amour": "Relation déséquilibrée ou manque de modération dans les émotions.",
            "travail": "Projets déséquilibrés ou collaborations difficiles.",
            "conseil": "Rétablissez l'équilibre. Les extrêmes ne mènent nulle part."
        }
    },
    15: {
        "nom": "Le Diable",
        "nom_en": "The Devil",
        "mots_cles": ["Tentation", "Attachement", "Passion", "Libération"],
        "element": "Terre",
        "planete": "Saturne",
        "description": "Le Diable représente les chaînes que nous nous imposons. Il parle des attachements, des tentations et du pouvoir de se libérer de nos prisons intérieures.",
        "droit": {
            "general": "Prenez conscience de ce qui vous enchaîne. La première étape vers la liberté est la lucidité.",
            "amour": "Passion intense mais possiblement toxique. Examinez vos attachements.",
            "travail": "Ambition dévorante ou environnement toxique. Évaluez le prix de votre succès.",
            "conseil": "Regardez vos ombres en face. La liberté commence par la conscience."
        },
        "renverse": {
            "general": "Libération d'une emprise ou d'une addiction. Rupture de chaînes.",
            "amour": "Sortie d'une relation toxique ou prise de conscience salutaire.",
            "travail": "Libération d'un environnement oppressant.",
            "conseil": "Vous avez le pouvoir de vous libérer. Utilisez-le."
        }
    },
    16: {
        "nom": "La Maison Dieu",
        "nom_en": "The Tower",
        "mots_cles": ["Révélation", "Destruction", "Libération", "Vérité"],
        "element": "Feu",
        "planete": "Mars",
        "description": "La Maison Dieu s'effondre sous la foudre. Elle représente la destruction soudaine des fausses structures, la révélation brutale et la libération par la vérité.",
        "droit": {
            "general": "Bouleversement nécessaire. Ce qui s'effondre devait tomber. La vérité éclate.",
            "amour": "Révélation ou crise qui peut purifier la relation. Vérité difficile à entendre.",
            "travail": "Changement soudain ou effondrement d'un projet. Reconstruction nécessaire.",
            "conseil": "Laissez tomber les fausses constructions. La foudre éclaire autant qu'elle détruit."
        },
        "renverse": {
            "general": "Résistance à un changement inévitable ou crise évitée de justesse.",
            "amour": "Crise relationnelle prolongée ou vérité difficile à accepter.",
            "travail": "Changement retardé mais inévitable.",
            "conseil": "Mieux vaut une destruction consciente qu'un effondrement subi."
        }
    },
    17: {
        "nom": "L'Étoile",
        "nom_en": "The Star",
        "mots_cles": ["Espoir", "Inspiration", "Sérénité", "Guidance"],
        "element": "Air",
        "planete": "Uranus",
        "description": "L'Étoile brille dans la nuit après la tempête. Elle représente l'espoir renouvelé, l'inspiration divine et la connexion avec le cosmos.",
        "droit": {
            "general": "Espoir et inspiration illuminent votre chemin. Période de grâce et de sérénité. Faites confiance.",
            "amour": "Amour authentique et inspirant. Connexion spirituelle avec votre partenaire.",
            "travail": "Période créative et inspirée. Vos projets sont bénis.",
            "conseil": "Suivez votre étoile. Elle vous guide vers votre vérité."
        },
        "renverse": {
            "general": "Perte d'espoir ou déconnexion spirituelle. Pessimisme passager.",
            "amour": "Désillusion amoureuse ou perte de foi dans l'amour.",
            "travail": "Manque d'inspiration ou découragement.",
            "conseil": "L'étoile brille toujours, même quand vous ne la voyez pas. Relevez la tête."
        }
    },
    18: {
        "nom": "La Lune",
        "nom_en": "The Moon",
        "mots_cles": ["Illusion", "Intuition", "Rêves", "Inconscient"],
        "element": "Eau",
        "planete": "Lune",
        "description": "La Lune éclaire le chemin entre les deux tours. Elle représente le monde des rêves, des illusions, des peurs et de l'inconscient.",
        "droit": {
            "general": "Faites confiance à votre intuition mais méfiez-vous des illusions. Les rêves portent des messages.",
            "amour": "Émotions profondes et parfois confuses. Écoutez votre intuition amoureuse.",
            "travail": "Créativité débordante mais attention aux projets flous.",
            "conseil": "Explorez votre inconscient. La vérité se cache derrière les apparences."
        },
        "renverse": {
            "general": "Confusion ou auto-illusion. Peurs irrationnelles qui vous paralysent.",
            "amour": "Malentendus ou secrets qui troublent la relation.",
            "travail": "Manque de clarté ou projet basé sur des illusions.",
            "conseil": "Dissipez le brouillard. La clarté viendra avec la patience."
        }
    },
    19: {
        "nom": "Le Soleil",
        "nom_en": "The Sun",
        "mots_cles": ["Joie", "Succès", "Vitalité", "Bonheur"],
        "element": "Feu",
        "planete": "Soleil",
        "description": "Le Soleil brille de tout son éclat. Il représente la joie pure, le succès éclatant, la vitalité et l'accomplissement lumineux.",
        "droit": {
            "general": "Succès et bonheur rayonnent sur vous. Période de joie et d'accomplissement. Célébrez !",
            "amour": "Amour joyeux et épanouissant. Bonheur partagé et projets lumineux.",
            "travail": "Réussite éclatante et reconnaissance. Vos talents brillent.",
            "conseil": "Rayonnez votre lumière. Le bonheur se partage."
        },
        "renverse": {
            "general": "Joie temporairement voilée ou optimisme excessif. Attention à l'orgueil.",
            "amour": "Bonheur superficiel ou attentes irréalistes.",
            "travail": "Succès qui tarde ou confiance excessive.",
            "conseil": "Le soleil reviendra. Gardez foi même dans les moments moins lumineux."
        }
    },
    20: {
        "nom": "Le Jugement",
        "nom_en": "Judgement",
        "mots_cles": ["Renaissance", "Appel", "Libération", "Réveil"],
        "element": "Feu",
        "planete": "Pluton",
        "description": "L'ange sonne la trompette et les âmes s'éveillent. Le Jugement représente la renaissance spirituelle, l'appel intérieur et la libération du passé.",
        "droit": {
            "general": "Éveil et renaissance. Un appel intérieur vous guide. Libérez-vous du passé.",
            "amour": "Renouveau dans la relation ou pardon libérateur. Nouveau départ à deux.",
            "travail": "Nouvelle vocation ou changement de direction inspiré.",
            "conseil": "Répondez à l'appel de votre âme. La renaissance est possible."
        },
        "renverse": {
            "general": "Refus d'évoluer ou de pardonner. Le passé vous retient.",
            "amour": "Incapacité à tourner la page ou culpabilité qui pèse.",
            "travail": "Appel ignoré ou peur du changement.",
            "conseil": "Le passé est passé. Répondez à l'appel du renouveau."
        }
    },
    21: {
        "nom": "Le Monde",
        "nom_en": "The World",
        "mots_cles": ["Accomplissement", "Plénitude", "Succès", "Harmonie"],
        "element": "Terre",
        "planete": "Saturne",
        "description": "Le Monde est la danse cosmique de l'accomplissement. Il représente la réalisation totale, l'harmonie universelle et la plénitude de l'être.",
        "droit": {
            "general": "Accomplissement et plénitude. Un cycle se complète avec succès. Célébrez cette victoire.",
            "amour": "Amour accompli et harmonieux. Union épanouie et équilibrée.",
            "travail": "Objectif atteint et reconnaissance méritée. Succès complet.",
            "conseil": "Savourez l'accomplissement. Vous avez mérité cette réussite."
        },
        "renverse": {
            "general": "Accomplissement incomplet ou sentiment de vide malgré le succès.",
            "amour": "Relation qui n'atteint pas son plein potentiel.",
            "travail": "Projet presque terminé ou insatisfaction malgré les résultats.",
            "conseil": "Qu'est-ce qui manque pour vous sentir complet ? Cherchez en vous."
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# POSITIONS DU TIRAGE CROIX CELTIQUE (10 cartes)
# ═══════════════════════════════════════════════════════════════════════════════

POSITIONS_CELTIQUE = {
    1: {
        "nom": "La Situation Présente",
        "description": "Le cœur de la question, ce qui vous préoccupe maintenant",
        "conseil": "Cette carte représente l'énergie centrale de votre question."
    },
    2: {
        "nom": "L'Obstacle ou le Défi",
        "description": "Ce qui croise votre chemin, pour le meilleur ou le pire",
        "conseil": "Ceci peut être un obstacle à surmonter ou une force qui vous aide."
    },
    3: {
        "nom": "Le Fondement",
        "description": "Les racines de la situation, ce qui a mené à ce point",
        "conseil": "Le passé récent ou les fondations de la question."
    },
    4: {
        "nom": "Le Passé Récent",
        "description": "Les influences qui s'éloignent de vous",
        "conseil": "Ce qui est en train de passer ou qui a récemment eu un impact."
    },
    5: {
        "nom": "La Couronne - Le Meilleur Possible",
        "description": "Le meilleur résultat possible ou votre objectif",
        "conseil": "Ce vers quoi vous tendez consciemment."
    },
    6: {
        "nom": "Le Futur Proche",
        "description": "Les influences qui arrivent vers vous",
        "conseil": "Ce qui va se manifester prochainement."
    },
    7: {
        "nom": "Votre Attitude",
        "description": "Comment vous vous percevez dans cette situation",
        "conseil": "Votre position, vos peurs et vos espoirs."
    },
    8: {
        "nom": "L'Environnement",
        "description": "Les influences extérieures et les autres personnes",
        "conseil": "Comment les autres vous perçoivent et influencent la situation."
    },
    9: {
        "nom": "Espoirs et Craintes",
        "description": "Ce que vous espérez ou redoutez secrètement",
        "conseil": "Vos peurs et vos espoirs les plus profonds concernant cette question."
    },
    10: {
        "nom": "Le Résultat Final",
        "description": "L'aboutissement probable si les choses continuent ainsi",
        "conseil": "La synthèse de toutes les énergies en jeu."
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# DOMAINES DE QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════

DOMAINES_QUESTIONS = {
    "amour": {
        "nom": "Amour & Relations",
        "icone": "❤️",
        "description": "Questions sur la vie amoureuse, les relations, la famille",
        "exemples": [
            "Cette relation est-elle faite pour durer ?",
            "Vais-je rencontrer l'amour bientôt ?",
            "Comment améliorer ma relation actuelle ?"
        ]
    },
    "travail": {
        "nom": "Carrière & Travail",
        "icone": "💼",
        "description": "Questions sur le travail, la carrière, les projets professionnels",
        "exemples": [
            "Dois-je accepter cette offre d'emploi ?",
            "Mon projet va-t-il réussir ?",
            "Est-ce le bon moment pour changer de carrière ?"
        ]
    },
    "argent": {
        "nom": "Finances & Abondance",
        "icone": "💰",
        "description": "Questions sur l'argent, les investissements, l'abondance",
        "exemples": [
            "Cet investissement est-il judicieux ?",
            "Ma situation financière va-t-elle s'améliorer ?",
            "Dois-je faire cet achat important ?"
        ]
    },
    "sante": {
        "nom": "Santé & Bien-être",
        "icone": "🌿",
        "description": "Questions sur la santé physique, mentale et spirituelle",
        "exemples": [
            "Que dois-je faire pour améliorer ma santé ?",
            "Cette période de stress va-t-elle passer ?",
            "Comment retrouver mon équilibre ?"
        ]
    },
    "spirituel": {
        "nom": "Spiritualité & Développement",
        "icone": "✨",
        "description": "Questions sur le chemin de vie, la spiritualité, la croissance personnelle",
        "exemples": [
            "Quelle est ma mission de vie ?",
            "Comment évoluer spirituellement ?",
            "Quel message l'univers a-t-il pour moi ?"
        ]
    },
    "general": {
        "nom": "Question Générale",
        "icone": "🔮",
        "description": "Toute autre question ou guidance générale",
        "exemples": [
            "Que dois-je savoir en ce moment ?",
            "Quelle direction prendre ?",
            "Quel conseil pour cette période de ma vie ?"
        ]
    }
}


def tirage_marseille_question(question: str, domaine: str = "general", seed: Optional[str] = None) -> Dict:
    """
    Tirage du Tarot de Marseille avec question personnalisée
    3 cartes: Passé - Présent - Futur
    """
    if seed:
        random.seed(int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32))
    else:
        random.seed()
    
    # Tirer 3 cartes uniques
    numeros = random.sample(list(ARCANES_MAJEURS.keys()), 3)
    orientations = [random.choice(["droit", "renverse"]) for _ in range(3)]
    
    positions = ["Passé", "Présent", "Futur"]
    descriptions_positions = [
        "Ce qui a influencé la situation",
        "L'énergie actuelle de la question",
        "L'évolution probable"
    ]
    
    cartes = []
    for i, (num, orient) in enumerate(zip(numeros, orientations)):
        arcane = ARCANES_MAJEURS[num]
        interpretation = arcane["droit"] if orient == "droit" else arcane["renverse"]
        
        # Adapter l'interprétation au domaine si possible
        domaine_key = domaine if domaine in ["amour", "travail"] else "general"
        
        cartes.append({
            "position": positions[i],
            "position_description": descriptions_positions[i],
            "numero": num,
            "nom": arcane["nom"],
            "orientation": orient,
            "orientation_fr": "Droit" if orient == "droit" else "Renversé",
            "mots_cles": arcane["mots_cles"],
            "element": arcane["element"],
            "interpretation": interpretation.get(domaine_key, interpretation.get("general", "")),
            "conseil": interpretation.get("conseil", ""),
            "description_arcane": arcane["description"]
        })
    
    # Générer la synthèse
    synthese = _generer_synthese_marseille(cartes, question, domaine)
    
    return {
        "type": "tirage_marseille",
        "question": question,
        "domaine": DOMAINES_QUESTIONS.get(domaine, DOMAINES_QUESTIONS["general"]),
        "cartes": cartes,
        "synthese": synthese,
        "date": datetime.now().isoformat(),
        "conseil_final": _generer_conseil_final(cartes, domaine)
    }


def tirage_croix_celtique(question: str, domaine: str = "general", seed: Optional[str] = None) -> Dict:
    """
    Tirage Croix Celtique complet - 10 cartes
    Le tirage le plus complet du tarot
    """
    if seed:
        random.seed(int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32))
    else:
        random.seed()
    
    # Tirer 10 cartes uniques
    numeros = random.sample(list(ARCANES_MAJEURS.keys()), 10)
    orientations = [random.choice(["droit", "renverse"]) for _ in range(10)]
    
    cartes = []
    for i, (num, orient) in enumerate(zip(numeros, orientations)):
        position_num = i + 1
        position_info = POSITIONS_CELTIQUE[position_num]
        arcane = ARCANES_MAJEURS[num]
        interpretation = arcane["droit"] if orient == "droit" else arcane["renverse"]
        
        # Domaine pour l'interprétation
        domaine_key = domaine if domaine in ["amour", "travail"] else "general"
        
        cartes.append({
            "position_numero": position_num,
            "position_nom": position_info["nom"],
            "position_description": position_info["description"],
            "position_conseil": position_info["conseil"],
            "numero": num,
            "nom": arcane["nom"],
            "orientation": orient,
            "orientation_fr": "Droit" if orient == "droit" else "Renversé",
            "mots_cles": arcane["mots_cles"],
            "element": arcane["element"],
            "planete": arcane["planete"],
            "interpretation": interpretation.get(domaine_key, interpretation.get("general", "")),
            "conseil": interpretation.get("conseil", ""),
            "description_arcane": arcane["description"]
        })
    
    # Analyse complète
    analyse = _analyser_croix_celtique(cartes, question, domaine)
    
    return {
        "type": "tirage_croix_celtique",
        "question": question,
        "domaine": DOMAINES_QUESTIONS.get(domaine, DOMAINES_QUESTIONS["general"]),
        "cartes": cartes,
        "analyse": analyse,
        "date": datetime.now().isoformat()
    }


def _generer_synthese_marseille(cartes: List[Dict], question: str, domaine: str) -> Dict:
    """Génère une synthèse du tirage Marseille"""
    passe = cartes[0]
    present = cartes[1]
    futur = cartes[2]
    
    # Analyser les éléments dominants
    elements = [c["element"] for c in cartes]
    element_dominant = max(set(elements), key=elements.count) if len(set(elements)) < 3 else "Mixte"
    
    # Orientation générale
    droits = sum(1 for c in cartes if c["orientation"] == "droit")
    tendance = "favorable" if droits >= 2 else "nuancée" if droits == 1 else "à travailler"
    
    return {
        "element_dominant": element_dominant,
        "tendance_generale": tendance,
        "message_passe": f"Le {passe['nom']} ({passe['orientation_fr']}) indique que {passe['interpretation'][:100]}...",
        "message_present": f"Le {present['nom']} ({present['orientation_fr']}) montre l'énergie actuelle : {present['interpretation'][:100]}...",
        "message_futur": f"Le {futur['nom']} ({futur['orientation_fr']}) suggère comme évolution : {futur['interpretation'][:100]}...",
        "fil_conducteur": f"De {passe['nom']} à {futur['nom']}, votre chemin passe par {present['nom']}. Les cartes indiquent une tendance {tendance}."
    }


def _generer_conseil_final(cartes: List[Dict], domaine: str) -> str:
    """Génère un conseil final basé sur le tirage"""
    futur = cartes[2]
    
    conseils_elements = {
        "Feu": "Agissez avec passion et détermination. Le moment est à l'action.",
        "Eau": "Faites confiance à vos émotions et votre intuition pour naviguer cette période.",
        "Air": "La communication et la réflexion seront vos meilleures alliées.",
        "Terre": "Restez ancré(e) et construisez pas à pas. La patience porte ses fruits."
    }
    
    conseil_element = conseils_elements.get(futur["element"], "Restez ouvert(e) aux signes de l'univers.")
    
    return f"{futur['conseil']} {conseil_element}"


def _analyser_croix_celtique(cartes: List[Dict], question: str, domaine: str) -> Dict:
    """Analyse complète du tirage Croix Celtique"""
    # Cartes clés
    situation = cartes[0]  # Position 1
    obstacle = cartes[1]   # Position 2
    fondement = cartes[2]  # Position 3
    resultat = cartes[9]   # Position 10
    
    # Analyser les éléments
    elements = [c["element"] for c in cartes]
    element_counts = {e: elements.count(e) for e in set(elements)}
    element_dominant = max(element_counts, key=element_counts.get)
    
    # Analyser les orientations
    droits = sum(1 for c in cartes if c["orientation"] == "droit")
    renverses = 10 - droits
    
    if droits >= 7:
        energie_globale = "Très favorable - Les énergies sont alignées en votre faveur"
    elif droits >= 5:
        energie_globale = "Favorable - Des défis existent mais peuvent être surmontés"
    elif droits >= 3:
        energie_globale = "Nuancée - Un travail intérieur est nécessaire"
    else:
        energie_globale = "Challengeante - Période de transformation profonde"
    
    # Analyser les planètes
    planetes = [c["planete"] for c in cartes]
    
    return {
        "energie_globale": energie_globale,
        "cartes_droites": droits,
        "cartes_renversees": renverses,
        "element_dominant": element_dominant,
        "elements_detail": element_counts,
        "situation_actuelle": {
            "carte": situation["nom"],
            "message": f"Au cœur de votre question se trouve {situation['nom']} ({situation['orientation_fr']}). {situation['interpretation']}"
        },
        "obstacle_principal": {
            "carte": obstacle["nom"],
            "message": f"Ce qui croise votre chemin : {obstacle['nom']} ({obstacle['orientation_fr']}). {obstacle['interpretation']}"
        },
        "fondement": {
            "carte": fondement["nom"],
            "message": f"Les racines de la situation : {fondement['nom']} ({fondement['orientation_fr']}). {fondement['interpretation']}"
        },
        "resultat_probable": {
            "carte": resultat["nom"],
            "message": f"L'aboutissement probable : {resultat['nom']} ({resultat['orientation_fr']}). {resultat['interpretation']}"
        },
        "synthese_finale": _generer_synthese_celtique(cartes, question, domaine),
        "conseil_action": _generer_conseil_action(cartes, domaine)
    }


def _generer_synthese_celtique(cartes: List[Dict], question: str, domaine: str) -> str:
    """Génère la synthèse finale du tirage Celtique"""
    situation = cartes[0]
    resultat = cartes[9]
    
    return f"""Concernant votre question, les cartes révèlent un voyage de {situation['nom']} vers {resultat['nom']}.

L'énergie actuelle ({situation['nom']} - {situation['orientation_fr']}) indique {situation['interpretation'][:150]}...

Le résultat probable ({resultat['nom']} - {resultat['orientation_fr']}) suggère {resultat['interpretation'][:150]}...

Ce tirage complet montre que votre chemin est pavé de défis et d'opportunités. Chaque carte a un message spécifique pour vous guider."""


def _generer_conseil_action(cartes: List[Dict], domaine: str) -> str:
    """Génère un conseil d'action basé sur l'ensemble du tirage"""
    attitude = cartes[6]  # Position 7 - Votre attitude
    environnement = cartes[7]  # Position 8 - L'environnement
    
    return f"""Pour naviguer cette période avec succès :

1. **Travaillez votre attitude** : {attitude['nom']} ({attitude['orientation_fr']}) dans cette position suggère {attitude['conseil']}

2. **Gérez votre environnement** : {environnement['nom']} ({environnement['orientation_fr']}) indique que votre entourage {environnement['interpretation'][:100]}...

3. **Action recommandée** : Intégrez la sagesse des cartes dans vos décisions quotidiennes. Les arcanes vous guident, mais c'est vous qui tracez le chemin."""



def _format_date_fr(dt: datetime) -> str:
    """Formatte une date en français (ex: 04 mars 2026)"""
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    return f"{dt.day:02d} {mois_fr[dt.month]} {dt.year}"


def tirage_du_jour() -> Dict:
    """
    Tirage du Jour - Une carte gratuite par jour
    La même carte pour tous les utilisateurs ce jour-là
    Basé sur la date pour garantir la cohérence
    """
    # Utiliser la date du jour comme seed pour avoir la même carte pour tous
    today = datetime.now().strftime("%Y-%m-%d")
    seed_value = int(hashlib.md5(today.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed_value)
    
    # Tirer une carte
    numero = random.randint(0, 21)
    orientation = random.choice(["droit", "renverse"])
    
    arcane = ARCANES_MAJEURS[numero]
    interpretation = arcane["droit"] if orientation == "droit" else arcane["renverse"]
    
    # Message du jour personnalisé selon l'orientation
    if orientation == "droit":
        message_energie = "Les énergies sont favorables aujourd'hui. Cette carte vous encourage à avancer avec confiance."
    else:
        message_energie = "Une journée d'introspection s'annonce. Cette carte vous invite à la réflexion et à l'ajustement."
    
    # Conseil du jour basé sur l'élément
    conseils_elements = {
        "Feu": "Laissez votre passion vous guider. L'action et l'enthousiasme sont vos alliés aujourd'hui.",
        "Eau": "Écoutez vos émotions et votre intuition. Elles ont des messages importants pour vous.",
        "Air": "La communication et la réflexion seront clés. Exprimez vos idées avec clarté.",
        "Terre": "Restez ancré(e) et pragmatique. Construisez pas à pas vers vos objectifs."
    }
    
    return {
        "type": "tirage_du_jour",
        "date": today,
        "date_fr": _format_date_fr(datetime.now()),
        "carte": {
            "numero": numero,
            "nom": arcane["nom"],
            "nom_en": arcane["nom_en"],
            "orientation": orientation,
            "orientation_fr": "Droit" if orientation == "droit" else "Renversé",
            "mots_cles": arcane["mots_cles"],
            "element": arcane["element"],
            "planete": arcane["planete"],
            "description": arcane["description"],
            "interpretation_generale": interpretation["general"],
            "interpretation_amour": interpretation["amour"],
            "interpretation_travail": interpretation["travail"],
            "conseil": interpretation["conseil"]
        },
        "message_energie": message_energie,
        "conseil_element": conseils_elements.get(arcane["element"], "Suivez votre intuition."),
        "affirmation_du_jour": _generer_affirmation(arcane, orientation),
        "rituel_suggere": _generer_rituel(arcane["element"])
    }


def _generer_affirmation(arcane: Dict, orientation: str) -> str:
    """Génère une affirmation positive basée sur la carte"""
    affirmations = {
        "Le Mat": "Je fais confiance au voyage de la vie et j'accueille l'inconnu avec joie.",
        "Le Bateleur": "J'ai tous les outils en moi pour créer la vie que je désire.",
        "La Papesse": "J'écoute ma sagesse intérieure et je fais confiance à mon intuition.",
        "L'Impératrice": "L'abondance coule vers moi naturellement. Je suis créateur/créatrice de beauté.",
        "L'Empereur": "Je suis maître/maîtresse de ma vie. Je construis avec force et sagesse.",
        "Le Pape": "Je suis guidé(e) par une sagesse supérieure. J'apprends et je transmets.",
        "L'Amoureux": "Mon cœur connaît le chemin. Je choisis avec amour.",
        "Le Chariot": "Je suis déterminé(e) et victorieux/victorieuse. Rien ne peut m'arrêter.",
        "La Justice": "L'équilibre revient dans ma vie. La vérité me libère.",
        "L'Hermite": "Dans le silence, je trouve la lumière. Ma sagesse intérieure me guide.",
        "La Roue de Fortune": "Je danse avec les cycles de la vie. La chance est de mon côté.",
        "La Force": "Je dompte mes peurs avec douceur. Ma force intérieure est infinie.",
        "Le Pendu": "Je lâche prise et je m'ouvre à une nouvelle perspective.",
        "L'Arcane sans Nom": "Je me transforme et je renaîs plus fort(e) que jamais.",
        "Tempérance": "L'harmonie habite mon cœur. Je trouve l'équilibre en tout.",
        "Le Diable": "Je me libère de mes chaînes. Ma lumière dissipe les ombres.",
        "La Maison Dieu": "De chaque destruction naît une renaissance. Je suis résilient(e).",
        "L'Étoile": "L'espoir illumine mon chemin. Je suis guidé(e) par les étoiles.",
        "La Lune": "J'explore mes profondeurs avec courage. Mes rêves me parlent.",
        "Le Soleil": "La joie rayonne en moi et autour de moi. Je célèbre la vie.",
        "Le Jugement": "Je réponds à l'appel de mon âme. Une nouvelle vie commence.",
        "Le Monde": "Je suis complet(e) et accompli(e). Le monde m'appartient."
    }
    
    return affirmations.get(arcane["nom"], "Je suis aligné(e) avec mon chemin de vie.")


def _generer_rituel(element: str) -> str:
    """Génère un rituel suggéré basé sur l'élément de la carte"""
    rituels = {
        "Feu": "Allumez une bougie et visualisez vos objectifs se réalisant. Laissez la flamme représenter votre passion intérieure.",
        "Eau": "Prenez un bain relaxant ou buvez une tisane en méditant sur vos émotions. Laissez l'eau purifier votre énergie.",
        "Air": "Faites quelques respirations profondes près d'une fenêtre ouverte. Laissez l'air frais clarifier vos pensées.",
        "Terre": "Marchez pieds nus sur l'herbe ou tenez une pierre dans vos mains. Connectez-vous à l'énergie stable de la terre."
    }
    
    return rituels.get(element, "Prenez 5 minutes pour méditer et vous connecter à votre guidance intérieure.")
