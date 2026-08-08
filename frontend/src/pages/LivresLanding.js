import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, ArrowRight, Sparkles, Gift, ShieldCheck } from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import PdfPreviewButton from '@/components/PdfPreviewButton';
import PdfFlipbook from '@/components/PdfFlipbook';

/**
 * /livres — Landing dédiée à la vente de rapports prestige comme livres imprimés
 * pour la campagne Noël. Présente les 6 rapports avec leur illustration hero,
 * un bouton de téléchargement d'aperçu 3 pages, et le lien vers la page produit.
 *
 * Palette V3 cream, Playfair Display, or #C9A24B.
 */
const BOOKS = [
  {
    slug: 'astrocartographie',
    productPath: '/astrocartographie',
    title: 'Astrocartographie',
    subtitle: 'Où vivre ta meilleure vie',
    tagline: 'Sept lignes planétaires tracées sur la carte du monde.',
    pages: '18 pages',
    price: '49€',
    heroPng: 'astrocarto_hero.png',
  },
  {
    slug: 'kabbale',
    productPath: '/kabbale',
    title: "Ton Arbre de Vie",
    subtitle: 'Kabbalistique',
    tagline: 'Dix séphiroth et vingt-deux chemins de conscience.',
    pages: '30 pages',
    price: '59€',
    heroPng: 'kabbale_hero.png',
  },
  {
    slug: 'karma-destin',
    productPath: '/karma-destin-pdf',
    title: 'Ton Analyse Karmique',
    subtitle: 'Destinée & Guérison',
    tagline: 'Nœuds lunaires, Saturne, Chiron, Pluton — le fil de ton âme.',
    pages: '25 pages',
    price: '54€',
    heroPng: 'karma_hero.png',
  },
  {
    slug: 'numerologie',
    productPath: '/numerologie-pdf',
    title: 'Ton Code Numérologique',
    subtitle: 'Cycles & Vibrations',
    tagline: 'Chemin de vie, année personnelle, biorythmes.',
    pages: '20 pages',
    price: '39€',
    heroPng: 'numerologie_hero.png',
  },
  {
    slug: 'theme-natal',
    productPath: '/theme-natal-luxe',
    title: 'Ton Thème Natal',
    subtitle: 'Ton ciel de naissance dévoilé',
    tagline: '38 pages sur les 12 signes, planètes, maisons et aspects.',
    pages: '38 pages',
    price: '69€',
    heroPng: 'natal_hero.png',
  },
  {
    slug: 'synastrie',
    productPath: '/synastrie',
    title: 'Votre Synastrie',
    subtitle: "L'astrologie de votre lien",
    tagline: "L'analyse détaillée de la rencontre entre deux ciels.",
    pages: '32 pages',
    price: '64€',
    heroPng: 'synastrie_hero.png',
  },
];

export default function LivresLanding() {
  const backend = process.env.REACT_APP_BACKEND_URL;
  const [flipbookBook, setFlipbookBook] = useState(null);

  return (
    <PsPageShell background="light">
      <SEO path="/livres" />

      {/* ═══ HERO ═══ */}
      <section
        data-testid="livres-hero"
        style={{
          padding: '110px 24px 40px',
          maxWidth: 960,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '6px 14px',
            borderRadius: 999,
            background: 'rgba(201,162,75,0.10)',
            border: '1px solid rgba(201,162,75,0.30)',
            color: '#8F6E24',
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: '0.18em',
            textTransform: 'uppercase',
            marginBottom: 20,
          }}
        >
          <BookOpen style={{ width: 12, height: 12 }} strokeWidth={2} />
          Édition prestige · offrir un livre
        </div>
        <h1
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(36px, 6vw, 58px)',
            color: '#0F1A3C',
            fontWeight: 500,
            lineHeight: 1.12,
            marginBottom: 20,
          }}
        >
          Nos livres <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>prestige</span>,{' '}
          <span style={{ display: 'block' }}>à offrir ou à s&apos;offrir.</span>
        </h1>
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 17,
            lineHeight: 1.65,
            color: '#232323',
            maxWidth: 620,
            margin: '0 auto 24px',
          }}
        >
          Six rapports personnalisés, chacun imprimé façon livre relié :
          couverture illustrée, sommaire romain, chapitres numérotés, papier
          crème. Un présent qui s&apos;ouvre — et qui se garde.
        </p>
        <div
          style={{
            display: 'inline-flex',
            gap: 20,
            flexWrap: 'wrap',
            justifyContent: 'center',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            letterSpacing: '0.10em',
            textTransform: 'uppercase',
            color: 'rgba(15,26,60,0.72)',
          }}
        >
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <Sparkles style={{ width: 14, height: 14, color: '#C9A24B' }} strokeWidth={1.8} />
            Aperçu 3 pages gratuit
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <Gift style={{ width: 14, height: 14, color: '#C9A24B' }} strokeWidth={1.8} />
            Option cadeau
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <ShieldCheck style={{ width: 14, height: 14, color: '#C9A24B' }} strokeWidth={1.8} />
            Livraison PDF immédiate
          </span>
        </div>
      </section>

      {/* ═══ GRILLE DES 6 LIVRES ═══ */}
      <section
        style={{
          padding: '32px 24px 96px',
          maxWidth: 1200,
          margin: '0 auto',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 28,
          }}
        >
          {BOOKS.map((b) => (
            <article
              key={b.slug}
              data-testid={`livres-card-${b.slug}`}
              style={{
                background: '#FFFFFF',
                border: '1px solid #E3E1DC',
                borderRadius: 18,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 16px 32px -20px rgba(15,26,60,0.10)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 24px 48px -20px rgba(15,26,60,0.18)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 16px 32px -20px rgba(15,26,60,0.10)';
              }}
            >
              {/* Cover thumbnail */}
              <div
                style={{
                  background: '#0F1A3C',
                  padding: 28,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  aspectRatio: '4 / 3',
                }}
              >
                <img
                  src={`${backend}/api/assets/pdf_covers/${b.heroPng}`}
                  alt={`Illustration ${b.title}`}
                  style={{
                    maxWidth: '75%',
                    maxHeight: '100%',
                    objectFit: 'contain',
                    filter: 'drop-shadow(0 12px 32px rgba(201,162,75,0.25))',
                  }}
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>

              {/* Contenu */}
              <div style={{ padding: '28px 26px', flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <p
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10,
                    fontWeight: 600,
                    letterSpacing: '0.20em',
                    textTransform: 'uppercase',
                    color: '#8F6E24',
                    marginBottom: 10,
                  }}
                >
                  {b.subtitle}
                </p>
                <h3
                  style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 24,
                    fontWeight: 500,
                    color: '#0F1A3C',
                    lineHeight: 1.2,
                    marginBottom: 10,
                  }}
                >
                  {b.title}
                </h3>
                <p
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14,
                    lineHeight: 1.55,
                    color: '#232323',
                    marginBottom: 18,
                    flexGrow: 1,
                  }}
                >
                  {b.tagline}
                </p>

                <div
                  style={{
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: 10,
                    marginBottom: 20,
                    paddingBottom: 16,
                    borderBottom: '1px dashed rgba(15,26,60,0.12)',
                  }}
                >
                  <span
                    style={{
                      fontFamily: 'Playfair Display, serif',
                      fontSize: 28,
                      fontWeight: 500,
                      color: '#0F1A3C',
                    }}
                  >
                    {b.price}
                  </span>
                  <span
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 12,
                      color: 'rgba(15,26,60,0.72)',
                    }}
                  >
                    · {b.pages}
                  </span>
                </div>

                {/* Actions */}
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 10,
                  }}
                >
                  <PdfPreviewButton
                    product={b.slug}
                    variant="ghost"
                    testid={`livres-preview-${b.slug}`}
                  />
                  <button
                    type="button"
                    onClick={() => setFlipbookBook(b)}
                    data-testid={`livres-flipbook-${b.slug}`}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 8,
                      padding: '11px 20px',
                      borderRadius: 999,
                      background: 'transparent',
                      color: '#0F1A3C',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 12,
                      fontWeight: 600,
                      letterSpacing: '0.10em',
                      textTransform: 'uppercase',
                      border: '1px solid #0F1A3C',
                      cursor: 'pointer',
                      transition: 'background 0.2s ease, color 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#0F1A3C';
                      e.currentTarget.style.color = '#F7F5F0';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = '#0F1A3C';
                    }}
                  >
                    <BookOpen style={{ width: 14, height: 14 }} strokeWidth={1.8} />
                    Feuilleter le livre
                  </button>
                  <Link
                    to={b.productPath}
                    data-testid={`livres-cta-${b.slug}`}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 10,
                      padding: '12px 22px',
                      borderRadius: 999,
                      background: '#C9A24B',
                      color: '#0F1A3C',
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 13,
                      fontWeight: 600,
                      letterSpacing: '0.10em',
                      textTransform: 'uppercase',
                      textDecoration: 'none',
                      boxShadow: '0 8px 20px -10px rgba(201,162,75,0.65)',
                      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      e.currentTarget.style.boxShadow = '0 12px 28px -10px rgba(201,162,75,0.80)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 8px 20px -10px rgba(201,162,75,0.65)';
                    }}
                  >
                    Découvrir
                    <ArrowRight style={{ width: 15, height: 15 }} strokeWidth={2} />
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ═══ CTA FINAL ═══ */}
      <section
        style={{
          padding: '32px 24px 96px',
          maxWidth: 780,
          margin: '0 auto',
          textAlign: 'center',
        }}
      >
        <p className="ps-eyebrow" style={{ marginBottom: 14 }}>Un présent qui reste</p>
        <h2
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(28px, 4vw, 40px)',
            color: '#0F1A3C',
            fontWeight: 500,
            lineHeight: 1.2,
            marginBottom: 14,
          }}
        >
          Un livre unique, <span style={{ fontStyle: 'italic', color: '#C9A24B' }}>écrit pour une seule personne au monde</span>.
        </h2>
        <p
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 16,
            lineHeight: 1.7,
            color: '#232323',
            marginBottom: 24,
          }}
        >
          Chaque rapport est généré à partir de la carte du ciel exacte du destinataire.
          Pas de modèle générique, pas de duplicata — le prénom se grave en dorure sur la couverture,
          les chapitres racontent son histoire à lui, à elle.
        </p>
        <div
          style={{
            display: 'inline-flex',
            gap: 14,
            flexWrap: 'wrap',
            justifyContent: 'center',
          }}
        >
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
            Commencer ma lecture
            <ArrowRight style={{ width: 15, height: 15 }} strokeWidth={2} />
          </Link>
        </div>
      </section>

      {/* ═══ FLIPBOOK MODAL ═══ */}
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
