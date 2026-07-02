/**
 * Données AstroSexo : profil sexuel + partenaires idéaux par signe.
 * Ton chic et poétique (validé user 2a) — sensualité voilée, jamais vulgaire.
 * Adapté de Femme Actuelle avec réécriture pour la voix Plume Astrale.
 */
export const ASTROSEXO_PROFILES = {
  belier: {
    sign: 'Bélier',
    element: 'Feu',
    dates: '21 mars — 20 avril',
    profile: "Le Bélier vit ses désirs avec franchise. Passionné, direct, il n'entre pas dans la relation par la porte des convenances — il y entre par le cœur, sans détour. Cette énergie de flamme cherche la sincérité plus que la séduction apprise. Il aime intensément quand la spontanéité est au rendez-vous.",
    ideal: [
      { sign: 'Lion', reason: 'Deux feux qui se reconnaissent, chaleur mutuelle et loyauté partagée.' },
      { sign: 'Gémeaux', reason: 'Un souffle d\'Air qui attise le Feu du Bélier — jeu, curiosité, complicité vive.' },
      { sign: 'Balance', reason: 'La grâce en miroir de la fougue : équilibre subtil qui fascine.' },
    ],
  },
  taureau: {
    sign: 'Taureau',
    element: 'Terre',
    dates: '21 avril — 21 mai',
    profile: "Épicurien dans l'âme, le Taureau élève la sensualité au rang d'art. Il aime lentement, avec attention aux détails — un parfum, une texture, une lumière. C'est un signe fidèle qui a besoin de se sentir en sécurité pour donner le meilleur. Une fois choisi, il chérit son partenaire avec constance.",
    ideal: [
      { sign: 'Scorpion', reason: 'Liaison de braise — la Terre et l\'Eau se mêlent en fusion durable.' },
      { sign: 'Poissons', reason: 'Douceur et rêverie partagées, un cocon qui traverse les saisons.' },
      { sign: 'Capricorne', reason: 'Terre à Terre, construction à deux, tendresse sans effet.' },
    ],
  },
  gemeaux: {
    sign: 'Gémeaux',
    element: 'Air',
    dates: '22 mai — 21 juin',
    profile: "Vif d'esprit et curieux, le Gémeaux séduit par les mots avant les gestes. Il aime la stimulation intellectuelle, les jeux de rôle, l'humour, la surprise. La lassitude est son ennemie — il a besoin d'un partenaire qui sait renouveler la relation, la faire respirer.",
    ideal: [
      { sign: 'Verseau', reason: 'Deux esprits d\'Air qui dansent — dialogue infini et liberté partagée.' },
      { sign: 'Lion', reason: 'Le Feu du Lion attise l\'Air du Gémeaux : passion joyeuse et généreuse.' },
      { sign: 'Balance', reason: 'Deux Airs harmonieux, esthétique du couple et fine complicité.' },
    ],
  },
  cancer: {
    sign: 'Cancer',
    element: 'Eau',
    dates: '22 juin — 22 juillet',
    profile: "Le Cancer est le cœur ouvert du zodiaque. Il aime avec profondeur, absorbe les émotions de l'autre, offre un nid. C'est un signe pudique qui a besoin de confiance pour s'ouvrir — mais une fois le seuil franchi, il donne tout, sans retenue.",
    ideal: [
      { sign: 'Scorpion', reason: 'Deux Eaux qui se reconnaissent — intensité fusionnelle, presque télépathique.' },
      { sign: 'Poissons', reason: 'Rêve à deux, tendresse infinie, communion douce.' },
      { sign: 'Taureau', reason: 'La Terre accueille l\'Eau — foyer stable et sensualité tranquille.' },
    ],
  },
  lion: {
    sign: 'Lion',
    element: 'Feu',
    dates: '23 juillet — 22 août',
    profile: "Le Lion aime en majesté. Généreux, ardent, il place l'autre au centre de sa scène — mais il attend en retour d'être admiré, honoré, reconnu. Sa sensualité est solaire et joyeuse. Il aime les rituels, les moments qui laissent une trace, les grandes déclarations.",
    ideal: [
      { sign: 'Sagittaire', reason: 'Deux Feux nomades — aventure, éclat, joie de vivre partagée.' },
      { sign: 'Bélier', reason: 'Flamme jumelle, complicité ardente, aucun jeu inutile.' },
      { sign: 'Balance', reason: 'La grâce en réponse au rayonnement, esthétique du couple.' },
    ],
  },
  vierge: {
    sign: 'Vierge',
    element: 'Terre',
    dates: '23 août — 22 septembre',
    profile: "La Vierge donne avec précision. Discrète en apparence, elle observe longtemps avant de s'engager — mais quand elle le fait, c'est avec un dévouement rare. Elle prête attention aux détails que d'autres négligent : un regard, un rythme, un besoin non exprimé.",
    ideal: [
      { sign: 'Taureau', reason: 'Deux Terres — sensualité posée, construction lente et fiable.' },
      { sign: 'Capricorne', reason: 'Rigueur et tendresse, respect mutuel, patience partagée.' },
      { sign: 'Poissons', reason: 'L\'opposé complémentaire : la Vierge structure, le Poissons rêve.' },
    ],
  },
  balance: {
    sign: 'Balance',
    element: 'Air',
    dates: '23 septembre — 22 octobre',
    profile: "La Balance cherche l'harmonie du geste. Esthète, raffinée, elle aime la beauté du rapport — le décor, les mots choisis, la mise en scène. Signe de couple par excellence, elle a besoin d'un partenaire qui sait équilibrer force et douceur, présence et espace.",
    ideal: [
      { sign: 'Gémeaux', reason: 'Deux Airs harmonieux, dialogue élégant, jeu et curiosité.' },
      { sign: 'Verseau', reason: 'Liberté partagée, vision commune du couple hors des conventions.' },
      { sign: 'Lion', reason: 'Le Feu du Lion illumine la Balance — couple flamboyant et sincère.' },
    ],
  },
  scorpion: {
    sign: 'Scorpion',
    element: 'Eau',
    dates: '23 octobre — 21 novembre',
    profile: "Le Scorpion est le signe le plus intense du zodiaque en matière d'union. Rien n'est jamais superficiel pour lui — il cherche la transformation, l'engagement total. C'est un signe qui aime en profondeur, avec loyauté et mystère, et dont l'attachement peut durer une vie.",
    ideal: [
      { sign: 'Cancer', reason: 'Deux Eaux qui communient — union fusionnelle, presque mystique.' },
      { sign: 'Taureau', reason: 'L\'opposé aimanté : sensualité de la Terre + profondeur de l\'Eau.' },
      { sign: 'Poissons', reason: 'Rêves partagés, intuition mutuelle, alchimie discrète.' },
    ],
  },
  sagittaire: {
    sign: 'Sagittaire',
    element: 'Feu',
    dates: '22 novembre — 21 décembre',
    profile: "Le Sagittaire aime en grand. Il a besoin d'horizon, de mouvement, de sens. Voyager avec lui, apprendre à ses côtés, découvrir le monde ensemble : voilà sa langue amoureuse. C'est un signe généreux qui donne beaucoup, à condition qu'on respecte sa liberté.",
    ideal: [
      { sign: 'Lion', reason: 'Deux Feux nomades — passion joyeuse, aventures, éclat mutuel.' },
      { sign: 'Bélier', reason: 'Complicité ardente, franchise, aucune manœuvre inutile.' },
      { sign: 'Verseau', reason: 'Air et Feu — libertés partagées, curiosité infinie.' },
    ],
  },
  capricorne: {
    sign: 'Capricorne',
    element: 'Terre',
    dates: '22 décembre — 19 janvier',
    profile: "Le Capricorne aime avec patience. Il construit dans la durée, ne cède pas aux emballements. Sa sensualité se révèle avec le temps : plus les années passent, plus il donne, plus il approfondit. C'est un signe fidèle qui trouve la beauté dans le rituel.",
    ideal: [
      { sign: 'Taureau', reason: 'Deux Terres — tendresse solide, construction à deux, engagement.' },
      { sign: 'Vierge', reason: 'Précision et attention mutuelle, respect profond du rythme de l\'autre.' },
      { sign: 'Poissons', reason: 'Rigueur et rêve — l\'un ancre, l\'autre élève.' },
    ],
  },
  verseau: {
    sign: 'Verseau',
    element: 'Air',
    dates: '20 janvier — 18 février',
    profile: "Le Verseau aime autrement. Original, libre, il refuse les conventions du couple classique. Il a besoin d'un partenaire qui partage ses idées, sa vision, sa liberté — plus qu'un amant, un complice. Sa sensualité est cérébrale avant d'être corporelle.",
    ideal: [
      { sign: 'Gémeaux', reason: 'Deux Airs libres — dialogue infini, curiosité et jeu.' },
      { sign: 'Balance', reason: 'Harmonie et vision commune, couple qui pense ensemble.' },
      { sign: 'Sagittaire', reason: 'Air et Feu — libertés jumelles, quêtes partagées.' },
    ],
  },
  poissons: {
    sign: 'Poissons',
    element: 'Eau',
    dates: '19 février — 20 mars',
    profile: "Le Poissons aime dans l'invisible. Sensible, empathique, il perçoit ce que les autres ne voient pas. Sa sensualité est enveloppante, presque onirique — il cherche la fusion, l'abolition des frontières. C'est un signe qui a besoin de tendresse et de douceur pour s'ouvrir pleinement.",
    ideal: [
      { sign: 'Cancer', reason: 'Deux Eaux fusionnelles — tendresse infinie, communion douce.' },
      { sign: 'Scorpion', reason: 'Intensité partagée, alchimie mystérieuse, engagement profond.' },
      { sign: 'Taureau', reason: 'Terre nourricière pour l\'Eau — cocon sensuel et rassurant.' },
    ],
  },
};

export const SIGN_LIST = Object.entries(ASTROSEXO_PROFILES).map(([id, data]) => ({ id, ...data }));
