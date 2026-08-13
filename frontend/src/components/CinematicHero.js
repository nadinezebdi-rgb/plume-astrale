import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * CinematicHero — Hero cinématographique, univers > personnalité.
 *
 * Univers visuel :
 *   • Fond bleu nuit profond avec radial glow doré
 *   • Champ d'étoiles procédural (canvas, 60 étoiles animées douces)
 *   • Lune dorée qui monte lentement (SVG + CSS transform)
 *   • Constellation stylisée en filigrane
 *   • Aucun portrait de Soléna
 *
 * Copy éditorial (repositionnement 2026-08) :
 *   H1 : « Comprendre les périodes de votre vie. »
 *   CTA : « Découvrir mon parcours »
 */
export default function CinematicHero() {
  const canvasRef = useRef(null);
  const [visible, setVisible] = useState(false);

  // Reveal animation on mount
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  // Starfield animation (soft twinkle)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W = canvas.width = canvas.offsetWidth;
    let H = canvas.height = canvas.offsetHeight;
    const stars = Array.from({ length: 90 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H * 0.85, // avoid ground area
      r: Math.random() * 1.4 + 0.3,
      phase: Math.random() * Math.PI * 2,
      speed: 0.005 + Math.random() * 0.008,
    }));
    let raf;
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      const t = performance.now() * 0.001;
      stars.forEach((s) => {
        const alpha = 0.35 + Math.sin(s.phase + t * s.speed * 100) * 0.35;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(247, 245, 240, ${Math.max(0.05, alpha)})`;
        ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    draw();
    const onResize = () => {
      W = canvas.width = canvas.offsetWidth;
      H = canvas.height = canvas.offsetHeight;
    };
    window.addEventListener('resize', onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
    };
  }, []);

  return (
    <section
      data-testid="cinematic-hero"
      style={{
        position: 'relative',
        minHeight: 'min(100vh, 780px)',
        overflow: 'hidden',
        background: 'radial-gradient(ellipse at 50% 120%, #1E2A5E 0%, #0F1A3C 35%, #0A1128 100%)',
        color: '#F7F5F0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Layer 1 · Starfield canvas */}
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 1,
        }}
      />

      {/* Layer 2 · Rising moon SVG */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          left: '50%',
          bottom: '-160px',
          transform: `translateX(-50%) translateY(${visible ? '0' : '80px'})`,
          transition: 'transform 3000ms cubic-bezier(0.16, 1, 0.3, 1)',
          zIndex: 2,
          opacity: visible ? 1 : 0,
          transitionProperty: 'transform, opacity',
          transitionDuration: '3000ms, 1600ms',
        }}
      >
        <svg width="720" height="720" viewBox="0 0 720 720" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <radialGradient id="moon-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#F5D896" stopOpacity="1" />
              <stop offset="40%" stopColor="#D4B369" stopOpacity="0.9" />
              <stop offset="70%" stopColor="#B8935A" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#B8935A" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="moon-body" cx="30%" cy="30%" r="70%">
              <stop offset="0%" stopColor="#FBF3DB" />
              <stop offset="55%" stopColor="#E8CC96" />
              <stop offset="100%" stopColor="#8F6E24" />
            </radialGradient>
          </defs>
          {/* Halo */}
          <circle cx="360" cy="360" r="340" fill="url(#moon-glow)" opacity="0.7" />
          <circle cx="360" cy="360" r="280" fill="url(#moon-glow)" opacity="0.5" />
          {/* Moon body */}
          <circle cx="360" cy="360" r="180" fill="url(#moon-body)" />
          {/* Subtle craters */}
          <circle cx="310" cy="310" r="18" fill="rgba(143,110,36,0.20)" />
          <circle cx="410" cy="380" r="12" fill="rgba(143,110,36,0.15)" />
          <circle cx="380" cy="440" r="22" fill="rgba(143,110,36,0.18)" />
          <circle cx="290" cy="410" r="9"  fill="rgba(143,110,36,0.14)" />
        </svg>
      </div>

      {/* Layer 3 · Filigrane constellation */}
      <svg
        aria-hidden="true"
        viewBox="0 0 1440 800"
        preserveAspectRatio="xMidYMid slice"
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          zIndex: 3,
          opacity: visible ? 0.35 : 0,
          transition: 'opacity 2400ms ease',
          pointerEvents: 'none',
        }}
      >
        <g stroke="#B8935A" strokeWidth="0.8" fill="none" opacity="0.55">
          <line x1="120" y1="200" x2="240" y2="150" />
          <line x1="240" y1="150" x2="330" y2="230" />
          <line x1="330" y1="230" x2="430" y2="180" />
          <line x1="430" y1="180" x2="520" y2="270" />
          <line x1="1050" y1="180" x2="1150" y2="240" />
          <line x1="1150" y1="240" x2="1240" y2="180" />
          <line x1="1240" y1="180" x2="1330" y2="260" />
          <line x1="150" y1="580" x2="240" y2="640" />
          <line x1="240" y1="640" x2="340" y2="600" />
        </g>
        <g fill="#B8935A">
          {[
            [120, 200], [240, 150], [330, 230], [430, 180], [520, 270],
            [1050, 180], [1150, 240], [1240, 180], [1330, 260],
            [150, 580], [240, 640], [340, 600],
          ].map(([cx, cy], i) => (
            <circle key={i} cx={cx} cy={cy} r="2.5" opacity="0.9" />
          ))}
        </g>
      </svg>

      {/* Layer 4 · Copy éditorial */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          textAlign: 'center',
          padding: '120px 24px 240px',
          maxWidth: 780,
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 1600ms 400ms ease, transform 1600ms 400ms cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            fontWeight: 500,
            letterSpacing: '0.4em',
            textTransform: 'uppercase',
            color: 'rgba(184, 147, 90, 0.85)',
            marginBottom: 32,
          }}
        >
          Plume Astrale
        </p>

        <h1
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(2.4rem, 5.5vw, 4.5rem)',
            fontWeight: 400,
            letterSpacing: '-0.01em',
            lineHeight: 1.12,
            color: '#F7F5F0',
            marginBottom: 32,
          }}
        >
          Comprendre les <em style={{ fontStyle: 'italic', color: '#B8935A' }}>périodes</em> de votre&nbsp;vie.
        </h1>

        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(15px, 1.4vw, 18px)',
            lineHeight: 1.65,
            color: 'rgba(247, 245, 240, 0.78)',
            maxWidth: 560,
            margin: '0 auto 48px',
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
            boxShadow: '0 12px 32px rgba(184, 147, 90, 0.35)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#C9A24B';
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 16px 40px rgba(184, 147, 90, 0.5)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#B8935A';
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 12px 32px rgba(184, 147, 90, 0.35)';
          }}
        >
          Découvrir mon parcours
          <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
        </Link>
      </div>

      {/* Layer 5 · Scroll indicator */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          bottom: 32,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
          opacity: visible ? 0.6 : 0,
          transition: 'opacity 2000ms 1200ms ease',
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
          50% { opacity: 0.9; transform: translateY(6px); }
        }
      `}</style>
    </section>
  );
}
