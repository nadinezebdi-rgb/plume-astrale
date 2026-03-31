import React, { useMemo } from 'react';

const StarField = ({ count = 320 }) => {
  const stars = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const rand = Math.random();
      const isBright  = rand < 0.18;
      const isMedium  = rand < 0.45;
      const isViolet  = rand > 0.72 && rand < 0.88;
      const isGold    = rand >= 0.88 && rand < 0.96;

      const size = isBright ? 3.8 : isMedium ? 2.6 : 1.6;

      let color;
      if (isGold)        color = 'rgba(212,180,106,0.95)';
      else if (isViolet) color = `rgba(${180 + Math.floor(Math.random()*40)},${120 + Math.floor(Math.random()*40)},255,0.9)`;
      else if (isBright) color = 'rgba(255,255,255,0.98)';
      else               color = `rgba(220,215,255,${0.55 + Math.random()*0.3})`;

      let boxShadow;
      if (isGold) {
        boxShadow = `0 0 ${size * 5}px ${size * 2}px rgba(212,180,106,0.55), 0 0 ${size * 10}px ${size * 4}px rgba(212,180,106,0.2)`;
      } else if (isViolet) {
        boxShadow = `0 0 ${size * 5}px ${size * 2}px rgba(160,100,255,0.6), 0 0 ${size * 10}px ${size * 4}px rgba(130,60,255,0.25)`;
      } else if (isBright) {
        boxShadow = `0 0 ${size * 4}px ${size * 1.5}px rgba(255,255,255,0.45), 0 0 ${size * 8}px ${size * 3}px rgba(200,180,255,0.2)`;
      } else {
        boxShadow = `0 0 ${size * 2}px ${size}px rgba(255,255,255,0.15)`;
      }

      const animName = isBright ? 'twinkle' : (Math.random() > 0.5 ? 'twinkle-slow' : 'twinkle-fast');

      return {
        id: i,
        left: `${Math.random() * 100}%`,
        top:  `${Math.random() * 100}%`,
        size,
        duration: `${1.5 + Math.random() * 4.5}s`,
        delay:    `${Math.random() * 5}s`,
        peakOpacity: isBright ? 1 : isMedium ? 0.88 : 0.60,
        color,
        boxShadow,
        animName,
      };
    });
  }, [count]);

  const shootingStars = useMemo(() => (
    Array.from({ length: 3 }, (_, i) => ({
      id: i,
      top:   `${10 + i * 20}%`,
      delay: `${4 + i * 8}s`,
      width: `${80 + i * 20}px`,
    }))
  ), []);

  return (
    <div className="starfield" aria-hidden="true">
      {/* Nébuleuses violettes */}
      <div className="orb orb-violet" style={{ width: '700px', height: '700px', top: '2%',  left: '-15%', animationDelay: '0s' }} />
      <div className="orb orb-violet" style={{ width: '500px', height: '500px', bottom: '2%', right: '-10%', animationDelay: '-7s' }} />
      <div className="orb orb-gold"   style={{ width: '380px', height: '380px', top: '35%', right: '8%',   animationDelay: '-12s' }} />
      <div className="orb orb-violet" style={{ width: '340px', height: '340px', top: '58%', left: '18%',  animationDelay: '-4s' }} />
      <div className="orb orb-violet" style={{ width: '260px', height: '260px', top: '15%', left: '40%',  animationDelay: '-9s', opacity: 0.6 }} />

      {/* Étoiles filantes */}
      {shootingStars.map(s => (
        <div
          key={s.id}
          className="shooting-star"
          style={{ top: s.top, width: s.width, animationDelay: s.delay }}
        />
      ))}

      {/* Étoiles scintillantes */}
      {stars.map(s => (
        <div
          key={s.id}
          className="star"
          style={{
            left: s.left,
            top:  s.top,
            width:  `${s.size}px`,
            height: `${s.size}px`,
            '--peak-opacity':     s.peakOpacity,
            animationName:     s.animName,
            animationDuration: s.duration,
            animationDelay:    s.delay,
            background: s.color,
            boxShadow:  s.boxShadow,
            borderRadius: '50%',
          }}
        />
      ))}
    </div>
  );
};

export default StarField;
