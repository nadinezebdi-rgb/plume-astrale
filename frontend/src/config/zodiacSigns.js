/**
 * Données éditoriales des 12 signes du zodiaque.
 *
 * Positionnement 2026-08 : ne parle PAS de "prédiction du jour"
 * mais de traits universels, cycles favorables et zones de vigilance.
 * Vocabulaire aligné Phase 3 (période, cycle, comprendre, aspirer).
 *
 * Chaque signe a :
 *   - slug (url + i18n)
 *   - name (nom français)
 *   - dates (période du signe)
 *   - element / modality
 *   - archetype (1 phrase forte)
 *   - traits (3-4 mots-clés positifs)
 *   - challenges (2-3 zones de vigilance formulées avec douceur)
 *   - keyPeriods (2 périodes de l'année particulièrement fortes)
 *   - relatedProduct (route sales page correspondante)
 */
export const ZODIAC_SIGNS = [
  {
    slug: 'belier',
    name: 'Bélier',
    dates: '21 mars — 19 avril',
    element: 'Feu',
    modality: 'Cardinal',
    ruler: 'Mars',
    glyph: '♈',
    archetype: 'Celui ou celle qui ose le premier pas.',
    intro: "Le Bélier ouvre la roue du zodiaque. Il incarne l'élan initial, ce moment précis où l'on choisit d'agir plutôt que d'attendre. Chaque nouveau départ, chaque décision qui demande du courage porte cette énergie.",
    traits: ['Courage', 'Spontanéité', 'Franchise', 'Initiative'],
    challenges: [
      "Apprendre à laisser mûrir les projets sans se précipiter.",
      "Reconnaître que la patience n'est pas un manque d'ambition.",
    ],
    keyPeriods: [
      { when: 'Mars — avril', what: 'Retour du Soleil sur votre signe : moment idéal pour poser une intention nouvelle.' },
      { when: 'Octobre', what: 'Six mois plus tard : bilan de ce que vous avez semé au printemps.' },
    ],
    relatedProduct: '/theme-natal',
  },
  {
    slug: 'taureau',
    name: 'Taureau',
    dates: '20 avril — 20 mai',
    element: 'Terre',
    modality: 'Fixe',
    ruler: 'Vénus',
    glyph: '♉',
    archetype: 'Celui ou celle qui bâtit avec constance.',
    intro: "Le Taureau enracine. Il cherche ce qui dure, ce qui apaise, ce qui compte vraiment. Dans un monde qui va vite, il rappelle que certaines choses demandent du temps — et méritent qu'on leur en donne.",
    traits: ['Constance', 'Sens du concret', 'Beauté', 'Loyauté'],
    challenges: [
      "Accepter que le changement, parfois, est plus vivifiant que la stabilité.",
      "S'autoriser à lâcher ce qui vous rassure mais ne vous porte plus.",
    ],
    keyPeriods: [
      { when: 'Avril — mai', what: 'Anniversaire solaire : période propice aux engagements durables (relations, achats, ancrages).' },
      { when: 'Novembre', what: 'Six mois plus tard : moment de récolte matérielle.' },
    ],
    relatedProduct: '/theme-natal',
  },
  {
    slug: 'gemeaux',
    name: 'Gémeaux',
    dates: '21 mai — 20 juin',
    element: 'Air',
    modality: 'Mutable',
    ruler: 'Mercure',
    glyph: '♊',
    archetype: 'Celui ou celle qui relie et fait circuler.',
    intro: "Le Gémeaux traduit. Il fait le lien entre les idées, entre les gens, entre les univers qui ne se parlent pas. Sa curiosité est un pont — mais il lui faut aussi apprendre à s'arrêter parfois.",
    traits: ['Curiosité', 'Communication', 'Adaptabilité', 'Vivacité'],
    challenges: [
      "Choisir une direction quand mille chemins semblent possibles.",
      "Ne pas confondre agitation et action véritable.",
    ],
    keyPeriods: [
      { when: 'Mai — juin', what: 'Anniversaire solaire : période propice à formuler, écrire, rencontrer.' },
      { when: 'Décembre', what: 'Six mois plus tard : les idées semées portent leurs fruits.' },
    ],
    relatedProduct: '/theme-natal',
  },
  {
    slug: 'cancer',
    name: 'Cancer',
    dates: '21 juin — 22 juillet',
    element: 'Eau',
    modality: 'Cardinal',
    ruler: 'Lune',
    glyph: '♋',
    archetype: 'Celui ou celle qui protège et fait mémoire.',
    intro: "Le Cancer garde. Il tient les liens familiaux, les racines, les souvenirs qui font qu'on sait d'où on vient. Sa sensibilité est un radar qui capte ce que d'autres ne voient même pas.",
    traits: ['Sensibilité', 'Mémoire', 'Attachement', 'Protection'],
    challenges: [
      "Reconnaître quand l'attachement devient enfermement.",
      "Oser sortir de la coquille pour laisser entrer du neuf.",
    ],
    keyPeriods: [
      { when: 'Juin — juillet', what: 'Anniversaire solaire : moment idéal pour renouer avec ses racines familiales.' },
      { when: 'Janvier', what: 'Six mois plus tard : bilan émotionnel et projet pour l\'année.' },
    ],
    relatedProduct: '/karma-destin',
  },
  {
    slug: 'lion',
    name: 'Lion',
    dates: '23 juillet — 22 août',
    element: 'Feu',
    modality: 'Fixe',
    ruler: 'Soleil',
    glyph: '♌',
    archetype: 'Celui ou celle qui rayonne et fait rayonner.',
    intro: "Le Lion illumine. Il porte en lui un besoin profond d'être vu — non par vanité, mais parce qu'il sait qu'exister pleinement, c'est aussi laisser une trace lumineuse. Sa générosité est solaire.",
    traits: ['Rayonnement', 'Générosité', 'Créativité', 'Confiance'],
    challenges: [
      "Trouver l'équilibre entre s'affirmer et laisser les autres briller.",
      "Reconnaître sa valeur sans avoir besoin qu'on la lui confirme.",
    ],
    keyPeriods: [
      { when: 'Juillet — août', what: 'Anniversaire solaire : période propice à se montrer, créer, oser.' },
      { when: 'Février', what: 'Six mois plus tard : les projets créatifs mûrissent.' },
    ],
    relatedProduct: '/theme-natal',
  },
  {
    slug: 'vierge',
    name: 'Vierge',
    dates: '23 août — 22 septembre',
    element: 'Terre',
    modality: 'Mutable',
    ruler: 'Mercure',
    glyph: '♍',
    archetype: 'Celui ou celle qui affine et rend meilleur.',
    intro: "La Vierge ajuste. Elle voit ce qui ne va pas, ce qui peut être amélioré, ce qui mérite d'être soigné avec précision. Son perfectionnisme est un service rendu au monde — quand elle apprend à ne pas le retourner contre elle-même.",
    traits: ['Précision', 'Sens du service', 'Discernement', 'Humilité'],
    challenges: [
      "S'autoriser l'imperfection sans se sentir en faute.",
      "Apprendre à recevoir autant qu'on donne.",
    ],
    keyPeriods: [
      { when: 'Août — septembre', what: 'Anniversaire solaire : moment idéal pour réorganiser vie pro, santé, quotidien.' },
      { when: 'Mars', what: 'Six mois plus tard : les habitudes semées deviennent structure.' },
    ],
    relatedProduct: '/numerologie-pdf',
  },
  {
    slug: 'balance',
    name: 'Balance',
    dates: '23 septembre — 22 octobre',
    element: 'Air',
    modality: 'Cardinal',
    ruler: 'Vénus',
    glyph: '♎',
    archetype: 'Celui ou celle qui cherche le juste équilibre.',
    intro: "La Balance harmonise. Elle a un besoin viscéral de justice, de beauté, d'accords justes entre les êtres. Ses hésitations ne sont pas de la faiblesse : elle pèse ce que d'autres tranchent trop vite.",
    traits: ['Diplomatie', 'Esthétique', 'Sens de la justice', 'Charme'],
    challenges: [
      "Apprendre à décider même quand tout n'est pas parfaitement clair.",
      "Reconnaître que dire non est aussi une forme d'harmonie.",
    ],
    keyPeriods: [
      { when: 'Septembre — octobre', what: 'Anniversaire solaire : période propice aux engagements de couple, aux collaborations.' },
      { when: 'Avril', what: 'Six mois plus tard : les liens tissés à l\'automne se solidifient.' },
    ],
    relatedProduct: '/synastrie',
  },
  {
    slug: 'scorpion',
    name: 'Scorpion',
    dates: '23 octobre — 21 novembre',
    element: 'Eau',
    modality: 'Fixe',
    ruler: 'Pluton',
    glyph: '♏',
    archetype: 'Celui ou celle qui va sous la surface.',
    intro: "Le Scorpion pénètre. Il refuse le vernis, cherche ce qui se cache sous les mots, sous les silences. Son intensité fait peur à certains et libère les autres — ceux qui n'avaient plus envie de faire semblant.",
    traits: ['Intensité', 'Profondeur', 'Transformation', 'Loyauté'],
    challenges: [
      "Doser la profondeur pour ne pas épuiser les liens.",
      "Accepter que certaines choses n'aient pas besoin d'être décodées.",
    ],
    keyPeriods: [
      { when: 'Octobre — novembre', what: 'Anniversaire solaire : période propice aux grandes remises en question.' },
      { when: 'Mai', what: 'Six mois plus tard : les métamorphoses semées commencent à porter.' },
    ],
    relatedProduct: '/karma-destin',
  },
  {
    slug: 'sagittaire',
    name: 'Sagittaire',
    dates: '22 novembre — 21 décembre',
    element: 'Feu',
    modality: 'Mutable',
    ruler: 'Jupiter',
    glyph: '♐',
    archetype: 'Celui ou celle qui cherche le sens et l\'horizon.',
    intro: "Le Sagittaire élève. Il refuse les cadres trop étroits, aime les grandes questions, les voyages qui bousculent, les cultures qui élargissent. Son optimisme est une conviction : la vie a plus à offrir qu'on ne croit.",
    traits: ['Élan', 'Sens du sens', 'Liberté', 'Enthousiasme'],
    challenges: [
      "Apprendre à s'ancrer sans se sentir prisonnier.",
      "Tenir dans la durée ce qui a été promis avec enthousiasme.",
    ],
    keyPeriods: [
      { when: 'Novembre — décembre', what: 'Anniversaire solaire : moment idéal pour élargir horizons, études, voyages.' },
      { when: 'Juin', what: 'Six mois plus tard : les projets d\'expansion trouvent leur forme.' },
    ],
    relatedProduct: '/astrocartographie',
  },
  {
    slug: 'capricorne',
    name: 'Capricorne',
    dates: '22 décembre — 19 janvier',
    element: 'Terre',
    modality: 'Cardinal',
    ruler: 'Saturne',
    glyph: '♑',
    archetype: 'Celui ou celle qui construit dans la durée.',
    intro: "Le Capricorne structure. Il sait qu'un projet solide se bâtit patiemment, pierre par pierre. Sa rigueur n'est pas de la sécheresse : c'est le respect de ce qui mérite d'exister durablement.",
    traits: ['Ambition', 'Discipline', 'Responsabilité', 'Endurance'],
    challenges: [
      "S'autoriser la spontanéité et la vulnérabilité.",
      "Célébrer ses accomplissements au lieu de courir déjà au suivant.",
    ],
    keyPeriods: [
      { when: 'Décembre — janvier', what: 'Anniversaire solaire : moment idéal pour poser les fondations d\'une année ambitieuse.' },
      { when: 'Juillet', what: 'Six mois plus tard : les projets professionnels s\'incarnent.' },
    ],
    relatedProduct: '/kabbale',
  },
  {
    slug: 'verseau',
    name: 'Verseau',
    dates: '20 janvier — 18 février',
    element: 'Air',
    modality: 'Fixe',
    ruler: 'Uranus',
    glyph: '♒',
    archetype: 'Celui ou celle qui pense librement et différemment.',
    intro: "Le Verseau invente. Il refuse d'entrer dans les cases qu'on lui prépare, aime les idées qui bousculent, les groupes qui font avancer les choses. Sa distance apparente cache un attachement profond à l'humanité.",
    traits: ['Originalité', 'Vision', 'Indépendance', 'Fraternité'],
    challenges: [
      "Laisser entrer l'émotion sans la trouver menaçante.",
      "Accepter d\'appartenir sans avoir l\'impression de se perdre.",
    ],
    keyPeriods: [
      { when: 'Janvier — février', what: 'Anniversaire solaire : moment idéal pour se réinventer, changer de cadre.' },
      { when: 'Août', what: 'Six mois plus tard : les idées nouvelles trouvent leur public.' },
    ],
    relatedProduct: '/theme-natal-luxe',
  },
  {
    slug: 'poissons',
    name: 'Poissons',
    dates: '19 février — 20 mars',
    element: 'Eau',
    modality: 'Mutable',
    ruler: 'Neptune',
    glyph: '♓',
    archetype: 'Celui ou celle qui ressent tout, qui rêve grand.',
    intro: "Le Poissons dissout. Il refuse les frontières trop nettes, capte ce qui flotte dans l'air, transforme la douleur des autres en art. Sa sensibilité est un don — à condition qu'il apprenne à s'en protéger.",
    traits: ['Empathie', 'Imagination', 'Intuition', 'Compassion'],
    challenges: [
      "Distinguer ce qui vous appartient de ce que vous absorbez des autres.",
      "S'ancrer dans le concret sans perdre sa magie intérieure.",
    ],
    keyPeriods: [
      { when: 'Février — mars', what: 'Anniversaire solaire : moment idéal pour un retrait créatif, une pause spirituelle.' },
      { when: 'Septembre', what: 'Six mois plus tard : les intuitions semées prennent forme.' },
    ],
    relatedProduct: '/karma-destin',
  },
];

export const getSignBySlug = (slug) => ZODIAC_SIGNS.find((s) => s.slug === slug) || null;
