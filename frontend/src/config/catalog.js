/**
 * Catalogue centralisé des lectures et outils Plume Astrale.
 * Utilisé par NavbarV2 (mega menu), NosLivres (vitrine) et éventuellement Homepage.
 *
 * Convention : garder l'ordre du plus phare/rentable au plus niche.
 */

export const LECTURES = [
  {
    key: 'natal',
    title: 'Thème Natal',
    tagline: '49 pages · 11 planètes décodées',
    price: '17,99€',
    to: '/theme-natal-luxe',
  },
  {
    key: 'kabbale',
    title: 'Arbre de Vie · Kabbale',
    tagline: '10 Sephiroth · 22 chemins hébraïques',
    price: '39€',
    to: '/kabbale',
  },
  {
    key: 'astrocarto',
    title: 'Astrocartographie',
    tagline: '7 lignes planétaires sur le monde',
    price: '49€',
    to: '/astrocartographie',
  },
  {
    key: 'karma',
    title: 'Karma & Destin',
    tagline: 'Ta lignée karmique décodée',
    price: '29€',
    to: '/karma-destin-pdf',
  },
  {
    key: 'numerologie',
    title: 'Numérologie sacrée',
    tagline: 'Chemin de vie + année personnelle',
    price: '29€',
    to: '/numerologie-pdf',
  },
  {
    key: 'karmique',
    title: 'Pack Karmique',
    tagline: '3 lectures réunies · offre écrin',
    price: '89€',
    to: '/pack-karmique',
    highlight: true,
  },
  {
    key: 'synastry',
    title: 'Astrologie relationnelle',
    tagline: 'Vos deux ciels croisés',
    price: '49€',
    to: '/synastrie',
  },
];

export const OUTILS = [
  { key: 'consultation', title: 'Consultation Soléna', tagline: 'Échange chat guidé par IA', to: '/outils/consultation' },
  { key: 'tarot', title: 'Tirage de tarot', tagline: '78 arcanes · plusieurs formats', to: '/outils/tarot' },
  { key: 'horoscope', title: 'Horoscope du jour', tagline: 'Guidance quotidienne · 12 signes', to: '/outils/horoscope' },
  { key: 'compatibilite', title: 'Compatibilité amoureuse', tagline: 'Deux prénoms, un aperçu', to: '/outils/compatibilite' },
  { key: 'rituel', title: 'Rituel du soir', tagline: 'Ancrage · lune du jour', to: '/outils/rituel' },
  { key: 'oracle', title: 'Oracle du jour', tagline: 'Une carte, une intention', to: '/outils/oracle' },
];

export const OUTILS_LABEL = 'Services complémentaires';
