import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Crown } from 'lucide-react';
import SEO from '@/components/SEO';

const HERO_IMAGE = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/kl8cl3tc_femme%20face%20%C3%A0%20la%20lune.png';

/**
 * Manifesto de Plume Astrale — page cinématique en 3 chapitres.
 *
 * Positionnement : renforce l'aura premium de la marque en racontant
 * la vision fondatrice sans concession. Style Hermès / Apple / Airbnb :
 * respiration, typographie éditoriale, révélations au scroll.
 *
 * Trois chapitres :
 *   I. Pourquoi Plume Astrale existe (le constat)
 *   II. Ce que nous croyons (la conviction)
 *   III. Ce que nous offrons (la promesse)
 */

const CHAPTERS = [
  {
    number: 'I',
    kicker: 'Le constat',
    title: 'La vie n\'est pas un problème à résoudre.',
    subtitle: 'C\'est une matière à comprendre.',
    body: [
      'Nous avons été éduqués à faire — plus, plus vite, plus efficacement. À planifier, à optimiser, à cocher.',
      'Mais tout ce qui compte vraiment échappe à cette logique : les rencontres qui bousculent, les cycles qui reviennent, les décisions qu\'aucun tableau ne peut trancher.',
      'Devant ces moments-là, on cherche autre chose : un langage capable d\'accueillir la nuance, la durée, l\'invisible.',
    ],
    quote: 'Nous n\'avons pas besoin de plus d\'informations. Nous avons besoin de meilleures perspectives.',
  },
  {
    number: 'II',
    kicker: 'La conviction',
    title: 'Les cycles ne sont pas des prédictions.',
    subtitle: 'Ce sont des repères.',
    body: [
      'Nous croyons que chaque vie traverse des grandes périodes — des vagues qui reviennent, des tournants qui ressemblent à d\'autres, des seuils qu\'il faut apprendre à reconnaître.',
      'L\'astrologie, la numérologie, la kabbale : ce ne sont pas des oracles. Ce sont des cartes. Elles n\'annoncent rien — elles éclairent ce qui, en vous, cherche à se dire.',
      'À vous, ensuite, de décider. Nous ne remplaçons pas votre discernement. Nous lui offrons un langage plus vaste.',
    ],
    quote: 'Le ciel n\'écrit pas votre histoire. Il en donne la trame — vous composez la mélodie.',
  },
  {
    number: 'III',
    kicker: 'La promesse',
    title: 'Un objet précieux pour vous accompagner.',
    subtitle: 'À lire lentement. À garder longtemps.',
    body: [
      'Chaque lecture Plume Astrale est calculée à partir de vos données de naissance exactes — pas d\'un horoscope générique par signe. Votre ciel, votre texte, votre livre.',
      'Nous écrivons dans un français choisi, éditorial, sans jargon. La beauté vient du mot juste, pas de la décoration.',
      'Vous recevez un PDF premium à télécharger, à imprimer si vous le souhaitez, à relire trois fois. Une conversation intime avec ce qui vous porte, à conserver comme on garde un livre qui compte.',
    ],
    quote: 'Comprendre les périodes de votre vie — pour traverser ce qui vient avec plus de justesse.',
  },
];

export default function Manifesto() {
  const chapterRefs = useRef([]);
  const [visibleChapters, setVisibleChapters] = useState([false, false, false]);
  const [ch3ParallaxY, setCh3ParallaxY] = useState(0);

  useEffect(() => {
    const observers = chapterRefs.current.map((el, i) => {
      if (!el) return null;
      const obs = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setVisibleChapters((prev) => {
              const copy = [...prev];
              copy[i] = true;
              return copy;
            });
            obs.disconnect();
          }
        },
        { threshold: 0.18 },
      );
      obs.observe(el);
      return obs;
    });
    return () => observers.forEach((o) => o && o.disconnect());
  }, []);

  // Parallax 0.3x sur le fond du Chapitre III uniquement (perf : rAF + délégation scroll)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mq.matches) return;
    let raf = null;
    const onScroll = () => {
      if (raf !== null) return;
      raf = requestAnimationFrame(() => {
        const el = chapterRefs.current[2]; // Chapitre III
        if (el) {
          const rect = el.getBoundingClientRect();
          // Décalage relatif au centre du viewport pour un effet symétrique
          const centerOffset = rect.top + rect.height / 2 - window.innerHeight / 2;
          setCh3ParallaxY(-centerOffset * 0.3);
        }
        raf = null;
      });
    };
    // 1er run pour position initiale
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      if (raf !== null) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div
      data-testid="manifesto-page"
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #0A1128 0%, #0F1A3C 50%, #0A1128 100%)',
        color: '#F7F5F0',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <SEO
        path="/manifesto"
        title="Manifesto · La vision Plume Astrale"
        description="Trois chapitres pour comprendre pourquoi Plume Astrale existe, ce que nous croyons, et ce que nous vous offrons. Une lecture cinématique du positionnement de la marque."
      />

      {/* Champ d'étoiles décoratif */}
      <div aria-hidden="true" style={{ position: 'fixed', inset: 0, pointerEvents: 'none', zIndex: 0 }}>
        {[...Array(60)].map((_, i) => {
          const size = 1 + Math.random() * 2;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                width: size,
                height: size,
                background: '#F7F5F0',
                borderRadius: '50%',
                opacity: 0.12 + Math.random() * 0.35,
                boxShadow: '0 0 6px rgba(247, 245, 240, 0.5)',
              }}
            />
          );
        })}
      </div>

      {/* Hero */}
      <section
        data-testid="manifesto-hero"
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '120px 24px 80px',
          textAlign: 'center',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Lune dorée en arrière-plan */}
        <svg
          aria-hidden="true"
          viewBox="0 0 400 400"
          style={{
            position: 'absolute',
            top: '15%', left: '50%',
            transform: 'translateX(-50%)',
            width: 320, height: 320,
            opacity: 0.55,
            zIndex: -1,
          }}
        >
          <defs>
            <radialGradient id="man-moon" cx="0.42" cy="0.42" r="0.55">
              <stop offset="0%" stopColor="#F7F5F0" />
              <stop offset="55%" stopColor="#E8D9B4" />
              <stop offset="100%" stopColor="#B8935A" />
            </radialGradient>
            <radialGradient id="man-halo" cx="0.5" cy="0.5" r="0.5">
              <stop offset="0%" stopColor="rgba(184,147,90,0.32)" />
              <stop offset="100%" stopColor="rgba(184,147,90,0)" />
            </radialGradient>
          </defs>
          <circle cx="200" cy="200" r="180" fill="url(#man-halo)" />
          <circle cx="200" cy="200" r="90" fill="url(#man-moon)" opacity="0.88" />
        </svg>

        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11, fontWeight: 500,
            letterSpacing: '0.4em', textTransform: 'uppercase',
            color: 'rgba(184, 147, 90, 0.85)',
            marginBottom: 32,
          }}
        >
          Notre Manifesto
        </p>
        <h1
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2.6rem, 6vw, 4.8rem)',
            fontWeight: 400,
            lineHeight: 1.08,
            color: '#F7F5F0',
            marginBottom: 32,
            maxWidth: 900,
          }}
        >
          Nous ne prédisons pas votre vie.<br />
          <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>Nous en éclairons les périodes.</span>
        </h1>
        <p
          style={{
            fontFamily: 'Playfair Display, serif',
            fontStyle: 'italic',
            fontSize: 'clamp(17px, 1.8vw, 20px)',
            lineHeight: 1.6,
            color: 'rgba(247, 245, 240, 0.75)',
            maxWidth: 640,
            margin: '0 auto',
          }}
        >
          Une marque française de développement personnel qui utilise l&apos;astrologie
          comme un langage — pas comme un oracle.
        </p>

        {/* Scroll indicator */}
        <div
          aria-hidden="true"
          style={{
            marginTop: 80,
            width: 1, height: 60,
            background: 'linear-gradient(180deg, rgba(184, 147, 90, 0.6) 0%, transparent 100%)',
          }}
        />
      </section>

      {/* Chapters */}
      {CHAPTERS.map((ch, i) => {
        const isPromise = i === 2; // Chapitre III · La promesse — fond photo cinématique
        return (
        <section
          key={ch.number}
          ref={(el) => (chapterRefs.current[i] = el)}
          data-testid={`manifesto-chapter-${i + 1}`}
          style={{
            padding: isPromise ? '160px 24px 200px' : '120px 24px',
            maxWidth: isPromise ? '100%' : 900,
            margin: isPromise ? '0' : '0 auto',
            position: 'relative',
            zIndex: 1,
            opacity: visibleChapters[i] ? 1 : 0,
            transform: visibleChapters[i] ? 'translateY(0)' : 'translateY(40px)',
            transition: 'opacity 1.1s cubic-bezier(.22,.61,.36,1), transform 1.1s cubic-bezier(.22,.61,.36,1)',
            overflow: isPromise ? 'hidden' : 'visible',
          }}
        >
          {/* Fond photo cinématique — uniquement pour le chapitre III (parallax 0.3x) */}
          {isPromise && (
            <>
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute',
                  top: '-15%',
                  left: 0,
                  right: 0,
                  height: '130%',
                  backgroundImage: `url("${HERO_IMAGE}")`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center 40%',
                  backgroundRepeat: 'no-repeat',
                  opacity: visibleChapters[i] ? 0.55 : 0.35,
                  transform: `translate3d(0, ${ch3ParallaxY}px, 0)`,
                  transition: 'opacity 1.6s ease',
                  willChange: 'transform',
                  zIndex: -2,
                }}
              />
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute', inset: 0,
                  background: `linear-gradient(180deg,
                    rgba(15, 26, 60, 0.85) 0%,
                    rgba(15, 26, 60, 0.55) 25%,
                    rgba(15, 26, 60, 0.55) 75%,
                    rgba(15, 26, 60, 0.92) 100%
                  )`,
                  zIndex: -1,
                }}
              />
            </>
          )}
          {/* Numéro romain géant en filigrane */}
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              top: 40, left: '50%',
              transform: 'translateX(-50%)',
              fontFamily: 'Playfair Display, serif',
              fontSize: 220,
              lineHeight: 1,
              color: isPromise ? 'rgba(184, 147, 90, 0.10)' : 'rgba(184, 147, 90, 0.06)',
              fontStyle: 'italic',
              userSelect: 'none',
            }}
          >
            {ch.number}
          </div>

          <div style={{
            position: 'relative',
            textAlign: 'center',
            maxWidth: isPromise ? 900 : 'auto',
            margin: isPromise ? '0 auto' : 0,
          }}>
            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11, fontWeight: 500,
                letterSpacing: '0.32em', textTransform: 'uppercase',
                color: '#B8935A',
                marginBottom: 24,
                textShadow: isPromise ? '0 2px 12px rgba(15, 26, 60,0.85)' : 'none',
              }}
            >
              Chapitre {ch.number} · {ch.kicker}
            </p>
            <h2
              style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 'clamp(2rem, 4.2vw, 3.4rem)',
                fontWeight: 400,
                lineHeight: 1.15,
                color: '#F7F5F0',
                marginBottom: 16,
                textShadow: isPromise ? '0 4px 32px rgba(15, 26, 60,0.85)' : 'none',
              }}
            >
              {ch.title}
            </h2>
            <p
              style={{
                fontFamily: 'Playfair Display, serif',
                fontStyle: 'italic',
                fontSize: 'clamp(18px, 2vw, 22px)',
                color: '#C9A24B',
                marginBottom: 48,
                textShadow: isPromise ? '0 2px 20px rgba(15, 26, 60,0.85)' : 'none',
              }}
            >
              {ch.subtitle}
            </p>

            <div style={{ maxWidth: 640, margin: '0 auto', textAlign: 'left' }}>
              {ch.body.map((p, j) => (
                <p
                  key={j}
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 17,
                    lineHeight: 1.75,
                    color: 'rgba(247, 245, 240, 0.9)',
                    marginBottom: 20,
                    textShadow: isPromise ? '0 2px 12px rgba(15, 26, 60,0.6)' : 'none',
                  }}
                >
                  {p}
                </p>
              ))}
            </div>

            <blockquote
              style={{
                marginTop: 56,
                padding: '32px 40px',
                borderLeft: '2px solid #B8935A',
                textAlign: 'left',
                maxWidth: 620,
                marginLeft: 'auto',
                marginRight: 'auto',
                background: isPromise ? 'rgba(15, 26, 60, 0.40)' : 'transparent',
                backdropFilter: isPromise ? 'blur(6px)' : 'none',
                borderRadius: isPromise ? 4 : 0,
              }}
            >
              <p
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontStyle: 'italic',
                  fontSize: 'clamp(19px, 2.2vw, 24px)',
                  lineHeight: 1.5,
                  color: '#F7F5F0',
                  margin: 0,
                }}
              >
                « {ch.quote} »
              </p>
            </blockquote>
          </div>
        </section>
      );
      })}

      {/* Mini-CTA Cercle Soléna — bascule vers l'abonnement mensuel après Chapitre III */}
      <section
        data-testid="manifesto-cta-cercle"
        style={{
          padding: '80px 24px 20px',
          textAlign: 'center',
          position: 'relative',
          zIndex: 1,
          maxWidth: 720,
          margin: '0 auto',
        }}
      >
        <Link
          to="/cercle-solena"
          data-testid="manifesto-cta-cercle-link"
          style={{
            display: 'block',
            padding: '32px 36px',
            borderRadius: 20,
            background: 'linear-gradient(135deg, rgba(184,147,90,0.18) 0%, rgba(201,162,75,0.10) 60%, rgba(184,147,90,0.06) 100%)',
            border: '1px solid rgba(201,162,75,0.42)',
            textDecoration: 'none',
            color: '#F7F5F0',
            position: 'relative',
            overflow: 'hidden',
            transition: 'all 0.45s cubic-bezier(.22,.61,.36,1)',
            boxShadow: '0 0 40px rgba(201,162,75,0.10)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-3px)';
            e.currentTarget.style.borderColor = 'rgba(201,162,75,0.65)';
            e.currentTarget.style.boxShadow = '0 20px 60px rgba(201,162,75,0.20)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.borderColor = 'rgba(201,162,75,0.42)';
            e.currentTarget.style.boxShadow = '0 0 40px rgba(201,162,75,0.10)';
          }}
        >
          {/* Halo décoratif */}
          <div
            aria-hidden="true"
            style={{
              position: 'absolute',
              top: '-50%', left: '50%',
              transform: 'translateX(-50%)',
              width: 360, height: 360,
              background: 'radial-gradient(circle, rgba(201,162,75,0.25) 0%, transparent 70%)',
              pointerEvents: 'none',
            }}
          />
          <div style={{ position: 'relative' }}>
            <div
              style={{
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                width: 54, height: 54, borderRadius: '50%',
                background: 'rgba(201,162,75,0.20)',
                border: '1px solid rgba(201,162,75,0.55)',
                marginBottom: 20,
              }}
            >
              <Crown size={26} strokeWidth={1.5} style={{ color: '#C9A24B' }} />
            </div>
            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11, fontWeight: 500,
                letterSpacing: '0.32em', textTransform: 'uppercase',
                color: '#B8935A',
                margin: 0, marginBottom: 12,
              }}
            >
              Cercle Soléna · L&apos;abonnement mensuel
            </p>
            <p
              style={{
                fontFamily: 'Playfair Display, serif',
                fontStyle: 'italic',
                fontSize: 'clamp(20px, 2.6vw, 26px)',
                lineHeight: 1.35,
                color: '#F7F5F0',
                margin: 0, marginBottom: 14,
                maxWidth: 560,
                marginLeft: 'auto', marginRight: 'auto',
              }}
            >
              Recevoir ce type de lecture chaque mois — <span style={{ color: '#C9A24B' }}>14,99€</span>
            </p>
            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 14, lineHeight: 1.6,
                color: 'rgba(247,245,240,0.72)',
                margin: 0, marginBottom: 20,
                maxWidth: 500,
                marginLeft: 'auto', marginRight: 'auto',
              }}
            >
              50 crédits chat + un rapport mensuel personnalisé livré le 1er.
              Sans engagement, résiliable en un clic.
            </p>
            <span
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                fontFamily: 'Inter, sans-serif',
                fontSize: 12, fontWeight: 600,
                letterSpacing: '0.18em', textTransform: 'uppercase',
                color: '#C9A24B',
              }}
            >
              Découvrir le Cercle
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2.5} />
            </span>
          </div>
        </Link>
      </section>

      {/* ═══ Section « Soléna — la voix qui écrit vos lectures » ═══ */}
      <section
        data-testid="manifesto-about-solena"
        style={{
          position: 'relative',
          zIndex: 1,
          padding: 'clamp(96px, 12vw, 160px) 24px',
          borderTop: '1px solid rgba(201, 162, 75, 0.14)',
          borderBottom: '1px solid rgba(201, 162, 75, 0.14)',
        }}
      >
        <div style={{
          maxWidth: 1080,
          margin: '0 auto',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 420px) minmax(0, 1fr)',
          gap: 'clamp(40px, 6vw, 96px)',
          alignItems: 'center',
        }} className="ne-about-solena-grid">
          <figure
            style={{
              margin: 0,
              padding: 12,
              position: 'relative',
              background: 'linear-gradient(180deg, rgba(201,162,75,0.18) 0%, rgba(201,162,75,0.04) 100%)',
              borderRadius: 4,
              boxShadow: '0 32px 80px -20px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(201, 162, 75, 0.20)',
            }}
          >
            <picture>
              <source srcSet="/branding/solena-portrait-v2.webp" type="image/webp" />
              <img
                src="/branding/solena-portrait.png"
                alt="Illustration représentant Soléna, voix éditoriale IA de Plume Astrale"
                loading="lazy"
                decoding="async"
                data-testid="manifesto-about-solena-portrait"
                style={{
                  width: '100%', height: 'auto', display: 'block',
                  aspectRatio: '4 / 5',
                  objectFit: 'cover',
                  objectPosition: '50% 22%',
                  filter: 'saturate(0.94)',
                }}
              />
            </picture>
            <figcaption
              style={{
                marginTop: 14,
                textAlign: 'right',
                fontFamily: 'Inter, sans-serif',
                fontSize: 10,
                letterSpacing: '0.24em',
                textTransform: 'uppercase',
                color: '#C9A24B',
                fontWeight: 600,
              }}
            >
              Soléna &middot; voix éditoriale IA
            </figcaption>
          </figure>

          <div>
            <p
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11, fontWeight: 500,
                letterSpacing: '0.32em', textTransform: 'uppercase',
                color: '#B8935A',
                marginBottom: 24, marginTop: 0,
              }}
            >
              Soléna &middot; la voix qui écrit vos lectures
            </p>
            <h2
              style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 'clamp(2rem, 3.8vw, 2.8rem)',
                fontWeight: 400,
                lineHeight: 1.18,
                color: '#F7F5F0',
                margin: 0, marginBottom: 32,
                letterSpacing: '-0.01em',
              }}
            >
              Une intelligence éditoriale,<br />
              <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>pas un psy.</span>
            </h2>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 16, lineHeight: 1.75,
              color: 'rgba(247, 245, 240, 0.78)',
              maxWidth: 560,
            }}>
              <p style={{ margin: '0 0 20px 0' }}>
                <strong style={{ color: '#F7F5F0' }}>Soléna est une voix éditoriale conçue par Plume Astrale et propulsée par une intelligence artificielle</strong>.
                Elle n&apos;est ni une personne réelle, ni une astrologue diplômée, ni une voyante&nbsp;: c&apos;est
                une plume — un style d&apos;écriture, un ton, un vocabulaire — que nous avons composé pour traduire
                les données astrologiques en textes littéraires et bienveillants.
              </p>
              <p style={{ margin: '0 0 20px 0' }}>
                Concrètement, chaque commande utilise les positions planétaires calculées à partir de vos données
                exactes de naissance (Swiss Ephemeris) et un modèle de langage entraîné par notre équipe éditoriale
                pour produire <em style={{ color: '#E5D9BA' }}>votre édition unique</em>. Aucun texte pré-écrit,
                aucun copier-coller — chaque phrase est générée pour vous, puis mise en page dans un PDF prestige.
              </p>
              <p style={{ margin: 0, fontStyle: 'italic', color: 'rgba(247, 245, 240, 0.62)' }}>
                Nous préférons vous dire ceci franchement plutôt que d&apos;entretenir un mystère. La beauté du texte
                que vous recevrez suffit — pas besoin d&apos;y ajouter une fiction.
              </p>
            </div>
          </div>
        </div>
        <style>{`
          @media (max-width: 880px) {
            .ne-about-solena-grid {
              grid-template-columns: 1fr !important;
            }
          }
        `}</style>
      </section>

      {/* CTA final */}
      <section
        data-testid="manifesto-cta"
        style={{
          padding: '120px 24px 160px',
          textAlign: 'center',
          position: 'relative',
          zIndex: 1,
          maxWidth: 720,
          margin: '0 auto',
        }}
      >
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11, fontWeight: 500,
            letterSpacing: '0.32em', textTransform: 'uppercase',
            color: '#B8935A',
            marginBottom: 24,
          }}
        >
          Commencer votre lecture
        </p>
        <h2
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2rem, 4.2vw, 3.2rem)',
            fontWeight: 400,
            lineHeight: 1.15,
            color: '#F7F5F0',
            marginBottom: 40,
          }}
        >
          Une lecture personnalisée,<br />
          <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>rien qu&apos;à vous.</span>
        </h2>
        <Link
          to="/decouvrir"
          data-testid="manifesto-cta-button"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 14,
            padding: '18px 40px',
            borderRadius: 999,
            background: '#B8935A',
            color: '#0A1128',
            fontFamily: 'Inter, sans-serif',
            fontSize: 13, fontWeight: 600,
            letterSpacing: '0.16em', textTransform: 'uppercase',
            textDecoration: 'none',
            transition: 'all 0.4s cubic-bezier(.22,.61,.36,1)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#C9A24B';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#B8935A';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          Découvrir mon parcours
          <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
        </Link>
      </section>
    </div>
  );
}
