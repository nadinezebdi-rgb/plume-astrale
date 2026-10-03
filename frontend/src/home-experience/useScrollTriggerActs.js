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
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Registration idempotente au module load (une seule fois par bundle)
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export default function useScrollTriggerActs({ actsCount = 4, onActChange }) {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const triggers = new Map();
    const syncTriggers = () => {
      let addedTrigger = false;
      for (let i = 1; i <= actsCount; i += 1) {
        const el = document.querySelector(`[data-testid="experience-scene-${i}"]`)
          || document.querySelector(`[data-testid="home-experience-scene-${i}"]`);
        if (!el || triggers.has(i)) continue;
        triggers.set(i, ScrollTrigger.create({
          trigger: el,
          start: 'top center',
          end: 'bottom center',
          onEnter: () => onActChange?.(i, 'enter'),
          onEnterBack: () => onActChange?.(i, 'enter-back'),
        }));
        addedTrigger = true;
      }
      if (addedTrigger) ScrollTrigger.refresh();
    };

    syncTriggers();
    const observer = new MutationObserver(syncTriggers);
    observer.observe(document.body, { childList: true, subtree: true });
    ScrollTrigger.refresh();

    return () => {
      observer.disconnect();
      triggers.forEach((trigger) => trigger.kill());
    };
  }, [actsCount, onActChange]);
}
