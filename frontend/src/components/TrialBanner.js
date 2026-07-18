import React from 'react';
import { useLocation } from 'react-router-dom';

// Routes where banner should NOT appear (premium/payment/auth flows)
const HIDE_ON_PATHS = ['/premium', '/paiement', '/credits/succes', '/commande/succes', '/inscription', '/connexion'];

export default function TrialBanner() {
  const location = useLocation();

  const onHiddenRoute = HIDE_ON_PATHS.some((p) => location.pathname.startsWith(p));
  if (onHiddenRoute) return null;

  return (
    <div
      data-testid="trial-banner"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 40,
        background: 'linear-gradient(90deg, rgba(212,175,55,0.18) 0%, rgba(232,199,102,0.28) 50%, rgba(212,175,55,0.18) 100%)',
        borderBottom: '1px solid rgba(212,175,55,0.35)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        animation: 'trialBannerSlide 0.6s ease-out',
      }}
    >
      <style>{`
        @keyframes trialBannerSlide {
          from { transform: translateY(-100%); opacity: 0; }
          to   { transform: translateY(0); opacity: 1; }
        }
        @keyframes trialBannerShine {
          0%, 100% { box-shadow: 0 0 0 rgba(232,199,102,0); }
          50%      { box-shadow: 0 0 16px rgba(232,199,102,0.35); }
        }
        .trial-pulse { animation: trialBannerShine 2.4s ease-in-out infinite; }
        .trial-banner-cta {
          padding: 6px 16px;
          border-radius: 999px;
          background: #0F1230;
          color: #E8C766;
          border: 1px solid rgba(232,199,102,0.55);
          font-family: 'Cinzel, serif';
          font-size: 11px;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          font-weight: 600;
          text-decoration: none;
          white-space: nowrap;
          transition: all 0.25s ease;
        }
        .trial-banner-cta:hover {
          background: #E8C766;
          color: #0F1230;
          transform: translateY(-1px);
        }
        @media (max-width: 640px) {
          .trial-text-long { display: none; }
          .trial-banner-cta { font-size: 10px; padding: 5px 12px; letter-spacing: 0.1em; }
        }
        @media (min-width: 641px) {
          .trial-text-short { display: none; }
        }
      `}</style>

      <div
        style={{
          margin: 0,
          fontFamily: '"Inter", system-ui, sans-serif',
          fontSize: 12,
          fontWeight: 400,
          color: '#000000',
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
        }}
      >
        <div
          className="trial-pulse"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 28,
            height: 28,
            borderRadius: '50%',
            background: 'rgba(15,18,48,0.7)',
            border: '1px solid rgba(232,199,102,0.5)',
            flexShrink: 0,
          }}
        >
          <Gift style={{ width: 14, height: 14, color: '#E8C766' }} strokeWidth={1.8} />
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            color: '#F4E4BC',
            fontSize: 13,
            lineHeight: 1.3,
            fontFamily: '"Inter", system-ui, sans-serif',
            flex: '1 1 auto',
            minWidth: 0,
          }}
        >
          <strong style={{ fontFamily: 'Cinzel, serif', letterSpacing: '0.06em', color: '#E8C766', whiteSpace: 'nowrap' }}>
            {showCountdown ? `${remainingDays}j` : '7 jours'}
          </strong>
          <span className="trial-text-long" style={{ color: 'rgba(244,228,188,0.85)' }}>
            {showCountdown
              ? `restant${remainingDays > 1 ? 's' : ''} sur ton essai gratuit Premium`
              : "d'essai gratuit Premium — annulable a tout moment, aucun debit"}
          </span>
          <span className="trial-text-short" style={{ color: 'rgba(244,228,188,0.85)', whiteSpace: 'nowrap' }}>
            {showCountdown ? 'essai restant' : "d'essai gratuit"}
          </span>
        </div>

        <Link
          to="/premium"
          className="trial-banner-cta"
          data-testid="trial-banner-cta"
        >
          <Sparkles style={{ width: 11, height: 11, display: 'inline', marginRight: 4 }} />
          {showCountdown ? 'Gerer' : 'En profiter'}
        </Link>

        <button
          onClick={handleDismiss}
          aria-label="Fermer la banniere"
          data-testid="trial-banner-close"
          style={{
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            padding: 4,
            color: 'rgba(244,228,188,0.6)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = '#E8C766'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(244,228,188,0.6)'; }}
        >
          <X style={{ width: 14, height: 14 }} strokeWidth={1.5} />
        </button>
      </div>
    </div>
  );
}
