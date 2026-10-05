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
    body: 'Composée à partir de ta date, heure et lieu de naissance exacts — pas une variation générique par signe. Chaque lecture est unique.',
  },
  {
    icon: Compass,
    title: 'Guidance douce et claire',
    body: 'Tu lis tes cycles, tes points d\'inflexion et tes talents sans rester dans le flou. Le ciel devient un miroir, pas un verdict.',
  },
  {
    icon: Heart,
    title: 'Livraison premium instantanée',
    body: 'Ton PDF est livré dès validation du paiement. Tu peux le conserver, le relire, l\'imprimer et le garder comme un objet de soin.',
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
    { slug: 'theme-natal',       title: 'Thème Natal',             tagline: '49 pages · 11 planètes décodées',                  price: '39€', to: '/theme-natal' },
    { slug: 'voyage-karmique',   title: 'Voyage Karmique',         tagline: 'Arbre de Vie + lignée d’âme',                      price: '49€', to: '/voyage-karmique' },
    { slug: 'astrocartographie', title: 'Astrocartographie',      tagline: '7 lignes planétaires · où vivre ta meilleure vie', price: '49€', to: '/astrocartographie' },
  ];

  const PRIMARY_CTA = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 10,
    padding: '14px 22px',
    borderRadius: 999,
    background: 'linear-gradient(135deg, #E4C97A 0%, #C9A24B 45%, #B98B2E 100%)',
    color: '#0F1A3C',
    fontFamily: 'Inter, sans-serif',
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: '0.14em',
    textTransform: 'uppercase',
    textDecoration: 'none',
    boxShadow: '0 18px 36px rgba(201, 162, 75, 0.22)',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
  };

  const SECONDARY_CTA = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    padding: '12px 18px',
    borderRadius: 999,
    border: '1px solid rgba(247,245,240,0.3)',
    color: '#F7F5F0',
    background: 'rgba(247,245,240,0.02)',
    fontFamily: 'Inter, sans-serif',
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
    textDecoration: 'none',
    transition: 'transform 0.2s ease, border-color 0.2s ease',
  };

  return (
    <div className="ps-home" data-testid="homepage-v2">
      <SEO
        path="/"
        title="Plume Astrale · Ton ciel, raconté avec douceur"
        description="Découvre ton thème natal, tes cycles et les clés de ta vie avec une guidance astrologique douce, précise et personnalisée."
      />

      {/* ═══ SECTION 1 · HERO NOCTURNE ÉDITORIAL (Feb 2026 — refonte artistique) ═══ */}
      <NocturneHero />

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
      <section className="ps-section ps-section-light" data-testid="ps-value" style={{ paddingTop: 96, paddingBottom: 96 }}>
        <div className="ps-container">
          <div style={{ maxWidth: 680, marginBottom: 64 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Plume Astrale · ton ciel, raconté avec douceur</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Le ciel n’a pas de formule, <span className="ps-italic">il a une histoire.</span>
            </h2>
            <p className="ps-body" style={{ color: '#232323' }}>
              Ton thème natal révèle des cycles, des talents, des tensions et des temps utiles.
              Plume Astrale te donne une lecture précise, poétique et claire pour comprendre ce qui compte vraiment.
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
      <section className="ps-section ps-section-dark" data-testid="ps-flipbook-teaser" style={{ paddingTop: 92, paddingBottom: 92 }}>
        <CelestialBackdrop density={90} shootingStars={false} />
        <div className="ps-container" style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ marginBottom: 56, maxWidth: 680 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Trois lectures. Le vôtre, à choisir.</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 16, lineHeight: 1.08, letterSpacing: '-0.03em' }}>
              Une lecture premium qui donne <span className="ps-italic">du sens au ciel.</span>
            </h2>
            <p className="ps-body" style={{ color: 'rgba(247,245,240,0.78)', lineHeight: 1.75 }}>
              Chaque livre est composé comme un objet de soin — couverture personnalisée, narration précise,
              synthèse symbolique et voix éditoriale qui te parle sans jargon inutile.
            </p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 28 }}>
            <Link
              to="/composer?edition=reliee"
              style={PRIMARY_CTA}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 22px 44px rgba(201, 162, 75, 0.30)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 18px 36px rgba(201, 162, 75, 0.22)';
              }}
            >
              Commencer mon parcours
              <ArrowRight style={{ width: 15, height: 15 }} strokeWidth={2} />
            </Link>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 24,
          }}>
            {FEATURED_BOOKS.map((b, index) => (
              <div key={b.slug}
                data-testid={`home-flipbook-card-${b.slug}`}
                style={{
                  position: 'relative',
                  overflow: 'hidden',
                  background: 'linear-gradient(180deg, rgba(18, 25, 42, 0.95) 0%, rgba(13, 19, 31, 0.92) 100%)',
                  border: '1px solid rgba(201,162,75,0.22)',
                  borderRadius: 22,
                  padding: 26,
                  display: 'flex', flexDirection: 'column', gap: 18,
                  minHeight: 360,
                  transition: 'border-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease',
                  boxShadow: index === 1 ? '0 20px 40px rgba(12, 17, 32, 0.28)' : '0 10px 25px rgba(12, 17, 32, 0.16)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(201,162,75,0.65)';
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 24px 54px rgba(12, 17, 32, 0.30)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(201,162,75,0.22)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = index === 1 ? '0 20px 40px rgba(12, 17, 32, 0.28)' : '0 10px 25px rgba(12, 17, 32, 0.16)';
                }}
              >
                <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at top right, rgba(201,162,75,0.18), transparent 43%)', pointerEvents: 'none' }} />

                <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <BookOpen style={{ width: 18, height: 18, color: '#D7B15B' }} strokeWidth={1.6} />
                    <span style={{
                      fontFamily: 'Inter, sans-serif', fontSize: 10, fontWeight: 700,
                      letterSpacing: '0.14em', textTransform: 'uppercase',
                      color: 'rgba(247,245,240,0.7)',
                    }}>Livre premium</span>
                  </div>
                  {index === 1 && (
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                      padding: '6px 10px', borderRadius: 999, background: 'rgba(201,162,75,0.12)',
                      border: '1px solid rgba(201,162,75,0.38)', color: '#F0D58D',
                      fontFamily: 'Inter, sans-serif', fontSize: 9, fontWeight: 700,
                      letterSpacing: '0.12em', textTransform: 'uppercase',
                    }}>Recommandé</span>
                  )}
                </div>

                <div style={{ position: 'relative' }}>
                  <h3 style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 26, fontWeight: 500, color: '#F7F5F0',
                    margin: 0, marginBottom: 8, lineHeight: 1.15, letterSpacing: '-0.02em',
                  }}>{b.title}</h3>
                  <p style={{
                    fontFamily: 'Inter, sans-serif', fontSize: 14, lineHeight: 1.7,
                    color: 'rgba(247,245,240,0.68)', margin: 0,
                  }}>{b.tagline}</p>
                </div>

                <div style={{ position: 'relative', display: 'flex', alignItems: 'end', justifyContent: 'space-between', gap: 14, paddingTop: 8 }}>
                  <div style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 30, color: '#D7B15B', fontStyle: 'italic', lineHeight: 1,
                  }}>{b.price}</div>
                  <div style={{
                    width: 54, height: 54, borderRadius: '50%',
                    background: 'linear-gradient(135deg, rgba(201,162,75,0.18), rgba(201,162,75,0.04))',
                    border: '1px solid rgba(201,162,75,0.35)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <ArrowRight style={{ width: 18, height: 18, color: '#F3D892' }} strokeWidth={2} />
                  </div>
                </div>

                <div style={{ position: 'relative', display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 'auto' }}>
                  <button
                    type="button"
                    onClick={() => setFlipbookBook(b)}
                    data-testid={`home-flipbook-open-${b.slug}`}
                    style={{
                      flex: '1 1 auto',
                      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                      padding: '12px 18px', borderRadius: 999,
                      background: 'linear-gradient(135deg, #E8C97B 0%, #D1A852 100%)', color: '#0F1A3C',
                      fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 700,
                      letterSpacing: '0.12em', textTransform: 'uppercase',
                      border: 'none', cursor: 'pointer',
                      transition: 'transform 0.2s ease, filter 0.2s ease',
                      boxShadow: '0 12px 24px rgba(201, 162, 75, 0.22)',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.filter = 'brightness(1.02)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.filter = 'none'; }}
                  >
                    Feuilleter
                    <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                  </button>
                  <Link
                    to={b.to}
                    data-testid={`home-flipbook-detail-${b.slug}`}
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: 6,
                      padding: '12px 14px',
                      color: 'rgba(247,245,240,0.9)',
                      fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                      letterSpacing: '0.12em', textTransform: 'uppercase',
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
              style={SECONDARY_CTA}>
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
        style={{ borderTop: '1px solid #E3E1DC', paddingTop: 88, paddingBottom: 88 }}
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
                ...SECONDARY_CTA,
                borderColor: 'rgba(201, 162, 75, 0.45)',
                color: '#0F1A3C',
                background: 'rgba(201, 162, 75, 0.05)',
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
