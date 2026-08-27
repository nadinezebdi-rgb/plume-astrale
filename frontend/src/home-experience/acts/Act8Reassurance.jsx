/**
 * Act8Reassurance — Acte VIII : La Rassurance + Footer signature
 * ────────────────────────────────────────────────────────────
 * Après la conversion émotionnelle, retour rationnel doux avec
 * 3 étapes concrètes. Puis footer minimal avec plume signature
 * dessinée en SVG (ligne dorée qui devient plume).
 *
 * Aucune sur-charge de témoignages / FAQ ici — la home classique
 * les héberge déjà (NocturneFAQ, /temoignages).
 */
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

const STEPS = [
  { n: '01', title: 'Créez votre espace',            body: 'Quelques informations et vous êtes chez vous.' },
  { n: '02', title: 'Recevez vos crédits',           body: '20 crédits offerts pour explorer immédiatement.' },
  { n: '03', title: 'Commencez votre exploration',   body: 'Tarot, thème natal, horoscope — à votre rythme.' },
];

const FOOTER_LINKS = [
  { label: 'Services',      to: '/livres' },
  { label: 'Mon espace',    to: '/mon-compte' },
  { label: 'FAQ',           to: '/#faq' },
  { label: 'Contact',       to: '/contact' },
  { label: 'Mentions',      to: '/mentions-legales' },
  { label: 'CGV',           to: '/cgv' },
  { label: 'Confidentialité', to: '/confidentialite' },
];

export default function Act8Reassurance() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { setVisible(true); io.disconnect(); }
        });
      },
      { threshold: 0.3 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      data-testid="home-experience-scene-8"
      className="hex3-section hex3-act-8"
      style={{
        position: 'relative', zIndex: 5,
        background: 'linear-gradient(180deg, #070713 0%, #05040A 100%)',
        padding: '120px 24px 60px',
        color: '#F4EFE6',
      }}
    >
      <div style={{
        maxWidth: 1100, margin: '0 auto',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'opacity 1400ms ease, transform 1400ms cubic-bezier(0.16, 1, 0.3, 1)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 70 }}>
          <p style={{
            fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.36em',
            textTransform: 'uppercase', color: 'rgba(216,183,106,0.75)', margin: '0 0 18px',
          }}>VOTRE ESPACE PLUME ASTRALE</p>
          <h2 style={{
            fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
            fontWeight: 400, fontSize: 'clamp(32px, 4.2vw, 48px)', lineHeight: 1.15,
            color: '#F4EFE6', margin: 0,
          }}>Trois pas <em style={{ color: '#D8B76A' }}>pour commencer.</em></h2>
        </div>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: 40, marginBottom: 100,
        }}>
          {STEPS.map((s, i) => (
            <div
              key={s.n}
              data-testid={`home-experience-step-${i + 1}`}
              style={{
                textAlign: 'left', padding: '0 12px',
                borderLeft: '1px solid rgba(216,183,106,0.28)',
              }}
            >
              <p style={{
                fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
                fontSize: 42, color: '#D8B76A', margin: '0 0 12px', lineHeight: 1,
              }}>{s.n}</p>
              <h3 style={{
                fontFamily: '"Cormorant Garamond", serif', fontWeight: 400,
                fontSize: 22, color: '#F4EFE6', margin: '0 0 8px',
              }}>{s.title}</h3>
              <p style={{
                fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
                fontSize: 16, color: 'rgba(244,239,230,0.60)', lineHeight: 1.55, margin: 0,
              }}>{s.body}</p>
            </div>
          ))}
        </div>

        {/* Ligne dorée + plume finale */}
        <div style={{
          position: 'relative', height: 140, margin: '80px auto 40px', textAlign: 'center',
        }}>
          <svg
            width="2" height="120" viewBox="0 0 2 120"
            style={{ display: 'block', margin: '0 auto' }}
            aria-hidden="true"
          >
            <line x1="1" y1="0" x2="1" y2="120"
                  stroke="rgba(216,183,106,0.5)" strokeWidth="1"
                  strokeDasharray="2 3" />
          </svg>
          <svg
            aria-hidden="true"
            viewBox="0 0 44 64"
            style={{
              position: 'absolute', bottom: 0, left: '50%',
              transform: 'translateX(-50%)',
              width: 34, height: 50,
              filter: 'drop-shadow(0 0 10px rgba(216,183,106,0.55))',
            }}
          >
            <path d="M22 4 Q 21 20 22 30 Q 23 44 22 60"
                  stroke="#C4A25C" strokeWidth="1.1" fill="none" strokeLinecap="round" />
            <g stroke="#D8B76A" strokeWidth="0.9" fill="none" strokeLinecap="round" opacity="0.75">
              {[10,16,22,28,34,40,46,52].flatMap((y) => [
                <path key={`l${y}`} d={`M22 ${y} Q 14 ${y+2} 7 ${y}`} />,
                <path key={`r${y}`} d={`M22 ${y} Q 30 ${y+2} 37 ${y}`} />,
              ])}
            </g>
          </svg>
        </div>

        <div style={{
          textAlign: 'center', marginBottom: 44,
          fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
          fontSize: 26, color: '#F4EFE6', letterSpacing: '0.05em',
        }}>
          PLUME <em style={{ color: '#D8B76A' }}>Astrale</em>
        </div>

        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 24, justifyContent: 'center',
          fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.14em',
          textTransform: 'uppercase',
          borderTop: '1px solid rgba(216,183,106,0.12)',
          paddingTop: 32,
        }}>
          {FOOTER_LINKS.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              style={{
                color: 'rgba(244,239,230,0.55)', textDecoration: 'none',
                transition: 'color 300ms ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = '#D8B76A'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'rgba(244,239,230,0.55)'; }}
              data-testid={`home-experience-footer-link-${l.to.replace(/[^a-z0-9]/gi, '-')}`}
            >
              {l.label}
            </Link>
          ))}
        </div>

        <p style={{
          textAlign: 'center', fontSize: 11,
          fontFamily: '"Inter", sans-serif', letterSpacing: '0.14em',
          color: 'rgba(244,239,230,0.28)', marginTop: 28,
        }}>
          © {new Date().getFullYear()} PLUME ASTRALE — TOUS DROITS RÉSERVÉS
        </p>
      </div>
    </section>
  );
}
