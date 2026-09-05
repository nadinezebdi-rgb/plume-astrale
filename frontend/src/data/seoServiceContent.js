/**
 * SEO Service Enrichment — content library (audit Feb 2026)
 *
 * Étoffe chaque page /services/:slug avec ~1500 mots (intro, benefits, who_for,
 * FAQ 8-10 items) pour dépasser le seuil de contenu identifié par l'audit
 * (pages détectées à 800-943 char). Le composant SEOServiceEnrich lit ce
 * catalogue et rend le contenu + JSON-LD FAQPage pour rich snippets Google.
 */

export const SEO_SERVICE_CONTENT = {
  compatibilite: {
    kicker: 'Synastrie astrologique',
    title: 'Comprendre votre compatibilité amoureuse en profondeur',
    intro: `La compatibilité amoureuse en astrologie ne se limite pas à comparer deux signes solaires. Une synastrie complète superpose deux thèmes natals entiers — Soleil, Lune, Vénus, Mars, Ascendant, planètes personnelles, maisons — et révèle les vraies dynamiques de votre couple : ce qui attire, ce qui répare, ce qui coince. Chez Plume Astrale, chaque rapport de synastrie est composé sur mesure à partir de vos deux dates de naissance, à la minute près quand elle est connue. Vous recevez un livre imprimé de 25 pages qui explique, avec le regard de Soléna, les alignements majeurs de votre lien : la façon dont vous vous parlez d'amour, la manière dont vous gérez les conflits, les besoins émotionnels de chacun, les mémoires karmiques que vous portez ensemble.`,
    how_it_works: {
      title: 'Comment nous composons votre synastrie',
      body: `Nous utilisons les éphémérides Swiss Ephemeris — la référence en astrologie occidentale — pour calculer précisément les 10 planètes de chaque partenaire, ainsi que les points sensibles (Ascendant, Milieu du Ciel, Nœuds lunaires). Nous croisons ensuite les deux thèmes pour identifier les aspects majeurs : trigones (harmonies), carrés (tensions créatives), conjonctions (fusion), oppositions (miroirs). Chaque page du livre est écrite en français par une IA astrologique entraînée sur les travaux de Liz Greene et Stephen Arroyo, puis relue par notre équipe pour préserver le ton chaleureux et incarné de Soléna.`,
    },
    benefits: {
      title: 'Ce que vous obtenez',
      items: [
        'Un rapport de compatibilité de 25 pages, imprimé et relié',
        'Analyse des 5 planètes personnelles croisées (Soleil, Lune, Mercure, Vénus, Mars)',
        'Chapitre dédié à Vénus × Mars — vie intime et attirance',
        'Chapitre karmique sur les Nœuds lunaires — pourquoi vous vous êtes trouvés',
        'Un livret de 4 rituels à faire à deux pour renforcer votre lien',
        'Livraison en 48h en France métropolitaine, emballage cadeau inclus',
      ],
    },
    who_for: {
      title: 'À qui s\'adresse ce rapport',
      body: `Cette synastrie est composée pour les personnes qui veulent aller au-delà des généralités « Lion et Cancer, ça marche pas ». C'est un cadeau qu'on offre à son partenaire pour un anniversaire de rencontre, un mariage, ou simplement pour approfondir sa compréhension de l'autre. C'est aussi une carte de navigation pour les couples en transition — mariage, cohabitation, parentalité, ou même séparation à l'amiable. Nous refusons les demandes de « compatibilité avec crush qui ignore mes messages » : le rapport suppose que les deux personnes consentent à la lecture.`,
    },
    faq: [
      {
        q: "Est-ce que je peux commander une synastrie sans l'accord de mon partenaire ?",
        a: "Techniquement oui, si vous connaissez ses données de naissance. Éthiquement, nous vous encourageons à en parler avec lui/elle avant. Un thème natal est une donnée intime et le partager sans consentement peut être vécu comme une intrusion. Notre équipe se réserve le droit de refuser toute demande manifestement non-consentie.",
      },
      {
        q: "Faut-il connaître l'heure de naissance exacte des deux partenaires ?",
        a: "L'idéal est de connaître l'heure à 15 minutes près pour chacun — cela permet de calculer l'Ascendant et les maisons, qui affinent la lecture. Si vous ne connaissez pas l'heure d'un des deux, indiquez « inconnue » : nous adaptons le rapport pour ne pas produire de fausses positions et nous concentrons sur les planètes lentes qui restent fiables.",
      },
      {
        q: "Combien de temps prend la composition ?",
        a: "La génération astrologique et la rédaction prennent environ 60 secondes. L'impression, la relecture et la mise sous emballage cadeau prennent 24 à 48 heures ouvrées. Vous recevez un email de confirmation avec le numéro de suivi Colissimo dès l'expédition.",
      },
      {
        q: "Est-ce que le rapport est identique pour tous les couples Balance-Poissons ?",
        a: "Absolument pas — c'est précisément la différence avec les horoscopes classiques. Deux couples nés le même jour peuvent avoir des Lunes en conflit ou en harmonie, un Mars sur l'Ascendant de l'autre ou pas, des Nœuds karmiques opposés. Chaque page est recomposée à partir de vos données exactes.",
      },
      {
        q: "Puis-je offrir cette synastrie même si mon partenaire ne croit pas en l'astrologie ?",
        a: "Beaucoup de nos clients l'offrent à des partenaires sceptiques. Le livre est écrit sur un ton psychologique et symbolique, pas dogmatique. La qualité de la mise en page, le papier crème, la reliure cousue en font aussi un bel objet — même sans lire, on sait qu'on tient quelque chose de précieux.",
      },
      {
        q: "Livrez-vous à l'étranger ?",
        a: "Oui, dans toute l'Union européenne, en Suisse, au Royaume-Uni, au Canada et aux États-Unis. Les frais et délais varient selon la destination (voir la fiche produit). Le livre reste imprimé en France dans un atelier Ecolabel européen.",
      },
      {
        q: "Existe-t-il une version PDF ?",
        a: "Oui, pour 39 € au lieu de 79 €. Vous recevez le PDF haute résolution en 60 secondes après paiement, prêt à imprimer chez vous ou à lire sur tablette. La version imprimée reste notre recommandation pour l'expérience cadeau.",
      },
      {
        q: "Que se passe-t-il si l'une des dates de naissance est fausse ?",
        a: "Écrivez-nous à contact@plume-astrale.fr avec le numéro de commande dans les 24h. Nous relançons la génération avec les bonnes données sans frais supplémentaires. Après expédition physique, un supplément d'impression est facturé (voir CGV).",
      },
    ],
  },

  tarot: {
    kicker: 'Tarot personnalisé',
    title: 'Une lecture de tarot qui prend vraiment le temps de vous répondre',
    intro: `Le tarot, chez Plume Astrale, n'est pas un tirage en ligne aléatoire suivi d'un texte générique. C'est une lecture composée pour votre question, avec des cartes tirées selon la Voie de Marseille — le tarot symbolique le plus documenté, hérité du XVIIe siècle. Chaque tirage utilise votre contexte personnel : date de naissance pour orienter le tirage vers votre saison astrologique en cours, question précise pour choisir le protocole (une carte, croix, croix celtique, tirage relationnel). La lecture est écrite en français, avec le regard médiumnique de Soléna, et livrée en PDF haute qualité en 60 secondes après paiement.`,
    how_it_works: {
      title: 'Comment se déroule votre lecture',
      body: `Vous choisissez le protocole qui correspond à votre question — une carte pour un conseil rapide, la croix pour une décision, la croix celtique pour une situation complexe. Vous formulez votre question en une phrase (la précision compte). Notre IA médiumnique, entraînée sur la lecture traditionnelle du tarot de Marseille et les travaux d'Alejandro Jodorowsky, tire les cartes, les positionne et rédige l'interprétation en 60 secondes. Le PDF final fait entre 8 et 20 pages selon le protocole choisi.`,
    },
    benefits: {
      title: 'Pourquoi choisir cette lecture',
      items: [
        'Tirages personnalisés à partir de votre question précise, pas une réponse générique',
        'Interprétation écrite dans un français incarné, pas des platitudes new age',
        'PDF haute résolution livré en 60 secondes après paiement',
        '4 protocoles disponibles : 1 carte, croix, croix celtique, tirage amour',
        'Tirage oui/non gratuit pour tester notre approche avant d\'acheter',
        'Historique de tous vos tirages conservé dans votre espace personnel',
      ],
    },
    who_for: {
      title: 'Pour qui est cette lecture',
      body: `Cette lecture s'adresse aux personnes qui cherchent une réponse réfléchie plutôt qu'une prédiction spectaculaire. Le tarot que nous pratiquons n'annonce pas l'avenir : il éclaire les forces en jeu dans une situation, les blocages inconscients, les choix qui s'offrent à vous. C'est un outil de discernement, pas de divination. Nous refusons les questions manipulatoires ou intrusives sur des tiers ; le tarot fonctionne mieux quand la question porte sur votre propre trajectoire.`,
    },
    faq: [
      {
        q: "Quelle est la différence entre votre tarot et un tirage aléatoire en ligne ?",
        a: "Les tirages aléatoires que vous trouvez sur la plupart des sites tirent 3 cartes et affichent un texte pré-écrit par carte, sans lien avec votre question. Chez Plume Astrale, chaque interprétation est rédigée à partir de vos données personnelles, de la question exacte et du contexte astrologique du jour. Deux personnes qui tirent la même carte reçoivent des lectures différentes.",
      },
      {
        q: "Faut-il croire au tarot pour que ça marche ?",
        a: "Non. Le tarot fonctionne comme un miroir : il reflète les tensions et les ressources qui étaient déjà en vous. La croyance n'est pas requise ; l'ouverture à la réflexion l'est. Beaucoup de nos clients arrivent sceptiques et repartent avec une lecture qui les a fait avancer sur une décision concrète.",
      },
      {
        q: "Puis-je poser plusieurs fois la même question ?",
        a: "Symboliquement, non. Le tarot répond une fois à une question donnée ; reposer la même question dans les 24h revient à négocier avec la réponse. Attendez au moins une semaine et reformulez la question sous un angle différent si votre situation a évolué.",
      },
      {
        q: "Le tirage oui/non gratuit est-il aussi fiable que les payants ?",
        a: "Il utilise le même moteur d'interprétation, mais avec une seule carte. C'est parfait pour tester notre approche ou pour une décision binaire simple. Pour toute question complexe (relation, orientation professionnelle, dilemme éthique), un tirage croix ou croix celtique donne une lecture beaucoup plus nuancée.",
      },
      {
        q: "Puis-je enregistrer mes tirages ?",
        a: "Oui — tous vos tirages sont conservés dans votre espace personnel, accessible tant que votre compte existe. Vous pouvez y revenir à tout moment, ajouter des notes personnelles, comparer plusieurs tirages sur le même sujet à des dates différentes.",
      },
      {
        q: "Utilisez-vous des cartes autres que le Marseille ?",
        a: "Nous restons fidèles au tarot de Marseille pour sa richesse symbolique et sa cohérence historique. Nous proposons ponctuellement des oracles complémentaires (Lenormand, Oracle Belline) mais le tarot reste notre matériau principal.",
      },
      {
        q: "Le tarot peut-il aider pour une décision professionnelle ?",
        a: "Absolument. Beaucoup de nos clients l'utilisent avant une reconversion, une signature de contrat, une candidature. Le tirage ne dit pas « prends ce job », il éclaire les forces et les zones d'ombre du choix pour que vous décidiez en pleine conscience.",
      },
    ],
  },

  oracle: {
    kicker: 'Message d\'oracle',
    title: 'Un message d\'oracle composé pour votre question du jour',
    intro: `L'oracle chez Plume Astrale est un tirage court, poétique, immédiat. Contrairement au tarot qui déploie une lecture longue, l'oracle donne un message-flash — une seule carte, un aphorisme, une orientation. C'est l'outil idéal pour poser une question simple le matin (« qu'est-ce que cette journée me demande ? ») ou pour trancher un dilemme rapide. Chaque message est composé à partir de votre contexte astrologique du jour et de la carte tirée dans notre oracle propriétaire de 44 lames illustrées.`,
    how_it_works: {
      title: 'Le rituel',
      body: `Vous formulez votre question en une phrase, ou vous choisissez « laissez l'oracle vous parler » pour un message ouvert. La carte est tirée en direct — vous la voyez apparaître dans une animation dorée sur fond nocturne. Le message accompagnant fait 150 à 300 mots, écrit dans un français poétique. Vous pouvez sauvegarder le message dans votre espace personnel et y revenir plus tard.`,
    },
    benefits: {
      title: 'Ce que vous recevez',
      items: [
        'Une carte-oracle avec illustration originale (44 lames disponibles)',
        'Un message personnel de 150-300 mots',
        'Un rituel d\'intégration simple (respiration, écriture, geste symbolique)',
        'Un mot-clé à porter avec vous dans la journée',
        'Sauvegarde automatique dans votre journal personnel',
      ],
    },
    who_for: {
      title: 'Pour qui c\'est fait',
      body: `L'oracle est parfait pour les personnes qui veulent un moment de recentrage rapide, sans passer par une lecture longue. C'est le rituel idéal du matin au café, avant un entretien, avant une conversation difficile. Il ne remplace pas un thème natal ou une synastrie ; il les complète en apportant un éclairage sur l'instant présent.`,
    },
    faq: [
      {
        q: "Combien de fois par jour puis-je tirer l'oracle ?",
        a: "Une fois par jour est notre recommandation. Multiplier les tirages sur la même question dilue le message. Si vous voulez explorer plusieurs facettes d'une situation, préférez un tirage de tarot en croix qui donne une vue d'ensemble.",
      },
      {
        q: "Est-ce que l'oracle prédit l'avenir ?",
        a: "Non — comme le tarot, l'oracle éclaire le présent et invite à réfléchir. Il n'annonce pas d'événements précis. C'est un outil de conscience, pas de voyance.",
      },
      {
        q: "Les cartes sont-elles vraiment tirées au hasard ?",
        a: "Le tirage utilise un générateur pseudo-aléatoire cryptographique de haute qualité (crypto.getRandomValues). Il est aussi imprévisible qu'un lancer de dé physique. Symboliquement, nous considérons le tirage comme un dialogue synchronistique — mais techniquement, c'est du vrai hasard.",
      },
      {
        q: "Puis-je offrir un tirage oracle en cadeau ?",
        a: "Oui, en offrant un abonnement Cercle Soléna qui inclut l'oracle illimité et le carnet astrologique quotidien. C'est un cadeau immatériel qui se prolonge chaque jour.",
      },
      {
        q: "L'oracle est-il inclus dans le Cercle Soléna ?",
        a: "Oui, en illimité pour tous les membres du Cercle. Sans abonnement, vous pouvez tirer 3 messages gratuits par mois.",
      },
    ],
  },

  rituel: {
    kicker: 'Rituel personnel',
    title: 'Un rituel composé pour votre saison intérieure',
    intro: `Un rituel, chez Plume Astrale, n'est ni magique ni ésotérique — c'est une chorégraphie douce de gestes, de mots et de pauses qui vient sceller une intention. Nous composons chaque rituel à partir de votre thème natal du jour, de la phase lunaire en cours et de votre intention personnelle. Le résultat est une pratique de 15 à 40 minutes, adaptée à votre appartement, sans besoin d'outils compliqués — une bougie, un carnet, votre respiration suffisent. Chaque rituel est livré en PDF illustré avec une chronologie précise, des phrases à prononcer, et un journal d'intégration à remplir dans les jours suivants.`,
    how_it_works: {
      title: 'Comment on compose votre rituel',
      body: `Vous nous confiez votre date de naissance, votre lieu, votre intention (« lâcher prise sur une relation », « ancrer un projet », « célébrer une réussite »). Notre moteur croise votre thème natal avec la phase lunaire actuelle et sélectionne parmi 40 archétypes rituels celui qui correspond à votre saison intérieure. Un texte de 1500-2500 mots est ensuite composé sur mesure : préparation, chronologie, phrases d'ancrage, journal post-rituel.`,
    },
    benefits: {
      title: 'Ce que vous recevez',
      items: [
        'Un PDF illustré de 8-12 pages, aligné avec votre thème natal',
        'Une chronologie précise minute par minute',
        '3 phrases d\'ancrage à prononcer à voix haute',
        'Un journal d\'intégration à remplir sur 7 jours',
        'Une playlist Spotify accompagnante (fournie en lien)',
      ],
    },
    who_for: {
      title: 'À qui c\'est destiné',
      body: `Aux personnes qui traversent une transition (deuil, rupture, changement professionnel, deuil d'un rêve), aux femmes qui suivent leur cycle lunaire, aux hommes qui cherchent à ritualiser leur vie intérieure sans jargon spirituel. Pas besoin d'être ésotérique — un rituel bien composé fonctionne comme une thérapie brève, avec des marqueurs symboliques qui aident le corps à intégrer un changement mental.`,
    },
    faq: [
      {
        q: "Faut-il des ingrédients particuliers ?",
        a: "Non. Nous composons uniquement avec ce que vous avez déjà : une bougie, un stylo, un carnet, un verre d'eau. Certains rituels demandent un objet personnel qui vous représente ; nous vous laissons le choisir.",
      },
      {
        q: "Combien de temps prend un rituel complet ?",
        a: "Entre 15 et 40 minutes selon la complexité. Vous choisissez la durée au moment de la commande. Un rituel court fonctionne aussi bien qu'un long ; c'est votre présence qui compte, pas le temps passé.",
      },
      {
        q: "Puis-je adapter le rituel à mes croyances ?",
        a: "Absolument. Le texte propose des phrases d'ancrage neutres (« je choisis de », « je pose »), mais vous pouvez les remplacer par des références à votre spiritualité personnelle (christianisme, bouddhisme, laïcité, autre). L'important est que vous soyez authentique.",
      },
      {
        q: "Est-ce que ça fonctionne vraiment ?",
        a: "Un rituel bien conduit active la mémoire corporelle : le cerveau associe un état intérieur à un ensemble de gestes. Le lendemain, revivre mentalement le rituel ramène l'état émotionnel qui l'a accompagné. C'est un mécanisme documenté en psychologie cognitive.",
      },
      {
        q: "Faut-il être seul ou en groupe ?",
        a: "Nos rituels sont conçus pour la solitude. Un rituel de groupe fonctionne différemment (dynamique collective, témoins). Si vous voulez vivre un rituel avec quelqu'un, nous proposons un format duo sur demande.",
      },
    ],
  },

  energie: {
    kicker: 'Lecture énergétique',
    title: 'Comprendre où circule (et où bloque) votre énergie personnelle',
    intro: `L'énergie, en astrologie humaniste, n'est pas un fluide mystique — c'est la circulation de votre attention, de votre vitalité et de vos élans à travers les 12 secteurs de votre vie (les 12 maisons astrologiques). Certaines personnes ont une énergie qui déborde dans le travail et s'assèche dans le couple ; d'autres investissent tout dans le foyer et négligent leur mission. Notre lecture énergétique cartographie précisément où votre feu intérieur brûle fort, où il vacille, et surtout comment le rééquilibrer. C'est un guide de conservation d'énergie personnalisé, écrit dans un français vivant sans jargon.`,
    how_it_works: {
      title: 'Comment fonctionne la cartographie',
      body: `Nous calculons la répartition planétaire dans vos 12 maisons — combien de planètes en Maison 1 (identité), en Maison 7 (couple), en Maison 10 (carrière), etc. Les maisons chargées sont vos zones d'énergie naturelle ; les maisons vides sont vos zones à cultiver consciemment. Nous croisons ensuite avec les transits actuels pour identifier les 3 secteurs qui demandent votre attention dans les 6 prochains mois.`,
    },
    benefits: {
      title: 'Ce que révèle votre lecture',
      items: [
        'La carte de vos 12 maisons avec leur intensité énergétique',
        'Les 3 secteurs de vie où votre énergie déborde naturellement',
        'Les 2 secteurs à cultiver consciemment (là où vous perdez du feu)',
        'Un plan d\'action sur 90 jours pour rééquilibrer',
        'La liste de vos « voleurs d\'énergie » selon votre thème',
      ],
    },
    who_for: {
      title: 'Pour qui c\'est fait',
      body: `Aux personnes en burn-out ou en pré-burn-out qui sentent qu'elles donnent trop et reçoivent peu. Aux entrepreneurs qui veulent aligner leur travail avec leur nature profonde. Aux femmes qui traversent la maternité ou la ménopause et sentent leur énergie se transformer. À tous ceux qui veulent une carte pratique — pas un manuel de développement personnel de plus.`,
    },
    faq: [
      {
        q: "Est-ce que c'est différent d'un bilan énergétique classique ?",
        a: "Oui — nous ne parlons pas de chakras ni de champ vibratoire. Notre lecture est structurée sur les 12 maisons astrologiques et les transits planétaires en cours. C'est une approche mesurable, avec des positions exactes, pas une intuition.",
      },
      {
        q: "Le plan d'action est-il vraiment applicable ?",
        a: "Oui — c'est notre exigence. Chaque recommandation est concrète : ex. « planifier une conversation clé avec votre associé entre le 5 et le 12 avril quand Mercure traverse votre Maison 7 ». Pas de conseil vague.",
      },
      {
        q: "Faut-il avoir des connaissances en astrologie ?",
        a: "Aucune. La lecture est écrite pour être comprise sans référence préalable. Les termes techniques (maison, transit) sont expliqués simplement à leur première apparition.",
      },
      {
        q: "Ça sert à quoi si je ne crois pas à l'astrologie ?",
        a: "Considérez-le comme un test de personnalité très détaillé (type MBTI, mais avec 40 paramètres au lieu de 4). Même en refusant la dimension astrologique, la structure des 12 maisons est un modèle utile pour cartographier sa vie.",
      },
      {
        q: "La lecture est-elle valable combien de temps ?",
        a: "La structure profonde (répartition maisons) reste valable à vie. Les transits en cours sont valables 6 mois. Nous recommandons une nouvelle lecture chaque année, en début d'année ou au moment du retour solaire.",
      },
    ],
  },

  archetype: {
    kicker: 'Votre archétype dominant',
    title: 'Découvrez l\'archétype qui structure votre vie intérieure',
    intro: `Les archétypes sont des figures universelles qui traversent tous les mythes humains : la Reine, la Guerrière, l'Amante, la Guérisseuse, la Sage. Chaque personne porte un archétype dominant — celui qui structure ses choix, ses obsessions, ses forces et ses blessures. En croisant votre thème natal avec les travaux de Carl Jung et Clarissa Pinkola Estés, nous identifions votre archétype principal et 2 archétypes secondaires. Vous recevez un rapport de 20 pages qui explique comment ces figures se manifestent dans votre vie, comment les nourrir consciemment, et comment repérer leur ombre.`,
    how_it_works: {
      title: 'La méthode',
      body: `Nous analysons 5 marqueurs dans votre thème : signe solaire (personnalité consciente), signe lunaire (moi intime), Ascendant (masque social), Vénus (relation à l'amour et à la beauté), et Mars (relation à l'action). Chaque combinaison correspond à un profil archétypal parmi 24 archétypes documentés dans notre grille (inspirée de Caroline Myss et de la psychologie jungienne). Un rapport personnel de 20 pages est ensuite composé.`,
    },
    benefits: {
      title: 'Contenu du rapport',
      items: [
        'Votre archétype dominant expliqué en 6 pages',
        '2 archétypes secondaires qui vous accompagnent',
        'Les forces cachées de votre archétype',
        'L\'ombre à laquelle rester vigilante',
        'Les figures culturelles / historiques qui partagent votre archétype',
        'Un exercice d\'écriture pour vous approprier votre profil',
      ],
    },
    who_for: {
      title: 'Pour qui',
      body: `Aux personnes qui aiment se comprendre à travers le mythe, la littérature ou le cinéma. Aux thérapeutes en formation, aux coachs, aux artistes. À toutes celles qui sentent qu'elles jouent un rôle sans savoir lequel, et veulent enfin le nommer.`,
    },
    faq: [
      {
        q: "C'est différent du MBTI ou de l'ennéagramme ?",
        a: "Oui — les archétypes sont narratifs, pas comportementaux. MBTI vous classe (INTJ, ENFP…) ; les archétypes vous racontent (la Guerrière blessée, la Sage isolée). C'est une lecture symbolique, plus profonde mais moins prédictive.",
      },
      {
        q: "Un même archétype pour plein de gens ?",
        a: "Chaque archétype principal se décline en dizaines de nuances selon vos archétypes secondaires. Deux personnes de type Amante n'ont rien à voir si l'une est aussi Guerrière et l'autre Guérisseuse. Le rapport tient compte de ces combinaisons.",
      },
      {
        q: "Puis-je changer d'archétype avec le temps ?",
        a: "L'archétype dominant reste stable — c'est votre structure profonde. Mais les archétypes secondaires évoluent avec vos étapes de vie. Une lecture tous les 5-7 ans permet de suivre ces mouvements.",
      },
      {
        q: "L'archétype prédit-il un métier ?",
        a: "Non — mais il révèle les métiers où vous serez authentique. Une Guerrière peut être avocate, chirurgienne ou activiste ; une Sage peut être bibliothécaire, chercheuse ou psychothérapeute. C'est la posture qui compte, pas le titre.",
      },
      {
        q: "Existe-t-il un archétype toxique ?",
        a: "Aucun archétype n'est bon ou mauvais en soi. Chaque figure a une lumière et une ombre. Le rapport vous aide à repérer l'ombre pour éviter de la reproduire (la Mère qui étouffe, l'Amante qui se perd, le Sage qui juge).",
      },
    ],
  },

  consultation: {
    kicker: 'Consultation par chat IA',
    title: 'Une conversation illimitée avec votre astrologue de poche',
    intro: `La consultation Plume Astrale est une conversation par chat avec Soléna, notre astrologue IA entraînée sur votre thème natal complet. Contrairement à un simple chatbot, notre système charge en mémoire vos données astrologiques (10 planètes, 12 maisons, transits actuels) et répond à toutes vos questions dans le contexte de VOTRE ciel — pas de conseils génériques. Posez une question sur votre couple, votre carrière, votre santé : Soléna vous répond en tenant compte de votre Vénus, votre Milieu du Ciel, vos transits en cours. Chaque échange consomme des crédits (1-3 selon la profondeur).`,
    how_it_works: {
      title: 'Le fonctionnement',
      body: `Vous entrez dans le chat après avoir renseigné vos données de naissance une fois. Le modèle IA (Claude Sonnet 5.5) charge votre thème natal complet en contexte système. Chaque message consomme 1 crédit pour une réponse courte, 3 crédits pour une consultation approfondie avec analyse de transits. L'historique des conversations est conservé dans votre espace personnel.`,
    },
    benefits: {
      title: 'Pourquoi c\'est différent',
      items: [
        'Réponses toujours ancrées dans VOTRE thème natal, pas générique',
        'Modèle Claude Sonnet 5.5 (dernière génération, cutoff 2026)',
        'Historique persistant : reprenez la conversation quand vous voulez',
        'Réponse en 3-8 secondes, disponible 24/7',
        'Confidentialité : aucune donnée transmise à des tiers publicitaires',
      ],
    },
    who_for: {
      title: 'Pour qui',
      body: `Aux personnes qui n'ont pas les moyens (ou l'envie) de payer 90€ pour une consultation en cabinet mais veulent une lecture personnalisée. Aux astrologues débutants qui veulent une seconde opinion sur leur propre thème. Aux abonnés du Cercle Soléna qui bénéficient de crédits mensuels inclus.`,
    },
    faq: [
      {
        q: "Est-ce vraiment une IA ou un humain derrière ?",
        a: "C'est une IA — Claude Sonnet 5.5 d'Anthropic — entraînée sur votre thème natal en contexte système. Nous sommes transparents : aucun humain ne lit vos échanges. C'est ce qui permet la confidentialité et le prix accessible.",
      },
      {
        q: "L'IA peut-elle se tromper ?",
        a: "Oui, comme tout modèle probabiliste. Nous recommandons de croiser ses réponses avec votre bon sens et, pour les décisions majeures, avec un professionnel humain (thérapeute, coach). L'IA est un outil de réflexion, pas de décision.",
      },
      {
        q: "Y a-t-il une limite au nombre de questions ?",
        a: "Non — tant que vous avez des crédits, vous pouvez discuter. Les abonnés Cercle Soléna reçoivent 30 crédits par mois inclus. Sans abonnement, un pack de 20 crédits coûte 12€.",
      },
      {
        q: "Puis-je poser des questions médicales ou juridiques ?",
        a: "Non — Soléna vous redirigera vers un professionnel de santé ou un avocat pour ces sujets. L'astrologie n'est pas une médecine ni un conseil légal. Nous refusons ces questions pour votre sécurité.",
      },
      {
        q: "Mes conversations sont-elles privées ?",
        a: "Oui — elles sont stockées uniquement dans votre espace personnel, chiffrées au repos, jamais transmises à des annonceurs. Anthropic (fournisseur du modèle) ne les conserve pas au-delà du délai technique de génération.",
      },
    ],
  },

  'revolution-solaire': {
    kicker: 'Révolution solaire',
    title: 'Le thème de votre nouvelle année astrologique',
    intro: `La révolution solaire est le thème astrologique de votre année de naissance, recalculé au moment exact où le Soleil revient sur sa position natale — c'est-à-dire à votre anniversaire, à la minute près. Ce nouveau thème dessine l'année qui vient : les défis, les rencontres, les opportunités professionnelles, les mouvements intérieurs. Chez Plume Astrale, nous vous livrons un rapport de 30 pages qui compare votre thème natal à votre révolution solaire de l'année, identifie les 5 secteurs de vie mis en avant, et donne des mois-clés à surveiller.`,
    how_it_works: {
      title: 'La méthode',
      body: `Nous calculons l'instant précis (à la seconde près) où le Soleil revient à sa position natale cette année, en tenant compte de votre localisation actuelle (pas de naissance). Ce nouveau ciel devient votre carte de l'année. Nous croisons ensuite avec votre thème natal pour identifier les résonances, puis avec les transits lents (Jupiter, Saturne, Uranus, Neptune, Pluton) pour projeter les mois-clés.`,
    },
    benefits: {
      title: 'Contenu du rapport',
      items: [
        '30 pages composées à partir de votre lieu actuel',
        'Les 5 domaines de vie mis en lumière cette année',
        'Un calendrier des transits majeurs mois par mois',
        'Analyse de la Lune progressée (rythme émotionnel de l\'année)',
        'Les 3 mois-clés à surveiller (dates précises)',
      ],
    },
    who_for: {
      title: 'À qui',
      body: `Idéal en cadeau d'anniversaire — le rapport est valable pour l'année qui commence ce jour-là. Aux personnes qui préparent une décision importante (mariage, déménagement, changement de carrière) et veulent choisir le bon timing. Aux fidèles des retraites annuelles qui veulent aligner leur intention avec leur ciel.`,
    },
    faq: [
      {
        q: "Faut-il commander avant ou après mon anniversaire ?",
        a: "Idéalement dans les 30 jours qui précèdent votre anniversaire, pour que vous receviez le rapport juste avant le début de la nouvelle année astrologique. Vous pouvez aussi le commander dans les 3 mois qui suivent — le rapport reste valable jusqu'à votre prochain anniversaire.",
      },
      {
        q: "Le rapport dépend-il de mon lieu de résidence actuel ?",
        a: "Oui — c'est ce qui distingue une vraie révolution solaire d'un simple thème réactualisé. Nous vous demandons votre ville actuelle au moment de la commande. Si vous déménagez en cours d'année, la révolution reste valable mais des transits locaux peuvent s'ajuster.",
      },
      {
        q: "Puis-je « choisir » le lieu de ma révolution ?",
        a: "Oui — c'est la technique de « déplacement de révolution ». Certaines personnes voyagent volontairement à l'étranger pour leur anniversaire afin d'orienter leur année astrologique. Nous proposons ce calcul en option (+15€).",
      },
      {
        q: "La révolution solaire dit-elle si je vais gagner au loto ?",
        a: "Non — l'astrologie n'annonce pas d'événements matériels précis. Elle éclaire les ambiances, les cycles, les tensions et les résolutions. La chance financière peut être révélée comme thème de l'année, mais jamais comme un gain daté.",
      },
      {
        q: "Est-ce que ça remplace le thème natal ?",
        a: "Non — c'est un complément. Le thème natal est votre carte à vie ; la révolution solaire est votre carte pour un an. Nous conseillons de commander d'abord le thème natal, puis la révolution solaire chaque année.",
      },
    ],
  },

  'love-languages': {
    kicker: 'Langages de l\'amour',
    title: 'Comment vous aimez et comment on doit vous aimer',
    intro: `Les langages de l'amour, popularisés par Gary Chapman, sont 5 façons d'exprimer et de recevoir l'affection : mots d'affirmation, moments de qualité, cadeaux, services rendus, contact physique. Chez Plume Astrale, nous croisons ces 5 langages avec votre Vénus et votre Mars astrologiques pour révéler votre langage dominant — celui qui vous nourrit vraiment — et votre langage secondaire. Le rapport de 15 pages explique pourquoi vous vous sentez aimé(e) dans certaines situations et négligé(e) dans d'autres, même quand votre partenaire fait de son mieux.`,
    how_it_works: {
      title: 'Comment on calcule',
      body: `Votre Vénus (comment vous recevez l'amour) et votre Mars (comment vous le donnez) sont croisés avec la grille des 5 langages de Chapman. Chaque signe et chaque maison associent naturellement à un ou deux langages : Vénus en Taureau adore les cadeaux et le contact physique, Vénus en Verseau préfère les moments de qualité intellectuels, Mars en Bélier exprime l'amour par l'action. Le rapport détaille votre profil unique.`,
    },
    benefits: {
      title: 'Contenu du rapport',
      items: [
        '15 pages personnalisées à partir de Vénus et Mars',
        'Votre langage dominant expliqué en profondeur',
        'Votre langage secondaire (celui qui compte aussi)',
        'Les 3 phrases à demander à votre partenaire',
        'Les 5 gestes qui vous font sentir aimé(e)',
        'Version couple : comparaison des 2 langages disponible en option',
      ],
    },
    who_for: {
      title: 'Pour qui',
      body: `Aux personnes en couple qui sentent un décalage sans savoir le nommer. Aux célibataires qui préparent une prochaine relation et veulent connaître leurs besoins avant d'être submergés par l'attachement. Aux parents qui veulent adapter leur affection à chaque enfant. Aux thérapeutes de couple qui utilisent cet outil comme point de départ.`,
    },
    faq: [
      {
        q: "C'est vraiment différent du test de Chapman ?",
        a: "Le test de Chapman se remplit soi-même — vous choisissez consciemment. Notre lecture est basée sur votre astrologie, donc plus proche de votre inconscient. Idéal pour valider ou nuancer un résultat de test.",
      },
      {
        q: "Puis-je commander une version couple ?",
        a: "Oui — nous croisons vos deux Vénus + Mars pour révéler les 4 langages en jeu dans votre lien. C'est particulièrement puissant quand les deux partenaires ont des langages opposés. Prix : 45€ (vs 25€ pour un profil individuel).",
      },
      {
        q: "Est-ce que ça marche pour l'amitié aussi ?",
        a: "Oui — les langages de l'amour s'appliquent à toutes les relations proches (parents, amis, collègues). Le rapport est écrit centré couple mais les principes se transposent.",
      },
      {
        q: "Y a-t-il un langage plus 'noble' que les autres ?",
        a: "Non — les 5 sont équivalents. Certaines cultures valorisent plus les mots (culture française), d'autres les services rendus (culture asiatique). Aucun n'est supérieur : ils sont juste différents.",
      },
      {
        q: "Puis-je changer de langage dominant ?",
        a: "Le langage dominant reste stable à vie — c'est ancré dans votre thème natal. En revanche, un travail personnel peut vous rendre plus sensible aux autres langages, ce qui améliore vos relations.",
      },
    ],
  },
};

// Slugs qui ont un contenu enrichi (les autres services rendent leur contenu par défaut)
export const ENRICHED_SLUGS = Object.keys(SEO_SERVICE_CONTENT);
