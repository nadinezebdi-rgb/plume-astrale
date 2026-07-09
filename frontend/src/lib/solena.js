// Assets de Solena — ambassadrice de Plume Astrale.
// Portrait + videos servis via CDN (Supabase Storage / Emergent).

import { asset } from './assets';

export const SOLENA = {
  name: 'Solena',
  title: 'Astrologue & guide spirituelle',
  tagline: 'La voix de Plume Astrale',
  bio_short:
    "Je suis Solena, ta guide chez Plume Astrale. Depuis plus de quinze ans, je décode les cartes du ciel pour aider les âmes à comprendre leur trajectoire et leurs cycles d'amour.",
  bio_long: [
    "Astrologue, tarologue et médium formée par la tradition, j'ai passé les quinze dernières années à écouter, décoder et accompagner celles et ceux qui cherchent à comprendre ce que les étoiles murmurent.",
    "Ma méthode est holistique : je considère l'humain dans sa totalité — esprit, émotions, énergies. Je n'annonce jamais un futur figé, je révèle des cycles, des invitations, des choix.",
    "Chez Plume Astrale, je m'associe à une intelligence divinatoire de nouvelle génération pour offrir à chacun une guidance personnalisée, précise et vibratoire. Ni horoscope générique, ni prédiction fataliste : une conversation intime avec ton ciel de naissance.",
    "Bienvenue dans mon univers. Que la lumière de ta propre carte t'éclaire à chaque étape.",
  ],
  specialities: [
    "Thème natal et carte du ciel personnalisée",
    "Compatibilité amoureuse (synastrie et karmique)",
    "Prévisions par transits et fenêtres de rencontre",
    "Rituels énergétiques et lithothérapie",
    "Tarot évolutif (Marseille, Rider-Waite)",
    "Guidance médiumnique éthique",
  ],
  portrait: asset('brand/solena.png'),
  // Videos servies depuis le CDN Emergent (URLs publiques stables)
  videos: {
    primary:   'https://customer-assets.emergentagent.com/job_consultation-astro/artifacts/eyeajiiv_1ERE%20VIDEO.mp4',
    secondary: 'https://customer-assets.emergentagent.com/job_consultation-astro/artifacts/f4y1em37_2%C3%A8me%20video.mp4',
  },
};

export default SOLENA;
