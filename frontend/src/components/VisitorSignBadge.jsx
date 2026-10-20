import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

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
 * Discreet pastille next to the brand logo showing the visitor's zodiac sign
 * once they've shared their birth date. Reads localStorage.plume_astrale_data.
 * Clicking it jumps to /quotidien (personalised daily horoscope).
 */
export default function VisitorSignBadge() {
  const [sign, setSign] = useState(null);

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
    // Re-read when storage changes elsewhere (cross-tab or custom event).
    window.addEventListener('storage', read);
    window.addEventListener('plume-sign-updated', read);
    return () => {
      window.removeEventListener('storage', read);
      window.removeEventListener('plume-sign-updated', read);
    };
  }, []);

  if (!sign) return null;
  const pair = SIGN_FR_SYMBOL[sign];
  if (!pair) return null;
  const [label, symbol] = pair;

  return (
    <Link
      to="/quotidien"
      data-testid="navbar-visitor-sign-badge"
      aria-label={`Votre signe · ${label}. Voir votre horoscope du jour.`}
      title={`Votre horoscope du jour · ${label}`}
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
  );
}
