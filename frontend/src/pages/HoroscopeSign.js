import React from 'react';
import { Link, useParams, Navigate } from 'react-router-dom';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import SEO from '@/components/SEO';
import { ZODIAC_SIGNS, getSignBySlug } from '@/config/zodiacSigns';

/**
 * Horoscope par signe · SEO longue traîne.
 *
 * Une page par signe (12 au total) pour capter des recherches type
 * "horoscope bélier", "signe astrologique cancer", "période favorable lion", etc.
 *
 * Contenu 100% aligné repositionnement 2026-08 :
 *   - Pas de "prédiction du jour"
 *   - Traits universels, cycles favorables, zones de vigilance
 *   - CTA vers /decouvrir ou vers un produit adapté au signe
 */
export default function HoroscopeSign() {
  const { sign: slug } = useParams();
  const sign = getSignBySlug(slug);

  if (!sign) return <Navigate to="/horoscope" replace />;

  // Signes précédent/suivant pour navigation cyclique
  const idx = ZODIAC_SIGNS.findIndex((s) => s.slug === slug);
  const prev = ZODIAC_SIGNS[(idx - 1 + 12) % 12];
  const next = ZODIAC_SIGNS[(idx + 1) % 12];

  const productSlugToTitle = {
    '/theme-natal': 'Votre thème personnel',
    '/theme-natal-luxe': 'Votre lecture Luxe',
    '/karma-destin': 'Comprendre les schémas qui reviennent',
    '/synastrie': 'Comprendre votre lien à deux',
    '/astrocartographie': 'Où votre vie peut respirer',
    '/kabbale': 'Votre architecture intérieure',
    '/numerologie-pdf': 'Les nombres qui vous rythment',
  };

  return (
    <div
      data-testid={`horoscope-${slug}`}
      style={{
        minHeight: '100vh',
        background: 'radial-gradient(ellipse at 50% 0%, #1E2A5E 0%, #0F1A3C 40%, #0A1128 100%)',
        color: '#F7F5F0',
        padding: '96px 24px 128px',
      }}
    >
      <SEO
        path={`/horoscope/${sign.slug}`}
        title={`${sign.name} · Comprendre votre signe · Plume Astrale`}
        description={`Traits, cycles favorables et périodes clés du signe ${sign.name} (${sign.dates}). Une lecture accessible pour mieux comprendre votre parcours.`}
      />

      <div style={{ maxWidth: 780, margin: '0 auto' }}>
        {/* Retour */}
        <Link
          to="/horoscope"
          data-testid={`${slug}-back`}
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            color: 'rgba(247, 245, 240, 0.55)',
            fontFamily: 'Inter, sans-serif', fontSize: 12,
            letterSpacing: '0.14em', textTransform: 'uppercase',
            textDecoration: 'none', marginBottom: 48,
          }}
        >
          <ArrowLeft style={{ width: 12, height: 12 }} /> Tous les signes
        </Link>

        {/* Hero du signe */}
        <div style={{ textAlign: 'center', marginBottom: 72 }}>
          <div
            style={{
              fontFamily: 'Playfair Display, serif', fontSize: 96, lineHeight: 1,
              color: '#B8935A', marginBottom: 24,
            }}
            aria-hidden="true"
          >
            {sign.glyph}
          </div>
          <p
            style={{
              fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 500,
              letterSpacing: '0.4em', textTransform: 'uppercase',
              color: 'rgba(184, 147, 90, 0.85)', marginBottom: 20,
            }}
          >
            {sign.dates} · {sign.element} · {sign.modality}
          </p>
          <h1
            style={{
              fontFamily: 'Playfair Display, serif',
              fontSize: 'clamp(2.4rem, 5vw, 3.8rem)',
              fontWeight: 400, lineHeight: 1.15,
              color: '#F7F5F0', marginBottom: 16,
            }}
          >
            {sign.name}
          </h1>
          <p
            style={{
              fontFamily: 'Playfair Display, serif', fontStyle: 'italic',
              fontSize: 'clamp(18px, 2vw, 22px)',
              color: '#B8935A', margin: 0,
            }}
          >
            {sign.archetype}
          </p>
        </div>

        {/* Intro */}
        <p
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: 'clamp(17px, 1.5vw, 20px)',
            lineHeight: 1.7,
            color: 'rgba(247, 245, 240, 0.9)',
            marginBottom: 72,
            textAlign: 'center',
          }}
        >
          {sign.intro}
        </p>

        {/* Traits + Défis en 2 colonnes */}
        <div
          style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 32, marginBottom: 72,
          }}
        >
          <section
            style={{
              background: 'rgba(30, 42, 94, 0.35)',
              border: '1px solid rgba(184, 147, 90, 0.20)',
              borderRadius: 16, padding: '36px 32px',
            }}
          >
            <h2 style={sectionH2}>Ce qui vous porte</h2>
            <ul style={{ padding: 0, listStyle: 'none', margin: 0 }}>
              {sign.traits.map((t) => (
                <li key={t} style={traitItem}>
                  <span style={{ color: '#B8935A', marginRight: 12 }}>✦</span>{t}
                </li>
              ))}
            </ul>
          </section>

          <section
            style={{
              background: 'rgba(30, 42, 94, 0.35)',
              border: '1px solid rgba(184, 147, 90, 0.20)',
              borderRadius: 16, padding: '36px 32px',
            }}
          >
            <h2 style={sectionH2}>Zones de vigilance</h2>
            <ul style={{ padding: 0, listStyle: 'none', margin: 0 }}>
              {sign.challenges.map((c, i) => (
                <li key={i} style={{ ...traitItem, alignItems: 'flex-start', display: 'flex', lineHeight: 1.55 }}>
                  <span style={{ color: '#B8935A', marginRight: 12, flexShrink: 0 }}>◦</span>{c}
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* Périodes clés */}
        <section style={{ marginBottom: 72 }}>
          <h2 style={{ ...sectionH2, textAlign: 'center', marginBottom: 32 }}>
            Vos périodes clés dans l&apos;année
          </h2>
          <div style={{ display: 'grid', gap: 20 }}>
            {sign.keyPeriods.map((p, i) => (
              <div
                key={i}
                style={{
                  padding: '24px 28px', borderRadius: 14,
                  background: 'rgba(30, 42, 94, 0.25)',
                  border: '1px solid rgba(184, 147, 90, 0.18)',
                }}
              >
                <p
                  style={{
                    fontFamily: 'Inter, sans-serif', fontSize: 11,
                    letterSpacing: '0.2em', textTransform: 'uppercase',
                    color: '#B8935A', margin: 0, marginBottom: 8,
                  }}
                >
                  {p.when}
                </p>
                <p
                  style={{
                    fontFamily: 'Inter, sans-serif', fontSize: 15,
                    lineHeight: 1.6, color: 'rgba(247, 245, 240, 0.85)', margin: 0,
                  }}
                >
                  {p.what}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section
          style={{
            background: 'linear-gradient(135deg, rgba(184, 147, 90, 0.12) 0%, rgba(184, 147, 90, 0.04) 100%)',
            border: '1px solid rgba(184, 147, 90, 0.3)',
            borderRadius: 20, padding: '56px 40px',
            textAlign: 'center', marginBottom: 48,
          }}
        >
          <p style={{ ...sectionH2, marginBottom: 16, textAlign: 'center' }}>
            {productSlugToTitle[sign.relatedProduct] || 'Aller plus loin'}
          </p>
          <p
            style={{
              fontFamily: 'Playfair Display, serif', fontStyle: 'italic',
              fontSize: 18, lineHeight: 1.55,
              color: 'rgba(247, 245, 240, 0.82)', margin: '0 auto 32px',
              maxWidth: 480,
            }}
          >
            Une lecture personnalisée pour comprendre ce qui vous porte au-delà de votre signe solaire.
          </p>
          <Link
            to={sign.relatedProduct}
            data-testid={`${slug}-cta`}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 12,
              padding: '16px 36px', borderRadius: 999,
              background: '#B8935A', color: '#0A1128',
              fontFamily: 'Inter, sans-serif', fontSize: 13, fontWeight: 600,
              letterSpacing: '0.14em', textTransform: 'uppercase', textDecoration: 'none',
              transition: 'all 0.4s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = '#C9A24B'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = '#B8935A'; }}
          >
            Découvrir
            <ArrowRight style={{ width: 14, height: 14 }} />
          </Link>
        </section>

        {/* Navigation prev/next */}
        <nav
          style={{
            display: 'flex', justifyContent: 'space-between', gap: 20,
            paddingTop: 32, borderTop: '1px solid rgba(184, 147, 90, 0.15)',
          }}
        >
          <Link to={`/horoscope/${prev.slug}`} data-testid={`${slug}-prev`} style={navLinkStyle}>
            <ArrowLeft style={{ width: 12, height: 12 }} />
            {prev.name}
          </Link>
          <Link to={`/horoscope/${next.slug}`} data-testid={`${slug}-next`} style={{ ...navLinkStyle, flexDirection: 'row-reverse' }}>
            <ArrowRight style={{ width: 12, height: 12 }} />
            {next.name}
          </Link>
        </nav>
      </div>
    </div>
  );
}

const sectionH2 = {
  fontFamily: 'Playfair Display, serif',
  fontSize: 22, fontWeight: 400,
  color: '#F7F5F0', margin: 0, marginBottom: 20,
};

const traitItem = {
  fontFamily: 'Inter, sans-serif', fontSize: 15,
  color: 'rgba(247, 245, 240, 0.85)',
  padding: '10px 0',
  borderBottom: '1px solid rgba(184, 147, 90, 0.08)',
};

const navLinkStyle = {
  display: 'inline-flex', alignItems: 'center', gap: 8,
  color: 'rgba(247, 245, 240, 0.6)',
  fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 500,
  letterSpacing: '0.14em', textTransform: 'uppercase',
  textDecoration: 'none',
};
