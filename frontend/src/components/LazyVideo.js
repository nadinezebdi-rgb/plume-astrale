import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * LazyVideo — Charge la vidéo uniquement au clic OU à l'entrée dans le viewport.
 *
 * Économie : le fichier vidéo (souvent 5-30 MB en 1080p) N'EST PAS téléchargé
 * tant que le composant n'est pas déclenché. Seul le poster (image) charge.
 *
 * Props :
 *   - src         : URL de la vidéo
 *   - poster      : image d'aperçu affichée avant chargement
 *   - autoLoad    : si true, charge dès que le composant entre dans le viewport
 *                   (défaut : false — on préfère un clic explicite)
 *   - onPlay/onPause : callbacks optionnels
 *   - className   : classes supplémentaires sur le wrapper
 *   - testId      : préfixe data-testid
 */
export default function LazyVideo({
  src,
  poster,
  autoLoad = false,
  onPlay,
  onPause,
  className = '',
  testId = 'lazy-video',
  ...videoProps
}) {
  const [mounted, setMounted] = useState(false);
  const [playing, setPlaying] = useState(false);
  const wrapperRef = useRef(null);
  const videoRef = useRef(null);

  // IntersectionObserver : mount when the wrapper enters viewport (only if autoLoad)
  useEffect(() => {
    if (!autoLoad || mounted) return;
    const el = wrapperRef.current;
    if (!el || typeof IntersectionObserver === 'undefined') { setMounted(true); return; }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        setMounted(true);
        io.disconnect();
      }
    }, { rootMargin: '200px 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, [autoLoad, mounted]);

  const handlePlay = useCallback(() => {
    if (!mounted) setMounted(true);
    // Petit délai pour que le <video> soit monté avant lecture
    setTimeout(() => {
      videoRef.current?.play().catch(() => {});
    }, 40);
  }, [mounted]);

  return (
    <div
      ref={wrapperRef}
      className={className}
      data-testid={testId}
      style={{ position: 'relative', width: '100%', cursor: mounted ? 'default' : 'pointer' }}
      onClick={mounted ? undefined : handlePlay}
    >
      {!mounted ? (
        <>
          <img
            src={poster}
            alt=""
            loading="lazy"
            decoding="async"
            data-testid={`${testId}-poster`}
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', borderRadius: 'inherit' }}
          />
          <div
            aria-hidden="true"
            data-testid={`${testId}-play-btn`}
            style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'linear-gradient(180deg, rgba(15,26,60,0) 40%, rgba(15,26,60,0.4) 100%)',
              borderRadius: 'inherit',
            }}
          >
            <div style={{
              width: 84, height: 84,
              borderRadius: '50%',
              background: 'rgba(201, 162, 75, 0.95)',
              color: '#0F1A3C',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 32,
              boxShadow: '0 12px 32px rgba(0,0,0,0.35)',
              transition: 'transform 0.2s ease',
              transform: 'scale(1)',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.08)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
            >
              ▶
            </div>
          </div>
        </>
      ) : (
        <video
          ref={videoRef}
          src={src}
          poster={poster}
          preload="metadata"
          playsInline
          controls
          {...videoProps}
          onPlay={(e) => { setPlaying(true); onPlay?.(e); }}
          onPause={(e) => { setPlaying(false); onPause?.(e); }}
          data-testid={`${testId}-player`}
          data-playing={playing}
          style={{ width: '100%', height: '100%', display: 'block', borderRadius: 'inherit' }}
        />
      )}
    </div>
  );
}
