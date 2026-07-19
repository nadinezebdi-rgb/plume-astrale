import React from 'react';

/**
 * LibraryImage — Image responsive tirée du bucket public Supabase `library`.
 *
 * Types supportés :
 *   sign    → 12 signes zodiacaux (aries, taurus, gemini, ... et alias FR)
 *   tarot   → 22 arcanes majeurs (00_le_mat ... 21_le_monde)
 *   planet  → 10 planètes (sun, moon, mercury, ... et alias FR)
 *   house   → maisons 1-12 (usage : house={7})
 *
 * Tailles disponibles côté Supabase Storage : 512, 1080, 2048.
 * Ce composant charge automatiquement la bonne taille via srcSet + sizes,
 * ce qui économise de la data mobile tout en gardant la qualité rétina desktop.
 *
 * Exemples :
 *   <LibraryImage type="sign" name="poissons" size={80} />
 *   <LibraryImage type="tarot" name="amoureux" size={200} rounded />
 *   <LibraryImage type="planet" name="vénus" size={64} />
 *   <LibraryImage type="house" house={7} size={64} />
 */

const BUCKET_URL = 'https://ebwicqvbkwogxneipaxh.supabase.co/storage/v1/object/public/library';

// Alias FR → slug EN
const SIGN_ALIASES = {
  belier: 'aries', bélier: 'aries', aries: 'aries',
  taureau: 'taurus', taurus: 'taurus',
  gemeaux: 'gemini', gémeaux: 'gemini', gemini: 'gemini',
  cancer: 'cancer',
  lion: 'leo', leo: 'leo',
  vierge: 'virgo', virgo: 'virgo',
  balance: 'libra', libra: 'libra',
  scorpion: 'scorpio', scorpio: 'scorpio',
  sagittaire: 'sagittarius', sagittarius: 'sagittarius',
  capricorne: 'capricorn', capricorn: 'capricorn',
  verseau: 'aquarius', aquarius: 'aquarius',
  poissons: 'pisces', pisces: 'pisces',
};

const PLANET_ALIASES = {
  soleil: 'sun', sun: 'sun',
  lune: 'moon', moon: 'moon',
  mercure: 'mercury', mercury: 'mercury',
  venus: 'venus', vénus: 'venus',
  mars: 'mars',
  jupiter: 'jupiter',
  saturne: 'saturn', saturn: 'saturn',
  uranus: 'uranus',
  neptune: 'neptune',
  pluton: 'pluto', pluto: 'pluto',
};

// Slug directs supportés + quelques alias FR
const TAROT_ALIASES = {
  mat: '00_le_mat', fou: '00_le_mat',
  bateleur: '01_le_bateleur', magicien: '01_le_bateleur',
  papesse: '02_la_papesse',
  imperatrice: '03_l_imperatrice', impératrice: '03_l_imperatrice',
  empereur: '04_l_empereur',
  pape: '05_le_pape',
  amoureux: '06_les_amoureux',
  chariot: '07_le_chariot',
  force: '08_la_force',
  hermite: '09_l_hermite', ermite: '09_l_hermite',
  roue: '10_la_roue_de_fortune', roue_fortune: '10_la_roue_de_fortune', roue_de_fortune: '10_la_roue_de_fortune',
  justice: '11_la_justice',
  pendu: '12_le_pendu',
  mort: '13_la_mort', sans_nom: '13_la_mort', arcane_sans_nom: '13_la_mort',
  temperance: '14_la_temperance', tempérance: '14_la_temperance',
  diable: '15_le_diable',
  maison_dieu: '16_la_maison_dieu', tour: '16_la_maison_dieu',
  etoile: '17_l_etoile', étoile: '17_l_etoile',
  lune: '18_la_lune',
  soleil: '19_le_soleil',
  jugement: '20_le_jugement',
  monde: '21_le_monde',
};

const _norm = (s) =>
  (s || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')  // strip accents
    .toLowerCase()
    .replace(/[^a-z0-9_]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');

function resolveSlug(type, name) {
  const n = _norm(name);
  if (type === 'sign') return SIGN_ALIASES[n] || SIGN_ALIASES[n.replace(/^(le|la|l)_/, '')] || null;
  if (type === 'planet') return PLANET_ALIASES[n] || PLANET_ALIASES[n.replace(/^(le|la|l)_/, '')] || null;
  if (type === 'tarot') {
    if (/^\d{2}_/.test(n)) return n;    // déjà au format 06_les_amoureux
    // Match direct puis fallback avec articles retirés ("le_bateleur" → "bateleur",
    // "l_amoureux" → "amoureux", "les_amoureux" → "amoureux", "la_papesse" → "papesse")
    const stripped = n.replace(/^(les|le|la|l)_/, '');
    return TAROT_ALIASES[n] || TAROT_ALIASES[stripped] || null;
  }
  return null;
}

const LibraryImage = ({
  type,           // 'sign' | 'tarot' | 'planet' | 'house'
  name,           // requis sauf pour type='house'
  house,          // 1-12 (pour type='house')
  size = 80,      // largeur d'affichage en px
  alt,
  rounded = false,
  className = '',
  style = {},
  'data-testid': testId,
}) => {
  let category, slug;

  if (type === 'house') {
    if (!house || house < 1 || house > 12) return null;
    category = 'houses';
    slug = `house${house}`;
  } else {
    const s = resolveSlug(type, name);
    if (!s) return null;
    category = type === 'sign' ? 'signs' : type === 'planet' ? 'planets' : 'tarot';
    slug = s;
  }

  const url = (px) => `${BUCKET_URL}/${category}/${slug}_${px}.png`;

  return (
    <img
      src={url(1080)}
      srcSet={`${url(512)} 512w, ${url(1080)} 1080w, ${url(2048)} 2048w`}
      sizes={`${size}px`}
      alt={alt || `${type} ${name || house}`}
      loading="lazy"
      decoding="async"
      className={className}
      data-testid={testId}
      style={{
        width: size,
        height: size,
        objectFit: 'contain',
        borderRadius: rounded ? '50%' : undefined,
        ...style,
      }}
    />
  );
};

/**
 * Retourne le nom FR du signe solaire à partir d'une date ISO 'YYYY-MM-DD'.
 * Compatible avec l'API LibraryImage : signFromDate('1990-06-15') → 'Gémeaux'.
 */
export const signFromDate = (dateStr) => {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return null;
  const m = d.getMonth() + 1;
  const j = d.getDate();
  if ((m === 3 && j >= 21) || (m === 4 && j <= 19)) return 'Bélier';
  if ((m === 4 && j >= 20) || (m === 5 && j <= 20)) return 'Taureau';
  if ((m === 5 && j >= 21) || (m === 6 && j <= 20)) return 'Gémeaux';
  if ((m === 6 && j >= 21) || (m === 7 && j <= 22)) return 'Cancer';
  if ((m === 7 && j >= 23) || (m === 8 && j <= 22)) return 'Lion';
  if ((m === 8 && j >= 23) || (m === 9 && j <= 22)) return 'Vierge';
  if ((m === 9 && j >= 23) || (m === 10 && j <= 22)) return 'Balance';
  if ((m === 10 && j >= 23) || (m === 11 && j <= 21)) return 'Scorpion';
  if ((m === 11 && j >= 22) || (m === 12 && j <= 21)) return 'Sagittaire';
  if ((m === 12 && j >= 22) || (m === 1 && j <= 19)) return 'Capricorne';
  if ((m === 1 && j >= 20) || (m === 2 && j <= 18)) return 'Verseau';
  return 'Poissons';
};

export default LibraryImage;
