import React, { useEffect, useState, useCallback, useRef } from 'react';

/**
 * ShootingStars — Étoiles filantes dorées discrètes, globales.
 * Une étoile toutes les ~8-12s, en diagonale. À monter une fois dans App.js
 * à côté de <Starfield />. CSS dans index.css (.plume-shooting-star).
 */
const ShootingStars = () => {
  const [stars, setStars] = useState([]);
  const idRef = useRef(0);

  const spawn = useCallback(() => {
    const id = idRef.current++;
    // Position de départ dans le quart haut-gauche de l'écran
    const top = Math.random() * 40;        // 0-40% du haut
    const left = Math.random() * 60;       // 0-60% de la gauche
    const duration = 1.1 + Math.random() * 0.8; // 1.1s à 1.9s de traînée
    setStars((prev) => [...prev, { id, top, left, duration }]);
    // Nettoyage après l'animation
    setTimeout(() => {
      setStars((prev) => prev.filter((s) => s.id !== id));
    }, duration * 1000 + 200);
  }, []);

  useEffect(() => {
    let timer;
    const loop = () => {
      spawn();
      const next = 8000 + Math.random() * 4000; // 8 à 12 secondes
      timer = setTimeout(loop, next);
    };
    // Premier lancement après un court délai
    timer = setTimeout(loop, 3000);
    return () => clearTimeout(timer);
  }, [spawn]);

  return (
    <div className="plume-shooting-layer" aria-hidden="true" data-testid="plume-shooting-stars">
      {stars.map((s) => (
        <span
          key={s.id}
          className="plume-shooting-star"
          style={{
            top: `${s.top}%`,
            left: `${s.left}%`,
            animationDuration: `${s.duration}s`,
          }}
        />
      ))}
    </div>
  );
};

export default ShootingStars;
