import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import SEO from '@/components/SEO';

/**
 * NotFound — Vraie page 404 Nocturne Éditorial (SEO P0, Feb 2026).
 *
 * Techniques anti soft-404 :
 *  1. <meta name="robots" content="noindex, follow"> via SEO component
 *  2. document.title préfixé "404" pour signal supplémentaire aux crawlers
 *  3. Pas de contenu commercial ni d'appels à l'action agressifs qui
 *     ressembleraient à une page normale (Google déteste ça)
 *  4. Trois liens sûrs : Accueil, Bibliothèque, Blog
 *
 * ⚠ Limite : le status HTTP 404 réel demande une config au niveau du serveur
 *   frontend (K8s / hosting). Cette page ne peut renvoyer que du 200 (SPA).
 *   Un noindex meta + JS reste toutefois le meilleur signal côté client.
 */
export default function NotFound() {
  const location = useLocation();

  useEffect(() => {
    // Signal supplémentaire pour les crawlers qui interprètent les codes HTTP
    // via une balise (Chromestatus, quelques crawlers custom).
    if (typeof document !== 'undefined') {
      const el = document.createElement('meta');
      el.setAttribute('name', 'prerender-status-code');
      el.setAttribute('content', '404');
      el.setAttribute('data-nf', 'true');
      document.head.appendChild(el);
    }
    return () => {
      if (typeof document !== 'undefined') {
        document.head.querySelectorAll('meta[data-nf="true"]').forEach((m) => m.remove());
      }
    };
  }, []);

  return (
    <div data-testid="notfound-page">
      <SEO
        path="/404"
        title="Page introuvable · Plume Astrale"
        description="Cette page n'existe pas ou n'existe plus. Retrouvez le sommaire ci-dessous."
        noindex
      />

      <section className="ne-section ne-section-night" style={{ minHeight: '80vh', display: 'flex', alignItems: 'center' }}>
        <div className="ne-container">
          <div style={{ maxWidth: 720 }}>
            <div className="ne-overline" data-testid="notfound-overline">
              Erreur 404 &middot; Page introuvable
            </div>

            <h1
              className="ne-display"
              data-testid="notfound-h1"
              style={{ marginTop: 24, color: 'var(--ne-celeste)' }}
            >
              Ce chemin
              <br />
              <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>
                ne mène nulle part.
              </span>
            </h1>

            <hr className="ne-rule-short" style={{ marginTop: 40, marginBottom: 32 }} />

            <p className="ne-lead" style={{ maxWidth: 620, marginBottom: 32 }}>
              L&rsquo;URL <code className="ne-mono" style={{ fontSize: 13, color: 'var(--ne-laiton)' }}>
                {location.pathname}
              </code> n&rsquo;existe pas dans notre bibliothèque, ou n&rsquo;existe plus.
              Nous vous invitons à reprendre depuis l&rsquo;un des points d&rsquo;entrée ci-dessous.
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 48 }}>
              <Link to="/" className="ne-btn ne-btn-primary" data-testid="notfound-home">
                Retour à l&rsquo;accueil
              </Link>
              <Link to="/livres" className="ne-btn ne-btn-secondary" data-testid="notfound-library">
                Bibliothèque
              </Link>
              <Link to="/blog" className="ne-btn-ghost" data-testid="notfound-blog" style={{ color: 'var(--ne-celeste)' }}>
                Journal éditorial
              </Link>
            </div>

            <div className="ne-mono" style={{
              marginTop: 96, fontSize: 10, letterSpacing: '0.28em',
              textTransform: 'uppercase', color: 'rgba(245,240,230,0.4)',
            }}>
              Édition Nocturne &middot; 2026
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
