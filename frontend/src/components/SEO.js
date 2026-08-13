import { Helmet } from 'react-helmet-async';

const DOMAIN = 'https://plume-astrale.fr';
const DEFAULT_IMAGE = 'https://static.prod-images.emergentagent.com/jobs/4ab45f1c-820b-4113-96c8-845aa5b0f3e2/images/e6ac5f3284cff4212addcf06b794de85c24a62bc2c57b60538aadfec8e4f2aa8.png';

const SEO_DATA = {
  '/': {
    title: 'Plume Astrale | Guidance Symbolique Personnalis\u00e9e \u2014 Astrologie & Tarot',
    description: 'Connaissance de soi \u2014 mieux comprendre ses \u00e9motions, besoins et fonctionnements. Aide \u00e0 la r\u00e9flexion, relations, cycles de vie, d\u00e9veloppement personnel et introspection. Th\u00e8me natal, tirage gratuit et guidance quotidienne.',
    keywords: 'astrologie, th\u00e8me natal, tarot gratuit, num\u00e9rologie, guidance spirituelle, horoscope personnalis\u00e9, tirage tarot, chemin de vie, compatibilit\u00e9 amoureuse',
  },
  '/premium': {
    title: 'Exp\u00e9rience Premium 199\u20ac | Cartographie C\u00e9leste Compl\u00e8te \u2014 Plume Astrale',
    description: 'Votre cartographie c\u00e9leste compl\u00e8te en 5 \u00e9tapes : th\u00e8me natal approfondi, num\u00e9rologie, cycles actuels, sch\u00e9mas r\u00e9p\u00e9titifs et projection 12 mois. Parcours guid\u00e9 immersif avec PDF Premium.',
    keywords: 'th\u00e8me natal complet, cartographie c\u00e9leste, lecture astrologique premium, num\u00e9rologie compl\u00e8te, projection astrologique, parcours guid\u00e9 astrologie',
  },
  '/tarot-oui-non': {
    title: 'Tirage Tarot Oui/Non Gratuit | R\u00e9ponse Imm\u00e9diate \u2014 Plume Astrale',
    description: 'Posez votre question et recevez une r\u00e9ponse symbolique imm\u00e9diate avec le tirage Tarot Oui/Non. 3 tirages gratuits par jour. Arcanes majeurs du Tarot de Marseille.',
    keywords: 'tirage tarot gratuit, tarot oui non, tarot en ligne, arcane majeur, tarot de marseille, tirage gratuit',
  },
  '/formulaire': {
    title: 'Calculer Mon Th\u00e8me Natal | Donn\u00e9es de Naissance \u2014 Plume Astrale',
    description: 'Entrez vos donn\u00e9es de naissance pour recevoir votre th\u00e8me astral personnalis\u00e9. Calculs astronomiques pr\u00e9cis bas\u00e9s sur votre date, heure et lieu de naissance.',
    keywords: 'calcul th\u00e8me natal, th\u00e8me astral gratuit, carte du ciel, ascendant astrologique, positions plan\u00e9taires',
  },
  '/numerologie': {
    title: 'Num\u00e9rologie Personnalis\u00e9e | Chemin de Vie & Ann\u00e9e Personnelle \u2014 Plume Astrale',
    description: 'D\u00e9couvrez votre chemin de vie, nombre d\'expression, nombre d\'\u00e2me et ann\u00e9e personnelle 2026. Analyse num\u00e9rologique compl\u00e8te et personnalis\u00e9e.',
    keywords: 'num\u00e9rologie, chemin de vie, nombre expression, ann\u00e9e personnelle, calcul num\u00e9rologique, nombre \u00e2me',
  },
  '/quotidien': {
    title: 'Guidance Quotidienne | Horoscope du Jour \u2014 Plume Astrale',
    description: 'Votre guidance quotidienne personnalis\u00e9e : horoscope du jour, phase lunaire, conseil spirituel et phrase inspirante pour chaque signe du zodiaque.',
    keywords: 'horoscope du jour, guidance quotidienne, phase lunaire, conseil astrologique, horoscope gratuit',
  },
  '/tarologie': {
    title: 'Tarologie & Lecture Symbolique | Tirage en Croix \u2014 Plume Astrale',
    description: 'Tirage en croix complet avec 5 arcanes majeurs et lecture symbolique. Interpr\u00e9tation approfondie de votre situation actuelle et de vos perspectives.',
    keywords: 'tarologie, tirage en croix, lecture tarot, arcanes majeurs, tirage complet',
  },
  '/compatibilite-amoureuse': {
    title: 'Compatibilit\u00e9 Amoureuse Astrologique | Astrologie relationnelle \u2014 Plume Astrale',
    description: 'Analysez la compatibilit\u00e9 amoureuse entre deux personnes gr\u00e2ce \u00e0 l\'astrologie relationnelle. Rapport complet de 25 pages en PDF.',
    keywords: 'compatibilit\u00e9 amoureuse, astrologie relationnelle, synastrie, compatibilit\u00e9 astrologique, compatibilit\u00e9 signes, amour astrologie',
  },
  '/synastrie': {
    title: 'Astrologie relationnelle \u2014 Rapport 25 pages | Plume Astrale',
    description: 'D\u00e9couvrez votre astrologie relationnelle : un rapport personnalis\u00e9 de 25 pages qui r\u00e9v\u00e8le les affinit\u00e9s, discordances et dynamiques karmiques de votre lien. \u00c0 partir de vos deux th\u00e8mes natals.',
    keywords: 'astrologie relationnelle, synastrie, compatibilit\u00e9 amoureuse, rapport couple, th\u00e8me astral couple, synastrie plume astrale',
  },
  '/astrosexo': {
    title: 'AstroSexo \u2014 Compatibilit\u00e9 sexuelle astrologique | Plume Astrale',
    description: 'D\u00e9couvrez votre profil sensuel astrologique et vos 3 partenaires les plus compatibles selon votre signe solaire. Analyse par les 4 \u00e9l\u00e9ments.',
    keywords: 'astrosexo, compatibilit\u00e9 sexuelle astrologique, profil sexuel astrologie, signe compatible au lit, alchimie astro, compatibilit\u00e9 intime signes',
  },
  '/horoscope': {
    title: 'Horoscope Hebdomadaire & Mensuel \u2014 Plume Astrale',
    description: 'Consultez votre horoscope hebdomadaire et mensuel pour chaque signe du zodiaque. Pr\u00e9visions astrologiques d\u00e9taill\u00e9es et traduites en fran\u00e7ais.',
    keywords: 'horoscope hebdomadaire, horoscope mensuel, pr\u00e9visions astrologiques, horoscope signe',
  },
  '/charte-de-confiance': {
    title: 'Charte de Confiance | Approche Responsable \u2014 Plume Astrale',
    description: 'Notre cadre : lecture symbolique personnalis\u00e9e, restitution claire. Une guidance symbolique, pas une v\u00e9rit\u00e9 absolue. D\u00e9couvrez notre engagement \u00e9thique.',
    keywords: 'charte confiance astrologie, \u00e9thique tarot, guidance responsable, approche astrologique, d\u00e9ontologie astrologie',
  },
  '/credits': {
    title: 'Comment fonctionnent les cr\u00e9dits \u2014 Plume Astrale',
    description: 'Un cr\u00e9dit, une intention pos\u00e9e \u00e0 Sol\u00e9na. D\u00e9couvre comment nos cr\u00e9dits te donnent acc\u00e8s aux consultations, tirages et rapports premium de Plume Astrale. Sans expiration, sans engagement.',
    keywords: 'cr\u00e9dits plume astrale, tarifs consultation astrologique, prix tarot en ligne, packs cr\u00e9dits astrologie, abonnement libre astrologie',
  },
  '/livres': {
    title: 'Nos livres prestige \u00e0 offrir \u2014 Plume Astrale',
    description: 'Six rapports astrologiques imprim\u00e9s fa\u00e7on livre reli\u00e9 : Astrocartographie, Kabbale, Karma & Destin, Num\u00e9rologie, Th\u00e8me Natal, Synastrie. Couverture illustr\u00e9e, sommaire romain, chapitres num\u00e9rot\u00e9s. Aper\u00e7u gratuit 3 pages.',
    keywords: 'livre astrologie personnalis\u00e9, cadeau astrologique No\u00ebl, rapport astral imprim\u00e9, livre th\u00e8me natal, livre kabbale, livre karma',
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
