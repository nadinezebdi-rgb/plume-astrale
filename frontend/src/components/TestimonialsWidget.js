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

// ─── Datasets pré-remplis (à remplacer par tes vrais témoignages) ────────────

export const TESTIMONIALS_KABBALE = [
  {
    name: 'Camille D.',
    city: 'Lyon',
    sign: 'Balance',
    rating: 5,
    quote: "Je n'avais jamais lu quelque chose d'aussi précis sur mon chemin intérieur. Les Sephiroth m'ont donné un langage pour ce que je ressens depuis toujours.",
  },
  {
    name: 'Élodie R.',
    city: 'Bordeaux',
    sign: 'Poissons',
    rating: 5,
    quote: "Reçu en 2 minutes après le paiement. 15 pages qui donnent des frissons. J'ai enfin compris pourquoi je fonctionne par cycles de 7 ans.",
  },
  {
    name: 'Sophie M.',
    city: 'Bruxelles',
    sign: 'Capricorne',
    rating: 5,
    quote: "Le diagnostic des Piliers a mis des mots sur mon déséquilibre. Je relis ce PDF chaque semaine. C'est devenu mon guide de fond.",
  },
];

export const TESTIMONIALS_ASTROCARTO = [
  {
    name: 'Nadia B.',
    city: 'Paris',
    sign: 'Sagittaire',
    rating: 5,
    quote: "J'hésitais entre Lisbonne et Barcelone. Soléna m'a orientée vers Lisbonne — 3 mois après j'y étais. Ma vie a basculé, littéralement.",
  },
  {
    name: 'Laurence P.',
    city: 'Montréal',
    sign: 'Taureau',
    rating: 5,
    quote: "18 pages hyper détaillées. La ligne Vénus qui passe sur Bali… je comprends enfin pourquoi j'y ai pleuré de bonheur en 2019.",
  },
  {
    name: 'Estelle V.',
    city: 'Nantes',
    sign: 'Vierge',
    rating: 5,
    quote: "Le bonus Soléna était une ville dont je n'avais jamais entendu parler. Je pars la visiter en avril. Je fais confiance au ciel maintenant.",
  },
];

export const TESTIMONIALS_KARMA = [
  {
    name: 'Aurélie J.',
    city: 'Toulouse',
    sign: 'Cancer',
    rating: 5,
    quote: "Le nœud sud dans ma 7e maison expliquait tout. J'ai enfin lâché une relation qui me tirait vers le passé depuis 10 ans.",
  },
  {
    name: 'Marion T.',
    city: 'Marseille',
    sign: 'Scorpion',
    rating: 5,
    quote: "89€ pour comprendre ma mission d'incarnation. Aucun coach ne m'avait donné cette clarté. Les rituels sont d'une justesse rare.",
  },
  {
    name: 'Céline F.',
    city: 'Genève',
    sign: 'Verseau',
    rating: 5,
    quote: "J'ai reconnu chaque schéma karmique décrit. C'est comme si Soléna m'avait lue à cœur ouvert. Bouleversant.",
  },
];

export const TESTIMONIALS_COMPATIBILITE = [
  {
    name: 'Julie & Thomas',
    city: 'Rennes',
    sign: 'Gémeaux × Lion',
    rating: 5,
    quote: "On l'a lu ensemble à voix haute. On a ri, on a pleuré. Ça a mis des mots sur ce qu'on n'arrivait pas à se dire depuis 4 ans.",
  },
  {
    name: 'Amélie C.',
    city: 'Lille',
    sign: 'Balance × Bélier',
    rating: 5,
    quote: "Analyse ultra fine des aspects. La synastrie Vénus-Mars nous a fait comprendre notre alchimie physique. Bluffant.",
  },
  {
    name: 'Inès L.',
    city: 'Nice',
    sign: 'Vierge × Poissons',
    rating: 5,
    quote: "Je l'ai offert à mon meilleur ami pour ses 30 ans (compat amitié). Il m'a rappelée en larmes le soir même.",
  },
];

export default TestimonialsWidget;
