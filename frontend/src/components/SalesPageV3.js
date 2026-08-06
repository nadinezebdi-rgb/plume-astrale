import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight, Sparkles, ShieldCheck, Clock, Mail, Star, BookOpen, Check,
} from 'lucide-react';
import PsPageShell from '@/components/PsPageShell';
import SEO from '@/components/SEO';
import ApercuLectureModal from '@/components/ApercuLectureModal';
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
          <div style={{ maxWidth: 780 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>{eyebrow}</p>
            <h1 className="ps-h1"
              style={{ color: '#0F1A3C', marginBottom: 24 }}
              dangerouslySetInnerHTML={{ __html: title }} />
            <p className="ps-body" style={{ color: '#232323', marginBottom: 32 }}>
              {subtitle}
            </p>

            {/* Prix hero card */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap',
              padding: '20px 24px',
              background: '#fff',
              border: heroBadge ? '1px solid #C9A24B' : '1px solid #E3E1DC',
              borderRadius: 12,
              maxWidth: 560,
              marginBottom: 24,
            }}>
              {heroBadge && (
                <span style={{
                  position: 'absolute', transform: 'translateY(-38px)',
                  background: '#C9A24B', color: '#0F1A3C',
                  fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                  letterSpacing: '0.14em', textTransform: 'uppercase',
                  padding: '5px 12px', borderRadius: 6,
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
                style={{ marginTop: 28, padding: '12px 24px' }}>
                <BookOpen style={{ width: 16, height: 16 }} strokeWidth={2} />
                Lire un extrait gratuit
              </button>
            )}
          </div>
        </div>
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
    </PsPageShell>
  );
}
