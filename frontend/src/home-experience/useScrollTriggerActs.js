/**
 * useScrollTriggerActs — Hook GSAP ScrollTrigger pour piloter les 8 actes.
 *
 * Rôle : associer chaque section `[data-testid=experience-scene-N]` à un
 * ScrollTrigger dont le callback pousse l'acte courant dans le store.
 * Remplace le useEffect(scroll) custom d'ExperienceRoot (qui reste en
 * place pour /experience standalone), sans casser rien.
 *
 * Le hook observe aussi les sections ajoutées après leur chargement différé.
 */
import { useEffect } from 'react';

export default function useScrollTriggerActs({ actsCount = 4, onActChange }) {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    let activeAct = null;
    let frame = null;

    const updateActiveAct = () => {
      frame = null;
      const viewportCenter = window.innerHeight / 2;
      let nearestAct = null;
      let nearestDistance = Infinity;

      for (let i = 1; i <= actsCount; i += 1) {
        const el = document.querySelector(`[data-testid="experience-scene-${i}"]`)
          || document.querySelector(`[data-testid="home-experience-scene-${i}"]`);
        if (!el) continue;
        const rect = el.getBoundingClientRect();
        const distance = viewportCenter < rect.top
          ? rect.top - viewportCenter
          : viewportCenter > rect.bottom
            ? viewportCenter - rect.bottom
            : 0;
        if (distance < nearestDistance) {
          nearestAct = i;
          nearestDistance = distance;
        }
      }

      if (nearestAct !== null && nearestAct !== activeAct) {
        activeAct = nearestAct;
        onActChange?.(nearestAct, 'scroll');
      }
    };

    const scheduleUpdate = () => {
      if (frame === null) frame = window.requestAnimationFrame(updateActiveAct);
    };
    scheduleUpdate();
    window.addEventListener('scroll', scheduleUpdate, { passive: true });
    window.addEventListener('resize', scheduleUpdate);
    const observer = new MutationObserver(scheduleUpdate);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', scheduleUpdate);
      window.removeEventListener('resize', scheduleUpdate);
      if (frame !== null) window.cancelAnimationFrame(frame);
    };
  }, [actsCount, onActChange]);
}
