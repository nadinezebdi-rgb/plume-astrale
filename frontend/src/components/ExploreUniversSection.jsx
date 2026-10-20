import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Sparkles, Heart, Sun } from 'lucide-react';
import './ExploreUniversSection.css';

const CARDS = [
  {
    key: 'theme-natal',
    to: '/theme-natal',
    eyebrow: 'Lecture signature',
    title: 'Thème natal',
    description: 'Ta carte du ciel décodée : personnalité, forces, défis et chemin de vie, dans un livre imprimable de 46 pages.',
    Icon: Sparkles,
    accent: '#D4AF37',
  },
  {
    key: 'synastrie',
    to: '/synastrie',
    eyebrow: 'Astrologie à deux',
    title: 'Compatibilité amoureuse',
    description: 'Comparez vos deux cartes du ciel et comprenez vraiment ce qui vous lie — et ce qui vous challenge.',
    Icon: Heart,
    accent: '#E8A5B9',
  },
  {
    key: 'quotidien',
    to: '/quotidien',
    eyebrow: 'Gratuit · Chaque matin',
    title: 'Horoscope du jour',
    description: 'Les énergies planétaires d’aujourd’hui pour ton signe, en 2 minutes de lecture dès le réveil.',
    Icon: Sun,
    accent: '#F6C77A',
  },
];

export default function ExploreUniversSection() {
  return (
    <section
      className="explore-univers"
      aria-labelledby="explore-univers-title"
      data-testid="explore-univers-section"
    >
      <div className="explore-univers__inner">
        <header className="explore-univers__header">
          <p className="explore-univers__eyebrow">Pour aller plus loin</p>
          <h2 id="explore-univers-title" className="explore-univers__title">
            Explore ton univers
          </h2>
          <p className="explore-univers__subtitle">
            Trois portes d’entrée pour continuer ton voyage astral, à ton rythme.
          </p>
        </header>

        <div className="explore-univers__grid">
          {CARDS.map(({ key, to, eyebrow, title, description, Icon, accent }) => (
            <Link
              key={key}
              to={to}
              className="explore-univers__card"
              data-testid={`explore-univers-card-${key}`}
              style={{ '--card-accent': accent }}
            >
              <div className="explore-univers__card-head">
                <span className="explore-univers__card-icon" aria-hidden="true">
                  <Icon size={22} strokeWidth={1.4} />
                </span>
                <ArrowUpRight
                  size={20}
                  strokeWidth={1.4}
                  className="explore-univers__card-arrow"
                  aria-hidden="true"
                />
              </div>
              <p className="explore-univers__card-eyebrow">{eyebrow}</p>
              <h3 className="explore-univers__card-title">{title}</h3>
              <p className="explore-univers__card-desc">{description}</p>
              <span className="explore-univers__card-cta" aria-hidden="true">
                Découvrir
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
