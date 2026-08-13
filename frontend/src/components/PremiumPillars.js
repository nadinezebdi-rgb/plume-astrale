import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';

/**
 * PremiumPillars — 4 cartes premium présentant l'offre par bénéfice utilisateur.
 *
 * Approche : ne parle PAS d'outils astrologiques (thème natal, tarot, etc.)
 * mais de bénéfices humains (cycles de vie, décisions, relations).
 * L'astrologie devient le moteur invisible derrière ces bénéfices.
 */
const PILLARS = [
  {
    key: 'cycles',
    glyph: '🌓',
    title: 'Comprendre vos cycles',
    body: 'Découvrez les périodes qui favorisent l\'action, la réflexion ou le changement.',
    to: '/decouvrir?theme=cycles',
    testid: 'pillar-cycles',
  },
  {
    key: 'relations',
    glyph: '♡',
    title: 'Vos relations',
    body: 'Comprenez les dynamiques qui influencent vos liens avec les autres.',
    to: '/decouvrir?theme=relations',
    testid: 'pillar-relations',
  },
  {
    key: 'decisions',
    glyph: '✦',
    title: 'Vos décisions',
    body: 'Choisissez avec davantage de recul et de clarté.',
    to: '/decouvrir?theme=decisions',
    testid: 'pillar-decisions',
  },
  {
    key: 'evolution',
    glyph: '∞',
    title: 'Votre évolution',
    body: 'Observez votre progression dans le temps et les grands chapitres qui s\'ouvrent.',
    to: '/decouvrir?theme=evolution',
    testid: 'pillar-evolution',
  },
];

export default function PremiumPillars() {
  return (
    <section
      data-testid="premium-pillars"
      style={{
        background: '#0A1128',
        padding: '140px 24px',
        color: '#F7F5F0',
      }}
    >
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* En-tête éditorial */}
        <div style={{ textAlign: 'center', marginBottom: 96, maxWidth: 640, marginLeft: 'auto', marginRight: 'auto' }}>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 11,
              fontWeight: 500,
              letterSpacing: '0.4em',
              textTransform: 'uppercase',
              color: 'rgba(184, 147, 90, 0.85)',
              marginBottom: 24,
            }}
          >
            Quatre repères pour votre parcours
          </p>
          <h2
            style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(1.8rem, 3.5vw, 2.6rem)',
              fontWeight: 400,
              lineHeight: 1.2,
              color: '#F7F5F0',
              margin: 0,
            }}
          >
            Chaque période de vie a son <em style={{ fontStyle: 'italic', color: '#B8935A' }}>sens</em>.
          </h2>
        </div>

        {/* Grille des 4 piliers */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 32,
          }}
        >
          {PILLARS.map((p) => (
            <Link
              key={p.key}
              to={p.to}
              data-testid={p.testid}
              style={{
                display: 'block',
                padding: '48px 32px',
                borderRadius: 20,
                background: 'linear-gradient(180deg, rgba(30, 42, 94, 0.5) 0%, rgba(15, 26, 60, 0.35) 100%)',
                border: '1px solid rgba(184, 147, 90, 0.18)',
                textDecoration: 'none',
                color: 'inherit',
                position: 'relative',
                transition: 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
                overflow: 'hidden',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(184, 147, 90, 0.55)';
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.background =
                  'linear-gradient(180deg, rgba(30, 42, 94, 0.75) 0%, rgba(15, 26, 60, 0.55) 100%)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(184, 147, 90, 0.18)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.background =
                  'linear-gradient(180deg, rgba(30, 42, 94, 0.5) 0%, rgba(15, 26, 60, 0.35) 100%)';
              }}
            >
              {/* Glyphe (grand, minimaliste) */}
              <div
                aria-hidden="true"
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 48,
                  color: '#B8935A',
                  marginBottom: 24,
                  fontWeight: 300,
                  lineHeight: 1,
                }}
              >
                {p.glyph}
              </div>

              <h3
                style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 22,
                  fontWeight: 500,
                  color: '#F7F5F0',
                  margin: 0,
                  marginBottom: 12,
                  lineHeight: 1.3,
                }}
              >
                {p.title}
              </h3>

              <p
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: 'rgba(247, 245, 240, 0.7)',
                  margin: 0,
                  marginBottom: 32,
                }}
              >
                {p.body}
              </p>

              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11,
                  fontWeight: 600,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  color: '#B8935A',
                }}
              >
                Explorer
                <ArrowUpRight style={{ width: 14, height: 14 }} strokeWidth={2} />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
