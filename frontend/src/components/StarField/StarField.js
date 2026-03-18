import React, { useMemo } from 'react';

const StarField = ({ count = 60 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const rand = Math.random();
      const isBright = rand < 0.1;
      const isMedium = rand < 0.35;
      const size = isBright ? 2.5 : isMedium ? 1.8 : 1;
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size,
        duration: `${2 + Math.random() * 4}s`,
        delay: `${Math.random() * 4}s`,
        peakOpacity: isBright ? 0.7 : isMedium ? 0.5 : 0.3,
        glow: isBright,
        color: isBright
          ? (Math.random() > 0.5 ? 'rgba(244,197,66,0.6)' : 'rgba(255,255,255,0.7)')
          : 'rgba(255,255,255,0.5)',
      };
    });
  }, [count]);

  return (
    <div className="starfield" aria-hidden="true">
      {/* Ambient orbs */}
      <div className="orb orb-violet" style={{ width: '400px', height: '400px', top: '5%', left: '-12%', animationDelay: '0s', opacity: 0.5 }} />
      <div className="orb orb-violet" style={{ width: '300px', height: '300px', bottom: '3%', right: '-8%', animationDelay: '-7s', opacity: 0.4 }} />
      <div className="orb orb-gold" style={{ width: '250px', height: '250px', top: '35%', right: '10%', animationDelay: '-12s', opacity: 0.3 }} />

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
              ? `0 0 ${s.size * 3}px ${s.size}px rgba(255,255,255,0.2), 0 0 ${s.size * 5}px ${s.size * 2}px rgba(244,197,66,0.1)`
              : `0 0 ${s.size}px ${s.size * 0.5}px rgba(255,255,255,0.08)`,
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
