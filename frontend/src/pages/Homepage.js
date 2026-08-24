import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight, Sparkles, Feather, BookOpen, Compass, Heart,
  Star, ShieldCheck, Clock, Mail,
} from 'lucide-react';
import SEO from '@/components/SEO';
import CelestialBackdrop from '@/components/CelestialBackdrop';
import LiveConstellation from '@/components/LiveConstellation';
import PdfFlipbook from '@/components/PdfFlipbook';
import CinematicHero from '@/components/CinematicHero';
import PremiumPillars from '@/components/PremiumPillars';
import SolenaGuideCard from '@/components/SolenaGuideCard';
import HomepageMiniQuiz from '@/components/HomepageMiniQuiz';
import TrustBar from '@/components/TrustBar';
import HowItWorks3Tiers from '@/components/HowItWorks3Tiers';
// Nocturne Éditorial — Feb 2026
import NocturneHero from '@/components/nocturne/NocturneHero';
import NocturneManifest from '@/components/nocturne/NocturneManifest';
import NocturneServices from '@/components/nocturne/NocturneServices';
import NocturneClosing from '@/components/nocturne/NocturneClosing';
import NocturneLeadMagnet from '@/components/nocturne/NocturneLeadMagnet';
import ContestVoteBanner from '@/components/ContestVoteBanner';
import { BLOG_ARTICLES } from '@/config/blogArticles';
import { useAuth } from '@/context/AuthContext';

/**
 * Homepage v3 — Refonte identité visuelle Feb 2026
 *
 * Grammaire : élégance lettrée + profondeur céleste nocturne.
 * Sections horizontales pleine largeur alternant clair (#F7F5F0) / sombre (#0F1A3C).
 * Playfair Display pour les titres, Inter pour le corps.
 * Un seul CTA doré par section. Grille 12 colonnes, max 1200px.
 */

const VALUE_PILLARS = [
  {
    icon: Feather,
    title: 'Analyse personnalisée',
    body: 'Composée à partir de vos données de naissance exactes (date, heure, lieu) — pas une variation générique par signe. Chaque lecture est unique.',
  },
  {
    icon: Compass,
    title: 'Guidance actionnable',
    body: 'Vos cycles, vos points d\'inflexion, vos leviers de décision. Pas de prédictions — un cadre pour lire les périodes qui comptent.',
  },
  {
    icon: Heart,
    title: 'Livraison sous 60 secondes',
    body: 'PDF premium reçu instantanément par email dès validation du paiement. À télécharger, archiver, imprimer — vous en gardez la propriété à vie.',
  },
];

const SERVICES = [
  {
    title: 'Thème Natal',
    desc: 'Onze planètes qui racontent qui tu es vraiment.',
    price: '29€',
    to: '/theme-natal',
  },
  {
    title: 'Arbre de Vie · Kabbale',
    desc: 'Tes dix Sephiroth posées sur ta cartographie d\'âme.',
    price: '39€',
    to: '/kabbale',
  },
  {
    title: 'Astrocartographie',
    desc: 'Où vivre ta meilleure vie — sept lignes planétaires.',
    price: '49€',
    to: '/astrocartographie',
  },
  {
    title: 'Karma & Destin',
    desc: 'Ta lignée karmique, Nœud Nord et mission de vie.',
    price: '29€',
    to: '/karma-destin',
  },
  {
    title: 'Compatibilité amoureuse',
    desc: 'Vos deux ciels comparés — affinités, tensions, karma.',
    price: '49€',
    to: '/compatibilite-amoureuse',
  },
  {
    title: 'Numérologie',
    desc: 'Chemin de vie, expression, âme, année personnelle.',
    price: '29€',
    to: '/numerologie',
  },
];

const TESTIMONIALS = [];  // Concours 2026 : aucun témoignage codé en dur.

export default function Homepage() {
  const { user } = useAuth();
  const signupPath = user ? '/mon-compte' : '/inscription';
  const [flipbookBook, setFlipbookBook] = useState(null);

  const FEATURED_BOOKS = [
    { slug: 'theme-natal',       title: 'Thème Natal',              tagline: '49 pages · 11 planètes décodées',   price: '39€', to: '/theme-natal' },
    { slug: 'kabbale',           title: 'Arbre de Vie · Kabbale',   tagline: '10 Sephiroth · 22 chemins',         price: '39€',    to: '/kabbale' },
    { slug: 'astrocartographie', title: 'Astrocartographie',        tagline: '7 lignes planétaires sur le monde', price: '49€',    to: '/astrocartographie' },
  ];

  return (
    <div className="ps-home" data-testid="homepage-v2">
      <SEO
        path="/"
        title="Plume Astrale · Lectures astrologiques personnalisées en PDF"
        description="Une lecture astrologique personnalisée, composée à partir de votre thème natal exact. PDF premium livré en 60 secondes · garantie 14 jours · paiement Stripe sécurisé."
      />

      {/* ═══ SECTION 1 · HERO NOCTURNE ÉDITORIAL (Feb 2026 — refonte artistique) ═══ */}
      <NocturneHero />

      {/* Floating CTA — concours Emergent Building France */}
      <ContestVoteBanner />

      {/* ═══ SECTION 1.05 · MANIFESTE NOCTURNE — les trois refus fondateurs ═══ */}
      <NocturneManifest />

      {/* ═══ SECTION 1.1 · TRUST BAR (F500 audit 2026-02) — garanties + livraison + support ═══ */}
      <TrustBar variant="dense" />

      {/* ═══ SECTION 1.5 · SOLÉNA (apparition douce au scroll) ═══ */}
      <SolenaGuideCard />

      {/* ═══ SECTION 1.7 · 4 PILIERS PREMIUM ═══ */}
      <PremiumPillars />

      {/* ═══ SECTION 1.75 · COMMENT ÇA MARCHE (F500 clarté PDF vs Crédits vs Gratuit) ═══ */}
      <HowItWorks3Tiers />

      {/* ═══ SECTION 1.77 · TROIS LECTURES NOCTURNE (remplace ancienne section services) ═══ */}
      <NocturneServices />

      {/* ═══ SECTION 1.8 · MINI-QUIZ (Preview onboarding — conversion précoce) ═══ */}
      <HomepageMiniQuiz />

      {/* ═══ SECTION 2 · PROPOSITION DE VALEUR (CLAIRE) ═══ */}
      <section className="ps-section ps-section-light" data-testid="ps-value">
        <div className="ps-container">
          <div style={{ maxWidth: 680, marginBottom: 64 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Trois engagements, tenus à chaque page</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Une lecture personnelle, <span className="ps-italic">jamais générique.</span>
            </h2>
            <p className="ps-body" style={{ color: '#232323' }}>
              Votre thème natal n&apos;est comparable à aucun autre — votre lecture ne l&apos;est pas non plus.
              Chaque PDF est calculé sur vos données exactes de naissance et rédigé sur mesure.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 32,
          }}>
            {VALUE_PILLARS.map((pillar) => {
              const Icon = pillar.icon;
              return (
                <div key={pillar.title} className="ps-card" data-testid={`value-${pillar.title.toLowerCase().replace(/\s+/g, '-')}`}>
                  <div style={{
                    width: 48, height: 48,
                    borderRadius: 12,
                    background: '#F7F5F0',
                    border: '1px solid #E3E1DC',
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: 20,
                  }}>
                    <Icon style={{ width: 22, height: 22, color: '#C9A24B' }} strokeWidth={1.6} />
                  </div>
                  <h3 className="ps-h3" style={{ color: '#0F1A3C', marginBottom: 12 }}>{pillar.title}</h3>
                  <p style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 15, lineHeight: 1.6,
                    color: '#6B7280',
                    margin: 0,
                  }}>
                    {pillar.body}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══ SECTION 3 · SUPPRIMÉE (2026-02-14) — Soléna n'est pas astrologue,
              c'est un avatar / une voix éditoriale. Aucune claim d'action humaine. ═══ */}

      {/* ═══ SECTION 4 · REMPLACÉE PAR NocturneServices (voir plus haut, section 1.77) ═══ */}


      {/* ═══ SECTION 4bis · FEUILLETAGE DES LIVRES (SOMBRE) ═══ */}
      <section className="ps-section ps-section-dark" data-testid="ps-flipbook-teaser">
        <CelestialBackdrop density={90} shootingStars={false} />
        <div className="ps-container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ marginBottom: 56, maxWidth: 680 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Feuilleter avant d&apos;acheter</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 16 }}>
              Un extrait, comme si tu tenais le <span className="ps-italic">livre</span> entre tes mains.
            </h2>
            <p className="ps-body" style={{ color: 'rgba(247,245,240,0.78)' }}>
              Chaque lecture est composée comme un vrai livre — couverture personnalisée, table
              des matières, ornements dorés. Ouvre-en un pour toucher la matière.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 24,
          }}>
            {FEATURED_BOOKS.map((b) => (
              <div key={b.slug}
                data-testid={`home-flipbook-card-${b.slug}`}
                style={{
                  background: 'rgba(247,245,240,0.04)',
                  border: '1px solid rgba(201,162,75,0.20)',
                  borderRadius: 14,
                  padding: 28,
                  display: 'flex', flexDirection: 'column', gap: 16,
                  transition: 'border-color 0.3s ease, transform 0.3s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(201,162,75,0.55)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(201,162,75,0.20)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <BookOpen style={{ width: 20, height: 20, color: '#C9A24B' }} strokeWidth={1.6} />
                  <span style={{
                    fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                    letterSpacing: '0.14em', textTransform: 'uppercase',
                    color: 'rgba(247,245,240,0.55)',
                  }}>Livre imprimé</span>
                </div>

                <div>
                  <h3 style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 22, fontWeight: 500, color: '#F7F5F0',
                    margin: 0, marginBottom: 6, lineHeight: 1.25,
                  }}>{b.title}</h3>
                  <p style={{
                    fontFamily: 'Inter, sans-serif', fontSize: 13,
                    color: 'rgba(247,245,240,0.62)',
                    margin: 0,
                  }}>{b.tagline}</p>
                </div>

                <div style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 24, color: '#C9A24B', fontStyle: 'italic',
                }}>{b.price}</div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 4 }}>
                  <button
                    type="button"
                    onClick={() => setFlipbookBook(b)}
                    data-testid={`home-flipbook-open-${b.slug}`}
                    style={{
                      flex: '1 1 auto',
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                      padding: '11px 18px', borderRadius: 999,
                      background: '#C9A24B', color: '#0F1A3C',
                      fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 600,
                      letterSpacing: '0.10em', textTransform: 'uppercase',
                      border: 'none', cursor: 'pointer',
                      transition: 'background 0.2s ease, transform 0.2s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = '#B58F3F'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = '#C9A24B'; }}
                  >
                    Feuilleter
                    <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                  </button>
                  <Link
                    to={b.to}
                    data-testid={`home-flipbook-detail-${b.slug}`}
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: 6,
                      padding: '11px 16px',
                      color: 'rgba(247,245,240,0.85)',
                      fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 500,
                      letterSpacing: '0.10em', textTransform: 'uppercase',
                      textDecoration: 'none',
                    }}
                  >
                    Détails
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 40 }}>
            <Link to="/livres" className="ps-btn ps-btn-outline"
              data-testid="home-flipbook-all-cta"
              style={{ color: '#F7F5F0', borderColor: 'rgba(247,245,240,0.4)' }}>
              Voir toute la bibliothèque
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 5 · TÉMOIGNAGES ═══
          Retirée pendant le concours 2026 : aucun avis codé en dur,
          aucune métrique non prouvée (4,9/5 sur 2 400 lectures). La section
          reviendra dès que des vrais témoignages seront collectés via
          /temoignages (soumission user → approbation admin). */}

      {/* ═══ SECTION 5.5 · ARTICLES BLOG À LA UNE (P8 maillage interne) ═══ */}
      <section
        className="ps-section ps-section-light"
        data-testid="ps-featured-articles"
        style={{ borderTop: '1px solid #E3E1DC' }}
      >
        <div className="ps-container">
          <div style={{ marginBottom: 40, display: 'flex', justifyContent: 'space-between', alignItems: 'end', flexWrap: 'wrap', gap: 20 }}>
            <div style={{ maxWidth: 560 }}>
              <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Le journal Plume Astrale</p>
              <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 12 }}>
                Articles à <span className="ps-italic">explorer</span>.
              </h2>
              <p className="ps-body" style={{ color: '#5A5D6B', margin: 0 }}>
                Six lectures pour comprendre les cycles, les relations, les décisions — sans jargon.
              </p>
            </div>
            <Link
              to="/blog"
              data-testid="featured-articles-see-all"
              style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 12, fontWeight: 600,
                letterSpacing: '0.16em', textTransform: 'uppercase',
                color: '#C9A24B', textDecoration: 'none',
                display: 'inline-flex', alignItems: 'center', gap: 8,
                paddingBottom: 4,
                borderBottom: '1px solid rgba(201, 162, 75, 0.4)',
              }}
            >
              Tous les articles
              <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
            </Link>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: 20,
          }}>
            {BLOG_ARTICLES.slice(0, 6).map((article, i) => (
              <Link
                key={article.slug}
                to={`/blog/${article.slug}`}
                data-testid={`featured-article-${i}`}
                style={{
                  display: 'flex', flexDirection: 'column',
                  padding: 24,
                  background: '#FFFFFF',
                  border: '1px solid #E3E1DC',
                  borderRadius: 12,
                  textDecoration: 'none',
                  color: '#0F1A3C',
                  transition: 'transform 240ms ease, box-shadow 240ms ease, border-color 240ms ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.borderColor = '#C9A24B';
                  e.currentTarget.style.boxShadow = '0 14px 34px rgba(15, 26, 60, 0.08)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = '#E3E1DC';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 10, letterSpacing: '0.22em',
                  textTransform: 'uppercase', color: '#B8935A',
                  fontWeight: 500, marginBottom: 12,
                }}>
                  {article.tag}
                </div>
                <h3 style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 19, lineHeight: 1.3, fontWeight: 400,
                  fontStyle: 'italic', color: '#0F1A3C',
                  margin: 0, marginBottom: 12,
                  flex: 1,
                }}>
                  {article.title}
                </h3>
                <p style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13, lineHeight: 1.55,
                  color: '#5A5D6B',
                  margin: 0, marginBottom: 16,
                }}>
                  {article.excerpt}
                </p>
                <span style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11, fontWeight: 600,
                  letterSpacing: '0.14em', textTransform: 'uppercase',
                  color: '#C9A24B',
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                }}>
                  Lire l&apos;article
                  <ArrowRight style={{ width: 12, height: 12 }} strokeWidth={2} />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ SECTION 5.7 · LEAD MAGNET NOCTURNE (aperçu 5 pages gratuit) ═══ */}
      <NocturneLeadMagnet />

      {/* ═══ SECTION 6 · APPEL À L'ACTION FINAL — NOCTURNE ÉDITORIAL ═══ */}
      <NocturneClosing signupPath={signupPath} />

      {/* Flipbook modal */}
      {flipbookBook && (
        <PdfFlipbook
          product={flipbookBook.slug}
          title={flipbookBook.title}
          onClose={() => setFlipbookBook(null)}
          testid="home-flipbook-modal"
        />
      )}
    </div>
  );
}
