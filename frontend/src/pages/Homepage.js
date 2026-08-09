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
import { useAuth } from '@/context/AuthContext';

/**
 * Homepage v3 — Refonte identité visuelle Feb 2026
 *
 * Grammaire : élégance lettrée + profondeur céleste nocturne.
 * Sections horizontales pleine largeur alternant clair (#F7F5F0) / sombre (#0F1A3C).
 * Playfair Display pour les titres, Inter pour le corps.
 * Un seul CTA doré par section. Grille 12 colonnes, max 1200px.
 */

const SOLENA_PORTRAIT = 'https://customer-assets-0z36b82j.emergentagent.net/job_consultation-astro/artifacts/72jssj5l_IMG01_portrait_femme_mystique_corrigee_2.png';

const VALUE_PILLARS = [
  {
    icon: Feather,
    title: 'Personnalisée pour toi',
    body: 'Chaque lecture est composée à partir de tes propres données de naissance — pas une variation générique par signe. Ton ciel, ton texte.',
  },
  {
    icon: Compass,
    title: 'Guidance ciblée',
    body: 'Les cycles, les répétitions, les tournants. Ce que ton ciel te propose — et le langage pour y répondre.',
  },
  {
    icon: Heart,
    title: 'Reçue en 48h',
    body: 'Ta lecture arrive par email en PDF premium à télécharger. À lire posément, à conserver longtemps.',
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

const TESTIMONIALS = [
  {
    name: 'Camille · Lyon',
    quote: '« J\'ai lu trois fois d\'affilée. C\'était comme si Soléna me connaissait depuis toujours. »',
  },
  {
    name: 'Elsa · Bruxelles',
    quote: '« Chaque page m\'a apaisée. C\'est un cadeau que je m\'offre chaque année désormais. »',
  },
  {
    name: 'Léa · Toulouse',
    quote: '« Un texte d\'une justesse rare. Un objet précieux. »',
  },
];

export default function Homepage() {
  const { user } = useAuth();
  const signupPath = user ? '/mon-compte' : '/inscription';
  const [flipbookBook, setFlipbookBook] = useState(null);

  const FEATURED_BOOKS = [
    { slug: 'theme-natal',       title: 'Thème Natal',              tagline: '49 pages · 11 planètes décodées',   price: '17,99€', to: '/theme-natal' },
    { slug: 'kabbale',           title: 'Arbre de Vie · Kabbale',   tagline: '10 Sephiroth · 22 chemins',         price: '39€',    to: '/kabbale' },
    { slug: 'astrocartographie', title: 'Astrocartographie',        tagline: '7 lignes planétaires sur le monde', price: '49€',    to: '/astrocartographie' },
  ];

  return (
    <div className="ps-home" data-testid="homepage-v2">
      <SEO
        path="/"
        title="Plume Astrale · Ta lecture astrologique écrite par Soléna"
        description="Une lecture astrologique personnalisée à partir de tes données de naissance, composée par Soléna. Livrée en PDF premium en quelques minutes."
      />

      {/* ═══ SECTION 1 · HERO SOMBRE ═══ */}
      <section className="ps-section ps-section-dark" data-testid="ps-hero">
        <CelestialBackdrop density={180} shootingStars interval={8000} />
        {/* Constellation zodiacale du mois — positionnée à gauche derrière le texte */}
        <div style={{
          position: 'absolute',
          left: '2%', top: '10%',
          width: 'min(560px, 42%)', height: '82%',
          pointerEvents: 'none', zIndex: 0,
        }} aria-hidden="true">
          <LiveConstellation sign="auto" size={520} />
        </div>
        <div className="ps-container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 48,
            alignItems: 'center',
          }} className="ps-hero-grid">
            {/* Copy */}
            <div>
              <p className="ps-eyebrow" style={{ marginBottom: 24 }}>Plume Astrale · Guidance céleste</p>
              <h1 className="ps-h1" style={{ color: '#F7F5F0', marginBottom: 24 }}>
                La lecture que ton <span className="ps-italic">ciel</span> attendait.
              </h1>
              <p className="ps-body" style={{ marginBottom: 32, color: 'rgba(247,245,240,0.85)' }}>
                Une lecture personnelle de ton thème natal par Soléna — les cycles,
                les répétitions, les tournants. Pas d&apos;horoscope générique.
              </p>
              <Link to={signupPath} className="ps-btn ps-btn-primary" data-testid="hero-cta"
                style={{ padding: '16px 32px', fontSize: 16 }}>
                Recevoir ma lecture
                <ArrowRight style={{ width: 18, height: 18 }} strokeWidth={2} />
              </Link>
              <p className="ps-caption" style={{ marginTop: 16, color: 'rgba(247,245,240,0.55)' }}>
                Sans carte bancaire · 20 crédits offerts à l&apos;inscription
              </p>
            </div>

            {/* Portrait */}
            <div style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                inset: '-20px',
                background: 'radial-gradient(ellipse 60% 70% at 50% 40%, rgba(201,162,75,0.18), transparent 65%)',
                zIndex: 0,
              }} />
              <img
                src={SOLENA_PORTRAIT}
                alt="Soléna, guide astrologique de Plume Astrale"
                data-testid="hero-portrait"
                style={{
                  position: 'relative', zIndex: 1,
                  width: '100%',
                  maxWidth: 480,
                  height: 'auto',
                  borderRadius: 12,
                  filter: 'brightness(0.95) contrast(1.02) saturate(0.95) hue-rotate(-8deg)',
                  boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
                  margin: '0 auto',
                  display: 'block',
                }}
                loading="eager"
              />
              <div style={{
                position: 'absolute', bottom: 24, left: '50%',
                transform: 'translateX(-50%)',
                background: 'rgba(15,26,60,0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(201,162,75,0.35)',
                borderRadius: 999,
                padding: '10px 20px',
                display: 'flex', alignItems: 'center', gap: 12,
                zIndex: 2,
              }}>
                <span style={{
                  fontFamily: 'Inter, sans-serif', fontSize: 13,
                  color: 'rgba(247,245,240,0.85)',
                }}>
                  Soléna, guide astrologique
                </span>
                <span style={{
                  color: '#C9A24B', fontWeight: 600, fontSize: 13,
                  display: 'flex', alignItems: 'center', gap: 4,
                }}>
                  <Star style={{ width: 14, height: 14, fill: '#C9A24B' }} strokeWidth={0} />
                  4,9/5
                </span>
              </div>
            </div>
          </div>
        </div>

        <style>{`
          @media (min-width: 900px) {
            .ps-hero-grid { grid-template-columns: 1.1fr 1fr !important; gap: 64px !important; }
          }
        `}</style>
      </section>

      {/* ═══ SECTION 2 · PROPOSITION DE VALEUR (CLAIRE) ═══ */}
      <section className="ps-section ps-section-light" data-testid="ps-value">
        <div className="ps-container">
          <div style={{ maxWidth: 680, marginBottom: 64 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Une seule promesse</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Une lecture personnelle, <span className="ps-italic">jamais générique.</span>
            </h2>
            <p className="ps-body" style={{ color: '#232323' }}>
              Ton thème natal n&apos;est comparable à aucun autre. Ta lecture ne l&apos;est pas non plus.
              Trois principes, tenus à chaque page.
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

      {/* ═══ SECTION 3 · L'HISTOIRE DE SOLÉNA (SOMBRE) ═══ */}
      <section className="ps-section ps-section-dark" data-testid="ps-story">
        <CelestialBackdrop density={140} shootingStars interval={10000} />
        <div className="ps-container">
          <div className="ps-narrow" style={{ textAlign: 'left' }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>La plume derrière les lectures</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 24 }}>
              Soléna écrit une lecture <span className="ps-italic">à la fois.</span>
            </h2>
            <p className="ps-body" style={{ color: 'rgba(247,245,240,0.85)', marginBottom: 20 }}>
              Astrologue formée à la tradition occidentale et à la kabbale hébraïque, Soléna
              travaille chaque lecture sur mesure. À partir de ta date, ton heure et ton lieu de naissance,
              chaque paragraphe est composé spécifiquement pour toi — jamais d&apos;horoscope générique.
            </p>
            <p className="ps-body" style={{ color: 'rgba(247,245,240,0.85)', marginBottom: 32 }}>
              Chaque texte est une conversation posée, précise, apaisée. Une main tendue par
              une amie qui connaît ton ciel mieux que toi.
            </p>
            <Link to="/temoignages" className="ps-btn ps-btn-outline" data-testid="story-cta">
              Lire les témoignages
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 4 · SERVICES (CLAIRE) ═══ */}
      <section className="ps-section ps-section-light" data-testid="ps-services">
        <div className="ps-container">
          <div style={{ marginBottom: 64 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Trois lectures, une signature</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 20, maxWidth: 640 }}>
              Choisis <span className="ps-italic">la lecture</span> qui te parle en ce moment.
            </h2>
            <p className="ps-body" style={{ color: '#232323', maxWidth: 640 }}>
              Chaque lecture est un PDF premium à télécharger, personnalisé à partir de ton thème natal complet. Livraison instantanée par email.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 24,
            marginBottom: 48,
          }}>
            {SERVICES.map((svc) => (
              <Link key={svc.to} to={svc.to}
                className="ps-card"
                data-testid={`service-${svc.title.toLowerCase().replace(/[^a-z]/g, '-')}`}
                style={{ textDecoration: 'none', display: 'block' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginBottom: 16,
                }}>
                  <BookOpen style={{ width: 22, height: 22, color: '#C9A24B' }} strokeWidth={1.6} />
                  <span style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 22, color: '#0F1A3C', fontWeight: 500,
                  }}>
                    {svc.price}
                  </span>
                </div>
                <h3 className="ps-h3" style={{ color: '#0F1A3C', marginBottom: 8 }}>{svc.title}</h3>
                <p style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 15, lineHeight: 1.55, color: '#6B7280', margin: 0, marginBottom: 20,
                }}>
                  {svc.desc}
                </p>
                <span style={{
                  fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 500,
                  color: '#C9A24B', display: 'inline-flex', alignItems: 'center', gap: 4,
                }}>
                  Découvrir <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                </span>
              </Link>
            ))}
          </div>

          <div style={{ textAlign: 'left' }}>
            <Link to="/nos-livres" className="ps-btn ps-btn-outline" data-testid="services-all-cta">
              Voir tous les services
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

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
            <Link to="/nos-livres" className="ps-btn ps-btn-outline"
              data-testid="home-flipbook-all-cta"
              style={{ color: '#F7F5F0', borderColor: 'rgba(247,245,240,0.4)' }}>
              Voir toute la bibliothèque
              <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 5 · TÉMOIGNAGES (SOMBRE) ═══ */}
      <section className="ps-section ps-section-dark" data-testid="ps-testimonials">
        <CelestialBackdrop density={140} shootingStars interval={10000} />
        <div className="ps-container">
          <div style={{ marginBottom: 56, maxWidth: 640 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Ce qu&apos;elles en disent</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 12 }}>
              Elles ont reçu leur <span className="ps-italic">lecture.</span>
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 16 }}>
              {[1, 2, 3, 4, 5].map(i => (
                <Star key={i} style={{ width: 18, height: 18, color: '#C9A24B', fill: '#C9A24B' }} strokeWidth={0} />
              ))}
              <span style={{
                fontFamily: 'Inter, sans-serif', fontSize: 14,
                color: 'rgba(247,245,240,0.75)', marginLeft: 8,
              }}>
                4,9/5 sur plus de 2 400 lectures livrées
              </span>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 24,
          }}>
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="ps-card" data-testid={`testimonial-${i}`}>
                <p style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 18, lineHeight: 1.5, fontStyle: 'italic',
                  color: 'rgba(247,245,240,0.95)', margin: 0, marginBottom: 20,
                }}>
                  {t.quote}
                </p>
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13, fontWeight: 500,
                  color: '#C9A24B', letterSpacing: '0.06em',
                }}>
                  — {t.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ SECTION 6 · APPEL À L'ACTION FINAL (CLAIRE) ═══ */}
      <section className="ps-section ps-section-light" data-testid="ps-final-cta">
        <div className="ps-container">
          <div style={{ maxWidth: 640 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Ta lecture t&apos;attend</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 24 }}>
              Prête à recevoir <span className="ps-italic">ta lecture personnelle ?</span>
            </h2>
            <p className="ps-body" style={{ color: '#232323', marginBottom: 32 }}>
              Ton compte t&apos;offre 20 crédits pour commencer — la première réponse arrive
              en deux minutes. Aucun engagement, aucune carte bancaire requise.
            </p>

            <Link to={signupPath} className="ps-btn ps-btn-primary"
              data-testid="final-cta"
              style={{ padding: '16px 32px', fontSize: 16 }}>
              Créer mon compte · 20 crédits offerts
              <Sparkles style={{ width: 18, height: 18 }} strokeWidth={2} />
            </Link>

            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: 24,
              marginTop: 32, color: '#6B7280',
              fontFamily: 'Inter, sans-serif', fontSize: 13,
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <ShieldCheck style={{ width: 16, height: 16, color: '#3C7A5A' }} strokeWidth={1.8} />
                Paiement sécurisé Stripe
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Clock style={{ width: 16, height: 16, color: '#3B5BA5' }} strokeWidth={1.8} />
                Réponse en 2 minutes
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Mail style={{ width: 16, height: 16, color: '#C9A24B' }} strokeWidth={1.8} />
                Livrée par email
              </span>
            </div>
          </div>
        </div>
      </section>

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
