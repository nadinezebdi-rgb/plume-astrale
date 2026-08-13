import React, { useEffect, useRef, useState } from 'react';

/**
 * SolenaGuideCard — Présentation discrète de Soléna, apparaît au scroll.
 *
 * Design premium : petit avatar circulaire, texte serif, apparition en fade+rise
 * une seule fois quand l'utilisateur passe la ligne de flottaison.
 *
 * Soléna n'est plus le personnage principal — elle est une présence rassurante
 * qui se dévoile au bon moment.
 */
const SOLENA_AVATAR = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/hp82ivrl_Solena-glow.png';

export default function SolenaGuideCard({ testid = 'solena-guide' }) {
  const [visible, setVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === 'undefined') { setVisible(true); return; }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setVisible(true);
            io.disconnect();
          }
        });
      },
      { rootMargin: '0px 0px -100px 0px', threshold: 0.2 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      data-testid={testid}
      style={{
        background: '#F7F5F0',
        padding: '120px 24px',
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          maxWidth: 520,
          display: 'flex',
          alignItems: 'center',
          gap: 28,
          padding: '32px 36px',
          borderRadius: 20,
          background: '#FFFFFF',
          border: '1px solid rgba(15, 26, 60, 0.08)',
          boxShadow: '0 24px 48px -20px rgba(10, 17, 40, 0.15)',
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(24px)',
          transition: 'opacity 1200ms cubic-bezier(0.16, 1, 0.3, 1), transform 1200ms cubic-bezier(0.16, 1, 0.3, 1)',
        }}
      >
        <div
          style={{
            width: 72,
            height: 72,
            flexShrink: 0,
            borderRadius: '50%',
            overflow: 'hidden',
            background: 'linear-gradient(135deg, #0A1128 0%, #1E2A5E 100%)',
            padding: 2,
          }}
        >
          <img
            src={SOLENA_AVATAR}
            alt="Soléna"
            data-testid={`${testid}-avatar`}
            loading="lazy"
            decoding="async"
            style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              objectFit: 'cover',
              display: 'block',
            }}
          />
        </div>

        <div>
          <p
            style={{
              fontFamily: 'Playfair Display, serif',
              fontStyle: 'italic',
              fontSize: 20,
              lineHeight: 1.4,
              color: '#0A1128',
              margin: 0,
              marginBottom: 6,
            }}
          >
            Bonjour, je suis Soléna.
          </p>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 14,
              lineHeight: 1.55,
              color: 'rgba(10, 17, 40, 0.72)',
              margin: 0,
            }}
          >
            Je serai votre guide tout au long de votre parcours.
          </p>
        </div>
      </div>
    </section>
  );
}
