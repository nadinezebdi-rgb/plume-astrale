import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Sparkles, Zap } from 'lucide-react';

/**
 * HomeCreditPacks — Teaser des packs de crédits en homepage.
 * Remplace l'ancienne grille "Six voies pour t'éclairer" (dilution du positionnement).
 * Point d'entrée à 7,99€ = casse la barrière psychologique du 89€.
 */
const PACKS = [
  {
    id: 'comete',
    name: 'Comète',
    price: '7,99 €',
    credits: 30,
    icon: Star,
    tagline: "L'étincelle rapide.",
    detail: '3 questions à Solena',
    badge: null,
  },
  {
    id: 'nebuleuse',
    name: 'Nébuleuse',
    price: '17,99 €',
    credits: 80,
    icon: Sparkles,
    tagline: 'Ton Thème Natal en 1 clic.',
    detail: '1 Thème Natal complet + 2 questions',
    badge: 'Le plus choisi',
  },
  {
    id: 'constellation',
    name: 'Constellation',
    price: '34,99 €',
    credits: 180,
    icon: Zap,
    tagline: 'Karma & relations en profondeur.',
    detail: '3 Thèmes Natals + synastrie amoureuse',
    badge: 'Meilleure valeur',
  },
  {
    id: 'voie_lactee',
    name: 'Voie Lactée',
    price: '59,99 €',
    credits: 350,
    icon: Zap,
    tagline: 'Le grand voyage.',
    detail: 'Tous les rapports premium débloqués',
    badge: null,
  },
];

const HomeCreditPacks = () => {
  return (
    <section
      className="py-20 md:py-28 px-6"
      style={{ background: 'linear-gradient(180deg, #0C0918 0%, #100926 100%)' }}
      data-testid="home-credit-packs"
    >
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-14">
          <p className="text-[10px] uppercase" style={{ color: '#D4AF37', letterSpacing: '0.3em', marginBottom: 12, fontWeight: 400 }}>
            Recharge ta puissance astrale
          </p>
          <h3 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontWeight: 200,
            fontSize: 'clamp(1.8rem, 4vw, 2.8rem)',
            color: '#F4E8D2',
            lineHeight: 1.2,
            marginBottom: 12,
          }}>
            À partir de <em style={{ color: '#D4AF37', fontStyle: 'italic', fontWeight: 300 }}>7,99&nbsp;€</em>,
            <br />pose ta première question.
          </h3>
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 'clamp(0.9rem, 1.15vw, 1rem)',
            color: 'rgba(244,232,210,0.72)',
            maxWidth: 520,
            margin: '0 auto',
            lineHeight: 1.6,
          }}>
            10 crédits = 1 question à Solena. Chaque pack contient des crédits offerts et n&apos;expire jamais.
          </p>
        </div>

        {/* Grille des 4 packs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5 mb-10">
          {PACKS.map((p) => {
            const Icon = p.icon;
            const isFeatured = p.badge === 'Le plus choisi';
            return (
              <Link
                key={p.id}
                to="/buy-credits"
                className="group relative rounded-2xl p-6 transition-all hover:scale-[1.03] hover:-translate-y-1"
                style={{
                  background: isFeatured
                    ? 'linear-gradient(160deg, rgba(212,175,55,0.15) 0%, rgba(30,26,51,0.85) 60%)'
                    : 'rgba(255,255,255,0.03)',
                  border: isFeatured
                    ? '1.5px solid rgba(212,175,55,0.55)'
                    : '1px solid rgba(212,175,55,0.20)',
                  backdropFilter: 'blur(12px)',
                  boxShadow: isFeatured
                    ? '0 12px 48px rgba(212,175,55,0.25), inset 0 1px 0 rgba(255,255,255,0.05)'
                    : '0 4px 24px rgba(0,0,0,0.3)',
                  textDecoration: 'none',
                  display: 'block',
                }}
                data-testid={`home-pack-${p.id}`}
              >
                {p.badge && (
                  <div
                    style={{
                      position: 'absolute',
                      top: -10,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      background: 'linear-gradient(135deg, #D4AF37 0%, #E8C766 100%)',
                      color: '#0A0603',
                      fontFamily: 'Cinzel, serif',
                      fontSize: 9,
                      letterSpacing: '0.18em',
                      textTransform: 'uppercase',
                      fontWeight: 700,
                      padding: '4px 12px',
                      borderRadius: 999,
                      whiteSpace: 'nowrap',
                      boxShadow: '0 4px 12px rgba(212,175,55,0.4)',
                    }}
                  >
                    {p.badge}
                  </div>
                )}

                {/* Icon */}
                <div className="flex items-center justify-center mb-4" style={{ height: 40 }}>
                  <Icon
                    style={{ width: 26, height: 26, color: '#E8C766', opacity: 0.9 }}
                    strokeWidth={1.3}
                  />
                </div>

                {/* Name */}
                <h4 style={{
                  fontFamily: 'Cormorant Garamond, serif',
                  fontSize: '1.35rem',
                  fontWeight: 300,
                  color: '#F4E8D2',
                  textAlign: 'center',
                  marginBottom: 6,
                  letterSpacing: '0.02em',
                }}>
                  {p.name}
                </h4>

                {/* Price + credits */}
                <div className="text-center mb-4">
                  <div style={{
                    fontFamily: 'Cinzel, serif',
                    fontSize: '1.6rem',
                    fontWeight: 500,
                    color: '#E8C766',
                    lineHeight: 1,
                  }}>
                    {p.price}
                  </div>
                  <div style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11,
                    letterSpacing: '0.15em',
                    color: 'rgba(244,232,210,0.55)',
                    marginTop: 6,
                    textTransform: 'uppercase',
                  }}>
                    {p.credits} crédits
                  </div>
                </div>

                {/* Tagline */}
                <p style={{
                  fontFamily: 'Cormorant Garamond, serif',
                  fontSize: '0.95rem',
                  color: 'rgba(244,232,210,0.85)',
                  textAlign: 'center',
                  fontStyle: 'italic',
                  marginBottom: 10,
                  lineHeight: 1.4,
                }}>
                  {p.tagline}
                </p>

                {/* Detail */}
                <p style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 12,
                  color: 'rgba(244,232,210,0.6)',
                  textAlign: 'center',
                  lineHeight: 1.5,
                  marginBottom: 16,
                }}>
                  {p.detail}
                </p>

                {/* CTA hint */}
                <div
                  className="text-center transition-all group-hover:opacity-100"
                  style={{
                    fontFamily: 'Cinzel, serif',
                    fontSize: 11,
                    letterSpacing: '0.18em',
                    color: '#E8C766',
                    textTransform: 'uppercase',
                    opacity: 0.75,
                  }}
                >
                  Choisir →
                </div>
              </Link>
            );
          })}
        </div>

        {/* Footer note */}
        <div className="text-center">
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            color: 'rgba(244,232,210,0.5)',
            marginBottom: 20,
          }}>
            Paiement sécurisé Stripe · Crédits non expirables · Utilisables sur tout le site
          </p>
          <Link
            to="/buy-credits"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '12px 28px',
              borderRadius: 999,
              background: 'transparent',
              border: '1px solid rgba(212,175,55,0.5)',
              color: '#E8C766',
              fontFamily: 'Cinzel, serif',
              fontSize: 12,
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(212,175,55,0.1)';
              e.currentTarget.style.borderColor = 'rgba(212,175,55,0.8)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'rgba(212,175,55,0.5)';
            }}
            data-testid="home-credit-packs-cta"
          >
            Voir tous les packs et détails
          </Link>
        </div>
      </div>
    </section>
  );
};

export default HomeCreditPacks;
