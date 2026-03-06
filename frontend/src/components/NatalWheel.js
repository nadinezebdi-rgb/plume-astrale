import React, { useState, useRef, useEffect } from 'react';

const ZODIAC = [
  { symbol: '\u2648', name: 'Belier', color: '#E879F9' },
  { symbol: '\u2649', name: 'Taureau', color: '#F4C542' },
  { symbol: '\u264A', name: 'Gemeaux', color: '#60A5FA' },
  { symbol: '\u264B', name: 'Cancer', color: '#E879F9' },
  { symbol: '\u264C', name: 'Lion', color: '#F4C542' },
  { symbol: '\u264D', name: 'Vierge', color: '#A78BFA' },
  { symbol: '\u264E', name: 'Balance', color: '#60A5FA' },
  { symbol: '\u264F', name: 'Scorpion', color: '#E879F9' },
  { symbol: '\u2650', name: 'Sagittaire', color: '#F4C542' },
  { symbol: '\u2651', name: 'Capricorne', color: '#A78BFA' },
  { symbol: '\u2652', name: 'Verseau', color: '#60A5FA' },
  { symbol: '\u2653', name: 'Poissons', color: '#E879F9' },
];

const PLANETS = [
  { symbol: '\u2609', name: 'Soleil', angle: 45, r: 95 },
  { symbol: '\u263D', name: 'Lune', angle: 120, r: 85 },
  { symbol: '\u263F', name: 'Mercure', angle: 200, r: 90 },
  { symbol: '\u2640', name: 'Venus', angle: 70, r: 80 },
  { symbol: '\u2642', name: 'Mars', angle: 280, r: 88 },
  { symbol: '\u2643', name: 'Jupiter', angle: 160, r: 75 },
  { symbol: '\u2644', name: 'Saturne', angle: 310, r: 70 },
];

const NatalWheel = ({ className = '' }) => {
  const [rotation, setRotation] = useState(0);
  const [hovered, setHovered] = useState(null);
  const [scale, setScale] = useState(1);
  const animRef = useRef(null);

  useEffect(() => {
    let frame;
    const animate = () => {
      setRotation(prev => (prev + 0.04) % 360);
      frame = requestAnimationFrame(animate);
    };
    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, []);

  const cx = 200, cy = 200;

  const zodiacRing = ZODIAC.map((z, i) => {
    const angle = (i * 30 - 90 + rotation) * (Math.PI / 180);
    const r = 165;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    const isHovered = hovered === z.name;
    return (
      <g key={z.name}
        onMouseEnter={() => setHovered(z.name)}
        onMouseLeave={() => setHovered(null)}
        style={{ cursor: 'pointer' }}
      >
        <text
          x={x} y={y}
          textAnchor="middle" dominantBaseline="central"
          fill={isHovered ? z.color : 'rgba(248,250,252,0.6)'}
          fontSize={isHovered ? 22 : 18}
          style={{ transition: 'all 0.3s', filter: isHovered ? `drop-shadow(0 0 8px ${z.color})` : 'none' }}
        >
          {z.symbol}
        </text>
        {isHovered && (
          <text x={x} y={y + 18} textAnchor="middle" fill={z.color}
            fontSize={8} fontFamily="Inter, sans-serif" fontWeight={500}
            style={{ letterSpacing: '0.1em', textTransform: 'uppercase' }}
          >
            {z.name}
          </text>
        )}
      </g>
    );
  });

  const houseDividers = Array.from({ length: 12 }, (_, i) => {
    const angle = (i * 30 + rotation) * (Math.PI / 180);
    const x1 = cx + 50 * Math.cos(angle);
    const y1 = cy + 50 * Math.sin(angle);
    const x2 = cx + 145 * Math.cos(angle);
    const y2 = cy + 145 * Math.sin(angle);
    return (
      <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
        stroke="rgba(248,250,252,0.06)" strokeWidth={0.5} />
    );
  });

  const planetMarkers = PLANETS.map(p => {
    const angle = (p.angle + rotation) * (Math.PI / 180);
    const x = cx + p.r * Math.cos(angle);
    const y = cy + p.r * Math.sin(angle);
    const isHovered = hovered === p.name;
    return (
      <g key={p.name}
        onMouseEnter={() => setHovered(p.name)}
        onMouseLeave={() => setHovered(null)}
        style={{ cursor: 'pointer' }}
      >
        <circle cx={x} cy={y} r={isHovered ? 12 : 8}
          fill={isHovered ? 'rgba(244,197,66,0.2)' : 'rgba(244,197,66,0.08)'}
          stroke={isHovered ? '#F4C542' : 'rgba(244,197,66,0.3)'}
          strokeWidth={0.8}
          style={{ transition: 'all 0.3s' }}
        />
        <text x={x} y={y} textAnchor="middle" dominantBaseline="central"
          fill={isHovered ? '#F4C542' : 'rgba(248,250,252,0.7)'}
          fontSize={isHovered ? 14 : 11}
          style={{ transition: 'all 0.3s', filter: isHovered ? 'drop-shadow(0 0 6px rgba(244,197,66,0.5))' : 'none' }}
        >
          {p.symbol}
        </text>
        {isHovered && (
          <text x={x} y={y + 18} textAnchor="middle" fill="#F4C542"
            fontSize={7} fontFamily="Inter, sans-serif" fontWeight={500}
            style={{ letterSpacing: '0.1em', textTransform: 'uppercase' }}
          >
            {p.name}
          </text>
        )}
      </g>
    );
  });

  return (
    <div
      className={`relative ${className}`}
      data-testid="natal-wheel"
      onMouseEnter={() => setScale(1.05)}
      onMouseLeave={() => setScale(1)}
      style={{ transition: 'transform 0.4s ease' }}
    >
      <svg
        viewBox="0 0 400 400"
        className="w-full h-full"
        style={{ transform: `scale(${scale})`, transition: 'transform 0.4s ease' }}
      >
        <defs>
          <radialGradient id="wheelGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(139,92,246,0.15)" />
            <stop offset="50%" stopColor="rgba(232,121,249,0.05)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>

        <circle cx={cx} cy={cy} r={195} fill="url(#wheelGlow)" />

        {/* Outer ring */}
        <circle cx={cx} cy={cy} r={185} fill="none"
          stroke="rgba(232,121,249,0.15)" strokeWidth={1} />
        <circle cx={cx} cy={cy} r={145} fill="none"
          stroke="rgba(248,250,252,0.06)" strokeWidth={0.5} />

        {/* Inner rings */}
        <circle cx={cx} cy={cy} r={110} fill="none"
          stroke="rgba(248,250,252,0.04)" strokeWidth={0.5} />
        <circle cx={cx} cy={cy} r={50} fill="none"
          stroke="rgba(244,197,66,0.12)" strokeWidth={0.8} />

        {/* Center dot */}
        <circle cx={cx} cy={cy} r={4} fill="#F4C542" opacity={0.6}>
          <animate attributeName="opacity" values="0.4;0.8;0.4" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx={cx} cy={cy} r={10} fill="none" stroke="rgba(244,197,66,0.2)" strokeWidth={0.5}>
          <animate attributeName="r" values="8;14;8" dur="4s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.3;0.1;0.3" dur="4s" repeatCount="indefinite" />
        </circle>

        {houseDividers}
        {planetMarkers}
        {zodiacRing}
      </svg>
    </div>
  );
};

export default NatalWheel;
