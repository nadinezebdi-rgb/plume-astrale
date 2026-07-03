import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Sparkles, Moon, Heart, Compass, MessageCircle, BookHeart,
  Flame, Stars, ArrowRight, Quote, Sun, Cloud, Wind
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import HeroOracle from '../components/HeroOracle';
import EnergyToday from '../components/EnergyToday';
import SocialProof from '../components/SocialProof';
import NatalCompletionPrompt from '../components/NatalCompletionPrompt';

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
   PILLAR CARD — emotional pillars
═══════════════════════════════════════════════════════════ */
const PillarCard = ({ icon: Icon, kicker, title, desc, to, accent = 'lavender', delay = 0 }) => {
  const colors = accent === 'gold' ? {
    glow: 'rgba(212,180,106,0.18)',
    border: 'rgba(212,180,106,0.25)',
    icon: '#E6C480',
    accent: '#C5A059',
  } : {
    glow: 'rgba(167,139,250,0.20)',
    border: 'rgba(167,139,250,0.25)',
    icon: '#C4B5FD',
    accent: '#A78BFA',
  };

  return (
    <Link
      to={to}
      className="group relative block animate-fade-up"
      style={{ animationDelay: `${delay}ms`, textDecoration: 'none' }}
    >
      <div className="relative p-7 rounded-2xl h-full transition-all duration-500 group-hover:-translate-y-1"
        style={{
          background: 'linear-gradient(160deg, rgba(167,139,250,0.06) 0%, rgba(22,28,68,0.4) 100%)',
          border: `1px solid ${colors.border}`,
          backdropFilter: 'blur(16px)',
          boxShadow: `0 8px 32px rgba(6,8,26,0.5)`,
        }}>
        {/* Glow */}
        <div className="absolute -top-12 -right-12 w-40 h-40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700"
          style={{ background: `radial-gradient(circle, ${colors.glow}, transparent 70%)`, filter: 'blur(20px)' }} />

        <div className="relative">
          <div className="mb-5 inline-flex items-center justify-center rounded-xl p-3"
            style={{ background: `linear-gradient(135deg, ${colors.glow}, transparent)`, border: `1px solid ${colors.border}` }}>
            <Icon style={{ width: 22, height: 22, color: colors.icon }} strokeWidth={1.4} />
          </div>
          <p className="text-[10px] uppercase tracking-[0.2em] mb-2" style={{ color: colors.accent }}>
            {kicker}
          </p>
          <h3 className="text-2xl mb-3 font-display" style={{ color: 'var(--pa-heading)', fontWeight: 400, lineHeight: 1.2 }}>
            {title}
          </h3>
          <p className="text-sm leading-relaxed mb-5" style={{ color: 'var(--pa-body)' }}>
            {desc}
          </p>
          <div className="flex items-center gap-2 text-xs uppercase tracking-widest transition-transform group-hover:translate-x-1"
            style={{ color: colors.accent, letterSpacing: '0.1em' }}>
            Explorer <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
          </div>
        </div>
      </div>
    </Link>
  );
};

/* ═══════════════════════════════════════════════════════════
   MOOD ORBS — interactive quick-mood selector
═══════════════════════════════════════════════════════════ */
const MoodOrbs = ({ onSelect }) => {
  const moods = [
    { icon: Sun, label: 'Radieux', color: '#F4D98C', q: 'Quelle énergie soutenir aujourd\'hui ?' },
    { icon: Cloud, label: 'Pensif', color: '#9089B5', q: 'Aide-moi à clarifier ce qui me traverse' },
    { icon: Heart, label: 'Amour', color: '#F47F92', q: 'Que disent les astres sur ma vie sentimentale ?' },
    { icon: Wind, label: 'Inquiet', color: '#A78BFA', q: 'J\'ai besoin de calmer mon mental, conseille-moi' },
    { icon: Flame, label: 'Determine', color: '#FF9F66', q: 'Comment canaliser mon élan aujourd\'hui ?' },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-3 sm:gap-4 mt-8">
      {moods.map((m, i) => (
        <button
          key={m.label}
          onClick={() => onSelect(m.q)}
          className="group flex flex-col items-center gap-2 transition-transform hover:scale-110"
          style={{ animationDelay: `${i * 60}ms` }}
        >
          <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center transition-all"
            style={{
              background: `radial-gradient(circle at 30% 30%, ${m.color}38 0%, ${m.color}12 60%, transparent 100%)`,
              border: `1px solid ${m.color}40`,
              boxShadow: `0 0 24px ${m.color}25`,
            }}>
            <m.icon style={{ width: 22, height: 22, color: m.color }} strokeWidth={1.4} />
          </div>
          <span className="text-[10px] uppercase tracking-widest opacity-70 group-hover:opacity-100" style={{ letterSpacing: '0.12em' }}>
            {m.label}
          </span>
        </button>
      ))}
    </div>
  );
};

/* ═══════════════════════════════════════════════════════════
   PAGE
═══════════════════════════════════════════════════════════ */
const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleMoodSelect = (q) => {
    try { localStorage.setItem('pa_chat_seed', q); } catch (e) { /* ignore */ }
    navigate('/consultation');
  };

  // Today's french date
  const today = new Date();
  const dateFr = today.toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long',
  });
  const moonPhases = ['Nouvelle Lune', 'Premier Croissant', 'Premier Quartier', 'Gibbeuse Croissante', 'Pleine Lune', 'Gibbeuse Decroissante', 'Dernier Quartier', 'Dernier Croissant'];
  const moonIdx = Math.floor(((today - new Date(today.getFullYear(), 0, 1)) / (1000 * 60 * 60 * 24 * 3.6875)) % 8);
  const moonPhase = moonPhases[moonIdx];

  return (
    <div className="relative" style={{ overflow: 'hidden' }}>
      <SEO path="/" />
      <CosmicCanvas />

      {/* ═══════ HERO ═══════ */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-32 sm:pt-32 pb-16 z-10">
        {/* Editorial kicker bar */}
        <div className="absolute top-20 sm:top-24 left-1/2 -translate-x-1/2 flex items-center gap-3 z-10 animate-fade-up"
          style={{ animationDelay: '0ms' }}>
          <span className="h-px w-12" style={{ background: 'linear-gradient(90deg, transparent, rgba(167,139,250,0.5))' }} />
          <p className="text-[10px] uppercase tracking-[0.4em]" style={{ color: 'var(--pa-lavender-bright)' }}>
            Sanctuaire numerique
          </p>
          <span className="h-px w-12" style={{ background: 'linear-gradient(90deg, rgba(167,139,250,0.5), transparent)' }} />
        </div>

        <div className="relative z-10 max-w-6xl w-full grid lg:grid-cols-2 gap-12 items-center">
          {/* LEFT — text */}
          <div className="text-center lg:text-left">
            <div className="animate-fade-up" style={{ animationDelay: '100ms' }}>
              <h1 className="font-display mb-6"
                style={{
                  fontSize: 'clamp(36px, 6vw, 68px)',
                  lineHeight: 1.0,
                  color: 'var(--pa-heading)',
                  fontWeight: 300,
                  letterSpacing: '-0.02em',
                }}>
                Découvre les <br />
                <span className="italic font-display pa-shimmer-gold" style={{ fontStyle: 'italic' }}>
                  cycles astrologiques
                </span><br />
                qui influencent ta vie.
              </h1>
            </div>

            <div className="animate-fade-up" style={{ animationDelay: '300ms' }}>
              <p className="text-base sm:text-lg max-w-xl mx-auto lg:mx-0 mb-2 leading-relaxed"
                style={{ color: 'var(--pa-body)' }}>
                Analyses personnalisées basées sur <span style={{ color: 'var(--pa-lavender-bright)' }}>ton thème astral</span>,
                tes relations et les mouvements planétaires actuels.
              </p>
              <p className="text-sm max-w-lg mx-auto lg:mx-0 mb-6" style={{ color: 'var(--pa-muted)' }}>
                Une plateforme premium de guidance émotionnelle, pour traverser tes jours avec sens.
              </p>

              {!isAuthenticated && (
                <Link to="/inscription"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-4 group hover:scale-[1.02] transition-transform"
                  style={{
                    background: 'linear-gradient(90deg, rgba(212,180,106,0.20), rgba(244,217,140,0.28), rgba(212,180,106,0.20))',
                    border: '1px solid rgba(244,217,140,0.55)',
                    boxShadow: '0 0 30px rgba(212,180,106,0.20)',
                  }}
                  data-testid="launch-offer-badge">
                  <Sparkles style={{ width: 12, height: 12, color: '#F4D98C' }} />
                  <span style={{ fontSize: 11, letterSpacing: '0.16em', color: '#F4D98C', textTransform: 'uppercase', fontFamily: 'Cinzel, serif' }}>
                    Offre de lancement — 20 crédits offerts pour révéler votre avenir amoureux
                  </span>
                  <span style={{ fontSize: 11, color: '#F4D98C', opacity: 0.85 }} className="group-hover:translate-x-0.5 transition-transform">→</span>
                </Link>
              )}
            </div>

            <div className="animate-fade-up flex flex-col sm:flex-row gap-3 justify-center lg:justify-start"
              style={{ animationDelay: '500ms' }}>
              <button onClick={() => navigate(isAuthenticated ? '/energie' : '/inscription')} className="pa-btn-primary" data-testid="hero-cta-primary">
                <Sparkles style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                {isAuthenticated ? 'Voir mon énergie actuelle' : 'Découvrir mon thème'}
              </button>
              <button onClick={() => navigate(isAuthenticated ? '/consultation' : '/connexion')} className="pa-btn-ghost" data-testid="hero-cta-secondary">
                <MessageCircle style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                {isAuthenticated ? 'Démarrer ma consultation' : 'Voir mon énergie actuelle'}
              </button>
            </div>

            {/* Mood orbs */}
            <div className="animate-fade-up" style={{ animationDelay: '700ms' }}>
              <p className="text-[11px] uppercase tracking-[0.25em] mt-12 mb-2 opacity-60" style={{ color: 'var(--pa-faint)' }}>
                Comment te sens-tu ?
              </p>
              <MoodOrbs onSelect={handleMoodSelect} />
            </div>
          </div>

          {/* RIGHT — Moon glyph */}
          <div className="hidden lg:flex justify-center items-center relative animate-fade-up" style={{ animationDelay: '400ms' }}>
            <div className="pa-halo" style={{
              width: 400, height: 400, top: -40, left: -40,
              background: 'radial-gradient(circle, rgba(167,139,250,0.25), transparent 70%)',
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
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 opacity-50"
          style={{ transform: `translateX(-50%) translateY(${Math.min(scrollY / 5, 30)}px)`, opacity: Math.max(0, 0.5 - scrollY / 200) }}>
          <p className="text-[10px] uppercase tracking-[0.4em]" style={{ color: 'var(--pa-faint)' }}>Decouvrir</p>
          <div className="w-px h-12 animate-pulse" style={{ background: 'linear-gradient(180deg, rgba(167,139,250,0.4), transparent)' }} />
        </div>
      </section>

      {/* ═══════ HERO ORACLE — Tunnel d'acquisition gratuit (NEW Phase 1) ═══════ */}
      {!isAuthenticated && (
        <section className="relative py-16 px-4 z-10" data-testid="home-hero-oracle">
          <HeroOracle />
        </section>
      )}

      {/* ═══════ SECTION — ASTROLOGIE RELATIONNELLE (produit haut-ticket 49€) ═══════ */}
      <section className="relative py-16 px-4 z-10" data-testid="home-relationship-section">
        <div className="max-w-4xl mx-auto">
          <a href="/synastrie" className="block rounded-3xl overflow-hidden transition-transform hover:scale-[1.01]" style={{
            background: 'linear-gradient(135deg, rgba(212,180,106,0.14) 0%, rgba(167,139,250,0.10) 100%)',
            border: '1px solid rgba(212,180,106,0.35)',
            boxShadow: '0 12px 48px rgba(0,0,0,0.4), 0 0 60px rgba(212,180,106,0.08)',
          }} data-testid="home-relationship-card">
            <div className="grid md:grid-cols-2 gap-0">
              <div className="p-8 sm:p-10 flex flex-col justify-center">
                <p className="text-[10px] uppercase tracking-[0.32em] mb-3" style={{ color: '#D4B46A', fontFamily: 'Cinzel, serif' }}>
                  Le cœur au centre
                </p>
                <h2 className="mb-4" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F0E6D3', fontWeight: 300, fontSize: '2.2rem', lineHeight: 1.1 }}>
                  <em style={{ fontStyle: 'italic', color: '#D4B46A' }}>Astrologie<br />relationnelle</em>
                </h2>
                <p className="text-sm mb-3" style={{ color: 'rgba(240,230,211,0.85)', lineHeight: 1.65 }}>
                  Un rapport de 25 pages composé sur vos deux thèmes natals — pour comprendre ce qui se joue, ce qui vous nourrit et ce qui demande attention dans votre lien.
                </p>
                <p className="text-xs italic mb-6" style={{ color: 'rgba(212,180,106,0.85)', lineHeight: 1.65 }}>
                  Plus fine et plus efficace qu&apos;une compatibilité amoureuse schématique — la synastrie révèle les affinités, les points de discordance, et ce que l&apos;autre active chez vous.
                </p>
                <div className="flex items-center gap-4">
                  <span className="text-2xl" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F4D98C' }}>49€</span>
                  <span className="text-[11px] uppercase tracking-widest px-4 py-2 rounded-full" style={{
                    background: 'linear-gradient(135deg, #D4B46A, #C5A059)', color: '#0C0918', letterSpacing: '0.12em', fontWeight: 600,
                  }}>
                    Découvrir →
                  </span>
                </div>
                <p className="text-[10px] mt-3" style={{ color: 'rgba(184,176,200,0.6)' }}>
                  ✦ Extrait gratuit 3 pages disponible sur la page
                </p>
              </div>
              <div className="hidden md:block relative" style={{ minHeight: 300, background: 'linear-gradient(180deg, rgba(212,180,106,0.05), rgba(167,139,250,0.08))' }}>
                <img src="/api/assets/synastrie_pdf/page-01.png" alt="Astrologie relationnelle" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.75 }} />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(90deg, rgba(12,9,24,0.7) 0%, transparent 50%)' }} />
              </div>
            </div>
          </a>
        </div>
      </section>

      {/* ═══════ SECTION — ENERGIE ACTUELLE (cœur du produit) ═══════ */}
      <section className="relative py-20 px-6 z-10" data-testid="home-energy-section">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12 animate-fade-up">
            <p className="text-[10px] uppercase tracking-[0.4em] mb-4" style={{ color: 'var(--pa-lavender-bright)' }}>
              Le cœur du produit
            </p>
            <h2 className="font-display mb-3" style={{
              fontSize: 'clamp(28px, 4vw, 44px)', color: 'var(--pa-heading)', fontWeight: 300, lineHeight: 1.15,
            }}>
              Ton <span className="italic pa-shimmer-gold">énergie actuelle</span>
            </h2>
            <p className="text-base max-w-xl mx-auto" style={{ color: 'var(--pa-muted)' }}>
              Chaque matin, une lecture personnalisée des cycles planétaires qui te traversent.
            </p>
          </div>

          {/* Soft nudge: complete birth_time if missing */}
          <div className="mb-8">
            <NatalCompletionPrompt />
          </div>

          <EnergyToday />
        </div>
      </section>

      {/* ═══════ SECTION — L'EXPERIENCE ═══════ */}
      <section className="relative py-24 px-6 z-10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 animate-fade-up">
            <p className="text-[10px] uppercase tracking-[0.4em] mb-4" style={{ color: 'var(--pa-lavender-bright)' }}>
              L&#39;experience Plume
            </p>
            <h2 className="font-display mb-4" style={{
              fontSize: 'clamp(32px, 5vw, 54px)',
              color: 'var(--pa-heading)',
              fontWeight: 300,
              lineHeight: 1.05,
              letterSpacing: '-0.01em',
            }}>
              Trois facettes pour <br />
              <span className="italic pa-shimmer-lavender">te rencontrer</span>.
            </h2>
            <p className="text-sm max-w-xl mx-auto" style={{ color: 'var(--pa-muted)' }}>
              Un rituel apaisant. Un oracle qui te comprend. Un miroir cosmique.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <PillarCard
              icon={MessageCircle}
              kicker="Consultation"
              title="Consultation astrale personnalisée"
              desc="Pose tes questions a un astrologue IA. Reponses personnalisees a partir de ton theme natal, en francais, 24/7."
              to="/consultation"
              accent="lavender"
              delay={100}
            />
            <PillarCard
              icon={BookHeart}
              kicker="Rituel quotidien"
              title="Ton journal cosmique"
              desc="Pose ton humeur, ton intention, ton message du jour. Recois en retour un eclairage astrologique apaisant."
              to="/mon-rituel"
              accent="gold"
              delay={200}
            />
            <PillarCard
              icon={Compass}
              kicker="Miroir cosmique"
              title="Ton theme natal"
              desc="Decouvre la cartographie celeste de ta naissance — planetes, maisons, aspects. Le reflet de qui tu es."
              to="/formulaire"
              accent="lavender"
              delay={300}
            />
          </div>
        </div>
      </section>

      {/* ═══════ SECTION — POSITIONNEMENT EDITORIAL ═══════ */}
      <section className="relative py-24 px-6 z-10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="pa-glass rounded-3xl p-10 sm:p-16 relative overflow-hidden animate-fade-up">
            {/* Decorative halo */}
            <div className="absolute -top-20 -left-20 w-60 h-60 rounded-full"
              style={{ background: 'radial-gradient(circle, rgba(167,139,250,0.18), transparent 70%)', filter: 'blur(40px)' }} />
            <div className="absolute -bottom-20 -right-20 w-60 h-60 rounded-full"
              style={{ background: 'radial-gradient(circle, rgba(212,180,106,0.15), transparent 70%)', filter: 'blur(40px)' }} />

            <Quote style={{ width: 36, height: 36, color: 'var(--pa-lavender)', opacity: 0.5, margin: '0 auto 24px' }} strokeWidth={1.2} />

            <p className="font-display italic mb-6 relative z-10"
              style={{
                fontSize: 'clamp(22px, 3.5vw, 36px)',
                lineHeight: 1.35,
                color: 'var(--pa-heading)',
                fontWeight: 300,
              }}>
              &laquo; Les astres ne predisent pas ton avenir.<br />
              <span className="pa-shimmer-gold">Ils t&#39;invitent a le co-creer.</span> &raquo;
            </p>

            <div className="flex items-center justify-center gap-3">
              <span className="h-px w-8" style={{ background: 'rgba(212,180,106,0.4)' }} />
              <p className="text-[11px] uppercase tracking-[0.3em]" style={{ color: 'var(--pa-accent)' }}>
                Plume Astrale
              </p>
              <span className="h-px w-8" style={{ background: 'rgba(212,180,106,0.4)' }} />
            </div>
          </div>
        </div>
      </section>

      {/* ═══════ SECTION — RITUEL DU JOUR ═══════ */}
      <section className="relative py-24 px-6 z-10">
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-up">
              <p className="text-[10px] uppercase tracking-[0.4em] mb-4" style={{ color: 'var(--pa-accent-bright)' }}>
                Le rituel d&#39;aujourd&#39;hui
              </p>
              <h2 className="font-display mb-6" style={{
                fontSize: 'clamp(28px, 4.5vw, 48px)',
                color: 'var(--pa-heading)',
                fontWeight: 300,
                lineHeight: 1.05,
              }}>
                Chaque jour, une <span className="italic pa-shimmer-gold">presence</span> a tes cotes.
              </h2>
              <p className="text-base leading-relaxed mb-4" style={{ color: 'var(--pa-body)' }}>
                Un check-in matinal pour poser ton humeur. Un message du jour calibre sur tes transits planetaires.
                Une question d&#39;intention. Un eclairage le soir.
              </p>
              <p className="text-sm leading-relaxed mb-8" style={{ color: 'var(--pa-muted)' }}>
                Plume Astrale t&#39;accompagne comme une amie attentive — sans jugement, avec poesie et precision astrologique.
              </p>

              <div className="space-y-3 mb-8">
                {[
                  { icon: Sun, txt: 'Check-in matinal — pose ton humeur en 1 tap' },
                  { icon: Stars, txt: 'Ton message du jour personnalisé (transits planétaires)' },
                  { icon: Moon, txt: 'Reflexion du soir — questions d\'introspection' },
                  { icon: Heart, txt: 'Score d\'energie, confiance, discipline' },
                ].map((it, i) => (
                  <div key={i} className="flex items-center gap-3 animate-fade-up" style={{ animationDelay: `${i * 80}ms` }}>
                    <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ background: 'rgba(167,139,250,0.10)', border: '1px solid rgba(167,139,250,0.20)' }}>
                      <it.icon style={{ width: 16, height: 16, color: 'var(--pa-lavender-bright)' }} strokeWidth={1.5} />
                    </div>
                    <p className="text-sm" style={{ color: 'var(--pa-body)' }}>{it.txt}</p>
                  </div>
                ))}
              </div>

              <Link to="/mon-rituel" className="pa-btn-ghost">
                <BookHeart style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                Decouvrir mon rituel
              </Link>
            </div>

            {/* Visual scores card */}
            <div className="relative animate-fade-up" style={{ animationDelay: '200ms' }}>
              <div className="pa-glass rounded-3xl p-8 relative overflow-hidden">
                <p className="text-[10px] uppercase tracking-[0.3em] mb-1 text-center" style={{ color: 'var(--pa-faint)' }}>
                  Aujourd&#39;hui
                </p>
                <p className="font-display text-center mb-6" style={{ fontSize: 22, color: 'var(--pa-heading)', fontStyle: 'italic', fontWeight: 300 }}>
                  &laquo; Une journee fertile &raquo;
                </p>

                {[
                  { label: 'Energie', value: 78, color: '#F47F92' },
                  { label: 'Confiance', value: 64, color: '#A78BFA' },
                  { label: 'Discipline', value: 82, color: '#E6C480' },
                  { label: 'Intuition', value: 71, color: '#C4B5FD' },
                ].map((s, i) => (
                  <div key={s.label} className="mb-4">
                    <div className="flex justify-between mb-1.5">
                      <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pa-body)', letterSpacing: '0.1em' }}>
                        {s.label}
                      </span>
                      <span className="text-xs" style={{ color: s.color, fontWeight: 600 }}>
                        {s.value}
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.04)' }}>
                      <div className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${s.value}%`,
                          background: `linear-gradient(90deg, ${s.color}aa, ${s.color})`,
                          boxShadow: `0 0 12px ${s.color}66`,
                          animationDelay: `${i * 100}ms`,
                        }} />
                    </div>
                  </div>
                ))}

                <div className="mt-6 pt-6 border-t" style={{ borderColor: 'var(--pa-divider-soft)' }}>
                  <p className="text-[11px] uppercase tracking-widest mb-2 opacity-70" style={{ color: 'var(--pa-faint)' }}>
                    Conseil cosmique
                  </p>
                  <p className="text-sm italic leading-relaxed" style={{ color: 'var(--pa-body)' }}>
                    Avec la Lune en Cancer, accueille tes emotions sans les juger.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════ SECTION — CTA FINAL ═══════ */}
      <section className="relative py-24 px-6 z-10">
        <div className="max-w-3xl mx-auto text-center">
          <div className="animate-fade-up">
            <Sparkles style={{ width: 32, height: 32, color: 'var(--pa-accent-bright)', margin: '0 auto 16px' }} strokeWidth={1.2} />
            <h2 className="font-display mb-4" style={{
              fontSize: 'clamp(28px, 4.5vw, 44px)',
              color: 'var(--pa-heading)',
              fontWeight: 300,
              lineHeight: 1.1,
            }}>
              Prets a rencontrer <br />
              <span className="italic pa-shimmer-lavender">votre boussole interieure</span> ?
            </h2>
            <p className="text-base mb-10 max-w-xl mx-auto" style={{ color: 'var(--pa-body)' }}>
              20 credits offerts a l&#39;inscription. Une consultation personnalisée et chaleureuse, alimentée par ton thème natal réel.
            </p>
            <button onClick={() => navigate(isAuthenticated ? '/consultation' : '/inscription')} className="pa-btn-primary" style={{ padding: '16px 36px' }}>
              <Sparkles style={{ width: 16, height: 16 }} strokeWidth={1.5} />
              {isAuthenticated ? 'Continuer ma traversee' : 'Commencer gratuitement'}
            </button>
            <p className="text-[11px] uppercase tracking-widest mt-6" style={{ color: 'var(--pa-faint)' }}>
              +2 000 ames deja accompagnees
            </p>
          </div>
        </div>
      </section>

      {/* ═══ TRUST BADGE — AstrologyAPI ═══ */}
      <section className="py-12 px-4" style={{ borderTop: '1px solid rgba(212,180,106,0.08)' }} data-testid="trust-astrology-api">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[10px] uppercase tracking-[0.25em] mb-4" style={{ color: 'var(--pa-faint)', letterSpacing: '0.25em' }}>
            Technologie de confiance
          </p>
          <p className="text-base mb-3" style={{ color: 'var(--pa-body)', fontFamily: 'Cormorant Garamond, serif', fontSize: 22, lineHeight: 1.4 }}>
            Calculs astrologiques propulsés par <span style={{ color: '#D4B46A', fontWeight: 500 }}>AstrologyAPI</span>
          </p>
          <p className="text-sm max-w-xl mx-auto" style={{ color: 'var(--pa-muted)', lineHeight: 1.6 }}>
            La même plateforme utilisée par des marques internationales et des applications d&apos;astrologie spécialisées —
            calculs précis d&apos;éphémérides, fuseaux horaires, maisons astrologiques et aspects planétaires.
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-[10px] uppercase tracking-widest" style={{ color: 'var(--pa-faint)' }}>
            <span>Données réelles</span>
            <span>·</span>
            <span>Calculs précis</span>
            <span>·</span>
            <span>Paiement sécurisé Stripe</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
