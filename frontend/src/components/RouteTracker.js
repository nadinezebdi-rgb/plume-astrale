import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { pageView } from '@/lib/analytics';

/**
 * RouteTracker — envoie un PageView aux trackers analytics à chaque changement
 * de route SPA (React Router ne recharge pas la page, donc les scripts
 * chargés au boot ne détectent pas les navigations internes).
 *
 * No-op si l'utilisateur n'a pas donné son consentement RGPD (voir analytics.js).
 * Ne rend rien.
 */
export default function RouteTracker() {
  const location = useLocation();
  useEffect(() => {
    pageView(location.pathname + (location.search || ''));
  }, [location.pathname, location.search]);
  return null;
}
