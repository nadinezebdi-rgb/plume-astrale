import React, { useRef, useCallback } from 'react';

/**
 * Bannière visuelle en haut de chaque page — image + overlay + titre
 * Props:
 *   image    : chemin relatif (ex: "/images/astrale/image-astrale2.jpg")
 *   title    : titre principal
 *   subtitle : sous-titre optionnel
 *   height   : hauteur (défaut "280px")
 *   align    : "center" | "left" (défaut "center")
 *   enable3D : active l'effet 3D au survol (défaut true)
 */
const PageHero = ({ image, title, subtitle, height = '280px', align = 'center', enable3D = true }) => {
  const ref = useRef(null);
  const raf = useRef(null);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const active = enable3D && !prefersReducedMotion;

  const handleMouseMove = useCallback((e) => {
    const el = ref.current;
    if (!el || !active) return;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    const max = 6;
    cancelAnimationFrame(raf.current);
    raf.current = requestAnimationFrame(() => {
      el.style.transform =
        `perspective(1200px) rotateX(${(-py * max).toFixed(2)}deg) rotateY(${(px * max).toFixed(2)}deg) scale(1.015)`;
    });
  }, [active]);

  const handleMouseLeave = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    cancelAnimationFrame(raf.current);
    el.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) scale(1)';
  }, []);

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        position: 'relative',
        width: '100%',
        height,
        overflow: 'hidden',
        borderRadius: '0 0 24px 24px',
        marginBottom: 32,
        transformStyle: 'preserve-3d',
        transition: 'transform 350ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 350ms cubic-bezier(0.22, 1, 0.36, 1)',
        boxShadow: active
          ? '0 30px 60px -20px rgba(0,0,0,0.75), 0 12px 24px -12px rgba(212,175,55,0.20), inset 0 1px 0 rgba(255,215,150,0.10)'
          : 'none',
        willChange: 'transform',
      }}
    >
      {/* Image de fond */}
      {image && (
        <img
          src={image}
          alt=""
          style={{
            position: 'absolute', inset: 0,
            width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'center top',
          }}
        />
      )}

      {/* Overlay dégradé */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(to bottom, rgba(12,9,24,0.35) 0%, rgba(12,9,24,0.75) 70%, rgba(12,9,24,0.97) 100%)',
      }} />

      {/* Contenu */}
      <div style={{
        position: 'relative', zIndex: 1,
        height: '100%',
        display: 'flex', flexDirection: 'column',
        alignItems: align === 'center' ? 'center' : 'flex-start',
        justifyContent: 'flex-end',
        padding: align === 'center' ? '0 24px 32px' : '0 32px 32px',
        textAlign: align,
      }}>
        {title && (
          <h1 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(28px, 5vw, 42px)',
            fontWeight: 300,
            color: '#F0E6D3',
            lineHeight: 1.1,
            marginBottom: subtitle ? 8 : 0,
            textShadow: '0 2px 16px rgba(0,0,0,0.7)',
          }}>
            {title}
          </h1>
        )}
        {subtitle && (
          <p style={{
            fontSize: 'clamp(12px, 2vw, 14px)',
            color: 'rgba(197,160,89,0.85)',
            fontWeight: 300,
            letterSpacing: '0.04em',
            textShadow: '0 1px 8px rgba(0,0,0,0.6)',
            maxWidth: 520,
          }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};

export default PageHero;
