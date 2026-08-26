/**
 * ExperienceFallback — version sobre pour :
 *   - prefers-reduced-motion (utilisateur qui refuse les animations)
 *   - environnement sans WebGL
 *
 * Même contenu textuel, mêmes 4 sections, mêmes CTA — mais aucune
 * animation JS/GL, seulement des fondus CSS courts + un dégradé radial
 * de fond figé qui rappelle l'atmosphère cosmique.
 */
import React, { useState } from 'react';

export default function ExperienceFallback({
  intents, cards, onIntentChoice, onCardDraw, onFinalCTA, intent, drawnCard,
}) {
  const [expanded, setExpanded] = useState(1);

  return (
    <div className="exp-root" data-fallback="true" data-testid="experience-fallback">
      <header className="exp-topbar">
        <span className="exp-topbar__logo">
          PLUME <em style={{ fontStyle: 'italic', letterSpacing: '0.05em', color: 'var(--exp-gold)' }}>Astrale</em>
        </span>
        <a className="exp-topbar__exit" href="/">Retour au sanctuaire</a>
      </header>

      {/* Scène 1 */}
      <section className="exp-section exp-s1" data-testid="experience-scene-1">
        <div className="exp-section-inner">
          <p className="exp-eyebrow" style={{ marginBottom: 24 }}>
            PLUME <em style={{ fontStyle: 'italic', letterSpacing: '0.06em', color: 'var(--exp-gold)' }}>Astrale</em>
          </p>
          <p className="exp-h2" style={{ marginBottom: 20 }}>
            Certaines réponses ne se cherchent pas.
          </p>
          <p className="exp-h1" style={{ marginBottom: 36 }}>
            Elles <em>se révèlent.</em>
          </p>
          <button type="button" className="exp-btn" onClick={() => setExpanded(2)} data-testid="scene-1-cta">
            <span className="exp-btn__glyph">✦</span>
            Entrer dans mon univers
          </button>
        </div>
      </section>

      {/* Scène 2 */}
      {expanded >= 2 && (
        <section className="exp-section" data-testid="experience-scene-2">
          <div className="exp-section-inner">
            <p className="exp-lead" style={{ marginBottom: 20 }}>
              Vous n'êtes peut-être pas arrivé ici par hasard.
            </p>
            <p className="exp-h2" style={{ marginBottom: 40 }}>
              Qu'est-ce qui vous amène aujourd'hui&nbsp;?
            </p>
            <div className="exp-s2__grid" data-testid="scene-2-grid">
              {intents.map((it) => (
                <button
                  key={it.id}
                  className="exp-s2__choice exp-gilded"
                  data-testid={`scene-2-choice-${it.id}`}
                  onClick={() => { onIntentChoice(it.id); setExpanded(3); }}
                >
                  <span className="exp-s2__choice-glyph">{it.glyph}</span>
                  <span className="exp-s2__choice-label">{it.label}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Scène 3 */}
      {expanded >= 3 && (
        <section className="exp-section" data-testid="experience-scene-3">
          <div className="exp-section-inner">
            <p className="exp-lead" style={{ marginBottom: 40 }}>
              Il y a probablement une question à laquelle vous pensez en ce moment.
            </p>
            <div className="exp-s3__cards" data-testid="scene-3-cards">
              {cards.map((c) => (
                <button
                  key={c.id}
                  className="exp-s3__card"
                  data-testid={`scene-3-card-${c.id}`}
                  data-flipped={drawnCard === c.id}
                  disabled={drawnCard && drawnCard !== c.id}
                  onClick={() => onCardDraw(c.id)}
                >
                  <div className="exp-s3__back"><span className="exp-s3__back-mark">P</span></div>
                  <div className="exp-s3__face">
                    <span className="exp-s3__face-glyph">{c.glyph}</span>
                    <div>
                      <p className="exp-s3__face-name">{c.name}</p>
                      <p className="exp-s3__face-tagline">{c.tagline}</p>
                    </div>
                    <span className="exp-eyebrow" style={{ opacity: 0.6 }}>Plume Astrale</span>
                  </div>
                </button>
              ))}
            </div>
            {drawnCard && (
              <div className="exp-s3__result" data-visible="true" style={{ marginTop: 50 }}>
                <p className="exp-lead">Cette carte a quelque chose à vous montrer.</p>
                <button className="exp-linkline" onClick={() => setExpanded(4)}>
                  Continuer mon tirage <span>↓</span>
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Scène 4 */}
      {expanded >= 4 && (
        <section className="exp-section" data-testid="experience-scene-4">
          <div className="exp-section-inner exp-s4__stack">
            <p className="exp-s4__written" data-visible="true">PLUME <em>Astrale</em></p>
            <div className="exp-s4__phrases">
              <p className="exp-h2 exp-s4__phrase" data-visible="true">Votre histoire est unique.</p>
              <p className="exp-h2 exp-s4__phrase" data-visible="true">Votre ciel aussi.</p>
            </div>
            <div className="exp-s4__final-cta" data-visible="true">
              <button className="exp-btn" onClick={onFinalCTA} data-testid="scene-4-cta">
                <span className="exp-btn__glyph">✦</span> Commencer mon voyage
              </button>
              <button className="exp-linkline" onClick={onFinalCTA} data-testid="scene-4-cta-secondary">
                Découvrir Plume Astrale <span>→</span>
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
