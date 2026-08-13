import React from 'react';
import { Link } from 'react-router-dom';
import { ZODIAC_SIGNS } from '@/config/zodiacSigns';

/**
 * ZodiacGrid — Grille des 12 signes en cartes cliquables (SEO longue traîne).
 *
 * Chaque carte pointe vers /horoscope/{slug} — une page dédiée par signe
 * avec archétype, traits, périodes clés, CTA vers un produit adapté.
 */
export default function ZodiacGrid() {
  return (
    <section
      data-testid="zodiac-grid"
      style={{
        padding: '80px 24px 40px',
        background: 'linear-gradient(180deg, #F7F5F0 0%, #EFEBE0 100%)',
      }}
    >
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <p
            style={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
              letterSpacing: '0.4em', textTransform: 'uppercase',
              color: '#8F6E24', marginBottom: 16,
            }}
          >
            Les douze signes
          </p>
          <h2
            style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(1.8rem, 3.5vw, 2.4rem)',
              fontWeight: 400, color: '#0A1128', margin: 0, lineHeight: 1.25,
            }}
          >
            Choisissez votre signe pour découvrir ce qui vous <em style={{ fontStyle: 'italic', color: '#8F6E24' }}>porte</em>.
          </h2>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: 16,
          }}
        >
          {ZODIAC_SIGNS.map((s) => (
            <Link
              key={s.slug}
              to={`/horoscope/${s.slug}`}
              data-testid={`zodiac-card-${s.slug}`}
              style={{
                display: 'block',
                padding: '24px 20px',
                background: '#FFFFFF',
                border: '1px solid rgba(15, 26, 60, 0.08)',
                borderRadius: 14,
                textAlign: 'center',
                textDecoration: 'none',
                transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#B8935A';
                e.currentTarget.style.transform = 'translateY(-3px)';
                e.currentTarget.style.boxShadow = '0 12px 24px -8px rgba(184, 147, 90, 0.25)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(15, 26, 60, 0.08)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div
                aria-hidden="true"
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 34, color: '#B8935A',
                  marginBottom: 8, lineHeight: 1,
                }}
              >
                {s.glyph}
              </div>
              <div
                style={{
                  fontFamily: 'Playfair Display, serif', fontSize: 18,
                  color: '#0A1128', marginBottom: 4,
                }}
              >
                {s.name}
              </div>
              <div
                style={{
                  fontFamily: 'Inter, sans-serif', fontSize: 10.5,
                  color: 'rgba(15, 26, 60, 0.55)',
                  letterSpacing: '0.05em',
                }}
              >
                {s.dates.split(' — ')[0]} → {s.dates.split(' — ')[1]}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
