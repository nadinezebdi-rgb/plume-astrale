/**
 * useSSRSnapshot — F500 SEO 2026-02.
 *
 * Sur chaque changement de route, appelle GET /api/seo/content?path=<route>
 * et INJECTE dans le <head> les meta_title, meta_desc, canonical, og:*,
 * JSON-LD précalculés côté serveur.
 *
 * ⚠ Fallback safe (Q5a) : si le backend renvoie 404 ou timeout, on ne fait
 * RIEN — le composant <SEO /> côté client prend le relais. Pas de degradation.
 *
 * Ce hook est complémentaire au composant <SEO /> ; il enrichit avec le
 * contenu pré-rendu quand disponible, sans forcer la présence.
 */
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

// Ne pas hit l'endpoint pour les routes protégées / dynamiques
const SKIP_PATHS = [
  '/mon-compte', '/admin', '/inscription', '/connexion',
  '/paiement', '/succes', '/formulaire',
];

function shouldSkip(pathname) {
  return SKIP_PATHS.some((p) => pathname.startsWith(p));
}

function setMeta(name, content, isProperty = false) {
  if (!content) return;
  const attr = isProperty ? 'property' : 'name';
  let el = document.head.querySelector(`meta[${attr}="${name}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function injectJsonLd(schemas) {
  // Retire les anciens JSON-LD marqués snapshot
  document.head.querySelectorAll('script[data-ssr-snapshot]').forEach((s) => s.remove());
  if (!Array.isArray(schemas)) return;
  schemas.forEach((schema) => {
    if (!schema || typeof schema !== 'object') return;
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.setAttribute('data-ssr-snapshot', 'true');
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  });
}

export default function useSSRSnapshot() {
  const { pathname } = useLocation();

  useEffect(() => {
    if (!API || shouldSkip(pathname)) return;
    let cancelled = false;

    (async () => {
      try {
        const r = await fetch(`${API}/api/seo/content?path=${encodeURIComponent(pathname)}`, {
          signal: AbortSignal.timeout ? AbortSignal.timeout(2000) : undefined,
        });
        if (!r.ok || cancelled) return;
        const data = await r.json();
        if (cancelled) return;
        // Injection non-destructive : n'écrase QUE si la donnée SSR existe
        if (data.meta_title) document.title = data.meta_title;
        if (data.meta_desc) setMeta('description', data.meta_desc);
        if (data.meta_desc) setMeta('og:description', data.meta_desc, true);
        if (data.meta_title) setMeta('og:title', data.meta_title, true);
        if (data.og_image) setMeta('og:image', data.og_image, true);
        if (data.og_type) setMeta('og:type', data.og_type, true);
        if (data.canonical) {
          let link = document.head.querySelector('link[rel="canonical"]');
          if (!link) {
            link = document.createElement('link');
            link.rel = 'canonical';
            document.head.appendChild(link);
          }
          link.href = data.canonical;
        }
        injectJsonLd(data.jsonld);
      } catch (_e) {
        // Silencieux — Q5a : fallback vers SPA vanilla
      }
    })();

    return () => { cancelled = true; };
  }, [pathname]);
}
