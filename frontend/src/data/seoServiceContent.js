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
};

// Slugs qui ont un contenu enrichi (les autres services rendent leur contenu par défaut)
export const ENRICHED_SLUGS = Object.keys(SEO_SERVICE_CONTENT);
