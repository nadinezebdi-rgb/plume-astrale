import React from 'react';
import { Sparkles } from 'lucide-react';

/**
 * Mockup 3D isométrique — 3 pages "leaked" avec flou artistique.
 * CSS pur, aucune image externe. Suggère la valeur du PDF Astrocarto
 * avant que l'acheteur tape sa CB.
 */
const PageBlurred = ({ variant = 0, delay = 0 }) => {
  // 3 variantes esthétiques : couverture, page carte, page ligne planétaire
  const isCover = variant === 0;
  const isMap = variant === 1;

  return (
    <div
      className="pdf-preview-page"
      style={{ animationDelay: `${delay}s` }}
      aria-hidden="true"
    >
      {/* En-tête doré */}
      <div style={{
        height: 22,
        background: 'linear-gradient(90deg, transparent, rgba(212,175,55,0.5), transparent)',
        marginBottom: 12,
        borderRadius: 2,
      }} />

      {/* Titre principal */}
      {isCover ? (
        <>
          <div style={{
            fontFamily: 'Cinzel, serif',
            fontSize: 13,
            color: '#D4AF37',
            letterSpacing: '0.3em',
            textAlign: 'center',
            filter: 'blur(1.5px)',
            marginBottom: 8,
          }}>
            ✦ PLUME ASTRALE ✦
          </div>
          <div style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
            fontSize: 20,
            color: '#F5EEE0',
            textAlign: 'center',
            filter: 'blur(2.5px)',
            lineHeight: 1.15,
            marginBottom: 6,
          }}>
            Ton Astrocartographie
          </div>
          <div style={{
            fontSize: 10,
            color: 'rgba(227,215,255,0.6)',
            textAlign: 'center',
            filter: 'blur(1.5px)',
            marginBottom: 18,
          }}>
            Analyse personnalisée · 18 pages
          </div>

          {/* Cercle astro décoratif */}
          <div style={{
            width: 90,
            height: 90,
            margin: '0 auto 14px',
            borderRadius: '50%',
            border: '1.5px solid rgba(212,175,55,0.6)',
            position: 'relative',
            filter: 'blur(0.8px)',
          }}>
            <div style={{
              position: 'absolute',
              inset: 8,
              borderRadius: '50%',
              border: '1px solid rgba(212,175,55,0.3)',
            }} />
            <div style={{
              position: 'absolute',
              inset: '48% 4px auto 4px',
              height: 1,
              background: 'rgba(212,175,55,0.4)',
            }} />
            <div style={{
              position: 'absolute',
              inset: '4px 48% 4px auto',
              width: 1,
              background: 'rgba(212,175,55,0.4)',
            }} />
          </div>
        </>
      ) : isMap ? (
        <>
          <div style={{
            fontFamily: 'Cinzel, serif',
            fontSize: 11,
            color: '#D4AF37',
            letterSpacing: '0.24em',
            filter: 'blur(1.5px)',
            marginBottom: 10,
          }}>
            LIGNES PLANÉTAIRES
          </div>
          {/* Fausse carte du monde */}
          <div style={{
            height: 100,
            background: 'radial-gradient(ellipse at 30% 40%, rgba(212,175,55,0.15), transparent 60%), radial-gradient(ellipse at 70% 60%, rgba(167,139,250,0.15), transparent 60%)',
            border: '1px solid rgba(212,175,55,0.25)',
            borderRadius: 4,
            marginBottom: 12,
            position: 'relative',
            filter: 'blur(2px)',
          }}>
            {/* Lignes courbes fake */}
            <div style={{ position: 'absolute', inset: '30% 10% auto 10%', height: 1, background: 'linear-gradient(90deg, transparent, #E8C766, transparent)', transform: 'rotate(-8deg)' }} />
            <div style={{ position: 'absolute', inset: '55% 15% auto 15%', height: 1, background: 'linear-gradient(90deg, transparent, #A78BFA, transparent)', transform: 'rotate(12deg)' }} />
            <div style={{ position: 'absolute', inset: '70% 20% auto 20%', height: 1, background: 'linear-gradient(90deg, transparent, #E8C766, transparent)', transform: 'rotate(-4deg)' }} />
            {/* Points villes */}
            <div style={{ position: 'absolute', top: '35%', left: '25%', width: 4, height: 4, borderRadius: '50%', background: '#D4AF37' }} />
            <div style={{ position: 'absolute', top: '60%', left: '55%', width: 4, height: 4, borderRadius: '50%', background: '#D4AF37' }} />
            <div style={{ position: 'absolute', top: '48%', left: '75%', width: 4, height: 4, borderRadius: '50%', background: '#D4AF37' }} />
          </div>
          {/* Faux paragraphes floutés */}
          {[92, 76, 88, 60].map((w, i) => (
            <div key={i} style={{
              width: `${w}%`,
              height: 6,
              background: 'rgba(245,238,224,0.35)',
              borderRadius: 2,
              marginBottom: 5,
              filter: 'blur(2px)',
            }} />
          ))}
        </>
      ) : (
        <>
          <div style={{
            fontFamily: 'Cinzel, serif',
            fontSize: 11,
            color: '#D4AF37',
            letterSpacing: '0.24em',
            filter: 'blur(1.5px)',
            marginBottom: 10,
          }}>
            ♀ LIGNE VÉNUS
          </div>
          <div style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
            fontSize: 14,
            color: '#F5EEE0',
            filter: 'blur(2.2px)',
            marginBottom: 12,
            lineHeight: 1.35,
          }}>
            &quot;Ta ligne Vénus traverse&nbsp;<span style={{ color: '#D4AF37' }}>Lisbonne</span>&nbsp;et éveille en toi&hellip;&quot;
          </div>
          {[95, 82, 90, 70, 88, 55].map((w, i) => (
            <div key={i} style={{
              width: `${w}%`,
              height: 6,
              background: 'rgba(245,238,224,0.35)',
              borderRadius: 2,
              marginBottom: 5,
              filter: 'blur(2px)',
            }} />
          ))}
          {/* Encadré doré */}
          <div style={{
            marginTop: 12,
            padding: 10,
            border: '1px solid rgba(212,175,55,0.4)',
            borderRadius: 4,
            background: 'rgba(212,175,55,0.05)',
            filter: 'blur(1.5px)',
          }}>
            <div style={{ width: '70%', height: 5, background: '#D4AF37', borderRadius: 2, marginBottom: 4 }} />
            <div style={{ width: '85%', height: 5, background: 'rgba(245,238,224,0.5)', borderRadius: 2 }} />
          </div>
        </>
      )}

      {/* Watermark "APERÇU" */}
      <div className="pdf-preview-watermark">APERÇU</div>
    </div>
  );
};

const PdfMockup3D = ({ testId = 'pdf-mockup' }) => (
  <section className="mb-12" data-testid={testId}>
    <div className="text-center mb-6">
      <p className="text-[10px] uppercase mb-3" style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}>
        ✦ Aperçu du rapport ✦
      </p>
      <h2 style={{
        fontFamily: 'Cormorant Garamond, serif',
        fontWeight: 300,
        fontSize: 'clamp(24px, 3vw, 32px)',
        color: '#F5EEE0',
        marginBottom: 6,
        lineHeight: 1.2,
      }}>
        Voici ce que tu vas recevoir dans <em style={{ color: '#D4AF37', fontStyle: 'italic' }}>ta boîte mail</em>
      </h2>
      <p className="text-sm max-w-xl mx-auto" style={{ color: 'rgba(227,215,255,0.65)', fontFamily: 'Cormorant Garamond, serif', fontStyle: 'italic' }}>
        18 pages sur mesure. Voici trois d&apos;entre elles, floutées pour préserver ton intimité.
      </p>
    </div>

    <div className="pdf-mockup-stage">
      <PageBlurred variant={0} delay={0} />
      <PageBlurred variant={1} delay={0.15} />
      <PageBlurred variant={2} delay={0.3} />
    </div>

    <div className="text-center mt-4 text-[11px]" style={{ color: 'rgba(212,175,55,0.75)', letterSpacing: '0.18em', fontFamily: 'Cinzel, serif' }}>
      <Sparkles className="w-3 h-3 inline mr-1.5" />
      Livraison instantanée · Cinzel &amp; Cormorant Garamond · Impression maison possible
    </div>

    <style>{`
      .pdf-mockup-stage {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        perspective: 1400px;
        max-width: 900px;
        margin: 0 auto;
      }
      .pdf-preview-page {
        position: relative;
        aspect-ratio: 0.72 / 1;
        padding: 22px 18px;
        background: linear-gradient(160deg, #1a1230 0%, #0e0a1e 100%);
        border: 1px solid rgba(212,175,55,0.35);
        border-radius: 6px;
        box-shadow: 0 30px 60px -20px rgba(0,0,0,0.6), 0 0 40px -20px rgba(212,175,55,0.4);
        overflow: hidden;
        opacity: 0;
        animation: pdfPageFloat 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards, pdfPageBob 6s ease-in-out infinite;
      }
      .pdf-preview-page:nth-child(1) { transform: rotateY(14deg) translateZ(0); }
      .pdf-preview-page:nth-child(2) { transform: translateZ(40px) translateY(-8px); z-index: 2; box-shadow: 0 40px 80px -20px rgba(0,0,0,0.7), 0 0 60px -15px rgba(212,175,55,0.5); }
      .pdf-preview-page:nth-child(3) { transform: rotateY(-14deg) translateZ(0); }
      .pdf-preview-watermark {
        position: absolute;
        bottom: 14px;
        left: 50%;
        transform: translateX(-50%) rotate(-4deg);
        font-family: 'Cinzel', serif;
        font-size: 22px;
        letter-spacing: 0.4em;
        color: rgba(212,175,55,0.28);
        pointer-events: none;
      }
      @keyframes pdfPageFloat {
        0%   { opacity: 0; transform: rotateY(30deg) translateY(30px) translateZ(-100px); }
        100% { opacity: 1; }
      }
      @keyframes pdfPageBob {
        0%, 100% { translate: 0 0; }
        50%      { translate: 0 -6px; }
      }
      @media (max-width: 640px) {
        .pdf-mockup-stage { grid-template-columns: 1fr; max-width: 260px; gap: 32px; }
        .pdf-preview-page:nth-child(1),
        .pdf-preview-page:nth-child(2),
        .pdf-preview-page:nth-child(3) { transform: none; }
      }
    `}</style>
  </section>
);

export default PdfMockup3D;
