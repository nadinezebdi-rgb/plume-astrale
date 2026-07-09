import React from 'react';
import { motion } from 'framer-motion';

/**
 * FloatingReviews — Preuve sociale organique.
 * Bulles de conversation flottantes (style SMS), avec avatars gradients.
 * Effet magazine + application native, plus intime que des cards classiques.
 */

const REVIEWS = [
  {
    name: 'Camille',
    sign: 'Balance',
    city: 'Paris',
    text: "J'ai reconnu la personne rencontrée 3 semaines après. Bluffant.",
    gradient: ['#D4AF37', '#7BA5D9'],
    align: 'left',
    tilt: -1.2,
  },
  {
    name: 'Léa',
    sign: 'Poissons',
    city: 'Lyon',
    text: "Le décodage est d'une finesse rare. Rien de générique. Merci Solena.",
    gradient: ['#C4B0E0', '#D4AF37'],
    align: 'right',
    tilt: 1.4,
  },
  {
    name: 'Sarah',
    sign: 'Cancer',
    city: 'Bordeaux',
    text: "Le prochain rendez-vous astral tombait dans 11 jours. J'ai rencontré quelqu'un au 9ᵉ.",
    gradient: ['#7BA5D9', '#E8A855'],
    align: 'left',
    tilt: 0.8,
  },
  {
    name: 'Manon',
    sign: 'Lion',
    city: 'Marseille',
    text: 'Le Guide Ultime à 29,99€ vaut chaque centime. Je le relis chaque semaine.',
    gradient: ['#E8A855', '#D4AF37'],
    align: 'right',
    tilt: -0.9,
  },
  {
    name: 'Julie',
    sign: 'Sagittaire',
    city: 'Nantes',
    text: "De la clarté, sans jugement, avec une bienveillance rare. Mon rituel du soir.",
    gradient: ['#9DAA82', '#C4B0E0'],
    align: 'left',
    tilt: 1.1,
  },
  {
    name: 'Emma',
    sign: 'Vierge',
    city: 'Toulouse',
    text: "Solena dans ma poche à 23h après une dispute. Réponse en 15 secondes. Wow.",
    gradient: ['#D4AF37', '#C4B0E0'],
    align: 'right',
    tilt: -0.7,
  },
];

const Avatar = ({ name, gradient }) => (
  <div
    aria-hidden="true"
    style={{
      width: 44,
      height: 44,
      borderRadius: '50%',
      background: `linear-gradient(135deg, ${gradient[0]} 0%, ${gradient[1]} 100%)`,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#111625',
      fontWeight: 600,
      fontSize: 15,
      fontFamily: 'Cinzel, serif',
      flexShrink: 0,
      border: '2px solid rgba(212,175,55,0.35)',
      boxShadow: `0 8px 24px ${gradient[0]}33`,
    }}
  >
    {name.charAt(0)}
  </div>
);

const Bubble = ({ review, index }) => {
  const isRight = review.align === 'right';
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.7, delay: index * 0.08, ease: [0.22, 1, 0.36, 1] }}
      style={{
        display: 'flex',
        flexDirection: isRight ? 'row-reverse' : 'row',
        gap: 14,
        alignItems: 'flex-end',
        maxWidth: 480,
        marginLeft: isRight ? 'auto' : 0,
        marginRight: isRight ? 0 : 'auto',
      }}
      data-testid={`floating-review-${review.name.toLowerCase()}`}
    >
      <Avatar name={review.name} gradient={review.gradient} />
      <motion.div
        whileHover={{ scale: 1.02, rotate: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          background: 'rgba(26, 32, 53, 0.60)',
          backdropFilter: 'blur(18px)',
          WebkitBackdropFilter: 'blur(18px)',
          border: '1px solid rgba(212,175,55,0.20)',
          borderRadius: 22,
          borderBottomLeftRadius: isRight ? 22 : 4,
          borderBottomRightRadius: isRight ? 4 : 22,
          padding: '14px 18px',
          transform: `rotate(${review.tilt}deg)`,
          boxShadow: '0 14px 40px rgba(0,0,0,0.28)',
          flex: '0 1 auto',
        }}
      >
        <p
          className="text-sm md:text-[15px]"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontStyle: 'italic',
            color: '#F5EEE0',
            lineHeight: 1.5,
            marginBottom: 6,
          }}
        >
          {review.text}
        </p>
        <div className="flex items-center gap-2">
          <span
            className="text-[10px]"
            style={{
              color: '#D4AF37',
              letterSpacing: '0.22em',
              textTransform: 'uppercase',
              fontFamily: 'Cinzel, serif',
              fontWeight: 400,
            }}
          >
            {review.name}
          </span>
          <span style={{ color: 'rgba(212,175,55,0.35)' }}>·</span>
          <span
            className="text-[10px]"
            style={{
              color: 'rgba(227,215,255,0.55)',
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
            }}
          >
            {review.sign} · {review.city}
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

const FloatingReviews = () => (
  <section
    className="relative py-24 px-4 z-10"
    data-testid="floating-reviews-section"
    style={{
      background:
        'radial-gradient(ellipse 80% 60% at 50% 50%, rgba(212,175,55,0.04) 0%, transparent 70%)',
    }}
  >
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-14">
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-5"
          style={{
            background: 'rgba(212,175,55,0.08)',
            border: '1px solid rgba(212,175,55,0.30)',
          }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="#E8C766">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          <span
            className="text-[10px] uppercase"
            style={{ color: '#D4AF37', letterSpacing: '0.3em', fontWeight: 400 }}
          >
            4.9 / 5 · +2 000 âmes accompagnées
          </span>
        </div>
        <h2
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(1.9rem, 4.5vw, 3rem)',
            lineHeight: 1.1,
            color: '#F5EEE0',
            marginBottom: 12,
          }}
        >
          Ce qu&apos;elles disent en <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>vrai</em>
        </h2>
        <p
          className="max-w-xl mx-auto text-sm md:text-base"
          style={{
            fontFamily: 'Cormorant Garamond, serif',
            color: 'rgba(227,215,255,0.55)',
            fontStyle: 'italic',
            lineHeight: 1.6,
          }}
        >
          Des extraits authentiques de conversations avec Solena. Pas de scripts, pas de mise en scène.
        </p>
      </div>

      <div className="flex flex-col gap-5">
        {REVIEWS.map((r, i) => (
          <Bubble key={r.name} review={r} index={i} />
        ))}
      </div>
    </div>
  </section>
);

export default FloatingReviews;
