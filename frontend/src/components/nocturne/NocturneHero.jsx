import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Clock3, ShieldCheck, Sparkles } from 'lucide-react';
import StarfieldBackdrop from '@/components/StarfieldBackdrop';

const PROOFS = [
  { value: '49', label: 'pages personnalisées' },
  { value: '< 60 s', label: 'pour recevoir votre livre' },
  { value: '5 pages', label: 'offertes pour commencer' },
];

/**
 * Hero concours 2026
 * Une promesse comprise en moins de trois secondes, un livrable tangible,
 * une action principale sans risque et une preuve immédiate de personnalisation.
 */
export default function NocturneHero() {
  return (
    <section className="ne-section ne-section-night ne-hero-premium" data-testid="nocturne-hero" style={{ position: 'relative', overflow: 'hidden' }}>
      <StarfieldBackdrop density={70} color="216, 183, 106" fade={0.45} />
      <div className="ne-container" style={{ position: 'relative', zIndex: 1 }}>
        <div className="ne-hero-premium-grid">
          <div className="ne-hero-premium-copy">
            <div className="ne-overline ne-reveal ne-reveal-1" data-testid="nocturne-hero-overline">
              Plume Astrale &middot; Atelier de personnalisation
            </div>

            <h1
              className="ne-display ne-reveal ne-reveal-2"
              data-testid="nocturne-hero-title"
              style={{ color: 'var(--ne-celeste)' }}
            >
              Votre ciel devient
              <span
                className="ne-hero-title-accent"
                style={{ fontFamily: '"Cormorant Garamond", "Playfair Display", Georgia, serif', fontStyle: 'italic', fontWeight: 500 }}
              > un livre.</span>
            </h1>

            <p className="ne-hero-premium-lead ne-reveal ne-reveal-3" data-testid="nocturne-hero-lead">
              À partir de vos données de naissance, Plume Astrale calcule, rédige et compose
              une lecture qui ne ressemble qu&rsquo;à vous — livrée par email en moins de 60 secondes.
            </p>

            <div className="ne-hero-actions ne-reveal ne-reveal-4">
              <Link
                to="/inscription"
                className="ne-btn ne-btn-primary ne-hero-primary"
                data-testid="nocturne-hero-cta-primary"
              >
                Créer mon aperçu offert
                <ArrowRight style={{ width: 17, height: 17 }} strokeWidth={1.7} />
              </Link>
              <Link
                to="/livres"
                className="ne-btn-ghost"
                data-testid="nocturne-hero-cta-ghost"
                style={{ color: 'var(--ne-celeste)' }}
              >
                <BookOpen style={{ width: 16, height: 16 }} strokeWidth={1.5} />
                Feuilleter un exemple
              </Link>
            </div>

            <Link
              to="/edition-reliee"
              className="ne-reveal ne-reveal-5"
              data-testid="nocturne-hero-cta-edition-reliee"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 10,
                marginTop: 18,
                padding: '10px 18px',
                borderRadius: 999,
                border: '1px solid rgba(196, 162, 92, 0.45)',
                background: 'linear-gradient(135deg, rgba(196, 162, 92, 0.14), rgba(196, 162, 92, 0.04))',
                color: 'var(--ne-or, #C4A25C)',
                fontFamily: 'Inter, sans-serif',
                fontSize: 12.5,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                textDecoration: 'none',
                fontWeight: 500,
                transition: 'transform 200ms ease, border-color 200ms ease, background 200ms ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.borderColor = 'rgba(196, 162, 92, 0.9)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.borderColor = 'rgba(196, 162, 92, 0.45)';
              }}
            >
              <Sparkles style={{ width: 14, height: 14 }} strokeWidth={1.6} />
              Voir l&rsquo;Édition Reliée — 149&nbsp;€
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={1.6} />
            </Link>

            <div className="ne-hero-reassurance ne-reveal ne-reveal-5">
              <span><ShieldCheck aria-hidden="true" /> Sans carte bancaire</span>
              <span><Clock3 aria-hidden="true" /> Livraison immédiate</span>
              <span><Sparkles aria-hidden="true" /> Lecture sur mesure</span>
            </div>

            <div className="ne-hero-proof-grid ne-reveal ne-reveal-6" data-testid="nocturne-hero-proofs">
              {PROOFS.map((proof) => (
                <div className="ne-hero-proof" key={proof.label}>
                  <strong>{proof.value}</strong>
                  <span>{proof.label}</span>
                </div>
              ))}
            </div>

            <p
              className="ne-reveal ne-reveal-7"
              data-testid="nocturne-hero-engine-note"
              style={{
                marginTop: 24,
                fontFamily: 'Inter, sans-serif',
                fontSize: 11.5,
                letterSpacing: '0.06em',
                color: 'rgba(247, 245, 240, 0.55)',
                lineHeight: 1.55,
                maxWidth: 520,
              }}
            >
              Moteur&nbsp;: basé sur la bibliothèque de précision <em style={{ color: 'rgba(247, 245, 240, 0.72)', fontStyle: 'italic' }}>Swiss Ephemeris</em> (norme NASA&nbsp;/&nbsp;JPL).
            </p>
          </div>

          <div className="ne-hero-book-stage ne-reveal ne-reveal-3" aria-label="Aperçu du livre personnalisé Plume Astrale">
            <div className="ne-hero-orbit ne-hero-orbit-outer" aria-hidden="true" />
            <div className="ne-hero-orbit ne-hero-orbit-inner" aria-hidden="true" />
            <div className="ne-hero-book-shadow" aria-hidden="true" />

            <div className="ne-hero-book">
              <div className="ne-hero-book-spine" aria-hidden="true" />
              <div className="ne-hero-book-cover">
                <img
                  data-image-slot="home.hero.book"
                  src="/images/astrale/image-astrale-3.jpg"
                  alt="Carte céleste bleu nuit et or illustrant une lecture Plume Astrale"
                />
                <div className="ne-hero-book-overlay" />
                <img
                  className="ne-hero-book-logo"
                  src="/branding/nocturne-v3-night-laiton.png"
                  alt="Plume Astrale"
                />
                <div className="ne-hero-book-kicker">Édition personnelle</div>
                <div className="ne-hero-book-name">Votre prénom</div>
                <div className="ne-hero-book-subtitle">Thème natal &middot; 49 pages</div>
              </div>
            </div>

            <div className="ne-hero-float-card ne-hero-float-card-top">
              <span className="ne-hero-float-dot" />
              Composition en cours
            </div>
            <div className="ne-hero-float-card ne-hero-float-card-bottom">
              <strong>Livré par email</strong>
              <span>PDF premium prêt à conserver</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
