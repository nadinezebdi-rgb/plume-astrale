import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * HomepageMiniQuiz — Preview onboarding sur la Homepage.
 *
 * Reprend la première étape du parcours /decouvrir avec 3 questions
 * situations pour amorcer la conversion dès la Homepage. Sélectionner
 * une situation redirige vers /decouvrir?situation={key} qui reprend le
 * contexte pré-rempli.
 *
 * Palette : light ivoire (#F7F5F0) pour harmoniser avec les sections
 * ps-section-light, or Hermès (#B8935A) en accent.
 */

const QUIZ_SITUATIONS = [
  {
    key: 'doute',
    label: 'Une période de doute',
    hint: 'Vous cherchez du sens, du recul, un point d\'ancrage.',
  },
  {
    key: 'relation',
    label: 'Une relation qui vous questionne',
    hint: 'Un lien important vous fait douter ou vous fatigue.',
  },
  {
    key: 'changement',
    label: 'Un tournant à préparer',
    hint: 'Un projet, une transition, un nouveau chapitre à ouvrir.',
  },
];

export default function HomepageMiniQuiz() {
  const navigate = useNavigate();
  const [hoveredKey, setHoveredKey] = useState(null);

  const handleSelect = (key) => {
    // Passe la situation pré-sélectionnée à /decouvrir (via query param)
    navigate(`/decouvrir?situation=${encodeURIComponent(key)}`);
  };

  return (
    <section
      className="ps-section"
      data-testid="homepage-mini-quiz"
      style={{
        background: 'linear-gradient(180deg, #0F1A3C 0%, #0A1128 100%)',
        padding: '96px 24px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Étoiles décoratives */}
      <div aria-hidden="true" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        {[...Array(30)].map((_, i) => {
          const s = 1 + Math.random() * 1.8;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                width: s, height: s,
                background: '#F7F5F0',
                borderRadius: '50%',
                opacity: 0.15 + Math.random() * 0.35,
                boxShadow: '0 0 6px rgba(247, 245, 240, 0.4)',
              }}
            />
          );
        })}
      </div>

      <div className="ps-container" style={{ position: 'relative', zIndex: 1, maxWidth: 900, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 11, fontWeight: 500,
              letterSpacing: '0.32em', textTransform: 'uppercase',
              color: '#B8935A',
              marginBottom: 20,
            }}
          >
            En 30 secondes
          </p>
          <h2
            style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(2rem, 4vw, 3rem)',
              fontWeight: 400,
              lineHeight: 1.2,
              color: '#F7F5F0',
              marginBottom: 20,
            }}
          >
            Qu&apos;est-ce qui vous amène ici <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>aujourd&apos;hui</span> ?
          </h2>
          <p
            style={{
              fontFamily: 'Playfair Display, serif',
              fontStyle: 'italic',
              fontSize: 'clamp(16px, 1.8vw, 19px)',
              lineHeight: 1.55,
              color: 'rgba(247, 245, 240, 0.75)',
              maxWidth: 560,
              margin: '0 auto',
            }}
          >
            Choisissez la situation qui vous ressemble le plus.
            Nous vous guidons vers la lecture qui vous parle vraiment.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 20,
          }}
        >
          {QUIZ_SITUATIONS.map((s) => {
            const isHovered = hoveredKey === s.key;
            return (
              <button
                key={s.key}
                type="button"
                onClick={() => handleSelect(s.key)}
                onMouseEnter={() => setHoveredKey(s.key)}
                onMouseLeave={() => setHoveredKey(null)}
                data-testid={`mini-quiz-option-${s.key}`}
                style={{
                  textAlign: 'left',
                  padding: '28px 26px',
                  borderRadius: 16,
                  background: isHovered
                    ? 'linear-gradient(135deg, rgba(184, 147, 90, 0.16) 0%, rgba(184, 147, 90, 0.08) 100%)'
                    : 'rgba(30, 42, 94, 0.35)',
                  border: isHovered
                    ? '1px solid rgba(184, 147, 90, 0.55)'
                    : '1px solid rgba(184, 147, 90, 0.22)',
                  color: '#F7F5F0',
                  cursor: 'pointer',
                  transition: 'all 0.35s cubic-bezier(.22,.61,.36,1)',
                  transform: isHovered ? 'translateY(-3px)' : 'translateY(0)',
                  boxShadow: isHovered
                    ? '0 20px 40px rgba(184, 147, 90, 0.15)'
                    : 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12,
                }}
              >
                <div
                  style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 20,
                    fontWeight: 400,
                    lineHeight: 1.3,
                    color: '#F7F5F0',
                  }}
                >
                  {s.label}
                </div>
                <div
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    lineHeight: 1.55,
                    color: 'rgba(247, 245, 240, 0.68)',
                  }}
                >
                  {s.hint}
                </div>
                <div
                  style={{
                    marginTop: 4,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 8,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    fontWeight: 500,
                    letterSpacing: '0.18em',
                    textTransform: 'uppercase',
                    color: '#B8935A',
                  }}
                >
                  Continuer
                  <ArrowRight
                    style={{
                      width: 14, height: 14,
                      transform: isHovered ? 'translateX(4px)' : 'translateX(0)',
                      transition: 'transform 0.3s ease',
                    }}
                    strokeWidth={2}
                  />
                </div>
              </button>
            );
          })}
        </div>

        <div style={{ textAlign: 'center', marginTop: 40 }}>
          <button
            type="button"
            onClick={() => navigate('/decouvrir')}
            data-testid="mini-quiz-see-all"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'rgba(247, 245, 240, 0.6)',
              fontFamily: 'Inter, sans-serif',
              fontSize: 12,
              letterSpacing: '0.16em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              textDecoration: 'underline',
              textUnderlineOffset: 4,
              padding: 4,
            }}
          >
            Voir toutes les situations
          </button>
        </div>
      </div>
    </section>
  );
}
