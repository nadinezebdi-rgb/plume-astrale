/**
 * useUtmTracking — capture UTM params on mount and persist to sessionStorage.
 * Returns an object with utm_source/medium/campaign/content/term ready to send
 * to backend endpoints for attribution.
 *
 * Usage:
 *   const utm = useUtmTracking();
 *   axios.post('/api/rencontres/reveal', { ...payload, utm });
 */
import { useEffect, useMemo } from 'react';

const STORAGE_KEY = 'pa_utm_attribution';
const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'referrer', 'landing_path'];

function readCurrent() {
  try {
    const params = new URLSearchParams(window.location.search);
    const found = {};
    UTM_KEYS.forEach(k => {
      const v = params.get(k);
      if (v) found[k] = v;
    });
    // toujours capturer referrer + landing_path (utile pour l'attribution)
    if (!found.referrer && document.referrer) found.referrer = document.referrer.slice(0, 200);
    found.landing_path = window.location.pathname + window.location.search;
    found.landing_ts = new Date().toISOString();
    return found;
  } catch (e) {
    return {};
  }
}

export default function useUtmTracking() {
  useEffect(() => {
    try {
      const current = readCurrent();
      // Ne stocke que s'il y a au moins un vrai UTM. Sinon garde la premiere valeur (first-touch attribution).
      const hasUtm = UTM_KEYS.some(k => current[k]);
      if (hasUtm) {
        const existing = sessionStorage.getItem(STORAGE_KEY);
        if (!existing) {
          sessionStorage.setItem(STORAGE_KEY, JSON.stringify(current));
        } else {
          // First-touch : on ne remplace pas. On merge juste les champs manquants.
          const merged = { ...current, ...JSON.parse(existing) };
          sessionStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
        }
      }
    } catch (e) { /* ignore */ }
  }, []);

  return useMemo(() => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }, []);
}
