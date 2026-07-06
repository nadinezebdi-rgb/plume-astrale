import React from 'react';

/**
 * Bannière visuelle en haut de chaque page — image + overlay + titre
 * Props:
 *   image     : chemin relatif (ex: "/images/astrale/image-astrale2.jpg")
 *   title     : titre principal
 *   subtitle  : sous-titre optionnel
 *   height    : hauteur (défaut "280px")
 *   align     : "center" | "left" (défaut "center")
 */
const PageHero = ({ image, title, subtitle, height = '280px', align = 'center' }) => (
  <div
    style={{
      position: 'relative',
      width: '100%',
      height,
      overflow: 'hidden',
      borderRadius: '0 0 24px 24px',
      marginBottom: 32,
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

export default PageHero;
