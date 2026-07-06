import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { SOLENA } from '../lib/solena';

const MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];
const BIRTH_KEY = 'pa_birth_data';

/**
 * Hero — présentation de Plume Astrale (maison d'astrologie) avec continuité vers Solena.
 * Pas de fausse lune 3D : la vidéo de Solena joue subtilement en fond → aucune cassure.
 * Une fois le formulaire complété, on scroll vers la section Solena et on émet un event
 * pour ouvrir la fenêtre de chat.
 */
export default function MoonHero() {
  const [step, setStep] = useState(1);
  const [birth, setBirth] = useState(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(BIRTH_KEY) || 'null');
      if (saved) return saved;
    } catch (e) { /* ignore */ }
    return { day: '', month: '', year: '', hour: '12', minute: '00', place: '' };
  });

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
    const data = {
      day: parseInt(birth.day, 10),
      month: parseInt(birth.month, 10),
      year: parseInt(birth.year, 10),
      hour: parseInt(birth.hour, 10),
      min: parseInt(birth.minute, 10),
      place: birth.place.trim(),
    };
    try { localStorage.setItem(BIRTH_KEY, JSON.stringify(data)); } catch (e) { /* ignore */ }
    // Émettre un event pour ouvrir la fenêtre de chat Solena
    window.dispatchEvent(new CustomEvent('pa:open-solena-chat', { detail: data }));
    // Scroll doux vers la section Solena
    const el = document.querySelector('[data-testid="home-solena-section"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <section
      className="relative w-full overflow-hidden"
      style={{
        background: '#050308',
        color: '#F4E8D2',
        minHeight: '100vh',
        paddingTop: 'clamp(80px, 12vh, 140px)',
        paddingBottom: 'clamp(60px, 10vh, 100px)',
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
          Offre de lancement · 20 crédits offerts à l&apos;inscription
        </span>
      </div>

      {/* ═══ FOND — vidéo Solena très diffuse pour continuité ═══ */}
      <div aria-hidden="true" style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden' }}>
        <video
          src={SOLENA.videos.secondary}
          poster={SOLENA.portrait}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          style={{
            position: 'absolute',
            top: '50%', left: '50%',
            width: '110%', height: '110%',
            objectFit: 'cover',
            transform: 'translate(-50%, -50%)',
            opacity: 0.28,
            filter: 'blur(3px) saturate(1.1)',
          }}
        />
        {/* Voile sombre pour lisibilité */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at 50% 40%, rgba(5,3,8,0.55) 0%, rgba(5,3,8,0.85) 55%, rgba(5,3,8,0.95) 100%)',
        }} />
        {/* Constellation étoiles subtiles */}
        <StarConstellations />
        {/* Aura dorée diffuse au centre */}
        <div style={{
          position: 'absolute', top: '35%', left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 'min(80vw, 700px)', height: 'min(80vw, 700px)',
          background: 'radial-gradient(circle, rgba(212,180,106,0.15) 0%, transparent 60%)',
          filter: 'blur(40px)',
        }} />
      </div>

      {/* ═══════ CONTENU CENTRAL ═══════ */}
      <div className="relative z-10 flex flex-col items-center justify-center text-center px-4 max-w-3xl mx-auto"
        style={{ minHeight: 'calc(100vh - 240px)' }}>

        {/* Ornement top */}
        <div className="mb-6" aria-hidden="true">
          <div className="flex items-center gap-3 opacity-60">
            <div style={{ width: 40, height: 1, background: 'linear-gradient(90deg, transparent, #D4B46A)' }} />
            <Sparkles style={{ width: 14, height: 14, color: '#D4B46A' }} strokeWidth={1.5} />
            <div style={{ width: 40, height: 1, background: 'linear-gradient(90deg, #D4B46A, transparent)' }} />
          </div>
        </div>

        {/* Kicker brand */}
        <div className="mb-4" data-testid="brand-kicker">
          <span
            className="text-[10px] md:text-xs uppercase"
            style={{ color: '#D4B46A', letterSpacing: '0.45em', fontWeight: 300, fontFamily: 'Cinzel, serif' }}
          >
            Plume&nbsp;·&nbsp;Astrale
          </span>
        </div>

        {/* Titre principal */}
        <h1
          className="mb-5"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(2rem, 5.5vw, 3.8rem)',
            lineHeight: 1.05,
            letterSpacing: '0.01em',
            color: '#F4E8D2',
            textShadow: '0 4px 40px rgba(0,0,0,0.9)',
          }}
          data-testid="moon-hero-title"
        >
          La maison d&apos;astrologie<br />
          où tes étoiles <em style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 200 }}>murmurent</em>.
        </h1>

        {/* Sous-titre — présentation Plume Astrale */}
        <p
          className="mb-10 max-w-xl mx-auto"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: 'clamp(1rem, 1.4vw, 1.15rem)',
            lineHeight: 1.6,
            color: 'rgba(244,232,210,0.78)',
            fontStyle: 'italic',
            textShadow: '0 2px 20px rgba(0,0,0,0.8)',
          }}
          data-testid="moon-hero-subtitle"
        >
          Décodage astral personnalisé, guidance intuitive et lecture de tes cycles amoureux —
          Solena t&apos;accueille dans son sanctuaire.
        </p>

        {/* Divider mystique */}
        <div className="flex items-center gap-2 mb-8 opacity-50" aria-hidden="true">
          <div style={{ width: 18, height: 1, background: 'rgba(212,180,106,0.6)' }} />
          <div style={{ width: 4, height: 4, borderRadius: '50%', background: '#D4B46A' }} />
          <div style={{ width: 18, height: 1, background: 'rgba(212,180,106,0.6)' }} />
        </div>

        {/* Instruction */}
        <p
          className="text-[10px] md:text-xs uppercase mb-3"
          style={{ color: 'rgba(212,180,106,0.85)', letterSpacing: '0.3em', fontWeight: 300 }}
          data-testid="moon-form-heading"
        >
          Ouvre les portes de ton ciel
        </p>

        {/* Step progress dots */}
        <div className="flex gap-2 mb-6" data-testid="step-progress">
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
              <MoonLabel>Étape 1 · Ta date de naissance</MoonLabel>
              <div className="grid grid-cols-3 gap-3">
                <MoonInput placeholder="Jour" value={birth.day} onChange={(v) => update('day', v)} testid="moon-day" />
                <select
                  value={birth.month}
                  onChange={(e) => update('month', e.target.value)}
                  className="w-full py-3 px-3 text-center outline-none text-white"
                  style={{ background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(212,180,106,0.25)', borderRadius: '999px', fontFamily: 'Cormorant Garamond, serif', fontSize: 15 }}
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
              <MoonLabel>Étape 2 · Ton heure de naissance</MoonLabel>
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
              <MoonLabel>Étape 3 · Ton lieu de naissance</MoonLabel>
              <MoonInput placeholder="Paris, France" value={birth.place} onChange={(v) => update('place', v)} testid="moon-place" fullWidth />
              <button
                onClick={submit}
                disabled={!canSubmit}
                className="w-full py-4 uppercase transition-all hover:scale-[1.02] disabled:opacity-40 flex items-center justify-center gap-2 relative overflow-hidden group"
                style={{
                  background: 'linear-gradient(135deg, #D4B46A 0%, #F4D98C 50%, #D4B46A 100%)',
                  color: '#0C0918',
                  letterSpacing: '0.15em',
                  fontWeight: 700,
                  fontSize: 11,
                  borderRadius: '999px',
                  boxShadow: '0 0 40px rgba(212,180,106,0.4), inset 0 1px 0 rgba(255,255,255,0.3)',
                }}
                data-testid="moon-submit-btn"
              >
                <Sparkles className="w-3.5 h-3.5" strokeWidth={2} />
                <span>Rencontrer Solena · Discuter maintenant</span>
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
             style={{ color: 'rgba(244,232,210,0.4)', letterSpacing: '0.28em' }}>
          AUCUNE CARTE BANCAIRE&nbsp;&nbsp;·&nbsp;&nbsp;RÉSULTAT INSTANTANÉ&nbsp;&nbsp;·&nbsp;&nbsp;100% CONFIDENTIEL
        </div>
      </div>
    </section>
  );
}

// ═══════════════════ Constellations SVG ═══════════════════
function StarConstellations() {
  // Generate a stable set of stars once
  const starsRef = useRef(null);
  if (!starsRef.current) {
    starsRef.current = Array.from({ length: 65 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      r: Math.random() * 1.4 + 0.4,
      op: 0.35 + Math.random() * 0.5,
      delay: Math.random() * 4,
    }));
  }
  return (
    <>
      <style>{`
        @keyframes pa-twinkle { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }
        .pa-star { animation: pa-twinkle 3.4s ease-in-out infinite; }
      `}</style>
      <svg
        aria-hidden="true"
        preserveAspectRatio="none"
        viewBox="0 0 100 100"
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
      >
        {starsRef.current.map((s, i) => (
          <circle
            key={i}
            className="pa-star"
            cx={s.x}
            cy={s.y}
            r={s.r * 0.08}
            fill="#F4E8D2"
            style={{ animationDelay: `${s.delay}s`, opacity: s.op }}
          />
        ))}
        {/* Trois constellations subtiles */}
        <g stroke="rgba(212,180,106,0.20)" strokeWidth="0.04" fill="none">
          <polyline points="12,18 18,22 25,20 32,26 28,33" />
          <polyline points="72,15 78,20 85,18 88,25" />
          <polyline points="20,78 28,82 35,80 42,86 48,82" />
        </g>
      </svg>
    </>
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
        background: 'rgba(0,0,0,0.5)',
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
