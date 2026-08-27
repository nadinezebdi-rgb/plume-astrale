/**
 * HomeExperienceRoot — Phase 1 (Actes I → IV)
 * ────────────────────────────────────────────────────────────
 * Phase 1 stratégie : RÉUTILISATION MAXIMALE de /experience.
 * L'orchestrateur de scroll, les 4 scènes 3D, les timings, le
 * store Zustand, les analytics events sont partagés à l'identique.
 *
 * Ce wrapper ajoute UNIQUEMENT :
 *   - <ActNav> : navigation verticale des actes (droite viewport)
 *   - Écoute du store pour synchroniser currentAct avec currentScene
 *   - Event d'analytics `home_v3_started` pour distinguer ce parcours
 *     de `/experience` standalone dans le dashboard GA4/Plausible.
 *
 * Phase 2 remplacera ce wrapper par une version étendue qui inclura
 * les actes V-VIII (Univers services, Personnalisation, Conversion,
 * Rassurance). Voir /app/memory/PRD.md → "Master Homepage Experience".
 */
import React, { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import ExperienceRoot from '@/experience/ExperienceRoot';
import { useExperienceStore } from '@/experience/useExperienceStore';
import { event as trackEvent } from '@/lib/analytics';
import ActNav from './ActNav';
import ActThread from './ActThread';
import useScrollTriggerActs from './useScrollTriggerActs';
import './HomeExperience.css';

// Actes V-VIII code-splittés : ne chargent qu'après le scroll utilisateur
// (déclenché quand on approche de la fin d'Acte IV). Perf critical mobile.
const Act5Universe        = lazy(() => import('./acts/Act5Universe'));
const Act6Personalization = lazy(() => import('./acts/Act6Personalization'));
const Act7Conversion      = lazy(() => import('./acts/Act7Conversion'));
const Act8Reassurance     = lazy(() => import('./acts/Act8Reassurance'));

const ACT_LABELS = {
  1: "Acte 1 : l'appel",
  2: 'Acte 2 : la question',
  3: 'Acte 3 : la révélation',
  4: 'Acte 4 : la plume',
  5: "Acte 5 : l'univers",
  6: 'Acte 6 : pour vous',
  7: 'Acte 7 : commencer',
  8: 'Acte 8 : votre espace',
};

export default function HomeExperienceRoot() {
  const currentScene = useExperienceStore((s) => s.currentScene);
  const setScene = useExperienceStore((s) => s.setScene);
  const [loadRest, setLoadRest] = useState(false);

  useEffect(() => {
    trackEvent('home_v3_started', {});
  }, []);

  useEffect(() => {
    if (currentScene >= 3 && !loadRest) setLoadRest(true);
    if (currentScene >= 1 && currentScene <= 8) {
      trackEvent('home_v3_act_viewed', { act: currentScene });
      // Annonce vocale discrète pour lecteurs d'écran
      const live = document.getElementById('hex3-live-region');
      if (live) live.textContent = ACT_LABELS[currentScene] || '';
    }
  }, [currentScene, loadRest]);

  // ScrollTrigger orchestrateur pour les 8 actes
  const handleActChange = useCallback((act) => setScene(act), [setScene]);
  useScrollTriggerActs({ actsCount: 8, onActChange: handleActChange });

  const handleJumpToAct = (actId) => {
    // Si le user saute directement à Act 5-8, force le lazy load immédiat
    if (actId >= 5 && !loadRest) setLoadRest(true);
    const el = document.querySelector(`[data-testid="experience-scene-${actId}"]`)
            || document.querySelector(`[data-testid="home-experience-scene-${actId}"]`);
    if (el) {
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      trackEvent('home_v3_actnav_clicked', { act: actId });
    }
  };

  // En mode fallback (WebGL absent ou reduced-motion), on cache ActNav :
  // la structure 8-actes n'est pas parfaitement reproduite dans le fallback
  // 2D, ce qui pourrait dérouter l'utilisateur.
  const webglAvailable = useExperienceStore((s) => s.webglAvailable);
  const reducedMotion = useExperienceStore((s) => s.reducedMotion);
  const showActNav = webglAvailable !== false && !reducedMotion;

  return (
    <>
      <ExperienceRoot />
      {loadRest && (
        <Suspense fallback={<div style={{ minHeight: '100vh', background: '#070713' }} />}>
          <ActThread heightVh={70} testid="hex3-thread-4-5" />
          <Act5Universe />
          <Act6Personalization />
          <Act7Conversion />
          <Act8Reassurance />
        </Suspense>
      )}
      <ActNav
        currentAct={currentScene}
        onJump={handleJumpToAct}
        actsAvailable={8}
        hidden={!showActNav}
      />
    </>
  );
}
