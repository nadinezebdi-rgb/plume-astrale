import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Bandeau offre de lancement — cliquable (→ /inscription), texte défilant en boucle.
 * Message unique et strict : "Crée ton compte et reçoit 20 crédits!"
 */
const LaunchBanner = () => {
  const navigate = useNavigate();

  const segment = (
    <span
      className="text-[10px] md:text-[11px] uppercase inline-flex items-center"
      style={{
        color: '#E8C766',
        letterSpacing: '0.28em',
        fontWeight: 300,
        fontFamily: 'Cinzel, Playfair Display, serif',
        whiteSpace: 'nowrap',
        paddingRight: 64,
      }}
      data-testid="launch-banner-text"
    >
      Crée ton compte et reçoit 20 crédits!
    </span>
  );

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => navigate('/inscription')}
      onKeyDown={(e) => { if (e.key === 'Enter') navigate('/inscription'); }}
      className="absolute top-0 left-0 right-0 z-40 overflow-hidden cursor-pointer"
      style={{
        height: 40,
        background: 'linear-gradient(90deg, transparent 0%, rgba(212,175,55,0.15) 20%, rgba(232,199,102,0.22) 50%, rgba(212,175,55,0.15) 80%, transparent 100%)',
        borderBottom: '1px solid rgba(212,175,55,0.35)',
        boxShadow: '0 0 24px rgba(212,175,55,0.3)',
      }}
      data-testid="launch-banner"
      aria-label="Offre de lancement — créer un compte"
    >
      <div className="plume-banner-track flex items-center h-full">
        {segment}
        {segment}
        {segment}
      </div>
    </div>
  );
};

export default LaunchBanner;
