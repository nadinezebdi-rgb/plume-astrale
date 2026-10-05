/**
 * Act6Personalization — Acte VI : La Personnalisation
 * ────────────────────────────────────────────────────────
 * Lit `intent` du store Experience (sélection Acte II) et affiche
 * une recommandation personnalisée à 2 CTA. Si aucun intent
 * (utilisateur a skippé Acte II), fallback message générique.
 *
 * L'objectif est de donner l'impression que "Plume Astrale s'est
 * souvenu de votre choix" — un des moments les plus émotionnels
 * du parcours.
 */
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import StarfieldBackdrop from '@/components/StarfieldBackdrop';
import { useExperienceStore } from '@/experience/useExperienceStore';
import { readIntent } from '@/experience/intentConfig';
import { event as trackEvent } from '@/lib/analytics';

// Mapping intent → recommandations. Aligné avec le brief user.
// Note : "Journal" est remplacé par "cercle solena" comme validé.
const RECOMMENDATIONS = {
  relationship: {
    intro: 'Tu sens qu’une relation demande plus de clarté.',
    tag: 'Voici le chemin le plus doux pour commencer.',
    primary:   { title: 'Compatibilité',    tagline: 'Vos deux ciels comparés.',        route: '/services/compatibilite' },
    secondary: { title: 'Tarot relationnel', tagline: 'Un tirage pour éclairer un lien.', route: '/services/tarot/amour' },
  },
  clarity: {
    intro: 'Tu as besoin de voir plus clair dans ce qui t’entoure.',
    tag: 'Commençons par éclairer le vrai rythme de ta vie.',
    primary:   { title: 'Tarot',        tagline: 'Une carte pour une question précise.', route: '/services/tarot' },
    secondary: { title: 'Cycle actuel', tagline: 'Ce que ton année te demande.',   route: '/services/revolution-solaire' },
  },
  self_discovery: {
    intro: 'Tu veux mieux comprendre ce qui t’anime.',
    tag: 'Ton ciel peut devenir un premier chemin de vérité.',
    primary:   { title: 'Thème natal', tagline: 'Onze planètes qui racontent qui tu es.', route: '/theme-natal' },
    secondary: { title: 'Numérologie', tagline: 'Ton chemin de vie chiffré.',              route: '/services/numerologie' },
  },
  specific_question: {
    intro: 'Une question précise te suit encore.',
    tag: 'La réponse peut être plus simple qu’elle n’y paraît.',
    primary:   { title: 'Tarot oui / non', tagline: 'Une réponse claire, en une carte.', route: '/services/tarot/oui-non' },
    secondary: { title: 'Tarot 3 cartes',  tagline: 'Passé, présent, à venir.',           route: '/services/tarot' },
  },
};

const FALLBACK = {
  intro: 'Par où veux-tu commencer ?',
  tag: 'Voici trois chemins pour découvrir Plume Astrale.',
  primary:   { title: 'Tarot',       tagline: 'Éclairer une question.',                  route: '/services/tarot' },
  secondary: { title: 'Thème natal', tagline: 'Comprendre ton ciel de naissance.',     route: '/theme-natal' },
};

export default function Act6Personalization() {
  const storeIntent = useExperienceStore((s) => s.intent);
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  // Lit d'abord le store (session en cours), fallback sur sessionStorage
  const intent = storeIntent || readIntent();
  const config = (intent && RECOMMENDATIONS[intent]) || FALLBACK;

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setVisible(true);
            trackEvent('home_v3_personalization_viewed', { intent: intent || 'none' });
            io.disconnect();
          }
        });
      },
      { threshold: 0.4 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [intent]);

  const handleClick = (which) => {
    trackEvent('home_v3_personalization_clicked', { intent: intent || 'none', choice: which });
  };

  return (
    <section
      ref={ref}
      data-testid="home-experience-scene-6"
      className="hex3-section hex3-act-6"
      style={{
        padding: '160px 24px 140px',
        opacity: visible ? 1 : 0,
        transition: 'opacity 1400ms cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      <StarfieldBackdrop density={60} color="216, 183, 106" fade={0.25} />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: 780, margin: '0 auto', textAlign: 'center' }}>
        <p className="hex3-eyebrow">ACTE VI · POUR VOUS</p>

        <p
          data-testid="home-experience-personalization-intro"
          style={{
            fontFamily: '"Cormorant Garamond", "Playfair Display", serif',
            fontStyle: 'italic',
            fontSize: 'clamp(24px, 3vw, 34px)', lineHeight: 1.4,
            color: 'var(--hex3-ivory)', margin: '0 0 12px',
          }}
        >{config.intro}</p>
        <p
          data-testid="home-experience-personalization-tag"
          style={{
            fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
            fontSize: 'clamp(17px, 1.8vw, 22px)',
            color: 'var(--hex3-ivory-mute)', margin: '0 0 56px',
          }}
        >{config.tag}</p>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 24, textAlign: 'left',
        }}>
          {[
            { ...config.primary,   which: 'primary',   accent: true },
            { ...config.secondary, which: 'secondary', accent: false },
          ].map((r) => (
            <Link
              key={r.which}
              to={r.route}
              onClick={() => handleClick(r.which)}
              data-testid={`home-experience-reco-${r.which}`}
              style={{
                display: 'block',
                padding: '28px 30px',
                background: r.accent ? 'rgba(212,175,55,0.08)' : 'rgba(26,32,53,0.76)',
                border: `1px solid rgba(212,175,55,${r.accent ? 0.48 : 0.22})`,
                borderRadius: 8,
                textDecoration: 'none', color: 'var(--hex3-ivory)',
                transition: 'border-color 400ms ease, background 400ms ease, transform 400ms ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(212,175,55,0.75)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = `rgba(212,175,55,${r.accent ? 0.48 : 0.22})`;
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <p style={{
                fontFamily: '"Inter", sans-serif', fontSize: 10, letterSpacing: '0.32em',
                textTransform: 'uppercase', color: 'var(--hex3-gold)',
                margin: '0 0 10px',
              }}>{r.accent ? 'RECOMMANDÉ' : 'AUTRE VOIE'}</p>
              <h3 style={{
                fontFamily: '"Cormorant Garamond", serif', fontWeight: 400,
                fontSize: 28, margin: '0 0 8px', color: 'var(--hex3-ivory)',
              }}>{r.title}</h3>
              <p style={{
                fontFamily: '"Cormorant Garamond", serif', fontStyle: 'italic',
                fontSize: 16, color: 'var(--hex3-ivory-mute)', lineHeight: 1.5,
                margin: 0,
              }}>{r.tagline}</p>
              <p style={{
                fontFamily: '"Inter", sans-serif', fontSize: 11, letterSpacing: '0.28em',
                textTransform: 'uppercase', color: 'var(--hex3-gold)', margin: '20px 0 0',
              }}>Explorer →</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
