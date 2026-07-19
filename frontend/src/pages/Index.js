import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import Hero3D from '../components/Hero3D';
import SolenaChat from '../components/SolenaChat';
import QuickOracle from '../components/QuickOracle';
import HomeCreditPacks from '../components/HomeCreditPacks';
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
    // Etoiles filantes (shooting stars)
    let shootingStars = [];
    const spawnShootingStar = () => {
      const startX = Math.random() * canvas.width;
      const startY = Math.random() * canvas.height * 0.5;
      shootingStars.push({
        x: startX, y: startY,
        len: 80 + Math.random() * 120,
        speed: 6 + Math.random() * 6,
        angle: Math.PI / 4,
        alpha: 1,
      });
    };
    let lastSpawn = 0;

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
      // Dessin des etoiles filantes
      const now = performance.now();
      if (now - lastSpawn > 2200 + Math.random() * 2600) {
        spawnShootingStar();
        lastSpawn = now;
      }
      shootingStars = shootingStars.filter((m) => m.alpha > 0);
      shootingStars.forEach((m) => {
        const dx = Math.cos(m.angle) * m.len;
        const dy = Math.sin(m.angle) * m.len;
        const grad = ctx.createLinearGradient(m.x, m.y, m.x - dx, m.y - dy);
        grad.addColorStop(0, `rgba(255,255,255,${m.alpha})`);
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.strokeStyle = grad;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(m.x, m.y);
        ctx.lineTo(m.x - dx, m.y - dy);
        ctx.stroke();
        m.x += Math.cos(m.angle) * m.speed;
        m.y += Math.sin(m.angle) * m.speed;
        m.alpha -= 0.012;
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
    <section className="relative py-12 md:py-16 px-4 z-10" data-testid="home-solena-section"
      style={{
        background: 'rgba(12, 17, 32, 0.55)',
      }}>
      <div className="max-w-6xl mx-auto">

        {/* === SOLENA SECTION — La voix de Plume Astrale === */}
        <div className="max-w-5xl mx-auto">
          {/* Bloc "Votre vie change" deplace depuis le hero */}
          <div style={{ maxWidth: 720, marginLeft: 'auto', marginRight: 'auto', marginBottom: 40, textAlign: 'center' }} data-testid="hero-positioning-text"><h2 style={{ fontFamily: 'Cinzel, Playfair Display, Cormorant Garamond, serif', fontWeight: 400, fontSize: 'clamp(1.2rem, 2.6vw, 1.85rem)', lineHeight: 1.25, letterSpacing: '0.02em', color: '#E8C766', textShadow: '0 2px 30px rgba(0,0,0,0.95)', marginBottom: 12 }}>Votre vie change. Comprenez pourquoi.</h2><p style={{ fontFamily: 'Inter, sans-serif', fontSize: 'clamp(0.9rem, 1.2vw, 1.05rem)', fontWeight: 300, lineHeight: 1.7, color: '#CBD5E1', textShadow: '0 2px 20px rgba(0,0,0,0.9)', margin: 0 }}>Découvrez les périodes qui favorisent l'amour, les opportunités et les grands tournants de votre parcours.</p></div>
          
          {/* Tagline + Header + Intro */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6"
              style={{ background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.30)' }}>
              <Sparkles style={{ width: 12, height: 12, color: '#D4AF37' }} strokeWidth={1.5} />
              <span className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.3em', fontWeight: 400 }}>
                {SOLENA.tagline}
              </span>
            </div>

            <h2 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontWeight: 200,
              fontSize: 'clamp(2.5rem, 6vw, 4rem)',
              lineHeight: 1.1,
              color: '#F4E8D2',
              marginBottom: 20,
            }}>
              Je suis <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>Solena</em>.
            </h2>

            <p style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 'clamp(1rem, 2vw, 1.25rem)',
              color: 'rgba(244,232,210,0.85)',
              lineHeight: 1.7,
              maxWidth: '800px',
              margin: '0 auto 28px',
            }}>
              {SOLENA.bio_short}
            </p>

            {/* Portrait */}
            <div className="mb-16 flex justify-center">
              <div style={{ maxWidth: '380px', width: '100%' }}>
                <img src={SOLENA.portrait} alt="Portrait de Solena — astrologue"
                  loading="lazy"
                  style={{
                    width: '100%',
                    height: 'auto',
                    aspectRatio: '9/16',
                    objectFit: 'cover',
                    objectPosition: 'center 20%',
                    borderRadius: '16px',
                    border: '2px solid rgba(212,175,55,0.35)',
                    boxShadow: '0 40px 100px rgba(212,175,55,0.15)',
                    display: 'block',
                  }} />
              </div>
            </div>
          </div>

          {/* === MA MISSION === */}
          <div className="mb-24">
            <div className="text-center mb-12">
              <p className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.3em', marginBottom: 12, fontWeight: 400 }}>
                Ma mission
              </p>
              <h3 style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontWeight: 200,
                fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
                color: '#F4E8D2',
                lineHeight: 1.2,
              }}>
                Une <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>conversation intime</em><br />
                avec ton ciel de naissance.
              </h3>
            </div>

            <div className="space-y-6 text-base md:text-lg leading-relaxed" style={{ color: 'rgba(244,232,210,0.85)', maxWidth: '900px', margin: '0 auto' }}>
              {SOLENA.bio_long.map((p, i) => (
                <p key={i} style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 400, lineHeight: 1.8 }}>
                  {p}
                </p>
              ))}
            </div>
          </div>

          {/* === MES SPÉCIALITÉS === (retiré — dilution du positionnement.
                Les 6 services restent accessibles via le menu.
                Remplacé par la section HomeCreditPacks juste après cette section.) */}

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
            Discuter avec Soléna
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
          </button>
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
        </>
      )}
      <HomeCreditPacks />
      <SolenaJourney />
      <ClientReviews />

      {/* ═══ Vitrine Rapports Prestige ═══ */}
      <section className="py-16 px-4 relative z-10" style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }} data-testid="prestige-showcase">
        <div className="max-w-5xl mx-auto">
          <p className="text-[10px] uppercase mb-3 text-center" style={{ color: '#D4AF37', letterSpacing: '0.3em', fontFamily: 'Cinzel, serif' }}>
            ✦ Éditions Prestige ✦
          </p>
          <h2 className="text-center mb-10" style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, fontSize: 'clamp(26px, 4vw, 40px)', color: '#F5EEE0' }}>
            Des documents <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>à garder toute une vie</em>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {[
              {
                to: '/pack-karmique',
                badge: 'LE PLUS COMPLET',
                title: 'Pack Karmique + Kabbale',
                price: '89€',
                desc: 'Ta mémoire karmique (80 sections) + ton Arbre de Vie + une synthèse croisée rédigée pour toi. PDF ~40 pages.',
                featured: true,
                testid: 'showcase-pack-karmique',
              },
              {
                to: '/kabbale',
                badge: null,
                title: 'Ton Arbre de Vie Kabbalistique',
                price: '39€',
                desc: 'Les 10 Sephiroth et 22 chemins de ton thème natal, décodés en français. PDF 15 pages.',
                featured: false,
                testid: 'showcase-kabbale',
              },
              {
                to: '/rencontres-astrales',
                badge: null,
                title: 'Compatibilité Ultime',
                price: '29,99€',
                desc: 'Votre synastrie sur 12 domaines de vie + tes fenêtres de rencontre. PDF 20 pages.',
                featured: false,
                testid: 'showcase-compat-ultime',
              },
            ].map((card) => (
              <Link
                key={card.to}
                to={card.to}
                data-testid={card.testid}
                className="block p-6 rounded-2xl transition-transform duration-300 hover:-translate-y-1"
                style={{
                  background: card.featured ? 'rgba(212,175,55,0.10)' : 'rgba(26,32,53,0.55)',
                  border: card.featured ? '1px solid rgba(212,175,55,0.45)' : '1px solid rgba(212,175,55,0.15)',
                  textDecoration: 'none',
                  boxShadow: card.featured ? '0 0 32px rgba(212,175,55,0.15)' : 'none',
                }}
              >
                {card.badge && (
                  <span className="inline-block text-[9px] uppercase mb-3 px-2 py-1 rounded-full" style={{ background: '#D4AF37', color: '#111625', letterSpacing: '0.2em', fontWeight: 700 }}>
                    {card.badge}
                  </span>
                )}
                <h3 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, color: '#F5EEE0', fontWeight: 400, marginBottom: 6 }}>
                  {card.title}
                </h3>
                <div style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 30, color: '#D4AF37', fontWeight: 300, marginBottom: 10 }}>
                  {card.price}
                </div>
                <p className="text-sm" style={{ color: 'rgba(244,232,210,0.7)', lineHeight: 1.6 }}>{card.desc}</p>
                <span className="inline-block mt-4 text-[11px] uppercase" style={{ color: '#E8C766', letterSpacing: '0.2em' }}>
                  Découvrir →
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Trust badge — technologie */}
      <section className="py-12 px-4 relative z-10" style={{ borderTop: '1px solid rgba(212,175,55,0.08)' }} data-testid="trust-astrology-api">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[10px] uppercase mb-4" style={{ color: 'rgba(244,232,210,0.5)', letterSpacing: '0.25em' }}>
            Technologie de confiance
          </p>
          <p className="text-base mb-3" style={{ color: 'rgba(244,232,210,0.85)', fontFamily: 'Cormorant Garamond, serif', fontSize: 22, lineHeight: 1.4 }}>
            Calculs astrologiques de précision professionnelle : éphémérides, transits et aspects planétaires calculés à partir de vos coordonnées de naissance réelles.
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
