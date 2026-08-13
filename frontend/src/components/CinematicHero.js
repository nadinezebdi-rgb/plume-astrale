import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * CinematicHero — Hero cinématographique · image full-bleed.
 *
 * Visuel : silhouette de femme en robe rouge face à une pleine lune, nuages
 * lumineux et envolée d'oiseaux. Universel, contemplatif, sans portrait
 * frontal — parfait pour incarner "comprendre les périodes de sa vie".
 *
 * Composition :
 *   • Image de fond en cover, ancrée haute pour garder ciel + lune
 *   • Voile bleu nuit dégradé pour lisibilité de la typo
 *   • Copy éditorial centré (H1, subtitle, CTA)
 *   • Scroll indicator discret
 */
const HERO_IMAGE = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/kl8cl3tc_femme%20face%20%C3%A0%20la%20lune.png';

export default function CinematicHero() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Préchargement pour éviter le flash pendant que l'image charge
    const img = new Image();
    img.src = HERO_IMAGE;
    const t = setTimeout(() => setVisible(true), 120);
    return () => clearTimeout(t);
  }, []);

  return (
    <section
      data-testid="cinematic-hero"
      style={{
        position: 'relative',
        minHeight: 'min(100vh, 820px)',
        overflow: 'hidden',
        background: '#0A1128',
        color: '#F7F5F0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Layer 1 · Image de fond cinématique */}
      <div
        aria-hidden="true"
        className="ch-bg"
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url("${HERO_IMAGE}")`,
          backgroundSize: 'cover',
          backgroundPosition: 'center 30%',
          backgroundRepeat: 'no-repeat',
          zIndex: 1,
          opacity: visible ? 1 : 0,
          transform: visible ? 'scale(1)' : 'scale(1.04)',
          transition: 'opacity 1600ms ease, transform 3600ms cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      />

      {/* Layer 2 · Voile de lisibilité — dégradé du bas vers le haut */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 2,
          background: `
            linear-gradient(180deg,
              rgba(10, 17, 40, 0.62) 0%,
              rgba(10, 17, 40, 0.30) 30%,
              rgba(10, 17, 40, 0.45) 60%,
              rgba(10, 17, 40, 0.88) 100%
            ),
            radial-gradient(ellipse at 50% 40%, rgba(10, 17, 40, 0) 0%, rgba(10, 17, 40, 0.35) 70%)
          `,
        }}
      />

      {/* Layer 3 · Copy éditorial */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          textAlign: 'center',
          padding: '120px 24px 200px',
          maxWidth: 820,
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 1600ms 500ms ease, transform 1600ms 500ms cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            fontWeight: 500,
            letterSpacing: '0.4em',
            textTransform: 'uppercase',
            color: 'rgba(184, 147, 90, 0.95)',
            marginBottom: 32,
            textShadow: '0 2px 12px rgba(10, 17, 40, 0.8)',
          }}
        >
          Plume Astrale
        </p>

        <h1
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2.4rem, 5.5vw, 4.6rem)',
            fontWeight: 400,
            letterSpacing: '-0.01em',
            lineHeight: 1.12,
            color: '#F7F5F0',
            marginBottom: 32,
            textShadow: '0 4px 32px rgba(10, 17, 40, 0.85)',
          }}
        >
          Comprendre les <em style={{ fontStyle: 'italic', color: '#C9A24B' }}>périodes</em> de votre&nbsp;vie.
        </h1>

        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(15px, 1.4vw, 18px)',
            lineHeight: 1.65,
            color: 'rgba(247, 245, 240, 0.90)',
            maxWidth: 560,
            margin: '0 auto 48px',
            textShadow: '0 2px 16px rgba(10, 17, 40, 0.8)',
          }}
        >
          Une lecture personnalisée pour vous aider à mieux comprendre
          les grands moments de votre parcours.
        </p>

        <Link
          to="/decouvrir"
          data-testid="cinematic-hero-cta"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            padding: '18px 40px',
            borderRadius: 999,
            background: '#B8935A',
            color: '#0A1128',
            fontFamily: 'Inter, sans-serif',
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            textDecoration: 'none',
            transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
            boxShadow: '0 12px 32px rgba(184, 147, 90, 0.45)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#C9A24B';
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 16px 40px rgba(184, 147, 90, 0.6)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#B8935A';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 12px 32px rgba(184, 147, 90, 0.45)';
          }}
        >
          Découvrir mon parcours
          <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
        </Link>
      </div>

      {/* Layer 4 · Scroll indicator */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 32,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
          opacity: visible ? 0.7 : 0,
          transition: 'opacity 2000ms 1400ms ease',
        }}
      >
        <div
          style={{
            width: 1,
            height: 48,
            background: 'linear-gradient(180deg, transparent, #B8935A, transparent)',
            animation: 'scrollHint 2.4s ease-in-out infinite',
          }}
        />
      </div>

      <style>{`
        @keyframes scrollHint {
          0%, 100% { opacity: 0.3; transform: translateY(0); }
          50%      { opacity: 0.95; transform: translateY(6px); }
        }
        /* Mobile portrait 9:16 — image carrée 1024x1024 : on doit garder
           à la fois la lune (haut) et la silhouette (bas). Astuces :
           - background-size: contain-then-cover en gardant width 100%
           - background-position en pourcentage bien calibré
           - Hauteur de section réduite pour laisser respirer la compo */
        @media (max-width: 640px) {
          [data-testid="cinematic-hero"] {
            min-height: min(92vh, 720px) !important;
          }
          .ch-bg {
            /* On zoome légèrement + décale pour cadrer moon + silhouette */
            background-size: 175% auto !important;
            background-position: 50% 22% !important;
          }
        }
        @media (max-width: 400px) {
          .ch-bg {
            background-size: 210% auto !important;
            background-position: 50% 18% !important;
          }
        }
      `}</style>
    </section>
  );
}
