import React from 'react';

/**
 * TarotCardBack — Dos de carte élégant (CSS uniquement, aucune image externe).
 * Motif célèste or sur fond midnight blue, monogramme central "P" (Plume Astrale).
 *
 * Utilisé en placeholder AVANT la révélation d'une carte tarot — remplace
 * l'ancien `<Sparkles />` lucide qui donnait un rendu générique et cassait
 * l'illusion "vraies cartes tirées d'un jeu".
 *
 * Props :
 *   size ?: { width: number, height: number } — défaut { width: 140, height: 200 }
 *   testId ?: string
 */
const TarotCardBack = ({ size = { width: 140, height: 200 }, testId }) => {
  const { width, height } = size;
  return (
    <div
      data-testid={testId || 'tarot-card-back'}
      className="tcb-root"
      style={{
        width, height,
        position: 'relative',
        borderRadius: 8,
        overflow: 'hidden',
        border: '2px solid rgba(212,175,55,0.75)',
        boxShadow:
          'inset 0 0 30px rgba(212,175,55,0.25), 0 8px 24px rgba(0,0,0,0.55), 0 0 22px rgba(212,175,55,0.18)',
        background:
          'radial-gradient(ellipse at center, #1c1740 0%, #0e0a24 55%, #06031a 100%)',
      }}
      aria-label="Dos de carte de tarot"
      role="img"
    >
      {/* Cadre or intérieur */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: '6%',
          border: '1px solid rgba(212,175,55,0.55)',
          borderRadius: 5,
          pointerEvents: 'none',
        }}
      />
      {/* Motif étoiles rayonnantes */}
      <svg
        aria-hidden="true"
        viewBox="0 0 140 200"
        preserveAspectRatio="xMidYMid slice"
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.55 }}
      >
        <defs>
          <radialGradient id="tcbGlow" cx="50%" cy="50%" r="55%">
            <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.55" />
            <stop offset="70%" stopColor="#D4AF37" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx="70" cy="100" r="66" fill="url(#tcbGlow)" />
        {/* Étoile 8 branches centrale */}
        <g transform="translate(70,100)" fill="none" stroke="#E8C766" strokeWidth="0.8" opacity="0.85">
          {Array.from({ length: 8 }, (_, i) => {
            const angle = (i * Math.PI) / 4;
            const x2 = Math.cos(angle) * 42; const y2 = Math.sin(angle) * 42;
            return <line key={i} x1="0" y1="0" x2={x2} y2={y2} />;
          })}
          <circle r="18" stroke="#D4AF37" strokeWidth="0.6" fill="none" />
          <circle r="10" stroke="#D4AF37" strokeWidth="0.5" fill="none" opacity="0.7" />
        </g>
        {/* Petites étoiles scintillantes autour */}
        {[[24,32],[116,28],[22,168],[118,172],[70,25],[70,175],[15,100],[125,100]].map(([cx, cy], i) => (
          <g key={i} transform={`translate(${cx},${cy})`} fill="#E8C766" opacity="0.8">
            <circle r="1.2" />
            <line x1="-3" y1="0" x2="3" y2="0" stroke="#E8C766" strokeWidth="0.35" />
            <line x1="0" y1="-3" x2="0" y2="3" stroke="#E8C766" strokeWidth="0.35" />
          </g>
        ))}
      </svg>
      {/* Monogramme Plume Astrale central */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'Cinzel, Playfair Display, serif',
          fontSize: Math.max(28, height * 0.22),
          color: '#F4D98C',
          textShadow: '0 0 12px rgba(212,175,55,0.6), 0 2px 4px rgba(0,0,0,0.7)',
          fontWeight: 500,
          letterSpacing: '0.02em',
        }}
      >
        ✦
      </div>
      {/* Micro texte marque en bas */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', bottom: 8, left: 0, right: 0, textAlign: 'center',
          fontFamily: 'Cinzel, serif',
          fontSize: Math.max(7, height * 0.045),
          color: 'rgba(212,175,55,0.7)',
          letterSpacing: '0.35em',
          textTransform: 'uppercase',
        }}
      >
        Plume Astrale
      </div>

      <style>{`
        .tcb-root { animation: tcb-breath 4.5s ease-in-out infinite; }
        @keyframes tcb-breath {
          0%, 100% { box-shadow: inset 0 0 30px rgba(212,175,55,0.2), 0 8px 24px rgba(0,0,0,0.55), 0 0 18px rgba(212,175,55,0.15); }
          50%      { box-shadow: inset 0 0 34px rgba(212,175,55,0.3), 0 8px 24px rgba(0,0,0,0.55), 0 0 30px rgba(212,175,55,0.32); }
        }
      `}</style>
    </div>
  );
};

export default TarotCardBack;
