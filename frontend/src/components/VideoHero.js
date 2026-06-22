import React, { useRef, useEffect } from 'react';

/**
 * Fond vidéo en boucle avec overlay + contenu — pour la homepage
 */
const VideoHero = ({ src, children, height = '100vh', overlay = true }) => {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  }, []);

  return (
    <div style={{ position: 'relative', width: '100%', height, overflow: 'hidden', minHeight: 400 }}>
      {/* Vidéo de fond */}
      <video
        ref={videoRef}
        src={src}
        autoPlay
        muted
        loop
        playsInline
        style={{
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          objectFit: 'cover', objectPosition: 'center',
        }}
      />

      {/* Overlay */}
      {overlay && (
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to bottom, rgba(12,9,24,0.5) 0%, rgba(12,9,24,0.3) 40%, rgba(12,9,24,0.8) 100%)',
        }} />
      )}

      {/* Contenu */}
      <div style={{ position: 'relative', zIndex: 1, height: '100%' }}>
        {children}
      </div>
    </div>
  );
};

export default VideoHero;
