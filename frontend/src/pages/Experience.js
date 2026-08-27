/**
 * /experience — prototype artistique immersif Plume Astrale
 * ─────────────────────────────────────────────────────────────
 * Route ISOLÉE. Ne remplace pas la home. Charge les libs 3D en lazy
 * pour n'impacter aucune autre page du site.
 */
import React, { Suspense, lazy, useEffect } from 'react';
import SEO from '@/components/SEO';

const ExperienceRoot = lazy(() => import('@/experience/ExperienceRoot'));

function LoaderBrand() {
  return (
    <div style={{
      position: 'fixed', inset: 0, background: '#070713', color: '#F4EFE6',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: '"Cormorant Garamond", Georgia, serif',
      letterSpacing: '0.32em', fontSize: 14, opacity: 0.65,
    }}>
      <span>PLUME <em style={{ fontStyle: 'italic', color: '#D8B76A', letterSpacing: '0.06em' }}>Astrale</em></span>
    </div>
  );
}

export default function ExperiencePage() {
  useEffect(() => {
    // Reset scroll top au montage
    window.scrollTo(0, 0);
    // Neutralise le padding/scroll body pour laisser l'expérience prendre 100vh
    const prev = { overflow: document.body.style.overflow };
    return () => { document.body.style.overflow = prev.overflow; };
  }, []);

  return (
    <>
      <SEO
        path="/experience"
        title="Plume Astrale · Expérience immersive"
        description="Certaines réponses ne se cherchent pas — elles se révèlent. Prototype artistique de Plume Astrale."
        noindex
      />
      <Suspense fallback={<LoaderBrand />}>
        <ExperienceRoot />
      </Suspense>
    </>
  );
}
