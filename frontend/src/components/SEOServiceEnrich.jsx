import React, { useState } from 'react';
import { ChevronDown, Sparkles, CheckCircle2 } from 'lucide-react';
import { SEO_SERVICE_CONTENT } from '../data/seoServiceContent';

/**
 * SEOServiceEnrich — Rendu SEO-friendly d'une page /services/:slug
 *
 * Étoffe automatiquement une page produit avec :
 * - Introduction longue (400 mots)
 * - Comment ça marche
 * - Bénéfices en liste
 * - Public cible
 * - FAQ interactive + JSON-LD FAQPage (rich snippets Google)
 *
 * À insérer en bas d'une page /services/tarot, /services/compatibilite, /services/oracle
 * pour dépasser le seuil de contenu identifié par l'audit SEO Feb 2026 (800-943 char).
 *
 * @param {string} slug — identifie l'entrée dans SEO_SERVICE_CONTENT
 */
export default function SEOServiceEnrich({ slug }) {
  const content = SEO_SERVICE_CONTENT[slug];
  const [openFaq, setOpenFaq] = useState(null);

  if (!content) return null;

  // Injection JSON-LD FAQPage pour rich snippets
  const faqJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': content.faq.map((item) => ({
      '@type': 'Question',
      'name': item.q,
      'acceptedAnswer': { '@type': 'Answer', 'text': item.a },
    })),
  };

  return (
    <section
      className="relative py-24 px-6"
      style={{ background: 'var(--pa-bg, #0F1A3C)', color: 'var(--pa-body, rgba(247,245,240,0.85))' }}
      data-testid={`seo-enrich-${slug}`}
    >
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <div className="max-w-3xl mx-auto">
        {/* Kicker + Titre */}
        <div className="text-xs uppercase tracking-widest mb-4 flex items-center gap-2"
             style={{ color: '#D4AF37', letterSpacing: '0.14em' }}
             data-testid={`seo-enrich-kicker-${slug}`}>
          <Sparkles className="w-3.5 h-3.5" strokeWidth={1.6} />
          {content.kicker}
        </div>
        <h2
          className="mb-8"
          style={{
            fontFamily: 'Cormorant Garamond, Playfair Display, serif',
            fontSize: 'clamp(28px, 4vw, 44px)',
            fontWeight: 400,
            lineHeight: 1.15,
            color: 'var(--pa-heading, #F5EEE0)',
          }}
          data-testid={`seo-enrich-title-${slug}`}
        >
          {content.title}
        </h2>

        {/* Intro (400 mots) */}
        <p
          className="mb-12"
          style={{ fontSize: 17, lineHeight: 1.75, color: 'rgba(247,245,240,0.85)' }}
          data-testid={`seo-enrich-intro-${slug}`}
        >
          {content.intro}
        </p>

        {/* How it works */}
        <div className="mb-12">
          <h3
            className="mb-4"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 24, fontWeight: 500,
              color: 'var(--pa-heading, #F5EEE0)',
            }}
          >
            {content.how_it_works.title}
          </h3>
          <p style={{ fontSize: 16, lineHeight: 1.75, color: 'rgba(247,245,240,0.80)' }}>
            {content.how_it_works.body}
          </p>
        </div>

        {/* Benefits — liste avec icônes */}
        <div className="mb-12">
          <h3
            className="mb-6"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 24, fontWeight: 500,
              color: 'var(--pa-heading, #F5EEE0)',
            }}
          >
            {content.benefits.title}
          </h3>
          <ul className="space-y-3 list-none p-0">
            {content.benefits.items.map((item, i) => (
              <li
                key={i}
                className="flex items-start gap-3"
                style={{ fontSize: 16, lineHeight: 1.65, color: 'rgba(247,245,240,0.85)' }}
              >
                <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#D4AF37' }} strokeWidth={1.6} />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Who for */}
        <div className="mb-16">
          <h3
            className="mb-4"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 24, fontWeight: 500,
              color: 'var(--pa-heading, #F5EEE0)',
            }}
          >
            {content.who_for.title}
          </h3>
          <p style={{ fontSize: 16, lineHeight: 1.75, color: 'rgba(247,245,240,0.80)' }}>
            {content.who_for.body}
          </p>
        </div>

        {/* FAQ interactive — accordion */}
        <div className="mb-8">
          <h3
            className="mb-8 text-center"
            style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: 32, fontWeight: 500,
              color: 'var(--pa-heading, #F5EEE0)',
            }}
            data-testid={`seo-enrich-faq-title-${slug}`}
          >
            Questions fréquentes
          </h3>
          <div className="space-y-2">
            {content.faq.map((item, i) => {
              const isOpen = openFaq === i;
              return (
                <div
                  key={i}
                  className="rounded-xl overflow-hidden"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(212,175,55,0.15)',
                  }}
                  data-testid={`seo-enrich-faq-${slug}-${i}`}
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : i)}
                    className="w-full text-left px-6 py-4 flex items-center justify-between gap-4 hover:bg-white/[0.02] transition-colors"
                    style={{ color: 'var(--pa-heading, #F5EEE0)', fontSize: 16 }}
                    aria-expanded={isOpen}
                    data-testid={`seo-enrich-faq-toggle-${slug}-${i}`}
                  >
                    <span style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 19 }}>{item.q}</span>
                    <ChevronDown
                      className="w-5 h-5 flex-shrink-0 transition-transform"
                      style={{
                        color: '#D4AF37',
                        transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                      }}
                    />
                  </button>
                  {isOpen && (
                    <div
                      className="px-6 pb-5"
                      style={{ fontSize: 15, lineHeight: 1.7, color: 'rgba(247,245,240,0.78)' }}
                    >
                      {item.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
