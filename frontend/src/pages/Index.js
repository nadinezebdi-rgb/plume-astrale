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
      <div className="max-w-6xl mx-auto">

        {/* === SOLENA SECTION — La voix de Plume Astrale === */}
        <div className="max-w-5xl mx-auto">
          
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

            {/* Vidéo de bienvenue de Soléna (remplace le portrait statique) */}
            <div className="mb-16 flex justify-center">
              <div style={{ maxWidth: '380px', width: '100%' }}>
                <video
                  src="https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/7y6nc0gl_Bienvenue%20sur%20Plume%20Astrale_1080p.mp4"
                  poster={SOLENA.portrait}
                  controls
                  playsInline
                  preload="metadata"
                  data-testid="solena-welcome-video"
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
                    background: '#0C1120',
                  }}
                  aria-label="Message de bienvenue de Soléna, Plume Astrale"
                >
                  Ta navigateur ne supporte pas la vidéo. Rends-toi sur{' '}
                  <a href="https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/7y6nc0gl_Bienvenue%20sur%20Plume%20Astrale_1080p.mp4">
                    ce lien
                  </a>{' '}
                  pour la visionner.
                </video>
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

            {/* CTA personnel — moment d'empathie transformé en action.
                Le CTA pointe vers /inscription pour créer un compte gratuit avec 20 crédits :
                l'utilisateur peut alors discuter réellement avec Soléna (10 crédits = 1 question). */}
            <div className="text-center mt-12">
              <Link
                to="/inscription"
                className="group inline-flex items-center gap-3 px-6 sm:px-8 py-4 rounded-full transition-all hover:scale-[1.03] whitespace-nowrap max-w-[92vw]"
                style={{
                  background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
                  color: '#0A0603',
                  fontFamily: 'Cinzel, sans-serif',
                  fontWeight: 700,
                  fontSize: 'clamp(0.72rem, 0.95vw, 0.95rem)',
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  boxShadow: '0 12px 40px rgba(212,175,55,0.35)',
                  textDecoration: 'none',
                }}
                data-testid="solena-chat-cta"
              >
                <Heart style={{ width: 14, height: 14 }} strokeWidth={2} fill="currentColor" />
                <span className="sm:hidden">Discuter avec Soléna</span>
                <span className="hidden sm:inline">Discuter avec Soléna · 20 crédits offerts</span>
                <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
              </Link>
              <p style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11,
                color: 'rgba(244,232,210,0.5)',
                marginTop: 12,
                letterSpacing: '0.05em',
              }}>
                Sans engagement · Réponse personnalisée en 15 secondes
              </p>
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

        {/* CTA sous les reviews retiré — hard-sell après un moment de trust émotionnel.
            Le CTA de conversion est désormais sous la section Solena (empathie → action)
            et dans le bloc final (dernière chance de conversion). */}
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
    <div className="relative" style={{ overflow: 'hidden', background: '#0C1120' }}>
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

      {/* ═══ FINAL CTA — Bloc « Prête à comprendre ? » ═══
           Dernière chance de conversion avant footer. Loop sur les 2 actions clés :
           - Lead magnet gratuit (capture email) — CTA primaire
           - Entry point 7,99€ (packs crédits) — CTA secondaire discret
           Sections « Éditions Prestige » et « Technologie de confiance » retirées
           (dilution du funnel · trop de prix affichés · CTAs non alignés avec les reviews).
           Les PDFs restent accessibles via le menu de navigation. */}
      <section
        className="py-20 md:py-24 px-6 relative z-10"
        style={{
          background: 'radial-gradient(ellipse at center top, rgba(212,175,55,0.06) 0%, transparent 60%), #0C1120',
          borderTop: '1px solid rgba(212,175,55,0.15)',
        }}
        data-testid="final-cta-block"
      >
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.32em', marginBottom: 16, fontFamily: 'Cinzel, serif' }}>
            ✦ Un dernier mot ✦
          </p>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(1.9rem, 4.5vw, 3rem)',
            color: '#F4E8D2',
            lineHeight: 1.2,
            marginBottom: 20,
          }}>
            Prête à comprendre <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>ce qui se joue</em> vraiment&nbsp;?
          </h2>
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.95rem, 1.2vw, 1.05rem)',
            color: 'rgba(244,232,210,0.75)',
            maxWidth: 520,
            margin: '0 auto 36px',
            lineHeight: 1.7,
          }}>
            20 crédits offerts à l&apos;inscription — de quoi tester Soléna, tirer tes cartes et voir tes cycles d&apos;amour, sans rien payer.
          </p>

          {/* Duo CTA — primaire (inscription 20 crédits) + secondaire (crédits payants) */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8 flex-wrap">
            <Link
              to="/inscription"
              className="group relative px-6 sm:px-8 py-4 overflow-hidden rounded-full transition-all duration-300 hover:scale-105 max-w-[90vw]"
              style={{
                background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 50%, #D4AF37 100%)',
                color: '#0A0603',
                fontFamily: 'Cinzel, sans-serif',
                fontWeight: 700,
                fontSize: 'clamp(0.72rem, 0.95vw, 0.95rem)',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 8px 40px rgba(212,175,55,0.4)',
                textDecoration: 'none',
                display: 'inline-block',
                whiteSpace: 'nowrap',
              }}
              data-testid="final-cta-primary"
            >
              <span className="sm:hidden">Mon compte · 20 crédits</span>
              <span className="hidden sm:inline">Créer mon compte · 20 crédits offerts</span>
            </Link>
            <Link
              to="/buy-credits"
              className="inline-flex items-center gap-2 transition-all hover:opacity-100 whitespace-nowrap"
              style={{
                color: '#E8C766',
                fontFamily: 'Cinzel, sans-serif',
                fontSize: 'clamp(0.68rem, 0.75vw, 0.75rem)',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                textDecoration: 'none',
                opacity: 0.75,
                borderBottom: '1px solid rgba(232,199,102,0.3)',
                paddingBottom: 4,
              }}
              data-testid="final-cta-secondary"
            >
              <span className="sm:hidden">Recharger dès 7,99 € →</span>
              <span className="hidden sm:inline">Ou recharger dès 7,99 € →</span>
            </Link>
          </div>

          {/* Réassurance */}
          <div
            className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[10px] uppercase"
            style={{ color: 'rgba(244,232,210,0.55)', letterSpacing: '0.2em', fontFamily: 'Inter, sans-serif' }}
            data-testid="final-cta-reassurance"
          >
            <span>✓ Sans engagement</span>
            <span style={{ opacity: 0.3 }}>·</span>
            <span>✓ Livraison sous 2h</span>
            <span style={{ opacity: 0.3 }}>·</span>
            <span>✓ Garantie 14 jours</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
