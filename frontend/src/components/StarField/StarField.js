import React, { useMemo } from 'react';

const StarField = ({ count = 80 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const size = Math.random() < 0.15 ? 2.5 : Math.random() < 0.4 ? 1.5 : 1;
      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        size,
        duration: `${3 + Math.random() * 6}s`,
        delay: `${Math.random() * 5}s`,
        peakOpacity: size > 2 ? 0.9 : size > 1 ? 0.6 : 0.35,
      };
    });
  }, [count]);

  return (
    <div className="starfield" aria-hidden="true">
      {/* Ambient orbs */}
      <div className="orb orb-violet" style={{ width: '500px', height: '500px', top: '10%', left: '-10%', animationDelay: '0s' }} />
      <div className="orb orb-violet" style={{ width: '400px', height: '400px', bottom: '5%', right: '-5%', animationDelay: '-7s' }} />
      <div className="orb orb-gold" style={{ width: '300px', height: '300px', top: '40%', right: '15%', animationDelay: '-12s' }} />

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
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
