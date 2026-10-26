/**
 * seoRoutes.js — Source unique de vérité pour les URLs SEO (SEO Audit Feb 2026).
 *
 * Trois exports :
 *   • VALID_ROUTES       — URLs canoniques, 200, indexables, à inclure dans sitemap.xml
 *   • REDIRECT_MAP       — URLs 301 → URL canonique (consommé par nginx + script sitemap)
 *   • HOROSCOPE_SIGNS    — 12 signes valides (consommé par 404 fallback)
 *
 * NB — Direction canonique : les routes réelles (composants React) vivent sous
 * `/services/<tool>` (Numerologie, Oracle, Rituel…). Les URL courtes et legacy
 * sont des redirections. On garde cette direction (non inversée) pour éviter de
 * casser les liens existants ; la cohérence SEO est assurée par `canonicalPath`
 * dans components/SEO.js et par les 301 nginx du deploy/nginx-frontend.conf.
 */

export const HOROSCOPE_SIGNS = [
  'belier', 'taureau', 'gemeaux', 'cancer', 'lion', 'vierge',
  'balance', 'scorpion', 'sagittaire', 'capricorne', 'verseau', 'poissons',
];

/**
 * URLs 301 permanentes (consommé par deploy/nginx-frontend.conf).
 *   Clef   : chemin source (exact match, pas de glob)
 *   Valeur : chemin destination absolue (sans domaine)
 */
export const REDIRECT_MAP = {
  // ── Correction des JS redirects → 301 serveur ──
  '/temoignage': '/temoignages',
  '/home-experience-v3': '/',
  '/compatibilite-amoureuse': '/services/compatibilite',

  // ── Doublons éditoriaux ──
  '/politique-de-confidentialite': '/confidentialite',
  '/privacy': '/confidentialite',
  '/nos-livres': '/livres',
  '/livre': '/livres',
  '/theme-natal-luxe': '/theme-natal',
  '/cercle': '/communaute',
  '/cercle-quotidien': '/communaute',
  '/cercle-dashboard': '/communaute',

  // ── Produits renommés ──
  '/kabbale': '/voyage-karmique',
  '/karma-destin': '/voyage-karmique',
  '/karma-destin-pdf': '/voyage-karmique',
  '/fenetre-rencontre-pdf': '/rencontres-astrales',
  '/premium': '/acheter-credits',
  '/premium/decouvrir': '/acheter-credits',
  '/premium/experience': '/acheter-credits',

  // ── Routes legacy ──
  '/tirage-tarot': '/services/tarot',
  '/tarot': '/services/tarot',
  '/compatibilite': '/services/compatibilite',
  '/mon-rituel': '/services/rituel',
  '/chat-astral': '/services/consultation',
  '/consultation': '/services/consultation',
  '/revolution-solaire': '/services/revolution-solaire',
  '/love-languages': '/services/love-languages',
  '/oracle': '/services/oracle',
  '/energie': '/services/energie',
  '/astrosexo': '/services/astrosexo',

  // ── /outils/* → /services/* ──
  '/outils/theme-natal': '/services/theme-natal',
  '/outils/tarot': '/services/tarot',
  '/outils/tarot/oui-non': '/services/tarot/oui-non',
  '/outils/tarot/croix-celtique': '/services/tarot/croix-celtique',
  '/outils/tarot/amour': '/services/tarot/amour',
  '/outils/horoscope': '/services/horoscope',
  '/outils/numerologie': '/services/numerologie',
  '/outils/archetype': '/services/archetype',
  '/outils/compatibilite': '/services/compatibilite',
  '/outils/revolution-solaire': '/services/revolution-solaire',
  '/outils/oracle': '/services/oracle',
  '/outils/energie': '/services/energie',
  '/outils/rituel': '/services/rituel',
  '/outils/consultation': '/services/consultation',
  '/outils/astrosexo': '/services/astrosexo',
  '/outils/love-languages': '/services/love-languages',
};

/**
 * URLs canoniques à inclure dans sitemap.xml.
 * `lastmod` sera calculé dynamiquement par scripts/generate_sitemap.py.
 */
export const VALID_ROUTES = [
  // ─── Accueil et pages éditoriales ───
  { path: '/', priority: 1.0, changefreq: 'weekly' },
  { path: '/decouvrir', priority: 0.9, changefreq: 'weekly' },
  { path: '/manifesto', priority: 0.75, changefreq: 'monthly' },
  { path: '/cercle-solena', priority: 0.95, changefreq: 'weekly' },
  { path: '/barometre-2026', priority: 0.8, changefreq: 'monthly' },
  { path: '/communaute', priority: 0.7, changefreq: 'weekly' },
  { path: '/faq', priority: 0.6, changefreq: 'monthly' },
  { path: '/contact', priority: 0.5, changefreq: 'yearly' },
  { path: '/charte-de-confiance', priority: 0.5, changefreq: 'yearly' },
  { path: '/notre-cadre', priority: 0.5, changefreq: 'yearly' },

  // ─── Produits phares (sales pages) ───
  { path: '/livres', priority: 0.9, changefreq: 'weekly' },
  { path: '/theme-natal', priority: 0.95, changefreq: 'weekly' },
  { path: '/theme-natal-pdf', priority: 0.85, changefreq: 'weekly' },
  { path: '/edition-reliee', priority: 0.9, changefreq: 'weekly' },
  { path: '/composer', priority: 0.9, changefreq: 'weekly' },
  { path: '/synastrie', priority: 0.85, changefreq: 'weekly' },
  { path: '/voyage-karmique', priority: 0.85, changefreq: 'weekly' },
  { path: '/astrocartographie', priority: 0.8, changefreq: 'monthly' },
  { path: '/pack-karmique', priority: 0.8, changefreq: 'monthly' },
  { path: '/rencontres-astrales', priority: 0.8, changefreq: 'monthly' },
  { path: '/numerologie-pdf', priority: 0.8, changefreq: 'monthly' },

  // ─── Services canoniques (/services/*) ───
  { path: '/services/theme-natal', priority: 0.85, changefreq: 'weekly' },
  { path: '/services/tarot', priority: 0.8, changefreq: 'weekly' },
  { path: '/services/tarot/oui-non', priority: 0.75, changefreq: 'weekly' },
  { path: '/services/tarot/croix-celtique', priority: 0.7, changefreq: 'weekly' },
  { path: '/services/tarot/amour', priority: 0.7, changefreq: 'weekly' },
  { path: '/services/numerologie', priority: 0.8, changefreq: 'weekly' },
  { path: '/services/compatibilite', priority: 0.8, changefreq: 'weekly' },
  { path: '/services/archetype', priority: 0.75, changefreq: 'monthly' },
  { path: '/services/revolution-solaire', priority: 0.75, changefreq: 'monthly' },
  { path: '/services/oracle', priority: 0.75, changefreq: 'weekly' },
  { path: '/services/energie', priority: 0.75, changefreq: 'monthly' },
  { path: '/services/rituel', priority: 0.75, changefreq: 'weekly' },
  { path: '/services/consultation', priority: 0.75, changefreq: 'weekly' },
  { path: '/services/astrosexo', priority: 0.7, changefreq: 'monthly' },
  { path: '/services/love-languages', priority: 0.7, changefreq: 'monthly' },

  // ─── Outils éditoriaux ───
  { path: '/tarologie', priority: 0.8, changefreq: 'weekly' },
  { path: '/tarot-oui-non', priority: 0.75, changefreq: 'weekly' },
  { path: '/quotidien', priority: 0.7, changefreq: 'daily' },
  { path: '/experience', priority: 0.7, changefreq: 'weekly' },
  { path: '/temoignages', priority: 0.7, changefreq: 'monthly' },
  { path: '/bibliotheque', priority: 0.65, changefreq: 'monthly' },

  // ─── Horoscopes (12 signes, SANS les 24 week/month qui sont duplicate) ───
  ...HOROSCOPE_SIGNS.map(s => ({
    path: `/horoscope/${s}`,
    priority: 0.75,
    changefreq: 'weekly',
  })),
  { path: '/horoscope', priority: 0.85, changefreq: 'weekly' },

  // ─── Blog (hub) ───
  { path: '/blog', priority: 0.85, changefreq: 'weekly' },
  // Les slugs d'articles sont ajoutés dynamiquement par generate_sitemap.py.
];

/**
 * Pages explicitement exclues du sitemap (noindex, privées, succès de commande).
 */
export const EXCLUDED_FROM_SITEMAP = [
  '/cgv',
  '/mentions-legales',
  '/confidentialite',
  '/panier',
  '/mon-compte',
  '/mon-accueil',
  '/admin',
  '/dashboard',
  '/inscription',
  '/connexion',
  '/formulaire',
  '/apercu',
  '/choix',
  '/resultats',
  '/paiement',
  '/commande',
  '/acheter-credits',
  '/desabonnement',
  '/mot-de-passe-oublie',
  '/reinitialiser-mot-de-passe',
  '/relecture',
  '/credits',
  '/credits/succes',
  // Toute route contenant '/succes' est automatiquement exclue.
];
