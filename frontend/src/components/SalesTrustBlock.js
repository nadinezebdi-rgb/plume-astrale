import React from 'react';

/**
 * SalesTrustBlock — bloc de confiance F500 réutilisable.
 *
 * 3 cartes horizontales : Garantie · Comparateur de valeur · Cadre & Support.
 * S'adapte automatiquement au thème (light/dark) via la prop `theme`.
 *
 * Props :
 *   priceMain   : prix affiché (ex. "29,99€")
 *   marketPrice : fourchette de marché (ex. "150-250€"), défaut consultation astro
 *   theme       : 'light' (fond ivoire) ou 'dark' (fond nuit + accent or)
 *   testid      : suffixe testid (ex. "natal", "theme-natal", "karma")
 */
export default function SalesTrustBlock({
  priceMain,
  marketPrice = '150-250€',
  marketLabel = 'consultation astro',
  theme = 'light',
  testid = 'sales',
}) {
  const isDark = theme === 'dark';
  const styles = {
    section: {
      padding: isDark ? '40px 20px' : '40px 0',
      background: isDark ? 'rgba(15,26,60,0.4)' : '#F7F5F0',
      borderTop: `1px solid ${isDark ? 'rgba(212,175,55,0.25)' : '#E3E1DC'}`,
      borderBottom: `1px solid ${isDark ? 'rgba(212,175,55,0.25)' : '#E3E1DC'}`,
    },
    card: {
      padding: 20,
      background: isDark ? 'rgba(255,255,255,0.03)' : '#fff',
      border: `1px solid ${isDark ? 'rgba(227,215,255,0.15)' : '#E3E1DC'}`,
      borderRadius: 12,
    },
    cardHighlight: {
      padding: 20,
      background: isDark ? 'rgba(212,175,55,0.10)' : '#fff',
      border: `1px solid ${isDark ? 'rgba(212,175,55,0.5)' : '#C9A24B'}`,
      borderRadius: 12,
    },
    eyebrow: {
      fontFamily: 'Inter, sans-serif',
      fontSize: 11, fontWeight: 600, letterSpacing: '0.16em',
      textTransform: 'uppercase',
      color: isDark ? '#D4AF37' : '#8F6E24',
      marginBottom: 8,
    },
    heading: {
      fontFamily: 'Playfair Display, Cormorant Garamond, serif',
      fontSize: 22, fontWeight: 500,
      color: isDark ? '#F5EEE0' : '#0F1A3C',
      lineHeight: 1.25, marginBottom: 6,
    },
    hint: {
      fontFamily: 'Inter, sans-serif',
      fontSize: 13, lineHeight: 1.5,
      color: isDark ? 'rgba(227,215,255,0.7)' : '#6B7280',
    },
    priceNum: {
      fontFamily: 'Playfair Display, Cormorant Garamond, serif',
      fontSize: 26, fontWeight: 500,
      color: isDark ? '#F5EEE0' : '#0F1A3C',
    },
    priceVs: {
      fontFamily: 'Inter, sans-serif',
      fontSize: 13,
      color: isDark ? 'rgba(227,215,255,0.7)' : '#6B7280',
    },
  };

  return (
    <section
      data-testid={`${testid}-trust-block`}
      style={styles.section}
    >
      <div
        style={{
          maxWidth: 1180, margin: '0 auto', padding: '0 24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 24,
          alignItems: 'start',
        }}
      >
        {/* Garantie */}
        <div data-testid={`${testid}-trust-guarantee`} style={styles.cardHighlight}>
          <div style={styles.eyebrow}>Garantie</div>
          <div style={styles.heading}>
            Satisfait ou remboursé <span style={{ fontStyle: 'italic' }}>14 jours</span>
          </div>
          <div style={styles.hint}>
            Sans condition. Un simple email à contact@plume-astrale.fr — remboursement sous 48h.
          </div>
        </div>

        {/* Comparateur */}
        <div data-testid={`${testid}-trust-compare`} style={styles.card}>
          <div style={styles.eyebrow}>Comparateur de valeur</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 6, flexWrap: 'wrap' }}>
            <span style={styles.priceNum}>{priceMain}</span>
            <span style={styles.priceVs}>
              vs. {marketLabel} : <s>{marketPrice}</s>
            </span>
          </div>
          <div style={styles.hint}>
            Analyse écrite, archivable, relisible à vie — vs. 1h d&apos;échange oral non transcrit.
          </div>
        </div>

        {/* Cadre & Support */}
        <div data-testid={`${testid}-trust-cadre`} style={styles.card}>
          <div style={styles.eyebrow}>Cadre &amp; Support</div>
          <ul
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              color: isDark ? 'rgba(227,215,255,0.85)' : '#232323',
              lineHeight: 1.7,
              margin: 0, padding: 0, listStyle: 'none',
            }}
          >
            <li>· Paiement Stripe (PCI DSS niveau 1)</li>
            <li>· PDF téléchargeable à vie · format A4</li>
            <li>· Support 7j/7 · réponse sous 24h</li>
            <li>· RGPD conforme · aucune revente de données</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
