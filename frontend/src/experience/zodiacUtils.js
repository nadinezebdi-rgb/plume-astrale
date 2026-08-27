/**
 * Utilitaire signe zodiacal — calcul depuis date + descriptions.
 * Zéro dépendance. Utilisé par ZodiacInterlude et WelcomeSplash.
 */

// Signes ordonnés + date de début (inclus). Dernière période (Capricorne)
// couvre à cheval sur l'année → gestion spéciale.
const ZODIAC_SIGNS = [
  { key: 'capricorne',  glyph: '♑', name: 'Capricorne',  element: 'Terre', start: [12, 22], end: [ 1, 19], trait: 'la patience de la montagne' },
  { key: 'verseau',     glyph: '♒', name: 'Verseau',     element: 'Air',   start: [ 1, 20], end: [ 2, 18], trait: 'la clarté de la vision' },
  { key: 'poissons',    glyph: '♓', name: 'Poissons',    element: 'Eau',   start: [ 2, 19], end: [ 3, 20], trait: 'la profondeur des courants intérieurs' },
  { key: 'belier',      glyph: '♈', name: 'Bélier',      element: 'Feu',   start: [ 3, 21], end: [ 4, 19], trait: 'le courage d\u2019ouvrir des portes' },
  { key: 'taureau',     glyph: '♉', name: 'Taureau',     element: 'Terre', start: [ 4, 20], end: [ 5, 20], trait: 'la lenteur qui construit' },
  { key: 'gemeaux',     glyph: '♊', name: 'Gémeaux',     element: 'Air',   start: [ 5, 21], end: [ 6, 20], trait: 'la vivacité des liens' },
  { key: 'cancer',      glyph: '♋', name: 'Cancer',      element: 'Eau',   start: [ 6, 21], end: [ 7, 22], trait: 'la mémoire des marées' },
  { key: 'lion',        glyph: '♌', name: 'Lion',        element: 'Feu',   start: [ 7, 23], end: [ 8, 22], trait: 'la générosité de la lumière' },
  { key: 'vierge',      glyph: '♍', name: 'Vierge',      element: 'Terre', start: [ 8, 23], end: [ 9, 22], trait: 'la précision qui prend soin' },
  { key: 'balance',     glyph: '♎', name: 'Balance',     element: 'Air',   start: [ 9, 23], end: [10, 22], trait: 'la recherche du juste équilibre' },
  { key: 'scorpion',    glyph: '♏', name: 'Scorpion',    element: 'Eau',   start: [10, 23], end: [11, 21], trait: 'l\u2019intensité de la transformation' },
  { key: 'sagittaire',  glyph: '♐', name: 'Sagittaire',  element: 'Feu',   start: [11, 22], end: [12, 21], trait: 'la flèche vers l\u2019horizon' },
];

/**
 * @param {string} iso  — Format YYYY-MM-DD (ou Date-parseable).
 * @returns {object|null} Signe ou null si input invalide.
 */
export function computeZodiac(iso) {
  if (!iso) return null;
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  const m = d.getUTCMonth() + 1;
  const day = d.getUTCDate();
  // Cas particulier Capricorne : Dec 22 → Jan 19.
  if ((m === 12 && day >= 22) || (m === 1 && day <= 19)) {
    return ZODIAC_SIGNS[0];
  }
  return ZODIAC_SIGNS.find((s) => {
    const [ms, ds] = s.start;
    const [me, de] = s.end;
    return (m === ms && day >= ds) || (m === me && day <= de);
  }) || null;
}

export function zodiacByKey(key) {
  return ZODIAC_SIGNS.find((s) => s.key === key) || null;
}

/**
 * Positions d'étoiles pour un mini-pattern par signe (SVG viewBox 200x200).
 * Volontairement stylisé — pas les vraies constellations, mais suffisant
 * pour évoquer la signature du signe.
 */
export const ZODIAC_STARS = {
  belier:     [[60,140],[90,90],[130,70],[160,90],[135,120]],
  taureau:    [[50,90],[90,70],[130,90],[160,120],[110,140]],
  gemeaux:    [[70,60],[70,140],[130,60],[130,140],[100,100]],
  cancer:     [[60,80],[100,70],[140,80],[130,130],[80,130]],
  lion:       [[50,120],[80,80],[120,70],[150,100],[130,140]],
  vierge:     [[60,60],[90,90],[120,110],[150,140],[100,150]],
  balance:    [[50,110],[100,80],[150,110],[100,130]],
  scorpion:   [[50,80],[80,90],[110,110],[130,130],[160,150]],
  sagittaire: [[50,150],[90,110],[130,80],[160,60],[130,100]],
  capricorne: [[60,80],[90,110],[120,90],[150,130],[100,150]],
  verseau:    [[60,70],[100,90],[140,70],[80,130],[130,140]],
  poissons:   [[60,80],[100,100],[140,80],[80,140],[130,140]],
};
