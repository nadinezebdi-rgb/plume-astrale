import React from 'react';
import { Shield, Lock, Zap, FileText, Mail, HelpCircle } from 'lucide-react';

/**
 * TrustBar — bandeau de confiance placé juste sous le hero.
 * Chaque item est une "réponse contractuelle" qu'un acheteur F500 scanne
 * en < 5 secondes : garantie, sécurité, livraison, format, support.
 *
 * Design : minimaliste ivoire, bordure fine or, icônes lucide fine,
 * texte Inter 13px letter-spaced. Aucune promesse mensongère.
 *
 * Utilisation :
 *   <TrustBar variant="dense" />       // 4 items, dense (home/sales)
 *   <TrustBar variant="detailed" />    // 5 items, avec sous-texte (pages checkout)
 */
const ITEMS = [
  { Icon: Shield, label: 'Garantie 14 jours', hint: 'Remboursement sans condition' },
  { Icon: Lock,   label: 'Paiement Stripe',   hint: '256-bit SSL · PCI DSS niveau 1' },
  { Icon: Zap,    label: 'Livraison instantanée', hint: 'PDF reçu en < 60 secondes' },
  { Icon: FileText, label: 'PDF premium',     hint: 'Format A4 · téléchargeable à vie' },
  { Icon: Mail,   label: 'Support 7j/7',      hint: 'Réponse sous 24h · plume-astrale.fr' },
];

export default function TrustBar({ variant = 'dense' }) {
  const items = variant === 'detailed' ? ITEMS : ITEMS.slice(0, 4);
  return (
    <div
      className="ps-trust-bar"
      data-testid="trust-bar"
      role="complementary"
      aria-label="Garanties et engagements"
      style={{
        background: '#F7F5F0',
        borderTop: '1px solid #E3E1DC',
        borderBottom: '1px solid #E3E1DC',
        padding: '20px 0',
      }}
    >
      <div className="ps-container" style={{ maxWidth: 1180 }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(auto-fit, minmax(${variant === 'detailed' ? 200 : 160}px, 1fr))`,
            gap: variant === 'detailed' ? 24 : 20,
            alignItems: 'start',
          }}
        >
          {items.map(({ Icon, label, hint }) => (
            <div
              key={label}
              data-testid={`trust-${label.toLowerCase().replace(/[^a-z]/g, '-')}`}
              style={{ display: 'flex', alignItems: 'flex-start', gap: 12, minWidth: 0 }}
            >
              <div
                style={{
                  width: 32, height: 32, flexShrink: 0,
                  borderRadius: 8,
                  background: '#fff',
                  border: '1px solid #E3E1DC',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                }}
              >
                <Icon style={{ width: 16, height: 16, color: '#8F6E24' }} strokeWidth={1.6} />
              </div>
              <div style={{ minWidth: 0 }}>
                <div
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 13, fontWeight: 600,
                    color: '#0F1A3C',
                    letterSpacing: '0.01em',
                    lineHeight: 1.3,
                  }}
                >
                  {label}
                </div>
                {variant === 'detailed' && (
                  <div
                    style={{
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 11.5, color: '#6B7280',
                      lineHeight: 1.4, marginTop: 2,
                    }}
                  >
                    {hint}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
