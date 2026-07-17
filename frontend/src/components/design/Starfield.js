import React, { useMemo } from 'react';

/**
 * Ciel étoilé global — étoiles dorées scintillantes, fixed derrière le contenu.
 * A monter une seule fois dans App.js (comme NoiseOverlay).
 */
const Starfield = ({ count = 90 }) => {
  const stars = useMemo(() => Array.from({ length: count }, () => ({
    left: Math.random() * 100,
    top: Math.random() * 100,
    size: Math.random() * 1.6 + 0.7,
    delay: Math.random() * 8,
    duration: 4 + Math.random() * 6,
    opacity: 0.25 + Math.random() * 0.5,
  })), [count]);

  return (
    <div className="plume-starfield" aria-hidden="true" data-testid="plume-starfield">
      {stars.map((s, i) => (
        <span
          key={i}
          className="plume-star"
          style={{
            left: `${s.left}%`,
            top: `${s.top}%`,
            width: `${s.size}px`,
            height: `${s.size}px`,
            '--star-opacity': s.opacity,
            animationDelay: `${s.delay}s`,
            animationDuration: `${s.duration}s`,
          }}
        />
      ))}
    </div>
  );
};

export default Starfield;
