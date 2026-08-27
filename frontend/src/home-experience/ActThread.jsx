/**
 * ActThread — Fil doré vertical scrub-triggered entre deux Actes.
 *
 * S'anime via GSAP ScrollTrigger scrub : plus l'utilisateur scrolle,
 * plus la ligne se dessine (stroke-dashoffset). Termine sur une petite
 * plume glyphe (écho de la Scène 4).
 *
 * Utilisé pour la transition majeure Acte IV → Acte V demandée par le
 * brief : « la plume descend, sa pointe trace une ligne dorée, le scroll
 * suit cette ligne ». Version 2D pure (SVG) pour zéro coût WebGL.
 *
 * Respect prefers-reduced-motion : ligne statique complète (pas d'anim).
 */
import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export default function ActThread({ heightVh = 70, testid = 'hex3-thread' }) {
  const lineRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const line = lineRef.current;
    const container = containerRef.current;
    if (!line || !container) return;

    // Longueur exacte du path : ~heightVh * 0.01 * innerHeight px
    const total = line.getTotalLength();
    line.style.strokeDasharray = String(total);
    line.style.strokeDashoffset = String(total);

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      // Ligne statique complète
      line.style.strokeDashoffset = '0';
      return;
    }

    const st = ScrollTrigger.create({
      trigger: container,
      start: 'top 90%',
      end: 'bottom 20%',
      scrub: 0.8,
      onUpdate: (self) => {
        line.style.strokeDashoffset = String(total * (1 - self.progress));
      },
    });

    return () => st.kill();
  }, []);

  return (
    <div
      ref={containerRef}
      data-testid={testid}
      style={{
        position: 'relative', width: '100%', height: `${heightVh}vh`,
        background: '#070713',
        display: 'flex', alignItems: 'stretch', justifyContent: 'center',
        overflow: 'hidden',
      }}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 4 100"
        preserveAspectRatio="none"
        style={{ width: 4, height: '100%', display: 'block' }}
      >
        <path
          ref={lineRef}
          d="M 2 0 L 2 100"
          stroke="rgba(216, 183, 106, 0.75)"
          strokeWidth="0.6"
          fill="none"
          strokeLinecap="round"
          style={{
            filter: 'drop-shadow(0 0 6px rgba(216, 183, 106, 0.55))',
          }}
        />
      </svg>
      {/* Petite plume glyphe en fin de ligne — écho de la Scène 4 */}
      <svg
        viewBox="0 0 44 64"
        style={{
          position: 'absolute', bottom: 16, left: '50%',
          transform: 'translateX(-50%) rotate(0deg)',
          width: 26, height: 38,
          filter: 'drop-shadow(0 0 10px rgba(216, 183, 106, 0.5))',
          opacity: 0.85,
        }}
      >
        <path d="M22 4 Q 21 20 22 30 Q 23 44 22 60"
              stroke="#C4A25C" strokeWidth="1.1" fill="none" strokeLinecap="round" />
        <g stroke="#D8B76A" strokeWidth="0.9" fill="none" strokeLinecap="round" opacity="0.75">
          {[12, 20, 28, 36, 44, 52].flatMap((y) => [
            <path key={`l${y}`} d={`M22 ${y} Q 14 ${y+2} 8 ${y}`} />,
            <path key={`r${y}`} d={`M22 ${y} Q 30 ${y+2} 36 ${y}`} />,
          ])}
        </g>
      </svg>
    </div>
  );
}
