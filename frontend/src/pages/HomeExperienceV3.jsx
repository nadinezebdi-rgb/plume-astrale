/**
 * HomeExperienceV3 — Page shell.
 *
 * Route : /home-experience-v3
 * Meta  : noindex tant que non validé pour prod.
 *
 * Optimisation Phase 4 :
 *  1. Lazy-load complet de HomeExperienceRoot (le bundle R3F ~250 KB gz
 *     ne charge PAS sur les autres pages du site).
 *  2. JSON-LD Organization + WebSite pour indexation propre (quand
 *     le noindex sera levé, aucun retravail SEO).
 *  3. Skip-link accessibilité clavier (visible on focus).
 *  4. aria-live discret pour annoncer les changements d'actes aux
 *     lecteurs d'écran (respecte l'expérience immersive visuelle).
 */
import React, { lazy, Suspense } from 'react';
import SEO from '@/components/SEO';

const HomeExperienceRoot = lazy(() => import('@/home-experience/HomeExperienceRoot'));

const JSONLD = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Plume Astrale — Prototype Immersif',
  url: 'https://plume-astrale.fr/home-experience-v3',
  description: 'Prototype homepage cinématographique de Plume Astrale. Un voyage en huit actes de la question intime à la découverte de votre univers astrologique.',
  publisher: {
    '@type': 'Organization',
    name: 'Plume Astrale',
    url: 'https://plume-astrale.fr',
  },
};

function LoadingVoid() {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Chargement de l'expérience immersive"
      style={{
        minHeight: '100vh',
        background: '#070713',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'rgba(216, 183, 106, 0.6)',
        fontFamily: '"Inter", sans-serif',
        fontSize: 11,
        letterSpacing: '0.32em',
        textTransform: 'uppercase',
      }}
    >
      <span aria-hidden="true" style={{ marginRight: 14 }}>✦</span>
      Le voyage commence…
    </div>
  );
}

export default function HomeExperienceV3() {
  return (
    <>
      <SEO
        path="/home-experience-v3"
        title="Prototype · Plume Astrale"
        description="Prototype homepage immersive Plume Astrale — un voyage en huit actes."
        noindex
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(JSONLD) }}
      />

      {/* Skip-link accessibilité clavier — invisible sauf au focus */}
      <a
        href="#hex3-main"
        style={{
          position: 'absolute', top: -40, left: 12, zIndex: 1000,
          background: '#0F1A3C', color: '#F4EFE6',
          padding: '10px 18px', borderRadius: 3,
          fontFamily: '"Inter", sans-serif', fontSize: 12,
          letterSpacing: '0.18em', textTransform: 'uppercase',
          textDecoration: 'none',
          border: '1px solid rgba(216, 183, 106, 0.4)',
        }}
        onFocus={(e) => { e.currentTarget.style.top = '12px'; }}
        onBlur={(e) => { e.currentTarget.style.top = '-40px'; }}
      >
        Aller au contenu principal
      </a>

      {/* H1 sémantique fondamental — visible via .exp-s1__brand en Acte I */}
      <main id="hex3-main" style={{ position: 'relative' }}>
        <Suspense fallback={<LoadingVoid />}>
          <HomeExperienceRoot />
        </Suspense>
      </main>

      {/* aria-live discret : voix off pour lecteurs d'écran uniquement */}
      <div
        id="hex3-live-region"
        aria-live="polite"
        aria-atomic="true"
        style={{
          position: 'absolute', width: 1, height: 1, padding: 0,
          margin: -1, overflow: 'hidden', clip: 'rect(0, 0, 0, 0)',
          whiteSpace: 'nowrap', border: 0,
        }}
      />
    </>
  );
}
