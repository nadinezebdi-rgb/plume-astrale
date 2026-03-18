import React, { useMemo } from 'react';

const StarField = ({ count = 180 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const rand = Math.random();
      const isBright = rand < 0.15;
      const isMedium = rand < 0.4;
      const size = isBright ? 3 : isMedium ? 2 : 1.2;
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size,
        duration: `${2 + Math.random() * 4}s`,
        delay: `${Math.random() * 5}s`,
        peakOpacity: isBright ? 0.95 : isMedium ? 0.7 : 0.4,
        glow: isBright,
        color: isBright
          ? (Math.random() > 0.5 ? 'rgba(244,197,66,0.85)' : 'rgba(255,255,255,0.95)')
          : isMedium
            ? 'rgba(255,255,255,0.75)'
            : 'rgba(255,255,255,0.6)',
      };
    });
  }, [count]);

  return (
    <div className="starfield" aria-hidden="true">
      {/* Ambient orbs */}
      <div className="orb orb-violet" style={{ width: '500px', height: '500px', top: '5%', left: '-12%', animationDelay: '0s', opacity: 0.7 }} />
      <div className="orb orb-violet" style={{ width: '400px', height: '400px', bottom: '3%', right: '-8%', animationDelay: '-7s', opacity: 0.6 }} />
      <div className="orb orb-gold" style={{ width: '300px', height: '300px', top: '35%', right: '10%', animationDelay: '-12s', opacity: 0.4 }} />

      {/* Stars */}
      {stars.map(s => (
        <div
          key={s.id}
          className="star"
          style={{
            left: s.left,
            top: s.top,
            width: `${s.size}px`,
            height: `${s.size}px`,
            '--duration': s.duration,
            '--peak-opacity': s.peakOpacity,
            animationDelay: s.delay,
            background: s.color,
            boxShadow: s.glow
              ? `0 0 ${s.size * 4}px ${s.size * 1.5}px rgba(255,255,255,0.35), 0 0 ${s.size * 8}px ${s.size * 3}px rgba(244,197,66,0.15)`
              : `0 0 ${s.size * 2}px ${s.size}px rgba(255,255,255,0.12)`,
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
