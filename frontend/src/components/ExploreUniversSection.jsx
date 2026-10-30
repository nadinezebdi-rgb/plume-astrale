import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Sparkles, Heart, Sun, FileText } from 'lucide-react';
import { event as trackEvent } from '../lib/analytics';
import './ExploreUniversSection.css';

const NATAL_PREVIEW_URL = process.env.REACT_APP_NATAL_BOOK_PREVIEW_URL;
const SYNASTRIE_PREVIEW_URL = process.env.REACT_APP_SYNASTRIE_PREVIEW_URL;
const API_URL = process.env.REACT_APP_BACKEND_URL;

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

/** SVG constellation decorative (subtle, in-card background) */
function ConstellationDecor({ variant }) {
  const common = {
    position: 'absolute',
    inset: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    opacity: 0.42,
  };
  if (variant === 'natal') {
    // Mini chart wheel
    return (
      <svg viewBox="0 0 200 200" style={common} aria-hidden="true">
        <defs>
          <radialGradient id="natalFade" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="var(--card-accent)" stopOpacity="0.0" />
            <stop offset="100%" stopColor="var(--card-accent)" stopOpacity="0.14" />
          </radialGradient>
        </defs>
        <circle cx="150" cy="40" r="60" fill="url(#natalFade)" />
        <circle cx="150" cy="40" r="42" fill="none" stroke="var(--card-accent)" strokeOpacity="0.28" strokeWidth="0.6" />
        <circle cx="150" cy="40" r="30" fill="none" stroke="var(--card-accent)" strokeOpacity="0.22" strokeWidth="0.5" />
        <circle cx="150" cy="40" r="18" fill="none" stroke="var(--card-accent)" strokeOpacity="0.18" strokeWidth="0.5" />
        {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => {
          const rad = (deg * Math.PI) / 180;
          const x1 = 150 + Math.cos(rad) * 18;
          const y1 = 40 + Math.sin(rad) * 18;
          const x2 = 150 + Math.cos(rad) * 42;
          const y2 = 40 + Math.sin(rad) * 42;
          return <line key={deg} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--card-accent)" strokeOpacity="0.26" strokeWidth="0.4" />;
        })}
      </svg>
    );
  }
  if (variant === 'synastrie') {
    // Two overlapping circles (venn-like) + heart cue
    return (
      <svg viewBox="0 0 200 200" style={common} aria-hidden="true">
        <circle cx="138" cy="42" r="28" fill="none" stroke="var(--card-accent)" strokeOpacity="0.38" strokeWidth="0.6" />
        <circle cx="168" cy="42" r="28" fill="none" stroke="var(--card-accent)" strokeOpacity="0.38" strokeWidth="0.6" />
        <circle cx="138" cy="42" r="3" fill="var(--card-accent)" fillOpacity="0.42" />
        <circle cx="168" cy="42" r="3" fill="var(--card-accent)" fillOpacity="0.42" />
        {/* small stars sprinkled */}
        {[[115, 70, 1], [190, 68, 1.2], [152, 18, 0.8], [177, 72, 0.9], [128, 20, 0.8]].map(([cx, cy, r], i) => (
          <circle key={i} cx={cx} cy={cy} r={r} fill="var(--card-accent)" fillOpacity="0.55" />
        ))}
      </svg>
    );
  }
  // horoscope: sun with rays
  return (
    <svg viewBox="0 0 200 200" style={common} aria-hidden="true">
      <defs>
        <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="var(--card-accent)" stopOpacity="0.2" />
          <stop offset="100%" stopColor="var(--card-accent)" stopOpacity="0.0" />
        </radialGradient>
      </defs>
      <circle cx="160" cy="40" r="52" fill="url(#sunGlow)" />
      <circle cx="160" cy="40" r="14" fill="none" stroke="var(--card-accent)" strokeOpacity="0.5" strokeWidth="0.8" />
      {Array.from({ length: 12 }).map((_, i) => {
        const deg = i * 30;
        const rad = (deg * Math.PI) / 180;
        const x1 = 160 + Math.cos(rad) * 20;
        const y1 = 40 + Math.sin(rad) * 20;
        const x2 = 160 + Math.cos(rad) * 32;
        const y2 = 40 + Math.sin(rad) * 32;
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--card-accent)" strokeOpacity="0.42" strokeWidth="0.6" />;
      })}
    </svg>
  );
}

/** Hook: detect the visitor's zodiac sign from localStorage (plume_astrale_data.dateNaissance) */
function useVisitorSign() {
  const [sign, setSign] = useState(null);
  useEffect(() => {
    try {
      const raw = localStorage.getItem('plume_astrale_data');
      if (!raw) return;
      const parsed = JSON.parse(raw);
      const s = getZodiacSign(parsed?.dateNaissance);
      if (s) setSign(s);
    } catch (_) { /* no-op */ }
  }, []);
  return sign;
}

/** Hook: fetch daily content for a given sign */
function useDailyContent(sign) {
  const [content, setContent] = useState(null);
  useEffect(() => {
    if (!sign || !API_URL) return;
    let cancelled = false;
    fetch(`${API_URL}/api/daily/${sign}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (!cancelled && data) setContent(data); })
      .catch(() => { /* no-op */ });
    return () => { cancelled = true; };
  }, [sign]);
  return content;
}

function PreviewLink({ href, label, event, testid }) {
  if (!href) return null;
  const onClick = (e) => {
    e.stopPropagation();
    try { trackEvent(event, { source: 'explore_univers' }); } catch (_) {}
  };
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="explore-univers__card-preview"
      onClick={onClick}
      data-testid={testid}
      style={{ position: 'relative', zIndex: 2 }}
    >
      <FileText size={14} strokeWidth={1.6} aria-hidden="true" />
      <span>{label}</span>
    </a>
  );
}

export default function ExploreUniversSection() {
  const visitorSign = useVisitorSign();
  const daily = useDailyContent(visitorSign);
  const signLabel = useMemo(() => {
    if (!visitorSign) return null;
    const pair = SIGN_FR_SYMBOL[visitorSign];
    return pair ? `${pair[0]} ${pair[1]}` : null;
  }, [visitorSign]);

  return (
    <section
      className="explore-univers"
      aria-labelledby="explore-univers-title"
      data-testid="explore-univers-section"
    >
      <div className="explore-univers__inner">
        <header className="explore-univers__header">
          <p className="explore-univers__eyebrow">Pour aller plus loin</p>
          <h2 id="explore-univers-title" className="explore-univers__title">
            Explore ton univers
          </h2>
          <p className="explore-univers__subtitle">
            Trois portes d’entrée pour continuer ton voyage astral, à ton rythme.
          </p>
        </header>

        <div className="explore-univers__grid">
          {/* Card 1 — Thème natal */}
          {/* AUDIT (2026-10-30 · Nao) : refacto <a> imbriqué en <article> + stretched-link overlay
              pour supprimer le warning React 19 "hydration error: <a> in <a>". */}
          <article
            className="explore-univers__card explore-univers__card--linked"
            data-testid="explore-univers-card-theme-natal"
            style={{ '--card-accent': '#D4AF37', position: 'relative' }}
          >
            <ConstellationDecor variant="natal" />
            <div className="explore-univers__card-head">
              <span className="explore-univers__card-icon" aria-hidden="true">
                <Sparkles size={22} strokeWidth={1.4} />
              </span>
              <ArrowUpRight size={20} strokeWidth={1.4} className="explore-univers__card-arrow" aria-hidden="true" />
            </div>
            <p className="explore-univers__card-eyebrow">Lecture signature</p>
            <h3 className="explore-univers__card-title">Thème natal</h3>
            <p className="explore-univers__card-desc">
              Ta carte du ciel décodée : personnalité, forces, défis et chemin de vie, dans un livre imprimable à partir de 49 pages.
            </p>
            <div className="explore-univers__card-footer">
              <span className="explore-univers__card-cta" aria-hidden="true">Découvrir</span>
              <PreviewLink
                href={NATAL_PREVIEW_URL}
                label="Feuilleter l’extrait"
                event="pdf_preview_click"
                testid="explore-univers-natal-preview"
              />
            </div>
            <Link
              to="/theme-natal"
              aria-label="Thème natal — découvrir"
              className="explore-univers__card-stretched"
              style={{ position: 'absolute', inset: 0, zIndex: 1, textIndent: '-9999px', overflow: 'hidden' }}
            >Thème natal</Link>
          </article>

          {/* Card 2 — Compatibilité amoureuse */}
          <article
            className="explore-univers__card explore-univers__card--linked"
            data-testid="explore-univers-card-synastrie"
            style={{ '--card-accent': '#E8A5B9', position: 'relative' }}
          >
            <ConstellationDecor variant="synastrie" />
            <div className="explore-univers__card-head">
              <span className="explore-univers__card-icon" aria-hidden="true">
                <Heart size={22} strokeWidth={1.4} />
              </span>
              <ArrowUpRight size={20} strokeWidth={1.4} className="explore-univers__card-arrow" aria-hidden="true" />
            </div>
            <p className="explore-univers__card-eyebrow">Astrologie à deux</p>
            <h3 className="explore-univers__card-title">Compatibilité amoureuse</h3>
            <p className="explore-univers__card-desc">
              Comparez vos deux cartes du ciel et comprenez vraiment ce qui vous lie — et ce qui vous challenge.
            </p>
            <div className="explore-univers__card-footer">
              <span className="explore-univers__card-cta" aria-hidden="true">Découvrir</span>
              <PreviewLink
                href={SYNASTRIE_PREVIEW_URL}
                label="Feuilleter l’extrait"
                event="synastrie_preview_click"
                testid="explore-univers-synastrie-preview"
              />
            </div>
            <Link
              to="/synastrie"
              aria-label="Compatibilité amoureuse — découvrir"
              className="explore-univers__card-stretched"
              style={{ position: 'absolute', inset: 0, zIndex: 1, textIndent: '-9999px', overflow: 'hidden' }}
            >Compatibilité amoureuse</Link>
          </article>

          {/* Card 3 — Horoscope du jour (live widget) */}
          <Link
            to="/quotidien"
            className="explore-univers__card explore-univers__card--horoscope"
            data-testid="explore-univers-card-quotidien"
            style={{ '--card-accent': '#F6C77A' }}
          >
            <ConstellationDecor variant="horoscope" />
            <div className="explore-univers__card-head">
              <span className="explore-univers__card-icon" aria-hidden="true">
                <Sun size={22} strokeWidth={1.4} />
              </span>
              <ArrowUpRight size={20} strokeWidth={1.4} className="explore-univers__card-arrow" aria-hidden="true" />
            </div>
            <p className="explore-univers__card-eyebrow">
              {visitorSign ? `Pour toi · ${signLabel}` : 'Gratuit · Chaque matin'}
            </p>
            <h3 className="explore-univers__card-title">
              {visitorSign ? "Ton horoscope du jour" : 'Horoscope du jour'}
            </h3>
            {visitorSign && daily ? (
              <p className="explore-univers__card-desc" data-testid="explore-univers-daily-text">
                « {daily.phrase_du_jour} »
              </p>
            ) : (
              <p className="explore-univers__card-desc">
                Les énergies planétaires d’aujourd’hui pour ton signe, en 2 minutes de lecture dès le réveil.
              </p>
            )}
            <div className="explore-univers__card-footer">
              <span className="explore-univers__card-cta" aria-hidden="true">
                {visitorSign ? 'Lire tout mon horoscope' : 'Découvrir'}
              </span>
              {visitorSign && daily?.energie_du_jour != null && (
                <span className="explore-univers__card-badge" data-testid="explore-univers-daily-energy">
                  Énergie · {daily.energie_du_jour}/10
                </span>
              )}
            </div>
          </Link>
        </div>
      </div>
    </section>
  );
}
