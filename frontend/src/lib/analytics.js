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

export function getConsent() {
  try {
    const v = localStorage.getItem(CONSENT_KEY);
    if (v === 'accepted') return 'accepted';
    if (v === 'refused') return 'refused';
  } catch (_e) { /* localStorage unavailable */ }
  return null;
}

export function setConsent(value) {
  try { localStorage.setItem(CONSENT_KEY, value); } catch (_e) { /* localStorage unavailable */ }
  if (value === 'accepted') loadTrackers();
}

let _loaded = false;

function loadTrackers() {
  if (_loaded) return;
  _loaded = true;

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
    gtag('config', GA, { anonymize_ip: true });
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
    window.fbq('track', 'PageView');
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
  credit_purchase:             'Purchase',
  pdf_download:                null,
  bundle_click:                'ViewContent',
  solena_click:                'ViewContent',
  solena_question:             'Contact',
};

/**
 * Track un event metier. No-op si l'utilisateur n'a pas consenti.
 * Envoi vers GA4, Plausible ET Meta Pixel (avec mapping vers events standard Meta).
 */
export function event(name, props = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.gtag) window.gtag('event', name, props);
    if (window.plausible) window.plausible(name, { props });
    if (window.fbq) {
      // 1) Event standard Meta (si mapping existe) — utilisé par les ads
      const metaStd = META_EVENT_MAP[name];
      if (metaStd) window.fbq('track', metaStd, props);
      // 2) Event custom Meta (tel quel) — utilisé pour créer des audiences custom
      window.fbq('trackCustom', name, props);
    }
    if (window.twq) {
      // X (Twitter) ads : track l'event custom pour créer des audiences
      window.twq('event', name, props);
    }
  } catch (_e) { /* analytics call failed silently */ }
}

export function pageView(path) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.gtag && process.env.REACT_APP_GA4_ID) {
      window.gtag('config', process.env.REACT_APP_GA4_ID, { page_path: path });
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
  SOLENA_CLICK:                'solena_click',
  SOLENA_QUESTION:             'solena_question',
  BUNDLE_CLICK:                'bundle_click',
  KABBALE_CHECKOUT:            'kabbale_checkout',
  ASTROCARTO_CHECKOUT:         'astrocarto_checkout',
  PACK_KARMIQUE_CHECKOUT:      'pack_karmique_checkout',
  CERCLE_SOLENA_CHECKOUT:      'cercle_solena_checkout',
  CERCLE_SOLENA_ACTIVE:        'cercle_solena_active',
  CREDIT_PURCHASE:             'credit_purchase',
  PDF_DOWNLOAD:                'pdf_download',
};

/**
 * Track une conversion avec un montant (EUR). GA4 event 'purchase' + Plausible
 * revenue tracking automatique via props.revenue.
 */
export function revenue(name, amountEur, extraProps = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    // event_id unique pour deduplication CAPI (server-side) ↔ pixel (client-side).
    // Meta considère 2 events avec même event_id + même event_name comme identiques.
    const eventID = extraProps.eventID || `${name}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const enriched = { ...extraProps, eventID };
    if (window.gtag) {
      window.gtag('event', name, { value: amountEur, currency: 'EUR', ...enriched });
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
