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
import React, { useEffect } from 'react';
import ExperienceRoot from '@/experience/ExperienceRoot';
import { useExperienceStore } from '@/experience/useExperienceStore';
import { event as trackEvent } from '@/lib/analytics';
import ActNav from './ActNav';
import './HomeExperience.css';

export default function HomeExperienceRoot() {
  const currentScene = useExperienceStore((s) => s.currentScene);

  // Analytics : distingue ce parcours de /experience standalone.
  // Firera une seule fois (dépendances vides), et seulement si consent RGPD OK
  // (l'event() est no-op sinon).
  useEffect(() => {
    trackEvent('home_v3_started', {});
  }, []);

  // Track chaque changement d'acte (mêmes bornes que les scènes actuelles)
  useEffect(() => {
    if (currentScene >= 1 && currentScene <= 4) {
      trackEvent('home_v3_act_viewed', { act: currentScene });
    }
  }, [currentScene]);

  const handleJumpToAct = (actId) => {
    // Réutilise le scroll natif — ExperienceRoot expose ses <section>
    // avec ref, mais on peut aussi scroller depuis l'extérieur via le
    // sélecteur data-testid (public).
    const el = document.querySelector(`[data-testid="experience-scene-${actId}"]`);
    if (el) {
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      trackEvent('home_v3_actnav_clicked', { act: actId });
    }
  };

  return (
    <>
      <ExperienceRoot />
      <ActNav
        currentAct={currentScene}
        onJump={handleJumpToAct}
        actsAvailable={4}
      />
    </>
  );
}
