import React, { useEffect, useRef, useMemo, useState } from 'react';

/**
 * CelestialBackdrop — étoiles scintillantes + étoiles filantes.
 * Empile en fond absolute derrière les sections navy.
 *
 * Props :
 *   density : nombre d'étoiles (défaut 80)
 *   shootingStars : bool (défaut true) — active les étoiles filantes
 *   interval : ms entre 2 étoiles filantes (défaut 12000, ±randomisé)
 *
 * Perf : SVG static circles + CSS animation-delay aléatoire (GPU-friendly).
 * Respecte prefers-reduced-motion (arrête le pulse + désactive shooting).
 */
export default function CelestialBackdrop({
  density = 80,
  shootingStars = true,
  interval = 12000,
}) {
  const prefersReduced = useMemo(
    () => typeof window !== 'undefined'
      && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches,
    []
  );

  // Génère positions stars une seule fois — le rendu SVG est stable.
  const stars = useMemo(() => {
    const arr = [];
    for (let i = 0; i < density; i++) {
      const size = Math.random() < 0.7 ? 1 : Math.random() < 0.9 ? 1.5 : 2.2;
      arr.push({
        id: i,
        x: Math.random() * 100,        // %
        y: Math.random() * 100,        // %
        r: size,
        delay: Math.random() * 6,      // s
        duration: 3 + Math.random() * 4, // s
        base: 0.3 + Math.random() * 0.5, // opacity min
      });
    }
    return arr;
  }, [density]);

  const [shots, setShots] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!shootingStars || prefersReduced) return;
    let timeoutId;
    const spawn = () => {
      const id = Date.now() + Math.random();
      // Départ random en haut-droite ou haut-gauche
      const fromRight = Math.random() < 0.5;
      const startX = fromRight ? 60 + Math.random() * 40 : Math.random() * 40;
      const startY = Math.random() * 30;
      const angle = fromRight ? -25 : 25;  // diagonale douce
      const shot = {
        id, startX, startY, angle,
        duration: 1400 + Math.random() * 1000,
      };
      setShots((cur) => [...cur, shot]);
      // Nettoie après l'animation
      setTimeout(() => {
        setShots((cur) => cur.filter((s) => s.id !== id));
      }, shot.duration + 200);

      // Prochain lancement
      const next = interval * (0.6 + Math.random() * 0.9);
      timeoutId = setTimeout(spawn, next);
    };
    // Premier lancement après un léger délai
    timeoutId = setTimeout(spawn, 2000 + Math.random() * 3000);
    return () => clearTimeout(timeoutId);
  }, [shootingStars, prefersReduced, interval]);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      data-testid="celestial-backdrop"
      style={{
        position: 'absolute', inset: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0,
      }}>
      <svg
        width="100%" height="100%"
        preserveAspectRatio="none"
        viewBox="0 0 100 100"
        style={{ position: 'absolute', inset: 0, display: 'block' }}>
        <defs>
          <radialGradient id="cb-star">
            <stop offset="0%" stopColor="#F7F5F0" stopOpacity="1" />
            <stop offset="60%" stopColor="#F7F5F0" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#F7F5F0" stopOpacity="0" />
          </radialGradient>
        </defs>
        {stars.map((s) => (
          <circle
            key={s.id}
            cx={s.x} cy={s.y} r={s.r / 10}
            fill="url(#cb-star)"
            style={{
              transformBox: 'fill-box',
              transformOrigin: 'center',
              animation: prefersReduced
                ? 'none'
                : `cb-twinkle ${s.duration}s ease-in-out ${s.delay}s infinite`,
              opacity: s.base,
            }}
          />
        ))}
      </svg>

      {/* Étoiles filantes */}
      {shots.map((s) => (
        <span
          key={s.id}
          data-testid="celestial-shooting-star"
          style={{
            '--rot': `${s.angle}deg`,
            position: 'absolute',
            left: `${s.startX}%`, top: `${s.startY}%`,
            width: 2, height: 2,
            transformOrigin: 'left center',
            animation: `cb-shoot ${s.duration}ms ease-out forwards`,
            pointerEvents: 'none',
          }}>
          <span style={{
            display: 'block',
            width: 120, height: 1.5,
            background: 'linear-gradient(90deg, rgba(247,245,240,0.95) 0%, rgba(201,162,75,0.9) 50%, rgba(201,162,75,0) 100%)',
            borderRadius: 999,
            filter: 'drop-shadow(0 0 4px rgba(255,235,180,0.75))',
          }} />
        </span>
      ))}

      <style>{`
        @keyframes cb-twinkle {
          0%, 100% { opacity: var(--o-low, 0.25); transform: scale(0.85); }
          50%      { opacity: 1;                  transform: scale(1.15); }
        }
        @keyframes cb-shoot {
          0%   { transform: rotate(var(--rot, -25deg)) translateX(0);      opacity: 0; }
          15%  { transform: rotate(var(--rot, -25deg)) translateX(60px);   opacity: 1; }
          80%  { transform: rotate(var(--rot, -25deg)) translateX(400px);  opacity: 0.7; }
          100% { transform: rotate(var(--rot, -25deg)) translateX(500px);  opacity: 0; }
        }
        @media (prefers-reduced-motion: reduce) {
          [data-testid="celestial-backdrop"] * { animation: none !important; }
        }
      `}</style>
    </div>
  );
}
