/**
 * Mapping intent → recommandation post-inscription.
 * Utilisé par WelcomeSplash.jsx pour afficher le service adapté.
 */

export const INTENT_CONFIG = {
  relationship: {
    label: 'Une relation vous questionne',
    icon: '♡',
    splashTitle: 'Explorer cette relation.',
    splashLead: 'Vos 20 crédits vous attendent — commençons par ce qui vous a amené ici.',
    primary: {
      label: 'Continuer mon tirage',
      route: '/services/tarot/amour',
      testid: 'welcome-primary-cta',
    },
    secondary: {
      label: 'Découvrir notre compatibilité',
      route: '/services/compatibilite',
      testid: 'welcome-secondary-cta',
    },
  },
  clarity: {
    label: 'Vous cherchiez à y voir plus clair',
    icon: '☾',
    splashTitle: 'Prenons un instant pour éclairer la situation.',
    splashLead: 'Vos 20 crédits vous attendent — offrons-nous une lecture.',
    primary: {
      label: 'Continuer avec le tarot',
      route: '/services/tarot',
      testid: 'welcome-primary-cta',
    },
    secondary: {
      label: 'Découvrir mon cycle actuel',
      route: '/services/revolution-solaire',
      testid: 'welcome-secondary-cta',
    },
  },
  self_discovery: {
    label: 'Vous vouliez mieux vous comprendre',
    icon: '✦',
    splashTitle: 'Et si nous commencions par votre ciel ?',
    splashLead: 'Vos 20 crédits vous attendent — votre thème natal vous révèlera beaucoup.',
    primary: {
      label: 'Découvrir mon thème natal',
      route: '/services/theme-natal',
      testid: 'welcome-primary-cta',
    },
    secondary: {
      label: 'Découvrir mon archétype',
      route: '/services/archetype',
      testid: 'welcome-secondary-cta',
    },
  },
  specific_question: {
    label: 'Vous aviez une question précise',
    icon: '◇',
    splashTitle: 'Gardez votre question en tête.',
    splashLead: 'Vos 20 crédits vous attendent — le tarot vous répondra.',
    primary: {
      label: 'Poser ma question',
      route: '/services/tarot/oui-non',
      testid: 'welcome-primary-cta',
    },
    secondary: {
      label: 'Un tirage plus complet',
      route: '/services/tarot/croix-celtique',
      testid: 'welcome-secondary-cta',
    },
  },
};

/**
 * Récupère l'intent depuis (dans l'ordre) query param, sessionStorage.
 * Retourne une clé valide de INTENT_CONFIG ou null.
 */
export function readIntent() {
  if (typeof window === 'undefined') return null;
  try {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('intent');
    if (q && INTENT_CONFIG[q]) return q;
    const s = window.sessionStorage.getItem('exp_intent');
    if (s && INTENT_CONFIG[s]) return s;
  } catch { /* noop */ }
  return null;
}

export function storeIntent(intent) {
  if (typeof window === 'undefined') return;
  try { window.sessionStorage.setItem('exp_intent', intent); } catch { /* noop */ }
}

export function readDrawnCard() {
  if (typeof window === 'undefined') return null;
  try {
    const params = new URLSearchParams(window.location.search);
    return params.get('exp_card') || window.sessionStorage.getItem('exp_card') || null;
  } catch { return null; }
}

export function storeDrawnCard(card) {
  if (typeof window === 'undefined') return;
  try { window.sessionStorage.setItem('exp_card', card); } catch { /* noop */ }
}

/** Capture UTM + source dès l'arrivée sur /experience — persistance session. */
export function captureUtm() {
  if (typeof window === 'undefined') return {};
  const params = new URLSearchParams(window.location.search);
  const keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'source', 'campaign'];
  const captured = {};
  keys.forEach((k) => {
    const v = params.get(k);
    if (v) captured[k] = v;
  });
  if (Object.keys(captured).length) {
    try { window.sessionStorage.setItem('exp_utm', JSON.stringify(captured)); } catch { /* noop */ }
  }
  return captured;
}

export function readUtm() {
  if (typeof window === 'undefined') return {};
  try {
    const s = window.sessionStorage.getItem('exp_utm');
    return s ? JSON.parse(s) : {};
  } catch { return {}; }
}

/** Signes zodiacaux détectés dans ?campaign=vierge etc. — pour court-circuit horoscope. */
const ZODIAC_CAMPAIGNS = new Set([
  'belier', 'taureau', 'gemeaux', 'cancer', 'lion', 'vierge',
  'balance', 'scorpion', 'sagittaire', 'capricorne', 'verseau', 'poissons',
]);

export function detectZodiacCampaign() {
  const utm = readUtm();
  let camp = (utm.campaign || utm.utm_campaign || '').toLowerCase();
  // Fallback direct URL (sessionStorage désactivé / capture non encore appliquée)
  if (!camp && typeof window !== 'undefined') {
    try {
      const p = new URLSearchParams(window.location.search);
      camp = (p.get('campaign') || p.get('utm_campaign') || '').toLowerCase();
    } catch { /* noop */ }
  }
  return ZODIAC_CAMPAIGNS.has(camp) ? camp : null;
}
