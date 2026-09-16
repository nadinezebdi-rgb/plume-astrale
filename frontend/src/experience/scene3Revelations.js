/**
 * Scene 3 — Micro-tension commerciale (Feb 2026)
 * ─────────────────────────────────────────────────────────────
 * Après le tirage d'une carte, la révélation actuelle ("Cette carte
 * éclaire une partie de votre question") est trop générique et trop
 * poétique. Elle ne produit pas de tension commerciale.
 *
 * On remplace par une phrase précise par (carte × intention) — 12
 * combinaisons — qui :
 *   1. Révèle un fragment SPÉCIFIQUE au contexte du user
 *   2. Nomme explicitement ce qui reste caché (tension)
 *   3. Pointe vers le service correspondant à l'intent (promesse)
 *
 * Format = 2 phrases courtes :
 *   • Phrase 1 : révélation partielle SPÉCIFIQUE
 *   • Phrase 2 : ce que le tirage complet / thème natal apportera
 *
 * Voix : Cormorant Garamond italique — mystique, précis, non-cliché.
 */

export const SCENE3_REVELATIONS = {
  heart: {
    relationship: {
      title: 'La Rencontre',
      revelation: 'La Rencontre révèle un lien qui vous porte plus que vous ne l\'imaginez.',
      tension: 'Reste à savoir dans quelle direction il vous emmène.',
      cta: 'Découvrir la suite de mon tirage',
    },
    clarity: {
      title: 'La Rencontre',
      revelation: 'La Rencontre parle d\'un événement qui a déjà commencé à bouger en vous.',
      tension: 'Le tirage complet vous dira lequel — et pourquoi maintenant.',
      cta: 'Découvrir la suite de mon tirage',
    },
    self_discovery: {
      title: 'La Rencontre',
      revelation: 'La Rencontre nomme une part de vous qui cherche à être vue.',
      tension: 'Votre thème natal dira laquelle — et comment l\'incarner pleinement.',
      cta: 'Découvrir mon thème natal',
    },
    specific_question: {
      title: 'La Rencontre',
      revelation: 'La Rencontre annonce que la réponse viendra d\'une personne — ou d\'un croisement inattendu.',
      tension: 'Le tirage complet révèle quand.',
      cta: 'Découvrir la suite de mon tirage',
    },
  },
  moon: {
    relationship: {
      title: 'Le Voile',
      revelation: 'Le Voile éclaire ce qui se joue en silence entre vous deux.',
      tension: 'Une seule carte ne peut dire ce qui, en vous, y répond.',
      cta: 'Découvrir la suite de mon tirage',
    },
    clarity: {
      title: 'Le Voile',
      revelation: 'Le Voile éclaire une clarté que vous ne voyez pas encore.',
      tension: 'Le tirage complet vous montrera où.',
      cta: 'Découvrir la suite de mon tirage',
    },
    self_discovery: {
      title: 'Le Voile',
      revelation: 'Le Voile révèle une intuition que vous n\'osez pas nommer.',
      tension: 'Votre thème natal vous montre pourquoi elle est juste.',
      cta: 'Découvrir mon thème natal',
    },
    specific_question: {
      title: 'Le Voile',
      revelation: 'Le Voile murmure que la vraie question n\'est pas exactement celle que vous posez.',
      tension: 'Le tirage complet dévoile laquelle.',
      cta: 'Découvrir la suite de mon tirage',
    },
  },
  star: {
    relationship: {
      title: 'La Trajectoire',
      revelation: 'La Trajectoire annonce un mouvement dans cette relation.',
      tension: 'Reste à comprendre s\'il vous rapproche ou vous prépare à autre chose.',
      cta: 'Découvrir la suite de mon tirage',
    },
    clarity: {
      title: 'La Trajectoire',
      revelation: 'La Trajectoire pointe une direction que quelque chose en vous a déjà choisie.',
      tension: 'Le tirage complet nomme cette direction.',
      cta: 'Découvrir la suite de mon tirage',
    },
    self_discovery: {
      title: 'La Trajectoire',
      revelation: 'La Trajectoire dessine ce vers quoi vous êtes en train de devenir.',
      tension: 'Votre thème natal en tient la carte détaillée.',
      cta: 'Découvrir mon thème natal',
    },
    specific_question: {
      title: 'La Trajectoire',
      revelation: 'La Trajectoire répond — mais indique aussi ce que vous êtes en train d\'apprendre en chemin.',
      tension: 'Le tirage complet lie les deux.',
      cta: 'Découvrir la suite de mon tirage',
    },
  },
};

/**
 * Fallback poétique si l'intent n'a pas été capturé (edge case).
 * Garde la voix Plume Astrale sans nommer un service précis.
 */
export const SCENE3_FALLBACK = {
  revelation: 'Cette carte éclaire une partie de votre question.',
  tension: 'Mais seule, elle ne raconte pas toute l\'histoire.',
  cta: 'Découvrir la suite de mon tirage',
};

/**
 * Retourne le combo (revelation, tension, cta) pour une carte + intent
 * donnés. Retombe sur SCENE3_FALLBACK si l'un des deux manque.
 */
export function getScene3Revelation(cardId, intentId) {
  const byCard = SCENE3_REVELATIONS[cardId];
  if (!byCard) return SCENE3_FALLBACK;
  const combo = byCard[intentId];
  if (!combo) return SCENE3_FALLBACK;
  return combo;
}
