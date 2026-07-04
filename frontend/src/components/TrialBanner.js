import React from 'react';
import { useLocation, Link } from 'react-router-dom';

// Routes where banner should NOT appear (premium/payment/auth flows)
const HIDE_ON_PATHS = ['/premium', '/paiement', '/credits/succes', '/commande/succes', '/inscription', '/connexion'];

export default function TrialBanner() {
  const location = useLocation();

  const onHiddenRoute = HIDE_ON_PATHS.some((p) => location.pathname.startsWith(p));
  if (onHiddenRoute) return null;

  return (
    <Link
      to="/inscription"
      data-testid="trial-banner"
      style={{
        display: 'block',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        background: 'linear-gradient(90deg, #D4AF37 0%, #F0D060 50%, #AA7C11 100%)',
        padding: '8px 16px',
        textAlign: 'center',
        textDecoration: 'none',
        cursor: 'pointer',
      }}
    >
      <p
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
        ✨ OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L&apos;INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX ✨
      </p>
    </Link>
  );
}
