import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const DURATION_MS = 48 * 3600 * 1000;

function getDeadline() {
  try {
    const stored = parseInt(localStorage.getItem('pa_offer_deadline') || '0', 10);
    if (stored && stored > Date.now()) return stored;
    const fresh = Date.now() + DURATION_MS;
    localStorage.setItem('pa_offer_deadline', String(fresh));
    return fresh;
  } catch (e) {
    return Date.now() + DURATION_MS;
  }
}

function fmt(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${String(h).padStart(2, '0')}H ${String(m).padStart(2, '0')}M ${String(sec).padStart(2, '0')}S`;
}

/**
 * Bandeau offre de lancement — cliquable (→ /inscription), texte défilant,
 * « VALABLE SUR TOUT LE SITE » en gras + compte à rebours 48 heures.
 */
const LaunchBanner = () => {
  const navigate = useNavigate();
  const [deadline, setDeadline] = useState(getDeadline);
  const [left, setLeft] = useState(deadline - Date.now());

  useEffect(() => {
    const id = setInterval(() => {
      const remaining = deadline - Date.now();
      if (remaining <= 0) {
        const fresh = getDeadline();
        setDeadline(fresh);
        setLeft(fresh - Date.now());
      } else {
        setLeft(remaining);
      }
    }, 1000);
    return () => clearInterval(id);
  }, [deadline]);

  const segment = (
    <span
      className="text-[10px] md:text-[11px] uppercase inline-flex items-center"
      style={{ color: '#E8C766', letterSpacing: '0.28em', fontWeight: 300, fontFamily: 'Cinzel, Playfair Display, serif', whiteSpace: 'nowrap', paddingRight: 64 }}
    >
      ✦&nbsp;&nbsp;OFFRE DE LANCEMENT&nbsp;·&nbsp;20 CRÉDITS OFFERTS À L&apos;INSCRIPTION&nbsp;·&nbsp;
      <strong style={{ fontWeight: 800, color: '#F4D98C' }}>VALABLE SUR TOUT LE SITE</strong>
      &nbsp;·&nbsp;⏳ OFFRE VALABLE 48 HEURES —&nbsp;
      <strong style={{ fontWeight: 800, color: '#F4D98C', fontVariantNumeric: 'tabular-nums' }}>{fmt(left)}</strong>
      &nbsp;&nbsp;✦
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
