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
import { ChevronLeft, ChevronRight } from 'lucide-react';

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
  const activeAct = Math.min(Math.max(currentAct, 1), actsAvailable);
  const activeLabel = ACTS[activeAct - 1]?.label || ACTS[0].label;

  return (
    <>
      <nav
        aria-label="Navigation des actes"
        data-testid="home-experience-actnav"
        className="hex3-actnav"
      >
        {ACTS.slice(0, actsAvailable).map((act) => {
          const isCurrent = act.id === activeAct;
          const isHover = hover === act.id;
          return (
            <div key={act.id} className="hex3-actnav__item">
              <span className="hex3-actnav__label" aria-hidden={!isHover} data-visible={isHover}>
                {act.label}
              </span>
              <button
                type="button"
                aria-label={`Aller à l'acte ${act.id} : ${act.label}`}
                aria-current={isCurrent ? 'step' : undefined}
                onClick={() => onJump?.(act.id)}
                onMouseEnter={() => setHover(act.id)}
                onMouseLeave={() => setHover(null)}
                onFocus={() => setHover(act.id)}
                onBlur={() => setHover(null)}
                data-testid={`home-experience-act-${act.id}`}
                data-current={isCurrent}
                className="hex3-actnav__button"
              >
                <span
                  className="hex3-actnav__dot"
                  data-current={isCurrent}
                  data-hover={isHover}
                  data-reduced-motion={reduce}
                />
              </button>
            </div>
          );
        })}
      </nav>

      <nav className="hex3-actnav-mobile" aria-label="Progression des actes" data-testid="home-experience-mobile-nav">
        <button
          type="button"
          className="hex3-actnav-mobile__arrow"
          aria-label={`Acte précédent : ${ACTS[Math.max(0, activeAct - 2)].label}`}
          disabled={activeAct <= 1}
          onClick={() => onJump?.(activeAct - 1)}
        >
          <ChevronLeft size={18} aria-hidden="true" />
        </button>
        <div className="hex3-actnav-mobile__progress">
          <div className="hex3-actnav-mobile__current">
            <span>ACTE {activeAct} / {actsAvailable}</span>
            <strong>{activeLabel}</strong>
          </div>
          <div className="hex3-actnav-mobile__steps">
            {ACTS.slice(0, actsAvailable).map((act) => (
              <button
                key={act.id}
                type="button"
                aria-label={`Aller à l'acte ${act.id} : ${act.label}`}
                aria-current={act.id === activeAct ? 'step' : undefined}
                onClick={() => onJump?.(act.id)}
                data-current={act.id === activeAct}
              />
            ))}
          </div>
        </div>
        <button
          type="button"
          className="hex3-actnav-mobile__next"
          aria-label={`Acte suivant : ${ACTS[Math.min(actsAvailable - 1, activeAct)].label}`}
          disabled={activeAct >= actsAvailable}
          onClick={() => onJump?.(activeAct + 1)}
        >
          Suivant <ChevronRight size={16} aria-hidden="true" />
        </button>
      </nav>
    </>
  );
}
