/**
 * Act7Conversion — Acte VII : La Conversion
 * ─────────────────────────────────────────────────────
 * "Votre voyage ne fait que commencer."
 *
 * Le CTA principal route vers /inscription (préserve les 20 crédits
 * offerts via le trigger Supabase — JAMAIS créer une deuxième
 * attribution). Le CTA secondaire route vers /connexion pour les
 * membres existants.
 *
 * Univers plus calme visuellement — moins de particules décoratives,
 * la plume revient très subtilement en fond.
 */
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import StarfieldBackdrop from '@/components/StarfieldBackdrop';
import { useAuth } from '@/context/AuthContext';
import { useExperienceStore } from '@/experience/useExperienceStore';
import { readIntent, readDrawnCard, readUtm } from '@/experience/intentConfig';
import { event as trackEvent } from '@/lib/analytics';

export default function Act7Conversion() {
  const { user } = useAuth();
  const intent = useExperienceStore((s) => s.intent) || readIntent();
  const drawnCard = useExperienceStore((s) => s.drawnCard) || readDrawnCard();
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setVisible(true);
            trackEvent('home_v3_signup_cta_viewed', { intent: intent || 'none' });
            io.disconnect();
          }
        });
      },
      { threshold: 0.5 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [intent]);

  // Construit un lien /inscription enrichi pour préserver intent + card + UTM
  // à travers l'onboarding (WelcomeSplash post-signup).
  const buildSignupUrl = () => {
    const utm = readUtm();
    const params = new URLSearchParams();
    if (intent) params.set('intent', intent);
    if (drawnCard) params.set('exp_card', drawnCard);
    Object.entries(utm).forEach(([k, v]) => { if (v) params.set(k, v); });
    params.set('welcome', '1');
    params.set('source', 'home_v3');
    return `/inscription?${params.toString()}`;
  };

  const handleSignupClick = () => {
    trackEvent('home_v3_signup_cta_clicked', { intent: intent || 'none', card: drawnCard || 'none' });
  };
  const handleLoginClick = () => {
    trackEvent('home_v3_login_clicked', { intent: intent || 'none' });
  };

  // Si utilisateur déjà connecté, redirection vers son espace
  const signupHref = user ? '/mon-compte' : buildSignupUrl();
  const primaryLabel = user ? 'Voir mon espace' : 'Commencer mon voyage';

  return (
    <section
      ref={ref}
      data-testid="home-experience-scene-7"
      className="hex3-section hex3-act-7"
      style={{
        padding: '180px 24px 160px',
        opacity: visible ? 1 : 0,
        transition: 'opacity 1600ms cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      <StarfieldBackdrop density={50} color="216, 183, 106" fade={0.22} />
      {/* Petite plume signature en fond (SVG stylisé, opacity très basse) */}
      <svg
        aria-hidden="true"
        viewBox="0 0 44 64"
        style={{
          position: 'absolute', top: '20%', left: '50%',
          transform: 'translateX(-50%) rotate(-14deg)',
          width: 90, height: 130, opacity: 0.15,
          filter: 'drop-shadow(0 0 30px rgba(216,183,106,0.4))',
        }}
      >
        <path d="M22 4 Q 21 20 22 30 Q 23 44 22 60"
              stroke="#C4A25C" strokeWidth="1.1" fill="none" strokeLinecap="round" />
        <g stroke="#D8B76A" strokeWidth="0.9" fill="none" strokeLinecap="round">
          {[10,16,22,28,34,40,46,52].flatMap((y) => [
            <path key={`l${y}`} d={`M22 ${y} Q 14 ${y+2} 7 ${y}`} />,
            <path key={`r${y}`} d={`M22 ${y} Q 30 ${y+2} 37 ${y}`} />,
          ])}
        </g>
      </svg>

      <div style={{ maxWidth: 620, margin: '0 auto', textAlign: 'center', position: 'relative', zIndex: 2 }}>
        <p className="hex3-eyebrow">ACTE VII · COMMENCER</p>

        <h2 className="hex3-h2">
          Votre voyage <em>ne fait que commencer.</em>
        </h2>

        <p style={{
          fontFamily: '"Inter", sans-serif', fontSize: 12, letterSpacing: '0.32em',
          textTransform: 'uppercase', color: '#D8B76A',
          margin: '32px 0 12px', display: 'inline-flex', alignItems: 'center', gap: 12,
        }}>
          <span style={{ fontSize: 18 }}>✦</span> 20 crédits offerts
        </p>
        <p style={{
          fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
          fontSize: 'clamp(16px, 1.7vw, 20px)',
          color: 'rgba(244,239,230,0.65)', lineHeight: 1.5,
          margin: '0 0 44px',
        }}>Pour commencer à explorer votre univers Plume Astrale.</p>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
          <Link
            to={signupHref}
            onClick={handleSignupClick}
            data-testid="home-experience-signup-cta"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 14,
              padding: '18px 40px', color: '#F4EFE6', textDecoration: 'none',
              fontFamily: '"Inter", sans-serif', fontSize: 12, letterSpacing: '0.32em',
              textTransform: 'uppercase', border: '1px solid rgba(216,183,106,0.7)',
              borderRadius: 2, transition: 'letter-spacing 400ms ease, background 300ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.letterSpacing = '0.38em';
              e.currentTarget.style.background = 'rgba(216,183,106,0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.letterSpacing = '0.32em';
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <span style={{ color: '#D8B76A', fontSize: 14 }}>✦</span>
            {primaryLabel}
          </Link>
          {!user && (
            <Link
              to="/connexion"
              onClick={handleLoginClick}
              data-testid="home-experience-login-cta"
              style={{
                fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.24em',
                textTransform: 'uppercase', color: 'rgba(244,239,230,0.5)',
                textDecoration: 'none', padding: '10px 14px',
              }}
            >
              Déjà membre&nbsp;? Se connecter →
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}
