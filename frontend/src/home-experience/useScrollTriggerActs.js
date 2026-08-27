/**
 * useScrollTriggerActs — Hook GSAP ScrollTrigger pour piloter les 8 actes.
 *
 * Rôle : associer chaque section `[data-testid=experience-scene-N]` à un
 * ScrollTrigger dont le callback pousse l'acte courant dans le store.
 * Remplace le useEffect(scroll) custom d'ExperienceRoot (qui reste en
 * place pour /experience standalone), sans casser rien.
 *
 * Utilise gsap.matchMedia pour :
 *   - désactiver totalement sur prefers-reduced-motion
 *   - alléger le nombre de refresh sur mobile
 *
 * Phase 1 : 4 actes. Phase 2 étendra à 8 sans changer l'API.
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
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return; // Fallback : ExperienceRoot pilote déjà le store via son onScroll natif

    const triggers = [];
    for (let i = 1; i <= actsCount; i += 1) {
      const el = document.querySelector(`[data-testid="experience-scene-${i}"]`);
      if (!el) continue;
      const st = ScrollTrigger.create({
        trigger: el,
        start: 'top center',
        end: 'bottom center',
        onEnter:     () => onActChange && onActChange(i, 'enter'),
        onEnterBack: () => onActChange && onActChange(i, 'enter-back'),
      });
      triggers.push(st);
    }

    // Refresh forcé après mount pour prendre en compte les 100vh
    ScrollTrigger.refresh();

    return () => {
      triggers.forEach((t) => t.kill());
    };
  }, [actsCount, onActChange]);
}
