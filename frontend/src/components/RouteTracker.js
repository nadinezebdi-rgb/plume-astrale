import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { pageView } from '@/lib/analytics';
import useSSRSnapshot from '@/hooks/useSSRSnapshot';

/**
 * RouteTracker — envoie un PageView aux trackers analytics à chaque changement
 * de route SPA + enrichit les meta SEO depuis le snapshot MongoDB (F500 2026-02).
 *
 * No-op analytics si l'utilisateur n'a pas donné son consentement RGPD.
 * L'injection SSR est non-destructive (fallback vers SPA vanilla si 404).
 * Ne rend rien.
 */
export default function RouteTracker() {
  const location = useLocation();
  useSSRSnapshot();
  useEffect(() => {
    pageView(location.pathname + (location.search || ''));
  }, [location.pathname, location.search]);
  return null;
}
