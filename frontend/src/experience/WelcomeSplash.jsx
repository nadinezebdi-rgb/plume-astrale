/**
 * WelcomeSplash — bandeau de bienvenue personnalisé affiché juste après
 * l'inscription sur /mon-accueil?welcome=1. Lit l'intent stocké pendant
 * /experience et propose le service correspondant.
 *
 * Montage : conditionnel dans AuthenticatedHome.js (si ?welcome=1).
 * Style : cohérent avec le prototype /experience (noir, or, ivoire).
 */
import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { INTENT_CONFIG, readIntent } from './intentConfig';
import { zodiacByKey } from './zodiacUtils';
import { event as trackEvent } from '@/lib/analytics';

function readZodiac() {
  try { return window.sessionStorage.getItem('exp_zodiac') || null; } catch { return null; }
}

export default function WelcomeSplash({ onDismiss }) {
  const navigate = useNavigate();
  const intent = readIntent();
  const config = intent ? INTENT_CONFIG[intent] : null;
  const zodiacKey = readZodiac();
  const zodiac = zodiacKey ? zodiacByKey(zodiacKey) : null;

  useEffect(() => {
    trackEvent('recommended_service_viewed', { intent_type: intent || 'none', zodiac: zodiacKey || 'none' });
  }, [intent, zodiacKey]);

  const handleCTA = (route, kind) => () => {
    trackEvent('recommended_service_clicked', { intent_type: intent, route, kind });
    // Nettoie l'intent — le user est arrivé au bout du funnel
    try { window.sessionStorage.removeItem('exp_intent'); } catch { /* noop */ }
    navigate(route);
  };

  if (!config) {
    // Pas d'intent → simple message d'accueil, pas de recommandation
    return (
      <div style={overlayStyle} data-testid="welcome-splash-generic">
        <style>{`@keyframes welcomeFadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }`}</style>
        <div style={cardStyle}>
          <p style={eyebrowStyle}>BIENVENUE · 20 CRÉDITS OFFERTS</p>
          <h1 style={titleStyle}>Votre voyage commence.</h1>
          <p style={leadStyle}>Explorez librement votre nouveau tableau de bord.</p>
          <button type="button" onClick={onDismiss} data-testid="welcome-dismiss" style={ctaPrimary}>
            <span style={{ color: '#D8B76A' }}>✦</span> Découvrir mon espace
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={overlayStyle} data-testid="welcome-splash">
      <style>{`@keyframes welcomeFadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }`}</style>
      <div style={cardStyle}>
        {zodiac && (
          <p style={{ ...eyebrowStyle, marginBottom: 8 }} data-testid="welcome-zodiac">
            <span style={{ color: '#D8B76A', fontSize: 18, marginRight: 10 }}>{zodiac.glyph}</span>
            SIGNE {zodiac.name.toUpperCase()}
          </p>
        )}
        <p style={eyebrowStyle}>
          <span style={{ color: '#D8B76A', fontSize: 18, marginRight: 12 }}>{config.icon}</span>
          {config.label.toUpperCase()}
        </p>
        <h1 style={titleStyle} data-testid="welcome-title">{config.splashTitle}</h1>
        <p style={leadStyle}>{config.splashLead}</p>

        <div style={ctaStackStyle}>
          <button
            type="button"
            data-testid={config.primary.testid}
            onClick={handleCTA(config.primary.route, 'primary')}
            style={ctaPrimary}
          >
            <span style={{ color: '#D8B76A' }}>✦</span> {config.primary.label.toUpperCase()}
          </button>
          <button
            type="button"
            data-testid={config.secondary.testid}
            onClick={handleCTA(config.secondary.route, 'secondary')}
            style={ctaGhost}
          >
            {config.secondary.label} →
          </button>
        </div>

        <button
          type="button"
          onClick={onDismiss}
          data-testid="welcome-skip"
          style={dismissLink}
        >
          Explorer mon espace →
        </button>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: 'fixed', inset: 0, zIndex: 1000,
  background: 'radial-gradient(ellipse at 50% 40%, rgba(23, 16, 46, 0.98), rgba(7, 7, 19, 0.99))',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  padding: '32px 20px',
  animation: 'welcomeFadeIn 800ms ease-out',
};
const cardStyle = {
  maxWidth: 560, width: '100%', textAlign: 'center',
  color: '#F4EFE6', fontFamily: '"Cormorant Garamond", Georgia, serif',
};
const eyebrowStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.28em',
  color: 'rgba(216, 183, 106, 0.75)', textTransform: 'uppercase',
  margin: '0 0 22px', display: 'inline-flex', alignItems: 'center',
};
const titleStyle = {
  fontFamily: '"Cormorant Garamond", serif', fontWeight: 400,
  fontSize: 'clamp(30px, 4.5vw, 46px)', lineHeight: 1.15,
  letterSpacing: '0.01em', margin: '0 0 20px',
};
const leadStyle = {
  fontStyle: 'italic', fontSize: 'clamp(15px, 1.6vw, 18px)',
  color: 'rgba(244, 239, 230, 0.7)', margin: '0 0 40px', lineHeight: 1.6,
};
const ctaStackStyle = {
  display: 'flex', flexDirection: 'column', gap: 14, alignItems: 'center',
};
const ctaPrimary = {
  display: 'inline-flex', alignItems: 'center', gap: 12,
  padding: '16px 32px', background: 'transparent', color: '#F4EFE6',
  fontFamily: '"Inter", sans-serif', fontSize: 12, fontWeight: 400,
  letterSpacing: '0.28em', textTransform: 'uppercase',
  border: '1px solid rgba(216, 183, 106, 0.5)', borderRadius: 2,
  cursor: 'pointer', transition: 'letter-spacing 500ms ease, color 400ms ease',
};
const ctaGhost = {
  background: 'transparent', border: 'none',
  color: 'rgba(216, 183, 106, 0.85)',
  fontFamily: '"Inter", sans-serif', fontSize: 12,
  letterSpacing: '0.16em', cursor: 'pointer', padding: '10px 4px',
};
const dismissLink = {
  marginTop: 28, background: 'transparent', border: 'none',
  color: 'rgba(244, 239, 230, 0.35)',
  fontFamily: '"Inter", sans-serif', fontSize: 10.5,
  letterSpacing: '0.28em', textTransform: 'uppercase',
  cursor: 'pointer', padding: 8,
};
