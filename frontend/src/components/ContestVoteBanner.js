/**
 * ContestVoteBanner — Floating CTA pour le concours "Building France" d'Emergent
 *
 * Affichée uniquement sur la homepage. Dismissible (persistance localStorage 7 jours).
 * Style : Nocturne Éditorial (navy #0F1A3C + doré #C9A24B).
 * Apparition avec micro-délai (3s après le chargement) pour laisser la page respirer.
 *
 * Design : bulle fixe bottom-right, mobile-safe (respect safe-area), animation slide-up.
 */
import React, { useState, useEffect } from 'react';
import { Trophy, X, ExternalLink } from 'lucide-react';

const CONTEST_URL = 'https://app.emergent.sh/showcase/building-france/984cc6e3-63c5-40e6-9b25-b4704912a70d?ref=nadi762374';
const DISMISS_KEY = 'contest_banner_dismissed_at';
const DISMISS_DAYS = 7;

function isDismissed() {
  if (typeof window === 'undefined') return false;
  try {
    const ts = localStorage.getItem(DISMISS_KEY);
    if (!ts) return false;
    const elapsed = Date.now() - parseInt(ts, 10);
    return elapsed < DISMISS_DAYS * 24 * 60 * 60 * 1000;
  } catch (_e) {
    return false;
  }
}

export default function ContestVoteBanner() {
  const [visible, setVisible] = useState(false);
  const [entered, setEntered] = useState(false);

  useEffect(() => {
    if (isDismissed()) return;
    // Attend 3s pour ne pas parasiter le premier scroll
    const timer = setTimeout(() => {
      setVisible(true);
      // Micro-délai pour permettre le rendu avant l'animation
      requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  const handleDismiss = (e) => {
    e.stopPropagation();
    setEntered(false);
    setTimeout(() => setVisible(false), 300);
    try {
      localStorage.setItem(DISMISS_KEY, String(Date.now()));
    } catch (_e) { /* silent */ }
  };

  const handleClick = () => {
    window.open(CONTEST_URL, '_blank', 'noopener,noreferrer');
  };

  if (!visible) return null;

  return (
    <>
      <style>{`
        .contest-banner {
          position: fixed;
          bottom: max(24px, env(safe-area-inset-bottom, 24px));
          right: 24px;
          z-index: 9998;
          max-width: 360px;
          background: linear-gradient(135deg, #0F1A3C 0%, #1a2755 100%);
          border: 1px solid rgba(201, 162, 75, 0.35);
          border-radius: 14px;
          padding: 18px 20px 18px 18px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4),
                      0 0 0 1px rgba(201, 162, 75, 0.08),
                      inset 0 1px 0 rgba(255, 255, 255, 0.06);
          cursor: pointer;
          transform: translateY(30px) scale(0.96);
          opacity: 0;
          transition: transform 460ms cubic-bezier(0.16, 1, 0.3, 1),
                      opacity 320ms ease,
                      border-color 220ms ease;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
          backdrop-filter: blur(10px);
        }
        .contest-banner.entered {
          transform: translateY(0) scale(1);
          opacity: 1;
        }
        .contest-banner:hover {
          border-color: rgba(201, 162, 75, 0.65);
        }
        .contest-banner:hover .contest-cta {
          background: #d6b262;
          transform: translateX(2px);
        }
        .contest-banner .contest-close {
          position: absolute;
          top: 10px;
          right: 10px;
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.45);
          cursor: pointer;
          padding: 4px;
          border-radius: 6px;
          transition: color 180ms ease, background 180ms ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .contest-banner .contest-close:hover {
          color: rgba(255, 255, 255, 0.95);
          background: rgba(255, 255, 255, 0.08);
        }
        .contest-banner .contest-eyebrow {
          font-size: 10px;
          letter-spacing: 0.24em;
          text-transform: uppercase;
          color: #C9A24B;
          font-weight: 600;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .contest-banner .contest-title {
          font-family: 'Playfair Display', Georgia, serif;
          font-size: 17px;
          line-height: 1.3;
          color: #F7F5F0;
          font-weight: 500;
          margin: 0 0 6px 0;
          padding-right: 20px;
        }
        .contest-banner .contest-sub {
          font-size: 12.5px;
          line-height: 1.5;
          color: rgba(247, 245, 240, 0.7);
          margin: 0 0 14px 0;
        }
        .contest-banner .contest-cta {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: #C9A24B;
          color: #0F1A3C;
          font-size: 12px;
          font-weight: 600;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          padding: 8px 14px;
          border-radius: 6px;
          transition: background 220ms ease, transform 220ms ease;
        }
        @media (max-width: 480px) {
          .contest-banner {
            right: 12px;
            left: 12px;
            max-width: unset;
            bottom: max(16px, env(safe-area-inset-bottom, 16px));
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .contest-banner {
            transition-duration: 100ms;
          }
        }
      `}</style>
      <div
        className={`contest-banner ${entered ? 'entered' : ''}`}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter') handleClick(); }}
        data-testid="contest-vote-banner"
        aria-label="Voter pour Plume Astrale au concours Emergent Building France"
      >
        <button
          className="contest-close"
          onClick={handleDismiss}
          aria-label="Fermer la bannière"
          data-testid="contest-vote-banner-close"
        >
          <X size={14} />
        </button>
        <div className="contest-eyebrow">
          <Trophy size={12} strokeWidth={2.2} /> Concours en cours
        </div>
        <p className="contest-title">
          Soutenez <em>Plume Astrale</em> au concours <em>Building France</em>
        </p>
        <p className="contest-sub">
          Emergent récompense les créations françaises indépendantes. Un clic, un vote — et vous nous aidez à faire connaître notre écriture.
        </p>
        <span className="contest-cta">
          Voter pour nous <ExternalLink size={12} strokeWidth={2.5} />
        </span>
      </div>
    </>
  );
}
