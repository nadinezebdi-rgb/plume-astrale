import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight } from 'lucide-react';

const MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];

/**
 * MoonHero — Hero minimaliste noir absolu.
 * Lune CSS ultra-realiste + aura doree + 3-step form transparent + micro-parallax souris.
 */
export default function MoonHero() {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const moonRef = useRef(null);
  const [step, setStep] = useState(1);
  const [birth, setBirth] = useState({ day: '', month: '', year: '', hour: '12', minute: '00', place: '' });

  // Parallax subtil : la lune tourne tres legerement selon la position souris
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current || !moonRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;   // -0.5 → +0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      // rotation tres douce : max 4°
      moonRef.current.style.transform = `translate(-50%, -50%) rotate(${x * 3}deg) translate(${x * 8}px, ${y * 6}px)`;
    };
    const el = containerRef.current;
    if (el) el.addEventListener('mousemove', handleMouseMove);
    return () => { if (el) el.removeEventListener('mousemove', handleMouseMove); };
  }, []);

  const update = (k, v) => setBirth((p) => ({ ...p, [k]: v }));

  const canProceedStep1 = birth.day && birth.month && birth.year;
  const canProceedStep2 = birth.hour !== '' && birth.minute !== '';
  const canSubmit = canProceedStep1 && canProceedStep2 && birth.place.trim().length >= 2;

  const goNext = () => {
    if (step === 1 && canProceedStep1) setStep(2);
    else if (step === 2 && canProceedStep2) setStep(3);
  };

  const submit = () => {
    if (!canSubmit) return;
    // On redirige vers /rencontres-astrales avec les donnees en query
    const q = new URLSearchParams({
      day: birth.day, month: birth.month, year: birth.year,
      hour: birth.hour, minute: birth.minute, place: birth.place.trim(),
    }).toString();
    navigate(`/rencontres-astrales?${q}`);
  };

  return (
    <section
      ref={containerRef}
      className="relative w-full overflow-hidden"
      style={{
        background: '#000000',
        color: '#F4E8D2',
        minHeight: '100vh',
        paddingTop: 'clamp(60px, 10vh, 120px)',
        paddingBottom: 'clamp(40px, 8vh, 80px)',
      }}
      data-testid="moon-hero"
    >
      {/* Bandeau or lumineux tout en haut */}
      <div
        className="absolute top-0 left-0 right-0 z-30 pointer-events-none"
        style={{
          height: '2px',
          background: 'linear-gradient(90deg, transparent, #D4B46A, #F4D98C, #D4B46A, transparent)',
          boxShadow: '0 0 20px rgba(212,180,106,0.6)',
        }}
        aria-hidden="true"
      />
      <div className="absolute top-3 left-0 right-0 z-30 text-center pointer-events-none">
        <span
          className="text-[9px] md:text-[10px] uppercase inline-block px-4"
          style={{ color: '#D4B46A', letterSpacing: '0.32em', fontWeight: 300 }}
          data-testid="launch-banner-text"
        >
          Offre de lancement · 20 crédits offerts à l&apos;inscription pour découvrir votre avenir amoureux
        </span>
      </div>

      {/* ═══════ LA LUNE ═══════ */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" style={{ zIndex: 1 }}>
        <div className="relative" style={{ width: 'min(85vw, 620px)', aspectRatio: '1/1' }}>
          {/* Aura doree diffuse */}
          <div style={{
            position: 'absolute', inset: '-30%',
            background: 'radial-gradient(circle at 50% 50%, rgba(212,180,106,0.25) 0%, rgba(212,180,106,0.12) 25%, rgba(197,160,89,0.05) 45%, transparent 70%)',
            filter: 'blur(30px)',
          }} />
          {/* Halo interne plus intense */}
          <div style={{
            position: 'absolute', inset: '5%',
            background: 'radial-gradient(circle at 55% 45%, rgba(244,217,140,0.18) 0%, rgba(212,180,106,0.10) 30%, transparent 60%)',
            filter: 'blur(20px)',
            borderRadius: '50%',
          }} />

          {/* La lune elle-meme (CSS pure) */}
          <div
            ref={moonRef}
            style={{
              position: 'absolute', top: '50%', left: '50%',
              width: '75%', height: '75%',
              borderRadius: '50%',
              transform: 'translate(-50%, -50%)',
              background: `
                radial-gradient(circle at 62% 32%, #F5E9D0 0%, #E4D3AC 18%, #C9B383 35%, #9E8B5F 55%, #6E5F3E 72%, #3A311F 88%, #1a1710 100%),
                radial-gradient(circle at 30% 70%, rgba(0,0,0,0.35) 0%, transparent 30%),
                radial-gradient(circle at 75% 60%, rgba(0,0,0,0.20) 0%, transparent 25%)
              `,
              backgroundBlendMode: 'multiply, multiply, normal',
              boxShadow: `
                inset -20px -30px 60px rgba(0,0,0,0.55),
                inset 20px 20px 40px rgba(255,235,190,0.10),
                0 0 80px rgba(212,180,106,0.35),
                0 0 160px rgba(212,180,106,0.20)
              `,
              transition: 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            data-testid="moon-sphere"
          >
            {/* Craters subtils (texture) */}
            <div style={{ position: 'absolute', top: '25%', left: '58%', width: '8%', height: '8%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,0,0,0.30), transparent 70%)' }} />
            <div style={{ position: 'absolute', top: '55%', left: '35%', width: '11%', height: '11%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,0,0,0.22), transparent 70%)' }} />
            <div style={{ position: 'absolute', top: '68%', left: '65%', width: '6%', height: '6%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,0,0,0.20), transparent 70%)' }} />
            <div style={{ position: 'absolute', top: '18%', left: '35%', width: '5%', height: '5%', borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,0,0,0.15), transparent 70%)' }} />
          </div>
        </div>
      </div>

      {/* ═══════ CONTENU CENTRAL ═══════ */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center px-4"
           style={{ minHeight: 'calc(100vh - 200px)' }}>

        {/* Titre magnetique */}
        <h1
          className="mb-6 md:mb-10"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(1.8rem, 5vw, 3.5rem)',
            lineHeight: 1.1,
            letterSpacing: '0.02em',
            color: '#F4E8D2',
            textShadow: '0 0 30px rgba(0,0,0,0.8)',
          }}
          data-testid="moon-hero-title"
        >
          Qui est écrit <em style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 200 }}>dans vos étoiles ?</em>
        </h1>

        {/* Step progress dots */}
        <div className="flex gap-2 mb-8" data-testid="step-progress">
          {[1, 2, 3].map((n) => (
            <div key={n} style={{
              width: 8, height: 8, borderRadius: '50%',
              background: step >= n ? '#D4B46A' : 'rgba(212,180,106,0.25)',
              boxShadow: step === n ? '0 0 12px rgba(212,180,106,0.7)' : 'none',
              transition: 'all 0.3s',
            }} />
          ))}
        </div>

        {/* Formulaire transparent 3 étapes */}
        <div className="w-full max-w-md" data-testid="moon-form">
          {step === 1 && (
            <div className="space-y-4">
              <MoonLabel>Étape 1 · Votre date de naissance</MoonLabel>
              <div className="grid grid-cols-3 gap-3">
                <MoonInput placeholder="Jour" value={birth.day} onChange={(v) => update('day', v)} testid="moon-day" />
                <select
                  value={birth.month}
                  onChange={(e) => update('month', e.target.value)}
                  className="w-full py-3 px-3 text-center outline-none text-white"
                  style={{ background: 'transparent', border: '1px solid rgba(212,180,106,0.25)', borderRadius: '999px', fontFamily: 'Cormorant Garamond, serif', fontSize: 15 }}
                  data-testid="moon-month">
                  <option value="" style={{ background: '#000' }}>Mois</option>
                  {MONTHS.map((m, i) => <option key={i} value={i + 1} style={{ background: '#000' }}>{m}</option>)}
                </select>
                <MoonInput placeholder="Année" value={birth.year} onChange={(v) => update('year', v)} testid="moon-year" />
              </div>
              <MoonNextBtn onClick={goNext} disabled={!canProceedStep1} testid="moon-next-1">Continuer</MoonNextBtn>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <MoonLabel>Étape 2 · Votre heure de naissance</MoonLabel>
              <div className="grid grid-cols-2 gap-3">
                <MoonInput placeholder="Heure (12)" value={birth.hour} onChange={(v) => update('hour', v)} testid="moon-hour" />
                <MoonInput placeholder="Minutes (00)" value={birth.minute} onChange={(v) => update('minute', v)} testid="moon-minute" />
              </div>
              <div className="text-[10px] opacity-40" style={{ letterSpacing: '0.15em' }}>Approximative si inconnue</div>
              <MoonNextBtn onClick={goNext} disabled={!canProceedStep2} testid="moon-next-2">Continuer</MoonNextBtn>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <MoonLabel>Étape 3 · Votre lieu de naissance</MoonLabel>
              <MoonInput placeholder="Paris, France" value={birth.place} onChange={(v) => update('place', v)} testid="moon-place" fullWidth />
              <button
                onClick={submit}
                disabled={!canSubmit}
                className="w-full py-4 uppercase transition-all hover:scale-[1.02] disabled:opacity-40 flex items-center justify-center gap-2 relative overflow-hidden group"
                style={{
                  background: 'linear-gradient(135deg, #D4B46A 0%, #F4D98C 50%, #D4B46A 100%)',
                  color: '#000000',
                  letterSpacing: '0.15em',
                  fontWeight: 600,
                  fontSize: 11,
                  borderRadius: '999px',
                  boxShadow: '0 0 40px rgba(212,180,106,0.4), inset 0 1px 0 rgba(255,255,255,0.3)',
                }}
                data-testid="moon-submit-btn"
              >
                <Sparkles className="w-3.5 h-3.5" strokeWidth={2} />
                <span>Révéler mes prochaines rencontres · 20 crédits offerts</span>
                <ArrowRight className="w-3.5 h-3.5" strokeWidth={2} />
              </button>
            </div>
          )}

          {/* Back link */}
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="mt-4 text-[10px] uppercase opacity-40 hover:opacity-80 transition-all"
              style={{ letterSpacing: '0.2em', color: '#F4E8D2' }}
              data-testid="moon-back-btn"
            >
              ← Étape précédente
            </button>
          )}
        </div>

        {/* Trust line */}
        <div className="mt-10 md:mt-14 text-[9px] md:text-[10px]"
             style={{ color: 'rgba(244,232,210,0.35)', letterSpacing: '0.28em' }}>
          AUCUNE CARTE BANCAIRE&nbsp;&nbsp;·&nbsp;&nbsp;RÉSULTAT INSTANTANÉ&nbsp;&nbsp;·&nbsp;&nbsp;100% CONFIDENTIEL
        </div>
      </div>
    </section>
  );
}

// ═══════════════════ Sub-components ═══════════════════
function MoonLabel({ children }) {
  return (
    <div
      className="text-[10px] md:text-xs uppercase mb-4"
      style={{ color: 'rgba(212,180,106,0.85)', letterSpacing: '0.3em', fontWeight: 300 }}
    >
      {children}
    </div>
  );
}

function MoonInput({ value, onChange, placeholder, fullWidth, testid }) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={`${fullWidth ? 'w-full' : ''} py-3 px-4 text-center outline-none text-white placeholder-white/30 transition-all focus:border-white/40`}
      style={{
        background: 'transparent',
        border: '1px solid rgba(212,180,106,0.25)',
        borderRadius: '999px',
        fontFamily: 'Cormorant Garamond, serif',
        fontSize: 15,
      }}
      data-testid={testid}
    />
  );
}

function MoonNextBtn({ children, onClick, disabled, testid }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full py-3.5 uppercase transition-all disabled:opacity-30 hover:scale-[1.01] flex items-center justify-center gap-2"
      style={{
        background: 'transparent',
        border: '1px solid rgba(212,180,106,0.6)',
        color: '#D4B46A',
        letterSpacing: '0.22em',
        fontSize: 11,
        fontWeight: 400,
        borderRadius: '999px',
      }}
      data-testid={testid}
    >
      {children} <ArrowRight className="w-3 h-3" />
    </button>
  );
}
