import React, { useMemo } from 'react';

const StarField = ({ count = 160 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const rand = Math.random();
      const isBright = rand < 0.12;
      const isMedium = rand < 0.35;
      const size = isBright ? 3 : isMedium ? 2 : 1;
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size,
        duration: `${1.5 + Math.random() * 4}s`,
        delay: `${Math.random() * 4}s`,
        peakOpacity: isBright ? 1 : isMedium ? 0.75 : 0.4,
        glow: isBright,
      };
    });
  }, [count]);

  return (
    <div className="starfield" aria-hidden="true">
      {/* Ambient orbs */}
      <div className="orb orb-violet" style={{ width: '600px', height: '600px', top: '5%', left: '-12%', animationDelay: '0s' }} />
      <div className="orb orb-violet" style={{ width: '450px', height: '450px', bottom: '3%', right: '-8%', animationDelay: '-7s' }} />
      <div className="orb orb-gold" style={{ width: '350px', height: '350px', top: '35%', right: '10%', animationDelay: '-12s' }} />
      <div className="orb orb-violet" style={{ width: '300px', height: '300px', top: '60%', left: '20%', animationDelay: '-4s' }} />

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
            boxShadow: s.glow ? `0 0 ${s.size * 3}px ${s.size}px rgba(255, 255, 255, 0.3), 0 0 ${s.size * 6}px ${s.size * 2}px rgba(197, 160, 89, 0.15)` : 'none',
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
