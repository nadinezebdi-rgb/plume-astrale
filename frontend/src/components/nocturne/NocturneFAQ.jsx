/**
 * NocturneFAQ — FAQ homepage qui répond aux questions honnêtes.
 *
 * Priorité éditoriale : la première question est "Qui est Soléna ?" —
 * on transforme la transparence sur l'IA en avantage compétitif plutôt
 * qu'en information cachée. Aucune personnification, zéro ambiguïté.
 *
 * Design Nocturne Éditorial : fond Papier céleste (crème), texte navy,
 * accents dorés, transitions douces sur ouverture/fermeture.
 *
 * data-testid: nocturne-faq, nocturne-faq-item-{index}
 */
import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const FAQ_ITEMS = [
  {
    q: 'Qui est Soléna ?',
    a: (
      <>
        <p>
          <strong>Soléna est la voix éditoriale de Plume Astrale, propulsée par une intelligence artificielle</strong>.
          Ce n&apos;est ni une personne réelle, ni une astrologue diplômée, ni une voyante, ni une thérapeute.
        </p>
        <p style={{ marginTop: 12 }}>
          Concrètement, chaque lecture est composée en deux temps&nbsp;:
        </p>
        <ol style={{ paddingLeft: 20, marginTop: 10, lineHeight: 1.7 }}>
          <li>Vos positions planétaires exactes sont calculées par <em>Swiss Ephemeris</em>, la bibliothèque astronomique de précision qui suit la norme NASA (JPL) et est utilisée en recherche universitaire.</li>
          <li>Un modèle de langage (OpenAI GPT) piloté par nos prompts éditoriaux traduit ces données en un texte littéraire, à partir du vocabulaire, du ton et du cadre que nous avons composés pour Soléna.</li>
        </ol>
        <p style={{ marginTop: 12 }}>
          Aucun texte pré-écrit, aucune variation par signe&nbsp;: chaque phrase est générée pour vous, à partir de vos données exactes.
        </p>
      </>
    ),
  },
  {
    q: 'L\'astrologie chez Plume Astrale, c\'est prédictif ou symbolique ?',
    a: (
      <>
        <p>
          <strong>Purement symbolique et éditorial.</strong> Nous ne prédisons rien&nbsp;: nous traduisons les mouvements planétaires en un langage
          qui vous aide à mieux nommer ce que vous traversez. Aucune allégation médicale, psychologique ou divinatoire n&apos;est faite.
        </p>
        <p style={{ marginTop: 12 }}>
          Si vous cherchez un accompagnement thérapeutique ou médical, consultez un professionnel de santé.
        </p>
      </>
    ),
  },
  {
    q: 'Que se passe-t-il avec mes données de naissance ?',
    a: (
      <>
        <p>
          Vos données de naissance (date, heure, ville) servent <strong>uniquement au calcul astronomique local</strong> et à la génération de votre texte personnalisé.
          Elles ne sont <strong>jamais transmises à un tiers publicitaire</strong> (ni Meta, ni Google Ads).
        </p>
        <p style={{ marginTop: 12 }}>
          Détails complets dans notre <a href="/confidentialite" style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3 }}>Politique de confidentialité</a>.
        </p>
      </>
    ),
  },
  {
    q: 'Combien de temps prend la génération de mon PDF ?',
    a: (
      <>
        <p>
          <strong>Moins d&apos;une minute</strong> pour la plupart des lectures. Les commandes complexes (livre premium à partir de 49 pages) peuvent demander jusqu&apos;à 3 minutes.
        </p>
        <p style={{ marginTop: 12 }}>
          Le PDF vous est ensuite envoyé par email et reste accessible dans votre espace <em>Ma Bibliothèque</em>.
        </p>
      </>
    ),
  },
  {
    q: 'Puis-je être remboursé si le texte ne me convient pas ?',
    a: (
      <>
        <p>
          Oui. <strong>Garantie satisfaction de 14 jours</strong>, sans justification.
          Écrivez à <a href="mailto:contact@plume-astrale.fr" style={{ color: '#C9A24B', textDecoration: 'underline', textUnderlineOffset: 3 }}>contact@plume-astrale.fr</a>
          &nbsp;dans les 14 jours suivant votre commande, nous vous remboursons intégralement.
        </p>
      </>
    ),
  },
];

export default function NocturneFAQ() {
  const [open, setOpen] = useState(0);

  return (
    <section
      className="ne-section ne-section-paper"
      data-testid="nocturne-faq"
      style={{
        paddingTop: 'clamp(72px, 9vw, 112px)',
        paddingBottom: 'clamp(72px, 9vw, 112px)',
      }}
    >
      <div className="ne-container" style={{ maxWidth: 860 }}>
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 11, fontWeight: 500,
            letterSpacing: '0.32em', textTransform: 'uppercase',
            color: '#B8935A',
            marginBottom: 20,
          }}
        >
          Nos réponses honnêtes
        </p>
        <h2
          className="ne-h1"
          style={{
            color: '#0F1A3C',
            marginBottom: 48,
            fontSize: 'clamp(2rem, 3.6vw, 2.6rem)',
          }}
        >
          Ce que <span className="ne-serif-italic" style={{ color: '#C9A24B' }}>vous méritez</span> de savoir
        </h2>

        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {FAQ_ITEMS.map((item, i) => {
            const isOpen = open === i;
            return (
              <li
                key={i}
                data-testid={`nocturne-faq-item-${i}`}
                style={{
                  borderTop: '1px solid rgba(15, 26, 60, 0.10)',
                  padding: '24px 0',
                  ...(i === FAQ_ITEMS.length - 1 && { borderBottom: '1px solid rgba(15, 26, 60, 0.10)' }),
                }}
              >
                <button
                  type="button"
                  onClick={() => setOpen(isOpen ? -1 : i)}
                  aria-expanded={isOpen}
                  data-testid={`nocturne-faq-toggle-${i}`}
                  style={{
                    all: 'unset',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    width: '100%',
                    gap: 24,
                  }}
                >
                  <h3
                    style={{
                      fontFamily: 'Playfair Display, serif',
                      fontSize: 'clamp(18px, 2.2vw, 22px)',
                      fontWeight: 500,
                      color: '#0F1A3C',
                      margin: 0,
                      lineHeight: 1.35,
                    }}
                  >
                    {item.q}
                  </h3>
                  <ChevronDown
                    size={20}
                    strokeWidth={1.6}
                    color="#C9A24B"
                    style={{
                      flexShrink: 0,
                      transition: 'transform 300ms cubic-bezier(0.16, 1, 0.3, 1)',
                      transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    }}
                  />
                </button>
                <div
                  style={{
                    overflow: 'hidden',
                    maxHeight: isOpen ? 1000 : 0,
                    opacity: isOpen ? 1 : 0,
                    transition: 'max-height 400ms cubic-bezier(0.4, 0, 0.2, 1), opacity 300ms ease',
                  }}
                >
                  <div
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 15.5,
                      lineHeight: 1.7,
                      color: 'rgba(15, 26, 60, 0.78)',
                      marginTop: 16,
                      maxWidth: 680,
                    }}
                  >
                    {item.a}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
