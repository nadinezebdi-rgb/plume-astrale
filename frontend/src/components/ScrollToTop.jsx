/**
 * ScrollToTop — force le scroll au top à chaque changement de route.
 *
 * Fix pour un bug bien connu de React Router : la position de scroll
 * est PRÉSERVÉE au changement de route par défaut. Si un utilisateur
 * clique un lien depuis le bas d'une page longue, il atterrit tout en
 * bas de la nouvelle page (ex. footer visible plutôt que le hero).
 *
 * Ce composant écoute `pathname` et remet le scroll à 0 dès qu'il change.
 * Se monte au niveau racine dans App.js. Ne rend rien.
 *
 * NOTE : Ne pas écraser l'ancre HTML (#faq etc.) — si le hash est
 * présent, on laisse le browser gérer.
 */
import { useLayoutEffect } from 'react';
import { useLocation } from 'react-router-dom';

export default function ScrollToTop() {
  const { pathname, hash } = useLocation();

  useLayoutEffect(() => {
    if (hash) return; // ancre — laisser le browser gérer
    // Instant scroll (pas smooth) pour éviter tout flash de contenu en cours
    // de route
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
  }, [pathname, hash]);

  return null;
}
