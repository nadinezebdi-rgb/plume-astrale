import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Moon, Stars } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

/* ═══════════════════════════════════════════════════════════
   COSMIC CANVAS — Multilayer animated background
═══════════════════════════════════════════════════════════ */
const CosmicCanvas = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = Math.max(window.innerHeight, 900);
    };
    resize();
    window.addEventListener('resize', resize);

    // Twinkling stars (conservé de ton code existant)
    const stars = Array.from({ length: 220 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.6 + 0.3,
      twinkle: Math.random() * Math.PI * 2,
      speed: 0.5 + Math.random() * 1.5,
      hue: Math.random() > 0.78
        ? `rgba(196,181,253,${0.55 + Math.random() * 0.45})`
        : `rgba(255,255,255,${0.55 + Math.random() * 0.45})`,
    }));

    // Shooting stars (conservé)
    const shootingStars = [];
    const spawnShooting = () => {
      if (Math.random() < 0.012 && shootingStars.length < 2) {
        shootingStars.push({
          x: Math.random() * canvas.width * 0.6,
          y: Math.random() * canvas.height * 0.4,
          length: 80 + Math.random() * 80,
          speed: 6 + Math.random() * 4,
          angle: Math.PI / 4 + (Math.random() * 0.15 - 0.075),
          life: 0,
        });
      }
    };

    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Stars
      stars.forEach(s => {
        s.twinkle += 0.025;
        const alpha = 0.5 + Math.sin(s.twinkle) * 0.5;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.hue.replace(/[\d.]+\)\$/, `${alpha.toFixed(2)})`);
        ctx.fill();
        if (s.r > 1.2) {
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 4, 0, Math.PI * 2);
          const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
          g.addColorStop(0, s.hue.replace(/[\d.]+\)\$/, `${(alpha * 0.4).toFixed(2)})`));
          g.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = g;
          ctx.fill();
        }
      });

      // Shooting stars
      spawnShooting();
      for (let i = shootingStars.length - 1; i >= 0; i--) {
        const ss = shootingStars[i];
        ss.x += Math.cos(ss.angle) * ss.speed;
        ss.y += Math.sin(ss.angle) * ss.speed;
        ss.life += 1;
        const tailX = ss.x - Math.cos(ss.angle) * ss.length;
        const tailY = ss.y - Math.sin(ss.angle) * ss.length;
        const grad = ctx.createLinearGradient(ss.x, ss.y, tailX, tailY);
        grad.addColorStop(0, 'rgba(255,255,255,0.9)');
        grad.addColorStop(0.4, 'rgba(196,181,253,0.4)');
        grad.addColorStop(1, 'rgba(196,181,253,0)');
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(ss.x, ss.y);
        ctx.lineTo(tailX, tailY);
        ctx.stroke();
        if (ss.life > 80 || ss.x > canvas.width || ss.y > canvas.height) {
          shootingStars.splice(i, 1);
        }
      }

      raf = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      style={{ opacity: 0.85 }}
    />
  );
};

/* ═══════════════════════════════════════════════════════════
   STICKY BANNER — Offre de lancement (NOUVEAU)
═══════════════════════════════════════════════════════════ */
const StickyBanner = () => {
  return (
    <div
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        background: 'linear-gradient(90deg, #D4AF37, #AA7C11)',
        padding: '12px 24px',
        textAlign: 'center',
        fontSize: '14px',
        fontWeight: '600',
        color: '#0B0E14',
        letterSpacing: '0.05em',
        boxShadow: '0 2px 12px rgba(212, 175, 55, 0.3)',
      }}
    >
      ✨ OFFRE DE LANCEMENT : 20 CRÉDITS OFFERTS À L'INSCRIPTION POUR DÉCOUVRIR VOTRE AVENIR AMOUREUX ✨
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   ANIMATED MOON — Rotating glyph for hero (AMÉLIORÉ)
═══════════════════════════════════════════════════════════ */
const MoonGlyph = () => (
  <div className="relative animate-float-soft" style={{ width: 260, height: 260 }}>
    {/* Outer halo (aura violette/indigo) */}
    <div
      className="absolute inset-0 rounded-full animate-glow-pulse"
      style={{
        background: 'radial-gradient(circle, rgba(74, 0, 224, 0.30) 0%, rgba(74, 0, 224, 0) 70%)',
      }}
    />
    {/* Moon disk */}
    <div
      className="absolute inset-8 rounded-full overflow-hidden"
      style={{
        background: 'radial-gradient(circle at 35% 35%, #F5EEE0 0%, #D9D3E8 35%, #9089B5 75%, #4A4870 100%)',
        boxShadow: 'inset -20px -20px 50px rgba(20, 15, 40, 0.6), 0 0 60px rgba(245, 238, 224, 0.15)',
      }}
    >
      {/* Rotating craters layer */}
      <div className="absolute inset-0 animate-spin-moon">
        <div className="absolute rounded-full" style={{ width: 18, height: 18, top: '25%', left: '32%', background: 'rgba(74, 72, 112, 0.4)', boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 12, height: 12, top: '50%', left: '55%', background: 'rgba(74, 72, 112, 0.35)' }} />
        <div className="absolute rounded-full" style={{ width: 8, height: 8, top: '65%', left: '30%', background: 'rgba(74, 72, 112, 0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 14, height: 14, top: '35%', left: '65%', background: 'rgba(74, 72, 112, 0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 6, height: 6, top: '70%', left: '60%', background: 'rgba(74, 72, 112, 0.28)' }} />
        <div className="absolute rounded-full" style={{ width: 10, height: 10, top: '20%', left: '60%', background: 'rgba(74, 72, 112, 0.32)' }} />
      </div>
    </div>
    {/* Rotating zodiac ring */}
    <svg className="absolute inset-0 animate-spin-slow" viewBox="0 0 260 260">
      <circle cx="130" cy="130" r="118" fill="none" stroke="rgba(212, 180, 106, 0.18)" strokeDasharray="2 6" />
      <circle cx="130" cy="130" r="126" fill="none" stroke="rgba(167, 139, 250, 0.12)" strokeDasharray="1 10" />
    </svg>
  </div>
);

/* ═══════════════════════════════════════════════════════════
   PAGE
═══════════════════════════════════════════════════════════ */
const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [scrollY, setScrollY] = useState(0);
  const [step, setStep] = useState(1);
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthCity, setBirthCity] = useState('');
  const [showOverlay, setShowOverlay] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [chatQuestion, setChatQuestion] = useState('');

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Today's date and moon phase (conservé)
  const today = new Date();
  const dateFr = today.toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long',
  });
  const moonPhases = ['Nouvelle Lune', 'Premier Croissant', 'Premier Quartier', 'Gibbeuse Croissante', 'Pleine Lune', 'Gibbeuse Décroissante', 'Dernier Quartier', 'Dernier Croissant'];
  const moonIdx = Math.floor(((today - new Date(today.getFullYear(), 0, 1)) / (1000 * 60 * 60 * 24 * 3.6875)) % 8);
  const moonPhase = moonPhases[moonIdx];

  // Next two months for transit window
  const monthNames = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  const nextMonth1 = monthNames[(today.getMonth() + 1) % 12];
  const nextMonth2 = monthNames[(today.getMonth() + 2) % 12];

  const handleCTAClick = () => {
    setShowOverlay(true);
    setTimeout(() => {
      setShowOverlay(false);
      setShowResults(true);
    }, 3000);
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    try { localStorage.setItem('pa_chat_seed', chatQuestion); } catch (_) {}
    navigate(isAuthenticated ? '/consultation' : '/inscription');
  };

  return (
    <div className="relative" style={{ overflow: 'hidden' }}>
      <SEO path="/" />
      <CosmicCanvas />
      <StickyBanner /> {/* NOUVEAU: Bandeau sticky en haut */}

      {/* ═══════ HERO SECTION ══════ */}
      <section
        className="relative min-h-screen flex items-center justify-center px-6 z-10"
        style={{
          paddingTop: 'calc(36px + 64px + 32px)', // Ajusté pour le bandeau sticky
          paddingBottom: '4rem',
        }}
      >
        {/* Vidéo de fond en loop (conservé) */}
        <video
          autoPlay
          muted
          loop
          playsInline
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            opacity: 0.18,
            zIndex: 0,
            pointerEvents: 'none',
          }}
        >
          <source src="/videos/hero.mp4" type="video/mp4" />
        </video>

        <div className="relative z-10 max-w-6xl w-full grid lg:grid-cols-2 gap-12 items-center">
          {/* LEFT — Text + Form */}
          <div className="text-center lg:text-left">
            {/* Logo simplifié (uniquement ACCUEIL et MON COMPTE) */}
            <div className="mb-8">
              <h1
                className="text-2xl font-bold tracking-wider"
                style={{
                  color: '#D4AF37',
                  fontFamily: 'Cinzel, serif',
                  letterSpacing: '0.1em',
                }}
              >
                PLUME ASTRALE
              </h1>
              <nav className="mt-4 flex gap-6 justify-center lg:justify-start">
                <a
                  href="/"
                  style={{
                    color: '#B0B5C0',
                    fontSize: '14px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    textDecoration: 'none',
                  }}
                >
                  Accueil
                </a>
                <a
                  href="/mon-compte"
                  style={{
                    color: '#B0B5C0',
                    fontSize: '14px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    textDecoration: 'none',
                  }}
                >
                  Mon Compte
                </a>
              </nav>
            </div>

            <div className="animate-fade-up" style={{ animationDelay: '100ms' }}>
              <h1
                className="font-display mb-6"
                style={{
                  fontSize: 'clamp(36px, 6vw, 68px)',
                  lineHeight: 1.05,
                  color: '#F8F9FA',
                  fontWeight: 300,
                  letterSpacing: '-0.02em',
                }}
              >
                Qui est écrit dans<br />
                <span className="italic pa-shimmer-gold">vos étoiles&nbsp;?</span>
              </h1>
            </div>

            <div className="animate-fade-up" style={{ animationDelay: '250ms' }}>
              <p
                className="text-base sm:text-lg max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed"
                style={{ color: '#B0B5C0', fontWeight: 300 }}
              >
                Découvrez votre potentiel de compatibilité et les périodes clés de rencontres
                amoureuses gravées dans votre ciel pour les prochains mois.
              </p>
            </div>

            {/* Formulaire étape par étape */}
            <div className="animate-fade-up" style={{ animationDelay: '400ms' }}>
              <div
                style={{
                  background: 'rgba(15, 14, 30, 0.65)',
                  border: '1px solid rgba(212, 175, 55, 0.25)',
                  borderRadius: 16,
                  padding: '24px 28px',
                  backdropFilter: 'blur(16px)',
                  maxWidth: 480,
                  marginLeft: 'auto',
                  marginRight: 'auto',
                }}
                className="lg:mx-0"
              >
                {/* Step 1: Date de naissance */}
                {step === 1 && (
                  <div data-testid="step-1">
                    <label
                      style={{
                        display: 'block',
                        fontSize: 13,
                        color: '#D4AF37',
                        letterSpacing: '0.06em',
                        marginBottom: 10,
                        fontFamily: 'Cinzel, serif',
                      }}
                    >
                      📅 Indiquez votre jour de naissance
                    </label>
                    <input
                      type="date"
                      lang="fr"
                      value={birthDate}
                      onChange={(e) => setBirthDate(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 14px',
                        borderRadius: 10,
                        background: 'rgba(255, 255, 255, 0.06)',
                        border: '1px solid rgba(212, 175, 55, 0.35)',
                        color: '#F8F9FA',
                        fontSize: 15,
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                    <button
                      onClick={() => birthDate && setStep(2)}
                      disabled={!birthDate}
                      style={{
                        marginTop: 14,
                        width: '100%',
                        padding: '12px',
                        borderRadius: 10,
                        background: birthDate ? 'linear-gradient(135deg, #D4AF37, #AA7C11)' : 'rgba(212, 175, 55, 0.2)',
                        border: 'none',
                        color: birthDate ? '#0B0E14' : 'rgba(212, 175, 55, 0.5)',
                        fontWeight: 700,
                        fontSize: 13,
                        letterSpacing: '0.1em',
                        textTransform: 'uppercase',
                        cursor: birthDate ? 'pointer' : 'default',
                        transition: 'all 0.2s',
                      }}
                      data-testid="step-1-continue"
                    >
                      Continuer →
                    </button>
                  </div>
                )}

                {/* Step 2: Heure de naissance */}
                {step === 2 && (
                  <div data-testid="step-2">
                    <label
                      style={{
                        display: 'block',
                        fontSize: 13,
                        color: '#D4AF37',
                        letterSpacing: '0.06em',
                        marginBottom: 10,
                        fontFamily: 'Cinzel, serif',
                      }}
                    >
                      🕒 L'heure exacte (si connue)
                    </label>
                    <input
                      type="time"
                      value={birthTime}
                      onChange={(e) => setBirthTime(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 14px',
                        borderRadius: 10,
                        background: 'rgba(255, 255, 255, 0.06)',
                        border: '1px solid rgba(212, 175, 55, 0.35)',
                        color: '#F8F9FA',
                        fontSize: 15,
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                    <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                      <button
                        onClick={() => setStep(1)}
                        style={{
                          flex: '0 0 auto',
                          padding: '12px 20px',
                          borderRadius: 10,
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(212, 175, 55, 0.2)',
                          color: 'rgba(212, 175, 55, 0.7)',
                          fontSize: 13,
                          cursor: 'pointer',
                        }}
                      >
                        ←
                      </button>
                      <button
                        onClick={() => setStep(3)}
                        style={{
                          flex: 1,
                          padding: '12px',
                          borderRadius: 10,
                          background: 'linear-gradient(135deg, #D4AF37, #AA7C11)',
                          border: 'none',
                          color: '#0B0E14',
                          fontWeight: 700,
                          fontSize: 13,
                          letterSpacing: '0.1em',
                          textTransform: 'uppercase',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                        }}
                        data-testid="step-2-continue"
                      >
                        {birthTime ? 'Continuer →' : 'Passer cette étape →'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3: Lieu de naissance */}
                {step === 3 && (
                  <div data-testid="step-3">
                    <label
                      style={{
                        display: 'block',
                        fontSize: 13,
                        color: '#D4AF37',
                        letterSpacing: '0.06em',
                        marginBottom: 10,
                        fontFamily: 'Cinzel, serif',
                      }}
                    >
                      📍 Votre lieu de naissance
                    </label>
                    <input
                      type="text"
                      placeholder="ex. Paris, Lyon, Marseille..."
                      value={birthCity}
                      onChange={(e) => setBirthCity(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 14px',
                        borderRadius: 10,
                        background: 'rgba(255, 255, 255, 0.06)',
                        border: '1px solid rgba(212, 175, 55, 0.35)',
                        color: '#F8F9FA',
                        fontSize: 15,
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                    <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                      <button
                        onClick={() => setStep(2)}
                        style={{
                          flex: '0 0 auto',
                          padding: '12px 20px',
                          borderRadius: 10,
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid rgba(212, 175, 55, 0.2)',
                          color: 'rgba(212, 175
