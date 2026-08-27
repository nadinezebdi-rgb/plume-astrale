/**
 * StarfieldBackdrop — canvas 2D léger qui dessine ~80 étoiles subtiles
 * dérivant lentement en arrière-plan. Aucun WebGL, aucun bundle 3D.
 *
 * Pensé pour unifier l'univers du prototype /experience avec la home
 * classique sans casser aucun style existant. Se pose en absolute avec
 * pointer-events:none — 100% non-breaking.
 *
 * Props:
 *   • density  (default 80) — nombre d'étoiles
 *   • color    (default '#F4EFE6') — couleur RGB des étoiles
 *   • fade     (default 0.55) — opacité max des twinkles
 *   • speed    (default 0.06) — vitesse de dérive (px/frame @ 60fps)
 */
import React, { useEffect, useRef } from 'react';

export default function StarfieldBackdrop({
  density = 80,
  color = '244, 239, 230',
  fade = 0.55,
  speed = 0.06,
  className,
  style,
}) {
  const canvasRef = useRef(null);
  const rafRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Respect reduced motion : dessine une frame statique et sort.
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

    const ctx = canvas.getContext('2d');
    const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    let w = 0, h = 0;
    const stars = [];

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      w = Math.max(1, Math.floor(rect.width));
      h = Math.max(1, Math.floor(rect.height));
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const init = () => {
      stars.length = 0;
      for (let i = 0; i < density; i += 1) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: Math.random() * 1.2 + 0.3,
          o: Math.random() * fade + 0.05,
          twk: Math.random() * 0.008 + 0.002,
          drift: (Math.random() - 0.5) * speed,
          phase: Math.random() * Math.PI * 2,
        });
      }
    };

    const draw = (t) => {
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < stars.length; i += 1) {
        const s = stars[i];
        s.phase += s.twk;
        const alpha = s.o * (0.55 + Math.sin(s.phase) * 0.45);
        s.y += s.drift;
        if (s.y > h + 2) s.y = -2;
        if (s.y < -2) s.y = h + 2;
        ctx.beginPath();
        ctx.fillStyle = `rgba(${color}, ${alpha.toFixed(3)})`;
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
      rafRef.current = requestAnimationFrame(draw);
    };

    resize();
    init();
    if (reduce) {
      // Une seule frame statique
      for (let i = 0; i < stars.length; i += 1) {
        const s = stars[i];
        ctx.beginPath();
        ctx.fillStyle = `rgba(${color}, ${(s.o * 0.6).toFixed(3)})`;
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }
    } else {
      rafRef.current = requestAnimationFrame(draw);
    }

    const onResize = () => { resize(); init(); };
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      cancelAnimationFrame(rafRef.current);
    };
  }, [density, color, fade, speed]);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      data-testid="starfield-backdrop"
      style={{
        position: 'absolute', inset: 0,
        width: '100%', height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
        ...style,
      }}
      aria-hidden="true"
    />
  );
}
