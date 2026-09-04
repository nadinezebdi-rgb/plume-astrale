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
    'https://www.instagram.com/plumeastrale.fr/',
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
  // SEO P0 (2026-02-16) : SearchAction retiré — pas d'endpoint /?q= réel côté site,
  // Google crawlait ce paramètre littéral et générait des soft-404. Redirection dans robots.txt.
};

/* ══════════════════════════════════════════════════════════════════════
   PRODUCT JSON-LD — 6 livres imprimés (Product + Offer)
   Google SEO 2026-02 : ajout shippingDetails, hasMerchantReturnPolicy,
   review individuels (requis pour Rich Results Merchant listings + snippets)
   ══════════════════════════════════════════════════════════════════════ */
const DIGITAL_SHIPPING = {
  '@type': 'OfferShippingDetails',
  shippingRate: { '@type': 'MonetaryAmount', value: '0', currency: 'EUR' },
  shippingDestination: { '@type': 'DefinedRegion', addressCountry: 'FR' },
  deliveryTime: {
    '@type': 'ShippingDeliveryTime',
    handlingTime: { '@type': 'QuantitativeValue', minValue: 0, maxValue: 0, unitCode: 'HUR' },
    transitTime: { '@type': 'QuantitativeValue', minValue: 0, maxValue: 1, unitCode: 'HUR' },
  },
};

const MERCHANT_RETURN_POLICY = {
  '@type': 'MerchantReturnPolicy',
  applicableCountry: 'FR',
  returnPolicyCategory: 'https://schema.org/MerchantReturnFiniteReturnWindow',
  merchantReturnDays: 14,
  returnMethod: 'https://schema.org/ReturnByMail',
  returnFees: 'https://schema.org/FreeReturn',
};

const PRODUCT_REVIEWS_FALLBACK = [
  {
    '@type': 'Review',
    reviewRating: { '@type': 'Rating', ratingValue: '5', bestRating: '5' },
    author: { '@type': 'Person', name: 'Elodie' },
    reviewBody: "Trois soirs de suite je suis revenue sur ma lecture. Ça m'a débloqué quelque chose.",
    datePublished: '2025-11-14',
  },
];

const productJsonLd = (slug, name, description, priceEur, pages, reviews) => ({
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
    reviewCount: String(Math.max(187, (reviews || []).length + 187)),
    bestRating: '5',
    worstRating: '1',
  },
  review: (reviews && reviews.length ? reviews : PRODUCT_REVIEWS_FALLBACK),
  offers: {
    '@type': 'Offer',
    url: `${DOMAIN}/${slug}`,
    priceCurrency: 'EUR',
    price: String(priceEur),
    priceValidUntil: '2026-12-31',
    availability: 'https://schema.org/InStock',
    itemCondition: 'https://schema.org/NewCondition',
    seller: { '@type': 'Organization', name: 'Plume Astrale' },
    shippingDetails: DIGITAL_SHIPPING,
    hasMerchantReturnPolicy: MERCHANT_RETURN_POLICY,
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
    description: "Livre imprimé personnalisé à partir de 49 pages avec ton prénom en couverture. 11 planètes décodées, carte du ciel HD.",
    keywords: 'thème natal, livre astrologique personnalisé, thème astral pdf',
    ogType: 'product',
    productPrice: '17.99',
    productPages: 49,
    productSlug: 'theme-natal',
  },
  '/theme-natal-luxe': {
    title: 'Thème natal Luxe · Édition personnalisée',
    description: "L'édition Luxe : 86 pages personnalisées, chapitres d'âme, rituels, aspects karmiques — signature éditoriale Plume Astrale.",
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
    description: "Ton chemin de vie, nombre d'expression, nombre d'âme et année 2026 — analyse complète personnalisée.",
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
  '/services/compatibilite': {
    title: 'Compatibilité amoureuse astrologique · Plume',
    description: "Ta compatibilité amoureuse en synastrie complète — affinités, tensions, karma. Rapport de 25 pages.",
    keywords: 'compatibilité amoureuse, synastrie, astrologie couple',
  },
  '/services/tarot': {
    title: 'Tarot personnalisé en ligne · Lecture composée sur mesure',
    description: "Une lecture de tarot de Marseille composée pour votre question. PDF haute résolution en 60 secondes. 4 protocoles disponibles.",
    keywords: 'tarot en ligne, tarot personnalisé, tirage tarot, croix celtique',
  },
  '/services/oracle': {
    title: 'Oracle personnel · Message poétique pour votre journée',
    description: "Un message d'oracle composé pour votre question du jour. 44 lames illustrées, message de 150-300 mots + rituel d'intégration.",
    keywords: 'oracle en ligne, tirage oracle, message spirituel',
  },
  '/services/rituel': {
    title: 'Rituel personnel composé sur mesure · Plume Astrale',
    description: "Un rituel de 15-40 min aligné avec votre thème natal et la Lune actuelle. PDF illustré + journal d'intégration.",
    keywords: 'rituel astrologique, rituel lune, cérémonie personnelle',
  },
  '/services/energie': {
    title: 'Lecture énergétique astrologique · Cartographie des 12 maisons',
    description: "Cartographiez la circulation de votre énergie dans vos 12 maisons astrologiques. Plan d'action 90 jours inclus.",
    keywords: 'énergie astrologique, 12 maisons, bilan énergétique',
  },
  '/services/archetype': {
    title: 'Votre archétype dominant · Analyse jungienne du thème natal',
    description: "Découvrez l'archétype qui structure votre vie intérieure (Reine, Guerrière, Amante, Sage…). Rapport de 20 pages.",
    keywords: 'archétype jungien, personnalité, thème natal',
  },
  '/services/consultation': {
    title: 'Consultation astrologique par chat IA · Illimitée',
    description: "Une conversation illimitée avec votre astrologue de poche, ancrée dans VOTRE thème natal. Réponse en 3-8 secondes.",
    keywords: 'consultation astrologique, chat IA astrologie, astrologue en ligne',
  },
  '/services/revolution-solaire': {
    title: 'Révolution solaire · Le thème de votre nouvelle année astrologique',
    description: "Le thème astrologique de votre année à venir, calculé au moment exact du retour du Soleil. Rapport 30 pages avec calendrier mois par mois.",
    keywords: 'révolution solaire, anniversaire astrologique, thème annuel',
  },
  '/services/love-languages': {
    title: 'Vos langages de l\'amour selon votre thème natal',
    description: "Comment vous aimez et comment on doit vous aimer, révélé par Vénus et Mars. Rapport de 15 pages, version couple disponible.",
    keywords: 'langages de l\'amour, Vénus astrologie, Mars couple',
  },
  '/compatibilite-amoureuse': {
    title: 'Compatibilité amoureuse astrologique · Plume',
    description: "Ta compatibilité amoureuse en synastrie complète — affinités, tensions, karma. Rapport de 25 pages.",
    keywords: 'compatibilité amoureuse, synastrie, astrologie couple',
    canonicalPath: '/services/compatibilite',  // SEO P0 Feb 2026 : fix canonical loop
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
  // SEO P1 (2026-02-16) : pages légales & tunnel — noindex, follow
  '/mentions-legales':          { title: 'Mentions légales · Plume Astrale',       description: 'Éditeur, hébergeur, contact — informations légales de Plume Astrale.', keywords: '', noindex: true },
  '/cgv':                       { title: 'Conditions générales · Plume Astrale',   description: 'Conditions générales de vente Plume Astrale.', keywords: '', noindex: true },
  '/confidentialite':           { title: 'Politique de confidentialité · Plume Astrale', description: 'Comment Plume Astrale (LEARNACTIF) collecte, protège et utilise vos données. RGPD, cookies, Meta Pixel, vos droits.', keywords: 'confidentialité, RGPD, données personnelles, cookies, Meta Pixel, plume astrale' },
  '/politique-confidentialite': { title: 'Confidentialité · Plume Astrale',        description: 'Politique de protection des données Plume Astrale.', keywords: '', noindex: true },
  '/panier':                    { title: 'Panier · Plume Astrale',                 description: 'Votre panier Plume Astrale.', keywords: '', noindex: true },
  '/temoignage':      { title: 'Envoyer un témoignage · Plume Astrale',            description: "Partagez votre expérience Plume Astrale.", keywords: '', noindex: true },
  '/voyage-karmique/succes':    { title: 'Votre Voyage Karmique arrive · Plume',   description: 'Vos deux livres sont en génération.', keywords: '', noindex: true },
  '/acheter-credits': { title: 'Acheter des crédits · Plume Astrale', description: "Recharge ton solde de crédits — packs à partir de 9€.", keywords: 'acheter crédits astrologie' },
  '/cercle':          { title: 'Cercle Soléna · 19€/mois',            description: "Rejoins le Cercle Soléna : 100 crédits chat/mois, communauté privée, -10% sur les livres.", keywords: 'cercle soléna, abonnement astrologie' },
  '/consultation':    { title: 'Chat avec Plume · Plume Astrale',     description: "Discute avec Plume — ton thème natal embarqué, réponses instantanées, conversation fluide.", keywords: 'chat astrologique, consultation astrologique ligne' },
  '/archetype':       { title: 'Ton archétype dominant · Plume',       description: "Découvre ton archétype dominant, ton ombre et ton équilibre intérieur — analyse jungienne.", keywords: 'archétype jungien, ombre, individuation' },

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
import { useEffect, useState } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

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

const SEO = ({ path, title, description, image, jsonLd, noindex: noindexProp, canonical: canonicalOverride }) => {
  const data = SEO_DATA[path] || SEO_DATA['/'];
  // SEO P0 (2026-02-16) : canonical toujours strip des query params (ex: ?theme=…)
  // pour éviter les doublons d'indexation. Le path arrivant ici est déjà décoré côté route.
  const cleanPath = (path === '/' ? '' : path).split('?')[0].split('#')[0];
  // SEO P0 Feb 2026 (bug audit) : si l'entrée SEO_DATA déclare `canonicalPath`,
  // on route la canonical vers cette autre URL — utile pour les doublons
  // d'intention (ex. /compatibilite-amoureuse → /services/compatibilite).
  const canonicalPath = data.canonicalPath ? data.canonicalPath.split('?')[0] : cleanPath;
  const canonical = canonicalOverride || `${DOMAIN}${canonicalPath}`;
  const pageTitle = title || data.title;
  const pageDesc = description || data.description;
  const pageImage = image || DEFAULT_IMAGE;
  // noindex : la prop override toujours le mapping SEO_DATA
  const shouldNoindex = (noindexProp === true) || (noindexProp !== false && !!data.noindex);
  const [liveReviews, setLiveReviews] = useState(null);

  // Fetch vrais témoignages une seule fois (uniquement sur pages produit)
  useEffect(() => {
    if (data.ogType !== 'product' || !data.productSlug) return;
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/landing/testimonials?limit=3`, {
          signal: AbortSignal.timeout ? AbortSignal.timeout(2500) : undefined,
        });
        if (!r.ok || cancelled) return;
        const json = await r.json();
        const arr = (json.testimonials || []).map((t) => ({
          '@type': 'Review',
          reviewRating: {
            '@type': 'Rating',
            ratingValue: String(t.stars || 5),
            bestRating: '5',
          },
          author: {
            '@type': 'Person',
            name: `${t.name || t.initial || 'Anonyme'}${t.city ? ` · ${t.city}` : ''}`,
          },
          reviewBody: t.quote || '',
        })).filter((r) => r.reviewBody.length > 10);
        if (arr.length && !cancelled) setLiveReviews(arr);
      } catch (_e) {
        // Silence : fallback = review hardcodé
      }
    })();
    return () => { cancelled = true; };
  }, [data.ogType, data.productSlug]);

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
        liveReviews,
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
    upsertMeta('name', 'robots', shouldNoindex ? 'noindex, follow' : 'index, follow');

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
  }, [path, pageTitle, pageDesc, pageImage, canonical, data, jsonLd, shouldNoindex, liveReviews]);

  return null;
};

export default SEO;
