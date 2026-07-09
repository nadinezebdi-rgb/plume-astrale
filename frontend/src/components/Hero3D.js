import React, { useState, useEffect, lazy, Suspense } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, User, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Moon3D = lazy(() => import('./Moon3D'));

const MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];
const BIRTH_KEY = 'pa_birth_data';

/**
 * Hero3D — expérience 3D immersive above-the-fold :
 *  - Vraie Lune 3D en WebGL avec shader procédural (fBm)
 *  - Aura fluide Perlin dorée + halo indigo
 *  - Form 3-steps fondu dans l'interface, la Lune réagit à chaque étape
 *  - Bandeau or offre de lancement + logo + Mon Compte uniquement
 */
export default function Hero3D() {
  const { isAuthenticated } = useAuth();
  const [step, setStep] = useState(1);
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
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const update = (k, v) => setBirth((p) => ({ ...p, [k]: v }));
  const updateWithValidation = (k, v) => {
    update(k, v);
    if (errors[k]) setErrors((prev) => ({ ...prev, [k]: '' }));
  };

  // ═══════════ VALIDATIONS ═══════════
  const isValidDay = (d) => d && /^\d{1,2}$/.test(d) && parseInt(d, 10) >= 1 && parseInt(d, 10) <= 31;
  const isValidMonth = (m) => m && m >= 1 && m <= 12;
  const isValidYear = (y) => y && /^\d{4}$/.test(y) && parseInt(y, 10) >= 1900 && parseInt(y, 10) <= new Date().getFullYear();
  const isValidHour = (h) => h !== '' && /^\d{1,2}$/.test(h) && parseInt(h, 10) >= 0 && parseInt(h, 10) <= 23;
  const isValidMinute = (m) => m !== '' && /^\d{1,2}$/.test(m) && parseInt(m, 10) >= 0 && parseInt(m, 10) <= 59;
  const isValidPlace = (p) => p.trim().length >= 2 && /^[a-zA-ZÀ-ÿ\s,'-]+$/.test(p.trim());

  const canProceedStep1 = isValidDay(birth.day) && isValidMonth(birth.month) && isValidYear(birth.year);
  const canProceedStep2 = isValidHour(birth.hour) && isValidMinute(birth.minute);
  const canSubmit = canProceedStep1 && canProceedStep2 && isValidPlace(birth.place);

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

  const submit = async () => {
    if (!canSubmit) return;
    setIsLoading(true);
    setErrors({});
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      const data = {
        day: parseInt(birth.day, 10),
        month: parseInt(birth.month, 10),
        year: parseInt(birth.year, 10),
        hour: parseInt(birth.hour, 10),
        min: parseInt(birth.minute, 10),
        place: birth.place.trim(),
      };
      try { localStorage.setItem(BIRTH_KEY, JSON.stringify(data)); } catch (e) { }
      window.dispatchEvent(new CustomEvent('pa:open-solena-chat', { detail: data }));
      const el = document.querySelector('[data-testid="home-solena-section"]');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      setErrors({ submit: 'Une erreur est survenue. Veuillez réessayer.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: 'radial-gradient(ellipse at 50% 30%, #1a1147 0%, #0C0918 55%, #050308 100%)',
        color: '#FFFFFF',
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

      {/* ═══ 3D Lune ═══ */}
      <div
        className={vibrate ? 'moon3d-vibrate' : ''}
        style={{ position: 'absolute', inset: 0, zIndex: 1, pointerEvents: 'none' }}
      >
        <Suspense fallback={null}>
          <Moon3D step={step} />
        </Suspense>
      </div>

      {/* ═══ Vignette pour focus sur le contenu ═══ */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, zIndex: 2, pointerEvents: 'none',
          background: 'radial-gradient(ellipse at 50% 50%, transparent 8%, rgba(12,9,24,0.28) 42%, rgba(5,3,8,0.85) 85%, #050308 100%)',
        }}
      />

      {/* ═══ Contenu texte + form ═══ */}
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
          className="mb-3 md:mb-4"
          style={{
            fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(1.9rem, 5.5vw, 3.6rem)',
            lineHeight: 1.08,
            letterSpacing: '0.01em',
            color: '#FFFFFF',
            textShadow: '0 4px 60px rgba(0,0,0,1), 0 0 30px rgba(226,191,101,0.15)',
            maxWidth: 720,
          }}
          data-testid="hero-title"
        >
          Qui est écrit <em style={{ color: '#E2BF65', fontStyle: 'italic', fontWeight: 300 }}>dans vos étoiles ?</em>
        </h1>

        <p
          className="mb-6 max-w-lg"
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.85rem, 1.2vw, 1rem)',
            fontWeight: 300,
            lineHeight: 1.6,
            color: '#CBD5E1',
            textShadow: '0 2px 20px rgba(0,0,0,0.9)',
          }}
          data-testid="hero-subtitle"
        >
          Trois pas suffisent pour révéler le portrait de votre âme sœur et vos prochaines fenêtres cosmiques de rencontre.
        </p>

        {/* Progress dots */}
        <div className="flex gap-2 mb-5" data-testid="step-progress">
          {[1, 2, 3].map((n) => (
            <div key={n} style={{
              width: 8, height: 8, borderRadius: '50%',
              background: step >= n ? '#E2BF65' : 'rgba(226,191,101,0.20)',
              boxShadow: step === n ? '0 0 14px rgba(226,191,101,0.8)' : 'none',
              transition: 'all 0.4s',
            }} />
          ))}
        </div>

        {/* Form fluide 3 étapes */}
        <div className="w-full max-w-md" data-testid="moon-form" style={{
          background: 'rgba(0,0,0,0.35)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(226,191,101,0.14)',
          borderRadius: 24,
          padding: 24,
        }}>
          {step === 1 && (
            <div className="space-y-4">
              <StepLabel step="1" icon="📅">Indiquez votre jour de naissance</StepLabel>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <FluidInput placeholder="Jour" value={birth.day} onChange={(v) => updateWithValidation('day', v)}
                    testid="moon-day" inputMode="numeric" pattern="[0-9]*" maxLength={2}
                    ariaLabel="Jour de naissance"
                    ariaInvalid={birth.day && !isValidDay(birth.day)}
                    ariaDescribedby="day-error" />
                  {birth.day && !isValidDay(birth.day) && (
                    <div id="day-error" className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      <span>Jour invalide (1-31)</span>
                    </div>
                  )}
                </div>
                <div>
                  <select
                    value={birth.month}
                    onChange={(e) => updateWithValidation('month', e.target.value)}
                    className="w-full py-3 px-3 text-center outline-none text-white transition-all focus:ring-2 focus:ring-offset-2 focus:ring-[#D4AF37]"
                    style={{
                      background: 'rgba(255,255,255,0.03)',
                      border: birth.month && !isValidMonth(birth.month) ? '1px solid #FF6B6B' : '1px solid rgba(226,191,101,0.25)',
                      borderRadius: 12,
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 14,
                      focusRingOffset: '2px',
                    }}
                    data-testid="moon-month"
                    aria-label="Mois de naissance"
                    aria-invalid={birth.month && !isValidMonth(birth.month)}>
                    <option value="" style={{ background: '#000' }}>Mois</option>
                    {MONTHS.map((m, i) => <option key={i} value={i + 1} style={{ background: '#000' }}>{m}</option>)}
                  </select>
                  {birth.month && !isValidMonth(birth.month) && (
                    <div className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      <span>Mois invalide</span>
                    </div>
                  )}
                </div>
                <div>
                  <FluidInput placeholder="Année" value={birth.year} onChange={(v) => updateWithValidation('year', v)}
                    testid="moon-year" inputMode="numeric" pattern="[0-9]*" maxLength={4}
                    ariaLabel="Année de naissance"
                    ariaInvalid={birth.year && !isValidYear(birth.year)}
                    ariaDescribedby="year-error" />
                  {birth.year && !isValidYear(birth.year) && (
                    <div id="year-error" className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      <span>Année invalide (1900-{new Date().getFullYear()})</span>
                    </div>
                  )}
                </div>
              </div>
              <NextBtn onClick={goNext} disabled={!canProceedStep1 || isLoading} testid="moon-next-1">Continuer</NextBtn>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <StepLabel step="2" icon="🕒">L&apos;heure exacte</StepLabel>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <FluidInput placeholder="Heure (12)" value={birth.hour} onChange={(v) => updateWithValidation('hour', v)}
                    testid="moon-hour" inputMode="numeric" pattern="[0-9]*" maxLength={2}
                    ariaLabel="Heure de naissance"
                    ariaInvalid={birth.hour && !isValidHour(birth.hour)}
                    ariaDescribedby="hour-error" />
                  {birth.hour && !isValidHour(birth.hour) && (
                    <div id="hour-error" className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      <span>Heure invalide (0-23)</span>
                    </div>
                  )}
                </div>
                <div>
                  <FluidInput placeholder="Minutes (00)" value={birth.minute} onChange={(v) => updateWithValidation('minute', v)}
                    testid="moon-minute" inputMode="numeric" pattern="[0-9]*" maxLength={2}
                    ariaLabel="Minutes de naissance"
                    ariaInvalid={birth.minute && !isValidMinute(birth.minute)}
                    ariaDescribedby="minute-error" />
                  {birth.minute && !isValidMinute(birth.minute) && (
                    <div id="minute-error" className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                      <AlertCircle style={{ width: 12, height: 12 }} />
                      <span>Minutes invalides (0-59)</span>
                    </div>
                  )}
                </div>
              </div>
              <div className="text-[10px]" style={{ color: 'rgba(203,213,225,0.65)', letterSpacing: '0.15em', fontFamily: 'Inter, sans-serif' }}>
                ✓ Approximative si inconnue
              </div>
              <NextBtn onClick={goNext} disabled={!canProceedStep2 || isLoading} testid="moon-next-2">Continuer</NextBtn>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <StepLabel step="3" icon="📍">Votre lieu de naissance</StepLabel>
              <div>
                <FluidInput placeholder="Paris, France" value={birth.place} onChange={(v) => updateWithValidation('place', v)}
                  testid="moon-place" fullWidth
                  ariaLabel="Lieu de naissance"
                  ariaInvalid={birth.place && !isValidPlace(birth.place)}
                  ariaDescribedby="place-error" />
                {birth.place && !isValidPlace(birth.place) && (
                  <div id="place-error" className="flex items-center gap-1 mt-1.5 text-[10px]" style={{ color: '#FF6B6B' }}>
                    <AlertCircle style={{ width: 12, height: 12 }} />
                    <span>Lieu invalide (min 2 caractères, lettres uniquement)</span>
                  </div>
                )}
              </div>
              <button
                onClick={submit}
                disabled={!canSubmit || isLoading}
                className="w-full py-4 uppercase disabled:opacity-40 flex items-center justify-center gap-2 relative overflow-hidden group liquid-cta transition-all focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37]"
                style={{
                  color: '#0A0603',
                  letterSpacing: '0.14em',
                  fontWeight: 700,
                  fontSize: 11,
                  borderRadius: 999,
                  border: 'none',
                  cursor: !canSubmit || isLoading ? 'not-allowed' : 'pointer',
                  fontFamily: 'Inter, sans-serif',
                  opacity: isLoading ? 0.8 : 1,
                }}
                data-testid="moon-submit-btn"
                aria-label={isLoading ? 'Révélation en cours...' : 'Révéler mes prochaines rencontres'}
                aria-disabled={!canSubmit || isLoading}>
                <span style={{ position: 'relative', zIndex: 2, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  {isLoading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>✨ Révélation en cours...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" strokeWidth={2} />
                      <span>🔮 Révéler mes prochaines rencontres (20 crédits offerts)</span>
                      <ArrowRight className="w-3.5 h-3.5" strokeWidth={2} />
                    </>
                  )}
                </span>
              </button>
              {errors.submit && (
                <div className="flex items-center gap-2 p-3 rounded-lg text-[10px]" style={{ background: 'rgba(255, 107, 107, 0.1)', border: '1px solid #FF6B6B', color: '#FF6B6B' }}>
                  <AlertCircle style={{ width: 14, height: 14, flexShrink: 0 }} />
                  <span>{errors.submit}</span>
                </div>
              )}
            </div>
          )}

          {/* Back link */}
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="mt-4 text-[10px] uppercase opacity-40 hover:opacity-80 transition-all"
              style={{ letterSpacing: '0.2em', color: '#CBD5E1', background: 'transparent', border: 'none', cursor: 'pointer', fontFamily: 'Inter, sans-serif' }}
              data-testid="moon-back-btn"
            >
              ← Étape précédente
            </button>
          )}
        </div>
      </div>

      {/* Styles locaux */}
      <style>{`
        @keyframes pa-moon-vibrate {
          0%, 100% { transform: translate(0, 0); }
          20% { transform: translate(-2px, 1px); }
          40% { transform: translate(2px, -1px); }
          60% { transform: translate(-1px, 2px); }
          80% { transform: translate(1px, -2px); }
        }
        .moon3d-vibrate { animation: pa-moon-vibrate 0.45s ease-in-out; }

        .liquid-cta {
          background: linear-gradient(135deg, #E2BF65 0%, #E8C766 50%, #B8860B 100%);
          box-shadow: 0 0 30px rgba(226,191,101,0.4), inset 0 1px 0 rgba(255,255,255,0.35);
          transition: transform 0.3s ease;
        }
        .liquid-cta::before {
          content: '';
          position: absolute;
          top: 50%; left: 50%;
          width: 0; height: 0;
          border-radius: 50%;
          background: radial-gradient(circle, #FFF3D6 0%, #E8C766 40%, transparent 100%);
          transform: translate(-50%, -50%);
          transition: width 0.6s cubic-bezier(0.16,1,0.3,1), height 0.6s cubic-bezier(0.16,1,0.3,1);
          z-index: 1;
        }
        .liquid-cta:hover::before {
          width: 220%; height: 220%;
        }
        .liquid-cta:hover {
          transform: scale(1.02);
          box-shadow: 0 0 50px rgba(226,191,101,0.7), inset 0 1px 0 rgba(255,255,255,0.5);
        }
      `}</style>
    </section>
  );
}

// ═══════════ Sub-components ═══════════
function StepLabel({ step, icon, children }) {
  return (
    <div className="flex items-center justify-center gap-2 mb-3">
      <span style={{ fontSize: 14 }}>{icon}</span>
      <div
        className="text-[10px] md:text-xs uppercase"
        style={{ color: '#E2BF65', letterSpacing: '0.28em', fontWeight: 400, fontFamily: 'Cinzel, Playfair Display, serif' }}
      >
        Étape {step} · {children}
      </div>
    </div>
  );
}

function FluidInput({ value, onChange, placeholder, fullWidth, testid, inputMode, pattern, maxLength, ariaLabel, ariaInvalid, ariaDescribedby }) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      inputMode={inputMode}
      pattern={pattern}
      maxLength={maxLength}
      className={`${fullWidth ? 'w-full' : ''} py-3 px-4 text-center outline-none text-white placeholder-white/30 transition-all focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37]`}
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: ariaInvalid ? '1px solid #FF6B6B' : '1px solid rgba(226,191,101,0.25)',
        borderRadius: 12,
        fontFamily: 'Inter, sans-serif',
        fontSize: 14,
        fontWeight: 300,
        focusRingOffset: '2px',
      }}
      data-testid={testid}
      aria-label={ariaLabel}
      aria-invalid={ariaInvalid}
      aria-describedby={ariaDescribedby}
    />
  );
}

function NextBtn({ children, onClick, disabled, testid }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full py-3.5 uppercase transition-all disabled:opacity-30 hover:scale-[1.01] flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[#D4AF37]"
      style={{
        background: 'transparent',
        border: '1px solid rgba(226,191,101,0.55)',
        color: '#E2BF65',
        letterSpacing: '0.22em',
        fontSize: 11,
        fontWeight: 400,
        borderRadius: 999,
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontFamily: 'Inter, sans-serif',
        focusRingOffset: '2px',
      }}
      data-testid={testid}
      aria-disabled={disabled}>
      {children} <ArrowRight className="w-3 h-3" />
    </button>
  );
}
