import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import Hero3D from '../components/Hero3D';
import SolenaChat from '../components/SolenaChat';
import QuickOracle from '../components/QuickOracle';
import StarsAndClouds from '../components/StarsAndClouds';
import {
  Sparkles, Heart, ArrowRight, Quote, CheckCircle2, Play, Star
} from 'lucide-react';
import SEO from '../components/SEO';
import { SOLENA } from '../lib/solena';

/* ═══════════════════════════════════════════════════════════
   COSMIC CANVAS — starfield d'arrière-plan léger
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

    const stars = Array.from({ length: 150 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 1.4 + 0.3,
      twinkle: Math.random() * Math.PI * 2,
      hue: Math.random() > 0.85
        ? `rgba(196,181,253,${0.5 + Math.random() * 0.4})`
        : `rgba(255,255,255,${0.4 + Math.random() * 0.4})`,
    }));

    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stars.forEach(s => {
        s.twinkle += 0.025;
        const alpha = 0.5 + Math.sin(s.twinkle) * 0.5;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = s.hue.replace(/[\d.]+\)$/, `${alpha.toFixed(2)})`);
        ctx.fill();
      });
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
      style={{ opacity: 0.65 }}
    />
  );
};

/* BrandStory removed — content consolidated into Hero3D and SolenaJourney */

/* ═══════════════════════════════════════════════════════════
   SOLENA JOURNEY — parcours storytelling + chat inline
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
        background: '#0C1120',
      }}>
      <StarsAndClouds />
      <div className="max-w-6xl mx-auto">

        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-5"
            style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.30)' }}>
            <Sparkles style={{ width: 12, height: 12, color: '#D4AF37' }} strokeWidth={1.5} />
            <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.3em', fontWeight: 400 }}>
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
            Je suis <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>Solena</em>,<br />
            la voix de <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>Plume Astrale</em>.
          </h2>
          <p className="max-w-2xl mx-auto text-base md:text-lg" style={{
            fontFamily: 'Cormorant Garamond, serif',
            color: 'rgba(244,232,210,0.75)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}>
            Astrologue, tarologue et médium depuis quinze ans — je décode ton ciel de naissance
            pour révéler tes cycles d&apos;amour et t&apos;éclairer, en direct.
          </p>
        </div>

        {/* Vidéo + Chat panel */}
        <div className="grid md:grid-cols-5 gap-8 md:gap-10 items-stretch mb-16">

          {/* Colonne vidéo — 2/5 */}
          <div className="md:col-span-2 flex justify-center">
            <div className="relative w-full max-w-sm">
              <div style={{
                position: 'absolute', inset: '-12%',
                background: 'radial-gradient(circle, rgba(212,175,55,0.35), transparent 65%)',
                filter: 'blur(35px)',
              }} />
              <div style={{
                position: 'relative',
                aspectRatio: '9/16',
                width: '100%',
                borderRadius: '32px',
                overflow: 'hidden',
                border: '2px solid rgba(212,175,55,0.55)',
                boxShadow: '0 40px 100px rgba(212,175,55,0.25), 0 0 60px rgba(212,175,55,0.15)',
              }}>
                <video
                  ref={videoRef}
                  src={SOLENA.videos.primary}
                  poster={SOLENA.portrait}
                  muted loop playsInline autoPlay preload="metadata"
                  onClick={toggleVideo}
                  style={{ width: '100%', height: '100%', objectFit: 'cover', cursor: 'pointer', display: 'block' }}
                  data-testid="home-solena-video"
                />
                <div style={{
                  position: 'absolute', bottom: 0, left: 0, right: 0,
                  padding: '30px 24px 20px',
                  background: 'linear-gradient(180deg, transparent, rgba(0,0,0,0.75))',
                  pointerEvents: 'none',
                }}>
                  <div style={{ color: '#E8C766', fontSize: 11, letterSpacing: '0.25em', textTransform: 'uppercase', fontWeight: 400 }}>
                    ✦ Solena
                  </div>
                  <div style={{ color: 'rgba(244,232,210,0.85)', fontSize: 12, marginTop: 4, fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
                    {SOLENA.title}
                  </div>
                </div>
                <button
                  onClick={toggleVideo}
                  aria-label={videoPlaying ? 'Couper le son' : 'Activer le son'}
                  style={{
                    position: 'absolute', top: 14, right: 14,
                    width: 40, height: 40, borderRadius: '50%',
                    background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(212,175,55,0.5)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    cursor: 'pointer', backdropFilter: 'blur(6px)',
                  }}
                  data-testid="home-solena-video-toggle"
                >
                  <Play style={{ width: 14, height: 14, color: '#E8C766', marginLeft: 2 }} strokeWidth={2} />
                </button>
              </div>
            </div>
          </div>

          {/* Colonne chat — 3/5 */}
          <div className="md:col-span-3 flex flex-col justify-center">
            <SolenaChat />
            <div className="mt-4 text-center text-[10px] uppercase" style={{ color: 'rgba(244,232,210,0.4)', letterSpacing: '0.2em' }}>
              Ta conversation reste privée · pas de carte bancaire
            </div>
          </div>
        </div>

        {/* Spécialités */}
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <p className="text-[10px] uppercase" style={{ color: 'rgba(212,175,55,0.7)', letterSpacing: '0.3em' }}>
              Ses six spécialités
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {SOLENA.specialities.map((s, i) => (
              <div key={i}
                className="plume-glass !rounded-2xl !p-4 flex items-start gap-3 transition-transform duration-400 ease-plume-silk hover:scale-[1.02]"
                data-testid={`home-solena-speciality-${i}`}>
                <CheckCircle2 style={{ width: 18, height: 18, color: '#D4AF37', flexShrink: 0, marginTop: 2 }} strokeWidth={1.5} />
                <span className="text-sm" style={{ fontFamily: 'Cormorant Garamond, serif', color: 'rgba(244,232,210,0.88)', lineHeight: 1.4 }}>
                  {s}
                </span>
              </div>
            ))}
          </div>
          <div className="text-center mt-8 flex flex-col sm:flex-row gap-3 justify-center items-center flex-wrap">
            <Link to="/solena" className="plume-btn-primary" data-testid="home-solena-discover-btn">
              Découvrir l&apos;univers de Solena
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
            </Link>
            <div className="text-[10px] text-center" style={{ color: 'rgba(244,232,210,0.4)', letterSpacing: '0.2em', maxWidth: 300 }}>
              Autres expériences:&nbsp;
              <Link to="/archetype" style={{ color: '#D4AF37', textDecoration: 'underline', fontSize: 10 }} data-testid="home-archetype-cta">
                Archétype&nbsp;(15 cr)
              </Link>
              &nbsp;·&nbsp;
              <Link to="/kabbale" style={{ color: '#D4AF37', textDecoration: 'underline', fontSize: 10 }} data-testid="home-kabbale-cta">
                Arbre de Vie&nbsp;(39€)
              </Link>
            </div>
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
  { name: 'Camille R.', location: 'Paris', sign: 'Balance', stars: 5, date: 'Janvier 2026',
    text: "Je suis restée bouche bée en lisant le portrait de mon âme sœur. J'ai reconnu la personne que j'ai rencontrée trois semaines plus tard sur une appli — les mêmes traits, la même énergie. Solena voit vraiment quelque chose." },
  { name: 'Léa M.', location: 'Lyon', sign: 'Poissons', stars: 5, date: 'Décembre 2025',
    text: "Ce qui m'a bouleversée, c'est la finesse du décodage. Rien de générique, rien de flou. Solena m'a expliqué pourquoi je revivais toujours le même schéma amoureux — et comment le couper. Depuis, je me sens plus alignée." },
  { name: 'Sarah T.', location: 'Bordeaux', sign: 'Cancer', stars: 5, date: 'Janvier 2026',
    text: "J'étais sceptique. Le portrait m'a scotchée. Le prochain rendez-vous astral tombait dans 11 jours — j'ai rencontré quelqu'un le 9ᵉ. Coïncidence ? Peut-être. Mais quelle coïncidence." },
  { name: 'Manon D.', location: 'Marseille', sign: 'Lion', stars: 5, date: 'Février 2026',
    text: "Le Guide Ultime à 29,99€ vaut chaque centime. 15 pages ultra personnalisées sur mes cycles d'amour de 2026. Je le relis chaque semaine. Plus efficace que trois ans de thérapie sur mes blocages relationnels." },
  { name: 'Julie P.', location: 'Nantes', sign: 'Sagittaire', stars: 5, date: 'Décembre 2025',
    text: "Après un divorce difficile, j'avais besoin de sens. Solena m'a offert exactement ça : de la clarté, sans jugement, avec une bienveillance rare. Le tarot évolutif du jour est devenu mon rituel." },
  { name: 'Emma L.', location: 'Toulouse', sign: 'Vierge', stars: 5, date: 'Janvier 2026',
    text: "Le chat avec Plume est incroyable. Je pose une question à 23h après une dispute, je reçois une lecture astro précise en 15 secondes. C'est comme avoir Solena dans ma poche." },
];

const StarRow = ({ n = 5 }) => (
  <div className="flex gap-0.5">
    {Array.from({ length: n }).map((_, i) => (
      <Star key={i} style={{ width: 12, height: 12, color: '#E8C766', fill: '#E8C766' }} strokeWidth={0} />
    ))}
  </div>
);

const ReviewCard = ({ review, active }) => (
  <div
    className="rounded-3xl p-6 md:p-8 h-full flex flex-col transition-all duration-500"
    style={{
      background: active
        ? 'linear-gradient(160deg, rgba(212,175,55,0.08) 0%, rgba(20,15,40,0.85) 100%)'
        : 'linear-gradient(160deg, rgba(255,255,255,0.02) 0%, rgba(20,15,40,0.5) 100%)',
      border: active ? '1px solid rgba(212,175,55,0.55)' : '1px solid rgba(212,175,55,0.15)',
      backdropFilter: 'blur(14px)',
      boxShadow: active
        ? '0 20px 60px rgba(212,175,55,0.15), 0 0 40px rgba(212,175,55,0.10)'
        : '0 10px 30px rgba(6,8,26,0.4)',
      opacity: active ? 1 : 0.65,
      transform: active ? 'scale(1)' : 'scale(0.94)',
      minHeight: 280,
    }}
    data-testid={`review-card-${review.name.replace(/\s+/g, '-').toLowerCase()}`}
  >
    <div className="flex items-center justify-between mb-4">
      <StarRow n={review.stars} />
      <span className="text-[9px] uppercase" style={{ color: 'rgba(212,175,55,0.5)', letterSpacing: '0.25em' }}>
        Vérifié
      </span>
    </div>
    <Quote style={{ width: 18, height: 18, color: '#D4AF37', opacity: 0.4, marginBottom: 8 }} strokeWidth={1.5} />
    <p className="text-base md:text-lg flex-1 mb-6" style={{
      fontFamily: 'Cormorant Garamond, serif',
      color: 'rgba(244,232,210,0.90)',
      lineHeight: 1.55,
      fontWeight: 400,
    }}>
      « {review.text} »
    </p>
    <div className="pt-4" style={{ borderTop: '1px solid rgba(212,175,55,0.15)' }}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm" style={{ color: '#F4E8D2', fontFamily: 'Cormorant Garamond, serif', fontWeight: 500, letterSpacing: '0.05em' }}>
            {review.name}
          </div>
          <div className="text-[10px] mt-0.5" style={{ color: 'rgba(212,175,55,0.65)', letterSpacing: '0.2em', textTransform: 'uppercase' }}>
            {review.sign} · {review.location}
          </div>
        </div>
        <div className="text-[10px]" style={{ color: 'rgba(212,175,55,0.45)', letterSpacing: '0.15em', textTransform: 'uppercase' }}>
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
  const visible = [0, 1, 2].map((offset) => REVIEWS[(index + offset) % total]);

  return (
    <section className="relative py-24 px-4 z-10" data-testid="client-reviews-section">
      <div className="max-w-6xl mx-auto">

        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-5"
            style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.30)' }}>
            <Star style={{ width: 12, height: 12, color: '#E8C766', fill: '#E8C766' }} strokeWidth={0} />
            <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.3em', fontWeight: 400 }}>
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
            <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>parler.</em>
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

        <div className="hidden md:grid grid-cols-3 gap-5 mb-8">
          {visible.map((r, i) => (
            <ReviewCard key={`${r.name}-${index}-${i}`} review={r} active={i === 1} />
          ))}
        </div>

        <div className="md:hidden mb-8">
          <ReviewCard review={REVIEWS[index]} active={true} />
        </div>

        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => go(-1)}
            className="w-10 h-10 rounded-full flex items-center justify-center transition-all hover:scale-110"
            style={{ border: '1px solid rgba(212,175,55,0.35)', color: '#D4AF37', background: 'transparent' }}
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
                  background: i === index ? '#D4AF37' : 'rgba(212,175,55,0.25)',
                  boxShadow: i === index ? '0 0 12px rgba(212,175,55,0.6)' : 'none',
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
            style={{ border: '1px solid rgba(212,175,55,0.35)', color: '#D4AF37', background: 'transparent' }}
            aria-label="Avis suivant"
            data-testid="reviews-next-btn"
          >
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
          </button>
        </div>

        <div className="text-center mt-10">
          <button
            onClick={() => {
              const el = document.querySelector('[data-testid="home-solena-section"]');
              if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
              window.dispatchEvent(new CustomEvent('pa:open-solena-chat'));
            }}
            className="inline-flex items-center gap-2 px-7 py-3 rounded-full text-xs uppercase transition-all hover:scale-[1.02]"
            style={{
              background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
              color: '#0C0918', letterSpacing: '0.2em', fontWeight: 700,
              boxShadow: '0 12px 40px rgba(212,175,55,0.30)',
              border: 'none', cursor: 'pointer',
            }}
            data-testid="reviews-cta-btn">
            <Heart style={{ width: 14, height: 14 }} strokeWidth={2} />
            Discuter avec Solena — Gratuit
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
          </button>
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
  const [showQuickOracle, setShowQuickOracle] = useState(false);

  return (
    <div className="relative" style={{ overflow: 'hidden' }}>
      <SEO path="/" />
      <CosmicCanvas />
      {showQuickOracle ? (
        <QuickOracle 
          onClose={() => setShowQuickOracle(false)}
          onSelectPack={(packId) => {
            const packMap = {
              initiation: 'essentiel',
              clarte: 'premium',
              flammes: 'premium'
            };
            localStorage.setItem('plume_astrale_plan', packMap[packId]);
            window.location.href = '/paiement';
          }}
        />
      ) : (
        <>
          <Hero3D />
          <section className="relative py-12 px-4 z-10 text-center" style={{ background: 'transparent' }} data-testid="oracle-cta-section">
            <div className="max-w-md mx-auto">
              <button
                onClick={() => setShowQuickOracle(true)}
                className="w-full px-8 py-4 rounded-2xl text-center transition-all hover:scale-105 active:scale-95"
                style={{
                  background: 'linear-gradient(135deg, #D4AF37, #E8C766)',
                  color: '#0C0918',
                  fontFamily: 'Cormorant Garamond, serif',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  letterSpacing: '0.08em',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 10px 30px rgba(212,175,55,0.3)',
                }}
                data-testid="quick-oracle-cta-hero"
              >
                Découvrez votre oracle du jour GRATUITEMENT
              </button>
              <p style={{ color: 'rgba(244,232,210,0.5)', fontSize: '0.85rem', marginTop: '1rem', letterSpacing: '0.05em' }}>
                Aucune inscription requise
              </p>
            </div>
          </section>
        </>
      )}
      <SolenaJourney />
      <ClientReviews />

      {/* Trust badge — technologie */}
      <section className="py-12 px-4 relative z-10" style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }} data-testid="trust-astrology-api">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[10px] uppercase mb-4" style={{ color: 'rgba(244,232,210,0.5)', letterSpacing: '0.25em' }}>
            Technologie de confiance
          </p>
          <p className="text-base mb-3" style={{ color: 'rgba(244,232,210,0.85)', fontFamily: 'Cormorant Garamond, serif', fontSize: 22, lineHeight: 1.4 }}>
            Calculs astrologiques propulsés par <span style={{ color: '#D4AF37', fontWeight: 500, fontStyle: 'italic' }}>astrology-api.io v3</span> · Textes générés par <span style={{ color: '#D4AF37', fontWeight: 500, fontStyle: 'italic' }}>OpenAI GPT</span>
          </p>
          <p className="text-sm max-w-xl mx-auto" style={{ color: 'rgba(244,232,210,0.55)', lineHeight: 1.6 }}>
            Éphémérides précises, fuseaux horaires, maisons astrologiques et aspects planétaires —
            la même plateforme utilisée par les applications spécialisées.
          </p>
          <div className="flex items-center justify-center gap-6 mt-6 text-[10px] uppercase" style={{ color: 'rgba(244,232,210,0.4)', letterSpacing: '0.25em' }}>
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
