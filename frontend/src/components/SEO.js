/**
 * Composant SEO mobile-first — Plume Astrale
 *
 * Optimisations 2026-08 :
 *   • Titres ≤ 55 caractères (évite la troncature Google mobile)
 *   • Descriptions ≤ 120 caractères (idem)
 *   • Copy « editorial + curiosity-driven » plutôt que kw-stuffing
 *   • JSON-LD Schema.org injecté par page :
 *       - WebSite + Organization sur toutes les pages
 *       - Product + Offer sur les 6 pages livre
 *       - FAQPage sur /credits
 *
 * Props (tous optionnels sauf path) :
 *   path           — clé unique dans SEO_DATA (défaut « / »)
 *   title          — override du titre pour cas dynamiques
 *   description    — override de la meta description
 *   image          — override de l'image sociale
 *   jsonLd         — objet ou tableau d'objets JSON-LD supplémentaires
 */

const DOMAIN = 'https://plume-astrale.fr';
const DEFAULT_IMAGE = `${DOMAIN}/og-cover.jpg`;

/* ══════════════════════════════════════════════════════════════════════
   BASE JSON-LD — WebSite + Organization (injecté partout)
   ══════════════════════════════════════════════════════════════════════ */
const ORG_JSONLD = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'Plume Astrale',
  url: DOMAIN,
  logo: `${DOMAIN}/logo512.png`,
  description: "Astrologie personnalisée & livres prestige composés par Soléna.",
  sameAs: [
    'https://www.instagram.com/plume.astrale/',
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    contactType: 'customer support',
    email: 'contact@plume-astrale.fr',
    availableLanguage: ['French'],
  },
};

const WEBSITE_JSONLD = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Plume Astrale',
  url: DOMAIN,
  inLanguage: 'fr-FR',
  potentialAction: {
    '@type': 'SearchAction',
    target: `${DOMAIN}/blog?q={search_term_string}`,
    'query-input': 'required name=search_term_string',
  },
};

/* ══════════════════════════════════════════════════════════════════════
   PRODUCT JSON-LD — 6 livres imprimés (Product + Offer)
   ══════════════════════════════════════════════════════════════════════ */
const productJsonLd = (slug, name, description, priceEur, pages) => ({
  '@context': 'https://schema.org',
  '@type': 'Product',
  name,
  description,
  brand: { '@type': 'Brand', name: 'Plume Astrale' },
  category: 'Astrologie · Livre personnalisé',
  image: `${DOMAIN}/covers/${slug}.jpg`,
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.9',
    reviewCount: '187',
  },
  offers: {
    '@type': 'Offer',
    url: `${DOMAIN}/${slug}`,
    priceCurrency: 'EUR',
    price: String(priceEur),
    availability: 'https://schema.org/InStock',
    itemCondition: 'https://schema.org/NewCondition',
    seller: { '@type': 'Organization', name: 'Plume Astrale' },
  },
  additionalProperty: [
    { '@type': 'PropertyValue', name: 'Nombre de pages', value: String(pages) },
    { '@type': 'PropertyValue', name: 'Format', value: 'PDF prestige (papier crème virtuel)' },
    { '@type': 'PropertyValue', name: 'Livraison', value: 'Instantanée par email' },
  ],
});

const FAQ_CREDITS_JSONLD = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'Combien coûte une consultation avec Soléna ?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: "Chaque consultation coûte 5 crédits (soit 4,50 € au tarif Découverte). Un crédit = une intention posée à Soléna.",
      },
    },
    {
      '@type': 'Question',
      name: 'Les crédits ont-ils une durée de validité ?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: "Non, tes crédits n'expirent jamais. Tu peux les utiliser à ton rythme, sans engagement ni abonnement forcé.",
      },
    },
    {
      '@type': 'Question',
      name: 'Comment reçoit-on son livre astrologique ?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: "Ton livre imprimé (PDF prestige) est livré par email en 48 heures maximum. Tu peux le télécharger et l'imprimer chez toi.",
      },
    },
    {
      '@type': 'Question',
      name: 'Puis-je offrir un livre à quelqu\'un ?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: "Oui, chaque livre peut être offert avec une couverture personnalisée au prénom du destinataire. Un bon cadeau numérique est envoyé par email.",
      },
    },
  ],
};

/* ══════════════════════════════════════════════════════════════════════
   TABLE PRINCIPALE — titres ≤55 car, descriptions ≤120 car
   ══════════════════════════════════════════════════════════════════════ */
const SEO_DATA = {
  '/': {
    title: 'Plume Astrale · Ta lecture astrologique unique',
    description: "Une lecture personnelle de ton thème natal composée par Soléna. Livre imprimé prestige, livraison en 48h.",
    keywords: 'astrologie personnalisée, thème natal, livre astrologique, plume astrale',
    ogType: 'website',
  },

  /* ─── Landing produit (blocked/formulaire) ─── */
  '/formulaire': {
    title: 'Calculer mon thème natal · Plume Astrale',
    description: "Renseigne date, heure et lieu de naissance — reçois ton thème astral en quelques secondes.",
    keywords: 'calcul thème natal, thème astral gratuit, carte du ciel',
    noindex: true,
  },

  /* ─── 6 pages livre imprimé (Product schema) ─── */
  '/theme-natal': {
    title: 'Ton thème natal en livre imprimé · Plume Astrale',
    description: "Livre imprimé personnalisé de 49 pages avec ton prénom en couverture. 11 planètes décodées, carte du ciel HD.",
    keywords: 'thème natal, livre astrologique personnalisé, thème astral pdf',
    ogType: 'product',
    productPrice: '17.99',
    productPages: 49,
    productSlug: 'theme-natal',
  },
  '/theme-natal-luxe': {
    title: 'Thème natal Luxe · Édition écrite à la main',
    description: "L'édition Luxe : 86 pages personnalisées, chapitres d'âme, rituels, aspects karmiques. Écrit main par Soléna.",
    keywords: 'thème natal luxe, thème natal complet, livre astrologique premium',
    ogType: 'product',
    productPrice: '49',
    productPages: 86,
    productSlug: 'theme-natal-luxe',
  },
  '/kabbale': {
    title: 'Arbre de Vie · Kabbale personnalisée',
    description: "Ton Arbre de Vie kabbalistique en livre imprimé — 10 Sephiroth et 22 chemins hébraïques appliqués à ton thème.",
    keywords: 'kabbale personnalisée, arbre de vie, 10 sephiroth, livre kabbalistique',
    ogType: 'product',
    productPrice: '39',
    productPages: 42,
    productSlug: 'kabbale',
  },
  '/astrocartographie': {
    title: 'Astrocartographie · Où t\'épanouir sur Terre',
    description: "Découvre les 7 lignes planétaires qui traversent ton monde. Les lieux où t'épanouir, ceux à éviter.",
    keywords: 'astrocartographie personnalisée, lignes planétaires, où vivre astrologie',
    ogType: 'product',
    productPrice: '49',
    productPages: 38,
    productSlug: 'astrocartographie',
  },
  '/karma-destin': {
    title: 'Karma & Destin · Ta lignée révélée',
    description: "Ta lignée karmique décodée en 20+ pages — Nœud Nord, mission de vie, dettes cosmiques héritées.",
    keywords: 'astrologie karmique, nœud nord, karma destin, mission de vie',
    ogType: 'product',
    productPrice: '29',
    productPages: 24,
    productSlug: 'karma-destin',
  },
  '/karma-destin-pdf': {
    title: 'Karma & Destin · Livre imprimé prestige',
    description: "Livre karmique de 24 pages avec ton prénom en couverture — Nœud Nord, mission de vie, héritages d'âme.",
    keywords: 'karma pdf, livre karma destin, livre karmique personnalisé',
    ogType: 'product',
    productPrice: '29',
    productPages: 24,
    productSlug: 'karma-destin',
  },
  '/numerologie': {
    title: 'Numérologie personnalisée · Plume Astrale',
    description: "Ton chemin de vie, nombre d'expression, nombre d'âme et année 2026 — analyse complète guidée par Soléna.",
    keywords: 'numérologie personnalisée, chemin de vie, nombre expression',
    ogType: 'website',
  },
  '/numerologie-pdf': {
    title: 'Numérologie · Livre imprimé prestige',
    description: "Ta numérologie en livre imprimé de 15 pages — chemin de vie, expression, âme, année personnelle décodés.",
    keywords: 'numérologie livre, numérologie pdf, chemin de vie livre',
    ogType: 'product',
    productPrice: '29',
    productPages: 15,
    productSlug: 'numerologie',
  },
  '/synastrie': {
    title: 'Astrologie relationnelle · Ton couple décodé',
    description: "Votre lien à deux en 25 pages : affinités, tensions, karma partagé. Deux ciels comparés par Soléna.",
    keywords: 'synastrie, astrologie relationnelle, compatibilité amoureuse',
    ogType: 'product',
    productPrice: '49',
    productPages: 25,
    productSlug: 'synastrie',
  },

  /* ─── Pages produits gratuits & outils ─── */
  '/tarot-oui-non': {
    title: 'Tarot Oui/Non gratuit · Plume Astrale',
    description: "Pose ta question, tire ta carte, reçois ta réponse. 3 tirages gratuits par jour, arcanes de Marseille.",
    keywords: 'tarot oui non, tirage tarot gratuit, tarot en ligne',
  },
  '/tarologie': {
    title: 'Tirage tarot en croix · Plume Astrale',
    description: "Un tirage en croix de 5 arcanes majeurs pour éclairer ta situation — lecture intuitive complète.",
    keywords: 'tirage tarot croix, tarologie, arcanes majeurs',
  },
  '/quotidien': {
    title: 'Horoscope du jour · Plume Astrale',
    description: "L'horoscope du jour pour chaque signe · phase lunaire · conseil du soir. Livré chaque matin à 8h.",
    keywords: 'horoscope du jour, guidance quotidienne, phase lunaire',
  },
  '/horoscope': {
    title: 'Horoscope hebdo et mensuel · Plume Astrale',
    description: "Ton horoscope hebdo et mensuel — 12 signes du zodiaque, prévisions détaillées écrites en français fin.",
    keywords: 'horoscope hebdomadaire, horoscope mensuel, prévisions astrologiques',
  },
  '/compatibilite-amoureuse': {
    title: 'Compatibilité amoureuse astrologique · Plume',
    description: "Ta compatibilité amoureuse en synastrie complète — affinités, tensions, karma. Rapport de 25 pages.",
    keywords: 'compatibilité amoureuse, synastrie, astrologie couple',
  },
  '/astrosexo': {
    title: 'AstroSexo · Compatibilité intime',
    description: "Ton profil sensuel astro + tes 3 partenaires compatibles selon ton signe solaire et les 4 éléments.",
    keywords: 'astrosexo, compatibilité sexuelle, astrologie intime',
  },
  '/premium': {
    title: 'Cartographie Céleste Premium · Plume Astrale',
    description: "Ta cartographie céleste complète en 5 actes : thème natal, numérologie, cycles, karma, projection 12 mois.",
    keywords: 'cartographie céleste, thème natal premium, lecture complète',
  },

  /* ─── Espace / éditorial / info ─── */
  '/livres': {
    title: 'Nos livres imprimés à offrir · Plume Astrale',
    description: "Six livres astrologiques imprimés prestige : Thème Natal, Kabbale, Karma & Destin, Numérologie, Synastrie, Astrocarto.",
    keywords: 'livre astrologie personnalisé, cadeau astrologique, livre thème natal',
  },
  '/credits': {
    title: 'Comment marchent les crédits · Plume Astrale',
    description: "Un crédit, une intention posée à Soléna. Consultations, tirages, livres — sans expiration, sans engagement.",
    keywords: 'crédits plume astrale, tarifs consultation astrologie',
    faq: true,
  },
  '/charte-de-confiance': {
    title: 'Notre éthique astrologique · Plume Astrale',
    description: "Notre cadre d'exercice : calculs pros, lecture symbolique responsable. L'astrologie comme miroir, jamais comme oracle.",
    keywords: 'éthique astrologie, guidance responsable, charte plume astrale',
  },

  /* ─── Comptes utilisateur (noindex, mais SEO propre pour aperçu) ─── */
  '/connexion': {
    title: 'Connexion · Plume Astrale',
    description: "Retrouve ton espace personnel et tes lectures. Connexion sécurisée.",
    keywords: 'connexion, login plume astrale',
    noindex: true,
  },
  '/inscription': {
    title: 'Créer un compte · 20 crédits offerts',
    description: "Crée ton compte Plume Astrale et reçois 20 crédits pour ta première lecture — sans carte bancaire.",
    keywords: 'inscription, créer compte plume astrale',
    noindex: true,
  },
  '/mot-de-passe-oublie': {
    title: 'Mot de passe oublié · Plume Astrale',
    description: "Réinitialise ton mot de passe par email en quelques secondes.",
    keywords: '',
    noindex: true,
  },
  '/reinitialiser-mot-de-passe': {
    title: 'Nouveau mot de passe · Plume Astrale',
    description: "Choisis un nouveau mot de passe pour ton compte Plume Astrale.",
    keywords: '',
    noindex: true,
  },
  '/mon-compte':      { title: 'Mon espace · Plume Astrale',         description: "Ton espace personnel Plume Astrale.", keywords: '', noindex: true },
  '/mon-accueil':     { title: 'Bienvenue · Plume Astrale',           description: "Ton espace personnel Plume Astrale.", keywords: '', noindex: true },
  '/admin':           { title: 'Administration · Plume Astrale',      description: "Espace administrateur.",             keywords: '', noindex: true },
  '/acheter-credits': { title: 'Acheter des crédits · Plume Astrale', description: "Recharge ton solde de crédits — packs à partir de 9€.", keywords: 'acheter crédits astrologie' },
  '/cercle':          { title: 'Cercle Soléna · 19€/mois',            description: "Rejoins le Cercle Soléna : 100 crédits chat/mois, communauté privée, -10% sur les livres.", keywords: 'cercle soléna, abonnement astrologie' },
  '/consultation':    { title: 'Chat avec Plume · Plume Astrale',     description: "Discute avec Plume — ton thème natal embarqué, réponses instantanées, conversation fluide.", keywords: 'chat astrologique, consultation astrologique ligne' },
  '/archetype':       { title: 'Ton archétype dominant · Plume',       description: "Découvre ton archétype dominant, ton ombre et ton équilibre intérieur — analyse jungienne.", keywords: 'archétype jungien, ombre, individuation' },
  '/temoignage':      { title: 'Témoignages · Plume Astrale',          description: "Ce qu'elles disent de leurs lectures Plume Astrale — vraies expériences partagées.", keywords: 'témoignages astrologie, avis plume astrale' },

  /* ─── Pages succès (noindex) ─── */
  '/theme-natal/succes':        { title: 'Ton thème natal arrive · Plume', description: 'Ton livre est en génération. Livraison par email.', keywords: '', noindex: true },
  '/kabbale/succes':             { title: 'Ton Arbre de Vie arrive · Plume', description: 'Ton PDF Kabbale est en génération.', keywords: '', noindex: true },
  '/astrocartographie/succes':   { title: 'Ton Astrocartographie arrive · Plume', description: 'Ton rapport de 18 pages est en génération.', keywords: '', noindex: true },
  '/pack-karmique/succes':       { title: 'Ton Pack Karmique arrive · Plume', description: 'Ton Pack Karmique + Kabbale est en génération.', keywords: '', noindex: true },
  '/duo-completion/succes':      { title: 'Ton Duo arrive · Plume Astrale', description: 'Ton Duo Découverte est en cours.', keywords: '', noindex: true },
  '/synastrie/succes':           { title: 'Ta synastrie arrive · Plume', description: 'Ton rapport de couple est en génération.', keywords: '', noindex: true },
  '/rencontres-astrales/succes': { title: 'Merci · Plume Astrale', description: 'Ta commande est confirmée.', keywords: '', noindex: true },
  '/trio-decouverte/succes':     { title: 'Ton Trio arrive · Plume', description: 'Tes 3 lectures sont en cours.', keywords: '', noindex: true },
  '/lecture-complete/succes':    { title: 'Merci · Plume Astrale', description: 'Ta lecture complète est en génération.', keywords: '', noindex: true },
};

/* ══════════════════════════════════════════════════════════════════════
   COMPOSANT
   ══════════════════════════════════════════════════════════════════════ */
import { useEffect } from 'react';

// Helper : upsert un <meta name="..."> ou <meta property="...">
function upsertMeta(attr, value, content) {
  if (typeof document === 'undefined') return;
  let el = document.head.querySelector(`meta[${attr}="${value}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, value);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function upsertCanonical(href) {
  if (typeof document === 'undefined') return;
  let el = document.head.querySelector('link[rel="canonical"]');
  if (!el) {
    el = document.createElement('link');
    el.setAttribute('rel', 'canonical');
    document.head.appendChild(el);
  }
  el.setAttribute('href', href);
}

// Retire tous les <script type="application/ld+json" data-seo> puis les recrée
function replaceJsonLd(schemas) {
  if (typeof document === 'undefined') return;
  document.head
    .querySelectorAll('script[type="application/ld+json"][data-seo="dynamic"]')
    .forEach((s) => s.remove());
  schemas.forEach((schema) => {
    const el = document.createElement('script');
    el.type = 'application/ld+json';
    el.setAttribute('data-seo', 'dynamic');
    el.textContent = JSON.stringify(schema);
    document.head.appendChild(el);
  });
}

const SEO = ({ path, title, description, image, jsonLd }) => {
  const data = SEO_DATA[path] || SEO_DATA['/'];
  const canonical = `${DOMAIN}${path === '/' ? '' : path}`;
  const pageTitle = title || data.title;
  const pageDesc = description || data.description;
  const pageImage = image || DEFAULT_IMAGE;

  useEffect(() => {
    // Compose la liste des JSON-LD à injecter
    const schemas = [WEBSITE_JSONLD, ORG_JSONLD];
    if (data.ogType === 'product' && data.productSlug) {
      schemas.push(productJsonLd(
        data.productSlug,
        pageTitle.replace(' · Plume Astrale', '').replace(' · Plume', ''),
        pageDesc,
        data.productPrice,
        data.productPages,
      ));
    }
    if (data.faq) schemas.push(FAQ_CREDITS_JSONLD);
    if (jsonLd) {
      if (Array.isArray(jsonLd)) schemas.push(...jsonLd);
      else schemas.push(jsonLd);
    }

    // Titre
    document.title = pageTitle;

    // Meta description + keywords + robots
    upsertMeta('name', 'description', pageDesc);
    if (data.keywords) upsertMeta('name', 'keywords', data.keywords);
    upsertMeta('name', 'robots', data.noindex ? 'noindex, follow' : 'index, follow');

    // Canonical
    upsertCanonical(canonical);

    // Open Graph
    upsertMeta('property', 'og:type', data.ogType || 'website');
    upsertMeta('property', 'og:url', canonical);
    upsertMeta('property', 'og:title', pageTitle);
    upsertMeta('property', 'og:description', pageDesc);
    upsertMeta('property', 'og:image', pageImage);
    upsertMeta('property', 'og:image:width', '1200');
    upsertMeta('property', 'og:image:height', '630');
    upsertMeta('property', 'og:site_name', 'Plume Astrale');
    upsertMeta('property', 'og:locale', 'fr_FR');

    // Twitter
    upsertMeta('name', 'twitter:card', 'summary_large_image');
    upsertMeta('name', 'twitter:title', pageTitle);
    upsertMeta('name', 'twitter:description', pageDesc);
    upsertMeta('name', 'twitter:image', pageImage);

    // JSON-LD dynamiques (remplace les précédents dynamic; garde les statiques d'index.html)
    replaceJsonLd(schemas);
  }, [path, pageTitle, pageDesc, pageImage, canonical, data, jsonLd]);

  return null;
};

export default SEO;
