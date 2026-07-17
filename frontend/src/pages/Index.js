import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Hero3D from '../components/Hero3D';
import SolenaChat from '../components/SolenaChat';
import TestimonialsMarquee from '../components/design/TestimonialsMarquee';
import JabInteractif from '../components/design/JabInteractif';
import FloatingReviews from '../components/design/FloatingReviews';
import { SectionTransition, FadeInUp } from '../components/design/Motion';
import {
  Sparkles, ArrowRight, CheckCircle2
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

/* ═══════════════════════════════════════════════════════════
   BRAND STORY — Le Sanctuaire Plume Astrale
═══════════════════════════════════════════════════════════ */
const BrandStory = () => (
  <section className="relative py-16 md:py-20 px-4 z-10" data-testid="home-brand-story">
    <div className="max-w-3xl mx-auto text-center">
      <p className="text-[10px] uppercase mb-5" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontWeight: 400 }}>
        ✦ Le Sanctuaire ✦
      </p>
      <h2 style={{
        fontFamily: 'Cormorant Garamond, serif',
        fontWeight: 200,
        fontSize: 'clamp(1.9rem, 4.5vw, 3rem)',
        lineHeight: 1.12,
        color: '#F5EEE0',
        marginBottom: 20,
      }}>
        Le Sanctuaire <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>Plume Astrale</em>
      </h2>
      <p className="text-base md:text-lg mx-auto max-w-2xl mb-5" style={{
        fontFamily: 'Cormorant Garamond, serif',
        color: 'rgba(244,232,210,0.90)',
        lineHeight: 1.7,
        fontStyle: 'italic',
        fontSize: '1.15rem',
      }}>
        Un coaching céleste de haute précision pour éclairer votre trajectoire.
      </p>
      <p className="text-base mx-auto max-w-2xl mb-5" style={{
        fontFamily: 'Cormorant Garamond, serif',
        color: 'rgba(244,232,210,0.78)',
        lineHeight: 1.75,
      }}>
        Plume Astrale s&apos;impose par la <em style={{ color: '#E8C766', fontStyle: 'italic' }}>rigueur scientifique</em> de ses calculs d&apos;éphémérides et le sérieux de sa charte déontologique.
        Conçu comme un véritable coach de vie spirituel et émotionnel, notre espace est <em style={{ color: '#E8C766', fontStyle: 'italic' }}>universel</em> :
        il accompagne n&apos;importe qui, peu importe votre parcours, là où vous en êtes aujourd&apos;hui.
      </p>
      <p className="text-base mx-auto max-w-2xl" style={{
        fontFamily: 'Cormorant Garamond, serif',
        color: 'rgba(244,232,210,0.78)',
        lineHeight: 1.75,
      }}>
        Ici, vous ne trouverez ni horoscope générique, ni prédiction fataliste. Vous entamez une
        <em style={{ color: '#E8C766', fontStyle: 'italic' }}> conversation intime et sur-mesure </em>
        avec votre ciel de naissance, guidé par la voix et l&apos;expertise de <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>Solena</em>.
      </p>
      <div className="mt-8 text-[10px] md:text-xs uppercase" style={{ color: '#D4AF37', letterSpacing: '0.28em', fontFamily: 'Cinzel, serif' }}>
        ✦ Rigueur des calculs&nbsp;·&nbsp;Charte de sérieux&nbsp;·&nbsp;Accompagnement universel ✦
      </div>
    </div>
  </section>
);

/* ═══════════════════════════════════════════════════════════
   SOLENA JOURNEY — parcours storytelling + chat inline
═══════════════════════════════════════════════════════════ */
const SolenaJourney = () => {
  return (
    <section className="relative py-24 md:py-32 px-4 z-10" data-testid="home-solena-section"
      style={{
        background: 'linear-gradient(180deg, transparent 0%, rgba(20,15,40,0.4) 30%, rgba(20,15,40,0.4) 70%, transparent 100%)',
      }}>
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
            color: '#F5EEE0',
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

          {/* Colonne portrait — 2/5 (portrait mystique unique, plus de vidéos) */}
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
                background: '#111625',
              }}>
                <img
                  src={SOLENA.portrait}
                  alt="Portrait de Solena, astrologue Plume Astrale"
                  loading="lazy"
                  style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 20%', display: 'block' }}
                  data-testid="home-solena-portrait"
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
            <Link to="/solena" className="plume-btn-secondary" data-testid="home-solena-discover-btn">
              Découvrir l&apos;univers de Solena
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
            </Link>
            <Link to="/archetype" className="plume-btn-primary" data-testid="home-archetype-cta">
              Découvre ton archétype
              <span style={{ fontSize: 10, marginLeft: 4, opacity: 0.75 }}>15 cr</span>
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
            </Link>
            <Link to="/kabbale" className="plume-btn-primary" data-testid="home-kabbale-cta">
              Ton Arbre de Vie
              <span style={{ fontSize: 10, marginLeft: 4, opacity: 0.75 }}>39€</span>
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
            </Link>
          </div>
        </div>

      </div>
    </section>
  );
};

/* ═══════════════════════════════════════════════════════════
   CLIENT REVIEWS — remplacé par FloatingReviews (composant dédié).
   Legacy code supprimé pour DRY.
═══════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   VITRINE DES SERVICES — visible juste sous le hero
═══════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   VITRINE DES SERVICES — visible juste sous le hero
═══════════════════════════════════════════════════════════ */
const ServicesShowcase = () => {
  const services = [
    { to: '/archetype', badge: '15 crédits', title: 'Ton Archétype', desc: 'Ton portrait jungien — 3 archétypes dominants + ton ombre.', icon: '✧' },
    { to: '/tirage-tarot', badge: 'Dès 5 cr', title: 'Tirage de Tarot', desc: 'Oui/Non, croix celtique, tirage médium — 22 arcanes majeurs.', icon: '◆' },
    { to: '/kabbale', badge: '39€ · PDF', title: 'Ton Arbre de Vie', desc: 'Kabbale personnalisée · 10 Sephiroth + 22 chemins · PDF 15 pages.', icon: '✦', featured: true },
    { to: '/compatibilite', badge: '10 crédits', title: 'Compatibilité astrale', desc: 'Analyse de synastrie complète pour ton couple actuel ou à venir.', icon: '◈' },
  ];
  return (
    <section className="py-20 px-4 relative z-10" data-testid="home-services-showcase" style={{
      background: 'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(212,175,55,0.045), transparent 70%)'
    }}>
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.32em', fontFamily: 'Cinzel, serif' }}>
            ✦ Ton sanctuaire ✦
          </p>
          <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontWeight: 300, lineHeight: 1.1, fontSize: 'clamp(30px, 4.5vw, 46px)', color: '#F5EEE0', marginBottom: 12 }}>
            Choisis ta première <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>révélation</em>
          </h2>
          <p className="text-base max-w-xl mx-auto" style={{ color: 'rgba(227,215,255,0.7)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic', lineHeight: 1.6 }}>
            Quatre portes d&apos;entrée pour éclairer ce qui t&apos;appelle aujourd&apos;hui.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((s, i) => (
            <Link key={i} to={s.to}
              className={`${s.featured ? 'plume-glass-featured' : 'plume-glass'} p-6 group transition-transform duration-400 ease-plume-silk hover:-translate-y-1 block`}
              data-testid={`showcase-${s.to.slice(1)}`}>
              <div className="flex items-start justify-between mb-4">
                <span style={{ fontSize: 26, color: '#D4AF37', fontFamily: 'Cinzel, serif' }}>{s.icon}</span>
                <span className="text-[10px] uppercase px-2 py-1 rounded-full" style={{
                  background: s.featured ? 'rgba(212,175,55,0.15)' : 'rgba(227,215,255,0.06)',
                  color: s.featured ? '#D4AF37' : 'rgba(227,215,255,0.7)',
                  border: `1px solid ${s.featured ? 'rgba(212,175,55,0.4)' : 'rgba(227,215,255,0.15)'}`,
                  letterSpacing: '0.12em',
                }}>{s.badge}</span>
              </div>
              <h3 className="text-xl mb-2" style={{ fontFamily: 'Cormorant Garamond, serif', color: '#F5EEE0', fontWeight: 400 }}>
                {s.title}
              </h3>
              <p className="text-sm mb-4" style={{ color: 'rgba(227,215,255,0.72)', lineHeight: 1.55 }}>
                {s.desc}
              </p>
              <span className="inline-flex items-center gap-1 text-xs uppercase group-hover:gap-2 transition-all" style={{ color: '#D4AF37', letterSpacing: '0.2em', fontFamily: 'Cinzel, serif' }}>
                Découvrir <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ═══════════════════════════════════════════════════════════
   PAGE
═══════════════════════════════════════════════════════════ */
const Index = () => {
  return (
    <div className="relative" style={{ overflow: 'hidden', background: '#111625' }}>
      <SEO path="/" />
      <CosmicCanvas />
      <Hero3D />
      <SectionTransition height={80} />
      <TestimonialsMarquee />
      <SectionTransition height={100} />
      <FadeInUp>
        <JabInteractif />
      </FadeInUp>
      <SectionTransition height={100} />
      <FadeInUp>
        <ServicesShowcase />
      </FadeInUp>
      <SectionTransition height={100} />
      <FadeInUp>
        <BrandStory />
      </FadeInUp>
      <SectionTransition height={100} />
      <SolenaJourney />
      <SectionTransition height={100} />
      <FloatingReviews />

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
