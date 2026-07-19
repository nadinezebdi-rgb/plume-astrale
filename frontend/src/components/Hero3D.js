import React, { useState, lazy, Suspense } from 'react';
import { Link } from 'react-router-dom';
import { User, AlertCircle, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import StarsAndClouds from './StarsAndClouds';
import LaunchBanner from './LaunchBanner';

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
  const [mysteryText, setMysteryText] = useState('');
  const [mysteryLink, setMysteryLink] = useState('');
  const [numerologyData, setNumerologyData] = useState({});

  // Messages d'analyse mystiques (3-4 secondes)
  const analysisMessages = [
    'Calcul de la synastrie des prénoms...',
    'Analyse des transits de Vénus et de la Lune...',
    'Soléna prépare votre clé de lecture...',
  ];

  const startAnalysis = async () => {
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

    // Appeler l'API pour générer le texte OpenAI + analyse numérique
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/couple/mystery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prenom1: nameOne.trim(),
          prenom2: nameTwo.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[Hero3D] Mystery analysis received:', data);
        setMysteryText(data.text || '');
        setMysteryLink(data.cta_link || '');
        setNumerologyData({
          letters_prenom1: data.letters_prenom1 || 0,
          letters_prenom2: data.letters_prenom2 || 0,
          total_letters: data.total_letters || 0,
          universal_year: data.universal_year || 0,
          compatibility_number: data.compatibility_number || 0,
          year: data.year || new Date().getFullYear(),
          numerology_1: data.numerology_1 || {},
          numerology_2: data.numerology_2 || {},
          compatibility: data.compatibility || {},
          personal_year: data.personal_year,
        });
      } else {
        console.error('[Hero3D] API error:', response.status);
        // Fallback text en cas d'erreur
        setMysteryText('Votre relation recèle des secrets que seuls les astres peuvent révéler...');
        setMysteryLink(`/outils/compatibilite?p1=${nameOne}&p2=${nameTwo}`);
        setNumerologyData({});
      }
    } catch (error) {
      console.error('[Hero3D] Fetch error:', error);
      // Fallback text
      setMysteryText('Votre relation recèle des secrets que seuls les astres peuvent révéler...');
      setMysteryLink(`/outils/compatibilite?p1=${nameOne}&p2=${nameTwo}`);
      setNumerologyData({});
    }
  };

  const handleCloseResult = () => {
    setShowModal(false);
    setShowResult(false);
    setNameOne('');
    setNameTwo('');
    setAnalysisStep(0);
    setMysteryText('');
    setMysteryLink('');
    setNumerologyData({});
  };

  // Formate l'analyse numérologique avec les données disponibles
  const formatNumerologyAnalysis = () => {
    if (!numerologyData || Object.keys(numerologyData).length === 0) {
      return null;
    }

    const {
      letters_prenom1 = 0,
      letters_prenom2 = 0,
      total_letters = 0,
      universal_year = 0,
      compatibility_number = 0,
      year = new Date().getFullYear(),
    } = numerologyData;

    return `Analyse numérologique du couple ${nameOne} et ${nameTwo}

Année ${year} · Chiffre vibratoire ${compatibility_number}

Cette vibration du chiffre ${compatibility_number} guide votre relation et révèle la nature profonde de votre connexion. Le calcul des lettres, l'année universelle, et l'harmonie de vos prénoms créent une géométrie énergétique unique.`;
  };

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: 'rgba(12, 17, 32, 0.55)',
        color: '#F5EEE0',
        minHeight: '100vh',
      }}
      data-testid="hero-3d"
    >
      {/* ═══ Bandeau d'urgence sticky top — cliquable + défilant + compte à rebours 48h ═══ */}
      <LaunchBanner />

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
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}><Link
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
        </Link><Link to="/connexion" className="flex items-center gap-2 group transition-all" style={{ color: '#0A0603', textDecoration: 'none', fontSize: 11, letterSpacing: '0.22em', textTransform: 'uppercase', padding: '8px 14px', borderRadius: 999, background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)', fontFamily: 'Inter, sans-serif', fontWeight: 600 }} data-testid="hero-login-btn"><User style={{ width: 12, height: 12 }} strokeWidth={1.5} />Se connecter</Link></div>
      </header>

      {/* ═══ Clouds & Stars Background Overlay ═══ */}
      <StarsAndClouds />

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
      <div style={{ position: 'absolute', inset: 0, zIndex: 1, filter: 'drop-shadow(0 30px 45px rgba(0,0,0,0.65)) drop-shadow(0 8px 18px rgba(0,0,0,0.45))' }}>          <Suspense fallback={null}>
                    
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
          minHeight: 'calc(88vh + 38px)',
          justifyContent: 'flex-end',
          paddingTop: '0px',
          paddingBottom: 'clamp(4px, 1vh, 12px)',
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
          Obtenez des réponses claires...
        </h2>

        {/* CTA Principal */}
        <button
          onClick={() => setShowModal(true)}
          className="group relative px-8 py-4 overflow-hidden rounded-full transition-all duration-300 hover:scale-105 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37]"
          style={{
            background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
            color: '#0A0603',
            fontFamily: 'Cinzel, sans-serif',
            fontWeight: 700,
            fontSize: 'clamp(0.95rem, 1.1vw, 1.1rem)',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 0 40px rgba(212,175,55,0.5)',
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

                <div className="text-center max-h-[70vh] overflow-y-auto pr-4">
                  {/* Result Header */}
                  <h4
                    style={{
                      fontFamily: 'Cinzel, Playfair Display, serif',
                      fontSize: '1.25rem',
                      fontWeight: 400,
                      color: '#E2BF65',
                      marginBottom: 12,
                      letterSpacing: '0.05em',
                    }}
                  >
                    ✨ Analyse Numérologique
                  </h4>
                  <p
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.85rem',
                      color: '#CBD5E1',
                      marginBottom: 20,
                    }}
                  >
                    Calcul pour <strong style={{ color: '#E2BF65' }}>{nameOne} & {nameTwo}</strong> en {numerologyData?.year || new Date().getFullYear()}
                  </p>

                  {/* Numerology Analysis - Displayed Immediately */}
                  <div
                    style={{
                      textAlign: 'left',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: '0.85rem',
                      color: '#CBD5E1',
                      lineHeight: 1.7,
                      marginBottom: 24,
                      whiteSpace: 'pre-wrap',
                      wordWrap: 'break-word',
                      background: 'rgba(226, 191, 101, 0.05)',
                      border: '1px solid rgba(226, 191, 101, 0.15)',
                      borderRadius: 8,
                      padding: 12,
                    }}
                    className="markdown-content"
                  >
                    {formatNumerologyAnalysis() || 'Calcul en cours...'}
                  </div>

                  {/* OpenAI Generated Text - Added Below */}
                  {mysteryText && (
                    <div
                      style={{
                        textAlign: 'left',
                        fontFamily: 'Inter, sans-serif',
                        fontSize: '0.9rem',
                        color: '#FFFFFF',
                        lineHeight: 1.8,
                        marginBottom: 24,
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word',
                        background: 'rgba(232, 199, 102, 0.03)',
                        border: '1px solid rgba(232, 199, 102, 0.1)',
                        borderRadius: 8,
                        padding: 12,
                      }}
                      className="markdown-content"
                    >
                      {mysteryText}
                    </div>
                  )}

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
                    Pour débloquer votre Étude de Synastrie Complète et explorer les aspects détaillés de votre compatibilité, créez un compte ou connectez-vous.
                  </p>

                  {/* Primary Upsell - Étude de Synastrie */}
                  <Link
                    to={mysteryLink || `/outils/compatibilite?p1=${nameOne}&p2=${nameTwo}`}
                    className="w-full py-3 px-4 rounded-lg font-semibold uppercase transition-all duration-300 hover:shadow-lg focus-visible:ring-2 focus-visible:ring-[#D4AF37] mb-3 inline-block"
                    style={{
                      background: 'linear-gradient(135deg, #E2BF65 0%, #E8C766 50%, #B8860B 100%)',
                      color: '#0A0603',
                      fontFamily: 'Cinzel, sans-serif',
                      fontSize: '0.9rem',
                      letterSpacing: '0.1em',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 0 30px rgba(226,191,101,0.4), inset 0 1px 0 rgba(255,255,255,0.35)',
                      textDecoration: 'none',
                      display: 'block',
                    }}
                    data-testid="upsell-synastrie-button"
                  >
                    Étude de Synastrie Complète
                  </Link>

                  {/* Auth Buttons Container */}
                  <div className="space-y-2 mt-4">
                    <p
                      style={{
                        fontFamily: 'Inter, sans-serif',
                        fontSize: '0.85rem',
                        color: '#E2BF65',
                        marginBottom: 12,
                        fontWeight: 600,
                        letterSpacing: '0.05em',
                      }}
                    >
                      Vous n'avez pas encore de compte ?
                    </p>

                    {/* Sign Up Button */}
                    <Link
                      to="/inscription"
                      className="w-full py-2.5 px-4 rounded-lg font-semibold uppercase transition-all duration-300"
                      style={{
                        background: 'rgba(226, 191, 101, 0.2)',
                        color: '#E8C766',
                        fontFamily: 'Cinzel, sans-serif',
                        fontSize: '0.85rem',
                        letterSpacing: '0.08em',
                        border: '1px solid rgba(226, 191, 101, 0.4)',
                        cursor: 'pointer',
                        textDecoration: 'none',
                        display: 'block',
                      }}
                      data-testid="signup-button"
                    >
                      Créer un Compte Gratuitement
                    </Link>

                    {/* Sign In Button */}
                    <Link
                      to="/connexion"
                      className="w-full py-2.5 px-4 rounded-lg font-semibold uppercase transition-all duration-300"
                      style={{
                        background: 'rgba(226, 191, 101, 0.1)',
                        color: '#CBD5E1',
                        fontFamily: 'Cinzel, sans-serif',
                        fontSize: '0.85rem',
                        letterSpacing: '0.08em',
                        border: '1px solid rgba(226, 191, 101, 0.2)',
                        cursor: 'pointer',
                        textDecoration: 'none',
                        display: 'block',
                      }}
                      data-testid="signin-button"
                    >
                      Se Connecter
                    </Link>
                  </div>
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
