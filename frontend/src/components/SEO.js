import { Helmet } from 'react-helmet-async';

const DOMAIN = 'https://plume-astrale.fr';
const DEFAULT_IMAGE = 'https://static.prod-images.emergentagent.com/jobs/4ab45f1c-820b-4113-96c8-845aa5b0f3e2/images/e6ac5f3284cff4212addcf06b794de85c24a62bc2c57b60538aadfec8e4f2aa8.png';

const SEO_DATA = {
  '/': {
    title: 'Plume Astrale | Guidance Symbolique Personnalisee — Astrologie & Tarot',
    description: 'Plume Astrale eclaire vos dynamiques de vie grace a l\'astrologie, la numerologie et le tarot. Calculs precis, interpretation experte. Decouvrez votre theme natal, tirage gratuit et guidance quotidienne.',
    keywords: 'astrologie, theme natal, tarot gratuit, numerologie, guidance spirituelle, horoscope personnalise, tirage tarot, chemin de vie, compatibilite amoureuse',
  },
  '/premium': {
    title: 'Experience Premium 199€ | Cartographie Celeste Complete — Plume Astrale',
    description: 'Votre cartographie celeste complete en 5 etapes : theme natal approfondi, numerologie, cycles actuels, schemas repetitifs et projection 12 mois. Parcours guide immersif avec PDF Premium.',
    keywords: 'theme natal complet, cartographie celeste, lecture astrologique premium, numerologie complete, projection astrologique, parcours guide astrologie',
  },
  '/tarot-oui-non': {
    title: 'Tirage Tarot Oui/Non Gratuit | Reponse Immediate — Plume Astrale',
    description: 'Posez votre question et recevez une reponse symbolique immediate avec le tirage Tarot Oui/Non. 3 tirages gratuits par jour. Arcanes majeurs du Tarot de Marseille.',
    keywords: 'tirage tarot gratuit, tarot oui non, tarot en ligne, arcane majeur, tarot de marseille, tirage gratuit',
  },
  '/formulaire': {
    title: 'Calculer Mon Theme Natal | Donnees de Naissance — Plume Astrale',
    description: 'Entrez vos donnees de naissance pour recevoir votre theme astral personnalise. Calculs astronomiques precis bases sur votre date, heure et lieu de naissance.',
    keywords: 'calcul theme natal, theme astral gratuit, carte du ciel, ascendant astrologique, positions planetaires',
  },
  '/numerologie': {
    title: 'Numerologie Personnalisee | Chemin de Vie & Annee Personnelle — Plume Astrale',
    description: 'Decouvrez votre chemin de vie, nombre d\'expression, nombre d\'ame et annee personnelle 2026. Analyse numerologique complete et personnalisee.',
    keywords: 'numerologie, chemin de vie, nombre expression, annee personnelle, calcul numerologique, nombre ame',
  },
  '/quotidien': {
    title: 'Guidance Quotidienne | Horoscope du Jour — Plume Astrale',
    description: 'Votre guidance quotidienne personnalisee : horoscope du jour, phase lunaire, conseil spirituel et phrase inspirante pour chaque signe du zodiaque.',
    keywords: 'horoscope du jour, guidance quotidienne, phase lunaire, conseil astrologique, horoscope gratuit',
  },
  '/tarologie': {
    title: 'Tarologie & Mediumnite | Tirage en Croix — Plume Astrale',
    description: 'Tirage en croix complet avec 5 arcanes majeurs et lecture mediumnique. Interpretation approfondie de votre situation actuelle et de vos perspectives.',
    keywords: 'tarologie, tirage en croix, mediumnite, lecture tarot, arcanes majeurs, tirage complet',
  },
  '/compatibilite-amoureuse': {
    title: 'Compatibilite Amoureuse Astrologique | Synastrie — Plume Astrale',
    description: 'Analysez la compatibilite amoureuse entre deux personnes grace a l\'astrologie. Rapport complet de 24 pages en PDF.',
    keywords: 'compatibilite amoureuse, synastrie, compatibilite astrologique, compatibilite signes, amour astrologie',
  },
  '/horoscope': {
    title: 'Horoscope Hebdomadaire & Mensuel — Plume Astrale',
    description: 'Consultez votre horoscope hebdomadaire et mensuel pour chaque signe du zodiaque. Previsions astrologiques detaillees et traduites en francais.',
    keywords: 'horoscope hebdomadaire, horoscope mensuel, previsions astrologiques, horoscope signe',
  },
  '/charte-de-confiance': {
    title: 'Charte de Confiance | Approche Responsable — Plume Astrale',
    description: 'Notre cadre : calculs astrologiques professionnels, lecture symbolique experte, restitution claire. Une guidance symbolique, pas une verite absolue. Decouvrez notre engagement ethique.',
    keywords: 'charte confiance astrologie, ethique tarot, guidance responsable, approche astrologique, deontologie astrologie',
  },
};

const SEO = ({ path }) => {
  const data = SEO_DATA[path] || SEO_DATA['/'];
  const canonical = `${DOMAIN}${path === '/' ? '' : path}`;
  const pageTitle = data.title;

  return (
    <Helmet title={pageTitle}>
      <meta name="description" content={data.description} />
      <meta name="keywords" content={data.keywords} />
      <link rel="canonical" href={canonical} />

      {/* Open Graph */}
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonical} />
      <meta property="og:title" content={pageTitle} />
      <meta property="og:description" content={data.description} />
      <meta property="og:image" content={DEFAULT_IMAGE} />
      <meta property="og:site_name" content="Plume Astrale" />
      <meta property="og:locale" content="fr_FR" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={pageTitle} />
      <meta name="twitter:description" content={data.description} />
      <meta name="twitter:image" content={DEFAULT_IMAGE} />
    </Helmet>
  );
};

export default SEO;
