/**
 * CinematicBookShowcase — Mini-vidéo animée reconstituée à partir de 3 photographies
 * cinématographiques du livre Plume Astrale personnalisé "Sophie".
 *
 * Effet Ken Burns (zoom + pan subtils) + cross-fade toutes les 5s pour donner
 * l'illusion d'une séquence vidéo tournée en atelier.
 *
 * Les images sont générées via Gemini Nano Banana et servies statiquement
 * depuis /videos/sophie/.
 *
 * Respect prefers-reduced-motion.
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Play, Pause } from 'lucide-react';

const SLIDES = [
  {
    src: '/videos/sophie/sophie-02-cover.png',
    alt: "Couverture navy et or du livre Plume Astrale personnalisé au prénom Sophie",
    caption: 'La couverture est gravée à votre prénom',
  },
  {
    src: '/videos/sophie/sophie-03-hands.png',
    alt: "Deux mains tournant une page du livre astral personnalisé Sophie",
    caption: "Vous tournez la première page — votre carte du ciel apparaît",
  },
  {
    src: '/videos/sophie/sophie-01-open.png',
    alt: "Livre astral Plume Astrale ouvert sur le chapitre Birth Chart",
    caption: "Chaque chapitre est composé à partir de vos données exactes",
  },
];

const SLIDE_DURATION = 5000; // 5 secondes par image

export default function CinematicBookShowcase() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused) return undefined;
    const t = setInterval(() => {
      setActive((i) => (i + 1) % SLIDES.length);
    }, SLIDE_DURATION);
    return () => clearInterval(t);
  }, [paused]);

  return (
    <section
      className="cbs-section"
      data-testid="cinematic-book-showcase"
      aria-label="Aperçu cinématique du livre Plume Astrale personnalisé"
    >
      <style>{`
        .cbs-section {
          position: relative;
          background: linear-gradient(180deg, #0B0F1E 0%, #0F1A3C 100%);
          padding: clamp(72px, 9vw, 128px) 0;
          overflow: hidden;
        }
        .cbs-section::before {
          content: '';
          position: absolute; inset: 0;
          background:
            radial-gradient(60% 60% at 30% 20%, rgba(201, 162, 75, 0.10) 0%, transparent 60%),
            radial-gradient(50% 50% at 80% 80%, rgba(201, 162, 75, 0.06) 0%, transparent 60%);
          pointer-events: none;
        }
        .cbs-container {
          position: relative;
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 clamp(16px, 4vw, 40px);
          display: grid;
          gap: clamp(32px, 5vw, 64px);
          grid-template-columns: 1fr;
          align-items: center;
        }
        @media (min-width: 880px) {
          .cbs-container {
            grid-template-columns: 5fr 6fr;
          }
        }
        .cbs-copy .cbs-eyebrow {
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          letter-spacing: 0.24em;
          text-transform: uppercase;
          color: #C9A24B;
          font-weight: 600;
          margin-bottom: 20px;
          display: inline-block;
        }
        .cbs-copy h2 {
          font-family: 'Playfair Display', Georgia, serif;
          font-size: clamp(30px, 4.4vw, 48px);
          line-height: 1.14;
          color: #F7F5F0;
          font-weight: 500;
          margin: 0 0 24px 0;
          letter-spacing: -0.01em;
        }
        .cbs-copy h2 em {
          font-style: italic;
          color: #C9A24B;
        }
        .cbs-copy p {
          font-family: 'Inter', sans-serif;
          font-size: 16px;
          line-height: 1.7;
          color: rgba(247, 245, 240, 0.72);
          margin: 0 0 20px 0;
          max-width: 480px;
        }
        .cbs-caption {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          padding: 10px 16px;
          background: rgba(201, 162, 75, 0.10);
          border: 1px solid rgba(201, 162, 75, 0.30);
          border-radius: 999px;
          color: #E5D9BA;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          margin-bottom: 24px;
          transition: opacity 400ms ease;
        }
        .cbs-caption-dot {
          width: 6px; height: 6px;
          border-radius: 50%;
          background: #C9A24B;
          box-shadow: 0 0 8px rgba(201, 162, 75, 0.7);
        }
        .cbs-cta {
          display: inline-flex; align-items: center; gap: 8px;
          padding: 14px 26px;
          background: #C9A24B;
          color: #0F1A3C;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 600;
          letter-spacing: 0.10em;
          text-transform: uppercase;
          border-radius: 8px;
          text-decoration: none;
          transition: background 220ms ease, transform 220ms ease, box-shadow 220ms ease;
        }
        .cbs-cta:hover {
          background: #d6b262;
          transform: translateY(-2px);
          box-shadow: 0 12px 28px rgba(201, 162, 75, 0.30);
        }
        /* Video-like stage */
        .cbs-stage {
          position: relative;
          aspect-ratio: 16 / 9.4;
          border-radius: 18px;
          overflow: hidden;
          box-shadow:
            0 40px 80px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(201, 162, 75, 0.18) inset;
          background: #0B0F1E;
        }
        .cbs-slide {
          position: absolute; inset: 0;
          opacity: 0;
          transition: opacity 1400ms cubic-bezier(0.4, 0, 0.2, 1);
        }
        .cbs-slide.active {
          opacity: 1;
        }
        .cbs-slide img {
          width: 100%; height: 100%;
          object-fit: cover;
          display: block;
          /* Ken Burns : le slide actif zoome et se déplace lentement */
          transform: scale(1.05);
          transition: transform 6000ms ease-out;
        }
        .cbs-slide.active img {
          animation: kenburns 6000ms ease-out forwards;
        }
        @keyframes kenburns {
          from { transform: scale(1.02) translate(0, 0); }
          to { transform: scale(1.12) translate(-2%, -1.5%); }
        }
        /* Vignette + film grain feel */
        .cbs-stage::after {
          content: '';
          position: absolute; inset: 0;
          background:
            radial-gradient(120% 120% at 50% 50%, transparent 55%, rgba(0, 0, 0, 0.55) 100%),
            linear-gradient(180deg, transparent 70%, rgba(0, 0, 0, 0.35) 100%);
          pointer-events: none;
        }
        .cbs-progress {
          position: absolute;
          bottom: 20px; left: 20px; right: 20px;
          display: flex; gap: 6px;
          z-index: 3;
        }
        .cbs-progress-bar {
          flex: 1;
          height: 2px;
          background: rgba(247, 245, 240, 0.25);
          border-radius: 2px;
          overflow: hidden;
          position: relative;
        }
        .cbs-progress-bar-fill {
          position: absolute;
          top: 0; left: 0; bottom: 0;
          background: #C9A24B;
          width: 0%;
        }
        .cbs-progress-bar.active .cbs-progress-bar-fill {
          animation: fill 5000ms linear forwards;
        }
        .cbs-progress-bar.done .cbs-progress-bar-fill { width: 100%; }
        @keyframes fill { from { width: 0%; } to { width: 100%; } }
        .cbs-play-toggle {
          position: absolute;
          top: 16px; right: 16px;
          z-index: 3;
          width: 36px; height: 36px;
          border-radius: 50%;
          background: rgba(11, 15, 30, 0.55);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          border: 1px solid rgba(247, 245, 240, 0.2);
          color: #F7F5F0;
          cursor: pointer;
          display: flex; align-items: center; justify-content: center;
          transition: background 200ms ease, border-color 200ms ease;
        }
        .cbs-play-toggle:hover {
          background: rgba(201, 162, 75, 0.30);
          border-color: rgba(201, 162, 75, 0.6);
        }
        .cbs-slide-caption {
          position: absolute;
          left: 20px; bottom: 40px;
          z-index: 2;
          font-family: 'Playfair Display', Georgia, serif;
          font-style: italic;
          font-size: 15px;
          color: #F7F5F0;
          text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
          max-width: 60%;
          opacity: 0;
          transform: translateY(6px);
          transition: opacity 800ms ease 400ms, transform 800ms ease 400ms;
        }
        .cbs-slide.active .cbs-slide-caption {
          opacity: 1;
          transform: translateY(0);
        }
        @media (prefers-reduced-motion: reduce) {
          .cbs-slide.active img { animation: none; }
          .cbs-slide { transition-duration: 200ms; }
          .cbs-progress-bar.active .cbs-progress-bar-fill { animation: none; width: 100%; }
        }
      `}</style>

      <div className="cbs-container">
        <div className="cbs-copy">
          <span className="cbs-eyebrow">Édition personnelle · Prénom Sophie</span>
          <h2>
            Un livre qui porte votre nom,<br />
            <em>composé pour vous.</em>
          </h2>
          <span className="cbs-caption" aria-live="polite">
            <span className="cbs-caption-dot" />
            {SLIDES[active].caption}
          </span>
          <p>
            Chaque commande est calculée, rédigée et composée à partir de vos données
            exactes de naissance. Vous ne recevez pas une variation par signe — vous recevez
            <em style={{ color: '#C9A24B', fontStyle: 'italic' }}> votre édition unique</em>.
          </p>
          <Link
            to="/inscription"
            className="cbs-cta"
            data-testid="cinematic-showcase-cta"
          >
            Créer mon aperçu offert <ArrowRight size={16} strokeWidth={1.8} />
          </Link>
        </div>

        <div className="cbs-stage" data-testid="cinematic-showcase-stage">
          {SLIDES.map((slide, i) => (
            <div
              key={slide.src}
              className={`cbs-slide ${i === active ? 'active' : ''}`}
              aria-hidden={i !== active}
            >
              <img
                src={slide.src}
                alt={slide.alt}
                loading={i === 0 ? 'eager' : 'lazy'}
                decoding="async"
              />
              <div className="cbs-slide-caption">{slide.caption}</div>
            </div>
          ))}

          <button
            type="button"
            className="cbs-play-toggle"
            onClick={() => setPaused((p) => !p)}
            aria-label={paused ? 'Reprendre l\'animation' : 'Mettre en pause'}
            data-testid="cinematic-showcase-toggle"
          >
            {paused ? <Play size={14} strokeWidth={2} /> : <Pause size={14} strokeWidth={2} />}
          </button>

          <div className="cbs-progress" aria-hidden="true">
            {SLIDES.map((_, i) => (
              <div
                key={i}
                className={`cbs-progress-bar ${i === active && !paused ? 'active' : ''} ${i < active ? 'done' : ''}`}
              >
                <span className="cbs-progress-bar-fill" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
