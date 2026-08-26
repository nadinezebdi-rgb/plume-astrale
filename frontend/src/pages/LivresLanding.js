import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  Gift,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import PdfPreviewButton from '@/components/PdfPreviewButton';
import PdfFlipbook from '@/components/PdfFlipbook';
import PhysicalBookScene from '@/components/PhysicalBookScene';
import './LivresLanding.css';

const BOOKS = [
  {
    slug: 'astrocartographie',
    productPath: '/astrocartographie',
    title: 'Astrocartographie',
    shortTitle: 'Astrocartographie',
    subtitle: 'Où vivre ta meilleure vie',
    tagline: 'Sept lignes planétaires tracées sur la carte du monde.',
    insideLabel: 'Votre carte du monde personnelle',
    coverLabel: 'Atlas céleste personnalisé',
    pages: '18 pages',
    price: '49€',
    heroPng: 'astrocarto_hero.png',
    symbol: '✦',
    accent: '#d8b557',
    accentSoft: '#b68e31',
    tilt: '-7deg',
  },
  {
    slug: 'kabbale',
    productPath: '/kabbale',
    title: 'Ton Arbre de Vie',
    shortTitle: 'Arbre de Vie',
    subtitle: 'Kabbalistique',
    tagline: 'Dix séphiroth et vingt-deux chemins de conscience.',
    insideLabel: 'Les dix séphiroth révélées',
    coverLabel: 'Étude kabbalistique',
    pages: '30 pages',
    price: '59€',
    heroPng: 'kabbale_hero.png',
    symbol: '◇',
    accent: '#c7a357',
    accentSoft: '#95752e',
    tilt: '-5deg',
  },
  {
    slug: 'karma-destin',
    productPath: '/karma-destin-pdf',
    title: 'Ton Analyse Karmique',
    shortTitle: 'Analyse Karmique',
    subtitle: 'Destinée & Guérison',
    tagline: 'Nœuds lunaires, Saturne, Chiron, Pluton — le fil de ton âme.',
    insideLabel: 'Les mémoires de votre âme',
    coverLabel: 'Destinée et guérison',
    pages: '25 pages',
    price: '54€',
    heroPng: 'karma_hero.png',
    symbol: '☊',
    accent: '#d2ae56',
    accentSoft: '#9d762d',
    tilt: '-8deg',
  },
  {
    slug: 'numerologie',
    productPath: '/numerologie-pdf',
    title: 'Ton Code Numérologique',
    shortTitle: 'Code Numérologique',
    subtitle: 'Cycles & Vibrations',
    tagline: 'Chemin de vie, année personnelle, biorythmes.',
    insideLabel: 'Votre signature vibratoire',
    coverLabel: 'Cycles et vibrations',
    pages: '20 pages',
    price: '39€',
    heroPng: 'numerologie_hero.png',
    symbol: 'Ⅶ',
    accent: '#d8b557',
    accentSoft: '#a17b30',
    tilt: '-6deg',
  },
  {
    slug: 'theme-natal',
    productPath: '/theme-natal-luxe',
    title: 'Ton Thème Natal',
    shortTitle: 'Thème Natal',
    subtitle: 'Ton ciel de naissance dévoilé',
    tagline: '38 pages sur les 12 signes, planètes, maisons et aspects.',
    insideLabel: 'La carte de votre ciel de naissance',
    coverLabel: 'Édition céleste complète',
    pages: '38 pages',
    price: '69€',
    heroPng: 'natal_hero.png',
    symbol: '☉',
    accent: '#e0bc62',
    accentSoft: '#a88438',
    tilt: '-7deg',
  },
  {
    slug: 'synastrie',
    productPath: '/synastrie',
    title: 'Votre Synastrie',
    shortTitle: 'Synastrie',
    subtitle: "L'astrologie de votre lien",
    tagline: "L'analyse détaillée de la rencontre entre deux ciels.",
    insideLabel: 'Deux cartes du ciel, une rencontre',
    coverLabel: 'Étude relationnelle',
    pages: '32 pages',
    price: '64€',
    heroPng: 'synastrie_hero.png',
    symbol: '☾',
    accent: '#d4b568',
    accentSoft: '#9f8139',
    tilt: '-5deg',
  },
];

export default function LivresLanding() {
  const backend = process.env.REACT_APP_BACKEND_URL || '';
  const [flipbookBook, setFlipbookBook] = useState(null);

  return (
    <PsPageShell background="light">
      <SEO path="/livres" />

      <main className="livres-page">
        <section className="livres-hero" data-testid="livres-hero">
          <div className="livres-hero__eyebrow">
            <BookOpen strokeWidth={1.8} />
            Édition prestige · votre histoire reliée
          </div>

          <h1>
            Ce n&apos;est pas un simple rapport.
            <span className="block">
              C&apos;est <em>votre livre.</em>
            </span>
          </h1>

          <p className="livres-hero__lead">
            Un ouvrage astrologique personnel, imprimé comme un beau livre :
            couverture illustrée, pages crème et chapitres écrits à partir de
            votre ciel. À feuilleter, à offrir et à garder.
          </p>

          <div className="livres-hero__proofs" aria-label="Avantages des livres">
            <span>
              <Sparkles strokeWidth={1.8} />
              Aperçu 3 pages gratuit
            </span>
            <span>
              <Gift strokeWidth={1.8} />
              Option cadeau
            </span>
            <span>
              <ShieldCheck strokeWidth={1.8} />
              Livraison PDF immédiate
            </span>
          </div>
        </section>

        <section className="livres-tiers" data-testid="livres-tiers" aria-labelledby="livres-tiers-title">
          <header className="livres-tiers__intro">
            <span className="livres-tiers__eyebrow">Le Thème Natal · trois façons de le recevoir</span>
            <h2 id="livres-tiers-title">
              Un même livre. <em>Trois manières de l&apos;offrir.</em>
            </h2>
            <p className="livres-tiers__lead">
              49 pages, composées à partir d&apos;un ciel de naissance exact.
              L&apos;aperçu pour se faire une idée. Le numérique pour lire.
              L&apos;Édition Reliée pour offrir un objet qui reste.
            </p>
          </header>

          <div className="livres-tiers__grid">
            <article className="livres-tier" data-testid="livres-tier-apercu">
              <p className="livres-tier__eyebrow">Pour découvrir</p>
              <h3 className="livres-tier__title">Aperçu offert</h3>
              <p className="livres-tier__price">
                <span className="livres-tier__amount">0 €</span>
                <span className="livres-tier__unit">5 pages · PDF</span>
              </p>
              <ul className="livres-tier__list">
                <li>Sa carte du ciel imprimable</li>
                <li>Trois chapitres composés</li>
                <li>Livré par email en 60 secondes</li>
              </ul>
              <Link
                to="/inscription"
                className="livres-tier__cta livres-tier__cta--ghost"
                data-testid="livres-tier-apercu-cta"
              >
                Créer mon aperçu
                <ArrowRight strokeWidth={2} />
              </Link>
            </article>

            <article className="livres-tier" data-testid="livres-tier-numerique">
              <p className="livres-tier__eyebrow">Pour lire</p>
              <h3 className="livres-tier__title">Édition Numérique</h3>
              <p className="livres-tier__price">
                <span className="livres-tier__amount">49 €</span>
                <span className="livres-tier__unit">49 pages · PDF haute résolution</span>
              </p>
              <ul className="livres-tier__list">
                <li>Onze chapitres complets</li>
                <li>Carte du ciel à imprimer</li>
                <li>Relu à la main avant envoi</li>
                <li>À télécharger, à conserver, à réimprimer</li>
              </ul>
              <Link
                to="/theme-natal-luxe"
                className="livres-tier__cta livres-tier__cta--ghost"
                data-testid="livres-tier-numerique-cta"
              >
                Commander le PDF
                <ArrowRight strokeWidth={2} />
              </Link>
            </article>

            <article
              className="livres-tier livres-tier--featured"
              data-testid="livres-tier-reliee"
            >
              <span className="livres-tier__badge">Le cadeau qui reste</span>
              <p className="livres-tier__eyebrow">Pour offrir</p>
              <h3 className="livres-tier__title">Édition Reliée</h3>
              <p className="livres-tier__price">
                <span className="livres-tier__amount">149 €</span>
                <span className="livres-tier__unit">Livre imprimé, cousu, numéroté</span>
              </p>
              <ul className="livres-tier__list">
                <li>Tout ce que contient l&apos;Édition Numérique</li>
                <li>Livre relié à la main dans son coffret</li>
                <li>Carte du ciel grand format à encadrer</li>
                <li>Votre dédicace imprimée en tête d&apos;ouvrage</li>
                <li>
                  <b>Vous lisez avant qu&apos;on imprime</b> · garantie 72 h
                </li>
              </ul>
              <Link
                to="/edition-reliee"
                className="livres-tier__cta livres-tier__cta--primary"
                data-testid="livres-tier-reliee-cta"
              >
                Voir l&apos;Édition Reliée
                <ArrowRight strokeWidth={2} />
              </Link>
            </article>
          </div>

          <p className="livres-tiers__note">
            Vous n&apos;avez pas son heure de naissance ?{' '}
            <Link to="/carte-cadeau" data-testid="livres-tiers-giftcard-link">
              La carte cadeau
            </Link>{' '}
            laisse la destinataire renseigner ses données elle-même.
          </p>
        </section>

        <section className="livres-collection" aria-labelledby="collection-title">
          <header className="livres-collection__intro">
            <div>
              <span className="livres-collection__eyebrow">
                La collection Plume Astrale
              </span>
              <h2 id="collection-title">
                Six portes d&apos;entrée vers votre histoire céleste.
              </h2>
            </div>
            <p>
              Chaque ouvrage est composé pour une seule personne. Choisissez
              celui qui répond à votre question du moment, puis découvrez son
              aperçu avant de commencer.
            </p>
          </header>

          <div className="livres-grid">
            {BOOKS.map((book) => (
              <article
                key={book.slug}
                className="livres-card"
                data-testid={`livres-card-${book.slug}`}
              >
                <PhysicalBookScene
                  book={book}
                  coverSrc={`${backend}/api/assets/pdf_covers/${book.heroPng}`}
                />

                <div className="livres-card__content">
                  <div className="livres-card__topline">
                    <p className="livres-card__category">{book.subtitle}</p>
                    <span className="livres-card__edition">Livre personnalisé</span>
                  </div>

                  <h3>{book.title}</h3>
                  <p className="livres-card__tagline">{book.tagline}</p>

                  <div className="livres-card__meta">
                    <span className="livres-card__price">{book.price}</span>
                    <span className="livres-card__meta-mark" aria-hidden="true" />
                    <span className="livres-card__pages">{book.pages}</span>
                    <span className="livres-card__material">
                      Couverture reliée · papier crème
                    </span>
                  </div>

                  <div className="livres-card__actions">
                    <PdfPreviewButton
                      product={book.slug}
                      variant="ghost"
                      testid={`livres-preview-${book.slug}`}
                    />

                    <button
                      type="button"
                      onClick={() => setFlipbookBook(book)}
                      className="livres-card__flip"
                      data-testid={`livres-flipbook-${book.slug}`}
                    >
                      <BookOpen strokeWidth={1.8} />
                      Feuilleter
                    </button>

                    <Link
                      to={book.productPath}
                      className="livres-card__cta"
                      data-testid={`livres-cta-${book.slug}`}
                    >
                      Découvrir
                      <ArrowRight strokeWidth={2} />
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="livres-final-cta">
          <div className="livres-final-cta__inner">
            <p className="ps-eyebrow">Un présent qui reste</p>
            <h2>
              Un livre unique,{' '}
              <em>écrit pour une seule personne au monde.</em>
            </h2>
            <p>
              Chaque rapport est construit à partir de la carte du ciel exacte
              du destinataire. Le prénom s&apos;inscrit sur la couverture et
              les chapitres racontent une histoire qui ne ressemble à aucune
              autre.
            </p>
            <div className="livres-final-cta__actions">
              <Link
                to="/credits"
                data-testid="livres-cta-credits"
                className="ps-btn ps-btn-outline"
                style={{ padding: '13px 26px' }}
              >
                Comprendre les crédits
              </Link>
              <Link
                to="/inscription"
                data-testid="livres-cta-signup"
                className="ps-btn ps-btn-primary"
                style={{ padding: '13px 26px' }}
              >
                Créer mon livre
                <ArrowRight style={{ width: 15, height: 15 }} strokeWidth={2} />
              </Link>
            </div>
          </div>
        </section>
      </main>

      {flipbookBook && (
        <PdfFlipbook
          product={flipbookBook.slug}
          title={flipbookBook.title}
          onClose={() => setFlipbookBook(null)}
          testid="livres-flipbook-modal"
        />
      )}
    </PsPageShell>
  );
}
