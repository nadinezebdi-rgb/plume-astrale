/**
 * StarsAndClouds — Overlay avec nuages animés et étoiles scintillantes
 * Utilisé dans Hero3D et sections de fond pour uniformiser l'apparence
 */
export default function StarsAndClouds() {
  return (
    <svg
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        opacity: 0.75,
      }}
      viewBox="0 0 1200 800"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <style>{`
          @keyframes twinkle {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
          }
          .star { animation: twinkle 3s ease-in-out infinite; }
          .star-1 { animation-delay: 0s; }
          .star-2 { animation-delay: 0.5s; }
          .star-3 { animation-delay: 1s; }
          .star-4 { animation-delay: 1.5s; }
          .star-5 { animation-delay: 2s; }
          .star-6 { animation-delay: 2.5s; }
          @keyframes cloudDrift {
            0% { transform: translateX(0px); opacity: 0.25; }
            50% { opacity: 0.5; }
            100% { transform: translateX(150px); opacity: 0.25; }
          }
          .cloud { animation: cloudDrift 12s ease-in-out infinite; }
          .cloud-1 { animation-delay: 0s; }
          .cloud-2 { animation-delay: 3s; }
          .cloud-3 { animation-delay: 6s; }
          .cloud-4 { animation-delay: 9s; }
        `}</style>
        <filter id="cloudBlur">
          <feGaussianBlur in="SourceGraphic" stdDeviation="5" />
        </filter>
        <pattern id="cottonTexture" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <circle cx="5" cy="5" r="2.5" fill="rgba(255,255,255,0.3)" />
          <circle cx="15" cy="10" r="2" fill="rgba(255,255,255,0.25)" />
          <circle cx="8" cy="15" r="2.2" fill="rgba(255,255,255,0.28)" />
        </pattern>
      </defs>
      
      {/* Cloud 1 - Top left white cotton cloud */}
      <g className="cloud cloud-1" filter="url(#cloudBlur)">
        <ellipse cx="80" cy="80" rx="120" ry="35" fill="rgba(245, 245, 250, 0.45)" />
        <ellipse cx="150" cy="75" rx="100" ry="30" fill="rgba(245, 245, 250, 0.4)" />
        <ellipse cx="210" cy="85" rx="90" ry="32" fill="rgba(245, 245, 250, 0.35)" />
        <ellipse cx="40" cy="90" rx="80" ry="28" fill="rgba(245, 245, 250, 0.3)" />
        <rect x="40" y="55" width="180" height="70" fill="url(#cottonTexture)" opacity="0.4" />
      </g>

      {/* Cloud 2 - Top right white cotton cloud */}
      <g className="cloud cloud-2" filter="url(#cloudBlur)">
        <ellipse cx="950" cy="120" rx="130" ry="38" fill="rgba(240, 248, 255, 0.4)" />
        <ellipse cx="1020" cy="115" rx="110" ry="32" fill="rgba(240, 248, 255, 0.35)" />
        <ellipse cx="1080" cy="125" rx="100" ry="35" fill="rgba(240, 248, 255, 0.3)" />
        <ellipse cx="900" cy="135" rx="95" ry="30" fill="rgba(240, 248, 255, 0.25)" />
        <rect x="900" y="85" width="190" height="75" fill="url(#cottonTexture)" opacity="0.35" />
      </g>

      {/* Cloud 3 - Bottom white cotton cloud */}
      <g className="cloud cloud-3" filter="url(#cloudBlur)">
        <ellipse cx="350" cy="680" rx="125" ry="36" fill="rgba(245, 245, 250, 0.4)" />
        <ellipse cx="420" cy="675" rx="105" ry="31" fill="rgba(245, 245, 250, 0.35)" />
        <ellipse cx="480" cy="685" rx="95" ry="33" fill="rgba(245, 245, 250, 0.3)" />
        <ellipse cx="300" cy="695" rx="85" ry="28" fill="rgba(245, 245, 250, 0.25)" />
        <rect x="300" y="650" width="190" height="70" fill="url(#cottonTexture)" opacity="0.4" />
      </g>

      {/* Cloud 4 - Middle white cotton cloud */}
      <g className="cloud cloud-4" filter="url(#cloudBlur)">
        <ellipse cx="700" cy="480" rx="128" ry="37" fill="rgba(240, 248, 255, 0.38)" />
        <ellipse cx="770" cy="475" rx="108" ry="31" fill="rgba(240, 248, 255, 0.33)" />
        <ellipse cx="830" cy="485" rx="98" ry="34" fill="rgba(240, 248, 255, 0.28)" />
        <ellipse cx="650" cy="495" rx="90" ry="29" fill="rgba(240, 248, 255, 0.23)" />
        <rect x="650" y="450" width="190" height="70" fill="url(#cottonTexture)" opacity="0.35" />
      </g>

      {/* Scattered stars */}
      <circle cx="50" cy="80" r="1.2" className="star star-1" fill="rgba(255, 255, 255, 0.95)" />
      <circle cx="120" cy="60" r="0.9" className="star star-3" fill="rgba(255, 255, 255, 0.8)" />
      <circle cx="280" cy="90" r="1.0" className="star star-5" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="320" cy="120" r="1.0" className="star star-2" fill="rgba(255, 255, 255, 0.9)" />
      <circle cx="450" cy="70" r="0.8" className="star star-4" fill="rgba(255, 255, 255, 0.75)" />
      <circle cx="600" cy="110" r="0.95" className="star star-6" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="750" cy="50" r="1.1" className="star star-1" fill="rgba(255, 255, 255, 0.9)" />
      <circle cx="900" cy="80" r="0.9" className="star star-2" fill="rgba(255, 255, 255, 0.8)" />
      <circle cx="1050" cy="100" r="1.0" className="star star-3" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="1100" cy="200" r="1.1" className="star star-4" fill="rgba(255, 255, 255, 0.9)" />
      
      <circle cx="200" cy="250" r="0.9" className="star star-5" fill="rgba(255, 255, 255, 0.8)" />
      <circle cx="380" cy="300" r="1.0" className="star star-6" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="550" cy="280" r="0.8" className="star star-1" fill="rgba(255, 255, 255, 0.75)" />
      <circle cx="720" cy="320" r="0.95" className="star star-2" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="900" cy="300" r="0.9" className="star star-3" fill="rgba(255, 255, 255, 0.8)" />
      <circle cx="1050" cy="350" r="1.0" className="star star-4" fill="rgba(255, 255, 255, 0.85)" />
      
      <circle cx="100" cy="500" r="1.1" className="star star-5" fill="rgba(255, 255, 255, 0.9)" />
      <circle cx="280" cy="550" r="0.9" className="star star-6" fill="rgba(255, 255, 255, 0.8)" />
      <circle cx="450" cy="520" r="1.0" className="star star-1" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="650" cy="580" r="0.8" className="star star-2" fill="rgba(255, 255, 255, 0.75)" />
      <circle cx="800" cy="550" r="0.95" className="star star-3" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="1000" cy="600" r="1.0" className="star star-4" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="150" cy="600" r="1.1" className="star star-5" fill="rgba(255, 255, 255, 0.9)" />
      <circle cx="500" cy="450" r="1.0" className="star star-6" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="1150" cy="650" r="0.95" className="star star-1" fill="rgba(255, 255, 255, 0.85)" />
      <circle cx="80" cy="700" r="1.1" className="star star-2" fill="rgba(255, 255, 255, 0.9)" />
    </svg>
  );
}
