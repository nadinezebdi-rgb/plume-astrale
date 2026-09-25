/**
 * Analytics Plume Astrale — RGPD-compliant.
 *
 * Aucun script tiers (GA4 / Plausible / Meta Pixel) n'est charge tant que
 * l'utilisateur n'a pas explicitement consenti via le bandeau cookies
 * (data-testid="cookie-consent").
 *
 * Si l'utilisateur consent :
 * - On charge GA4 (si REACT_APP_GA4_ID defini)
 * - On charge Plausible (si REACT_APP_PLAUSIBLE_DOMAIN defini)
 * - On charge Meta Pixel (si REACT_APP_META_PIXEL_ID defini) — couvre FB + Instagram
 * - On expose un event() pour tracker les funnels cles
 *
 * Si refus : aucune trace, fonction event() devient un no-op.
 */

const CONSENT_KEY = 'pa_consent_v1';
const CONSENT_TIMESTAMP_KEY = 'pa_consent_ts_v1';
// CNIL 2020 : la durée de vie du consentement ne peut excéder 13 mois.
const CONSENT_MAX_AGE_MS = 13 * 30 * 24 * 60 * 60 * 1000; // ≈ 13 mois

export function getConsent() {
  try {
    const v = localStorage.getItem(CONSENT_KEY);
    if (v !== 'accepted' && v !== 'refused') return null;
    // Vérifie l'âge du consentement (CNIL 13 mois)
    const ts = parseInt(localStorage.getItem(CONSENT_TIMESTAMP_KEY) || '0', 10);
    if (ts && Date.now() - ts > CONSENT_MAX_AGE_MS) {
      // Consentement expiré : purge et redemande
      localStorage.removeItem(CONSENT_KEY);
      localStorage.removeItem(CONSENT_TIMESTAMP_KEY);
      return null;
    }
    return v;
  } catch (_e) { /* localStorage unavailable */ }
  return null;
}

export function setConsent(value) {
  try {
    localStorage.setItem(CONSENT_KEY, value);
    localStorage.setItem(CONSENT_TIMESTAMP_KEY, String(Date.now()));
  } catch (_e) { /* localStorage unavailable */ }
  if (value === 'accepted') loadTrackers();
}

// ─── Google Consent Mode v2 ───────────────────────────────────────────
// Google exige (Mars 2024) que les signaux de consentement soient déclarés
// AVANT le chargement de gtag.js pour l'UE. Defaults = 'denied'. Passe à
// 'granted' quand l'utilisateur accepte via CookieConsent.
// Sans ça, GA4 n'anonymise pas correctement les visiteurs UE non-consentants.
function pushConsentDefaults() {
  if (typeof window === 'undefined') return;
  window.dataLayer = window.dataLayer || [];
  // eslint-disable-next-line no-inner-declarations
  function gtag() { window.dataLayer.push(arguments); }
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'granted',   // strictement nécessaire
    security_storage: 'granted',        // strictement nécessaire
    wait_for_update: 500,               // ms — le CMP peut update sans data loss
  });
}

function pushConsentGranted() {
  if (typeof window === 'undefined' || !window.dataLayer) return;
  // eslint-disable-next-line no-inner-declarations
  function gtag() { window.dataLayer.push(arguments); }
  gtag('consent', 'update', {
    ad_storage: 'granted',
    ad_user_data: 'granted',
    ad_personalization: 'granted',
    analytics_storage: 'granted',
  });
}

// Publie les defaults IMMÉDIATEMENT (avant tout script tiers)
if (typeof window !== 'undefined') pushConsentDefaults();

let _loaded = false;

function loadTrackers() {
  if (_loaded) return;
  _loaded = true;

  // Signaux de consentement UE — active la mesure complète
  pushConsentGranted();

  const GA = process.env.REACT_APP_GA4_ID;
  const PLAUSIBLE_DOMAIN = process.env.REACT_APP_PLAUSIBLE_DOMAIN;
  const META_PIXEL = process.env.REACT_APP_META_PIXEL_ID;

  if (GA) {
    const s = document.createElement('script');
    s.async = true;
    s.src = `https://www.googletagmanager.com/gtag/js?id=${GA}`;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    // send_page_view=false : le RouteTracker est la source unique de page_view
    // (évite double comptage entre config initial + navigation SPA)
    gtag('config', GA, {
      anonymize_ip: true,
      send_page_view: false,
    });
  }

  if (PLAUSIBLE_DOMAIN) {
    const s = document.createElement('script');
    s.defer = true;
    s.setAttribute('data-domain', PLAUSIBLE_DOMAIN);
    s.src = 'https://plausible.io/js/script.js';
    document.head.appendChild(s);
    window.plausible = window.plausible || function () { (window.plausible.q = window.plausible.q || []).push(arguments); };
  }

  if (META_PIXEL) {
    // Meta Pixel Code (Facebook + Instagram) — chargé UNIQUEMENT après consentement
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', META_PIXEL);
    // NB : PageView initial délégué à RouteTracker (source unique de vérité).
    // Éviter fbq('track','PageView') ici pour ne pas double-compter au chargement.
  }

  const X_PIXEL = process.env.REACT_APP_X_PIXEL_ID;
  if (X_PIXEL) {
    // X (Twitter) Universal Website Tag — chargé UNIQUEMENT après consentement
    !function(e,t,n,s,u,a){e.twq||(s=e.twq=function(){s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);},s.version='1.1',s.queue=[],u=t.createElement(n),u.async=!0,u.src='https://static.ads-twitter.com/uwt.js',a=t.getElementsByTagName(n)[0],a.parentNode.insertBefore(u,a))}(window,document,'script');
    window.twq('config', X_PIXEL);
  }
}

// Charge si consentement deja accorde (page reload)
if (typeof window !== 'undefined' && getConsent() === 'accepted') {
  loadTrackers();
}

// Mapping des events métier Plume Astrale → events standard Meta Pixel
// (Meta ne comprend que ses events standard pour l'optimisation des ads).
const META_EVENT_MAP = {
  signup_started:              'Lead',
  signup_completed:            'CompleteRegistration',
  login:                       null,               // pas trackable côté ads
  kabbale_checkout:            'InitiateCheckout',
  astrocarto_checkout:         'InitiateCheckout',
  pack_karmique_checkout:      'InitiateCheckout',
  cercle_solena_checkout:      'InitiateCheckout',
  cercle_solena_active:        'Subscribe',
  credit_purchase:             'Purchase',      // achat d'un pack (vrai revenu)
  credits_spent:               null,            // consommation de crédits déjà achetés
  pdf_download:                null,
  bundle_click:                'ViewContent',
  solena_click:                'ViewContent',
  solena_question:             'Contact',
};

// Mapping des events métier Plume Astrale → events standard GA4.
// GA4 reconnaît nativement une liste courte d'events pour l'e-commerce et
// les rapports de conversion (Explorations, Attribution, Funnel).
// Les events non-mappés partent quand même en GA4 en tant que custom events.
const GA4_EVENT_MAP = {
  signup_started:              'sign_up_start',       // début du parcours d'inscription
  signup_completed:            'sign_up',             // GA4 standard
  login_success:               'login',               // GA4 standard
  login:                       'login',               // GA4 standard
  kabbale_checkout:            'begin_checkout',      // GA4 e-commerce
  astrocarto_checkout:         'begin_checkout',
  pack_karmique_checkout:      'begin_checkout',
  cercle_solena_checkout:      'begin_checkout',
  cercle_solena_active:        'subscribe',
  credit_purchase:             'purchase',            // GA4 e-commerce (via revenue())
  bundle_click:                'view_item',
  solena_click:                'view_item',
  // Autres : passent tels quels en GA4 custom events
};

/**
 * Génère un event_id unique, partagé pixel client ↔ CAPI serveur.
 */
export function newEventId(prefix = 'evt') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function readCookie(name) {
  try {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  } catch (_e) { return null; }
}

/**
 * Signaux d'attribution Meta. Renvoie {} sans consentement.
 * - event_id : clé de déduplication pixel <-> CAPI
 * - fbp/fbc  : cookies posés par le pixel (fbc reconstruit depuis ?fbclid= si absent)
 */
export function getCapiAttribution(prefix = 'evt') {
  if (getConsent() !== 'accepted') return {};
  const out = { event_id: newEventId(prefix) };
  const fbp = readCookie('_fbp');
  if (fbp) out.fbp = fbp;
  let fbc = readCookie('_fbc');
  if (!fbc) {
    try {
      const fbclid = new URLSearchParams(window.location.search).get('fbclid');
      if (fbclid) fbc = `fb.1.${Date.now()}.${fbclid}`;
    } catch (_e) { /* URL non parsable */ }
  }
  if (fbc) out.fbc = fbc;
  return out;
}

/**
 * Track un event metier. No-op si l'utilisateur n'a pas consenti.
 * Envoi vers GA4 (nom mappé si dispo), Plausible ET Meta Pixel.
 *
 * Anti-PII : `props` ne DOIT PAS contenir email, prénom, téléphone, adresse,
 * mot de passe, token. Voir sanitizeProps() ci-dessus. Les callers restent
 * responsables de ne pas passer de PII, sanitizeProps() est un garde-fou.
 */
export function event(name, props = {}) {
  if (getConsent() !== 'accepted') return;
  const safe = sanitizeProps(props);
  try {
    if (window.gtag) {
      // Utilise le nom GA4 standard si mappé (sign_up, login, purchase, etc.)
      // sinon envoie le nom custom (compat rétro + audiences custom).
      const ga4Name = GA4_EVENT_MAP[name] || name;
      window.gtag('event', ga4Name, safe);
    }
    if (window.plausible) window.plausible(name, { props: safe });
    if (window.fbq) {
      // 1) Event standard Meta (si mapping existe) — utilisé par les ads
      const metaStd = META_EVENT_MAP[name];
      if (metaStd) window.fbq('track', metaStd, safe);
      // 2) Event custom Meta (tel quel) — utilisé pour créer des audiences custom
      window.fbq('trackCustom', name, safe);
    }
    if (window.twq) {
      // X (Twitter) ads : track l'event custom pour créer des audiences
      window.twq('event', name, safe);
    }
  } catch (_e) { /* analytics call failed silently */ }
}

/**
 * Anti-PII garde-fou : supprime les clés potentiellement identifiantes
 * avant d'envoyer vers les trackers. Ne modifie pas l'objet original.
 */
const PII_KEYS = new Set([
  'email', 'e_mail', 'user_email',
  'password', 'pwd', 'motdepasse', 'mot_de_passe',
  'prenom', 'first_name', 'last_name', 'nom',
  'phone', 'telephone', 'mobile',
  'address', 'adresse', 'postal_code', 'code_postal',
  'token', 'access_token', 'jwt', 'authorization', 'bearer',
]);
function sanitizeProps(props) {
  if (!props || typeof props !== 'object') return {};
  const out = {};
  for (const k of Object.keys(props)) {
    if (PII_KEYS.has(k.toLowerCase())) continue;
    const v = props[k];
    // Détection basique d'email en valeur (au cas où un caller confond les clés)
    if (typeof v === 'string' && /@[a-z0-9.-]+\.[a-z]{2,}/i.test(v)) continue;
    out[k] = v;
  }
  return out;
}

/**
 * Helper : track un clic sur CTA avec paramètres normalisés pour GA4.
 * Émis en tant que `cta_click` — event custom trackable dans les Explorations.
 * @param {string} name - libellé humain, ex: 'Découvrir mon thème natal'
 * @param {object} extra - { destination, cta_location } — pas de PII
 */
export function ctaClick(name, extra = {}) {
  if (getConsent() !== 'accepted') return;
  const page_location = typeof window !== 'undefined'
    ? (window.location.pathname + window.location.search)
    : '';
  event('cta_click', { cta_name: name, page_location, ...extra });
}

/**
 * Helper : marque le début du parcours d'inscription (event GA4 `sign_up_start`).
 * Dedup côté client via sessionStorage — un user ne devrait pas générer 5 events
 * si on remonte et redescend le form. La complétion émet `sign_up` séparément.
 */
export function signUpStart(props = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.sessionStorage.getItem('pa_signup_start_tracked') === '1') return;
    window.sessionStorage.setItem('pa_signup_start_tracked', '1');
  } catch { /* noop */ }
  event('signup_started', props); // → mappé sign_up_start (GA4) + Lead (Meta)
}

/**
 * Helper : marque l'arrivée sur une page de checkout Stripe (event GA4
 * `begin_checkout`). Dedup par `checkoutKey` unique (ex: pack_id + session_id)
 * pour éviter les doubles émissions si l'utilisateur reload la page.
 * @param {string} name      - event métier (kabbale_checkout, astrocarto_checkout, …)
 * @param {string} checkoutKey - clé unique du checkout (ex: pack_id ou session_id)
 * @param {number} amountEur - montant en euros
 * @param {object} extra     - { item_name, item_category, ... }
 */
export function beginCheckout(name, checkoutKey, amountEur, extra = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    const key = `pa_begin_checkout_${checkoutKey}`;
    if (window.sessionStorage.getItem(key) === '1') return; // anti-double
    window.sessionStorage.setItem(key, '1');
  } catch { /* noop */ }
  const items = extra.items || [{
    item_id: extra.pack_id || checkoutKey || name,
    item_name: extra.item_name || name,
    item_category: extra.item_category || 'checkout',
    price: amountEur,
    quantity: 1,
  }];
  // Envoie via event() (mappe sur `begin_checkout` GA4 + `InitiateCheckout` Meta)
  event(name, {
    value: amountEur,
    currency: 'EUR',
    items,
    ...extra,
  });
}

export function pageView(path) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.gtag && process.env.REACT_APP_GA4_ID) {
      // GA4 event `page_view` explicite — pas config() car send_page_view=false.
      // Émettre un unique event `page_view` par navigation SPA évite le double
      // comptage (config()+event() combinés produisaient 2 hits par route).
      const page_location = typeof window !== 'undefined'
        ? window.location.origin + path
        : path;
      const page_title = typeof document !== 'undefined' ? document.title : '';
      window.gtag('event', 'page_view', {
        page_path: path,
        page_location,
        page_title,
      });
    }
    if (window.fbq) window.fbq('track', 'PageView');
    // plausible auto-track les pageviews
  } catch (_e) { /* analytics call failed silently */ }
}

/**
 * Constantes d'événements — source of truth (évite les typos, facilite
 * les Goals côté dashboard Plausible / GA4).
 */
export const EVENTS = {
  SIGNUP_STARTED:              'signup_started',
  SIGNUP_COMPLETED:            'signup_completed',
  LOGIN:                       'login',
  CTA_CLICK:                   'cta_click',
  SOLENA_CLICK:                'solena_click',
  SOLENA_QUESTION:             'solena_question',
  BUNDLE_CLICK:                'bundle_click',
  KABBALE_CHECKOUT:            'kabbale_checkout',
  ASTROCARTO_CHECKOUT:         'astrocarto_checkout',
  PACK_KARMIQUE_CHECKOUT:      'pack_karmique_checkout',
  CERCLE_SOLENA_CHECKOUT:      'cercle_solena_checkout',
  CERCLE_SOLENA_ACTIVE:        'cercle_solena_active',
  CREDIT_PURCHASE:             'credit_purchase',   // achat d'un pack de crédits
  CREDITS_SPENT:               'credits_spent',     // usage d'un outil payé en crédits
  PDF_DOWNLOAD:                'pdf_download',
  // ── Prototype /experience V3 · funnel de conversion ──
  EXP_STARTED:                 'experience_started',
  EXP_SKIPPED:                 'experience_skipped',
  EXP_SOURCE_CAPTURED:         'experience_source_captured',  // 1× à l'arrivée si UTM/source détectés
  EXP_SCENE1_COMPLETED:        'experience_scene_1_completed',
  EXP_SCENE2_VIEWED:           'experience_scene_2_viewed',
  EXP_INTENT_VIEWED:           'intent_viewed',               // affichage de la question des 4 intents
  EXP_INTENT_SELECTED:         'intent_selected',             // + intent_type
  EXP_TAROT_STARTED:           'tarot_scene_started',
  EXP_TAROT_HOVERED:           'tarot_card_hovered',
  EXP_TAROT_SELECTED:          'tarot_card_selected',
  EXP_TAROT_REVEALED:          'tarot_card_revealed',
  EXP_TAROT_CONTINUE:          'tarot_continue_clicked',
  EXP_FEATHER_STARTED:         'feather_scene_started',
  EXP_FEATHER_COMPLETED:       'feather_completed',
  EXP_SIGNUP_CTA_VIEWED:       'signup_cta_viewed',
  EXP_SIGNUP_CTA_CLICKED:      'signup_cta_clicked',
  EXP_RECOMMENDED_VIEWED:      'recommended_service_viewed',
  EXP_RECOMMENDED_CLICKED:     'recommended_service_clicked',
};

/**
 * Track une conversion avec un montant (EUR). Envoie l'event standard GA4
 * `purchase` (structure e-commerce complète avec items[]) + Plausible revenue
 * + Meta Pixel Purchase (dédup via eventID) + X Pixel.
 *
 * Dédup :
 *   - Meta ↔ CAPI : `eventID` partagé client/serveur (transmis via extraProps.eventID)
 *   - Rafraîchissement page : le CALLER doit gérer une clé sessionStorage
 *     (voir CreditSuccess.js `pa_purchase_tracked_${sessionId}`).
 *   - GA4 : GA4 déduplique nativement sur `transaction_id` (ne pas oublier)
 *
 * @param {string} name         - nom métier (ex: 'credit_purchase') — mappé GA4 → 'purchase'
 * @param {number} amountEur    - montant en euros (obligatoire)
 * @param {object} extraProps   - { eventID, transaction_id, credits, items, ... }
 *                                items = [{ item_id, item_name, item_category, price, quantity }]
 */
export function revenue(name, amountEur, extraProps = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    // event_id unique pour deduplication CAPI (server-side) ↔ pixel (client-side).
    // Meta considère 2 events avec même event_id + même event_name comme identiques.
    const eventID = extraProps.eventID || `${name}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    // transaction_id GA4 = clé de dédup native GA4. Reprend eventID si absent.
    const transaction_id = extraProps.transaction_id || eventID;

    // Structure e-commerce GA4 : items[] permet aux rapports Explorer / Monetization
    // de fonctionner. On dérive un item par défaut si le caller n'en fournit pas.
    const items = extraProps.items || [{
      item_id: extraProps.pack_id || name,
      item_name: extraProps.item_name || name,
      item_category: extraProps.item_category || 'credits',
      price: amountEur,
      quantity: 1,
    }];

    const enriched = { ...extraProps, eventID, transaction_id };

    if (window.gtag) {
      // Nom GA4 standard : 'purchase' (mappé) ou fallback custom
      const ga4Name = GA4_EVENT_MAP[name] || name;
      window.gtag('event', ga4Name, {
        transaction_id,
        value: amountEur,
        currency: 'EUR',
        items,
        ...extraProps,
      });
    }
    if (window.plausible) {
      window.plausible(name, { props: enriched, revenue: { amount: amountEur, currency: 'EUR' } });
    }
    if (window.fbq) {
      // Meta ads : Purchase = event standard optimisable, value + currency requis
      // 3ème arg = { eventID } → clé de deduplication avec la CAPI backend
      window.fbq('track', 'Purchase', { value: amountEur, currency: 'EUR', ...extraProps }, { eventID });
      window.fbq('trackCustom', name, { value: amountEur, currency: 'EUR', ...extraProps }, { eventID });
    }
    if (window.twq) {
      window.twq('event', name, { value: amountEur, currency: 'EUR', ...extraProps });
    }
    // Retourne l'eventID pour que l'appelant puisse le transmettre au backend
    // et que le backend le rejoue dans son event CAPI (dédup Meta).
    return eventID;
  } catch (_e) { /* silent */ }
  return null;
}
