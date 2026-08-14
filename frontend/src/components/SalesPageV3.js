import React, { useState } from 'react';import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, Sparkles, ShieldCheck, Clock, Mail, Star, BookOpen, Check, Gift,
} from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import ApercuLectureModal from '@/components/ApercuLectureModal';
import GiftModal from '@/components/GiftModal';
import PdfPreviewButton from '@/components/PdfPreviewButton';
import PdfFlipbook from '@/components/PdfFlipbook';
import CelestialBackdrop from '@/components/CelestialBackdrop';
import { useAuth } from '@/context/AuthContext';

/**
 * SalesPageV3 — Template unifié pour toutes les pages de vente PDF.
 * Charte v3 light. Props-driven, très concis à instancier.
 *
 * Props :
 *   slug            : 'natal' | 'kabbale' | 'astrocarto' | ...  (pour testid + apercus)
 *   path            : '/theme-natal-luxe' (pour SEO)
 *   seoTitle, seoDescription
 *   eyebrow         : "La bibliothèque Plume Astrale · Thème Natal"
 *   title           : "Ton Thème Natal, écrit pour toi." (peut contenir <em>...</em>)
 *   subtitle        : paragraphe descriptif
 *   priceMain       : "17,99€"
 *   priceStrike     : "29€"     (optionnel — prix barré)
 *   priceHint       : "paiement unique · PDF 49 pages"
 *   pages           : 49
 *   deliveryTime    : "5 min"
 *   heroBadge       : "L'offre écrin" (optionnel)
 *
 *   includes        : [{ title, text }]  // "Ce que ta lecture contient"
 *
 *   testimonials    : [{ name, quote, stars? }] (optionnel)
 *
 *   apercu          : object depuis config/apercus.js (déclenche le modal)
 *
 *   guarantee       : "Clarté ou remboursée · 14 jours" (optionnel)
 *
 *   ctaLabelAuth    : "Générer ma lecture"
 *   ctaLabelGuest   : "Recevoir mes 20 crédits · Commencer"
 *   ctaTargetAuth   : "/mon-compte?generate=natal"
 *   ctaTargetGuest  : "/inscription?next=/mon-compte"
 */
export default function SalesPageV3({
  slug,
  path,
  seoTitle,
  seoDescription,
  eyebrow,
  title,
  subtitle,
  priceMain,
  priceStrike,
  priceHint,
  pages,
  deliveryTime = '5 min',
  heroBadge,
  heroImage,          // { src, alt, caption? }
  heroNode,           // ReactNode — alternative visuel personnalisé (SVG, composant custom)
  previewProduct,     // id du produit pour l'aperçu PDF 3 pages (ex: 'astrocartographie')
  includes,
  testimonials,
  apercu,
  guarantee,
  ctaLabelAuth,
  ctaLabelGuest,
  ctaTargetAuth,
  ctaTargetGuest,
}) {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [apercuOpen, setApercuOpen] = useState(false);
  const [giftOpen, setGiftOpen] = useState(false);
  const [flipbookOpen, setFlipbookOpen] = useState(false);

  const handleCta = () => {
    navigate(isAuthenticated ? ctaTargetAuth : ctaTargetGuest);
  };

  const ctaLabel = isAuthenticated ? ctaLabelAuth : ctaLabelGuest;

  return (
    <PsPageShell background="light">
      <SEO path={path} title={seoTitle} description={seoDescription} />

      {/* ─── HERO (light) ────────────────────────────────────── */}
      <section className="ps-section ps-section-light" data-testid={`sales-${slug}-hero`}>
        <div className="ps-container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 48,
            alignItems: 'center',
          }} className="ps-sales-hero-grid">
            <div style={{ maxWidth: 780 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>{eyebrow}</p>
            <h1 className="ps-h1"
              style={{ color: '#0F1A3C', marginBottom: 24 }}
              dangerouslySetInnerHTML={{ __html: title }} />
            <p className="ps-body" style={{ color: '#232323', marginBottom: 32 }}>
              {subtitle}
            </p>

            {/* Prix hero card */}
            <div className="ps-sales-hero-price" style={{
              position: 'relative',
              display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap',
              padding: heroBadge ? '32px 24px 20px' : '20px 24px',
              background: '#fff',
              border: heroBadge ? '1px solid #C9A24B' : '1px solid #E3E1DC',
              borderRadius: 12,
              maxWidth: 560,
              marginBottom: 24,
              marginTop: heroBadge ? 20 : 0,
            }}>
              {heroBadge && (
                <span style={{
                  position: 'absolute', top: -14, left: 24,
                  background: '#C9A24B', color: '#0F1A3C',
                  fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                  letterSpacing: '0.14em', textTransform: 'uppercase',
                  padding: '5px 12px', borderRadius: 6,
                  boxShadow: '0 4px 10px rgba(201,162,75,0.35)',
                }}>{heroBadge}</span>
              )}
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                  <span style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 40, fontWeight: 500,
                    color: '#0F1A3C', lineHeight: 1,
                  }}>{priceMain}</span>
                  {priceStrike && (
                    <span style={{
                      fontFamily: 'Playfair Display, serif',
                      fontSize: 20, color: '#6B7280',
                      textDecoration: 'line-through',
                    }}>{priceStrike}</span>
                  )}
                </div>
                {priceHint && (
                  <div style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 13, color: '#6B7280', marginTop: 6,
                  }}>{priceHint}</div>
                )}
              </div>
              <div style={{ flex: 1 }} />
              <button
                onClick={handleCta}
                data-testid={`sales-${slug}-cta-hero`}
                className="ps-btn ps-btn-primary"
                style={{ padding: '14px 28px' }}>
                {ctaLabel}
                <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
              </button>
            </div>

            {/* Ligne rassurance */}
            <div style={{
              display: 'flex', flexWrap: 'wrap', gap: 20,
              fontFamily: 'Inter, sans-serif', fontSize: 13,
              color: '#6B7280',
            }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <ShieldCheck style={{ width: 15, height: 15, color: '#3C7A5A' }} strokeWidth={1.8} />
                Paiement sécurisé Stripe
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <Clock style={{ width: 15, height: 15, color: '#3B5BA5' }} strokeWidth={1.8} />
                Livraison PDF en {deliveryTime}
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <BookOpen style={{ width: 15, height: 15, color: '#C9A24B' }} strokeWidth={1.8} />
                {pages} pages
              </span>
            </div>

            {/* Bouton aperçu gratuit */}
            {apercu && (
              <button
                type="button"
                onClick={() => setApercuOpen(true)}
                data-testid={`sales-${slug}-apercu-btn`}
                className="ps-btn ps-btn-outline"
                style={{ marginTop: 28, marginRight: 12, padding: '12px 24px' }}>
                <BookOpen style={{ width: 16, height: 16 }} strokeWidth={2} />
                Lire un extrait gratuit
              </button>
            )}
            <button
              type="button"
              onClick={() => setGiftOpen(true)}
              data-testid={`sales-${slug}-gift-btn`}
              className="ps-btn ps-btn-outline"
              style={{ marginTop: 28, padding: '12px 24px' }}>
              <Gift style={{ width: 16, height: 16 }} strokeWidth={2} />
              Offrir cette lecture
            </button>

            {/* Aperçu 3 pages téléchargeable (livre prestige) */}
            {previewProduct && (
              <div style={{ marginTop: 24, display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
                <button
                  type="button"
                  onClick={() => setFlipbookOpen(true)}
                  data-testid={`sales-${slug}-flipbook-btn`}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: 8,
                    padding: '11px 20px', borderRadius: 999,
                    background: '#0F1A3C', color: '#F7F5F0',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12, fontWeight: 600,
                    letterSpacing: '0.10em', textTransform: 'uppercase',
                    border: '1px solid #0F1A3C', cursor: 'pointer',
                    transition: 'background 0.2s ease, color 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#C9A24B';
                    e.currentTarget.style.color = '#0F1A3C';
                    e.currentTarget.style.borderColor = '#C9A24B';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = '#0F1A3C';
                    e.currentTarget.style.color = '#F7F5F0';
                    e.currentTarget.style.borderColor = '#0F1A3C';
                  }}
                >
                  <BookOpen style={{ width: 14, height: 14 }} strokeWidth={1.8} />
                  Feuilleter le livre
                </button>
                <PdfPreviewButton
                  product={previewProduct}
                  variant="ghost"
                  testid={`sales-${slug}-pdf-preview-btn`}
                />
              </div>
            )}
            </div>

            {/* Colonne visuelle décorative */}
            {heroNode && (
              <div style={{ position: 'relative', textAlign: 'center' }} data-testid={`sales-${slug}-hero-node`}>
                <div style={{
                  position: 'absolute',
                  inset: '-30px',
                  background: 'radial-gradient(circle at center, rgba(201,162,75,0.16) 0%, transparent 65%)',
                  filter: 'blur(24px)',
                  zIndex: 0,
                }} />
                <div style={{ position: 'relative', zIndex: 1 }}>{heroNode}</div>
              </div>
            )}
            {!heroNode && heroImage && (
              <div style={{ position: 'relative', textAlign: 'center' }} data-testid={`sales-${slug}-hero-image`}>
                <div style={{
                  position: 'absolute',
                  inset: '-30px',
                  background: 'radial-gradient(circle at center, rgba(201,162,75,0.16) 0%, transparent 65%)',
                  filter: 'blur(24px)',
                  zIndex: 0,
                }} />
                <img
                  src={heroImage.src}
                  alt={heroImage.alt || ''}
                  loading="lazy"
                  style={{
                    position: 'relative', zIndex: 1,
                    maxWidth: 380, width: '100%', height: 'auto',
                    borderRadius: 16,
                    boxShadow:
                      '0 24px 48px rgba(15,26,60,0.16), 0 0 0 1px rgba(201,162,75,0.15)',
                    display: 'block', margin: '0 auto',
                  }}
                />
                {heroImage.caption && (
                  <div style={{
                    position: 'relative', zIndex: 1,
                    marginTop: 16,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12, letterSpacing: '0.16em',
                    textTransform: 'uppercase',
                    color: 'rgba(201,162,75,0.75)',
                  }}>
                    {heroImage.caption}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <style>{`
          @media (min-width: 900px) {
            .ps-sales-hero-grid { grid-template-columns: 1.3fr 1fr !important; gap: 64px !important; }
          }
        `}</style>
      </section>

      {/* ─── INCLUDES (dark) ─────────────────────────────────── */}
      <section className="ps-section ps-section-dark" data-testid={`sales-${slug}-includes`}>
        <CelestialBackdrop density={70} shootingStars interval={14000} />
        <div className="ps-container">
          <div style={{ maxWidth: 720, marginBottom: 56 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Ce que ta lecture contient</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 16 }}>
              {pages} pages, <span className="ps-italic">personnalisées à partir de ton thème</span> natal.
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 20,
          }}>
            {includes.map((it, i) => (
              <div key={i} className="ps-card" data-testid={`sales-${slug}-include-${i}`}>
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 11, fontWeight: 600,
                  letterSpacing: '0.16em', textTransform: 'uppercase',
                  color: '#C9A24B', marginBottom: 10,
                }}>{it.title}</div>
                <p style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 14, lineHeight: 1.6,
                  color: 'rgba(247,245,240,0.82)', margin: 0,
                }}>{it.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── TESTIMONIALS (light) ────────────────────────────── */}
      {testimonials && testimonials.length > 0 && (
        <section className="ps-section ps-section-light" data-testid={`sales-${slug}-testimonials`}>
          <div className="ps-container">
            <div style={{ marginBottom: 48, maxWidth: 640 }}>
              <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Ce qu&apos;elles en disent</p>
              <h2 className="ps-h2" style={{ color: '#0F1A3C' }}>
                Elles ont reçu leur <span className="ps-italic">lecture.</span>
              </h2>
            </div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 20,
            }}>
              {testimonials.map((t, i) => (
                <div key={i} className="ps-card" data-testid={`sales-${slug}-testimonial-${i}`}>
                  <div style={{ display: 'flex', gap: 2, marginBottom: 12 }}>
                    {[...Array(t.stars || 5)].map((_, k) => (
                      <Star key={k} style={{ width: 14, height: 14, color: '#C9A24B', fill: '#C9A24B' }} strokeWidth={0} />
                    ))}
                  </div>
                  <p style={{
                    fontFamily: 'Playfair Display, serif',
                    fontSize: 16, lineHeight: 1.55, fontStyle: 'italic',
                    color: '#232323', margin: 0, marginBottom: 16,
                  }}>« {t.quote} »</p>
                  <div style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 13, fontWeight: 500, color: '#C9A24B',
                    letterSpacing: '0.06em',
                  }}>— {t.name}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ─── PRICING + FINAL CTA (dark) ──────────────────────── */}
      <section className="ps-section ps-section-dark" data-testid={`sales-${slug}-final`}>
        <CelestialBackdrop density={65} shootingStars interval={16000} />
        <div className="ps-container">
          <div className="ps-narrow" style={{
            marginLeft: 0,
            padding: '48px 40px',
            background: 'linear-gradient(160deg, rgba(30,42,94,0.85) 0%, rgba(15,26,60,0.95) 100%)',
            border: '1px solid rgba(201,162,75,0.4)',
            borderRadius: 16,
          }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Prête à commencer ?</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 20 }}>
              Ta lecture <span className="ps-italic">t&apos;attend</span> dans ta boîte mail.
            </h2>

            <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 28 }}>
              <span style={{
                fontFamily: 'Playfair Display, serif',
                fontSize: 48, fontWeight: 500,
                color: '#F7F5F0', lineHeight: 1,
              }}>{priceMain}</span>
              {priceStrike && (
                <span style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 22, color: 'rgba(247,245,240,0.5)',
                  textDecoration: 'line-through',
                }}>{priceStrike}</span>
              )}
              {priceHint && (
                <span style={{
                  fontFamily: 'Inter, sans-serif', fontSize: 13,
                  color: 'rgba(247,245,240,0.65)', marginLeft: 8,
                }}>· {priceHint}</span>
              )}
            </div>

            <button
              onClick={handleCta}
              data-testid={`sales-${slug}-cta-final`}
              className="ps-btn ps-btn-primary"
              style={{ padding: '16px 32px', fontSize: 16, marginBottom: 24 }}>
              <Sparkles style={{ width: 18, height: 18 }} strokeWidth={2} />
              {ctaLabel}
              <ArrowRight style={{ width: 18, height: 18 }} strokeWidth={2} />
            </button>

            {/* Rassurances */}
            <div style={{
              display: 'flex', flexDirection: 'column', gap: 10,
              fontFamily: 'Inter, sans-serif', fontSize: 14,
              color: 'rgba(247,245,240,0.78)',
            }}>
              {guarantee && (
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Check style={{ width: 15, height: 15, color: '#C9A24B' }} strokeWidth={2.5} />
                  {guarantee}
                </span>
              )}
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Mail style={{ width: 15, height: 15, color: '#C9A24B' }} strokeWidth={2} />
                Livraison instantanée par email — {deliveryTime} après paiement
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ShieldCheck style={{ width: 15, height: 15, color: '#C9A24B' }} strokeWidth={2} />
                Paiement Stripe · 3-D Secure · Sans engagement
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Modal aperçu */}
      {apercu && (
        <ApercuLectureModal
          open={apercuOpen}
          onClose={() => setApercuOpen(false)}
          apercu={apercu}
          productSlug={slug}
          ctaLabel={ctaLabel}
          onCta={() => { setApercuOpen(false); handleCta(); }}
        />
      )}

      {/* Modal cadeau */}
      <GiftModal
        open={giftOpen}
        onClose={() => setGiftOpen(false)}
        productSlug={slug}
        productLabel={apercu?.label || eyebrow?.split(' · ').pop() || 'Lecture'}
        productPrice={priceMain}
      />

      {/* Flipbook 3D — feuilletage interactif */}
      {flipbookOpen && previewProduct && (
        <PdfFlipbook
          product={previewProduct}
          title={apercu?.label || eyebrow?.split(' · ').pop() || 'Aperçu du livre'}
          onClose={() => setFlipbookOpen(false)}
          testid={`sales-${slug}-flipbook-modal`}
        />
      )}
    </PsPageShell>
  );
}
