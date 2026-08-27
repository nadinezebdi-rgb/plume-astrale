/**
 * FeatherCursor — plume calligraphique qui suit le curseur avec un
 * l\u00e9ger d\u00e9calage (lerp) et une rotation subtile bas\u00e9e sur la direction
 * du mouvement.
 *
 * Mont\u00e9 UNIQUEMENT sur desktop pointeur fin (matchMedia hover:hover).
 * Se cache automatiquement quand la souris sort du conteneur parent
 * (via bounding rect check dans le rAF loop).
 *
 * Perf : un seul rAF loop, position en transform (GPU), rendu SVG l\u00e9ger.
 * Non-breaking : pointer-events:none, position:absolute, z-index bas.
 */
import React, { useEffect, useRef, useState } from 'react';

const LERP = 0.18;      // lissage position (plus bas = plus tra\u00eenant)
const ROT_LERP = 0.12;  // lissage rotation

export default function FeatherCursor({ containerRef }) {
  const [mounted, setMounted] = useState(false);
  const nodeRef = useRef(null);
  const state = useRef({
    x: 0, y: 0, tx: 0, ty: 0,
    rot: -20, trot: -20,
    lastMoveTs: 0,
    inside: false,
  });

  useEffect(() => {
    // Mont\u00e9 uniquement si pointeur fin + pas de reduced motion
    const canRun = window.matchMedia?.('(hover: hover) and (pointer: fine)').matches;
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (!canRun || reduce) return;

    // Attend que le containerRef soit disponible
    if (!containerRef?.current) return;
    setMounted(true);

    let rafId = 0;

    const onMove = (e) => {
      const box = containerRef.current?.getBoundingClientRect();
      if (!box) return;
      const inside = e.clientX >= box.left && e.clientX <= box.right
                  && e.clientY >= box.top  && e.clientY <= box.bottom;
      state.current.inside = inside;
      if (inside) {
        // Coordonn\u00e9es relatives au container
        const nx = e.clientX - box.left;
        const ny = e.clientY - box.top;
        // Rotation d'apr\u00e8s la direction du mouvement
        const dx = nx - state.current.tx;
        const dy = ny - state.current.ty;
        if (Math.abs(dx) + Math.abs(dy) > 0.5) {
          const ang = Math.atan2(dy, dx) * (180 / Math.PI);
          // Plume orient\u00e9e globalement en diagonale (-20\u00b0), la direction module l\u00e9g\u00e8rement
          state.current.trot = -20 + Math.max(-25, Math.min(25, ang * 0.08));
        }
        state.current.tx = nx;
        state.current.ty = ny;
        state.current.lastMoveTs = performance.now();
      }
    };

    const loop = () => {
      const s = state.current;
      s.x += (s.tx - s.x) * LERP;
      s.y += (s.ty - s.y) * LERP;
      s.rot += (s.trot - s.rot) * ROT_LERP;
      if (nodeRef.current) {
        const idle = performance.now() - s.lastMoveTs > 1200;
        const visible = s.inside && !idle;
        nodeRef.current.style.opacity = visible ? '0.85' : '0';
        nodeRef.current.style.transform = `translate3d(${s.x - 22}px, ${s.y - 32}px, 0) rotate(${s.rot}deg)`;
      }
      rafId = requestAnimationFrame(loop);
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    rafId = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(rafId);
    };
  }, [containerRef]);

  if (!mounted) return null;

  return (
    <svg
      ref={nodeRef}
      data-testid="feather-cursor"
      width="44" height="64" viewBox="0 0 44 64"
      style={{
        position: 'absolute', top: 0, left: 0,
        pointerEvents: 'none',
        zIndex: 2,
        opacity: 0,
        transition: 'opacity 400ms ease',
        filter: 'drop-shadow(0 4px 8px rgba(216, 183, 106, 0.25))',
        willChange: 'transform, opacity',
      }}
      aria-hidden="true"
    >
      {/* Rachis (tige centrale courbe) */}
      <path
        d="M22 4 Q 21 20 22 30 Q 23 44 22 60"
        stroke="#C4A25C" strokeWidth="1.1" fill="none"
        strokeLinecap="round"
      />
      {/* Barbes gauche */}
      <g stroke="#D8B76A" strokeWidth="0.9" strokeLinecap="round" fill="none" opacity="0.75">
        <path d="M22 10 Q 15 12 10 10" />
        <path d="M22 16 Q 13 19 7  17" />
        <path d="M22 22 Q 11 26 5  24" />
        <path d="M22 28 Q 11 32 5  30" />
        <path d="M22 34 Q 12 38 7  37" />
        <path d="M22 40 Q 14 43 9  42" />
        <path d="M22 46 Q 16 49 12 48" />
        <path d="M22 52 Q 18 54 15 53" />
      </g>
      {/* Barbes droite */}
      <g stroke="#D8B76A" strokeWidth="0.9" strokeLinecap="round" fill="none" opacity="0.75">
        <path d="M22 10 Q 29 12 34 10" />
        <path d="M22 16 Q 31 19 37 17" />
        <path d="M22 22 Q 33 26 39 24" />
        <path d="M22 28 Q 33 32 39 30" />
        <path d="M22 34 Q 32 38 37 37" />
        <path d="M22 40 Q 30 43 35 42" />
        <path d="M22 46 Q 28 49 32 48" />
        <path d="M22 52 Q 26 54 29 53" />
      </g>
    </svg>
  );
}
