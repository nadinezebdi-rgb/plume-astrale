import React from 'react';
import { Star, Quote } from 'lucide-react';

/**
 * Widget témoignages premium — cohérent avec la charte Plume Astrale
 * (Cinzel + Cormorant Garamond, palette or/nuit).
 *
 * Props:
 *  - testimonials: [{ name, city, sign, quote, rating }]
 *  - title:        titre optionnel (défaut: "Elles nous ont fait confiance")
 *  - subtitle:     sous-titre optionnel
 *  - testIdPrefix: préfixe pour data-testid (défaut: "testimonial")
 */
const TestimonialsWidget = ({
  testimonials,
  title = 'Elles ont vécu la lecture',
  subtitle = 'Retours de femmes qui ont reçu leur analyse Plume Astrale',
  testIdPrefix = 'testimonial',
}) => {
  if (!testimonials || testimonials.length === 0) return null;

  return (
    <section
      className="mb-12"
      aria-labelledby="plume-testimonials-title"
      data-testid={`${testIdPrefix}-widget`}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <p
          className="text-[10px] uppercase mb-3"
          style={{ color: '#D4AF37', letterSpacing: '0.35em', fontFamily: 'Cinzel, serif' }}
        >
          ✦ Témoignages ✦
        </p>
        <h2
          id="plume-testimonials-title"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 300,
            fontSize: 'clamp(26px, 3.4vw, 36px)',
            color: '#F5EEE0',
            marginBottom: 8,
            lineHeight: 1.2,
          }}
        >
          {title}
        </h2>
        <p
          className="text-sm max-w-xl mx-auto"
          style={{
            color: 'rgba(227,215,255,0.65)',
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
          }}
        >
          {subtitle}
        </p>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {testimonials.map((t, i) => (
          <article
            key={i}
            className="plume-glass p-6 relative flex flex-col"
            data-testid={`${testIdPrefix}-card-${i}`}
            style={{ minHeight: 220 }}
          >
            {/* Guillemet décoratif */}
            <Quote
              className="absolute -top-3 -left-1"
              style={{
                color: 'rgba(212,175,55,0.35)',
                width: 32,
                height: 32,
              }}
              strokeWidth={1.2}
              aria-hidden="true"
            />

            {/* Étoiles */}
            <div className="flex gap-0.5 mb-3" data-testid={`${testIdPrefix}-rating-${i}`}>
              {Array.from({ length: 5 }).map((_, s) => (
                <Star
                  key={s}
                  className="w-3.5 h-3.5"
                  strokeWidth={1.5}
                  style={{
                    color: s < (t.rating || 5) ? '#D4AF37' : 'rgba(212,175,55,0.2)',
                    fill: s < (t.rating || 5) ? '#D4AF37' : 'transparent',
                  }}
                />
              ))}
            </div>

            {/* Quote */}
            <p
              className="flex-1 text-sm mb-4"
              style={{
                color: 'rgba(245,238,224,0.92)',
                fontFamily: 'Cormorant Garamond, serif',
                fontStyle: 'italic',
                fontSize: 15,
                lineHeight: 1.55,
              }}
              data-testid={`${testIdPrefix}-quote-${i}`}
            >
              « {t.quote} »
            </p>

            {/* Signature */}
            <div className="pt-3" style={{ borderTop: '1px solid rgba(212,175,55,0.15)' }}>
              <div
                className="text-sm"
                style={{
                  color: '#F5EEE0',
                  fontFamily: 'Cinzel, serif',
                  letterSpacing: '0.08em',
                }}
                data-testid={`${testIdPrefix}-name-${i}`}
              >
                {t.name}
              </div>
              <div
                className="text-[11px] mt-0.5"
                style={{
                  color: 'rgba(212,175,55,0.7)',
                  letterSpacing: '0.15em',
                }}
                data-testid={`${testIdPrefix}-meta-${i}`}
              >
                {t.city}
                {t.sign ? ` · ${t.sign}` : ''}
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* Confiance bar */}
      <div
        className="mt-6 flex items-center justify-center gap-6 text-[11px]"
        style={{
          color: 'rgba(227,215,255,0.55)',
          letterSpacing: '0.18em',
          fontFamily: 'Cinzel, serif',
        }}
        data-testid={`${testIdPrefix}-trust-bar`}
      >
        <span className="flex items-center gap-1.5">
          <Star className="w-3 h-3" strokeWidth={1.5} style={{ color: '#D4AF37', fill: '#D4AF37' }} />
          4,9/5 · Note moyenne
        </span>
        <span aria-hidden="true" style={{ opacity: 0.4 }}>·</span>
        <span>Livraison en moins de 5 min</span>
      </div>
    </section>
  );
};

// ─── Datasets — vidés pour le concours 2026 (rien ne doit être faux). ────
// Ils seront remplis dès que de vrais témoignages seront collectés via
// /temoignages (soumission user → approbation admin dans /admin).

export const TESTIMONIALS_KABBALE = [];

export const TESTIMONIALS_ASTROCARTO = [];

export const TESTIMONIALS_KARMA = [];

export const TESTIMONIALS_COMPATIBILITE = [];

export default TestimonialsWidget;
