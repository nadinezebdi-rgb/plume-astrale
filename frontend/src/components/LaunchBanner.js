import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// Durée totale de l'offre = 48h à partir du 1er affichage (par visiteur, cookie-less
// via localStorage). Reset automatique quand la fenêtre expire → nouveau cycle 48h.
const OFFER_HOURS = 48;
const STORAGE_KEY = 'plume_offer_deadline_v1';

function getDeadline() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const d = parseInt(raw, 10);
      if (!Number.isNaN(d) && d > Date.now()) return d;
    }
  } catch { /* localStorage disabled */ }
  const d = Date.now() + OFFER_HOURS * 3600 * 1000;
  try { localStorage.setItem(STORAGE_KEY, String(d)); } catch { /* noop */ }
  return d;
}

function fmt(ms) {
  const total = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(h)}h ${pad(m)}m ${pad(s)}s`;
}

/**
 * Bandeau offre de lancement — cliquable (→ /inscription), texte défilant,
 * countdown 48h dynamique par visiteur (localStorage, cycle auto-reset).
 */
const LaunchBanner = () => {
  const navigate = useNavigate();
  const [deadline] = useState(() => (typeof window !== 'undefined' ? getDeadline() : Date.now() + OFFER_HOURS * 3600 * 1000));
  const [remaining, setRemaining] = useState(() => deadline - Date.now());

  useEffect(() => {
    const id = setInterval(() => {
      const r = deadline - Date.now();
      if (r <= 0) {
        // Cycle terminé → on relance immédiatement 48h (soft evergreen)
        try { localStorage.removeItem(STORAGE_KEY); } catch { /* noop */ }
        setRemaining(OFFER_HOURS * 3600 * 1000);
      } else {
        setRemaining(r);
      }
    }, 1000);
    return () => clearInterval(id);
  }, [deadline]);

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
    >
      ✦&nbsp;&nbsp;20 CRÉDITS OFFERTS · CODE&nbsp;
      <strong style={{ fontWeight: 800, color: '#F4D98C', letterSpacing: '0.18em' }}>PLUME2026</strong>
      &nbsp;·&nbsp;
      <span style={{ color: '#FFD87A' }}>EXPIRE DANS</span>&nbsp;
      <strong data-testid="launch-banner-countdown" style={{ fontWeight: 800, color: '#F4D98C', letterSpacing: '0.12em', fontVariantNumeric: 'tabular-nums' }}>
        {fmt(remaining)}
      </strong>
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
