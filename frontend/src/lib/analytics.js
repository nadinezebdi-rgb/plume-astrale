/**
 * Analytics Plume Astrale — RGPD-compliant.
 *
 * Aucun script tiers (GA4 / Plausible) n'est charge tant que l'utilisateur
 * n'a pas explicitement consenti via le bandeau cookies (data-testid="cookie-consent").
 *
 * Si l'utilisateur consent :
 * - On charge GA4 (si REACT_APP_GA4_ID defini)
 * - On charge Plausible (si REACT_APP_PLAUSIBLE_DOMAIN defini)
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
}

// Charge si consentement deja accorde (page reload)
if (typeof window !== 'undefined' && getConsent() === 'accepted') {
  loadTrackers();
}

/**
 * Track un event metier. No-op si l'utilisateur n'a pas consenti.
 * Exemples d'events critiques :
 *   event('signup_completed')
 *   event('premium_checkout_started')
 *   event('premium_checkout_success')
 *   event('synastrie_checkout_started', { price: 49 })
 *   event('synastrie_purchase_success')
 *   event('oracle_email_captured')
 *   event('cercle_checkin_done', { mood })
 */
export function event(name, props = {}) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.gtag) window.gtag('event', name, props);
    if (window.plausible) window.plausible(name, { props });
  } catch (_e) { /* analytics call failed silently */ }
}

export function pageView(path) {
  if (getConsent() !== 'accepted') return;
  try {
    if (window.gtag && process.env.REACT_APP_GA4_ID) {
      window.gtag('config', process.env.REACT_APP_GA4_ID, { page_path: path });
    }
    // plausible auto-track les pageviews
  } catch (_e) { /* analytics call failed silently */ }
}
