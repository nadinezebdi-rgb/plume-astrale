/**
 * ActNav — Navigation verticale discrète (droite du viewport) pour la
 * homepage-experience V3. Cinq points invisibles, labels au hover.
 *
 * Phase 1 : 4 actes utilisables (I → IV). Les actes V-VIII seront ajoutés
 * en Phase 2. Les actes non-encore-atteints sont grisés et non-cliquables.
 *
 * Desktop uniquement (masqué < 900px via CSS). Aucun impact SEO
 * (aria-label, elements bien nommés).
 */
import React, { useEffect, useState } from 'react';

const ACTS = [
  { id: 1, label: "L'APPEL",         glyph: '·' },
  { id: 2, label: 'LA QUESTION',     glyph: '·' },
  { id: 3, label: 'LA RÉVÉLATION',   glyph: '✦' },
  { id: 4, label: 'LA PLUME',        glyph: '·' },
  { id: 5, label: "L'UNIVERS",       glyph: '·' },
  { id: 6, label: 'POUR VOUS',       glyph: '·' },
  { id: 7, label: 'COMMENCER',       glyph: '✦' },
  { id: 8, label: 'VOTRE ESPACE',    glyph: '·' },
];

export default function ActNav({ currentAct = 1, onJump, actsAvailable = 8, hidden = false }) {
  const [hover, setHover] = useState(null);

  // Respect reduced motion : pas de scale sur hover
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    if (!mq) return;
    setReduce(mq.matches);
    const listener = (e) => setReduce(e.matches);
    mq.addEventListener?.('change', listener);
    return () => mq.removeEventListener?.('change', listener);
  }, []);

  if (hidden) return null;

  return (
    <nav
      aria-label="Navigation des actes"
      data-testid="home-experience-actnav"
      style={{
        position: 'fixed', top: '50%', right: 26,
        transform: 'translateY(-50%)',
        display: 'flex', flexDirection: 'column', gap: 26,
        zIndex: 20,
        pointerEvents: 'auto',
      }}
      className="hex3-actnav"
    >
      {ACTS.slice(0, actsAvailable).map((a) => {
        const isCurrent = a.id === currentAct;
        const isHover = hover === a.id;
        return (
          <div key={a.id} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            {/* Label au hover */}
            <span
              aria-hidden={!isHover}
              style={{
                position: 'absolute', right: 22, top: '50%', transform: 'translateY(-50%)',
                fontFamily: '"Inter", sans-serif',
                fontSize: 10, letterSpacing: '0.24em', textTransform: 'uppercase',
                color: 'rgba(216, 183, 106, 0.9)',
                whiteSpace: 'nowrap',
                opacity: isHover ? 1 : 0,
                pointerEvents: 'none',
                transition: 'opacity 320ms ease',
              }}
            >
              {a.label}
            </span>
            <button
              type="button"
              aria-label={`Aller à l'acte ${a.id} : ${a.label}`}
              onClick={() => onJump && onJump(a.id)}
              onMouseEnter={() => setHover(a.id)}
              onMouseLeave={() => setHover(null)}
              onFocus={() => setHover(a.id)}
              onBlur={() => setHover(null)}
              data-testid={`home-experience-act-${a.id}`}
              data-current={isCurrent}
              style={{
                width: 8, height: 8, padding: 0,
                borderRadius: '50%',
                background: isCurrent
                  ? 'rgba(216, 183, 106, 0.95)'
                  : (isHover ? 'rgba(216, 183, 106, 0.55)' : 'rgba(244, 239, 230, 0.28)'),
                border: 'none', cursor: 'pointer',
                transform: !reduce && (isCurrent || isHover) ? 'scale(1.35)' : 'scale(1)',
                transition: 'transform 360ms cubic-bezier(0.16, 1, 0.3, 1), background 320ms ease',
                boxShadow: isCurrent
                  ? '0 0 12px rgba(216, 183, 106, 0.55)'
                  : 'none',
              }}
            />
          </div>
        );
      })}
    </nav>
  );
}
