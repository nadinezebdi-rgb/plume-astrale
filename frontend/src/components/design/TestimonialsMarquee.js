import React from 'react';
import Marquee from 'react-fast-marquee';

/**
 * TestimonialsMarquee — bandeau de preuve sociale animé
 * Se place JUSTE en dessous du Hero3D pour rassurer avant le CTA "Continuer" du wizard.
 * Style bulles de conversation glass, tons Nuit Douce, ne casse pas l'harmonie visuelle.
 */
const TESTIMONIALS = [
  {
    name: 'Léa',
    age: 32,
    city: 'Lyon',
    text: "J'ai enfin compris pourquoi je fuyais l'amour. Trois séances avec Soléna et tout s'éclaire.",
    stars: 5,
  },
  {
    name: 'Camille',
    age: 28,
    city: 'Paris',
    text: "Le PDF Rencontres Ultime m'a bluffée — les dates exactes de ma prochaine rencontre étaient justes.",
    stars: 5,
  },
  {
    name: 'Marion',
    age: 41,
    city: 'Bordeaux',
    text: "L'archétype jungien m'a révélé ma vraie nature. Je me sens réconciliée avec moi-même.",
    stars: 5,
  },
  {
    name: 'Sophie',
    age: 36,
    city: 'Toulouse',
    text: "L'Arbre de Vie kabbalistique est d'une profondeur rare. Un cadeau que je m'offre chaque année.",
    stars: 5,
  },
  {
    name: 'Alice',
    age: 29,
    city: 'Nantes',
    text: "Soléna ne raconte pas de banalités. Elle capte ce qui compte vraiment. Bluffant.",
    stars: 5,
  },
];

const Bubble = ({ t }) => (
  <div
    className="mx-3 flex-shrink-0"
    style={{
      width: 340,
      background: 'rgba(26, 32, 53, 0.55)',
      backdropFilter: 'blur(18px)',
      WebkitBackdropFilter: 'blur(18px)',
      border: '1px solid rgba(212, 175, 55, 0.18)',
      borderRadius: 20,
      padding: '18px 20px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.25)',
    }}
    data-testid={`testimonial-${t.name.toLowerCase()}`}
  >
    <div className="flex items-center gap-2 mb-2">
      {Array.from({ length: t.stars }).map((_, i) => (
        <svg key={i} width="12" height="12" viewBox="0 0 24 24" fill="#D4AF37">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ))}
    </div>
    <p
      className="text-sm mb-3"
      style={{
        color: '#E3D7FF',
        fontFamily: 'Cormorant Garamond, serif',
        fontStyle: 'italic',
        lineHeight: 1.55,
        fontSize: 15,
      }}
    >
      &laquo;&nbsp;{t.text}&nbsp;&raquo;
    </p>
    <p
      className="text-[11px]"
      style={{
        color: 'rgba(212, 175, 55, 0.85)',
        letterSpacing: '0.18em',
        textTransform: 'uppercase',
        fontFamily: 'Cinzel, serif',
        fontWeight: 400,
      }}
    >
      — {t.name}, {t.age} ans &middot; {t.city}
    </p>
  </div>
);

const TestimonialsMarquee = () => {
  return (
    <section
      className="relative py-12 z-10"
      data-testid="testimonials-marquee"
      style={{
        /* Transition brumeuse depuis le Hero (fond identique #111625) */
        background:
          'linear-gradient(180deg, #111625 0%, #131829 100%)',
      }}
    >
      <div className="text-center mb-7 px-4">
        <p
          className="text-[10px] mb-2"
          style={{
            color: 'rgba(212, 175, 55, 0.75)',
            letterSpacing: '0.35em',
            fontFamily: 'Cinzel, serif',
            textTransform: 'uppercase',
          }}
        >
          ✦ Elles ont osé consulter ✦
        </p>
        <p
          className="text-sm"
          style={{
            color: 'rgba(227, 215, 255, 0.55)',
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
          }}
        >
          Plus de 2&nbsp;400 femmes ont déjà éclairci leur chemin amoureux avec Plume Astrale.
        </p>
      </div>

      <Marquee
        gradient
        gradientColor="#111625"
        gradientWidth={90}
        speed={38}
        pauseOnHover
        aria-label="Témoignages clientes"
      >
        {TESTIMONIALS.map((t, i) => (
          <Bubble key={i} t={t} />
        ))}
      </Marquee>
    </section>
  );
};

export default TestimonialsMarquee;
