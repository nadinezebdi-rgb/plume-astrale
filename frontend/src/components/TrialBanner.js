import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Gift, X, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const STORAGE_KEY = 'plume_trial_banner_dismissed_v1';
const DISMISS_HOURS = 24;

function getRemainingDays(createdAt) {
  if (!createdAt) return null;
  try {
    const created = new Date(createdAt).getTime();
    const elapsed = Date.now() - created;
    const trialMs = 7 * 24 * 60 * 60 * 1000;
    const remaining = Math.max(0, Math.ceil((trialMs - elapsed) / (24 * 60 * 60 * 1000)));
    return remaining;
  } catch {
    return null;
  }
}

export default function TrialBanner() {
  const { user, isAuthenticated } = useAuth();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Hide for Premium members
    if (user?.is_premium || user?.premium_status === 'active') {
      setVisible(false);
      return;
    }
    // Check dismissal expiry (24h)
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const dismissedAt = parseInt(raw, 10);
        if (Date.now() - dismissedAt < DISMISS_HOURS * 60 * 60 * 1000) {
          setVisible(false);
          return;
        }
      }
    } catch {}
    setVisible(true);
  }, [user]);

  const handleDismiss = () => {
    try { localStorage.setItem(STORAGE_KEY, String(Date.now())); } catch {}
    setVisible(false);
  };

  if (!visible) return null;

  const remainingDays = isAuthenticated ? getRemainingDays(user?.created_at) : null;
  const showCountdown = remainingDays !== null && remainingDays > 0 && remainingDays <= 7;

  return (
    <div
      data-testid="trial-banner"
      style={{
        position: 'relative',
        zIndex: 40,
        background: 'linear-gradient(90deg, rgba(212,180,106,0.18) 0%, rgba(244,217,140,0.28) 50%, rgba(212,180,106,0.18) 100%)',
        borderBottom: '1px solid rgba(212,180,106,0.35)',
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
          0%, 100% { box-shadow: 0 0 0 rgba(244,217,140,0); }
          50%      { box-shadow: 0 0 16px rgba(244,217,140,0.35); }
        }
        .trial-pulse { animation: trialBannerShine 2.4s ease-in-out infinite; }
        .trial-banner-cta {
          padding: 6px 16px;
          border-radius: 999px;
          background: #0F1230;
          color: #F4D98C;
          border: 1px solid rgba(244,217,140,0.55);
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
          background: #F4D98C;
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
          maxWidth: 1280,
          margin: '0 auto',
          padding: '8px 16px 8px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 14,
          flexWrap: 'nowrap',
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
            border: '1px solid rgba(244,217,140,0.5)',
            flexShrink: 0,
          }}
        >
          <Gift style={{ width: 14, height: 14, color: '#F4D98C' }} strokeWidth={1.8} />
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
          <strong style={{ fontFamily: 'Cinzel, serif', letterSpacing: '0.06em', color: '#F4D98C', whiteSpace: 'nowrap' }}>
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
          onMouseEnter={(e) => { e.currentTarget.style.color = '#F4D98C'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(244,228,188,0.6)'; }}
        >
          <X style={{ width: 14, height: 14 }} strokeWidth={1.5} />
        </button>
      </div>
    </div>
  );
}
