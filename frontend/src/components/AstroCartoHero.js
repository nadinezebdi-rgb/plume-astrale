import React from 'react';

/**
 * AstroCartoHero — visuel signature de la page /astrocartographie.
 * Une carte du monde très épurée avec 7 lignes planétaires colorées
 * qui la traversent — pour que l'utilisateur comprenne immédiatement
 * ce qu'est l'astrocartographie.
 *
 * Style : palette V3 (navy #0F1A3C, or #C9A24B, crème #F7F5F0), 
 * lignes minimalistes façon planche d'astronome ancien.
 */
const PLANETS = [
  { key: 'sun',     label: 'Soleil',   color: '#C9A24B', d: 'M 20 190 Q 200 40 380 210' },
  { key: 'moon',    label: 'Lune',     color: '#7A8AB0', d: 'M 30 60 Q 200 260 380 90' },
  { key: 'venus',   label: 'Vénus',    color: '#D4A574', d: 'M 40 240 Q 200 100 370 260' },
  { key: 'mars',    label: 'Mars',     color: '#B0533F', d: 'M 20 130 C 120 40 300 320 380 150' },
  { key: 'jupiter', label: 'Jupiter',  color: '#8B7A4E', d: 'M 30 280 C 140 200 260 60 380 240' },
  { key: 'saturn',  label: 'Saturne',  color: '#4E5B7A', d: 'M 40 40 C 160 200 240 120 380 300' },
  { key: 'neptune', label: 'Neptune',  color: '#6A8FA6', d: 'M 20 300 Q 200 200 380 40' },
];

const CITY_MARKERS = [
  { x: 88,  y: 138, label: 'Lisbonne' },
  { x: 198, y: 108, label: 'Paris' },
  { x: 285, y: 165, label: 'Bali' },
];

export default function AstroCartoHero({ size = 380 }) {
  return (
    <div
      data-testid="astrocarto-hero"
      style={{
        width: '100%',
        maxWidth: size,
        aspectRatio: '1 / 1',
        margin: '0 auto',
        position: 'relative',
        borderRadius: 20,
        overflow: 'hidden',
        background: 'linear-gradient(180deg, #F7F5F0 0%, #EFECE4 100%)',
        border: '1px solid rgba(201,162,75,0.35)',
        boxShadow:
          '0 24px 48px rgba(15,26,60,0.16), 0 0 0 1px rgba(201,162,75,0.15)',
      }}
    >
      <svg
        viewBox="0 0 400 340"
        width="100%"
        height="100%"
        preserveAspectRatio="xMidYMid meet"
        style={{ display: 'block' }}
      >
        {/* ═══ Grain papier via feTurbulence ═══ */}
        <defs>
          <filter id="acg-grain" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" />
            <feColorMatrix values="0 0 0 0 0.06  0 0 0 0 0.10  0 0 0 0 0.24  0 0 0 0.04 0" />
          </filter>
          {/* Gradient doré discret pour les liserés */}
          <linearGradient id="acg-gold" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#C9A24B" stopOpacity="0.35" />
            <stop offset="50%" stopColor="#C9A24B" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#C9A24B" stopOpacity="0.35" />
          </linearGradient>
        </defs>

        {/* ═══ Fond papier ═══ */}
        <rect width="400" height="340" fill="url(#acg-grain)" opacity="0.6" />

        {/* ═══ Cadre astronome ═══ */}
        <rect
          x="12" y="12" width="376" height="316"
          fill="none" stroke="url(#acg-gold)" strokeWidth="0.8"
          strokeDasharray="1 3" opacity="0.65"
        />

        {/* ═══ Méridiens & parallèles (grille discrète) ═══ */}
        <g stroke="#0F1A3C" strokeWidth="0.35" opacity="0.14">
          {[80, 130, 170, 210, 260].map((y) => (
            <line key={`h-${y}`} x1="24" y1={y} x2="376" y2={y} />
          ))}
          {[80, 140, 200, 260, 320].map((x) => (
            <line key={`v-${x}`} x1={x} y1="24" x2={x} y2="316" />
          ))}
        </g>

        {/* ═══ Silhouettes continents (chemins simplifiés artistiques) ═══ */}
        <g fill="#0F1A3C" opacity="0.10">
          {/* Amérique du Nord */}
          <path d="M 40 90 Q 55 75, 78 82 Q 100 88, 108 110 L 105 145 Q 85 155, 70 148 Q 55 142, 48 130 Q 40 118, 42 100 Z" />
          {/* Amérique du Sud */}
          <path d="M 100 170 Q 118 168, 125 185 L 128 220 Q 122 245, 108 250 Q 95 245, 92 225 Q 90 200, 98 178 Z" />
          {/* Europe */}
          <path d="M 175 95 Q 190 88, 210 92 Q 220 98, 218 112 Q 210 122, 195 122 Q 180 118, 172 108 Z" />
          {/* Afrique */}
          <path d="M 185 135 Q 210 130, 225 145 Q 232 175, 225 200 Q 215 230, 200 245 Q 185 240, 178 220 Q 170 190, 175 160 Z" />
          {/* Asie */}
          <path d="M 225 82 Q 260 78, 300 88 Q 322 102, 320 122 Q 305 138, 275 138 Q 240 132, 225 118 Z" />
          {/* Océanie */}
          <path d="M 290 195 Q 310 190, 320 205 Q 325 220, 315 232 Q 300 235, 290 225 Q 285 210, 290 198 Z" />
        </g>

        {/* ═══ Lignes planétaires ═══ */}
        <g fill="none" strokeLinecap="round">
          {PLANETS.map((p, i) => (
            <path
              key={p.key}
              d={p.d}
              stroke={p.color}
              strokeWidth={i === 0 ? 1.6 : 1.2}
              strokeDasharray={i % 2 === 0 ? '' : '4 3'}
              opacity="0.85"
            />
          ))}
        </g>

        {/* ═══ Points villes (les 3 "villes idéales") ═══ */}
        <g>
          {CITY_MARKERS.map((c) => (
            <g key={c.label}>
              <circle cx={c.x} cy={c.y} r="4.5" fill="#C9A24B" opacity="0.35" />
              <circle cx={c.x} cy={c.y} r="2.2" fill="#C9A24B" />
              <text
                x={c.x + 8}
                y={c.y + 3}
                fontFamily="Inter, sans-serif"
                fontSize="8"
                fontWeight="600"
                fill="#0F1A3C"
                opacity="0.75"
              >
                {c.label}
              </text>
            </g>
          ))}
        </g>

        {/* ═══ Étoile de repère (compass) ═══ */}
        <g transform="translate(345, 285)">
          <circle r="16" fill="none" stroke="#C9A24B" strokeWidth="0.6" opacity="0.7" />
          <path d="M 0 -12 L 2 0 L 0 12 L -2 0 Z" fill="#C9A24B" />
          <path d="M -12 0 L 0 2 L 12 0 L 0 -2 Z" fill="#C9A24B" opacity="0.5" />
          <text x="0" y="-19" fontFamily="Inter, sans-serif" fontSize="6" fontWeight="600" fill="#C9A24B" textAnchor="middle">
            N
          </text>
        </g>

        {/* ═══ Étiquette de la carte ═══ */}
        <text
          x="24" y="322"
          fontFamily="Inter, sans-serif"
          fontSize="8"
          letterSpacing="1.6"
          fill="#0F1A3C"
          opacity="0.55"
        >
          CARTE ASTRALE PLANÉTAIRE · PLUME ASTRALE
        </text>
      </svg>

      {/* ═══ Légende planètes ═══ */}
      <div
        style={{
          position: 'absolute',
          bottom: 12,
          right: 12,
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
          background: 'rgba(247,245,240,0.85)',
          border: '1px solid rgba(15,26,60,0.10)',
          borderRadius: 6,
          padding: '6px 8px',
          backdropFilter: 'blur(2px)',
          maxWidth: 92,
        }}
      >
        {PLANETS.slice(0, 4).map((p) => (
          <div
            key={p.key}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 5,
              fontFamily: 'Inter, sans-serif',
              fontSize: 7.5,
              color: '#0F1A3C',
              letterSpacing: '0.04em',
            }}
          >
            <span
              style={{
                width: 10,
                height: 1.5,
                background: p.color,
                borderRadius: 1,
                flexShrink: 0,
              }}
            />
            {p.label}
          </div>
        ))}
        <div
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 6.5,
            color: 'rgba(15,26,60,0.50)',
            marginTop: 2,
            fontStyle: 'italic',
          }}
        >
          + 3 autres lignes
        </div>
      </div>
    </div>
  );
}
