import React, { useRef, useState, useEffect } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

/**
 * SolenaVideoHero — Vidéo hero avec autoplay muted + overlay "Activer le son".
 *
 * Pattern Instagram/TikTok/Airbnb : la vidéo tourne en boucle silencieuse dès
 * qu'elle est visible, un tap sur l'overlay active le son + repart du début.
 * Cette approche multiplie par 3-4 le taux de visionnage réel du message.
 *
 * Props :
 *   src    - URL de la vidéo
 *   poster - Image de fallback (chargée avant la vidéo)
 */
const SolenaVideoHero = ({ src, poster }) => {
  const videoRef = useRef(null);
  const [muted, setMuted] = useState(true);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  // Play/pause selon la visibilité du composant (économise du CPU + data mobile)
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (!video) return;
        if (entry.isIntersecting) {
          video.play().catch(() => {}); // autoplay muted toujours autorisé
        } else {
          video.pause();
        }
      },
      { threshold: 0.25 }
    );
    io.observe(video);
    return () => io.disconnect();
  }, []);

  const handleUnmute = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = false;
    v.currentTime = 0; // repart du début pour ne pas rater l'intro
    v.play().catch(() => {});
    setMuted(false);
    setHasInteracted(true);
  };

  const handleToggleSound = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !v.muted;
    setMuted(v.muted);
  };

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        aspectRatio: '9/16',
        borderRadius: '16px',
        overflow: 'hidden',
        border: '2px solid rgba(212,175,55,0.35)',
        boxShadow: '0 40px 100px rgba(212,175,55,0.15)',
        background: '#0C1120',
      }}
    >
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        autoPlay
        muted
        loop
        playsInline
        preload="metadata"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        data-testid="solena-welcome-video"
        aria-label="Message de bienvenue de Soléna, Plume Astrale"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center 20%',
          display: 'block',
        }}
      />

      {/* Overlay initial (tant que muted && jamais interagi) */}
      {muted && !hasInteracted && (
        <button
          type="button"
          onClick={handleUnmute}
          className="group"
          data-testid="solena-video-unmute-btn"
          aria-label="Activer le son de la vidéo"
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            border: 'none',
            cursor: 'pointer',
            background:
              'radial-gradient(ellipse at center, rgba(12,17,32,0.15) 0%, rgba(12,17,32,0.55) 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            transition: 'background 0.3s ease',
          }}
        >
          <div
            style={{
              width: 76,
              height: 76,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 12px 40px rgba(212,175,55,0.55), 0 0 0 8px rgba(212,175,55,0.15)',
              transition: 'transform 0.3s ease',
            }}
            className="group-hover:scale-110"
          >
            <Volume2 style={{ width: 30, height: 30, color: '#0A0603' }} strokeWidth={2} />
          </div>
          <span
            style={{
              color: '#F4E8D2',
              fontFamily: 'Cinzel, sans-serif',
              fontSize: 12,
              letterSpacing: '0.28em',
              textTransform: 'uppercase',
              textShadow: '0 2px 12px rgba(0,0,0,0.8)',
              fontWeight: 500,
            }}
          >
            Activer le son
          </span>
        </button>
      )}

      {/* Petit bouton discret en bas à droite (une fois qu'on a interagi) */}
      {hasInteracted && (
        <button
          type="button"
          onClick={handleToggleSound}
          data-testid="solena-video-sound-toggle"
          aria-label={muted ? 'Activer le son' : 'Couper le son'}
          style={{
            position: 'absolute',
            bottom: 14,
            right: 14,
            width: 40,
            height: 40,
            borderRadius: '50%',
            border: '1px solid rgba(212,175,55,0.45)',
            background: 'rgba(12,17,32,0.65)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
        >
          {muted ? (
            <VolumeX style={{ width: 18, height: 18, color: '#E8C766' }} strokeWidth={1.7} />
          ) : (
            <Volume2 style={{ width: 18, height: 18, color: '#E8C766' }} strokeWidth={1.7} />
          )}
        </button>
      )}
    </div>
  );
};

export default SolenaVideoHero;
