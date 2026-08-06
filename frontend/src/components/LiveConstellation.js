import React, { useMemo } from 'react';

/**
 * LiveConstellation — SVG constellation vivante des 12 signes du zodiaque.
 *
 * Props :
 *   sign : 'aries' | 'taurus' | ... | 'pisces' | 'auto' (défaut 'auto')
 *          'auto' → détecte le signe zodiacal en cours à partir de la date du jour
 *   size : px, défaut 380
 *
 * Rendu :
 *   - Étoiles principales qui pulsent (halo doré + cœur crème)
 *   - Lignes dorées tracées progressivement au chargement
 *   - Rotation ultra-lente 360° sur 2min
 */

/* ── 12 constellations zodiacales ──
 * Positions approximatives, adaptées pour un rendu 100×100 viewBox esthétique.
 */
const CONSTELLATIONS = {
  aries: {
    label: 'Bélier',
    fr: 'Bélier',
    stars: [
      { id: 'hamal', x: 30, y: 25, r: 3.6, brightness: 1 },
      { id: 'sheratan', x: 45, y: 32, r: 2.8, brightness: 0.95 },
      { id: 'mesarthim', x: 52, y: 40, r: 2.4, brightness: 0.9 },
      { id: 'delta', x: 58, y: 55, r: 2.2, brightness: 0.85 },
      { id: 'epsilon', x: 65, y: 70, r: 2.0, brightness: 0.8 },
    ],
    lines: [['hamal', 'sheratan'], ['sheratan', 'mesarthim'], ['mesarthim', 'delta'], ['delta', 'epsilon']],
  },

  taurus: {
    label: 'Taureau',
    fr: 'Taureau',
    stars: [
      { id: 'aldebaran', x: 55, y: 55, r: 3.8, brightness: 1 },
      { id: 'elnath', x: 25, y: 22, r: 3.2, brightness: 0.95 },
      { id: 'zeta', x: 50, y: 30, r: 2.6, brightness: 0.9 },
      { id: 'lambda', x: 65, y: 45, r: 2.4, brightness: 0.85 },
      { id: 'theta1', x: 60, y: 60, r: 2.2, brightness: 0.85 },
      { id: 'theta2', x: 50, y: 62, r: 2.2, brightness: 0.85 },
      { id: 'gamma', x: 45, y: 50, r: 2.6, brightness: 0.9 },
      { id: 'omicron', x: 30, y: 78, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['aldebaran', 'lambda'], ['aldebaran', 'gamma'], ['gamma', 'theta1'],
      ['theta1', 'theta2'], ['theta2', 'omicron'], ['aldebaran', 'zeta'], ['zeta', 'elnath'],
    ],
  },

  gemini: {
    label: 'Gémeaux',
    fr: 'Gémeaux',
    stars: [
      { id: 'castor', x: 30, y: 22, r: 3.4, brightness: 1 },
      { id: 'pollux', x: 55, y: 25, r: 3.6, brightness: 1 },
      { id: 'wasat', x: 42, y: 45, r: 2.4, brightness: 0.85 },
      { id: 'mebsuta', x: 25, y: 42, r: 2.6, brightness: 0.9 },
      { id: 'alhena', x: 55, y: 55, r: 2.8, brightness: 0.9 },
      { id: 'tejat', x: 20, y: 62, r: 2.4, brightness: 0.85 },
      { id: 'propus', x: 15, y: 80, r: 2.2, brightness: 0.8 },
      { id: 'zeta', x: 62, y: 75, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['castor', 'mebsuta'], ['mebsuta', 'tejat'], ['tejat', 'propus'],
      ['pollux', 'wasat'], ['wasat', 'alhena'], ['alhena', 'zeta'],
      ['castor', 'pollux'],
    ],
  },

  cancer: {
    label: 'Cancer',
    fr: 'Cancer',
    stars: [
      { id: 'acubens', x: 65, y: 55, r: 3.0, brightness: 0.95 },
      { id: 'altarf', x: 30, y: 72, r: 3.4, brightness: 1 },
      { id: 'asellus-borealis', x: 50, y: 30, r: 2.6, brightness: 0.9 },
      { id: 'asellus-australis', x: 55, y: 42, r: 2.4, brightness: 0.85 },
      { id: 'iota', x: 35, y: 18, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['iota', 'asellus-borealis'], ['asellus-borealis', 'asellus-australis'],
      ['asellus-australis', 'acubens'], ['asellus-australis', 'altarf'],
    ],
  },

  leo: {
    label: 'Lion',
    fr: 'Lion',
    stars: [
      { id: 'regulus', x: 32, y: 58, r: 3.8, brightness: 1 },
      { id: 'denebola', x: 78, y: 42, r: 3.2, brightness: 0.95 },
      { id: 'algieba', x: 42, y: 40, r: 3.0, brightness: 0.95 },
      { id: 'zosma', x: 68, y: 32, r: 2.6, brightness: 0.9 },
      { id: 'chort', x: 72, y: 48, r: 2.4, brightness: 0.85 },
      { id: 'eta', x: 32, y: 45, r: 2.4, brightness: 0.85 },
      { id: 'adhafera', x: 42, y: 25, r: 2.6, brightness: 0.9 },
      { id: 'ras-elased', x: 32, y: 18, r: 2.6, brightness: 0.9 },
    ],
    lines: [
      ['ras-elased', 'adhafera'], ['adhafera', 'algieba'], ['algieba', 'zosma'],
      ['zosma', 'denebola'], ['denebola', 'chort'], ['chort', 'regulus'],
      ['regulus', 'eta'], ['eta', 'algieba'],
    ],
  },

  virgo: {
    label: 'Vierge',
    fr: 'Vierge',
    stars: [
      { id: 'spica', x: 62, y: 72, r: 3.8, brightness: 1 },
      { id: 'porrima', x: 45, y: 50, r: 3.0, brightness: 0.95 },
      { id: 'vindemiatrix', x: 30, y: 25, r: 3.0, brightness: 0.95 },
      { id: 'auva', x: 42, y: 32, r: 2.6, brightness: 0.9 },
      { id: 'zavijava', x: 25, y: 40, r: 2.4, brightness: 0.85 },
      { id: 'zaniah', x: 32, y: 45, r: 2.4, brightness: 0.85 },
      { id: 'heze', x: 68, y: 55, r: 2.4, brightness: 0.85 },
      { id: 'syrma', x: 78, y: 68, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['vindemiatrix', 'auva'], ['auva', 'porrima'], ['porrima', 'zaniah'],
      ['zaniah', 'zavijava'], ['porrima', 'heze'], ['heze', 'syrma'],
      ['heze', 'spica'],
    ],
  },

  libra: {
    label: 'Balance',
    fr: 'Balance',
    stars: [
      { id: 'zubeneschamali', x: 32, y: 30, r: 3.4, brightness: 1 },
      { id: 'zubenelgenubi', x: 62, y: 55, r: 3.4, brightness: 1 },
      { id: 'sigma', x: 78, y: 40, r: 2.6, brightness: 0.9 },
      { id: 'upsilon', x: 45, y: 62, r: 2.4, brightness: 0.85 },
      { id: 'iota', x: 50, y: 78, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['zubeneschamali', 'sigma'], ['sigma', 'zubenelgenubi'],
      ['zubenelgenubi', 'zubeneschamali'], ['zubenelgenubi', 'upsilon'],
      ['upsilon', 'iota'],
    ],
  },

  scorpio: {
    label: 'Scorpion',
    fr: 'Scorpion',
    stars: [
      { id: 'antares', x: 42, y: 45, r: 3.8, brightness: 1 },
      { id: 'shaula', x: 82, y: 68, r: 3.4, brightness: 1 },
      { id: 'lesath', x: 82, y: 78, r: 2.8, brightness: 0.9 },
      { id: 'graffias', x: 25, y: 28, r: 2.8, brightness: 0.9 },
      { id: 'dschubba', x: 30, y: 32, r: 2.6, brightness: 0.9 },
      { id: 'pi', x: 22, y: 40, r: 2.4, brightness: 0.85 },
      { id: 'tau', x: 50, y: 52, r: 2.6, brightness: 0.9 },
      { id: 'epsilon', x: 62, y: 60, r: 2.4, brightness: 0.85 },
      { id: 'mu', x: 72, y: 65, r: 2.6, brightness: 0.9 },
    ],
    lines: [
      ['pi', 'graffias'], ['graffias', 'dschubba'], ['dschubba', 'antares'],
      ['antares', 'tau'], ['tau', 'epsilon'], ['epsilon', 'mu'],
      ['mu', 'shaula'], ['shaula', 'lesath'],
    ],
  },

  sagittarius: {
    label: 'Sagittaire',
    fr: 'Sagittaire',
    stars: [
      { id: 'kaus-australis', x: 35, y: 52, r: 3.6, brightness: 1 },
      { id: 'nunki', x: 55, y: 40, r: 3.2, brightness: 0.95 },
      { id: 'ascella', x: 68, y: 48, r: 2.8, brightness: 0.9 },
      { id: 'kaus-media', x: 38, y: 45, r: 2.8, brightness: 0.9 },
      { id: 'kaus-borealis', x: 42, y: 35, r: 2.6, brightness: 0.9 },
      { id: 'alnasl', x: 25, y: 55, r: 2.4, brightness: 0.85 },
      { id: 'tau', x: 70, y: 65, r: 2.4, brightness: 0.85 },
      { id: 'zeta', x: 65, y: 70, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['alnasl', 'kaus-australis'], ['kaus-australis', 'kaus-media'],
      ['kaus-media', 'kaus-borealis'], ['kaus-borealis', 'nunki'],
      ['nunki', 'ascella'], ['ascella', 'tau'], ['tau', 'zeta'],
      ['zeta', 'kaus-australis'],
    ],
  },

  capricorn: {
    label: 'Capricorne',
    fr: 'Capricorne',
    stars: [
      { id: 'algedi', x: 22, y: 28, r: 3.0, brightness: 0.95 },
      { id: 'dabih', x: 28, y: 35, r: 3.0, brightness: 0.95 },
      { id: 'nashira', x: 65, y: 60, r: 2.8, brightness: 0.9 },
      { id: 'deneb-algedi', x: 78, y: 55, r: 3.2, brightness: 0.95 },
      { id: 'omega', x: 42, y: 55, r: 2.4, brightness: 0.85 },
      { id: 'psi', x: 55, y: 68, r: 2.4, brightness: 0.85 },
      { id: 'zeta', x: 60, y: 65, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['algedi', 'dabih'], ['dabih', 'omega'], ['omega', 'psi'],
      ['psi', 'zeta'], ['zeta', 'nashira'], ['nashira', 'deneb-algedi'],
      ['deneb-algedi', 'dabih'],
    ],
  },

  aquarius: {
    label: 'Verseau',
    fr: 'Verseau',
    stars: [
      { id: 'sadalmelik', x: 45, y: 30, r: 3.2, brightness: 1 },
      { id: 'sadalsuud', x: 25, y: 38, r: 3.6, brightness: 1 },
      { id: 'sadachbia', x: 60, y: 42, r: 2.5, brightness: 0.9 },
      { id: 'skat', x: 52, y: 72, r: 3.0, brightness: 1 },
      { id: 'ancha', x: 45, y: 48, r: 2.2, brightness: 0.85 },
      { id: 'albali', x: 15, y: 55, r: 2.4, brightness: 0.9 },
      { id: 'situla', x: 35, y: 15, r: 2.0, brightness: 0.8 },
      { id: 'lambda', x: 62, y: 58, r: 2.4, brightness: 0.85 },
      { id: 'psi', x: 40, y: 82, r: 2.6, brightness: 0.9 },
    ],
    lines: [
      ['situla', 'sadalmelik'], ['sadalmelik', 'sadalsuud'], ['sadalmelik', 'ancha'],
      ['sadalsuud', 'albali'], ['ancha', 'sadachbia'], ['ancha', 'skat'],
      ['sadachbia', 'lambda'], ['skat', 'psi'],
    ],
  },

  pisces: {
    label: 'Poissons',
    fr: 'Poissons',
    stars: [
      { id: 'alpherg', x: 30, y: 30, r: 3.2, brightness: 1 },
      { id: 'eta', x: 46, y: 25, r: 2.8, brightness: 0.95 },
      { id: 'gamma', x: 60, y: 35, r: 2.6, brightness: 0.9 },
      { id: 'omega', x: 70, y: 50, r: 2.4, brightness: 0.85 },
      { id: 'iota', x: 78, y: 68, r: 2.6, brightness: 0.9 },
      { id: 'lambda', x: 62, y: 75, r: 2.2, brightness: 0.8 },
      { id: 'kappa', x: 46, y: 68, r: 2.4, brightness: 0.85 },
      { id: 'delta', x: 34, y: 55, r: 2.6, brightness: 0.9 },
      { id: 'nu', x: 22, y: 45, r: 2.4, brightness: 0.85 },
    ],
    lines: [
      ['alpherg', 'eta'], ['eta', 'gamma'], ['gamma', 'omega'], ['omega', 'iota'],
      ['iota', 'lambda'], ['lambda', 'kappa'], ['kappa', 'delta'],
      ['delta', 'nu'], ['nu', 'alpherg'],
    ],
  },
};

/**
 * Détermine le signe zodiacal courant à partir de la date du jour.
 */
export function getCurrentZodiacSign(date = new Date()) {
  const m = date.getMonth() + 1;  // 1..12
  const d = date.getDate();
  const md = m * 100 + d;         // ex: 218 = 18 février
  // Bornes selon Tropical Zodiac usuel
  if (md >= 321 && md <= 419) return 'aries';
  if (md >= 420 && md <= 520) return 'taurus';
  if (md >= 521 && md <= 620) return 'gemini';
  if (md >= 621 && md <= 722) return 'cancer';
  if (md >= 723 && md <= 822) return 'leo';
  if (md >= 823 && md <= 922) return 'virgo';
  if (md >= 923 && md <= 1022) return 'libra';
  if (md >= 1023 && md <= 1121) return 'scorpio';
  if (md >= 1122 && md <= 1221) return 'sagittarius';
  if (md >= 1222 || md <= 119) return 'capricorn';
  if (md >= 120 && md <= 218) return 'aquarius';
  return 'pisces';   // 219 → 320
}

export default function LiveConstellation({ sign = 'auto', size = 380 }) {
  const resolvedSign = sign === 'auto' ? getCurrentZodiacSign() : sign;
  const constellation = CONSTELLATIONS[resolvedSign] || CONSTELLATIONS.aquarius;

  const byId = useMemo(() => {
    const m = {};
    constellation.stars.forEach((s) => { m[s.id] = s; });
    return m;
  }, [constellation]);

  return (
    <div
      aria-hidden="true"
      data-testid="live-constellation"
      data-sign={resolvedSign}
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 0,
      }}>
      <div style={{
        width: size, height: size,
        animation: 'lc-rotate 120s linear infinite',
      }}>
        <svg viewBox="0 0 100 100" width="100%" height="100%" style={{ overflow: 'visible' }}>
          <defs>
            <radialGradient id="lc-glow">
              <stop offset="0%" stopColor="#F7F5F0" stopOpacity="1" />
              <stop offset="50%" stopColor="#C9A24B" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#C9A24B" stopOpacity="0" />
            </radialGradient>
            <filter id="lc-star-glow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="0.6" />
              <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {constellation.lines.map(([a, b], i) => {
            const sa = byId[a]; const sb = byId[b];
            if (!sa || !sb) return null;
            return (
              <line
                key={`${resolvedSign}-l-${i}`}
                x1={sa.x} y1={sa.y}
                x2={sb.x} y2={sb.y}
                stroke="#C9A24B"
                strokeWidth="0.15"
                strokeOpacity="0.55"
                strokeLinecap="round"
                style={{
                  strokeDasharray: '200',
                  strokeDashoffset: '200',
                  animation: `lc-draw 2200ms ease-out ${1 + i * 0.35}s forwards`,
                }}
              />
            );
          })}

          {constellation.stars.map((s, i) => (
            <g key={`${resolvedSign}-s-${s.id}`}>
              <circle cx={s.x} cy={s.y} r={s.r * 1.6} fill="url(#lc-glow)"
                style={{
                  transformBox: 'fill-box', transformOrigin: 'center',
                  opacity: 0.45 * s.brightness,
                  animation: `lc-pulse-halo 4.5s ease-in-out ${i * 0.4}s infinite`,
                }} />
              <circle cx={s.x} cy={s.y} r={s.r * 0.35} fill="#F7F5F0"
                filter="url(#lc-star-glow)"
                style={{
                  transformBox: 'fill-box', transformOrigin: 'center',
                  opacity: 0.85 * s.brightness,
                  animation: `lc-pulse-core 4.5s ease-in-out ${i * 0.4}s infinite`,
                }} />
            </g>
          ))}
        </svg>

        {/* Nom du signe — micro label discret */}
        <div style={{
          position: 'absolute', bottom: -8, left: '50%', transform: 'translateX(-50%)',
          fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 500,
          letterSpacing: '0.32em', textTransform: 'uppercase',
          color: 'rgba(201,162,75,0.55)',
          animation: 'lc-fadein 1.6s ease-out 3s both',
        }}>
          {constellation.fr}
        </div>
      </div>

      <style>{`
        @keyframes lc-rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes lc-draw { from { stroke-dashoffset: 200; } to { stroke-dashoffset: 0; } }
        @keyframes lc-pulse-halo {
          0%, 100% { transform: scale(0.85); opacity: 0.28; }
          50%      { transform: scale(1.15); opacity: 0.55; }
        }
        @keyframes lc-pulse-core {
          0%, 100% { transform: scale(1);    opacity: 0.82; }
          50%      { transform: scale(1.25); opacity: 1; }
        }
        @keyframes lc-fadein { from { opacity: 0; transform: translate(-50%, 4px); } to { opacity: 1; transform: translate(-50%, 0); } }
        @media (prefers-reduced-motion: reduce) {
          [data-testid="live-constellation"] * { animation: none !important; }
        }
      `}</style>
    </div>
  );
}
