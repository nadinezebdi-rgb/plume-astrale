import React, { useEffect } from 'react';

/**
 * Grain SVG 3% opacite fixed en overlay + Souffle Astral (pulsation 12s).
 * Evite le banding OLED + effet ciel etoile subtil.
 * A monter une seule fois dans App.js.
 */
const NoiseOverlay = () => {
  useEffect(() => {
    // Detect prefers-reduced-motion pour ne pas animer inutilement
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const el = document.querySelector('.plume-noise-overlay');
    if (mq.matches && el) {
      el.style.animation = 'none';
      el.style.opacity = '0.03';
    }
  }, []);

  return <div className="plume-noise-overlay" aria-hidden="true" data-testid="plume-noise-overlay" />;
};

export default NoiseOverlay;
