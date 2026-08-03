"""
Fallback statique riche pour l'enrichissement des rapports.

Utilisé quand l'admin désactive l'enrichissement IA (toggle OFF) OU quand
l'appel LLM échoue (timeout, budget, quota).

Contrairement à un fallback minimal (texte vide → pages courtes), ce module
retourne des sections narratives complètes (2-4 paragraphes chacune) déjà
rédigées à la voix de Soléna. Le PDF reste donc « étoffé » même sans IA.

Le prénom est interpolé dans les textes via `{prenom}`.
"""
from __future__ import annotations
from typing import Dict


_FALLBACKS: Dict[str, Dict[str, str]] = {
    # ═══════════════════════════════════════════════════════════════
    'karma_destin': {
        'introduction': (
            "{prenom}, ton karma n'est pas une punition. C'est une mémoire — celle des "
            "vies antérieures, des serments prononcés, des blessures inachevées que ton "
            "âme a choisi de reprendre. Ce document ne dresse pas la liste de tes dettes, "
            "il dessine la carte de ton pardon."
            "<br/><br/>"
            "Trois axes vont structurer cette lecture : ce que tu as déjà maîtrisé et que "
            "tu dois lâcher (le Nœud Sud), ce que ton âme vient apprendre dans cette vie "
            "(le Nœud Nord), et les archétypes qui viennent tester ta lumière (Saturne, "
            "Chiron, Pluton)."
            "<br/><br/>"
            "Prends ce texte comme une main tendue. Il ne te dit pas qui tu <i>dois</i> "
            "devenir. Il te rappelle ce que tu es déjà en train de devenir, parfois "
            "sans le savoir."
        ),
        'noeud_nord': (
            "Ton Nœud Nord est la boussole silencieuse de ta destinée. C'est la direction "
            "que ton âme a choisie avant de venir, celle qui te fera grandir même quand "
            "elle te fera peur. Les premières fois où tu iras dans son sens, tu auras "
            "l'impression de mal parler la langue — c'est normal, c'est une langue neuve."
            "<br/><br/>"
            "Cette destinée ne se conquiert pas par la performance. Elle s'apprivoise par "
            "des gestes concrets et minuscules, répétés jusqu'à ce qu'ils cessent d'être "
            "inconfortables. Tu vas devoir désapprendre ce qui t'a rendu(e) forte pour "
            "apprendre ce qui va te rendre libre."
            "<br/><br/>"
            "Attends-toi à un signe : chaque fois qu'une opportunité te terrifie <i>et</i> "
            "t'attire, c'est probablement ton Nœud Nord qui frappe à la porte."
        ),
        'noeud_sud': (
            "Ton Nœud Sud raconte ce que ton âme sait déjà faire les yeux fermés — parfois "
            "trop bien. Ce sont les talents automatiques, les rôles rassurants, les "
            "réflexes qui te sauvent depuis des vies. Le problème, c'est qu'ils ne te font "
            "plus grandir."
            "<br/><br/>"
            "Le paradoxe karmique : cette zone où tu excelles est aussi celle qui te "
            "retient. Chaque fois que tu retombes dans ce vieux réflexe, tu retardes le "
            "chemin promis à ton Nœud Nord. La sagesse consiste non pas à renier ces dons, "
            "mais à les utiliser au service de ta nouvelle direction."
        ),
        'saturne': (
            "Saturne est le maître d'école bienveillant que tu croies parfois cruel. Il "
            "n'ajoute rien à ton chemin qui ne serve à te structurer. Il enlève, il "
            "dépouille, il retarde — jusqu'à ce que tu comprennes ce qui tient vraiment."
            "<br/><br/>"
            "Son grand rendez-vous, tu l'as autour de 29-30 ans (retour de Saturne), puis "
            "vers 58-60 ans. Chacun de ces passages te demande de choisir entre la "
            "sécurité qui étouffe et la vérité qui grandit. Beaucoup de femmes vivent ces "
            "âges comme des naissances secondes."
            "<br/><br/>"
            "Saturne ne récompense pas la vitesse. Il récompense la constance. Tout ce "
            "que tu construis lentement avec lui devient inaltérable."
        ),
        'chiron': (
            "Chiron est ta blessure sacrée — celle qui ne guérira jamais complètement, et "
            "qui pourtant t'apprend à guérir les autres. Chaque fois que quelqu'un te "
            "confie précisément la douleur qui t'a construite, ce n'est pas un hasard : "
            "c'est Chiron qui envoie ses élèves."
            "<br/><br/>"
            "La faille et le don logent à la même adresse. Ce que tu crois être ton point "
            "faible est en fait ton plus grand outil de service. Ta guérison n'est pas "
            "l'absence de cicatrice ; c'est l'usage juste que tu en fais."
            "<br/><br/>"
            "Aujourd'hui, Chiron te demande d'oser en parler. Pas de tout raconter — mais "
            "de reconnaître ta faille avec dignité. Ce que tu tairas, tu le porteras. Ce "
            "que tu partageras, tu le transformeras."
        ),
        'pluton': (
            "Pluton est le sorcier discret de ton thème. Il ne parle pas fort — il "
            "transforme en profondeur. Là où il se pose, quelque chose meurt régulièrement "
            "pour renaître autrement. C'est ta zone de mues successives."
            "<br/><br/>"
            "Ces morts symboliques ne sont pas des drames : ce sont les conditions de tes "
            "renaissances. Chaque fois que tu perds une identité, un rôle, un objet "
            "d'attachement, Pluton te rappelle que tu es plus vaste que ce que tu croyais "
            "être. Le prix de cette leçon est réel. La récompense l'est aussi."
        ),
        'karma_generationnel': (
            "Tu ne portes pas seulement ton karma. Tu portes celui de ta lignée — les "
            "silences féminins, les colères non dites, les rêves interrompus de tes "
            "grands-mères. Ta place dans l'arbre familial n'est pas neutre. Ton âme a "
            "choisi cette porte pour transmuter quelque chose."
            "<br/><br/>"
            "Guérir un karma générationnel ne demande pas de comprendre toute l'histoire. "
            "Il suffit d'oser un geste que personne, dans ta lignée, n'a osé avant toi. "
            "Une phrase dite, une limite posée, une joie assumée : tout cela devient un "
            "cadeau rétroactif à tes ancêtres."
            "<br/><br/>"
            "Rappelle-toi que le karma familial n'est pas une faute à expier — c'est un "
            "héritage à transformer. Tu es la première génération qui a le droit de dire "
            "certaines choses tout haut."
        ),
        'dates_cles': (
            "Voici les fenêtres karmiques majeures de ta vie :"
            "<br/><br/>"
            "<b>29-30 ans</b> — Premier retour de Saturne : la vérité de ta vocation se "
            "dévoile souvent brutalement. On garde ce qui tient, on lâche ce qui pesait."
            "<br/><br/>"
            "<b>42-44 ans</b> — Milieu de vie : Uranus s'oppose à sa position natale. C'est "
            "l'âge des vrais choix, souvent des refontes de couple, de métier, de sens."
            "<br/><br/>"
            "<b>50-52 ans</b> — Retour de Chiron : la blessure originelle se transforme "
            "en médecine. Beaucoup entrent ici dans leur vocation d'accompagnement."
            "<br/><br/>"
            "<b>58-60 ans</b> — Second retour de Saturne : la sagesse s'ancre. Ce qui a "
            "été construit avec constance devient inaltérable."
        ),
        'invitation_finale': (
            "{prenom}, tu n'es pas venue sur cette terre pour réparer tout ce qui est "
            "cassé. Tu es venue apprendre à aimer ce qui est déjà entier, y compris tes "
            "propres fissures. Ton karma n'est pas ta prison — c'est ton texte de "
            "naissance, et tu écris déjà la suite chaque fois que tu choisis la vérité "
            "sur la peur."
            "<br/><br/>"
            "Reviens à ce document dans six mois. Certaines pages te sembleront évidentes, "
            "d'autres se seront réveillées. C'est le signe que ton âme travaille — même "
            "quand ta tête doute."
        ),
    },

    # ═══════════════════════════════════════════════════════════════
    'numerology': {
        'introduction': (
            "{prenom}, la numérologie n'est pas une superstition — c'est la plus vieille "
            "langue humaine avant l'écriture. Chaque nombre porte une vibration, chaque "
            "date de naissance dessine une signature vibratoire. La tienne va se révéler "
            "au fil de ces pages."
            "<br/><br/>"
            "Nous allons descendre du général au précis : ton chemin de vie (la trajectoire "
            "globale), ta destinée (ce que tu es venue exprimer), ton nombre d'âme (ce "
            "que tu désires en secret), et l'année personnelle qui structure les 12 mois "
            "qui viennent."
        ),
        'chemin_de_vie': (
            "Ton chemin de vie est l'axe principal de ton incarnation — la direction "
            "d'ensemble que ton âme a choisie. Il ne dicte pas ce qui va t'arriver ; il "
            "décrit ce que tu vas apprendre à travers ce qui t'arrive."
            "<br/><br/>"
            "Cette trajectoire n'est jamais linéaire. Les nombres sont des cycles qui "
            "reviennent, chaque fois à un niveau plus subtil. Si tu as l'impression de "
            "traverser la même leçon plusieurs fois, c'est probablement parce que ton "
            "chemin de vie te la propose à des altitudes différentes."
            "<br/><br/>"
            "L'invitation ici est d'accueillir cette trajectoire comme une école plutôt "
            "qu'un tribunal. Tu n'es pas jugée sur la vitesse — tu es accompagnée sur la "
            "profondeur."
        ),
        'destinee': (
            "Ta destinée numérique — calculée à partir des lettres de ton nom complet — "
            "révèle ce que tu es venue exprimer publiquement dans cette vie. Ce n'est pas "
            "forcément un métier ; c'est plutôt une <i>manière</i> d'être présente au monde."
            "<br/><br/>"
            "Cette destinée peut mettre du temps à se déployer. Certaines femmes la "
            "reconnaissent à 20 ans, d'autres la découvrent à 55. Ce qui compte n'est pas "
            "le moment — c'est de sentir <i>quand</i> quelque chose sonne juste."
        ),
        'ame': (
            "Ton nombre d'âme (calculé à partir des voyelles de ton nom) est ce que tu "
            "désires vraiment, au-delà des attentes des autres. C'est souvent le désir le "
            "moins avouable, celui qui semble « trop » ou « pas assez »."
            "<br/><br/>"
            "Honorer ce nombre ne veut pas dire tout casser pour le suivre. Ça veut dire "
            "faire, chaque jour, une chose (une petite) qui va dans son sens. Les âmes "
            "s'apaisent quand elles se sentent enfin écoutées."
        ),
        'personnalite': (
            "Ton nombre de personnalité (les consonnes de ton nom) décrit l'image que "
            "tu projettes quand quelqu'un te rencontre pour la première fois. C'est ta "
            "vitrine, souvent différente de ce que tu es en profondeur."
            "<br/><br/>"
            "Ce nombre n'est pas un masque. C'est ton emballage — utile, protecteur, "
            "parfois trompeur pour toi-même. La sagesse consiste à savoir quand t'appuyer "
            "sur lui et quand oser le poser."
        ),
        'jour_naissance': (
            "Le nombre du jour où tu es née est ton talent inné — celui que tu maîtrises "
            "sans avoir jamais eu à l'apprendre. C'est ta signature spontanée, ce qui te "
            "rend reconnaissable même dans le silence."
            "<br/><br/>"
            "Attention à ne pas le sous-estimer parce qu'il est facile pour toi. Ce qui "
            "te paraît évident est souvent précieux pour d'autres. Ton talent inné est un "
            "cadeau à faire circuler."
        ),
        'annee_personnelle': (
            "Chaque année, tu traverses un cycle numérique de 1 à 9. Ton année personnelle "
            "en cours colore les 12 prochains mois : elle ouvre certaines portes et en "
            "ferme d'autres, elle appelle certaines actions et en décourage d'autres."
            "<br/><br/>"
            "Les années impaires sont plus actives, tournées vers le mouvement ; les "
            "années paires sont plus intérieures, tournées vers la consolidation. Aligne "
            "tes projets sur ce rythme et tu constateras que les efforts deviennent "
            "étrangement moins lourds."
            "<br/><br/>"
            "L'invitation concrète : identifie une action qui correspond à l'énergie de "
            "l'année en cours et engage-toi dessus 90 jours. Les cycles récompensent ceux "
            "qui les respectent."
        ),
        'lo_shu': (
            "La numérologie chinoise complète l'occidentale par une grille — le carré "
            "Lo-Shu — qui révèle tes forces et tes zones d'apprentissage à travers la "
            "présence ou l'absence de chaque nombre dans ta date de naissance."
            "<br/><br/>"
            "Les nombres présents sont tes appuis naturels. Les nombres absents ne sont "
            "pas des failles — ce sont des rendez-vous d'apprentissage. Toute une vie "
            "peut se dérouler autour de la maîtrise d'un ou deux nombres manquants."
        ),
        'biorythmes': (
            "Les biorythmes découpent ta vitalité en trois cycles : physique (23 jours), "
            "émotionnel (28 jours) et intellectuel (33 jours). Les jours où deux cycles "
            "sont hauts sont tes fenêtres d'excellence ; les jours où deux sont bas "
            "invitent à ralentir."
            "<br/><br/>"
            "Utilise cette information pour placer intelligemment tes défis importants. "
            "Ce n'est pas de la magie — c'est de la stratégie corporelle."
        ),
        'invitation_finale': (
            "{prenom}, les nombres ne te disent pas <i>ce</i> que tu es. Ils te disent "
            "<i>comment</i> tu es faite pour aimer, créer, décider, aimer encore. Reviens "
            "à ce document au moment où tu doutes de ton propre rythme — il te rappellera "
            "que tu es parfaitement à l'heure sur ton propre calendrier."
        ),
    },

    # ═══════════════════════════════════════════════════════════════
    'mediumnite': {
        'introduction': (
            "{prenom}, ta sensibilité vibratoire n'est pas une fragilité — c'est un "
            "instrument. Beaucoup de femmes traversent leur vie sans reconnaître ce "
            "qu'elles perçoivent : les intuitions justes, les rêves qui préviennent, les "
            "présences ressenties dans les pièces vides. Ce document te propose de "
            "nommer ces capacités."
            "<br/><br/>"
            "La médiumnité n'est pas un don réservé à quelques élues. C'est une "
            "compétence humaine, en sommeil chez la plupart, mais éveillable par tout le "
            "monde. La tienne s'est probablement déjà manifestée — sans que tu oses la "
            "prendre au sérieux."
            "<br/><br/>"
            "Prends ce que tu vas lire comme une carte, pas comme un verdict. Tu es la "
            "seule à décider ce que tu en fais."
        ),
        'clairs': (
            "<b>Clairvoyance</b> : tu vois — parfois en rêve, parfois en flash éveillé — "
            "des scènes que tu n'as pas vécues mais qui sont vraies. Ce sens s'affine "
            "avec le sommeil régulier et l'écriture matinale."
            "<br/><br/>"
            "<b>Clairaudience</b> : tu entends — dans le silence, souvent le matin — des "
            "phrases courtes, presque murmurées. Ce ne sont pas des voix intrusives ; ce "
            "sont des rappels justes. Note-les avant qu'elles s'effacent."
            "<br/><br/>"
            "<b>Clairsentience</b> : tu ressens dans ton corps l'état émotionnel des "
            "personnes que tu croises. Ce n'est pas de l'imagination : c'est ton système "
            "nerveux qui capte des informations subtiles. Apprends à distinguer ce qui "
            "est toi de ce qui est l'autre."
            "<br/><br/>"
            "<b>Claircognisance</b> : tu <i>sais</i>, sans pouvoir expliquer comment. Ce "
            "savoir arrive d'un bloc, souvent hors de propos. Fais-lui confiance quand "
            "il est doux ; interroge-le quand il vient teinté de peur."
        ),
        'guides': (
            "Tu n'es pas seule. Autour de toi circulent — que tu y crois ou non — des "
            "présences bienveillantes : des ancêtres féminines de ta lignée, un ou "
            "plusieurs guides d'âme, parfois un être plus vaste qui veille depuis "
            "toujours. Ces présences ne <i>font</i> pas les choses à ta place ; elles "
            "orientent, elles rappellent, elles réconfortent."
            "<br/><br/>"
            "Reconnaître leur travail commence par de petits signes : plumes, papillons "
            "blancs, séries de chiffres qui reviennent, chansons qui surgissent au bon "
            "moment. Le monde parle constamment — il attend que tu écoutes."
            "<br/><br/>"
            "Une pratique douce : chaque soir, remercie mentalement les présences qui "
            "t'ont accompagnée dans la journée. Ce simple geste installe un dialogue."
        ),
        'blocages': (
            "Ce qui bouche ta médiumnité n'est pas ton âme — c'est ton mental fatigué. "
            "Trois blocages classiques : le doute permanent (« je vais inventer »), la "
            "peur de ce qui pourrait être vu, et la surcharge sensorielle (écrans, "
            "bruits, agenda saturé)."
            "<br/><br/>"
            "L'ouverture médiumnique ne se force pas. Elle se libère par soustraction : "
            "moins d'informations parasites, plus de silence, un corps posé. Ta clarté "
            "revient à la vitesse de ton apaisement."
        ),
        'pratiques': (
            "<b>1. La marche silencieuse quotidienne (15 min)</b> — Marche seule, sans "
            "téléphone, sans musique. Observe ce que ton attention accroche naturellement. "
            "Après trois semaines, ton canal médiumnique commence à circuler."
            "<br/><br/>"
            "<b>2. Le journal des présences</b> — Chaque soir, note trois choses : une "
            "intuition que tu as eue, un signe que tu as vu, une émotion qui t'a semblé "
            "venir d'ailleurs. La médiumnité n'apparaît pas — elle se remarque."
            "<br/><br/>"
            "<b>3. Le silence hebdomadaire (2h)</b> — Une fois par semaine, offre-toi "
            "deux heures sans stimulation extérieure. C'est dans cet espace que tes "
            "guides trouvent la place de te parler."
        ),
        'invitation_finale': (
            "{prenom}, tu n'as pas besoin de <i>devenir</i> médium — tu l'es déjà. Ce "
            "document t'invite juste à cesser de nier ce que tu perçois. Le monde a besoin "
            "de femmes qui écoutent l'invisible sans en faire un spectacle."
        ),
    },

    # ═══════════════════════════════════════════════════════════════
    'kabbale': {
        'introduction': (
            "{prenom}, la Kabbale n'est pas une religion — c'est une carte de l'âme "
            "vieille de deux mille ans. Elle décrit dix sphères de conscience (les "
            "Séphiroth) reliées par vingt-deux chemins, et te montre où ta lumière "
            "circule le plus fort dans cette incarnation."
            "<br/><br/>"
            "Ton thème natal, cartographié sur cet Arbre de Vie, révèle un portrait "
            "unique : les qualités divines qui parlent le plus fort en toi, les zones "
            "d'apprentissage encore endormies, et le sens spirituel que ton âme cherche "
            "à incarner."
            "<br/><br/>"
            "Prends ces pages lentement. La Kabbale n'est pas un texte à consommer, "
            "c'est un texte à laisser infuser."
        ),
        'sephiroth_principales': (
            "Trois séphiroth structurent ta lumière dominante. Elles ne sont pas des "
            "qualités séparées mais un triangle vivant : quand l'une s'exprime trop "
            "seule, les deux autres viennent la rééquilibrer."
            "<br/><br/>"
            "L'équilibre entre elles définit ta signature spirituelle. Si tu vis un "
            "moment de déséquilibre — trop de rigueur, trop de générosité, trop "
            "d'intériorité — c'est probablement l'une des trois qui a pris le pouvoir. "
            "Le retour se fait en rappelant les deux autres à leur juste place."
            "<br/><br/>"
            "Ton travail spirituel de cette vie tourne autour de cette triangulation. "
            "Chaque fois que tu la sens circuler harmonieusement, tu es exactement à "
            "ta place."
        ),
        'chemin_kabbalistique': (
            "Ton chemin kabbalistique est l'axe principal que ton âme a choisi de "
            "traverser. Il relie deux Séphiroth précises, et le passage entre elles "
            "constitue le grand apprentissage de cette incarnation."
            "<br/><br/>"
            "Ce chemin n'est pas linéaire — il alterne des phases d'ascension (montée "
            "vers la lumière) et des phases de descente (incarnation, matière). Aucune "
            "n'est meilleure que l'autre. C'est le va-et-vient qui construit."
        ),
        'gematria_nom': (
            "La Gematria de ton nom — sa valeur numérique en hébreu — révèle une "
            "vibration cachée. Elle ne remplace pas ta numérologie occidentale ; elle la "
            "complète d'une couche plus profonde, plus sacrée."
            "<br/><br/>"
            "Ce nombre sacré est un pont entre ton identité quotidienne et ton identité "
            "spirituelle. Le méditer régulièrement (le contempler, l'écrire, le "
            "prononcer) installe une résonance particulière."
        ),
        'lettres_hebraiques': (
            "Trois lettres hébraïques ont une résonance particulière avec ton profil. "
            "Chacune porte une vibration spécifique et un enseignement précis, souvent "
            "lié à un moment ou un thème de ta vie."
            "<br/><br/>"
            "Les lettres hébraïques ne sont pas de simples signes graphiques — ce sont, "
            "selon la Kabbale, les briques par lesquelles la Création s'est déployée. "
            "Les tiennes te rappellent où ton âme puise sa force créatrice."
        ),
        'invitation_finale': (
            "{prenom}, ton Arbre de Vie n'est pas un diagramme à comprendre — c'est un "
            "corps subtil à habiter. Chaque Séphirah que tu as activée est un muscle "
            "spirituel à exercer ; chaque chemin que tu as ouvert est une porte qui "
            "reste, désormais, à ta disposition."
            "<br/><br/>"
            "La Kabbale te murmure une seule chose, au fond : tu es déjà tout ce que tu "
            "cherches. Il te reste à l'incarner."
        ),
    },

    # ═══════════════════════════════════════════════════════════════
    'pack_karmique': {
        'synthese': (
            "{prenom}, ce document est le plus complet que Plume Astrale rédige. Il "
            "croise deux traditions millénaires — l'astrologie karmique et la Kabbale — "
            "pour dessiner la carte de ton âme dans cette incarnation."
            "<br/><br/>"
            "Ce que tu vas découvrir n'est pas un horoscope. C'est une lecture "
            "structurelle : la mémoire de ton âme, ses apprentissages en cours, la "
            "direction qu'elle a choisie, et la lumière kabbalistique qui la nourrit."
            "<br/><br/>"
            "Ne cherche pas à tout intégrer en une lecture. Prends chaque partie "
            "séparément, laisse-la infuser plusieurs jours, puis reviens à la suivante. "
            "Ce document est fait pour t'accompagner sur plusieurs années."
        ),
        'axe_karmique_principal': (
            "Ton axe karmique principal est le grand fil rouge de ta vie. Il traverse "
            "toutes tes relations, toutes tes vocations, toutes tes crises importantes. "
            "L'identifier te permet de comprendre <i>pourquoi</i> certains thèmes "
            "reviennent, quel que soit le décor."
            "<br/><br/>"
            "Cet axe se construit à partir de la ligne entre ton Nœud Sud (ce que tu "
            "sais déjà faire) et ton Nœud Nord (ce que tu es venue apprendre). Le "
            "chemin entre les deux n'est jamais direct — c'est plutôt une spirale, "
            "avec des rendez-vous périodiques que ton âme provoque discrètement."
            "<br/><br/>"
            "Reconnaître cet axe change ta manière de traverser les épreuves. Elles "
            "cessent d'être aléatoires — elles deviennent des étapes d'un apprentissage "
            "cohérent."
        ),
        'liens_karmiques': (
            "Certaines personnes croisent ta route pour rester peu ; d'autres pour "
            "changer tout. Les liens karmiques sont les seconds : ils apparaissent avec "
            "une intensité disproportionnée, brièvement ou longtemps, et te "
            "transforment durablement."
            "<br/><br/>"
            "Ces liens ne sont pas toujours agréables. Certains sont là pour t'apprendre "
            "à aimer, d'autres pour t'apprendre à te choisir. Ceux qui te blessent "
            "profondément portent souvent la leçon la plus précieuse — mais tu n'es "
            "obligée d'accepter aucune violence pour apprendre."
            "<br/><br/>"
            "Une règle intime : quand un lien te fatigue plus qu'il ne te nourrit, il "
            "a probablement terminé son enseignement. Le laisser partir n'est pas un "
            "échec — c'est un accomplissement."
        ),
        'invitation_finale': (
            "{prenom}, ton âme n'est pas arrivée ici par hasard. Elle porte une "
            "mémoire, une dette, une promesse — et ce document en est la carte. "
            "Reviens-y à chaque grand seuil de ta vie."
            "<br/><br/>"
            "Ce que tu es venue accomplir dans cette incarnation ne se mesure pas en "
            "diplômes, en revenus, ni en likes. Ça se mesure en fidélité à ta "
            "trajectoire — cette petite voix intérieure qui sait, depuis toujours, ce "
            "qui est juste pour toi."
        ),
    },

    # ═══════════════════════════════════════════════════════════════
    'tarot_natal': {
        'introduction': (
            "{prenom}, le tarot de naissance associe à ton jour, ton mois et ton année "
            "trois arcanes majeurs qui structurent ton chemin. Ces cartes ne sont pas "
            "aléatoires — elles sont ta signature symbolique dans la lame du destin."
        ),
        'carte_ame': (
            "Ta carte d'âme raconte ce que tu es venue apprendre au niveau le plus "
            "profond. C'est le rôle de fond de cette incarnation, celui qui ne change "
            "pas avec les saisons."
            "<br/><br/>"
            "Cette carte peut ne pas ressembler à ton comportement quotidien — elle "
            "décrit une pulsion souterraine, un archétype qui te tire vers l'avant "
            "même quand ta tête doute."
        ),
        'carte_personnalite': (
            "Ta carte de personnalité est la manière dont tu vis ton archétype d'âme "
            "au quotidien. C'est ta façon d'incarner ta mission, dans les gestes "
            "concrets, dans les relations, dans les choix ordinaires."
        ),
        'carte_annee': (
            "Ta carte de l'année en cours colore les 12 prochains mois. Elle indique "
            "les qualités à cultiver, les défis à traverser, et les invitations "
            "cachées derrière les événements apparents."
        ),
        'invitation_finale': (
            "{prenom}, ces trois cartes te suivent à vie — mais tu peux les habiter de "
            "mille manières. Le tarot n'est jamais une prophétie fermée ; c'est un "
            "miroir vibrant qui te renvoie ta propre lumière."
        ),
    },
}


def get_static_fallback(report_type: str, prenom: str) -> Dict[str, str]:
    """Retourne un dictionnaire de sections narratives statiques riches.

    Utilisé comme fallback quand l'enrichissement IA est désactivé (toggle admin)
    ou quand l'appel LLM échoue. Chaque section fait 2-4 paragraphes rédigés
    d'avance à la voix de Soléna, avec interpolation du prénom.
    """
    template = _FALLBACKS.get(report_type)
    if not template:
        return {}
    safe_name = (prenom or 'toi').strip() or 'toi'
    return {k: v.replace('{prenom}', safe_name) for k, v in template.items()}
