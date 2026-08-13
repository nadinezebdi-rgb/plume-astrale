import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
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
          {/* Fond photo cinématique — uniquement pour le chapitre III */}
          {isPromise && (
            <>
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute', inset: 0,
                  backgroundImage: `url("${HERO_IMAGE}")`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center 40%',
                  backgroundRepeat: 'no-repeat',
                  opacity: visibleChapters[i] ? 0.55 : 0.35,
                  transition: 'opacity 1.6s ease',
                  zIndex: -2,
                }}
              />
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute', inset: 0,
                  background: `linear-gradient(180deg,
                    rgba(10, 17, 40, 0.85) 0%,
                    rgba(10, 17, 40, 0.55) 25%,
                    rgba(10, 17, 40, 0.55) 75%,
                    rgba(10, 17, 40, 0.92) 100%
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
                textShadow: isPromise ? '0 2px 12px rgba(10,17,40,0.85)' : 'none',
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
                textShadow: isPromise ? '0 4px 32px rgba(10,17,40,0.85)' : 'none',
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
                textShadow: isPromise ? '0 2px 20px rgba(10,17,40,0.85)' : 'none',
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
                    textShadow: isPromise ? '0 2px 12px rgba(10,17,40,0.6)' : 'none',
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
                background: isPromise ? 'rgba(10, 17, 40, 0.40)' : 'transparent',
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
