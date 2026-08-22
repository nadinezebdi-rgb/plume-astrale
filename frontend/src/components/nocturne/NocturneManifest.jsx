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
        <div style={{ maxWidth: 780 }}>
          <div className="ne-overline" data-testid="nocturne-manifest-overline">Acte II &middot; Le Manifeste</div>
          <h2 className="ne-h1" style={{ marginTop: 24, color: 'var(--ne-fusain)', maxWidth: 720 }}>
            Nous croyons que chaque vie est un <span className="ne-serif-italic" style={{ color: 'var(--ne-vigne)' }}>texte</span>.
          </h2>
          <hr className="ne-rule-short" style={{ marginTop: 32, marginBottom: 32 }} />
          <p className="ne-lead" style={{ marginBottom: 48 }}>
            Que ce texte a des chapitres, des saisons, des respirations.
            <br />
            Que le ciel n&rsquo;est pas un oracle mais un <em>calendrier poétique</em>.
            <br />
            Que comprendre son cycle n&rsquo;est pas prédire son destin&nbsp;: c&rsquo;est habiter son présent avec plus de justesse.
          </p>
        </div>

        {/* Trois refus, éditorial */}
        <div className="ne-grid-3" style={{ marginTop: 64 }} data-testid="nocturne-manifest-tenets">
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
