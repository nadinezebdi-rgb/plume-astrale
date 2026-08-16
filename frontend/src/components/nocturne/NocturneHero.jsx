import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

/**
 * NocturneHero — Hero Nocturne Éditorial (Feb 2026)
 * Direction artistique : page arrachée à un livre d'art au coucher du soleil.
 * - Fond Bleu Prussien Nocturne (#0B1A2E) avec halo Laiton discret
 * - Une seule question éditoriale, une seule voie
 * - Aucun compteur, aucune urgence, aucune sur-promesse
 */
export default function NocturneHero() {
  return (
    <section
      className="ne-section ne-section-night"
      data-testid="nocturne-hero"
      style={{ paddingTop: 'clamp(96px, 12vh, 160px)', paddingBottom: 'clamp(96px, 12vh, 160px)' }}
    >
      <div className="ne-container">
        <div className="ne-narrow" style={{ maxWidth: 820 }}>
          {/* Overline mono */}
          <div className="ne-overline ne-reveal ne-reveal-1" data-testid="nocturne-hero-overline">
            Acte I &middot; Le Seuil
          </div>

          {/* Question éditoriale */}
          <h1
            className="ne-display ne-reveal ne-reveal-2"
            data-testid="nocturne-hero-title"
            style={{ marginTop: 24, color: 'var(--ne-celeste)' }}
          >
            Que traversez-vous
            <br />
            <span className="ne-serif-italic" style={{ color: 'var(--ne-laiton)' }}>ce mois-ci</span>&nbsp;?
          </h1>

          {/* Filet Laiton */}
          <hr className="ne-rule-short ne-reveal ne-reveal-3" style={{ marginTop: 40, marginBottom: 32 }} />

          {/* Lead paragraphe */}
          <p
            className="ne-lead ne-reveal ne-reveal-4"
            data-testid="nocturne-hero-lead"
            style={{ marginTop: 0, marginBottom: 48, maxWidth: 640 }}
          >
            Plume Astrale ne prédit rien. Elle vous aide à <span className="ne-signature">lire ce qui traverse</span> —
            vos cycles, vos saisons intérieures, vos points d&rsquo;inflexion. Un livre qui s&rsquo;ouvre pour vous seul(e).
          </p>

          {/* CTA unique — proposition, jamais poussée */}
          <div className="ne-reveal ne-reveal-5" style={{ display: 'flex', flexWrap: 'wrap', gap: 16, alignItems: 'center' }}>
            <Link
              to="/theme-natal"
              className="ne-btn ne-btn-primary"
              data-testid="nocturne-hero-cta-primary"
            >
              Recevoir ma lecture
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.5} />
            </Link>
            <Link
              to="/nos-livres"
              className="ne-btn-ghost"
              data-testid="nocturne-hero-cta-ghost"
              style={{ color: 'var(--ne-celeste)' }}
            >
              Feuilleter la bibliothèque
            </Link>
          </div>

          {/* Coordonnées célestes discrètes — micro-labels mono */}
          <div
            className="ne-reveal ne-reveal-6"
            style={{
              marginTop: 96, display: 'flex', flexWrap: 'wrap',
              gap: 32, opacity: 0.65,
            }}
            data-testid="nocturne-hero-coords"
          >
            <span className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: 'rgba(245,240,230,0.5)' }}>
              47° 22&#39; N &middot; 05° 04&#39; E
            </span>
            <span className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: 'rgba(245,240,230,0.5)' }}>
              Édition Nocturne &middot; 2026
            </span>
            <span className="ne-mono" style={{ fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: 'rgba(245,240,230,0.5)' }}>
              Une lecture, un livre
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
