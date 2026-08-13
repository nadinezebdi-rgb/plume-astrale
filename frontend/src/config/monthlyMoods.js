/**
 * L'humeur du mois — contenu SEO dynamique pour /horoscope/:sign.
 *
 * Objectif : Googlebot revient tous les 30 jours parce que la page CHANGE
 * (le mois affiché varie). Une "humeur du mois" universelle est modulée
 * par l'élément du signe (Feu/Terre/Air/Eau) pour donner un texte cohérent
 * mais suffisamment personnel pour chaque signe.
 *
 * 12 mois × 4 éléments = 48 accents uniques × 12 signes = ~48 lectures
 * distinctes chaque mois (chaque signe reçoit un texte propre à son élément).
 *
 * Vocabulaire : cycles, périodes, comprendre — pas de "prédiction", pas de
 * "voyance", pas de "destin".
 */

const MONTH_NAMES = [
  'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
];

// 12 climats universels — un par mois.
const UNIVERSAL_CLIMATES = [
  { // Janvier
    title: 'Un mois pour poser des fondations',
    body: 'Le début d\'année invite à la clarté. Ce n\'est pas le moment de tout révolutionner — c\'est celui d\'écrire, doucement, ce que vous voulez que cette année porte pour vous.',
  },
  { // Février
    title: 'Un mois pour approfondir',
    body: 'Février resserre. On y regarde ce qui compte vraiment : les liens, les priorités, les gestes du quotidien. Une période idéale pour trier sans brusquer.',
  },
  { // Mars
    title: 'Un mois de bascule',
    body: 'L\'équinoxe rouvre l\'horizon. Ce mois-ci, quelque chose que vous portez depuis l\'hiver demande à voir le jour. Écoutez ce qui frémit — c\'est rarement anodin.',
  },
  { // Avril
    title: 'Un mois pour oser',
    body: 'Le printemps ne demande pas la perfection : il demande l\'élan. Une conversation reportée, un projet mis de côté, un pas simple à franchir — c\'est le mois pour.',
  },
  { // Mai
    title: 'Un mois pour incarner',
    body: 'Mai concrétise. Ce que vous avez semé en début d\'année prend forme, doucement. Cherchez la beauté dans les gestes ordinaires : ils portent plus que vous ne croyez.',
  },
  { // Juin
    title: 'Un mois pour relier',
    body: 'Juin ouvre l\'espace des rencontres et des retrouvailles. Les liens qui comptent se réactivent. Prenez le temps de choisir ceux à qui vous donnez le vôtre.',
  },
  { // Juillet
    title: 'Un mois pour respirer',
    body: 'L\'été invite au ralentissement. La pause n\'est pas une fuite — c\'est une méthode. Ce que vous laissez décanter maintenant reviendra plus juste ensuite.',
  },
  { // Août
    title: 'Un mois pour rêver plus grand',
    body: 'Août élargit la perspective. Prenez de la hauteur sur les six premiers mois : qu\'avez-vous appris ? qu\'aimeriez-vous transformer pour la rentrée ?',
  },
  { // Septembre
    title: 'Un mois pour se remettre en mouvement',
    body: 'La rentrée rassemble l\'énergie éparse de l\'été. Un cap se dessine à nouveau. Ne forcez rien — laissez le rythme naturel se réinstaller.',
  },
  { // Octobre
    title: 'Un mois pour trancher',
    body: 'Octobre confronte aux choix qu\'on a évités. Le mois demande de la clarté, pas du drame. Une décision posée maintenant libère beaucoup plus que vous n\'imaginez.',
  },
  { // Novembre
    title: 'Un mois pour se recentrer',
    body: 'Novembre invite à revenir à soi. Moins d\'agitation, plus d\'écoute intérieure. Ce que vous entendez dans le silence de ce mois éclaire souvent l\'année à venir.',
  },
  { // Décembre
    title: 'Un mois pour clore et intégrer',
    body: 'Décembre rassemble le fil de l\'année. Ce n\'est pas le moment des grands départs — c\'est celui des remerciements et de la préparation intérieure.',
  },
];

// Accents par élément — 12 mois × 4 éléments.
const ELEMENT_ACCENTS = {
  Feu: [
    'Pour vous, signe de Feu, la retenue est votre discipline du mois : posez un pas à la fois.',
    'Votre énergie de Feu gagne à s\'orienter vers l\'intime plutôt que le spectaculaire ce mois-ci.',
    'Le Feu se réveille avec l\'équinoxe : suivez l\'impulsion, mais choisissez sa direction.',
    'Votre nature de Feu aime les commencements — avril vous rend particulièrement à l\'aise.',
    'Le Feu apprend l\'incarnation en mai : passez de l\'idée au geste concret.',
    'En juin, votre Feu communique. C\'est le moment d\'exposer clairement ce que vous portez.',
    'Le Feu apprend le repos en juillet : ce n\'est pas une trahison de votre nature, c\'est sa maturation.',
    'Août redonne à votre Feu une vision large. Rêvez sans vous censurer.',
    'Septembre canalise votre Feu vers un cap précis. Ne l\'éparpillez pas.',
    'Votre Feu tranche mieux qu\'aucun autre en octobre. Utilisez ce clair-obscur.',
    'Novembre demande à votre Feu la nuance. Contenance ne veut pas dire renoncement.',
    'Décembre veut de votre Feu une chaleur qui rassemble, plus qu\'une flamme qui perce.',
  ],
  Terre: [
    'Pour vous, signe de Terre, janvier ressemble à un début parfait : lente, méthodique, ancrée.',
    'Votre Terre affine ses priorités en février. Ce que vous décidez de garder aura du poids.',
    'La Terre s\'ouvre à la vibration du printemps en mars : laissez la sève monter.',
    'Avril demande à votre Terre un peu de spontanéité. Sortez d\'un plan pour voir ce qui apparaît.',
    'Mai est votre mois par excellence, signe de Terre : récoltez ce que vous avez patiemment cultivé.',
    'Juin invite votre Terre à s\'ouvrir aux liens. Ne restez pas seul avec vos réussites.',
    'La Terre se régénère en juillet : mangez lentement, marchez sans but, dormez profondément.',
    'Août réoxygène votre Terre. Autorisez-vous une pensée plus ample que le quotidien.',
    'Votre Terre reprend son sillon en septembre. Elle sait exactement quoi faire.',
    'Octobre récolte vraiment pour vous. Ce que vous décidez porte des fruits durables.',
    'Novembre est un mois riche pour votre Terre : elle sait bien vieillir ce qui compte.',
    'Décembre demande à votre Terre de se laisser inspirer. Écoutez plutôt qu\'organisez.',
  ],
  Air: [
    'Votre Air structure ses idées en janvier. Écrivez plus que d\'habitude.',
    'Février resserre les liens et vous invite, signe d\'Air, à choisir la profondeur.',
    'L\'Air adore mars : les échanges se multiplient. Sélectionnez ceux qui nourrissent.',
    'En avril, votre Air passe de la pensée à l\'action. Ne restez pas au stade du concept.',
    'Mai demande à votre Air un peu de patience. La lenteur ouvre parfois de nouvelles idées.',
    'Juin est votre mois : votre Air relie, présente, ouvre des ponts. Profitez-en.',
    'L\'Air prend de la hauteur en juillet. Un voyage, un livre, une pause changent tout.',
    'Août élargit encore votre horizon d\'Air. Osez les questions qui font vraiment bouger.',
    'La rentrée met votre Air en mouvement. Les projets à plusieurs vous portent particulièrement.',
    'Octobre demande à votre Air une décision claire — pas une nouvelle option.',
    'Novembre invite votre Air à écouter plus qu\'à formuler. Une intuition mérite d\'être suivie.',
    'Décembre récolte les idées semées : notez tout ce qui remonte, même flou.',
  ],
  Eau: [
    'Janvier apaise votre Eau. Suivez le rythme intérieur, il porte des choses justes.',
    'Février creuse pour vous. Ce que vous ressentez ce mois-ci révèle ce qui compte vraiment.',
    'L\'Eau se renouvelle avec mars. Les émotions bougent — accompagnez-les sans les figer.',
    'Avril demande à votre Eau du courage. Une émotion prête à se dire mérite un espace clair.',
    'En mai, votre Eau s\'incarne. Traduisez le ressenti en geste concret ou en art.',
    'Juin ouvre votre Eau aux autres. Les liens du cœur reprennent de la place.',
    'Juillet est votre mois par excellence, signe d\'Eau : la lenteur régénère profondément.',
    'Août prolonge votre Eau vers l\'imaginaire. Rêvez, écrivez, dessinez.',
    'Septembre demande à votre Eau de reprendre un cap sans se disperser dans l\'émotion.',
    'Octobre confronte vos zones d\'ombre. Votre Eau sait s\'y aventurer avec grâce.',
    'Novembre est riche pour votre Eau : intuition, guidance, silences habités.',
    'Décembre invite votre Eau à intégrer, remercier, préparer l\'année à venir doucement.',
  ],
};

/**
 * Renvoie l'humeur du mois pour un signe donné.
 * @param {object} sign - Un objet issu de ZODIAC_SIGNS (doit avoir .element)
 * @param {Date} [date] - Optionnel, sinon date courante.
 * @returns {{ monthName: string, monthNumber: number, title: string, body: string, accent: string }}
 */
export function getMonthlyMood(sign, date) {
  const now = date instanceof Date ? date : new Date();
  const monthIndex = now.getMonth(); // 0..11
  const climate = UNIVERSAL_CLIMATES[monthIndex];
  const element = (sign && sign.element) || 'Air';
  const accentList = ELEMENT_ACCENTS[element] || ELEMENT_ACCENTS.Air;
  const accent = accentList[monthIndex];
  return {
    monthName: MONTH_NAMES[monthIndex],
    monthNumber: monthIndex + 1,
    title: climate.title,
    body: climate.body,
    accent,
  };
}
