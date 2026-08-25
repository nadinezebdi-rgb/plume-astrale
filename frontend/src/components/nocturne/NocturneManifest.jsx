import React from 'react';

/**
 * NocturneManifest — Manifeste éditorial (fond Papier Céleste).
 * Trois refus, trois inclinations — la promesse artistique.
 */
export default function NocturneManifest() {
  return (
    <section
      className="ne-section ne-section-paper"
      data-testid="nocturne-manifest"
    >
      <div className="ne-container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 380px)',
          gap: 'clamp(32px, 5vw, 80px)',
          alignItems: 'start',
        }} className="ne-manifest-hero">
          <div>
            <div className="ne-overline" data-testid="nocturne-manifest-overline">Acte II &middot; Le Manifeste</div>
            <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)', maxWidth: 720 }}>
              Nous croyons que chaque vie est un <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>texte</span>.
            </h2>
            <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
            <p className="ne-lead" style={{ marginBottom: 0 }}>
              Que ce texte a des chapitres, des saisons, des respirations.
              <br />
              Que le ciel n&rsquo;est pas un oracle mais un <em>calendrier poétique</em>.
              <br />
              Que comprendre son cycle n&rsquo;est pas prédire son destin&nbsp;: c&rsquo;est habiter son présent avec plus de justesse.
            </p>
          </div>

          {/* Portrait Soléna — présence éditoriale de l'auteure */}
          <figure
            data-testid="nocturne-manifest-portrait"
            style={{
              margin: 0,
              position: 'relative',
              padding: 10,
              background: 'linear-gradient(180deg, rgba(201,162,75,0.14) 0%, rgba(201,162,75,0.04) 100%)',
              borderRadius: 4,
              boxShadow: '0 24px 60px -20px rgba(15, 26, 60, 0.35), 0 0 0 1px rgba(201, 162, 75, 0.18)',
            }}
          >
            <picture>
              <source srcSet="/branding/solena-portrait.webp" type="image/webp" />
              <img
                src="/branding/solena-portrait.png"
                alt="Portrait de Soléna, guide éditoriale de Plume Astrale"
                loading="lazy"
                decoding="async"
                data-testid="nocturne-manifest-portrait-img"
                style={{
                  width: '100%',
                  height: 'auto',
                  display: 'block',
                  aspectRatio: '4 / 5',
                  objectFit: 'cover',
                  objectPosition: '50% 25%',
                  filter: 'saturate(0.92) contrast(1.02)',
                }}
              />
            </picture>
            <figcaption
              className="ne-mono"
              style={{
                marginTop: 14,
                textAlign: 'right',
                fontSize: 10,
                letterSpacing: '0.24em',
                color: 'var(--ne-laiton)',
                textTransform: 'uppercase',
              }}
            >
              — Soléna &middot; guide éditoriale
            </figcaption>
          </figure>
        </div>

        <style>{`
          @media (max-width: 880px) {
            .ne-manifest-hero {
              grid-template-columns: 1fr !important;
            }
          }
        `}</style>

        {/* Trois refus, éditorial */}
        <div className="ne-grid-3" style={{ marginTop: 96 }} data-testid="nocturne-manifest-tenets">
          {[
            {
              n: '01',
              title: 'Refus du déterminisme',
              body: 'Aucun mot n\'enferme dans un futur écrit. Nous nommons ce qui traverse, jamais ce qui doit arriver.',
            },
            {
              n: '02',
              title: 'Refus du kitsch ésotérique',
              body: 'Ni cristaux, ni cartes néon, ni prophéties spectaculaires. Une écriture littéraire, un artisanat sobre.',
            },
            {
              n: '03',
              title: 'Refus de la sur-promesse',
              body: 'La marque murmure, ne crie jamais. Un texte, une image, une invitation. Rien de plus.',
            },
          ].map((t) => (
            <div key={t.n} data-testid={`manifest-tenet-${t.n}`} style={{ padding: '32px 0' }}>
              <div className="ne-mono" style={{ fontSize: 11, letterSpacing: '0.24em', color: 'var(--ne-laiton)', marginBottom: 20 }}>
                {t.n}
              </div>
              <h3 className="ne-h3" style={{ color: 'var(--ne-fusain)', marginBottom: 12, fontFamily: 'var(--ne-serif)', fontWeight: 400, fontStyle: 'italic', fontSize: 22 }}>
                {t.title}
              </h3>
              <p className="ne-body" style={{ color: 'rgba(10,10,15,0.72)', fontSize: 15 }}>
                {t.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
