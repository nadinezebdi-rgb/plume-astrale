import React, { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, User, Calendar, Clock, MapPin } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import QuickOracle from '../components/QuickOracle';

const EnhancedMoon3D = lazy(() => import('../components/EnhancedMoon3D'));

const MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];
const BIRTH_KEY = 'pa_birth_data_v2';

/**
 * NewHome - Expérience immersive 3D unifiée
 * Design ultra-moderne avec :
 * - Fond noir absolu (#000000)
 * - Lune 3D photoréaliste avec aura fluide
 * - Formulaire 3 étapes intégré
 * - Animations liquides
 * - Typographie élégante (Cinzel/Inter)
 */
export default function NewHome() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showQuickOracle, setShowQuickOracle] = useState(false);
  const [birth, setBirth] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(BIRTH_KEY) || 'null');
      if (saved) return {
        day: String(saved.day || ''),
        month: String(saved.month || ''),
        year: String(saved.year || ''),
        hour: String(saved.hour ?? '12'),
        minute: String(saved.min ?? saved.minute ?? '00'),
        place: saved.place || '',
      };
    } catch (e) { /* ignore */ }
    return { day: '', month: '', year: '', hour: '12', minute: '00', place: '' };
  });
  const [vibrate, setVibrate] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const formRef = useRef(null);

  const update = (k, v) => setBirth((p) => ({ ...p, [k]: v }));

  const canProceedStep1 = birth.day && birth.month && birth.year;
  const canProceedStep2 = birth.hour !== '' && birth.minute !== '';
  const canSubmit = canProceedStep1 && canProceedStep2 && birth.place.trim().length >= 2;

  const triggerVibration = () => {
    setVibrate(true);
    setTimeout(() => setVibrate(false), 500);
  };

  const goNext = () => {
    if (step === 1 && canProceedStep1) {
      setStep(2);
      triggerVibration();
    } else if (step === 2 && canProceedStep2) {
      setStep(3);
      triggerVibration();
    }
  };

  const submit = () => {
    if (!canSubmit) return;
    const data = {
      day: parseInt(birth.day, 10),
      month: parseInt(birth.month, 10),
      year: parseInt(birth.year, 10),
      hour: parseInt(birth.hour, 10),
      min: parseInt(birth.minute, 10),
      place: birth.place.trim(),
    };
    try { localStorage.setItem(BIRTH_KEY, JSON.stringify(data)); } catch (e) { /* ignore */ }
    window.dispatchEvent(new CustomEvent('pa:open-solena-chat', { detail: data }));
    // Scroll vers la section Solena
    const el = document.querySelector('[data-testid="home-solena-section"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // Pré-chargement des assets
  useEffect(() => {
    const preloadAssets = async () => {
      try {
        // Pré-charger les textures de la lune
        const moonTexture = new Image();
        moonTexture.src = '/assets/moon_1024.jpg';
        await new Promise((resolve) => { moonTexture.onload = resolve; });
        
        // Pré-charger les polices
        document.fonts.ready.then(() => {
          setIsLoading(false);
        });
      } catch (e) {
        setIsLoading(false);
      }
    };
    preloadAssets();
  }, []);

  // Animation d'entrée
  useEffect(() => {
    const timer = setTimeout(() => {
      if (formRef.current) {
        formRef.current.style.opacity = '1';
        formRef.current.style.transform = 'translateY(0)';
      }
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: '#000000',
        color: '#FFFFFF',
        minHeight: '100vh',
        position: 'relative',
      }}
      data-testid="new-hero"
    >
      {/* ==================== AURA GLOW BACKGROUND ==================== */}
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(ellipse 80% 60% at 50% 50%, rgba(226, 191, 101, 0.08) 0%, transparent 40%),
            radial-gradient(ellipse 70% 50% at 50% 50%, rgba(167, 139, 250, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse 100% 100% at 50% 50%, rgba(18, 10, 30, 0.95) 0%, #000000 100%)
          `,
          animation: 'aurora-pulse 20s ease-in-out infinite alternate',
        }}
      />
      
      {/* ==================== STARS TWINKLING ==================== */}
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.85) 0%, transparent 100%),
            radial-gradient(1.2px 1.2px at 22% 38%, rgba(255,255,255,0.75) 0%, transparent 100%),
            radial-gradient(1px 1px at 35% 8%, rgba(255,255,255,0.90) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 48% 55%, rgba(255,255,255,0.65) 0%, transparent 100%),
            radial-gradient(1.3px 1.3px at 62% 20%, rgba(255,255,255,0.80) 0%, transparent 100%),
            radial-gradient(1px 1px at 75% 70%, rgba(255,255,255,0.70) 0%, transparent 100%),
            radial-gradient(1.4px 1.4px at 88% 35%, rgba(255,255,255,0.95) 0%, transparent 100%),
            radial-gradient(1px 1px at 5% 80%, rgba(255,255,255,0.60) 0%, transparent 100%),
            radial-gradient(1px 1px at 17% 92%, rgba(255,255,255,0.75) 0%, transparent 100%),
            radial-gradient(1.2px 1.2px at 30% 65%, rgba(255,255,255,0.55) 0%, transparent 100%),
            radial-gradient(1px 1px at 53% 88%, rgba(255,255,255,0.80) 0%, transparent 100%),
            radial-gradient(1.3px 1.3px at 67% 48%, rgba(255,255,255,0.65) 0%, transparent 100%),
            radial-gradient(1px 1px at 82% 12%, rgba(255,255,255,0.85) 0%, transparent 100%),
            radial-gradient(1px 1px at 92% 60%, rgba(255,255,255,0.70) 0%, transparent 100%),
            radial-gradient(1px 1px at 44% 30%, rgba(255,255,255,0.60) 0%, transparent 100%)
          `,
          backgroundSize: '100% 100%',
          animation: 'stars-twinkle 8s ease-in-out infinite alternate',
          opacity: 0.8,
        }}
      />

      {/* ==================== BANDEAU D'URGENCE ==================== */}
      <div
        className="absolute top-0 left-0 right-0 z-40 flex items-center justify-center px-4"
        style={{
          height: 40,
          background: 'linear-gradient(90deg, transparent 0%, rgba(226, 191, 101, 0.12) 20%, rgba(244, 217, 140, 0.18) 50%, rgba(226, 191, 101, 0.12) 80%, transparent 100%)',
          borderBottom: '1px solid rgba(226, 191, 101, 0.25)',
          boxShadow: '0 0 32px rgba(226, 191, 101, 0.25)',
        }}
        data-testid="launch-banner"
      >
        <span
          className="text-[10px] md:text-[11px] uppercase text-center"
          style={{
            color: '#E2BF65',
            letterSpacing: '0.28em',
            fontWeight: 300,
            fontFamily: 'Cinzel, serif',
            textShadow: '0 0 10px rgba(226, 191, 101, 0.3)',
          }}
        >
          ✧ OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L'INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX ✧
        </span>
      </div>

      {/* ==================== HEADER ÉPURÉ ==================== */}
      <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between px-6 md:px-10"
        style={{ paddingTop: 52, paddingBottom: 12 }}>
        <Link to="/" style={{
          fontFamily: 'Cinzel, serif',
          color: '#E2BF65',
          fontWeight: 400,
          fontSize: 15,
          letterSpacing: '0.35em',
          textDecoration: 'none',
          textShadow: '0 0 20px rgba(226, 191, 101, 0.4)',
        }} data-testid="hero-brand-logo">
          PLUME ASTRALE
        </Link>
        <Link
          to={isAuthenticated ? '/mon-compte' : '/connexion'}
          className="flex items-center gap-2 group transition-all"
          style={{
            color: 'rgba(226, 191, 101, 0.75)',
            textDecoration: 'none',
            fontSize: 11,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            padding: '8px 14px',
            borderRadius: 999,
            border: '1px solid rgba(226, 191, 101, 0.20)',
            fontFamily: 'Inter, sans-serif',
            background: 'rgba(226, 191, 101, 0.05)',
            backdropFilter: 'blur(10px)',
          }}
          data-testid="hero-account-btn"
        >
          <User style={{ width: 12, height: 12 }} strokeWidth={1.5} />
          Mon Compte
        </Link>
      </header>

      {/* ==================== LUNE 3D AMÉLIORÉE ==================== */}
      <div
        className={vibrate ? 'moon-vibrate' : ''}
        style={{ position: 'absolute', inset: 0, zIndex: 1, pointerEvents: 'none' }}
      >
        <Suspense fallback={
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{ color: 'rgba(226, 191, 101, 0.4)', fontSize: 10, letterSpacing: '0.3em', textTransform: 'uppercase' }}>
              La lune s'éveille…
            </div>
          </div>
        }>
          <EnhancedMoon3D step={step} isLoading={isLoading} />
        </Suspense>
      </div>

      {/* ==================== VIGNETTE DE FOCUS ==================== */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at 50% 50%, transparent 12%, rgba(0,0,0,0.25) 45%, rgba(0,0,0,0.75) 85%, #000000 100%)',
        }}
      />

      {/* ==================== CONTENU PRINCIPAL ==================== */}
      <div
        className="relative z-10 flex flex-col items-center justify-center text-center px-4"
        style={{
          minHeight: '100vh',
          paddingTop: 'clamp(80px, 11vh, 130px)',
          paddingBottom: 'clamp(30px, 5vh, 60px)',
        }}
      >
        {/* Titre magnétique */}
        <h1
          className="mb-4 md:mb-6"
          style={{
            fontFamily: 'Cinzel, Playfair Display, serif',
            fontWeight: 300,
            fontSize: 'clamp(2rem, 6vw, 4rem)',
            lineHeight: 1.08,
            letterSpacing: '0.02em',
            color: '#FFFFFF',
            textShadow: '0 4px 80px rgba(0,0,0,1), 0 0 40px rgba(226, 191, 101, 0.15)',
            maxWidth: 800,
          }}
          data-testid="hero-title"
        >
          Qui est écrit <em style={{ color: '#E2BF65', fontStyle: 'italic', fontWeight: 300 }}>dans vos étoiles</em> ?
        </h1>

        <p
          className="mb-8 max-w-lg"
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.9rem, 1.3vw, 1.1rem)',
            fontWeight: 300,
            lineHeight: 1.7,
            color: '#CBD5E1',
            textShadow: '0 2px 30px rgba(0,0,0,0.9)',
          }}
          data-testid="hero-subtitle"
        >
          Trois étapes suffisent pour révéler le portrait de votre âme sœur
          et vos prochaines fenêtres cosmiques de rencontre.
        </p>

        {/* CTA Quick Oracle - Friction elimination */}
        {!showQuickOracle && (
          <button
            onClick={() => {
              console.log('[CTA] "Découvrez votre oracle" cliqué');
              setShowQuickOracle(true);
            }}
            className="w-full max-w-md mb-8 py-4 rounded-2xl text-center transition-all hover:scale-105"
            style={{
              background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
              color: '#0C0918',
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '1.1rem',
              fontWeight: 600,
              letterSpacing: '0.1em',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 10px 30px rgba(212,175,55,0.3)',
            }}
            data-testid="quick-oracle-cta"
          >
            ✨ Découvrez votre oracle du jour GRATUITEMENT
          </button>
        )}

        {/* Indicateur d'étape */}
        <div className="flex gap-2 mb-6" data-testid="step-progress">
          {[1, 2, 3].map((n) => (
            <div key={n} style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: step >= n ? '#E2BF65' : 'rgba(226, 191, 101, 0.15)',
              boxShadow: step === n 
                ? '0 0 20px rgba(226, 191, 101, 0.8), 0 0 0 2px rgba(226, 191, 101, 0.3)'
                : 'none',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            }} />
          ))}
        </div>

        {/* Quick Oracle Component */}
        {showQuickOracle && (
          <QuickOracle 
            onClose={() => setShowQuickOracle(false)}
            onSelectPack={(packId) => {
              // Navigation via React Router
              const packMap = {
                initiation: 'essentiel',
                clarte: 'premium',
                flammes: 'premium'
              };
              const planId = packMap[packId];
              localStorage.setItem('plume_astrale_plan', planId);
              console.log(`[QuickOracle] Pack sélectionné: ${packId} → Plan: ${planId}`);
              
              // Utiliser navigate au lieu de window.location.href
              setTimeout(() => {
                navigate('/paiement', { replace: false });
              }, 300);
            }}
          />
        )}

        {/* Formulaire 3 étapes */}
        {!showQuickOracle && (
        <div 
          ref={formRef}
          className="w-full max-w-md"
          data-testid="moon-form"
          style={{
            background: 'rgba(0, 0, 0, 0.45)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(226, 191, 101, 0.12)',
            borderRadius: 28,
            padding: 28,
            opacity: 0,
            transform: 'translateY(20px)',
            transition: 'opacity 0.6s ease, transform 0.6s ease',
          }}
        >
          {step === 1 && (
            <div className="space-y-5">
              <StepLabel step="1" icon="📅">Indiquez votre jour de naissance</StepLabel>
              <div className="grid grid-cols-3 gap-3">
                <FluidInput 
                  placeholder="Jour" 
                  value={birth.day} 
                  onChange={(v) => update('day', v)}
                  testid="moon-day" 
                  inputMode="numeric" 
                  pattern="[0-9]*" 
                  maxLength={2} 
                />
                <select
                  value={birth.month}
                  onChange={(e) => update('month', e.target.value)}
                  className="w-full py-3.5 px-4 text-center outline-none text-white transition-all"
                  style={{
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(226, 191, 101, 0.18)',
                    borderRadius: 14,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    fontWeight: 300,
                    color: '#FFFFFF',
                  }}
                  data-testid="moon-month">
                  <option value="" style={{ background: '#000', color: '#666' }}>Mois</option>
                  {MONTHS.map((m, i) => (
                    <option key={i} value={i + 1} style={{ background: '#000', color: '#FFF' }}>
                      {m}
                    </option>
                  ))}
                </select>
                <FluidInput 
                  placeholder="Année" 
                  value={birth.year} 
                  onChange={(v) => update('year', v)}
                  testid="moon-year" 
                  inputMode="numeric" 
                  pattern="[0-9]*" 
                  maxLength={4} 
                />
              </div>
              <NextBtn onClick={goNext} disabled={!canProceedStep1} testid="moon-next-1">
                Continuer
              </NextBtn>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <StepLabel step="2" icon="🕒">L'heure exacte</StepLabel>
              <div className="grid grid-cols-2 gap-3">
                <FluidInput 
                  placeholder="Heure (12)" 
                  value={birth.hour} 
                  onChange={(v) => update('hour', v)}
                  testid="moon-hour" 
                  inputMode="numeric" 
                  pattern="[0-9]*" 
                  maxLength={2} 
                />
                <FluidInput 
                  placeholder="Minutes (00)" 
                  value={birth.minute} 
                  onChange={(v) => update('minute', v)}
                  testid="moon-minute" 
                  inputMode="numeric" 
                  pattern="[0-9]*" 
                  maxLength={2} 
                />
              </div>
              <div className="text-[10px]" style={{
                color: 'rgba(203, 213, 225, 0.5)',
                letterSpacing: '0.15em',
                fontFamily: 'Inter, sans-serif',
                textAlign: 'center',
              }}>
                Approximative si inconnue
              </div>
              <NextBtn onClick={goNext} disabled={!canProceedStep2} testid="moon-next-2">
                Continuer
              </NextBtn>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-5">
              <StepLabel step="3" icon="📍">Votre lieu de naissance</StepLabel>
              <FluidInput 
                placeholder="Paris, France" 
                value={birth.place} 
                onChange={(v) => update('place', v)}
                testid="moon-place" 
                fullWidth 
              />
              <button
                onClick={submit}
                disabled={!canSubmit}
                className="w-full py-4.5 uppercase disabled:opacity-40 flex items-center justify-center gap-2 relative overflow-hidden group liquid-cta"
                style={{
                  color: '#0A0603',
                  letterSpacing: '0.14em',
                  fontWeight: 700,
                  fontSize: 11,
                  borderRadius: 999,
                  border: 'none',
                  cursor: canSubmit ? 'pointer' : 'not-allowed',
                  fontFamily: 'Inter, sans-serif',
                }}
                data-testid="moon-submit-btn"
              >
                <span style={{ position: 'relative', zIndex: 2, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  <Sparkles className="w-4 h-4" strokeWidth={2} />
                  <span>🔮 RÉVÉLER MES PROCHAINES RENCONTRES (20 CRÉDITS OFFERTS)</span>
                  <ArrowRight className="w-4 h-4" strokeWidth={2} />
                </span>
              </button>
            </div>
          )}

          {/* Bouton retour */}
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="mt-5 text-[10px] uppercase opacity-40 hover:opacity-80 transition-all"
              style={{
                letterSpacing: '0.2em',
                color: '#CBD5E1',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontFamily: 'Inter, sans-serif',
              }}
              data-testid="moon-back-btn"
            >
              ← Étape précédente
            </button>
          )}
        </div>
        )}

        {/* CTA secondaire pour découvrir Solena */}
        {!showQuickOracle && (
        <div className="mt-10">
          <Link
            to="/solena"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
            style={{
              border: '1px solid rgba(226, 191, 101, 0.35)',
              color: 'rgba(226, 191, 101, 0.85)',
              letterSpacing: '0.2em',
              fontWeight: 400,
              background: 'rgba(226, 191, 101, 0.05)',
              textDecoration: 'none',
              backdropFilter: 'blur(10px)',
            }}
            data-testid="discover-solena-btn"
          >
            <Sparkles style={{ width: 12, height: 12 }} strokeWidth={1.5} />
            Découvrir Solena
            <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={1.5} />
          </Link>
        </div>
        )}
      </div>

      {/* ==================== STYLES LOCAUX ==================== */}
      <style jsx>{`
        @keyframes aurora-pulse {
          0%, 100% { 
            opacity: 0.95;
            transform: scale(1); 
          }
          50% { 
            opacity: 1;
            transform: scale(1.02); 
          }
        }
        
        @keyframes stars-twinkle {
          0%, 100% { opacity: 0.7; }
          50% { opacity: 1; }
        }
        
        @keyframes moon-vibrate {
          0%, 100% { transform: translate(0, 0); }
          20% { transform: translate(-3px, 2px); }
          40% { transform: translate(3px, -2px); }
          60% { transform: translate(-2px, 3px); }
          80% { transform: translate(2px, -3px); }
        }
        
        .moon-vibrate {
          animation: moon-vibrate 0.5s ease-in-out;
        }
        
        .liquid-cta {
          background: linear-gradient(135deg, #E2BF65 0%, #F4D98C 50%, #B8860B 100%);
          box-shadow: 0 0 40px rgba(226, 191, 101, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.35);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .liquid-cta::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 50%;
          width: 0;
          height: 0;
          border-radius: 50%;
          background: radial-gradient(circle, #FFF3D6 0%, #F4D98C 40%, transparent 100%);
          transform: translate(-50%, -50%);
          transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1), height 0.6s cubic-bezier(0.16, 1, 0.3, 1);
          z-index: 1;
        }
        
        .liquid-cta:hover::before {
          width: 250%;
          height: 250%;
        }
        
        .liquid-cta:hover {
          transform: scale(1.02);
          box-shadow: 0 0 60px rgba(226, 191, 101, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }
        
        /* Focus states pour accessibilité */
        input:focus, select:focus {
          outline: none;
          border-color: rgba(226, 191, 101, 0.6) !important;
          box-shadow: 0 0 0 2px rgba(226, 191, 101, 0.15);
        }
        
        /* Placeholder styling */
        input::placeholder, select option[value=""] {
          color: rgba(255, 255, 255, 0.25) !important;
          font-style: italic;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
          width: 6px;
        }
        ::-webkit-scrollbar-track {
          background: #000000;
        }
        ::-webkit-scrollbar-thumb {
          background: rgba(226, 191, 101, 0.3);
          border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: rgba(226, 191, 101, 0.5);
        }
      `}</style>
    </section>
  );
}

// ==================== SUB-COMPONENTS ====================

function StepLabel({ step, icon, children }) {
  return (
    <div className="flex items-center justify-center gap-2 mb-2">
      <span style={{ fontSize: 16 }}>{icon}</span>
      <div
        className="text-[10px] md:text-xs uppercase"
        style={{
          color: '#E2BF65',
          letterSpacing: '0.28em',
          fontWeight: 400,
          fontFamily: 'Cinzel, serif',
        }}
      >
        Étape {step} · {children}
      </div>
    </div>
  );
}

function FluidInput({ value, onChange, placeholder, fullWidth, testid, inputMode, pattern, maxLength }) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      inputMode={inputMode}
      pattern={pattern}
      maxLength={maxLength}
      className={`${fullWidth ? 'w-full' : ''} py-3.5 px-4 text-center outline-none text-white placeholder-white/20 transition-all`}
      style={{
        background: 'rgba(255, 255, 255, 0.04)',
        border: '1px solid rgba(226, 191, 101, 0.18)',
        borderRadius: 14,
        fontFamily: 'Inter, sans-serif',
        fontSize: 14,
        fontWeight: 300,
      }}
      data-testid={testid}
    />
  );
}

function NextBtn({ children, onClick, disabled, testid }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full py-3.5 uppercase transition-all disabled:opacity-30 hover:scale-[1.01] flex items-center justify-center gap-2"
      style={{
        background: 'transparent',
        border: '1px solid rgba(226, 191, 101, 0.45)',
        color: '#E2BF65',
        letterSpacing: '0.22em',
        fontSize: 11,
        fontWeight: 400,
        borderRadius: 999,
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontFamily: 'Inter, sans-serif',
        boxShadow: '0 0 15px rgba(226, 191, 101, 0.15)',
      }}
      data-testid={testid}
    >
      {children} <ArrowRight className="w-3.5 h-3.5" />
    </button>
  );
}
