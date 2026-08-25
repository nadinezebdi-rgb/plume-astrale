import { useRef, useCallback } from 'react';

/**
 * Hook d'inclinaison 3D suivant la souris.
 * Retourne { ref, onMouseMove, onMouseLeave } à brancher sur l'élément.
 *
 * @param {object}  opts
 * @param {number}  opts.max     Angle d'inclinaison maximum en degrés (défaut 9)
 * @param {number}  opts.scale   Facteur de zoom au survol (défaut 1.03)
 * @param {number}  opts.perspective  Profondeur de la perspective en px (défaut 1000)
 */
export default function use3DTilt({ max = 9, scale = 1.03, perspective = 1000 } = {}) {
  const ref = useRef(null);
  const raf = useRef(null);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const onMouseMove = useCallback((e) => {
    const el = ref.current;
    if (!el || prefersReducedMotion) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    cancelAnimationFrame(raf.current);
    raf.current = requestAnimationFrame(() => {
      el.style.transform =
        `perspective(${perspective}px) rotateX(${(-py * max).toFixed(2)}deg) ` +
        `rotateY(${(px * max).toFixed(2)}deg) scale(${scale})`;
    });
  }, [max, scale, perspective, prefersReducedMotion]);

  const onMouseLeave = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    cancelAnimationFrame(raf.current);
    el.style.transform = `perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale(1)`;
  }, [perspective]);

  return { ref, onMouseMove, onMouseLeave };
}
