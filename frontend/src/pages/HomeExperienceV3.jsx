import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Check, Plus, Sparkles } from 'lucide-react';
import SEO from '@/components/SEO';
import { useCart } from '@/context/CartContext';
import { LECTURES, OUTILS } from '@/config/catalog';
import '../home-experience/HomeExperience.css';

const JSONLD = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Plume Astrale',
  url: 'https://plume-astrale.fr',
  description: 'Lectures astrologiques, tarot et guidances pour prendre des décisions éclairées.',
  publisher: {
    '@type': 'Organization',
    name: 'Plume Astrale',
    url: 'https://plume-astrale.fr',
  },
};

function ServiceList({ title, items, testid }) {
  const { addItem, items: cartItems } = useCart();

  return (
    <section className="home-gateway__group" aria-label={title} data-testid={testid}>
      <h3>{title}</h3>
      <ul>
        {items.map((item) => {
          const inCart = cartItems.some((entry) => entry.key === item.key);
          return (
            <li key={item.key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Link to={item.to} data-testid={`home-gateway-service-${item.key}`} style={{ flex: 1, minWidth: 0 }}>
                <span className="home-gateway__service-copy">
                  <strong>{item.title}</strong>
                  <span>{item.tagline}</span>
                </span>
                <span className="home-gateway__service-meta">
                  {item.price && <span>{item.price}</span>}
                  <ArrowRight size={16} aria-hidden="true" />
                </span>
              </Link>
              {item.price && (
                <button
                  type="button"
                  aria-label={inCart ? `${item.title} est dans le panier` : `Ajouter ${item.title} au panier`}
                  title={inCart ? 'Déjà dans le panier' : 'Ajouter au panier'}
                  data-testid={`home-gateway-add-${item.key}`}
                  onClick={() => addItem(item)}
                  disabled={inCart}
                  style={{ display: 'grid', width: 40, height: 40, flex: '0 0 40px', placeItems: 'center', border: '1px solid rgba(212,175,55,0.45)', borderRadius: 3, background: 'transparent', color: 'var(--plume-gold)', cursor: inCart ? 'default' : 'pointer', opacity: inCart ? 0.72 : 1 }}
                >
                  {inCart ? <Check size={17} aria-hidden="true" /> : <Plus size={17} aria-hidden="true" />}
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export default function HomeExperienceV3() {
  return (
    <>
      <SEO
        path="/"
        title="Plume Astrale — Lectures et services pour éclairer vos choix"
        description="Astrologie, tarot et guidances personnalisées pour mieux vous comprendre et prendre des décisions éclairées."
        canonical="https://plume-astrale.fr/"
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(JSONLD) }}
      />
      <main className="home-gateway" data-testid="home-gateway">
        <section className="home-gateway__hero" aria-labelledby="home-gateway-title">
          <p className="home-gateway__eyebrow"><Sparkles size={14} aria-hidden="true" /> Lectures · Tarot · Guidances</p>
          <h1 id="home-gateway-title">Plume Astrale</h1>
          <p className="home-gateway__promise">Mieux vous comprendre. <em>Choisir la suite.</em></p>
          <p className="home-gateway__description">
            Des lectures personnalisées et des services pour éclairer ce que vous traversez et prendre vos décisions avec plus de clarté.
          </p>
          <a href="#home-gateway-services" className="home-gateway__primary" data-testid="home-gateway-primary-cta">
            Voir tous les services <ArrowRight size={17} aria-hidden="true" />
          </a>
        </section>

        <section
          className="home-gateway__catalog"
          id="home-gateway-services"
          aria-labelledby="home-gateway-services-title"
          data-testid="home-gateway-services"
        >
          <header>
            <p className="home-gateway__eyebrow">À explorer</p>
            <h2 id="home-gateway-services-title">Choisissez votre éclairage</h2>
          </header>
          <div className="home-gateway__lists">
            <ServiceList title="Lectures personnalisées" items={LECTURES} testid="home-gateway-readings" />
            <ServiceList title="Guidances et outils" items={OUTILS} testid="home-gateway-tools" />
          </div>
        </section>
      </main>
    </>
  );
}