/**
 * Registre des articles blog · SEO P2 (concours 2026-02).
 *
 * Les articles réels sont servis par Soro (widget embarqué), mais leurs
 * URLs paramétrées `/blog?post=slug` étaient invisibles pour Google
 * (canonical pointait à la home + H1 partagé avec /blog). Solution :
 *   1. Route dédiée /blog/:slug (frontend React Router)
 *   2. Chaque article a title/description/canonical/H1 unique
 *   3. Sitemap XML étendu avec les 9 URLs propres
 *   4. Redirection depuis /blog?post=slug → /blog/slug
 *
 * NB : Les meta et le H1 sont définis en dur ici parce que la source
 * Soro ne les expose pas via API publique.
 */

export const BLOG_ARTICLES = [
  {
    slug: 'calculer-son-chemin-de-vie-avec-precision',
    title: 'Calculer son chemin de vie avec précision',
    description: "Comment calculer votre chemin de vie en numérologie sans se tromper, et ce que ce nombre révèle vraiment de votre parcours.",
    tag: 'Numérologie',
    date: '2026-01-12',
    excerpt: "Une méthode claire pour obtenir votre chemin de vie exact, expliquée pas à pas — et ce que chaque nombre invite à comprendre.",
  },
  {
    slug: 'interpreter-venus-en-astrologie',
    title: 'Interpréter Vénus en astrologie — au-delà du romantisme',
    description: "Vénus décrit votre rapport à l'amour, à la beauté, aux valeurs. Un guide clair pour lire cette planète dans votre thème natal.",
    tag: 'Astrologie',
    date: '2026-01-05',
    excerpt: "Vénus ne raconte pas seulement vos histoires d'amour. Elle éclaire comment vous aimez, comment vous appréciez, ce qui vous ressemble.",
  },
  {
    slug: 'comprendre-le-retour-de-saturne',
    title: 'Comprendre le retour de Saturne (29-30 ans)',
    description: "Le retour de Saturne autour de 29-30 ans est un des grands rendez-vous du parcours astral. Ce qu'il apporte, ce qu'il demande.",
    tag: 'Cycles',
    date: '2025-12-18',
    excerpt: "Vers 29-30 ans, un moment charnière : Saturne revient à sa position de naissance. Comprendre ce cycle change la manière de le traverser.",
  },
  {
    slug: 'theme-natal-vocation-professionnelle',
    title: 'Votre thème natal peut-il révéler votre vocation ?',
    description: "Comment lire les indications de vocation professionnelle dans un thème natal — Maison X, Milieu du Ciel, planètes actives.",
    tag: 'Thème natal',
    date: '2025-12-10',
    excerpt: "La Maison X et le Milieu du Ciel donnent des repères précieux sur votre orientation professionnelle. Ce que votre thème raconte.",
  },
  {
    slug: 'compatibilite-amoureuse-selon-theme-natal',
    title: 'Compatibilité amoureuse selon le thème natal — au-delà des signes',
    description: "La compatibilité astrologique ne se lit pas dans les signes solaires. Comment évaluer une véritable synastrie entre deux thèmes.",
    tag: 'Relations',
    date: '2025-12-02',
    excerpt: "Oublier les 'signes compatibles' des magazines : la vraie synastrie regarde Vénus, Mars, la Lune et les aspects entre deux thèmes.",
  },
  {
    slug: 'signification-des-maisons-astrologiques',
    title: 'Les 12 maisons astrologiques expliquées simplement',
    description: "Un tour clair des 12 maisons du thème natal : ce que chacune décrit dans votre vie quotidienne et intérieure.",
    tag: 'Astrologie',
    date: '2025-11-24',
    excerpt: "Les maisons astrologiques cartographient les grandes zones de votre existence : couple, travail, foyer, transformation, spiritualité.",
  },
  {
    slug: 'comment-connaitre-son-ascendant-astrologique',
    title: "Comment connaître son ascendant astrologique",
    description: "Trouver son ascendant à partir de sa date, heure et lieu de naissance. Pourquoi ce point du ciel est essentiel dans votre thème natal.",
    tag: 'Thème natal',
    date: '2025-11-15',
    excerpt: "L'ascendant représente la façon dont vous entrez dans le monde. Voici comment le calculer précisément et ce qu'il change à votre lecture.",
  },
  {
    slug: 'previsions-astrologiques-personnalisees-2026',
    title: 'Prévisions astrologiques personnalisées 2026 : les cycles à venir',
    description: "Les grands cycles astrologiques de 2026 — Jupiter, Saturne, Uranus — et comment les lire selon votre thème natal personnel.",
    tag: 'Cycles',
    date: '2025-11-04',
    excerpt: "2026 apporte des transits collectifs importants. Comment les lire personnellement à partir de votre thème pour anticiper vos périodes.",
  },
  {
    slug: 'theme-astral-personnalise-gratuit',
    title: 'Un thème astral personnalisé, gratuit — vraiment ?',
    description: "Que peut-on vraiment obtenir d'un thème astral gratuit, et à partir de quel niveau de lecture il vaut mieux passer à une analyse experte.",
    tag: 'Thème natal',
    date: '2025-10-22',
    excerpt: "Les thèmes natals gratuits en ligne donnent une bonne base. Voici où ils s'arrêtent — et ce qu'une lecture experte peut réellement ajouter.",
  },
];

export function getArticleBySlug(slug) {
  return BLOG_ARTICLES.find((a) => a.slug === slug) || null;
}
