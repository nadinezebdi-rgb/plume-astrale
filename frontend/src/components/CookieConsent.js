import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getConsent, setConsent } from '@/lib/analytics';

/**
 * Bandeau RGPD — apparait uniquement si l'utilisateur n'a pas encore
 * fait son choix. Stocke 'accepted' ou 'refused' dans localStorage.
 *
 * Tant qu'aucun choix n'est fait : aucun script tiers n'est charge.
 */
export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => {
      if (getConsent() === null) setVisible(true);
    }, 1200);
    return () => clearTimeout(t);
  }, []);

  if (!visible) return null;

  const decide = (value) => {
    setConsent(value);
    setVisible(false);
  };

  return (
    <div
      className="fixed bottom-3 left-3 right-3 sm:left-auto sm:right-6 sm:bottom-6 sm:max-w-md rounded-2xl px-5 py-4 z-50"
      style={{
        background: 'rgba(11,11,15,0.97)',
        border: '1px solid rgba(212,175,55,0.25)',
        backdropFilter: 'blur(14px)',
        boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
      }}
      role="dialog"
      aria-label="Consentement cookies"
      data-testid="cookie-consent"
    >
      <p className="text-sm mb-3" style={{ color: 'rgba(240,230,211,0.92)', fontFamily: 'Cormorant Garamond, serif', lineHeight: 1.5 }}>
        Nous utilisons quelques cookies pour comprendre comment Plume vous accompagne — uniquement avec votre accord.{' '}
        <Link to="/notre-cadre" className="underline" style={{ color: '#D4AF37' }}>En savoir plus</Link>.
      </p>
      <div className="flex gap-2">
        <button
          onClick={() => decide('refused')}
          className="flex-1 text-xs uppercase tracking-widest px-4 py-2 rounded-full"
          style={{ border: '1px solid rgba(184,176,200,0.25)', color: 'rgba(184,176,200,0.75)', letterSpacing: '0.1em' }}
          data-testid="cookie-refuse"
        >
          Refuser
        </button>
        <button
          onClick={() => decide('accepted')}
          className="flex-1 text-xs uppercase tracking-widest px-4 py-2 rounded-full"
          style={{ background: 'linear-gradient(135deg, #D4AF37, #D4AF37)', color: '#111625', letterSpacing: '0.1em', fontWeight: 600 }}
          data-testid="cookie-accept"
        >
          Accepter
        </button>
      </div>
    </div>
  );
}
