/**
 * ZodiacInterlude — overlay élégant qui apparaît sur la scène 2 après
 * la sélection d'une intention. Demande la date de naissance, calcule
 * le signe, affiche une mini-constellation stylée pendant ~5s, puis
 * appelle onComplete() → scroll vers scène 3 (Tarot).
 *
 * Skippable ("Passer") à tout moment.
 * Persiste le signe en sessionStorage `exp_zodiac` pour WelcomeSplash.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { computeZodiac, ZODIAC_STARS } from './zodiacUtils';
import { event as trackEvent } from '@/lib/analytics';

export default function ZodiacInterlude({ visible, onComplete, onSkip }) {
  const [step, setStep] = useState('input'); // 'input' | 'reveal'
  const [dob, setDob] = useState('');
  const [sign, setSign] = useState(null);

  const stars = useMemo(() => (sign ? ZODIAC_STARS[sign.key] || [] : []), [sign]);

  useEffect(() => {
    if (!visible) {
      setStep('input');
      setSign(null);
      setDob('');
    }
  }, [visible]);

  // Auto-continuation 5s après reveal
  useEffect(() => {
    if (step !== 'reveal') return;
    const t = setTimeout(() => onComplete && onComplete(sign), 5200);
    return () => clearTimeout(t);
  }, [step, sign, onComplete]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const s = computeZodiac(dob);
    if (!s) return;
    try { window.sessionStorage.setItem('exp_zodiac', s.key); } catch { /* noop */ }
    trackEvent('zodiac_computed', { zodiac: s.key, element: s.element });
    setSign(s);
    setStep('reveal');
  };

  const handleSkip = () => {
    trackEvent('zodiac_skipped', { step });
    onSkip && onSkip();
  };

  if (!visible) return null;

  return (
    <div style={overlayStyle} data-testid="zodiac-interlude">
      <style>{`
        @keyframes zodiacFade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes starBirth  { from { opacity: 0; transform: scale(0.4); } to { opacity: 1; transform: scale(1); } }
        @keyframes linePull   { from { stroke-dashoffset: 240; } to { stroke-dashoffset: 0; } }
      `}</style>

      {step === 'input' && (
        <form onSubmit={handleSubmit} style={cardStyle} data-testid="zodiac-form">
          <p style={eyebrowStyle}>✦ VOTRE CIEL DE NAISSANCE</p>
          <p style={leadStyle}>
            Le ciel n&apos;était pas le même le jour où vous êtes venu au monde.<br />
            <em style={{ opacity: 0.75 }}>Confiez-nous cette date, un instant.</em>
          </p>
          <input
            type="date"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            required
            min="1900-01-01"
            max="2026-12-31"
            style={inputStyle}
            data-testid="zodiac-date-input"
            aria-label="Date de naissance"
          />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14, alignItems: 'center', marginTop: 12 }}>
            <button
              type="submit"
              disabled={!dob}
              style={{ ...ctaPrimary, opacity: dob ? 1 : 0.4, cursor: dob ? 'pointer' : 'default' }}
              data-testid="zodiac-submit"
            >
              <span style={{ color: '#D8B76A' }}>✦</span> RÉVÉLER MON SIGNE
            </button>
            <button
              type="button"
              onClick={handleSkip}
              style={skipStyle}
              data-testid="zodiac-skip"
            >
              Continuer sans mon signe →
            </button>
          </div>
        </form>
      )}

      {step === 'reveal' && sign && (
        <div style={cardStyle} data-testid="zodiac-reveal">
          <p style={eyebrowStyle} data-testid="zodiac-eyebrow">
            {sign.element.toUpperCase()} · SIGNE {sign.name.toUpperCase()}
          </p>

          <svg viewBox="0 0 200 200" style={{ width: 220, height: 220, margin: '4px auto 12px', display: 'block' }} aria-hidden="true">
            {/* Lignes du pattern */}
            {stars.slice(1).map((pt, i) => {
              const prev = stars[i];
              return (
                <line
                  key={`ln-${i}`}
                  x1={prev[0]} y1={prev[1]} x2={pt[0]} y2={pt[1]}
                  stroke="rgba(216, 183, 106, 0.65)" strokeWidth="0.9"
                  strokeDasharray="240"
                  style={{ animation: `linePull ${1200 + i * 220}ms cubic-bezier(0.22, 1, 0.36, 1) forwards` }}
                />
              );
            })}
            {/* Étoiles */}
            {stars.map(([x, y], i) => (
              <circle
                key={`s-${i}`} cx={x} cy={y} r="3.4"
                fill="#F4EFE6"
                style={{
                  filter: 'drop-shadow(0 0 6px rgba(216, 183, 106, 0.9))',
                  animation: `starBirth ${700 + i * 180}ms ease-out both`,
                }}
              />
            ))}
            {/* Glyphe central subtle */}
            <text x="100" y="112" textAnchor="middle" fontSize="42"
                  fill="rgba(216, 183, 106, 0.18)"
                  style={{ fontFamily: '"Cormorant Garamond", serif' }}>
              {sign.glyph}
            </text>
          </svg>

          <h2 style={titleStyle} data-testid="zodiac-name">{sign.name}</h2>
          <p style={{ ...leadStyle, marginTop: 6 }}>
            En vous, <em>{sign.trait}</em>.
          </p>
          <button
            type="button"
            onClick={() => onComplete && onComplete(sign)}
            style={{ ...ctaPrimary, marginTop: 12 }}
            data-testid="zodiac-continue"
          >
            <span style={{ color: '#D8B76A' }}>✦</span> CONTINUER
          </button>
        </div>
      )}
    </div>
  );
}

const overlayStyle = {
  position: 'fixed', inset: 0, zIndex: 900,
  background: 'radial-gradient(ellipse at 50% 42%, rgba(23, 16, 46, 0.94), rgba(7, 7, 19, 0.98))',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  padding: '24px 20px',
  animation: 'zodiacFade 700ms ease-out',
};
const cardStyle = {
  maxWidth: 520, width: '100%', textAlign: 'center',
  color: '#F4EFE6', fontFamily: '"Cormorant Garamond", Georgia, serif',
};
const eyebrowStyle = {
  fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.32em',
  color: 'rgba(216, 183, 106, 0.75)', textTransform: 'uppercase',
  margin: '0 0 20px',
};
const titleStyle = {
  fontFamily: '"Cormorant Garamond", serif', fontWeight: 400,
  fontSize: 'clamp(30px, 4.8vw, 46px)', lineHeight: 1.1,
  letterSpacing: '0.02em', margin: '0 0 6px',
};
const leadStyle = {
  fontStyle: 'italic', fontSize: 'clamp(15px, 1.6vw, 18px)',
  color: 'rgba(244, 239, 230, 0.72)', margin: '0 0 26px', lineHeight: 1.6,
};
const inputStyle = {
  background: 'transparent',
  border: 'none', borderBottom: '1px solid rgba(216, 183, 106, 0.4)',
  color: '#F4EFE6',
  fontFamily: '"Inter", sans-serif', fontSize: 14,
  letterSpacing: '0.14em',
  padding: '10px 4px', width: 240, textAlign: 'center',
  outline: 'none', colorScheme: 'dark',
};
const ctaPrimary = {
  display: 'inline-flex', alignItems: 'center', gap: 12,
  padding: '14px 30px', background: 'transparent', color: '#F4EFE6',
  fontFamily: '"Inter", sans-serif', fontSize: 11.5, fontWeight: 400,
  letterSpacing: '0.28em', textTransform: 'uppercase',
  border: '1px solid rgba(216, 183, 106, 0.55)', borderRadius: 2,
  cursor: 'pointer', transition: 'letter-spacing 400ms ease',
};
const skipStyle = {
  background: 'transparent', border: 'none',
  color: 'rgba(244, 239, 230, 0.4)',
  fontFamily: '"Inter", sans-serif', fontSize: 11,
  letterSpacing: '0.22em', textTransform: 'uppercase',
  cursor: 'pointer', padding: '8px 4px',
};
