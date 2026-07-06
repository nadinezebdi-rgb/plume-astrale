import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import MoonHero from '../components/MoonHero';
import {
  Sparkles, Moon, Heart, Compass, MessageCircle, BookHeart,
  Flame, Stars, ArrowRight, Quote, Sun, Cloud, Wind, CheckCircle2, Play, Star
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import HeroOracle from '../components/HeroOracle';
import EnergyToday from '../components/EnergyToday';
import SocialProof from '../components/SocialProof';
import NatalCompletionPrompt from '../components/NatalCompletionPrompt';
import { SOLENA } from '../lib/solena';

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
   SOLENA JOURNEY — parcours storytelling de l'ambassadrice
═══════════════════════════════════════════════════════════ */
const SolenaJourney = () => {
  const videoRef = useRef(null);
  const [videoPlaying, setVideoPlaying] = useState(false);

  const toggleVideo = () => {
    if (!videoRef.current) return;
    if (videoPlaying) {
      videoRef.current.pause();
      setVideoPlaying(false);
    } else {
      videoRef.current.muted = false;
      videoRef.current.play();
      setVideoPlaying(true);
    }
  };

  return (
    <section className="relative py-24 md:py-32 px-4 z-10" data-testid="home-solena-section"
      style={{
        background: 'linear-gradient(180deg, transparent 0%, rgba(20,15,40,0.4) 30%, rgba(20,15,40,0.4) 70%, transparent 100%)',
      }}>
      <div className="max-w-6xl mx-auto">

        {/* Kicker centré */}
        <div className="text-center mb-14 animate-fade-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-5"
            style={{ background: 'rgba(212,180,106,0.08)', border: '1px solid rgba(212,180,106,0.30)' }}>
            <Sparkles style={{ width: 12, height: 12, color: '#D4B46A' }} strokeWidth={1.5} />
            <span className="text-[10px] uppercase" style={{ color: '#D4B46A', letterSpacing: '0.3em', fontWeight: 400 }}>
              Rencontre ta guide
            </span>
          </div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(2rem, 5vw, 3.5rem)',
            lineHeight: 1.05,
            color: '#F4E8D2',
            marginBottom: 16,
          }}>
            Je suis <em style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 300 }}>Solena</em>,<br />
            la voix de <em style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 300 }}>Plume Astrale</em>.
          </h2>
          <p className="max-w-2xl mx-auto text-base md:text-lg" style={{
            fontFamily: 'Cormorant Garamond, serif',
            color: 'rgba(244,232,210,0.75)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}>
            Astrologue, tarologue et médium depuis quinze ans — je décode ton ciel de naissance
            pour révéler les cycles d&apos;amour qui t&apos;attendent.
          </p>
        </div>

        {/* Vidéo + Storytelling */}
        <div className="grid md:grid-cols-5 gap-10 md:gap-14 items-center mb-20">

          {/* Colonne vidéo — 2/5 */}
          <div className="md:col-span-2 flex justify-center order-1">
            <div className="relative w-full max-w-sm">
              {/* Aura dorée */}
              <div style={{
                position: 'absolute', inset: '-12%',
                background: 'radial-gradient(circle, rgba(212,180,106,0.35), transparent 65%)',
                filter: 'blur(35px)',
              }} />

              {/* Vidéo en cadre rond */}
              <div style={{
                position: 'relative',
                aspectRatio: '9/16',
                width: '100%',
                borderRadius: '32px',
                overflow: 'hidden',
                border: '2px solid rgba(212,180,106,0.55)',
                boxShadow: '0 40px 100px rgba(212,180,106,0.25), 0 0 60px rgba(212,180,106,0.15)',
              }}>
                <video
                  ref={videoRef}
                  src={SOLENA.videos.primary}
                  poster={SOLENA.portrait}
                  muted
                  loop
                  playsInline
                  autoPlay
                  preload="metadata"
                  onClick={toggleVideo}
                  style={{ width: '100%', height: '100%', objectFit: 'cover', cursor: 'pointer', display: 'block' }}
                  data-testid="home-solena-video"
                />
                {/* Overlay bas */}
                <div style={{
                  position: 'absolute', bottom: 0, left: 0, right: 0,
                  padding: '30px 24px 20px',
                  background: 'linear-gradient(180deg, transparent, rgba(0,0,0,0.75))',
                  pointerEvents: 'none',
                }}>
                  <div style={{ color: '#F4D98C', fontSize: 11, letterSpacing: '0.25em', textTransform: 'uppercase', fontWeight: 400 }}>
                    ✦ Solena
                  </div>
                  <div style={{ color: 'rgba(244,232,210,0.85)', fontSize: 12, marginTop: 4, fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                    {SOLENA.title}
                  </div>
                </div>
                {/* Play / mute badge */}
                <button
                  onClick={toggleVideo}
                  aria-label={videoPlaying ? 'Couper le son' : 'Activer le son'}
                  style={{
                    position: 'absolute', top: 14, right: 14,
                    width: 40, height: 40, borderRadius: '50%',
                    background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(212,180,106,0.5)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', backdropFilter: 'blur(6px)',
                  }}
                  data-testid="home-solena-video-toggle"
                >
                  <Play style={{ width: 14, height: 14, color: '#F4D98C', marginLeft: 2 }} strokeWidth={2} />
                </button>
              </div>
            </div>
          </div>

          {/* Colonne texte — 3/5 */}
          <div className="md:col-span-3 order-2">
            <div className="space-y-5" style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '1.05rem', lineHeight: 1.7, color: 'rgba(244,232,210,0.88)' }}>
              <p>
                <span style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 500 }}>Bienvenue.</span>{' '}
                Je considère chaque personne dans sa totalité — esprit, émotions, énergies.
                Je n&apos;annonce jamais un futur figé : je révèle des <em style={{ color: '#F4D98C' }}>cycles</em>, des <em style={{ color: '#F4D98C' }}>invitations</em>, des <em style={{ color: '#F4D98C' }}>choix</em>.
              </p>
              <p>
                Chez Plume Astrale, je m&apos;associe à une intelligence divinatoire de nouvelle génération
                pour t&apos;offrir une guidance personnalisée, précise et vibratoire.
              </p>
              <p style={{ color: '#F4D98C', fontStyle: 'italic', fontSize: '1.1rem' }}>
                « Ni horoscope générique, ni prédiction fataliste — une conversation intime avec ton ciel de naissance. »
              </p>
            </div>

            {/* CTA */}
            <div className="flex flex-wrap gap-3 mt-8">
              <Link to="/rencontres-astrales"
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
                style={{
                  background: 'linear-gradient(135deg, #D4B46A 0%, #F4D98C 50%, #D4B46A 100%)',
                  color: '#0C0918',
                  letterSpacing: '0.2em',
                  fontWeight: 700,
                  boxShadow: '0 12px 40px rgba(212,180,106,0.35)',
                }}
                data-testid="home-solena-consult-btn">
                <Heart style={{ width: 14, height: 14 }} strokeWidth={2} />
                Consulter Solena · Gratuit
                <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
              </Link>
              <Link to="/solena"
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
                style={{
                  border: '1px solid rgba(212,180,106,0.5)',
                  color: '#D4B46A',
                  letterSpacing: '0.2em',
                  fontWeight: 400,
                  background: 'transparent',
                }}
                data-testid="home-solena-discover-btn">
                Découvrir son univers
              </Link>
            </div>
          </div>
        </div>

        {/* Spécialités — 6 cartes minimalistes */}
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <p className="text-[10px] uppercase" style={{ color: 'rgba(212,180,106,0.7)', letterSpacing: '0.3em' }}>
              Ses six spécialités
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {SOLENA.specialities.map((s, i) => (
              <div key={i}
                className="rounded-2xl p-4 flex items-start gap-3 transition-all hover:scale-[1.02] animate-fade-up"
                style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(212,180,106,0.18)',
                  backdropFilter: 'blur(10px)',
                  animationDelay: `${i * 70}ms`,
                }}
                data-testid={`home-solena-speciality-${i}`}>
                <CheckCircle2 style={{ width: 18, height: 18, color: '#D4B46A', flexShrink: 0, marginTop: 2 }} strokeWidth={1.5} />
                <span className="text-sm" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'rgba(244,232,210,0.88)', lineHeight: 1.4 }}>
                  {s}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
};

/* ═══════════════════════════════════════════════════════════
   CLIENT REVIEWS — carrousel avis authentiques
═══════════════════════════════════════════════════════════ */
const REVIEWS = [
  {
    name: 'Camille R.',
    location: 'Paris',
    sign: 'Balance',
    stars: 5,
    date: 'Janvier 2026',
    text: "Je suis restée bouche bée en lisant le portrait de mon âme sœur. J'ai reconnu la personne que j'ai rencontrée trois semaines plus tard sur une appli — les mêmes traits, la même énergie. Solena voit vraiment quelque chose.",
    highlight: 'j\'ai reconnu la personne',
  },
  {
    name: 'Léa M.',
    location: 'Lyon',
    sign: 'Poissons',
    stars: 5,
    date: 'Décembre 2025',
    text: "Ce qui m'a bouleversée, c'est la finesse du décodage. Rien de générique, rien de flou. Solena m'a expliqué pourquoi je revivais toujours le même schéma amoureux — et comment le couper. Depuis, je me sens plus alignée.",
    highlight: 'la finesse du décodage',
  },
  {
    name: 'Sarah T.',
    location: 'Bordeaux',
    sign: 'Cancer',
    stars: 5,
    date: 'Janvier 2026',
    text: "J'étais sceptique. Le portrait m'a scotchée. Le prochain rendez-vous astral tombait dans 11 jours — j'ai rencontré quelqu'un le 9ᵉ. Coïncidence ? Peut-être. Mais quelle coïncidence.",
    highlight: 'quelle coïncidence',
  },
  {
    name: 'Manon D.',
    location: 'Marseille',
    sign: 'Lion',
    stars: 5,
    date: 'Février 2026',
    text: "Le Guide Ultime à 29,99€ vaut chaque centime. 15 pages ultra personnalisées sur mes cycles d'amour de 2026. Je le relis chaque semaine. Plus efficace que trois ans de thérapie sur mes blocages relationnels.",
    highlight: 'vaut chaque centime',
  },
  {
    name: 'Julie P.',
    location: 'Nantes',
    sign: 'Sagittaire',
    stars: 5,
    date: 'Décembre 2025',
    text: "Après un divorce difficile, j'avais besoin de sens. Solena m'a offert exactement ça : de la clarté, sans jugement, avec une bienveillance rare. Le tarot évolutif du jour est devenu mon rituel.",
    highlight: 'clarté sans jugement',
  },
  {
    name: 'Emma L.',
    location: 'Toulouse',
    sign: 'Vierge',
    stars: 5,
    date: 'Janvier 2026',
    text: "Le chat avec Plume est incroyable. Je pose une question à 23h après une dispute, je reçois une lecture astro précise en 15 secondes. C'est comme avoir Solena dans ma poche.",
    highlight: 'Solena dans ma poche',
  },
];

const StarRow = ({ n = 5 }) => (
  <div className="flex gap-0.5">
    {Array.from({ length: n }).map((_, i) => (
      <Star key={i} style={{ width: 12, height: 12, color: '#F4D98C', fill: '#F4D98C' }} strokeWidth={0} />
    ))}
  </div>
);

const ReviewCard = ({ review, active }) => (
  <div
    className="rounded-3xl p-6 md:p-8 h-full flex flex-col transition-all duration-500"
    style={{
      background: active
        ? 'linear-gradient(160deg, rgba(212,180,106,0.08) 0%, rgba(20,15,40,0.85) 100%)'
        : 'linear-gradient(160deg, rgba(255,255,255,0.02) 0%, rgba(20,15,40,0.5) 100%)',
      border: active ? '1px solid rgba(212,180,106,0.55)' : '1px solid rgba(212,180,106,0.15)',
      backdropFilter: 'blur(14px)',
      boxShadow: active
        ? '0 20px 60px rgba(212,180,106,0.15), 0 0 40px rgba(212,180,106,0.10)'
        : '0 10px 30px rgba(6,8,26,0.4)',
      opacity: active ? 1 : 0.65,
      transform: active ? 'scale(1)' : 'scale(0.94)',
      minHeight: 280,
    }}
    data-testid={`review-card-${review.name.replace(/\s+/g, '-').toLowerCase()}`}
  >
    <div className="flex items-center justify-between mb-4">
      <StarRow n={review.stars} />
      <span className="text-[9px] uppercase" style={{ color: 'rgba(212,180,106,0.5)', letterSpacing: '0.25em' }}>
        Vérifié
      </span>
    </div>
    <Quote style={{ width: 18, height: 18, color: '#D4B46A', opacity: 0.4, marginBottom: 8 }} strokeWidth={1.5} />
    <p className="text-base md:text-lg flex-1 mb-6" style={{
      fontFamily: 'Cormorant Garamond, serif',
      color: 'rgba(244,232,210,0.90)',
      lineHeight: 1.55,
      fontWeight: 400,
    }}>
      « {review.text} »
    </p>
    <div className="pt-4" style={{ borderTop: '1px solid rgba(212,180,106,0.15)' }}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm" style={{ color: '#F4E8D2', fontFamily: 'Cormorant Garamond, serif', fontWeight: 500, letterSpacing: '0.05em' }}>
            {review.name}
          </div>
          <div className="text-[10px] mt-0.5" style={{ color: 'rgba(212,180,106,0.65)', letterSpacing: '0.2em', textTransform: 'uppercase' }}>
            {review.sign} · {review.location}
          </div>
        </div>
        <div className="text-[10px]" style={{ color: 'rgba(212,180,106,0.45)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
          {review.date}
        </div>
      </div>
    </div>
  </div>
);

const ClientReviews = () => {
  const [index, setIndex] = useState(0);
  const total = REVIEWS.length;

  useEffect(() => {
    const timer = setInterval(() => setIndex((i) => (i + 1) % total), 6000);
    return () => clearInterval(timer);
  }, [total]);

  const go = (delta) => setIndex((i) => (i + delta + total) % total);

  // Show current + next 2 in a horizontal window (desktop 3-up)
  const visible = [0, 1, 2].map((offset) => REVIEWS[(index + offset) % total]);

  return (
    <section className="relative py-24 px-4 z-10" data-testid="client-reviews-section">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-5"
            style={{ background: 'rgba(212,180,106,0.08)', border: '1px solid rgba(212,180,106,0.30)' }}>
            <Star style={{ width: 12, height: 12, color: '#F4D98C', fill: '#F4D98C' }} strokeWidth={0} />
            <span className="text-[10px] uppercase" style={{ color: '#D4B46A', letterSpacing: '0.3em', fontWeight: 400 }}>
              4.9 / 5 · +2 000 âmes accompagnées
            </span>
          </div>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(1.9rem, 4.5vw, 3rem)',
            lineHeight: 1.1,
            color: '#F4E8D2',
            marginBottom: 12,
          }}>
            Elles ont laissé leurs étoiles<br />
            <em style={{ color: '#D4B46A', fontStyle: 'italic', fontWeight: 300 }}>parler.</em>
          </h2>
          <p className="max-w-xl mx-auto text-sm md:text-base" style={{
            fontFamily: 'Cormorant Garamond, serif',
            color: 'rgba(244,232,210,0.65)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}>
            Des retours authentiques de la communauté Plume Astrale.
          </p>
        </div>

        {/* Desktop 3-up grid */}
        <div className="hidden md:grid grid-cols-3 gap-5 mb-8">
          {visible.map((r, i) => (
            <ReviewCard key={`${r.name}-${index}-${i}`} review={r} active={i === 1} />
          ))}
        </div>

        {/* Mobile — single card */}
        <div className="md:hidden mb-8">
          <ReviewCard review={REVIEWS[index]} active={true} />
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => go(-1)}
            className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-110"
            style={{ border: '1px solid rgba(212,180,106,0.35)', color: '#D4B46A', background: 'transparent' }}
            aria-label="Avis précédent"
            data-testid="reviews-prev-btn"
          >
            <ArrowRight style={{ width: 14, height: 14, transform: 'rotate(180deg)' }} strokeWidth={1.5} />
          </button>

          <div className="flex gap-2">
            {REVIEWS.map((_, i) => (
              <button
                key={i}
                onClick={() => setIndex(i)}
                style={{
                  width: i === index ? 24 : 8,
                  height: 8,
                  borderRadius: 999,
                  background: i === index ? '#D4B46A' : 'rgba(212,180,106,0.25)',
                  boxShadow: i === index ? '0 0 12px rgba(212,180,106,0.6)' : 'none',
                  transition: 'all 0.3s',
                  border: 'none',
                  cursor: 'pointer',
                }}
                aria-label={`Aller à l'avis ${i + 1}`}
                data-testid={`reviews-dot-${i}`}
              />
            ))}
          </div>

          <button
            onClick={() => go(1)}
            className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-110"
            style={{ border: '1px solid rgba(212,180,106,0.35)', color: '#D4B46A', background: 'transparent' }}
            aria-label="Avis suivant"
            data-testid="reviews-next-btn"
          >
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
          </button>
        </div>

        {/* CTA sous les avis */}
        <div className="text-center mt-10">
          <Link to="/rencontres-astrales"
            className="inline-flex items-center gap-2 px-7 py-3 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
            style={{
              background: 'linear-gradient(135deg, #D4B46A 0%, #F4D98C 50%, #D4B46A 100%)',
              color: '#0C0918', letterSpacing: '0.2em', fontWeight: 700,
              boxShadow: '0 12px 40px rgba(212,180,106,0.30)',
            }}
            data-testid="reviews-cta-btn">
            <Heart style={{ width: 14, height: 14 }} strokeWidth={2} />
            Recevoir mon portrait — Gratuit
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
          </Link>
          <p className="text-[10px] mt-4" style={{ color: 'rgba(244,232,210,0.4)', letterSpacing: '0.2em' }}>
            AUCUNE CARTE BANCAIRE · RÉSULTAT INSTANTANÉ
          </p>
        </div>

      </div>
    </section>
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

      <MoonHero />


      {/* ═══════ SECTION — PARCOURS SOLENA (ambassadrice) ═══════ */}
      <SolenaJourney />

      {/* ═══════ SECTION — AVIS CLIENTS (social proof) ═══════ */}
      <ClientReviews />

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
