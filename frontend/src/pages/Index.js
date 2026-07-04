import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Moon, Stars } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

/* ═══════════════════════════════════════════════════════════
   COSMIC CANVAS — multilayer animated background
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

    // Twinkling stars
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

    // Shooting stars
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

      // stars
      stars.forEach(s => {
        s.twinkle += 0.025;
        const alpha = 0.5 + Math.sin(s.twinkle) * 0.5;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.hue.replace(/[\d.]+\)$/, `${alpha.toFixed(2)})`);
        ctx.fill();
        // halo for big stars
        if (s.r > 1.2) {
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 4, 0, Math.PI * 2);
          const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
          g.addColorStop(0, s.hue.replace(/[\d.]+\)$/, `${(alpha * 0.4).toFixed(2)})`));
          g.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = g;
          ctx.fill();
        }
      });

      // shooting
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
   ANIMATED MOON — rotating glyph for hero
═══════════════════════════════════════════════════════════ */
const MoonGlyph = () => (
  <div className="relative animate-float-soft" style={{ width: 260, height: 260 }}>
    {/* Outer halo */}
    <div className="absolute inset-0 rounded-full animate-glow-pulse"
      style={{
        background: 'radial-gradient(circle, rgba(167,139,250,0.30) 0%, rgba(167,139,250,0) 70%)',
      }} />
    {/* Moon disk (lighting stays static for realism) */}
    <div className="absolute inset-8 rounded-full overflow-hidden"
      style={{
        background: 'radial-gradient(circle at 35% 35%, #F5EEE0 0%, #D9D3E8 35%, #9089B5 75%, #4A4870 100%)',
        boxShadow: 'inset -20px -20px 50px rgba(20,15,40,0.6), 0 0 60px rgba(245,238,224,0.15)',
      }}>
      {/* Rotating craters layer — gives the impression of the moon spinning on its axis */}
      <div className="absolute inset-0 animate-spin-moon">
        <div className="absolute rounded-full" style={{ width: 18, height: 18, top: '25%', left: '32%', background: 'rgba(74,72,112,0.4)', boxShadow: 'inset 2px 2px 4px rgba(0,0,0,0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 12, height: 12, top: '50%', left: '55%', background: 'rgba(74,72,112,0.35)' }} />
        <div className="absolute rounded-full" style={{ width: 8, height: 8, top: '65%', left: '30%', background: 'rgba(74,72,112,0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 14, height: 14, top: '35%', left: '65%', background: 'rgba(74,72,112,0.3)' }} />
        <div className="absolute rounded-full" style={{ width: 6, height: 6, top: '70%', left: '60%', background: 'rgba(74,72,112,0.28)' }} />
        <div className="absolute rounded-full" style={{ width: 10, height: 10, top: '20%', left: '60%', background: 'rgba(74,72,112,0.32)' }} />
      </div>
    </div>
    {/* Rotating zodiac ring */}
    <svg className="absolute inset-0 animate-spin-slow" viewBox="0 0 260 260">
      <circle cx="130" cy="130" r="118" fill="none" stroke="rgba(212,180,106,0.18)" strokeDasharray="2 6" />
      <circle cx="130" cy="130" r="126" fill="none" stroke="rgba(167,139,250,0.12)" strokeDasharray="1 10" />
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

  // Step-by-step birth form
  const [step, setStep] = useState(1);
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthCity, setBirthCity] = useState('');

  // Constellation overlay state
  const [showOverlay, setShowOverlay] = useState(false);
  const [showResults, setShowResults] = useState(false);

  // Chat CTA input
  const [chatQuestion, setChatQuestion] = useState('');

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Today's french date
  const today = new Date();
  const dateFr = today.toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long',
  });
  const moonPhases = ['Nouvelle Lune', 'Premier Croissant', 'Premier Quartier', 'Gibbeuse Croissante', 'Pleine Lune', 'Gibbeuse Decroissante', 'Dernier Quartier', 'Dernier Croissant'];
  const moonIdx = Math.floor(((today - new Date(today.getFullYear(), 0, 1)) / (1000 * 60 * 60 * 24 * 3.6875)) % 8);
  const moonPhase = moonPhases[moonIdx];

  // Get approximate next two months for the transit window
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
    try { localStorage.setItem('pa_chat_seed', chatQuestion); } catch (_) { /* ignore */ }
    navigate(isAuthenticated ? '/consultation' : '/inscription');
  };

  return (
    <div className="relative" style={{ overflow: 'hidden' }}>
      <SEO path="/" />
      <CosmicCanvas />

      {/* ═══════ HERO ═══════ */}
      <section className="relative min-h-screen flex items-center justify-center px-6 z-10"
        style={{ paddingTop: 'calc(36px + 64px + 32px)', paddingBottom: '4rem' }}>
        {/* Vidéo de fond en loop */}
        <video
          autoPlay muted loop playsInline
          style={{
            position: 'absolute', inset: 0, width: '100%', height: '100%',
            objectFit: 'cover', objectPosition: 'center', opacity: 0.18, zIndex: 0,
            pointerEvents: 'none',
          }}
        >
          <source src="/videos/hero.mp4" type="video/mp4" />
        </video>

        <div className="relative z-10 max-w-6xl w-full grid lg:grid-cols-2 gap-12 items-center">
          {/* LEFT — text + form */}
          <div className="text-center lg:text-left">
            <div className="animate-fade-up" style={{ animationDelay: '100ms' }}>
              <h1 className="font-display mb-6"
                style={{
                  fontSize: 'clamp(36px, 6vw, 68px)',
                  lineHeight: 1.05,
                  color: '#F8F9FA',
                  fontWeight: 300,
                  letterSpacing: '-0.02em',
                }}>
                Qui est écrit dans<br />
                <span className="italic pa-shimmer-gold">vos étoiles&nbsp;?</span>
              </h1>
            </div>

            <div className="animate-fade-up" style={{ animationDelay: '250ms' }}>
              <p className="text-base sm:text-lg max-w-xl mx-auto lg:mx-0 mb-8 leading-relaxed"
                style={{ color: '#B0B5C0', fontWeight: 300 }}>
                Découvrez votre potentiel de compatibilité et les périodes clés de rencontres
                amoureuses gravées dans votre ciel pour les prochains mois.
              </p>
            </div>

            {/* ── Step-by-step birth form ── */}
            <div className="animate-fade-up" style={{ animationDelay: '400ms' }}>
              <div
                data-testid="birth-form-steps"
                style={{
                  background: 'rgba(15,14,30,0.65)',
                  border: '1px solid rgba(212,175,55,0.25)',
                  borderRadius: 16,
                  padding: '24px 28px',
                  backdropFilter: 'blur(16px)',
                  maxWidth: 480,
                  marginLeft: 'auto',
                  marginRight: 'auto',
                }}
                className="lg:mx-0"
              >
                {/* Step 1 */}
                {step === 1 && (
                  <div data-testid="step-1">
                    <label style={{ display: 'block', fontSize: 13, color: '#D4AF37', letterSpacing: '0.06em', marginBottom: 10, fontFamily: 'Cinzel, serif' }}>
                      📅 Indiquez votre jour de naissance
                    </label>
                    <input
                      type="date"
                      lang="fr"
                      value={birthDate}
                      onChange={(e) => setBirthDate(e.target.value)}
                      style={{
                        width: '100%', padding: '12px 14px', borderRadius: 10,
                        background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(212,175,55,0.35)',
                        color: '#F8F9FA', fontSize: 15, outline: 'none', boxSizing: 'border-box',
                      }}
                    />
                    <button
                      onClick={() => birthDate && setStep(2)}
                      disabled={!birthDate}
                      style={{
                        marginTop: 14, width: '100%', padding: '12px', borderRadius: 10,
                        background: birthDate ? 'linear-gradient(135deg, #D4AF37, #AA7C11)' : 'rgba(212,175,55,0.2)',
                        border: 'none', color: birthDate ? '#0B0E14' : 'rgba(212,175,55,0.5)',
                        fontWeight: 700, fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase',
                        cursor: birthDate ? 'pointer' : 'default', transition: 'all 0.2s',
                      }}
                      data-testid="step-1-continue"
                    >
                      Continuer →
                    </button>
                  </div>
                )}

                {/* Step 2 */}
                {step === 2 && (
                  <div data-testid="step-2">
                    <label style={{ display: 'block', fontSize: 13, color: '#D4AF37', letterSpacing: '0.06em', marginBottom: 10, fontFamily: 'Cinzel, serif' }}>
                      🕒 L&apos;heure exacte (si connue)
                    </label>
                    <input
                      type="time"
                      value={birthTime}
                      onChange={(e) => setBirthTime(e.target.value)}
                      style={{
                        width: '100%', padding: '12px 14px', borderRadius: 10,
                        background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(212,175,55,0.35)',
                        color: '#F8F9FA', fontSize: 15, outline: 'none', boxSizing: 'border-box',
                      }}
                    />
                    <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                      <button
                        onClick={() => setStep(1)}
                        style={{
                          flex: '0 0 auto', padding: '12px 20px', borderRadius: 10,
                          background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(212,175,55,0.2)',
                          color: 'rgba(212,175,55,0.7)', fontSize: 13, cursor: 'pointer',
                        }}
                      >
                        ←
                      </button>
                      <button
                        onClick={() => setStep(3)}
                        style={{
                          flex: 1, padding: '12px', borderRadius: 10,
                          background: 'linear-gradient(135deg, #D4AF37, #AA7C11)',
                          border: 'none', color: '#0B0E14',
                          fontWeight: 700, fontSize: 13, letterSpacing: '0.1em', textTransform: 'uppercase',
                          cursor: 'pointer', transition: 'all 0.2s',
                        }}
                        data-testid="step-2-continue"
                      >
                        {birthTime ? 'Continuer →' : 'Passer cette étape →'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3 */}
                {step === 3 && (
                  <div data-testid="step-3">
                    <label style={{ display: 'block', fontSize: 13, color: '#D4AF37', letterSpacing: '0.06em', marginBottom: 10, fontFamily: 'Cinzel, serif' }}>
                      📍 Votre lieu de naissance
                    </label>
                    <input
                      type="text"
                      placeholder="ex. Paris, Lyon, Marseille..."
                      value={birthCity}
                      onChange={(e) => setBirthCity(e.target.value)}
                      style={{
                        width: '100%', padding: '12px 14px', borderRadius: 10,
                        background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(212,175,55,0.35)',
                        color: '#F8F9FA', fontSize: 15, outline: 'none', boxSizing: 'border-box',
                      }}
                    />
                    <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                      <button
                        onClick={() => setStep(2)}
                        style={{
                          flex: '0 0 auto', padding: '12px 20px', borderRadius: 10,
                          background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(212,175,55,0.2)',
                          color: 'rgba(212,175,55,0.7)', fontSize: 13, cursor: 'pointer',
                        }}
                      >
                        ←
                      </button>
                      <button
                        onClick={() => birthCity && handleCTAClick()}
                        disabled={!birthCity}
                        style={{
                          flex: 1, padding: '14px 20px', borderRadius: 10,
                          background: birthCity
                            ? 'linear-gradient(135deg, #D4AF37 0%, #F0D060 50%, #AA7C11 100%)'
                            : 'rgba(212,175,55,0.2)',
                          border: 'none',
                          color: birthCity ? '#0B0E14' : 'rgba(212,175,55,0.5)',
                          fontWeight: 800, fontSize: 13, letterSpacing: '0.08em',
                          textTransform: 'uppercase', cursor: birthCity ? 'pointer' : 'default',
                          transition: 'all 0.3s',
                          boxShadow: birthCity ? '0 0 24px rgba(212,175,55,0.45)' : 'none',
                          animation: birthCity ? 'ctaPulse 2s ease-in-out infinite' : 'none',
                        }}
                        data-testid="hero-cta-primary"
                      >
                        🔮 RÉVÉLER MES PROCHAINES RENCONTRES (20 CRÉDITS OFFERTS)
                      </button>
                    </div>
                  </div>
                )}

                {/* Step dots */}
                <div style={{ display: 'flex', justifyContent: 'center', gap: 6, marginTop: 18 }}>
                  {[1, 2, 3].map((s) => (
                    <div key={s} style={{
                      width: s === step ? 20 : 6, height: 6, borderRadius: 3,
                      background: s === step ? '#D4AF37' : 'rgba(212,175,55,0.25)',
                      transition: 'all 0.3s',
                    }} />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT — Moon glyph */}
          <div className="hidden lg:flex justify-center items-center relative animate-fade-up" style={{ animationDelay: '400ms' }}>
            <div className="pa-halo" style={{
              width: 400, height: 400, top: -40, left: -40,
              background: 'radial-gradient(circle, rgba(74,0,224,0.20), transparent 70%)',
            }} />
            <MoonGlyph />

            {/* Floating tags */}
            <div className="absolute top-10 -left-4 px-4 py-2 rounded-full text-[11px] uppercase tracking-widest pa-glass animate-float-soft"
              style={{ color: 'var(--pa-lavender-bright)', letterSpacing: '0.15em', animationDelay: '1s' }}>
              <Moon className="inline mr-1.5" style={{ width: 12, height: 12 }} /> {moonPhase}
            </div>
            <div className="absolute bottom-12 -right-4 px-4 py-2 rounded-full text-[11px] uppercase tracking-widest pa-glass-gold animate-float-soft"
              style={{ color: 'var(--pa-accent-bright)', letterSpacing: '0.15em', animationDelay: '2s' }}>
              <Stars className="inline mr-1.5" style={{ width: 12, height: 12 }} /> {dateFr}
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
          style={{ transform: `translateX(-50%) translateY(${Math.min(scrollY / 5, 30)}px)`, opacity: Math.max(0, 0.5 - scrollY / 200) }}>
          <p className="text-[10px] uppercase tracking-[0.4em]" style={{ color: 'var(--pa-faint)' }}>Découvrir</p>
          <div className="w-px h-12 animate-pulse" style={{ background: 'linear-gradient(180deg, rgba(167,139,250,0.4), transparent)' }} />
        </div>
      </section>

      {/* ═══════ CONSTELLATION OVERLAY ═══════ */}
      {showOverlay && (
        <div
          data-testid="constellation-overlay"
          style={{
            position: 'fixed', inset: 0, zIndex: 100,
            background: 'rgba(11,14,20,0.92)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            animation: 'fadeIn 0.4s ease-out',
          }}
        >
          <style>{`
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes ctaPulse {
              0%, 100% { box-shadow: 0 0 18px rgba(212,175,55,0.35); }
              50% { box-shadow: 0 0 36px rgba(212,175,55,0.65); }
            }
            @keyframes constellationDraw {
              from { stroke-dashoffset: 800; opacity: 0; }
              to { stroke-dashoffset: 0; opacity: 1; }
            }
          `}</style>
          <svg width="320" height="320" viewBox="0 0 320 320" style={{ opacity: 0.7 }}>
            {/* Constellation lines */}
            {[
              [60, 80, 140, 120], [140, 120, 200, 60], [200, 60, 260, 110],
              [260, 110, 240, 180], [240, 180, 160, 200], [160, 200, 80, 170],
              [80, 170, 60, 80], [140, 120, 160, 200], [200, 60, 160, 200],
            ].map(([x1, y1, x2, y2], i) => (
              <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke="rgba(212,175,55,0.6)" strokeWidth={1}
                strokeDasharray="800" strokeDashoffset="800"
                style={{ animation: `constellationDraw 1.5s ease-out ${i * 0.12}s forwards` }}
              />
            ))}
            {/* Stars */}
            {[[60,80],[140,120],[200,60],[260,110],[240,180],[160,200],[80,170]].map(([cx, cy], i) => (
              <circle key={i} cx={cx} cy={cy} r={4} fill="#D4AF37" style={{ opacity: 0, animation: `fadeIn 0.3s ease-out ${0.2 + i * 0.15}s forwards` }} />
            ))}
          </svg>
          <p style={{
            fontFamily: 'Cinzel, serif', color: '#D4AF37', fontSize: 15,
            letterSpacing: '0.15em', textTransform: 'uppercase', marginTop: 32,
            textAlign: 'center', padding: '0 24px',
          }}>
            Calcul de votre carte du ciel relationnelle en cours...
          </p>
        </div>
      )}

      {/* ═══════ POST-CTA RESULTS ═══════ */}
      {showResults && (
        <section
          data-testid="results-section"
          style={{ position: 'relative', zIndex: 10, paddingTop: 48, paddingBottom: 64 }}
        >
          <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px' }}>

            {/* Section A — Portrait du Partenaire Idéal */}
            <div
              data-testid="partner-portrait"
              style={{
                background: 'linear-gradient(160deg, rgba(74,0,224,0.12), rgba(15,14,30,0.7))',
                border: '1px solid rgba(167,139,250,0.25)',
                borderRadius: 20,
                padding: '40px 36px',
                marginBottom: 24,
                backdropFilter: 'blur(16px)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <circle cx="20" cy="20" r="19" stroke="rgba(167,139,250,0.4)" strokeWidth="1" />
                  <circle cx="20" cy="15" r="5" stroke="#C4B5FD" strokeWidth="1.5" fill="none" />
                  <path d="M10 34 Q20 26 30 34" stroke="#C4B5FD" strokeWidth="1.5" fill="none" />
                  {[[20,5],[32,12],[35,24],[26,35],[14,35],[5,24],[8,12]].map(([x, y], i) => (
                    <circle key={i} cx={x} cy={y} r={1.5} fill="#C4B5FD" opacity="0.6" />
                  ))}
                </svg>
                <div>
                  <p style={{ fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#A78BFA', marginBottom: 4 }}>
                    Portrait-Robot du Partenaire Idéal 👤
                  </p>
                  <h2 style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F8F9FA', fontSize: '1.7rem', fontWeight: 300, lineHeight: 1.1, margin: 0 }}>
                    Votre Maison VII révèle...
                  </h2>
                </div>
              </div>
              <p style={{ color: 'rgba(248,249,250,0.85)', lineHeight: 1.7, fontSize: 15 }}>
                Votre Maison VII en Signe d&apos;Eau indique que votre âme sœur possède une sensibilité
                à fleur de peau, une grande intuition et un besoin de connexion fusionnelle.
                Vous n&apos;êtes pas fait pour les amours tièdes.
              </p>
            </div>

            {/* Section B — Chronomètre des Étoiles */}
            <div
              data-testid="star-chronometer"
              style={{
                background: 'linear-gradient(160deg, rgba(212,175,55,0.10), rgba(15,14,30,0.7))',
                border: '1px solid rgba(212,175,55,0.25)',
                borderRadius: 20,
                padding: '40px 36px',
                marginBottom: 40,
                backdropFilter: 'blur(16px)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <circle cx="20" cy="20" r="16" stroke="rgba(212,175,55,0.45)" strokeWidth="1.5" />
                  <circle cx="20" cy="20" r="2" fill="#D4AF37" />
                  <line x1="20" y1="20" x2="20" y2="8" stroke="#D4AF37" strokeWidth="1.5" strokeLinecap="round" />
                  <line x1="20" y1="20" x2="28" y2="24" stroke="rgba(212,175,55,0.6)" strokeWidth="1" strokeLinecap="round" />
                  {[0,30,60,90,120,150,180,210,240,270,300,330].map((angle, i) => {
                    const rad = (angle - 90) * Math.PI / 180;
                    return <circle key={i} cx={20 + 14 * Math.cos(rad)} cy={20 + 14 * Math.sin(rad)} r={i % 3 === 0 ? 1.5 : 1} fill="rgba(212,175,55,0.5)" />;
                  })}
                </svg>
                <div>
                  <p style={{ fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase', color: '#D4AF37', marginBottom: 4 }}>
                    Chronomètre des Étoiles ⏳
                  </p>
                  <h2 style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F8F9FA', fontSize: '1.7rem', fontWeight: 300, lineHeight: 1.1, margin: 0 }}>
                    Votre fenêtre de rencontre
                  </h2>
                </div>
              </div>
              <p style={{ color: 'rgba(248,249,250,0.85)', lineHeight: 1.7, fontSize: 15 }}>
                Les mouvements de Vénus indiquent qu&apos;une zone de haute intensité relationnelle
                s&apos;active pour vous très bientôt. Une rencontre marquante est hautement favorisée
                entre <span style={{ color: '#D4AF37', fontWeight: 600 }}>{nextMonth1}</span> et{' '}
                <span style={{ color: '#D4AF37', fontWeight: 600 }}>{nextMonth2}</span> de cette année...
              </p>
            </div>

            {/* Premium CTA — La Relance Finale */}
            <div
              data-testid="premium-chat-cta"
              style={{
                background: 'linear-gradient(160deg, rgba(212,175,55,0.15), rgba(74,0,224,0.10))',
                border: '1px solid rgba(212,175,55,0.35)',
                borderRadius: 20,
                padding: '40px 36px',
                textAlign: 'center',
              }}
            >
              <h3 style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F8F9FA', fontSize: '1.8rem', fontWeight: 300, marginBottom: 12 }}>
                Envie de lui parler directement ?
              </h3>
              <p style={{ color: '#B0B5C0', marginBottom: 28, lineHeight: 1.6, maxWidth: 540, margin: '0 auto 28px' }}>
                Vos 20 crédits gratuits sont activés. Posez votre première question à notre IA Holistique
                sur votre avenir amoureux, ou débloquez votre calendrier de rencontres détaillé sur 15 pages.
              </p>
              <form onSubmit={handleChatSubmit} style={{ display: 'flex', gap: 10, maxWidth: 560, margin: '0 auto' }}>
                <input
                  type="text"
                  placeholder="Posez votre question secrète..."
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  style={{
                    flex: 1, padding: '14px 18px', borderRadius: 12,
                    background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(212,175,55,0.35)',
                    color: '#F8F9FA', fontSize: 14, outline: 'none',
                  }}
                  data-testid="chat-question-input"
                />
                <button
                  type="submit"
                  style={{
                    padding: '14px 24px', borderRadius: 12,
                    background: 'linear-gradient(135deg, #D4AF37, #AA7C11)',
                    border: 'none', color: '#0B0E14', fontWeight: 700,
                    fontSize: 13, cursor: 'pointer', whiteSpace: 'nowrap',
                  }}
                  data-testid="chat-submit-btn"
                >
                  💬 Poser ma question secrète
                </button>
              </form>
            </div>
          </div>
        </section>
      )}

    </div>
  );
};

export default Index;
