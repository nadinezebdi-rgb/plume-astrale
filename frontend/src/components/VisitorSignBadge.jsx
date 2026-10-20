import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Keep in sync with ExploreUniversSection & Quotidien.
const SIGN_FR_SYMBOL = {
  Aries: ['Bélier', '♈'],
  Taurus: ['Taureau', '♉'],
  Gemini: ['Gémeaux', '♊'],
  Cancer: ['Cancer', '♋'],
  Leo: ['Lion', '♌'],
  Virgo: ['Vierge', '♍'],
  Libra: ['Balance', '♎'],
  Scorpio: ['Scorpion', '♏'],
  Sagittarius: ['Sagittaire', '♐'],
  Capricorn: ['Capricorne', '♑'],
  Aquarius: ['Verseau', '♒'],
  Pisces: ['Poissons', '♓'],
};

function getZodiacSign(dateStr) {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return null;
  const m = d.getMonth() + 1;
  const day = d.getDate();
  if ((m === 3 && day >= 21) || (m === 4 && day <= 19)) return 'Aries';
  if ((m === 4 && day >= 20) || (m === 5 && day <= 20)) return 'Taurus';
  if ((m === 5 && day >= 21) || (m === 6 && day <= 20)) return 'Gemini';
  if ((m === 6 && day >= 21) || (m === 7 && day <= 22)) return 'Cancer';
  if ((m === 7 && day >= 23) || (m === 8 && day <= 22)) return 'Leo';
  if ((m === 8 && day >= 23) || (m === 9 && day <= 22)) return 'Virgo';
  if ((m === 9 && day >= 23) || (m === 10 && day <= 22)) return 'Libra';
  if ((m === 10 && day >= 23) || (m === 11 && day <= 21)) return 'Scorpio';
  if ((m === 11 && day >= 22) || (m === 12 && day <= 21)) return 'Sagittarius';
  if ((m === 12 && day >= 22) || (m === 1 && day <= 19)) return 'Capricorn';
  if ((m === 1 && day >= 20) || (m === 2 && day <= 18)) return 'Aquarius';
  return 'Pisces';
}

/**
 * Pastille signe + mini-popup "horoscope du jour" au hover.
 *
 * - Lit `localStorage.plume_astrale_data.dateNaissance` → calcule signe
 * - Au premier hover, fetch /api/daily/{sign} et cache en mémoire pour la session
 * - Popup affiche la phrase du jour + lien "Lire tout mon horoscope"
 */
export default function VisitorSignBadge() {
  const [sign, setSign] = useState(null);
  const [daily, setDaily] = useState(null);
  const [showPopup, setShowPopup] = useState(false);
  const closeTimer = useRef(null);

  useEffect(() => {
    const read = () => {
      try {
        const raw = localStorage.getItem('plume_astrale_data');
        if (!raw) { setSign(null); return; }
        const parsed = JSON.parse(raw);
        setSign(getZodiacSign(parsed?.dateNaissance));
      } catch (_) {
        setSign(null);
      }
    };
    read();
    window.addEventListener('storage', read);
    window.addEventListener('plume-sign-updated', read);
    return () => {
      window.removeEventListener('storage', read);
      window.removeEventListener('plume-sign-updated', read);
    };
  }, []);

  const fetchDaily = () => {
    if (!sign || daily || !API_URL) return;
    fetch(`${API_URL}/api/daily/${sign}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (data) setDaily(data); })
      .catch(() => { /* noop */ });
  };

  const openNow = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    fetchDaily();
    setShowPopup(true);
  };
  const closeSoon = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    closeTimer.current = setTimeout(() => setShowPopup(false), 180);
  };

  if (!sign) return null;
  const pair = SIGN_FR_SYMBOL[sign];
  if (!pair) return null;
  const [label, symbol] = pair;

  return (
    <div
      style={{ position: 'relative', display: 'inline-block' }}
      onMouseEnter={openNow}
      onMouseLeave={closeSoon}
      onFocus={openNow}
      onBlur={closeSoon}
    >
      <Link
        to="/quotidien"
        data-testid="navbar-visitor-sign-badge"
        aria-label={`Votre signe · ${label}. Voir votre horoscope du jour.`}
        aria-expanded={showPopup}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 10px 4px 8px',
          marginLeft: 10,
          borderRadius: 999,
          border: '1px solid rgba(212,175,55,0.45)',
          background: 'rgba(212,175,55,0.08)',
          color: 'rgba(17,22,37,0.82)',
          fontFamily: 'Inter, sans-serif',
          fontSize: 12,
          fontWeight: 500,
          letterSpacing: '0.02em',
          textDecoration: 'none',
          transition: 'background 200ms ease, border-color 200ms ease',
          whiteSpace: 'nowrap',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(212,175,55,0.18)';
          e.currentTarget.style.borderColor = 'rgba(212,175,55,0.75)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'rgba(212,175,55,0.08)';
          e.currentTarget.style.borderColor = 'rgba(212,175,55,0.45)';
        }}
      >
        <span style={{ fontSize: 14, lineHeight: 1, color: 'var(--plume-gold)' }}>{symbol}</span>
        <span>{label}</span>
      </Link>

      {showPopup && (
        <div
          data-testid="navbar-visitor-sign-popup"
          role="tooltip"
          onMouseEnter={openNow}
          onMouseLeave={closeSoon}
          style={{
            position: 'absolute',
            top: 'calc(100% + 10px)',
            left: 10,
            width: 288,
            minWidth: 288,
            maxWidth: 'none',
            boxSizing: 'border-box',
            padding: 16,
            background: 'linear-gradient(180deg, #0F1A3A 0%, #0C132E 100%)',
            border: '1px solid rgba(212,175,55,0.4)',
            borderRadius: 8,
            boxShadow: '0 20px 48px rgba(0,0,0,0.4)',
            color: '#F5EEE0',
            fontFamily: 'Inter, sans-serif',
            zIndex: 200,
          }}
        >
          {/* Arrow */}
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              top: -6,
              left: 24,
              width: 10,
              height: 10,
              transform: 'rotate(45deg)',
              background: '#0F1A3A',
              borderLeft: '1px solid rgba(212,175,55,0.4)',
              borderTop: '1px solid rgba(212,175,55,0.4)',
            }}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 20, color: 'var(--plume-gold)' }}>{symbol}</span>
            <div>
              <div style={{ fontFamily: 'Cinzel, serif', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'rgba(212,175,55,0.85)' }}>
                Ton horoscope du jour
              </div>
              <div style={{ fontFamily: '"Fraunces", serif', fontSize: 15, color: '#F5EEE0' }}>{label}</div>
            </div>
          </div>
          {daily ? (
            <>
              <p
                data-testid="navbar-visitor-sign-popup-phrase"
                style={{ margin: 0, fontSize: 13, lineHeight: 1.55, color: 'rgba(244,239,230,0.82)', fontStyle: 'italic' }}
              >
                « {daily.phrase_du_jour} »
              </p>
              {daily.energie_du_jour != null && (
                <div
                  data-testid="navbar-visitor-sign-popup-energy"
                  style={{ marginTop: 12, display: 'inline-flex', padding: '3px 10px', borderRadius: 999, background: 'rgba(212,175,55,0.14)', border: '1px solid rgba(212,175,55,0.35)', color: '#F6C77A', fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase' }}
                >
                  Énergie · {daily.energie_du_jour}/10
                </div>
              )}
            </>
          ) : (
            <p style={{ margin: 0, fontSize: 13, color: 'rgba(244,239,230,0.55)' }}>Chargement…</p>
          )}
          <Link
            to="/quotidien"
            data-testid="navbar-visitor-sign-popup-cta"
            style={{
              marginTop: 14,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 11.5,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--plume-gold)',
              fontWeight: 500,
              textDecoration: 'none',
            }}
          >
            Lire tout mon horoscope →
          </Link>
        </div>
      )}
    </div>
  );
}
