import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * NocturneServices — Les trois lectures principales, format éditorial.
 * Fond Nuit. Cartes Astre avec filet Laiton.
 */
const LECTURES = [
  {
    n: '01',
    titre: 'Thème Natal',
    murmure: 'Onze planètes qui composent votre signature dans le ciel.',
    detail: 'PDF de 49 pages. Livré par email, à conserver, à imprimer, à relire.',
    prix: '39 €',
    to: '/theme-natal',
  },
  {
    n: '02',
    titre: 'Voyage Karmique',
    murmure: 'Votre Arbre de Vie et votre lignée d\'âme, réunis en un seul livre.',
    detail: 'Fusion Kabbale + Karma Destin. 39 pages composées à la main.',
    prix: '49 €',
    to: '/voyage-karmique',
    highlight: true,
  },
  {
    n: '03',
    titre: 'Astrocartographie',
    murmure: 'Où vivre votre meilleure vie — sept lignes planétaires sur le monde.',
    detail: 'Carte du monde annotée + interprétation littéraire par ville.',
    prix: '49 €',
    to: '/astrocartographie',
  },
];

export default function NocturneServices() {
  return (
    <section
      className="ne-section ne-section-night"
      data-testid="nocturne-services"
    >
      <div className="ne-container">
        <div style={{ maxWidth: 720, marginBottom: 96 }}>
          <div className="ne-overline" data-testid="nocturne-services-overline">Acte III &middot; Les Lectures</div>
          <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-celeste)' }}>
            Trois livres.
            <br />
            <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>Le vôtre, à choisir.</span>
          </h2>
          <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
          <p className="ne-lead" style={{ color: 'rgba(245,240,230,0.82)' }}>
            Chaque lecture est un PDF premium composé sur vos données de naissance exactes.
            Livraison instantanée. À télécharger, archiver, imprimer.
          </p>
        </div>

        <div className="ne-grid-3" style={{ gap: 24 }}>
          {LECTURES.map((l) => (
            <Link
              key={l.n}
              to={l.to}
              data-testid={`service-nocturne-${l.n}`}
              className={l.highlight ? 'ne-card ne-card-sealed' : 'ne-card'}
              style={{
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: 20,
                minHeight: 320,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div className="ne-mono" style={{ fontSize: 11, letterSpacing: '0.24em', color: 'var(--ne-laiton)' }}>
                  {l.n}
                </div>
                {l.highlight && (
                  <div className="ne-mono" style={{ fontSize: 9, letterSpacing: '0.28em', color: 'var(--ne-laiton)', textTransform: 'uppercase' }}>
                    Recommandé
                  </div>
                )}
              </div>

              <h3 className="ne-h2" style={{ color: 'var(--ne-celeste)', fontSize: 32, lineHeight: 1.15 }}>
                {l.titre}
              </h3>

              <p className="ne-serif-italic" style={{ color: 'rgba(245,240,230,0.85)', fontSize: 18, lineHeight: 1.5, margin: 0 }}>
                {l.murmure}
              </p>

              <p className="ne-caption" style={{ marginTop: 'auto' }}>
                {l.detail}
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingTop: 20, borderTop: '1px solid rgba(184,147,90,0.25)' }}>
                <span style={{ fontFamily: 'var(--ne-serif)', fontWeight: 400, fontSize: 26, color: 'var(--ne-laiton)' }}>
                  {l.prix}
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--ne-laiton)', fontFamily: 'var(--ne-sans)', fontSize: 13, fontWeight: 500 }}>
                  Lire
                  <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
                </span>
              </div>
            </Link>
          ))}
        </div>

        <div style={{ marginTop: 64, textAlign: 'left' }}>
          <Link to="/livres" className="ne-btn-ghost" data-testid="nocturne-services-all" style={{ color: 'var(--ne-celeste)' }}>
            Voir toute la bibliothèque
            <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.5} />
          </Link>
        </div>
      </div>
    </section>
  );
}
