/**
 * Utilitaire signe zodiacal — calcul depuis date + descriptions.
 * Zéro dépendance. Utilisé par ZodiacInterlude et WelcomeSplash.
 */

// Signes ordonnés + date de début (inclus). Dernière période (Capricorne)
// couvre à cheval sur l'année → gestion spéciale.
// `verses` : 3 vers courts hand-crafted par signe — ancrés dans le
// développement personnel plutôt que dans la prédiction. Affichés
// séquentiellement (stagger 900ms) sur le reveal de la scène Zodiac.
const ZODIAC_SIGNS = [
  { key: 'capricorne',  glyph: '♑', name: 'Capricorne',  element: 'Terre', start: [12, 22], end: [ 1, 19], trait: 'la patience de la montagne',
    verses: [
      'Vous savez attendre. C\u2019est votre pouvoir le plus discret.',
      'Ce que vous construisez ne se voit qu\u2019au bout de dix ans.',
      'Sous votre calme, il y a une ambition que peu soup\u00e7onnent.',
    ] },
  { key: 'verseau',     glyph: '♒', name: 'Verseau',     element: 'Air',   start: [ 1, 20], end: [ 2, 18], trait: 'la clart\u00e9 de la vision',
    verses: [
      'Vous voyez le monde depuis un angle que peu ont explor\u00e9.',
      'Vos amiti\u00e9s valent plus que la plupart des liens convenus.',
      'Vous \u00eates en avance \u2014 souvent seul, jamais perdu.',
    ] },
  { key: 'poissons',    glyph: '♓', name: 'Poissons',    element: 'Eau',   start: [ 2, 19], end: [ 3, 20], trait: 'la profondeur des courants int\u00e9rieurs',
    verses: [
      'Vous ne traversez pas la vie, vous la ressentez.',
      'Ce qui \u00e9chappe aux autres, vous l\u2019entendez d\u00e9j\u00e0.',
      'Votre douceur cache une profondeur que peu explorent.',
    ] },
  { key: 'belier',      glyph: '♈', name: 'B\u00e9lier',  element: 'Feu',   start: [ 3, 21], end: [ 4, 19], trait: 'le courage d\u2019ouvrir des portes',
    verses: [
      'Vous commencez avant que les autres n\u2019aient fini de r\u00e9fl\u00e9chir.',
      'Le monde vous doit une chose : de la place pour vos \u00e9lans.',
      'Votre courage n\u2019a pas de mode d\u2019emploi \u2014 et c\u2019est bien.',
    ] },
  { key: 'taureau',     glyph: '♉', name: 'Taureau',     element: 'Terre', start: [ 4, 20], end: [ 5, 20], trait: 'la lenteur qui construit',
    verses: [
      'Vous ne bougez pas vite. Vous bougez juste.',
      'Chez vous, la beaut\u00e9 n\u2019est pas un luxe : c\u2019est un besoin.',
      'Ce que vous construisez tient longtemps \u2014 parce que vous, vous tenez.',
    ] },
  { key: 'gemeaux',     glyph: '♊', name: 'G\u00e9meaux', element: 'Air',   start: [ 5, 21], end: [ 6, 20], trait: 'la vivacit\u00e9 des liens',
    verses: [
      'Vous \u00eates toujours au moins deux. C\u2019est votre force, pas un d\u00e9faut.',
      'Rien ne vous ennuie plus qu\u2019une seule v\u00e9rit\u00e9.',
      'Vos mots vont plus vite que la plupart des silences.',
    ] },
  { key: 'cancer',      glyph: '♋', name: 'Cancer',      element: 'Eau',   start: [ 6, 21], end: [ 7, 22], trait: 'la m\u00e9moire des mar\u00e9es',
    verses: [
      'Vous ressentez ce que les autres n\u2019ont pas encore nomm\u00e9.',
      'Votre maison n\u2019est pas un lieu, c\u2019est un \u00e9tat.',
      'On revient toujours vers vous \u2014 on se souvient d\u2019y avoir \u00e9t\u00e9 accueilli.',
    ] },
  { key: 'lion',        glyph: '♌', name: 'Lion',        element: 'Feu',   start: [ 7, 23], end: [ 8, 22], trait: 'la g\u00e9n\u00e9rosit\u00e9 de la lumi\u00e8re',
    verses: [
      'Vous ne demandez pas la lumi\u00e8re. Elle vous cherche.',
      'Vous \u00eates g\u00e9n\u00e9reux comme on donne le soleil : sans compter.',
      'Ce que vous appelez fiert\u00e9, d\u2019autres l\u2019appellent dignit\u00e9.',
    ] },
  { key: 'vierge',      glyph: '♍', name: 'Vierge',      element: 'Terre', start: [ 8, 23], end: [ 9, 22], trait: 'la pr\u00e9cision qui prend soin',
    verses: [
      'Vous voyez ce que personne ne voit \u2014 et vous rangez.',
      'Vos gestes ordinaires ont une pr\u00e9cision d\u2019orf\u00e8vre.',
      'Prendre soin, chez vous, c\u2019est une forme d\u2019amour.',
    ] },
  { key: 'balance',     glyph: '♎', name: 'Balance',     element: 'Air',   start: [ 9, 23], end: [10, 22], trait: 'la recherche du juste \u00e9quilibre',
    verses: [
      'Vous cherchez l\u2019\u00e9quilibre comme on cherche \u00e0 respirer.',
      'Vos d\u00e9cisions prennent du temps \u2014 parce qu\u2019elles vous engagent.',
      'La beaut\u00e9, pour vous, n\u2019est jamais accessoire.',
    ] },
  { key: 'scorpion',    glyph: '♏', name: 'Scorpion',    element: 'Eau',   start: [10, 23], end: [11, 21], trait: 'l\u2019intensit\u00e9 de la transformation',
    verses: [
      'Vous n\u2019avez pas peur du fond. C\u2019est l\u00e0 que vous respirez.',
      'Ce que vous transformez, vous le transformez pour de bon.',
      'Votre intensit\u00e9 n\u2019est pas un exc\u00e8s \u2014 c\u2019est votre langue maternelle.',
    ] },
  { key: 'sagittaire',  glyph: '♐', name: 'Sagittaire',  element: 'Feu',   start: [11, 22], end: [12, 21], trait: 'la fl\u00e8che vers l\u2019horizon',
    verses: [
      'Vous cherchez plus loin que le prochain virage.',
      'Votre foi dans la vie d\u00e9place vraiment quelque chose.',
      'Vous partez avant de savoir \u2014 et vous savez en marchant.',
    ] },
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
