import React, { useEffect, useRef, useState } from 'react';

/**
 * Curseur custom desktop — cercle dore 8px avec effet aura.
 * S'agrandit sur les elements `[data-cursor="hover"]`, boutons, links.
 * Auto-desactive sur mobile (pointer:coarse).
 */
const CustomCursor = () => {
  const dot = useRef(null);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    // Desactiver sur mobile ou preference reduce motion
    const coarse = window.matchMedia('(pointer: coarse)').matches;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (coarse || reduce) return;
    setEnabled(true);

    let rafId;
    let x = window.innerWidth / 2, y = window.innerHeight / 2;
    let tx = x, ty = y;

    const onMove = (e) => { tx = e.clientX; ty = e.clientY; };

    const loop = () => {
      // easing 40ms delay ~ lerp 0.15
      x += (tx - x) * 0.18;
      y += (ty - y) * 0.18;
      if (dot.current) {
        dot.current.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
      }
      rafId = requestAnimationFrame(loop);
    };

    const onOver = (e) => {
      const t = e.target;
      if (!dot.current) return;
      const clickable = t.closest('a, button, [role="button"], [data-cursor="hover"], input, select, textarea, label');
      if (clickable) dot.current.classList.add('is-hover');
      else dot.current.classList.remove('is-hover');
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    document.addEventListener('mouseover', onOver, { passive: true });
    rafId = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseover', onOver);
    };
  }, []);

  if (!enabled) return null;
  return <div ref={dot} className="plume-cursor" aria-hidden="true" data-testid="plume-cursor" />;
};

export default CustomCursor;
