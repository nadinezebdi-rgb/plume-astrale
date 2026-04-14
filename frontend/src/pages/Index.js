import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Star, Sparkles, Eye, Moon, Heart, Hash, TrendingUp, Flame } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import TirageDuJour from '../components/TirageDuJour';
import NatalWheel from '../components/NatalWheel';
import ShareableCard from '../components/ShareableCard';

const PLUME_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/v8g1i6qn_une%20plume.png";
const OEIL_IMG = "https://customer-assets.emergentagent.com/job_6ebe2661-1b82-4742-afc5-632bf29dfcc5/artifacts/lkljttvo_img1.png";

/* ─── Enhanced cosmic animated background with shooting stars ─── */
const CosmicBg = () => {
  const canvasRef = useRef(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    let stars = [];
    let shootingStars = [];
    let nebulae = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = document.documentElement.scrollHeight || window.innerHeight * 4;
    };

    const initStars = () => {
      stars = [];
      const colors = [
        [248, 250, 252],
        [232, 121, 249],
        [167, 139, 250],
        [244, 197, 66],
        [96, 165, 250],
      ];
      for (let i = 0; i < 400; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 2.5 + 0.3,
          speed: Math.random() * 0.5 + 0.05,
          opacity: Math.random() * 0.8 + 0.2,
          phase: Math.random() * Math.PI * 2,
          color: colors[Math.floor(Math.random() * colors.length)],
          parallax: Math.random() * 0.3 + 0.1,
          twinkleSpeed: Math.random() * 2 + 1,
        });
      }
    };

    const initNebulae = () => {
      nebulae = [];
      for (let i = 0; i < 5; i++) {
        nebulae.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 200 + 100,
          color: [
            [139, 92, 246, 0.03],
            [232, 121, 249, 0.02],
            [244, 197, 66, 0.015],
          ][Math.floor(Math.random() * 3)],
          drift: Math.random() * 0.2 - 0.1,
          phase: Math.random() * Math.PI * 2,
        });
      }
    };

    const spawnShootingStar = () => {
      if (shootingStars.length > 2) return;
      if (Math.random() > 0.003) return;
      const startX = Math.random() * canvas.width;
      const startY = Math.random() * canvas.height * 0.5;
      shootingStars.push({
        x: startX,
        y: startY,
        vx: (Math.random() - 0.3) * 8,
        vy: Math.random() * 4 + 2,
        life: 1,
        decay: 0.015 + Math.random() * 0.01,
        length: 40 + Math.random() * 60,
      });
    };

    const draw = (time) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      // Nebulae
      nebulae.forEach(n => {
        const pulse = 0.8 + 0.2 * Math.sin(time * 0.0003 + n.phase);
        const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * pulse);
        grad.addColorStop(0, `rgba(${n.color[0]},${n.color[1]},${n.color[2]},${n.color[3] * pulse})`);
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.fillRect(n.x - n.r, n.y - n.r, n.r * 2, n.r * 2);
      });

      // Stars with parallax and bright twinkle
      stars.forEach(s => {
        const twinkle = 0.3 + 0.7 * Math.pow(Math.sin(time * 0.001 * s.twinkleSpeed + s.phase), 2);
        const o = s.opacity * twinkle;
        const px = s.x + mx * s.parallax * 0.01;
        const py = s.y + my * s.parallax * 0.01;

        ctx.beginPath();
        ctx.arc(px, py, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${s.color[0]},${s.color[1]},${s.color[2]},${o})`;
        ctx.fill();

        // Bright glow for all visible stars
        if (s.r > 0.8) {
          ctx.beginPath();
          ctx.arc(px, py, s.r * 5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${s.color[0]},${s.color[1]},${s.color[2]},${o * 0.12})`;
          ctx.fill();
        }
        // Extra glow for large stars
        if (s.r > 1.5) {
          ctx.beginPath();
          ctx.arc(px, py, s.r * 8, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${s.color[0]},${s.color[1]},${s.color[2]},${o * 0.05})`;
          ctx.fill();
        }
      });

      // Shooting stars
      spawnShootingStar();
      shootingStars = shootingStars.filter(ss => {
        ss.x += ss.vx;
        ss.y += ss.vy;
        ss.life -= ss.decay;
        if (ss.life <= 0) return false;

        const tailX = ss.x - ss.vx * (ss.length / 8);
        const tailY = ss.y - ss.vy * (ss.length / 8);

        const grad = ctx.createLinearGradient(tailX, tailY, ss.x, ss.y);
        grad.addColorStop(0, `rgba(248,250,252,0)`);
        grad.addColorStop(0.7, `rgba(248,250,252,${ss.life * 0.4})`);
        grad.addColorStop(1, `rgba(244,197,66,${ss.life * 0.8})`);

        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(ss.x, ss.y);
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Head glow
        ctx.beginPath();
        ctx.arc(ss.x, ss.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(248,250,252,${ss.life * 0.9})`;
        ctx.fill();
        return true;
      });

      animId = requestAnimationFrame(draw);
    };

    const handleMouse = (e) => {
      mouseRef.current = { x: e.clientX - window.innerWidth / 2, y: e.clientY - window.innerHeight / 2 };
    };

    resize();
    initStars();
    initNebulae();
    animId = requestAnimationFrame(draw);
    window.addEventListener('resize', () => { resize(); initStars(); initNebulae(); });
    window.addEventListener('mousemove', handleMouse);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', handleMouse);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-0" style={{ opacity: 0.7 }} />;
};

/* ─── Cosmic alignment bars with stagger animation ─── */
const CosmicScore = () => {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.3 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  const scores = [
    { label: 'Amour', pct: 70, color: '#E879F9', icon: Heart },
    { label: 'Carriere', pct: 55, color: '#F4C542', icon: TrendingUp },
    { label: 'Energie', pct: 85, color: '#A78BFA', icon: Sparkles },
    { label: 'Intuition', pct: 90, color: '#60A5FA', icon: Eye },
  ];

  return (
    <div ref={ref} className="space-y-5" data-testid="cosmic-score">
      <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ fontFamily: 'Cinzel, serif', color: '#F4C542', letterSpacing: '0.2em' }}>
        Alignement Cosmique
      </p>
      {scores.map((s, i) => {
        const Icon = s.icon;
        return (
          <div key={s.label}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="flex items-center gap-2 text-sm" style={{ fontFamily: 'Inter, sans-serif', color: '#F8FAFC', fontWeight: 400 }}>
                <Icon className="w-3.5 h-3.5" style={{ color: s.color }} strokeWidth={1.5} />
                {s.label}
              </span>
              <span className="text-sm font-medium tabular-nums" style={{ fontFamily: 'Inter, sans-serif', color: s.color, fontWeight: 600 }}>
                {visible ? s.pct : 0}%
              </span>
            </div>
            <div className="h-2.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.04)' }}>
              <div
                className="h-full rounded-full"
                style={{
                  width: visible ? `${s.pct}%` : '0%',
                  background: `linear-gradient(90deg, ${s.color}40, ${s.color})`,
                  boxShadow: visible ? `0 0 16px ${s.color}50, inset 0 1px 0 rgba(255,255,255,0.15)` : 'none',
                  transition: `width 1.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 250}ms`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

/* ─── Cosmic glassmorphism card ─── */
const CosmicCard = ({ children, className = '', glow = 'purple', testId, onClick }) => {
  const glowMap = {
    gold: 'rgba(244,197,66,0.12)',
    pink: 'rgba(232,121,249,0.12)',
    purple: 'rgba(139,92,246,0.12)',
  };
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl p-6 transition-all duration-300 ${onClick ? 'cursor-pointer hover:-translate-y-1' : ''} ${className}`}
      style={{
        background: 'rgba(255,255,255,0.03)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.07)',
        boxShadow: `0 0 40px ${glowMap[glow] || glowMap.purple}`,
      }}
      data-testid={testId}
    >
      {children}
    </div>
  );
};

/* ─── CTA Button cosmic gradient ─── */
const CosmicBtn = ({ children, onClick, testId, secondary }) => (
  <button
    onClick={onClick}
    className="inline-flex items-center gap-2 px-8 py-4 rounded-full text-sm font-semibold transition-all duration-300 hover:scale-105"
    style={secondary ? {
      background: 'transparent',
      border: '1px solid rgba(232,121,249,0.4)',
      color: '#E879F9',
      fontFamily: 'Inter, sans-serif',
    } : {
      background: 'linear-gradient(135deg, #F4C542, #E879F9)',
      color: '#0F172A',
      fontFamily: 'Inter, sans-serif',
      fontWeight: 600,
      boxShadow: '0 0 20px rgba(244,197,66,0.3)',
    }}
    data-testid={testId}
  >
    {children}
  </button>
);

const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated, creditBalance } = useAuth();

  return (
    <div className="relative z-10" style={{ background: 'linear-gradient(180deg, #2B0A3D 0%, #1E1B4B 30%, #0F172A 70%, #2B0A3D 100%)' }} data-testid="homepage">
      <SEO path="/" />
      <CosmicBg />

      {/* Nebula orbs */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[10%] left-[15%] w-[500px] h-[500px] rounded-full opacity-30"
          style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)', filter: 'blur(80px)', animation: 'orbFloat 25s ease-in-out infinite' }} />
        <div className="absolute top-[50%] right-[10%] w-[400px] h-[400px] rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, rgba(232,121,249,0.2) 0%, transparent 70%)', filter: 'blur(80px)', animation: 'orbFloat 30s ease-in-out infinite reverse' }} />
        <div className="absolute bottom-[20%] left-[40%] w-[350px] h-[350px] rounded-full opacity-25"
          style={{ background: 'radial-gradient(circle, rgba(244,197,66,0.12) 0%, transparent 70%)', filter: 'blur(80px)', animation: 'orbFloat 20s ease-in-out infinite' }} />
      </div>

      {/* ─── HERO ─── */}
     {/* ─── HERO ORACLE (NEW CORE BUSINESS) ─── */}
<section className="relative z-10 min-h-screen flex items-center pt-20 pb-16 px-6 md:px-8" data-testid="hero-section">
  <div className="max-w-5xl mx-auto flex flex-col items-center text-center w-full">

    <p className="text-xs uppercase tracking-[0.3em] mb-4"
      style={{ fontFamily: 'Inter, sans-serif', color: '#E879F9', letterSpacing: '0.3em', fontWeight: 500 }}>
      Oracle Personnel
    </p>

    <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl mb-5"
      style={{ fontFamily: 'Cinzel, serif', fontWeight: 600, color: '#F8FAFC', lineHeight: 1.05 }}>
      Pose ta question<br />à ton Oracle
    </h1>

    <p className="text-lg max-w-xl mb-8"
      style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.6)' }}>
      Une réponse claire pour ce qui compte vraiment : amour, décisions, avenir.
    </p>

    {/* CTA PRINCIPAL */}
    <div className="flex flex-col sm:flex-row gap-4">
      <CosmicBtn
        onClick={() => navigate('/oracle')}
        testId="cta-oracle-main"
      >
        🔮 Consulter mon Oracle
      </CosmicBtn>

      <CosmicBtn
        onClick={() => navigate('/tarot-oui-non')}
        secondary
      >
        Tester gratuitement
      </CosmicBtn>
    </div>

    {/* 🔥 PREUVE SOCIALE */}
    <p className="text-xs mt-6 opacity-60"
      style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)' }}>
      +2 000 consultations déjà réalisées
    </p>

  </div>
</section>
      {/* ─── INTERACTIVE NATAL WHEEL ─── */}
      <section className="relative z-10 py-16 px-6 md:px-8" data-testid="section-natal-wheel">
        <div className="max-w-4xl mx-auto">
          <CosmicCard glow="purple" testId="natal-wheel-card">
            <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12">
              <div className="w-64 md:w-80 flex-shrink-0">
                <NatalWheel />
              </div>
              <div className="flex-1 text-center md:text-left">
                <p className="text-xs uppercase tracking-[0.2em] mb-3"
                  style={{ fontFamily: 'Inter, sans-serif', color: '#E879F9', letterSpacing: '0.25em', fontWeight: 500 }}>
                  Roue Natale Interactive
                </p>
                <h2 className="text-2xl md:text-3xl mb-3"
                  style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
                  Votre carte du ciel
                </h2>
                <p className="text-sm mb-5"
                  style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)', lineHeight: '1.8' }}>
                  Explorez les 12 signes et les planetes majeures. Survolez chaque symbole
                  pour decouvrir ses energies. Creez votre profil pour une roue personnalisee.
                </p>
                <CosmicBtn onClick={() => navigate(isAuthenticated ? '/formulaire' : '/inscription')} testId="cta-wheel">
                  <Star className="w-4 h-4" /> {isAuthenticated ? 'Mon theme complet' : 'Creer mon profil'}
                </CosmicBtn>
              </div>
            </div>
          </CosmicCard>
        </div>
      </section>

      {/* ─── TIRAGE DU JOUR ─── */}
      <section className="relative z-10 max-w-2xl mx-auto px-6 md:px-8 pb-8" data-testid="section-tirage-du-jour">
        <TirageDuJour />
      </section>

      {/* ─── COSMIC SCORE ─── */}
      <section className="relative z-10 py-16 px-6 md:px-8" data-testid="section-score">
        <div className="max-w-4xl mx-auto">
          <CosmicCard glow="purple" testId="cosmic-score-card">
            <div className="flex flex-col md:flex-row gap-8 md:gap-12 items-center">
              <div className="flex-1">
                <h2 className="text-2xl md:text-3xl mb-3"
                  style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
                  Votre Indice Cosmique
                </h2>
                <p className="text-sm mb-6"
                  style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)' }}>
                  Base sur les transits planetaires actuels et votre theme natal.
                  Creez votre profil pour un alignement personnalise.
                </p>
                <CosmicScore />
              </div>
              <div className="w-40 md:w-52 flex-shrink-0">
                <img src={OEIL_IMG} alt="" className="w-full h-auto rounded-xl"
                  style={{ filter: 'drop-shadow(0 0 30px rgba(232,121,249,0.2))' }} />
              </div>
            </div>
          </CosmicCard>
        </div>
      </section>

      {/* ─── SERVICES ─── */}
      <section className="relative z-10 py-16 px-6 md:px-8" data-testid="section-services">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs uppercase tracking-[0.2em] mb-3"
              style={{ fontFamily: 'Inter, sans-serif', color: '#E879F9', letterSpacing: '0.25em', fontWeight: 500 }}>
              Vos Experiences
            </p>
            <h2 className="text-3xl md:text-4xl"
              style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
              Explorez votre univers interieur
            </h2>
          </div>

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { to: '/tarot-oui-non', icon: Eye, title: 'Tarot Oui / Non', desc: 'Posez une question, recevez une reponse claire des Arcanes', cost: '1er gratuit', glow: 'pink' },
              { to: '/tirage-tarot', icon: Sparkles, title: 'Lecture Tarot', desc: 'Tirage Marseille ou Croix Celtique avec interpretation', cost: '10 credits', glow: 'purple' },
              { to: '/numerologie', icon: Hash, title: 'Numerologie', desc: "Chemin de vie, nombre d'ame et annee personnelle", cost: '10 credits', glow: 'gold' },
              { to: '/tarologie', icon: Moon, title: 'Tarologie', desc: 'Tirage en croix de 5 Arcanes avec lecture profonde', cost: '10 credits', glow: 'purple' },
              { to: '/compatibilite-amoureuse', icon: Heart, title: 'Compatibilite', desc: 'Rapport astral complet entre deux personnes (PDF)', cost: '10 credits', glow: 'pink' },
              { to: '/premium/experience', icon: TrendingUp, title: 'Cartographie Premium', desc: '5 etapes initiatiques + manuscrit PDF personnalise', cost: '60 credits', glow: 'gold' },
            ].map(s => {
              const Icon = s.icon;
              return (
                <CosmicCard key={s.to} glow={s.glow} onClick={() => navigate(s.to)} testId={`service-card-${s.to.replace(/\//g, '')}`}>
                  <Icon className="w-6 h-6 mb-3" style={{ color: s.glow === 'gold' ? '#F4C542' : s.glow === 'pink' ? '#E879F9' : '#A78BFA' }} strokeWidth={1.5} />
                  <h3 className="text-lg mb-2" style={{ fontFamily: 'Playfair Display, serif', color: '#F8FAFC', fontWeight: 500 }}>
                    {s.title}
                  </h3>
                  <p className="text-sm mb-3" style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)', lineHeight: '1.6' }}>
                    {s.desc}
                  </p>
                  <span className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Inter, sans-serif', color: '#F4C542', letterSpacing: '0.08em', fontWeight: 500 }}>
                    {s.cost}
                  </span>
                </CosmicCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── SHAREABLE PROFILE CARD ─── */}
      {isAuthenticated && (
        <section className="relative z-10 py-12 px-6 md:px-8" data-testid="section-share-card">
          <div className="max-w-3xl mx-auto">
            <CosmicCard glow="pink" className="text-center" testId="share-card-section">
              <p className="text-xs uppercase tracking-[0.2em] mb-3"
                style={{ fontFamily: 'Inter, sans-serif', color: '#E879F9', letterSpacing: '0.25em', fontWeight: 500 }}>
                Votre Profil Cosmique
              </p>
              <h2 className="text-2xl md:text-3xl mb-3"
                style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
                Partagez votre empreinte celeste
              </h2>
              <p className="text-sm max-w-md mx-auto mb-6"
                style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)', lineHeight: '1.8' }}>
                Generez votre carte de profil cosmique personnalisee et partagez-la
                sur vos reseaux sociaux.
              </p>
              <ShareableCard />
            </CosmicCard>
          </div>
        </section>
      )}

      {/* ─── NOTRE APPROCHE ─── */}
      <section className="relative z-10 py-16 px-6 md:px-8" data-testid="section-cadre">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs uppercase tracking-[0.2em] mb-3"
            style={{ fontFamily: 'Inter, sans-serif', color: '#F4C542', letterSpacing: '0.25em', fontWeight: 500 }}>
            Notre approche
          </p>
          <h2 className="text-3xl md:text-4xl mb-6"
            style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
            Un cadre clair. Une approche responsable.
          </h2>
          <div className="space-y-4 text-base"
            style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.6)', lineHeight: '2' }}>
            <p>Plume Astrale ne predit pas votre avenir. Elle eclaire des dynamiques.</p>
            <p>Les calculs sont precis. L'interpretation est structuree.</p>
            <p style={{ color: '#F8FAFC', fontFamily: 'Playfair Display, serif', fontSize: '1.2rem', fontStyle: 'italic' }}>
              La decision vous appartient toujours.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-6 mt-10">
            {[
              { n: '01', label: 'Calculs astrologiques professionnels' },
              { n: '02', label: 'Lecture symbolique experte' },
              { n: '03', label: 'Restitution claire et accessible' },
            ].map(m => (
              <div key={m.n} className="text-center">
                <span className="text-3xl block mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#F4C542', fontWeight: 400 }}>{m.n}</span>
                <span className="text-xs" style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)' }}>{m.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── LE CERCLE CTA ─── */}
      <section className="relative z-10 py-16 px-6 md:px-8" data-testid="section-cercle">
        <div className="max-w-4xl mx-auto">
          <CosmicCard glow="pink" className="text-center">
            <Flame className="w-10 h-10 mx-auto mb-4" style={{ color: '#FF6B35' }} strokeWidth={1.5} />
            <h2 className="text-2xl md:text-3xl mb-3"
              style={{ fontFamily: 'Cinzel, serif', color: '#F8FAFC', fontWeight: 500 }}>
              Rejoignez le Cercle
            </h2>
            <p className="text-base max-w-md mx-auto mb-6"
              style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.6)', lineHeight: '1.8' }}>
              Votre espace quotidien. Insights cosmiques, carte du jour, streak de check-in.
              Revenez chaque jour pour gagner des credits bonus.
            </p>
            <CosmicBtn onClick={() => navigate('/cercle')} testId="cta-final-cercle">
              <Flame className="w-4 h-4" /> Entrer dans le Cercle
            </CosmicBtn>
          </CosmicCard>
        </div>
      </section>

      {/* ─── FINAL CTA ─── */}
      <section className="relative z-10 py-20 px-6 md:px-8 text-center" data-testid="section-final">
        <h2 className="text-3xl md:text-4xl lg:text-5xl mb-6"
          style={{ fontFamily: 'Cinzel, serif', fontWeight: 500, color: '#F8FAFC' }}>
          Prenez un moment pour vous<br />comprendre autrement.
        </h2>
        <p className="text-base mb-8 max-w-md mx-auto"
          style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.5)' }}>
          {!isAuthenticated ? "20 credits offerts a l'inscription." : `Votre solde : ${creditBalance} credits`}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <CosmicBtn onClick={() => navigate(isAuthenticated ? '/formulaire' : '/inscription')} testId="cta-final-main">
            <Sparkles className="w-4 h-4" /> {isAuthenticated ? 'Decouvrir mon analyse' : 'Commencer gratuitement'}
          </CosmicBtn>
          <CosmicBtn onClick={() => navigate('/acheter-credits')} testId="cta-final-credits" secondary>
            Voir les offres <ArrowRight className="w-4 h-4" />
          </CosmicBtn>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 px-6 text-center" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <p className="text-xs tracking-widest"
          style={{ fontFamily: 'Inter, sans-serif', color: 'rgba(248,250,252,0.3)', letterSpacing: '0.15em' }}>
          Plume Astrale — Guidance symbolique personnalisee.
        </p>
      </footer>
    </div>
  );
};

export default Index;
