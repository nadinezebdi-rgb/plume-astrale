import React from 'react';
import { Link } from 'react-router-dom';
import { Gift, MessageCircle, BookOpen, ArrowRight } from 'lucide-react';

/**
 * HowItWorks3Tiers — clarification F500 majeure : Gratuit / Crédits / PDF Signature.
 *
 * Résout la confusion "PDF vs Crédits" qui plombait la conversion.
 * Chaque tier a une couleur / icône / usage concret / prix.
 *
 * Section auto-adaptive : responsive mobile + desktop, sur fond ivoire.
 */
const TIERS = [
  {
    icon: Gift,
    tag: 'GRATUIT',
    tagColor: '#4A7C4E',
    title: 'Découvrir',
    subtitle: 'Sans engagement, sans compte à créer',
    items: [
      'Horoscope quotidien personnalisé',
      'Guidance du jour + prévisions hebdo et mensuelles',
      'Newsletter éditoriale · désabo en 1 clic',
    ],
    cta: 'Voir mon horoscope',
    ctaLink: '/horoscope',
    testid: 'how-tier-gratuit',
  },
  {
    icon: MessageCircle,
    tag: 'À L\u2019USAGE',
    tagColor: '#8F6E24',
    title: 'Crédits Soléna',
    subtitle: 'Un compagnon quotidien à la carte',
    items: [
      '1 question au chat Soléna · 5 crédits',
      '1 tirage tarot approfondi · 15 crédits',
      '1 astro-guidance mensuelle · 10 crédits',
    ],
    footer: 'Packs à partir de 6,99€ · pas d\u2019engagement',
    cta: 'Voir les packs',
    ctaLink: '/credits',
    testid: 'how-tier-credits',
    highlight: true,
  },
  {
    icon: BookOpen,
    tag: 'ARCHIVE À VIE',
    tagColor: '#0F1A3C',
    title: 'PDF Signature',
    subtitle: 'Une lecture-signature, gardée pour toujours',
    items: [
      'Thème Natal Signature · 49 pages · 39€',
      'Astrologie relationnelle · 25 pages · 29€',
      'Voyage karmique · 35 pages · 49€',
    ],
    footer: 'Aucun crédit requis · livré en 60 secondes',
    cta: 'Voir les PDF',
    ctaLink: '/livres',
    testid: 'how-tier-pdf',
  },
];

export default function HowItWorks3Tiers() {
  return (
    <section
      className="ps-section"
      data-testid="how-it-works-3tiers"
      style={{ background: '#F7F5F0', paddingTop: 72, paddingBottom: 72 }}
    >
      <div className="ps-container" style={{ maxWidth: 1180 }}>
        <div style={{ maxWidth: 720, marginBottom: 48 }}>
          <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Comment ça marche</p>
          <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 16 }}>
            Trois façons d&apos;entrer <span className="ps-italic">chez Plume.</span>
          </h2>
          <p className="ps-body" style={{ color: '#232323' }}>
            Commence gratuitement avec ton horoscope quotidien. Utilise des crédits
            pour poser tes questions au fil des mois. Ou choisis une lecture-signature en
            PDF, à archiver pour la vie. Trois portes, une même signature éditoriale.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 24,
            alignItems: 'stretch',
          }}
        >
          {TIERS.map((tier) => {
            const Icon = tier.icon;
            const isHighlight = tier.highlight;
            return (
              <div
                key={tier.testid}
                data-testid={tier.testid}
                style={{
                  padding: 28,
                  background: '#fff',
                  border: isHighlight ? '1.5px solid #C9A24B' : '1px solid #E3E1DC',
                  borderRadius: 14,
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  boxShadow: isHighlight ? '0 12px 28px -20px rgba(201,162,75,0.5)' : 'none',
                }}
              >
                <div style={{
                  display: 'inline-block',
                  padding: '4px 10px',
                  borderRadius: 4,
                  background: `${tier.tagColor}15`,
                  color: tier.tagColor,
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase',
                  fontFamily: 'Inter, sans-serif',
                  marginBottom: 16,
                  alignSelf: 'flex-start',
                }}>
                  {tier.tag}
                </div>
                <Icon
                  style={{ width: 32, height: 32, color: tier.tagColor, marginBottom: 12 }}
                  strokeWidth={1.4}
                />
                <div style={{
                  fontFamily: 'Playfair Display, serif',
                  fontSize: 26, fontWeight: 500,
                  color: '#0F1A3C', marginBottom: 6, lineHeight: 1.15,
                }}>
                  {tier.title}
                </div>
                <div style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13, color: '#6B7280', lineHeight: 1.5, marginBottom: 20,
                }}>
                  {tier.subtitle}
                </div>
                <ul style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 14, color: '#232323', lineHeight: 1.7,
                  margin: 0, padding: 0, listStyle: 'none',
                  flexGrow: 1,
                }}>
                  {tier.items.map((it) => (
                    <li key={it} style={{ marginBottom: 6, paddingLeft: 16, position: 'relative' }}>
                      <span style={{
                        position: 'absolute', left: 0, top: 10,
                        width: 6, height: 6, borderRadius: '50%',
                        background: tier.tagColor,
                      }} />
                      {it}
                    </li>
                  ))}
                </ul>
                {tier.footer && (
                  <div style={{
                    marginTop: 20, padding: '10px 12px',
                    background: '#F7F5F0',
                    borderRadius: 6,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 12, color: '#6B7280', textAlign: 'center',
                  }}>
                    {tier.footer}
                  </div>
                )}
                <Link
                  to={tier.ctaLink}
                  data-testid={`${tier.testid}-cta`}
                  style={{
                    marginTop: 20,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                    padding: '11px 16px',
                    borderRadius: 999,
                    background: isHighlight ? tier.tagColor : 'transparent',
                    color: isHighlight ? '#fff' : tier.tagColor,
                    border: isHighlight ? 'none' : `1px solid ${tier.tagColor}`,
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 13, fontWeight: 500,
                    letterSpacing: '0.05em',
                    textDecoration: 'none',
                  }}
                >
                  {tier.cta}
                  <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                </Link>
              </div>
            );
          })}
        </div>

        {/* Bonus inscription — barre soulignée */}
        <div
          data-testid="signup-incentive-banner"
          style={{
            marginTop: 32,
            padding: '18px 24px',
            background: '#0F1A3C',
            borderRadius: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            flexWrap: 'wrap',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1, minWidth: 240 }}>
            <span style={{ fontSize: 24 }}>🎁</span>
            <div>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 11, fontWeight: 700, letterSpacing: '0.16em',
                textTransform: 'uppercase', color: '#D4AF37', marginBottom: 2,
              }}>
                Offert à l&apos;inscription
              </div>
              <div style={{
                fontFamily: 'Inter, sans-serif',
                fontSize: 14, fontWeight: 500, color: '#F5EEE0',
              }}>
                <b>Aperçu Thème Natal 5 pages</b> + <b>20 crédits</b> — sans carte bancaire
              </div>
            </div>
          </div>
          <Link
            to="/inscription"
            data-testid="signup-incentive-cta"
            className="ps-btn ps-btn-primary"
            style={{ flexShrink: 0 }}
          >
            Créer mon compte
            <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={2} />
          </Link>
        </div>
      </div>
    </section>
  );
}
