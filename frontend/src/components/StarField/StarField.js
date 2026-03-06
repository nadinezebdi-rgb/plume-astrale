import React, { useMemo } from 'react';

const StarField = ({ count = 260 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const rand = Math.random();
      const isBright = rand < 0.2;
      const isMedium = rand < 0.5;
      const size = isBright ? 3.5 : isMedium ? 2.5 : 1.5;
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size,
        duration: `${1.2 + Math.random() * 3}s`,
        delay: `${Math.random() * 3}s`,
        peakOpacity: isBright ? 1 : isMedium ? 0.85 : 0.55,
        glow: isBright || isMedium,
        color: isBright
          ? (Math.random() > 0.5 ? 'rgba(244,197,66,0.9)' : 'rgba(255,255,255,0.95)')
          : 'rgba(255,255,255,0.8)',
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
            background: s.color,
            boxShadow: s.glow
              ? `0 0 ${s.size * 4}px ${s.size * 1.5}px rgba(255,255,255,0.4), 0 0 ${s.size * 8}px ${s.size * 3}px rgba(244,197,66,0.2)`
              : `0 0 ${s.size * 2}px ${s.size}px rgba(255,255,255,0.15)`,
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
