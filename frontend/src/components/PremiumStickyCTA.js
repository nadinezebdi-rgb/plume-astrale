import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

/**
 * Sticky bottom-fixed CTA Premium (mobile only).
 * Visible sur les pages cles, masquee sur les pages dejà commerciales / admin / auth.
 */
const HIDE_ON = [
  '/premium', '/paiement', '/admin', '/connexion', '/inscription',
  '/mot-de-passe-oublie', '/reinitialiser-mot-de-passe',
  '/credits/succes', '/commande/succes', '/acheter-credits',
];

const PremiumStickyCTA = () => {
  const location = useLocation();
  const { user } = useAuth();
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    // Cache si user deja Premium
    if (user?.is_premium) setHidden(true);
    else setHidden(false);
  }, [user]);

  // Cache sur certaines pages
  const path = location.pathname;
  const onExcludedPath = HIDE_ON.some(p => path.startsWith(p));
  if (hidden || onExcludedPath) return null;

  return (
    <div
      data-testid="premium-sticky-cta"
      className="premium-sticky-cta"
      style={{
        position: 'fixed',
        left: 0, right: 0, bottom: 0, zIndex: 45,
        padding: '10px 16px calc(10px + env(safe-area-inset-bottom, 0px))',
        background: 'linear-gradient(180deg, rgba(11,9,24,0.55) 0%, rgba(11,9,24,0.95) 60%)',
        backdropFilter: 'blur(14px)',
        borderTop: '1px solid rgba(212,180,106,0.18)',
        pointerEvents: 'none',
      }}
    >
      <Link
        to="/premium"
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
          padding: '16px 20px', borderRadius: 999,
          background: 'linear-gradient(135deg, #D4B46A 0%, #C5A059 100%)',
          color: '#0C0918', fontWeight: 700,
          fontSize: 13, letterSpacing: '0.14em', textTransform: 'uppercase',
          textDecoration: 'none', minHeight: 56,
          boxShadow: '0 6px 24px rgba(212,180,106,0.45)',
          pointerEvents: 'auto',
        }}
        data-testid="premium-sticky-cta-link"
      >
        ✦ L'Expérience Premium
      </Link>
      <style>{`
        @media (min-width: 1024px) { .premium-sticky-cta { display: none !important; } }
      `}</style>
    </div>
  );
};

export default PremiumStickyCTA;
