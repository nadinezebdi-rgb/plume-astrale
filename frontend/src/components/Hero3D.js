import React, { useState, lazy, Suspense } from 'react';
import { Link } from 'react-router-dom';
import { User, AlertCircle, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Moon3D = lazy(() => import('./Moon3D'));

/**
 * Hero3D — Funnel de Conversion Psychologique
 * ÉTAPE 1: CTA sur la lune (Hameçon)
 * ÉTAPE 2: Modal glassmorphism pour 2 prénoms (Micro-friction)
 * ÉTAPE 3: Animation mystique 3-4 secondes (Création de valeur)
 * ÉTAPE 4: Résultat + Upsell (Right Hook)
 */
export default function Hero3D() {
  const { isAuthenticated } = useAuth();
  
  // ═════ États du Funnel ═════
  const [showModal, setShowModal] = useState(false);
  const [nameOne, setNameOne] = useState('');
  const [nameTwo, setNameTwo] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [errors, setErrors] = useState({});

  // Messages d'analyse mystiques (3-4 secondes)
  const analysisMessages = [
    'Calcul de la synastrie des prénoms...',
    'Analyse des transits de Vénus et de la Lune...',
    'Soléna prépare votre clé de lecture...',
  ];

  const startAnalysis = () => {
    // Validation
    if (!nameOne.trim() || !nameTwo.trim()) {
      setErrors({
        nameOne: !nameOne.trim() ? 'Prénom requis' : '',
        nameTwo: !nameTwo.trim() ? 'Prénom requis' : '',
      });
      return;
    }
    setErrors({});
    setAnalyzing(true);
    setAnalysisStep(0);

    // Animation de 3.3 secondes (1.1 sec par message)
    const duration = 3300;
    const messages = analysisMessages.length;
    const intervalDuration = duration / messages;

    let step = 0;
    const interval = setInterval(() => {
      step++;
      setAnalysisStep(step);
      if (step >= messages) {
        clearInterval(interval);
        setTimeout(() => {
          setAnalyzing(false);
          setShowResult(true);
        }, 300);
      }
    }, intervalDuration);
  };

  const handleCloseResult = () => {
    setShowModal(false);
    setShowResult(false);
    setNameOne('');
    setNameTwo('');
    setAnalysisStep(0);
  };

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: '#111625',
        color: '#F5EEE0',
        minHeight: '100vh',
      }}
      data-testid="hero-3d"
    >
      {/* ═══ Bandeau d'urgence sticky top ═══ */}
      <div
        className="absolute top-0 left-0 right-0 z-40 flex items-center justify-center px-4"
        style={{
          height: 40,
          background: 'linear-gradient(90deg, transparent 0%, rgba(212,175,55,0.15) 20%, rgba(232,199,102,0.22) 50%, rgba(212,175,55,0.15) 80%, transparent 100%)',
          borderBottom: '1px solid rgba(212,175,55,0.35)',
          boxShadow: '0 0 24px rgba(212,175,55,0.3)',
        }}
        data-testid="launch-banner"
      >
        <span
          className="text-[10px] md:text-[11px] uppercase text-center"
          style={{ color: '#E8C766', letterSpacing: '0.28em', fontWeight: 300, fontFamily: 'Cinzel, Playfair Display, serif' }}
        >
          OFFRE DE LANCEMENT&nbsp;·&nbsp;20 CRÉDITS OFFERTS À L&apos;INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX
        </span>
      </div>

      {/* ═══ Header ultra-épuré ═══ */}
      <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 md:px-10"
        style={{ paddingTop: 52, paddingBottom: 12 }}>
        <Link to="/" style={{
          fontFamily: 'Cinzel, Playfair Display, serif',
          color: '#E2BF65',
          fontWeight: 400,
          fontSize: 15,
          letterSpacing: '0.35em',
          textDecoration: 'none',
          textShadow: '0 0 16px rgba(226,191,101,0.35)',
        }} data-testid="hero-brand-logo">
          PLUME ASTRALE
        </Link>
        <Link
          to={isAuthenticated ? '/mon-compte' : '/connexion'}
          className="flex items-center gap-2 group transition-all"
          style={{
            color: 'rgba(226,191,101,0.85)',
            textDecoration: 'none',
            fontSize: 11,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            padding: '8px 14px',
            borderRadius: 999,
            border: '1px solid rgba(226,191,101,0.50)',
            fontFamily: 'Inter, sans-serif',
          }}
          data-testid="hero-account-btn"
        >
          <User style={{ width: 12, height: 12 }} strokeWidth={1.5} />
          Mon Compte
        </Link>
      </header>

      {/* ═══ Clouds & Stars Background Overlay ═══ */}
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

        {/* Scattered stars - MANY MORE */}
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

      {/* ═══ 3D Lune avec Halo ═══ */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 1,
          pointerEvents: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Halo Glow autour de la lune */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            width: '600px',
            height: '600px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(232, 199, 102, 0.15) 0%, rgba(167, 139, 250, 0.08) 40%, transparent 70%)',
            filter: 'blur(60px)',
            zIndex: 0,
          }}
        />
        {/* Moon3D rendu par-dessus le halo */}
        <div style={{ position: 'absolute', inset: 0, zIndex: 1 }}>
          <Suspense fallback={null}>
            <Moon3D />
          </Suspense>
        </div>
      </div>

      {/* ═══ Vignette subtle harmony ═══ */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at 50% 50%, transparent 0%, rgba(17, 22, 37, 0.0) 100%)',
        }}
      />

      {/* ═══ ÉTAPE 1: L'Hameçon - CTA sur la lune ═══ */}
      <div
        className="relative z-10 flex flex-col items-center justify-center text-center px-4"
        style={{
          minHeight: '100vh',
          paddingTop: 'clamp(80px, 11vh, 130px)',
          paddingBottom: 'clamp(30px, 5vh, 60px)',
        }}
      >
        {/* Titre Principal */}
        <h2
          style={{
            fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(1.7rem, 4.8vw, 3.2rem)',
            lineHeight: 1.15,
            letterSpacing: '0.02em',
            color: '#FFFFFF',
            textShadow: '0 4px 60px rgba(0,0,0,1), 0 0 30px rgba(226,191,101,0.15)',
            maxWidth: 680,
            marginBottom: 16,
          }}
          data-testid="hero-headline"
        >
          Cessez de deviner ses sentiments.
          <br />
          Obtenez des réponses claires.
        </h2>

        {/* Sous-texte */}
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.95rem, 1.3vw, 1.1rem)',
            fontWeight: 300,
            lineHeight: 1.7,
            color: '#CBD5E1',
            textShadow: '0 2px 20px rgba(0,0,0,0.9)',
            maxWidth: 580,
            marginBottom: 32,
            fontStyle: 'italic',
          }}
          data-testid="hero-subheadline"
        >
          Soléna décode les énergies de votre relation pour vous dire exactement où vous allez.
        </p>

        {/* CTA Principal */}
        <button
          onClick={() => setShowModal(true)}
          className="group relative px-8 py-4 overflow-hidden rounded-full transition-all duration-300 hover:scale-105 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37]"
          style={{
            background: 'linear-gradient(135deg, #E2BF65 0%, #E8C766 50%, #B8860B 100%)',
            color: '#0A0603',
            fontFamily: 'Cinzel, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(0.95rem, 1.1vw, 1.1rem)',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 0 40px rgba(226,191,101,0.5), inset 0 1px 0 rgba(255,255,255,0.35)',
          }}
          data-testid="hero-cta-button"
        >
          <span style={{ position: 'relative', zIndex: 2 }}>
            Lever le voile sur mon couple
          </span>
          <div
            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            style={{
              background: 'radial-gradient(circle at 50% 50%, #FFF3D6 0%, #E8C766 40%, transparent 100%)',
              animation: 'pulse 2s ease-in-out infinite',
            }}
          />
        </button>
      </div>

      {/* ═══ ÉTAPE 2 + 3 + 4: Modal Glassmorphism ═══ */}
      {showModal && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-50 transition-opacity duration-300"
            style={{
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
            }}
            onClick={() => {
              if (!analyzing && !showResult) setShowModal(false);
            }}
            data-testid="modal-backdrop"
          />

          {/* Modal Container */}
          <div
            className="fixed top-1/2 left-1/2 z-50 w-full max-w-md transform -translate-x-1/2 -translate-y-1/2 p-6 rounded-2xl transition-all duration-300"
            style={{
              background: 'rgba(255, 243, 214, 0.08)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(226, 191, 101, 0.25)',
              boxShadow: '0 20px 80px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255,255,255,0.1)',
            }}
            data-testid="modal-container"
          >
            {/* ÉTAPE 2: Formulaire Input */}
            {!analyzing && !showResult && (
              <>
                {/* Close Button */}
                <button
                  onClick={() => setShowModal(false)}
                  className="absolute top-4 right-4 p-2 text-[#CBD5E1] hover:text-[#E2BF65] transition-colors"
                  style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
                >
                  <X size={20} strokeWidth={1.5} />
                </button>

                {/* Header */}
                <div className="mb-6 text-center">
                  <h3
                    style={{
                      fontFamily: 'Cinzel, Playfair Display, serif',
                      fontSize: '1.3rem',
                      fontWeight: 400,
                      color: '#FFFFFF',
                      marginBottom: 8,
                      letterSpacing: '0.05em',
                    }}
                  >
                    Votre Guidance Amoureuse
                  </h3>
                  <p
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.9rem',
                      color: '#CBD5E1',
                      fontStyle: 'italic',
                    }}
                  >
                    Pour aligner les astres, Soléna a besoin de vos vibrations
                  </p>
                </div>

                {/* Form Fields */}
                <div className="space-y-4 mb-6">
                  {/* Prénom 1 */}
                  <div>
                    <input
                      type="text"
                      placeholder="Votre prénom"
                      value={nameOne}
                      onChange={(e) => {
                        setNameOne(e.target.value);
                        if (errors.nameOne) setErrors((p) => ({ ...p, nameOne: '' }));
                      }}
                      className="w-full py-3 px-4 rounded-lg outline-none transition-all focus:ring-2 focus:ring-[#D4AF37] focus:ring-offset-2 focus:ring-offset-[rgba(255,243,214,0.08)]"
                      style={{
                        background: 'rgba(255,255,255,0.05)',
                        border: errors.nameOne ? '1px solid #FF6B6B' : '1px solid rgba(226,191,101,0.25)',
                        color: '#FFFFFF',
                        fontFamily: 'Inter, sans-serif',
                        fontSize: '0.95rem',
                      }}
                      data-testid="modal-name-one"
                    />
                    {errors.nameOne && (
                      <div
                        className="flex items-center gap-1 mt-1.5 text-[12px]"
                        style={{ color: '#FF6B6B' }}
                      >
                        <AlertCircle size={12} />
                        <span>{errors.nameOne}</span>
                      </div>
                    )}
                  </div>

                  {/* Prénom 2 */}
                  <div>
                    <input
                      type="text"
                      placeholder="Son prénom"
                      value={nameTwo}
                      onChange={(e) => {
                        setNameTwo(e.target.value);
                        if (errors.nameTwo) setErrors((p) => ({ ...p, nameTwo: '' }));
                      }}
                      className="w-full py-3 px-4 rounded-lg outline-none transition-all focus:ring-2 focus:ring-[#D4AF37] focus:ring-offset-2 focus:ring-offset-[rgba(255,243,214,0.08)]"
                      style={{
                        background: 'rgba(255,255,255,0.05)',
                        border: errors.nameTwo ? '1px solid #FF6B6B' : '1px solid rgba(226,191,101,0.25)',
                        color: '#FFFFFF',
                        fontFamily: 'Inter, sans-serif',
                        fontSize: '0.95rem',
                      }}
                      data-testid="modal-name-two"
                    />
                    {errors.nameTwo && (
                      <div
                        className="flex items-center gap-1 mt-1.5 text-[12px]"
                        style={{ color: '#FF6B6B' }}
                      >
                        <AlertCircle size={12} />
                        <span>{errors.nameTwo}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* CTA Button */}
                <button
                  onClick={startAnalysis}
                  className="w-full py-3 px-4 rounded-lg font-semibold uppercase transition-all duration-300 hover:shadow-lg focus-visible:ring-2 focus-visible:ring-[#D4AF37]"
                  style={{
                    background: 'linear-gradient(135deg, #E2BF65 0%, #E8C766 50%, #B8860B 100%)',
                    color: '#0A0603',
                    fontFamily: 'Cinzel, sans-serif',
                    fontSize: '0.9rem',
                    letterSpacing: '0.1em',
                    border: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 0 30px rgba(226,191,101,0.4), inset 0 1px 0 rgba(255,255,255,0.35)',
                  }}
                  data-testid="modal-submit-button"
                >
                  Lancer l'analyse vibratoire
                </button>
              </>
            )}

            {/* ÉTAPE 3: Animation Mystique */}
            {analyzing && (
              <div className="flex flex-col items-center justify-center py-12 gap-6">
                {/* Animated Constellation */}
                <div
                  style={{
                    width: 60,
                    height: 60,
                    position: 'relative',
                    animation: 'spin 4s linear infinite',
                  }}
                >
                  <svg
                    viewBox="0 0 100 100"
                    style={{
                      width: '100%',
                      height: '100%',
                      fill: 'none',
                      stroke: '#E2BF65',
                      strokeWidth: 1,
                      opacity: 0.6,
                    }}
                  >
                    {/* Simple constellation pattern */}
                    <circle cx="50" cy="20" r="3" />
                    <circle cx="80" cy="50" r="3" />
                    <circle cx="50" cy="80" r="3" />
                    <circle cx="20" cy="50" r="3" />
                    <line x1="50" y1="20" x2="80" y2="50" />
                    <line x1="80" y1="50" x2="50" y2="80" />
                    <line x1="50" y1="80" x2="20" y2="50" />
                    <line x1="20" y1="50" x2="50" y2="20" />
                  </svg>
                </div>

                {/* Analysis Message */}
                <div className="text-center">
                  <p
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.95rem',
                      color: '#E2BF65',
                      letterSpacing: '0.08em',
                      height: 24,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      minWidth: 280,
                    }}
                  >
                    {analysisStep > 0 && analysisMessages[analysisStep - 1]}
                  </p>
                </div>

                {/* Progress Dots */}
                <div className="flex gap-2">
                  {analysisMessages.map((_, i) => (
                    <div
                      key={i}
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: i < analysisStep ? '#E2BF65' : 'rgba(226,191,101,0.2)',
                        transition: 'all 0.3s ease',
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* ÉTAPE 4: Résultat + Upsell */}
            {showResult && !analyzing && (
              <>
                {/* Close Button */}
                <button
                  onClick={handleCloseResult}
                  className="absolute top-4 right-4 p-2 text-[#CBD5E1] hover:text-[#E2BF65] transition-colors"
                  style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
                >
                  <X size={20} strokeWidth={1.5} />
                </button>

                <div className="text-center">
                  {/* Result Header */}
                  <h4
                    style={{
                      fontFamily: 'Cinzel, Playfair Display, serif',
                      fontSize: '1.1rem',
                      fontWeight: 400,
                      color: '#E2BF65',
                      marginBottom: 16,
                      letterSpacing: '0.05em',
                    }}
                  >
                    Analyse Terminée
                    <br />
                    pour {nameTwo} & {nameOne}
                  </h4>

                  {/* Insight */}
                  <p
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.95rem',
                      color: '#FFFFFF',
                      lineHeight: 1.6,
                      marginBottom: 20,
                      fontWeight: 500,
                    }}
                  >
                    Soléna a détecté
                    <br />
                    <span style={{ color: '#E2BF65', fontWeight: 700 }}>
                      2 points d'alignement majeurs
                    </span>
                    <br />
                    et
                    <br />
                    <span style={{ color: '#FF6B6B', fontWeight: 700 }}>
                      1 blocage karmique
                    </span>
                    <br />
                    cette semaine dans votre relation.
                  </p>

                  {/* CTA Text */}
                  <p
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.9rem',
                      color: '#CBD5E1',
                      lineHeight: 1.6,
                      marginBottom: 24,
                      fontStyle: 'italic',
                    }}
                  >
                    Ne restez pas dans le flou. Découvrez immédiatement ce que les astres révèlent pour l'avenir de votre couple.
                  </p>

                  {/* Primary Upsell */}
                  <button
                    className="w-full py-3 px-4 rounded-lg font-semibold uppercase transition-all duration-300 hover:shadow-lg focus-visible:ring-2 focus-visible:ring-[#D4AF37] mb-3"
                    style={{
                      background: 'linear-gradient(135deg, #E2BF65 0%, #E8C766 50%, #B8860B 100%)',
                      color: '#0A0603',
                      fontFamily: 'Cinzel, sans-serif',
                      fontSize: '0.9rem',
                      letterSpacing: '0.1em',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 0 30px rgba(226,191,101,0.4), inset 0 1px 0 rgba(255,255,255,0.35)',
                    }}
                    data-testid="upsell-primary-button"
                  >
                    Accéder à ma guidance complète (10 crédits)
                  </button>

                  {/* Secondary Upsell */}
                  <button
                    className="w-full py-2 px-4 rounded-lg font-semibold uppercase transition-all duration-300 hover:bg-opacity-80"
                    style={{
                      background: 'rgba(226, 191, 101, 0.1)',
                      color: '#E2BF65',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.8rem',
                      letterSpacing: '0.08em',
                      border: '1px solid rgba(226, 191, 101, 0.3)',
                      cursor: 'pointer',
                    }}
                    data-testid="upsell-secondary-button"
                  >
                    Vous n'avez pas de crédits ? À partir de 4,99 €
                  </button>
                </div>
              </>
            )}
          </div>
        </>
      )}

      {/* Styles locaux */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
      `}</style>
    </section>
  );
}
