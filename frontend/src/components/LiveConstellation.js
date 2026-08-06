import React, { useMemo } from 'react';

/**
 * LiveConstellation — SVG constellation vivante.
 *
 * Rendu :
 *   - Étoiles principales qui pulsent (scale 1↔1.2, opacity 0.85↔1)
 *   - Lignes dorées tracées au chargement via stroke-dasharray
 *   - Le container tourne de 360° sur 2min (imperceptible, hypnotique)
 *
 * Props :
 *   sign : 'aquarius' | 'pisces' | 'orion' (défaut 'aquarius')
 *   size : px, défaut 380
 */

const CONSTELLATIONS = {
  // Verseau — Sadalmelik, Sadalsuud, Sadachbia, Skat, Ancha, Albali, Situla
  aquarius: {
    label: 'Verseau',
    stars: [
      { id: 'sadalmelik', x: 68, y: 22, r: 3.2, brightness: 1 },
      { id: 'sadalsuud',  x: 46, y: 30, r: 3.6, brightness: 1 },
      { id: 'sadachbia',  x: 82, y: 40, r: 2.5, brightness: 0.9 },
      { id: 'skat',       x: 74, y: 68, r: 3.0, brightness: 1 },
      { id: 'ancha',      x: 68, y: 45, r: 2.2, brightness: 0.85 },
      { id: 'albali',     x: 28, y: 50, r: 2.4, brightness: 0.9 },
      { id: 'situla',     x: 58, y: 12, r: 2.0, brightness: 0.8 },
      { id: 'lambda',     x: 82, y: 55, r: 2.4, brightness: 0.85 },
      { id: 'psi',        x: 60, y: 80, r: 2.6, brightness: 0.9 },
    ],
    lines: [
      ['situla', 'sadalmelik'],
      ['sadalmelik', 'sadalsuud'],
      ['sadalmelik', 'ancha'],
      ['sadalsuud', 'albali'],
      ['ancha', 'sadachbia'],
      ['ancha', 'skat'],
      ['sadachbia', 'lambda'],
      ['skat', 'psi'],
    ],
  },

  pisces: {
    label: 'Poissons',
    stars: [
      { id: 'alpherg',   x: 30, y: 30, r: 3.2, brightness: 1 },
      { id: 'eta',       x: 46, y: 25, r: 2.8, brightness: 0.95 },
      { id: 'gamma',     x: 60, y: 35, r: 2.6, brightness: 0.9 },
      { id: 'omega',     x: 70, y: 50, r: 2.4, brightness: 0.85 },
      { id: 'iota',      x: 78, y: 68, r: 2.6, brightness: 0.9 },
      { id: 'lambda',    x: 62, y: 75, r: 2.2, brightness: 0.8 },
      { id: 'kappa',     x: 46, y: 68, r: 2.4, brightness: 0.85 },
      { id: 'delta',     x: 34, y: 55, r: 2.6, brightness: 0.9 },
      { id: 'nu',        x: 22, y: 45, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['alpherg', 'eta'],
      ['eta', 'gamma'],
      ['gamma', 'omega'],
      ['omega', 'iota'],
      ['iota', 'lambda'],
      ['lambda', 'kappa'],
      ['kappa', 'delta'],
      ['delta', 'nu'],
      ['nu', 'alpherg'],
    ],
  },
};

export default function LiveConstellation({ sign = 'aquarius', size = 380 }) {
  const constellation = CONSTELLATIONS[sign] || CONSTELLATIONS.aquarius;

  const byId = useMemo(() => {
    const m = {};
    constellation.stars.forEach((s) => { m[s.id] = s; });
    return m;
  }, [constellation]);

  return (
    <div
      aria-hidden="true"
      data-testid="live-constellation"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 0,
      }}>
      <div style={{
        width: size, height: size,
        animation: 'lc-rotate 120s linear infinite',
      }}>
        <svg
          viewBox="0 0 100 100"
          width="100%" height="100%"
          style={{ overflow: 'visible' }}>
          <defs>
            <radialGradient id="lc-glow">
              <stop offset="0%"  stopColor="#F7F5F0" stopOpacity="1" />
              <stop offset="50%" stopColor="#C9A24B" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#C9A24B" stopOpacity="0" />
            </radialGradient>
            <filter id="lc-star-glow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="0.6" />
              <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Lignes — dessinées progressivement */}
          {constellation.lines.map(([a, b], i) => {
            const sa = byId[a]; const sb = byId[b];
            if (!sa || !sb) return null;
            return (
              <line
                key={i}
                x1={sa.x} y1={sa.y}
                x2={sb.x} y2={sb.y}
                stroke="#C9A24B"
                strokeWidth="0.15"
                strokeOpacity="0.55"
                strokeLinecap="round"
                style={{
                  strokeDasharray: '200',
                  strokeDashoffset: '200',
                  animation: `lc-draw 2200ms ease-out ${1 + i * 0.35}s forwards`,
                }}
              />
            );
          })}

          {/* Étoiles — pulsent */}
          {constellation.stars.map((s, i) => (
            <g key={s.id}>
              {/* Halo */}
              <circle
                cx={s.x} cy={s.y}
                r={s.r * 1.6}
                fill="url(#lc-glow)"
                style={{
                  transformBox: 'fill-box',
                  transformOrigin: 'center',
                  opacity: 0.45 * s.brightness,
                  animation: `lc-pulse-halo 4.5s ease-in-out ${i * 0.4}s infinite`,
                }}
              />
              {/* Cœur */}
              <circle
                cx={s.x} cy={s.y}
                r={s.r * 0.35}
                fill="#F7F5F0"
                filter="url(#lc-star-glow)"
                style={{
                  transformBox: 'fill-box',
                  transformOrigin: 'center',
                  opacity: 0.85 * s.brightness,
                  animation: `lc-pulse-core 4.5s ease-in-out ${i * 0.4}s infinite`,
                }}
              />
            </g>
          ))}
        </svg>
      </div>

      <style>{`
        @keyframes lc-rotate {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes lc-draw {
          from { stroke-dashoffset: 200; }
          to   { stroke-dashoffset: 0; }
        }
        @keyframes lc-pulse-halo {
          0%, 100% { transform: scale(0.85); opacity: 0.28; }
          50%      { transform: scale(1.15); opacity: 0.55; }
        }
        @keyframes lc-pulse-core {
          0%, 100% { transform: scale(1); opacity: 0.82; }
          50%      { transform: scale(1.25); opacity: 1; }
        }
        @media (prefers-reduced-motion: reduce) {
          [data-testid="live-constellation"] * { animation: none !important; }
        }
      `}</style>
    </div>
  );
}
